# Later owner physical acceptance

Status: NOT_RUN / HARDWARE_RETEST_REQUIRED. Use only the new exact candidate tuple
in [CANDIDATE.json](CANDIDATE.json); source/build/custody are retained and exact hardware observations remain pending. This packet performs no device
action. Do not substitute old accepted de793f34 bytes or a rebuild. Installation is
manual owner work, not automated here. No fresh install/nuker/storage destruction.
Retain current readable Config and all ProfileStore records before any installation;
record initial source/artifact identity and ordinary backend/profile selection.
Use the existing [narrow installation/preservation contract](../beta-readiness/QUALIFICATION.md).
Capture final readback and account for intentional selector changes; no profile
CREATE/update/delete is needed. Preserve every anomaly and stop on unexpected state.

Record exact source SHA, tree, UF2 SHA-256/size, controller unit, host/OS, cable,
receiver, selected backend/profile and observed output for every applicable row.
Identify the executing profile by output when practical; a saved label alone is
not execution proof. Use PASS/FAIL/NOT_TESTED/N/A explicitly, never infer results.

| Row | Owner observation required |
| --- | --- |
| A1 Windows XInput identity — primary defect | Select XInput normally, direct USB to Windows. Record Device Manager identity and Hardware IDs; expected VID_0738 & PID_4726. Must no longer appear only as generic Pico. |
| A2 Windows XInput inputs | An actual XInput-capable receiver recognizes the controller; record changing LX and LY, one representative button, correct release and expected axis neutral; one profile-distinguishing value if practical. Browser tester is supplementary. |
| B1 Original Nintendo Switch USB identity | Original Switch recognizes controller with intended backend/profile. Switch 2 excluded. |
| B2 Switch / Ultimate regression | Left-stick movement, representative digital button, correct release/neutral and actual Ultimate input. Bounded regression only. |
| C DInput applicability and smoke | Use an existing selected beta profile only if its actual applicable_backends normally exposes DInput. Record final HID gamepad detection, changing axes, one button, release/neutral and distinguishing value if practical. Otherwise record exactly: N/A — no selected beta profile exposes DInput. Do not edit/create a profile for qualification. |
| D1 GameCube final beta route | Glyph → GC cable/adapter → original Switch → Ultimate; record cardinal + diagonal left stick, modifier-altered output, face button, shoulder/trigger, simultaneous input and release/neutral. |
| D2 GameCube gameplay / profile | Short normal gameplay, menu transition/return, and intended active profile distinguished by observed behavior. Existing earlier-image evidence does not replace this final candidate row. |
| P Config/ProfileStore preservation | Current preflight + final API-visible readback, all existing records/raw wrappers/revisions/inventory and Config; account for intentional normal selection changes. Preserve original restoration contract. |

N64/NES/SNES are excluded from reconnect by host/source proof. No new physical
retro qualification is required unless separately selected by the owner. Nunchuk
NOT_TESTED; keyboard and optional routes retain their existing deferred scope.
Do not test destructive recovery, change gameplay/report semantics, or expand beta
scope. Unexpected behavior stops the affected row for source-backed diagnosis.

After exact owner observations, fresh evidence review may accept only the reported
candidate/artifact/scope. Source-free hardware evidence precedes any tested-source
canonical integration and separate completion. Until then XInput remains
HARDWARE_RETEST_REQUIRED; Switch requires regression; beta release remains owner-held.
