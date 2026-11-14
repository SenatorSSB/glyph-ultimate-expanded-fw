#pragma once
#include <cstdint>

using absolute_time_t = uint64_t;
inline uint64_t clock_us = 0;
inline absolute_time_t make_timeout_time_us(uint64_t us) { return clock_us + us; }
inline absolute_time_t make_timeout_time_ms(uint64_t ms) { return clock_us + 1000 * ms; }
inline bool time_reached(absolute_time_t deadline) { return clock_us >= deadline; }
inline void tight_loop_contents() { ++clock_us; }
