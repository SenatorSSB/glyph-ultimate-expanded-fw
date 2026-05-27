# Glyph Ultimate LT3 Standalone Hardware Result - 2026-05-27

## Scope

- Hardware result after serial/config active profile application.
- No runtime/source/configurator behavior change in this result doc.
- No firmware flashing automation.
- No push-to-device firmware automation.

## Application Method

- Method: `SERIAL_CONFIG_TOOL_WRITE` / active config write path.
- Applied artifact: `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`.

## Hardware Observations

| Check | Result | Notes |
| --- | --- | --- |
| Standalone physical LT3 directions 1..9 | PASS_TILT3_TABLE_VERIFIED | User reported standalone physical LT3 now acts as standalone Tilt3 modifier and works across directions. |
| LT1+LT2 directions 1..9 | PASS_TILT3_TABLE_VERIFIED | User reported LT1+LT2 remained correct across direction combinations. |
| LT1 alone directions 1..9 | PASS_TILT1_TABLE_VERIFIED | User-reported verification. |
| LT2 alone directions 1..9 | PASS_TILT2_TABLE_VERIFIED | User-reported verification. |
| All Tilt modifier button combinations | PASS_EXPECTED_TILT_PRIORITY | User reported combined modifier behavior remained expected. |
| Right stick orthogonal to Tilt3 | PASS_SMOKE_USER_REPORTED | User reported orthogonality as expected. |
| D-pad inputs orthogonal to Tilt3 | PASS_SMOKE_USER_REPORTED | User reported orthogonality as expected. |
| Physical LT3 no longer acts as previous LF4/trigger L digital role | PASS_SMOKE_USER_REPORTED | Inferred from standalone LT3 behavior report; no separate trigger-role probe details were provided in this result. |
| Nunchuk | NOT_TESTED_UNAVAILABLE | No nunchuk evidence provided for this run. |

## Final Disposition

`PASS_STANDALONE_LT3_AND_TILT3_COMBINATIONS`

## Caveats

- D-pad profile mapping defect remains open separately: two D-pad Left mappings were observed.
- This result validates Tilt behavior, not full profile layout correctness.

## 2026-05-27 Amendment: Repaired D-pad Profile Confirmation

- The repaired D-pad profile artifact was later applied and confirmed working on hardware.
- Final confirmation is recorded in:
  - `docs/calibration/glyph_ultimate_lt3_dpad_fix_hardware_result_2026-05-27.md`
