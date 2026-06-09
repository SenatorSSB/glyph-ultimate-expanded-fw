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
| `uf2` | `.pio/build/glyph_mk6/firmware.uf2` | `791552` | `5d3cdfb267edd9e1c3bcfac4cd77d4c058270bfa1b8071bf108da8ec52683a73` |
| `elf` | `.pio/build/glyph_mk6/firmware.elf` | `5407148` | `a7c7ec8a4f9bd70343e76aad5f666049187c4a724b32ae3bc84814b6b583a800` |
| `bin` | `.pio/build/glyph_mk6/firmware.bin` | `395664` | `ee09db320725d4d17b4d915ed3c86bd251eb32383cd3a06dd21445e5562a158b` |

## Build constraints

- `artifact_hashes_are_rebuild_stable`: `false`
- `artifact_hashes_are_checker_gate`: `false`
- `hardware_result_claimed`: `false`

## Scope and behavior notes

- Source-owned active config preselection scaffold added in firmware source.
- Hot-path resolution now binds through `ResolveActiveRuntimeConfig()`.
- No parsed table materialization, parser calls, storage, WebSerial/device write, or flashing automation added.
- RF5/RF6/LT6 expression logic and `UpdateDigitalOutputs(...)` behavior are intended to remain unchanged relative to `configurator` baseline.
