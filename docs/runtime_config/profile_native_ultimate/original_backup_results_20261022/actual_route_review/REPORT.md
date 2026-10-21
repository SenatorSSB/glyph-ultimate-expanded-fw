# Actual-Config route and next hardware-packet recommendation

Finite offline M6 planning, 2026-10-22. No device request, source/queue change,
new build, original-backup write, installation, physical test or approval occurs
in this report. F334f and its exact retained instrumented UF2/build/resource/
identity contracts remain frozen. Original Config publication is hash-only;
only the necessary derived route/chord facts are stated below. Full original or
derived Config/profile payloads are not emitted into this report directory.

## Actual configuration and exact Switch route gap

The252-byte original Config payload SHA256 is
`54fda3988c30e03b653153ec23d0623674da3649492caa75da8aa08fbce6b460`.
Its decoded JSON and complete protobuf agree. It is existing compact store
format1/incarnation1/root2 with no embedded profiles and three existing Ultimate
mode rows. Both backend default indices are1. The necessary route facts are:

| Existing backend row (one-based) | Backend | Default Ultimate row | Startup binding |
| --- | --- | --- | --- |
| 1 | XInput | 3 | empty |
| 2 | GameCube | 1 | empty |
| 3 | Configurator | 1 | BTN_RT2 (physical ID42) |

All three GameModeConfig activation chords are empty. This is actual saved
configuration, distinct from the temporary live-RAM Configurator default used
while the backup was obtained. Original complete data remains private and exact.

No Nintendo Switch USB backend row exists. F `console_detection.cpp:21–43`
reports the USB-connected sentinel as XInput; `backend_init.cpp:69–96,343–353`
then uses the selected USB default configuration. It does not infer Nintendo
Switch reports from the attached console. The USB menu at
`DefaultConfigMenu.cpp:17–44` lists only existing configured XInput/DInput/Switch
rows, so a missing Switch row cannot be selected there. This observed route gap
must not be hidden by prior owner reports of older Switch testing or by source
support for the backend itself.

The smallest necessary **USB Switch data delta** preserves existing entries and
indices and appends one fourth CommunicationBackendConfig:

```text
backend_id = COMMS_BACKEND_NINTENDO_SWITCH
default_mode_config = 3
activation_binding = empty
```

This uses the existing supported NintendoSwitchBackend; no firmware/backend/
descriptor modification or new activation chord is needed. Appending the record
alone leaves both defaults1. Entering its route later requires explicitly
selecting USB backend row4 and reinitializing; returning to XInput selects row1.
These are future approved controller operations, not read-only actions.

The structural append adds6 bytes to this original Config encoding (252→258),
within the existing15-backend capacity; no Config struct or resource limit is
expanded. Hashes of the offline exact data variants are in `result.json`; no
variant payload is published or sent. A new Switch route has no prior ordinary
physical H1 baseline under this current Config. Its ordinary baseline should be
established with the existing selected legacy Ultimate row after enabling that
route, explicitly labeled a newly enabled route, rather than invented as an
already observed original Switch configuration.

## Recommended minimum test-routing economy

Use existing Ultimate row3 (zero-based mode index2) as the single controlled
native test row. Current XInput already selects it, and the new Switch row can
select it. To use the same native profile/context on GameCube, temporarily change
only existing GameCube backend row2's `default_mode_config` from1 to3. That one
field is an economical shared-row choice, **not** a logical requirement for
enabling Switch: alternatively GC can retain row1 and receive its own separately
planned native context/reference sequence. Do not silently assume GC uses the
same row as XInput today.

With a shared row, preserve all three existing backend records/order, every
startup/mode chord, all other mode rows, original references/payloads and both
default indices except the expressly approved USB1↔4 selection. Apply the
existing fixture context only to row3 and select disposable native profile IDs
through the existing checked-reference operation. Distinct profiles remain in
storage and boot-bound; do not hot-swap, overwrite original IDs or cache bodies.

The existing `prepare_native_context` helper admits only remap/SOCD replacement
inside one existing Ultimate row. It does **not** implement append-backend,
backend default-mode, or default-USB edits. Its whole-Config whitelist must not
be bypassed with a fabricated “original” restore backup. The generic older
artifact CLI's fixture policy is also not a justified substitute for a guarded
actual-unit route edit.

