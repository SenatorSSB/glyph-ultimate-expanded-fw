#include <cstdlib>
#include <cstring>
#include <iostream>
#include <new>

#include "modes/CustomControllerMode.hpp"

// Compile the exact production implementation once; this harness does not copy
// CustomControllerMode method bodies.
#include "../../../src/modes/CustomControllerMode.cpp"

namespace {

void populate(CustomModeConfig &config, size_t count) {
    config.modifiers_count = count;
    for (size_t i = 0; i < count && i < 20; ++i) {
        config.modifiers[i].buttons_count = 1;
        config.modifiers[i].buttons[0] = static_cast<Button>(BTN_LF1 + i);
        config.modifiers[i].axis = AXIS_LSTICK_X;
        config.modifiers[i].multiplier = 1.0f;
        config.modifiers[i].combination_mode = COMBINATION_MODE_COMPOUND;
    }
}

void configure_adjacent_state(CustomModeConfig &config) {
    config.stick_direction_mappings_count = 1;
    config.stick_direction_mappings[0] = BTN_LF1;
    config.button_combo_mappings_count = 1;
    config.button_combo_mappings[0].buttons_count = 1;
    config.button_combo_mappings[0].buttons[0] = BTN_LF3;
}

int run_case(const char *case_name) {
    const std::string name(case_name);
    const bool processing = name.rfind("process_", 0) == 0;
    const size_t count = std::strtoul(name.substr(processing ? 8 : 10).c_str(), nullptr, 10);

    GameModeConfig game_config{};
    CustomModeConfig custom_config{};
    populate(custom_config, 10);
    configure_adjacent_state(custom_config);

    alignas(CustomControllerMode) unsigned char storage[sizeof(CustomControllerMode)];
    std::memset(storage, 0, sizeof(storage));
    auto *mode = new (storage) CustomControllerMode();
    mode->SetConfig(game_config, custom_config);

    if (processing) {
        custom_config.modifiers_count = count;
        if (count > 10) {
            custom_config.modifiers[10].buttons_count = 1;
            custom_config.modifiers[10].buttons[0] = BTN_LF2;
            custom_config.modifiers[10].axis = AXIS_LSTICK_X;
            custom_config.modifiers[10].multiplier = 2.0f;
            custom_config.modifiers[10].combination_mode = COMBINATION_MODE_COMPOUND;
        }
        InputState inputs{};
        OutputState outputs{};
        inputs.buttons = UINT64_MAX;
        mode->UpdateOutputs(inputs, outputs, COMMS_BACKEND_CONFIGURATOR);
        mode->~CustomControllerMode();
        if (count > 10 && outputs.leftStickX != 0) {
            std::cerr << "BOUNDARY_VIOLATION: processing read did not reach injected index\n";
            return 91;
        }
    } else {
        unsigned char control[sizeof(storage)];
        std::memcpy(control, storage, sizeof(control));
        mode->~CustomControllerMode();
        std::memset(storage, 0, sizeof(storage));
        mode = new (storage) CustomControllerMode();
        custom_config.modifiers_count = count;
        mode->SetConfig(game_config, custom_config);
        const bool changed = std::memcmp(control, storage, sizeof(control)) != 0;
        mode->~CustomControllerMode();
        if (count > 10 && !changed) {
            std::cerr << "BOUNDARY_VIOLATION: constructor write was not observed\n";
            return 91;
        }
    }

    std::cout << "case=" << case_name << " status=completed count=" << count << "\n";
    return 0;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc != 2) {
        std::cerr << "usage: modifier_cache_harness CASE\n";
        return 2;
    }
    return run_case(argv[1]);
}
