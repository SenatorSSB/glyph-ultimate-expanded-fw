# Comprehensive RT2 USB observer contract

Disposition: MULTI_PROFILE_STORE_RT2_COMPREHENSIVE_USB_OBSERVER_READY_WITH_RESIDUALS,
conditional on exact committed build, source/harness/ELF/custody proof and fresh
independent review. Firmware-active diagnostic candidate only. Direct owner
request2026-10-17 authorizes this extension; response-only schema additions
explicitly approved in chat. No controller actions or canonical merge. Do not
run the superseded3b5c hardware packet. New branch codex/profile-store-rt2-comprehensive
is direct child of3b5c92b2200753c795315a166dc7bd501a93a9f6 (tree
8637a3d0c1ae5be03c64628cca3fca56842803f9; its parent88ab0029d464175865e1ce3e9a19b462579ffed4).
Canonical/base remains6b73a7c507f35c111745c6bdd341618b490cbdcd. Final candidate/tree/
UF2 identities live in external exact-artifact handoff; no self-SHA cycle.

## Separate physical evidence

466: owner establishes route/inspection/Serial/backend/read-only/publication,
loop and first SendReport return, normal Configurator PASS, no RT2 USB device/
serial. Keep that application phase11 boundary; it does not establish current
pull-up or every task return on a different snapshot.
5913: retained2E8A:000A still failed; identity switch is physically insufficient,
though mixed identity source mechanism remains real. Its RED is no proven exact
SendReport block. Ordinary recovery1092 remains; no retain000A A/B is carried.
b075: one distinct boot purple/violet consistent MAGENTA supports
RT2_DCD_BUS_RESET_RECEIVED_NO_SETUP_OBSERVED, not independent pull-up ON proof.
88ab: normal control chip2/ROM3/B2/E5flags0 establishes
E5_PHYSICALLY_INAPPLICABLE_ON_TEST_CONTROLLER. Its separate RT2 RED establishes
only REPEATED_RECOVERY_LOOP_OBSERVATION_NOT_ESTABLISHED, no reset or exact block.
3b5c remains hardware NOT_TESTED. Do not transfer milestones between boots.
The retained profile_store_rt2_task_physical_adjudication.json binds88ab normal
baseline and original evidence hashes. Root cause UNPROVEN; Nunchuk NOT_TESTED.

## Integration and observer authority

Pinned framework Arduino-Pico3.6.3/package1.30603.0, Adafruit2.3.0/TinyUSB0.16.0,
SDK1.5.1; actual hashes/compiled flags and final ARM bindings accompany custody.
No installed package edits. E5 stays compiled OFF and physically inapplicable.
The existing core1 recovery branch follows synchronized published boot outcome;
setup1 refuses recovery before normal menus/RGB/gameplay construction. Existing
loop1 recovery branch runs observer then returns. No TinyUSB, USB mutex,
Configurator, input scan, display/menu initialization, backend selection or
persistence operations on that branch. Core1 reads only bounded atomic banks,
non-destructive USB status registers and hardware time; writes dedicated LED
PIO/diagnostic scratch only. Core1 NVIC is not mistaken for core0's USB NVIC.
No application branch or USB drain/queue/descriptor/identity policy is changed.

Fourteen source-owned GNU wrappers call original once, preserving arguments,
return values and function-pointer behavior: existing tud_task_ext,
tud_control_xfer,dcd_set_address,dcd_edpt0_status_complete,usbd_control_reset,
user_irq_claim_unused,C++ _Z23TinyUSB_Port_InitDeviceh; plus tu_fifo_write/read,
cdcd_reset,mscd_reset,hidd_reset,midid_reset,
usbd_control_set_complete_callback. Strict Mk6 candidate source/link gating;
other FIFOs transparently pass through by exact &_usbd_qdef.ff identity check.
Final proof must check incoming calls AND actual builtin driver table pointers,
not symbol presence alone. See independent source audit for pinned lines and
relocations. No sleeps/delays/detach/attach/retries/task budgets/event drops/
reordering/drain-loop edits/descriptor edits/E5 workaround/persistence changes.

