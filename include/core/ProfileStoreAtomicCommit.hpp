/* Small, testable primitive for publishing one redundant ProfileStore root. */
#ifndef _CORE_PROFILE_STORE_ATOMIC_COMMIT_HPP
#define _CORE_PROFILE_STORE_ATOMIC_COMMIT_HPP

#include <cstddef>
#include <cstdint>

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
                                    ProfileStoreIoStage *failure_stage = nullptr) {
        if (failure_stage) *failure_stage = ProfileStoreIoStage::None;
        if (!storage.Write(temporary, bytes, length)) {
            if (failure_stage) *failure_stage = storage.LastFailureStage() == ProfileStoreIoStage::None
                ? ProfileStoreIoStage::RecordTempWrite : storage.LastFailureStage();
            return false;
        }
        // Scratch ownership stays with the caller so firmware can avoid heap use.
        if (!storage.Read(temporary, const_cast<uint8_t *>(bytes), length)) {
            if (failure_stage) *failure_stage = storage.LastFailureStage() == ProfileStoreIoStage::None
                ? ProfileStoreIoStage::RecordTempRead : storage.LastFailureStage();
            return false;
        }
        if (!validator(context, bytes, length)) {
            if (failure_stage) *failure_stage = ProfileStoreIoStage::RecordVerify;
            return false;
        }
        // destination is deliberately the inactive redundant root.  A first
        // publication has no destination, so do not require a strict
        // filesystem remove of an absent file. Losing an existing inactive
        // root before a failed rename leaves the current root intact.
        if (storage.Exists(destination) && !storage.Remove(destination)) {
            if (failure_stage) *failure_stage = ProfileStoreIoStage::RecordDestRemove;
            return false;
        }
        if (!storage.Rename(temporary, destination)) {
            if (failure_stage) *failure_stage = ProfileStoreIoStage::RecordRename;
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
        return ReplaceVerifiedFile(storage, temporary, destination, bytes, length, validator, context, failure_stage);
    }
};

#endif
