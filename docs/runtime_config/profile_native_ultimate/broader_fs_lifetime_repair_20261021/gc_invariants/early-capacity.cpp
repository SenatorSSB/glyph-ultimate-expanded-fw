#include "core/ProfileStoreReadTrace.hpp"
#include "core/ProfileStore.hpp"

#include "config_rgb_target_domain.hpp"
#include "core/ConfigWriteCandidate.hpp"
#include "core/ProfileStoreAtomicCommit.hpp"
#include "core/ProfileStoreName.hpp"
#include "core/ProfileStorePaths.hpp"
#include "core/Sha256.hpp"
#include "core/config_validation.hpp"

#include <climits>
#include <cstdio>
#include <cstring>
#include <new>
#include <initializer_list>
#include <pb_decode.h>
#include <pb_encode.h>

namespace {
    constexpr uint32_t kDirectoryMagic = 0x31534450u, kRootMagic = 0x32534450u,
                       kControlMagic = 0x32435350u, kRecordMagic = 0x31525055u;
    constexpr size_t kLegacyDirectoryBytes = 2620, kRootHeader = 320, kEntryBytes = 56;
    constexpr size_t kDirectoryWireBytes = kRootHeader + 64 * kEntryBytes + 4;
    constexpr size_t kMaxProfileWireBytes = 4096, kMaxRecordWireBytes = 4128;
    constexpr const char *kControl = "/ultimate-v2.ctrl", *kControlTemp = "/ultimate-v2.ctmp";
    constexpr uint64_t kReserve = 16384;

    bool duplicate_prepared = false;

    // One synchronous Create call owns these borrowed inputs. They are reset
    // at entry and cleared on every exit; no callback/reentrant store exists.
    struct PreparedCreate {
        const UltimateProfile *profile;
        const char *input_name;
        uint32_t id, rank, schema;
        size_t bytes;
        char name[ProfileStore::kNameCapacity];
        ProfileStore::TransactionIdentity identity;
        ProfileStore::TransactionResult result;
        bool ready;
    };
    PreparedCreate prepared_create{};

    struct PreparedRecordWrite {
        uint8_t record[kMaxRecordWireBytes]; size_t n; pb_ostream_t stream;
        char path[32], temp[32];
    };
    PreparedRecordWrite prepared_record{};

    uint32_t Crc32(const uint8_t *p, size_t n) {
        uint32_t c = ~0u;
        while (n--) {
            c ^= *p++;
            for (unsigned j = 0; j < 8; ++j)
                c = (c >> 1) ^ (0xedb88320u & (0u - (c & 1)));
        }
        return ~c;
    }

    void Put16(uint8_t *p, uint16_t v) {
        p[0] = v;
        p[1] = v >> 8;
    }

    void Put32(uint8_t *p, uint32_t v) {
        for (unsigned i = 0; i < 4; ++i)
            p[i] = v >> (8 * i);
    }

    void Put64(uint8_t *p, uint64_t v) {
        for (unsigned i = 0; i < 8; ++i)
            p[i] = v >> (8 * i);
    }

    uint16_t Get16(const uint8_t *p) {
        return p[0] | uint16_t(p[1]) << 8;
    }

    uint32_t Get32(const uint8_t *p) {
        uint32_t v = 0;
        for (unsigned i = 0; i < 4; ++i)
            v |= uint32_t(p[i]) << (8 * i);
        return v;
    }

    uint64_t Get64(const uint8_t *p) {
        uint64_t v = 0;
        for (unsigned i = 0; i < 8; ++i)
            v |= uint64_t(p[i]) << (8 * i);
        return v;
    }

    void RootPath(char *p, size_t n, unsigned slot) {
        std::snprintf(p, n, "/ultimate-v2-%u.bin", slot);
    }

    void RootTemp(char *p, size_t n, unsigned slot) {
        std::snprintf(p, n, "/ultimate-v2-%u.tmp", slot);
    }

    __attribute__((noinline)) bool HashMessage(const pb_msgdesc_t *fields, const void *message, uint8_t out[32]) {
        Sha256 hash;
        pb_ostream_t stream{};
        stream.callback = [](pb_ostream_t *s, const pb_byte_t *b, size_t n) {
            static_cast<Sha256 *>(s->state)->Update(b, n);
            return true;
        };
        stream.state = &hash;
        stream.max_size = SIZE_MAX;
        if (!pb_encode(&stream, fields, message))
            return false;
        hash.Final(out);
        return true;
    }

    bool ValidName(const char *p) {
        return ProfileStoreNameValid(p, 33);
    }

    uint64_t Round(uint64_t n, uint32_t b) {
        return b ? ((n + b - 1) / b) * b : UINT64_MAX;
    }

    // CTZ data blocks contain pointers. Charge one additional pointer per block
    // plus an entire extra block, so record accounting never assumes inline data.
    uint64_t FileCharge(uint64_t n, uint32_t b) {
        return Round(n + 4 * ((n + b - 1) / b + 1), b);
    }

    using Outcome = CheckedStorage::Outcome;
    using Kind = CheckedStorage::Kind;
    using Result = CheckedStorage::Result;

    class MountedStorage final : public ProfileStoreStorage {
      public:
        bool Write(const char *p, const uint8_t *b, size_t n) override {
            return bool(CheckedWrite(p, b, n, Kind::Record));
        }

        bool Read(const char *p, uint8_t *b, size_t n) override {
            return bool(CheckedRead(p, b, n, Kind::Record));
        }

        size_t Size(const char *p) override {
            size_t n = 0;
            return Probe(p, &n) ? n : 0;
        }

        bool Exists(const char *p) override { return bool(Probe(p)); }

        bool Remove(const char *p) override { return bool(CheckedRemove(p)); }

        bool Rename(const char *a, const char *b) override {
            return bool(CheckedRename(a, b, Kind::Record));
        }

        Result CheckedWrite(const char *p, const uint8_t *b, size_t n, Kind k) override {
            // Same checked WriteFile sequence, with one fixed handle instead
            // of retaining its native lfs_file_t on every nested write frame.
            // The existing store/record/publication workspaces are synchronous
            // core0-only; no callback recursively enters a store operation.
            static CheckedStorage::File file;
            static Result r; ::new (&r) Result(CheckedStorage::Open(file, p, true, k));
            if (r) {
                ::new (&r) Result(CheckedStorage::Write(file, b, n));
                if (r) ::new (&r) Result(CheckedStorage::Sync(file));
                static Result close; ::new (&close) Result(CheckedStorage::Close(file)); if (!close) r = close;
            }
            Remember(r, true, n);
            return r;
        }

        Result CheckedRead(const char *p, uint8_t *b, size_t n, Kind k) override {
            auto r = CheckedStorage::ReadFile(p, b, n, k);
            Remember(r, false, n);
            return r;
        }

        ProfileStoreStorageFailure LastFailure() const override { return _last_failure; }

        Result Probe(const char *p, size_t *n = nullptr) override {
            return CheckedStorage::Stat(p, n);
        }

        Result CheckedRename(const char *a, const char *b, Kind k) override {
            return CheckedStorage::Rename(a, b, k);
        }

        Result CheckedRemove(const char *p) override { return CheckedStorage::Remove(p); }

        bool ReadRange(const char *p, size_t offset, uint8_t *b, size_t n) override {
            CheckedStorage::File f;
            if (!CheckedStorage::Open(f, p, false, Kind::Record))
                return false;
            bool ok = bool(CheckedStorage::Seek(f, offset));
            if (ok) {
                const auto read = CheckedStorage::Read(f, b, n);
                ok = bool(read) && read.bytes == n;
            }
            auto closed = CheckedStorage::Close(f);
            return ok && bool(closed);
        }

        bool Geometry(CheckedStorage::Geometry &g) override {
            return bool(CheckedStorage::Capacity(g));
        }

        bool Enumerate(CheckedStorage::Visitor v, void *c) override {
            return bool(CheckedStorage::Enumerate("/", v, c));
        }

      private:
        ProfileStoreStorageFailure _last_failure = ProfileStoreStorageFailure::None;

        void Remember(const Result &r, bool write, size_t expected) {
            _last_failure = ProfileStoreStorageFailure::None;
            if (r)
                return;
            switch (r.operation) {
                case CheckedStorage::Operation::OpenWrite:
                    _last_failure = ProfileStoreStorageFailure::TempOpenWrite;
                    break;
                case CheckedStorage::Operation::OpenRead:
                case CheckedStorage::Operation::Read:
                    _last_failure = ProfileStoreStorageFailure::TempRead;
                    break;
                case CheckedStorage::Operation::Stat:
                    _last_failure = ProfileStoreStorageFailure::TempSize;
                    break;
                case CheckedStorage::Operation::Sync:
                    _last_failure = ProfileStoreStorageFailure::TempSync;
                    break;
                case CheckedStorage::Operation::Close:
                    _last_failure = ProfileStoreStorageFailure::TempClose;
                    break;
                default:
                    _last_failure =
                        write ? ProfileStoreStorageFailure::TempWrite
                              : (r.bytes != expected ? ProfileStoreStorageFailure::TempSize
                                                     : ProfileStoreStorageFailure::TempRead);
                    break;
            }
        }
    };

