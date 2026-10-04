#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include "modes/CustomKeyboardMode.hpp"
#include "util/state_util.hpp"
#include "source_defaults.hpp"

static void require(bool condition, const char *message) {
    if (!condition) { std::cerr << message << '\n'; std::exit(1); }
}
// Observe the actual virtual callbacks in SendReport, without replacing logic.
class ObservedKeyboard : public CustomKeyboardMode {
public:
    uint64_t remapped = 0, transformed = 0;
    unsigned remap_calls = 0, socd_calls = 0;
protected:
    void HandleRemap(const InputState &original, InputState &copy) override {
        InputMode::HandleRemap(original, copy); remapped = copy.buttons; ++remap_calls;
    }
    void HandleSocd(InputState &copy) override {
        InputMode::HandleSocd(copy); transformed = copy.buttons; ++socd_calls;
    }
};
static uint64_t mask(std::initializer_list<Button> buttons) {
    uint64_t value = 0;
    for (auto b : buttons) set_button(value, b, true);
    return value;
}
static void step(ObservedKeyboard &mode, const KeyboardModeConfig &keys,
                 const char *id, uint64_t original, uint64_t remapped, uint64_t transformed) {
    InputState input{}; input.buttons = original;
    unsigned remap_before = mode.remap_calls, socd_before = mode.socd_calls;
    size_t reports_before = TUKeyboard::reports.size(), presses_before = TUKeyboard::presses.size();
    mode.SendReport(input);
    require(input.buttons == original, "original input mutated");
    require(mode.remap_calls == remap_before + 1 && mode.socd_calls == socd_before + 1, "pipeline omitted");
    require(mode.remapped == remapped && mode.transformed == transformed, "transformed copy mismatch");
    require(TUKeyboard::reports.size() == reports_before + 1, "sendState count mismatch");
    std::array<bool, 256> expected{};
    size_t call = presses_before;
    for (size_t i = 0; i < keys.buttons_to_keycodes_count; ++i) {
        auto entry = keys.buttons_to_keycodes[i];
        if (entry.button == BTN_UNSPECIFIED) continue;
        bool pressed = get_button(original, entry.button);
        require(call < TUKeyboard::presses.size(), "missing key call");
        require(TUKeyboard::presses[call++] == std::make_pair(uint8_t(entry.keycode), pressed), "original key call mismatch");
        expected[entry.keycode] = pressed;
    }
    require(call == TUKeyboard::presses.size(), "extra key call");
    require(TUKeyboard::reports.back() == expected, "key snapshot mismatch");
    std::cout << id << ':' << original << ':' << mode.remapped << ':' << mode.transformed << ':';
    for (size_t i = 0; i < expected.size(); ++i) if (expected[i]) std::cout << i << ',';
    std::cout << '\n';
}
int main() {
    require(source_profile.mode_id == MODE_KEYBOARD && source_profile.keyboard_mode_config == 1, "default profile mismatch");
    require(source_profile.socd_pairs_count == 2 && source_keys.buttons_to_keycodes_count == 35, "default counts mismatch");
    TUKeyboard::reset();
    {
        auto config = source_profile;
        ObservedKeyboard mode; mode.SetConfig(config, source_keys);
        require(TUKeyboard::begins == 1, "begin missing");
        step(mode, source_keys, "idle", 0, 0, 0);
        // Exercise each default plain key and release with fresh neutral SOCD history.
        for (size_t i = 0; i < source_keys.buttons_to_keycodes_count; ++i) {
            auto b = source_keys.buttons_to_keycodes[i].button;
            std::string id = "plain_" + std::to_string(i);
            step(mode, source_keys, id.c_str(), mask({b}), mask({b}), mask({b}));
            step(mode, source_keys, (id + "_release").c_str(), 0, 0, 0);
        }
    }
    require(TUKeyboard::releases == 1 && TUKeyboard::reports.back() == std::array<bool, 256>{}, "destructor releaseAll/sendState mismatch");
    require(TUKeyboard::events[TUKeyboard::events.size()-2] == 'R' && TUKeyboard::events.back() == 'S', "destructor order mismatch");
    for (unsigned pair = 0; pair < 2; ++pair) {
        auto config = source_profile; ObservedKeyboard mode; mode.SetConfig(config, source_keys);
        Button a = config.socd_pairs[pair].button_dir1, b = config.socd_pairs[pair].button_dir2;
        std::string id = "socd_" + std::to_string(pair);
        step(mode, source_keys, (id + "_simultaneous").c_str(), mask({a,b}), mask({a,b}), 0);
        step(mode, source_keys, (id + "_first").c_str(), mask({a}), mask({a}), mask({a}));
        step(mode, source_keys, (id + "_second").c_str(), mask({a,b}), mask({a,b}), mask({b}));
        step(mode, source_keys, (id + "_release_second").c_str(), mask({a}), mask({a}), mask({a}));
        step(mode, source_keys, (id + "_reverse_first").c_str(), mask({b}), mask({b}), mask({b}));
        step(mode, source_keys, (id + "_reverse_second").c_str(), mask({a,b}), mask({a,b}), mask({a}));
        step(mode, source_keys, (id + "_release").c_str(), 0, 0, 0);
    }
    {
        auto config = source_profile; ObservedKeyboard mode; mode.SetConfig(config, source_keys);
        for (Button b : {BTN_MB1, BTN_MB2, BTN_MB3, BTN_MB4, BTN_MB5, BTN_MB6})
            step(mode, source_keys, ("default_unmap_" + std::to_string(b)).c_str(), mask({b}), 0, 0);
        // The literal count is seven although eight initializer entries exist.
        step(mode, source_keys, "default_mb7_outside_count", mask({BTN_MB7}), mask({BTN_MB7}), mask({BTN_MB7}));
    }
    {
        auto config = source_profile;
        // Deliberate bounded test config; no source default or policy change.
        config.button_remapping_count = 1;
        config.button_remapping[0] = { BTN_RF1, BTN_LF3 };
        ObservedKeyboard mode; mode.SetConfig(config, source_keys);
        step(mode, source_keys, "remap_plain", mask({BTN_RF1}), mask({BTN_LF3}), mask({BTN_LF3}));
        step(mode, source_keys, "remap_socd_second", mask({BTN_RF1, BTN_LF1}), mask({BTN_LF3, BTN_LF1}), mask({BTN_LF1}));
        step(mode, source_keys, "remap_release", 0, 0, 0);
        config.button_remapping[0] = { BTN_RF1, BTN_UNSPECIFIED };
        step(mode, source_keys, "unmap_mapped_key", mask({BTN_RF1}), 0, 0);
    }
    {
        auto config = source_profile; ObservedKeyboard mode; mode.SetConfig(config, source_keys);
        step(mode, source_keys, "both_pairs_simultaneous", mask({BTN_LF3,BTN_LF1,BTN_LT1,BTN_RT4}), mask({BTN_LF3,BTN_LF1,BTN_LT1,BTN_RT4}), 0);
    }
    {
        auto config = source_profile;
        config.button_remapping_count = 2;
        config.button_remapping[0] = { BTN_RF1, BTN_LF2 };
        config.button_remapping[1] = { BTN_RF1, BTN_LF4 };
        ObservedKeyboard mode; mode.SetConfig(config, source_keys);
        step(mode, source_keys, "duplicate_physical_first_wins", mask({BTN_RF1}), mask({BTN_LF2}), mask({BTN_LF2}));
        config.button_remapping[1] = { BTN_RF2, BTN_LF2 };
        step(mode, source_keys, "shared_target_first_only", mask({BTN_RF1}), mask({BTN_LF2}), mask({BTN_LF2}));
        step(mode, source_keys, "shared_target_second_only", mask({BTN_RF2}), mask({BTN_LF2}), mask({BTN_LF2}));
        step(mode, source_keys, "shared_target_both", mask({BTN_RF1,BTN_RF2}), mask({BTN_LF2}), mask({BTN_LF2}));
        step(mode, source_keys, "shared_target_release", 0, 0, 0);
    }
    {
        auto config = source_profile; auto keys = source_keys;
        keys.buttons_to_keycodes[keys.buttons_to_keycodes_count++] = { BTN_UNSPECIFIED, 200 };
        ObservedKeyboard mode; mode.SetConfig(config, keys);
        step(mode, keys, "unspecified_key_skipped", mask({BTN_RF1}), mask({BTN_RF1}), mask({BTN_RF1}));
    }
    require(TUKeyboard::begins == 8 && TUKeyboard::releases == 8, "lifecycle counts mismatch");
    require(TUKeyboard::reports.back() == std::array<bool, 256>{}, "held key destructor release failed");
    require(TUKeyboard::events[TUKeyboard::events.size()-2] == 'R' && TUKeyboard::events.back() == 'S', "final destructor order mismatch");
    std::cout << "lifecycle:8:8:released\n";
}
