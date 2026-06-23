# Active Storage Publication Model Build Report

status: LOCAL_BUILD_REPORT

branch: `runtime-config-active-storage-publication-model`

baseline branch: `configurator`

## Build Command

Canonical command: pio run -e glyph_mk6

```bash
pio run -e glyph_mk6
```

Canonical command available in this environment: `false`

Canonical command failure: `zsh:1: command not found: pio`

Fallback command if `pio` is unavailable:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

Local command used in this environment:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

Result: PASS.

## Source Summary

- Dedicated active storage scaffolding is source-present.
- Candidate buffer is not active buffer.
- Candidate view is not active.
- Dedicated active storage is not active.
- Published active view remains `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Active behavior changed: `false`.
- Parser payload path implemented: `false`.
- `UpdateAnalogOutputs(...)` binds runtime config through
  `ResolveActiveRuntimeConfig()`.
- `ResolveActiveRuntimeConfig()` dereferences only
  `GetActiveRuntimeConfigState().active_view`.

## Artifact Notes

Artifact hashes are local observations only, not checker gates.

`artifact_hashes_are_rebuild_stable`: `false`

`artifact_hashes_are_checker_gate`: `false`

Local artifact observations:

| Artifact | Size bytes | SHA-256 |
| --- | ---: | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | `792576` | `5e16f0b68a4ff3af901fba6822b0c28f80fd79ccbadaaf84cc25ee66e11693e1` |
| `.pio/build/glyph_mk6/firmware.elf` | `5407708` | `d73daf419209ac14c1f7dfe4eaae3ffe19e507abfad8bb5811d0326c27496468` |
| `.pio/build/glyph_mk6/firmware.bin` | `396068` | `d2587f8d5e0c90ec2241fe2c624e12300c088905b0668d9c97617c2527016aee` |

## Hardware

No hardware result is claimed by this build report.

hardware_test_required_before_merge: false

No hardware test is required before merge because this branch is
source-scaffold-only and active behavior remains source-owned baseline.
Nunchuk remains NOT_TESTED.
