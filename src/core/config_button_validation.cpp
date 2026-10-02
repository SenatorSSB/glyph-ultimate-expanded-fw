/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 */

#include "core/config_button_validation.hpp"

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#include <type_traits>

namespace {

constexpr Button kSupportedButtons[] = {
    BTN_LF1,  BTN_LF2,  BTN_LF3,  BTN_LF4,  BTN_LF5,  BTN_LF6,  BTN_LF7,  BTN_LF8,
    BTN_LF9,  BTN_LF10, BTN_LF11, BTN_LF12, BTN_LF13, BTN_LF14, BTN_LF15, BTN_LF16,
    BTN_RF1,  BTN_RF2,  BTN_RF3,  BTN_RF4,  BTN_RF5,  BTN_RF6,  BTN_RF7,  BTN_RF8,
    BTN_RF9,  BTN_RF10, BTN_RF11, BTN_RF12, BTN_RF13, BTN_RF14, BTN_RF15, BTN_RF16,
    BTN_LT1,  BTN_LT2,  BTN_LT3,  BTN_LT4,  BTN_LT5,  BTN_LT6,  BTN_LT7,  BTN_LT8,
    BTN_RT1,  BTN_RT2,  BTN_RT3,  BTN_RT4,  BTN_RT5,  BTN_RT6,  BTN_RT7,  BTN_RT8,
    BTN_MB1,  BTN_MB2,  BTN_MB3,  BTN_MB4,  BTN_MB5,  BTN_MB6,  BTN_MB7,  BTN_MB8,
    BTN_MB9,  BTN_MB10, BTN_MB11, BTN_MB12,
};

static_assert(std::is_enum<Button>::value, "Button must remain a generated enum");
static_assert(sizeof(Button) == sizeof(int), "selected Pico enum ABI must match int width");
static_assert(sizeof(Button) == 4, "selected Pico Button representation must remain four bytes");
static_assert(std::numeric_limits<unsigned int>::digits == sizeof(Button) * 8,
              "Button object representation must match an unsigned integer width");
static_assert(sizeof(kSupportedButtons) / sizeof(kSupportedButtons[0]) == 60,
              "the supported Button domain must remain complete");

constexpr bool button_domain_is_exact() {
    for (size_t i = 0; i < sizeof(kSupportedButtons) / sizeof(kSupportedButtons[0]); ++i) {
        if (static_cast<unsigned>(kSupportedButtons[i]) != i + 1) {
            return false;
        }
    }
    return true;
}

static_assert(button_domain_is_exact(), "Button IDs must be exactly BTN_LF1..BTN_MB12 (1..60)");

bool valid_button(const Button &button) {
    // Do not evaluate decoder-controlled enum storage as Button until its
    // complete object representation matches one of the named enumerators.
    // The selected Pico ABI stores these enums as four bytes, while Nanopb's
    // IS_8 option controls the wire field width. Comparing object bytes avoids
    // reading an invalid enum value as a typed enum or assuming host endianness.
    for (const Button supported : kSupportedButtons) {
        if (std::memcmp(&button, &supported, sizeof(Button)) == 0) {
            return true;
        }
    }
    return false;
}

bool is_remap_disable(const Button &button) {
    const Button disabled = BTN_UNSPECIFIED;
    return std::memcmp(&button, &disabled, sizeof(Button)) == 0;
}

template <typename Array, typename Count>
bool count_fits(const Array &, Count count, size_t capacity) {
    return static_cast<size_t>(count) <= capacity;
}

bool all_extents_fit(const Config &config) {
    if (!count_fits(config.game_mode_configs, config.game_mode_configs_count,
                    sizeof(config.game_mode_configs) / sizeof(config.game_mode_configs[0])) ||
        !count_fits(config.communication_backend_configs,
                    config.communication_backend_configs_count,
                    sizeof(config.communication_backend_configs) /
                        sizeof(config.communication_backend_configs[0])) ||
        !count_fits(config.custom_modes, config.custom_modes_count,
                    sizeof(config.custom_modes) / sizeof(config.custom_modes[0])) ||
        !count_fits(config.keyboard_modes, config.keyboard_modes_count,
                    sizeof(config.keyboard_modes) / sizeof(config.keyboard_modes[0]))) {
        return false;
    }

    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        if (!count_fits(mode.socd_pairs, mode.socd_pairs_count,
                        sizeof(mode.socd_pairs) / sizeof(mode.socd_pairs[0])) ||
            !count_fits(mode.button_remapping, mode.button_remapping_count,
                        sizeof(mode.button_remapping) / sizeof(mode.button_remapping[0])) ||
            !count_fits(mode.activation_binding, mode.activation_binding_count,
                        sizeof(mode.activation_binding) / sizeof(mode.activation_binding[0]))) {
            return false;
        }
    }

    for (size_t i = 0; i < config.communication_backend_configs_count; ++i) {
        const CommunicationBackendConfig &backend = config.communication_backend_configs[i];
        if (!count_fits(backend.activation_binding, backend.activation_binding_count,
                        sizeof(backend.activation_binding) / sizeof(backend.activation_binding[0]))) {
            return false;
        }
    }