Therefore the final packet needs a narrow host-only route-data adapter or an
equivalently pinned exact-artifact workflow: start from a fresh verified backup,
allow exactly the append/fixed default changes above, retain incarnation and
all firmware-owned receipts/current reference metadata, compare every other
field, reserve exact custody and require the existing exclusive Configurator
session/fresh STATUS/GET_CONFIG fences before its one approved SET. Whole-Config
SET still lacks an atomic generation fence; retain that honest limitation and
no automatic retry. This report is not an executable adapter or execution
authorization.

Pure calls to the existing frozen helpers confirm that representative exact
compatibility and safe complete-sample contexts can still be applied to row3
after this in-memory route delta without changing any backend/default field.
`prepare_native_restore` with the **true original** then restores original user
fields and three backend records; actual later restoration must retain current
firmware-owned monotonic receipts as the existing helper requires. These checks
are limited host preparation evidence, not target acceptance or a new semantic/
resource proof. No firmware change or rebuild follows from this Config data gap.

## H11 reentry: known menu is valid at the source boundary

The owner-known Menu → Configurator path is a source-grounded normal-mode H11
reentry choice. F `Ultimate.cpp:782–800` sets NativeUnavailable for an unavailable
or mismatched native program and neutralizes **OutputState** only. It does not
disable input scanning, delete the mode object, stop normal loops, or alter raw
menu controls. `ControllerMode.cpp:20–27` remaps/SOCDs copies; the original input
snapshot remains intact. `CommunicationBackend.cpp:9–21` shares the original
InputState, and `IntegratedDisplay.cpp:8–28,60–90` reads physical MB1/MB2/MB3/MB4
directly from that original state. `config.cpp:419–430` supplies the same global
inputs and controls; its normal loop1 continues display/menu service.

Thus neutral native controller reports do not themselves prevent navigating to
the known menu action, whose existing Configurator branch skips its watchdog
Save action and restarts into the ordinary Configurator session. This is an
inference from the exact control/data paths, not a physical observation of F in
NativeUnavailable or a guarantee against unrelated UI/transport failure.

Use this route for H11 on **XInput**. The menu item is usb=true; ConfigMenu skips
USB-only top-level items for GameCube/other console backends. Do not assume the
same on-device item is reachable directly while running the GC backend.
The existing mandatory addendum literally called for a verified raw-input
startup route. Root has accepted the narrow procedural clarification: retain
that historical addendum and explicitly replace only the H11 entry method with
the known ordinary menu operating on original physical input. Preserve the
actual reentry/normal-session/restore safety requirement and all other addendum
steps. This changes the chosen procedure, not the H11 neutral/refusal/rollback
acceptance criterion.

In the future exact packet, after approved F installation but **before** the
first deliberate native mismatch, verify the ordinary menu works on F and returns
an identified normal Configurator session with original/durable readback and
fresh fences. Recheck its availability during matched native use before H11.
After H11's expected neutral/refusal observation, use only this verified menu
entry and checked reference back to matched A; record the actual result. If the
menu or normal CDC session is unavailable, stop H11 and preserve evidence, with
no speculative chord, reset/flash/erase or automatic recovery fallback.

## BTN_RT2 is a startup hazard to avoid, not a mandatory recovery experiment

The actual Config stores BTN_RT2/ID42 as an ordinary backend activation binding.
`config_utils.cpp:8–25` selects a nonempty matching raw held subset at startup;
`state_util.hpp:34–35` makes empty masks nonmatching. A cold boot/reconnect held
with RT2 can therefore select Configurator after ordinary Config/store startup.
It is not proof of the retired early/manual RT2 recovery route. F config.cpp's
PrepareBootDisplay explicitly states that manual RT2 inspection is deferred;
normal stored Config must already load successfully for the ordinary backend
selector to run.

There is no need to physically exercise RT2 cold entry when the known raw-input
menu route is used for H11. Its startup possibility is source-backed but remains
physically unverified. Existing RT2 deferral forbids reopening severe/manual
recovery investigation or treating ordinary source selection as RT2 acceptance.
Retain B7A normal refusal/recovery safety and B7B deferred/unresolved status.

