# Candidate-only RT2 DCD observer

Disposition: MULTI_PROFILE_STORE_RT2_DCD_DIAGNOSTIC_READY, contingent on final
clean committed build, custody and fresh review receipt. This is a diagnostic
candidate, not a proven enumeration repair. Direct owner request of2026-10-17
is authority for this bounded experiment. Active firmware behavior changes;
no device access or canonical merge. Branch codex/profile-store-rt2-dcd-diagnostics
is a direct child of466f91ed867884640375627734d3473e9fb22c32 (tree
6aab0abcfd8a8c6bddd21d96e31432cbbfd31ba7). Canonical/base remains
6b73a7c507f35c111745c6bdd341618b490cbdcd. Final identity belongs to the
external exact-artifact handoff receipt; no self-referential commit hash here.

## Physical adjudication

Owner reports466 normal Configurator PASS. Its manual RT2 completed application
phase11 (inspection, Serial, backend, read-only installation, publication,
loop entry and first SendReport return), with continued recovery-loop sampling,
black display, no host USB device or serial endpoint. Keep this established
application boundary. Precision:466 MB1 phase11 yellow alone does not encode
tud_connected; that bit was LF4/scratch. Owner reports no observed connected or
mounted state; do not derive a false connected bit from MB1 alone.

5913e49f054eadd2554f94dd1d07908a6178e57e normal Configurator PASS, then one
RT2 attempt with no device/serial and coarse RED; no second attempt. Classification:
MULTI_PROFILE_STORE_5913_RT2_IDENTITY_AB_TRANSPORT_UNAVAILABLE. Its retained
bootstrap2e8a:000a was insufficient physically. Live mixed identity is a real
source mechanism, but demoted from primary physical-cause hypothesis. RED only
proves phase<11 at the last successful display; no exact block location.
The new constructor and application route retain ordinary466 setID2e8a:1092,
with no5913 retention policy. Root cause UNPROVEN; Nunchuk NOT_TESTED.

## Exact pinned source and startup map

Authority: installed framework-arduinopico package1.30603.0, Arduino-Pico3.6.3,
Adafruit TinyUSB2.3.0, TinyUSB0.16.0, SDK1.5.1. Below USB means
libraries/Adafruit_TinyUSB_Arduino/src/ within that package. Source hashes,
extracted-function hashes, actual compile DB and ELF bindings accompany custody.
Not current upstream. E5 enumeration and E15 uframe fixes are undefined/0 in
actual preprocessed DCD; PICO_RP2040_USB_FAST_IRQ=0. SDK E5 workaround exists
but is not active here; it can manipulate GPIO15/mux with alarm/busy-wait and
is not enabled by this candidate.

| Step | Pinned writer/advance | Register/state | Observation |
| --- | --- | --- | --- |
| Core bootstrap | cores/rp2040/main.cpp TinyUSB_Device_Init before core1/setup; Adafruit_USBD_Device::begin auto-registers Serial then port init | one CDC instance/config buffer | existing flags; no late-CDC assumption |
| USB reset/init | portable/raspberrypi/rp2040/rp2040_usb.c rp2040_usb_init: reset_block, unreset_block_wait, memset registers/DPRAM | USBCTRL reset_done; USB_MUXING TO_PHY+SOFTCON | read-only reset_done/main_ctrl snapshot |
| Endpoint setup | dcd_rp2040.c dcd_init/hw_endpoint_init/reset_non_control_endpoints | EP0 IN/OUT64; EP0_INT_1BUF; endpoint controls/DPRAM buffers | real source modeled; no production DPRAM read |
| IRQ install | dcd_init shared USBCTRL_IRQ5 handler highest priority; dcd_int_enable enables NVIC | INTE buffer/reset/setup/suspend/resume; NVIC ISER/ISPR | raw INTE/INTS/INTR, NVIC flags |
| Attach | dcd_connect SET alias SIE_CTRL PULLUP_EN; dcd_disconnect CLEAR alias | internal DP pull-up enable | raw SIE_CTRL and sticky ON sampled after repeated loop |
| Host reset | dcd_rp2040_irq reset branch resets addr/noncontrol and queues bus_reset event | SIE_STATUS BUS_RESET; dev_addr_ctrl=0 | existing optional tud_event_hook_cb records DCD receipt |
| SETUP | same IRQ copies eight setup bytes, queues event, clears SETUP_REC | DPRAM setup_packet, SIE_STATUS/INTS | event hook records receipt even if event queue cannot accept |
| Device descriptor | usbd.c task SETUP sets connected=1 then processes standard request; tud_control_xfer submits response | USBD connected, EP0 transfer | wrapper observes successful submission, not host ACK |
| SET_ADDRESS | usbd.c calls dcd_set_address; DCD queues EP0 IN ZLP | requested address only until status completes | requested sticky bit |
| Address applied | usbd_control.c invokes dcd_edpt0_status_complete; DCD writes dev_addr_ctrl | actual device address | post-real wrapper applied bit plus raw address |
| Config descriptor | usbd.c request returns configuration descriptor through control transfer | EP0 data | actual descriptor exercised in harness; not separate LED color |
| SET_CONFIGURATION | usbd.c processes descriptor, opens CDC endpoints and sets cfg_num; status callback | cfg_num!=0 means tud_mounted | post-status nonzero effective8-bit SET_CONFIG bit plus sticky sampled mounted |

