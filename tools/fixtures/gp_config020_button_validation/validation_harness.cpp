#include "core/config_button_validation.hpp"
#include "config_defaults.hpp"

#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool condition, const std::string &message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

Config blank_config() {
    return Config_init_default;
}

void store_raw(Button &target, uint32_t raw) {
    static_assert(sizeof(target) == sizeof(raw), "test raw representation must match selected enum ABI");
    std::memcpy(&target, &raw, sizeof(raw));
}

struct BindingCase {
    const char *name;
    void (*populate)(Config &, uint32_t);
    void (*set_count)(Config &, pb_size_t);
    size_t capacity;
    bool zero_allowed;
};

#define BINDING_CASE(case_name, populate_fn, count_fn, max_count, zero_ok) \
    {case_name, populate_fn, count_fn, max_count, zero_ok}

void game_activation(Config &c, uint32_t raw) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].activation_binding_count = 1;
    store_raw(c.game_mode_configs[0].activation_binding[0], raw);
}
void game_activation_count(Config &c, pb_size_t n) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].activation_binding_count = n;
}
void remap_physical(Config &c, uint32_t raw) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].button_remapping_count = 1;
    store_raw(c.game_mode_configs[0].button_remapping[0].physical_button, raw);
}
void remap_physical_count(Config &c, pb_size_t n) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].button_remapping_count = n;
}
void remap_activates(Config &c, uint32_t raw) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].button_remapping_count = 1;
    store_raw(c.game_mode_configs[0].button_remapping[0].physical_button, BTN_LF1);
    store_raw(c.game_mode_configs[0].button_remapping[0].activates, raw);
}
void remap_activates_count(Config &c, pb_size_t n) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].button_remapping_count = n;
}
void socd_dir1(Config &c, uint32_t raw) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].socd_pairs_count = 1;
    store_raw(c.game_mode_configs[0].socd_pairs[0].button_dir1, raw);
    store_raw(c.game_mode_configs[0].socd_pairs[0].button_dir2, BTN_RF1);
}
void socd_dir2(Config &c, uint32_t raw) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].socd_pairs_count = 1;
    store_raw(c.game_mode_configs[0].socd_pairs[0].button_dir1, BTN_LF1);
    store_raw(c.game_mode_configs[0].socd_pairs[0].button_dir2, raw);
}
void socd_count(Config &c, pb_size_t n) {
    c.game_mode_configs_count = 1;
    c.game_mode_configs[0].socd_pairs_count = n;
}
void backend_activation(Config &c, uint32_t raw) {
    c.communication_backend_configs_count = 1;
    c.communication_backend_configs[0].activation_binding_count = 1;
    store_raw(c.communication_backend_configs[0].activation_binding[0], raw);
}
void backend_activation_count(Config &c, pb_size_t n) {
    c.communication_backend_configs_count = 1;
    c.communication_backend_configs[0].activation_binding_count = n;
}
void modifier_button(Config &c, uint32_t raw) {
    c.custom_modes_count = 1;
    c.custom_modes[0].modifiers_count = 1;
    c.custom_modes[0].modifiers[0].buttons_count = 1;
    store_raw(c.custom_modes[0].modifiers[0].buttons[0], raw);
}
void modifier_count(Config &c, pb_size_t n) {
    c.custom_modes_count = 1;
    c.custom_modes[0].modifiers_count = 1;
    c.custom_modes[0].modifiers[0].buttons_count = n;
}
void combo_button(Config &c, uint32_t raw) {
    c.custom_modes_count = 1;
    c.custom_modes[0].button_combo_mappings_count = 1;
    c.custom_modes[0].button_combo_mappings[0].buttons_count = 1;
    store_raw(c.custom_modes[0].button_combo_mappings[0].buttons[0], raw);
}
void combo_count(Config &c, pb_size_t n) {
    c.custom_modes_count = 1;
    c.custom_modes[0].button_combo_mappings_count = 1;
    c.custom_modes[0].button_combo_mappings[0].buttons_count = n;
}
void digital_button(Config &c, uint32_t raw) {
    c.custom_modes_count = 1;
    c.custom_modes[0].digital_button_mappings_count = 1;
    store_raw(c.custom_modes[0].digital_button_mappings[0], raw);
}
void digital_count(Config &c, pb_size_t n) {
    c.custom_modes_count = 1;
    c.custom_modes[0].digital_button_mappings_count = n;
}
void stick_button(Config &c, uint32_t raw) {
    c.custom_modes_count = 1;
    c.custom_modes[0].stick_direction_mappings_count = 1;
    store_raw(c.custom_modes[0].stick_direction_mappings[0], raw);
}
void stick_count(Config &c, pb_size_t n) {
    c.custom_modes_count = 1;
    c.custom_modes[0].stick_direction_mappings_count = n;
}
void trigger_button(Config &c, uint32_t raw) {
    c.custom_modes_count = 1;
    c.custom_modes[0].analog_trigger_mappings_count = 1;
    store_raw(c.custom_modes[0].analog_trigger_mappings[0].button, raw);
}
void trigger_count(Config &c, pb_size_t n) {
    c.custom_modes_count = 1;
    c.custom_modes[0].analog_trigger_mappings_count = n;
}
void keyboard_button(Config &c, uint32_t raw) {
    c.keyboard_modes_count = 1;
    c.keyboard_modes[0].buttons_to_keycodes_count = 1;
    store_raw(c.keyboard_modes[0].buttons_to_keycodes[0].button, raw);
}
void keyboard_count(Config &c, pb_size_t n) {
    c.keyboard_modes_count = 1;
    c.keyboard_modes[0].buttons_to_keycodes_count = n;
}

