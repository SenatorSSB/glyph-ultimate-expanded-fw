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
| `uf2` | `.pio/build/glyph_mk6/firmware.uf2` | `791552` | `53719bb3d58659e071793ef4102f16f40b4f823066d2bcd5f71f9db5082d842a` |
| `elf` | `.pio/build/glyph_mk6/firmware.elf` | `5407148` | `f1b92b9db343e42ea9fbddffccb0896c2273d6d80667f7469f262012253f9395` |
| `bin` | `.pio/build/glyph_mk6/firmware.bin` | `395664` | `ffa5c4f54e94bea7aad8e26b059ee38d297a52442469caa71e27da6738b45ce6` |

## Build constraints

- `artifact_hashes_are_rebuild_stable`: `false`
- `artifact_hashes_are_checker_gate`: `false`
- `hardware_result_claimed`: `false`

## Scope and behavior notes

- Source-owned active config preselection scaffold added in firmware source.
- Hot-path resolution now binds through `ResolveActiveRuntimeConfig()`.
- No parsed table materialization, parser calls, storage, WebSerial/device write, or flashing automation added.
- RF5/RF6/LT6 expression logic and `UpdateDigitalOutputs(...)` behavior are intended to remain unchanged relative to `configurator` baseline.
