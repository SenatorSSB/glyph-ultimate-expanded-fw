# RT2 / E5 independent review

Status: source/design and focused host review APPROVED for the bounded
diagnostic candidate; exact build/resources/custody review pending. This is
not hardware acceptance or merge approval.

The independent reviewer read the explicit owner request in the attached
`Pasted text.txt`, the repository operating boundaries and the pinned source.
Review baseline is `b07502866c56a1c7e1e217132aea30366e234461`, tree
`f6274649de4a7e620b19be795d16f95e53550683`, parent
`466f91ed867884640375627734d3473e9fb22c32`; canonical source remains
`6b73a7c507f35c111745c6bdd341618b490cbdcd`. No controller operation, production
test/source edit, Git mutation, final build or persistence change was performed
by this reviewer. Reviewer output is `/private/tmp/glyph-rt2-e5-review`.

## Independent E5 adjudication

The source supports **E5_DEFERRED**, not E5 rejected and not an E5 repair claim.
Pico SDK 1.5.1 `pico_platform/platform.c` reads the SYSINFO revision field;
`pico/platform.h` explicitly maps chip version 1 to B0/B1 and 2 to B2. ROM
version is a distinct value (1=B0, 2=B1, 3=B2). The actual controller revision
is UNKNOWN until a normal read-only diagnostic response reports it.
The official [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf),
USB errata E5, describes the post-reset idle-time failure on B0/B1 and its
hardware correction on B2. This matches the class of observed failure, without
establishing its cause.

The exact SDK workaround checks `rp2040_chip_version()==1`, waits for SE0 to
end, changes GPIO15 input override/function/pads, forces USB LS_J, and later
restores the saved GPIO15 control/pad words. It has no general finite worst-case
duration: both SE0 and CONNECTED waits can continue indefinitely. Alarm success
returns while the workaround remains in progress; alarm exhaustion uses busy
wait. The two saved GPIO registers are singleton static state without an
explicit reentry guard. Register restoration is exact only for a completed,
nonoverlapping execution without another owner changing those same registers.

The Mk6 matrix is COL2ROW, with rows 26/25/24/23 driven and GPIO15 read as
column zero. That column contains MB1/LF3/LF4/LT5; RT2 is on GPIO21. The scanner
changes row pins, not GPIO15 per scan. `gpio::read_digital` calls `gpio_get`,
and the official workaround's GPIO15 `INOVER_HIGH` can therefore suppress a
held column-zero button while its asynchronous interval overlaps scanning.
The first sample occurs in core0 setup; normal backend scanning also occurs in
core0. USBCTRL IRQ can preempt either; returning asynchronously does not lock
out scanning. The debounce logic accepts a changed value immediately and then
locks it for 5 ms, so it does not prove this transient harmless. MB1 boot
priority can be lost if held with RT2. A later normal-mode host reset can
reintroduce the same hazard.

Arduino-Pico starts TinyUSB before core1 launch and application setup. Thus a
bus reset can be observed before setup, during the first matrix sample, after
route entry or after publication. A runtime RT2 flag set after sampling cannot
protect the early reset that may require the workaround. There is no existing
ownership interlock making global E5 safe, and no source-backed late gate that
covers all the requested timing. Keeping E5 disabled and exposing silicon plus
raw/DCD/task diagnostics is within the bounded diagnostic request.

## Physical interpretation and preserved boundaries

The owner's b075 purple/violet observation is conditionally adjudicated as
MAGENTA under that candidate's source mapping: repeated recovery loop,
DCD bus reset observed, no later recorded SETUP/control milestone. Source
inspection corrects one premise of the request: MAGENTA does not require the
`pullup_seen` flag, because the reset branch overrides the progress value
independently of that flag. Pull-up ON was separately observed in normal
control, but the RT2 color alone does not establish it. The color does not
establish absence of a host SETUP packet, hardware
latch, raw IRQ, event-queue delivery or USB task execution. Root cause remains
UNPROVEN. VID/PID timing alone is physically insufficient; V/W PASS is retained
separately; selection remains NOT_TESTED / FIXTURE_NOT_SAFELY_CONSTRUCTIBLE.

## Design review findings to resolve before acceptance

1. Pre-reset raw/SETUP/descriptor evidence must not falsely classify a later
   reset-only failure. The implementation must define its reset epoch, test
   simultaneous SETUP+RESET (pinned DCD handles SETUP first), and test a queued
   pre-reset SETUP while the USB task is deferred. Any intentional reset of a
   previously sticky LED needs an explicit per-epoch contract.
2. A USBCTRL reset can interrupt a wrapper between its real function and its
   diagnostic mark. Epoch attribution must prevent that old work becoming new
   epoch progress. Foreground register reads are not atomic snapshots.