    // A checked rename replaces an existing file atomically on this same mount.
    // There is deliberately no remove(destination) gap. All readback is independent.
    // Keep checked publication in its caller: a retained adapter frame would
    // consume stack throughout LittleFS metadata compaction. Semantics stay
    // in this single shared implementation.
    struct PreparedPublication {
        ProfileStoreStorage *storage;
        const char *tmp, *dest;
        const uint8_t *bytes;
        size_t length;
        Kind kind;
        ProfileStoreIoStage *stage;
    };
    PreparedPublication publishing{};
    __attribute__((always_inline)) inline Result Publish(
        ProfileStoreStorage &s,
        const char *tmp,
        const char *dest,
        const uint8_t *b,
        size_t n,
        Kind k,
        ProfileStoreIoStage *stage
    ) {
        publishing = {&s, tmp, dest, b, n, k, stage};
        static uint8_t readback[kMaxRecordWireBytes];
        if (publishing.stage)
            *publishing.stage = ProfileStoreIoStage::None;
        if (publishing.length > sizeof(readback)) {
            std::memset(&publishing, 0, sizeof(publishing));
            return { Outcome::Failed, 0, 0 };
        }
        const auto publication = publishing.kind == Kind::Root ? ProfileStorePublicationKind::Directory
                                                 : ProfileStorePublicationKind::Record;
        // C++17 constructs returned PODs directly in fixed scratch. Publication
        // inputs are reset each call and cleared on every exit. No callback
        // recursively enters the synchronous core0 store/publication path.
        static Result r;
        ::new (&r) Result(publishing.storage->CheckedWrite(publishing.tmp, publishing.bytes, publishing.length, publishing.kind));
        if (!r) {
            if (publishing.stage) {
                *publishing.stage = ProfileStoreStage(publication, publishing.storage->LastFailure());
                if (*publishing.stage == ProfileStoreIoStage::None)
                    *publishing.stage = ProfileStoreStage(publication, ProfileStoreIoStage::RecordTempWrite);
            }
            std::memset(&publishing, 0, sizeof(publishing));
            return r;
        }
        ::new (&r) Result(publishing.storage->CheckedRead(publishing.tmp, readback, publishing.length, publishing.kind));
        if (!r) {
            if (publishing.stage) {
                *publishing.stage = ProfileStoreStage(publication, publishing.storage->LastFailure());
                if (*publishing.stage == ProfileStoreIoStage::None)
                    *publishing.stage = publication == ProfileStorePublicationKind::Directory
                                 ? ProfileStoreIoStage::DirectoryTempRead
                                 : ProfileStoreIoStage::RecordTempRead;
            }
            std::memset(&publishing, 0, sizeof(publishing));
            return r;
        }
        if (std::memcmp(publishing.bytes, readback, publishing.length) != 0) {
            if (publishing.stage)
                *publishing.stage = ProfileStoreStage(publication, ProfileStoreIoStage::RecordVerify);
            std::memset(&publishing, 0, sizeof(publishing));
            return { Outcome::Failed, 0, 0 };
        }
        ::new (&r) Result(publishing.storage->CheckedRename(publishing.tmp, publishing.dest, publishing.kind));
        if (!r && publishing.stage)
            *publishing.stage = ProfileStoreStage(
                publishing.kind == Kind::Root ? ProfileStorePublicationKind::Directory
                                : ProfileStorePublicationKind::Record,
                ProfileStoreIoStage::RecordRename
            );
        std::memset(&publishing, 0, sizeof(publishing));
        return r;
    }
}

struct ProfileStore::Directory {
    uint32_t generation = 0, incarnation = 0, high_water_id = 0;
    uint32_t migration_state = 0, migration_version = 0, migration_count = 0;
    uint8_t migration_source[32]{}, migration_payloads[2][32]{}, migration_receipt[32]{},
        compact_digest[32]{};
    uint32_t migration_ids[2]{}, migration_revisions[2]{};
    TransactionIdentity last_identity{};
    TransactionResult last_result{};
    size_t count = 0;
    Entry entries[kMaxEntries]{};
};

namespace {
    void Receipt(ProfileStore::Directory &);

    // Reset in place: assigning Directory{} materializes a roughly 4 KiB automatic
    // temporary on the pinned ARM compiler. Preserve the sole nonzero default.
    void ClearDirectory(ProfileStore::Directory &directory) {
        std::memset(static_cast<void *>(&directory), 0, sizeof(directory));
        directory.last_result.status = ProfileStore::Status::NotFound;
    }

    ProfileStore::Directory *Workspace() {
        static ProfileStore::Directory directories[3];
        return directories;
    }

    bool Structural(const ProfileStore::Directory &d) {
        if (!d.incarnation || d.count > 64 || d.migration_state > 2 || d.migration_count > 2)
            return false;
        for (size_t i = 0; i < d.count; ++i) {
            const auto &e = d.entries[i];
            if (!e.id || !e.revision || e.id > d.high_water_id || !ValidName(e.name) ||
                e.previous_revision >= e.revision)
                return false;
            for (size_t j = 0; j < i; ++j)
                if (d.entries[j].id == e.id)
                    return false;
        }
        if (d.migration_state &&
            ((d.migration_version != 2 && d.migration_version != 3) || !d.migration_count))
            return false;
        for (size_t i = 0; i < d.migration_count; ++i)
            if (!d.migration_ids[i] || !d.migration_revisions[i] ||
                d.migration_ids[i] > d.high_water_id)
                return false;
        return true;
    }

    bool EncodeDirectory(const ProfileStore::Directory &d, uint8_t *wire) {
        if (!Structural(d))
            return false;
        std::memset(wire, 0, kDirectoryWireBytes);
        Put32(wire, kRootMagic);
        Put16(wire + 4, 2);
        Put16(wire + 6, d.count);
        Put32(wire + 8, d.generation);
        Put32(wire + 12, d.incarnation);
        Put32(wire + 16, d.high_water_id);
        Put32(wire + 20, d.migration_state);
        Put64(wire + 24, d.last_identity.token);
        std::memcpy(wire + 32, d.last_identity.digest, 32);
        Put32(wire + 64, static_cast<uint32_t>(d.last_result.status));
        Put32(wire + 68, d.last_result.id);
        Put32(wire + 72, d.last_result.revision);
        Put32(wire + 76, d.last_result.generation);
        Put32(wire + 80, d.migration_version);
        Put32(wire + 84, d.migration_count);
        std::memcpy(wire + 88, d.migration_source, 32);
        for (unsigned i = 0; i < 2; ++i) {
            Put32(wire + 120 + i * 4, d.migration_ids[i]);
            Put32(wire + 128 + i * 4, d.migration_revisions[i]);
            std::memcpy(wire + 136 + i * 32, d.migration_payloads[i], 32);
        }
        std::memcpy(wire + 200, d.migration_receipt, 32);
        std::memcpy(wire + 232, d.compact_digest, 32);
        for (size_t i = 0; i < d.count; ++i) {
            auto *p = wire + kRootHeader + i * kEntryBytes;
            const auto &e = d.entries[i];
            Put32(p, e.id);
            Put32(p + 4, e.revision);
            Put32(p + 8, e.previous_revision);
            Put32(p + 12, e.payload_version);
            Put32(p + 16, e.rank);
            std::memcpy(p + 20, e.name, 33);
        }
        Put32(wire + kDirectoryWireBytes - 4, Crc32(wire, kDirectoryWireBytes - 4));
        return true;
    }

    bool DecodeDirectory(const uint8_t *wire, size_t length, ProfileStore::Directory *d) {
        if (length != kDirectoryWireBytes || Get32(wire) != kRootMagic || Get16(wire + 4) != 2 ||
            Get16(wire + 6) > 64 || Get32(wire + length - 4) != Crc32(wire, length - 4))
            return false;
        ClearDirectory(*d);
        d->count = Get16(wire + 6);
        d->generation = Get32(wire + 8);
        d->incarnation = Get32(wire + 12);
        d->high_water_id = Get32(wire + 16);
        d->migration_state = Get32(wire + 20);
        d->last_identity.token = Get64(wire + 24);
        std::memcpy(d->last_identity.digest, wire + 32, 32);
        d->last_result = { static_cast<ProfileStore::Status>(Get32(wire + 64)),
                           Get32(wire + 68),
                           Get32(wire + 72),
                           Get32(wire + 76) };
        if (Get32(wire + 64) > static_cast<uint32_t>(ProfileStore::Status::Aborted))
            return false;
        d->migration_version = Get32(wire + 80);
        d->migration_count = Get32(wire + 84);
        std::memcpy(d->migration_source, wire + 88, 32);
        for (unsigned i = 0; i < 2; ++i) {
            d->migration_ids[i] = Get32(wire + 120 + i * 4);
            d->migration_revisions[i] = Get32(wire + 128 + i * 4);
            std::memcpy(d->migration_payloads[i], wire + 136 + i * 32, 32);
        }
        std::memcpy(d->migration_receipt, wire + 200, 32);
        std::memcpy(d->compact_digest, wire + 232, 32);
        for (size_t i = 0; i < d->count; ++i) {
            const auto *p = wire + kRootHeader + i * kEntryBytes;
            auto &e = d->entries[i];
            e.id = Get32(p);
            e.revision = Get32(p + 4);
            e.previous_revision = Get32(p + 8);
            e.payload_version = Get32(p + 12);
            e.rank = Get32(p + 16);
            std::memcpy(e.name, p + 20, 33);
        }
        return Structural(*d);
    }

