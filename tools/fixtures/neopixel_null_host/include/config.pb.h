#pragma once
#include <cstddef>
#include <cstdint>
using pb_size_t = std::size_t;
using Button = int;
struct ButtonToColorMapping { Button button = 0; std::uint32_t color = 0; };
enum RgbAnimationId {
    RGB_ANIM_STATIC = 0,
    RGB_ANIM_BREATHE = 1,
    RGB_ANIM_REACTIVE_SIMPLE = 2,
    RGB_ANIM_RAINBOW_SHIFT = 3,
    RGB_ANIM_RAINBOW_XWAVE_LEFT = 4,
    RGB_ANIM_UNSUPPORTED = 255
};
struct RgbConfig {
    ButtonToColorMapping button_colors[36] = {};
    std::size_t button_colors_count = 0;
    RgbAnimationId animation = RGB_ANIM_STATIC;
    std::uint8_t speed = 0;
};
struct GameModeConfig { std::uint8_t rgb_config = 0; };
