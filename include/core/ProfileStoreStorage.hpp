/* Same-mount named-file operations used by ProfileStore persistence. */
#ifndef _CORE_PROFILE_STORE_STORAGE_HPP
#define _CORE_PROFILE_STORE_STORAGE_HPP

#include "core/CheckedStorage.hpp"

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
    DirectoryEncode,
    DirectoryTempOpenWrite,
    DirectoryTempWrite,
    DirectoryTempRead,
    DirectoryTempSize,
    DirectoryVerify,
    DirectoryDestRemove,
    DirectoryRename,
    DirectoryGenerationMismatch,
    RecordTempSync,
    RecordTempClose,
    DirectoryTempSync,
    DirectoryTempClose,
};

enum class ProfileStoreStorageFailure : uint8_t {
    None,
    TempOpenWrite,
    TempWrite,
    TempRead,
    TempSize,
    TempSync,
    TempClose
};
enum class ProfileStorePublicationKind : uint8_t {
    Record,
    Directory
};

inline ProfileStoreIoStage ProfileStoreStage(
    ProfileStorePublicationKind kind,
    ProfileStoreStorageFailure failure
) {
    if (kind == ProfileStorePublicationKind::Directory) {
        switch (failure) {
            case ProfileStoreStorageFailure::TempOpenWrite:
                return ProfileStoreIoStage::DirectoryTempOpenWrite;
            case ProfileStoreStorageFailure::TempWrite:
                return ProfileStoreIoStage::DirectoryTempWrite;
            case ProfileStoreStorageFailure::TempRead:
                return ProfileStoreIoStage::DirectoryTempRead;
            case ProfileStoreStorageFailure::TempSize:
                return ProfileStoreIoStage::DirectoryTempSize;
            case ProfileStoreStorageFailure::TempSync:
                return ProfileStoreIoStage::DirectoryTempSync;
            case ProfileStoreStorageFailure::TempClose:
                return ProfileStoreIoStage::DirectoryTempClose;
            default:
                return ProfileStoreIoStage::None;
        }
    }
    switch (failure) {
        case ProfileStoreStorageFailure::TempOpenWrite:
            return ProfileStoreIoStage::RecordTempOpenWrite;
        case ProfileStoreStorageFailure::TempWrite:
            return ProfileStoreIoStage::RecordTempWrite;
        case ProfileStoreStorageFailure::TempRead:
            return ProfileStoreIoStage::RecordTempRead;
        case ProfileStoreStorageFailure::TempSize:
            return ProfileStoreIoStage::RecordTempSize;
        case ProfileStoreStorageFailure::TempSync:
            return ProfileStoreIoStage::RecordTempSync;
        case ProfileStoreStorageFailure::TempClose:
            return ProfileStoreIoStage::RecordTempClose;
        default:
            return ProfileStoreIoStage::None;
    }
}

inline ProfileStoreIoStage ProfileStoreStage(
    ProfileStorePublicationKind kind,
    ProfileStoreIoStage operation
) {
    if (kind == ProfileStorePublicationKind::Directory) {
        if (operation == ProfileStoreIoStage::RecordVerify)
            return ProfileStoreIoStage::DirectoryVerify;
        if (operation == ProfileStoreIoStage::RecordDestRemove)
            return ProfileStoreIoStage::DirectoryDestRemove;
        if (operation == ProfileStoreIoStage::RecordRename)
            return ProfileStoreIoStage::DirectoryRename;
    }
    return operation;
}

inline const char *ProfileStoreIoDiagnostic(ProfileStoreIoStage stage) {
    switch (stage) {
        case ProfileStoreIoStage::RecordTempSync:
            return "record.sync";
        case ProfileStoreIoStage::RecordTempClose:
            return "record.close";
        case ProfileStoreIoStage::DirectoryTempSync:
            return "directory.sync";
        case ProfileStoreIoStage::DirectoryTempClose:
            return "directory.close";
        case ProfileStoreIoStage::RecordEncodeSize:
            return "record.encode_size";
        case ProfileStoreIoStage::RecordEncode:
            return "record.encode";
        case ProfileStoreIoStage::RecordTempOpenWrite:
            return "record.temp_open_write";
        case ProfileStoreIoStage::RecordTempWrite:
            return "record.temp_write";
        case ProfileStoreIoStage::RecordTempRead:
            return "record.temp_read";
        case ProfileStoreIoStage::RecordTempSize:
            return "record.temp_size";
        case ProfileStoreIoStage::RecordVerify:
            return "record.verify";
        case ProfileStoreIoStage::RecordDestRemove:
            return "record.dest_remove";
        case ProfileStoreIoStage::RecordRename:
            return "record.rename";
        case ProfileStoreIoStage::DirectoryEncode:
            return "directory.encode";
        case ProfileStoreIoStage::DirectoryTempOpenWrite:
            return "directory.temp_open_write";
        case ProfileStoreIoStage::DirectoryTempWrite:
            return "directory.temp_write";
        case ProfileStoreIoStage::DirectoryTempRead:
            return "directory.temp_read";
        case ProfileStoreIoStage::DirectoryTempSize:
            return "directory.temp_size";
        case ProfileStoreIoStage::DirectoryVerify:
            return "directory.verify";
        case ProfileStoreIoStage::DirectoryDestRemove:
            return "directory.dest_remove";
        case ProfileStoreIoStage::DirectoryRename:
            return "directory.rename";
        case ProfileStoreIoStage::DirectoryGenerationMismatch:
            return "directory.generation_mismatch";
        default:
            return "";
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
    virtual ProfileStoreStorageFailure LastFailure() const {
        return ProfileStoreStorageFailure::None;
    }

    // Idempotent ensure-absent operation: success means the path is absent
    // afterward, whether it was absent initially or was removed. A real
    // removal failure for an existing path must return false.
    virtual bool Remove(const char *path) = 0;
    virtual bool Rename(const char *from, const char *to) = 0;
    using Result = CheckedStorage::Result;
    using Outcome = CheckedStorage::Outcome;

    virtual Result CheckedWrite(const char *p, const uint8_t *b, size_t n, CheckedStorage::Kind) {
        return { Write(p, b, n) ? Outcome::Ok : Outcome::Failed, 0, n };
    }

    virtual Result CheckedRead(const char *p, uint8_t *b, size_t n, CheckedStorage::Kind) {
        return { Read(p, b, n) ? Outcome::Ok : Outcome::Failed, 0, n };
    }

    virtual Result Probe(const char *p, size_t *n = nullptr) {
        if (!Exists(p))
            return { Outcome::NotFound, 0, 0 };
        if (n)
            *n = Size(p);
        return { Outcome::Ok, 0, 0 };
    }

    virtual Result CheckedRename(const char *a, const char *b, CheckedStorage::Kind) {
        return { Rename(a, b) ? Outcome::Ok : Outcome::Uncertain, 0, 0 };
    }

    virtual Result CheckedRemove(const char *p) {
        return { Remove(p) ? Outcome::Ok : Outcome::Uncertain, 0, 0 };
    }

    virtual bool ReadRange(const char *, size_t, uint8_t *, size_t) { return false; }

    virtual bool Geometry(CheckedStorage::Geometry &) { return false; }

    virtual bool Enumerate(CheckedStorage::Visitor, void *) { return false; }
};

#endif
