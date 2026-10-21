/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software. If not, see <http://www.gnu.org/licenses/>.
 */

#include "core/Persistence.hpp"
#include "core/CompactConfigRecovery.hpp"
#include "core/Sha256.hpp"

#include "stdlib.hpp"

#include <CRC32.h>
#include <LittleFS.h>
#include <pb_arduino.h>
#include <pb_decode.h>
#include "modes/UltimateNativeProfile.hpp"
#include <pb_encode.h>

#include <cstring>
#include <new>

namespace {

// Config save and migration-copy writers are synchronous core0 operations.
// Only the original copy input shares this slot; its output remains automatic.
// No Save/Capture/callback/IRQ/core1 path recursively acquires a live slot.
// Every scope explicitly destroys its File and clears the raw bytes on exit.
alignas(CheckedStorageFile) uint8_t save_file_slot[sizeof(CheckedStorageFile)]{};
template <bool Write> class SynchronousFileScope {
  public:
    __attribute__((noinline)) SynchronousFileScope(const char *path) {
        std::memset(save_file_slot, 0, sizeof(save_file_slot));
        _file = ::new (save_file_slot) CheckedStorageFile(path, Write ? "w+" : "r");
    }
    __attribute__((noinline)) ~SynchronousFileScope() {
        _file->CheckedStorageFile::~CheckedStorageFile(); // preserve opened-handle destructor fallback
        std::memset(save_file_slot, 0, sizeof(save_file_slot));
    }
    CheckedStorageFile &File() { return *_file; }
    SynchronousFileScope(const SynchronousFileScope &) = delete;
    SynchronousFileScope &operator=(const SynchronousFileScope &) = delete;
  private:
    CheckedStorageFile *_file;
};
struct SavePhaseState {
    size_t encoded_size;
    Persistence::ConfigHeader header;
    bool current;
    CheckedStorage::Result operation;
};
SavePhaseState save_phase{};
// Reuse the original single load candidate; only scalar phase facts survive
// preparation. Filenames below refer solely to the existing static constants.
Config loaded_candidate;
struct LoadPhaseState { CompactConfigRecovery::Source source; uint32_t crc; } load_phase{};
struct CapturePhaseState { const char *filename; size_t length; } capture_phase{};
struct LoadPhaseReset { ~LoadPhaseReset() { std::memset(&load_phase, 0, sizeof(load_phase)); } };
struct CapturePhaseReset { ~CapturePhaseReset() { std::memset(&capture_phase, 0, sizeof(capture_phase)); } };

struct SavePhaseReset {
    ~SavePhaseReset() { std::memset(&save_phase, 0, sizeof(save_phase)); }
};
constexpr char save_temporary_filename[] = "config-v2.tmp";

struct ConfigFileReader {
    CheckedStorageFile *file;
    bool io_failed = false;
};

bool read_config_file(pb_istream_t *stream, pb_byte_t *buffer, size_t count) {
    ConfigFileReader &reader = *static_cast<ConfigFileReader *>(stream->state);
    // Nanopb may request a skipped field with a null buffer. Keep that read
    // bounded, and distinguish short/error I/O from a complete malformed payload.
    uint8_t skipped[32];
    while (count != 0) {
        const size_t chunk = buffer == nullptr && count > sizeof(skipped)
            ? sizeof(skipped) : count;
        uint8_t *destination = buffer != nullptr ? buffer : skipped;
        const int read = reader.file->read(destination, chunk);
        if (read < 0 || static_cast<size_t>(read) != chunk) {
            reader.io_failed = true;
            return false;
        }
        count -= chunk;
        if (buffer != nullptr) buffer += chunk;
    }
    return true;
}

bool compare_config_bytes(CheckedStorageFile &file, const Config &config, size_t encoded_size) {
    if (!file.seek(Persistence::config_offset)) return false;
    pb_ostream_t compare{};
    compare.callback = [](pb_ostream_t *out, const pb_byte_t *bytes, size_t count) {
        auto &input = *static_cast<CheckedStorageFile *>(out->state);
        uint8_t actual[32];
        while (count) {
            const size_t chunk = count > sizeof(actual) ? sizeof(actual) : count;
            if (input.read(actual, chunk) != static_cast<int>(chunk) || std::memcmp(actual, bytes, chunk)) return false;
            bytes += chunk; count -= chunk;
        }
        return true;
    };
    compare.state = &file; compare.max_size = encoded_size;
    return pb_encode(&compare, Config_fields, &config) && compare.bytes_written == encoded_size;
}

__attribute__((noinline)) bool copy_open_files(CheckedStorageFile &input, CheckedStorageFile &output, size_t length, bool &uncertain) {
    bool copied = input && output;
    uint8_t scratch[64]; size_t remaining = length;
    while (copied && remaining) {
        const size_t count = remaining > sizeof(scratch) ? sizeof(scratch) : remaining;
        copied = input.read(scratch, count) == static_cast<int>(count) && output.write(scratch, count) == count;
        remaining -= count;
    }
    copied = copied && output.sync();
    const bool input_closed = input.close(), output_closed = output.close();
    uncertain = input.uncertain() || output.uncertain();
    return copied && input_closed && output_closed;
}

__attribute__((noinline)) bool copy_checked_file(const char *from, const char *to, size_t length, bool &uncertain) {
    SynchronousFileScope<false> input_scope(from);
    CheckedStorageFile output(to, "w+"); // constructed even when input failed
    return copy_open_files(input_scope.File(), output, length, uncertain);
}

__attribute__((noinline)) bool hash_file(const char *path, uint8_t digest[32]) {
    CheckedStorageFile file(path, "r");
    if (!file) return false;
    Sha256 hash; uint8_t scratch[128]; size_t remaining = file.size();
    while (remaining) {
        const size_t count = remaining > sizeof(scratch) ? sizeof(scratch) : remaining;
        if (file.read(scratch, count) != static_cast<int>(count)) { file.close(); return false; }
        hash.Update(scratch, count); remaining -= count;
    }
    if (!file.close()) return false;
    hash.Final(digest); return true;
}

bool select_config_filename(const char *current, const char *prior, const char *legacy,
                            const char *&filename, CompactConfigRecovery::Source &source) {
    using namespace CheckedStorage;
    const auto current_stat = Stat(current, nullptr, Kind::Config);
    if (!current_stat && current_stat.outcome != Outcome::NotFound) return false;
    const auto prior_stat = Stat(prior, nullptr, Kind::Config);
    if (!prior_stat && prior_stat.outcome != Outcome::NotFound) return false;
    source = CompactConfigRecovery::Select(bool(current_stat), bool(prior_stat));
    filename = source == CompactConfigRecovery::Source::Current ? current :
        (source == CompactConfigRecovery::Source::PriorCompact ? prior : legacy);
    return true;
}

}  // namespace

