# Glyph Ultimate Preservation Hardware Handoff

Date: 2026-05-26

## What This Branch Adds

- `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`, a manual preservation matrix for future runtime changes.
- `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`, a result capture template only.
- `tools/check_glyph_ultimate_preservation_hardware_result.py`, a read-only checker that reports `status=NO_RESULT_FILE` before real hardware evidence exists.

## Important Boundaries

- No fake hardware results were added.
- No flashing automation was added.
- No runtime behavior was changed.
- No SOCD, remap, profile schema, or configurator behavior was changed.
- No hardware verification is claimed until a real result file exists.

## Next Hardware Gate

Before any new runtime patch is accepted, a human should complete the preservation result file from the template and use one of the allowed final dispositions: `PASS`, `FAIL_ROLLBACK`, `BLOCKED_NOT_TESTED`, or `NEEDS_FIRMWARE_FIX`.
