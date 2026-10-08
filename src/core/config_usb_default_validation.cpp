#include "core/config_usb_default_validation.hpp"

#include <cstddef>

bool is_valid_usb_default_index(const Config &config) {
    const size_t count = config.communication_backend_configs_count;
    const size_t extent = sizeof(config.communication_backend_configs) /
        sizeof(config.communication_backend_configs[0]);
    const size_t index = config.default_usb_backend_config;
    return count <= extent && index >= 1 && index <= count;
}
