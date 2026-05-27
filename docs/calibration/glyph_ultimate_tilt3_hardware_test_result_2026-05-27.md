# Glyph Ultimate Tilt3 Hardware Test Result - 2026-05-27

## Scope

- Manual hardware result for native Ultimate Tilt3 runtime.
- Current test layout does not include an actionable dedicated Tilt3 button.
- Current test layout does not expose D-pad buttons.
- No runtime/source/configurator behavior change in this result branch.
- No firmware artifact committed.
- No flashing automation.
- No push-to-device automation.

## Test Identity

| Field | Value |
| --- | --- |
| Branch tested | glyph/gfw2-ultimate-tilt3-runtime |
| Commit SHA tested | UNKNOWN_NOT_RECORDED |
| Firmware artifact path | UNKNOWN_NOT_RECORDED |
| Artifact SHA-256 | UNKNOWN_NOT_RECORDED |
| Hardware identity | Glyph MK6 / exact unit identifier not separately recorded |
| Profile/config state | normal current layout; no dedicated Tilt3 button configured/actionable separately |

## Exact Hardware Observations Used

- "the normal layout does not have dpad buttons at all, so cannot confirm the dpad interaction now, will come with later builds."
- "LT1+LT2 results in LT3 table, and all of the 3 modifiers tables are verified."
- "However, there was no Tilt3 button set or actionable separately. Only Tilt1+Tilt2."

## Expected Table References

- Tilt1 table reference: `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md` and `docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json` (`tilt1_lt1`).
- Tilt2 table reference: `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md` and `docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json` (`tilt2_lt2`).

### Tilt3 Table (Expected and User-Verified via LT1+LT2)

| Direction | Raw left-stick | Offset |
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

## Hardware Result Table

| Check | Result | Notes |
| --- | --- | --- |
| LT1 alone directions 1..9 | PASS_TILT1_TABLE_VERIFIED | User reported all three modifier tables verified; this row records Tilt1 table verification. |
| LT2 alone directions 1..9 | PASS_TILT2_TABLE_VERIFIED | User reported all three modifier tables verified; this row records Tilt2 table verification. |
| LT1+LT2 directions 1..9 | PASS_TILT3_TABLE_VERIFIED | User explicitly reported LT1+LT2 resolves to Tilt3 table. |
| Dedicated LT3 directions 1..9 | NOT_TESTED_NO_ACTIONABLE_TILT3_BINDING | No dedicated Tilt3 button was configured/actionable separately. |
| D-pad side-effect check | NOT_TESTED_NO_DPAD_BUTTONS_IN_NORMAL_LAYOUT | Normal layout does not expose D-pad buttons. |
| LT1+LT2 D-pad side-effect removal | NOT_TESTED_NO_DPAD_BUTTONS_IN_NORMAL_LAYOUT | Cannot be observed on current normal layout. |
| LT1+LT2 C-stick/right-stick side-effect removal | NOT_TESTED | Not separately reported in this hardware observation set. |
| LT3 mixed with LT1/LT2 | NOT_TESTED_NO_ACTIONABLE_TILT3_BINDING | No dedicated actionable LT3 path available to form LT3-mixed chords. |
| Nunchuk | NOT_TESTED_UNAVAILABLE | No nunchuk evidence provided for this run. |
| Other buttons smoke | PASS_SMOKE_USER_REPORTED | Carries forward prior user hardware smoke evidence that other tested buttons worked as expected; not exhaustive per-button verification. |

## Final Disposition

`PASS_TILT3_CHORD_PATH`

Interpretation for this result document:

- LT1+LT2 -> Tilt3 table is hardware-verified.
- Dedicated LT3 remains unverified until a layout binds/actionably exposes LT3.
- D-pad side-effect removal remains unverified until a future layout exposes D-pad outputs.
- This is not a full broad preservation result.

## 2026-05-27 Amendment: LT3 Profile Binding Branch

- At the time this hardware result was recorded, no dedicated Tilt3 button was configured/actionable.
- In branch `glyph/gfw2-ultimate-lt3-profile-binding`, the Ultimate MVP profile binding changes physical `BTN_LT3` from logical `BTN_LF4` to logical `BTN_LT3`.
- A new hardware test is required to validate standalone physical LT3 -> logical LT3 -> Tilt3 behavior.

## Boundaries and Non-Claims

- No claim of dedicated LT3 hardware verification.
- No claim of D-pad interaction hardware verification.
- No claim of exhaustive C-stick/right-stick/trigger/SOCD/remap/profile preservation.
- No overwrite of historical RF5 ambiguity (no explicit RF5 retest evidence was provided here).

## 2026-05-27 Amendment: Post-Binding Path Check

- Post-binding-path review still found no standalone LT3 action on hardware.
- `LT1+LT2 -> Tilt3` remains hardware-verified.
- Dedicated LT3 remains blocked by the active profile binding path until the stored on-device Ultimate profile is actually updated.

## 2026-05-27 Amendment: Next Application Path

- This branch provides the next source-backed application path for active profile update:
  - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
  - manual configurator apply path to write active config
- Existing hardware disposition in this file is still limited to:
  - `PASS_TILT3_CHORD_PATH`
- Dedicated standalone LT3 remains `NOT_TESTED_NO_ACTIONABLE_TILT3_BINDING` until that artifact/default path is applied and retested on hardware.

## 2026-05-27 Amendment: Webapp Import Observation

- After webapp import/push attempts, standalone LT3 still did not produce Tilt3 in observed hardware behavior.
- `LT1+LT2 -> Tilt3` remained the verified path.
- Dedicated standalone LT3 remains unverified pending a verified active config write/readback path (Path B) or another verified configurator write path.

## 2026-05-27 Amendment: Serial Active Config Standalone LT3 Validation

- After serial active config write, standalone physical LT3 was hardware-verified.
- `LT1+LT2` remains verified.
- All Tilt modifier combinations work as expected.
- Right-stick and D-pad inputs are orthogonal to Tilt3.
- D-pad visual/profile duplicate-left defect remains open.

## 2026-05-27 Amendment: Final LT3 and D-pad Repair Confirmation

- Final active profile path now has standalone LT3 and repaired D-pad mapping hardware-confirmed.
- The original chord-path result (`PASS_TILT3_CHORD_PATH`) remains historically accurate for its recorded test state.
- Final repaired-profile confirmation is recorded in:
  - `docs/calibration/glyph_ultimate_lt3_dpad_fix_hardware_result_2026-05-27.md`
