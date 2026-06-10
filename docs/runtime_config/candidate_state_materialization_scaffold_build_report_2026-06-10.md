# Candidate State Materialization Scaffold Build Report

status: build_completed

branch: `runtime-config-candidate-state-materialization-scaffold`

baseline branch: `configurator`

## Canonical and actual build commands

- canonical build command: `pio run -e glyph_mk6`
- canonical build available in this agent environment: `false`
- canonical build failure: `zsh:1: command not found: pio`
- actual local build command: `./scripts/build-glyph-mk6-quiet.sh`
- actual local build completed: `true`

## Build result

- build completed: `true`
- build exit code: `0`
- build date: `2026-06-10`

## Build artifacts (local observations)

Artifact hashes, if recorded, are local observations only.

| artifact | path | size_bytes | sha256 |
| --- | --- | ---: | --- |
| `uf2` | `.pio/build/glyph_mk6/firmware.uf2` | `791552` | `29bb24db025aedab287536ff7af8ffb6acaaa2b03f50015cc53df35afc245486` |
| `elf` | `.pio/build/glyph_mk6/firmware.elf` | `5407148` | `a855ede80d8316cb1b699698951e7f55278bec7f1aa5e681317d4d0cc06abc98` |
| `bin` | `.pio/build/glyph_mk6/firmware.bin` | `395672` | `984904dee96d7823248c751a44cf79f9a6a270a9cd2e206458ba997a959159a4` |

## Build constraints

- `artifact_hashes_are_rebuild_stable`: `false`
- `artifact_hashes_are_checker_gate`: `false`
- `hardware_result_claimed`: `false`

## Scope and behavior notes

- Candidate runtime config state scaffold added in firmware source.
- Candidate materialization is not active and does not publish active state.
- `ResolveActiveRuntimeConfig()` remains stable active-view only.
- `UpdateAnalogOutputs(...)` still binds through `ResolveActiveRuntimeConfig()`.
- No parser-status hot-path read, runtime-loaded config, storage, WebSerial/device write, or flashing automation is added.
- No hardware test is required for this branch because candidate state is not active.
- Nunchuk remains NOT_TESTED.
