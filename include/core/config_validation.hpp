#ifndef _CORE_CONFIG_VALIDATION_HPP
#define _CORE_CONFIG_VALIDATION_HPP

#include <cstddef>
#include <config.pb.h>
#include "core/config_usb_default_validation.hpp"

struct ConfigValidationError {
    char message[128] = {};
    // Packet length is explicit: the historical binding error includes its NUL,
    // while formatted reference errors do not.
    size_t length = 0;
};

using ConfigSemanticValidator = bool (*)(const Config &, ConfigValidationError &);

bool validate_config_extents(const Config &config);
// Validates only an independently stored Ultimate profile.  Full Config
// validation continues to own controller/backend/reference semantics.
bool validate_ultimate_profile_semantics(const UltimateProfile &profile,
                                         ConfigValidationError &error);
bool validate_config_semantics(const Config &config, ConfigValidationError &error);

#endif
