# Phase 7A Diagnostic D5A Build Report

status: DIAGNOSTIC_D5A_BUILD_REPORT_PENDING_HARDWARE_RESULT

diagnostic_mode: `D5A`

branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

base_branch: `phase7a-diagnostic-d3-global-parse-result-only`

build command: `./scripts/build-glyph-mk6-quiet.sh`

firmware source commit under build: `97eb4da6c3dc500392b38c348ec463902ff3d15d`

source tree state at build: `dirty_with_d5a_reframe_delta_pending_commit`

build date (local): `2026-06-09 20:40:28 +0300`

payload bytes retained: `true`

global_parse_result_added: `true`

parser_called_by_global_static_initialization: `true`

resolver_added: `true`

parsed_result_routed_to_runtime_output_lookup: `false`

parsed_table_materialization_added: `false`

parse_status_gated_routing_added: `true`

source_owned_runtime_view_routed_after_parse_ok: `true`

true_parsed_result_routing_deferred: `true`

d5b_required_for_true_parsed_data_routing: `true`

storage_added: `false`

write_path_added: `false`

flashing_automation_added: `false`

runtime_behavior_changed_intended: `true` only in the narrow sense that the
source-owned baseline-equivalent `runtime_config` view is now selected through
a parse-status-gated resolver; no intended output value change.

expected_output_values_changed: `false`

hardware_required: `true`

hardware_result_claimed: `false`

nunchuk_status: `not_tested`

artifact_hashes_are_rebuild_stable: `false`

artifact_hashes_are_checker_gate: `false`

Artifact observations are local build observations only. They are not a future
rebuild hash gate.

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 797696 | 53fc213da0c54fe53087aa49db370851b872c2adf0f3fdd7b6ba443c230b49c3 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407980 | 4d070ffee54012707b3ba85e64084653a580664294fa487db26d38ab505c1bdf | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 398604 | 43fc8837788ee0066a662c8893b24b644656a8f80f62348f840d4bbafb19b359 | available |

## Caveats

- D5A reuses the D2B retained payload `.incbin` symbol as parser input.
- The global/static parse result remains the D3 parse result.
- The parser result shape records status and counts; it does not materialize a
  separate table array or `RuntimeConfigView`.
- D5A does not change parser semantics.
- D5A routes analog runtime-config lookup through `ResolveActiveRuntimeConfig()`
  after a parse-status gate.
- D5A routes source-owned current-baseline equivalent data, not parsed table
  data.
- D5A does not change expected output values.
- True parsed-result table-data routing is deferred to possible D5B.
- No runtime-loaded config, storage/config.bin/Persistence, WebSerial/device
  write, command IDs, or flashing automation is added.
- No hardware result is recorded on this branch.
- Hardware result required before conclusions.
- Nunchuk remains not tested.
