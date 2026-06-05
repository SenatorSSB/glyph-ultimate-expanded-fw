# Glyph GFW3 Runtime Remap Hardware Test Plan - 2026-06-04

## Scope

Manual hardware execution packet for the GFW3 Glyph / Smash Box runtime remap in
native `MODE_ULTIMATE`.

- This is not a hardware result.
- Hardware validation is not claimed by this plan.
- No runtime-loaded config is implemented or tested here.
- No WebSerial/device write workflow is implemented or tested here.
- Do not merge `glyph/gfw3-runtime-remap-rework` into `configurator` until the
  user hardware test passes and a separate hardware result document is recorded.

## Source Authority

- Behavior spec:
  `docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md`
- Firmware runtime source:
  `src/modes/Ultimate.cpp`
- Mirrored evaluator/cases:
  `tools/check_glyph_identity_runtime_behavior_evaluator.py`
  `tools/check_glyph_identity_runtime_behavior_cases.py`

## Execution Rules

- Record measured controller output, not inferred behavior.
- Keep all rows `NOT_EXECUTED` until the user performs hardware testing.
- If nunchuk hardware is unavailable, keep the nunchuk row unavailable/not
  tested and do not claim nunchuk hardware coverage.
- Record the eventual result in a separate result doc/fixture before any final
  merge to `configurator`.

## Manual Test Matrix

