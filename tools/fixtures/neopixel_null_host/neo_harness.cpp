#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
struct absolute_time_t { std::int64_t _private_us_since_boot = 0; };
inline absolute_time_t get_absolute_time() { static std::int64_t now = 1000; return absolute_time_t{now += 1000}; }
inline std::int64_t absolute_time_diff_us(absolute_time_t from, absolute_time_t to) { return to._private_us_since_boot - from._private_us_since_boot; }
#include <config.pb.h>
class InputMode {
public:
    explicit InputMode(GameModeConfig *cfg) : cfg_(cfg) {}
    GameModeConfig *GetConfig() { return cfg_; }
private:
    GameModeConfig *cfg_;
};
#include "../../../HAL/pico/include/comms/NeoPixelBackend.hpp"
ButtonToColorMappingHSV RGB_Wave_StarterHSV[36] = {};
ButtonToColorMapping RGB_Wave_Starter[36] = {};

int main(int argc, char **argv) {
    if (argc != 2) return 90;
    const char *which = argv[1];
    InputState inputs;
    std::uint8_t brightness = 96;
    Button buttons[4] = {1, 2, 3, 4};
    RgbConfig configs[2] = {};
    configs[0].speed = 2;
    configs[0].animation = RGB_ANIM_STATIC;
    configs[0].button_colors_count = 1;
    configs[0].button_colors[0] = {1, 0x123456};
    configs[1].speed = 3;
    configs[1].animation = RGB_ANIM_RAINBOW_SHIFT;
    configs[1].button_colors_count = 1;
    configs[1].button_colors[0] = {1, 0x00ffffff};
    NeoPixelBackend<1, 4> backend(inputs, nullptr, 0, buttons, configs, 2, brightness);
    GameModeConfig game_cfg{};
    InputMode mode(&game_cfg);

    if (std::strcmp(which, "startup_null") == 0) {
        // Source-supported initial state: constructor leaves _config null.
    } else if (std::strcmp(which, "no_mode") == 0) {
        backend.SetGameMode(nullptr); // Injected direct host call; loop1 does not establish reachability.
    } else if (std::strcmp(which, "no_config") == 0) {
        InputMode no_config(nullptr);
        backend.SetGameMode(&no_config); // Injected direct host call.
    } else if (std::strcmp(which, "zero_rgb_index") == 0) {
        game_cfg.rgb_config = 0;
        backend.SetGameMode(&mode); // Injected malformed config sequence.
    } else if (std::strcmp(which, "out_of_range_rgb_index") == 0) {
        game_cfg.rgb_config = 3;
        backend.SetGameMode(&mode); // Injected malformed config sequence.
    } else if (std::strcmp(which, "unsupported_animation") == 0) {
        game_cfg.rgb_config = 1;
        configs[0].animation = RGB_ANIM_BREATHE;
        backend.SetGameMode(&mode); // Injected unsupported animation sequence.
    } else if (std::strcmp(which, "unknown_animation_enum") == 0) {
        game_cfg.rgb_config = 1;
        configs[0].animation = static_cast<RgbAnimationId>(6);
        backend.SetGameMode(&mode); // Injected unknown enum follows default branch.
    } else if (std::strcmp(which, "valid_static") == 0) {
        game_cfg.rgb_config = 1;
        backend.SetGameMode(&mode);
    } else if (std::strcmp(which, "valid_dynamic") == 0) {
        game_cfg.rgb_config = 2;
        backend.SetGameMode(&mode);
    } else {
        return 91;
    }
    std::fprintf(stderr, "case=%s reached_SendReport\n", which);
    backend.SendReport();
    std::printf("case=%s result=RETURNED show_count=%d brightness=%u\n", which, FastLED.show_count, FastLED.brightness);
    return 0;
}
