#include "core/ProfileStoreAtomicCommit.hpp"

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
    std::puts("profile_store_atomic_commit interrupted_root_update_recovery=PASS");
    return 0;
}
