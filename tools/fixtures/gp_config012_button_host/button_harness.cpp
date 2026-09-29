#include <config.pb.h>
#include <pb_common.h>
#include <pb_decode.h>

struct OutputState {
    uint8_t leftStickX = 0;
    uint8_t leftStickY = 0;
    uint8_t rightStickX = 0;
    uint8_t rightStickY = 0;
    uint8_t triggerLAnalog = 0;
    uint8_t triggerRAnalog = 0;
};

#include "util/state_util.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

static_assert(sizeof(Button) == 1, "the authorized Pico -fshort-enums ABI is one byte");
static_assert(sizeof(((GameModeConfig *)nullptr)->activation_binding[0]) == 1,
              "generated repeated Button storage follows the Pico enum ABI");
static_assert(sizeof(((AnalogModifier *)nullptr)->buttons[0]) == 1,
              "generated modifier Button storage follows the Pico enum ABI");

constexpr size_t kModeActivationMaskCapacity = 30;
uint64_t mode_activation_masks[kModeActivationMaskCapacity]{};

struct InputState {
    uint64_t buttons = 0;
};

class InputMode {
  public:
    void SetConfig(GameModeConfig &) {}
};

class CustomControllerMode : public InputMode {
  public:
    const CustomModeConfig *_custom_mode_config = nullptr;
    uint64_t _modifier_button_masks[10]{};
    uint64_t _button_combo_mappings_masks[5]{};

    void SetConfig(GameModeConfig &config, const CustomModeConfig &custom_mode_config);
};

void setup_mode_activation_bindings(const GameModeConfig *mode_configs, size_t mode_configs_count);
CommunicationBackendConfig backend_config_from_buttons(
    const InputState &inputs,
    const CommunicationBackendConfig *backend_configs,
    size_t backend_configs_count
);

#include "production_fragments.inc"

