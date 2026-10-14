#include "core/ProfileStore.hpp"
#include "core/ProfileStoreAtomicCommit.hpp"
#include "core/ProfileStoreCapacity.hpp"
#include "core/ProfileStoreStorage.hpp"

#include "core/config_validation.hpp"

#include <LittleFS.h>
#include <pb_decode.h>
#include <pb_encode.h>

#include <cstdio>
#include <cstring>

namespace {

constexpr uint32_t kDirectoryMagic = 0x31534450u; // "PDS1" little endian
constexpr uint32_t kRecordMagic = 0x31525055u;    // "UPR1" little endian
constexpr uint16_t kEnvelopeVersion = 1;
constexpr uint16_t kPayloadUltimateProfile = 1;
constexpr size_t kRecordHeaderSize = 32;
constexpr size_t kMaxProfileWireBytes = 4096;
constexpr size_t kMaxRecordWireBytes = kRecordHeaderSize + kMaxProfileWireBytes;
constexpr size_t kDirectoryWireBytes = 32 + ProfileStore::kMaxEntries * 40 + 28;
static_assert(ProfileStoreCapacity::FitsRepresentativeSet(ProfileStore::kMinimumAdmissionProfiles,
              kMaxRecordWireBytes, kDirectoryWireBytes),
              "the frozen 512KiB/16KiB-reserve capacity must admit twenty profiles");

uint32_t Crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xffffffffu;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}
void Put16(uint8_t *p, uint16_t value) { p[0] = value; p[1] = value >> 8; }
void Put32(uint8_t *p, uint32_t value) { for (size_t i = 0; i < 4; ++i) p[i] = value >> (i * 8); }
uint16_t Get16(const uint8_t *p) { return static_cast<uint16_t>(p[0] | (p[1] << 8)); }
uint32_t Get32(const uint8_t *p) { uint32_t value = 0; for (size_t i = 0; i < 4; ++i) value |= uint32_t(p[i]) << (i * 8); return value; }

bool WriteAll(File &file, const uint8_t *bytes, size_t length) {
    return file.write(bytes, length) == length;
}
bool ReadAll(File &file, uint8_t *bytes, size_t length) {
    return file.read(bytes, length) == static_cast<int>(length) && file.available() == 0;
}
void DirectoryPath(char *out, size_t length, uint8_t slot) { std::snprintf(out, length, "/ultimate-dir-%u.bin", slot); }
void RecordPath(char *out, size_t length, uint32_t id, uint32_t revision) {
    std::snprintf(out, length, "/ultimate-%08lx-%08lx.bin", static_cast<unsigned long>(id), static_cast<unsigned long>(revision));
}

} // namespace

struct ProfileStore::Directory {
    uint32_t generation = 0;
    uint32_t incarnation = 0;
    uint32_t high_water_id = 0;
    uint32_t migration_digest = 0;
    uint32_t migration_state = 0; // 0 none, 1 receipt/fenced, 2 compact config published
    uint32_t migration_ids[2] = {};
    uint32_t last_token = 0;
    uint32_t last_digest = 0;
    TransactionResult last_result{};
    size_t count = 0;
    Entry entries[kMaxEntries] = {};
};

