/* Same-mount named-file operations used by ProfileStore persistence. */
#ifndef _CORE_PROFILE_STORE_STORAGE_HPP
#define _CORE_PROFILE_STORE_STORAGE_HPP

#include <cstddef>
#include <cstdint>

class ProfileStoreStorage {
  public:
    virtual ~ProfileStoreStorage() = default;
    virtual bool Write(const char *path, const uint8_t *bytes, size_t length) = 0;
    virtual bool Read(const char *path, uint8_t *bytes, size_t length) = 0;
    virtual size_t Size(const char *path) = 0;
    virtual bool Exists(const char *path) = 0;
    // Idempotent ensure-absent operation: success means the path is absent
    // afterward, whether it was absent initially or was removed. A real
    // removal failure for an existing path must return false.
    virtual bool Remove(const char *path) = 0;
    virtual bool Rename(const char *from, const char *to) = 0;
};

#endif
