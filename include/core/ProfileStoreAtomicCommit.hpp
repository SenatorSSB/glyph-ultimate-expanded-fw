/* Small, testable primitive for publishing one redundant ProfileStore root. */
#ifndef _CORE_PROFILE_STORE_ATOMIC_COMMIT_HPP
#define _CORE_PROFILE_STORE_ATOMIC_COMMIT_HPP

#include <cstddef>
#include <cstdint>
#include <cstring>

#include "core/ProfileStoreStorage.hpp"

class ProfileStoreAtomicCommit {
  public:
    using Storage = ProfileStoreStorage;

    using Validator = bool (*)(void *context, const uint8_t *bytes, size_t length);

    // A failed temporary write/read/validation/rename never publishes the
    // destination.  ProfileStore uses this for both immutable profile records
    // and the inactive redundant directory root.
    static bool ReplaceVerifiedFile(Storage &storage, const char *temporary,
                                    const char *destination, const uint8_t *bytes,
                                    size_t length, Validator validator, void *context,
                                    ProfileStoreIoStage *failure_stage = nullptr,
                                    ProfileStorePublicationKind kind = ProfileStorePublicationKind::Record) {
        if (failure_stage) *failure_stage = ProfileStoreIoStage::None;
        // One synchronous core0 transaction owns this bounded scratch through
        // validation. Never overwrite the expected bytes during readback: a
        // stale but internally valid record/root is not the requested commit.
        static uint8_t readback[32 + 4096];
        if (length > sizeof(readback)) {
            if (failure_stage) *failure_stage = ProfileStoreStage(kind, ProfileStoreIoStage::RecordVerify);
            return false;
        }
        if (!storage.Write(temporary, bytes, length)) {
            if (failure_stage) { const auto stage = ProfileStoreStage(kind, storage.LastFailure()); *failure_stage = stage == ProfileStoreIoStage::None ? ProfileStoreStage(kind, ProfileStoreStorageFailure::TempWrite) : stage; }
            return false;
        }
        if (!storage.Read(temporary, readback, length)) {
            if (failure_stage) { const auto stage = ProfileStoreStage(kind, storage.LastFailure()); *failure_stage = stage == ProfileStoreIoStage::None ? ProfileStoreStage(kind, ProfileStoreStorageFailure::TempRead) : stage; }
            return false;
        }
        if (std::memcmp(bytes, readback, length) != 0 || !validator(context, readback, length)) {
            if (failure_stage) *failure_stage = ProfileStoreStage(kind, ProfileStoreIoStage::RecordVerify);
            return false;
        }
        // destination is deliberately the inactive redundant root.  A first
        // publication has no destination, so do not require a strict
        // filesystem remove of an absent file. Losing an existing inactive
        // root before a failed rename leaves the current root intact.
        if (storage.Exists(destination) && !storage.Remove(destination)) {
            if (failure_stage) *failure_stage = ProfileStoreStage(kind, ProfileStoreIoStage::RecordDestRemove);
            return false;
        }
        if (!storage.Rename(temporary, destination)) {
            if (failure_stage) *failure_stage = ProfileStoreStage(kind, ProfileStoreIoStage::RecordRename);
            return false;
        }
        return true;
    }

    // The caller selects the inactive redundant root as destination.  Losing
    // that slot before a failed rename leaves the active root intact.
    static bool ReplaceInactiveRoot(Storage &storage, const char *temporary,
                                    const char *destination, const uint8_t *bytes,
                                    size_t length, Validator validator, void *context,
                                    ProfileStoreIoStage *failure_stage = nullptr) {
        return ReplaceVerifiedFile(storage, temporary, destination, bytes, length, validator, context, failure_stage,
                                   ProfileStorePublicationKind::Directory);
    }
};

#endif
