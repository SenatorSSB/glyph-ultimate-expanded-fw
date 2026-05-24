# Glyph Ultimate Tilt Hardware Result File Policy (2026-05-24)

## Scope

This policy defines how hardware test results must be recorded for the native Ultimate Tilt/Tilt2 runtime implementation.

## Result File Rules

- The template file is intentionally blank and must not be edited into a fake result.
- The template remains: `docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md`.
- The real result file, when available after manual testing, must be:
  - `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
- Hardware result evidence must be committed only after an actual human-controlled manual hardware test.

## Required Result Content

The real result file must include:

- tester, date, and hardware identifier
- branch name and commit SHA
- firmware artifact path and SHA-256 hash
- profile/config used during test
- smoke-test outcomes (including Tilt1/Tilt2 direction rows)
- rollback status
- final disposition

## Allowed Final Dispositions

- `PASS`
- `FAIL_ROLLBACK`
- `BLOCKED_NOT_FLASHED`
- `NEEDS_FIRMWARE_FIX`

## Non-Goals

- No flashing automation should be added by this policy.
- This policy does not authorize push-to-device automation.
