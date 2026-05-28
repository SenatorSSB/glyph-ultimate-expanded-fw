# Glyph Identity Runtime Smash Box Hardware Result - 2026-05-28

## Scope

- Hardware result after flashing identity-runtime Smash Box firmware and applying explicit self-activated identity profile.
- No runtime/source/configurator behavior change in this result branch.
- No firmware flashing automation.
- No push-to-device firmware automation.

## Application Method

- Firmware build: current `configurator` with identity-runtime Smash Box implementation.
- Profile: explicit self-activated identity artifact:
  - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- Config application path:
  - serial config tool / active config write path (`CMD_SET_CONFIG` -> `Persistence::SaveConfig`) as documented in current workflow docs.

## User Confirmation

- "The firmware+profile acted as designed. All angles, functions, combinations."

## Hardware Result Table

| Check | Result | Notes |
| --- | --- | --- |
| Explicit self-activated identity profile applied | PASS_USER_REPORTED | Applied profile artifact path validated by user hardware confirmation. |
| Normal game buttons | PASS_USER_REPORTED | `RF1=A`, `RF5=B`, `LF4=B`, `RF2=X`, `RF10=Y`, `RT1=Z`, `LT1=L`, `RF16=R`. |
| Left-stick directions | PASS_USER_REPORTED | `LF3=Left`, `LF1=Right`, `LF2=Up`, `LF5=Down`. |
| RF6 forced-Up | PASS_USER_REPORTED | `RF6` alone -> Up; `RF6+Down` -> Up; diagonal forced-Up combinations covered by all-combinations confirmation. |
| Custom modifiers | PASS_USER_REPORTED | `RF8=Mode`, `LT5=X1`, `LT4=X2`, `LT2=Y1`, `LT3=Y2`, `RF3=Tilt1`, `RF4=Tilt2`, `RF3+RF4=Tilt3`. |
| All modifier tables / angles | PASS_USER_REPORTED | User reported all configured angles/tables behaved as designed. |
| Mode-prefixed tables | PASS_USER_REPORTED | User reported combinations and functions behaved as designed. |
| Multi-modifier composition/deactivation policy | PASS_USER_REPORTED | User reported combinations behaved as designed. |
| LS->DPad | PASS_USER_REPORTED | User-reported PASS within all-functions/all-combinations confirmation. |
| Right-stick/C-stick | PASS_USER_REPORTED | User-reported PASS within all-functions confirmation. |
| Empty/no-output buttons | PASS_USER_REPORTED | Covered by user-reported all-functions confirmation. |
| Nunchuk | NOT_TESTED_UNAVAILABLE | No explicit nunchuk test evidence provided for this run. |

## Final Disposition

`PASS_IDENTITY_RUNTIME_SMASHBOX_PROFILE`

## Caveats

- Nunchuk not tested.
- Result applies to the current identity-runtime firmware plus explicit self-activated identity profile path.
- Future modifier value changes require new firmware build until config-driven modifier tables are implemented.

## 2026-05-28 Direction-Plus-A Amendment

- Direction-plus-A behavior changed after this hardware result to hard final direction+A overrides (`LT6=Down+A`, `RF12=Up+A`).
- New hard override behavior requires a dedicated hardware validation pass before claiming hardware pass for those rows.

## 2026-05-28 LT1/LT3 Reassignment Amendment

- This PASS result predates the LT3/L reassignment, Y2/MY2 runtime scratch, and LT1 Z-airdodge low-magnitude override changes.
- This PASS result therefore does not validate:
  - `LT3 -> L`,
  - `LT1 -> Z` plus low-magnitude table override,
  - unreachable/scratched `Y2/MY2` runtime paths.
- A new hardware validation run is required before claiming PASS for these reassigned rows.

## 2026-05-28 Pre-Hardware Tuning Amendment

- This PASS result predates additional runtime tuning in this branch:
  - Tilt1 non-Mode y-offset change to 81 from center (`47/128/209`),
  - `RF15` hard Up+A alias behavior matching `RF12`,
  - `Y1+Tilt1` special composite tables (Mode and non-Mode),
  - `RT4/RT5` C-stick right/up swap.
- These rows require new hardware validation before claiming PASS for the updated behavior.

## 2026-05-28 Latest Table/RF9 Amendment

- This PASS result also predates the latest Smash Box table-value conversion update in this branch:
  - Mode default table update (`Mode 5 = (128,169)`, `Mode 2 = (128,87)`),
  - MX1/MX2 update,
  - MY1 update,
  - MTilt1/MTilt2/MTilt3 update,
  - Mode Y1+Tilt1 composite update (`179/169/77` y-values).
- This PASS result predates RF9 null-modifier runtime behavior:
  - RF9 final analog left-stick override to `(128,128)`,
  - RF9 exclusion from modifier-count composition,
  - RF9 non-ownership of game buttons/D-pad/right-stick outputs.
- New hardware validation is required before claiming PASS for these updated table rows and RF9 rows.

## 2026-05-28 RF11 Z-Airdodge Alias Amendment

- This PASS result predates the RF11 runtime alias to LT1 Z-airdodge low-magnitude behavior.
- This PASS result therefore does not validate:
  - `RF11 -> Z` shared carrier behavior,
  - RF11 low-magnitude directional override parity with LT1,
  - RF11 interactions with RF9 and LS->DPad rows.
- New hardware validation is required before claiming PASS for RF11 alias rows.