3. The raw observer must remain read-only, avoid GPIO15 ownership, avoid IRQ
   masking/acknowledgement, and distinguish positive samples from unique packet
   counts. The pinned event hook executes after an enqueue attempt regardless
   of enqueue success; CYAN cannot claim successful queue delivery.
4. Final exact ELF proof must bind the existing wrappers and show the E5 macro
   chain remains disabled. Host models cannot establish physical USB timing,
   real NVIC scheduling or hardware acceptance.

These design findings are resolved by the final reviewed source and tests
described below; exact build/custody remains the separate final gate.

## Independent validation and source verdict

The reviewer independently reran `tools/check_glyph_rt2_dcd_observer.py` with
output `/private/tmp/glyph-rt2-e5-review/observer`: all initial 23 scenarios and the
removed-reset-hook negative control PASS under ASan/UBSan. This includes raw
SETUP with NVIC disabled, PRIMASK masking and INTE masking; DCD event with task
deferred; old queued SETUP followed by reset; simultaneous SETUP/reset in one
DCD interrupt; replug epoch regression; and B0/B1 chip eligibility with the
workaround disabled. The MMIO and IRQ environment remains an explicit host
model, not electrical proof.

The independent startup run at `/private/tmp/glyph-rt2-e5-review/startup`
passes 20 timing/PIO cases and both normal Configurator controls. Its real
pinned descriptor/USBD/CDC/backend path preserves read-only recovery; it does
not simulate macOS enumeration policy or prove hardware regression PASS.

All 29 retained physical evidence files named in
`profile_store_rt2_e5_physical_adjudication.json` were independently rehashed
and matched. The operator file identifies exactly one b075 attempt and
purple/violet; no current device access was performed. The prepared b075
adjudication and one-attempt packet preserve the stop-before-replacement gate,
normal silicon readback, ten-second host ceilings and no second attempt after
failure. The stale old capture identity fields are explicitly distinguished
from actual b075 identity/custody evidence.

The implementation now uses a seventh pass-through wrapper around
`usbd_control_reset`; independently inspected pinned `usbd.c` calls it only
from its reset routine when consuming BUS_RESET or UNPLUGGED. Equal DCD and
task reset counters exclude stale queued task work, and epoch-stamped control
milestones exclude an interrupted old wrapper from the new epoch. No vendor
source was patched. The observer's MMIO accesses are reads, and no new GPIO15,
USB acknowledgement, IRQ enable/disable, timer or persistence write appears
in the source delta. LED transport is unchanged from b075; the interpretation
is now sticky within each reset episode and may regress at a new bus reset.

The final independent observer rerun at
`/private/tmp/glyph-rt2-e5-review/observer-final/report.json` passes all 28 cases
and the removed-reset-hook negative. Added checks inject reset during a
foreground snapshot and inside the real control-transfer path, force a lost
reset event through a full queue, and observe resets during inspection and
after publication. The resulting invalid-snapshot retry, no false GREEN from
an interrupted wrapper, conservative CYAN after a lost reset queue entry and
correct route/publication bits all PASS. The read observer samples before and
after a reset epoch and withholds mixed-epoch advancement; short-lived display
changes between loop samples are not an atomic hardware trace.

The final event observation bank admits only BUS_RESET/SETUP hooks executing
on core0 in USBCTRL IRQ. This enforces its single-writer premise even though
the general TinyUSB event hook API can also be invoked for deferred functions.
The task control wrappers preserve original calls, arguments and return
values; their writes are only diagnostic counters/flags. The existing task
mutex serializes the task writers. Snapshot register ORs are cumulative
observations, not one coherent hardware configuration, and raw SETUP count
counts positive samples rather than distinct packets.

No blocking source finding remains. Source approval covers the finite
diagnostic delta from b075, the additive response fields and seven wrapper
bindings, with E5 disabled. It does not approve a silicon workaround, claim a
reset-to-SETUP repair, establish normal hardware regression or authorize a
canonical merge. Exact committed candidate identity, final ELF bindings,
resource delta and preserved UF2 custody still require final review.

The final directly affected selection/recovery fixture change adds the missing
`core/RecoveryUsbDiagnostics.hpp` include for the extracted setup source's new
stage markers. Independent inspection confirms it supplies inactive no-op
diagnostics in that fixture; it changes no product behavior or expectation.
Its previously observed compile failure is resolved by the implementation
role's rerun, which reports all selection/recovery route and negative cases
PASS. The reviewer read the final diagnostic contract and source audit; their
case, epoch, GPIO15, counter, queue and non-claim descriptions match the source.
The final reviewed changed non-document inventory contains 13 paths in
`/private/tmp/glyph-rt2-e5-review/reviewed-source-hashes.json`.
