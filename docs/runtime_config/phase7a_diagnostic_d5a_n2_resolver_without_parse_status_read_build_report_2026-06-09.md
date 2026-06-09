# Phase 7A Diagnostic D5A-N2 Build Report

status: DIAGNOSTIC_D5A_N2_BUILD_REPORT_PENDING_HARDWARE_RESULT

diagnostic_mode: `D5A-N2`

branch: `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read`

base_branch: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`

build command: `pio run -e glyph_mk6`

firmware source commit under build: `1555a9c1131541151ecb3fab2ac89409aa5586aa`

source tree state at build: `dirty_with_d5a_n2_source_delta_pending_commit`

build date (local): `2026-06-09 22:16:05 +0300`

payload bytes retained: `true`

global_parse_result_added: `true`

parser_called_by_global_static_initialization: `true`

resolver_added: `true`

parsed_result_routed_to_runtime_output_lookup: `false`

parsed_table_materialization_added: `false`

parse_status_gated_routing_added: `false`

source_owned_runtime_view_routed_after_parse_ok: `false`

runtime_behavior_changed_intended: `true` only in the narrow sense that runtime
resolver no longer branches on parse status in hot path.

runtime_behavior_changed_intended_scope: `remove parse-status hot-path branch in runtime resolver while retaining global parse result, direct source-owned fallback resolver contract, and unchanged routing path`

expected_output_values_changed: `false`

update_analog_outputs_changed: `true`

update_digital_outputs_changed: `false`

rf5_rf6_lt6_source_expressions_changed: `false`

storage_added: `false`

write_path_added: `false`

flashing_automation_added: `false`

runtime_loaded_config_added: `false`

hardware_required: `true`

hardware_result_claimed: `false`

nunchuk_status: `not_tested`

artifact_hashes_are_rebuild_stable: `false`

artifact_hashes_are_checker_gate: `false`

artifact_observations_are_local_not_rebuild_gate: `true`

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 793088 | `4da26197beb6a2ec8e045282698ae296962a84e136134eb1e04388e3b8f4f286` | true |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407436 | `a3a72e268cba1517d2ba3693671a29ec6708b97272e05ec6acc3f1fc3134f13a` | true |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 396532 | `420f5797a0925232ed7cbd7d0156778a765612e3882d0c2b62914bcdb8256208` | true |