namespace {

bool EncodeDirectory(const ProfileStore::Directory &directory, uint8_t (&wire)[kDirectoryWireBytes]) {
    if (directory.count > ProfileStore::kMaxEntries || directory.incarnation == 0) return false;
    std::memset(wire, 0, sizeof(wire));
    Put32(wire, kDirectoryMagic); Put16(wire + 4, kEnvelopeVersion); Put16(wire + 6, static_cast<uint16_t>(directory.count));
    Put32(wire + 8, directory.generation); Put32(wire + 12, directory.incarnation); Put32(wire + 16, directory.high_water_id);
    Put32(wire + 20, directory.migration_digest); Put32(wire + 24, directory.migration_state); Put32(wire + 28, directory.last_token);
    size_t off = 32;
    for (size_t i = 0; i < directory.count; ++i, off += 40) {
        const auto &entry = directory.entries[i];
        if (entry.id == 0 || entry.revision == 0) return false;
        Put32(wire + off, entry.id); Put32(wire + off + 4, entry.revision); Put32(wire + off + 8, entry.previous_revision);
        Put32(wire + off + 12, entry.payload_version); Put32(wire + off + 16, entry.rank);
        std::memcpy(wire + off + 20, entry.name, ProfileStore::kNameCapacity);
        Put16(wire + off + 38, 0);
    }
    off = 32 + ProfileStore::kMaxEntries * 40;
    Put32(wire + off, directory.last_digest); Put32(wire + off + 4, static_cast<uint32_t>(directory.last_result.status));
    Put32(wire + off + 8, directory.last_result.id); Put32(wire + off + 12, directory.last_result.revision);
    Put32(wire + off + 16, directory.migration_ids[0]); Put32(wire + off + 20, directory.migration_ids[1]);
    Put32(wire + off + 24, Crc32(wire, off + 24));
    return true;
}

bool DecodeDirectory(const uint8_t (&wire)[kDirectoryWireBytes], ProfileStore::Directory *directory) {
    const size_t trailer = 32 + ProfileStore::kMaxEntries * 40;
    if (Get32(wire) != kDirectoryMagic || Get16(wire + 4) != kEnvelopeVersion ||
        Get16(wire + 6) > ProfileStore::kMaxEntries || Get32(wire + trailer + 24) != Crc32(wire, trailer + 24)) return false;
    static ProfileStore::Directory parsed;
    parsed = {};
    parsed.count = Get16(wire + 6); parsed.generation = Get32(wire + 8); parsed.incarnation = Get32(wire + 12);
    parsed.high_water_id = Get32(wire + 16); parsed.migration_digest = Get32(wire + 20); parsed.migration_state = Get32(wire + 24);
    parsed.last_token = Get32(wire + 28); parsed.last_digest = Get32(wire + trailer); parsed.last_result.status = static_cast<ProfileStore::Status>(Get32(wire + trailer + 4));
    parsed.last_result.id = Get32(wire + trailer + 8); parsed.last_result.revision = Get32(wire + trailer + 12); parsed.migration_ids[0] = Get32(wire + trailer + 16); parsed.migration_ids[1] = Get32(wire + trailer + 20); parsed.last_result.generation = parsed.generation;
    if (parsed.incarnation == 0 || (parsed.high_water_id == 0 && parsed.count != 0)) return false;
    size_t off = 32;
    for (size_t i = 0; i < parsed.count; ++i, off += 40) {
        auto &entry = parsed.entries[i]; entry.id = Get32(wire + off); entry.revision = Get32(wire + off + 4); entry.previous_revision = Get32(wire + off + 8);
        entry.payload_version = Get32(wire + off + 12); entry.rank = Get32(wire + off + 16); std::memcpy(entry.name, wire + off + 20, ProfileStore::kNameCapacity);
        if (entry.id == 0 || entry.revision == 0 || entry.id > parsed.high_water_id) return false;
        for (size_t j = 0; j < i; ++j) if (parsed.entries[j].id == entry.id) return false;
    }
    *directory = parsed; return true;
}

class LittleFsDirectoryStorage final : public ProfileStoreStorage {
  public:
    bool Write(const char *path, const uint8_t *bytes, size_t length) override {
        _last_failure = ProfileStoreIoStage::None;
        File file = LittleFS.open(path, "w+");
        if (!file) { _last_failure = ProfileStoreIoStage::RecordTempOpenWrite; return false; }
        const bool ok = WriteAll(file, bytes, length);
        if (!ok) _last_failure = ProfileStoreIoStage::RecordTempWrite;
        if (file) file.close();
        return ok;
    }
    bool Read(const char *path, uint8_t *bytes, size_t length) override {
        _last_failure = ProfileStoreIoStage::None;
        File file = LittleFS.open(path, "r");
        if (!file) { _last_failure = ProfileStoreIoStage::RecordTempRead; return false; }
        if (file.size() != length) { _last_failure = ProfileStoreIoStage::RecordTempSize; file.close(); return false; }
        const bool ok = ReadAll(file, bytes, length);
        if (!ok) _last_failure = ProfileStoreIoStage::RecordTempRead;
        if (file) file.close();
        return ok;
    }
    size_t Size(const char *path) override {
        File file = LittleFS.open(path, "r");
        const size_t size = file ? file.size() : 0;
        if (file) file.close();
        return size;
    }
    bool Exists(const char *path) override { return LittleFS.exists(path); }
    ProfileStoreIoStage LastFailureStage() const override { return _last_failure; }
    bool Remove(const char *path) override {
        return !LittleFS.exists(path) || LittleFS.remove(path);
    }
    bool Rename(const char *from, const char *to) override { return LittleFS.rename(from, to); }
  private:
    ProfileStoreIoStage _last_failure = ProfileStoreIoStage::None;
};

bool ReadDirectorySlot(ProfileStoreStorage &storage, uint8_t slot, ProfileStore::Directory *directory) {
    char path[32]; DirectoryPath(path, sizeof(path), slot);
    static uint8_t wire[kDirectoryWireBytes];
    return storage.Read(path, wire, sizeof(wire)) && DecodeDirectory(wire, directory);
}

bool DecodeDirectoryCommit(void *context, const uint8_t *bytes, size_t length) {
    if (length != kDirectoryWireBytes) return false;
    auto *directory = static_cast<ProfileStore::Directory *>(context);
    uint8_t wire[kDirectoryWireBytes];
    std::memcpy(wire, bytes, sizeof(wire));
    return DecodeDirectory(wire, directory);
}

struct RecordCommitContext {
    uint32_t incarnation;
    uint32_t id;
    uint32_t revision;
};

bool VerifyRecordCommit(void *context, const uint8_t *bytes, size_t length) {
    const auto *expected = static_cast<const RecordCommitContext *>(context);
    if (length < kRecordHeaderSize || Get32(bytes) != kRecordMagic ||
        Get16(bytes + 4) != kEnvelopeVersion || Get16(bytes + 6) != kPayloadUltimateProfile ||
        Get32(bytes + 8) != expected->incarnation || Get32(bytes + 12) != expected->id ||
        Get32(bytes + 16) != expected->revision || Get32(bytes + 20) != length - kRecordHeaderSize ||
        Get32(bytes + 20) > kMaxProfileWireBytes || Get32(bytes + 24) != Crc32(bytes, 24) ||
        Get32(bytes + 28) != Crc32(bytes + kRecordHeaderSize, length - kRecordHeaderSize)) return false;
    return true;
}

} // namespace

