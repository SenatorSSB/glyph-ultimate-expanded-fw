#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <iterator>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>
#include <config.pb.h>
#include "core/config_validation.hpp"

static_assert(std::is_same<decltype(GameModeConfig::custom_mode_config), uint32_t>::value,
              "custom references retain the authenticated decoded width");
static_assert(std::is_same<decltype(GameModeConfig::keyboard_mode_config), uint8_t>::value,
              "keyboard references use the authenticated generated width");
static_assert(std::is_same<decltype(CommunicationBackendConfig::default_mode_config), uint8_t>::value,
              "backend mode references use the authenticated generated width");
static_assert(std::is_same<decltype(Config::default_backend_config), uint8_t>::value,
              "default backend references use the authenticated generated width");
static Config value, original;
static size_t cases = 0, extent_cases = 0, reference_cases = 0, binding_cases = 0,
              order_cases = 0, control_cases = 0;
static const std::string binding_error = "Config contains an invalid button binding";
static void require(bool condition, const std::string &message) {
    if (!condition) throw std::runtime_error(message);
}

static void reset() {
    value = Config_init_default;
    value.game_mode_configs_count = std::size(value.game_mode_configs);
    value.communication_backend_configs_count = std::size(value.communication_backend_configs);
    value.custom_modes_count = std::size(value.custom_modes);
    value.keyboard_modes_count = std::size(value.keyboard_modes);
    value.rgb_configs_count = std::size(value.rgb_configs);
    for (auto &mode : value.game_mode_configs) {
        mode.mode_id = MODE_ULTIMATE;
        mode.socd_pairs_count = std::size(mode.socd_pairs);
        for (auto &pair : mode.socd_pairs) { pair.button_dir1 = BTN_LF1; pair.button_dir2 = BTN_RF1; }
        mode.button_remapping_count = std::size(mode.button_remapping);
        for (auto &remap : mode.button_remapping) { remap.physical_button = BTN_LF1; remap.activates = BTN_RF1; }
        mode.activation_binding_count = std::size(mode.activation_binding);
        for (auto &button : mode.activation_binding) button = BTN_LF1;
        mode.applicable_backends_count = std::size(mode.applicable_backends);
        mode.menu_button_icon_count = std::size(mode.menu_button_icon);
    }
    for (auto &backend : value.communication_backend_configs) {
        backend.activation_binding_count = std::size(backend.activation_binding);
        for (auto &button : backend.activation_binding) button = BTN_LF1;
    }
    for (auto &mode : value.custom_modes) {
        mode.digital_button_mappings_count = std::size(mode.digital_button_mappings);
        for (auto &button : mode.digital_button_mappings) button = BTN_LF1;
        mode.stick_direction_mappings_count = std::size(mode.stick_direction_mappings);
        for (auto &button : mode.stick_direction_mappings) button = BTN_LF1;
        mode.analog_trigger_mappings_count = std::size(mode.analog_trigger_mappings);
        for (auto &mapping : mode.analog_trigger_mappings) mapping.button = BTN_LF1;
        mode.modifiers_count = std::size(mode.modifiers);
        for (auto &modifier : mode.modifiers) {
            modifier.buttons_count = std::size(modifier.buttons);
            for (auto &button : modifier.buttons) button = BTN_LF1;
        }
        mode.button_combo_mappings_count = std::size(mode.button_combo_mappings);
        for (auto &combo : mode.button_combo_mappings) {
            combo.buttons_count = std::size(combo.buttons);
            for (auto &button : combo.buttons) button = BTN_LF1;
        }
    }
    for (auto &mode : value.keyboard_modes) {
        mode.buttons_to_keycodes_count = std::size(mode.buttons_to_keycodes);
        for (auto &mapping : mode.buttons_to_keycodes) mapping.button = BTN_LF1;
    }
    for (auto &rgb : value.rgb_configs) rgb.button_colors_count = std::size(rgb.button_colors);
}