USB Port InitDevice initializes __usb_mutex, tud_init, claims an unused software
IRQ dynamically (31 in the host model), installs exclusive usb_task_irq and
lower-priority USB shared trigger. Both software IRQ and foreground Device_Task
try the same mutex then tud_task. Captured software IRQ number is observed from
the actual port claim, not assumed31 on target. Bus reset alone leaves connected
false; SETUP task processing sets true. No external pin or cable measurement is
claimed by register PULLUP_EN. OFF at the next repeated-loop observation gives
orange; actual current hardware value on frozen466 is still UNKNOWN pending
owner observation. If yellow then later cleared, sticky yellow does not prove
continuous/current ON. Scratch low-byte/current SIE snapshot distinguishes that.

Potential pull-up clear writers: pinned dcd_disconnect (via tud_disconnect/
Adafruit detach), USBCTRL reset/init memset, explicit register writers. Recovery
route has no detach, reset, or clear path after bootstrap in the audited source.
No claim that hardware fault, electrical host recognition or IRQ receipt works
merely because a software bit is ON.

## Interference audit and5913 first SendReport

LittleFS read callback memcpy from XIP does not disable IRQs or write USB.
Flash prog/erase brackets noInterrupts, idleOtherCore, flash operation,
resumeOtherCore, interrupts. A hang within that bracket cannot explain466's
subsequent repeated phase11 sampling. Recovery inspection itself is read-only;
initial filesystem mount precedes USB initialization. No lasting USB IRQ disable,
USB reset or disconnect was found in recovery initialization/fault bookkeeping.
Root fault candidate machinery is unchanged and models storage state; no USB
register/IRQ writer. Core1 recovery waits on boot decision and returns to the
headless path; no USB teardown. These are source findings, not proof against all
physical interference.

CoordinatedCdcStream::available -> fillRx -> serviceRx calls Device_Task outside
the stream guard, then reads at most64 bytes under guard, releases, tasks again.
Pinned tud_cdc_n_read is FIFO receive, no host wait. Device_Task uses try-lock,
not blocking acquisition. Pico queue receive with timeout0 returns immediately
when empty. tud_task_ext drains until queue empty, however; a continuous stream
of events can prevent return. Therefore a task block is not source-proven
impossible in every environment. No VID/PID-dependent blocking path or
5913-specific deadlock was found.5913 RED is not proven SendReport blockage;
it may be stale/early indicator or an unrelated startup event. Do not overwrite
466 phase11. Wrapper task entry/return counters and IRQ-task flags provide
secondary evidence if an endpoint becomes available.

PIO uses GPIO11, a claimed unused SM and four instructions from pinned FastLED
clockless program, with per-SM clock divider at8MHz. It does not change system
clock/PLL, USB pins, USBCTRL or NVIC. Four FIFO words are preloaded while only
that SM is disabled, then enabled. IRQs remain enabled during the200us LED
protocol frame/latch interval. Earlier repeated frames could perturb foreground
scheduling even without masking USB IRQs; this candidate emits only successful
state changes (at most eight per boot), retries a skipped/busy frame and never
refreshes unchanged displayed state. PIO ends each bit low; after96 bits its next
OUT autopull stalls on empty FIFO while pin stays low. This provides the low
latch interval; the clockless pixel retains its last frame without refresh.
This conclusion follows the exact pinned LED protocol/program. The harness
verifies word colors/frame counts and idle no-refresh, not physical LED silicon.
No startup sleep or deliberate phase delay was added;200us is inherited frame
protocol cost, not a timing repair.