ProfileStore::ProfileStore(ProfileStoreStorage *storage) : _storage(storage) {}
bool ProfileStore::Begin() {
    static Directory directory{};
    static LittleFsDirectoryStorage default_storage;
    if (_storage == nullptr) _storage = &default_storage;
    _directory = &directory; _active_id = 0; _ready = false; _read_only_recovery = false;
    return LoadDirectory();
}
bool ProfileStore::IsReady() const { return _ready; }
bool ProfileStore::IsReadOnlyRecovery() const { return _read_only_recovery; }
bool ProfileStore::MigrationPending() const { return _directory && _directory->migration_state == 1; }
uint32_t ProfileStore::LegacyMigrationId(size_t legacy_index) const { return !_directory || legacy_index >= 2 ? 0 : _directory->migration_ids[legacy_index]; }
uint32_t ProfileStore::Incarnation() const { return _directory ? _directory->incarnation : 0; }
uint32_t ProfileStore::Generation() const { return _directory ? _directory->generation : 0; }
size_t ProfileStore::Count() const { return _directory ? _directory->count : 0; }
const ProfileStore::Entry *ProfileStore::EntryAt(size_t index) const { return !_directory || index >= _directory->count ? nullptr : &_directory->entries[index]; }
ProfileStore::Status ProfileStore::Read(uint32_t id, UltimateProfile &into, uint32_t *revision) const {
    if (!_ready) return Status::IoFailure;
    const int index = Find(id);
    if (index < 0) return Status::NotFound;
    const Entry &entry = _directory->entries[index];
    if (!ReadProfile(id, entry.revision, into)) return Status::Invalid;
    if (revision) *revision = entry.revision;
    return Status::Ok;
}
const UltimateProfile *ProfileStore::ActiveProfile() const { return _active_id == 0 ? nullptr : &_active_profile; }
uint32_t ProfileStore::ActiveId() const { return _active_id; }

bool ProfileStore::LoadDirectory() {
    static Directory a{}, b{}; a = {}; b = {};
    const bool a_ok = ReadDirectorySlot(*_storage, 0, &a), b_ok = ReadDirectorySlot(*_storage, 1, &b);
    if (!a_ok && !b_ok) { // Empty store is the only writable implicit state.
        _directory->incarnation = 1; _directory->generation = 0; _directory->high_water_id = 0; _ready = true; return true;
    }
    if (a_ok && b_ok && a.generation == b.generation && std::memcmp(&a, &b, sizeof(Directory)) != 0) { _read_only_recovery = true; return false; }
    *_directory = (!b_ok || (a_ok && a.generation > b.generation)) ? a : b;
    _ready = true; return true;
}

