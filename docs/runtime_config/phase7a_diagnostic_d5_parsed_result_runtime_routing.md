# Phase 7A Diagnostic D5A: Parse-Status-Gated Source-Owned Runtime Routing

status: DIAGNOSTIC_D5A_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

base branch: `phase7a-diagnostic-d3-global-parse-result-only`

diagnostic target:
route analog runtime-config lookup through a resolver path gated by the global
parse status, while still returning source-owned current-baseline equivalent
runtime-config data.

## Truthful Scope Correction

D5A is not true parsed-result data routing.

The parser result shape in `src/modes/UltimateRuntimeConfigParser.hpp` is:

```cpp
struct ParseResult {
    ParseStatus status;
    size_t table_count;
    size_t point_count_per_table;
};
```

`ParseResult` supplies status/count metadata only. It does not expose or
materialize a parsed `RuntimeConfigView`, parsed runtime tables, or parsed table
data. The `RuntimeConfigView` returned by the D5A resolver is a source-owned
current-baseline equivalent alias, selected only when the retained payload parse
status is `Ok` and the alias view validates.

True parsed table materialization/routing is deferred to a possible D5B.

## Target Question

Does the combination of D2B retained payload bytes, D3 global/static parser
initialization, a resolver/reference path, and parse-status-gated runtime
analog routing through source-owned baseline-equivalent data reproduce the
RF5/RF6 disconnect?

## Prior Evidence

- D2B passed: retained payload bytes only; no parser call; no global
  `ParseResult`; no resolver; RF5/RF6 did not disconnect; H2 reduced in
  likelihood.
- D3 passed: retained payload bytes; global/static parse result; parser called
  by global/static initialization; no runtime resolver; no runtime output
  routing to parsed result; RF5/RF6 did not disconnect; H1/H4 reduced in
  likelihood.
- D4 passed: resolver/reference wrapper only; no parser call; no global
  `ParseResult`; no compiled payload; RF5/RF6 did not disconnect; H3 reduced in
  likelihood.

## Source Delta

- D5A keeps the D2B retained payload symbol:
  `kPhase7AD2BRetainedPayloadAnchor`.
- D5A keeps the D3 global/static parse result:
  `kPhase7AD3GlobalParseResult`.
- Exact parser call remains:
  `UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload(kPhase7AD2BRetainedPayloadAnchor, UltimateRuntimeConfigParser::kPayloadSize)`.
- D5A adds the source-local source-owned alias view:
  `kPhase7AD5AParseStatusGatedRuntimeConfigView`.
- D5A adds the source-local resolver:
  `ResolveActiveRuntimeConfig()`.
- `UpdateAnalogOutputs(...)` changes only the local runtime-config binding from
  the direct source-owned current-baseline selection to:
  `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`

D5A does not change parser semantics, does not materialize parsed tables, and
does not change table values.

## Resolver Logic

Exact parse-status-gated source-owned selection rule:

```cpp
if (
    kPhase7AD3GlobalParseResult.status == UltimateRuntimeConfigParser::ParseStatus::Ok &&
    ValidateRuntimeConfigView(kPhase7AD5AParseStatusGatedRuntimeConfigView)
) {
    return kPhase7AD5AParseStatusGatedRuntimeConfigView;
}
```

Exact fallback rule:

```cpp
return ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)
    ? kSourceOwnedCurrentBaselineRuntimeConfig
    : kKnownGoodRuntimeConfig;
```

The source-owned alias view is selected only when the retained payload parses
successfully and the alias runtime-config view validates.

## Guardrails

- no parsed `RuntimeConfigView` in `ParseResult`;
- no parsed table materialization;
- no true parsed-result data routing;
- no storage/config.bin/Persistence;
- no runtime-loaded config from device/user storage;
- no WebSerial/device write;
- no runtime-config command IDs;
- no firmware flashing automation;
- no new payload bytes beyond the D2B retained payload;
- no duplicate payload array;
- no table value change;
- no RF5/RF6 source-expression change;
- no `UpdateDigitalOutputs(...)` change;
- no behavioral claim before hardware test;
- no nunchuk validation claim.

Artifact hashes are local observations only and are not a checker gate.
Firmware build artifacts are not byte-stable across rebuilds in this workflow,
so a later `.uf2`, `.elf`, or `.bin` hash drift must not fail the D5A checker.

## Build And Hardware Evidence

Build report:
`docs/runtime_config/phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.md`

Build report JSON:
`docs/runtime_config/fixtures/phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.json`

Hardware plan:
`docs/calibration/glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.json`

## Hardware And Nunchuk Scope

- hardware result required before conclusion;
- hardware-result claim: none;
- nunchuk status: `not_tested`;
- no nunchuk validation is claimed.

## Diagnostic Interpretation

- If D5A passes, the failed branch likely depended on something more specific
  than parse-status-gated source-owned runtime routing alone.
- If D5A fails, the combination of global parser initialization,
  parse-status gate, resolver path, and runtime analog routing becomes a strong
  suspect and should be narrowed further before any repair.
- True parsed-result table-data routing remains untested and is deferred to a
  possible D5B if needed.

This branch is evidence-producing only and is not a merge candidate. Hardware
result must be recorded separately before drawing any activation conclusion.
