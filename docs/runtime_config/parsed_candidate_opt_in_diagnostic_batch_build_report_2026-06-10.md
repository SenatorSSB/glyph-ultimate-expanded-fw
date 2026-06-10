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
| UF2 | `.pio/build/glyph_mk6/firmware.uf2` | 798720 | `eb8e9efc58fa828b06b6d5701bec7996ad6eadea93f1dc9b5f090dbd898c0446` |
| ELF | `.pio/build/glyph_mk6/firmware.elf` | 5408232 | `44acf96c79da3d13c3b9cf1a103f1e170413f055b8ac50a5f76db5bf14aa18fa` |
| BIN | `.pio/build/glyph_mk6/firmware.bin` | 399356 | `d892f21109a98d03537b4fad99498306dd6984acf08d281f18bb984fd1d5fc20` |

## Scope Notes

- The diagnostic opt-in activation flag is enabled.
- The source-owned static parser fixture is materialized into candidate state
  before namespace-scope publication.
- The candidate must prove equivalent to the source-owned baseline before it can
  be accepted.
- Active output generation consumes only the published active view.
- The active hot-path resolver chain no longer first-triggers parser,
  materialization, decision, or publication work.
- Runtime-loaded config, storage, WebSerial/device write, backend/config.pb
  write behavior, and flashing automation remain not implemented.
- No hardware result is recorded in this branch.
- Nunchuk remains NOT_TESTED.
