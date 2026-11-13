#pragma once

#include "core/ProfileStore.hpp"
#include "core/PackageOwnership.hpp"
#include "core/ModeSelectionTransaction.hpp"

namespace profile_selection {
bool IsUsb(CommunicationBackendId backend);
bool Eligible(const GameModeConfig &mode, CommunicationBackendId backend);
bool NativeTemplate(const GameModeConfig &mode);

struct Target {
    uint32_t profile_id = 0; // zero denotes an ordinary Config row
    uint8_t mode_index = 0;
};
static_assert(sizeof(Config::game_mode_configs) / sizeof(GameModeConfig) == 30, "bounded Config row capacity");
constexpr size_t kMaxTargets = ProfileStore::kMaxEntries + 30;
static_assert(kMaxTargets < 256, "menu keys represent list indices, never IDs");
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
// Only a row already bound to this record can be a normal profile destination.
bool BoundPair(const Config &, const ProfileStore::Entry &, size_t row, CommunicationBackendId);
#endif
const ProfileStore::Entry *FindEntry(const ProfileStore &store, uint32_t id);
size_t BuildTargets(const Config &config, const ProfileStore &store,
    CommunicationBackendId backend, Target *targets, size_t capacity);

// Single producer (menu/core1), single consumer (application/core0). A pending
// ID stays occupied throughout validation/publication. Zero is never selectable.
bool Request(uint32_t id);
bool Request(uint32_t id, CommunicationBackendId route);
CommunicationBackendId RequestedBackend();
uint32_t Pending();
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
uint32_t GamecubeSelectionPending();
#endif
void Complete();

// No additional Config/profile owner. The compact Config's unused embedded
// slot is borrowed only while reading/validating the selected native body.
template <typename PersistenceType, typename StoreType>
__attribute__((noinline)) ModeDestinationResult Persist(PersistenceType &storage,
    StoreType &store, Config &candidate, CommunicationBackendId backend,
    uint32_t id, size_t preferred_mode, size_t &mode_index, size_t &backend_index) {
    if (!id || !storage.IsAvailable() || storage.IsMutationFenced() ||
        !store.IsReady() || store.MigrationPending() || store.IsReadOnlyRecovery() || store.IsTransactionUncertain() ||
        storage.LoadConfigChecked(candidate) != PersistenceType::LoadResult::Loaded ||
        candidate.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat ||
        candidate.ultimate_profiles_count != 0 ||
        candidate.ultimate_profile_store_incarnation != store.Incarnation())
        return ModeDestinationResult::Refused;
#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    const auto *entry = FindEntry(store, id);
    if (!entry) return ModeDestinationResult::Refused;
    // Never substitute another template or change a row reference. There must
    // be one matching pair on the same backend when the checked save starts.
    mode_index = candidate.game_mode_configs_count;
    for (size_t i = 0; i < candidate.game_mode_configs_count; ++i) {
        if (!BoundPair(candidate, *entry, i, backend)) continue;
        if (mode_index != candidate.game_mode_configs_count) return ModeDestinationResult::Refused;
        mode_index = i;
    }
    if (mode_index == candidate.game_mode_configs_count) return ModeDestinationResult::Refused;
#endif
    const uint32_t generation = storage.ConfigGeneration(candidate);
    const auto read = store.Read(id, candidate.ultimate_profiles[0]);
    if ((read != ProfileStore::Status::Ok && read != ProfileStore::Status::RecoveredPrevious) ||
        candidate.ultimate_profiles[0].schema_version != ultimate_native::kSchema)
        return ModeDestinationResult::Refused;

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
    const bool matched = read == ProfileStore::Status::Ok &&
        ultimate_native::ContextMatches(ultimate_native::CandidateView(), candidate.game_mode_configs[mode_index]);
    candidate.ultimate_profiles[0] = UltimateProfile_init_default;
    if (!matched) return ModeDestinationResult::Refused;
#else
    mode_index = candidate.game_mode_configs_count;
    // Prefer the active context; otherwise resolve an explicitly matching
    // existing template. No preprocessing field is ever synthesized or edited.
    for (size_t step = 0; step <= candidate.game_mode_configs_count; ++step) {
        const size_t i = step == 0 ? preferred_mode : step - 1;
        if (i >= candidate.game_mode_configs_count) continue;
        const auto &mode = candidate.game_mode_configs[i];
        if (NativeTemplate(mode) && Eligible(mode, backend) &&
            ultimate_native::ContextMatches(ultimate_native::CandidateView(), mode)) {
            mode_index = i;
            break;
        }
    }
    candidate.ultimate_profiles[0] = UltimateProfile_init_default;
    if (mode_index == candidate.game_mode_configs_count) return ModeDestinationResult::Refused;
#endif
    backend_index = candidate.communication_backend_configs_count;
    for (size_t i = 0; i < candidate.communication_backend_configs_count; ++i) {
        if (candidate.communication_backend_configs[i].backend_id == backend) {
            backend_index = i;
            break;
        }
    }
    if (backend_index == candidate.communication_backend_configs_count ||
        backend == COMMS_BACKEND_UNSPECIFIED || backend == COMMS_BACKEND_CONFIGURATOR)
        return ModeDestinationResult::Refused;
#if !defined(GLYPH_PACKAGE_V1) || !GLYPH_PACKAGE_V1
    auto &mode = candidate.game_mode_configs[mode_index];
    mode.ultimate_profile_id = id;
    mode.ultimate_profile_engine = 1;
    mode.ultimate_profile_config = 0;
#endif
    (IsUsb(backend) ? candidate.default_usb_backend_config : candidate.default_backend_config) = backend_index + 1;
    candidate.communication_backend_configs[backend_index].default_mode_config = mode_index + 1;
    if (!validate_mode_destination(storage, candidate)) return ModeDestinationResult::Refused;
    return storage.SaveConfigIfGenerationMatches(candidate, generation) == PersistenceType::SaveResult::Saved
        ? ModeDestinationResult::Saved : ModeDestinationResult::Refused;
}
} // namespace profile_selection
