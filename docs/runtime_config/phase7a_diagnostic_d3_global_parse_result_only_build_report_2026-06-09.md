# Phase 7A Diagnostic D3 Build Report

status: DIAGNOSTIC_D3_BUILD_REPORT_PENDING_HARDWARE_RESULT

diagnostic_mode: `D3`

branch: `phase7a-diagnostic-d3-global-parse-result-only`

base_branch: `phase7a-diagnostic-d2b-retained-payload-bytes`

build command: `./scripts/build-glyph-mk6-quiet.sh`

firmware source commit under build: `1af6c522b8f15f706072ec88315978281af8f4c4`

source tree state at build: `dirty_with_d3_source_delta_pending_commit`

build date (local): `2026-06-09 17:23:01 +0300`

payload bytes retained: `true`

parser_called_by_global_static_initialization: `true`

global_parse_result_added: `true`

resolver_added: `false`

runtime_behavior_changed_intended: `false`

UpdateAnalogOutputs changed: `false`

storage/write/flashing: `false`

hardware_required: `true`

hardware_result_claimed: `false`

nunchuk_status: `not_tested`

artifact observations are local build observations and are not a future rebuild
hash gate.

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 793088 | ee428514a0f00873ab900cc5649b7cec5f3f5a83867e05b613b50fb063cf0a19 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407436 | 23f06368ece84c171c1e3c3ce94f1fefdac236d6fba4d55c4b2b4941eef37d32 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 396532 | ded8da7b3e91fa4252f13cf32b8eae4a122987471d7cc77bcc88f9c0ee748a2f | available |

## Artifact Size Deltas Vs D2B

| artifact_type | D2B size_bytes | D2B sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 792576 | c3196352f508e999e9c4f1d5a8a5de96409e9591f4f71c64817cdc06a4b985b4 | 793088 | ee428514a0f00873ab900cc5649b7cec5f3f5a83867e05b613b50fb063cf0a19 | 512 |
| elf | 5407276 | b7aa9b045c1b55e2674e880afc801d2e1cbf23af7f8026d95a4b0519e8b92118 | 5407436 | 23f06368ece84c171c1e3c3ce94f1fefdac236d6fba4d55c4b2b4941eef37d32 | 160 |
| bin | 396208 | ee3c37855e6d53ce18b32a5c32c3f9faa6525014f7bea93d99ddd6756655e37d | 396532 | ded8da7b3e91fa4252f13cf32b8eae4a122987471d7cc77bcc88f9c0ee748a2f | 324 |

## Artifact Size Deltas Vs Baseline

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 793088 | ee428514a0f00873ab900cc5649b7cec5f3f5a83867e05b613b50fb063cf0a19 | 1536 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407436 | 23f06368ece84c171c1e3c3ce94f1fefdac236d6fba4d55c4b2b4941eef37d32 | 288 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 396532 | ded8da7b3e91fa4252f13cf32b8eae4a122987471d7cc77bcc88f9c0ee748a2f | 868 |

## Payload Sequence Scan

Scanned fixture:
`docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin`

| artifact path | full payload sequence found | offsets decimal | offsets hex |
| --- | --- | ---: | --- |
| `.pio/build/glyph_mk6/firmware.bin` | true | 370188 | `0x5a60c` |
| `.pio/build/glyph_mk6/firmware.elf` | true | 435724 | `0x6a60c` |
| `.pio/build/glyph_mk6/firmware.uf2` | false | none | none |

## Caveats

- D3 reuses the D2B retained payload `.incbin` symbol as parser input.
- The global/static parse result exists only as diagnostic initialization.
- No resolver/reference routing is added.
- No parsed result is passed into output lookup.
- No runtime-loaded config, storage, WebSerial/device write, command IDs, or
  flashing automation is added.
- No hardware result is recorded on this branch.
- Hardware result required before conclusions.
- Nunchuk remains not tested.