## Candidate observer and sticky MB1 contract

Only MB1 top-left menu pair is colored; LF4 words are zero. Colors encode
furthest sticky evidence, gated by two recovery-loop entries. At most eight
states, no regression across bus reset/unplug/replug within a boot.

| MB1 settled color | Evidence |
| --- | --- |
| RED | repeated recovery-loop entry not yet observed; no exact application phase claim |
| ORANGE | repeated loop, pull-up ON not yet sampled after repeat |
| YELLOW | repeated loop and pull-up ON sampled after repeat; no later DCD reset/SETUP/address/config/inspection milestone |
| MAGENTA | DCD bus reset received, no later milestone |
| BLUE | DCD SETUP received or device descriptor submitted; not yet addressed/configured |
| CYAN | SET_ADDRESS processed (requested or applied); not yet configured |
| GREEN | nonzero effective8-bit SET_CONFIGURATION status completed or mounted sampled |
| WHITE | whole supported version-valid recovery PULSE/STATUS/LIST/READ/HEALTH request decoded, regardless operation success; still require full service responses |

No LED or scratch value alone proves successful transport or complete service.
No LEDs is UNKNOWN (PIO unavailable/pre-setup stall/indicator failure possible).
Sticky history can outlive current USB state. Report the settled color once,
USB tree and endpoint presence; no sequence/video requirement.

Repository-owned optional event callback and six GNU --wrap interpositions:
tud_control_xfer, dcd_set_address, dcd_edpt0_status_complete, tud_task_ext,
user_irq_claim_unused, C++ _Z23TinyUSB_Port_InitDeviceh. Real calls are exactly
once with original arguments/results; no allocation/LED/task/USB writes in
observer callbacks. Core0 task counters serialize under existing USB mutex;
IRQ flags only false->true, so no cross-context bitset RMW. Port capture occurs
before core1 launch. Snapshot fields are asynchronous observations, not an atomic
hardware transaction. A single entry/return counter difference can reflect IRQ
preemption between reads and alone cannot prove a blocked task. Compile and link gating requires strict Mk6 candidate.
Installed framework files are not edited. Accepted RX/TX paths unchanged.

ProfileStoreResponse only adds fields61..70, diagnostic version3, uint32 register/
IRQ/task observations. Config, UltimateProfile and persistent schema unchanged.
Scratch3 alone owned:0x5256 namespace, milestone bits12..15, application phase
bits8..11, flags0..7; old0x5254 accepted for previous-marker readback. RUN/power
reset may erase scratch. No reset solely to recover evidence. irq_state bits:
0 USB NVIC enabled,1 pending,2 software IRQ known,3 enabled,4 pending,5 PRIMASK,
6 USB reset_done,7 currently in exception,8 port returned,9 tud_inited,
10 current connected,11 current mounted; bits24..31 IRQ number or255 unknown.
Milestones are declared in RecoveryUsbDiagnostics.hpp. Raw SIE_CTRL/INTE/INTS/
INTR/address/main_ctrl and task-entered/returned are included if serial works.

## Validation and limits

check_glyph_rt2_dcd_observer.py extracts pinned real init/reset/IRQ decoder,
address status and endpoint-open functions. Real USBD/control/CDC/backend/store
run under ASan/UBSan. Exact SDK register layout/bits retained, host address bases
and SET/CLEAR/W1C side effects modeled. NVIC delivery, packet completion and
DPRAM electrical transfer explicitly modeled; full DMA continuation fails closed.
Mach-O uses symbol renames rather than GNU wrapping, so final ARM ELF binding
proof remains separate. Physical macOS recognition/timing/electrical failure is
NOT_MODELED. Forced VBUS pin makes unplug a suspend perception; the source-faithful
replug case uses suspend then reset, not invented unplug callback.
Tests distinguish pull-up off/silent/reset/setup/descriptor/address requested vs
applied/configured, IRQ delivery withheld/NVIC disabled/global mask, software
task deferred, and replug. They require at most eight frames, MB1-only exact GRB
words, zero refresh over10000 idle and1000 white loops, unchanged filesystem and
complete inspection/refusals. Removing DCD event capture is a negative control.
Existing startup timing/PIO fallbacks/normal Configurator, recovery/store/CDC,
resource/stack/source invariance and target build gates are recorded separately.
No build/host result constitutes hardware PASS. Final resource deltas and exact
UF2 size/hash/custody are in final handoff receipt, pinned to reviewed commit.
