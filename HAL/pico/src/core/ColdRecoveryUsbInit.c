/* Deliberately exclude Adafruit's weak API declaration from this definition. */
#include "core/ColdRecoveryBoot.h"
#if defined(GLYPH_RT2_COLD_RECOVERY_CANDIDATE) && GLYPH_RT2_COLD_RECOVERY_CANDIDATE
void TinyUSB_Device_Init(uint8_t rhport) {
    GlyphColdRecoveryEarlyInit(rhport);
}
#endif