const BindingCase kCases[] = {
    BINDING_CASE("game_activation", game_activation, game_activation_count, 4, false),
    BINDING_CASE("remap_physical", remap_physical, remap_physical_count, 60, false),
    BINDING_CASE("remap_activates", remap_activates, remap_activates_count, 60, true),
    BINDING_CASE("socd_dir1", socd_dir1, socd_count, 10, false),
    BINDING_CASE("socd_dir2", socd_dir2, socd_count, 10, false),
    BINDING_CASE("backend_activation", backend_activation, backend_activation_count, 2, false),
    BINDING_CASE("modifier_button", modifier_button, modifier_count, 3, false),
    BINDING_CASE("combo_button", combo_button, combo_count, 3, false),
    BINDING_CASE("digital_button", digital_button, digital_count, 18, false),
    BINDING_CASE("stick_button", stick_button, stick_count, 8, false),
    BINDING_CASE("trigger_button", trigger_button, trigger_count, 4, false),
    BINDING_CASE("keyboard_button", keyboard_button, keyboard_count, 60, false),
};

void positive_matrix() {
    for (const BindingCase &binding : kCases) {
        for (uint32_t id = 1; id <= 60; ++id) {
            Config config = blank_config();
            binding.populate(config, id);
            const Config before = config;
            require(validate_config_button_bindings(config), std::string(binding.name) + " rejects named ID " + std::to_string(id));
            require(std::memcmp(&config, &before, sizeof(Config)) == 0, std::string(binding.name) + " mutated config");
        }
    }
}

void negative_matrix() {
    const uint32_t invalid[] = {0, 61, 62, 63, 64, 65, 127, 255, 0xFFFFFFFFu};
    for (const BindingCase &binding : kCases) {
        for (uint32_t raw : invalid) {
            Config config = blank_config();
            binding.populate(config, raw);
            const Config before = config;
            const bool accepted = validate_config_button_bindings(config);
            require(accepted == (binding.zero_allowed && raw == 0), std::string(binding.name) + " invalid control " + std::to_string(raw));
            require(std::memcmp(&config, &before, sizeof(Config)) == 0, std::string(binding.name) + " mutated rejected config");
        }
    }
}