Queue send/read wrappers run inside existing Pico OSAL critical section, around
out-of-line FIFO calls. They add no lock; they do add bounded loads/stores/DMBs
to the existing IRQ-masked interval. This perturbation is real, not certified
negligible or physically causal. Queue non-overwriting capacity16 unchanged.
Write bool is exact acceptance/failure; event hook remains only DCD emission.
Queue occupancy/max is exact at instrumented boundaries, not electrical demand.
Read bool+copied event gives consumption; no event bytes are modified. Reset
versus SETUP drops recorded independently, aggregate other failures separate.

Successful SETUP consume precedes control-processing entry. First NULL
usbd_control_set_complete_callback in process_control_request gives entry;
latch once per consumed event, despite later NULL calls. Descriptor wrapper
records successful submission, never host receipt. Address request and actual
post-status application differ. Nonzero effective8-bit SET_CONFIGURATION status
marks configuration; consumed RESET/UNPLUG or cfg0 retires its shadow. This is
last observed software boundary, not an atomic tud_mounted read on core1.
Ever-configured but retired is separate MAGENTA enumeration indication. Supported
inspection decode is whole version-valid PULSE/STATUS/LIST/READ/HEALTH, not proof
response succeeded. New comprehensive progress is independent of legacy88ab
reset-epoch count matching, so a dropped RESET cannot hide later actual control.
Existing raw register response fields keep their old live/epoch meanings.

## Foreground and reset semantics

Foreground means armed recovery observer + core0 + exception0. Pre-loop calls,
hardware IRQ and software USB-task IRQ are excluded. Entered invocation IDs
increase monotonically, current ID is published at active.store; Return clears
active at its linearization point, retains latest returned and first_returned.
Never reuse saturated ID; snapshot invalid at UINT32_MAX. First-call history
cannot hide later active calls. Counters saturate; sequence words are validation
generations, not event counts. They may wrap; accepting requires no change over
the bounded sample (no2^32 updates can occur inside that sample at target clock).

DCD reset bank independently keeps total since enable, before first entry,
during first, current invocation-tagged count, and after first return. IRQ
interruptions during odd foreground publication are attributed using the active
ID linearization, not entered count. Pre-active entry is pre-first; after active
clear is outside that invocation. Current resets zero/one/2+ never use stale prior
ID. Two resets are evidence of multiple emissions, not an infinite reset storm.

Successful RESET/UNPLUG consume sets generic reset stage1 and invocation ID;
stages2/3 CDC entry/return,4/5 MIDI entry/return,6 after-real usbd_control_reset,
7 next queue-read attempt (even if empty). Class entered/returned masks reset on
each newly consumed reset. Four builtin wrappers record exact MSC/HID as well;
class callbacks from SET_CONFIGURATION are excluded by consumed-event context.
XInput reset is local/static and empty; ordinary external wrap unavailable.
Consumption-to-CDC brackets it; do not shadow a driver table just to mark empty
code. This is XINPUT_RESET_BOUNDARY_RESIDUAL. Reset completion marker is generic
RESET/UNPLUG processing, distinguished by event telemetry; forced VBUS target
unplug normally appears as suspend, not invented disconnect callback.

Atomic banks: foreground, hardware IRQ events, serialized USB task owner,
queue producers split foreground/hardware/software IRQ, core1 raw sampler.
Aligned32-bit seq_cst load/store only, no atomic RMW/helper library, heap, added
USB lock, spin or waiting. USB task bank changes only under existing serialized
owner. Supported inspection flag has a separate foreground single-writer word,
so IRQ task cannot nest a write to that sequence bank. Core1 performs one bounded
double-sample attempt; mixed bank generations reject and retry next ordinary
loop. Snapshot is coherent bank publication, not a simultaneous electrical world
snapshot; cross-bank pipeline steps can legitimately be in flight.

## Static ten-second panel