Thirteen selected logical rows contain RT2: O185/O212/O293,
N074–N078/N082/N083/N086/N088/N110. They are **runtime** held states after normal
gameplay initialization; they are not boot-entry procedures. Keep controls
released at every normal boot/reconnect and never hold these sets across it.
Do not drop those RS/rebinding cases merely because RT2 is also a startup chord.
All actual GameMode activation masks are empty, so this backup has no nonempty
runtime mode chord hidden inside those held sets; preserve that fact in planned
Config modifications and keep the existing held-subset guard.

## XInput CDC is a separate source-feasible observation channel

F XInputBackend begins Serial at115200 and the secondary-backend initializer
installs B0XXInputViewer for XInput. The viewer sends25-byte records containing
physical **inputs**, not native OutputState or transmitted controller report
fields. It cannot replace failed raw USB output capture.

The normal core0 loop services current-session RuntimeIdentity only for primary
XInput after viewer output; `RuntimeIdentityService.hpp` preserves the original
16/72-byte identity protocol and demultiplexes the separately authorized fixed
native metrics request/160-byte response. The exact existing identity and metrics
host tools can parse viewer interleaving. The metrics path remains source-bound,
bounded, read-only and instrumentation-specific; it reports post-startup timing/
stack observations, never six controller analog values or a complete virtual
button mask. It cannot close unobserved outputs or GC/Switch timing.

This supports feasibility of later XInput CDC viewer/identity/metrics use under
an explicit exact-candidate packet. It does not establish this Mac's XInput CDC
port, access, report delivery or current installed firmware support. The successful
ordinary Configurator CDC session is a different backend/session. The one raw
XInput USB capture stopped at its interface-selection guard before opening and
returned zero reports; that does not prove the CDC channel failed or succeeded.
No XInput retry, new serial lookup/open/query, route change or candidate install
is proposed for execution now.

## Minimum concrete prerequisites for the next owner approval

The exact source/build/resource/review/artifact tuple is already frozen. Root
reports original Config and all22 original profile custody audit PASS; bind those
private hashes, the retained legacy metadata/body distinction and the exact
completed-read counter audit in the final source-free packet. No further backup
read or generic review/build campaign follows from this report.

Offline M6 preparation already covers the actual route delta/data receipts,
guarded host-only preparation, row3 context/reference schedule, known-menu H11
clarification, exact physical fixture allocation and true-original restoration
plan. Pin the actual scripts/data used. Protect original profiles and use only
the two owned disposable IDs, fresh fences and exact known-outcome readbacks.
No firmware source or memory/storage-cap change is needed.

The next explicit candidate-specific owner packet must authorize its exact F/UF2
installation procedure, each temporary Config/backend/default/context change,
owned ProfileStore mutation sequence, manual reinitializations and menu entries,
bounded XInput CDC identity/metrics/report observation operations, physical
all18/H1–H12 stimuli, monotonic metadata/cleanup/restoration and uncertainty stops.
The approved read-only preflight grants none of those writes/installations or
the campaign. Approval can be staged within one concrete packet: after install,
verify normal ordinary behavior/menu/identified CDC and observer availability;
only then perform its separately enumerated native profile operations. A failed
prerequisite stops the dependent phase rather than triggering another route or
automatic device operation. No additional intermediate preference or RT2 question
is needed solely because this report identified the routing data.

For complete physical acceptance, actual output observers remain indispensable.
The owner will use the existing manual GameCube → WUP-028 → Switch route; no
WUP-to-Mac access is required. The exact existing Switch screen/game and exposure
of simultaneous L/R/Z, analog triggers and other required fields remain UNKNOWN;
root has asked one concise field-capability question. Paired OLED and downstream
console observations are useful but retain their separate boundaries. The prior
finite console report already supplies N129–N137 and S021–S038 observation cards
and all334 logical templates; keep all18 families/H1–H12 and route-specific H1/
H6/H12 observations without blindly repeating334 rows on every route.

If available observers cannot expose a required field, leave it PARTIAL/
NOT_TESTED and obtain the precise bounded evidence-standard decision before
claiming complete acceptance. Do not substitute input viewer, identity, metrics,
source tests or OLED for unobserved backend fields. Candidate installation can
only be a separately approved staged action, never a claim that these physical
gaps are already solved. Human HEP PASS, tested-source integration and strict
DONE remain later gates. RT2 remains deferred/unresolved, Nunchuk NOT_TESTED,
timing/highwater NOT_MEASURED until actually captured, root cause UNPROVEN.