void extent_matrix() {
    for (const BindingCase &binding : kCases) {
        Config config = blank_config();
        binding.set_count(config, static_cast<pb_size_t>(binding.capacity + 1));
        require(!validate_config_button_bindings(config), std::string(binding.name) + " count overflow accepted");
    }

    Config top = blank_config();
    top.game_mode_configs_count = sizeof(top.game_mode_configs) / sizeof(top.game_mode_configs[0]) + 1;
    require(!validate_config_button_bindings(top), "top-level game-mode extent overflow accepted");
    top = blank_config();
    top.communication_backend_configs_count = sizeof(top.communication_backend_configs) / sizeof(top.communication_backend_configs[0]) + 1;
    require(!validate_config_button_bindings(top), "top-level backend extent overflow accepted");
    top = blank_config();
    top.custom_modes_count = sizeof(top.custom_modes) / sizeof(top.custom_modes[0]) + 1;
    require(!validate_config_button_bindings(top), "top-level custom-mode extent overflow accepted");
    top = blank_config();
    top.keyboard_modes_count = sizeof(top.keyboard_modes) / sizeof(top.keyboard_modes[0]) + 1;
    require(!validate_config_button_bindings(top), "top-level keyboard extent overflow accepted");

    static Config full = Config_init_default;
    full.game_mode_configs_count = sizeof(full.game_mode_configs) / sizeof(full.game_mode_configs[0]);
    for (size_t i = 0; i < full.game_mode_configs_count; ++i) {
        GameModeConfig &mode = full.game_mode_configs[i];
        mode.socd_pairs_count = sizeof(mode.socd_pairs) / sizeof(mode.socd_pairs[0]);
        for (size_t j = 0; j < mode.socd_pairs_count; ++j) {
            mode.socd_pairs[j].button_dir1 = BTN_LF1;
            mode.socd_pairs[j].button_dir2 = BTN_RF1;
        }
        mode.button_remapping_count = sizeof(mode.button_remapping) / sizeof(mode.button_remapping[0]);
        for (size_t j = 0; j < mode.button_remapping_count; ++j) {
            mode.button_remapping[j].physical_button = BTN_LF1;
            mode.button_remapping[j].activates = BTN_UNSPECIFIED;
        }
        mode.activation_binding_count = sizeof(mode.activation_binding) / sizeof(mode.activation_binding[0]);
        for (size_t j = 0; j < mode.activation_binding_count; ++j) mode.activation_binding[j] = BTN_MB12;
    }
    full.communication_backend_configs_count = sizeof(full.communication_backend_configs) /
                                               sizeof(full.communication_backend_configs[0]);
    for (size_t i = 0; i < full.communication_backend_configs_count; ++i) {
        CommunicationBackendConfig &backend = full.communication_backend_configs[i];
        backend.activation_binding_count = sizeof(backend.activation_binding) / sizeof(backend.activation_binding[0]);
        for (size_t j = 0; j < backend.activation_binding_count; ++j) backend.activation_binding[j] = BTN_MB12;
    }
    full.custom_modes_count = sizeof(full.custom_modes) / sizeof(full.custom_modes[0]);
    for (size_t i = 0; i < full.custom_modes_count; ++i) {
        CustomModeConfig &mode = full.custom_modes[i];
        mode.digital_button_mappings_count = sizeof(mode.digital_button_mappings) / sizeof(mode.digital_button_mappings[0]);
        for (size_t j = 0; j < mode.digital_button_mappings_count; ++j) mode.digital_button_mappings[j] = BTN_MB12;
        mode.stick_direction_mappings_count = sizeof(mode.stick_direction_mappings) / sizeof(mode.stick_direction_mappings[0]);
        for (size_t j = 0; j < mode.stick_direction_mappings_count; ++j) mode.stick_direction_mappings[j] = BTN_MB12;
        mode.analog_trigger_mappings_count = sizeof(mode.analog_trigger_mappings) / sizeof(mode.analog_trigger_mappings[0]);
        for (size_t j = 0; j < mode.analog_trigger_mappings_count; ++j) mode.analog_trigger_mappings[j].button = BTN_MB12;
        mode.modifiers_count = sizeof(mode.modifiers) / sizeof(mode.modifiers[0]);
        for (size_t j = 0; j < mode.modifiers_count; ++j) {
            mode.modifiers[j].buttons_count = sizeof(mode.modifiers[j].buttons) / sizeof(mode.modifiers[j].buttons[0]);
            for (size_t k = 0; k < mode.modifiers[j].buttons_count; ++k) mode.modifiers[j].buttons[k] = BTN_MB12;
        }
        mode.button_combo_mappings_count = sizeof(mode.button_combo_mappings) / sizeof(mode.button_combo_mappings[0]);
        for (size_t j = 0; j < mode.button_combo_mappings_count; ++j) {
            mode.button_combo_mappings[j].buttons_count = sizeof(mode.button_combo_mappings[j].buttons) /
                                                          sizeof(mode.button_combo_mappings[j].buttons[0]);
            for (size_t k = 0; k < mode.button_combo_mappings[j].buttons_count; ++k)
                mode.button_combo_mappings[j].buttons[k] = BTN_MB12;
        }
    }
    full.keyboard_modes_count = sizeof(full.keyboard_modes) / sizeof(full.keyboard_modes[0]);
    for (size_t i = 0; i < full.keyboard_modes_count; ++i) {
        KeyboardModeConfig &mode = full.keyboard_modes[i];
        mode.buttons_to_keycodes_count = sizeof(mode.buttons_to_keycodes) / sizeof(mode.buttons_to_keycodes[0]);
        for (size_t j = 0; j < mode.buttons_to_keycodes_count; ++j) mode.buttons_to_keycodes[j].button = BTN_MB12;
    }
    require(validate_config_button_bindings(full), "all populated arrays at maximum valid extents rejected");

    auto rejected = [](const Config &candidate, const char *label) {
        require(!validate_config_button_bindings(candidate), std::string(label) + " count overflow accepted");
    };
    Config over = blank_config();
    over.game_mode_configs_count = 1; over.game_mode_configs[0].socd_pairs_count = 11; rejected(over, "SOCD");
    over = blank_config(); over.game_mode_configs_count = 1; over.game_mode_configs[0].button_remapping_count = 61; rejected(over, "remap");
    over = blank_config(); over.game_mode_configs_count = 1; over.game_mode_configs[0].activation_binding_count = 5; rejected(over, "game activation");
    over = blank_config(); over.communication_backend_configs_count = 1; over.communication_backend_configs[0].activation_binding_count = 3; rejected(over, "backend activation");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].digital_button_mappings_count = 19; rejected(over, "custom digital");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].stick_direction_mappings_count = 9; rejected(over, "custom stick");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].analog_trigger_mappings_count = 5; rejected(over, "custom trigger");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].modifiers_count = 21; rejected(over, "custom modifiers");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].modifiers_count = 1; over.custom_modes[0].modifiers[0].buttons_count = 4; rejected(over, "modifier buttons");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].button_combo_mappings_count = 6; rejected(over, "custom combos");
    over = blank_config(); over.custom_modes_count = 1; over.custom_modes[0].button_combo_mappings_count = 1; over.custom_modes[0].button_combo_mappings[0].buttons_count = 4; rejected(over, "combo buttons");
    over = blank_config(); over.keyboard_modes_count = 1; over.keyboard_modes[0].buttons_to_keycodes_count = 61; rejected(over, "keyboard keymap");
}

