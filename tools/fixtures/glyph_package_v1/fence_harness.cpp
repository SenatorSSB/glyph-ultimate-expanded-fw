#include "core/PackageStorageFence.hpp"
#include <lfs.h>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
using namespace CheckedStorage;
namespace {
lfs_t filesystem{};
lfs_config configuration{};
std::vector<uint8_t> flash(4096 * 128, 0xff);
unsigned programs = 0, erases = 0, syncs = 0;
void require(bool value, const char *message) { if (!value) throw std::runtime_error(message); }
int read_block(const lfs_config *, lfs_block_t block, lfs_off_t offset, void *bytes, lfs_size_t count) {
    std::memcpy(bytes, flash.data() + block * 4096 + offset, count); return 0;
}
int program_block(const lfs_config *, lfs_block_t block, lfs_off_t offset, const void *bytes, lfs_size_t count) {
    ++programs;
    auto *out = flash.data() + block * 4096 + offset;
    const auto *in = static_cast<const uint8_t *>(bytes);
    for (size_t i = 0; i < count; ++i) {
        if ((out[i] & in[i]) != in[i]) return LFS_ERR_CORRUPT;
        out[i] &= in[i];
    }
    return 0;
}
int erase_block(const lfs_config *, lfs_block_t block) {
    ++erases; std::fill_n(flash.data() + block * 4096, 4096, 0xff); return 0;
}
int sync_blocks(const lfs_config *) { ++syncs; return 0; }
bool authorize(void *, PackageStorageFence::WriteKind, uint64_t, Operation operation, const char *path, const char *destination) {
    if (!path || std::strcmp(path, "/stage")) return false;
    return operation != Operation::Rename ||
           (destination && std::strcmp(destination, "/installed") == 0);
}
void observe_mount() {
    PackageStorageFence::BeginMountAttempt();
    PackageStorageFence::FinishMountAttempt(true, true);
    PackageStorageFence::Classify(PackageStorageFence::Classification::LegacyHealthy);
}
}
lfs_t *CheckedStorageTestMount() { return &filesystem; }
unsigned p_at_fail, e_at_fail, s_at_fail;
Operation target;
Fault cut(Kind, Operation op, Phase phase, const char*) {
    if (op != target || phase != Phase::Before) return Fault::None;
    p_at_fail=programs; e_at_fail=erases; s_at_fail=syncs;
    return Fault::Fail;
}
int main(int argc, char **argv) {
    try {
        configuration.read = read_block; configuration.prog = program_block;
        configuration.erase = erase_block; configuration.sync = sync_blocks;
        configuration.read_size = 256; configuration.prog_size = 256;
        configuration.block_size = 4096; configuration.block_count = 128;
        configuration.cache_size = 256; configuration.lookahead_size = 256;
        configuration.block_cycles = 16;
        require(lfs_format(&filesystem, &configuration) == 0, "test-only fixture format");
        require(lfs_mount(&filesystem, &configuration) == 0, "test mount");
        const auto original = flash;
        const char *scenario = argc == 2 ? argv[1] : "unclassified";
        if (!std::strcmp(scenario, "failed-mount")) {
            PackageStorageFence::BeginMountAttempt();
            PackageStorageFence::FinishMountAttempt(false, false);
            PackageStorageFence::Classify(PackageStorageFence::Classification::LegacyHealthy);
            require(!PackageStorageFence::Available(), "failed mount remains unavailable");
        } else if (std::strcmp(scenario, "unclassified")) {
            observe_mount();
        }
        File file;
        require(!Open(file, "/stage", true, Kind::Config), "no implicit writer");
        require(flash == original, "denied open preserves exact NOR bytes");
        unsigned owner = 1;
        if (!std::strcmp(scenario, "unclassified") || !std::strcmp(scenario, "failed-mount")) {
            require(!PackageStorageFence::BeginWrite(&owner, PackageStorageFence::WriteKind::Package, 1, authorize, nullptr), "unproved state denies admission");
        } else {
            require(PackageStorageFence::BeginWrite(&owner, PackageStorageFence::WriteKind::Package, 1, authorize, nullptr), "proved exact scope");
            unsigned other_owner = 2;
            require(PackageStorageFence::IsPackageWriter(&owner, 1), "exact admitted package identity");
            require(!PackageStorageFence::IsPackageWriter(&owner, 2) &&
                    !PackageStorageFence::IsPackageWriter(&other_owner, 1), "stale token and foreign owner cannot publish Config");
            require(!Open(file, "/foreign", true, Kind::Config), "scope path denial");
            if (!std::strcmp(scenario, "sync-before") || !std::strcmp(scenario, "close-before")) {
                std::vector<uint8_t> bytes(600,0x53);
                target=!std::strcmp(scenario,"sync-before")?Operation::Sync:Operation::Close;
                SetFaultHook(cut);
                if (target==Operation::Sync) require(!WriteFile("/stage",bytes.data(),bytes.size(),Kind::Config),"expect fail");
                else {require(bool(Open(file,"/stage",true,Kind::Config)),"open");require(bool(Write(file,bytes.data(),bytes.size())),"dirty");require(!Close(file),"expect fail");}
                SetFaultHook(nullptr);
                size_t n=0; require(bool(Stat("/stage",&n)),"stage extent available");
                std::printf("post-failure NOR program=%u erase=%u sync=%u staged=%zu live_fence=%d\n",programs-p_at_fail,erases-e_at_fail,syncs-s_at_fail,n,PackageStorageFence::MutationFenced());
                require(programs==p_at_fail&&erases==e_at_fail&&syncs==s_at_fail&&PackageStorageFence::MutationFenced(),"no post-failure publication or dirty close writes");
                require(filesystem.mlist==nullptr,"failed write releases handle");
                return 0;
            }
            require(bool(Open(file, "/stage", true, Kind::Config)), "admitted open");
            std::vector<uint8_t> bytes(600, 0x53);
            require(bool(Write(file, bytes.data(), bytes.size())), "admitted dirty write");
            const auto dirty = flash;
            const auto p = programs, e = erases, s = syncs;
            if (!std::strcmp(scenario, "revoked-dirty")) {
                PackageStorageFence::Fence();
                uint8_t byte{};
                require(!Read(file, &byte, 1) && !Seek(file, 0) && !Sync(file), "revoked flush-capable operations denied");
                require(!Write(file, bytes.data(), 1), "revoked write denied");
                require(!Close(file), "revoked close reports refusal");
                require(flash == dirty && programs == p && erases == e && syncs == s,
                        "revoked dirty close releases without program erase or sync");
                require(filesystem.mlist == nullptr, "dirty cleanup releases native handle");
                PackageStorageFence::Classify(PackageStorageFence::Classification::LegacyHealthy);
                require(!PackageStorageFence::BeginWrite(&owner, PackageStorageFence::WriteKind::Package, 2, authorize, nullptr), "reclassification never clears fence");
                require(!Rename("/stage", "/installed", Kind::Config) && !Remove("/stage", Kind::Config), "revoked metadata denied");
            } else {
                require(bool(Sync(file)) && bool(Close(file)), "healthy dirty sync close");
                require(!Rename("/stage", "/foreign", Kind::Config), "destination denial");
                require(bool(Rename("/stage", "/installed", Kind::Config)), "admitted rename");
                PackageStorageFence::EndWrite(&owner);
                require(!PackageStorageFence::BeginWrite(&owner, PackageStorageFence::WriteKind::Package, 0, authorize, nullptr), "zero token has no package authority");
                require(PackageStorageFence::BeginWrite(&owner, PackageStorageFence::WriteKind::Legacy, 1, authorize, nullptr), "ordinary writer has separate authority");
                require(!PackageStorageFence::IsPackageWriter(&owner, 1), "ordinary writer cannot become package publication");
                PackageStorageFence::EndWrite(&owner);
                std::vector<uint8_t> actual(bytes.size());
                require(bool(ReadFile("/installed", actual.data(), actual.size(), Kind::Config)), "healthy exact read");
                require(actual == bytes, "healthy bytes preserved");
                require(!Remove("/installed", Kind::Config), "closed writer cannot remove");
            }
        }
        require(lfs_unmount(&filesystem) == 0, "unmount");
        std::printf("PASS fence scenario=%s ram_only=true\n", scenario);
        return 0;
    } catch (const std::exception &error) { std::fprintf(stderr, "FAIL: %s\n", error.what()); return 1; }
}
