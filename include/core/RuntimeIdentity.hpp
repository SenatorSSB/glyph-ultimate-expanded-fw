#pragma once

#include "core/CommunicationBackend.hpp"
#include "core/ProfileStore.hpp"
#include "core/RuntimeIdentityWire.hpp"
#include "core/RuntimeProfileDigest.hpp"
#include "modes/Ultimate.hpp"

namespace runtime_identity {
// Caller supplies ONLY the actual current primary, on the owning core0 path.
// Active payload/Ultimate configuration cannot be replaced during this call.
inline Snapshot Observe(CommunicationBackend *primary, const Config &config,
                        const ProfileStore &store, const Ultimate &ultimate) {
    Snapshot s;
    if (!primary) return s;
    s.backend = static_cast<uint8_t>(primary->BackendId());
    if (s.backend == COMMS_BACKEND_CONFIGURATOR) { s.status = Status::Configurator; return s; }
    const InputMode *mode = primary->ObservedGameMode();
    if (!mode) { s.status = Status::NoMode; return s; }
    if (mode != &ultimate) { s.status = Status::NonUltimate; return s; }
    const GameModeConfig *context = ultimate.ConfigPointer();
    if (config.game_mode_configs_count > sizeof(config.game_mode_configs)/sizeof(config.game_mode_configs[0])) {
        s.status = Status::ContextUnavailable; return s;
    }
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        if (context == &config.game_mode_configs[i]) {
            s.row = static_cast<uint16_t>(i+1);
            s.requested = context->ultimate_profile_id;
            break;
        }
    }
    if (!s.row || context->mode_id != MODE_ULTIMATE) { s.status = Status::ContextUnavailable; return s; }
    const UltimateProfile *profile = ultimate.SelectedProfile();
    if (!profile) { s.status = Status::SourceFallback; return s; }
    if (!config.ultimate_profile_store_format) {
        if (config.ultimate_profiles_count <= sizeof(config.ultimate_profiles)/sizeof(config.ultimate_profiles[0])) {
            for (size_t i = 0; i < config.ultimate_profiles_count; ++i) {
                if (profile == &config.ultimate_profiles[i]) { s.status = Status::EmbeddedLegacy; return s; }
            }
        }
        s.status = Status::ObjectMismatch; return s;
    }
    if (config.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat) {
        s.status = Status::StoreUnavailable; return s;
    }
    if (!store.IsReady() || store.IsReadOnlyRecovery() || !store.Incarnation()) {
        s.status = Status::StoreUnavailable; return s;
    }
    if (profile != store.ActiveProfile() || !store.ActiveId() || !store.ActiveRevision()) {
        s.status = Status::ObjectMismatch; return s;
    }
    if (!PayloadDigest(*profile, s.digest)) { s.status = Status::DigestFailure; return s; }
    if (primary->ObservedGameMode() != mode || ultimate.SelectedProfile() != profile) {
        std::memset(s.digest, 0, sizeof(s.digest));
        s.status = Status::SnapshotUnavailable; return s;
    }
    s.incarnation = store.Incarnation(); s.id = store.ActiveId();
    s.revision = store.ActiveRevision(); s.schema = profile->schema_version;
    s.status = Status::Persisted;
    return s;
}
} // namespace runtime_identity
