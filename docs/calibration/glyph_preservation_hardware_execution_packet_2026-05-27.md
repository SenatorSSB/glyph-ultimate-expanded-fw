# Glyph Preservation Hardware Execution Packet - 2026-05-27

Purpose: operator-facing packet for preparing a future manual preservation hardware run without recording results here.

## Scope

- manual hardware execution preparation only
- no flashing automation
- no push-to-device automation
- no firmware runtime change
- no result claim

## Required Inputs Before Execution

Tester must have all of the following before a run:

- exact branch/commit under test
- built artifact path and checksum, when relevant
- rollback firmware/profile readiness
- target Glyph hardware identity
- profile/config state under test
- existing preservation matrix path: `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
- existing result template path: `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- result checker path: `tools/check_glyph_ultimate_preservation_hardware_result.py`

## Execution Preparation Checklist

- run prehardware checks
- build with `.venv/bin/python -m platformio run -e glyph_mk6` if building a test artifact
- record artifact SHA-256 if a UF2 is produced
- perform manual UF2 flow only if explicitly approved by hardware owner
- record results in `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md` workflow/output path, not in this packet

## Preservation Categories To Test

- board boots
- device enumerates
- baseline buttons
- SOCD directions
- remap behavior
- C-stick/right-stick
- triggers
- nunchuk if available
- current Tilt1/Tilt2
- both-held behavior as observed-only unless explicitly promoted

## Blocking Rule

hardware preservation claims remain blocked until a filled preservation result file is reviewed.
This packet is a planning/execution-preparation control only and does not itself verify hardware behavior.
