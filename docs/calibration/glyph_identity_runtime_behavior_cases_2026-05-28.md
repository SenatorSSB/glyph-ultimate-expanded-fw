# Glyph Identity Runtime Behavior Cases - GFW3 Remap Update

## Purpose and status

This is the representative behavior-case matrix for the requested Glyph GFW3
runtime remap rework in native `MODE_ULTIMATE`.

Status:

- Docs/fixture/checker-only evaluator update for the new requested firmware
  behavior.
- Primary machine-readable fixture:
  `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`.
- Executable checker: `tools/check_glyph_identity_runtime_behavior_evaluator.py`.
- Firmware source implementation is not claimed by this branch.
- No new hardware claim.

Non-goals:

- No generated config.
- No runtime-loaded config.
- No serial writing.
- No push-to-device or flashing workflow.
- No Senscope browser app semantic claim.
- No Super Smash Bros. Ultimate gameplay-semantic source authority.

## Source authority

Primary source authority for this case matrix:

- `docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md`
- `docs/calibration/fixtures/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.json`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md`

The GFW3 spec records the requested behavior. Current firmware source remains
the implementation target until the later firmware branch lands. No case should
be treated as a hardware validation result.

Nunchuk behavior is source-present and preserved in `src/modes/Ultimate.cpp`,
but nunchuk behavior is not hardware-tested here.

## Case schema explanation

Each behavior case represents one representative input condition and the
expected output subset for that condition.

- `case_id`: Stable identifier for checker/harness migration.
- `category`: Behavioral group used by this document and the checker.
- `input_buttons`: Physical/logical identity-runtime button IDs.
- `input_state`: Optional non-button source state, currently used only for
  nunchuk preservation cases.
- `expected.digital_buttons`: Digital game/menu output carriers asserted.
- `expected.suppressed_buttons`: Carriers expected not to assert.
- `expected.effective_direction`: Resolved left/right/up/down state.
- `expected.analog_source`: Analog phase responsible for an asserted coordinate.
- `expected.table_id`: Runtime table identifier when table selection is part of
  the case.
- `expected.direction_index`: Numpad direction index.
- `expected.left_stick`: Expected left-stick raw output.
- `expected.dpad`: Expected D-pad output.
- `expected.right_stick`: Expected right-stick raw output.
- `expected.right_stick_digital`: Expected C-stick digital/cardinal output.
- `source_refs`: Source files/docs that back the case.
- `notes`: Caveats, priority notes, or source-backed exclusion notes.

Cases are representative, not exhaustive. Missing table rows or output fields
are not negative claims.

## Base role cases

Fixture case IDs:

- `gfw3_rf6_z_airdodge_neutral`
- `gfw3_rf5_forced_up_a`
- `gfw3_rf15_scratched`
- `gfw3_rf12_scratched`
- `gfw3_rf11_scratched`
- `gfw3_rf3_base_x`
- `gfw3_rf2_base_b`
- `gfw3_rf4_base_tilt1`
- `gfw3_rf4_rt2_suppresses_tilt1`
- `gfw3_rt1_base_tilt2`
- `gfw3_mode_rf4_mode_default`
- `gfw3_mode_rf4_rt2_suppressed_mode_default`
- `gfw3_mode_rt1_mtilt2`
- `gfw3_mode_rt1_rf4_custom`
- `gfw3_rf3_rf4_no_tilt3`

## Custom modifier cases

Fixture case IDs:

- `gfw3_rt1_rf4_rt2_custom_preserved`
- `gfw3_rt1_rf4_custom_1`
- `gfw3_rt1_rf4_custom_2`
- `gfw3_rt1_rf4_custom_3`
- `gfw3_rt1_rf4_custom_4`
- `gfw3_rt1_rf4_custom_6`
- `gfw3_rt1_rf4_custom_7`
- `gfw3_rt1_rf4_custom_8`
- `gfw3_rt1_rf4_custom_9`
- `gfw3_rf4_rf2_base_minus41`
- `gfw3_rf4_rf2_base_minus41_left`
- `gfw3_rf4_rf2_base_minus41_down`
- `gfw3_rf4_rf2_base_minus41_neutral`
- `gfw3_rf4_rf2_base_minus41_up`
- `gfw3_rf4_rf2_base_minus41_diag1`
- `gfw3_rf4_rf2_rt2_suppresses_minus41`

## RF9 null cases

Fixture case IDs:

- `gfw3_rf9_nulls_left_and_right_stick`
- `gfw3_rf9_rf4_disables_null`
- `gfw3_rf9_rf4_rt4_null_reenabled`
- `gfw3_rf9_rf3_suppresses_x`
- `gfw3_rf9_rf3_rt2_restores_x`
- `gfw3_rf9_rf3_rt5_restores_x_cstick_active`
- `gfw3_rf9_rf3_lf3_rt5_cstick_up_left_special`
- `gfw3_rf9_rf3_lf3_rt2_cstick_down_left_special`
- `gfw3_rf9_rf3_rf4_suppresses_rf4_no_full_null`
- `gfw3_rf9_rf3_rf4_rt5_restores_x_cstick_active`
- `gfw3_rf9_rf3_rt1_rf4_suppresses_custom_no_full_null`
- `gfw3_rf9_rf4_rt5_without_rf3_full_null_preserved`
- `gfw3_lt2_rf9_rf3_remains_b_not_x_full_null`
- `gfw3_lt2_rf9_rf3_rt2_remains_b_not_x`
- `gfw3_lf4_rf9_rf3_remains_forced_up_not_x_full_null`
- `gfw3_lf4_rf9_rf3_rt2_remains_forced_up_not_x`

## LT physical move cycle cases

Fixture case IDs:

- `gfw3_lt1_l`
- `gfw3_lt4_x2`
- `gfw3_lt5_x1`
- `gfw3_lt3_l_plus_r`

## LF8/LF7 removal cases

Fixture case IDs:

- `gfw3_lf8_no_layer_left`
- `gfw3_lf7_no_layer_right`

## LT2 sublayer cases

Fixture case IDs:

- `gfw3_lt2_base_y1`
- `gfw3_lt2_rf4_flipper`
- `gfw3_lt2_rf4_rt2_suppresses_flipper`
- `gfw3_lt2_rf3_b_normal_x`
- `gfw3_lt2_rf3_rf4_b_flipper`
- `gfw3_lt2_rf3_rf4_rt2_falls_back_to_rf3`
- `gfw3_lt2_rf2_forced_up`
- `gfw3_lt2_rf1_x`
- `gfw3_lt2_rf1_rt2_suppresses_x`

## LF4 submode cases

Fixture case IDs:

- `gfw3_lf4_rf4_tilt1`
- `gfw3_lf4_rf4_rt2_suppresses_tilt1`
- `gfw3_lf4_rf3_forced_up`
- `gfw3_lf4_rf2_x`
- `gfw3_lf4_rf2_rf4_deactivates_rf4`
- `gfw3_lf4_rf2_rt2_suppresses_x_deactivates_rf4`
- `gfw3_lf4_lt2_uses_lf4_behavior`
- `gfw3_lf4_lt2_rf4_tilt1`
- `gfw3_lf4_lt2_rf2_rf4_deactivates_rf4`
- `gfw3_lf4_lt2_rf2_rf4_rt2_suppresses_x_deactivates_rf4`

## RF3 vertical C-stick cases

Fixture case IDs:

- `gfw3_rf3_lf3_rt5_cstick_up_left_special`
- `gfw3_rf3_lf1_rt5_cstick_up_right_special`
- `gfw3_rf3_lf3_rt2_cstick_down_left_special`
- `gfw3_rf3_lf1_rt2_cstick_down_right_special`
- `gfw3_rf3_rt5_no_horizontal_normal_cup`
- `gfw3_rf3_rt2_no_horizontal_normal_cdown`
- `gfw3_rf3_lf1_rt4_normal_cright`
- `gfw3_rf3_lf1_rt5_rt4_preserves_two_axis_cstick`

## Preservation cases

Fixture case IDs:

- `gfw3_rf7_hard_up_b_preserved`
- `gfw3_rf13_ls_to_dpad_preserved`
- `gfw3_nunchuk_connected_left_stick_override`

Hardware status remains `not_new_hardware_result`; nunchuk status remains
`preserved_but_not_hardware_validated`.
