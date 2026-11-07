#pragma once
#include <cstdint>

// Diagnostic only: scratch3 is outside SDK watchdog reboot scratch4..7 and
// source mode-routing scratch0..2. No filesystem, reset policy or authority.
namespace boot_diagnostics {
enum class Stage : uint8_t {
    Enter=1, DisplayReady, ValidatorReady, ConfigLoadBegin, ConfigLoadDone,
    StoreBegin, StoreReady, ReceiptBegin, ReceiptDone, MigrationBegin,
    MigrationDone, LayoutBegin, LayoutDone, BackendBegin, BackendDone, Normal
};
constexpr uint32_t kTag=0xB0030000u;
inline void Mark(volatile uint32_t &slot,Stage stage) {
    slot=kTag|uint32_t(stage);
}
inline void Recovery(volatile uint32_t &slot,bool ready) {
    // Preserve the last startup stage. Entered != transport ready.
    slot=kTag|(slot&0xffu)|(ready?0x200u:0x100u);
}
inline uint8_t StageCode(uint32_t slot){return slot&0xffu;}
inline bool RecoveryReady(uint32_t slot){return (slot&0x300u)==0x200u;}
}
