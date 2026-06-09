# Runtime Config Docs

Status label: CURRENT.

These packets describe Glyph runtime-config architecture, source authority,
offline fixtures, and future implementation gates. They are design/docs/tools
artifacts unless a specific packet says otherwise.

## Current Phase 6 Boundary

- `phase6_bounded_config_owned_data_architecture.md` - Phase 6 stable firmware
  and bounded config-owned modifier-data architecture; design complete, not
  implemented.
- `phase6_bounded_config_source_authority.md` - Phase 6 source-authority packet
  and inspected source/search record.
- `runtime_config_blockers_1_to_5_decision_packet.md` - proposed decisions for
  storage, parser format, boot/load, fallback/recovery/rollback, and
  WebSerial/device-write authority; all not implemented.
- `phase6_to_phase7_implementation_slice_plan.md` - future implementation
  slices and hardware gates; not an approval to implement.
- `fixtures/phase6_bounded_config_owned_modifier_data_schema_candidate.json` -
  schema/metadata candidate only; not runtime-loaded config.
- `fixtures/phase6_bounded_config_invalid_cases.json` - invalid corpus for
  forbidden config-owned semantics and malformed bounded data claims.

## Existing Runtime-Config Packets

- `phase7a_runtime_config_parser_offline_and_compiled_scaffold.md` - Phase 7A
  offline parser/generator/oracle/checker/storage-simulator foundation with a
  compiled but not runtime-active firmware parser scaffold.
- `phase7a_compiled_activation_failure_analysis_2026-06-08.md` - failure
  analysis only for the Phase 7A compiled/test payload activation hardware
  failure; no fix implemented and failed activation branch must not merge.
- `phase7a_runtime_config_activation_repair_minimal.md` - minimal source-level
  repair packet for Option A. This branch uses build-time/source validation only,
  records no runtime behavior changes, and marks the failed activation branch as
  abandoned.
- `phase7a_build_size_and_map_baseline_2026-06-08.md` - build-size/map/artifact
  baseline recorded from a known-good `configurator` lineage firmware build.
- `fixtures/phase7a_build_size_and_map_baseline_2026-06-08.json` - machine-readable
  artifact table for the build-size baseline.
- `tools/check_glyph_phase7a_build_size_and_map_baseline.py` - read-only checker
  for the Phase 7A build-size and map baseline packet/fixture.
- `phase7a_activation_failure_root_cause_analysis_2026-06-09.md` - root-cause
  analysis packet for the failed Phase 7A compiled-payload activation branch;
  analysis-only, no fix implemented, root cause not proven.
- `fixtures/phase7a_activation_failure_root_cause_analysis_2026-06-09.json` -
  machine-readable evidence fixture for the Phase 7A activation failure
  root-cause analysis.
- `phase7a_activation_failure_diagnostic_build_matrix.md` - diagnostic build
  matrix plan for isolating the activation failure cause; plan-only and not
  implemented.
- `phase7a_diagnostic_d4_runtime_resolver_only.md` - runtime-resolver-only
  diagnostic packet for RF5/RF6 disconnect isolation; no parser call or
  compiled payload usage.
- `phase7a_diagnostic_d4_runtime_resolver_only_build_report_2026-06-09.md` -
  D4 build report (diagnostic-only, no parser/compile-payload changes).
- `fixtures/phase7a_diagnostic_d4_runtime_resolver_only_build_report_2026-06-09.json` -
  machine-readable D4 build report metadata.
- [`../calibration/glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.md`](../calibration/glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.md) -
  D4 user-reported hardware result for the runtime-resolver-only branch.
- `../../tools/check_glyph_phase7a_diagnostic_d4_hardware_result.py` - D4
  hardware-result checker for branch/result/documentation scope.
- `tools/check_glyph_phase7a_diagnostic_d4_runtime_resolver_only.py` - D4
  diagnostic checker for resolver-only source/doc/build constraints.
- `tools/check_glyph_phase7a_activation_failure_root_cause_analysis.py` -
  read-only checker for the root-cause analysis packet, fixture, diagnostic
  matrix, and no-firmware-source-change guardrail.
- `phase7a_safer_activation_repair_plan.md` - plan-only next-branch strategy
  for a safer minimal activation repair attempt; not implemented.
- `runtime_config_semantics_evaluator_bridge.md`
- `runtime_loaded_config_schema_design.md`
- `firmware_interpreter_architecture_spec.md`
- `runtime_config_storage_fallback_source_authority.md`
- `runtime_config_storage_fallback_architecture.md`
- `runtime_config_binary_representation_design.md`
- `runtime_config_firmware_binary_parser_source_authority.md`
- `runtime_config_firmware_binary_parser_integration_plan.md`
- `runtime_config_manual_load_path_plan.md`
- `runtime_config_webserial_device_write_source_authority.md`
- `runtime_config_device_write_safety_plan.md`
- `runtime_config_flashing_automation_safety_boundary.md`

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware parser integration/runtime activation is not implemented; Phase 7A
  adds only a compiled inert parser scaffold.
- Phase 7A compiled/test payload activation failed hardware testing on its
  activation branch and is recorded as failure analysis only here.
- Phase 7A activation root cause is not proven; the failed activation branch
  must remain abandoned and future runtime activation requires hardware-gated
  diagnostic builds.
- WebSerial/device write is not implemented.
- Firmware flashing automation is not implemented.
- Official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
