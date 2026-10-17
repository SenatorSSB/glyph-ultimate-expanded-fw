# Manual RT2 USB startup diagnosis and diagnostic candidate

Disposition: `MULTI_PROFILE_STORE_RT2_TRANSPORT_DIAGNOSTIC_READY`, conditional
on the accompanying fresh review and exact committed build/custody receipt.
This is a candidate for physical localization, not a proven transport repair.
Direct owner authority is the 2026-10-16 RT2 request. Frozen parent is
`2e0a608622e8363ec7e2ef2aacc224e0810020ed`, tree
`00c321bc0ce4de4e9c67a913c0c0f0be23375c69`; canonical/base remains
`6b73a7c507f35c111745c6bdd341618b490cbdcd`. Branch:
`codex/profile-store-rt2-transport`. Active firmware behavior classification;
no canonical merge, controller operation or hardware PASS in this source task.

## Physical boundary

The owner reports exact2e0 root-reconciliation PASS: generation165→healthy166,
actual ID22 revision132 retained, useful IDs1/3/4 unchanged. GC V/W subsequently
triggered and reconciled safely, with healthy generation166 afterward. These
are user-reported physical facts, not new observations by this agent.
Selection is `NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE`, not FAIL.

Two manual RT2 stimuli produced an alternate black-screen boot and no serial
endpoint. Classification: `MANUAL_RT2_RECOVERY_TRANSPORT_UNAVAILABLE`. No
GET_DEVICE_INFO/PULSE/STATUS/LIST/READ/HEALTH could be sent. The operator stopped;
no cleanup followed. A source-defined headless recovery service requires that
transport, so the row remains blocking. Route entry, initialization completion,
CDC construction and enumeration stage remain **inferences or unknowns**.
Black screen alone is expected for a completed headless route and proves none
of those stages. Nunchuk remains NOT_TESTED.

## Exact pinned mechanism

Authority is the installed package selected by `platformio.ini`, not current
upstream: Arduino-Pico3.6.3, package `1.30603.0` (+sha32e74d0 package identity),
USE_TINYUSB, bundled Adafruit TinyUSB2.3.0 and TinyUSB0.16.0. Selected config is
`HAL/pico/include/tusb_config_pico.h`: device enabled, Pico OSAL, one each of
CDC/MSC/HID/MIDI, no vendor class; CDC RX/TX256 each, MSC512, HID64, MIDI128 each.
The config misspells `CFG_TUD_ENDOINT0_SIZE`; TinyUSB's default correctly spelled
`CFG_TUD_ENDPOINT0_SIZE` is64. Actual compile DB and source hashes are preserved
with the handoff; these values are not inferred from another release.

Pinned source paths below are relative to the framework package
`~/.platformio/packages/framework-arduinopico/` (USB prefix means
`libraries/Adafruit_TinyUSB_Arduino/src/`):

- `cores/rp2040/main.cpp:105` invokes `TinyUSB_Device_Init(0)` before launching
  core1 and before setup. Its weak API implementation invokes
  `TinyUSBDevice.begin(0)`.
- USB `arduino/Adafruit_USBD_Device.cpp:286` clears configuration, assigns the
  miscellaneous/IAD device class, invokes **SerialTinyUSB.begin(115200)** at297,
  then `TinyUSB_Port_InitDevice` at300. Serial is that same global instance.
- USB `arduino/Adafruit_USBD_CDC.cpp:68` returns immediately when already valid;
  otherwise it claims the single CDC instance and adds its descriptor. Thus
  RT2's later Serial.begin is idempotent: CDC is already present before attach.
- `addInterface` edits the live configuration buffer. Descriptor callbacks at
  Device.cpp:376 return that buffer; there is no separate immutable descriptor
  snapshot. Once a host has consumed a configuration, edits alone do not prove
  that host will refetch it. No late interface edit occurs on pure RT2 startup.
- USB `arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp:98` initializes the shared
  USB mutex, calls tud_init, and installs the USB-triggered software IRQ task.
  `portable/raspberrypi/rp2040/dcd_rp2040.c` dcd_init connects the pull-up.
  `device/usbd.c` parses SET_CONFIGURATION and opens CDC endpoints. This IRQ
  service is independent of application core1/display/menu initialization.
- Device.cpp:100 setID changes live VID/PID bytes; it does not detach/attach.
  Both direct normal Configurator and RT2 construct Configurator after core
  attach, setting2e8a:1092 in the same constructor. Host caching of an earlier
  device descriptor remains a physical timing question, not a proven cause.
- Core `__loop` calls yield after every app loop, including an early-returning
  recovery loop. delay.cpp yield tasks USB and flushes CDC; delay uses sleep_ms
  and does not itself yield. Existing CoordinatedCdcStream explicitly tasks
  outside its guard; accepted RX/TX code and deadlines remain unchanged.

