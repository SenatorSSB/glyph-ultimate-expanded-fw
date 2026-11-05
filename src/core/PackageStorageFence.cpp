#include "core/PackageStorageFence.hpp"
#include <limits>

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
namespace PackageStorageFence {
namespace {
struct Authority {
    const void *owner = nullptr;
    Authorize authorize = nullptr;
    void *context = nullptr;
    const void *handle_owner = nullptr;
    uint64_t token = 0;
    WriteKind kind = WriteKind::Legacy;
    uint16_t handles = 0;
    Classification classification = Classification::Unclassified;
    bool mount_attempted = false;
    bool mounted = false;
    bool boot_failed = false;
    bool fenced = false;
} authority;
bool healthy() {
    return authority.classification == Classification::LegacyHealthy ||
           authority.classification == Classification::ManagedHealthy;
}
void revoke() {
    authority.owner = nullptr;
    authority.authorize = nullptr;
    authority.context = nullptr;
    authority.token = 0;
    authority.kind = WriteKind::Legacy;
}
}
void BeginMountAttempt() {
    // A second attempt is not recovery authority. Even a later successful
    // mount cannot clear a failed configuration/mount in the same boot.
    if (authority.mount_attempted || authority.handles) authority.boot_failed = true;
    authority.mount_attempted = true;
    authority.mounted = false;
    authority.classification = Classification::Unclassified;
    revoke();
}
void FinishMountAttempt(bool configuration_ok, bool mounted) {
    if (!authority.mount_attempted || !configuration_ok || !mounted)
        authority.boot_failed = true;
    authority.mounted = configuration_ok && mounted;
}
bool Available() { return authority.mounted && !authority.boot_failed; }
bool MutationFenced() { return !Available() || authority.fenced || !healthy(); }
void Fence() {
    authority.fenced = true;
    revoke();
}
void Classify(Classification classification) {
    // No public observation, query, or re-entry clears a boot/transaction fence.
    if (authority.owner || authority.handles) {
        Fence();
        return;
    }
    authority.classification = classification;
    if (classification == Classification::Unresolved ||
        classification == Classification::Unsupported) Fence();
}
bool BeginWrite(const void *owner, WriteKind kind, uint64_t token, Authorize authorize, void *context) {
    if ((kind != WriteKind::Legacy && kind != WriteKind::Package) ||
        (kind == WriteKind::Package && !token) ||
        !owner || !authorize || authority.owner || authority.handles || MutationFenced())
        return false;
    authority.owner = owner;
    authority.token = token;
    authority.kind = kind;
    authority.authorize = authorize;
    authority.context = context;
    return true;
}
void EndWrite(const void *owner) {
    if (!owner || owner != authority.owner) { Fence(); return; }
    if (authority.handles) Fence();
    revoke();
}
bool Permit(CheckedStorage::Operation operation, const char *path, const char *destination) {
    if (MutationFenced() || !authority.owner || !authority.authorize) return false;
    const auto *owner = authority.owner;
    const auto token = authority.token;
    const auto kind = authority.kind;
    return authority.authorize(authority.context, kind, token, operation, path, destination) &&
           !MutationFenced() && authority.owner == owner && authority.token == token && authority.kind == kind;
}
const void *WriteOwner() { return authority.owner; }
bool PermitLegacy(CheckedStorage::Operation operation,const char *path,const char *destination) {
    return authority.kind==WriteKind::Legacy&&Permit(operation,path,destination);
}
bool IsPackageWriter(const void *owner, uint64_t token) {
    return owner && owner == authority.owner && token && token == authority.token &&
           authority.kind == WriteKind::Package && !MutationFenced();
}
bool RetainHandle(const void *owner) {
    if (!owner || owner != authority.owner || MutationFenced() ||
        authority.handles == std::numeric_limits<uint16_t>::max()) {
        Fence();
        return false;
    }
    ++authority.handles;
    authority.handle_owner = owner;
    return true;
}
void ReleaseHandle(const void *owner) {
    // Revocation deliberately clears the active owner; cleanup still releases
    // the handle count, and never restores the revoked scope.
    if (!owner || owner != authority.handle_owner || !authority.handles) { Fence(); return; }
    --authority.handles;
    if (!authority.handles) authority.handle_owner = nullptr;
}
bool PermitHandle(const void *owner, CheckedStorage::Operation operation, const char *path) {
    return owner && owner == authority.owner && Permit(operation, path);
}
}

#endif
