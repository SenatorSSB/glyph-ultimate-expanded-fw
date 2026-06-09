# Phase 7A Diagnostic D5A-N1: Direct Canonical Source-Owned View After Parse Gate

status: DIAGNOSTIC_D5A_N1_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`

base branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

diagnostic target:
remove the separate parse-status alias and apply parse-status-gated source-owned
runtime-config selection directly to `kSourceOwnedCurrentBaselineRuntimeConfig`.

## Hypothesis Focus

The D5A branch reproduced RF5/RF6 disconnects in previous hardware attempts. D5A-N1 tests a narrower hypothesis: if we remove the separate
`kPhase7AD5AParseStatusGatedRuntimeConfigView` alias and return
`kSourceOwnedCurrentBaselineRuntimeConfig` directly after `ParseStatus::Ok` and
validation in `ResolveActiveRuntimeConfig()`, does the disconnect disappear?

## Scope (What is kept)

- D2B retained payload bytes (`kPhase7AD2BRetainedPayloadAnchor`).
- D3 global/static parser result (`kPhase7AD3GlobalParseResult`).
- resolver call from `UpdateAnalogOutputs(...)`.
- parse-status gate remains in resolver.

## Scope (What is changed)

- remove `kPhase7AD5AParseStatusGatedRuntimeConfigView`.
- in resolver, return `kSourceOwnedCurrentBaselineRuntimeConfig` directly after
  parse-status+validation check.

Do not add parsed table materialization.

No additional parsed payload data path, no runtime storage, no runtime config
write behavior, and no firmware flashing automation are introduced.

## Resolver Rule

```cpp
const RuntimeConfigView& ResolveActiveRuntimeConfig() {
    if (
        kPhase7AD3GlobalParseResult.status == UltimateRuntimeConfigParser::ParseStatus::Ok &&
        ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)
    ) {
        return kSourceOwnedCurrentBaselineRuntimeConfig;
    }

    return kKnownGoodRuntimeConfig;
}
```

## Guardrails

- D2B retained payload bytes remain.
- D3 global/static parse result remains.
- resolver read of parse status stays (`kPhase7AD3GlobalParseResult.status`).
- `UpdateAnalogOutputs(...)` still uses
  `ResolveActiveRuntimeConfig()`.
- parsed-table materialization is still not added.
- no true parsed-result data routing.
- no table value changes.
- no parsed table/copy of data introduced in firmware source.
- `UpdateDigitalOutputs(...)` unchanged.
- no RF5/RF6/LT6 source expressions changed.
- no storage/webserial/device-write/flashing automation paths.
- no hardware result claim in this branch.
- nunchuk remains not_tested.

## Evidence Intent

This branch is evidence-only and is not a merge candidate.

- If D5A-N1 passes, the previous parse-path alias/copy was likely not the
  cause.
- If D5A-N1 fails, parse-status-gated source-owned routing (still via
  `ResolveActiveRuntimeConfig()`) remains in scope for the failure mechanism.

## Build And Hardware Evidence

Build report:
`docs/runtime_config/phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.md`

Build report JSON:
`docs/runtime_config/fixtures/phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.json`

Hardware plan:
`docs/calibration/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.json`

## Hardware Requirement

- hardware result required before conclusion.
- this branch records no hardware result.
- no root-cause claim.
- focus of required hardware checks:
  RF5, RF6, and LT6 disconnect reproduction.
