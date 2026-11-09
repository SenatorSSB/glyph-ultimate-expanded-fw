#pragma once
#ifndef GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC
#define GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC 0
#endif

#if GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC
#if !defined(GLYPH_PACKAGE_V1) || !GLYPH_PACKAGE_V1
#error Config.bin diagnostic is restricted to the isolated Mk6 package candidate
#endif
#include <cstddef>
#include <cstdint>
#ifdef GLYPH_CHECKED_STORAGE_TEST_MOUNT
#include <lfs.h>
#else
#include <LittleFS.h>
#endif
#include "core/Sha256.hpp"

// This transport is candidate-only. It does not extend either package schema.
namespace config_bin_diagnostic {
constexpr uint8_t kCommand = 0x7e;
constexpr size_t kRequestBytes = 16, kChunkBytes = 128, kFinalBytes = 116;
constexpr uint32_t kMaxFileBytes = 524288, kDeadlineMs = 60000;
enum class Status : uint16_t {
    Ok=0, NotRecovery=1, AlreadyUsed=2, StorageUnavailable=3, NotFound=4,
    OpenFailed=5, SizeLimit=6, ReadFailed=7, CloseFailed=8, Deadline=9, Internal=10
};
using Send = bool (*)(void *, const uint8_t *, size_t);
struct Workspace {
    lfs_t *fs = nullptr;
    lfs_file_t file{};
    lfs_file_config file_config{};
    alignas(8) uint8_t file_cache[256]{};
    Sha256 full_hash{}, body_hash{};
    uint8_t wire[24+kChunkBytes]{}, header[8]{};
    uint32_t file_size=0, sent=0, started=0, body_crc=~0u;
    uint64_t nonce=0;
    Send send=nullptr;
    void *context=nullptr;
    uint32_t count=0;
    Status status=Status::Ok;
    uint8_t header_count=0;
    bool opened=false, complete=false, closed=false;
};
bool InstallReadOnlyMount();
bool DecodeRequest(const uint8_t *, size_t, uint64_t &);
void Prepare(Workspace &, uint64_t, Status, Send, void *);
bool Extract(Workspace &);
}
#endif
