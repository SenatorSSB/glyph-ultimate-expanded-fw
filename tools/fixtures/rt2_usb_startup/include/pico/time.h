#pragma once
#include <stdint.h>
static inline void sleep_ms(uint32_t){}
void busy_wait_us_32(uint32_t);

// Legacy startup harness never executes the independent timed observer.
static inline uint64_t time_us_64(){return 0;}