    // The deployed f7ba root reader remains explicit. Upgrade never reinterprets it
    // as v2 and never reconstructs identity from orphan filenames.
    __attribute__((noinline)) bool DecodeLegacy(const uint8_t *w, size_t n, ProfileStore::Directory *d) {
        constexpr size_t trailer = 2592;
        if (n != kLegacyDirectoryBytes || Get32(w) != kDirectoryMagic || Get16(w + 4) != 1 ||
            Get16(w + 6) > 64 || Get32(w + trailer + 24) != Crc32(w, trailer + 24))
            return false;
        ClearDirectory(*d);
        d->count = Get16(w + 6);
        d->generation = Get32(w + 8);
        d->incarnation = Get32(w + 12);
        d->high_water_id = Get32(w + 16);
        // Completed old receipts are retained as dependencies during upgrade. A pending
        // unauthenticated v1 migration cannot be silently blessed as authenticated v2.
        if (Get32(w + 24) > 2)
            return false;
        d->migration_count = 0;
        if (Get32(w + 24) != 0) {
            d->migration_state = Get32(w + 24);
            d->migration_version = 3;
            for (unsigned i = 0; i < 2; ++i) {
                uint32_t id = Get32(w + trailer + 16 + i * 4);
                if (id) {
                    d->migration_ids[d->migration_count] = id;
                    d->migration_revisions[d->migration_count++] = 1;
                }
            }
            Sha256 hash;
            hash.Update(w, n);
            hash.Final(d->migration_source);
        }

        for (size_t i = 0; i < d->count; ++i) {
            const auto *p = w + 32 + i * 40;
            auto &e = d->entries[i];
            e.id = Get32(p);
            e.revision = Get32(p + 4);
            e.previous_revision = Get32(p + 8);
            e.payload_version = Get32(p + 12);
            e.rank = Get32(p + 16);
            std::memcpy(e.name, p + 20, 18);
            e.name[17] = 0;
        }
        return d->generation != 0 && Structural(*d);
    }

    bool SameDirectory(const ProfileStore::Directory &a, const ProfileStore::Directory &b) {
        // Both objects are value-initialized; compare portable serialization, not ABI padding.
        static uint8_t wire[kDirectoryWireBytes];
        uint8_t first[32], second[32];
        if (!EncodeDirectory(a, wire))
            return false;
        Sha256 h1;
        h1.Update(wire, sizeof(wire));
        h1.Final(first);
        if (!EncodeDirectory(b, wire))
            return false;
        Sha256 h2;
        h2.Update(wire, sizeof(wire));
        h2.Final(second);
        return std::memcmp(first, second, 32) == 0;
    }
}

ProfileStore::ProfileStore(ProfileStoreStorage *s) : _storage(s) {}

bool ProfileStore::Begin(uint32_t expected, uint32_t required_root_format) {
    static MountedStorage storage;
    Directory *work = Workspace();
    if (!_storage)
        _storage = &storage;
    _directory = &work[0];
    _next = &work[1];
    _other = &work[2];
    ClearDirectory(*_directory);
    ClearDirectory(*_next);
    ClearDirectory(*_other);
    _expected_incarnation = expected;
    _required_root_format = required_root_format;
    _ready = false;
    _root_invalid = false;
    _v2 = false;
    _uncertain = false;
    _read_only_recovery = false;
    _recovery_only = false;
    _protected_ready = false;
    _active_id = 0;
    _active_revision = 0;
    _active_native.view.valid = false; _active_native_lease.Release();
    return Bootstrap(false);
}

bool ProfileStore::BeginRecovery(uint32_t expected, uint32_t required_root_format) {
    static MountedStorage storage;
    Directory *work = Workspace();
    if (!_storage)
        _storage = &storage;
    _directory = &work[0];
    _next = &work[1];
    _other = &work[2];
    ClearDirectory(*_directory);
    ClearDirectory(*_next);
    ClearDirectory(*_other);
    _expected_incarnation = expected;
    _required_root_format = required_root_format;
    _ready = false;
    _root_invalid = false;
    _v2 = false;
    _uncertain = false;
    _read_only_recovery = true;
    _recovery_only = true;
    _protected_ready = false;
    _active_id = 0;
    _active_revision = 0;
    _active_native.view.valid = false; _active_native_lease.Release();
    return Bootstrap(true);
}

bool ProfileStore::ReadRoot(uint8_t slot, Directory &d) const {
    char p[32];
    RootPath(p, sizeof(p), slot);
    static uint8_t wire[kDirectoryWireBytes];
    return _storage->CheckedRead(p, wire, sizeof(wire), Kind::Root) &&
           DecodeDirectory(wire, sizeof(wire), &d);
}

bool ProfileStore::LoadControl(Directory &seed, uint32_t &phase) const {
    static uint8_t wire[kDirectoryWireBytes + 16];
    if (!_storage->CheckedRead(kControl, wire, sizeof(wire), Kind::Root) ||
        Get32(wire) != kControlMagic ||
        Get32(wire + 12) != (Crc32(wire, 12) ^ Crc32(wire + 16, kDirectoryWireBytes)))
        return false;
    phase = Get32(wire + 4);
    return (phase == 1 || phase == 2 || phase == 3) && Get32(wire + 8) == kDirectoryWireBytes &&
           DecodeDirectory(wire + 16, kDirectoryWireBytes, &seed);
}

// Share the control publication body while ending its preparation phases
// inside each synchronous caller; no retained control adapter frame.
__attribute__((always_inline)) inline bool ProfileStore::WriteControl(const Directory &seed, uint32_t phase) {
    static uint8_t wire[kDirectoryWireBytes + 16];
    if (!EncodeDirectory(seed, wire + 16))
        return false;
    Put32(wire, kControlMagic);
    Put32(wire + 4, phase);
    Put32(wire + 8, kDirectoryWireBytes);
    Put32(wire + 12, Crc32(wire, 12) ^ Crc32(wire + 16, kDirectoryWireBytes));
    static Result r; ::new (&r) Result(
        Publish(*_storage, kControlTemp, kControl, wire, sizeof(wire), Kind::Root, &_last_io_stage));
    if (r.outcome == Outcome::Uncertain)
        _uncertain = true;
    return bool(r);
}

// Keep bootstrap publication in its owning Begin frame; decode/hash helpers
// above remain separate so their scratch ends before any filesystem write.
__attribute__((always_inline)) inline bool ProfileStore::InitializeV2(const Directory &seed) {
    static CheckedStorage::Geometry geometry; geometry = {};
    if (!_storage->Geometry(geometry) || !geometry.erase_bytes ||
        geometry.free_bytes < kReserve +
                                  3 * FileCharge(kDirectoryWireBytes + 16, geometry.erase_bytes) +
                                  4ull * geometry.erase_bytes) {
        _read_only_recovery = true;
        return false;
    }
    static uint8_t wire[kDirectoryWireBytes];
    if (!EncodeDirectory(seed, wire))
        return false;
    for (unsigned slot = 0; slot < 2; ++slot) {
        static char p[32], t[32];
        RootPath(p, sizeof(p), slot);
        RootTemp(t, sizeof(t), slot);
        static Result r; ::new (&r) Result(Publish(*_storage, t, p, wire, sizeof(wire), Kind::Root, &_last_io_stage));
        if (!r) {
            _uncertain = r.outcome == Outcome::Uncertain;
            _read_only_recovery = true;
            return false;
        }
    }
    if (!WriteControl(seed, 2)) {
        _read_only_recovery = true;
        return false;
    }
    return LoadDirectory();
}

