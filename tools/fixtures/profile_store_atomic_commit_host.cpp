#include "core/ProfileStoreAtomicCommit.hpp"
#include "core/ProfileStoreCapacity.hpp"
#include "core/CompactConfigRecovery.hpp"

#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>

namespace {
struct MemoryStorage final : ProfileStoreAtomicCommit::Storage {
    std::map<std::string, std::vector<uint8_t>> files;
    bool fail_rename = false;
    bool Write(const char *path, const uint8_t *bytes, size_t length) override {
        files[path] = std::vector<uint8_t>(bytes, bytes + length); return true;
    }
    bool Read(const char *path, uint8_t *bytes, size_t length) override {
        const auto found = files.find(path);
        if (found == files.end() || found->second.size() != length) return false;
        std::memcpy(bytes, found->second.data(), length); return true;
    }
    size_t Size(const char *path) override {
        const auto found = files.find(path);
        return found == files.end() ? 0 : found->second.size();
    }
    bool Remove(const char *path) override { files.erase(path); return true; }
    bool Rename(const char *from, const char *to) override {
        if (fail_rename) return false;
        const auto found = files.find(from); if (found == files.end()) return false;
        files[to] = found->second; files.erase(found); return true;
    }
};

bool nonempty(void *, const uint8_t *bytes, size_t length) { return length != 0 && bytes[0] == 0x5a; }
bool require(bool condition, const char *message) {
    if (condition) return true;
    std::fprintf(stderr, "FAIL: %s\n", message); return false;
}
}

int main() {
    MemoryStorage storage;
    const uint8_t previous[] = {0x5a, 5};
    const uint8_t next[] = {0x5a, 6};
    storage.files["/ultimate-dir-0.bin"] = {previous, previous + sizeof(previous)};
    storage.fail_rename = true;
    if (!require(!ProfileStoreAtomicCommit::ReplaceInactiveRoot(storage, "/ultimate-dir-1.bin.tmp",
            "/ultimate-dir-1.bin", next, sizeof(next), nonempty, nullptr), "interrupted publish must fail")) return 1;
    // A fresh boot selects the remaining valid highest root; this is the root
    // recovery guarantee used by ProfileStore::LoadDirectory.
    const auto root = storage.files.find("/ultimate-dir-0.bin");
    if (!require(root != storage.files.end() && root->second == std::vector<uint8_t>(previous, previous + sizeof(previous)),
                 "previous root must survive interrupted inactive-root update")) return 1;
    if (!require(storage.files.find("/ultimate-dir-1.bin") == storage.files.end(),
                 "failed root publication must not publish destination")) return 1;

    // Profile revisions are immutable files.  If staging a replacement revision
    // is interrupted, the current directory still resolves the known-good r1.
    MemoryStorage record_storage;
    const uint8_t record_r1[] = {0x5a, 1};
    const uint8_t record_r2[] = {0x5a, 2};
    record_storage.files["/ultimate-00000001-00000001.bin"] = {record_r1, record_r1 + sizeof(record_r1)};
    record_storage.fail_rename = true;
    if (!require(!ProfileStoreAtomicCommit::ReplaceVerifiedFile(record_storage,
            "/ultimate-00000001-00000002.bin.tmp", "/ultimate-00000001-00000002.bin",
            record_r2, sizeof(record_r2), nonempty, nullptr), "interrupted record publication must fail")) return 1;
    const auto active = record_storage.files.find("/ultimate-00000001-00000001.bin");
    if (!require(active != record_storage.files.end() && active->second == std::vector<uint8_t>(record_r1, record_r1 + sizeof(record_r1)),
                 "interrupted replacement must retain known-good active revision")) return 1;
    if (!require(record_storage.files.find("/ultimate-00000001-00000002.bin") == record_storage.files.end(),
                 "interrupted replacement must not publish new revision")) return 1;
    constexpr size_t max_record_bytes = 32 + 4096;
    constexpr size_t max_directory_bytes = 32 + 64 * 40 + 28;
    static_assert(ProfileStoreCapacity::FitsRepresentativeSet(20, max_record_bytes, max_directory_bytes));
    if (!require(ProfileStoreCapacity::FitsRepresentativeSet(20, max_record_bytes, max_directory_bytes),
                 "512KiB capacity with 16KiB reserve must admit twenty max-size records")) return 1;
    if (!require(!ProfileStoreCapacity::FitsRepresentativeSet(200, max_record_bytes, max_directory_bytes),
                 "capacity proof must reject an oversized representative set")) return 1;
    if (!require(CompactConfigRecovery::Select(false, true) == CompactConfigRecovery::Source::PriorCompact,
                 "after old compact rename before new publish, boot must choose retained compact prior")) return 1;
    if (!require(CompactConfigRecovery::Select(false, false) == CompactConfigRecovery::Source::Legacy,
                 "legacy is selected only with no compact generation to recover")) return 1;
    std::puts("profile_store_atomic_commit interrupted_root_update_recovery=PASS interrupted_record_replacement_recovery=PASS capacity_512KiB_reserve_16KiB_profiles_20=PASS compact_config_prior_recovery=PASS");
    return 0;
}