| Row ID | Area | Input condition | Directions | Expected result | Status |
| --- | --- | --- | --- | --- | --- |
| boot_profile_sanity | Boot/profile sanity | Boot GFW3 firmware and select Ultimate runtime profile | N/A | Device enumerates normally; Ultimate profile is active; no device write path is involved | NOT_EXECUTED |
| base_rf6_z_airdodge | RF6 Z-airdodge | `RF6` alone and with LS directions | 1..9 | Z asserted; left stick uses existing low-magnitude Z-airdodge raw table | NOT_EXECUTED |
| base_rf5_up_a | RF5 forced Up+A | `RF5` alone and with Down held | N/A | A asserted; effective Up wins over Down | NOT_EXECUTED |
| scratched_rf11 | Scratched RF11 | `RF11` alone and with directions | 1..9 | RF11 no longer asserts Z-airdodge alias behavior | NOT_EXECUTED |
| scratched_rf12 | Scratched RF12 | `RF12` alone and with directions | 1..9 | RF12 no longer asserts hard Up+A alias behavior | NOT_EXECUTED |
| scratched_rf15 | Scratched RF15 | `RF15` alone and with directions | 1..9 | RF15 no longer asserts hard Up+A alias behavior | NOT_EXECUTED |
| base_rf2_b | RF2 base role | `RF2` only | N/A | B asserted; no forced Up from RF2 in base behavior | NOT_EXECUTED |
| base_rf3_x | RF3 base role | `RF3` only | N/A | X asserted; RF3 does not select Tilt1 in base behavior | NOT_EXECUTED |
| base_rf4_tilt1 | RF4 base role | `RF4` plus LS directions | 1..9 | Left stick uses Tilt1 table | NOT_EXECUTED |
| rf4_cstick_suppresses_base_tilt1 | RF4 C-stick suppression | `RF4 + any RT2/RT3/RT4/RT5` | Representative | RF4 base Tilt1 modifier behavior is suppressed while normal C-stick output remains active | NOT_EXECUTED |
| base_rt1_tilt2 | RT1 base role | `RT1` plus LS directions | 1..9 | Left stick uses Tilt2 table; RT1 does not assert old Z carrier role | NOT_EXECUTED |
| rf3_rf4_no_tilt3 | RF3+RF4 fusion scratched | `RF3 + RF4` plus LS directions | 1..9 | X remains from RF3 and RF4 uses Tilt1 behavior; Tilt3 is not selected | NOT_EXECUTED |
| rt1_rf4_custom_table | RT1+RF4 custom table | `RT1 + RF4` plus LS directions | 1,2,3,4,6,7,8,9 | Left stick raw outputs are 1=(69,78), 2=(128,78), 3=(187,78), 4=(69,128), 6=(187,128), 7=(72,172), 8=(128,179), 9=(184,172); neutral 5 is unchanged/unset | NOT_EXECUTED |
| rt1_rf4_cstick_custom_preserved | RT1+RF4 C-stick exception | `RT1 + RF4 + any RT2/RT3/RT4/RT5` | Representative | RT1+RF4 custom table remains active and is not suppressed by C-stick | NOT_EXECUTED |
| rf4_rf2_minus41 | RF4+RF2 -41 interaction | `RF4 + RF2` plus LS directions | 1..9 | RF4 keeps Tilt1 behavior except X offset changes to -41 | NOT_EXECUTED |
| rf4_rf2_cstick_suppresses_minus41 | RF4+RF2 C-stick suppression | `RF4 + RF2 + any RT2/RT3/RT4/RT5` | Representative | RF4+RF2 Tilt1-minus-41 modifier behavior is suppressed while RF2 still asserts B | NOT_EXECUTED |
| rf9_null_both_sticks | RF9 null both sticks | `RF9` with LS and C-stick activity | Representative | Left stick and right stick are both centered/nullified; RF9 does not assert extra game output | NOT_EXECUTED |
| rf9_rf4_null_disabled | RF9+RF4 exception | `RF9 + RF4` with no C-stick button held | 1..9 | RF9 performs no left-stick null, no right-stick null, and does not replace RF4 modifier behavior | NOT_EXECUTED |
| rf9_rf4_cstick_reenables_null | RF9+RF4 C-stick priority | `RF9 + RF4 + any RT2/RT3/RT4/RT5` | Representative | C-stick suppresses RF4 behavior, so RF9 null is active again and centers both sticks | NOT_EXECUTED |
| rf9_rf3_suppresses_x | RF9+RF3 X suppression | `RF9 + RF3` with no C-stick button held | N/A | RF9 suppresses base RF3 X | NOT_EXECUTED |
| rf9_rf3_cstick_restores_x | RF9+RF3 X restoration | `RF9 + RF3 + any RT2/RT3/RT4/RT5` | Representative | C-stick restores base RF3 X; RF9 analog null behavior remains late | NOT_EXECUTED |
| lt1_l | LT physical move cycle | `LT1` only | N/A | L asserted | NOT_EXECUTED |
| lt3_l_r | LT physical move cycle | `LT3` only | N/A | L and R asserted | NOT_EXECUTED |
| lt4_x2_mx2 | LT physical move cycle | `LT4` with/without Mode | 1..9 | X2 table selected, or MX2 when Mode is held | NOT_EXECUTED |
| lt5_x1_mx1 | LT physical move cycle | `LT5` with/without Mode | 1..9 | X1 table selected, or MX1 when Mode is held; no LT5 Z-airdodge behavior | NOT_EXECUTED |
| lt2_base_y1_my1 | LT2 base role | `LT2` with no LT2 sublayer button | 1..9 | Y1 table selected, or MY1 when Mode is held | NOT_EXECUTED |
| lt2_rf4_flipper | LT2 sublayer | `LT2 + RF4` | 1..9 | RF4 selects -41 flipper table; LT2 Y1/MY1 is suppressed | NOT_EXECUTED |
| lt2_rf4_cstick_suppresses_flipper | LT2 RF4 C-stick suppression | `LT2 + RF4 + any RT2/RT3/RT4/RT5` | Representative | C-stick suppresses LT2+RF4 flipper behavior | NOT_EXECUTED |
| lt2_rf3_b_normal_x | LT2 sublayer | `LT2 + RF3` | 1..9 | B asserted and +41 normal-x table selected; RF3 is not X | NOT_EXECUTED |
| lt2_rf3_rf4_b_flipper | LT2 sublayer priority | `LT2 + RF3 + RF4` | 1..9 | B asserted and RF4 -41 flipper wins over RF3 normal-x | NOT_EXECUTED |
| lt2_rf3_rf4_cstick_fallback_rf3 | LT2 RF3/RF4 C-stick priority | `LT2 + RF3 + RF4 + any RT2/RT3/RT4/RT5` | Representative | C-stick suppresses RF4 flipper, so behavior falls back to LT2+RF3 B plus normal-x | NOT_EXECUTED |
| lt2_rf2_forced_up | LT2 sublayer | `LT2 + RF2` | N/A | Forced Up active; RF2 is not B | NOT_EXECUTED |
| lt2_rf1_x_cstick_suppression | LT2 C-stick suppression | `LT2 + RF1` with and without any `RT2/RT3/RT4/RT5` | N/A | RF1 asserts X only when no C-stick button is pressed; C-stick behavior remains normal | NOT_EXECUTED |
| lf4_rf4_tilt1 | LF4 submode | `LF4 + RF4` | 1..9 | LF4 asserts B and RF4 selects Tilt1 | NOT_EXECUTED |
| lf4_rf4_cstick_suppresses_tilt1 | LF4 RF4 C-stick suppression | `LF4 + RF4 + any RT2/RT3/RT4/RT5` | Representative | C-stick suppresses LF4+RF4 Tilt1 while LF4 still asserts B | NOT_EXECUTED |
| lf4_rf3_forced_up | LF4 submode | `LF4 + RF3` | N/A | LF4 asserts B and RF3 contributes forced Up | NOT_EXECUTED |
| lf4_rf2_x | LF4 submode | `LF4 + RF2` | N/A | LF4 asserts B and RF2 asserts X | NOT_EXECUTED |
| lf4_rf2_rf4_deactivates_rf4 | LF4 RF2/RF4 priority | `LF4 + RF2 + RF4` | 1..9 | RF2 deactivates RF4 modifier behavior while X remains asserted | NOT_EXECUTED |
| lf4_rf2_cstick_suppression | LF4 C-stick suppression | `LF4 + RF2 + RF4 + any RT2/RT3/RT4/RT5` | 1..9 plus C-stick smoke | RF2 X is suppressed, but RF2 still deactivates RF4; C-stick behavior remains normal | NOT_EXECUTED |
| lf4_overrides_lt2 | LF4 over LT2 | `LF4 + LT2` with RF2/RF3/RF4 spot checks | Representative | LF4 submode behavior wins over LT2 sublayer behavior | NOT_EXECUTED |
| rf3_rt5_left_special | RF3 vertical C-stick special | `RF3 + RT5 + resolved Left` | Left | Right stick raw output is (95,165) | NOT_EXECUTED |
| rf3_rt5_right_special | RF3 vertical C-stick special | `RF3 + RT5 + resolved Right` | Right | Right stick raw output is (161,165) | NOT_EXECUTED |
| rf3_rt2_left_special | RF3 vertical C-stick special | `RF3 + RT2 + resolved Left` | Left | Right stick raw output is (95,91) | NOT_EXECUTED |
| rf3_rt2_right_special | RF3 vertical C-stick special | `RF3 + RT2 + resolved Right` | Right | Right stick raw output is (161,91) | NOT_EXECUTED |
| rf3_vertical_no_horizontal_preserves_normal | RF3 vertical C-stick neutral horizontal | `RF3 + RT2/RT5` with no resolved left/right | Neutral horizontal | Normal C-stick vertical behavior is preserved | NOT_EXECUTED |
| rf3_horizontal_unaffected | RF3 C-stick horizontal | `RF3 + RT3/RT4` | Horizontal C-stick | Normal C-left/C-right behavior is preserved | NOT_EXECUTED |
| rf3_two_axis_cstick_preserved | RF3 two-axis C-stick preservation | `RF3 + RT2/RT5 + RT3/RT4` | Two-axis C-stick | Existing two-axis C-stick diagonal/ASDI behavior is preserved | NOT_EXECUTED |
| rf7_hard_up_b_unchanged | RF7 preservation | `RF7` alone and with left/right directions | Representative | Existing hard Up+B behavior remains unchanged | NOT_EXECUTED |
| rf13_ls_to_dpad_unchanged | RF13 preservation | `RF13` with LS direction buttons | Cardinal and diagonals | Existing LS-to-DPad behavior remains unchanged | NOT_EXECUTED |
| nunchuk_preserved_not_tested | Nunchuk caveat | Nunchuk connected, if available | Representative | Nunchuk behavior is preserved by source intent, but this GFW3 packet does not claim nunchuk hardware validation | NOT_EXECUTED_UNAVAILABLE |

## RT1+RF4 Raw Table

Only raw firmware coordinates are in scope.

| Direction | Raw coordinate |
| --- | --- |
| 1 | `(69,78)` |
| 2 | `(128,78)` |
| 3 | `(187,78)` |
| 4 | `(69,128)` |
| 5 | unchanged/unset |
| 6 | `(187,128)` |
| 7 | `(72,172)` |
| 8 | `(128,179)` |
| 9 | `(184,172)` |

## Merge Gate

`glyph/gfw3-runtime-remap-rework` is blocked from `configurator` until:

1. User hardware testing passes.
2. A separate hardware result document records the measured result.
3. The result doc repeats that nunchuk was either measured or explicitly left
   unavailable/not tested.
