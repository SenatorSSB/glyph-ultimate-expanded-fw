# Glyph Generated Constants Refactor Hardware Result - 2026-06-03

## Purpose and scope

This document records the branch-specific hardware result for the generated
constants firmware refactor on `glyph/gfw2-generated-constants-refactor`.

This result applies only to `glyph/gfw2-generated-constants-refactor`. It does
not validate runtime-loaded config, serial/device write behavior, profile schema
changes, nunchuk hardware behavior, or new gameplay semantics.

## Branch and implementation under test

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Branch under test: `glyph/gfw2-generated-constants-refactor`
- Implementation class: generated constants firmware refactor
- Result date: 2026-06-03
- Result fixture: `docs/calibration/fixtures/glyph_generated_constants_refactor_hardware_result_2026-06-03.json`

## Source authority

The hardware matrix source is:

- `docs/calibration/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.md`
- `docs/calibration/fixtures/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.json`

The recorded result is based on the user-reported row outcomes for this branch.
Unknown backend behavior remains unknown.

## Build/check status

The implementation branch had already run source, generated-config, behavior,
profile, serial dry-run, hygiene, build, and artifact-inspection checks before
this result was recorded.

This document is a hardware-result record, not build output and not hardware
flashing automation.

## Hardware matrix result table

| Row ID | Category | Status | Notes |
| --- | --- | --- | --- |
| BOOT-001 | boot | PASS | Reported pass. |
| PROFILE-001 | identity_profile | PASS | Reported pass. |
| DEFAULT-001 | default_table | PASS | Reported pass. |
| MODE-001 | mode_default | PASS | Reported pass. |
| XMOD-001 | x_modifiers | PASS | Reported pass. |
| YMOD-001 | y_modifiers | PASS | Reported pass. |
| TILT-001 | tilt_modifiers | PASS | Reported pass. |
| ZAIR-001 | z_airdodge_low_magnitude | PASS | Reported pass. |
| UPB-001 | hard_up_b | PASS | Reported pass. |
| NULL-001 | null_override | PASS | Reported pass. |
| DPA-001 | ls_to_dpad | PASS | Reported pass. |
| LAYER-001 | pure_layer | PASS | Reported pass. |
| LF4-001 | lf4_submode | PASS | Reported pass. |
| CSUP-001 | cstick_suppression | NOT_TESTED_USER_ACCEPTED_RISK | C-stick suppression was not independently hardware-tested in this run. User accepted risk for this behavior-preserving refactor; this is not hardware evidence. |
| DA-001 | direction_plus_a | PASS | Reported pass. |
| RS-001 | right_stick | PASS | Reported pass. |
| SYS-001 | system_buttons | PASS | Reported pass. |
| PROFREG-001 | profile_regression | PASS | Reported pass; no profile artifact regression reported. |
| NUNCHUK-001 | nunchuk_scope | NOT_TESTED | Nunchuk hardware behavior was not tested and is not hardware-validated by this result. |

## PASS rows

The following 17 rows were reported as PASS:

- BOOT-001
- PROFILE-001
- DEFAULT-001
- MODE-001
- XMOD-001
- YMOD-001
- TILT-001
- ZAIR-001
- UPB-001
- NULL-001
- DPA-001
- LAYER-001
- LF4-001
- DA-001
- RS-001
- SYS-001
- PROFREG-001

All reported non-nunchuk rows passed except `CSUP-001`, which was not tested
and is recorded as user-accepted risk.

## NOT_TESTED / waived rows

`CSUP-001` is recorded as `NOT_TESTED_USER_ACCEPTED_RISK`, not PASS.
C-stick suppression was not independently hardware-tested in this run. The user
indicated it can be assumed working for this behavior-preserving generated
constants refactor, but that is not hardware evidence and not full C-stick suppression hardware validation.

`NUNCHUK-001` is recorded as `NOT_TESTED`.

## Nunchuk status

Nunchuk remains not hardware-validated. This result must not be cited as
nunchuk hardware validation.

## Profile/artifact status

No profile artifact regression was reported for `PROFREG-001`. This result does
not approve profile artifact changes and does not validate profile schema
changes.

## Runtime behavior claim boundary

This result is for a generated constants firmware refactor only. It does not
validate runtime-loaded config, does not validate serial/device write behavior,
does not validate profile schema changes, does not validate nunchuk hardware
behavior, and does not prove new gameplay semantics.
This result is not runtime-loaded config and not serial/device write behavior.

## Merge gate interpretation

The generated constants refactor hardware gate is considered satisfied for merge
only under the documented user-accepted-risk interpretation for `CSUP-001`.

This result must not be cited as full C-stick suppression hardware validation.
This result is not nunchuk hardware validation and must not be cited as nunchuk hardware validation.

If future work changes LF4/C-stick suppression behavior directly, `CSUP-001`
must be tested rather than waived.

## Rollback status

No rollback was triggered by the reported result rows. If a future checker,
build, or hardware retest contradicts this result, stop merge preparation and
use the normal Git-history rollback path for the implementation branch.

## Follow-up requirements

- Preserve this result as branch-specific evidence for
  `glyph/gfw2-generated-constants-refactor`.
- Do not cite `CSUP-001` as tested hardware evidence.
- Do not cite nunchuk as hardware-validated.
- Test `CSUP-001` directly before any future LF4/C-stick suppression behavior
  change.
