# Phase 7A Diagnostic D5 Build Report

status: DIAGNOSTIC_D5_BUILD_REPORT_PENDING_HARDWARE_RESULT

diagnostic_mode: `D5`

branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

base_branch: `phase7a-diagnostic-d3-global-parse-result-only`

build command: `./scripts/build-glyph-mk6-quiet.sh`

firmware source commit under build: `7f63312277f0434f33fe39305b11d3f9d66c27dc`

source tree state at build: `dirty_with_d5_source_delta_pending_commit`

build date (local): `2026-06-09 20:26:35 +0300`

payload bytes retained: `true`

global_parse_result_added: `true`

parser_called_by_global_static_initialization: `true`

resolver_added: `true`

parsed_result_routed_to_runtime_output_lookup: `true`

storage_added: `false`

write_path_added: `false`

flashing_automation_added: `false`

runtime_behavior_changed_intended: `true` only in the narrow sense that the
source of the `runtime_config` view changes from direct source-owned selection
to the parsed-result resolver-selected equivalent view; no intended output
value change.

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
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 797696 | d5e8a2b9ee973fdc204bce4ffc78c30d2560f59cff0e531f0fc44689a86a31cb | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407968 | 2ca1c36b420c7ff4af7655a622be6c8e1c4a73b744212f7ed41d2df3ad700e45 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 398604 | 3cc437473ce49e3560f0dce1856c87ca33c35f19429a011699cf7c2a25d026e6 | available |

## Caveats

- D5 reuses the D2B retained payload `.incbin` symbol as parser input.
- The global/static parse result remains the D3 parse result.
- The parser result shape records status and counts; it does not materialize a
  separate table array.
- D5 does not change parser semantics.
- D5 routes analog runtime-config lookup through `ResolveActiveRuntimeConfig()`.
- D5 does not change expected output values.
- No runtime-loaded config, storage/config.bin/Persistence, WebSerial/device
  write, command IDs, or flashing automation is added.
- No hardware result is recorded on this branch.
- Hardware result required before conclusions.
- Nunchuk remains not tested.
