# Parsed Candidate Opt-In Diagnostic Batch Build Report - 2026-06-10

status: BUILD_PASS

branch: `runtime-config-parsed-candidate-opt-in-diagnostic-batch`

baseline branch: `configurator`

## Build Identity

| Field | Value |
| --- | --- |
| Canonical command | `pio run -e glyph_mk6` |
| Canonical command available | `false` |
| Canonical command result | `pio` command not found |
| Actual local build command | `./scripts/build-glyph-mk6-quiet.sh` |
| Build exit code | `0` |
| Build result | `PASS` |
| Hardware result recorded | `false` |
| Hardware test required before merge | `true` |
| Nunchuk status | `NOT_TESTED` |

## Artifact Observations

These hashes are local observations only and are not checker gates.

| Artifact | Path | Size bytes | SHA-256 |
| --- | --- | ---: | --- |
| UF2 | `.pio/build/glyph_mk6/firmware.uf2` | 801280 | `181dc011693c639e8b544fa3e9ecea51719d60ad6f683096de3d52419478472f` |
| ELF | `.pio/build/glyph_mk6/firmware.elf` | 5408396 | `65ab332948499c75a433098643fa89e105f7b454f6bec7f5ffde035a89b3b2e7` |
| BIN | `.pio/build/glyph_mk6/firmware.bin` | 400440 | `87847b911fd1eaebce7bcabed0678fdb7fec855627b53ff21fd8da4fa0e8efcf` |

## Scope Notes

- The diagnostic opt-in activation flag is enabled.
- The source-owned static parser fixture is materialized into candidate state
  before publication.
- The candidate must prove equivalent to the source-owned baseline before it can
  be accepted.
- Active output generation consumes only the published active view.
- Runtime-loaded config, storage, WebSerial/device write, backend/config.pb
  write behavior, and flashing automation remain not implemented.
- No hardware result is recorded in this branch.
- Nunchuk remains NOT_TESTED.