Persistence::Persistence() {
    _configuration_ok = LittleFS.setConfig(LittleFSConfig(false));
    if (_configuration_ok) {
        _mounted = LittleFS.begin();
    }
}

Persistence::~Persistence() {
    if (_mounted) {
        LittleFS.end();
    }
}

bool Persistence::IsAvailable() const {
    return _configuration_ok && _mounted;
}

uint32_t Persistence::ConfigGeneration(const Config &config) const {
    (void)config;
    return _config_generation;
}

bool Persistence::SetValidator(ConfigSemanticValidator validator) {
    if (validator == nullptr) {
        return false;
    }
    if (_validator != nullptr) {
        return _validator == validator;
    }
    _validator = validator;
    return true;
}

bool Persistence::ValidateConfig(const Config &config, ConfigValidationError &error) const {
    error = ConfigValidationError{};
    if (_validator == nullptr) {
        static const char message[] = "Config validator is not installed";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }
    // Every adapter receives an already bounded object. The generic callback
    // retains the existing binding and reference rules; 022 can add its adapter.
    if (!validate_config_extents(config)) {
        static const char message[] = "Config contains an invalid button binding";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }
    return _validator(config, error);
}

__attribute__((noinline)) Persistence::SaveResult Persistence::VerifyExpectedConfigGeneration(uint64_t expected_generation) {
    if (_mutation_fenced) return SaveResult::Uncertain;
    if (expected_generation != _config_generation) return SaveResult::Conflict;
    if (!IsAvailable()) return SaveResult::StorageFailure;
    CompactConfigRecovery::Source source;
    const char *filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, filename, source))
        return SaveResult::StorageFailure;
    SynchronousFileScope<false> scope(filename);
    auto &current = scope.File();
    if (!current) return SaveResult::StorageFailure;
    ConfigHeader header;
    const bool checked = CheckSavedConfig(current) && current.seek(0) &&
        current.read(reinterpret_cast<uint8_t *>(&header), sizeof(header)) == static_cast<int>(sizeof(header));
    const bool current_closed = current.close();
    if (!checked || !current_closed) return SaveResult::StorageFailure;
    if (expected_generation != header.config_crc) return SaveResult::Conflict;
    return SaveResult::Saved;
}