__attribute__((always_inline)) inline bool ProfileStore::Bootstrap(bool recovery) {
    if (_required_root_format > 2) {
        _root_invalid = true;
        _read_only_recovery = true;
        return false;
    }
    static CheckedStorage::Geometry g; g = {};
    if (!_storage->Geometry(g) || !g.erase_bytes || g.total_bytes < kReserve) {
        _read_only_recovery = true;
        return false;
    }
    static Result ctrl; ::new (&ctrl) Result(_storage->Probe(kControl));
    if (ctrl.outcome != Outcome::NotFound) {
        uint32_t phase = 0;
        if (!ctrl || !LoadControl(*_next, phase)) {
            _read_only_recovery = true;
            return false;
        }
        _v2 = true;
        if (_expected_incarnation && _next->incarnation != _expected_incarnation) {
            _read_only_recovery = true;
            return false;
        }
        if (phase == 1) {
            if (recovery) {
                _read_only_recovery = true;
                return false;
            }
            return InitializeV2(*_next);
        }
        if (phase == 3) {
            _uncertain = true;
            if (recovery) {
                LoadDirectory();
                _read_only_recovery = true;
                return _ready;
            }
            return ReconcileTransaction();
        }
        const uint32_t floor = _next->generation, high = _next->high_water_id,
                       inc = _next->incarnation;
        if (!LoadDirectory())
            return false;
        if (Generation() != floor || _directory->high_water_id != high || Incarnation() != inc ||
            !SameDirectory(*_directory, *_next)) {
            _root_invalid = true;
            _read_only_recovery = true;
            return _ready;
        }
        return true;
    }
    // Config independently records that v2 authority was accepted. Losing all
    // v2 files must not resurrect the retained pre-upgrade v1 roots.
    if (_required_root_format >= 2) {
        _root_invalid = true;
        _read_only_recovery = true;
        return false;
    }
    // A missing control with any v2 path is damaged, never permission to downgrade.
    for (unsigned i = 0; i < 2; ++i) {
        static char p[32];
        RootPath(p, sizeof(p), i);
        if (_storage->Probe(p).outcome != Outcome::NotFound) {
            _read_only_recovery = true;
            return false;
        }
    }
    bool exists[2]{}, valid[2]{};
    static uint8_t old[kLegacyDirectoryBytes];
    for (unsigned i = 0; i < 2; ++i) {
        static char p[32];
        ProfileStorePaths::DirectoryPath(p, sizeof(p), i);
        static Result probe; ::new (&probe) Result(_storage->Probe(p));
        exists[i] = probe.outcome != Outcome::NotFound;
        valid[i] = probe && _storage->CheckedRead(p, old, sizeof(old), Kind::Root) &&
                   DecodeLegacy(old, sizeof(old), i ? _other : _directory);
    }
    if (exists[0] || exists[1]) {
        if (!valid[0] || !valid[1]) {
            _root_invalid = true;
            if (valid[1])
                *_directory = *_other;
            _ready = valid[0] || valid[1];
            _read_only_recovery = true;
            return _ready;
        }
        if (_directory->incarnation != _other->incarnation ||
            (_directory->generation == _other->generation &&
             !SameDirectory(*_directory, *_other))) {
            _read_only_recovery = true;
            return false;
        }
        if (_other->generation > _directory->generation) {
            Directory *swap = _directory;
            _directory = _other;
            _other = swap;
        }
        if (_directory->generation - _other->generation > 1 ||
            _directory->high_water_id < _other->high_water_id) {
            _read_only_recovery = true;
            return false;
        }
        if (_expected_incarnation && Incarnation() != _expected_incarnation) {
            _read_only_recovery = true;
            return false;
        }
        _ready = true;
        if (recovery || _directory->migration_state == 1) {
            _read_only_recovery = true;
            return true;
        }
        // Preserve every existing payload; malformed dependencies stop upgrade.
        for (size_t i = 0; i < Count(); ++i) {
            const auto &e = _directory->entries[i];
            if (!ReadProfile(e.id, e.revision, _candidate_profile) ||
                (e.previous_revision &&
                 !ReadProfile(e.id, e.previous_revision, _candidate_profile))) {
                _read_only_recovery = true;
                return false;
            }
        }
        for (size_t i = 0; i < _directory->migration_count; ++i) {
            if (!ReadProfile(
                    _directory->migration_ids[i],
                    _directory->migration_revisions[i],
                    _candidate_profile
                ) ||
                !HashMessage(
                    UltimateProfile_fields,
                    &_candidate_profile,
                    _directory->migration_payloads[i]
                )) {
                _read_only_recovery = true;
                return false;
            }
        }
        if (_directory->migration_count)
            Receipt(*_directory);
    } else {
        if (_expected_incarnation || recovery) {
            _read_only_recovery = true;
            return false;
        }
        _directory->incarnation = 1;
    }
    // Reserve bootstrap/upgrade space before the first new persistent authority.
    if (g.free_bytes <
        kReserve + 4 * FileCharge(kDirectoryWireBytes + 16, g.erase_bytes) + 4ull * g.erase_bytes) {
        _read_only_recovery = true;
        return false;
    }
    *_next = *_directory;
    if (!WriteControl(*_next, 1)) {
        _read_only_recovery = true;
        return false;
    }
    _v2 = true;
    return InitializeV2(*_next);
}

bool ProfileStore::LoadDirectory() {
    bool a = ReadRoot(0, *_directory), b = ReadRoot(1, *_other);
    _protected_ready = false;
    _ready = a || b;
    _root_invalid = !a || !b;
    _read_only_recovery = _recovery_only || !a || !b;
    if (!a && !b)
        return false;
    if (!a)
        *_directory = *_other;
    if (a && b) {
        if (_directory->incarnation != _other->incarnation ||
            (_directory->generation == _other->generation &&
             !SameDirectory(*_directory, *_other))) {
            _ready = false;
            _read_only_recovery = true;
            return false;
        }
        if (_other->generation > _directory->generation) {
            Directory *swap = _directory;
            _directory = _other;
            _other = swap;
        }
        if (_directory->generation - _other->generation > 1 ||
            _directory->high_water_id < _other->high_water_id) {
            _root_invalid = true;
            _read_only_recovery = true;
        }
    }
    if (_expected_incarnation && Incarnation() != _expected_incarnation) {
        _ready = false;
        _read_only_recovery = true;
        return false;
    }
    return _ready;
}

bool ProfileStore::PublishDirectory(const Directory &next) {
    if (!_ready || _read_only_recovery || _uncertain || !_v2)
        return false;
    static uint8_t wire[kDirectoryWireBytes];
    if (!EncodeDirectory(next, wire))
        return false;
    // Persist the intended next high-water/root before publication. This one
    // format-owned control record fences rollback of an entire older root pair.
    if (!WriteControl(next, 3)) {
        _uncertain = true;
        return false;
    }
    static char p[32], t[32];
    unsigned slot = next.generation & 1u;
    RootPath(p, sizeof(p), slot);
    RootTemp(t, sizeof(t), slot);
    static Result r; ::new (&r) Result(Publish(*_storage, t, p, wire, sizeof(wire), Kind::Root, &_last_io_stage));
    if (!r) {
        _uncertain = true;
        return false;
    }
    *_directory = next;
    _protected_ready = false;
    if (!WriteControl(next, 2)) {
        _uncertain = true;
        return false;
    }
    return true;
}

bool ProfileStore::IsReady() const {
    return _ready;
}

bool ProfileStore::IsReadOnlyRecovery() const {
    return _read_only_recovery;
}

bool ProfileStore::MigrationPending() const {
    return _directory && _directory->migration_state == 1;
}

uint32_t ProfileStore::LegacyMigrationId(size_t i) const {
    return _directory && i < 2 ? _directory->migration_ids[i] : 0;
}

uint32_t ProfileStore::Incarnation() const {
    return _directory ? _directory->incarnation : 0;
}

uint32_t ProfileStore::Generation() const {
    return _directory ? _directory->generation : 0;
}

uint64_t ProfileStore::LastTransactionToken() const {
    return _directory ? _directory->last_identity.token : 0;
}

size_t ProfileStore::Count() const {
    return _directory ? _directory->count : 0;
}

const ProfileStore::Entry *ProfileStore::EntryAt(size_t i) const {
    return i < Count() ? &_directory->entries[i] : nullptr;
}

const UltimateProfile *ProfileStore::ActiveProfile() const {
    return _active_id ? &_active_profile : nullptr;
}

uint32_t ProfileStore::ActiveId() const {
    return _active_id;
}

int ProfileStore::Find(uint32_t id) const {
    for (size_t i = 0; i < Count(); ++i)
        if (_directory->entries[i].id == id)
            return static_cast<int>(i);
    return -1;
}

// End validation-error scratch before record encoding/storage begins.
__attribute__((noinline)) bool ProfileStore::ValidateProfile(const UltimateProfile &p) const {
    ConfigValidationError e;
    return validate_ultimate_profile_semantics(p, e);
}

void ProfileStore::ResetDiagnostic() {
    _last_io_stage = ProfileStoreIoStage::None;
}

const char *ProfileStore::LastDiagnostic() const {
    return ProfileStoreIoDiagnostic(_last_io_stage);
}

bool ProfileStore::IsTransactionUncertain() const {
    return _uncertain;
}

bool ProfileStore::ReconcileTransaction() {
    if (!_uncertain)
        return _ready && !_read_only_recovery;
    uint32_t phase = 0;
    if (!LoadControl(*_next, phase) || !LoadDirectory() || _read_only_recovery)
        return false;
    if (phase == 3) {
        if (Generation() == _next->generation) {
            if (!SameDirectory(*_directory, *_next))
                return false;
            if (!WriteControl(*_next, 2))
                return false;
        } else if (Generation() + 1 == _next->generation) {
            // Both checked roots prove the intended mutation did not publish. Commit
            // an identity-only checkpoint retaining its reserved high-water and
            // accepted request identity. A changed request cannot reuse an aborted
            // token. Migration maintenance has no new token and retains the prior
            // successful receipt instead of falsely marking it aborted.
            const uint32_t reserved = _next->high_water_id;
            const TransactionIdentity attempted = _next->last_identity;
            TransactionResult aborted = _next->last_result;
            const bool accepted_request = attempted.token > _directory->last_identity.token;
            *_next = *_directory;
            if (accepted_request) {
                aborted.status = Status::Aborted;
                _next->last_identity = attempted;
                _next->last_result = aborted;
            }
            if (reserved > _next->high_water_id)
                _next->high_water_id = reserved;
            ++_next->generation;
            _uncertain = false;
            if (!PublishDirectory(*_next)) {
                _uncertain = true;
                return false;
            }
        } else
            return false;
    } else if (phase != 2 || !SameDirectory(*_directory, *_next))
        return false;
    _uncertain = false;
    return true;
}

uint32_t ProfileStore::HealthFlags() const {
    return ((!_ready || _root_invalid) ? RootInvalid : 0u) | (!_v2 ? LegacyUpgradeRequired : 0u) |
           (_read_only_recovery ? ReadOnlyFlag : 0u) |
           (MigrationPending() ? MigrationFencedFlag : 0u) |
           (_uncertain ? TransactionUncertain : 0u);
}

bool ProfileStore::PrepareProfileWrite(uint32_t id, uint32_t rev, const UltimateProfile &p) {
    if (!ValidateProfile(p))
        return false;
    auto &record = prepared_record.record;
    auto &n = prepared_record.n; n=0;
    if (!pb_get_encoded_size(&n, UltimateProfile_fields, &p) || n > kMaxProfileWireBytes) {
        _last_io_stage = ProfileStoreIoStage::RecordEncodeSize;
        return false;
    }
    // Encoding is complete before Publish; this fixed workspace is distinct
    // from the immutable record bytes and READ/candidate/active owners.
    auto &s = prepared_record.stream; s = pb_ostream_from_buffer(record + 32, kMaxProfileWireBytes);
    if (!pb_encode(&s, UltimateProfile_fields, &p)) {
        _last_io_stage = ProfileStoreIoStage::RecordEncode;
        return false;
    }
    std::memset(record, 0, 32);
    Put32(record, kRecordMagic);
    Put16(record + 4, 1);
    Put16(record + 6, 1);
    Put32(record + 8, Incarnation());
    Put32(record + 12, id);
    Put32(record + 16, rev);
    Put32(record + 20, n);
    Put32(record + 24, Crc32(record, 24));
    Put32(record + 28, Crc32(record + 32, n));
    auto &path = prepared_record.path; auto &temp = prepared_record.temp;
    ProfileStorePaths::RecordPath(path, sizeof(path), id, rev);
    ProfileStorePaths::RecordTemporaryPath(temp, sizeof(temp), id, rev);
    return true;
}