## Side-by-side complete startup timeline

| Boundary | Normal boot then menu/Configurator | RT2 without MB1 |
| --- | --- | --- |
| Before main | Global Persistence configures LittleFS with autoformat false and mounts; this precedes USB in both routes. | Same global mount; a stall here cannot be observed by the new route marker. |
| Core bootstrap | Device.begin → auto CDC registration → tud_init/attach → USB IRQ service → core1 launch → setup. | Identical. No dependency on a gameplay backend or core1 display initialization. |
| Initial setup | Resource initialization, capture previous marker, matrix input read. | Same, then RT2&&!MB1 branches immediately. MB1 wins when both held. |
| Storage | Display/I2C/splash attempt; defaults and validator; checked Config load; normal store Begin/migration/root-marker policy as applicable. | Clear existing selectors0..2; install validator, IsAvailable, checked Config load and BeginRecovery of available store. No normal Begin/migration/Config publication. |
| Backend choice | initialize_backends validates selections, consumes committed destination or watchdog override; may instantiate default USB backend before console detection. Detection provides500ms timing opportunity; actual path depends on Config/selector. | No selector evaluation, default backend, console detection, secondary backends or gameplay activation. |
| Prior USB edits | XInput if selected: Serial.end clears configuration/CDC instance, gamepad registration, Serial.begin re-adds CDC, ID change. Direct Configurator need not take this path. Menu destination uses existing watchdog/scratch route. | No Serial.end, no prior gamepad class registration. Initial auto CDC retained. |
| Configurator | init_primary_backend calls Serial.begin then new ConfiguratorBackend → setID. | After inspection, same Serial.begin/new constructor/setID; install read-only state before publication. |
| Publication/loop | Publish Normal; ordinary loop dispatch plus core __loop yield; core1 normal display/RGB. | Publish RecoveryConfigurator/display false; SendReport only; core __loop still yields; core1 remains headless. |

Normal working transport is a physical owner fact. The different storage work,
prior USB backend edits and timing are real source differences; none is proven
to explain the observed RT2 failure. No gameplay/display initializer was added.

## Hypothesis adjudication

| Hypothesis | Result from exact pin / remaining boundary |
| --- | --- |
| A late CDC/frozen descriptors | Rejected for this route: core auto-registers CDC before tud_init. Frozen2e0 positive control confirms that path under modeled host timings. |
| B detach/attach required after late CDC | No late CDC addition on RT2; no source basis to add a detach/attach repair. Host refetch after arbitrary later edits is outside the demonstrated route. |
| C move transport before inspection | Already registered before inspection at core bootstrap. An inspection stall remains possible, but moving the idempotent call is not a demonstrated fix. |
| D late VID/PID | Both direct Configurator routes set live ID after attach. Timing/cache difference remains unproven; host model is not macOS caching. |
| E insufficient task service | Core IRQ and __loop yield exist; actual recovery/backend succeeds in host task model. Target IRQ starvation or a pre-loop stall is unknown. |
| F framework service skipped by RT2 | No required core startup tail is skipped: setup return continues core loop; USB precedes setup/core1. Target execution not established. |
| G different held-input route | Source RT2&&!MB1 and MB1 priority tested; actual input classification remains inference. No route-entry marker on original2e0. |
| H inspection hangs | Unknown physically. New phases2/3 bracket all recovery inspection. Global mount before setup is separately outside that bracket. |
| I new/heap failure | Unknown physically. Phases6/7 bracket constructor/new; exact build and heap accounting are separate from target live allocation proof. |
| J CDC instance exhausted | Sole core auto CDC is valid; later begin returns. No competing RT2 registration; host checks instance count1. Target corruption remains unknown. |
| K host/macOS race | Unknown and not faithfully represented by a DCD/event host model; requires narrow physical evidence. |

## Non-USB observations

Only strict-hardening candidates on RP2040 enable the implementation.
`RecoveryStartupDiagnostics` owns scratch3, magic0x5254 in its high16bits,
phase in bits8–15, observation flags in low8bits. Setup reads valid prior markers
and clears scratch3; foreign magic and phase0/>13 are rejected. Existing
selectors0/1 and committed magic in2 are unchanged. SDK watchdog/ROM4..7 are
untouched. Prior marker is optional warm/watchdog/software/SWD evidence:
**RUN reset/power loss may erase scratch; do not expect retention there.**

