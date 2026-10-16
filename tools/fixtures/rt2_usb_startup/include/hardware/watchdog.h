#pragma once
#include <cstdint>
struct WatchdogHw { uint32_t scratch[8]={}; };
extern WatchdogHw watchdog_registers;
#define watchdog_hw (&watchdog_registers)
