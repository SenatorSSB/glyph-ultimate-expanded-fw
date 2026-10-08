#include "glyph_config_validation.hpp"
#include "config_rgb_target_domain.hpp"

#include <cstring>

bool validate_glyph_config(const Config &config, ConfigValidationError &error) {
    // Preserve the existing extent, binding and full-width reference errors.
    if (!validate_config_semantics(config, error)) {
        return false;
    }
    if (!validate_glyph_rgb_targets(config)) {
        static const char message[] = "Config contains an invalid RGB target";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }
    return true;
}