// This harness exercises the real pure callback and its error byte/length
// contract. Actual WritePacket transport is exercised by the separate SET TU.
static void check(const std::string &label, bool accepted,
                  const std::string &message = "", bool includes_nul = false,
                  bool extents_fit = true) {
    std::memcpy(&original, &value, sizeof(value));
    ConfigValidationError error;
    std::memset(error.message, 'X', sizeof(error.message));
    error.length = sizeof(error.message);
    require(validate_config_extents(value) == extents_fit, label + ": extent verdict");
    require(validate_config_semantics(value, error) == accepted, label + ": semantic verdict");
    require(std::memcmp(&original, &value, sizeof(value)) == 0, label + ": mutated Config");
    if (accepted) {
        require(error.length == 0, label + ": stale error length");
        for (char byte : error.message) require(byte == 0, label + ": stale error bytes");
    } else {
        require(std::string(error.message) == message, label + ": error words/order");
        require(error.length == message.size() + (includes_nul ? 1 : 0), label + ": wire length");
        require(std::memcmp(error.message, message.c_str(), message.size() + 1) == 0,
                label + ": diagnostic bytes/terminator");
    }
    ++cases;
    std::cout << "semantic_case=" << label << " accepted=" << accepted
              << " error_length=" << error.length << " pure=BYTE_EXACT PASS\n";
}

struct Extent {
    const char *name;
    size_t capacity;
    bool nested;
    std::function<pb_size_t &(Config &, bool)> count;
};
#define TOP(field) Extent{#field, std::size(value.field), false, [](Config &c, bool)->pb_size_t& { return c.field##_count; }}
#define NEST(name, object, field) Extent{name, [](const Config &c) { constexpr bool last = false; return std::size(c.object.field); }(value), true, [](Config &c, bool last)->pb_size_t& { (void)last; return c.object.field##_count; }}
static void extents() {
    const Extent fields[] = {
        TOP(game_mode_configs), TOP(communication_backend_configs), TOP(custom_modes), TOP(keyboard_modes), TOP(rgb_configs),
        NEST("game.socd_pairs", game_mode_configs[last ? 29 : 0], socd_pairs),
        NEST("game.button_remapping", game_mode_configs[last ? 29 : 0], button_remapping),
        NEST("game.activation_binding", game_mode_configs[last ? 29 : 0], activation_binding),
        NEST("game.applicable_backends", game_mode_configs[last ? 29 : 0], applicable_backends),
        NEST("game.menu_button_icon", game_mode_configs[last ? 29 : 0], menu_button_icon),
        NEST("backend.activation_binding", communication_backend_configs[last ? 14 : 0], activation_binding),
        NEST("custom.digital_button_mappings", custom_modes[last ? 9 : 0], digital_button_mappings),
        NEST("custom.stick_direction_mappings", custom_modes[last ? 9 : 0], stick_direction_mappings),
        NEST("custom.analog_trigger_mappings", custom_modes[last ? 9 : 0], analog_trigger_mappings),
        NEST("custom.modifiers", custom_modes[last ? 9 : 0], modifiers),
        NEST("custom.button_combo_mappings", custom_modes[last ? 9 : 0], button_combo_mappings),
        NEST("custom.modifier.buttons", custom_modes[last ? 9 : 0].modifiers[last ? 19 : 0], buttons),
        NEST("custom.combo.buttons", custom_modes[last ? 9 : 0].button_combo_mappings[last ? 4 : 0], buttons),
        NEST("keyboard.buttons_to_keycodes", keyboard_modes[last ? 9 : 0], buttons_to_keycodes),
        NEST("rgb.button_colors", rgb_configs[last ? 29 : 0], button_colors),
    };
    require(std::size(fields) == 20, "complete generated extent census");
    for (const Extent &field : fields) {
        for (bool last : {false, true}) {
            if (last && !field.nested) continue;
            for (size_t count : {size_t(0), field.capacity, field.capacity + 1}) {
                reset(); field.count(value, last) = count;
                const bool valid = count <= field.capacity;
                check(std::string("extent/") + field.name + (last ? "/last/" : "/first/") + std::to_string(count),
                      valid, valid ? "" : binding_error, !valid, valid);
                ++extent_cases;
            }
        }
    }
}
#undef TOP
#undef NEST

