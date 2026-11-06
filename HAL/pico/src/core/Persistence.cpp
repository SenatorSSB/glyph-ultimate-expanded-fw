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
#include "core/PackageStorageFence.hpp"
#include "core/ConfigWireValidator.hpp"
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
#include "core/ProfileStore.hpp"
#endif
#include "core/Sha256.hpp"

#include "stdlib.hpp"

#include <CRC32.h>
#include <LittleFS.h>
#include <pb_arduino.h>
#include <pb_decode.h>
#include <pb_common.h>
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
    SynchronousFileScope(const char *path) { Construct(path); }
    ~SynchronousFileScope() { Destroy(); }
    static CheckedStorageFile &File() { return *std::launder(reinterpret_cast<CheckedStorageFile *>(save_file_slot)); }
    SynchronousFileScope(const SynchronousFileScope &) = delete;
    SynchronousFileScope &operator=(const SynchronousFileScope &) = delete;
  private:
    static __attribute__((noinline)) void Construct(const char *path) {
        std::memset(save_file_slot,0,sizeof(save_file_slot));
        ::new (save_file_slot) CheckedStorageFile(path,Write?"w+":"r");
    }
    static __attribute__((noinline)) void Destroy() {
        File().CheckedStorageFile::~CheckedStorageFile();
        std::memset(save_file_slot,0,sizeof(save_file_slot));
    }
};
struct SavePublicationState { bool current; CheckedStorage::Result operation; };
struct SavePhaseState {
    size_t encoded_size;
    Persistence::ConfigHeader header;
    union { SavePublicationState publication{}; pb_ostream_t stream; } temporary;
};

// Reuse the original single load candidate; only scalar phase facts survive
// preparation. Filenames below refer solely to the existing static constants.
Config loaded_candidate;
struct LoadPhaseState { CompactConfigRecovery::Source source; uint32_t crc; };
struct SaveSourceContext { Persistence *owner; Config *config; bool package = false; };
union SourcePhaseContext { LoadPhaseState load{}; SaveSourceContext save; } source_phase{};
#define load_phase source_phase.load
#define save_context source_phase.save

struct CapturePhaseState { const char *filename; size_t length; } capture_phase{};
struct LoadPhaseReset { ~LoadPhaseReset() { std::memset(&source_phase, 0, sizeof(source_phase)); } };
struct CapturePhaseReset { ~CapturePhaseReset() { std::memset(&capture_phase, 0, sizeof(capture_phase)); } };

constexpr char save_temporary_filename[] = "config-v2.tmp";

struct ConfigFileReader {
    CheckedStorageFile *file;
    bool io_failed = false;
};

// One finite synchronous observation; these scalar outputs survive sibling
// decode/wire/canonical phases, never another Config or encoded-body owner.
struct PackageObservationState {
    Config *into = nullptr;
    Persistence::PackageConfigFacts *facts = nullptr;
    bool *source_valid = nullptr;
    const char *path = nullptr;
    size_t maximum = 0;
    bool decoded = false;
    bool live = false;
} package_observation{};
// Borrowed scalar inputs span only the synchronous package save phases.
// Both fact objects live in the existing publication owner until completion.
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
struct PackageSaveState {
    Persistence *persistence=nullptr;
    const Persistence::PackageConfigFacts *baseline=nullptr,*expected=nullptr;
    const void *owner=nullptr;
    uint64_t token=0;
} package_save{};
#endif
struct PackageObservationReset {
    ~PackageObservationReset() { package_observation = {}; }
};
// Four is the frozen Config wire schema's complete message depth, including
// legacy embedded UltimateProfile children. Streams borrow the same read file;
// no Config/encoded-body owner or recursive filesystem decoder is added.
struct ObservedMessageFrame { pb_istream_t stream; const pb_msgdesc_t *descriptor; void *message; };
struct ObservedEncodingFrame { pb_field_iter_t field; size_t child_index; bool have_field; };
struct ReadWorkspace {
    ConfigFileReader reader; pb_istream_t stream; size_t file_size;
    union { ObservedMessageFrame observed[4]; ObservedEncodingFrame encoding[4]; };
};
union SynchronousPhaseWorkspace { SavePhaseState save{}; ReadWorkspace read; } phase_workspace{};
__attribute__((always_inline)) inline SavePhaseState &SavePhase(){return phase_workspace.save;}
__attribute__((always_inline)) inline ReadWorkspace &ReadPhase(){return phase_workspace.read;}
#define save_phase SavePhase()
#define read_workspace ReadPhase()
__attribute__((noinline)) void ResetReadWorkspace(){::new (&phase_workspace.read) ReadWorkspace;std::memset(&phase_workspace,0,sizeof(phase_workspace));}
struct SavePhaseReset {
    ~SavePhaseReset() { std::memset(&save_phase, 0, sizeof(save_phase)); }
};
struct ReadWorkspaceReset { ~ReadWorkspaceReset(){ResetReadWorkspace();} };
__attribute__((noinline)) bool skip_config_bytes(ConfigFileReader &reader, size_t count) {
    uint8_t skipped[32];
    while(count) {
        const size_t chunk=count>sizeof(skipped)?sizeof(skipped):count;
        const int n=reader.file->read(skipped,chunk);
        if(n<0||static_cast<size_t>(n)!=chunk){reader.io_failed=true;return false;}
        count-=chunk;
    }
    return true;
}
bool read_config_file(pb_istream_t *stream,pb_byte_t *buffer,size_t count) {
    auto &reader=*static_cast<ConfigFileReader *>(stream->state);
    if(!buffer)return skip_config_bytes(reader,count);
    if(!count)return true;
    const int n=reader.file->read(buffer,count);
    if(n<0||static_cast<size_t>(n)!=count){reader.io_failed=true;return false;}
    return true;
}

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
__attribute__((noinline)) config_wire::Result ValidatePackageConfigWire(CheckedStorageFile &file, size_t bytes) {
    config_wire::Workspace parser;
    uint8_t chunk[32];
    return config_wire::ValidateReader(parser,
        [](void *context, size_t offset, uint8_t *into, size_t count) {
            auto &source = *static_cast<CheckedStorageFile *>(context);
            return source.seek(Persistence::config_offset + offset) &&
                   source.read(into, count) == static_cast<int>(count);
        }, &file, bytes, chunk, sizeof(chunk));
}

