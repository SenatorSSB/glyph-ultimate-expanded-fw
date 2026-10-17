#pragma once
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif
/* One deterministic explicit-manual-RT2 warm reset, after the read-only backend
 * and existing CDC Configurator identity are established. Core0/thread only.
 * Preserves initialized IRQ/OSAL allocations; never retries. A false return
 * before reset leaves USB unchanged; after reset starts it remains detached
 * with USB IRQs disabled. This is not an upstream deinit API or cold init.
 */
bool GlyphRecoveryUsbReinitialize(void);
/* Private generated-TU seams: call only while USB users/IRQs are quiesced. */
bool GlyphRecoveryUsbdPreflight(void);
bool GlyphRecoveryUsbdReset(void);
void GlyphRecoveryDcdReset(void);
#ifdef __cplusplus
}
#endif
