#include "core/ColdRecoveryBoot.h"
#if defined(GLYPH_RT2_COLD_RECOVERY_CANDIDATE) && GLYPH_RT2_COLD_RECOVERY_CANDIDATE
#include "core/ColdRecoveryIntent.hpp"
#include <Adafruit_TinyUSB.h>
#include <atomic>
#include "hardware/watchdog.h"
#include "pico/platform.h"

namespace {
enum Phase : uint32_t { Ordinary, Deferred, Preparing, Prepared, Starting, Started, Failed };
std::atomic<uint32_t> cold_boot{0}, phase{Ordinary};
uint8_t saved_port = 0;
bool arm_attempted = false, deferred_port = false, forwarded_port = false;
// ARMv6-M lacks atomic RMW, so the general is_always_lock_free trait is false.
// These gates use only aligned word loads/stores; final assembly must prove
// inline operations/barriers with no runtime atomic helper.
static_assert(sizeof(std::atomic<uint32_t>) == 4 && alignof(std::atomic<uint32_t>) >= 4,
    "boot gates require aligned words");

bool context() { return get_core_num() == 0 && __get_current_exception() == 0; }
bool fail() { phase.store(Failed, std::memory_order_release); return false; }

// Pin-derived original begin/addInterface output; preparation cannot merely
// trust begin's unconditional true result. No TinyUSB FIFO/lock is used here.
bool cdc_descriptor(bool final_identity) {
    const uint8_t *device = tud_descriptor_device_cb();
    const uint8_t *cfg = tud_descriptor_configuration_cb(0);
    if (!device || !cfg || device[0] != 18 || device[1] != TUSB_DESC_DEVICE ||
        device[4] != TUSB_CLASS_MISC || device[5] != MISC_SUBCLASS_COMMON ||
        device[6] != MISC_PROTOCOL_IAD || device[7] != 64 || device[17] != 1 ||
        cfg[0] != 9 || cfg[1] != TUSB_DESC_CONFIGURATION || cfg[2] != 75 ||
        cfg[3] != 0 || cfg[4] != 2 || cfg[5] != 1) return false;
    if (final_identity && (device[8] != 0x8a || device[9] != 0x2e ||
        device[10] != 0x92 || device[11] != 0x10)) return false;
    const uint8_t expected[] = {TUD_CDC_DESCRIPTOR(0, 0, 0x81, 8, 0x01, 0x82, 64)};
    static_assert(sizeof(expected) == 66, "pinned CDC descriptor size");
    for (unsigned i = 0; i < sizeof(expected); ++i)
        if (cfg[9 + i] != ((i == 16) ? 4 : expected[i])) return false;
    return true;
}
}

extern "C" bool GlyphColdRecoveryBoot(void) {
    return cold_boot.load(std::memory_order_relaxed) != 0;
}

extern "C" void GlyphColdRecoveryEarlyInit(uint8_t rhport) {
    if (GlyphColdRecoveryBoot()) { fail(); return; }
    if (ColdRecoveryIntent::Consume(watchdog_hw->scratch, watchdog_hw->reason)) {
        saved_port = rhport;
        phase.store(Deferred, std::memory_order_relaxed);
        cold_boot.store(1, std::memory_order_release);
        if (rhport != 0 || !context() || tud_inited()) fail();
        return;
    }
    // Same pinned ordinary API body at the original Arduino main call point.
    TinyUSBDevice.begin(rhport);
}

extern "C" bool GlyphColdRecoveryArm(void) {
    if (!context() || GlyphColdRecoveryBoot() || arm_attempted) return false;
    arm_attempted = true;
    return ColdRecoveryIntent::Arm(watchdog_hw->scratch);
}

extern "C" bool GlyphColdRecoveryDeferPort(uint8_t rhport) {
    if (!GlyphColdRecoveryBoot()) return false;
    if (!context() || rhport != saved_port) { fail(); return true; }
    const uint32_t state = phase.load(std::memory_order_relaxed);
    if (state == Preparing && !deferred_port) {
        deferred_port = true;
        return true; // Descriptor-only begin; no port/stack/hardware init.
    }
    if (state == Starting && !forwarded_port) {
        forwarded_port = true;
        return false; // Permit the original hardware initialization once.
    }
    fail();
    return true;
}

extern "C" bool GlyphColdRecoveryPrepare(void) {
    if (!GlyphColdRecoveryBoot() || !context() ||
        phase.load(std::memory_order_relaxed) != Deferred || tud_inited() ||
        Adafruit_USBD_CDC::getInstanceCount() != 0) return fail();
    phase.store(Preparing, std::memory_order_relaxed);
    const bool prepared = TinyUSBDevice.begin(saved_port);
    if (!prepared || !deferred_port || phase.load(std::memory_order_relaxed) != Preparing ||
        tud_inited() || Adafruit_USBD_CDC::getInstanceCount() != 1 ||
        !cdc_descriptor(false)) return fail();
    phase.store(Prepared, std::memory_order_release);
    return true;
}

extern "C" bool GlyphColdRecoveryStart(void) {
    if (!GlyphColdRecoveryBoot() || !context() ||
        phase.load(std::memory_order_relaxed) != Prepared || tud_inited() ||
        Adafruit_USBD_CDC::getInstanceCount() != 1 || !cdc_descriptor(true)) return fail();
    phase.store(Starting, std::memory_order_relaxed);
    TinyUSB_Port_InitDevice(saved_port);
    if (!forwarded_port || phase.load(std::memory_order_relaxed) != Starting ||
        !tud_inited() || !cdc_descriptor(true)) return fail();
    phase.store(Started, std::memory_order_release);
    return true;
}

extern "C" bool GlyphColdRecoveryUsbReady(void) {
    // Ordinary yield forwards without a new barrier. Cold Started publishes
    // the initialized mutex/queue/class state to any caller on either core.
    if (!GlyphColdRecoveryBoot()) return true;
    return phase.load(std::memory_order_acquire) == Started;
}
extern "C" void __real_TinyUSB_Device_Task(void);
extern "C" void __wrap_TinyUSB_Device_Task(void) {
    if (GlyphColdRecoveryUsbReady()) __real_TinyUSB_Device_Task();
}
extern "C" void __real_TinyUSB_Device_FlushCDC(void);
extern "C" void __wrap_TinyUSB_Device_FlushCDC(void) {
    if (GlyphColdRecoveryUsbReady()) __real_TinyUSB_Device_FlushCDC();
}
#endif