#endif

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
bool CompareObservedConfigBytes(CheckedStorageFile &,const Config &,size_t);
#endif
bool compare_config_bytes(CheckedStorageFile &file, const Config &config, size_t encoded_size) {
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    if(package_observation.live)return CompareObservedConfigBytes(file,config,encoded_size);
#endif
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

__attribute__((noinline)) bool copy_open_files(CheckedStorageFile &input, CheckedStorageFile &output, size_t length) {
    bool copied = input && output;
    uint8_t scratch[64]; size_t remaining = length;
    while (copied && remaining) {
        const size_t count = remaining > sizeof(scratch) ? sizeof(scratch) : remaining;
        copied = input.read(scratch, count) == static_cast<int>(count) && output.write(scratch, count) == count;
        remaining -= count;
    }
    return copied;
}

__attribute__((noinline)) bool copy_checked_file(const char *from, const char *to, size_t length, bool &uncertain) {
    SynchronousFileScope<false> input_scope(from);
    CheckedStorageFile output(to, "w+"); // constructed even when input failed
    auto &input = input_scope.File();
    bool copied = copy_open_files(input, output, length);
    copied = copied && output.sync();
    const bool input_closed = input.close(), output_closed = output.close();
    uncertain = input.uncertain() || output.uncertain();
    return copied && input_closed && output_closed;
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
    PackageStorageFence::BeginMountAttempt();
    _configuration_ok = LittleFS.setConfig(LittleFSConfig(false));
    if (_configuration_ok) {
        _mounted = LittleFS.begin();
    }
    PackageStorageFence::FinishMountAttempt(_configuration_ok, _mounted);
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
    auto &removed = save_phase.temporary.publication.operation;
    ::new (&removed) CheckedStorage::Result(CheckedStorage::Remove(save_temporary_filename, CheckedStorage::Kind::Config));
    if (!removed) { _mutation_fenced = removed.outcome == CheckedStorage::Outcome::Uncertain; return false; }
    return true;
}

__attribute__((noinline)) bool Persistence::StageSaveConfig() {
    SynchronousFileScope<true> scope(save_temporary_filename);
    if(!InitializeStagedConfig())return FailStagedConfig();
    InitializeStagedStream();
    const bool encoded=EncodeStagedConfig();
    EndStagedStream();
    if(!encoded||!PositionStagedConfig())return FailStagedConfig();
    return CompleteStagedConfig();
}
// The exact existing slot holds CheckedStorageFile, so no virtual Print bridge
// is needed. This callback owns no state and preserves byte-count semantics.
static __attribute__((noinline)) bool WriteStagedBytes(pb_ostream_t *, const pb_byte_t *bytes, size_t count) {
    return SynchronousFileScope<true>::File().CheckedStorageFile::write(bytes, count) == count;
}
__attribute__((noinline)) void Persistence::InitializeStagedStream() {
    ::new (&save_phase.temporary.stream) pb_ostream_t{WriteStagedBytes, nullptr, SIZE_MAX, 0};
}
__attribute__((noinline)) bool Persistence::EncodeStagedConfig() {
    return pb_encode(&save_phase.temporary.stream,Config_fields,save_context.config)&&save_phase.temporary.stream.bytes_written==save_phase.encoded_size;
}
__attribute__((noinline)) void Persistence::EndStagedStream() {
    save_phase.temporary.stream.~pb_ostream_t();
    ::new (&save_phase.temporary.publication) SavePublicationState{};
}
__attribute__((noinline)) bool Persistence::PositionStagedConfig() { return SynchronousFileScope<true>::File().seek(config_offset); }
__attribute__((noinline)) bool Persistence::CompleteStagedConfig() {
    auto &file=SynchronousFileScope<true>::File();
    auto *owner=save_context.owner;
    auto &header=save_phase.header;
    auto staging_failed=[owner,&file](){if(save_context.package)PackageStorageFence::Fence();file.close();if(file.uncertain()||save_context.package)owner->_mutation_fenced=true;return false;};
    CRC32 crc;
    for (size_t i = 0; i < save_phase.encoded_size; ++i) {
        int value = file.read();
        if (value < 0) return staging_failed();
        crc.update(static_cast<uint8_t>(value));
    }
    header.config_size = save_phase.encoded_size; header.config_crc = crc.finalize();
    if (!file.seek(0) || file.write(reinterpret_cast<const uint8_t *>(&header), sizeof(header)) != sizeof(header) || !file.sync())
        return staging_failed();
    if (!file.close()) { owner->_mutation_fenced = file.uncertain(); return false; }
    return true;
}
__attribute__((noinline)) bool Persistence::FailStagedConfig() {
    auto &file=SynchronousFileScope<true>::File();auto *owner=save_context.owner;
    if(save_context.package)PackageStorageFence::Fence();
    file.close();if(file.uncertain()||save_context.package)owner->_mutation_fenced=true;return false;
}
__attribute__((noinline)) bool Persistence::InitializeStagedConfig() {
    auto &file=SynchronousFileScope<true>::File();
    if(!file)return false;
    return file.write(reinterpret_cast<const uint8_t *>(&save_phase.header),sizeof(save_phase.header))==sizeof(save_phase.header);
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
    auto &current = save_phase.temporary.publication.operation;
    ::new (&current) Result(Stat(config_filename, nullptr, Kind::Config));
    if (!current && current.outcome != Outcome::NotFound) return false;
    save_phase.temporary.publication.current = bool(current);
    if (current) {
#if !defined(GLYPH_PACKAGE_V1) || !GLYPH_PACKAGE_V1
        auto &prior_removed = save_phase.temporary.publication.operation;
        ::new (&prior_removed) Result(Remove(prior_compact_filename, Kind::Config));
        if (!prior_removed) { _mutation_fenced = prior_removed.outcome == Outcome::Uncertain; return false; }
#endif
        auto &rotated = save_phase.temporary.publication.operation;
        ::new (&rotated) Result(Rename(config_filename, prior_compact_filename, Kind::Config));
        if (!rotated) { _mutation_fenced = rotated.outcome == Outcome::Uncertain; return false; }
    }
    return true;
}

__attribute__((noinline)) bool Persistence::PublishStagedConfig(Config &config) {
    using namespace CheckedStorage;
    _pending_crc = save_phase.header.config_crc; _pending_size = save_phase.encoded_size;
    auto &publication = save_phase.temporary.publication.operation;
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
        if (save_phase.temporary.publication.current) {
            auto &rollback = save_phase.temporary.publication.operation;
            ::new (&rollback) Result(Rename(prior_compact_filename, config_filename, Kind::Config));
            if (!rollback) _mutation_fenced = true;
        }
        return false;
    }
    _config_generation = save_phase.header.config_crc;
    return true;
}

