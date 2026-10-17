# One-attempt silicon and raw SETUP diagnostic packet

PREPARED / NOT EXECUTED. A separately authorized human session owns all device
operations. Source diagnosis performs none. Bind the final candidate SHA/tree
and immutable UF2 size/hash from HANDOFF; rehash those exact preserved bytes
before installation. No rebuild, substitute image, factory reset or canonical
merge. Complete the separate [b075 read-only adjudication](profile_store_rt2_e5_device_adjudication.md)
first; a failed adjudication blocks replacement.

## Scope of this candidate

The official E5 workaround remains DISABLED. This is a diagnostic comparison,
not an E5-on A/B or a claimed reset-to-SETUP repair. GPIO15 remains under its
existing matrix configuration; the observer does not borrow it or restore it.
The official workaround's asynchronous pin ownership and unbounded waits lack a
safe global bound here. An RT2 flag created after startup sampling would miss a
reset before that flag. No imitation of the workaround is installed.

None of the owner's three conditional E5/repair completion labels applies:
E5 is not ruled out on the unknown chip, an official E5 A/B is not justified,
and no alternate physical cause is proven. The honest handoff is
`MULTI_PROFILE_STORE_RT2_DCD_DIAGNOSTIC_READY` with
`E5_DEFERRED_GPIO15_TIMING_UNBOUNDED`. Normal chip reporting resolves the next
silicon question without pretending the workaround ran.

## Normal control before RT2

1. After b075 adjudication PASS, install the exact new preserved UF2 through the
   established manual route, preserving storage. Normal boot without RT2/MB1.
2. Require Configurator enumeration, exact firmware identity, complete PULSE,
   STATUS, LIST, READ1/3/4/22 and GET_CONFIG. Retain raw responses and hashes in a
   unique directory. Compare incarnation/generation166, Config and useful
   profile bytes/revisions/reference authority to the adjudicated state. Require
   no pending/armed fault or unresolved receipt/transaction and valid resources.
   Stop at the first timeout/discrepancy. Host waits are at most ten seconds.
3. Record additive silicon fields: `recovery_usb_chip_version`,
   `recovery_usb_rom_version`, and `recovery_usb_e5_flags`, interpreting exact
   bits: bit0 compile-enabled, bit1 chip eligible, bit2 would execute. This
   artifact must report bit0=0 and bit2=0; bit1 is independently observed.
   Version1 means B0/B1
   (E5 affected); version2 means B2 (E5 fixed). ROM version1/2/3 distinguishes
   B0/B1/B2 respectively. Unexpected or inconsistent values require adjudication,
   not an inference from product age. E5 compile-enabled and would-execute must
   both be false in this artifact; chip eligibility is reported separately.
4. If version2/B2: E5 is physically inapplicable to this controller; do not run
   an E5-fix test. If version1/B0/B1: E5 remains a possible cause, but this image
   still does not enable it. Either known case may proceed to the one raw
   discriminator attempt below. Report normal matrix sanity through an already
   available input observer if possible; do not alter Config or start broad
   gameplay testing. E5 GPIO15-restoration validation is NOT_APPLICABLE because
   no workaround executes, not a hardware PASS for that workaround.

## Exactly one RT2 attempt

5. Enter manual RT2 exactly once without MB1 using the established stimulus.
   Wait ten seconds. Report settled MB1 top-left pair color, black/other display,
   host USB-tree matching identity present/absent and serial endpoint
   present/absent. Retain the actual identity if present. No video or transient
   color sequence is required. The ten seconds is an operator observation window,
   not an added firmware startup delay.
6. Interpret the current reset episode's furthest meaningful evidence:

   | Settled MB1 | Meaning |
   | --- | --- |
   | RED | repeated recovery-loop observation not yet established |
   | ORANGE | repeated loop, pull-up ON not yet observed |
   | YELLOW | pull-up/repeated loop, no processed DCD bus reset |
   | MAGENTA | DCD reset received, no raw SETUP indication observed afterward |
   | BLUE | raw SETUP hardware indication observed; no current-episode DCD SETUP event |
   | CYAN | DCD SETUP event emitted; no current-episode control progress established |
   | GREEN | current-episode device descriptor/control progress established |
   | WHITE | configured or a complete supported recovery inspection decoded |

   Color is an observation boundary, not proof that a response reached the host.
   MAGENTA cannot distinguish host-not-sent from hardware-not-latched. BLUE
   separates raw hardware observation from DCD emission; CYAN separates DCD
   emission from task/control progress. Queue emission is not queue acceptance.
   A newly processed bus reset starts a new diagnostic episode: stale progress
   from an earlier episode must not mask the later reset-only boundary. Within
   an episode progress is sticky. LEDs do not continuously refresh unchanged
   states. No LEDs or an uncertain color is UNKNOWN.
7. If endpoint absent: STOP in place after preserving settled color and host
   inventories. No second attempt, reset, reflash, cleanup, fault operation or
   attempt to retrieve RAM through another transport. Do not manufacture serial
   evidence for an absent endpoint.
8. If endpoint exists: read device info, PULSE/STATUS, LIST, full READ1/3/4/22 and
   GET_CONFIG. Require complete valid responses, read-only recovery state and
   unchanged useful authority. Capture the full additive diagnostic fields:
   chip/E5 state, reset-order bits, SIE_STATUS/INTR/INTS/INTE and their sticky
   observations, NVIC enabled/pending, PRIMASK/reset_done, EP0 buffer controls,
   reset/raw-observation/DCD-event counts, task-reset count, observation-valid
   flag and task entry/return counts. An invalid observation is retried by
   firmware later; it is not a coherent register snapshot.
   Exact field semantics and concurrency limitations are in the
   [diagnostic contract](profile_store_rt2_e5_diagnostic_contract.md).
   No fault matrix, CREATE/SET refusal mutation, GC, selection or cleanup belongs
   to this narrower silicon/DCD diagnostic attempt. Stop after capture; later
   recovery acceptance/exit is separately authorized.

Preserve exact SHA/artifact and request/response/host-inventory hashes with
PASS/FAIL/NOT_TESTED rows. A new observation does not erase b075's failed RT2,
466 phase11 evidence, the failed5913 identity control or separate root/GC V/W
PASS. Selection remains NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE; Nunchuk
NOT_TESTED. Physical E5 or other root cause remains UNPROVEN until evidence
establishes it. No source merge before exact hardware acceptance.
