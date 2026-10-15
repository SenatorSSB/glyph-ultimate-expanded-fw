/* Diagnostic candidate only: no flash logging, FIFO calls, or IRQ changes. */
#ifndef GLYPH_PROFILE_STORE_CREATE_PROBE_HPP
#define GLYPH_PROFILE_STORE_CREATE_PROBE_HPP
#include <cstdint>
#if defined(ARDUINO_ARCH_RP2040)
#include <hardware/watchdog.h>
#include <hardware/structs/watchdog.h>
#endif

namespace ProfileStoreCreateProbe {
enum class Stage : uint32_t {
    RequestDecoded = 1, RecordEntered, RecordWritten, RecordRead, RecordRenamed,
    DirectoryEncoded, DirectoryWriteEntered, DirectoryWritten, DirectoryRead,
    DirectoryVerified, DirectoryDestinationHandled, DirectoryRenamed,
    DirectoryPublished, ResponseEncodeEntered, ResponseEncoded, ResponseEnded,
    RecordWriteEntered, RecordVerified, RecordDestinationHandled,
    RecordOpenEntered, RecordOpenComplete, RecordDataWritten, RecordCloseComplete,
    DirectoryOpenEntered, DirectoryOpenComplete, DirectoryDataWritten,
    DirectoryCloseComplete, Failed
};
constexpr uint32_t kMagic = 0x43525042; // CRPB; scratch0/1 and4..7 remain owned elsewhere
inline bool active = false;
inline uint32_t recovered_stage = 0;
inline uint32_t last_stage = 0;
inline bool Recovery() { return recovered_stage != 0; }

inline void Mark(Stage stage) {
    if (!active) return;
    last_stage = static_cast<uint32_t>(stage);
#if defined(ARDUINO_ARCH_RP2040)
    // One atomic stage store, then refresh the eight-second stage deadline.
    // The watchdog runs independently even with local IRQs/USB blocked.
    watchdog_hw->scratch[3] = last_stage;
    watchdog_update();
#endif
}
inline void Begin() {
    active = true;
    last_stage = static_cast<uint32_t>(Stage::RequestDecoded);
#if defined(ARDUINO_ARCH_RP2040)
    watchdog_hw->scratch[3] = last_stage;
    watchdog_hw->scratch[2] = kMagic;
    watchdog_enable(8000, true);
#endif
}
inline void Finish() {
    if (!active) return;
#if defined(ARDUINO_ARCH_RP2040)
    hw_clear_bits(&watchdog_hw->ctrl, WATCHDOG_CTRL_ENABLE_BITS);
    watchdog_hw->scratch[2] = 0;
#endif
    active = false;
}
// Called first in setup(), before Config loading, migration, or display work.
// After a timed-out CREATE, boot enters transport-only recovery. It must not
// mount or mutate the filesystem just to report the retained stage.
inline bool CaptureBoot() {
#if defined(ARDUINO_ARCH_RP2040)
    if (watchdog_caused_reboot() && watchdog_hw->scratch[2] == kMagic) {
        hw_clear_bits(&watchdog_hw->ctrl, WATCHDOG_CTRL_ENABLE_BITS);
        recovered_stage = watchdog_hw->scratch[3];
        if (recovered_stage == 0 || recovered_stage > static_cast<uint32_t>(Stage::Failed))
            recovered_stage = 0xffffffffu;
    }
#endif
    return Recovery();
}
}
#endif
