# Glyph Identity Runtime Behavior Cases - 2026-05-28

## Purpose and status

This is a source-backed expected-behavior case matrix for the current Glyph Smash Box identity runtime in native `MODE_ULTIMATE`.

Status:

- Docs/fixture/checker-only canonicalization of representative runtime behavior cases.
- Primary machine-readable fixture: `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`.
- Executable checker: `tools/check_glyph_identity_runtime_behavior_evaluator.py` mechanically evaluates the representative fixture with a bounded source-backed Python mirror; it is not hardware validation.
- The cases are intended to help future mirror evaluators, C++ unit-style harnesses, generated-config regression checks, Senscope export validation reports, and manual hardware checklist generation.

Non-goals:

- No runtime behavior change.
- No generated config.
- No runtime-loaded config.
- No serial writing.
- No push-to-device or flashing workflow.
- No new hardware claim.
- No Senscope browser app semantic claim.
- No Super Smash Bros. Ultimate gameplay-semantic source authority.

## Source authority

Primary source authority for this case matrix:

- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md`
- `docs/calibration/glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md`
- `docs/calibration/glyph_smashbox_modifiers_hardware_test_plan_2026-05-27.md`

The runtime source owns the coordinate tables, helper ordering, direction resolution, table selection, override ordering, D-pad routing, C-stick routing, and nunchuk preservation paths. The role-map document and fixture are the primary behavioral index used to organize this case matrix.

The hardware result document records the existing hardware-observed scope for the current identity runtime. This matrix derives from that hardware-verified role map and current runtime source, but no case in this document should be treated as a new hardware validation result.

Nunchuk behavior is source-present and preserved in `src/modes/Ultimate.cpp`, but nunchuk behavior is not hardware-tested in the cited latest result.

## Case schema explanation

Each behavior case represents one representative input condition and the expected source-backed output subset for that condition.

- `case_id`: Stable identifier for checker/harness migration.
- `category`: Behavioral group used by this document and the checker.
- `input_buttons`: Physical/logical identity-runtime button IDs such as `RF1`, `LF3`, or `LT5`.
- `input_state`: Optional non-button source state, currently used only for nunchuk preservation cases.
- `expected.digital_buttons`: Source-backed digital game/menu output carriers asserted by the case.
- `expected.suppressed_buttons`: Source-backed carriers that are specifically expected not to assert in the case.
- `expected.effective_direction`: Resolved left/right/up/down state after source direction resolution.
- `expected.analog_source`: The source-backed analog phase responsible for the expected left-stick coordinate when asserted.
- `expected.table_id`: Runtime table identifier where table selection is part of the case.
- `expected.direction_index`: Numpad direction index where a deterministic table lookup is asserted.
- `expected.left_stick`: Expected left-stick raw output when deterministic and source-backed.
- `expected.dpad`: Expected D-pad output when routing or nunchuk C behavior is part of the case.
- `expected.right_stick`: Expected right-stick raw output when deterministic and source-backed.
- `expected.right_stick_digital`: Expected C-stick digital/cardinal output when relevant.
- `source_refs`: Source files/docs that back the case.
- `notes`: Short caveats, priority notes, or source-backed exclusion notes.

Cases are representative, not exhaustive. Missing table rows or output fields are not negative claims. A future executable harness can expand these cases, but expansion must remain source-backed or be explicitly marked inferred/unknown.

No case should be treated as a new hardware validation result.

## Digital button carrier cases

Digital carrier cases document source-owned button/menu carrier assertions before table-modifier concerns.

Fixture case IDs:

- `digital_rf1_a_carrier`: `RF1` asserts `A`.
- `digital_rf5_b_carrier`: `RF5` asserts `B`.
- `digital_lf4_b_carrier`: `LF4` asserts `B`.
- `digital_rf10_y_carrier`: `RF10` asserts `Y`.
- `digital_rf2_x_non_layer_carrier`: `RF2` asserts `X` outside pure layer and LF4 C-stick suppression.
- `digital_rt1_z_carrier`: `RT1` asserts source-confirmed `Z` through the shared carrier.
- `digital_lt5_z_carrier`: `LT5` asserts the shared `Z` carrier.
- `digital_rf11_z_carrier`: `RF11` asserts the shared `Z` carrier.
- `digital_lt3_l_carrier`: `LT3` asserts `L` and the L analog companion.
- `digital_rf16_r_carrier`: `RF16` asserts `R` and the R analog companion.
- `digital_mb4_capture_carrier`: `MB4` asserts Capture.
- `digital_mb5_home_carrier`: `MB5` asserts Home.
- `digital_mb6_select_minus_carrier`: `MB6` asserts Select/Minus.
- `digital_mb7_start_plus_carrier`: `MB7` asserts Start/Plus.

## Base direction cases

Base direction cases document effective direction resolution before special table selection and override cases.

Fixture case IDs:

- `base_lf3_effective_left`
- `base_lf1_effective_right`
- `base_lf2_effective_up`
- `base_lf5_effective_down`
- `base_lf3_lf1_horizontal_cancel`
- `base_lf2_lf5_up_down_both_source_present`
- `base_rf6_forced_up`
- `base_rf6_lf5_forced_up_suppresses_down`

The horizontal cancellation case is source-backed by `ResolveHorizontalAxis`. The LF2+LF5 case records only the directly source-backed effective-direction booleans and intentionally does not assert an analog coordinate.

## Modifier table-selection cases

Single-modifier cases document the one-effective-modifier path in `SelectStickTable`.

Fixture case IDs:

- `single_x1_neutral`
- `single_x1_right`
- `single_x2_neutral`
- `single_x2_right`
- `single_y1_neutral`
- `single_y1_up`
- `single_y1_down`
- `single_tilt1_neutral`
- `single_tilt1_right`
- `single_tilt2_neutral`
- `single_tilt2_right`
- `single_tilt3_neutral`
- `single_tilt3_right`

`RF3`/`RF4` are Tilt1/Tilt2 only outside layer/sub-mode. `RF3+RF4` becomes Tilt3 only outside layer/sub-mode.

## Mode table-selection cases

Mode cases document `RF8` table selection and Mode-default fallback behavior.

Fixture case IDs:

- `mode_default_direction_5_neutral`
- `mode_default_direction_4_left`
- `mode_default_direction_6_right`
- `mode_default_direction_2_down`
- `mode_default_direction_8_up`
- `mode_default_direction_1_left_down`
- `mode_default_direction_3_right_down`
- `mode_default_direction_7_left_up`
- `mode_default_direction_9_right_up`
- `mode_modifier_mx1_neutral`
- `mode_modifier_mx2_neutral`
- `mode_modifier_my1_neutral`
- `mode_modifier_mtilt1_neutral`
- `mode_modifier_mtilt2_neutral`
- `mode_modifier_mtilt3_neutral`

Mode does not count as the non-mode modifier. It selects Mode-default or the corresponding `M*` table once modifier selection resolves.

## Composite table cases

Composite cases document source-defined exceptions that are checked before ordinary one-modifier counting.

Fixture case IDs:

- `composite_y1_tilt1_neutral`
- `composite_y1_tilt1_right`
- `composite_mode_y1_tilt1_neutral`
- `composite_mode_y1_tilt1_right`
- `composite_y1_layer_normal_x_left`
- `composite_y1_layer_flipper_left`
- `composite_mode_y1_layer_normal_x_left`
- `composite_mode_y1_layer_flipper_left`
- `composite_layer_rf4_flipper_wins_over_rf3_normal_x`

The source-backed composite priority is `Y1+Tilt1`, then `Y1+LayerNormalX`, then `Y1+LayerFlipper`. RF4 flipper wins over RF3 normal-x for layer table selection when both are held, while RF3 can still contribute B in pure layer.

## Pure layer cases

Pure layer cases document `LF8`/`LF7` behavior without `LF4`.

Fixture case IDs:

- `pure_layer_lf8_layer_left`
- `pure_layer_lf7_layer_right`
- `pure_layer_lf8_rf2_forced_up_no_x`
- `pure_layer_lf7_rf2_forced_up_no_x`
- `pure_layer_lf8_rf3_b_layer_normal_x`
- `pure_layer_lf8_rf4_layer_flipper`
- `pure_layer_lf8_rf3_rf4_flipper_wins`

Pure layer behavior is source-backed as:

- `LF8` contributes layer-left.
- `LF7` contributes layer-right.
- `RF2` becomes forced Up and does not output X.
- `RF3` contributes B plus layer normal-x.
- `RF4` contributes layer flipper.

## LF4 sub-mode cases

LF4 sub-mode cases document behavior when `LF4 && (LT2 || LF8 || LF7)` activates source sub-mode handling.

Fixture case IDs:

- `lf4_submode_lf4_lt2_y1_suppressed_default_neutral`
- `lf4_submode_lf4_lt2_rf2_x_no_forced_up`
- `lf4_submode_lf4_lt2_rf3_forced_up`
- `lf4_submode_lf4_lf8_rf4_layer_flipper`
- `lf4_submode_lf4_lf8_rf3_rf4_flipper_forced_up`

LF4 always contributes B. While LF4 is held, LT2/Y1 is suppressed. In LF4 sub-mode, RF2 is X unless C-stick suppressed, RF3 is forced Up, and RF4 is layer flipper.

## C-stick suppression cases

C-stick suppression cases document the LF4 sub-mode RF2 suppression rule.

Fixture case IDs:

- `cstick_suppression_lf4_lt2_rf2_rt2_no_x`
- `cstick_suppression_lf4_lt2_rf2_rt3_no_x`
- `cstick_suppression_lf4_lt2_rf2_rt4_no_x`
- `cstick_suppression_lf4_lt2_rf2_rt5_no_x`
- `cstick_suppression_lf4_lf8_rf2_rt5_no_x_no_rf2_forced_up`

Any `RT2`/`RT3`/`RT4`/`RT5` C-stick input suppresses RF2 completely in LF4 sub-mode: no X, no RF2 forced-Up contribution, and no RF2-owned D-pad Up contribution under RF13.

The `LF4+LF8+RF2+RT5` case is retained separately to cover the layer/sub-mode variant where layer-left remains active while RF2-owned X and forced-Up behavior are suppressed.

## Direction-plus-A override cases

Direction-plus-A cases document the hard analog override applied after table output and before LT5/RF11 low-magnitude override.

Fixture case IDs:

- `direction_plus_a_lt6_down_a_default`
- `direction_plus_a_rf12_up_a_default`
- `direction_plus_a_rf15_up_a_default`
- `direction_plus_a_mode_lt6_down_a`
- `direction_plus_a_mode_rf12_up_a`
- `direction_plus_a_rf12_lt6_forced_up_wins`

`LT6` contributes A plus Down unless forced Up is active. `RF12` and `RF15` contribute A plus forced Up. Mode selects Mode-default coordinates for the hard Direction+A override.

## LT5/RF11 low-magnitude Z-airdodge override cases

LT5/RF11 cases document the shared Z carrier and low-magnitude table override when LS->DPad is inactive.

Fixture case IDs:

- `z_airdodge_lt5_neutral_low_magnitude`
- `z_airdodge_lt5_left_low_magnitude`
- `z_airdodge_rf11_right_up_low_magnitude`
- `z_airdodge_lt5_rf12_forced_up_low_magnitude`

The low-magnitude table is selected after Direction+A and before RF7 hard Up+B and RF9 null. RF11 shares LT5 low-magnitude behavior in source.

## RF7 hard Up+B cases

RF7 cases document the hard Up+B analog override and B carrier when LS->DPad is inactive.

Fixture case IDs:

- `rf7_hard_up_b_neutral`
- `rf7_hard_up_b_left`
- `rf7_hard_up_b_right`

RF7 contributes B. The analog left-stick output is `(128,172)` at neutral, `(77,172)` with effective left, and `(179,172)` with effective right. RF7 is not part of forced-up direction aggregation.

## RF9 null override cases

RF9 cases document final null priority and RF9 exclusion from digital game outputs and table selection.

Fixture case IDs:

- `rf9_null_neutral`
- `rf9_null_overrides_rf7_hard_up_b`
- `rf9_null_overrides_lt5_low_magnitude`
- `rf9_null_with_rf13_keeps_dpad_left`

RF9 forces final analog left stick to `(128,128)` after table output, Direction+A, LT5/RF11 low-magnitude override, RF7 hard Up+B, and LS->DPad centering. RF9 does not suppress unrelated digital carriers or D-pad routing.

## RF13 LS->DPad cases

RF13 cases document D-pad routing and analog centering.

Fixture case IDs:

- `rf13_left_to_dpad_center_left_stick`
- `rf13_mode_left_to_dpad_mode_center`
- `rf13_lf8_rf2_dpad_up_left_no_x`
- `rf13_rf7_left_dpad_center_b`
- `rf13_lt5_left_dpad_center_z`

RF13 suppresses digital left-stick direction outputs and ORs effective directions into D-pad. Analog left stick is centered from Default direction 5 or ModeDefault direction 5. The LT5/RF11 low-magnitude override and RF7 hard Up+B override are bypassed while RF13 LS->DPad is active.

## Right-stick / C-stick cases

Right-stick cases document source C-stick routing.

Fixture case IDs:

- `right_stick_rt3_c_left`
- `right_stick_rt4_c_right`
- `right_stick_rt5_c_up`
- `right_stick_rt2_c_down`
- `right_stick_rt3_rt5_diagonal_angle`

`RT3` drives C-left, `RT4` drives C-right, `RT5` drives C-up, and `RT2` drives C-down. Diagonal C-stick coordinates use the source 42/68 slideoff angle override.

## Nunchuk source-preservation cases

Nunchuk cases are source-preservation cases only.

Fixture case IDs:

- `nunchuk_c_rt5_dpad_up_right_stick_neutral`
- `nunchuk_connected_left_stick_override`

Nunchuk C can route the C cluster into D-pad and neutralize the right stick. Nunchuk connected left-stick analog input overrides software left-stick output after modifier processing. These behaviors are source-present, but not hardware-tested in the cited latest result.

## Future harness migration notes

This case matrix is not an executable firmware simulator. Future harness migration should preserve the current boundaries:

- Treat the JSON fixture as representative expected-behavior data, not as a full state-space.
- Prefer source-parsed constants or generated fixtures when moving to a Python mirror evaluator or C++ unit-style harness.
- Keep hardware-result evidence separate from source-backed expected cases.
- Keep nunchuk rows marked as source-present but not hardware-validated unless new hardware evidence is recorded.
- Do not use this matrix to add runtime-loaded config, serial writing, push-to-device behavior, Senscope game semantics, macros, turbo behavior, or timing automation.
- If runtime source changes, update the role map, behavior matrix, checker, and hardware status language before carrying old expectations forward.
