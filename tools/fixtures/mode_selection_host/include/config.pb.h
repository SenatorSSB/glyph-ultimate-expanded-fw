#pragma once

#include <cstddef>
#include <cstdint>

enum GameModeId {
    MODE_UNSPECIFIED = 0,
    MODE_MELEE,
    MODE_PROJECT_M,
    MODE_ULTIMATE,
    MODE_FGC,
    MODE_RIVALS_OF_AETHER,
    MODE_RIVALS2,
    MODE_KEYBOARD,
    MODE_CUSTOM,
    MODE_64,
};

enum CommunicationBackendId {
    COMMS_BACKEND_XINPUT = 1,
    COMMS_BACKEND_DINPUT = 2,
};

struct GameModeConfig {
    GameModeId mode_id = MODE_UNSPECIFIED;
    uint64_t activation_binding = 0;
    size_t activation_binding_count = 0;
    size_t keyboard_mode_config = 0;
    size_t custom_mode_config = 0;
};

struct Config {
    size_t game_mode_configs_count = 0;
    GameModeConfig game_mode_configs[30]{};
    size_t keyboard_modes_count = 0;
    int keyboard_modes[30]{};
    size_t custom_modes_count = 0;
    int custom_modes[30]{};
    int melee_options = 0;
    int project_m_options = 0;
};
