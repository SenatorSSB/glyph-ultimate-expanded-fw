# Finite GameCube observation and acceptance-authority finding

Date: 2026-10-22. Read-only finite review. No repository, source, queue, device,
firmware, Config, ProfileStore or hardware-contract action was performed. The
canonical local worktree was clean at b28c3da9dd134bae4aa1c9ab75a6f82be254dbaf.
This role did not claim fresh live GitHub verification. Exact F334f and its source,
build, artifact and resource holds are unchanged.

## Finding

The frozen acceptance contract does **not** mandate WUP USB capture on a Mac,
any particular computer, a raw-report reader, or electrical Joybus capture.
The Mac WUP reader is an observer proposal introduced to fill identified output
visibility gaps. Its unavailable connection is not itself a firmware failure
and should not become an invented equipment requirement.

The underlying contract still requires complete expected OutputState and backend
report observations for selected physical stimuli (protocol lines14–17), actual
backend bits and analog-trigger relationships with distinct GameCube L/R/Z
(H6, line60), honest limitations for indistinguishable outputs (H7, line61), and
own applicable GameCube route observations rather than transferred XInput PASS
(lines68–70). Owner M7 independently requires complete output observations and
prohibits transferring route acceptance. No amendment or waiver follows from the
owner's equipment statement or this review.

Manual observation on the owner's existing Mk6 GameCube → MOD. WUP-028 → Switch
route is therefore relevant end-to-end physical evidence. It can be recorded
under its actual exposed labels/actions, alongside native miniscreen numbers.
It establishes only what that screen exposes. It cannot automatically establish
the original GameCube bits, numeric trigger bytes, unshown simultaneous outputs,
or precise raw stick values upstream of the adapter. The mandatory session
addendum and reviewed packet already state that limitation; the proposed Mac
WUP37 report itself would also have remained an adapter-boundary observation,
not electrical pre-adapter capture.

## Source-grounded field boundary

F `HAL/pico/src/comms/GamecubeBackend.cpp:45–65` assigns12 digital report fields:
`a,b,x,y,z,l,r,start,dpad_left,dpad_right,dpad_down,dpad_up`, and six analog bytes:
`stick_x,stick_y,cstick_x,cstick_y,l_analog,r_analog`.
Z is `_outputs.buttonR`; L/R are `_outputs.triggerLDigital` and
`_outputs.triggerRDigital`. The six analog bytes are direct OutputState values;
there is no source authorization to equate downstream console labels or actions
with an unchanged raw GameCube wire representation. `buttonL`, select, home,
capture and stick clicks are not additional GC report fields in this serializer.

F `config/glyph/common/src/display/MenuButtonHints.cpp:252–257,354–373` reads
the primary backend's OutputState and prints four stick values minus128, plus
the two unscaled native trigger values. This is useful native output evidence
when actually readable, not proof that any backend transmitted it. Lines92–177
return one priority icon: A/B/X/Y precede Z/L/R, and one trigger can hide the
other. A+L+R cannot be proven by its A icon, and L+R cannot be proven by its L
icon. Static serializer proof and the existing host fixtures prove assignments
or corresponding tests, not physical delivery. A system/game action without
identified field meaning is downstream behavior only; no Smash semantics are
invented here.

## Concrete later manual-console plan from existing fixtures

This is preparation only. Do not execute it under the Mac-preflight approval;
that approval explicitly excludes installing F, Config/profile mutation and the
H1–H12 campaign. First complete the separately approved original-state backup,
known entry/restoration, chord subset and native-packet eligibility gates. Then
root may bind an owner-approved exact candidate-specific installation/test packet.

1. Name the actual already available Switch system/game screen and record what
   fields it shows. Establish labels by isolated controls rather than guessed
   GameCube/Switch equivalence. Record adapter-to-console path and session. Do
   not request an unavailable Mac connection, install tools, or add telemetry.
2. Keep H1 ordinary original-state recognition, neutral, both sticks, ordinary
   mapped buttons/triggers and reconnect on this route. Derive expectations from
   the actual preserved Config/profile; these are not fixed native fixture rows.
   The same observer/session mapping is needed for H12 restored ordinary output.
3. Reuse the existing nine N129–N137 isolated-L/R/Z controls below. Record actual
   console indicators/actions separately and all readable native OLED numbers.
   Other GC bits are0 and all four stick bytes128 in these rows. Record invisible
   fields as unobserved; absence of an icon is not a false bit observation.

| Row | Held physical inputs | GC L | GC R | GC Z | native/expected GC L analog | native/expected GC R analog |
| --- | --- | --- | --- | --- | --- | --- |
| N129 | released | 0 | 0 | 0 | 0 | 0 |
| N130 | BTN_LF6 | 1 | 0 | 0 | 140 | 0 |
| N131 | BTN_LF7 | 0 | 1 | 0 | 0 | 140 |
| N132 | BTN_LF8 | 0 | 0 | 1 | 0 | 0 |
| N133 | BTN_LF6, BTN_LF7 | 1 | 1 | 0 | 140 | 140 |
| N134 | BTN_LF6, BTN_LF8 | 1 | 0 | 1 | 140 | 0 |
| N135 | BTN_LF7, BTN_LF8 | 0 | 1 | 1 | 0 | 140 |
| N136 | BTN_LF6, BTN_LF7, BTN_LF8 | 1 | 1 | 1 | 140 | 140 |
| N137 | released | 0 | 0 | 0 | 0 | 0 |

