/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 */

#include "core/config_rgb_target_validation.hpp"

#include <climits>
#include <cstring>
#include <limits>
#include <type_traits>

namespace {
using ButtonStorage = std::underlying_type<Button>::type;
static_assert(std::is_enum<Button>::value, "Button must remain a generated enum");
static_assert(CHAR_BIT == 8, "RGB target validation requires eight-bit bytes");
static_assert(std::is_unsigned<ButtonStorage>::value,
              "Button storage must be unsigned");
static_assert(std::numeric_limits<ButtonStorage>::digits == sizeof(Button) * CHAR_BIT,
              "Button storage must have no padding bits");
static_assert(sizeof(Button) == 1 || sizeof(Button) == 4,
              "Button representation must match a verified one- or four-byte ABI");

bool is_physical_target(const Button &button, const Button *targets, size_t count) {
    const Button absent = BTN_UNSPECIFIED;
    if (std::memcmp(&button, &absent, sizeof(Button)) == 0) {
        return false;
    }
    for (size_t i = 0; i < count; ++i) {
        if (std::memcmp(&button, &targets[i], sizeof(Button)) == 0) {
            return true;
        }
    }
    return false;
}
}  // namespace

bool validate_config_rgb_targets(const Config &config,
                                 const Button *physical_targets,
                                 size_t physical_target_count) {
    if (physical_targets == nullptr && physical_target_count != 0) {
        return false;
    }
    if (static_cast<size_t>(config.rgb_configs_count) >
        sizeof(config.rgb_configs) / sizeof(config.rgb_configs[0])) {
        return false;
    }
    // Prove every nested extent before inspecting any decoder-controlled target.
    for (size_t i = 0; i < config.rgb_configs_count; ++i) {
        const RgbConfig &rgb = config.rgb_configs[i];
        if (static_cast<size_t>(rgb.button_colors_count) >
            sizeof(rgb.button_colors) / sizeof(rgb.button_colors[0])) {
            return false;
        }
    }
    for (size_t i = 0; i < config.rgb_configs_count; ++i) {
        const RgbConfig &rgb = config.rgb_configs[i];
        for (size_t j = 0; j < rgb.button_colors_count; ++j) {
            if (!is_physical_target(rgb.button_colors[j].button,
                                    physical_targets, physical_target_count)) {
                return false;
            }
        }
    }
    return true;
}
