#pragma once
// Platform header boundary for host execution of the unchanged Pico source.
#include <cstdint>
using uint = unsigned int;
struct absolute_time_t {
    int64_t _private_us_since_boot;
    absolute_time_t(int64_t value = 0) : _private_us_since_boot(value) {}
    operator int64_t() const { return _private_us_since_boot; }
};
inline absolute_time_t get_absolute_time() { return absolute_time_t(0); }
inline int64_t absolute_time_diff_us(absolute_time_t from, absolute_time_t to) {
    return to._private_us_since_boot - from._private_us_since_boot;
}
inline bool time_reached(absolute_time_t) { return true; }
inline absolute_time_t make_timeout_time_ms(uint32_t ms) { return absolute_time_t(ms * 1000LL); }
inline bool gpio_get(unsigned) { return true; }
inline void gpio_put(unsigned, bool) {}
inline constexpr int GPIO_OUT = 1;
inline constexpr int GPIO_IN = 0;
inline void gpio_init(unsigned) {}
inline void gpio_set_dir(unsigned, int) {}
inline void gpio_pull_up(unsigned) {}
inline void gpio_pull_down(unsigned) {}