void last_element_invalid_controls() {
    for (size_t binding_class = 0; binding_class < 12; ++binding_class) {
        Config config = blank_config();
        switch (binding_class) {
            case 0:
                config.game_mode_configs_count = 1;
                config.game_mode_configs[0].activation_binding_count = 2;
                config.game_mode_configs[0].activation_binding[0] = BTN_LF1;
                store_raw(config.game_mode_configs[0].activation_binding[1], 61);
                break;
            case 1:
            case 2:
                config.game_mode_configs_count = 1;
                config.game_mode_configs[0].button_remapping_count = 2;
                for (size_t i = 0; i < 2; ++i) config.game_mode_configs[0].button_remapping[i].physical_button = BTN_LF1;
                if (binding_class == 1) store_raw(config.game_mode_configs[0].button_remapping[1].physical_button, 61);
                else { config.game_mode_configs[0].button_remapping[0].activates = BTN_LF1; store_raw(config.game_mode_configs[0].button_remapping[1].activates, 61); }
                break;
            case 3:
            case 4:
                config.game_mode_configs_count = 1;
                config.game_mode_configs[0].socd_pairs_count = 2;
                for (size_t i = 0; i < 2; ++i) {
                    config.game_mode_configs[0].socd_pairs[i].button_dir1 = BTN_LF1;
                    config.game_mode_configs[0].socd_pairs[i].button_dir2 = BTN_RF1;
                }
                if (binding_class == 3) store_raw(config.game_mode_configs[0].socd_pairs[1].button_dir1, 61);
                else store_raw(config.game_mode_configs[0].socd_pairs[1].button_dir2, 61);
                break;
            case 5:
                config.communication_backend_configs_count = 1;
                config.communication_backend_configs[0].activation_binding_count = 2;
                config.communication_backend_configs[0].activation_binding[0] = BTN_LF1;
                store_raw(config.communication_backend_configs[0].activation_binding[1], 61);
                break;
            case 6:
            case 7: {
                config.custom_modes_count = 1;
                CustomModeConfig &mode = config.custom_modes[0];
                if (binding_class == 6) {
                    mode.modifiers_count = 2;
                    for (size_t i = 0; i < 2; ++i) { mode.modifiers[i].buttons_count = 2; mode.modifiers[i].buttons[0] = BTN_LF1; mode.modifiers[i].buttons[1] = BTN_RF1; }
                    store_raw(mode.modifiers[1].buttons[1], 61);
                } else {
                    mode.button_combo_mappings_count = 2;
                    for (size_t i = 0; i < 2; ++i) { mode.button_combo_mappings[i].buttons_count = 2; mode.button_combo_mappings[i].buttons[0] = BTN_LF1; mode.button_combo_mappings[i].buttons[1] = BTN_RF1; }
                    store_raw(mode.button_combo_mappings[1].buttons[1], 61);
                }
                break;
            }
            case 8:
            case 9:
                config.custom_modes_count = 1;
                if (binding_class == 8) {
                    config.custom_modes[0].digital_button_mappings_count = 2;
                    config.custom_modes[0].digital_button_mappings[0] = BTN_LF1;
                    store_raw(config.custom_modes[0].digital_button_mappings[1], 61);
                } else {
                    config.custom_modes[0].stick_direction_mappings_count = 2;
                    config.custom_modes[0].stick_direction_mappings[0] = BTN_LF1;
                    store_raw(config.custom_modes[0].stick_direction_mappings[1], 61);
                }
                break;
            case 10:
                config.custom_modes_count = 1;
                config.custom_modes[0].analog_trigger_mappings_count = 2;
                config.custom_modes[0].analog_trigger_mappings[0].button = BTN_LF1;
                config.custom_modes[0].analog_trigger_mappings[1].button = BTN_RF1;
                store_raw(config.custom_modes[0].analog_trigger_mappings[1].button, 61);
                break;
            case 11:
                config.keyboard_modes_count = 1;
                config.keyboard_modes[0].buttons_to_keycodes_count = 2;
                config.keyboard_modes[0].buttons_to_keycodes[0].button = BTN_LF1;
                config.keyboard_modes[0].buttons_to_keycodes[1].button = BTN_RF1;
                store_raw(config.keyboard_modes[0].buttons_to_keycodes[1].button, 61);
                break;
        }
        require(!validate_config_button_bindings(config), "last populated invalid element accepted in class " +
                std::to_string(binding_class));
    }
}

