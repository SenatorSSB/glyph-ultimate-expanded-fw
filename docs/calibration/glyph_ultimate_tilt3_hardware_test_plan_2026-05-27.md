# Glyph Ultimate Tilt3 Hardware Test Plan (2026-05-27)

## Scope

Manual hardware test plan for `glyph/gfw2-ultimate-tilt3-runtime`.

- No flashing automation is included.
- No push-to-device automation is included.
- Results must not claim PASS until measured on hardware.
- This plan requires one recorded and verified application method before test execution.

## Application Methods

- `WEBAPP_IMPORT_UNSUPPORTED_FOR_LT3`
  - Closed-source webapp path observed as not verified for standalone LT3 in this workstream.
- `SERIAL_CONFIG_TOOL_WRITE`
  - Use source-backed serial configurator protocol write with verified readback.
- `FRESH_INSTALL_DEFAULT_RESTORE`
  - Use verified default-restore path when testing default-source edits.
- `OTHER_VERIFIED_CONFIGURATOR_PATH`
  - Use another configurator write path only when verified for active profile state.

Standalone LT3 hardware rows in this plan should run only after either:
- verified write + verified readback, or
- another verified profile-state confirmation path.

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
| Application path record | N/A | N/A | Record exactly one: `ARTIFACT_IMPORT` or `DEFAULT_RESTORE_FRESH_INSTALL` before test evidence | NOT_RECORDED |
| Standalone physical LT3 | Physical `BTN_LT3` (remapped to logical `BTN_LT3` in Ultimate MVP profile) | 1..9 | Tilt3 table above | NOT_TESTED |
| LT1+LT2 Tilt3 regression | `LT1+LT2` | 1..9 | Tilt3 table above | NOT_TESTED |
| D-pad Up physical mapping (post-fix profile) | D-pad Up physical binding | N/A | D-pad Up only (`BTN_RF8`) | NOT_TESTED |
| D-pad Down physical mapping (post-fix profile) | D-pad Down physical binding | N/A | D-pad Down only (`BTN_RF7`) | NOT_TESTED |
| D-pad Left physical mapping (post-fix profile) | D-pad Left physical binding | N/A | D-pad Left only (`BTN_LF8`) | NOT_TESTED |
| D-pad Right physical mapping (post-fix profile) | D-pad Right physical binding | N/A | D-pad Right only (`BTN_LF6`) | NOT_TESTED |
| D-pad duplicate-left guard (post-fix profile) | D-pad cluster smoke | N/A | No duplicate D-pad Left behavior | NOT_TESTED |
| Orthogonality regression (post-fix profile) | Tilt3 with D-pad and right-stick smoke | Representative smoke | Tilt3 remains orthogonal to D-pad/right-stick | NOT_TESTED |
| Tilt3 mixed input | `LT3+LT1` | 1..9 | Tilt3 table above | NOT_TESTED |
| Tilt3 mixed input | `LT3+LT2` | 1..9 | Tilt3 table above | NOT_TESTED |
| Tilt3 mixed input | `LT3+LT1+LT2` | 1..9 | Tilt3 table above | NOT_TESTED |
| Tilt3 chord D-pad side effect guard | `LT1+LT2` plus D-pad-observable buttons as needed | Representative smoke | `LT1+LT2` does not activate D-pad outputs by itself | NOT_TESTED |
| Tilt3 chord C-stick side effect guard | `LT1+LT2` plus C-left/C-right/C-down/C-up | Cardinal and diagonal smoke | `LT1+LT2` does not shut off or neutralize C-stick/right-stick unless another actual D-pad-layer condition applies | NOT_TESTED |
| Tilt3 chord prototype side effect guard | `LT1+LT2` plus C-stick direction smoke | Cardinal and diagonal smoke | No hidden C-stick/right-stick modification from the old `LT1` prototype block | NOT_TESTED |
| Dedicated Tilt3 prototype side effect guard | `LT3` plus C-stick direction smoke | Cardinal and diagonal smoke | No hidden C-stick/right-stick modification from old prototype blocks | NOT_TESTED |
| LT1 regression | `LT1` alone | 1..9 | Existing Tilt1 table `(187,87)`, `(128,87)`, `(69,87)`, `(187,128)`, `(128,128)`, `(69,128)`, `(187,169)`, `(128,169)`, `(69,169)` | NOT_TESTED |
| LT2 regression | `LT2` alone | 1..9 | Existing Tilt2 table `(88,79)`, `(128,79)`, `(168,79)`, `(88,128)`, `(128,128)`, `(168,128)`, `(88,177)`, `(128,177)`, `(168,177)` | NOT_TESTED |
| LT3 previous-role removal | Physical `BTN_LT3` press in Ultimate MVP profile | N/A | Does not activate previous logical `BTN_LF4` / `triggerLDigital` role | NOT_TESTED |
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
- If the tested layout still has no D-pad-observable buttons, keep D-pad side-effect rows as `NOT_TESTED_NO_DPAD_BUTTONS_IN_NORMAL_LAYOUT`.
- If nunchuk hardware is unavailable, keep nunchuk row as `NOT_TESTED_UNAVAILABLE`.
- This plan does not authorize flashing automation.
- This plan does not add or imply push-to-device workflow support.

## 2026-05-27 Note: Final Plan Row Satisfaction

- Current hardware plan rows for standalone LT3 and D-pad profile repair are satisfied by:
  - `docs/calibration/glyph_ultimate_lt3_dpad_fix_hardware_result_2026-05-27.md`