bool ProfileStore::PublishPreparedProfile() {
    auto &record = prepared_record.record;
    auto &n = prepared_record.n;
    auto &path = prepared_record.path; auto &temp = prepared_record.temp;
    static Result result; ::new (&result) Result(Publish(*_storage, temp, path, record, n + 32, Kind::Record, &_last_io_stage));
    if (result.outcome == Outcome::Uncertain)
        _uncertain = true;
    return bool(result);
}

bool ProfileStore::ReadProfile(
    uint32_t id,
    uint32_t rev,
    UltimateProfile &out,
    bool *unsupported
) const {
    if (unsupported)
        *unsupported = false;
    char path[32];
    ProfileStorePaths::RecordPath(path, sizeof(path), id, rev);
    size_t n = 0;
    static uint8_t wire[kMaxRecordWireBytes];
    static ultimate_native::PayloadLease read_lease;
    read_lease.Release(); // invalidate the prior read before reusing its wire
    if (!ProfileStoreReadTrace::Mark(10) || !_storage->Probe(path, &n) ||
        !ProfileStoreReadTrace::Mark(11, n) || n < 32 || n > sizeof(wire) ||
        !ProfileStoreReadTrace::Mark(12) || !_storage->CheckedRead(path, wire, n, Kind::Record) ||
        ProfileStoreReadTrace::Failed())
        return false;
    if (Get32(wire) != kRecordMagic || Get32(wire + 8) != Incarnation() || Get32(wire + 12) != id ||
        Get32(wire + 16) != rev || Get32(wire + 20) != n - 32 ||
        Get32(wire + 24) != Crc32(wire, 24) || Get32(wire + 28) != Crc32(wire + 32, n - 32))
        return false;
    if (!ProfileStoreReadTrace::Mark(16)) return false;
    if (Get16(wire + 4) != 1 || Get16(wire + 6) != 1) {
        if (unsupported)
            *unsupported = true;
        return false;
    }
    out = UltimateProfile_init_default;
    if (!ultimate_native::DecodeProfile(wire + 32, n - 32, out, read_lease))
        return false;
    if (!ProfileStoreReadTrace::Mark(17)) return false;
    if ((out.schema_version < 1 || out.schema_version > 3) && out.schema_version != ultimate_native::kSchema) {
        if (unsupported)
            *unsupported = true;
        return false;
    }
    const bool valid = ValidateProfile(out);
    return ProfileStoreReadTrace::Mark(18, valid) && valid;
}

ProfileStore::Status ProfileStore::Read(uint32_t id, UltimateProfile &out, uint32_t *rev) const {
    if (!_ready)
        return Status::IoFailure;
    int index = Find(id);
    if (index < 0)
        return Status::NotFound;
    const auto &e = _directory->entries[index];
    if (!ReadProfile(id, e.revision, out))
        return Status::Invalid;
    if (rev)
        *rev = e.revision;
    return Status::Ok;
}

const UltimateProfile *ProfileStore::Activate(uint32_t id, Status *status) {
    _active_native.view.valid = false; _active_native_lease.Release();
    ++_native_generation; if (!_native_generation) ++_native_generation;
    if (!id) {
        _active_id = 0;
        _active_revision = 0;
        if (status)
            *status = Status::Ok;
        return nullptr;
    }
    int index = Find(id);
    if (!_ready || index < 0) {
        if (status)
            *status = Status::NotFound;
        return nullptr;
    }
    const auto &e = _directory->entries[index];
    bool previous = false;
    if (!ReadProfile(id, e.revision, _candidate_profile)) {
        if (!e.previous_revision || !ReadProfile(id, e.previous_revision, _candidate_profile)) {
            if (status)
                *status = Status::Invalid;
            return nullptr;
        }
        previous = true;
    }
    const bool native = _candidate_profile.schema_version == ultimate_native::kSchema;
    if (native != (e.payload_version == ultimate_native::kSchema) || (native && _read_only_recovery)) {
        if (status) *status = Status::Invalid;
        return nullptr;
    }
    _active_profile = _candidate_profile;
    if (_active_profile.schema_version == ultimate_native::kSchema) {
        if (!ultimate_native::CopyProgram(ultimate_native::CandidateView(), _active_native, _native_generation, true) ||
            !ultimate_native::BindOwned(_active_profile, _active_native, _active_native_lease)) {
            if (status) *status = Status::Invalid;
            return nullptr;
        }
    }
    _active_id = id;
    _active_revision = previous ? e.previous_revision : e.revision;
    if (status)
        *status = previous ? Status::RecoveredPrevious : Status::Ok;
    return &_active_profile;
}

ProfileStore::RecordHealth ProfileStore::Health(uint32_t id) const {
    int i = Find(id);
    if (i < 0)
        return RecordHealth::Missing;
    const auto &e = _directory->entries[i];
    // This is explicit inspection scratch, never active publication.
    auto &candidate = const_cast<ProfileStore *>(this)->_candidate_profile;
    bool unsupported = false;
    if (ReadProfile(id, e.revision, candidate, &unsupported))
        return RecordHealth::Healthy;
    if (e.previous_revision && ReadProfile(id, e.previous_revision, candidate))
        return RecordHealth::RecoveredPrevious;
    char path[32];
    ProfileStorePaths::RecordPath(path, sizeof(path), id, e.revision);
    if (_storage->Probe(path).outcome == Outcome::NotFound)
        return RecordHealth::Missing;
    if (unsupported)
        return RecordHealth::Unsupported;
    return RecordHealth::Corrupt;
}

bool ProfileStore::LoadProtectedRoot() const {
    if (!_ready || !_v2)
        return false;
    if (_protected_ready)
        return true;
    // After a commit the opposite slot is the preceding authority; before the
    // first commit the two identical bootstrap roots are both protected.
    if (!ReadRoot(static_cast<uint8_t>((Generation() & 1u) ^ 1u), *_other))
        return false;
    if (_other->incarnation != Incarnation() || _other->generation > Generation() ||
        Generation() - _other->generation > 1)
        return false;
    _protected_ready = true;
    return true;
}

bool ProfileStore::Protected(uint32_t id, uint32_t rev) const {
    if (id == _active_id && rev == _active_revision)
        return true;
    for (const Directory *d : { _directory, _other }) {
        for (size_t i = 0; i < d->count; ++i) {
            const auto &e = d->entries[i];
            if (e.id == id && (e.revision == rev || e.previous_revision == rev))
                return true;
        }
        for (size_t i = 0; i < d->migration_count; ++i)
            if (d->migration_ids[i] == id && d->migration_revisions[i] == rev)
                return true;
    }
    return false;
}

