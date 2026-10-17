# Minimal RT2 S0/S1 late SETUP diagnostic

Direct owner94b72102-c0d6-4424-9671-468508d9de49 authorizes this bounded diagnostic
from d30e5250ef2e5e425cc0f217fd37247b484ca988/tree259a311fe5f2ea5bee3fff9bb74600edcd883399.
Canonical6b73a7c507f35c111745c6bdd341618b490cbdcd unchanged. No controller action,
new RT2, USB repair, force/retry/service/clear/reset change or canonical merge.
Exact final candidate/artifact identity is in its sealed HANDOFF. Hardware NOT_TESTED.

## Physical authority and source gate

Owner reports d30e normal PASS (minfree1864/3716,heap10224/capacity71664,FS147456used/
376832free,B2/ROM3,E5disabled/inapplicable) and exactly one RT2 CYAN/OFF/OFF,
black/off,no matching USB identity,no serial. Under exact d30e contract, entries
occurred and RAW SETUP was positive, but ZERO private initial snapshots contained
SETUP. No local SETUP record/downstream. This is not failure inside the SETUP branch
and does not order RAW against entry/return. Prior88a36e/0f22/3761 boots stay separate.
See profile_store_rt2_late_physical_adjudication.json; root cause UNPROVEN.

Source audit completed before implementation: profile_store_rt2_late_source_audit.md.
RP2040 INTS is read-only masked/forced status; SETUP_REQ derives from SETUP_REC.
No read acknowledgement is documented. Pinned DCD SETUP branch is sole named
SETUP_REC clear; other branches clear disjoint flags. Ordinary BUS_RESET software
branch does not clear SETUP_REC; electrical reset/latch arbitration/synchronization
remain UNKNOWN. SDK1.5.1 official irq.c/chain.S/irq.h bytes match installed source.

ARM level-source expectation permits repending at architectural exception return.
ISPR0 during active USBCTRL is compatible with later repending, never proof of
failure. SDK shared chain does not clear USBCTRL pending/rescan INTS on return;
its later lowest-order port callback pends separate USB_TASK_IRQ. S1 precedes hook,
epilogue, remaining shared callbacks and EXC_RETURN; none are observed completed.

## Exact source custody and two hooks

Installed/pristine18095B SHA25692a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12.
Generated18267B SHA25677b27cfe939676abe4fc7986c1a6f82f9da9634a9e6915d60e9e4db145dee922.
Accepted candidate-owned replacement mechanism remains: fail-closed installed and
repository pin, deterministic insertion, original object excluded, exactly one
final DCD. Remove one header include, two calls and one S1 declaration to recover
exact pristine bytes. No installed package edits, upgrade or E5/E15/E16 option change.

Original first statement remains `uint32_t const status = usb_hw->ints;` (S0).
Zero intentional diagnostic operations/barriers before it; no trampoline/H0.
Immediately afterward GlyphDcdPrivateStatus(status) publishes compact initial facts.
Entire original vendor body/unhandled check unchanged. Then exactly one new read:
`uint32_t const late_status = usb_hw->ints;` (S1), followed by
GlyphDcdPrivateReturn(status,late_status), then normal source return. No H2-H8
callbacks, event/PID/clear markers, loops or USB work based on S1. There are exactly
two INTS reads, one original and one intentionally diagnostic.

Return hook samples core0 ISER, ISPR, then PRIMASK after S1. Gatebits1enabled,
2pending,4masked; zero means all sampled false only when associated record exists.
Samples are sequential, not simultaneous. Core1 never reads core0 NVIC/PRIMASK.

## Bank, history and publication

Snapshot16uint32/64B: valid,entries,returns,setup_status_count,reset_status_count,
buff_status_count,latest_s0,latest_s1,latest_gates,late_count,first_late_id,
first_late_s0,first_late_s1,first_late_gates,first_post_late_setup_id,overflow_flags.
State68B (15atomic payload words+enabled+sequence). Boot-lifetime history starts at
first S0 hook; Enable gates reader validity, never resets history. No extra duplicate
enabled-window records. latest_id=entries; active derived from entries>returns only
while precise. latest_s0 belongs to entries; latest_s1/gates to returns. They form
same-invocation latest pair ONLY if entries==returns with overflow_flags0. First
late tuple is always same invocation because Return takes actual S0/S1 arguments.

LATE_SETUP means !(S0&SETUP)&&S1&SETUP. Count occurrences; freeze FIRST tuple
{N,S0,S1,gates} forever. entries==N means no later S0 publication by captured sample;
entries>N means later private snapshot published. A S0 read whose hook publication
is incomplete is not yet visible. first_post_late_setup_id is set only by S0 with
existing N and current ID>N; an earlier global S0 SETUP never creates WHITE.

Sole serialized core0 USBCTRL writer, atomic32 payload, no RMW/helper/mutex/spin/
allocation. Each of two hooks independently closes its transaction: relaxed odd
sequence, release fence, relaxed payload, release even sequence. Reader acquire
begin, relaxed payload, acquire fence, relaxed end; equal even only, one bounded
attempt. Initial acquire excludes older payload. A newer payload read bridges
release/acquire fences, forcing final seq beyond old even by atomic coherence.
No odd record remains open across original vendor body/nonreturn.