static std::vector<uint32_t> unique_values(std::initializer_list<uint32_t> input) {
    std::vector<uint32_t> result;
    for (uint32_t item : input) {
        bool found = false; for (uint32_t previous : result) found |= previous == item;
        if (!found) result.push_back(item);
    }
    return result;
}
static void references() {
    for (size_t count : {size_t(0), size_t(1), size_t(15)}) {
        for (uint32_t index : unique_values({0, 1, uint32_t(count), uint32_t(count+1), 255})) {
            reset(); value.communication_backend_configs_count = count; value.default_backend_config = index;
            const bool valid = index <= count;
            check("default_backend/" + std::to_string(count) + "/" + std::to_string(index), valid,
                  valid ? "" : "Default backend ID is " + std::to_string(index) + " but only " + std::to_string(count) + " backend configs are defined");
            ++reference_cases;
        }
    }
    for (bool last : {false, true}) {
        const size_t b = last ? 14 : 0, g = last ? 29 : 0;
        for (size_t count : {size_t(0), size_t(1), size_t(30)}) {
            for (uint32_t index : unique_values({0, 1, uint32_t(count), uint32_t(count+1), 255})) {
                reset(); value.game_mode_configs_count = count; value.communication_backend_configs[b].default_mode_config = index;
                const bool valid = index <= count;
                check("backend_mode/" + std::to_string(b+1) + "/" + std::to_string(count) + "/" + std::to_string(index), valid,
                    valid ? "" : "Default mode ID is " + std::to_string(index) + " for backend " + std::to_string(b+1) + " but only " + std::to_string(count) + " modes are defined");
                ++reference_cases;
            }
        }
        for (size_t count : {size_t(0), size_t(1), size_t(10)}) {
            for (GameModeId mode : {MODE_UNSPECIFIED, MODE_MELEE, MODE_PROJECT_M, MODE_ULTIMATE, MODE_FGC,
                    MODE_RIVALS_OF_AETHER, MODE_KEYBOARD, MODE_CUSTOM, MODE_64, MODE_RIVALS2, MODE_NUM_VALUES}) {
                for (uint32_t index : unique_values({0, 1, uint32_t(count), uint32_t(count+1), 255})) {
                    reset(); value.keyboard_modes_count = count; value.game_mode_configs[g].mode_id = mode;
                    value.game_mode_configs[g].keyboard_mode_config = index;
                    const bool wrong = index > 0 && mode != MODE_KEYBOARD, valid = !wrong && index <= count;
                    const std::string error = wrong ? "keyboard_mode_id is set for game mode " + std::to_string(g+1) + " but mode_id is not MODE_KEYBOARD"
                        : "Keyboard mode ID " + std::to_string(index) + " is for game mode " + std::to_string(g+1) + " but only " + std::to_string(count) + " keyboard modes are defined";
                    check("keyboard/" + std::to_string(g+1) + "/" + std::to_string(mode) + "/" + std::to_string(count) + "/" + std::to_string(index), valid, valid ? "" : error);
                    ++reference_cases;
                }
                for (uint32_t index : unique_values({0, 1, uint32_t(count), uint32_t(count+1), 255, 256, 257, 65536, std::numeric_limits<uint32_t>::max()})) {
                    reset(); value.custom_modes_count = count; value.game_mode_configs[g].mode_id = mode;
                    value.game_mode_configs[g].custom_mode_config = index;
                    const bool wrong = index > 0 && mode != MODE_CUSTOM, valid = !wrong && index <= count;
                    const std::string error = wrong ? "custom_mode_id is set for game mode " + std::to_string(g+1) + " but mode_id is not MODE_CUSTOM"
                        : "Custom mode ID " + std::to_string(index) + " is for game mode config " + std::to_string(g+1) + " but only " + std::to_string(count) + " custom modes are defined";
                    check("custom32/" + std::to_string(g+1) + "/" + std::to_string(mode) + "/" + std::to_string(count) + "/" + std::to_string(index), valid, valid ? "" : error);
                    ++reference_cases;
                }
            }
        }
    }
    require(static_cast<uint8_t>(uint32_t(256)) == 0, "dangerous narrowing negative-control identity");
}