    for (size_t i = 0; i < config.custom_modes_count; ++i) {
        const CustomModeConfig &mode = config.custom_modes[i];
        if (!count_fits(mode.digital_button_mappings, mode.digital_button_mappings_count,
                        sizeof(mode.digital_button_mappings) / sizeof(mode.digital_button_mappings[0])) ||
            !count_fits(mode.stick_direction_mappings, mode.stick_direction_mappings_count,
                        sizeof(mode.stick_direction_mappings) / sizeof(mode.stick_direction_mappings[0])) ||
            !count_fits(mode.analog_trigger_mappings, mode.analog_trigger_mappings_count,
                        sizeof(mode.analog_trigger_mappings) / sizeof(mode.analog_trigger_mappings[0])) ||
            !count_fits(mode.modifiers, mode.modifiers_count,
                        sizeof(mode.modifiers) / sizeof(mode.modifiers[0])) ||
            !count_fits(mode.button_combo_mappings, mode.button_combo_mappings_count,
                        sizeof(mode.button_combo_mappings) / sizeof(mode.button_combo_mappings[0]))) {
            return false;
        }
        for (size_t j = 0; j < mode.modifiers_count; ++j) {
            const AnalogModifier &modifier = mode.modifiers[j];
            if (!count_fits(modifier.buttons, modifier.buttons_count,
                            sizeof(modifier.buttons) / sizeof(modifier.buttons[0]))) {
                return false;
            }
        }
        for (size_t j = 0; j < mode.button_combo_mappings_count; ++j) {
            const ButtonComboMapping &combo = mode.button_combo_mappings[j];
            if (!count_fits(combo.buttons, combo.buttons_count,
                            sizeof(combo.buttons) / sizeof(combo.buttons[0]))) {
                return false;
            }
        }
    }

    for (size_t i = 0; i < config.keyboard_modes_count; ++i) {
        const KeyboardModeConfig &mode = config.keyboard_modes[i];
        if (!count_fits(mode.buttons_to_keycodes, mode.buttons_to_keycodes_count,
                        sizeof(mode.buttons_to_keycodes) / sizeof(mode.buttons_to_keycodes[0]))) {
            return false;
        }
    }
    return true;
}

bool valid_button_list(const Button *buttons, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        if (!valid_button(buttons[i])) {
            return false;
        }
    }
    return true;
}

}  // namespace

bool validate_config_button_bindings(const Config &config) {
    // Validate every count before inspecting any nested element.
    if (!all_extents_fit(config)) {
        return false;
    }

    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        if (!valid_button_list(mode.activation_binding, mode.activation_binding_count)) {
            return false;
        }
        for (size_t j = 0; j < mode.button_remapping_count; ++j) {
            const ButtonRemap &remap = mode.button_remapping[j];
            if (!valid_button(remap.physical_button)) {
                return false;
            }
            // BTN_UNSPECIFIED is the source-defined remap disable operation.
            if (!is_remap_disable(remap.activates) && !valid_button(remap.activates)) {
                return false;
            }
        }
        for (size_t j = 0; j < mode.socd_pairs_count; ++j) {
            const SocdPair &pair = mode.socd_pairs[j];
            if (!valid_button(pair.button_dir1) || !valid_button(pair.button_dir2)) {
                return false;
            }
        }
    }

    for (size_t i = 0; i < config.communication_backend_configs_count; ++i) {
        if (!valid_button_list(config.communication_backend_configs[i].activation_binding,
                               config.communication_backend_configs[i].activation_binding_count)) {
            return false;
        }
    }

    for (size_t i = 0; i < config.custom_modes_count; ++i) {
        const CustomModeConfig &mode = config.custom_modes[i];
        if (!valid_button_list(mode.digital_button_mappings, mode.digital_button_mappings_count) ||
            !valid_button_list(mode.stick_direction_mappings, mode.stick_direction_mappings_count)) {
            return false;
        }
        for (size_t j = 0; j < mode.modifiers_count; ++j) {
            if (!valid_button_list(mode.modifiers[j].buttons, mode.modifiers[j].buttons_count)) {
                return false;
            }
        }
        for (size_t j = 0; j < mode.button_combo_mappings_count; ++j) {
            if (!valid_button_list(mode.button_combo_mappings[j].buttons,
                                   mode.button_combo_mappings[j].buttons_count)) {
                return false;
            }
        }
        for (size_t j = 0; j < mode.analog_trigger_mappings_count; ++j) {
            if (!valid_button(mode.analog_trigger_mappings[j].button)) {
                return false;
            }
        }
    }

    for (size_t i = 0; i < config.keyboard_modes_count; ++i) {
        const KeyboardModeConfig &mode = config.keyboard_modes[i];
        for (size_t j = 0; j < mode.buttons_to_keycodes_count; ++j) {
            if (!valid_button(mode.buttons_to_keycodes[j].button)) {
                return false;
            }
        }
    }
    return true;
}