__attribute__((noinline)) bool Persistence::FinishSaveConfig(bool saved) {
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    if (!save_context.package) profile_store.EndOrdinaryConfigWrite();
#endif
    std::memset(&save_phase,0,sizeof(save_phase));
    std::memset(&source_phase,0,sizeof(source_phase));
    return saved;
}
__attribute__((noinline)) void Persistence::InitializeSaveContext(Persistence *owner,Config *config) {
    ::new (&source_phase.save) SaveSourceContext{owner,config};
    ::new (&phase_workspace.save) SavePhaseState;
    std::memset(&save_phase,0,sizeof(save_phase));
    ::new (&save_phase.temporary.publication) SavePublicationState{};
}
__attribute__((noinline)) bool Persistence::InitializeOrdinarySaveContext(Persistence *owner, Config *config) {
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    if (!profile_store.BeginOrdinaryConfigWrite(*config)) return false;
#endif
    InitializeSaveContext(owner, config);
    return true;
}
bool Persistence::SaveConfig(Config &config) {
    if (!InitializeOrdinarySaveContext(this,&config)) return false;
    return FinishSaveConfig(save_context.owner->PrepareSaveConfig(*save_context.config)&&
        save_context.owner->RemoveSaveTemporary()&&StageSaveConfig()&&
        save_context.owner->VerifyStagedConfig(*save_context.config)&&save_context.owner->RotateSavedConfig()&&
        save_context.owner->PublishStagedConfig(*save_context.config));
}