bool ProfileStore::PublishDirectory(const Directory &next) {
    if (!_ready || _read_only_recovery) return false;
    static uint8_t wire[kDirectoryWireBytes];
    if (!EncodeDirectory(next, wire)) return false;
    const uint8_t slot = static_cast<uint8_t>((next.generation + 1) & 1u); char path[32], temporary[40]; DirectoryPath(path, sizeof(path), slot); std::snprintf(temporary, sizeof(temporary), "%s.tmp", path);
    static Directory verified;
    verified = {};
    if (!ProfileStoreAtomicCommit::ReplaceInactiveRoot(*_storage, temporary, path, wire, sizeof(wire),
            DecodeDirectoryCommit, &verified) || verified.generation != next.generation) return false;
    *_directory = next; return true;
}

int ProfileStore::Find(uint32_t id) const { if (!_directory || id == 0) return -1; for (size_t i = 0; i < _directory->count; ++i) if (_directory->entries[i].id == id) return static_cast<int>(i); return -1; }
bool ProfileStore::ValidateProfile(const UltimateProfile &profile) const {
    ConfigValidationError error;
    return validate_ultimate_profile_semantics(profile, error);
}
bool ProfileStore::WriteProfile(uint32_t id, uint32_t revision, const UltimateProfile &profile) {
    _last_io_stage = ProfileStoreIoStage::None;
    if (!ValidateProfile(profile)) return false;
    size_t length = 0;
    if (!pb_get_encoded_size(&length, UltimateProfile_fields, &profile) || length > kMaxProfileWireBytes) {
        _last_io_stage = ProfileStoreIoStage::RecordEncodeSize;
        return false;
    }
    static uint8_t record[kMaxRecordWireBytes];
    std::memset(record, 0, sizeof(record));
    Put32(record, kRecordMagic); Put16(record + 4, kEnvelopeVersion); Put16(record + 6, kPayloadUltimateProfile);
    Put32(record + 8, Incarnation()); Put32(record + 12, id); Put32(record + 16, revision); Put32(record + 20, static_cast<uint32_t>(length));
    pb_ostream_t stream = pb_ostream_from_buffer(record + kRecordHeaderSize, length);
    if (!pb_encode(&stream, UltimateProfile_fields, &profile) || stream.bytes_written != length) {
        _last_io_stage = ProfileStoreIoStage::RecordEncode;
        return false;
    }
    Put32(record + 24, Crc32(record, 24)); Put32(record + 28, Crc32(record + kRecordHeaderSize, length));
    char path[64], temporary[72]; RecordPath(path, sizeof(path), id, revision); std::snprintf(temporary, sizeof(temporary), "%s.tmp", path);
    const RecordCommitContext expected{Incarnation(), id, revision};
    return ProfileStoreAtomicCommit::ReplaceVerifiedFile(*_storage, temporary, path, record,
            kRecordHeaderSize + length, VerifyRecordCommit, const_cast<RecordCommitContext *>(&expected),
            &_last_io_stage);
}
void ProfileStore::ResetDiagnostic() { _last_io_stage = ProfileStoreIoStage::None; }
const char *ProfileStore::LastDiagnostic() const { return ProfileStoreIoDiagnostic(_last_io_stage); }
bool ProfileStore::ReadProfile(uint32_t id, uint32_t revision, UltimateProfile &into) const {
    char path[64]; RecordPath(path, sizeof(path), id, revision);
    const size_t wire_size = _storage->Size(path);
    static uint8_t wire[kMaxRecordWireBytes];
    if (wire_size < kRecordHeaderSize || wire_size > sizeof(wire) || !_storage->Read(path, wire, wire_size)) return false;
    uint8_t *header = wire;
    if (Get32(header) != kRecordMagic || Get16(header + 4) != kEnvelopeVersion || Get16(header + 6) != kPayloadUltimateProfile || Get32(header + 8) != Incarnation() || Get32(header + 12) != id || Get32(header + 16) != revision || Get32(header + 20) > kMaxProfileWireBytes || Get32(header + 24) != Crc32(header, 24)) return false;
    const size_t length = Get32(header + 20); if (wire_size != kRecordHeaderSize + length || Get32(header + 28) != Crc32(wire + kRecordHeaderSize, length)) return false;
    into = UltimateProfile_init_default; pb_istream_t stream{}; stream.callback = [](pb_istream_t *s, pb_byte_t *buffer, size_t count) { const auto *state = static_cast<const uint8_t *>(s->state); if (count > s->bytes_left) return false; std::memcpy(buffer, state, count); s->state = const_cast<uint8_t *>(state + count); return true; }; stream.state = wire + kRecordHeaderSize; stream.bytes_left = length;
    return pb_decode(&stream, UltimateProfile_fields, &into) && stream.bytes_left == 0 && ValidateProfile(into);
}

