#pragma once

#include "core/config_rgb_target_validation.hpp"
#include "neopixel_definitions.hpp"

// Compile-selected Glyph pixel map. Mk6's 76 pixels identify 36 unique targets;
// gameplay bindings and mode enablement do not participate in this domain.
inline bool validate_glyph_rgb_targets(const Config &config) {
    return validate_config_rgb_targets(
        config, pixel_to_button_mappings,
        sizeof(pixel_to_button_mappings) / sizeof(pixel_to_button_mappings[0]),
        // Captured pre-store Configs encode historical RGB no-op slots as
        // BTN_UNSPECIFIED. They are migration input only; compact Configs and
        // ordinary target validation retain the strict target domain.
        config.ultimate_profile_store_format == 0);
}

// Legacy persisted Configs encoded RGB no-op slots explicitly. Remove those
// entries only while producing the compact-store successor, never from an
// ordinary compact Config.
inline void normalize_legacy_glyph_rgb_noops(Config &config) {
    if (config.ultimate_profile_store_format != 0) return;
    for (size_t i = 0; i < config.rgb_configs_count; ++i) {
        RgbConfig &rgb = config.rgb_configs[i];
        size_t next = 0;
        for (size_t j = 0; j < rgb.button_colors_count; ++j) {
            if (rgb.button_colors[j].button != BTN_UNSPECIFIED) {
                rgb.button_colors[next++] = rgb.button_colors[j];
            }
        }
        rgb.button_colors_count = next;
    }
}
