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
- Candidate validation and source-owned equivalence validation are present.
- Candidate active publication is enabled only after validation/equivalence
  success.
- Published active view falls back to
  `kSourceOwnedCurrentBaselineRuntimeConfig` if validation or equivalence fails.
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
| `.pio/build/glyph_mk6/firmware.uf2` | `ba519464a14f11909c8f85c7964e3a2b55db1747e8f53d05da1735979f13685f` |
| `.pio/build/glyph_mk6/firmware.elf` | `f93d212caa80a4c40d17ce0b3f0bf06e8d2b766ffc32b73ff56461ab9314d00b` |
| `.pio/build/glyph_mk6/firmware.bin` | `d9105e4137e848ce25c2e286ecf73851dc2db3355ae720f7b8f20f2afb67cb29` |

## Hardware

No hardware result is claimed by this build report. Hardware testing is still
required. Nunchuk remains NOT_TESTED.
