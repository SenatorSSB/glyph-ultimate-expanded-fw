#pragma once
#include <cstdint>
struct pio_hw;
using PIO = pio_hw *;
inline PIO pio0 = nullptr;
inline PIO pio1 = nullptr;
struct pio_sm_config { uint32_t host_placeholder = 0; };
