# Glyph Ultimate LT3 and D-pad Fix Hardware Result - 2026-05-27

## Scope

- Hardware result after repaired active profile artifact was applied through serial config tool.
- No runtime/source/configurator behavior change in this result branch.
- No firmware flashing automation.
- No push-to-device firmware automation.

## Application Method

- Method: `SERIAL_CONFIG_TOOL_WRITE`.
- Applied artifact: `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`.

## Final User Confirmation

- "confirmed working"

## Hardware Result Table

| Check | Result | Notes |
| --- | --- | --- |
| Standalone physical LT3 directions 1..9 | PASS_TILT3_TABLE_VERIFIED | User-confirmed after repaired artifact apply via serial config tool write path. |
| LT1+LT2 directions 1..9 | PASS_TILT3_TABLE_VERIFIED | User-confirmed preserved behavior. |
| LT1 alone directions 1..9 | PASS_TILT1_TABLE_VERIFIED | User-confirmed preserved behavior. |
| LT2 alone directions 1..9 | PASS_TILT2_TABLE_VERIFIED | User-confirmed preserved behavior. |
| LT3 mixed with LT1/LT2 | PASS_EXPECTED_TILT3_PRIORITY | User-confirmed all Tilt modifier combinations work with Tilt3 priority. |
| Right stick orthogonal to Tilt behavior | PASS_SMOKE_USER_REPORTED | User-confirmed orthogonality. |
| D-pad orthogonal to Tilt behavior | PASS_SMOKE_USER_REPORTED | User-confirmed orthogonality. |
| D-pad Up | PASS_PROFILE_MAPPING_VERIFIED | User-confirmed repaired mapping behavior. |
| D-pad Down | PASS_PROFILE_MAPPING_VERIFIED | User-confirmed repaired mapping behavior. |
| D-pad Left | PASS_PROFILE_MAPPING_VERIFIED | User-confirmed repaired mapping behavior. |
| D-pad Right | PASS_PROFILE_MAPPING_VERIFIED | User-confirmed repaired mapping behavior. |
| Duplicate D-pad Left defect | PASS_FIXED | User-confirmed defect fixed in repaired mapping. |
| Nunchuk | NOT_TESTED_UNAVAILABLE | No nunchuk test evidence provided for this run. |

## Final Disposition

`PASS_LT3_TILT3_AND_DPAD_PROFILE_FIX`

## Caveats

- Nunchuk not tested.
- This result applies to the current active Ultimate MVP profile artifact path, not as a generic guarantee for future profiles.

## 2026-05-27 Amendment: Identity Baseline Transition

- This hardware result remains valid historical evidence for the serial-applied LT3/D-pad remap artifact path used at the time of test execution.
- The identity-baseline branch moves active development away from profile semantic remap preservation and toward runtime-owned behavior.
- Future identity-baseline behavior requires dedicated runtime implementation and new hardware testing before any equivalent LT3/D-pad behavioral claims are made.
