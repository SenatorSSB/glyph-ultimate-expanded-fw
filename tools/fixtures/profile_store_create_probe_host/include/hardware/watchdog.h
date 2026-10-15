#pragma once
#include <hardware/structs/watchdog.h>
inline uint32_t host_watchdog_deadline = 0, host_magic_at_enable = 0, host_stage_at_enable = 0;
inline unsigned host_enable_calls = 0, host_update_calls = 0;
inline bool host_pause_on_debug = false, host_caused_reboot = false;
inline void watchdog_enable(uint32_t deadline, bool pause) {
  ++host_enable_calls; host_watchdog_deadline = deadline; host_pause_on_debug = pause;
  host_magic_at_enable = watchdog_hw->scratch[2]; host_stage_at_enable = watchdog_hw->scratch[3];
  // Exact pinned SDK watchdog_enable owns this non-reboot marker.
  watchdog_hw->scratch[4] = 0x6ab73121;
  watchdog_hw->ctrl |= WATCHDOG_CTRL_ENABLE_BITS;
}
inline void watchdog_update() { ++host_update_calls; }
inline bool watchdog_caused_reboot() { return host_caused_reboot; }
