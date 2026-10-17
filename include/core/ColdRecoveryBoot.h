#pragma once
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if (defined(GLYPH_RT2_COLD_RECOVERY_CANDIDATE) && GLYPH_RT2_COLD_RECOVERY_CANDIDATE) || defined(GLYPH_COLD_RECOVERY_HOST)
/* Ephemeral boot control, not diagnostic telemetry or persistent Config. */
void GlyphColdRecoveryEarlyInit(uint8_t rhport);
bool GlyphColdRecoveryBoot(void);
bool GlyphColdRecoveryArm(void);
bool GlyphColdRecoveryPrepare(void);
bool GlyphColdRecoveryStart(void);
/* Existing external port interposer calls this BEFORE touching port state. */
bool GlyphColdRecoveryDeferPort(uint8_t rhport);
bool GlyphColdRecoveryUsbReady(void);
#else
static inline bool GlyphColdRecoveryBoot(void) { return false; }
static inline bool GlyphColdRecoveryArm(void) { return false; }
static inline bool GlyphColdRecoveryPrepare(void) { return false; }
static inline bool GlyphColdRecoveryStart(void) { return false; }
static inline bool GlyphColdRecoveryDeferPort(uint8_t rhport) { (void)rhport; return false; }
static inline bool GlyphColdRecoveryUsbReady(void) { return true; }
#endif

#ifdef __cplusplus
}
#endif
