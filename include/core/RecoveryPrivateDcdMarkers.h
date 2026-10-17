#pragma once
#include <stdint.h>
/* Diagnostic-only fixed ABI shared with the pinned C translation unit. */
#ifdef __cplusplus
extern "C" {
#endif
// The original S0 read occurs before this first one-argument callback.
void GlyphDcdPrivateStatus(uint32_t s0);
// Both arguments are actual handler locals. The callback samples core0 gates
// after S1, then publishes; it neither rereads INTS nor services its value.
void GlyphDcdPrivateReturn(uint32_t s0,uint32_t s1);
#ifdef __cplusplus
}
#endif