void structural_absence_and_exclusions() {
    Config config = blank_config();
    config.game_mode_configs_count = 1;
    config.communication_backend_configs_count = 1;
    config.custom_modes_count = 1;
    config.keyboard_modes_count = 1;
    require(validate_config_button_bindings(config), "count-zero backing zeros rejected");
    config.rgb_configs_count = sizeof(config.rgb_configs) / sizeof(config.rgb_configs[0]);
    store_raw(config.rgb_configs[0].button_colors[0].button, 0);
    config.rgb_configs[0].button_colors_count = 1;
    require(validate_config_button_bindings(config), "excluded RGB target affected binding validation");
}

void accepted_glyph_defaults() {
    require(validate_config_button_bindings(default_config), "accepted Glyph source defaults rejected");
}

}  // namespace

int main() {
    try {
        static_assert(sizeof(Button) == 4, "host must exercise the selected four-byte Pico enum representation");
        positive_matrix();
        negative_matrix();
        extent_matrix();
        last_element_invalid_controls();
        structural_absence_and_exclusions();
        accepted_glyph_defaults();
        std::cout << "button_class_count=" << (sizeof(kCases) / sizeof(kCases[0])) << " result=PASS\n";
        std::cout << "named_ids=1..60 per class result=PASS\n";
        std::cout << "invalid_raw=0,61..65,127,255,ffffffff per class result=PASS\n";
        std::cout << "extent_absence_disable_sentinel_rgb_exclusion accepted_defaults result=PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "result=FAIL error=" << error.what() << "\n";
        return 1;
    }
}
