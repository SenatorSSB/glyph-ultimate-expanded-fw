# Diagnostic Source-View Candidate Published Build Report

status: LOCAL_BUILD_REPORT

branch: `runtime-config-diagnostic-source-view-candidate-published`

baseline branch: `configurator`

## Build Command

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

- Parser payload activation is disabled and absent.
- `ParseUltimateRuntimeConfigPayload(...)` is not called.
- Source-owned parsed diagnostic payload bytes are not present.
- Candidate state is materialized from
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Source-view candidate materialization/publication is namespace-scope
  initialized before active resolver use.
- Candidate validation and source-owned equivalence validation are present.
- Candidate active publication is enabled only after validation/equivalence
  success.
- Published active view falls back to
  `kSourceOwnedCurrentBaselineRuntimeConfig` if validation or equivalence fails.
- `UpdateAnalogOutputs(...)` binds runtime config through
  `ResolveActiveRuntimeConfig()`.
- `ResolveActiveRuntimeConfig()` dereferences only
  `GetActiveRuntimeConfigState().active_view`.
- Active resolver chain:
  `UpdateAnalogOutputs -> ResolveActiveRuntimeConfig -> GetActiveRuntimeConfigState -> gActiveRuntimeConfigState.active_view`.
- Active resolver chain does not first-trigger candidate materialization.

## Artifact Notes

Artifact hashes are local observations only, not checker gates.

`artifact_hashes_are_checker_gate`: `false`

Local artifact observations:

| Artifact | SHA-256 |
| --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | `0be16e660e3fa9b180201eb2630d77eb9a065b1c3312f8e1943e9bb8f5fef229` |
| `.pio/build/glyph_mk6/firmware.elf` | `9f3124c17807ce5f383ef26d87005b9a373fc1844d421ee9cbee020590d90596` |
| `.pio/build/glyph_mk6/firmware.bin` | `d761894b49e085dab6ff88cbd34b52ae1751dd4182d4ee3af80e09f9206caa28` |

## Hardware

No hardware result is claimed by this build report. Hardware testing is still
required. Nunchuk remains NOT_TESTED.
