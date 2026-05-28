# Glyph Smash Box Modifiers Hardware Test Plan - 2026-05-27

## Scope

Manual hardware plan for identity-runtime Smash Box modifiers in native `MODE_ULTIMATE`.

- No flashing automation.
- No live serial write automation in this plan.
- Hardware pass claims require measured hardware results.

## Canonical Table Source

- `docs/calibration/glyph_smash_box_profile_output_tables_2026-05-27.md`

## Manual Test Matrix

| Area | Input condition | Directions | Expected result | Status |
| --- | --- | --- | --- | --- |
| Profile artifact baseline | Apply active Ultimate artifact with explicit self-activates identity | N/A | `MODE_ULTIMATE` remaps use `physicalButton == activates` | NOT_TESTED |
| RF1 game output | Press `RF1` in `MODE_ULTIMATE` runtime path | N/A | A output asserted | NOT_TESTED |
| RF5 game output | Press `RF5` in `MODE_ULTIMATE` runtime path | N/A | B output asserted | NOT_TESTED |
| LF4 duplicate B output | Press `LF4` in `MODE_ULTIMATE` runtime path | N/A | B output asserted; L trigger is not asserted from LF4 | NOT_TESTED |
| RF2 game output | Press `RF2` in `MODE_ULTIMATE` runtime path | N/A | X output asserted | NOT_TESTED |
| RF10 game output | Press `RF10` in `MODE_ULTIMATE` runtime path | N/A | Y output asserted | NOT_TESTED |
| RT1 game output | Press `RT1` in `MODE_ULTIMATE` runtime path | N/A | Z output asserted through source-confirmed Z carrier | NOT_TESTED |
| LT1 game output | Press `LT1` in `MODE_ULTIMATE` runtime path | N/A | L output asserted | NOT_TESTED |
| RF16 game output | Press `RF16` in `MODE_ULTIMATE` runtime path | N/A | R output asserted through source-confirmed R carrier; RF5 does not assert R | NOT_TESTED |
| LF2 Up direction | Press `LF2` in `MODE_ULTIMATE` runtime path | N/A | Up direction is visible to runtime table | NOT_TESTED |
| LF5 Down direction | Press `LF5` in `MODE_ULTIMATE` runtime path | N/A | Down direction is visible to runtime table | NOT_TESTED |
| LF3 Left direction | Press `LF3` in `MODE_ULTIMATE` runtime path | N/A | Left direction is visible to runtime table | NOT_TESTED |
| LF1 Right direction | Press `LF1` in `MODE_ULTIMATE` runtime path | N/A | Right direction is visible to runtime table | NOT_TESTED |
| RF6 forced-Up restore check | Press RF6 in `MODE_ULTIMATE` runtime path | N/A | RF6 forced-Up is restored and visible as runtime input | NOT_TESTED |
| Modifier visibility check | Press X1/X2/Y1/Y2/Tilt1/Tilt2 inputs | N/A | `LT5/LT4/LT2/LT3/RF3/RF4` are visible to runtime | NOT_TESTED |
| Default table | Mode off, no non-Mode modifiers | 1..9 | Default table exact outputs | NOT_TESTED |
| Mode default table | Mode on, no non-Mode modifiers | 1..9 | Mode default table exact outputs | NOT_TESTED |
| X family | X1, X2, MX1, MX2 (single-modifier only) | 1..9 each | Exact X/X+Mode table outputs | NOT_TESTED |
| Y family | Y1, Y2, MY1, MY2 (single-modifier only) | 1..9 each | Exact Y/Y+Mode table outputs | NOT_TESTED |
| Tilt family | Tilt1, Tilt2, Tilt3, MTilt1, MTilt2, MTilt3 (single-modifier only) | 1..9 each | Exact Tilt/Tilt+Mode table outputs | NOT_TESTED |
| RF6 forced-Up | `RF6` only | N/A | Effective direction `8` table output | NOT_TESTED |
| RF6 forced-Up with Down | `RF6 + Down` | N/A | Effective direction `8` table output (Down overridden) | NOT_TESTED |
| RF6 forced-Up with Left | `RF6 + Left` | N/A | Effective direction `7` table output | NOT_TESTED |
| RF6 forced-Up with Right | `RF6 + Right` | N/A | Effective direction `9` table output | NOT_TESTED |
| RF6 forced-Up with Down+Left | `RF6 + Down + Left` | N/A | Effective direction `7` table output | NOT_TESTED |
| RF6 forced-Up with Down+Right | `RF6 + Down + Right` | N/A | Effective direction `9` table output | NOT_TESTED |
| RF6 game Y guard | `RF6` only | N/A | Forced-Up behavior is present and game Y is not pressed | NOT_TESTED |
| RF6 Down override guard | `RF6 + LF5` | N/A | Up remains effective and Down is suppressed in runtime table direction | NOT_TESTED |
| Tilt3 chord source | `RF3 + RF4` | 1..9 | Effective Tilt3 table (or MTilt3 when Mode on) | NOT_TESTED |
| LT3 role | `LT3` only | 1..9 | Y2 table (or MY2 when Mode on), not standalone Tilt3 | NOT_TESTED |
| RF4 role guard | `RF4` only (no direction inputs) | N/A | Tilt2 neutral-direction behavior; RF4 does not act as Up direction source | NOT_TESTED |
| RF3 role guard | `RF3` only | N/A | Tilt1 behavior and does not assert R | NOT_TESTED |
| LT1 modifier guard | `LT1` only | N/A | Does not emit old LT1->modX behavior | NOT_TESTED |
| LT2 modY guard | `LT2` only | N/A | Y1 modifier behavior only and no LT2->modY output | NOT_TESTED |
| Multi-mod X+Y deactivation | Any X plus any Y | Representative + 1..9 spot checks | Falls back to Default/Mode default | NOT_TESTED |
| Multi-mod X/Y+Tilt deactivation | Any X or Y plus any effective Tilt | Representative + 1..9 spot checks | Falls back to Default/Mode default | NOT_TESTED |
| Mode with multiple modifiers | Mode + 2 or more effective non-mode modifiers | Representative + 1..9 spot checks | Mode default table | NOT_TESTED |
| Mode with exactly one modifier | Mode + exactly one effective non-mode modifier | 1..9 each modifier case | Matching `M*` table | NOT_TESTED |
| LS->DPad inactive baseline | `RF7` not pressed | N/A | LS buttons drive left stick only | NOT_TESTED |
| LS->DPad active core | `RF7` pressed | N/A | LS buttons drive D-pad directions and LS is centered | NOT_TESTED |
| LS->DPad digital suppression | `RF7` pressed | N/A | `leftStickLeft/Right/Down/Up` digital outputs suppressed | NOT_TESTED |
| LS->DPad center Mode off | `RF7` on, Mode off | N/A | Left stick forced to `(128,128)` | NOT_TESTED |
| LS->DPad center Mode on | `RF7` on, Mode on | N/A | Left stick forced to `(128,172)` | NOT_TESTED |
| LS->DPad D-pad directions | `RF7` on + LS direction buttons | Left/Right/Down/Up and diagonals | Corresponding D-pad direction outputs | NOT_TESTED |
| LS->DPad with RF6 | `RF7 + RF6` | N/A | D-pad Up asserted | NOT_TESTED |
| LS->DPad with RF6 and Down | `RF7 + RF6 + Down` | N/A | D-pad Up asserted, Down not asserted | NOT_TESTED |
| LS->DPad with RF6 and lateral | `RF7 + RF6 + Left/Right` | N/A | D-pad Up+Left / Up+Right if simultaneous D-pad outputs are supported | NOT_TESTED |
| No standalone D-pad outputs | Press `LF6`, `LF8`, old D-pad cluster placeholders, and RF7 inactive | N/A | No D-pad output unless nunchuk C or RF7 LS->DPad is active | NOT_TESTED |
| Empty button no-output smoke | Press `LF6/LF7/LF8/LT6/RF9/RF11/RF12/RF13/RF14/RF15/MB1/MB2/MB3` one at a time | N/A | No game output asserted | NOT_TESTED |
| Custom modifiers still work | Press `RF8/LT5/LT4/LT2/LT3/RF3/RF4` across representative directions | 1..9 spot checks | Mode, X1, X2, Y1, Y2, Tilt1, Tilt2, and RF3+RF4 Tilt3 all select expected tables | NOT_TESTED |
| Right-stick directions | Press `RT4/RT3/RT5/RT2` | Cardinal C-stick directions | C-Up/C-Left/C-Right/C-Down work as before | NOT_TESTED |
| Menu buttons | Press `MB4/MB5/MB6/MB7` | N/A | Capture/Home/Select-minus/Start-plus outputs asserted respectively | NOT_TESTED |
| Right-stick orthogonality | LS->DPad on/off with C-stick activity | Cardinal + diagonal smoke | Right-stick/C-stick behavior preserved | NOT_TESTED |
| Trigger smoke | LS->DPad and modifier combinations | N/A | LT1/RF16 trigger analog companions follow digital L/R carriers; LF4/RF5 remain B only | NOT_TESTED |
| Nunchuk override smoke | Nunchuk connected | Representative | Nunchuk overwrite behavior preserved | NOT_TESTED_UNAVAILABLE |

## Evidence Rules

- If nunchuk hardware is unavailable, keep `NOT_TESTED_UNAVAILABLE`.
- Do not claim standalone LT3 Tilt3 behavior for this identity runtime.
- Report physical/logical role evidence and measured outputs together in the hardware result.

## 2026-05-28 Note

- Current plan rows are satisfied by:
  - `docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md`
- Nunchuk remains unavailable/not tested.
