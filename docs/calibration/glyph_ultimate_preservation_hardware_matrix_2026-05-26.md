# Glyph Ultimate Preservation Hardware Matrix (2026-05-26)

Scope: manual hardware preservation checklist for native Ultimate mode before any future runtime changes. This document defines protocol only. It does not claim execution, does not add hardware evidence, and does not change runtime/configurator/source behavior.

Source discipline:
- Source-confirmed behavior should be cited from repo source/docs.
- Hardware-observed behavior must come from a real filled result file.
- Unknown behavior must be recorded as unknown/blocked/not tested.

Reference sources used for matrix design:
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
- `docs/calibration/glyph_full_capability_inventory_2026-05-26.md`
- `src/modes/Ultimate.cpp`
- `src/core/InputMode.cpp`
- `src/core/socd.cpp`
- `src/core/ControllerMode.cpp`
- `config/glyph/glyph_mk6/include/button_positions.hpp`
- `config/glyph/glyph_mk6/include/matrix_definition.hpp`

## 1. Test Identity And Setup

Record all fields:
- branch tested
- commit SHA tested
- firmware artifact path
- firmware artifact hash (SHA-256)
- profile/config used
- controller model/hardware identifier
- flash method used (manual only)
- observation method used:
  - Glyph mini-screen offsets
  - Nintendo Switch controller visualization
  - Ultimate Training Mode behavior (if used)

## 2. Baseline No-Modifier Checks

Manual checklist:
- no-modifier left-stick directions `1..9`
- basic movement sanity
- no stuck inputs

Record observed behavior only (no inferred expectations beyond source-confirmed baseline paths).

## 3. Existing Tilt/Tilt2 Preservation

Manual checklist:
- Tilt1 preservation (`lt1`) as spot-check or full 9-direction table
- Tilt2 preservation (`lt2`) as spot-check or full 9-direction table
- both-held Tilt1+Tilt2 existing combined behavior

Required note:
- Both-held Tilt1+Tilt2 exact behavior is recorded as observed existing behavior, not a new guaranteed table contract.

## 4. C-Stick/Right-Stick Preservation

Manual checklist:
- neutral
- cardinals (left/right/up/down)
- diagonals when practical
- D-pad/right-stick interaction checks for source paths where D-pad layer can neutralize right stick (`src/modes/Ultimate.cpp`)

Constraint:
- Do not make exact gameplay semantic claims; only record controller input/output observations.

## 5. Trigger Preservation

Manual checklist:
- L/R/Z or profile-relevant trigger buttons
- analog trigger observation if available
- digital trigger behavior if visible

Record whether trigger behavior matches prior observed baseline for this profile/hardware.

## 6. SOCD/Opposite Direction Behavior

Manual checklist:
- left+right
- up+down
- left+right with Tilt1
- left+right with Tilt2
- up+down with Tilt1
- up+down with Tilt2

Record observed outcomes only. Do not infer desired outcomes beyond configured/source-confirmed SOCD handling.

## 7. RF5 Physical Identity / Negative Check

RF5 location for future tests (user-provided transcription for this workstream):
- center-right / RF cluster, far-right upper button = `RF5`

Manual checklist:
- RF5 alone with neutral and selected directions
- RF5 + Tilt1
- RF5 + Tilt2
- RF5 + Tilt1+Tilt2 (if safe/practical)

Conservative expectation language:
- RF5-specific behavior is observed and recorded.
- RF5 should not be classified as Tilt1/Tilt2 unless the loaded profile maps it that way.
- This is a new preservation check; do not overwrite/retcon the previous ambiguous RF5 negative result.

## 8. Profile Preservation / Readback

Manual checklist:
- profile list still appears as expected
- default profile behavior remains as expected
- Ultimate profile selected/default as applicable
- if configurator readback is possible, record whether profile data matches expected profile/config

Constraint:
- No push-to-device automation.

## 9. Optional Nunchuk

This section is explicitly optional.
- If nunchuk is unavailable: mark `NOT_TESTED`.
- If tested: record whether nunchuk behavior remains source-consistent for the tested setup.

## 10. Basic Button Regression

Manual checklist:
- basic mapped buttons (A/B/jump/shield/grab equivalents as mapped in current profile)
- menu buttons if relevant
- no stuck state
- no crash/reboot during test flow

## 11. Result Disposition Definitions

Allowed final dispositions:
- `PASS`
- `FAIL_ROLLBACK`
- `BLOCKED_NOT_TESTED`
- `NEEDS_FIRMWARE_FIX`

No preservation hardware pass claim is allowed until a real filled result file exists at:
- `docs/calibration/glyph_ultimate_preservation_hardware_result.md`
