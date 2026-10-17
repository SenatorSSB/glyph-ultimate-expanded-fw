#pragma once
#include <cstdint>

// Volatile acceptance-candidate observations. No selector/config/store writes.
namespace RecoveryStartupDiagnostics {
enum class Phase : uint8_t {
    RouteEntry=1, InspectionEntered, InspectionReturned,
    SerialBeginEntered, SerialBeginReturned, BackendNewEntered,
    BackendNewReturned, ReadOnlyInstalled, Published, LoopEntered,
    ReportReturned, UsbConfigured, RequestByteSeen
};
constexpr uint32_t kMagic = 0x52540000u;
constexpr uint32_t kMagicMask = 0xffff0000u;
inline bool Valid(uint32_t value) {
    const unsigned phase=(value>>8)&255u;
    return (value&kMagicMask)==kMagic&&phase>=1&&phase<=13;
}
// Only scratch3 is owned here. Selectors0..2 and SDK4..7 are never touched.
inline uint32_t TakePrevious(volatile uint32_t *scratch) {
    const uint32_t value=scratch[3];scratch[3]=0;return Valid(value)?value:0;
}
// Flags: initialized1, CDC instance2, CDC descriptor4, pull-up8,
// bus-connected16, configured32, CDC DTR64, indicator available128.
#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RECOVERY_DIAGNOSTICS_HOST))
void CapturePrevious();
void Mark(Phase phase);
void ValidInspectionCommandReceived();
uint32_t Current();
uint32_t Previous();
#else
inline void CapturePrevious(){}
inline void Mark(Phase){}
inline void ValidInspectionCommandReceived(){}
inline uint32_t Current(){return 0;}
inline uint32_t Previous(){return 0;}
#endif
}
