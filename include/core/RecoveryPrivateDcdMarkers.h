#pragma once
#include <stdint.h>
/* Diagnostic-only, numeric ABI shared with the pinned C translation unit. */
enum GlyphDcdPrivateMarkerId {
    GLYPH_DCD_PRIVATE_ENTRY=0, /* obsolete: bit0 is merged post-status entry fact */
    GLYPH_DCD_PRIVATE_STATUS=1,
    GLYPH_DCD_PRIVATE_SOF_DONE=2, GLYPH_DCD_PRIVATE_BUFF_DONE=3,
    GLYPH_DCD_PRIVATE_SETUP_TEST=4, GLYPH_DCD_PRIVATE_SETUP_ENTERED=5,
    GLYPH_DCD_PRIVATE_SETUP_POINTER_ACQUIRED=6, GLYPH_DCD_PRIVATE_PID_DONE=7,
    GLYPH_DCD_PRIVATE_BEFORE_EVENT=8, GLYPH_DCD_PRIVATE_AFTER_EVENT=9,
    GLYPH_DCD_PRIVATE_BEFORE_CLEAR=10, GLYPH_DCD_PRIVATE_AFTER_CLEAR=11,
    GLYPH_DCD_PRIVATE_RETURN=12
};
#ifdef __cplusplus
extern "C" {
#endif
// One-argument first publication keeps the actual sampled word in the ABI
// argument register without a pre-read diagnostic marker-ID setup.
void GlyphDcdPrivateStatus(uint32_t value);
void GlyphDcdPrivateMarker(uint32_t marker,uint32_t value);
#ifdef __cplusplus
}
#endif
