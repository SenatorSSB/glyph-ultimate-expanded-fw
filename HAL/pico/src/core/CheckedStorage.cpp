#include "core/ProfileStoreReadTrace.hpp"
#include "core/CheckedStorage.hpp"
#include "core/PackageStorageFence.hpp"
#ifdef GLYPH_CHECKED_STORAGE_TEST_MOUNT
#include <lfs.h>
extern lfs_t *CheckedStorageTestMount();
#else
#include <LittleFS.h>
#include <RP2040Version.h>
#if ARDUINO_PICO_MAJOR != 3 || ARDUINO_PICO_MINOR != 6 || ARDUINO_PICO_REVISION != 3
#error CheckedStorage same-mount shim must be reviewed against the selected Arduino-Pico version
#endif
#endif
#include <cstring>
#include <new>

namespace CheckedStorage {
namespace {
#if (defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE) || defined(GLYPH_CHECKED_STORAGE_TEST_MOUNT)
#define GLYPH_CHECKED_STORAGE_FAULT_TEST 1
FaultHook faults = nullptr;
#else
#define GLYPH_CHECKED_STORAGE_FAULT_TEST 0
#endif
#ifndef GLYPH_CHECKED_STORAGE_TEST_MOUNT
// C++ protected member pointers refer to members of the declaring base. Apply
// them to the actual base object: never downcast LittleFS to an invented subtype.
struct FsAccess : fs::FS {
    static fs::FSImplPtr fs::FS::* implementation() { return &FsAccess::_impl; }
};
struct LfsAccess : littlefs_impl::LittleFSImpl {
    static lfs_t littlefs_impl::LittleFSImpl::* filesystem() { return &LfsAccess::_lfs; }
    static bool littlefs_impl::LittleFSImpl::* mounted() { return &LfsAccess::_mounted; }
};
#endif
lfs_t *mount() {
#ifdef GLYPH_CHECKED_STORAGE_TEST_MOUNT
    return CheckedStorageTestMount();
#else
    auto impl = LittleFS.*FsAccess::implementation();
    // Pinned LittleFS.cpp constructs this exact global with LittleFSImpl.
    auto *native = static_cast<littlefs_impl::LittleFSImpl *>(impl.get());
    if (!native || !(native->*LfsAccess::mounted())) return nullptr;
    return &(native->*LfsAccess::filesystem());
#endif
}
static_assert(sizeof(lfs_file_t) <= sizeof(File::native), "checked file handle bound");
static_assert(alignof(lfs_file_t) <= alignof(File), "checked file alignment");
lfs_file_t *handle(File &f) { return reinterpret_cast<lfs_file_t *>(f.native); }
lfs_t *filesystem(File &f) { return static_cast<lfs_t *>(f.mount); }
Result result(int rc, bool metadata = false) {
    if (rc >= 0) return {Outcome::Ok, 0, static_cast<size_t>(rc)};
    if (rc == LFS_ERR_NOENT) return {Outcome::NotFound, rc, 0};
    return {metadata ? Outcome::Uncertain : Outcome::Failed, rc, 0};
}
Fault fault(Kind k, Operation op, Phase p, const char *path) {
#if GLYPH_CHECKED_STORAGE_FAULT_TEST
    return faults ? faults(k, op, p, path) : Fault::None;
#else
    (void)k; (void)op; (void)p; (void)path;
    return Fault::None;
#endif
}
Result before(Kind k, Operation op, const char *path) {
    auto f = fault(k, op, Phase::Before, path);
    return f == Fault::None ? Result{Outcome::Ok, 0, 0, op} :
        Result{f == Fault::LostAcknowledgement ? Outcome::Uncertain : Outcome::Failed, LFS_ERR_IO, 0, op};
}
void afterInPlace(Kind k, Operation op, const char *path, Result &r) {
    if (fault(k, op, Phase::After, path) != Fault::None) {
        r.outcome = Outcome::Uncertain;
        r.error = LFS_ERR_IO;
    }
    r.operation = op;
}
bool valid(const char *p) {
    if (!p || !*p) return false;
    size_t component = 0;
    while (*p) { if (*p++ == '/') component = 0; else if (++component > 31) return false; }
    return true;
}
}
#if GLYPH_CHECKED_STORAGE_FAULT_TEST
void SetFaultHook(FaultHook hook) { faults = hook; }
#endif
Result Open(File &f, const char *path, bool write, Kind kind) {
    if (write && !PackageStorageFence::Permit(Operation::OpenWrite, path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::OpenWrite};
    if (f.opened || !valid(path)) return {Outcome::Failed, LFS_ERR_INVAL, 0};
    auto b = before(kind, write ? Operation::OpenWrite : Operation::OpenRead, path); if (!b) return b;
    lfs_t *fs = mount(); if (!fs) return {Outcome::Failed, LFS_ERR_IO, 0};
    if (write && !PackageStorageFence::Permit(Operation::OpenWrite, path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::OpenWrite};
    new (f.native) lfs_file_t{};
    auto r = result(lfs_file_open(fs, handle(f), path, write ? LFS_O_CREAT | LFS_O_TRUNC | LFS_O_RDWR : LFS_O_RDONLY));
    if (r) {
        f.mount = fs; f.opened = true; f.path = path; f.kind = kind;
        f.writable = write;
        f.write_owner = write ? PackageStorageFence::WriteOwner() : nullptr;
        if (write && !PackageStorageFence::RetainHandle(f.write_owner)) {
            // The open already happened. Release without permitting a dirty
            // sync; this is uncertainty, never a safe-to-retry failed open.
            handle(f)->flags |= LFS_F_ERRED;
            lfs_file_close(fs, handle(f)); f.opened = false;
            return {Outcome::Uncertain, LFS_ERR_INVAL, 0, Operation::OpenWrite};
        }
    }
    afterInPlace(kind, write ? Operation::OpenWrite : Operation::OpenRead, path, r);
    // A lost open acknowledgement still owns a native handle; close it exactly
    // once so a failed stage cannot leak into the next synchronous operation.
    if (!r && f.opened) {
        if (f.writable && PackageStorageFence::kEnabled) {
            PackageStorageFence::Fence();
            handle(f)->flags |= LFS_F_ERRED;
        }
        lfs_file_close(fs, handle(f)); f.opened = false;
        if (f.writable) PackageStorageFence::ReleaseHandle(f.write_owner);
    }
    return r;
}
Result Read(File &f, void *bytes, size_t length) {
    if (f.opened && f.writable &&
        !PackageStorageFence::PermitHandle(f.write_owner, Operation::Read, f.path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Read};
    if (!f.opened) return {Outcome::Failed, LFS_ERR_BADF, 0};
    auto b = before(f.kind, Operation::Read, f.path);
    if (!b) { if (f.writable) PackageStorageFence::Fence(); return b; }
    if (f.writable && !PackageStorageFence::PermitHandle(f.write_owner, Operation::Read, f.path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Read};
    auto r = result(lfs_file_read(filesystem(f), handle(f), bytes, length));
    afterInPlace(f.kind, Operation::Read, f.path, r);
    if (!r && f.writable) PackageStorageFence::Fence();
    return r;
}
static __attribute__((noinline)) bool PermitWriteHandle(File &f) {
    return !f.writable || PackageStorageFence::PermitHandle(f.write_owner, Operation::Write, f.path);
}
Result Write(File &f, const void *bytes, size_t length) {
    if (f.opened && !PermitWriteHandle(f))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Write};
    if (!f.opened) return {Outcome::Failed, LFS_ERR_BADF, 0};
    auto b = before(f.kind, Operation::Write, f.path);
    if (!b) { if (f.writable) PackageStorageFence::Fence(); return b; }
    if (!PermitWriteHandle(f))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Write};
    auto r = result(lfs_file_write(filesystem(f), handle(f), bytes, length));
    if (r && r.bytes != length) r.outcome = Outcome::Failed;
    afterInPlace(f.kind, Operation::Write, f.path, r);
    if (!r) PackageStorageFence::Fence();
    return r;
}
Result Seek(File &f, size_t offset) {
    if (f.opened && f.writable &&
        !PackageStorageFence::PermitHandle(f.write_owner, Operation::Seek, f.path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Seek};
    if (!f.opened || offset > INT32_MAX) return {Outcome::Failed, LFS_ERR_INVAL, 0};
    auto b = before(f.kind, Operation::Seek, f.path);
    if (!b) { if (f.writable) PackageStorageFence::Fence(); return b; }
    if (f.writable && !PackageStorageFence::PermitHandle(f.write_owner, Operation::Seek, f.path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Seek};
    auto r = result(lfs_file_seek(filesystem(f), handle(f), offset, LFS_SEEK_SET));
    afterInPlace(f.kind, Operation::Seek, f.path, r);
    if (!r && f.writable) PackageStorageFence::Fence();
    return r;
}
Result Sync(File &f) {
    if (f.opened && f.writable &&
        !PackageStorageFence::PermitHandle(f.write_owner, Operation::Sync, f.path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Sync};
    if (!f.opened) return {Outcome::Failed, LFS_ERR_BADF, 0};
    auto b = before(f.kind, Operation::Sync, f.path);
    if (!b) { if (f.writable) PackageStorageFence::Fence(); return b; }
    if (f.writable && !PackageStorageFence::PermitHandle(f.write_owner, Operation::Sync, f.path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Sync};
    auto r = result(lfs_file_sync(filesystem(f), handle(f)));
    afterInPlace(f.kind, Operation::Sync, f.path, r);
    if (!r && f.writable) PackageStorageFence::Fence();
    return r;
}
Result Close(File &f) {
    if (!f.opened) return {Outcome::Failed, LFS_ERR_BADF, 0};
    bool denied = f.writable &&
        !PackageStorageFence::PermitHandle(f.write_owner, Operation::Close, f.path);
    // Pinned LittleFS rawclose always calls rawsync. LFS_F_ERRED makes rawsync
    // return before flushing dirty data/metadata; native handle/cache release
    // still runs. Never turn a revoked handle's cleanup into a new write.
    if (denied) handle(f)->flags |= LFS_F_ERRED;
    auto b = before(f.kind, Operation::Close, f.path);
    if (!b && f.writable) PackageStorageFence::Fence();
    denied = denied || (f.writable && !PackageStorageFence::PermitHandle(f.write_owner, Operation::Close, f.path));
    if (denied) handle(f)->flags |= LFS_F_ERRED;
    // Even an injected close failure must release the native handle. Its return
    // is observed, then the injection classifies the acknowledgement.
    auto r = result(lfs_file_close(filesystem(f), handle(f))); f.opened = false;
    if (f.writable) PackageStorageFence::ReleaseHandle(f.write_owner);
    if (denied) return !b ? b : Result{Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Close};
    if (!b) return b;
    afterInPlace(f.kind, Operation::Close, f.path, r);
    if (!r && f.writable) PackageStorageFence::Fence();
    return r;
}
Result Stat(const char *path, size_t *size, Kind kind) {
    if (!valid(path)) return {Outcome::Failed, LFS_ERR_INVAL, 0};
    auto b = before(kind, Operation::Stat, path); if (!b) return b;
    auto *fs = mount(); if (!fs) return {Outcome::Failed, LFS_ERR_IO, 0};
    lfs_info info{}; auto r = result(lfs_stat(fs, path, &info));
    if (r && size) *size = info.size;
    afterInPlace(kind, Operation::Stat, path, r);
    return r;
}
Result Remove(const char *path, Kind kind) {
    if (!PackageStorageFence::Permit(Operation::Remove, path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Remove};
    if (!valid(path)) return {Outcome::Failed, LFS_ERR_INVAL, 0};
    auto b = before(kind, Operation::Remove, path); if (!b) { PackageStorageFence::Fence(); return b; }
    auto *fs = mount(); if (!fs) return {Outcome::Failed, LFS_ERR_IO, 0};
    if (!PackageStorageFence::Permit(Operation::Remove, path))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Remove};
    auto r = result(lfs_remove(fs, path), true);
    if (r.outcome == Outcome::NotFound) r = {Outcome::Ok, 0, 0};
    afterInPlace(kind, Operation::Remove, path, r);
    if (!r) PackageStorageFence::Fence();
    return r;
}
Result Rename(const char *from, const char *to, Kind kind) {
    if (!PackageStorageFence::Permit(Operation::Rename, from, to))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Rename};
    if (!valid(from) || !valid(to)) return {Outcome::Failed, LFS_ERR_INVAL, 0};
    auto b = before(kind, Operation::Rename, from); if (!b) { PackageStorageFence::Fence(); return b; }
    auto *fs = mount(); if (!fs) return {Outcome::Failed, LFS_ERR_IO, 0};
    if (!PackageStorageFence::Permit(Operation::Rename, from, to))
        return {Outcome::Failed, LFS_ERR_INVAL, 0, Operation::Rename};
    auto r = result(lfs_rename(fs, from, to), true);
    afterInPlace(kind, Operation::Rename, from, r);
    if (!r) PackageStorageFence::Fence();
    return r;
}
Result Capacity(Geometry &g) {
    auto b = before(Kind::Root, Operation::Capacity, "/"); if (!b) return b;
    auto *fs = mount(); if (!fs || !fs->cfg) return {Outcome::Failed, LFS_ERR_IO, 0};
    const auto blocks = lfs_fs_size(fs); if (blocks < 0) return result(blocks);
    const auto &c = *fs->cfg;
    g.total_bytes = uint64_t(c.block_count) * c.block_size;
    g.used_bytes = uint64_t(blocks) * c.block_size;
    if (g.used_bytes > g.total_bytes) return {Outcome::Failed, LFS_ERR_CORRUPT, 0};
    g.free_bytes = g.total_bytes - g.used_bytes;
    g.erase_bytes = c.block_size; g.program_bytes = c.prog_size; g.read_bytes = c.read_size;
    g.block_count = c.block_count; g.cache_bytes = c.cache_size; g.name_max = 31;
    Result r{Outcome::Ok, 0, 0};
    afterInPlace(Kind::Root, Operation::Capacity, "/", r);
    return r;
}
Result Enumerate(const char *directory, Visitor visitor, void *context) {
    if (!visitor || !valid(directory)) return {Outcome::Failed, LFS_ERR_INVAL, 0};
    auto b = before(Kind::Root, Operation::Enumerate, directory); if (!b) return b;
    auto *fs = mount(); if (!fs) return {Outcome::Failed, LFS_ERR_IO, 0};
    lfs_dir_t dir{}; auto r = result(lfs_dir_open(fs, &dir, directory)); if (!r) return r;
    lfs_info info{};
    for (;;) {
        int rc = lfs_dir_read(fs, &dir, &info);
        if (rc <= 0) { r = result(rc); break; }
        if (!std::strcmp(info.name, ".") || !std::strcmp(info.name, "..")) continue;
        Entry entry{}; std::strncpy(entry.name, info.name, sizeof(entry.name) - 1);
        entry.bytes = info.size; entry.directory = info.type == LFS_TYPE_DIR;
        if (!visitor(context, entry)) { r = {Outcome::Failed, LFS_ERR_INVAL, 0}; break; }
    }
    auto closed = result(lfs_dir_close(fs, &dir)); if (!closed) r = closed;
    afterInPlace(Kind::Root, Operation::Enumerate, directory, r);
    return r;
}
Result WriteFile(const char *path, const uint8_t *bytes, size_t length, Kind kind) {
    File file; auto r = Open(file, path, true, kind); if (!r) return r;
    r = Write(file, bytes, length);
    if (r) r = Sync(file);
    auto close = Close(file); if (!close) r = close;
    return r;
}
Result ReadFile(const char *path, uint8_t *bytes, size_t length, Kind kind) {
    size_t size = 0; auto r = Stat(path, &size, kind); if (!r) return r;
    if (size != length) return {Outcome::Failed, LFS_ERR_INVAL, size};
    File file; r = Open(file, path, false, kind); if (!r) return r;
    if (kind == Kind::Record) ProfileStoreReadTrace::Mark(13);
    r = Read(file, bytes, length); if (r && r.bytes != length) r.outcome = Outcome::Failed;
    if (kind == Kind::Record) ProfileStoreReadTrace::Mark(14, r.bytes);
    // Always close even if the USB observer failed while this file was open.
    auto closed = Close(file); if (!closed) r = closed;
    if (kind == Kind::Record) ProfileStoreReadTrace::Mark(15, bool(closed));
    return r;
}
}
