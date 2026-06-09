# Phase 7A Diagnostic D5: Parsed-Result Runtime Routing

status: DIAGNOSTIC_D5_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

base branch: `phase7a-diagnostic-d3-global-parse-result-only`

diagnostic target:
route analog runtime-config lookup through the parsed-result resolver-selected
view with no storage, write, flashing, or user/device runtime-loaded config.

## Target Question

Does using the parsed result as the active runtime-config view in
`UpdateAnalogOutputs(...)`, with no storage/write/flashing behavior, reproduce
the RF5/RF6 disconnect?

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

- D5 keeps the D2B retained payload symbol:
  `kPhase7AD2BRetainedPayloadAnchor`.
- D5 keeps the D3 global/static parse result:
  `kPhase7AD3GlobalParseResult`.
- Exact parser call remains:
  `UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload(kPhase7AD2BRetainedPayloadAnchor, UltimateRuntimeConfigParser::kPayloadSize)`.
- D5 adds the source-local parsed-equivalent runtime view:
  `kPhase7AD5ParsedRuntimeConfigView`.
- D5 adds the source-local resolver:
  `ResolveActiveRuntimeConfig()`.
- `UpdateAnalogOutputs(...)` changes only the local runtime-config binding from
  the direct source-owned current-baseline selection to:
  `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`

The existing parser result shape records status and counts; it does not
materialize a separate table array. D5 therefore does not change parser
semantics. The resolver uses the D3 parse status as the selection gate and
routes to a source-local parsed-equivalent view that references the existing
source-owned baseline tables. No table values are changed.

## Resolver Logic

Exact parsed-result selection rule:

```cpp
if (
    kPhase7AD3GlobalParseResult.status == UltimateRuntimeConfigParser::ParseStatus::Ok &&
    ValidateRuntimeConfigView(kPhase7AD5ParsedRuntimeConfigView)
) {
    return kPhase7AD5ParsedRuntimeConfigView;
}
```

Exact fallback rule:

```cpp
return ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)
    ? kSourceOwnedCurrentBaselineRuntimeConfig
    : kKnownGoodRuntimeConfig;
```

The parsed-result route is selected only when the retained payload parses
successfully and the selected runtime-config view validates.

## Guardrails

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
so a later `.uf2`, `.elf`, or `.bin` hash drift must not fail the D5 checker.

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

- If D5 passes, the failed branch likely depended on something more specific
  than parsed-result routing alone.
- If D5 fails, parsed-result runtime routing becomes a strong suspect and
  should be narrowed further before any repair.

This branch is evidence-producing only and is not a merge candidate. Hardware
result must be recorded separately before drawing any activation conclusion.