struct Binding { const char *name; bool zero_allowed; std::function<Button &(Config &, bool)> leaf; };
static void bindings() {
    const Binding fields[] = {
        {"game.activation", false, [](Config &c, bool last)->Button& { return c.game_mode_configs[last?29:0].activation_binding[last?3:0]; }},
        {"game.remap.physical", false, [](Config &c, bool last)->Button& { return c.game_mode_configs[last?29:0].button_remapping[last?59:0].physical_button; }},
        {"game.remap.activates", true, [](Config &c, bool last)->Button& { return c.game_mode_configs[last?29:0].button_remapping[last?59:0].activates; }},
        {"game.socd.dir1", false, [](Config &c, bool last)->Button& { return c.game_mode_configs[last?29:0].socd_pairs[last?9:0].button_dir1; }},
        {"game.socd.dir2", false, [](Config &c, bool last)->Button& { return c.game_mode_configs[last?29:0].socd_pairs[last?9:0].button_dir2; }},
        {"backend.activation", false, [](Config &c, bool last)->Button& { return c.communication_backend_configs[last?14:0].activation_binding[last?1:0]; }},
        {"custom.digital", false, [](Config &c, bool last)->Button& { return c.custom_modes[last?9:0].digital_button_mappings[last?17:0]; }},
        {"custom.stick", false, [](Config &c, bool last)->Button& { return c.custom_modes[last?9:0].stick_direction_mappings[last?7:0]; }},
        {"custom.modifier", false, [](Config &c, bool last)->Button& { return c.custom_modes[last?9:0].modifiers[last?19:0].buttons[last?2:0]; }},
        {"custom.combo", false, [](Config &c, bool last)->Button& { return c.custom_modes[last?9:0].button_combo_mappings[last?4:0].buttons[last?2:0]; }},
        {"custom.trigger", false, [](Config &c, bool last)->Button& { return c.custom_modes[last?9:0].analog_trigger_mappings[last?3:0].button; }},
        {"keyboard.key", false, [](Config &c, bool last)->Button& { return c.keyboard_modes[last?9:0].buttons_to_keycodes[last?59:0].button; }},
    };
    require(std::size(fields) == 12, "complete existing020 binding class census");
    using Storage = std::underlying_type<Button>::type;
    for (const Binding &field : fields) {
        for (bool last : {false, true}) {
            auto raws = unique_values({0, 1, 60, 61, 255});
            if (sizeof(Button) == 4) { raws.push_back(256); raws.push_back(257); raws.push_back(65536); raws.push_back(std::numeric_limits<uint32_t>::max()); }
            for (uint32_t number : raws) {
                reset(); const Storage representation = number;
                std::memcpy(&field.leaf(value, last), &representation, sizeof(Button));
                const bool valid = (number >= 1 && number <= 60) || (number == 0 && field.zero_allowed);
                check(std::string("binding/") + field.name + (last?"/last/":"/first/") + std::to_string(number), valid,
                      valid ? "" : binding_error, !valid);
                ++binding_cases;
            }
        }
    }
}