namespace {

void append_varint(std::vector<uint8_t> &out, uint64_t value) {
    while (value >= 0x80) {
        out.push_back(static_cast<uint8_t>((value & 0x7f) | 0x80));
        value >>= 7;
    }
    out.push_back(static_cast<uint8_t>(value));
}

void append_field(std::vector<uint8_t> &out, uint32_t tag, int64_t value) {
    append_varint(out, (static_cast<uint64_t>(tag) << 3) | 0);
    append_varint(out, static_cast<uint64_t>(value));
}

void append_bytes(std::vector<uint8_t> &out, uint32_t tag, const std::vector<uint8_t> &value) {
    append_varint(out, (static_cast<uint64_t>(tag) << 3) | 2);
    append_varint(out, value.size());
    out.insert(out.end(), value.begin(), value.end());
}

enum class Encoding { Unpacked, Packed, Mixed };

void append_repeated_buttons(std::vector<uint8_t> &out, uint32_t tag,
                             const std::vector<int64_t> &values, Encoding encoding) {
    if (encoding == Encoding::Unpacked) {
        for (int64_t value : values) append_field(out, tag, value);
    } else if (encoding == Encoding::Packed) {
        std::vector<uint8_t> packed;
        for (int64_t value : values) append_varint(packed, static_cast<uint64_t>(value));
        append_bytes(out, tag, packed);
    } else {
        if (!values.empty()) append_field(out, tag, values.front());
        if (values.size() > 1) {
            std::vector<uint8_t> packed;
            for (size_t i = 1; i < values.size() - 1; ++i) {
                append_varint(packed, static_cast<uint64_t>(values[i]));
            }
            if (!packed.empty()) append_bytes(out, tag, packed);
            append_field(out, tag, values.back());
        }
    }
}

std::vector<uint8_t> activation_payload(const std::vector<int64_t> &values, Encoding encoding) {
    std::vector<uint8_t> game_mode;
    append_repeated_buttons(game_mode, 5, values, encoding);
    std::vector<uint8_t> config;
    append_bytes(config, 1, game_mode);
    return config;
}

std::vector<uint8_t> modifier_payload(const std::vector<int64_t> &values, Encoding encoding) {
    std::vector<uint8_t> modifier;
    append_repeated_buttons(modifier, 1, values, encoding);
    std::vector<uint8_t> custom_mode;
    append_bytes(custom_mode, 5, modifier);
    std::vector<uint8_t> config;
    append_bytes(config, 3, custom_mode);
    return config;
}

bool decode(const std::vector<uint8_t> &wire, Config &config) {
    config = Config_init_zero;
    pb_istream_t stream = pb_istream_from_buffer(wire.data(), wire.size());
    return pb_decode(&stream, Config_fields, &config);
}

uint8_t raw_activation(const Config &config, size_t index = 0) {
    uint8_t raw = 0;
    std::memcpy(&raw, &config.game_mode_configs[0].activation_binding[index], sizeof(raw));
    return raw;
}

void report_decode(const std::string &name, const std::vector<uint8_t> &wire,
                   bool activation, size_t raw_index = 0) {
    Config config{};
    bool accepted = decode(wire, config);
    std::cout << "case=" << name << " decoder=" << (accepted ? "accept" : "reject");
    if (accepted && activation && config.game_mode_configs_count > 0) {
        std::cout << " count=" << config.game_mode_configs[0].activation_binding_count;
        if (config.game_mode_configs[0].activation_binding_count > raw_index) {
            std::cout << " raw=" << static_cast<unsigned>(raw_activation(config, raw_index));
        }
    } else if (accepted && !activation && config.custom_modes_count > 0) {
        std::cout << " custom_count=" << config.custom_modes_count;
        std::cout << " modifier_count=" << config.custom_modes[0].modifiers_count;
        if (config.custom_modes[0].modifiers_count > 0) {
            std::cout << " button_count=" << config.custom_modes[0].modifiers[0].buttons_count;
        }
    }
    std::cout << '\n';
}

int decode_cases() {
    std::cout << "abi sizeof_button=" << sizeof(Button)
              << " activation_element=" << sizeof(GameModeConfig::activation_binding[0])
              << " modifier_element=" << sizeof(AnalogModifier::buttons[0]);
    Config empty{};
    bool empty_ok = decode({}, empty);
    std::cout << " empty_config=" << (empty_ok ? "accept" : "reject") << '\n';

    pb_field_iter_t iter{};
    GameModeConfig mode{};
    size_t descriptor_width = 0;
    if (pb_field_iter_begin(&iter, GameModeConfig_fields, &mode)) {
        do {
            if (iter.tag == 5) descriptor_width = iter.data_size;
        } while (pb_field_iter_next(&iter));
    }
    std::cout << "descriptor activation_element=" << descriptor_width << '\n';

    for (int value = 0; value <= 60; ++value) {
        report_decode("enum_" + std::to_string(value), activation_payload({value}, Encoding::Unpacked), true);
    }
    for (int value : {61, 62, 63, 64, 65, 127, 255, 256, 300, -1}) {
        report_decode("enum_" + std::to_string(value), activation_payload({value}, Encoding::Unpacked), true);
    }
    report_decode("packed_four", activation_payload({1, 2, 3, 60}, Encoding::Packed), true, 3);
    report_decode("mixed_four", activation_payload({1, 2, 3, 60}, Encoding::Mixed), true, 3);
    report_decode("extent_activation_five",
                  activation_payload({1, 2, 3, 4, 5}, Encoding::Unpacked), true);
    report_decode("extent_modifier_four", modifier_payload({1, 2, 3, 4}, Encoding::Packed), false);

    std::vector<uint8_t> truncated = {0x0a, 0x02, 0x28, 0x80};
    report_decode("malformed_truncated_varint", truncated, true);
    std::vector<uint8_t> overlong = {0x0a, 0x0c, 0x28};
    overlong.insert(overlong.end(), 11, 0x80);
    report_decode("malformed_overlong_varint", overlong, true);

    return descriptor_width == 1 && empty_ok ? 0 : 2;
}

uint8_t button_from_raw(unsigned raw) {
    return static_cast<uint8_t>(raw & 0xffu);
}

int caller_case(const std::string &name, unsigned raw) {
    Button value = static_cast<Button>(button_from_raw(raw));
    if (name == "mode_activation") {
        GameModeConfig mode{};
        mode.activation_binding_count = 1;
        mode.activation_binding[0] = value;
        setup_mode_activation_bindings(&mode, 1);
        std::cout << "caller=mode_activation mask=" << mode_activation_masks[0] << '\n';
        return 0;
    }
    if (name == "backend_activation") {
        CommunicationBackendConfig backend{};
        backend.backend_id = COMMS_BACKEND_DINPUT;
        backend.activation_binding_count = 1;
        backend.activation_binding[0] = value;
        InputState inputs{};
        inputs.buttons = ~uint64_t{0};
        CommunicationBackendConfig selected = backend_config_from_buttons(inputs, &backend, 1);
        std::cout << "caller=backend_activation backend_id="
                  << static_cast<unsigned>(selected.backend_id) << '\n';
        return 0;
    }
    if (name == "custom_modifier" || name == "custom_combo") {
        GameModeConfig mode{};
        CustomModeConfig custom{};
        custom.modifiers_count = 1;
        custom.modifiers[0].buttons_count = 1;
        custom.modifiers[0].buttons[0] = name == "custom_combo" ? BTN_LF1 : value;
        custom.button_combo_mappings_count = 1;
        custom.button_combo_mappings[0].buttons_count = 1;
        custom.button_combo_mappings[0].buttons[0] = name == "custom_combo" ? value : BTN_LF1;
        CustomControllerMode controller;
        controller.SetConfig(mode, custom);
        uint64_t result = name == "custom_combo" ? controller._button_combo_mappings_masks[0]
                                                   : controller._modifier_button_masks[0];
        std::cout << "caller=" << name << " mask=" << result << '\n';
        return 0;
    }
    if (name == "direct_helper") {
        uint64_t result = make_button_mask(&value, 1);
        std::cout << "caller=direct_helper mask=" << result << '\n';
        return 0;
    }
    if (name == "empty_helper") {
        uint64_t result = make_button_mask(nullptr, 0);
        std::cout << "caller=empty_helper mask=" << result << '\n';
        return result == 0 ? 0 : 3;
    }
    return 4;
}

int enum_read(unsigned raw) {
    Button value{};
    uint8_t byte = button_from_raw(raw);
    std::memcpy(&value, &byte, sizeof(byte));
    volatile Button observed = value;
    (void)observed;
    return 0;
}

int decoded_enum_read(unsigned raw) {
    Config config{};
    if (!decode(activation_payload({static_cast<int64_t>(raw)}, Encoding::Unpacked), config)) return 6;
    volatile Button observed = config.game_mode_configs[0].activation_binding[0];
    (void)observed;
    return 0;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "decode") return decode_cases();
    if (argc == 2 && std::string(argv[1]) == "empty_helper") return caller_case("empty_helper", 0);
    if (argc == 3 && std::string(argv[1]) == "caller") return caller_case(argv[2], 1);
    if (argc == 4 && std::string(argv[1]) == "caller")
        return caller_case(argv[2], static_cast<unsigned>(std::stoul(argv[3])));
    if (argc == 3 && std::string(argv[1]) == "enum_read")
        return enum_read(static_cast<unsigned>(std::stoul(argv[2])));
    if (argc == 3 && std::string(argv[1]) == "decoded_enum_read")
        return decoded_enum_read(static_cast<unsigned>(std::stoul(argv[2])));
    if (argc == 3 && std::string(argv[1]) == "shift")
        return caller_case("direct_helper", static_cast<unsigned>(std::stoul(argv[2])));
    return 5;
}
