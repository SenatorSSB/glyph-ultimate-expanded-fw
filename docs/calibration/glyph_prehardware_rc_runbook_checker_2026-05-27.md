# Glyph Prehardware RC Runbook Checker - 2026-05-27

Purpose: define the structure-only validation contract for `tools/check_glyph_prehardware_rc_runbook.py`.

## What It Validates

- required scope/boundary phrases are present in `docs/calibration/glyph_prehardware_rc_runbook_2026-05-27.md`
- required build/artifact/reference anchors are present
- required preservation-boundary phrases are present
- required referenced files for template/matrix/checkers exist
- checker output text keeps PASS interpretation constrained to structure/presence only

## What It Intentionally Does Not Validate

- it does not build firmware
- it does not flash hardware
- it does not push to device
- it does not approve hardware testing
- it does not claim preservation verification
- it does not convert observed-only both-held behavior into a contract
- it does not resolve RF5 historical ambiguity
- it does not approve runtime behavior changes

## Interpretation Rule

A PASS from this checker means structure/presence constraints passed only.
A PASS from this checker does not imply hardware readiness, firmware safety, flashing approval, or preservation verification.