static void error_order() {
    for (bool last : {false, true}) {
        const size_t g = last?29:0, b = last?14:0;
        const std::string game = std::to_string(g+1), backend = std::to_string(b+1);
        reset(); value.game_mode_configs[g].custom_mode_config = 256; value.default_backend_config = 16;
        value.game_mode_configs[g].activation_binding[0] = BTN_UNSPECIFIED;
        check("order/binding_before_defaults/"+game, false, binding_error, true); ++order_cases;
        reset(); value.rgb_configs[29].button_colors_count = 61; value.default_backend_config = 16;
        check("order/extents_before_defaults/"+game, false, binding_error, true, false); ++order_cases;
        reset(); value.default_backend_config = 16; value.communication_backend_configs[b].default_mode_config = 31;
        check("order/default_backend_before_backend_mode/"+game, false, "Default backend ID is 16 but only 15 backend configs are defined"); ++order_cases;
        reset(); value.communication_backend_configs[b].default_mode_config = 31; value.game_mode_configs[g].keyboard_mode_config = 1;
        check("order/backend_mode_before_game_refs/"+game, false, "Default mode ID is 31 for backend "+backend+" but only 30 modes are defined"); ++order_cases;
        reset(); value.game_mode_configs[g].keyboard_mode_config = 11; value.game_mode_configs[g].custom_mode_config = 256;
        check("order/keyboard_condition_before_custom_condition/"+game, false, "keyboard_mode_id is set for game mode "+game+" but mode_id is not MODE_KEYBOARD"); ++order_cases;
        reset(); value.game_mode_configs[g].mode_id = MODE_KEYBOARD; value.game_mode_configs[g].keyboard_mode_config = 11; value.game_mode_configs[g].custom_mode_config = 256;
        check("order/custom_condition_before_keyboard_bound/"+game, false, "custom_mode_id is set for game mode "+game+" but mode_id is not MODE_CUSTOM"); ++order_cases;
        reset(); value.game_mode_configs[g].mode_id = MODE_CUSTOM; value.game_mode_configs[g].custom_mode_config = 256;
        check("order/custom_count_fullwidth/"+game, false, "Custom mode ID 256 is for game mode config "+game+" but only 10 custom modes are defined"); ++order_cases;
        reset(); value.game_mode_configs[0].mode_id = MODE_CUSTOM; value.game_mode_configs[0].custom_mode_config = 11;
        value.game_mode_configs[29].keyboard_mode_config = 1;
        check("order/earlier_game_before_later_game/"+game, false, "Custom mode ID 11 is for game mode config 1 but only 10 custom modes are defined"); ++order_cases;
        reset(); value.communication_backend_configs[0].default_mode_config = 31; value.communication_backend_configs[14].default_mode_config = 32;
        check("order/earlier_backend_before_later_backend/"+game, false, "Default mode ID is 31 for backend 1 but only 30 modes are defined"); ++order_cases;
    }
}

static void controls() {
    reset(); check("control/all_generated_counts_at_bound_zero_refs", true); ++control_cases;
    value = Config_init_default; check("control/all_absent_zero_counts_zero_refs", true); ++control_cases;
    reset(); value.game_mode_configs[0].mode_id = MODE_CUSTOM; value.game_mode_configs[0].custom_mode_config = 10;
    value.game_mode_configs[29].mode_id = MODE_KEYBOARD; value.game_mode_configs[29].keyboard_mode_config = 10;
    value.default_backend_config = 15; value.communication_backend_configs[14].default_mode_config = 30;
    check("control/all_reference_exact_bounds", true); ++control_cases;
    reset(); for (auto &mode : value.game_mode_configs) for (auto &remap : mode.button_remapping) remap.activates = BTN_UNSPECIFIED;
    check("control/all_remap_disable_sentinels_preserved", true); ++control_cases;
    reset(); value.game_mode_configs[12].button_remapping[0] = ButtonRemap{BTN_RF3, BTN_LT1};
    value.game_mode_configs[12].button_remapping[1] = ButtonRemap{BTN_RF4, BTN_LT2};
    value.game_mode_configs[12].button_remapping[2] = ButtonRemap{BTN_LT3, BTN_LT3};
    check("control/source_qualified_three_remaps", true); ++control_cases;
    reset(); for (auto &rgb : value.rgb_configs) for (auto &color : rgb.button_colors) color.button = BTN_UNSPECIFIED;
    check("control/rgb_buttons_remain_outside020_policy", true); ++control_cases;
}

int main() {
    try {
        extents(); references(); bindings(); error_order(); controls();
        std::cout << "semantic_matrix extents=" << extent_cases << " extent_classes=20 references=" << reference_cases
                  << " bindings=" << binding_cases << " binding_classes=12 order=" << order_cases
                  << " controls=" << control_cases << " total=" << cases << " button_width=" << sizeof(Button)
                  << " custom_reference_width=" << sizeof(GameModeConfig::custom_mode_config) << " PASS\n";
        std::cout << "case=literal_semantic_fullwidth_0_1_N_Nplus1_255_256_65536_uint32max PASS\n"
                  << "case=wrongmode_error_order_and_256_not_zero PASS\n"
                  << "case=bounded_extents_and_pure_bytes PASS\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