4. Reuse complete sample1 S021–S029 and sample2 S030–S038 as intact ordered
   nine-step groups. They already supply one-input A+L+R (S022/S031), genuine
   direction+A and cancellation (S023/S024 and S032/S033), independently active
   A/OR and forced coordinate controls, and combined A+L+R+forced coordinates
   (S027/S036). The distinguishing forced coordinates are sample1(78,84) and
   sample2(79,85), OLED(-50,-44) versus(-49,-43). These distinguish profiles in
   native numbers even when the downstream screen cannot resolve a one-unit
   difference. They do not establish downstream exact coordinate equality.
   Preserve every listed transition, inserting no release/reboot inside a group.
   Capture separately approved persistence/reboot/reselect controls and ordinary
   final restoration; never infer GameCube active-runtime identity from XInput.
5. Allocate remaining logical coverage across the actually available physical
   observers. The complete334 logical rows, all18 families and H1–H12 remain
   preserved in `finding_and_manual_cards.json`; it copies each selected row's
   exact context, held inputs, full prior history, complete native/GC fields,
   OLED expectations and null observations. That file is a template, not an
   alternate expected-output oracle or authorization.

The27 core rows above are an economical **distinction/visibility block**, not a
complete GameCube acceptance minimum or chapter completion. The frozen contract
does not set a number of GameCube rows or mandate334 repetitions on each of three
routes. H1 does explicitly cover every affected supported route; H6 requires its
actual GameCube distinctions. H2–H8 and all18 logical families cannot disappear
when duplicate route work is reduced. Primary comprehensive output capture was
proposed on XInput, but currently has zero reports; it is not an achieved basis
for omitting another physical row. Preserve all78 SOCD history steps and all21
forced win/lose/filter rows somewhere in actual logical physical coverage, plus
every required modifier/rebinding/conflict sample. The existing packet's default
and Mode nine-entry rows, RS axes/diagonals, RF5/6/7, Dpad/null and rebound rows
remain available without inventing new test profiles. Any final per-route
allocation needs explicit coverage/observer rationale. H10 remains qualified
XInput/current-Configurator/new-gameplay-session work; it adds no GC attestation.

## Only indispensable unknowns and conditional substantive decision

Root needs the exact existing system/game screen name and whether it exposes
simultaneous L and R and a separately distinguishable Z; the six stick/trigger
numbers or only directional/actions; A/B/X/Y/start/Dpad combinations; and actual
miniscreen readability. A single compact question can ask those field capabilities;
no new device action or unavailable equipment is needed to answer it. Unknown
screen semantics remain unknown, and a lack of numeric/bit display is a valid
answer. The owner's phrase “see that the claimed output matches” is not evidence
that an unshown bit or byte is observed.

If that existing screen cannot expose required fields, there is a precise
evidence-standard decision: either retain the affected physical acceptance gate,
or obtain an explicit bounded owner amendment defining acceptance from paired
native OLED numbers plus the named console's actual observable outputs while
preserving a list of original GC wire fields as physically unobserved. Such an
amendment would change the existing complete-backend-observation standard; it
cannot be silently issued by this reviewer, root, a host test, or the general
“proceed” instruction. This review does not prescribe a purchase, install, new
observer implementation, extra firmware telemetry, or impossible Mac equipment.
It does not call the revised evidence standard already approved.

## Preserved actual state and limits

The root-supplied approved preflight found one XInput0738/4726 at location0x100000,
then its sole capture stopped at the interface guard before open with zero reports;
no retry is approved. This role did not re-execute or independently reinterpret
that session. WUP Mac inspection/capture/0x13 were never performed; the owner's
unavailable route is NOT_TESTED/UNAVAILABLE, never FAIL/PASS. No installation,
profile/Config mutation or physical campaign approval exists. The27-card block and
all334 templates remain NOT_TESTED with null observations. Timing/highwater remain
NOT_MEASURED, GC/Switch timing unmeasured, no GC runtime identity is invented,
Nunchuk remains NOT_TESTED, and RT2 remains deferred/unresolved. Source/artifact
holds, original evidence and all resource limits are untouched. Independent HEP,
exact tested-source integration and strict DONE remain required.

## Narrow known-menu backup-entry qualification

The separately requested source check is recorded in `CONFIGURATOR_ENTRY_QUALIFICATION.md` and `configurator_entry_source_comparison.json`. The existing Configurator branch specifically skips its watchdog Save action; GET_CONFIG streams saved bytes rather than the temporary live RAM default. Full menu/selector/GET/raw-load bodies match accepted307d/baseline976 as recorded. This supports a separately owner-approved known menu entry with its actual firmware restart, while retaining unknown installed firmware, ordinary startup/recovery and positive CDC identity/normal-status/backup validation limits. It does not approve or execute that entry.
