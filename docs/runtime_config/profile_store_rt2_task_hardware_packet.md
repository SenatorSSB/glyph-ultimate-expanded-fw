# One-attempt first-task / reset diagnostic packet

PREPARED / NOT EXECUTED. Source agents do not operate the controller. A separately
authorized human hardware session must first complete the [88ab read-only
adjudication](profile_store_rt2_task_device_adjudication.md). Any failed command
or authority discrepancy blocks replacement. Bind the new candidate SHA/tree
and exact preserved UF2 size/SHA-256 from HANDOFF; rehash those preserved bytes.
Do not rebuild or substitute an image.

## Established silicon and retained evidence

`RP2040_E5_PHYSICALLY_INAPPLICABLE_ON_THIS_CONTROLLER`: normal88ab reports chip2,
ROM3, B2 and E5 flags0. No E5 workaround or GPIO15 experiment is in this packet.
The single failed88ab RT2 was RED/black/no transport: only repeated recovery-loop
observation was not established. No88ab reset receipt or task non-return is
proven. Historical b075 MAGENTA/reset-with-no-later-SETUP belongs to a separate
boot; its color does not prove pull-up ON. Preserve both results separately.

## Normal control, then exactly one attempt

1. After88ab adjudication PASS, install the exact new preserved UF2 using the
   established manual route, preserving storage. Perform normal boot without
   RT2/MB1 and require Configurator enumeration and exact firmware identity.
2. Capture device info, PULSE/STATUS, complete LIST, full READ1/3/4/22 and
   GET_CONFIG. Require incarnation1/generation166, accepted Config generation
   1182731055 and full Config/profile correspondence to the adjudicated state.
   Require no uncertainty, pending/armed fault or unresolved transaction/receipt.
   Record stack/heap measurements. Confirm chip2/ROM3 and E5 flags0 again.
   Ten-second host ceiling per command; stop on the first failure/discrepancy.
3. Enter RT2 exactly once without MB1. Wait ten seconds. Report the two settled
   colors in the existing MB1 top-left pair, display appearance, matching
   controller USB-tree identity present/absent, and serial endpoint present/
   absent. No video or transient sequence is needed. Preserve actual host
   inventories and identities. No further lights are used.

## Version5 settled MB1 pair

The two existing MB1 pixels now carry independent facts so reset-count evidence
cannot be hidden by SETUP/control progress. Pixel0 is the task indicator and
pixel1 is progress by source wiring order. Physical upper/lower orientation is
not source-established and need not be guessed: report both colors in either
order. The palettes overlap only in GREEN, which is unambiguous when both are
GREEN. If light diffusion prevents distinguishing the pair, report UNKNOWN;
do not turn a blended color into a guessed software state.

Task pixel (RED / ORANGE / MAGENTA / BLUE / GREEN):

| Settled color | Meaning |
| --- | --- |
| RED | First recovery foreground USB-task entry not established |
| ORANGE | First task entry recorded, return not recorded, zero DCD reset emissions during its observed active interval |
| MAGENTA | First task return not recorded, exactly one DCD reset emission during that interval |
| BLUE | First task return not recorded, two or more DCD reset emissions during that interval |
| GREEN | That same first task invocation returned at least once; latched thereafter |

Progress pixel (OFF / YELLOW / CYAN / GREEN / WHITE):

| Settled color | Meaning |
| --- | --- |
| OFF | No later progress marker recorded |
| YELLOW | A reset-processing path completed during the first foreground invocation: class resets and control reset returned |
| CYAN | DCD SETUP event emitted since recovery observation began |
| GREEN | Attributable device-descriptor/address control progress observed |
| WHITE | Configuration completion or complete supported recovery inspection decoded |

For example, BLUE+YELLOW retains both repeated DCD reset emissions before the
first task returns and a completed reset-processing path. ORANGE+CYAN records
SETUP while no reset emission was attributed to that first active interval.
GREEN+OFF establishes first-call return, leaving any later transport failure
outside that first-call non-return hypothesis.

These are observed source boundaries, not proofs of an infinite hang or an
electrical reset storm. BLUE means at least two DCD reset emissions during one
observed invocation; no measured reset rate or perpetual queue replenishment is
implied. Events may be dropped by a full queue. The completion marker also serves
UNPLUGGED, and queued events can predate invocation entry; YELLOW does not identify
which emitted reset was consumed. CYAN/GREEN/WHITE are cumulative progress and
may precede a later reset. None proves host receipt of a response.

Task entry/return markers bracket the real call with small instruction windows;
IRQ observations in those windows belong to the recorded interval. The task
pixel intentionally anchors the first invocation and stays GREEN after its
return. It does not identify a stall in a later invocation. Current-invocation
counters remain available only through working read-only transport. This avoids
healthy repeated calls creating flicker or a false settled non-return claim.

Core1 publishes changed states independently of core0 foreground diagnostic
reads. It does not run USB/Configurator, alter inputs, or initialize recovery
menu/display/gameplay. A missing/failed publisher, unavailable PIO, or halted
core1 cannot establish observer liveness; no lights or unclear colors are UNKNOWN.
No timing-based non-return threshold or firmware startup delay is added.

## Stop and capture

4. If no endpoint exists: STOP in place after the settled-pair/host-inventory
   capture. No second RT2 attempt, reset, command, reflash, cleanup, QUERY, fault
   operation, GC or selection. Do not attempt another transport to retrieve RAM.
5. If endpoint exists: bounded read-only device info, PULSE/STATUS, complete LIST,
   READ1/3/4/22 and GET_CONFIG only. Require unchanged useful authority and valid
   recovery read-only state. Capture `recovery_task_version=5` and
   `recovery_startup_diagnostics_version=5`, task invocation and
   return counts, active ID, first-return flag, current/first reset counts,
   generic/first-invocation reset-completion counts, event/task flags and pair,
   plus retained silicon/USB observations and resources. Use the [versioned
   contract](profile_store_rt2_task_diagnostic_contract.md) for exact field bits.
   Stop after capture; no fault campaign or automatic recovery exit follows.

Retain exact candidate/artifact and all request/response/host-evidence hashes.
Hardware PASS is not inferred from source tests or build success. Root cause
remains UNPROVEN. Root/GC V/W PASS remains separate; selection remains NOT_TESTED
— FIXTURE_NOT_SAFELY_CONSTRUCTIBLE and Nunchuk NOT_TESTED. No canonical merge.
