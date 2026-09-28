#pragma once
#include <cstddef>
#include <cstdint>
using pb_size_t = std::size_t;
using Button = int;
struct ButtonToColorMapping { Button button = 0; std::uint32_t color = 0; };
enum RgbAnimationId {
    RGB_ANIM_UNSPECIFIED = 0,
    RGB_ANIM_STATIC = 1,
    RGB_ANIM_BREATHE = 2,
    RGB_ANIM_REACTIVE_SIMPLE = 3,
    RGB_ANIM_RAINBOW_SHIFT = 4,
    RGB_ANIM_RAINBOW_XWAVE_LEFT = 5
};
struct RgbConfig {
    std::size_t button_colors_count = 0;
    ButtonToColorMapping button_colors[60] = {};
    std::uint32_t default_color = 0;
    RgbAnimationId animation = RGB_ANIM_STATIC;
    std::uint8_t speed = 0;
};
struct GameModeConfig { std::uint8_t rgb_config = 0; };