ProfileStore::CapacityInfo ProfileStore::Capacity() const {
    CapacityInfo c;
    CheckedStorage::Geometry g;
    if (!_storage || !_storage->Geometry(g) || !g.erase_bytes)
        return c;
    c.total_bytes = g.total_bytes;
    c.used_bytes = g.used_bytes;
    c.free_bytes = g.free_bytes;
    c.block_size = g.erase_bytes;
    c.page_size = g.program_bytes;
    if (!LoadProtectedRoot())
        return c;
    // Enumerate the deduplicated union without caching bodies. Both roots contain
    // at most64 entries, plus2 migration dependencies each. Nested bounded scans.
    uint32_t ids[2] = {};
    (void)ids;
    uint64_t protected_records = 0;
    size_t files = 0;
    auto charge = [&](uint32_t id, uint32_t rev) {
        if (!rev)
            return;
        char p[32];
        ProfileStorePaths::RecordPath(p, sizeof(p), id, rev);
        size_t n = 0;
        if (_storage->Probe(p, &n))
            protected_records += FileCharge(n, g.erase_bytes);
        else
            protected_records += FileCharge(kMaxRecordWireBytes, g.erase_bytes);
        ++files;
    };
    for (size_t root = 0; root < 2; ++root) {
        const Directory *d = root ? _other : _directory;
        for (size_t i = 0; i < d->count; ++i) {
            const auto &e = d->entries[i];
            for (unsigned v = 0; v < 2; ++v) {
                uint32_t rev = v ? e.previous_revision : e.revision;
                if (!rev)
                    continue;
                bool seen = false;
                if (root) {
                    for (size_t j = 0; j < _directory->count; ++j) {
                        const auto &o = _directory->entries[j];
                        if (o.id == e.id && (o.revision == rev || o.previous_revision == rev))
                            seen = true;
                    }
                }
                if (!seen)
                    charge(e.id, rev);
            }
        }
    }
    for (size_t i = 0; i < _directory->migration_count; ++i) {
        uint32_t id = _directory->migration_ids[i], rev = _directory->migration_revisions[i];
        bool seen = false;
        for (const Directory *d : { _directory, _other })
            for (size_t j = 0; j < d->count; ++j)
                if (d->entries[j].id == id &&
                    (d->entries[j].revision == rev || d->entries[j].previous_revision == rev))
                    seen = true;
        if (!seen)
            charge(id, rev);
    }
    if (_active_id && _active_revision) {
        bool seen = false;
        for (const Directory *d : { _directory, _other }) {
            for (size_t j = 0; j < d->count; ++j)
                if (d->entries[j].id == _active_id &&
                    (d->entries[j].revision == _active_revision ||
                     d->entries[j].previous_revision == _active_revision))
                    seen = true;
            for (size_t j = 0; j < d->migration_count; ++j)
                if (d->migration_ids[j] == _active_id &&
                    d->migration_revisions[j] == _active_revision)
                    seen = true;
        }
        if (!seen)
            charge(_active_id, _active_revision);
    }
    // Current allocated filesystem usage already includes allocator metadata.
    // Model protected content independently, including retained v1 roots, v2
    // control+two roots, Config current/prior/legacy/source copies. The metadata
    // allowance covers pair COW and 128 bytes per named immutable object.
    uint64_t fixed = 3 * FileCharge(kDirectoryWireBytes + 16, g.erase_bytes) +
                     2 * FileCharge(kLegacyDirectoryBytes, g.erase_bytes);
    const char *configs[] = { "/config-v2.bin",
                              "/config-v2.prev",
                              "/config.bin",
                              "/ultimate-migration.src" };
    for (const char *p : configs) {
        size_t n = 0;
        if (_storage->Probe(p, &n))
            fixed += FileCharge(n, g.erase_bytes);
    }
    const uint64_t metadata = 8ull * g.erase_bytes + 2 * Round((files + 12) * 128, g.erase_bytes);
    c.protected_bytes = protected_records + fixed + metadata;
    // One maximum record, one root COW, one checked Config replacement (maximum
    // encoded legacy body capped by existing transfer limit), metadata COW.
    c.staging_bytes = FileCharge(kMaxRecordWireBytes, g.erase_bytes) +
                      2 * FileCharge(kDirectoryWireBytes + 16, g.erase_bytes) +
                      FileCharge(8192 + 8, g.erase_bytes) + 4ull * g.erase_bytes;
    c.mutation_feasible = _ready && !_read_only_recovery && !_uncertain && !MigrationPending() &&
                          c.free_bytes >= c.reserve_bytes + c.staging_bytes &&
                          c.total_bytes >= c.protected_bytes + c.reserve_bytes + c.staging_bytes;
    // Representative complete native record envelope <=3373 bytes. Allow three
    // revisions per profile (union of both roots) and two metadata entries each.
    uint64_t per = 3 * FileCharge(ultimate_native::kRecordMax, g.erase_bytes) + 256;
    uint64_t overhead = fixed + metadata + c.reserve_bytes + c.staging_bytes;
    c.admissible_profiles =
        c.total_bytes > overhead ? static_cast<uint32_t>((c.total_bytes - overhead) / per) : 0;
    if (c.admissible_profiles > kMaxEntries)
        c.admissible_profiles = kMaxEntries;
    return c;
}

ProfileStore::Status ProfileStore::CollectGarbage() {
    if (!_ready || _read_only_recovery)
        return Status::ReadOnlyRecovery;
    if (_uncertain)
        return Status::UnknownOutcome;
    if (MigrationPending())
        return Status::MigrationFenced;
    if (!LoadProtectedRoot())
        return Status::IoFailure;

    struct Search {
        ProfileStore *store;
        char path[34];
        bool found;
    };

    static Search search{};
    struct SearchReset {
        Search &state;
        ~SearchReset() { std::memset(&state, 0, sizeof(state)); }
    } reset{search};
    for (unsigned budget = 0; budget < 128; ++budget) {
        std::memset(&search, 0, sizeof(search));
        search.store = this;
        bool enumerated = _storage->Enumerate([](void *opaque, const CheckedStorage::Entry &e) {
            auto &s = *static_cast<Search *>(opaque);
            if (e.directory || s.found)
                return true;
            unsigned id = 0, rev = 0;
            char ext[4]{};
            int used = 0;
            const char *name = e.name[0] == '/' ? e.name + 1 : e.name;
            if (std::sscanf(name, "ultimate-%8x-%8x.%3s%n", &id, &rev, ext, &used) != 3 ||
                static_cast<size_t>(used) != std::strlen(name) || std::strlen(name) != 30)
                return true;
            if (std::strcmp(ext, "bin") != 0 && std::strcmp(ext, "tmp") != 0)
                return true;
            if (s.store->Protected(id, rev))
                return true;
            std::snprintf(s.path, sizeof(s.path), "/%s", name);
            s.found = true;
            return true;
        }, &search);
        if (!enumerated)
            return Status::IoFailure;
        if (!search.found)
            return Status::Ok;
        if (!_storage->CheckedRemove(search.path))
            return Status::IoFailure;
    }
    return Status::Full; // bounded cleanup budget; retry is safe and deterministic.
}

bool ProfileStore::Admit(size_t bytes, size_t records) {
    const bool early = EvaluateAdmission(bytes, records);
    if (CollectGarbage() != Status::Ok)
        return false;
    return early;
}

__attribute__((noinline)) bool ProfileStore::EvaluateAdmission(size_t bytes, size_t records) {
    auto c = Capacity();
    if (!c.block_size)
        return false;
    uint64_t actual = records * FileCharge(bytes, c.block_size) +
                      2 * FileCharge(kDirectoryWireBytes + 16, c.block_size) +
                      FileCharge(8192 + 8, c.block_size) + 4ull * c.block_size;
    return c.free_bytes >= kReserve + actual &&
           c.total_bytes >= c.protected_bytes + kReserve + actual;
}

ProfileStore::TransactionResult ProfileStore::QueryTransaction(uint64_t token) const {
    if (_uncertain && !const_cast<ProfileStore *>(this)->ReconcileTransaction())
        return { Status::UnknownOutcome };
    if (!_ready)
        return { Status::IoFailure };
    if (!token || _directory->last_identity.token != token)
        return { Status::NotFound };
    return _directory->last_result;
}

ProfileStore::TransactionResult ProfileStore::QueryTransaction(const TransactionIdentity &t) const {
    auto r = QueryTransaction(t.token);
    if ((r.status == Status::Ok || r.status == Status::Aborted) &&
        !_directory->last_identity.SameRequest(t))
        return { Status::Conflict };
    return r;
}

__attribute__((noinline)) ProfileStore::TransactionResult ProfileStore::Start(const TransactionIdentity &t) const {
    if (_uncertain)
        return { Status::UnknownOutcome };
    if (!_ready)
        return { Status::IoFailure };
    if (_read_only_recovery)
        return { Status::ReadOnlyRecovery };
    if (MigrationPending())
        return { Status::MigrationFenced };
    if (!t.token)
        return { Status::Invalid };
    if (t.token < _directory->last_identity.token)
        return { Status::Conflict };
    auto r = QueryTransaction(t);
    if (r.status != Status::NotFound)
        return r;
    if (Generation() == UINT32_MAX)
        return { Status::Full };
    return { Status::NotFound };
}

// Receipt preparation and publication share the caller frame; transaction
// ordering and the single authoritative directory publication stay unchanged.
__attribute__((always_inline)) inline ProfileStore::TransactionResult ProfileStore::Commit(
    Directory &next,
    uint32_t id,
    uint32_t rev,
    const TransactionIdentity &t
) {
    next.generation = Generation() + 1;
    next.last_identity = t;
    next.last_result = { Status::Ok, id, rev, next.generation };
    static TransactionResult result; result = next.last_result;
    if (PublishDirectory(next)) return result;
    result = { _uncertain ? Status::UnknownOutcome : Status::IoFailure, id, rev, next.generation };
    return result;
}

__attribute__((noinline)) void ProfileStore::PrepareCreate() {
    prepared_create.ready = false;
    if (Count() >= 64 || _directory->high_water_id == UINT32_MAX) {
        prepared_create.result = { Status::Full }; return;
    }
    if (!ValidName(prepared_create.input_name) || !ValidateProfile(*prepared_create.profile)) {
        prepared_create.result = { Status::Invalid }; return;
    }
    prepared_create.bytes = 0;
    if (!pb_get_encoded_size(&prepared_create.bytes, UltimateProfile_fields, prepared_create.profile) || prepared_create.bytes > 4096) {
        prepared_create.result = { Status::Full }; return;
    }
    prepared_create.id = _directory->high_water_id + 1;
    prepared_create.schema = prepared_create.profile->schema_version;
    std::memcpy(prepared_create.name, prepared_create.input_name, std::strlen(prepared_create.input_name) + 1);
    prepared_create.ready = true;
}

__attribute__((noinline)) ProfileStore::TransactionResult ProfileStore::FinalizePreparedCreate() {
    *_next = *_directory;
    auto &e = _next->entries[_next->count++];
    e = {};
    e.id = prepared_create.id;
    e.revision = 1;
    e.payload_version = prepared_create.schema;
    e.rank = prepared_create.rank;
    std::memcpy(e.name, prepared_create.name, std::strlen(prepared_create.name) + 1);
    _next->high_water_id = prepared_create.id;
    return Commit(*_next, prepared_create.id, 1, prepared_create.identity);
}

