#pragma once
#include <cstddef>
#include <cstdint>

using pb_size_t = std::size_t;

enum CommunicationBackendId {
    COMMS_BACKEND_UNSPECIFIED = 0,
    COMMS_BACKEND_CONFIGURATOR = 1,
    COMMS_BACKEND_DINPUT = 2,
    COMMS_BACKEND_XINPUT = 3,
    COMMS_BACKEND_NINTENDO_SWITCH = 4,
};
enum GameModeId { MODE_UNSPECIFIED = 0, MODE_KEYBOARD = 1, MODE_CUSTOM = 2, MODE_MELEE = 3 };
enum SocdType { SOCD_NEUTRAL = 1, _SocdType_MAX = 4, _SocdType_ARRAYSIZE = 4 };

struct GameModeConfig {
    GameModeId mode_id = MODE_UNSPECIFIED;
    char name[32] = {};
    std::uint8_t keyboard_mode_config = 0;
    std::uint8_t custom_mode_config = 0;
    std::size_t applicable_backends_count = 0;
    CommunicationBackendId applicable_backends[8] = {};
};
struct CommunicationBackendConfig {
    CommunicationBackendId backend_id = COMMS_BACKEND_UNSPECIFIED;
    std::uint8_t default_mode_config = 0;
    std::uint8_t keyboard_mode_config = 0;
};
struct Config {
    GameModeConfig game_mode_configs[8] = {};
    std::size_t game_mode_configs_count = 0;
    CommunicationBackendConfig communication_backend_configs[8] = {};
    std::size_t communication_backend_configs_count = 0;
    std::uint8_t default_dashboard_option = 0;
};
