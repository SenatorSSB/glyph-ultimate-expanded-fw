# Phase 7A Diagnostic D4: Runtime Resolver Only

status: DIAGNOSTIC_D4_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d4-runtime-resolver-only`

base branch: `configurator`

D4 mode selected:
`D4` — resolver wrapper around the existing source-owned runtime-config view, with no parser and no compiled payload.

source delta summary:
- no `src/modes/UltimateRuntimeConfigCompiledPayload.hpp`
- no `src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp`
- added local resolver wrapper in `src/modes/Ultimate.cpp`:
  - `const RuntimeConfigView& ResolveActiveRuntimeConfig() {\
      return ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)
          ? kSourceOwnedCurrentBaselineRuntimeConfig
          : kKnownGoodRuntimeConfig;\
    }`
- replaced the local runtime-config conditional in `UpdateAnalogOutputs(...)` with
  `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`
- no parser call
- no global `ParseResult`
- no `kPhase7ACompiledPayloadParseResult`
- no `UpdateDigitalOutputs(...)` edits
- no runtime-config/runtime storage/write/WebSerial/flash behavior edits
- no storage/runtime command IDs introduced
- no runtime behavior change intended
- no compiled payload header

exact resolver logic:
`ResolveActiveRuntimeConfig()` returns `kSourceOwnedCurrentBaselineRuntimeConfig` when
`ValidateRuntimeConfigView(...)` succeeds; otherwise it returns `kKnownGoodRuntimeConfig`.

exact `UpdateAnalogOutputs(...)` callsite change:
from `const RuntimeConfigView &runtime_config = ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig) ? ...` to
`const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`

guardrails and restrictions:
- no parser call
- no parsed payload bytes retained in firmware image
- no parsed payload header
- no payload anchor
- no parser/runtime-activated global parse state in firmware source
- no global parse result
- no runtime-config storage/read/runtime-config persistence
- no WebSerial/device write
- no firmware flashing automation
- no runtime-config command IDs
- no nunchuk validation
- no hardware-result claim on this branch
- this branch is evidence-producing only

build report path:
`docs/runtime_config/phase7a_diagnostic_d4_runtime_resolver_only_build_report_2026-06-09.md`

hardware plan path:
`docs/calibration/glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_plan_2026-06-09.json`

This diagnostic branch is evidence-producing only and is not a merge candidate into
`configurator` until a separate hardware-result branch records and audits results.

This branch is not hardware-result.

Diagnostic interpretation:
- if D4 later passes, resolver/reference path alone is unlikely to be the RF5/RF6 disconnect cause;
- if D4 later fails, H3 resolver/reference path is a strong suspect.
