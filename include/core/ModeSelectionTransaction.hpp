#ifndef _CORE_MODE_SELECTION_TRANSACTION_HPP
#define _CORE_MODE_SELECTION_TRANSACTION_HPP

#include <config.pb.h>
#include <cstddef>
#include <cstdint>
#include "core/config_validation.hpp"

// Only written after checked Config publication. Consumed by backend startup;
// unlike the older menu selector this target never requests a second save.
constexpr uint32_t kCommittedModeDestination = 0x4d445354u;

// Consume even an invalid target before ordinary selectors can interpret the
// old menu scratch fields. A valid target must exactly match checked durable
// Config; no one-shot value can edit Config on boot.
inline bool consume_committed_mode_destination(volatile uint32_t *scratch,
    bool watchdog_reboot, const Config &config, CommunicationBackendConfig &destination) {
    if (scratch[2] != kCommittedModeDestination) return false;
    const uint32_t backend = scratch[0], mode = scratch[1];
    scratch[0] = scratch[1] = scratch[2] = 0;
    if (!watchdog_reboot || backend == 0 || backend > config.communication_backend_configs_count ||
        mode == 0 || mode > config.game_mode_configs_count) return false;
    const auto &saved = config.communication_backend_configs[backend - 1];
    const bool usb = saved.backend_id == COMMS_BACKEND_DINPUT || saved.backend_id == COMMS_BACKEND_XINPUT ||
        saved.backend_id == COMMS_BACKEND_NINTENDO_SWITCH;
    const uint32_t selected = usb ? config.default_usb_backend_config : config.default_backend_config;
    if (selected != backend || saved.default_mode_config != mode ||
        saved.backend_id == COMMS_BACKEND_CONFIGURATOR || saved.backend_id == COMMS_BACKEND_UNSPECIFIED) return false;
    destination = saved;
    return true;
}

enum class ModeDestinationResult { Unchanged, Saved, Refused };

template <typename PersistenceType>
__attribute__((noinline)) bool validate_mode_destination(PersistenceType &storage, const Config &candidate) {
    ConfigValidationError error;
    return storage.ValidateConfig(candidate, error);
}

template <typename PersistenceType>
ModeDestinationResult persist_mode_destination(PersistenceType &storage, Config &candidate,
    CommunicationBackendId backend, size_t mode_index, size_t &backend_index) {
    if (!storage.IsAvailable() ||
        storage.LoadConfigChecked(candidate) != PersistenceType::LoadResult::Loaded ||
        mode_index >= candidate.game_mode_configs_count) return ModeDestinationResult::Refused;
    backend_index = candidate.communication_backend_configs_count;
    for (size_t i = 0; i < candidate.communication_backend_configs_count; ++i) {
        if (candidate.communication_backend_configs[i].backend_id == backend) {
            backend_index = i;
            break;
        }
    }
    if (backend_index == candidate.communication_backend_configs_count ||
        backend == COMMS_BACKEND_CONFIGURATOR || backend == COMMS_BACKEND_UNSPECIFIED)
        return ModeDestinationResult::Refused;
    const bool usb = backend == COMMS_BACKEND_DINPUT || backend == COMMS_BACKEND_XINPUT ||
        backend == COMMS_BACKEND_NINTENDO_SWITCH;
    auto &selected_backend = candidate.communication_backend_configs[backend_index];
    auto &default_backend = usb ? candidate.default_usb_backend_config : candidate.default_backend_config;
    if (default_backend == backend_index + 1 && selected_backend.default_mode_config == mode_index + 1)
        return ModeDestinationResult::Unchanged;
    const uint32_t generation = storage.ConfigGeneration(candidate);
    default_backend = backend_index + 1;
    selected_backend.default_mode_config = mode_index + 1;
    if (!validate_mode_destination(storage, candidate)) return ModeDestinationResult::Refused;
    return storage.SaveConfigIfGenerationMatches(candidate, generation) == PersistenceType::SaveResult::Saved
        ? ModeDestinationResult::Saved : ModeDestinationResult::Refused;
}
#endif
