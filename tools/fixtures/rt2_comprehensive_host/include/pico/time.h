#pragma once
#include <stdint.h>
static inline void sleep_ms(uint32_t ms){(void)ms;}
void busy_wait_us_32(uint32_t);
uint32_t time_us_32();
uint64_t time_us_64();