Persistence::SaveResult Persistence::SaveConfigIfGenerationMatches(Config &config, uint64_t expected_generation) {
    const auto verified = VerifyExpectedConfigGeneration(expected_generation);
    if (verified != SaveResult::Saved) return verified;
    // All Config writers execute synchronously on core0. No callback or yield
    // runs a Config writer between this fence and SaveConfig's publication.
    if (SaveConfig(config)) return SaveResult::Saved;
    return _mutation_fenced ? SaveResult::Uncertain : SaveResult::StorageFailure;
}

__attribute__((noinline)) bool Persistence::PrepareSaveConfig(const Config &config) {
    if (!IsAvailable() || _mutation_fenced) return false;
    return pb_get_encoded_size(&save_phase.encoded_size, Config_fields, &config);
}

__attribute__((noinline)) bool Persistence::RemoveSaveTemporary() {
    auto &removed = save_phase.operation;
    ::new (&removed) CheckedStorage::Result(CheckedStorage::Remove(save_temporary_filename, CheckedStorage::Kind::Config));
    if (!removed) { _mutation_fenced = removed.outcome == CheckedStorage::Outcome::Uncertain; return false; }
    return true;
}

__attribute__((noinline)) bool Persistence::StageSaveConfig(Config &config) {
    SynchronousFileScope<true> scope(save_temporary_filename);
    return WriteStagedConfig(scope.File(), config);
}

__attribute__((noinline)) bool Persistence::WriteStagedConfig(CheckedStorageFile &file, Config &config) {
    auto &header = save_phase.header;
    auto staging_failed = [this, &file]() {
        file.close();
        if (file.uncertain()) _mutation_fenced = true;
        return false;
    };
    if (!file) return staging_failed();
    if (file.write(reinterpret_cast<const uint8_t *>(&header), sizeof(header)) != sizeof(header))
        return staging_failed();
    pb_ostream_t stream = as_pb_ostream(file);
    if (!pb_encode(&stream, Config_fields, &config) || stream.bytes_written != save_phase.encoded_size || !file.seek(config_offset))
        return staging_failed();
    CRC32 crc;
    for (size_t i = 0; i < save_phase.encoded_size; ++i) {
        int value = file.read();
        if (value < 0) return staging_failed();
        crc.update(static_cast<uint8_t>(value));
    }
    header.config_size = save_phase.encoded_size; header.config_crc = crc.finalize();
    if (!file.seek(0) || file.write(reinterpret_cast<const uint8_t *>(&header), sizeof(header)) != sizeof(header) || !file.sync())
        return staging_failed();
    if (!file.close()) { _mutation_fenced = file.uncertain(); return false; }
    return true;
}