const UltimateProfile *ProfileStore::Activate(uint32_t id, Status *status) {
    if (id == 0) { _active_id = 0; if (status) *status = Status::Ok; return nullptr; }
    const int index = Find(id);
    if (!_ready || index < 0) { if (status) *status = Status::NotFound; return nullptr; }
    bool recovered = false;
    if (!ReadProfile(id, _directory->entries[index].revision, _candidate_profile)) {
        const uint32_t previous = _directory->entries[index].previous_revision;
        if (previous == 0 || !ReadProfile(id, previous, _candidate_profile)) { if (status) *status = Status::Invalid; return nullptr; }
        recovered = true;
    }
    _active_profile = _candidate_profile; _active_id = id; if (status) *status = recovered ? Status::RecoveredPrevious : Status::Ok; return &_active_profile;
}

ProfileStore::TransactionResult ProfileStore::BeginMutation(uint32_t token, uint32_t digest) const {
    if (!_ready) return {Status::IoFailure};
    if (_read_only_recovery || _directory->migration_state == 1) return {Status::MigrationFenced};
    if (_directory->last_token == token && token != 0) return _directory->last_digest == digest ? _directory->last_result : TransactionResult{Status::Conflict};
    return {Status::Ok};
}
void ProfileStore::Finish(TransactionResult *result, uint32_t id, uint32_t revision) const { result->id = id; result->revision = revision; result->generation = _directory ? _directory->generation + 1 : 0; }

