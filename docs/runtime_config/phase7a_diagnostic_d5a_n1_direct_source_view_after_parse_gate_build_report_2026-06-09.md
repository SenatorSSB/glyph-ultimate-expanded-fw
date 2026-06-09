# Phase 7A Diagnostic D5A-N1 Build Report

status: DIAGNOSTIC_D5A_N1_BUILD_REPORT_PENDING_HARDWARE_RESULT

diagnostic_mode: `D5A-N1`

branch: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`

base_branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

build command: `pio run -e glyph_mk6`

firmware source commit under build: `390cdecd612ede368ae289029b90b5a77af8883d`

source tree state at build: `dirty_with_d5a_n1_source_delta_pending_commit`

build date (local): `2026-06-09 21:28:09 +0300`

payload bytes retained: `true`

global_parse_result_added: `true`

parser_called_by_global_static_initialization: `true`

resolver_added: `true`

parsed_result_routed_to_runtime_output_lookup: `false`

parsed_table_materialization_added: `false`

parse_status_gated_routing_added: `true`

source_owned_runtime_view_routed_after_parse_ok: `true`

runtime_behavior_changed_intended: `true` only in the narrow sense that source-owned
baseline view selection is now parse-gated through a direct canonical source-owned
return path after parse-status gate.

expected_output_values_changed: `false`

storage_added: `false`

write_path_added: `false`

flashing_automation_added: `false`

runtime_behavior_changed_intended: `true`

hardware_required: `true`

hardware_result_claimed: `false`

nunchuk_status: `not_tested`

artifact_hashes_are_rebuild_stable: `false`

artifact_hashes_are_checker_gate: `false`

Artifact observations are local build observations only.

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 797696 | `bef237562575990e12be5dd45af5aeb0d4fd4551841dbac78f30f17287441ae3` | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407960 | `de323d5d805fd21a05641e43385a07ba6349d94cbc2a16770229a4a7046d7252` | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 398604 | `e4d3e02f8571b8d807118adbcdffaff5421e59e47559e8251c811076edaaa529` | available |
