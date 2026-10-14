// Source-owned LittleFS filename contract for the deployed Arduino-Pico 3.6.3
// wrapper: pathValid() rejects a component whose length is >= LFS_NAME_MAX
// (32). Keep every generated component at or below this conservative bound.
#ifndef _CORE_PROFILE_STORE_PATHS_HPP
#define _CORE_PROFILE_STORE_PATHS_HPP

#include <cstddef>
#include <cstdint>
#include <cstdio>

namespace ProfileStorePaths {

constexpr size_t kMaxFsComponent = 31;
constexpr size_t kHex32Width = 8;
constexpr size_t kRecordComponentLength =
    sizeof("ultimate-") - 1 + kHex32Width + 1 + kHex32Width + sizeof(".bin") - 1;
constexpr size_t kRecordTemporaryComponentLength =
    sizeof("ultimate-") - 1 + kHex32Width + 1 + kHex32Width + sizeof(".tmp") - 1;
constexpr size_t kDirectoryComponentLength = sizeof("ultimate-dir-0.bin") - 1;
constexpr size_t kDirectoryTemporaryComponentLength = sizeof("ultimate-dir-0.tmp") - 1;

static_assert(kRecordComponentLength <= kMaxFsComponent, "record name exceeds LittleFS component bound");
static_assert(kRecordTemporaryComponentLength <= kMaxFsComponent, "record temporary name exceeds LittleFS component bound");
static_assert(kDirectoryComponentLength <= kMaxFsComponent, "directory name exceeds LittleFS component bound");
static_assert(kDirectoryTemporaryComponentLength <= kMaxFsComponent, "directory temporary name exceeds LittleFS component bound");

inline void DirectoryPath(char *out, size_t length, uint8_t slot) {
    std::snprintf(out, length, "/ultimate-dir-%u.bin", slot);
}

inline void DirectoryTemporaryPath(char *out, size_t length, uint8_t slot) {
    std::snprintf(out, length, "/ultimate-dir-%u.tmp", slot);
}

inline void RecordPath(char *out, size_t length, uint32_t id, uint32_t revision) {
    std::snprintf(out, length, "/ultimate-%08lx-%08lx.bin", static_cast<unsigned long>(id),
                  static_cast<unsigned long>(revision));
}

inline void RecordTemporaryPath(char *out, size_t length, uint32_t id, uint32_t revision) {
    std::snprintf(out, length, "/ultimate-%08lx-%08lx.tmp", static_cast<unsigned long>(id),
                  static_cast<unsigned long>(revision));
}

} // namespace ProfileStorePaths

#endif
