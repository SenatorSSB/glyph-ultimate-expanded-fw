#pragma once
#include <cstdint>
struct HostWatchdog { volatile uint32_t ctrl = 0; volatile uint32_t scratch[8] = {}; };
inline HostWatchdog host_watchdog;
inline HostWatchdog *watchdog_hw = &host_watchdog;
constexpr uint32_t WATCHDOG_CTRL_ENABLE_BITS = 1u << 30;
inline unsigned host_clear_calls = 0;
inline void hw_clear_bits(volatile uint32_t *value, uint32_t mask) { ++host_clear_calls; *value &= ~mask; }