__attribute__((noinline)) bool Persistence::VerifyStagedConfig(Config &config) {
    SynchronousFileScope<false> scope(save_temporary_filename);
    auto &staged = scope.File();
    bool verified = staged && CheckSavedConfig(staged) && staged.seek(config_offset);
    // Compare independently reopened bytes with a second deterministic encode.
    verified = verified && compare_config_bytes(staged, config, save_phase.encoded_size);
    if (!staged.close() || !verified) { _mutation_fenced = staged.uncertain(); return false; }
    return true;
}

__attribute__((noinline)) bool Persistence::RotateSavedConfig() {
    using namespace CheckedStorage;
    auto &current = save_phase.operation;
    ::new (&current) Result(Stat(config_filename, nullptr, Kind::Config));
    if (!current && current.outcome != Outcome::NotFound) return false;
    save_phase.current = bool(current);
    if (current) {
        auto &prior_removed = save_phase.operation;
        ::new (&prior_removed) Result(Remove(prior_compact_filename, Kind::Config));
        if (!prior_removed) { _mutation_fenced = prior_removed.outcome == Outcome::Uncertain; return false; }
        auto &rotated = save_phase.operation;
        ::new (&rotated) Result(Rename(config_filename, prior_compact_filename, Kind::Config));
        if (!rotated) { _mutation_fenced = rotated.outcome == Outcome::Uncertain; return false; }
    }
    return true;
}

__attribute__((noinline)) bool Persistence::PublishStagedConfig(Config &config) {
    using namespace CheckedStorage;
    _pending_crc = save_phase.header.config_crc; _pending_size = save_phase.encoded_size;
    auto &publication = save_phase.operation;
    ::new (&publication) Result(Rename(save_temporary_filename, config_filename, Kind::Config));
    if (!publication) {
        if (publication.outcome == Outcome::Uncertain) {
            _mutation_fenced = true;
            // Exact authenticated readback can resolve a lost acknowledgement.
            SynchronousFileScope<false> scope(config_filename);
            auto &published = scope.File();
            ConfigHeader actual{};
            bool match = published && CheckSavedConfig(published) && published.seek(0) &&
                published.read(reinterpret_cast<uint8_t *>(&actual), sizeof(actual)) == static_cast<int>(sizeof(actual)) &&
                actual.config_crc == _pending_crc && actual.config_size == _pending_size &&
                compare_config_bytes(published, config, save_phase.encoded_size);
            if (published.close() && match) {
                _config_generation = save_phase.header.config_crc; _mutation_fenced = false; return true;
            }
            return false;
        }
        if (save_phase.current) {
            auto &rollback = save_phase.operation;
            ::new (&rollback) Result(Rename(prior_compact_filename, config_filename, Kind::Config));
            if (!rollback) _mutation_fenced = true;
        }
        return false;
    }
    _config_generation = save_phase.header.config_crc;
    return true;
}

bool Persistence::SaveConfig(Config &config) {
    std::memset(&save_phase, 0, sizeof(save_phase));
    SavePhaseReset reset;
    return PrepareSaveConfig(config) && RemoveSaveTemporary() && StageSaveConfig(config) &&
           VerifyStagedConfig(config) && RotateSavedConfig() && PublishStagedConfig(config);
}

Persistence::SaveResult Persistence::ReconcileConfig(Config &authoritative) {
    if (!IsAvailable()) return SaveResult::Uncertain;
    // Reload the actually selected current/prior publication, never stale RAM.
    const auto loaded = LoadConfigChecked(authoritative);
    if (loaded != LoadResult::Loaded) return SaveResult::Uncertain;
    _mutation_fenced = false;
    return SaveResult::Saved;
}

__attribute__((noinline)) bool Persistence::ValidateLegacySource() {
    if (!IsAvailable()) return false;
    CheckedStorageFile source("/ultimate-migration.src", "r");
    if (!source) return false;
    const bool valid = CheckSavedConfig(source);
    if (!source.close() || !valid) return false;
    return true;
}

__attribute__((noinline)) bool Persistence::LegacySourceIdentity(uint8_t digest[32]) {
    if (!ValidateLegacySource()) return false;
    return hash_file("/ultimate-migration.src", digest);
}

