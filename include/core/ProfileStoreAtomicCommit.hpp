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
                                    size_t length, Validator validator, void *context) {
        if (!storage.Write(temporary, bytes, length)) return false;
        // Scratch ownership stays with the caller so firmware can avoid heap use.
        if (!storage.Read(temporary, const_cast<uint8_t *>(bytes), length) ||
            !validator(context, bytes, length)) return false;
        // destination is deliberately the inactive redundant root.  Losing it
        // before a failed rename leaves the current root intact for boot recovery.
        if (!storage.Remove(destination)) return false;
        return storage.Rename(temporary, destination);
    }

    // The caller selects the inactive redundant root as destination.  Losing
    // that slot before a failed rename leaves the active root intact.
    static bool ReplaceInactiveRoot(Storage &storage, const char *temporary,
                                    const char *destination, const uint8_t *bytes,
                                    size_t length, Validator validator, void *context) {
        return ReplaceVerifiedFile(storage, temporary, destination, bytes, length, validator, context);
    }
};

#endif
