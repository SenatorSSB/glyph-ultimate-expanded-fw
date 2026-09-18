#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#define private public
#include "../../../HAL/pico/include/comms/ConfiguratorBackend.hpp"
#undef private

namespace {

enum class Scenario {
    MalformedDecode,
    InvalidDefaultBackend,
    InvalidDefaultGameMode,
    InvalidKeyboardCondition,
    InvalidCustomCondition,
    OutOfRangeKeyboard,
    OutOfRangeCustom,
    SaveFailure,
    Success,
};

Scenario scenario;
Config decode_candidate{};
Config *live_config = nullptr;
Config saved_candidate{};
Config live_at_save{};
Config *save_argument = nullptr;
size_t save_calls = 0;
bool save_result = true;

class TestStream final : public Stream {
  public:
    std::vector<uint8_t> output;

    int available() override { return 0; }
    int read() override { return -1; }
    int peek() override { return -1; }
    void flush() override {}
    size_t write(uint8_t value) override {
        output.push_back(value);
        return 1;
    }
    size_t write(const uint8_t *buffer, size_t size) override {
        output.insert(output.end(), buffer, buffer + size);
        return size;
    }
};

struct Addresses {
    const void *config;
    const void *game_modes;
    const void *game_mode_zero;
    const void *backends;
    const void *custom_modes;
    const void *custom_mapping;
    const void *keyboard_modes;
    const void *keyboard_mapping;
};

Addresses addresses(const Config &config) {
    return {
        &config,
        &config.game_mode_configs,
        &config.game_mode_configs[0],
        &config.communication_backend_configs,
        &config.custom_modes,
        &config.custom_modes[0].digital_button_mappings,
        &config.keyboard_modes,
        &config.keyboard_modes[0].buttons_to_keycodes,
    };
}

bool operator==(const Addresses &left, const Addresses &right) {
    return std::memcmp(&left, &right, sizeof(Addresses)) == 0;
}

bool same_config(const Config &left, const Config &right) {
    return std::memcmp(&left, &right, sizeof(Config)) == 0;
}

void require(bool condition, const std::string &message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

Config accepted_config() {
    Config result;
    std::memset(&result, 0x3c, sizeof(result));
    return result;
}

Config valid_candidate() {
    Config result;
    std::memset(&result, 0xa5, sizeof(result));
    result.game_mode_configs_count = 1;
    result.communication_backend_configs_count = 1;
    result.custom_modes_count = 1;
    result.keyboard_modes_count = 1;
    result.rgb_configs_count = 1;
    result.default_backend_config = 1;
    result.communication_backend_configs[0].default_mode_config = 1;
    result.game_mode_configs[0].mode_id = MODE_MELEE;
    result.game_mode_configs[0].keyboard_mode_config = 0;
    result.game_mode_configs[0].custom_mode_config = 0;
    return result;
}

std::vector<uint8_t> response(Command command, const std::string &text, bool nul = false) {
    std::vector<uint8_t> result{static_cast<uint8_t>(command)};
    result.insert(result.end(), text.begin(), text.end());
    if (nul) {
        result.push_back(0);
    }
    return result;
}

std::vector<uint8_t> expected_response(Scenario current) {
    switch (current) {
        case Scenario::MalformedDecode:
            return response(CMD_ERROR, "Failed to decode config: synthetic malformed input");
        case Scenario::InvalidDefaultBackend:
            return response(CMD_ERROR, "Default backend ID is 2 but only 1 backend configs are defined");
        case Scenario::InvalidDefaultGameMode:
            return response(CMD_ERROR, "Default mode ID is 2 for backend 1 but only 1 modes are defined");
        case Scenario::InvalidKeyboardCondition:
            return response(CMD_ERROR, "keyboard_mode_id is set for game mode 1 but mode_id is not MODE_KEYBOARD");
        case Scenario::InvalidCustomCondition:
            return response(CMD_ERROR, "custom_mode_id is set for game mode 1 but mode_id is not MODE_CUSTOM");
        case Scenario::OutOfRangeKeyboard:
            return response(CMD_ERROR, "Keyboard mode ID 2 is for game mode 1 but only 1 keyboard modes are defined");
        case Scenario::OutOfRangeCustom:
            return response(CMD_ERROR, "Custom mode ID 2 is for game mode config 1 but only 1 custom modes are defined");
        case Scenario::SaveFailure:
            return response(CMD_ERROR, "Failed to save config to memory", true);
        case Scenario::Success:
            return response(CMD_SUCCESS, "");
    }
    throw std::runtime_error("unreachable scenario");
}

const char *name(Scenario current) {
    switch (current) {
        case Scenario::MalformedDecode: return "malformed_decode";
        case Scenario::InvalidDefaultBackend: return "invalid_default_backend_index";
        case Scenario::InvalidDefaultGameMode: return "invalid_default_game_mode_reference";
        case Scenario::InvalidKeyboardCondition: return "invalid_keyboard_mode_condition";
        case Scenario::InvalidCustomCondition: return "invalid_custom_mode_condition";
        case Scenario::OutOfRangeKeyboard: return "out_of_range_keyboard_config";
        case Scenario::OutOfRangeCustom: return "out_of_range_custom_config";
        case Scenario::SaveFailure: return "save_failure";
        case Scenario::Success: return "full_success";
    }
    return "unknown";
}

Config candidate_for(Scenario current) {
    Config result = valid_candidate();
    switch (current) {
        case Scenario::InvalidDefaultBackend:
            result.default_backend_config = 2;
            break;
        case Scenario::InvalidDefaultGameMode:
            result.communication_backend_configs[0].default_mode_config = 2;
            break;
        case Scenario::InvalidKeyboardCondition:
            result.game_mode_configs[0].keyboard_mode_config = 1;
            break;
        case Scenario::InvalidCustomCondition:
            result.game_mode_configs[0].custom_mode_config = 1;
            break;
        case Scenario::OutOfRangeKeyboard:
            result.game_mode_configs[0].mode_id = MODE_KEYBOARD;
            result.game_mode_configs[0].keyboard_mode_config = 2;
            break;
        case Scenario::OutOfRangeCustom:
            result.game_mode_configs[0].mode_id = MODE_CUSTOM;
            result.game_mode_configs[0].custom_mode_config = 2;
            break;
        default:
            break;
    }
    return result;
}

void run_case(Scenario current) {
    scenario = current;
    Config live = accepted_config();
    const Config before = live;
    const Addresses address_before = addresses(live);
    const GameModeConfig cached_game_mode = live.game_mode_configs[0];
    const CustomModeConfig cached_custom_mode = live.custom_modes[0];
    const KeyboardModeConfig cached_keyboard_mode = live.keyboard_modes[0];
    GameModeConfig *const game_mode_pointer = &live.game_mode_configs[0];
    CustomModeConfig *const custom_mode_pointer = &live.custom_modes[0];
    KeyboardModeConfig *const keyboard_mode_pointer = &live.keyboard_modes[0];

    decode_candidate = candidate_for(current);
    save_calls = 0;
    save_argument = nullptr;
    save_result = current != Scenario::SaveFailure;
    live_config = &live;
    TestStream stream;
    InputState inputs;
    ConfiguratorBackend backend(inputs, nullptr, 0, live, stream);
    const bool result = backend.HandleSetConfig();

    const bool success = current == Scenario::Success;
    const bool reaches_save = current == Scenario::SaveFailure || success;
    require(result == success, std::string(name(current)) + ": return value");
    require(stream.output == expected_response(current), std::string(name(current)) + ": response bytes");
    require(addresses(live) == address_before, std::string(name(current)) + ": embedded address stability");
    require(game_mode_pointer == &live.game_mode_configs[0], std::string(name(current)) + ": game-mode pointer stability");
    require(custom_mode_pointer == &live.custom_modes[0], std::string(name(current)) + ": custom-mode pointer stability");
    require(keyboard_mode_pointer == &live.keyboard_modes[0], std::string(name(current)) + ": keyboard-mode pointer stability");
    require(save_calls == (reaches_save ? 1U : 0U), std::string(name(current)) + ": SaveConfig count/order");

    if (!success) {
        require(same_config(live, before), std::string(name(current)) + ": rejected request changed live bytes");
        require(std::memcmp(game_mode_pointer, &cached_game_mode, sizeof(cached_game_mode)) == 0,
                std::string(name(current)) + ": cached game-mode pointee changed");
        require(std::memcmp(custom_mode_pointer, &cached_custom_mode, sizeof(cached_custom_mode)) == 0,
                std::string(name(current)) + ": cached custom-mode pointee changed");
        require(std::memcmp(keyboard_mode_pointer, &cached_keyboard_mode, sizeof(cached_keyboard_mode)) == 0,
                std::string(name(current)) + ": cached keyboard-mode pointee changed");
    }

    if (reaches_save) {
        require(save_argument != live_config, std::string(name(current)) + ": SaveConfig received live storage");
        require(same_config(saved_candidate, decode_candidate), std::string(name(current)) + ": SaveConfig candidate bytes");
        require(same_config(live_at_save, before), std::string(name(current)) + ": live changed before SaveConfig returned");
    }

    if (success) {
        require(same_config(live, decode_candidate), "full_success: candidate was not published");
        require(std::memcmp(game_mode_pointer, &decode_candidate.game_mode_configs[0], sizeof(*game_mode_pointer)) == 0,
                "full_success: stable pointee did not observe published candidate");
    }

    std::cout << "case=" << name(current) << " result=PASS\n";
}

}  // namespace

pb_istream_t as_pb_istream(Stream &) {
    return {nullptr};
}

pb_ostream_t as_pb_ostream(Print &) {
    return {0};
}

bool pb_decode(pb_istream_t *stream, const void *, void *destination) {
    auto *config = static_cast<Config *>(destination);
    if (scenario == Scenario::MalformedDecode) {
        std::memset(config, 0xee, sizeof(*config));
        stream->errmsg = "synthetic malformed input";
        return false;
    }
    *config = decode_candidate;
    return true;
}

Persistence persistence;

bool Persistence::SaveConfig(Config &config) {
    ++save_calls;
    save_argument = &config;
    saved_candidate = config;
    live_at_save = *live_config;
    return save_result;
}

// This literal include is the correspondence contract: the host binary compiles
// the repository's production implementation, not a copied handler model.
#include "../../../HAL/pico/src/comms/ConfiguratorBackend.cpp"

int main() {
    try {
        constexpr std::array<Scenario, 9> cases = {
            Scenario::MalformedDecode,
            Scenario::InvalidDefaultBackend,
            Scenario::InvalidDefaultGameMode,
            Scenario::InvalidKeyboardCondition,
            Scenario::InvalidCustomCondition,
            Scenario::OutOfRangeKeyboard,
            Scenario::OutOfRangeCustom,
            Scenario::SaveFailure,
            Scenario::Success,
        };
        for (Scenario current : cases) {
            run_case(current);
        }
        std::cout << "production_source=HAL/pico/src/comms/ConfiguratorBackend.cpp\n";
        std::cout << "production_handler_cases=9 result=PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "result=FAIL error=" << error.what() << "\n";
        return 1;
    }
}