__attribute__((noinline)) bool Persistence::CheckCaptureInput() {
    using namespace CheckedStorage;
    if (!IsAvailable() || _mutation_fenced) return false;
    CompactConfigRecovery::Source selected;
    auto &filename = capture_phase.filename;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, filename, selected)) return false;
    auto &length = capture_phase.length;
    {
        CheckedStorageFile source(filename, "r");
        if (!source) return false;
        const bool valid = CheckSavedConfig(source);
        length = source.size();
        if (!source.close() || !valid) return false;
    }
    return true;
}

__attribute__((noinline)) bool Persistence::AdmitCaptureSource() {
    using namespace CheckedStorage;
    const auto length = capture_phase.length;
    Geometry geometry{};
    if (!Capacity(geometry) || !geometry.erase_bytes) return false;
    // Snapshot must not consume the project reserve or copy-on-write metadata
    // reserve even before ProfileStore performs its complete import admission.
    const uint64_t blocks = (uint64_t(length) + geometry.erase_bytes - 1) / geometry.erase_bytes;
    const uint64_t charged = uint64_t(length) + 4 * (blocks + 1);
    const uint64_t staged = ((charged + geometry.erase_bytes - 1) / geometry.erase_bytes) * geometry.erase_bytes;
    if (geometry.free_bytes < staged + 16384 + uint64_t(4) * geometry.erase_bytes) return false;
    return true;
}

__attribute__((noinline)) Persistence::CaptureAction Persistence::PrepareCaptureSource(uint8_t digest[32]) {
    using namespace CheckedStorage;
    if (!CheckCaptureInput()) return CaptureAction::Refused;
    const auto length = capture_phase.length;
    const char *filename = capture_phase.filename;
    if (length > 65536 || !hash_file(filename, digest)) return CaptureAction::Refused;
    auto snapshot = Stat("/ultimate-migration.src", nullptr, Kind::Config);
    if (snapshot) {
        uint8_t previous[32];
        return LegacySourceIdentity(previous) && std::memcmp(previous, digest, sizeof(previous)) == 0 ? CaptureAction::ExistingExact : CaptureAction::Refused;
    }
    if (snapshot.outcome != Outcome::NotFound) return CaptureAction::Refused;
    return AdmitCaptureSource() ? CaptureAction::NeedsCopy : CaptureAction::Refused;
}

bool Persistence::CaptureLegacySource(uint8_t digest[32]) {
    using namespace CheckedStorage;
    std::memset(&capture_phase, 0, sizeof(capture_phase));
    CapturePhaseReset reset;
    const auto action = PrepareCaptureSource(digest);
    if (action != CaptureAction::NeedsCopy) return action == CaptureAction::ExistingExact;
    return ExecuteCaptureSource(digest);
}

__attribute__((noinline)) bool Persistence::RemoveCaptureTemporary() {
    using namespace CheckedStorage;
    auto removed = Remove("/ultimate-migration.tmp", Kind::Config);
    if (!removed) { _mutation_fenced = removed.outcome == Outcome::Uncertain; return false; }
    return true;
}

__attribute__((noinline)) bool Persistence::CopyCapturedSource() {
    bool uncertain = false;
    if (!copy_checked_file(capture_phase.filename, "/ultimate-migration.tmp", capture_phase.length, uncertain)) {
        _mutation_fenced = uncertain; return false;
    }
    return true;
}

__attribute__((noinline)) bool Persistence::VerifyPublishCapturedSource(uint8_t digest[32]) {
    using namespace CheckedStorage;
    uint8_t actual[32];
    if (!hash_file("/ultimate-migration.tmp", actual) || std::memcmp(actual, digest, sizeof(actual))) return false;
    auto published = Rename("/ultimate-migration.tmp", "/ultimate-migration.src", Kind::Config);
    if (!published && published.outcome != Outcome::Uncertain) return false;
    if (!LegacySourceIdentity(actual) || std::memcmp(actual, digest, sizeof(actual))) {
        _mutation_fenced = published.outcome == Outcome::Uncertain; return false;
    }
    return true;
}