Route entry writes a minimal scratch marker before any PIO claim or USB query.
An established Mk6 LED GPIO11 emits four pixels (MB1 pair, LF4 pair). A free PIO
SM/program is claimed without panic, DMA, IRQ handler, heap allocation or array
buffer. If neither PIO has resources, or FIFO is busy, the LED update is skipped;
scratch remains available but standalone physical localization then may fail.
The four-instruction program and8MHz timing match the pinned FastLED program.
The SM is disabled while four FIFO words are preloaded (USB IRQs enabled), then
runs the120us frame plus80us latch. This bounded200us interval is diagnostic
perturbation, **not a USB timing repair**. GPIO/PIO are never claimed by normal
boot or MB1 diagnostics. Existing MB1 FastLED behavior is untouched.

MB1 RGB encodes phase bits0(red)/1(green)/2(blue); LF4 red encodes bit3,
green means configured, blue means connected. Brightness is24/255. The first
pair's colors are red1, green2, yellow3, blue4, magenta5, cyan6, white7, off8,
red9, green10, yellow11, blue12, magenta13. LF4 red is on for phases8–13;
configuration/connection flags can make it yellow/magenta/white. Observe only
these first two button pairs; other pixels are not a diagnostic signal.

| Phase | Last completed observation / next suspect if stationary |
| --- | --- |
| 1 | Route entered; indicator/flag observation itself may follow. |
| 2 | Entering initialize_recovery; inspection may not return. |
| 3 | Inspection returned. |
| 4 / 5 | Entering / returned from the route's idempotent Serial.begin. |
| 6 / 7 | Entering / returned from new ConfiguratorBackend. |
| 8 | Read-only state installed. |
| 9 | Recovery publication completed. |
| 10 / 11 | Loop entered / SendReport returned. |
| 12 | USB mounted/configured observed after loop. |
| 13 | First command byte seen, not proof of complete command or host response. |

Flags: init1, sole CDC instance2, live CDC descriptor4, pull-up8, connected16,
configured32, DTR64, indicator claimed128. Mounted is not macOS endpoint/DTR/open
proof. Additive response58/59/60 expose current/previous/version1 on candidates;
no PersistentConfig/Profile or disk-format change. Monotonic phase plus changing
flags remain stable in scratch; updates occur only when the observation changes.

## Test scope and readiness

`check_glyph_profile_store_selection_recovery.py` still proves extracted actual
setup selection/MB1 priority/validator/BeginRecovery/no gameplay. Its Serial and
backend stubs do **not** prove enumeration. This proof gap remains explicit.

`check_glyph_rt2_usb_startup.py` links real pinned descriptor/CDC C++, TinyUSB
USBD/control/event/Pico OSAL and CDC/HID/MSC/MIDI drivers, actual production
ConfiguratorBackend/ProfileStore and extracted recovery function/loop. Config
and storage physical I/O, DCD bus/IRQ timing, GPIO/PIO and host are explicit
models. ASan/UBSan run frozen2e0 and current source at five exact recovery
boundaries plus before core auto-CDC (not attached then; pending host request
is delivered after attach). Each exercises endpoint activation, task progress,
PULSE/STATUS/LIST/full READ1/3/4/HEALTH/deviceinfo, every new mutation and whole
Config SET refusal, and unchanged files/generation/save count. Normal direct
Configurator bootstrap and inactive diagnostic PIO, unavailable program/SM,
pio1 fallback, busy FIFO and scratch namespace are checked. Deliberately removed
auto-CDC is detected by the negative oracle; frozen2e0 itself passes and is a
**positive falsification control**, not a fabricated negative reproduction.

Host adaptations: Device language-ID pointer cast uses uintptr_t on64-bit host
before unchanged uint16 conversion; observation hooks bracket auto-CDC and
inspection/Serial calls; absent optional weak callbacks have explicit null/no-op
models for Mach-O. The host supplies no XInput app driver/BOS/vendor override,
whereas the target links those optional callbacks; source audit finds its
init/reset no-op and open rejects CDC. This is not full linked production
callback closure and does not test XInput composite enumeration. Installed
dependencies are never edited. No actual RP2040
DCD register execution, electrical timing, allocation under physical load,
macOS serial-node creation or controller acceptance is claimed.

Focused prior recovery, strict protocol, root reconcile, Config persistence,
CDC TX/RX, RX framing and liveness regressions plus exact target resources are
retained with the handoff. B1/B2/B4/B5/B6/B8 persistence mechanisms are unchanged;
B3 source priority/selection preserved; B7 remains physically blocked by RT2
transport. An aggregate B1–B8 unaffected/hardware PASS would be false.

The diagnostic candidate must pass the [new narrow hardware packet](profile_store_rt2_usb_hardware_packet.md)
after [installed2e0 adjudication](profile_store_rt2_usb_device_adjudication.md).
Do not repeat GC/fault matrices, cleanup, selection fixture construction or
power-loss scenarios. Exact candidate identity, resources, review and immutable
UF2 locator are in the final owner-held handoff receipt accompanying this file.
