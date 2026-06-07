# Glyph Public / Manual Workflow Release Candidate Hardware Plan

Status: TEMPLATE_ONLY_NOT_A_RESULT
Branch: `runtime-config-public-workflow-release-candidate-plan`

This is a hardware-test template for the manual/public workflow release-candidate preparation. It is not a hardware result and does not claim any unexecuted behavior.

## 1) Build Artifact Identity

| Field | Value |
| --- | --- |
| Build command used | `./scripts/build-glyph-mk6-quiet.sh` |
| Firmware artifact path | _fill after local build (if emitted)_ |
| Firmware artifact SHA-256 | _fill after local build (if emitted)_ |
| Commit SHA under test | _fill before test_ |
| Tester | _fill_ |
| Test date | _fill_ |

## 2) Intent

- Manual/operator-run firmware update path only.
- No runtime-loaded config.
- No WebSerial/device write.
- No flashing automation.
- No hidden writes.
- Hardware result must be recorded in a separate result branch after the test.

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after the manual workflow update path reaches expected boot state | NOT_TESTED |
| PROFILE-001 | profile | Current profile remains usable after the workflow preparation | NOT_TESTED |
| BASELINE-001 | baseline | Source-backed baseline outputs remain preserved | NOT_TESTED |
| MODIFIERS-001 | modifiers | Representative modifier tables remain preserved | NOT_TESTED |
| SPECIAL-001 | special_tables | Special tables remain preserved | NOT_TESTED |
| OVERRIDE-001 | override_paths | Representative override paths remain preserved | NOT_TESTED |
| CSTICK-001 | cstick_interaction | C-stick interaction is not regressed where doable | NOT_TESTED |
| DOCS-001 | docs_navigation | Docs/navigation/checklist links remain synchronized | NOT_TESTED |
| NO-WRITE-001 | no_write | No hidden write, runtime-loaded config, or WebSerial/device write occurs | NOT_TESTED |
| NO-FLASH-AUTO-001 | no_flash_automation | No flashing automation, UF2 copy automation, or bootloader automation occurs | NOT_TESTED |
| RECOVERY-001 | recovery | Manual recovery/rollback path remains operator-run only | NOT_TESTED |
| PROFILE-REG-001 | profile_regression | No profile regression observed | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED |

Allowed result statuses:
- `PASS`
- `FAIL`
- `NOT_TESTED`
- `BLOCKED`
- `USER_ACCEPTED_RISK`

## 4) Manual Boundary

- Manual/operator-run only.
- No hidden writes.
- No runtime-loaded config.
- No WebSerial/device write.
- No flashing automation.
- No public release claim.

## 5) Nunchuk Scope

- Nunchuk scope for this branch: `NOT_TESTED`.
- Do not upgrade this row to PASS or FAIL unless a separate documented nunchuk hardware run is performed.

## 6) Result Recording Boundary

- Record any later result in a separate result branch.
- Do not turn this template into a result packet.
- Do not claim official configurator compatibility from this template.

## 7) Caveats

- `no_runtime_loaded_config` remains in force.
- `no_webserial_or_device_write` remains in force.
- `no_firmware_flashing_automation` remains in force.
- This plan is only a test template and does not replace a hardware result document.