__attribute__((noinline)) bool Persistence::ExecuteCaptureSource(uint8_t digest[32]) {
    if (!RemoveCaptureTemporary() || !CopyCapturedSource()) return false;
    return VerifyPublishCapturedSource(digest);
}

Persistence::LoadResult Persistence::ReadLegacyProfile(size_t index, UltimateProfile &profile) {
    if (!IsAvailable() || index >= 2) return LoadResult::StorageFailure;
    CheckedStorageFile source("/ultimate-migration.src", "r");
    if (!source) return LoadResult::StorageFailure;
    LoadResult failure = LoadResult::Rejected;
    if (!CheckSavedConfig(source, &failure) || !source.seek(config_offset)) { source.close(); return failure; }
    ConfigFileReader reader{&source};
    pb_istream_t stream{}; stream.callback = read_config_file; stream.state = &reader;
    stream.bytes_left = source.size() - config_offset;
    size_t found = 0; bool decoded = false;
    while (stream.bytes_left) {
        pb_wire_type_t wire; uint32_t tag; bool eof;
        if (!pb_decode_tag(&stream, &wire, &tag, &eof)) break;
        if (tag == Config_ultimate_profiles_tag) {
            if (wire != PB_WT_STRING) break;
            if (found++ == index) {
                pb_istream_t substream;
                if (!pb_make_string_substream(&stream, &substream)) break;
                profile = UltimateProfile_init_default;
                profile.native_payload.funcs.decode = ultimate_native::RejectPayload;
                decoded = pb_decode(&substream, UltimateProfile_fields, &profile) && substream.bytes_left == 0;
                if (!pb_close_string_substream(&stream, &substream)) decoded = false;
                profile.native_payload = {};
                break;
            }
        }
        if (!pb_skip_field(&stream, wire)) break;
    }
    const bool closed = source.close();
    if (!closed || reader.io_failed) return LoadResult::StorageFailure;
    return decoded ? LoadResult::Loaded : LoadResult::Rejected;
}

bool Persistence::LoadConfig(Config &config) {
    return LoadConfigChecked(config) == LoadResult::Loaded;
}

__attribute__((noinline)) Persistence::LoadResult Persistence::ReadConfigCandidate() {
    if (!IsAvailable() || _validator == nullptr) {
        return LoadResult::StorageFailure;
    }

    // Config is too large for the core stack. This boot-owned candidate never
    // becomes active and is reset for every attempt, including partial decodes.
    auto &candidate = loaded_candidate;
    candidate = Config_init_default;

    auto &source = load_phase.source;
    const char *selected_filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, selected_filename, source))
        return LoadResult::StorageFailure;
    CheckedStorageFile config_file(selected_filename, "r");
    if (!config_file) {
        // The selected Boolean FS API cannot distinguish absence from I/O failure.
        // Absent remains reserved for positively proved absence; it is not inferred.
        return LoadResult::StorageFailure;
    }

    LoadResult failure = LoadResult::Rejected;
    if (!CheckSavedConfig(config_file, &failure)) {
        config_file.close();
        return failure;
    }
    const size_t file_size = config_file.size();
    if (file_size < config_offset || !config_file.seek(config_offset)) {
        config_file.close();
        return LoadResult::StorageFailure;
    }

    ConfigFileReader reader{ &config_file };
    ultimate_native::RejectEmbedded(candidate);
    pb_istream_t istream{};
    istream.callback = read_config_file;
    istream.state = &reader;
    istream.bytes_left = file_size - config_offset;
    if (!pb_decode(&istream, Config_fields, &candidate)) {
        config_file.close();
        return reader.io_failed ? LoadResult::StorageFailure : LoadResult::Rejected;
    }
    if (istream.bytes_left != 0 || config_file.position() != file_size ||
        config_file.size() != file_size) {
        config_file.close();
        return LoadResult::StorageFailure;
    }

    ultimate_native::ClearEmbeddedCallbacks(candidate);
    ConfigValidationError error;
    if (!ValidateConfig(candidate, error)) {
        config_file.close();
        return LoadResult::Rejected;
    }

    ConfigHeader header;
    if (!config_file.seek(0) ||
        config_file.read(reinterpret_cast<uint8_t *>(&header), sizeof(header)) != static_cast<int>(sizeof(header))) {
        config_file.close();
        return LoadResult::StorageFailure;
    }
    if (!config_file.close()) return LoadResult::StorageFailure;
    load_phase.crc = header.config_crc;
    return LoadResult::Loaded;
}

