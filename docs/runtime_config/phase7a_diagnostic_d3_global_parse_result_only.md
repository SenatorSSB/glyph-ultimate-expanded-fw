# Phase 7A Diagnostic D3: Global Parse Result Only

status: DIAGNOSTIC_D3_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d3-global-parse-result-only`

base branch: `phase7a-diagnostic-d2b-retained-payload-bytes`

diagnostic target:
global/static parser initialization only.

## Purpose

D3 isolates the global/static parser initialization result from the failed
Phase 7A compiled-payload activation branch. It keeps the D2B retained payload
bytes and adds only a global parse-result object initialized at startup by
calling the existing parser.

Target question:
does adding only the global/static parser initialization result, while keeping
the payload bytes and no runtime resolver/output routing, reproduce the RF5/RF6
disconnect?

## Source Delta

- `src/modes/Ultimate.cpp` declares the existing D2B retained `.incbin` payload
  symbol:
  `kPhase7AD2BRetainedPayloadAnchor`.
- `src/modes/Ultimate.cpp` adds the file-local global parse result:
  `kPhase7AD3GlobalParseResult`.
- Exact parser call:
  `UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload(kPhase7AD2BRetainedPayloadAnchor, UltimateRuntimeConfigParser::kPayloadSize)`.
- Exact payload source used:
  `src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp` retained
  `.incbin` symbol for
  `docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin`.
- No second payload copy is intentionally introduced by D3; the parser input is
  the already retained D2B payload symbol.

## Guardrails

- no runtime resolver;
- no `ResolveActiveRuntimeConfig`;
- no runtime output routing to the parsed result;
- no `UpdateAnalogOutputs(...)` output behavior change;
- no `UpdateDigitalOutputs(...)` edit;
- no RF5/RF6 expression edit;
- no table value change;
- no runtime-loaded config;
- no storage/config.bin/Persistence;
- no WebSerial/device write;
- no runtime-config command IDs;
- no firmware flashing automation;
- no hardware-result claim;
- no nunchuk validation claim.

## Prior Evidence

- D2B retained the full 530-byte payload sequence in the firmware image with no
  parser call, no global parse result, no resolver, and no runtime-output path
  change. The user reported pass, especially RF5/RF6 did not disconnect.
- D4 runtime resolver/reference wrapper only was user-reported pass in separate
  prior evidence. Resolver/reference wrapper alone did not reproduce the
  disconnect.

## Diagnostic Interpretation

- If D3 passes, static/global parser initialization alone is unlikely to be the
  RF5/RF6 disconnect trigger.
- If D3 fails, H1 global/static parser initialization and H4 parser loop/static-init become strong suspects.
- Root cause is not proven until a follow-up narrowing test confirms the exact
  failure mechanism.

## Build And Hardware Evidence

Build report:
`docs/runtime_config/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md`

Build report JSON:
`docs/runtime_config/fixtures/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.json`

Hardware plan:
`docs/calibration/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.json`

This branch is evidence-producing only and is not a merge candidate. Hardware
result must be recorded separately before drawing any activation conclusion.
