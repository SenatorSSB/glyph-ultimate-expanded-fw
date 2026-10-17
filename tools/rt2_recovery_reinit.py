"""Exact pinned recovery warm-reset helpers; installed packages are read only.

Normal source bytes (including existing S0/S1 DCD insertions) are unchanged.
Only helpers are inserted before each TU's final build guard. No public deinit
API is invented. This builder replaces the earlier private-DCD builder.
"""
from hashlib import sha256
from pathlib import Path
import json
import rt2_private_dcd

PINS = {'dcd': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c',
         'pristine': 'vendor/recovery/arduino-pico-3.6.3/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c',
         'sha256': '92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12'},
 'usbd': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/device/usbd.c',
          'pristine': 'vendor/recovery/arduino-pico-3.6.3/libraries/Adafruit_TinyUSB_Arduino/src/device/usbd.c',
          'sha256': 'c39f68050719aaa803b193206baf117cfe6e763e47065ed1ffbab745ada173a4'},
 'port': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',
          'pristine': 'vendor/recovery/arduino-pico-3.6.3/libraries/Adafruit_TinyUSB_Arduino/src/arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',
          'sha256': 'ac9a2397254aafc498ad1d1eb59d0a8291c6943f9261369b8c49b09c19691c3a'}}
GENERATED_RELATIVE = ".pio/rt2-recovery-reinit"
PORT_HELPER = r'''#include "core/RecoveryUsbReinitialization.h"
#include "hardware/sync.h"
#include "pico/platform.h"
#include "device/dcd.h"

static bool glyph_recovery_usb_consumed = false;

static uint32_t glyph_recovery_primask(void) {
  uint32_t value;
  __asm volatile ("mrs %0, primask" : "=r" (value));
  return value;
}

static bool glyph_recovery_cdc_descriptor(void) {
  uint8_t const *device = tud_descriptor_device_cb();
  uint8_t const *cfg = tud_descriptor_configuration_cb(0);
  if (!device || !cfg || device[0] != 18 || device[1] != TUSB_DESC_DEVICE ||
      device[4] != TUSB_CLASS_MISC || device[5] != MISC_SUBCLASS_COMMON ||
      device[6] != MISC_PROTOCOL_IAD || device[7] != 64 ||
      device[8] != 0x8a || device[9] != 0x2e ||
      device[10] != 0x92 || device[11] != 0x10 || device[17] != 1 ||
      cfg[0] != 9 || cfg[1] != TUSB_DESC_CONFIGURATION ||
      cfg[2] != 75 || cfg[3] != 0 || cfg[4] != 2 || cfg[5] != 1) return false;
  uint8_t const expected[] = {TUD_CDC_DESCRIPTOR(0, 0, 0x81, 8, 0x01, 0x82, 64)};
  static_assert(sizeof(expected) == 66, "pinned CDC descriptor size");
  for (unsigned i = 0; i < sizeof(expected); ++i) {
    // Adafruit addInterface assigns string4 to the first interface only.
    uint8_t const value = (i == 16) ? 4 : expected[i];
    if (cfg[9 + i] != value) return false;
  }
  return true;
}

extern "C" bool GlyphRecoveryUsbReinitialize(void) {
  // Preflight is read-only. The existing port's exclusive task callback also
  // proves its static IRQ number was assigned by the original initialization.
  if (get_core_num() != 0 || __get_current_exception() != 0 ||
      glyph_recovery_primask() != 0 || glyph_recovery_usb_consumed || !tud_inited() ||
      !irq_is_enabled(USBCTRL_IRQ) || !irq_is_enabled(USB_TASK_IRQ) ||
      irq_get_exclusive_handler(USB_TASK_IRQ) != usb_task_irq ||
      !irq_has_shared_handler(USBCTRL_IRQ) ||
      !glyph_recovery_cdc_descriptor() || !GlyphRecoveryUsbdPreflight()) return false;
  uint32_t const saved = save_and_disable_interrupts();
  if (!mutex_try_enter(&__usb_mutex, NULL)) {
    restore_interrupts(saved);
    return false;
  }
  if (!GlyphRecoveryUsbdPreflight()) {
    mutex_exit(&__usb_mutex);
    restore_interrupts(saved);
    return false;
  }
  glyph_recovery_usb_consumed = true;
  irq_set_enabled(USBCTRL_IRQ, false);
  irq_set_enabled(USB_TASK_IRQ, false);
  dcd_disconnect(0);
  irq_clear(USBCTRL_IRQ);
  irq_clear(USB_TASK_IRQ);
  GlyphRecoveryDcdReset();
  bool const reset_ok = GlyphRecoveryUsbdReset();
  irq_clear(USBCTRL_IRQ);
  irq_clear(USB_TASK_IRQ);
  if (!reset_ok) {
    mutex_exit(&__usb_mutex);
    restore_interrupts(saved);
    return false;
  }
  irq_set_enabled(USB_TASK_IRQ, true);
  irq_set_enabled(USBCTRL_IRQ, true);
  dcd_connect(0);
  mutex_exit(&__usb_mutex);
  restore_interrupts(saved);
  return true;
}
'''
USBD_HELPER = r'''#include "core/RecoveryUsbReinitialization.h"

bool GlyphRecoveryUsbdPreflight(void) {
  if (_usbd_rhport != 0 || _usbd_q != &_usbd_qdef ||
      !_usbd_qdef.critsec.spin_lock || !_usbd_mutex ||
      !_usbd_mutex->core.spin_lock || _usbd_mutex->owner != LOCK_INVALID_OWNER_ID ||
      BUILTIN_DRIVER_COUNT != 4 || _app_driver_count != 1 || !_app_driver ||
      TOTAL_DRIVER_COUNT != 5 || !_app_driver[0].init || !_app_driver[0].reset ||
      _usbd_driver[0].init != cdcd_init || _usbd_driver[0].reset != cdcd_reset ||
      _usbd_driver[1].init != mscd_init || _usbd_driver[1].reset != mscd_reset ||
      _usbd_driver[2].init != hidd_init || _usbd_driver[2].reset != hidd_reset ||
      _usbd_driver[3].init != midid_init || _usbd_driver[3].reset != midid_reset)
    return false;
  return true;
}

bool GlyphRecoveryUsbdReset(void) {
  if (!GlyphRecoveryUsbdPreflight()) return false;
  // Existing reset semantics retain CDC coding and initialized FIFO/lock
  // storage. Queue ownership is retained; never recreate its critical section.
  usbd_reset(0);
  return tu_fifo_clear(&_usbd_qdef.ff);
}
'''


