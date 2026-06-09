# Phase 7A Diagnostic D5A-N2: Resolver Without Parse-Status Hot-Path Read

status: DIAGNOSTIC_D5A_N2_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read`

base branch: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`

diagnostic target:
keep the parse-result and resolver routing scope from D5A-N1 but remove any
runtime hot-path read/branch on `kPhase7AD3GlobalParseResult.status`.

## Hypothesis Focus

D5A-N1 kept the D2B retained payload and D3 global parse result, kept
`ResolveActiveRuntimeConfig()` in the analog path, and still disconnected RF5/RF6/LT6.

This branch tests whether the disconnect is specifically caused by reading or
branching on `kPhase7AD3GlobalParseResult.status` in runtime analog hot path.

## Scope (What is kept)

- D2B retained payload bytes (`kPhase7AD2BRetainedPayloadAnchor`).
- D3 global/static parse result (`kPhase7AD3GlobalParseResult`).
- resolver call from `UpdateAnalogOutputs(...)`.
- direct canonical source-owned runtime-config return contract.
- global parse-result parse call remains only as global/static initialization for future
  diagnostics and not in hot path.
- no parsed table materialization.
- no storage/write/WebSerial/flashing changes.
- no RF5/RF6/LT6 expression or `UpdateDigitalOutputs(...)` behavior changes.

## Scope (What is changed)

- remove runtime hot-path read/branch on `kPhase7AD3GlobalParseResult.status`.
- `ResolveActiveRuntimeConfig()` now returns the canonical source-owned config via
  validation fallback, without parse-status reads:

```cpp
const RuntimeConfigView& ResolveActiveRuntimeConfig() {
    if (ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)) {
        return kSourceOwnedCurrentBaselineRuntimeConfig;
    }
    return kKnownGoodRuntimeConfig;
}
```

- keep `kPhase7AD5AParseStatusGatedRuntimeConfigView` removed.
- keep no separate runtime-config alias/copy.

No parsed data materialization is added.

## Guardrails

- D2B retained payload bytes remain.
- D3 global/static parse result remains.
- `UpdateAnalogOutputs(...)` still uses
  `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`.
- Resolver returns source-owned canonical config with fallback and does not read
  `kPhase7AD3GlobalParseResult.status`.
- no parsed-table materialization added.
- no storage/write/WebSerial/flashing.
- no hardware result claim in this branch.
- no nunchuk claim.

## Evidence Intent

This branch is evidence-only and not a merge candidate.

- If D5A-N2 passes, runtime hot-path parse-status read in resolver was the likely
  trigger.
- If D5A-N2 fails, the combination of:
  - D3 global parse result presence and
  - resolver call from `UpdateAnalogOutputs(...)`
  remains suspect even without parse-status hot-path reads.

## Build and Hardware Evidence

Build report:
`docs/runtime_config/phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.md`

Build report JSON:
`docs/runtime_config/fixtures/phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.json`

Hardware plan:
`docs/calibration/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.json`

## Hardware Requirement

- hardware result required before conclusion.
- this branch records no hardware result.
- no hardware-result claim.
- nunchuk not tested.
- no root-cause claim.
