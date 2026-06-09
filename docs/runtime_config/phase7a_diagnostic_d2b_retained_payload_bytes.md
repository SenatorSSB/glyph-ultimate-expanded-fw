# Phase 7A Diagnostic D2B: Retained Payload Bytes

status: DIAGNOSTIC_D2B_IMPLEMENTED_PENDING_HARDWARE_RESULT

diagnostic branch: `phase7a-diagnostic-d2b-retained-payload-bytes`

base branch: `configurator`

D2 mode selected:
`D2B` — retain compiled payload bytes in firmware image only, with no parser/use
activation.

source delta summary:
- kept `src/modes/UltimateRuntimeConfigCompiledPayload.hpp` from D2A branch
  to preserve payload bytes and metadata;
- added `src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp` as the minimal
  retention anchor with an unused-but-used symbol;
- no changes under `src/modes/Ultimate.cpp`;
- no parser call;
- no global parse result;
- no `ResolveActiveRuntimeConfig`;
- no `UpdateAnalogOutputs` or other output-path changes.

retention mechanism:
- compile-time retention anchor:
  `src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp` defines
  `kPhase7AD2BRetainedPayloadAnchor` in a retained read-only section containing
  the committed payload fixture bytes.

retained payload verification basis:
- build report confirms `payload_bytes_retained_in_firmware_image: true`;
- build report confirms `payload_sequence_scan_performed: true`;
- full committed 530-byte payload sequence is present in
  `.pio/build/glyph_mk6/firmware.bin` and `.pio/build/glyph_mk6/firmware.elf`;
- sequence offsets are recorded in
  `phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md`;
- artifact size deltas vs baseline and D2A are recorded in
  `phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md`;
- retained size is reported as 530 bytes.

build report path:
`docs/runtime_config/phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md`

hardware plan path:
`docs/calibration/glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_plan_2026-06-09.md`

Hardware plan JSON:
`docs/calibration/fixtures/glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_plan_2026-06-09.json`

guardrails and restrictions:
- no parser call;
- no global parse result;
- no runtime resolver;
- no runtime behavior change intended;
- no storage/read/runtime-config persistence;
- no WebSerial/device write;
- no firmware flashing automation;
- no runtime-config runtime activation;
- no `UpdateAnalogOutputs` source-path edits;
- no nunchuk validation claim;
- no hardware-result claim on this branch.

This diagnostic branch is evidence-producing only and is not a merge candidate
into `configurator` until a separate hardware-result branch records results.
This branch is not merge candidate until hardware result is recorded.

This branch is not a hardware-result branch and records no activation conclusion.
