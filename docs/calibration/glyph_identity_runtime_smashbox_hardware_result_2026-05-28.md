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
