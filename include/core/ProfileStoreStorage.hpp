/* Same-mount named-file operations used by ProfileStore persistence. */
#ifndef _CORE_PROFILE_STORE_STORAGE_HPP
#define _CORE_PROFILE_STORE_STORAGE_HPP

#include <cstddef>
#include <cstdint>

enum class ProfileStoreIoStage : uint8_t {
    None,
    RecordEncodeSize,
    RecordEncode,
    RecordTempOpenWrite,
    RecordTempWrite,
    RecordTempRead,
    RecordTempSize,
    RecordVerify,
    RecordDestRemove,
    RecordRename,
};

inline const char *ProfileStoreIoDiagnostic(ProfileStoreIoStage stage) {
    switch (stage) {
        case ProfileStoreIoStage::RecordEncodeSize: return "record.encode_size";
        case ProfileStoreIoStage::RecordEncode: return "record.encode";
        case ProfileStoreIoStage::RecordTempOpenWrite: return "record.temp_open_write";
        case ProfileStoreIoStage::RecordTempWrite: return "record.temp_write";
        case ProfileStoreIoStage::RecordTempRead: return "record.temp_read";
        case ProfileStoreIoStage::RecordTempSize: return "record.temp_size";
        case ProfileStoreIoStage::RecordVerify: return "record.verify";
        case ProfileStoreIoStage::RecordDestRemove: return "record.dest_remove";
        case ProfileStoreIoStage::RecordRename: return "record.rename";
        default: return "";
    }
}

class ProfileStoreStorage {
  public:
    virtual ~ProfileStoreStorage() = default;
    virtual bool Write(const char *path, const uint8_t *bytes, size_t length) = 0;
    virtual bool Read(const char *path, uint8_t *bytes, size_t length) = 0;
    virtual size_t Size(const char *path) = 0;
    virtual bool Exists(const char *path) = 0;
    // A concrete adapter may refine a false Write/Read outcome. Atomic
    // publication supplies a truthful generic stage when it does not.
    virtual ProfileStoreIoStage LastFailureStage() const { return ProfileStoreIoStage::None; }
    // Idempotent ensure-absent operation: success means the path is absent
    // afterward, whether it was absent initially or was removed. A real
    // removal failure for an existing path must return false.
    virtual bool Remove(const char *path) = 0;
    virtual bool Rename(const char *from, const char *to) = 0;
};

#endif