Persistence::SaveResult Persistence::ReconcileConfig(Config &authoritative) {
    if (!IsAvailable()) return SaveResult::Uncertain;
    // Reload the actually selected current/prior publication, never stale RAM.
    const auto loaded = LoadConfigDriver(authoritative);
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
    ResetReadWorkspace(); ReadWorkspaceReset read_reset;
    SynchronousFileScope<false> source_scope("/ultimate-migration.src");
    auto &source=source_scope.File();
    if (!source) return LoadResult::StorageFailure;
    LoadResult failure = LoadResult::Rejected;
    if (!CheckSavedConfig(source, &failure) || !source.seek(config_offset)) { source.close(); return failure; }
    auto &reader=read_workspace.reader;reader={&source};
    auto &stream=read_workspace.stream;stream={};stream.callback=read_config_file;stream.state=&reader;
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

__attribute__((noinline)) Persistence::LoadResult Persistence::CompleteReadConfigCandidate(CheckedStorageFile &config_file) {
    auto &candidate=loaded_candidate;
    ultimate_native::ClearEmbeddedCallbacks(candidate);
    ConfigValidationError error;
    if (!ValidateConfig(loaded_candidate, error)) {
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
__attribute__((noinline)) const char *Persistence::SelectReadConfigCandidate() {
    if(!IsAvailable()||_validator==nullptr)return nullptr;
    loaded_candidate=Config_init_default;
    const char *selected=nullptr;
    return select_config_filename(config_filename,prior_compact_filename,legacy_config_filename,selected,load_phase.source)?selected:nullptr;
}
__attribute__((noinline)) Persistence::LoadResult Persistence::InitializeReadConfigCandidate(CheckedStorageFile &file) {
    if(!file)return LoadResult::StorageFailure;
    LoadResult failure=LoadResult::Rejected;
    if(!CheckSavedConfig(file,&failure)){file.close();return failure;}
    read_workspace.file_size=file.size();
    if(read_workspace.file_size<config_offset||!file.seek(config_offset)){file.close();return LoadResult::StorageFailure;}
    read_workspace.reader={&file};
    ultimate_native::RejectEmbedded(loaded_candidate);
    read_workspace.stream={};read_workspace.stream.callback=read_config_file;
    read_workspace.stream.state=&read_workspace.reader;
    read_workspace.stream.bytes_left=read_workspace.file_size-config_offset;
    return LoadResult::Loaded;
}
__attribute__((noinline)) Persistence::LoadResult Persistence::FinishConfigDecode(CheckedStorageFile &file,bool decoded) {
    if(!decoded){file.close();return read_workspace.reader.io_failed?LoadResult::StorageFailure:LoadResult::Rejected;}
    if(read_workspace.stream.bytes_left!=0||file.position()!=read_workspace.file_size||file.size()!=read_workspace.file_size){file.close();return LoadResult::StorageFailure;}
    return CompleteReadConfigCandidate(file);
}
__attribute__((always_inline)) inline Persistence::LoadResult Persistence::ReadConfigCandidate() {
    const char *selected=SelectReadConfigCandidate();
    if(!selected)return LoadResult::StorageFailure;
    ResetReadWorkspace();ReadWorkspaceReset reset;
    SynchronousFileScope<false> scope(selected);
    const auto initialized=InitializeReadConfigCandidate(scope.File());
    if(initialized!=LoadResult::Loaded)return initialized;
    return FinishConfigDecode(scope.File(),pb_decode(&read_workspace.stream,Config_fields,&loaded_candidate));
}

__attribute__((noinline)) Persistence::LoadResult Persistence::FinishLoadedConfig(Config &config) {
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
__attribute__((always_inline)) inline Persistence::LoadResult Persistence::LoadConfigDriver(Config &config) {
    ::new (&source_phase.load) LoadPhaseState{};std::memset(&source_phase,0,sizeof(source_phase));LoadPhaseReset reset;
    const auto prepared=ReadConfigCandidate();
    if(prepared!=LoadResult::Loaded)return prepared;
    return FinishLoadedConfig(config);
}
Persistence::LoadResult Persistence::LoadConfigChecked(Config &config){return LoadConfigDriver(config);}


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

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
const char *Persistence::PackageFilename(PackageConfigFile file) {
    switch (file) {
        case PackageConfigFile::Current: return config_filename;
        case PackageConfigFile::Prior: return prior_compact_filename;
        case PackageConfigFile::Staged: return save_temporary_filename;
        case PackageConfigFile::Legacy: return legacy_config_filename;
        case PackageConfigFile::MigrationSource: return "/ultimate-migration.src";
        case PackageConfigFile::MigrationTemporary: return "/ultimate-migration.tmp";
    }
    return nullptr;
}

// SHA compression/finalization scratch ends before the next filesystem read.
static __attribute__((noinline)) void UpdatePackageHash(Sha256 &hash, const uint8_t *bytes, size_t count) {
    hash.Update(bytes, count);
}
static __attribute__((noinline)) void FinalizePackageHash(Sha256 &hash, uint8_t out[32]) {
    hash.Final(out);
}
__attribute__((noinline)) Persistence::LoadResult Persistence::ReadPackageFacts(
    const char *path, size_t maximum, PackageConfigFacts &facts) {
    facts = {};
    SynchronousFileScope<false> scope(path);
    auto &file = scope.File();
    if (!file) return LoadResult::StorageFailure;
    if (file.size() < config_offset || file.size() - config_offset > maximum) {
        return file.close() ? LoadResult::Rejected : LoadResult::StorageFailure;
    }
    ConfigHeader header;
    if (file.read(reinterpret_cast<uint8_t *>(&header), sizeof(header)) != static_cast<int>(sizeof(header)))
        return LoadResult::StorageFailure;
    if (header.config_size != file.size() - config_offset) {
        return file.close() ? LoadResult::Rejected : LoadResult::StorageFailure;
    }
    Sha256 hash;
    CRC32 crc;
    uint8_t scratch[32];
    size_t remaining = header.config_size;
    while (remaining) {
        const size_t count = remaining < sizeof(scratch) ? remaining : sizeof(scratch);
        if (file.read(scratch, count) != static_cast<int>(count)) return LoadResult::StorageFailure;
        UpdatePackageHash(hash, scratch, count); crc.update(scratch, count); remaining -= count;
    }
    if (file.position() != file.size() || !file.close()) return LoadResult::StorageFailure;
    if (crc.finalize() != header.config_crc) return LoadResult::Rejected;
    FinalizePackageHash(hash, facts.sha); facts.crc = header.config_crc; facts.bytes = header.config_size;
    return LoadResult::Loaded;
}

__attribute__((noinline)) bool Persistence::ValidateObservedPackageConfig(const Config &config) const {
    ConfigValidationError error;
    return ValidateConfig(config,error);
}
__attribute__((noinline)) Persistence::LoadResult Persistence::PrepareObservedPackageConfig() {
    auto &state = package_observation;
    if (!IsAvailable() || !_validator) return LoadResult::StorageFailure;
    const auto present = CheckedStorage::Stat(state.path, nullptr, CheckedStorage::Kind::Config);
    if (present.outcome == CheckedStorage::Outcome::NotFound) return LoadResult::Absent;
    if (!present) return LoadResult::StorageFailure;
    if (state.maximum > 65536) return LoadResult::Rejected;
    return ReadPackageFacts(state.path, state.maximum, *state.facts);
}
__attribute__((noinline)) Persistence::LoadResult Persistence::InitializeObservedPackageConfig() {
    auto &file = SynchronousFileScope<false>::File();
    auto &facts = *package_observation.facts;
    if (!file) { facts = {}; return LoadResult::StorageFailure; }
    const auto strict = ValidatePackageConfigWire(file, facts.bytes);
    if (strict != config_wire::Result::Valid) {
        const bool closed = file.close(); facts = {};
        return !closed || strict == config_wire::Result::StorageFailure ? LoadResult::StorageFailure : LoadResult::Rejected;
    }
    if (!file.seek(config_offset)) { facts = {}; return LoadResult::StorageFailure; }
    read_workspace.reader = {&file};
    read_workspace.stream = {};
    read_workspace.stream.callback = read_config_file;
    read_workspace.stream.state = &read_workspace.reader;
    read_workspace.stream.bytes_left = facts.bytes;
    ultimate_native::RejectEmbedded(loaded_candidate);
    return LoadResult::Loaded;
}
// Initialize only through the original generated descriptor. The frozen
// schema has no required fields; callbacks retain nanopb's original default
// policy, including the already-bound native-payload reject callback.
__attribute__((noinline)) bool InitializeObservedMessage(ObservedMessageFrame &frame) {
    if(frame.descriptor->required_field_count)return false;
    auto empty=pb_istream_from_buffer(nullptr,0);
    return pb_decode(&empty,frame.descriptor,frame.message);
}
__attribute__((noinline)) bool DecodeObservedField(size_t &depth) {
    auto &frame=read_workspace.observed[depth];auto &stream=frame.stream;
    auto &file=SynchronousFileScope<false>::File();
    const size_t start=file.position(),remaining=stream.bytes_left;
    pb_wire_type_t wire;uint32_t tag;bool eof;
    if(!pb_decode_tag(&stream,&wire,&tag,&eof))return false;
    pb_field_iter_t field;
    if(!pb_field_iter_begin(&field,frame.descriptor,frame.message)||!pb_field_iter_find(&field,tag))return false;
    if(PB_HTYPE(field.type)==PB_HTYPE_ONEOF||PB_ATYPE(field.type)==PB_ATYPE_POINTER||PB_LTYPE(field.type)==PB_LTYPE_EXTENSION)return false;
    if(PB_LTYPE_IS_SUBMSG(field.type)) {
        // Unsupported descriptor representations cannot fall through to a
        // recursive decode. The frozen schema uses STATIC SUBMESSAGE only.
        if(PB_ATYPE(field.type)!=PB_ATYPE_STATIC||PB_LTYPE(field.type)!=PB_LTYPE_SUBMESSAGE||
           wire!=PB_WT_STRING||depth+1>=sizeof(read_workspace.observed)/sizeof(*read_workspace.observed))return false;
        void *destination=field.pField;
        if(PB_HTYPE(field.type)==PB_HTYPE_REPEATED) {
            if(!field.pSize)return false;
            auto &count=*static_cast<pb_size_t*>(field.pSize);
            if(count>=field.array_size)return false;
            destination=static_cast<char*>(field.pField)+size_t(field.data_size)*count++;
        } else if(PB_HTYPE(field.type)==PB_HTYPE_OPTIONAL) {
            if(field.pSize)*static_cast<bool*>(field.pSize)=true;
        } else return false;
        auto &child=read_workspace.observed[depth+1];
        child.descriptor=field.submsg_desc;child.message=destination;
        if(!child.descriptor||!pb_make_string_substream(&stream,&child.stream)||!InitializeObservedMessage(child))return false;
        ++depth;return true;
    }
    // Scalar, fixed bytes, callbacks and packed arrays retain the original
    // descriptor decoder and its NOINIT accumulation/presence semantics. The
    // exact one-field replay cannot enter a following submessage recursively.
    if(!pb_skip_field(&stream,wire))return false;
    const size_t after=stream.bytes_left;
    if(!file.seek(start)){read_workspace.reader.io_failed=true;return false;}
    stream.bytes_left=remaining-after;
    if(!pb_decode_ex(&stream,frame.descriptor,frame.message,PB_DECODE_NOINIT)||stream.bytes_left)return false;
    stream.bytes_left=after;return true;
}
__attribute__((noinline)) bool DecodeObservedConfigFields() {
    ::new(static_cast<void*>(&read_workspace.observed))ObservedMessageFrame[4]{};
    auto &root=read_workspace.observed[0];root={read_workspace.stream,Config_fields,&loaded_candidate};
    size_t depth=0;
    for(;;) {
        auto &frame=read_workspace.observed[depth];
        if(frame.stream.bytes_left){if(!DecodeObservedField(depth))return false;}
        else if(depth){
            if(!pb_close_string_substream(&read_workspace.observed[depth-1].stream,&frame.stream))return false;
            frame={};--depth;
        } else break;
    }
    read_workspace.stream=root.stream;
    auto &file=SynchronousFileScope<false>::File();
    return file.position()==file.size()&&!read_workspace.reader.io_failed;
}
namespace {
__attribute__((noinline)) bool CompareObservedBytes(pb_ostream_t *out,const pb_byte_t *bytes,size_t count) {
    auto &file=*static_cast<CheckedStorageFile*>(out->state);uint8_t actual[32];
    while(count){const size_t chunk=count>sizeof(actual)?sizeof(actual):count;
        if(file.read(actual,chunk)!=static_cast<int>(chunk)){read_workspace.reader.io_failed=true;return false;}
        if(std::memcmp(actual,bytes,chunk))return false;
        bytes+=chunk;count-=chunk;
    }
    return true;
}
void NextObservedEncodingField(ObservedEncodingFrame &frame) {
    frame.child_index=0;frame.have_field=pb_field_iter_next(&frame.field);
}
__attribute__((noinline)) bool EncodeObservedField(pb_ostream_t &out,size_t &depth) {
    auto &frame=read_workspace.encoding[depth];auto &field=frame.field;
    if(PB_HTYPE(field.type)==PB_HTYPE_ONEOF||PB_ATYPE(field.type)==PB_ATYPE_POINTER||PB_LTYPE(field.type)==PB_LTYPE_EXTENSION)return false;
    if(PB_LTYPE_IS_SUBMSG(field.type)) {
        if(PB_ATYPE(field.type)!=PB_ATYPE_STATIC||PB_LTYPE(field.type)!=PB_LTYPE_SUBMESSAGE||
           !field.submsg_desc)return false;
        const void *message=field.pField;
        if(PB_HTYPE(field.type)==PB_HTYPE_REPEATED){
            if(!field.pSize)return false;
            const size_t count=*static_cast<const pb_size_t*>(field.pSize);
            if(count>field.array_size)return false;
            if(frame.child_index==count){NextObservedEncodingField(frame);return true;}
            message=static_cast<const char*>(field.pField)+size_t(field.data_size)*frame.child_index++;
        }else if(PB_HTYPE(field.type)==PB_HTYPE_OPTIONAL){
            // Every optional submessage in the frozen schema has a has flag.
            if(!field.pSize)return false;
            if(frame.child_index||!*static_cast<const bool*>(field.pSize)){NextObservedEncodingField(frame);return true;}
            frame.child_index=1;
        }else return false;
        if(depth+1>=sizeof(read_workspace.encoding)/sizeof(*read_workspace.encoding))return false;
        size_t bytes=0;
        // Sizing uses the original child descriptor after native callbacks have
        // been cleared. secondary_backends remains null from generated defaults
        // and strict callback-wire rejection; all sizing callbacks are null.
        if(!pb_get_encoded_size(&bytes,field.submsg_desc,message)||
           !pb_encode_tag(&out,PB_WT_STRING,field.tag)||!pb_encode_varint(&out,bytes))return false;
        auto &child=read_workspace.encoding[depth+1];child={};
        child.have_field=pb_field_iter_begin_const(&child.field,field.submsg_desc,message);
        ++depth;return true;
    }
    // This exact original field-info record retains type, width, offsets,
    // count/presence and packed/default/callback behavior. Its descriptor view
    // contains no message field, so encoding cannot recurse over filesystem I/O.
    const pb_msgdesc_t one{field.descriptor->field_info+field.field_info_index,nullptr,
        field.descriptor->default_value,field.descriptor->field_callback,1,0,field.tag};
    if(!pb_encode(&out,&one,field.message))return false;
    NextObservedEncodingField(frame);return true;
}
__attribute__((noinline)) bool CompareObservedConfigBytes(CheckedStorageFile &file,const Config &config,size_t bytes) {
    if(!file.seek(Persistence::config_offset))return false;
    // Decode streams are dead before this mutually exclusive phase begins.
    ::new(static_cast<void*>(&read_workspace.encoding))ObservedEncodingFrame[4]{};
    auto &root=read_workspace.encoding[0];root.have_field=pb_field_iter_begin_const(&root.field,Config_fields,&config);
    pb_ostream_t out{};out.callback=CompareObservedBytes;out.state=&file;out.max_size=bytes;
    size_t depth=0;
    for(;;){auto &frame=read_workspace.encoding[depth];
        if(frame.have_field){if(!EncodeObservedField(out,depth))return false;}
        else if(depth){frame={};--depth;}else break;
    }
    return out.bytes_written==bytes;
}
}
__attribute__((noinline)) void Persistence::DecodeObservedPackageConfig() {
    package_observation.decoded = DecodeObservedConfigFields();
    ultimate_native::ClearEmbeddedCallbacks(loaded_candidate);
}
__attribute__((noinline)) Persistence::LoadResult Persistence::FinishObservedPackageConfig() {
    auto &file = SynchronousFileScope<false>::File();
    auto &state = package_observation;
    auto &facts = *state.facts;
    const bool canonical = state.decoded && compare_config_bytes(file, loaded_candidate, facts.bytes);
    const bool io_failed=read_workspace.reader.io_failed||file.failed();
    const bool closed = file.close();
    if (io_failed||!closed) { facts = {}; return LoadResult::StorageFailure; }
    if (!canonical) { facts = {}; return LoadResult::Rejected; }
    *state.source_valid = ValidateObservedPackageConfig(loaded_candidate);
    *state.into = loaded_candidate;
    return LoadResult::Loaded;
}
__attribute__((noinline)) Persistence::LoadResult Persistence::ObservePackageConfig(
    PackageConfigFile selection, Config &into, PackageConfigFacts &facts, bool &source_valid,size_t maximum) {
    facts = {}; source_valid = false;
    if (package_observation.live||package_save.persistence) return LoadResult::StorageFailure;
    PackageObservationReset observation_reset;
    if (!maximum) maximum = selection == PackageConfigFile::Current || selection == PackageConfigFile::Staged ? 8191 : 65536;
    package_observation = {&into, &facts, &source_valid, PackageFilename(selection), maximum, false, true};
    const auto prepared = PrepareObservedPackageConfig();
    if (prepared != LoadResult::Loaded) return prepared;
    ResetReadWorkspace(); ReadWorkspaceReset reset;
    loaded_candidate = Config_init_default;
    SynchronousFileScope<false> scope(package_observation.path);
    const auto initialized = InitializeObservedPackageConfig();
    if (initialized != LoadResult::Loaded) return initialized;
    DecodeObservedPackageConfig();
    return FinishObservedPackageConfig();
}

__attribute__((noinline)) bool Persistence::MatchPackageConfig(
    const char *path, const PackageConfigFacts &expected) {
    PackageConfigFacts actual;
    return ReadPackageFacts(path, 8191, actual) == LoadResult::Loaded && actual.bytes == expected.bytes &&
           actual.crc == expected.crc && !std::memcmp(actual.sha, expected.sha, 32);
}

__attribute__((noinline)) bool Persistence::RotatePackagePrior() {
    auto &operation=save_phase.temporary.publication.operation;
    ::new (&operation) CheckedStorage::Result(CheckedStorage::Rename(config_filename,prior_compact_filename,CheckedStorage::Kind::Config));
    return bool(operation);
}
__attribute__((noinline)) bool Persistence::VerifyPackagePrior() {
    if(!package_save.persistence->MatchPackageConfig(prior_compact_filename,*package_save.baseline))return false;
    auto &operation=save_phase.temporary.publication.operation;
    ::new (&operation) CheckedStorage::Result(CheckedStorage::Stat(config_filename,nullptr,CheckedStorage::Kind::Config));
    return operation.outcome==CheckedStorage::Outcome::NotFound;
}
__attribute__((noinline)) bool Persistence::RotatePackageFinal() {
    auto &operation=save_phase.temporary.publication.operation;
    ::new (&operation) CheckedStorage::Result(CheckedStorage::Rename(save_temporary_filename,config_filename,CheckedStorage::Kind::Config));
    return bool(operation);
}
__attribute__((noinline)) bool Persistence::PublishPackageStaged() {
    // Same-mount replacement; no delete, rollback, continuation or cleanup.
    return RotatePackagePrior()&&VerifyPackagePrior()&&RotatePackageFinal();
}

__attribute__((noinline)) bool Persistence::PreparePackageConfig(
    Config &config,const PackageConfigFacts &baseline,const PackageConfigFacts &expected,
    const void *package_owner,uint64_t token) {
    if(package_save.persistence||package_observation.live||!IsAvailable()||_mutation_fenced||PackageStorageFence::MutationFenced()||
       !PackageStorageFence::IsPackageWriter(package_owner,token))return false;
    package_save={this,&baseline,&expected,package_owner,token};
    InitializeSaveContext(this,&config);save_context.package=true;
    return true;
}
__attribute__((noinline)) bool Persistence::PreparePackageSave() {
    auto &operation=save_phase.temporary.publication.operation;
    ::new (&operation) CheckedStorage::Result(CheckedStorage::Stat(save_temporary_filename,nullptr,CheckedStorage::Kind::Config));
    return operation.outcome==CheckedStorage::Outcome::NotFound&&
        package_save.persistence->MatchPackageConfig(config_filename,*package_save.baseline)&&
        package_save.persistence->PrepareSaveConfig(*save_context.config)&&
        save_phase.encoded_size==package_save.expected->bytes&&package_save.expected->bytes&&package_save.expected->bytes<=8191;
}
__attribute__((noinline)) bool Persistence::VerifyPackageSave() {
    return save_phase.header.config_crc==package_save.expected->crc&&
        package_save.persistence->VerifyStagedConfig(*save_context.config)&&
        package_save.persistence->MatchPackageConfig(save_temporary_filename,*package_save.expected);
}
__attribute__((noinline)) bool Persistence::VerifyPackageBaseline() {
    return package_save.persistence->MatchPackageConfig(config_filename,*package_save.baseline);
}
__attribute__((noinline)) bool Persistence::VerifyPackagePublished() {
    if(!package_save.persistence->MatchPackageConfig(config_filename,*package_save.expected))return false;
    auto &operation=save_phase.temporary.publication.operation;
    ::new (&operation) CheckedStorage::Result(CheckedStorage::Stat(save_temporary_filename,nullptr,CheckedStorage::Kind::Config));
    return operation.outcome==CheckedStorage::Outcome::NotFound&&
        PackageStorageFence::IsPackageWriter(package_save.owner,package_save.token);
}
__attribute__((noinline)) Persistence::SaveResult Persistence::FinishPackageSave(bool saved) {
    if(saved)package_save.persistence->_config_generation=package_save.expected->crc;
    else {package_save.persistence->_mutation_fenced=true;PackageStorageFence::Fence();}
    FinishSaveConfig(saved);package_save={};
    return saved?SaveResult::Saved:SaveResult::Uncertain;
}
__attribute__((noinline)) Persistence::SaveResult Persistence::PublishPreparedPackageConfig() {
    if(package_save.persistence!=this)return SaveResult::Uncertain;
    return FinishPackageSave(PreparePackageSave()&&StageSaveConfig()&&VerifyPackageSave()&&
        VerifyPackageBaseline()&&PublishPackageStaged()&&VerifyPackagePublished());
}

Config &Persistence::PackageConfigScratch() { return loaded_candidate; }

#endif

Persistence persistence;
