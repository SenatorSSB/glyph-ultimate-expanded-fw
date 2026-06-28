# Diagnostic Active Storage Published Build Report

status: LOCAL_BUILD_REPORT

branch: `runtime-config-diagnostic-active-storage-published`

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

- Dedicated active storage is populated from
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Dedicated active storage is validated and point/table-equivalence checked
  before publication.
- Published active view is dedicated active storage when validation/equivalence
  succeeds.
- Fallback active view is `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Candidate view is not active.
- Candidate-owned table pointers are not active.
- Active behavior changed: `true`.
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
| `.pio/build/glyph_mk6/firmware.uf2` | `798208` | `bb8d97e965ec7b36d6bd0acdfd63124be1351bb3f303fa6f2085957056fb07e4` |
| `.pio/build/glyph_mk6/firmware.elf` | `5408124` | `4eb28572af7c47203d80a7546fda14e6bdeea0dd53fbcb10cfd237d7d07f973a` |
| `.pio/build/glyph_mk6/firmware.bin` | `398852` | `8b7b017a061d16ab69c74c2c147935287cc671c82b419f6e1190b9636501e7a3` |

## Hardware

No hardware result is claimed by this build report.

hardware_test_required_before_merge: true

Hardware PASS is required before merge for this diagnostic because the active
view changes to dedicated active storage when validation/equivalence succeeds.
Nunchuk remains NOT_TESTED.
