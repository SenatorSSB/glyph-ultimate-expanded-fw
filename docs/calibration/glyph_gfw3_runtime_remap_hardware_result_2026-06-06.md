# Glyph GFW3 Runtime Remap Hardware Result - 2026-06-06

## Scope

This records a user-reported hardware pass for the GFW3 runtime remap branch.

- User report: "everything passing as expected".
- User is content for now.
- Branch tested: `glyph/gfw3-runtime-remap-rework`.
- Result date: 2026-06-06.
- Result scope: GFW3 runtime remap behavior only.
- Source test plan: `docs/calibration/glyph_gfw3_runtime_remap_hardware_test_plan_2026-06-04.md`.
- Source fixture: `docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_test_plan_2026-06-04.json`.

This is not a claim about any behavior outside the GFW3 runtime remap test plan.

## Explicit Non-Claims

- No active profile artifact change was made or required.
- No runtime-loaded config was implemented or validated.
- No WebSerial write workflow was implemented or validated.
- No serial/device write workflow was implemented or validated.
- No generated config/export artifact was changed.
- Nunchuk was not hardware-validated unless explicitly tested; no separate nunchuk hardware validation was reported.
- This does not claim official configurator compatibility or push-to-device behavior.

## Result Summary

| Field | Value |
| --- | --- |
| schema_name | `glyph_gfw3_runtime_remap_hardware_result` |
| result_version | `1` |
| status | `user_reported_hardware_pass` |
| hardware_status | `user_hardware_validated` |
| hardware_validation_claimed | `true` |
| runtime_loaded_config_implemented | `false` |
| webserial_write_implemented | `false` |
| device_write_implemented | `false` |
| profile_artifact_changed | `false` |
| nunchuk_hardware_validated | `false` |
| nunchuk_status | `not_tested_or_not_claimed` |
| pass rows | `56` |
| not-tested rows | `1` |

## Row Results

All executable rows from the current GFW3 hardware test plan fixture are marked PASS under the user's report. The unavailable nunchuk row remains NOT_TESTED because no nunchuk hardware validation was separately reported.

| Row ID | Area | Status | Notes |
| --- | --- | --- | --- |
| boot_profile_sanity | boot_profile_sanity | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| base_rf6_z_airdodge | base_button_role_changes | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| base_rf5_up_a | base_button_role_changes | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| scratched_rf11 | scratched_roles | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| scratched_rf12 | scratched_roles | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| scratched_rf15 | scratched_roles | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| base_rf2_b | base_button_role_changes | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| base_rf3_x | base_button_role_changes | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| base_rf4_tilt1 | base_button_role_changes | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf4_cstick_suppresses_base_tilt1 | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| base_rt1_tilt2 | base_button_role_changes | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_rf4_no_tilt3 | scratched_roles | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rt1_rf4_custom_table | custom_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rt1_rf4_cstick_custom_preserved | custom_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf4_rf2_minus41 | priority | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf4_rf2_cstick_suppresses_minus41 | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_null_both_sticks | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf4_null_disabled | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf4_cstick_reenables_null | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_suppresses_x | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_cstick_restores_x | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_rt5_restores_x_cstick_active | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_rt5_left_special_no_full_null | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_rt2_left_special_no_full_null | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_rf4_suppresses_rf4_no_full_null | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf3_rt1_rf4_suppresses_custom_no_full_null | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_alone_full_null_preserved | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf9_rf4_cstick_without_rf3_full_null_preserved | null_modifier | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt1_l | lt_physical_move_cycle | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt3_l_r | lt_physical_move_cycle | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt4_x2_mx2 | lt_physical_move_cycle | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt5_x1_mx1 | lt_physical_move_cycle | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_base_y1_my1 | lt2_sublayer | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf4_flipper | lt2_sublayer | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf4_cstick_suppresses_flipper | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf3_b_normal_x | lt2_sublayer | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf3_rf4_b_flipper | lt2_sublayer | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf3_rf4_cstick_fallback_rf3 | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf2_forced_up | lt2_sublayer | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lt2_rf1_x_cstick_suppression | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_rf4_tilt1 | lf4_submode | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_rf4_cstick_suppresses_tilt1 | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_rf3_forced_up | lf4_submode | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_rf2_x | lf4_submode | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_rf2_rf4_deactivates_rf4 | priority | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_rf2_cstick_suppression | cstick_suppression | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| lf4_overrides_lt2 | priority | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_rt5_left_special | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_rt5_right_special | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_rt2_left_special | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_rt2_right_special | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_vertical_no_horizontal_preserves_normal | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_horizontal_unaffected | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf3_two_axis_cstick_preserved | rf3_vertical_cstick_special | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf7_hard_up_b_unchanged | preservation | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| rf13_ls_to_dpad_unchanged | preservation | PASS | User-reported pass within the current GFW3 hardware test plan scope; no extra measured values claimed. |
| nunchuk_preserved_not_tested | preservation | NOT_TESTED | Nunchuk hardware validation was not separately reported; no nunchuk coverage claimed. |

## Merge Gate Interpretation

This user-reported hardware pass unblocks merge of `glyph/gfw3-runtime-remap-rework` into `configurator` if the branch inspection, repository checks, and firmware build pass.

The result should be inspected first by the supervisor/chat before any merge. Do not merge this hardware-result branch directly to `configurator`.
