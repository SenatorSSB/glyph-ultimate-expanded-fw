# External pre-SETUP RT2 observer contract

Direct owner scope: one observer-only descendant of0f22b6d3b5d4a1a16fc7fd03866cfa44336de4ff,
tree4f5fb41553f98da3f11108685b2eaa0942583fc0, parent3761b702ea09f50b9c98a55bea91caa337a3f62e.
Canonical6b73a7c507f35c111745c6bdd341618b490cbdcd remains unchanged. No source-agent
controller action, USB/endpoint repair, panic suppression, private-handler or
installed vendor edit, persistence/mutation change or canonical merge. Exact final
source/build/resource/custody/review identities are in the preserved HANDOFF.

## Owner physical authority

Normal0f22 is owner-reported PASS: /dev/cu.usbmodem101, generation166, useful profiles
and Config preserved, core min-free1856/3716, heap11244/capacity72684. Exactly one RT2:
LF4WHITE/LF3YELLOW/LF5OFF, black/no matching IORegistry controller/no serial; no later
action. See profile_store_rt2_pre_setup_physical_adjudication.json.

Classification SETUP_INTERRUPT_STATUS_OBSERVED_NO_DCD_SETUP_EVENT. SIE/INTR/INTS
SETUP were each sampled positive historically, not necessarily simultaneously.
No stronger sampled gate or raw-positive trampoline boundary was established;
these conditions were not proved impossible between samples. No SETUP event,
queue/control/descriptor/address/configuration was established. Do not infer IRQ
never entered: an earlier invocation may have stopped before later SETUP arrived.
DCD_HANDLER_STATUS_RESIDUAL, DCD_EARLY_SETUP_BRANCH_RESIDUAL and
RAW_REGISTER_SAMPLING_RESIDUAL remain. Root cause UNPROVEN. Historical boots,
MB1 visual unreliability, B2/E5 physical inapplicability and prior V/W PASS remain
separate. Selection/Nunchuk NOT_TESTED.

## Active source and external seams

Pinned Arduino-Pico3.6.3 / Adafruit2.3.0 / TinyUSB0.16.0 / PicoSDK1.5.1. Exact active
DCD is the framework Adafruit source, not the SDK's other TinyUSB copy. Single
private status read precedes SOF, BUFF_STATUS, SETUP, then later bus/reset branches.
An invocation entered before SETUP can remain active while core1 later observes
SETUP. Existing single-slot registration trampoline is retained; new entered,
returned, current ID and latest-returned state no longer require SETUP-positive
entry. Each sequence bank closes before real code so non-return does not leave
an eternally invalid snapshot. Duration is an independent core1 observation of
one active ID, never a USB time budget or proof of infinite non-return.

SOF: E15/uframe fix OFF, so optional endpoint loop absent. All five target driver
SOF callbacks (XInput/CDC/MSC/HID/MIDI) are NULL. Ordinary initialized SOF processing
is finite; suspended-SOF RESUME enqueue and transfer-complete enqueue can acquire
the PicoOSAL critical-section spinlock without timeout. Queue FIFO depth16 has
no FIFO mutex; once its critical lock is acquired, valid event copy/index work is
bounded. Queue full returns false and does not panic. Record external SOF/event
entry/return; no unnecessary private SOF instrumentation.

BUFF_STATUS uses one finite32-bit snapshot, clears a selected bit before external
hw_endpoint_xfer_continue, then can emit XFER_COMPLETE and reset transfer state.
The continuation wrapper records entry, software ep_addr/active, current remaining
buf_status, object pointer and current IRQ ID BEFORE one real call, then result
and return if it returns. Return true means source transfer-complete result;
return false means continuation returned with further work, not failure. A returned
continuation does not prove the private BUFF_STATUS branch, queue or handler returned.

Continuation's explicit inactive-endpoint panic survives NDEBUG. The helper's
already-AVAIL buffer panic and private handler's Unhandled IRQ panic also survive.
The endpoint lock helper is empty; active continuation and start-next-buffer have
finite per-buffer work under valid lengths, at most2 buffer copies, no active
abort polling. Standard asserts are removed by NDEBUG. Corrupted pointers/lengths,
SDK locks and other faults remain outside the bounded-valid-state proof.

