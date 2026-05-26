# Glyph Ultimate Tilt3 Hardware Test Plan (2026-05-27)

## Scope

Manual hardware test plan for `glyph/gfw2-ultimate-tilt3-runtime`.

- No flashing automation is included.
- No push-to-device automation is included.
- Results must not claim PASS until measured on hardware.

## Expected Tilt3 Table

Formula:

```text
leftStickX = 128 + directions.x * 53
leftStickY = 128 + directions.y * 42
```

| Direction | Raw left-stick | Mini-screen offset |
| --- | --- | --- |
| 1 | `(75, 86)` | `(-53, -42)` |
| 2 | `(128, 86)` | `(0, -42)` |
| 3 | `(181, 86)` | `(53, -42)` |
| 4 | `(75, 128)` | `(-53, 0)` |
| 5 | `(128, 128)` | `(0, 0)` |
| 6 | `(181, 128)` | `(53, 0)` |
| 7 | `(75, 170)` | `(-53, 42)` |
| 8 | `(128, 170)` | `(0, 42)` |
| 9 | `(181, 170)` | `(53, 42)` |

## Manual Test Rows

| Area | Input | Directions | Expected result | Status |
| --- | --- | --- | --- | --- |
| Dedicated Tilt3 | Logical `LT3` | 1..9 | Tilt3 table above | NOT_TESTED |
| Tilt3 chord | `LT1+LT2` | 1..9 | Tilt3 table above | NOT_TESTED |
| Tilt1 preservation | `LT1` alone | 1..9 | Existing Tilt1 table `(187,87)`, `(128,87)`, `(69,87)`, `(187,128)`, `(128,128)`, `(69,128)`, `(187,169)`, `(128,169)`, `(69,169)` | NOT_TESTED |
| Tilt2 preservation | `LT2` alone | 1..9 | Existing Tilt2 table `(88,79)`, `(128,79)`, `(168,79)`, `(88,128)`, `(128,128)`, `(168,128)`, `(88,177)`, `(128,177)`, `(168,177)` | NOT_TESTED |
| Baseline preservation | No modifier | 1..9 | Existing baseline table `(28,28)`, `(128,28)`, `(228,28)`, `(28,128)`, `(128,128)`, `(228,128)`, `(28,228)`, `(128,228)`, `(228,228)` | NOT_TESTED |
| Other buttons smoke | A/B/X/Y/R/L/start/select/home/capture as applicable | N/A | Existing digital behavior unchanged | NOT_TESTED |
| C-stick/right-stick smoke | C-left/C-right/C-down/C-up | Cardinal and diagonal smoke | Existing right-stick behavior unchanged | NOT_TESTED |
| Triggers smoke | L/R trigger inputs | N/A | Existing trigger behavior unchanged | NOT_TESTED |
| SOCD/remap smoke | Existing SOCD pairs and remapped LT inputs | Representative chords | Existing SOCD/remap behavior unchanged; Tilt3 uses post-remap logical `inputs.lt3` only | NOT_TESTED |
| Nunchuk smoke | Nunchuk connected and disconnected | Representative left-stick states | Connected nunchuk remains authoritative over left-stick output | NOT_TESTED_UNAVAILABLE if no hardware |

## RF5 Historical Ambiguity Note

Earlier Tilt1/Tilt2 identification work rejected `BTN_RF5` for the uploaded MVP Tilt1/Tilt2 target. Tilt3 in this branch does not use raw RF physical checks. Dedicated Tilt3 is logical `inputs.lt3` through the existing post-remap path only.

## Acceptance Notes

- Hardware acceptance requires a Tilt3-specific result file or equivalent user-provided measurements.
- This plan does not authorize flashing automation.
- This plan does not add or imply push-to-device workflow support.
