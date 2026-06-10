# Diagnostic Parsed Candidate Present, Source-Owned Published Build Report

status: LOCAL_BUILD_REPORT

branch: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published`

baseline branch: `configurator`

## Build Command

Canonical command:

Canonical command: pio run -e glyph_mk6

```bash
pio run -e glyph_mk6
```

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

- Parsed candidate machinery is source-present and initialized.
- Candidate parser bridge is source-present.
- Candidate materialization is source-present.
- Candidate equivalence validation is source-present.
- Published active view remains source-owned baseline.
- Candidate view is not active.
- `UpdateAnalogOutputs(...)` binds runtime config through
  `ResolveActiveRuntimeConfig()`.
- `ResolveActiveRuntimeConfig()` dereferences only
  `GetActiveRuntimeConfigState().active_view`.

## Artifact Notes

Artifact hashes are local observations only, not checker gates.

`artifact_hashes_are_checker_gate`: `false`

Local artifact observations:

| Artifact | SHA-256 |
| --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | `e0e412eee7a35dda44090a8a5e60a4e9e50d878700cd9e459c8480e9e1735cc1` |
| `.pio/build/glyph_mk6/firmware.elf` | `b2c83e0ccdacdf50fb138a3ad527fc3d76407d8fca7f33cbd873e7eda4741597` |
| `.pio/build/glyph_mk6/firmware.bin` | `74eda651dd5b1ee14c09919654ea360490d24d34dd5c49a98c0452dcf134044c` |

## Hardware

No hardware result is claimed by this build report. Hardware testing is still
required. Nunchuk remains NOT_TESTED.