HandOffIndicator records hardware time then release-publishes ownership after
core0 final PIO write; after existing boot publication only core1 owns SM/FIFO
and scratch3. Core1 takes valid bank samples while waiting for elapsed10s,
without blocking either core. At first valid sample at/after10s it copies the
entire immutable Snapshot, elapsed time and observed active-ID age, release-
publishes full dashboard, then emits exactly one successful panel frame. No
bank changes after that can refresh it. Mixed snapshot can postpone capture;
serial elapsed field records actual capture time. Failed PIO availability leaves
unknown human display; no LEDs is never proof of non-entry.

First ORANGE means active at capture, not proof of10s non-return. Later WHITE
requires same active ID observed for at least1s on core1; later YELLOW is active
but observed for less than1s, possibly a healthy transient. This duration is a
reporting qualification only, never USB execution budget/timeout/action. Same-ID
observation across endpoints establishes non-return across those samples, not
infinite hang or actual function-entry timestamp. Core1 first sees the ID after
its publication; age is a lower-bound observation duration. First/current counts
and exact IDs remain in captured telemetry. Human reads once, no color sequence.

Exact source pixel_to_button_mappings at Mk6 neopixel_definitions.hpp:11-14:
0/1 MB1,2/3 LF4,4/5 LF3,6/7 LF5; LED_PIN11,GRB. Button-association source-backed;
left/right orientation inside a pair is unproven. Report the two colors in each
pair in EITHER ORDER; role palettes decode unambiguously. LF4 shared BLUE is
unambiguous because stage never MAGENTA. A pair may contain identical colors.
Physical ability to resolve both component colors remains hardware observation.
Other68 LEDs are outside dashboard and not evidence. Display-layout labels in
button_positions.hpp locate LF4(6,29), LF3(15,23), LF5(24,32); these are rendered
layout coordinates, not invented PCB pixel coordinates. No claim of which side
of a physical pair is first in its wire chain.

| Pair/pixel | Meaning | Static colors |
| --- | --- | --- |
| MB1 pixel0 | foreground task | RED not entered; ORANGE first active; GREEN first returned/no current active; YELLOW later active<1s observed; WHITE later active>=1s observed |
| MB1 pixel1 | resets in captured current invocation | OFF0; BLUE1; MAGENTA2+; OFF when no current invocation |
| LF4 pixel2 | last reset-processing stage for current invocation (or latest if none active) | OFF no matching consume; RED consumed/pre-CDC; ORANGE CDC entered; YELLOW CDC returned/pre-MIDI; CYAN MIDI entered; GREEN MIDI returned; WHITE usbd_control_reset returned; BLUE next queue-read attempt |
| LF4 pixel3 | total DCD reset emissions after enable | OFF0; BLUE1; MAGENTA2+ |
| LF3 pixel4 | SETUP pipeline, ever observed since enable | OFF none; BLUE raw only; CYAN DCD emitted; GREEN consumed; WHITE control processing began |
| LF3 pixel5 | queue loss/pressure | OFF no loss/full boundary; MAGENTA max occupancy16; RED RESET drop; ORANGE SETUP drop; YELLOW both critical drops or other event loss |
| LF5 pixel6 | enumeration, ever/current-boundary-qualified | OFF none; YELLOW device descriptor submitted; CYAN address requested; BLUE address applied; GREEN configured at latest observed boundary; MAGENTA configured history retired by reset/cfg0; WHITE supported inspection decoded |
| LF5 pixel7 | pull-up register sampled at capture | RED PULLUP_EN OFF; ORANGE ON; OFF unknown. This is a control bit, not electrical PHY/host recognition proof |

PIO uses dedicated unused SM, joined8-word TX FIFO preloaded completely with SM
disabled. No blocking FIFO puts or CPU refill, DMA/IRQ handler or PLL/system
clock changes. Eight pixels take240us at800kHz; inherited200us IRQ-enabled
protocol interval returns while PIO finishes the final40us independently, then
last SET drives pin low and next OUT stalls empty. Pixels retain frame through
low latch; no subsequent frame competes. Frame hardware behavior/LED silicon
and USB timing still require owner observation, not host inference.

