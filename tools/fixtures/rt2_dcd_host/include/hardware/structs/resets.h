#pragma once
#include <stdint.h>
#include "hardware/regs/resets.h"
typedef struct {uint32_t reset=0,reset_done=0;} ResetsHw;
extern ResetsHw reset_registers;
#define resets_hw (&reset_registers)
