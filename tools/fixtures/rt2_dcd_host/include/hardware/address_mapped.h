#pragma once
#include <stdint.h>
typedef volatile uint32_t io_rw_32;
// Hardware read-only registers are writable by the explicit host MMIO model.
typedef volatile uint32_t io_ro_32;
typedef volatile uint32_t io_wo_32;
#define _REG_(x)