## Panic observation and forwarding

The original exact target panic is noreturn: banner puts, optional viprintf,
newline puts, then _exit(1). Original libc recursive lock acquisition can block
before _exit. Exact _exit repeatedly executes BKPT0; do not substitute generic
SDK WFE semantics. Target _write is a no-op return0, not Serial/USB diagnostic
output. Original panic does not explicitly stop core1, reset USB or disable its
clocks. Continued independent core1/peripheral operation is source-consistent
inference, not a guarantee against debugger/HardFault/global-fault behavior.

GNU wrap panic at external references. A naked Thumb veneer saves r0-r3,r4,LR
in24 bytes (8-byte aligned), calls a bounded observer, restores original argument
registers/r4/SP/LR, and tail-branches through IP to real panic. Variadic stack
arguments remain untouched. The observer only samples enabled/core0/USBCTRL
context and bounded format prefixes, writing closed atomic panic kind/currentIRQ
state. It performs no logging, heap, lock, recovery or MMIO writes. Inactive,
Unhandled and OtherUsb are separate kinds. No real call is skipped or repeated.
Unarmed paths still forward. The original code may block, trap or never return.

The24-byte manual frame may not appear in compiler .su; account it separately
only while the observer runs. It is released before real panic. Compiled-Thumb
instruction modeling with adversarial caller-saved clobbers complements, but does
not replace, independent final ELF ABI/relocation proof. Host tests throw only at
the real extracted source panic boundary; they do not execute target libc panic.

Coverage is explicit external DCD/helper panic relocations, not every conceivable
panic/fault. Same-TU hard_assertion_failure->panic can bypass GNU wrapping;
__assert_func->_exit can bypass it too. No active standard DCD assertion remains
under NDEBUG. No panic latch is not universal proof of no panic: a live handler
with no exact marker remains NONRETURN_NARROWED, including these residuals.

## Reset/late buffer hypothesis

See profile_store_rt2_pre_setup_reset_audit.md for official register and timing
matrices. Software reset_non_control_endpoints clears EP1–15 endpoint controls,
software endpoint objects and allocation pointer. It does not write BUF_STATUS,
noncontrol buffer-control DPRAM words, EP_ABORT or EP0 state. Hardware USB bus
reset effects on BUF_STATUS clearing/preservation and completion-versus-disable
arbitration are UNKNOWN in the inspected authority. Register RESET defaults
refer to peripheral reset and cannot substitute for USB bus-reset evidence.

A buffer bit arriving after the handler INTS snapshot or after its later fresh
BUF_STATUS snapshot can evade that invocation's finite buffer loop. If it
survives reset's endpoint-state clear, a later handler could reach an inactive
object. This is a conditional source mechanism, not proof hardware preserves
such a bit or that this physical boot followed it. Combined BUFF+RESET status
alone services BUFF before software reset and does not prove reset-induced panic.
EP0 IN/OUT are not zeroed by noncontrol reset. Unconfigured/just-initialized
endpoints are inactive but no ordinary packet completion is assumed there.
Double-buffer reassert wording is not evidence this target exercised that mode.
Conditional test schedules must retain both the software order and hardware unknowns.

A zeroed noncontrol object's ep_addr becomes0 and can misidentify it as EP0/OUT.
Expose exact target object pointer as separate32-bit telemetry. Final ELF private
hw_endpoints base/stride can decode object identity offline; no private symbol is
referenced by running observer code. Software address number/direction and actual
array identity must not be conflated. A photo alone cannot identify endpoint index.

## Whole main-button panel and immutable publication

GPIO11 map: MB1 pixels0/1 DARK; LF4 pixels2/3 handler liveness; LF3 pixels4/5
pre-SETUP evidence; LF5 pixels6/7 retained SETUP/downstream. Both LEDs of each main
button are identical. No menu diagnostics, orientation, mixed pairs, video or
transient sequence. Three main buttons fit the existing joined8-word FIFO.