def _insert(base, helper):
    # Preserve original newline convention and every original byte.
    nl = b"\r\n" if b"\r\n" in base else b"\n"
    anchor = b"#endif" + nl
    pos = base.rfind(anchor)
    if pos < 0 or base[pos + len(anchor):].strip():
        raise ValueError("final TU guard anchor changed")
    addition = nl + helper.replace("\r\n", "\n").replace("\n", nl.decode()).encode() + nl
    return base[:pos] + addition + base[pos:]


def _dcd_helper(pristine):
    # Derive from the exact original init body: two deliberate removals and
    # explicit SOF software reset. Preserve all reset/endpoint/register order.
    text = pristine.decode()
    start = text.index("void dcd_init (uint8_t rhport)")
    end = text.index("\r\nvoid dcd_int_enable", start)
    body = text[start:end]
    remove = ["  irq_add_shared_handler(USBCTRL_IRQ, dcd_rp2040_irq, PICO_SHARED_IRQ_HANDLER_HIGHEST_ORDER_PRIORITY);\r\n",
              "  dcd_connect(rhport);\r\n"]
    for line in remove:
        if body.count(line) != 1:
            raise ValueError("pinned DCD initialization seam changed")
        body = body.replace(line, "", 1)
    body = body.replace("void dcd_init (uint8_t rhport)", "void GlyphRecoveryDcdReset(void)", 1)
    body = body.replace("  assert(rhport == 0);", "  _sof_enable = false;", 1)
    return '#include "core/RecoveryUsbReinitialization.h"\n' + body


def verify_pin(data, key, label):
    if sha256(data).hexdigest() != PINS[key]["sha256"]:
        raise ValueError(label + ": exact installed/pristine pin mismatch")


def prepare(root, framework):
    root, framework = Path(root), Path(framework)
    records = {}
    for key, pin in PINS.items():
        pristine = (root / pin["pristine"]).read_bytes()
        verify_pin(pristine, key, "repository " + key)
        verify_pin((framework / pin["installed"]).read_bytes(), key, "installed " + key)
        base = rt2_private_dcd.patch_source(pristine) if key == "dcd" else pristine
        helper = _dcd_helper(pristine) if key == "dcd" else USBD_HELPER if key == "usbd" else PORT_HELPER
        patched = _insert(base, helper)
        generated = root / GENERATED_RELATIVE / Path(pin["installed"]).name
        generated.parent.mkdir(parents=True, exist_ok=True)
        if not generated.exists() or generated.read_bytes() != patched:
            generated.write_bytes(patched)
        records[key] = dict(pin, generated=str(generated),
                            generated_sha256=sha256(patched).hexdigest(),
                            base_sha256=sha256(base).hexdigest(), bytes=len(patched))
    (root / GENERATED_RELATIVE / "generation.json").write_text(json.dumps(records, indent=2) + "\n")
    return records


def validate_routing(records, counts, linked):
    for key in PINS:
        if counts.get(key) != 1 or set(linked.get(key, ())) != {str(Path(records[key]["object"]).resolve())}:
            raise ValueError("requires exactly one replacement and no original object for " + key)
