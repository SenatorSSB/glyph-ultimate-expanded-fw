#ifndef _CORE_RECOVERY_INITIALIZATION_HPP
#define _CORE_RECOVERY_INITIALIZATION_HPP

#include <config.pb.h>
#include "core/config_validation.hpp"

struct RecoveryInitialization {
    bool config_invalid = true;
    bool storage_available = false;
};

// Recovery is inspection-only. In particular this never calls normal Begin(),
// which can initialize/upgrade a store, migrate, or publish persistent state.
template <typename PersistenceType, typename StoreType>
RecoveryInitialization initialize_recovery(PersistenceType &storage, StoreType &store,
    Config &live, Config &candidate, ConfigSemanticValidator validator) {
    RecoveryInitialization state;
    const bool validator_ready = storage.SetValidator(validator);
    state.storage_available = storage.IsAvailable();
    if (validator_ready && state.storage_available &&
        storage.LoadConfigChecked(candidate) == PersistenceType::LoadResult::Loaded) {
        live = candidate;
        state.config_invalid = false;
    }
    if (state.storage_available) {
        const uint32_t incarnation = !state.config_invalid &&
            live.ultimate_profile_store_format == StoreType::kCompactConfigFormat
            ? live.ultimate_profile_store_incarnation : 0;
        const uint32_t required_root_format = !state.config_invalid
            ? live.ultimate_profile_root_format : 0;
        store.BeginRecovery(incarnation, required_root_format);
    }
    return state;
}
#endif