ProfileStore::TransactionResult ProfileStore::Create(
    const UltimateProfile &p, const char *name, uint32_t rank, const TransactionIdentity &t
) {
    prepared_create.ready = false;
    prepared_create.profile = &p;
    prepared_create.input_name = name;
    prepared_create.rank = rank;
    prepared_create.identity = t;
    ::new (&prepared_create.result) TransactionResult(Start(prepared_create.identity));
    if (prepared_create.result.status == Status::NotFound) {
        PrepareCreate();
        prepared_create.input_name = nullptr;
        if (prepared_create.ready) {
            if (!Admit(prepared_create.bytes + 32)) prepared_create.result = { Status::Full };
            else {
                const bool encoded = PrepareProfileWrite(prepared_create.id, 1, *prepared_create.profile);
                prepared_create.profile = nullptr;
                if (!encoded || !PublishPreparedProfile())
                    prepared_create.result = { _uncertain ? Status::UnknownOutcome : Status::IoFailure };
                else ::new (&prepared_create.result) TransactionResult(FinalizePreparedCreate());
            }
        }
    }
    prepared_create.profile = nullptr;
    prepared_create.input_name = nullptr;
    prepared_create.ready = false;
    return prepared_create.result;
}

ProfileStore::TransactionResult ProfileStore::Update(
    uint32_t id,
    const UltimateProfile &p,
    uint32_t rev,
    const TransactionIdentity &t
) {
    static TransactionResult r; ::new (&r) TransactionResult(Start(t));
    if (r.status != Status::NotFound)
        return r;
    int i = Find(id);
    if (i < 0)
        return { Status::NotFound };
    if (_directory->entries[i].revision != rev)
        return { Status::Conflict };
    if (rev == UINT32_MAX)
        return { Status::Full };
    if ((_directory->entries[i].payload_version == ultimate_native::kSchema) != (p.schema_version == ultimate_native::kSchema))
        return { Status::Invalid };
    if (!ValidateProfile(p))
        return { Status::Invalid };
    size_t n = 0;
    if (!pb_get_encoded_size(&n, UltimateProfile_fields, &p) || n > 4096 || !Admit(n + 32))
        return { Status::Full };
    if (!PrepareProfileWrite(id, rev + 1, p) || !PublishPreparedProfile())
        return { _uncertain ? Status::UnknownOutcome : Status::IoFailure };
    *_next = *_directory;
    _next->entries[i].previous_revision = rev;
    _next->entries[i].revision = rev + 1;
    _next->entries[i].payload_version = p.schema_version;
    return Commit(*_next, id, rev + 1, t);
}

__attribute__((noinline)) ProfileStore::TransactionResult ProfileStore::PrepareDuplicate(
    uint32_t id, uint32_t rev, const TransactionIdentity &t
) {
    auto r = Start(t);
    if (r.status != Status::NotFound)
        return r;
    int i = Find(id);
    if (i < 0)
        return { Status::NotFound };
    if (_directory->entries[i].revision != rev)
        return { Status::Conflict };
    if (!ReadProfile(id, rev, _candidate_profile))
        return { Status::Invalid };
    if (!ultimate_native::PreserveProfile(_candidate_profile)) return { Status::Invalid };
    duplicate_prepared = true;
    return { Status::NotFound };
}

ProfileStore::TransactionResult ProfileStore::Duplicate(
    uint32_t id,
    uint32_t rev,
    const char *name,
    uint32_t rank,
    const TransactionIdentity &t
) {
    duplicate_prepared = false;
    static TransactionResult r; ::new (&r) TransactionResult(PrepareDuplicate(id, rev, t));
    if (!duplicate_prepared) return r;
    return Create(_candidate_profile, name, rank, t);
}

ProfileStore::TransactionResult ProfileStore::Rename(
    uint32_t id,
    const char *name,
    uint32_t generation,
    const TransactionIdentity &t
) {
    static TransactionResult r; ::new (&r) TransactionResult(Start(t));
    if (r.status != Status::NotFound)
        return r;
    int i = Find(id);
    if (i < 0)
        return { Status::NotFound };
    if (generation != Generation())
        return { Status::Conflict };
    if (!ValidName(name))
        return { Status::Invalid };
    if (!Admit(0, 0))
        return { Status::Full };
    *_next = *_directory;
    std::memset(_next->entries[i].name, 0, 33);
    std::memcpy(_next->entries[i].name, name, std::strlen(name));
    return Commit(*_next, id, _next->entries[i].revision, t);
}

ProfileStore::TransactionResult ProfileStore::Reorder(
    uint32_t id,
    uint32_t rank,
    uint32_t generation,
    const TransactionIdentity &t
) {
    static TransactionResult r; ::new (&r) TransactionResult(Start(t));
    if (r.status != Status::NotFound)
        return r;
    int i = Find(id);
    if (i < 0)
        return { Status::NotFound };
    if (generation != Generation())
        return { Status::Conflict };
    if (!Admit(0, 0))
        return { Status::Full };
    *_next = *_directory;
    _next->entries[i].rank = rank;
    return Commit(*_next, id, _next->entries[i].revision, t);
}

ProfileStore::TransactionResult ProfileStore::Delete(
    uint32_t id,
    uint32_t generation,
    uint32_t referenced,
    const TransactionIdentity &t
) {
    static TransactionResult r; ::new (&r) TransactionResult(Start(t));
    if (r.status != Status::NotFound)
        return r;
    int i = Find(id);
    if (i < 0)
        return { Status::NotFound };
    if (generation != Generation())
        return { Status::Conflict };
    if (id == referenced || id == _active_id)
        return { Status::Referenced };
    if (!Admit(0, 0))
        return { Status::Full };
    *_next = *_directory;
    for (size_t j = i + 1; j < _next->count; ++j)
        _next->entries[j - 1] = _next->entries[j];
    --_next->count;
    return Commit(*_next, id, 0, t);
}

namespace {
    bool HashFile(ProfileStoreStorage &s, const char *path, uint8_t out[32]) {
        size_t n = 0;
        if (!s.Probe(path, &n) || n > 65536)
            return false;
        Sha256 hash;
        uint8_t buffer[128];
        for (size_t off = 0; off < n; off += sizeof(buffer)) {
            size_t take = n - off < sizeof(buffer) ? n - off : sizeof(buffer);
            if (!s.ReadRange(path, off, buffer, take))
                return false;
            hash.Update(buffer, take);
        }
        hash.Final(out);
        return true;
    }

    void Receipt(ProfileStore::Directory &d) {
        Sha256 h;
        const char domain[] = "Glyph.ProfileStore.Migration.v2";
        h.Update(domain, sizeof(domain));
        uint8_t words[16];
        Put32(words, d.migration_version);
        Put32(words + 4, d.incarnation);
        Put32(words + 8, d.migration_count);
        Put32(words + 12, 0);
        h.Update(words, sizeof(words));
        h.Update(d.migration_source, 32);
        for (size_t i = 0; i < d.migration_count; ++i) {
            Put32(words, d.migration_ids[i]);
            Put32(words + 4, d.migration_revisions[i]);
            h.Update(words, 8);
            h.Update(d.migration_payloads[i], 32);
        }
        h.Final(d.migration_receipt);
    }

    bool CompactHash(const Config &c, uint8_t out[32]) {
        return HashMessage(Config_fields, &c, out);
    }

    ProfileStoreTransactionIdentity HistoricalIdentity(
        uint32_t token,
        uint32_t salt,
        uint32_t op,
        uint32_t id,
        uint32_t rev,
        const UltimateProfile *p,
        const char *name,
        uint32_t rank
    ) {
        ProfileStoreTransactionIdentity t;
        t.token = uint64_t(salt) << 32 | token;
        Sha256 h;
        const char domain[] = "Glyph.ProfileStore.Internal.v2";
        h.Update(domain, sizeof(domain));
        uint8_t b[16];
        Put32(b, op);
        Put32(b + 4, id);
        Put32(b + 8, rev);
        Put32(b + 12, rank);
        h.Update(b, sizeof(b));
        if (name)
            h.Update(name, std::strlen(name));
        if (p) {
            uint8_t digest[32];
            if (HashMessage(UltimateProfile_fields, p, digest))
                h.Update(digest, 32);
        }
        h.Final(t.digest);
        return t;
    }
}

bool ProfileStore::PrepareCompact(Config &c) const {
    if (!_directory || (c.ultimate_profiles_count && !_directory->migration_state))
        return false;
    if (c.ultimate_profile_store_format == 0) {
        for (size_t i = 0; i < c.game_mode_configs_count; ++i) {
            auto &m = c.game_mode_configs[i];
            if (m.mode_id == MODE_ULTIMATE && m.ultimate_profile_config) {
                if (m.ultimate_profile_config > _directory->migration_count)
                    return false;
                m.ultimate_profile_id = _directory->migration_ids[m.ultimate_profile_config - 1];
                m.ultimate_profile_config = 0;
            }
        }
        c.ultimate_profiles_count = 0;
        c.ultimate_profile_store_format = kCompactConfigFormat;
        c.ultimate_profile_store_incarnation = Incarnation();
        normalize_legacy_glyph_rgb_noops(c);
    }
    if (c.ultimate_profile_store_incarnation != Incarnation() || c.ultimate_profiles_count)
        return false;
    c.ultimate_profile_root_format = 2;
    std::memcpy(c.ultimate_profile_migration_receipt, _directory->migration_receipt, 32);
    return true;
}

bool ProfileStore::ValidateCompactReceipt(const Config &c) const {
    if (!_directory || c.ultimate_profile_root_format != 2 ||
        c.ultimate_profile_store_format != kCompactConfigFormat ||
        c.ultimate_profile_store_incarnation != Incarnation() || c.ultimate_profiles_count)
        return false;
    if (!_directory->migration_state)
        return true;
    if (std::memcmp(c.ultimate_profile_migration_receipt, _directory->migration_receipt, 32) != 0)
        return false;
    if (_directory->migration_state == 1) {
        uint8_t digest[32];
        if (!CompactHash(c, digest) || std::memcmp(digest, _directory->compact_digest, 32) != 0)
            return false;
    }
    return true;
}