All counters saturate with sticky quality bits: entry1,return2,setup4,reset8,buff16,
late32. Sequence at0xfffffffc performs final flags-only transaction ending0xfffffffe
with SequenceExhausted64; subsequent hooks no-op. No wrap/ABA. Partial last invocation
is retained but no precise absence/count/redispatch inference after quality loss.
Any positive retained SETUP stays a fact. Finite225RF illustration/source-order
mutants support the separate proof, not a general C++ verifier or physical model.

## Panel and response

LF4pixels2/3,LF3pixels4/5,LF5pixels6/7. Both LEDs SAME,MB/menu0/1dark. At/after10s
core1 freezes first valid coherent samples and publishes one immutable whole frame;
banks/MMIO/time are not a simultaneous hardware snapshot or exact10s instant.
Scratch3 namespace525d(v10), historical525c and earlier accepted; selectors0..2,
SDK4..7 unchanged. No refresh/video/transient/within-button decoding.

LF4: GREEN validempty/noRAW; MAGENTA noentry/RAW or precisionUNKNOWN; BLUE entries/
noS0SETUP/noRAW; CYAN entries/noS0SETUP/RAW; YELLOW any S0SETUP; RED retainedUSBpanic
override. Quality loss suppresses absence claims (MAGENTA), positiveSETUPstillYELLOW.
RAW means any historical SIE/INTR/INTS positive, never simultaneous/current packets.

LF3: OFF no late; RED late with entries==N; CYAN entries>N/no strictlypostN S0SETUP;
WHITE strictlypostN S0SETUP; MAGENTA qualityUNKNOWN. Pending-at-late is telemetry,
not an intermediate transient color. A later entry need not return to count.
LF5: OFF none; ORANGE external/oldhook entry; CYANaccepted; YELLOWconsumed; BLUEcontrol;
GREENdescriptor/address; WHITEconfigured/inspection; REDdrop. All-dark/unclear UNKNOWN.
LF4YELLOW means old cyan boundary did not reproduce; classify downstream. Private
history is boot-global, external bank recovery-only; do not infer cross-window loss.

Response-only private version3 retains fields183..190 and193..194/196 semantics
where applicable. Unsupported old multi/ever/marker/first/latestSETUPprogress/
enabled-window fields explicitly0, never negative evidence. New209..217 respectively:
latest_s1,latest_gates,late_count,first_late_id,first_late_s0,first_late_s1,
first_late_gates,first_post_late_setup_id,overflow_flags (recovery_private_dcd_ prefix).
Same captured/live publication and static caller-owned cache. No Config/Profile/
Request/persistent schema changes or mutation policy change.

## Perturbation, validation and decisions

Exploratory retained-flags probe is not final acceptance: expected noevent83added
instructions/4DMB vs d30e184/6; final ELF/assembly is authoritative. Final report
separates preS0 intentional0/compiler saves, S0→firstvendorbranch interval, S1read,
gates/returnpublication and total normal path deltas. Fresh review must explicitly
ask whether observer itself could materially create the late window. YES is possible:
postS0 work lengthens S0→S1; late publication lengthens S1→actualreturn; compiler
allocation can move saves before S0. No zero/negligible perturbation or cycle bound.
Existing external SOF/xfer/event/queue wrappers remain separately audited latency.

Current source-faithful harness replaces obsolete45branchtrace cases with minimal
S0/S1 cases while retaining89external/functional cases. Actual generated DCD,
production bank, real wrappers/task/queue and independent core1 freeze are used;
host MMIO/NVIC/latch transitions are explicit models, not silicon proof. Source/
assembly negatives reject any beforeS0 diagnostics, accidentalread, omittedS1,
S1USBbranch/clear/force/retry, sourceorder change, wrong arguments and dualobject.
All model counts/tests, actualtarget costs/resources, final source review and exact
candidate SHA/tree/parent/UF2 custody are bound in sealed HANDOFF. No aggregate PASS
by omission; unrelated framework aggregate NOT_RUN/NOT_CLAIMED. Hardware NOT_TESTED.

Decision1 RAW+/S0SETUP0/late+/entries==N: MULTI_PROFILE_STORE_RT2_LATE_SETUP_NOT_REDISPATCHED;
means late source-return sample and no later published S0 by capture, not completed
exception return or NVIC fault. Firstlatependingbit adds LATE_SETUP_NVIC_PENDING_AT_RETURN
(sampled afterS1). Decision2 RAW+/S0SETUP0/late+/entries>N/no postlateS0SETUP:
MULTI_PROFILE_STORE_RT2_SETUP_LOST_BETWEEN_RETURN_AND_NEXT_SNAPSHOT is cautious shorthand
for changed samples, not proven lost silicon latch. Decision3 late then postlateS0:
redispatch observed this boot; classify LF5. Decision4 RAW+/S0SETUP0/late0: no S1
caught it; outside windows or transience remains possible. If no safe discriminator,
MULTI_PROFILE_STORE_RT2_SOFTWARE_OBSERVABILITY_LIMIT_REACHED; use practical SWD or
externalUSB analyzer/authoritative host-bus trace next, not more software polling.
Any S0SETUP means old cyan boundary did not reproduce. Root cause UNPROVEN.

Separate d30e adjudication PASS before any replacement, then futureowner exactUF2/
normalcontrol/ONE RT2/wait10s/colors/display/USB/serial, absentSTOPINPLACE, present
boundedreadonlythenSTOP. No source-agent action/newRT2 now. See separate packets.
