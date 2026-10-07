#include "core/config_validation.hpp"
#include "core/config_button_validation.hpp"

#include <cstdio>
#include <cstring>
#include <type_traits>

namespace {

template <typename T, size_t N, typename Count>
bool fits(const T (&)[N], Count count) {
    return static_cast<size_t>(count) <= N;
}

template <typename... Args>
bool reference_error(ConfigValidationError &error, const char *format, Args... args) {
    const int length = std::snprintf(error.message, sizeof(error.message), format, args...);
    error.length = length > 0 && static_cast<size_t>(length) < sizeof(error.message)
        ? static_cast<size_t>(length) : sizeof(error.message) - 1;
    return false;
}

}  // namespace

bool validate_config_extents(const Config &config) {
    if (!fits(config.game_mode_configs, config.game_mode_configs_count) ||
        !fits(config.communication_backend_configs, config.communication_backend_configs_count) ||
        !fits(config.custom_modes, config.custom_modes_count) ||
        !fits(config.keyboard_modes, config.keyboard_modes_count) ||
        !fits(config.rgb_configs, config.rgb_configs_count)) {
        return false;
    }
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        if (!fits(mode.socd_pairs, mode.socd_pairs_count) ||
            !fits(mode.button_remapping, mode.button_remapping_count) ||
            !fits(mode.activation_binding, mode.activation_binding_count) ||
            !fits(mode.applicable_backends, mode.applicable_backends_count) ||
            !fits(mode.menu_button_icon, mode.menu_button_icon_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.communication_backend_configs_count; ++i) {
        const CommunicationBackendConfig &backend = config.communication_backend_configs[i];
        if (!fits(backend.activation_binding, backend.activation_binding_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.custom_modes_count; ++i) {
        const CustomModeConfig &mode = config.custom_modes[i];
        if (!fits(mode.digital_button_mappings, mode.digital_button_mappings_count) ||
            !fits(mode.stick_direction_mappings, mode.stick_direction_mappings_count) ||
            !fits(mode.analog_trigger_mappings, mode.analog_trigger_mappings_count) ||
            !fits(mode.modifiers, mode.modifiers_count) ||
            !fits(mode.button_combo_mappings, mode.button_combo_mappings_count)) {
            return false;
        }
        for (size_t j = 0; j < mode.modifiers_count; ++j) {
            if (!fits(mode.modifiers[j].buttons, mode.modifiers[j].buttons_count)) {
                return false;
            }
        }
        for (size_t j = 0; j < mode.button_combo_mappings_count; ++j) {
            if (!fits(mode.button_combo_mappings[j].buttons,
                      mode.button_combo_mappings[j].buttons_count)) {
                return false;
            }
        }
    }
    for (size_t i = 0; i < config.keyboard_modes_count; ++i) {
        if (!fits(config.keyboard_modes[i].buttons_to_keycodes,
                  config.keyboard_modes[i].buttons_to_keycodes_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.rgb_configs_count; ++i) {
        if (!fits(config.rgb_configs[i].button_colors, config.rgb_configs[i].button_colors_count)) {
            return false;
        }
    }
    return true;
}

bool validate_config_semantics(const Config &config, ConfigValidationError &error) {
    error = ConfigValidationError{};
    // Complete bounds precede both semantic callbacks and every nested walk.
    // Keep the existing binding error and its wire length for structural failures.
    if (!validate_config_extents(config) || !validate_config_button_bindings(config)) {
        static const char message[] = "Config contains an invalid button binding";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }

    if (config.default_backend_config > config.communication_backend_configs_count) {
        return reference_error(error,
            "Default backend ID is %d but only %d backend configs are defined",
            static_cast<uint8_t>(config.default_backend_config),
            static_cast<uint8_t>(config.communication_backend_configs_count));
    }
    for (size_t i = 0; i < config.communication_backend_configs_count; ++i) {
        const uint8_t default_mode_id = config.communication_backend_configs[i].default_mode_config;
        if (default_mode_id > config.game_mode_configs_count) {
            return reference_error(error,
                "Default mode ID is %d for backend %d but only %d modes are defined",
                default_mode_id, static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.game_mode_configs_count));
        }
    }

    static_assert(std::is_same<decltype(GameModeConfig::custom_mode_config), uint32_t>::value,
                  "custom reference must retain its authoritative decoded width");
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        const uint8_t keyboard_mode_id = mode.keyboard_mode_config;
        const uint32_t custom_mode_id = mode.custom_mode_config;
        if (keyboard_mode_id > 0 && mode.mode_id != MODE_KEYBOARD) {
            return reference_error(error,
                "keyboard_mode_id is set for game mode %d but mode_id is not MODE_KEYBOARD",
                static_cast<uint8_t>(i) + 1);
        }
        if (custom_mode_id > 0 && mode.mode_id != MODE_CUSTOM) {
            return reference_error(error,
                "custom_mode_id is set for game mode %d but mode_id is not MODE_CUSTOM",
                static_cast<uint8_t>(i) + 1);
        }
        if (keyboard_mode_id > config.keyboard_modes_count) {
            return reference_error(error,
                "Keyboard mode ID %d is for game mode %d but only %d keyboard modes are defined",
                keyboard_mode_id, static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.keyboard_modes_count));
        }
        if (custom_mode_id > config.custom_modes_count) {
            return reference_error(error,
                "Custom mode ID %lu is for game mode config %d but only %d custom modes are defined",
                static_cast<unsigned long>(custom_mode_id), static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.custom_modes_count));
        }
    }
    return true;
}