ProfileStore::TransactionResult ProfileStore::Create(const UltimateProfile &profile, const char *name, uint32_t rank, uint32_t token, uint32_t digest) {
    auto result = BeginMutation(token, digest); if (result.status != Status::Ok) return result; if (_directory->count == kMaxEntries || _directory->high_water_id == UINT32_MAX || !ValidateProfile(profile)) return { _directory->count == kMaxEntries ? Status::Full : Status::Invalid };
    const uint32_t id = _directory->high_water_id + 1, revision = 1; if (!WriteProfile(id, revision, profile)) return {Status::IoFailure}; static Directory next; next = *_directory; auto &entry = next.entries[next.count++]; entry.id = id; entry.revision = revision; entry.payload_version = kEnvelopeVersion; entry.rank = rank; if (name) std::strncpy(entry.name, name, sizeof(entry.name) - 1); next.high_water_id = id; next.generation++; next.last_token = token; next.last_digest = digest; Finish(&result, id, revision); next.last_result = result; return PublishDirectory(next) ? result : TransactionResult{Status::UnknownOutcome, id, revision, next.generation};
}
ProfileStore::TransactionResult ProfileStore::Update(uint32_t id, const UltimateProfile &profile, uint32_t expected_revision, uint32_t token, uint32_t digest) {
    auto result = BeginMutation(token, digest); const int index = Find(id); if (result.status != Status::Ok) return result; if (index < 0) return {Status::NotFound}; if (_directory->entries[index].revision != expected_revision || !ValidateProfile(profile)) return {Status::Conflict}; const uint32_t revision = expected_revision + 1; if (!WriteProfile(id, revision, profile)) return {Status::IoFailure}; static Directory next; next = *_directory; next.entries[index].previous_revision = expected_revision; next.entries[index].revision = revision; next.generation++; next.last_token = token; next.last_digest = digest; Finish(&result, id, revision); next.last_result = result; return PublishDirectory(next) ? result : TransactionResult{Status::UnknownOutcome, id, revision, next.generation};
}
ProfileStore::TransactionResult ProfileStore::Duplicate(uint32_t id, uint32_t expected_revision, const char *name,
                                                         uint32_t rank, uint32_t token, uint32_t digest) {
    const auto mutation = BeginMutation(token, digest);
    if (mutation.status != Status::Ok) return mutation;
    const int index = Find(id);
    if (index < 0) return {Status::NotFound};
    if (_directory->entries[index].revision != expected_revision) return {Status::Conflict};
    UltimateProfile profile = UltimateProfile_init_default;
    if (!ReadProfile(id, expected_revision, profile)) return {Status::Invalid};
    return Create(profile, name, rank, token, digest);
}
ProfileStore::TransactionResult ProfileStore::Rename(uint32_t id, const char *name, uint32_t generation, uint32_t token, uint32_t digest) {
    auto result = BeginMutation(token, digest); const int index = Find(id); if (result.status != Status::Ok) return result; if (index < 0) return {Status::NotFound}; if (_directory->generation != generation || name == nullptr) return {Status::Conflict}; static Directory next; next = *_directory; std::memset(next.entries[index].name, 0, kNameCapacity); std::strncpy(next.entries[index].name, name, kNameCapacity - 1); next.generation++; next.last_token = token; next.last_digest = digest; Finish(&result, id, next.entries[index].revision); next.last_result = result; return PublishDirectory(next) ? result : TransactionResult{Status::UnknownOutcome, id, next.entries[index].revision, next.generation};
}
ProfileStore::TransactionResult ProfileStore::Reorder(uint32_t id, uint32_t rank, uint32_t generation, uint32_t token, uint32_t digest) { auto result = BeginMutation(token, digest); const int index = Find(id); if (result.status != Status::Ok) return result; if (index < 0) return {Status::NotFound}; if (_directory->generation != generation) return {Status::Conflict}; static Directory next; next = *_directory; next.entries[index].rank = rank; next.generation++; next.last_token = token; next.last_digest = digest; Finish(&result, id, next.entries[index].revision); next.last_result = result; return PublishDirectory(next) ? result : TransactionResult{Status::UnknownOutcome, id, next.entries[index].revision, next.generation}; }
ProfileStore::TransactionResult ProfileStore::Delete(uint32_t id, uint32_t generation, uint32_t referenced_id, uint32_t token, uint32_t digest) { auto result = BeginMutation(token, digest); const int index = Find(id); if (result.status != Status::Ok) return result; if (index < 0) return {Status::NotFound}; if (_directory->generation != generation) return {Status::Conflict}; if (id == referenced_id || id == _active_id) return {Status::Referenced}; static Directory next; next = *_directory; for (size_t i = index + 1; i < next.count; ++i) next.entries[i - 1] = next.entries[i]; --next.count; next.generation++; next.last_token = token; next.last_digest = digest; Finish(&result, id, 0); next.last_result = result; return PublishDirectory(next) ? result : TransactionResult{Status::UnknownOutcome, id, 0, next.generation}; }
ProfileStore::TransactionResult ProfileStore::QueryTransaction(uint32_t token, uint32_t digest) const { if (!_directory || _directory->last_token != token || _directory->last_digest != digest) return {Status::NotFound}; return _directory->last_result; }
ProfileStore::Status ProfileStore::ImportLegacy(const Config &legacy, uint32_t *mapping, size_t capacity) { if (!_ready || _read_only_recovery) return Status::ReadOnlyRecovery; if (legacy.ultimate_profiles_count > capacity || legacy.ultimate_profiles_count > 2) return Status::Invalid; if (_directory->migration_state == 1) { for (size_t i = 0; i < legacy.ultimate_profiles_count; ++i) mapping[i] = _directory->migration_ids[i]; return Status::MigrationFenced; } if (_directory->migration_state != 0) return Status::MigrationFenced; static Directory next; next = *_directory; for (size_t i = 0; i < legacy.ultimate_profiles_count; ++i) { if (!ValidateProfile(legacy.ultimate_profiles[i])) return Status::Invalid; const uint32_t id = next.high_water_id + 1; if (!WriteProfile(id, 1, legacy.ultimate_profiles[i])) return Status::IoFailure; auto &entry = next.entries[next.count++]; entry.id = id; entry.revision = 1; entry.payload_version = kEnvelopeVersion; entry.rank = i; std::snprintf(entry.name, sizeof(entry.name), "Migrated %lu", static_cast<unsigned long>(i + 1)); next.high_water_id = id; next.migration_ids[i] = id; mapping[i] = id; } next.migration_state = 1; next.migration_digest = Crc32(reinterpret_cast<const uint8_t *>(&legacy), sizeof(legacy)); ++next.generation; return PublishDirectory(next) ? Status::Ok : Status::UnknownOutcome; }
ProfileStore::Status ProfileStore::CompleteMigration(const Config &compact) { if (!_ready || _directory->migration_state != 1 || compact.ultimate_profile_store_format != kCompactConfigFormat || compact.ultimate_profile_store_incarnation != Incarnation()) return Status::Invalid; static Directory next; next = *_directory; next.migration_state = 2; ++next.generation; return PublishDirectory(next) ? Status::Ok : Status::UnknownOutcome; }

ProfileStore profile_store;