| Button | Settled color meaning |
|---|---|
| LF4 | BLUE coherent frozen observer/no handler entered; GREEN latest observed handler returned; ORANGE current ID observed active<1s; RED same ID observed active>=1s; WHITE intercepted USBCTRL-context panic |
| LF3 | OFF no branch marker; YELLOW SOF returned; BLUE continuation entered; CYAN continuation returned; ORANGE SOF external call entered/not returned; MAGENTA inactive endpoint observed before real continuation; WHITE exact inactive panic; RED Unhandled IRQ panic; GREEN OtherUsb panic |
| LF5 | OFF no SETUP boundary; ORANGE external SETUP entry; MAGENTA old hook; CYAN SETUP accepted; YELLOW task consumed; BLUE control began; GREEN descriptor/address milestone; WHITE configured-current/inspection; RED SETUP drop overrides |

LF4 BLUE is a deliberate positive ready/no-entry color, avoiding all-dark ambiguity.
All-dark/unresolved panel remains UNKNOWN. LF3 markers are last/sticky history with
higher-priority active SOF/inactive/panic evidence; they are not a private branch
trace. In particular CYAN means continuation returned, not complete BUFF_STATUS
return. LF4WHITE+LF3WHITE identifies the observed inactive-panic call site;
WHITE+RED identifies Unhandled IRQ; WHITE+GREEN another intercepted USB panic.
MAGENTA is the inactive predicate before the original call, not proof the panic
wrapper ran. LF5 progress can show that the previous boundary did not reproduce.

Core1 remains independent after existing recovery handoff; no TinyUSB/USB mutex,
Config/persistence, gameplay/input or normal display calls. Bounded aligned32-bit
load/store banks, no RMW, heap, shared locks or spins. Each failed/mixed read gets
one retry on a later ordinary loop. At/after10s freeze task/setup/pre-SETUP copies
and panel under the same release publication. Backend caller-owned static caches
share that one frozen/live decision. Handler age has new getter/response182;
existing foreground-task age127 retains its meaning.

PIO preloads one8-word frame with its SM disabled, then hardware finishes without
CPU refill, blocking FIFO put or DMA. Retain inherited IRQ-enabled200us protocol
interval; frame240us finishes independently and stalls low. No startup delay,
USB retry/budget/drop/reorder/drain or descriptor policy change. Scratch3 namespace
0x525b stores LF4 nibble12/LF3 nibble8/LF5 nibble4/darkMB1 nibble0; historical525a,
5259 and older remain accepted. Selectors0–2 and SDK4–7 untouched. Full Dashboard
still has8 wire-order nibbles. Panic before core1 handoff/observer publication,
PIO unavailable, sampling misses and hardware faults remain honest residuals.

Response-only156–182 version1 exposes IRQ/endpoint/SOF/xfer/panic fields, pointer,
capture mode/validity and handler age. Existing task/reset/raw/setup fields remain.
No Config/Profile/Request/storage/schema-persistence or mutation-protocol delta.

## Physical decisions and stop

Normal0f22 adjudication packet is separate: one normal boot, bounded read-only
GET_DEVICE_INFO/PULSE/STATUS/all LIST/READ1/3/4/22/GET_CONFIG, incarnation1/store166,
accepted useful bytes and Config1182731055, no uncertainty/unresolved receipt or
armed/pending fault, resources, STOP. Any failure blocks replacement.
After PASS: exact new manual install, normal control/authority then one RT2,
wait10s, one settled LF4/LF3/LF5 observation plus display/USB/serial. No endpoint:
STOP IN PLACE. Endpoint: bounded read-only capture, STOP. No retry, GC, selection,
cleanup or mutation/refusal campaign. HOST_PACKET_TRACE remains NOT_AUTHORITATIVE.

Inactive panic physically observed -> PRE_SETUP_PANIC_PHYSICALLY_SUPPORTED,
no immediate fix; separate source diagnosis/proposal for exact stale-buffer cause.
Active/nonreturn with no exact panic -> DCD_HANDLER_NONRETURN_NARROWED.
Returned handler + raw SETUP/no event -> PRIVATE_HANDLER_DIAGNOSTIC_REQUIRED,
only then evaluate reproducible private TU copy/patch or SWD in a separate bounded
step. Setup succeeds -> classify downstream evidence. No private source modification
is necessary or implemented in this external candidate. Root cause UNPROVEN.
