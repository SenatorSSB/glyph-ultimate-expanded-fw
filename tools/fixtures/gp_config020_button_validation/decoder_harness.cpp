#include "core/config_button_validation.hpp"

#include <pb_decode.h>

#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

extern "C" int gp_config020_abi_probe();

namespace {

void require(bool condition, const std::string &message) {
    if (!condition) throw std::runtime_error(message);
}

void append_varint(std::vector<uint8_t> &out, uint64_t value) {
    while (value >= 0x80) {
        out.push_back(static_cast<uint8_t>(value) | 0x80);
        value >>= 7;
    }
    out.push_back(static_cast<uint8_t>(value));
}

std::vector<uint8_t> varint_field(uint32_t field, uint64_t value) {
    std::vector<uint8_t> out;
    append_varint(out, (static_cast<uint64_t>(field) << 3) | 0);
    append_varint(out, value);
    return out;
}

std::vector<uint8_t> message_field(uint32_t field, const std::vector<uint8_t> &inner) {
    std::vector<uint8_t> out;
    append_varint(out, (static_cast<uint64_t>(field) << 3) | 2);
    append_varint(out, inner.size());
    out.insert(out.end(), inner.begin(), inner.end());
    return out;
}

void append(std::vector<uint8_t> &out, const std::vector<uint8_t> &part) {
    out.insert(out.end(), part.begin(), part.end());
}

std::vector<uint8_t> binding_wire(size_t binding_class, uint64_t raw) {
    switch (binding_class) {
        case 0: return message_field(1, varint_field(5, raw)); // game mode activation
        case 1: return message_field(1, message_field(4, varint_field(1, raw))); // remap physical
        case 2: {
            std::vector<uint8_t> remap = varint_field(1, 1);
            append(remap, varint_field(2, raw));
            return message_field(1, message_field(4, remap)); // remap activates
        }
        case 3: {
            std::vector<uint8_t> pair = varint_field(1, raw);
            append(pair, varint_field(2, 1));
            return message_field(1, message_field(3, pair)); // SOCD dir1
        }
        case 4: {
            std::vector<uint8_t> pair = varint_field(1, 1);
            append(pair, varint_field(2, raw));
            return message_field(1, message_field(3, pair)); // SOCD dir2
        }
        case 5: return message_field(2, varint_field(3, raw)); // backend activation
        case 6: return message_field(3, message_field(5, varint_field(1, raw))); // modifier button
        case 7: return message_field(3, message_field(7, varint_field(1, raw))); // combo button
        case 8: return message_field(3, varint_field(2, raw)); // custom digital
        case 9: return message_field(3, varint_field(3, raw)); // custom stick direction
        case 10: return message_field(3, message_field(4, varint_field(1, raw))); // analog trigger
        case 11: return message_field(4, message_field(2, varint_field(1, raw))); // keyboard keymap
        default: throw std::runtime_error("unknown binding class");
    }
}

bool decode(const std::vector<uint8_t> &wire, Config &config) {
    pb_istream_t stream = pb_istream_from_buffer(wire.data(), wire.size());
    return pb_decode(&stream, Config_fields, &config);
}

const Button &decoded_slot(const Config &config, size_t binding_class) {
    switch (binding_class) {
        case 0: return config.game_mode_configs[0].activation_binding[0];
        case 1: return config.game_mode_configs[0].button_remapping[0].physical_button;
        case 2: return config.game_mode_configs[0].button_remapping[0].activates;
        case 3: return config.game_mode_configs[0].socd_pairs[0].button_dir1;
        case 4: return config.game_mode_configs[0].socd_pairs[0].button_dir2;
        case 5: return config.communication_backend_configs[0].activation_binding[0];
        case 6: return config.custom_modes[0].modifiers[0].buttons[0];
        case 7: return config.custom_modes[0].button_combo_mappings[0].buttons[0];
        case 8: return config.custom_modes[0].digital_button_mappings[0];
        case 9: return config.custom_modes[0].stick_direction_mappings[0];
        case 10: return config.custom_modes[0].analog_trigger_mappings[0].button;
        case 11: return config.keyboard_modes[0].buttons_to_keycodes[0].button;
        default: throw std::runtime_error("unknown decoded binding class");
    }
}

uint32_t decoded_raw(const Config &config, size_t binding_class) {
    using Storage = std::underlying_type<Button>::type;
    Storage bytes{};
    const Button &slot = decoded_slot(config, binding_class);
    std::memcpy(&bytes, &slot, sizeof(slot));
    return static_cast<uint32_t>(bytes);
}

void named_decoder_matrix() {
    for (size_t binding_class = 0; binding_class < 12; ++binding_class) {
        for (uint32_t id = 1; id <= 60; ++id) {
            Config config = Config_init_default;
            const std::vector<uint8_t> wire = binding_wire(binding_class, id);
            require(decode(wire, config), "Nanopb rejected named ID " + std::to_string(id) +
                    " class " + std::to_string(binding_class));
            require(decoded_raw(config, binding_class) == id, "named wire value changed in enum storage");
            require(validate_config_button_bindings(config), "validator rejected decoded named ID " +
                    std::to_string(id) + " class " + std::to_string(binding_class));
        }
    }
}

void raw_decoder_matrix() {
    for (size_t binding_class = 0; binding_class < 12; ++binding_class) {
        for (uint32_t raw = 0; raw <= 255; ++raw) {
            Config config = Config_init_default;
            const bool decoded = decode(binding_wire(binding_class, raw), config);
            require(decoded, "Nanopb rejected byte-range enum control " + std::to_string(raw));
            require(decoded_raw(config, binding_class) == raw, "byte-range wire value changed in storage");
            const bool accepted = validate_config_button_bindings(config);
            require(accepted == ((raw >= 1 && raw <= 60) || (binding_class == 2 && raw == 0)),
                    "validator result drift for decoder raw control " + std::to_string(raw));
        }
    }

    for (uint64_t raw : std::array<uint64_t, 5>{256, 257, 300, UINT32_MAX, UINT64_MAX}) {
        size_t decoded_count = 0;
        for (size_t binding_class = 0; binding_class < 12; ++binding_class) {
            Config config = Config_init_default;
            const bool decoded = decode(binding_wire(binding_class, raw), config);
            if (sizeof(Button) == 1) {
                require(!decoded, "byte ABI accepted wire value that narrows to a valid enum " +
                        std::to_string(raw) + " class " + std::to_string(binding_class));
            } else if (decoded) {
                ++decoded_count;
                require(decoded_raw(config, binding_class) == static_cast<uint32_t>(raw),
                        "wide wire value changed in enum storage");
                require(!validate_config_button_bindings(config),
                        "validator accepted wide/negative decoder value " + std::to_string(raw));
            }
        }
        std::cout << "wire_raw=" << raw << " decoded_classes=" << decoded_count
                  << " rejected_or_decode_failed=" << (12 - decoded_count) << " result=PASS\n";
    }
}

void malformed_and_last_element_controls() {
    std::vector<uint8_t> malformed = binding_wire(0, 1);
    malformed.push_back(0x80); // truncated trailing key varint after a valid partial decode
    Config partial = Config_init_default;
    require(!decode(malformed, partial), "malformed trailing input accepted");

    std::vector<uint8_t> truncated = binding_wire(0, 1);
    truncated.pop_back(); // length-delimited nested message is now truncated
    Config truncated_config = Config_init_default;
    require(!decode(truncated, truncated_config), "truncated nested message accepted");

    std::vector<uint8_t> overlong = binding_wire(0, 1);
    overlong.insert(overlong.end(), {0x80, 0x80, 0x80, 0x80, 0x80, 0x80,
                                     0x80, 0x80, 0x80, 0x80, 0x00});
    Config overlong_config = Config_init_default;
    require(!decode(overlong, overlong_config), "overlong trailing varint accepted");

    std::vector<uint8_t> mode;
    append(mode, varint_field(5, 1));
    append(mode, varint_field(5, 60));
    append(mode, varint_field(5, 61));
    Config last_invalid = Config_init_default;
    const std::vector<uint8_t> last_invalid_wire = message_field(1, mode);
    require(decode(last_invalid_wire, last_invalid), "last-element vector failed to decode");
    require(!validate_config_button_bindings(last_invalid), "last invalid populated element was missed");
    require(last_invalid.game_mode_configs[0].activation_binding_count == 3,
            "last-element vector count/order not preserved by decoder");

    std::vector<uint8_t> overflow_mode;
    for (uint32_t i = 0; i < 5; ++i) append(overflow_mode, varint_field(5, i == 4 ? 61 : 1));
    Config overflow = Config_init_default;
    require(!decode(message_field(1, overflow_mode), overflow), "activation list overflow accepted");
}

void ordering_and_mask_identity() {
    std::vector<uint8_t> mode;
    append(mode, varint_field(5, 60));
    append(mode, varint_field(5, 1));
    append(mode, varint_field(5, 33));
    Config config = Config_init_default;
    require(decode(message_field(1, mode), config), "ordered activation vector failed to decode");
    const Config before = config;
    require(validate_config_button_bindings(config), "ordered activation vector rejected");
    require(config.game_mode_configs[0].activation_binding[0] == BTN_MB12 &&
            config.game_mode_configs[0].activation_binding[1] == BTN_LF1 &&
            config.game_mode_configs[0].activation_binding[2] == BTN_LT1,
            "validator or decoder changed binding order");
    const uint64_t expected = (uint64_t{1} << 59) | (uint64_t{1} << 0) | (uint64_t{1} << 32);
    uint64_t mask = 0;
    for (size_t i = 0; i < config.game_mode_configs[0].activation_binding_count; ++i) {
        const unsigned id = static_cast<unsigned>(config.game_mode_configs[0].activation_binding[i]);
        mask |= uint64_t{1} << (id - 1);
    }
    require(mask == expected, "valid decoded order/mask identity changed");
    require(std::memcmp(&config, &before, sizeof(Config)) == 0,
            "validator mutated decoded repeated-field bytes");
}

}  // namespace

int main() {
    try {
        require(gp_config020_abi_probe() == 0, "generated descriptor/struct layout mismatch before decode");
        named_decoder_matrix();
        raw_decoder_matrix();
        malformed_and_last_element_controls();
        ordering_and_mask_identity();
        std::cout << "decoded_named_ids=1..60 across 12 classes result=PASS\n";
        std::cout << "decoded_raw=0..255,256,257,300,uint32max,uint64max across 12 classes result=PASS\n";
        std::cout << "malformed_trailing_last_element_overflow result=PASS\n";
        std::cout << "binding_order_mask_identity_no_mutation result=PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "result=FAIL error=" << error.what() << "\n";
        return 1;
    }
}
