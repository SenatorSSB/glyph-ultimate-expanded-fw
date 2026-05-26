# Glyph Ultimate Tilt Hardware Retest Result - 2026-05-27

## Scope

- current native Ultimate Tilt/Tilt2 behavior retest
- manual hardware evidence
- no runtime/source/configurator behavior change
- no firmware artifact committed
- no flashing automation
- no push-to-device automation

## Source Observation

User-provided observation source:
"Ran hardware checks. All results are the same as previously. All of them. All directions. Tilt1, Tilt2, Tilt1+Tilt2."

Interpreted retest meaning for this document:
- Tilt1 all directions 1..9 matched previous recorded hardware result.
- Tilt2 all directions 1..9 matched previous recorded hardware result.
- Tilt1+Tilt2 both-held all directions 1..9 matched previous recorded hardware result.

## Test Identity

| Field | Value |
| --- | --- |
| Branch tested | UNKNOWN_NOT_RECORDED |
| Commit SHA tested | UNKNOWN_NOT_RECORDED |
| Firmware artifact path | UNKNOWN_NOT_RECORDED |
| Artifact SHA-256 | UNKNOWN_NOT_RECORDED |
| Hardware identity | Glyph MK6 / exact unit identifier not separately recorded |
| Profile/config state | not separately recorded |

## Retest Result Table

| Slice | Directions | Result |
| --- | --- | --- |
| Tilt1 LT1 | 1..9 | PASS_MATCHED_PREVIOUS_RESULT |
| Tilt2 LT2 | 1..9 | PASS_MATCHED_PREVIOUS_RESULT |
| Both-held LT1+LT2 | 1..9 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR_MATCHED_PREVIOUS_RESULT |

## Previous Coordinate References

### Tilt1 Table Reference (from `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`)

| Direction | Raw `(x, y)` | Offset `(x, y)` |
| --- | --- | --- |
| 1 | `(187, 87)` | `(59, -41)` |
| 2 | `(128, 87)` | `(0, -41)` |
| 3 | `(69, 87)` | `(-59, -41)` |
| 4 | `(187, 128)` | `(59, 0)` |
| 5 | `(128, 128)` | `(0, 0)` |
| 6 | `(69, 128)` | `(-59, 0)` |
| 7 | `(187, 169)` | `(59, 41)` |
| 8 | `(128, 169)` | `(0, 41)` |
| 9 | `(69, 169)` | `(-59, 41)` |

### Tilt2 Table Reference (from `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`)

| Direction | Raw `(x, y)` | Offset `(x, y)` |
| --- | --- | --- |
| 1 | `(88, 79)` | `(-40, -49)` |
| 2 | `(128, 79)` | `(0, -49)` |
| 3 | `(168, 79)` | `(40, -49)` |
| 4 | `(88, 128)` | `(-40, 0)` |
| 5 | `(128, 128)` | `(0, 0)` |
| 6 | `(168, 128)` | `(40, 0)` |
| 7 | `(88, 177)` | `(-40, 49)` |
| 8 | `(128, 177)` | `(0, 49)` |
| 9 | `(168, 177)` | `(40, 49)` |

### Both-Held LT1+LT2 Observed Offset Reference (from `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`)

| Direction | Observed offset `(x, y)` |
| --- | --- |
| 1 | `(-35, -53)` |
| 2 | `(0, -53)` |
| 3 | `(35, -53)` |
| 4 | `(-41, 0)` |
| 5 | `(0, 0)` |
| 6 | `(41, 0)` |
| 7 | `(-35, 53)` |
| 8 | `(0, 53)` |
| 9 | `(35, 53)` |

Both-held reference remains observed existing combined behavior and is not promoted here to a production table contract.

## Caveats

- This retest confirms the current Tilt/Tilt2 slice only.
- It does not broaden preservation claims for C-stick/right-stick, triggers, SOCD, remap, profile preservation, or nunchuk unless separately observed.
- Both-held behavior remains observed-only/non-contractual.
- RF5 historical negative check remains NOT_TESTED_AMBIGUOUS unless RF5 was explicitly retested using the now-known RF5 location.

## Final Disposition

- For this retest document: PASS_TILT_RETEST
- Do not use this custom disposition in `docs/calibration/glyph_ultimate_preservation_hardware_result.md` unless the checker supports it.
