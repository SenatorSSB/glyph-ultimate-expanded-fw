# Phase 7A Diagnostic D2: Compiled Payload Header Only

status: DIAGNOSTIC_D2_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d2-compiled-payload-header-only`

base branch: `configurator`

purpose:
isolate static image/rodata/layout effects from the compiled Phase 7A baseline
payload bytes/header without parser/runtime-activation behavior.

D2 mode selected:
`D2A` — header present only, not linked from firmware translation units.

Selected payload retention behavior:
no

firmware image retention intent:
the added header is visible in repo source only and is not expected to be retained
in the firmware image in this branch because it is not included by any compiled
firmware source file.

build report path:
`docs/runtime_config/phase7a_diagnostic_d2_compiled_payload_header_only_build_report_2026-06-09.md`

hardware plan path:
`docs/calibration/glyph_phase7a_diagnostic_d2_compiled_payload_header_only_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d2_compiled_payload_header_only_hardware_plan_2026-06-09.json`

## Source Delta Summary

- Added `src/modes/UltimateRuntimeConfigCompiledPayload.hpp` with:
  - fixture path constant
  - SHA-256 constant
  - payload size constant
  - byte array exactly matching
    `docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin`
- No `Ultimate.cpp` include or compile-unit change.
- No parser invocation in runtime code.
- No global parse-result declaration.
- No runtime resolver addition.
- No `UpdateAnalogOutputs(...)` or runtime-config path edit.
- No storage/read/write path edits.

## D2 Guardrails

- no parser call
- no global `ParseResult`
- no `ResolveActiveRuntimeConfig`
- no runtime behavior change intended
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation

## Evidence Claims

- This diagnostic branch is evidence-producing only and is not merge candidate
  until a separate hardware-result result branch records a result.
- No runtime behavior change is intended in this branch.
- No nunchuk validation is performed in this diagnostic branch.
- This branch does not claim firmware pass or compatibility claims.
- Hardware result is required before any conclusion.
