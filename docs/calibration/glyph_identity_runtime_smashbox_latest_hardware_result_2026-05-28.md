# Glyph Identity Runtime Smash Box Latest Hardware Result - 2026-05-28

## Scope

- Hardware result for current `glyph/gfw2-lt1-z-airdodge-l-on-lt3` branch after commit `68474ccbb818ff23350908ccfcb8f59ec6207d4e`.
- No runtime/source/configurator behavior change in this result commit.
- No firmware flashing automation.
- No push-to-device firmware automation.
- Profile was not re-pushed for this run because the existing explicit self-activated identity profile stayed resident across firmware updates.

## Tested Firmware/Profile State

- Firmware branch: `glyph/gfw2-lt1-z-airdodge-l-on-lt3`
- Firmware commit: `68474ccbb818ff23350908ccfcb8f59ec6207d4e`
- Profile path: explicit self-activated identity artifact:
  - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- Profile application status:
  - not re-pushed during this run
  - previously resident on device
  - still compatible with the tested firmware

## User Confirmation

"Everything works as expected (I have not been rebuilding the profile, as that stays across fw updates)."

## Hardware Result Table

| Check | Result | Notes |
| --- | --- | --- |
| Explicit self-activated identity profile compatibility | PASS_USER_REPORTED | Profile stayed resident across firmware updates. |
| Latest table-value update | PASS_USER_REPORTED | Covers Mode default update; MX1/MX2 update; MY1 update; MTilt1/MTilt2/MTilt3 update; Tilt1 y offset update. |
| Default table | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| X1/X2 | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Y1/MY1 | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Tilt1/Tilt2/Tilt3 | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Mode-prefixed tilt tables | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Y2/MY2 scratched | PASS_USER_REPORTED | User-reported current runtime behavior works as expected for the scratched/inactive runtime paths. |
| Y1+Tilt1 special composite | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Mode+Y1+Tilt1 special composite | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RF9 null modifier | PASS_USER_REPORTED | Final analog left stick forced to `(128,128)`; does not suppress other game outputs. |
| LT1 Z-airdodge low-magnitude override | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RF11 Z-airdodge alias | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| LT3=L | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RT1=Z | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RF16=R | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| LT6 hard Down+A | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RF12 hard Up+A | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RF15 hard Up+A alias | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RF6 forced-Up | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| RT4=C-right / RT5=C-up swap | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| LS->DPad | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Normal game buttons | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Right-stick/C-stick | PASS_USER_REPORTED | User-reported current runtime behavior works as expected. |
| Empty/no-output buttons | PASS_USER_REPORTED | Current docs list empty/no-output button smoke coverage; user-reported current runtime behavior works as expected. |
| Nunchuk | NOT_TESTED_UNAVAILABLE | No explicit nunchuk test evidence provided for this run. |

## Final Disposition

`PASS_IDENTITY_RUNTIME_SMASHBOX_LATEST_PROFILE`

## Caveats

- Nunchuk not tested.
- Result applies to current hardcoded runtime firmware plus explicit self-activated identity profile.
- Future modifier value changes require new firmware build until config-driven modifier tables are implemented.
- Profile was not re-pushed in this run; this is intentionally recorded as resident-profile compatibility, not as a fresh serial-write validation.

## LT1/LT4/LT5 Relocation Hardware Result

- Date: `2026-05-28`
- User confirmation quote: "works, it's time to merge"
- Result: `PASS_USER_REPORTED`

| Row | Result |
| --- | --- |
| LT5 Z-airdodge primary | PASS_USER_REPORTED |
| RF11 Z-airdodge alias | PASS_USER_REPORTED |
| LT4 X1/MX1 | PASS_USER_REPORTED |
| LT1 X2/MX2 | PASS_USER_REPORTED |
| stale LT1 Z-airdodge removed | PASS_USER_REPORTED |
| stale LT5 X1 removed | PASS_USER_REPORTED |
| stale LT4 X2 removed | PASS_USER_REPORTED |
| prior branch behavior preserved | PASS_USER_REPORTED |
| nunchuk | NOT_TESTED_UNAVAILABLE |

- Final disposition remains: `PASS_IDENTITY_RUNTIME_SMASHBOX_LATEST_PROFILE`

## 2026-06-01 Amendment: LF7/LF8 Layer-Direction Behavior

- The PASS result in this file predates LF7/LF8 layer-direction runtime behavior (`LF8=layer-left`, `LF7=layer-right`, layered `RF2/RF3/RF4` behavior).
- This file does not validate the new LF7/LF8 layer-direction behavior.
- A new hardware validation run is required before claiming PASS for the LF7/LF8 layer-direction runtime update.
- The previous LF7/LF8 layer amendment also predates the RF3 layer normal-x modifier addition and RF4-over-RF3 layered precedence update.
- RF3 layer normal-x behavior and RF4 layered precedence require a fresh hardware validation run before any PASS claim for this revision.
- The previous LF7/LF8 layer amendment also predates the LF4 sub-mode RF2/RF3 interchange (`LF4 sub-mode: RF2 => X, RF3 => forced Up`) and LF4+LT2 activation path.
- The previous LF7/LF8 layer amendment also predates LF4-held LT2/Y1 suppression (`LF4 + LT2` no longer activates Y1).
- LF4 sub-mode RF2/RF3 interchange plus LF4+LT2 Y1 suppression require fresh hardware validation before any PASS claim for this revision.
- The previous LF7/LF8 layer amendment also predates RF13 LS->DPad source migration, RF7 hard Up+B behavior, and LF4-submode RF2 suppression when any C-stick button is held.
- RF13 LS->DPad migration, RF7 hard Up+B behavior, and LF4-submode RF2 C-stick suppression require fresh hardware validation before any PASS claim for this revision.

## LF7/LF8/LF4 Layer Behavior Hardware Result

- Date: `2026-05-28`
- User confirmation quote: "all works."
- Result: `PASS_USER_REPORTED`
- This amendment supersedes the pending-validation note above for this behavior set.

| Row | Result |
| --- | --- |
| LF8 layer-left | PASS_USER_REPORTED |
| LF7 layer-right | PASS_USER_REPORTED |
| Pure layer RF2 forced-Up | PASS_USER_REPORTED |
| Pure layer RF3 B + normal-x | PASS_USER_REPORTED |
| Layer RF4 flipper | PASS_USER_REPORTED |
| RF4 flipper precedence over RF3 normal-x | PASS_USER_REPORTED |
| LF4 sub-mode | PASS_USER_REPORTED |
| LF4+LT2 Y1 suppression | PASS_USER_REPORTED |
| LF4 sub-mode RF2=X | PASS_USER_REPORTED |
| LF4 sub-mode RF3=forced-Up | PASS_USER_REPORTED |
| RF2 suppressed by C-stick in all LF4 sub-mode cases | PASS_USER_REPORTED |
| RF13 LS->DPad | PASS_USER_REPORTED |
| RF7 hard Up+B | PASS_USER_REPORTED |
| RF13+RF7 interaction | PASS_USER_REPORTED |
| RF9 null priority preserved | PASS_USER_REPORTED |
| LT5/RF11 Z-airdodge preserved | PASS_USER_REPORTED |
| existing latest table/modifier behavior preserved | PASS_USER_REPORTED |
| explicit self-activated identity profile compatibility | PASS_USER_REPORTED |
| nunchuk | NOT_TESTED_UNAVAILABLE |

- Final disposition remains: `PASS_IDENTITY_RUNTIME_SMASHBOX_LATEST_PROFILE`
