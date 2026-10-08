#pragma once

#include "core/config_rgb_target_validation.hpp"
#include "neopixel_definitions.hpp"

// Compile-selected Glyph pixel map. Mk6's 76 pixels identify 36 unique targets;
// gameplay bindings and mode enablement do not participate in this domain.
inline bool validate_glyph_rgb_targets(const Config &config) {
    return validate_config_rgb_targets(
        config, pixel_to_button_mappings,
        sizeof(pixel_to_button_mappings) / sizeof(pixel_to_button_mappings[0]));
}
