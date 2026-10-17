#pragma once
#include "hardware/structs/resets.h"
inline void reset_block(uint32_t mask){resets_hw->reset|=mask;resets_hw->reset_done&=~mask;}
inline void unreset_block_wait(uint32_t mask){resets_hw->reset&=~mask;resets_hw->reset_done|=mask;}