Full32-bit Dashboard packs8 color nibbles in wire order, low nibble pixel0.
Scratch3 namespace0x5259 contains task/current-reset/setup/enumeration nibbles;
it is a partial summary, not all8 pixels. Legacy namespaces remain valid for
previous-marker readback; selectors0..2 and SDK4..7 untouched. Volatile captures
can be lost on reset; no reset just to recover scratch evidence.

Diagnostic response-only fields103..128 extend task version5/startup version6.
Before frozen capture, task fields are a bounded live sample and Dashboard0;
after capture, all task fields come from the immutable captured Snapshot.
Response chooses that mode once and only emits dashboard/age/elapsed for that
same captured decision, preventing mixed live/frozen response. Existing USB raw
fields remain asynchronous live observations, explicitly separate. Config,
UltimateProfile, requests, storage and mutation behavior remain unchanged.

## Residuals and coverage

Complete A-Q/critical-outcome matrix is profile_store_rt2_comprehensive_coverage.json.
Every branch has bank instrumentation or named source limitation; photo summaries
have finite precision and are not all counters. Outside-current reset before/
during first/after first is exact captured telemetry but total/current pixels
cannot identify every historical epoch without serial. MSC/HID exact bracket
masks are telemetry; photo YELLOW only narrows CDC-return through pre-MIDI.
Those are PANEL_SUMMARY_RESIDUAL, retained rather than adding DMA, streamed
frames, uncertain extra mapping, subtle colors or another physical attempt.
No raw positive sample is RAW_SETUP_SAMPLING_RESIDUAL: brief latch may be missed
by polling. DCD emission independently proves an event. BUS_RESET with no raw
SETUP observed cannot distinguish no host packet from electrical/PHY/controller
failure to latch: HOST_PHY_SETUP_RESIDUAL. Use external USB protocol analysis or
authoritative host USB trace if capture ends there. Queue acceptance is observed
exactly, not QUEUE_ACCEPTANCE_RESIDUAL, while filtered-before-queue events and
electrical packet demand remain unobserved. Short active call at capture is not
a proven block: TASK_SAMPLE_DURATION_RESIDUAL. Snapshot/PIO unavailable is
OBSERVER_UNAVAILABLE_RESIDUAL. No observer is proven to cause physical failure;
no root-cause or negligible-perturbation claim is made.

## Verification and delegation

Focused source-faithful harness uses pinned Pico OSAL/FIFO, real USBD/control/
class drivers/backend/store and extracted DCD init/IRQ functions. Electrical
completion/MMIO/NVIC/core scheduling and stall injection are explicit host
models; actual macOS acceptance NOT_MODELED. All seven requested negatives,
queue pressure/drop/consume, class boundaries and concurrent snapshot rejection
are required. Actual final results/source hashes are in handoff evidence.
Historical b075/88ab/3b5c post-handoff color assertions are superseded by this
comprehensive consumer; their source-bound harnesses stay with frozen commits.
Frozen3b5c runs as a historical positive control. Current shared startup/normal/
PIO fallback consumer is checked separately.
Existing accepted d596 coordination/895TX/4eeRX, root, Config/persistence/fault,
migration/selection/read-only consumers are focused regressions. No global
framework aggregate PASS is claimed. Final target RAM/flash/ABI/both-core stack
and all14 wrapper bindings must be independently checked before custody handoff.
Hardware acceptance remains NOT_EXECUTED and required before any merge.

Delegation guidance applicable: AGENTS + VALIDATION_AND_GATES/SUBAGENT_CONTRACTS;
complete visible runtime capability catalog confirms native collaboration.
Independent bounded source specialist audited queue/class/control symbols;
separate harness helper owns only new checker/fixtures; fresh independent
reviewer owns review, not implementation/publication. Root owns integrated diff,
validation, exact build/custody/publication; no new user chats or Planner/Curator.
