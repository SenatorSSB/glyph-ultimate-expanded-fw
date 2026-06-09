# Active Runtime Config State Source-Owned Preselection Build Report

status: build_completed

branch: `runtime-active-config-state-source-owned-preselection`

baseline branch: `configurator`

## Canonical and actual build commands

- canonical build command: `pio run -e glyph_mk6`
- canonical build available in this agent environment: `false`
- actual local build command: `./scripts/build-glyph-mk6-quiet.sh`
- actual local build completed: `true`

## Build result

- build completed: `true`
- build exit code: `0`
- build date: `2026-06-10`

## Build artifacts (local observations)

| artifact | path | size_bytes | sha256 |
| --- | --- | ---: | --- |
| `uf2` | `.pio/build/glyph_mk6/firmware.uf2` | `791552` | `ba64e1120b21c5a93fa3fcafbfa149cfa89c86ebbd75aa83a03f119555795a02` |
| `elf` | `.pio/build/glyph_mk6/firmware.elf` | `5407148` | `953022722a3ed73eae250fc9ad5ac86e8c6817def512a60c5fd0a237d6b84b91` |
| `bin` | `.pio/build/glyph_mk6/firmware.bin` | `395664` | `57a72145aa368220f233a88791477283dbbd06f64b51de4e298fde6ca55469e3` |

## Build constraints

- `artifact_hashes_are_rebuild_stable`: `false`
- `artifact_hashes_are_checker_gate`: `false`
- `hardware_result_claimed`: `false`

## Scope and behavior notes

- Source-owned active config preselection scaffold added in firmware source.
- Hot-path resolution now binds through `ResolveActiveRuntimeConfig()`.
- No parsed table materialization, parser calls, storage, WebSerial/device write, or flashing automation added.
- RF5/RF6/LT6 expression logic and `UpdateDigitalOutputs(...)` behavior are intended to remain unchanged relative to `configurator` baseline.
