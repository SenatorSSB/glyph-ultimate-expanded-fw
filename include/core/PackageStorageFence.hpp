#ifndef GLYPH_PACKAGE_STORAGE_FENCE_HPP
#define GLYPH_PACKAGE_STORAGE_FENCE_HPP
#include "core/CheckedStorage.hpp"

// Synchronous core0 authority. Classification is supplied only after the
// package namespace observer has completed its no-write proof. The observer
// must not acquire a writer, and no writer callback may enter storage.
namespace PackageStorageFence {
enum class Classification : uint8_t {
    Unclassified, LegacyHealthy, ManagedHealthy, Unresolved, Unsupported
};
enum class WriteKind : uint8_t { Legacy, Package };
using Authorize = bool (*)(void *, WriteKind, uint64_t, CheckedStorage::Operation,
                          const char *, const char *);
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
constexpr bool kEnabled = true;
void BeginMountAttempt();
void FinishMountAttempt(bool configuration_ok, bool mounted);
void Classify(Classification);
bool Available();
bool MutationFenced();
void Fence();
bool BeginWrite(const void *owner, WriteKind, uint64_t token, Authorize, void *context);
bool IsPackageWriter(const void *owner, uint64_t token);
void EndWrite(const void *owner);
bool Permit(CheckedStorage::Operation, const char *path,
            const char *destination = nullptr);
// An opened writable handle belongs to exactly one scope. A later scope
// cannot start until every handle from the previous scope is released.
const void *WriteOwner();
bool RetainHandle(const void *owner);
void ReleaseHandle(const void *owner);
bool PermitHandle(const void *owner, CheckedStorage::Operation, const char *);
#else
constexpr bool kEnabled = false;
inline void BeginMountAttempt() {}
inline void FinishMountAttempt(bool, bool) {}
inline void Classify(Classification) {}
inline bool Available() { return true; }
inline bool MutationFenced() { return false; }
inline void Fence() {}
inline bool BeginWrite(const void *, WriteKind, uint64_t, Authorize, void *) { return false; }
inline bool IsPackageWriter(const void *, uint64_t) { return false; }
inline void EndWrite(const void *) {}
inline bool Permit(CheckedStorage::Operation, const char *, const char * = nullptr) { return true; }
inline const void *WriteOwner() { return nullptr; }
inline bool RetainHandle(const void *) { return true; }
inline void ReleaseHandle(const void *) {}
inline bool PermitHandle(const void *, CheckedStorage::Operation, const char *) { return true; }
#endif

}
#endif