ProfileStore::Status ProfileStore::ImportLegacyStream(
    const Config &legacy,
    const uint8_t source[32],
    LegacyReader reader,
    void *context,
    uint32_t *mapping,
    size_t capacity
) {
    if (!_ready || _read_only_recovery)
        return Status::ReadOnlyRecovery;
    if (_uncertain)
        return Status::UnknownOutcome;
    size_t count = legacy.ultimate_profiles_count;
    if (!count || count > 2 || count > capacity || !reader || !mapping)
        return Status::Invalid;
    uint8_t actual[32];
    if (!HashFile(*_storage, "/ultimate-migration.src", actual) ||
        std::memcmp(actual, source, 32) != 0)
        return Status::Invalid;
    if (_directory->migration_state) {
        if (_directory->migration_version != 2 || _directory->migration_count != count ||
            std::memcmp(source, _directory->migration_source, 32) != 0)
            return Status::Conflict;
        for (size_t i = 0; i < count; ++i) {
            if (!ReadProfile(
                    _directory->migration_ids[i],
                    _directory->migration_revisions[i],
                    _candidate_profile
                ) ||
                !HashMessage(UltimateProfile_fields, &_candidate_profile, actual) ||
                std::memcmp(actual, _directory->migration_payloads[i], 32) != 0)
                return Status::Invalid;
            mapping[i] = _directory->migration_ids[i];
        }
        return _directory->migration_state == 1 ? Status::MigrationFenced : Status::Ok;
    }
    if (count > kMaxEntries - Count() || _directory->high_water_id > UINT32_MAX - count ||
        Generation() == UINT32_MAX)
        return Status::Full;
    if (!Admit(kMaxRecordWireBytes, count))
        return Status::Full;
    *_next = *_directory;
    _next->migration_version = 2;
    _next->migration_count = count;
    _next->migration_state = 1;
    std::memcpy(_next->migration_source, source, 32);
    for (size_t i = 0; i < count; ++i) {
        if (!reader(context, i, _candidate_profile) || !ValidateProfile(_candidate_profile))
            return Status::Invalid;
        uint32_t id = _next->high_water_id + 1;
        if (!PrepareProfileWrite(id, 1, _candidate_profile) || !PublishPreparedProfile())
            return _uncertain ? Status::UnknownOutcome : Status::IoFailure;
        auto &e = _next->entries[_next->count++];
        e = {};
        e.id = id;
        e.revision = 1;
        e.payload_version = _candidate_profile.schema_version;
        e.rank = i;
        std::snprintf(e.name, sizeof(e.name), "Migrated %u", unsigned(i + 1));
        _next->high_water_id = id;
        _next->migration_ids[i] = id;
        _next->migration_revisions[i] = 1;
        mapping[i] = id;
        if (!HashMessage(UltimateProfile_fields, &_candidate_profile, _next->migration_payloads[i]))
            return Status::Invalid;
    }
    Receipt(*_next);
    // The existing shared Config scratch is unpublished and never an automatic
    // whole-Config frame. Actual imported bodies came from the bounded reader.
    Config &compact = ConfigWriteCandidate();
    compact = legacy;
    normalize_legacy_glyph_rgb_noops(compact);
    compact.ultimate_profiles_count = 0;
    compact.ultimate_profile_store_format = 1;
    compact.ultimate_profile_root_format = 2;
    compact.ultimate_profile_store_incarnation = Incarnation();
    for (size_t i = 0; i < compact.game_mode_configs_count; ++i) {
        auto &m = compact.game_mode_configs[i];
        if (m.mode_id == MODE_ULTIMATE && m.ultimate_profile_config) {
            if (m.ultimate_profile_config > count)
                return Status::Invalid;
            m.ultimate_profile_id = mapping[m.ultimate_profile_config - 1];
            m.ultimate_profile_config = 0;
        }
    }
    std::memcpy(compact.ultimate_profile_migration_receipt, _next->migration_receipt, 32);
    if (!CompactHash(compact, _next->compact_digest))
        return Status::Invalid;
    _next->generation = Generation() + 1;
    return PublishDirectory(*_next) ? Status::Ok
                                    : (_uncertain ? Status::UnknownOutcome : Status::IoFailure);
}

ProfileStore::Status ProfileStore::ImportLegacy(
    const Config &legacy,
    uint32_t *mapping,
    size_t capacity
) {
    // Portable host/application entry: capture the canonical immutable source.
    // Device boot uses Persistence's exact-file snapshot and streamed reader.
    static uint8_t wire[8192];
    pb_ostream_t stream = pb_ostream_from_buffer(wire, sizeof(wire));
    if (!pb_encode(&stream, Config_fields, &legacy))
        return Status::Invalid;
    Sha256 h;
    h.Update(wire, stream.bytes_written);
    uint8_t digest[32];
    h.Final(digest);
    size_t existing = 0;
    auto present = _storage->Probe("/ultimate-migration.src", &existing);
    if (present.outcome == Outcome::NotFound) {
        if (!_storage->CheckedWrite(
                "/ultimate-migration.src",
                wire,
                stream.bytes_written,
                Kind::Record
            ))
            return Status::IoFailure;
    } else {
        uint8_t old[32];
        if (!present || !HashFile(*_storage, "/ultimate-migration.src", old) ||
            std::memcmp(old, digest, 32))
            return Status::Conflict;
    }
    return ImportLegacyStream(legacy, digest, [](void *p, size_t i, UltimateProfile &out) {
        const auto &c = *static_cast<const Config *>(p);
        if (i >= c.ultimate_profiles_count)
            return false;
        out = c.ultimate_profiles[i];
        return true;
    }, const_cast<Config *>(&legacy), mapping, capacity);
}

ProfileStore::Status ProfileStore::CompleteMigration(const Config &compact) {
    if (!_ready || _read_only_recovery)
        return Status::ReadOnlyRecovery;
    if (_uncertain)
        return Status::UnknownOutcome;
    if (!_directory->migration_state || !ValidateCompactReceipt(compact))
        return Status::Invalid;
    uint8_t digest[32];
    if (_directory->migration_version == 2 &&
        (!HashFile(*_storage, "/ultimate-migration.src", digest) ||
         std::memcmp(digest, _directory->migration_source, 32)))
        return Status::Invalid;
    for (size_t i = 0; i < _directory->migration_count; ++i)
        if (!ReadProfile(
                _directory->migration_ids[i],
                _directory->migration_revisions[i],
                _candidate_profile
            ) ||
            !HashMessage(UltimateProfile_fields, &_candidate_profile, digest) ||
            std::memcmp(digest, _directory->migration_payloads[i], 32))
            return Status::Invalid;
    if (_directory->migration_state == 2)
        return Status::Ok;
    if (Generation() == UINT32_MAX)
        return Status::Full;
    *_next = *_directory;
    _next->migration_state = 2;
    _next->generation = Generation() + 1;
    return PublishDirectory(*_next) ? Status::Ok
                                    : (_uncertain ? Status::UnknownOutcome : Status::IoFailure);
}

// Compatibility overloads for existing internal callers use a firmware-derived
// content digest; the caller's old digest word is only part of the opaque token.
ProfileStore::TransactionResult ProfileStore::Create(
    const UltimateProfile &p,
    const char *n,
    uint32_t rank,
    uint32_t t,
    uint32_t d
) {
    return Create(p, n, rank, HistoricalIdentity(t, d, 4, 0, 0, &p, n, rank));
}

ProfileStore::TransactionResult ProfileStore::Update(
    uint32_t id,
    const UltimateProfile &p,
    uint32_t rev,
    uint32_t t,
    uint32_t d
) {
    return Update(id, p, rev, HistoricalIdentity(t, d, 5, id, rev, &p, nullptr, 0));
}

ProfileStore::TransactionResult ProfileStore::Duplicate(
    uint32_t id,
    uint32_t rev,
    const char *n,
    uint32_t rank,
    uint32_t t,
    uint32_t d
) {
    return Duplicate(id, rev, n, rank, HistoricalIdentity(t, d, 6, id, rev, nullptr, n, rank));
}

ProfileStore::TransactionResult ProfileStore::Rename(
    uint32_t id,
    const char *n,
    uint32_t g,
    uint32_t t,
    uint32_t d
) {
    return Rename(id, n, g, HistoricalIdentity(t, d, 7, id, g, nullptr, n, 0));
}

ProfileStore::TransactionResult ProfileStore::Reorder(
    uint32_t id,
    uint32_t rank,
    uint32_t g,
    uint32_t t,
    uint32_t d
) {
    return Reorder(id, rank, g, HistoricalIdentity(t, d, 8, id, g, nullptr, nullptr, rank));
}

ProfileStore::TransactionResult ProfileStore::Delete(
    uint32_t id,
    uint32_t g,
    uint32_t ref,
    uint32_t t,
    uint32_t d
) {
    return Delete(id, g, ref, HistoricalIdentity(t, d, 9, id, g, nullptr, nullptr, 0));
}

ProfileStore::TransactionResult ProfileStore::QueryTransaction(uint32_t t, uint32_t d) const {
    return QueryTransaction(uint64_t(d) << 32 | t);
}

ProfileStore::TransactionResult ProfileStore::BeginMutation(uint32_t t, uint32_t d) const {
    TransactionIdentity identity;
    identity.token = uint64_t(d) << 32 | t;
    return Start(identity);
}

void ProfileStore::Finish(TransactionResult *r, uint32_t id, uint32_t rev) const {
    *r = { Status::Ok, id, rev, Generation() + 1 };
}

ProfileStore profile_store;