Persistence::LoadResult Persistence::LoadConfigChecked(Config &config) {
    std::memset(&load_phase, 0, sizeof(load_phase));
    LoadPhaseReset reset;
    const auto prepared = ReadConfigCandidate();
    if (prepared != LoadResult::Loaded) return prepared;
    if (load_phase.source == CompactConfigRecovery::Source::PriorCompact) {
        auto restored = CheckedStorage::Rename(prior_compact_filename, config_filename, CheckedStorage::Kind::Config);
        if (!restored) {
            if (restored.outcome == CheckedStorage::Outcome::Uncertain) _mutation_fenced = true;
            return LoadResult::StorageFailure;
        }
    }
    config = loaded_candidate;
    _config_generation = load_phase.crc;
    return LoadResult::Loaded;
}

bool Persistence::CheckSavedConfig() {
    if (!IsAvailable()) {
        return false;
    }
    // Open file to load config data from.
    CompactConfigRecovery::Source source;
    const char *selected_filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, selected_filename, source))
        return false;
    CheckedStorageFile config_file(selected_filename, "r");
    if (!config_file) {
        return false;
    }

    bool is_valid = CheckSavedConfig(config_file);
    return config_file.close() && is_valid;
}

size_t Persistence::LoadConfigRaw(Print &out, bool validate) {
    if (!IsAvailable()) {
        return false;
    }
    // Open file to load config data from.
    CompactConfigRecovery::Source source;
    const char *selected_filename = nullptr;
    if (!select_config_filename(config_filename, prior_compact_filename, legacy_config_filename, selected_filename, source))
        return false;
    CheckedStorageFile config_file(selected_filename, "r");
    if (!config_file) {
        return false;
    }

    // Optionally perform validation.
    if (validate && !CheckSavedConfig(config_file)) {
        config_file.close();
        return false;
    }

    // Seek to start of Protobuf data.
    if (!config_file.seek(config_offset)) {
        config_file.close();
        return false;
    }

    // Write raw Protobuf encoded data to output stream.
    int value;
    while ((value = config_file.read()) != -1) {
        out.write((uint8_t)value);
    }

    return config_file.close();
}

bool Persistence::CheckSavedConfig(CheckedStorageFile &config_file, LoadResult *failure) {
    if (failure != nullptr) {
        *failure = LoadResult::Rejected;
    }
    const size_t file_size = config_file.size();
    if (file_size < config_offset) {
        return false;
    }
    if (!config_file.seek(0)) {
        if (failure != nullptr) *failure = LoadResult::StorageFailure;
        return false;
    }

    ConfigHeader header;
    const int bytes_read = config_file.read((uint8_t *)&header, sizeof(ConfigHeader));
    if (bytes_read != static_cast<int>(sizeof(ConfigHeader))) {
        if (failure != nullptr) *failure = LoadResult::StorageFailure;
        return false;
    }
    const size_t config_size = file_size - config_offset;
    if (config_size != header.config_size) {
        return false;
    }

    CRC32 crc;
    for (size_t i = 0; i < config_size; ++i) {
        const int value = config_file.read();
        if (value < 0) {
            if (failure != nullptr) *failure = LoadResult::StorageFailure;
            return false;
        }
        crc.update((uint8_t)value);
    }
    if (config_file.position() != file_size || config_file.size() != file_size) {
        if (failure != nullptr) *failure = LoadResult::StorageFailure;
        return false;
    }
    return crc.finalize() == header.config_crc;
}

Persistence persistence;
