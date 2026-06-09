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
- `phase7a_diagnostic_d2_compiled_payload_header_only.md` - diagnostic D2 packet for
  compiled payload header-only branch (`D2A`) isolation; no parser/parse-result/
  resolver/runtime behavior changes.
- `phase7a_diagnostic_d2b_retained_payload_bytes.md` - diagnostic D2B packet for
  payload retention verification in firmware image with no runtime parser or
  resolver usage.
- `phase7a_diagnostic_d3_global_parse_result_only.md` - diagnostic D3 packet
  for global/static parser initialization using the retained D2B payload symbol,
  with no resolver and no runtime output routing to the parsed result.
- `phase7a_diagnostic_d5_parsed_result_runtime_routing.md` - diagnostic D5A
  packet for parse-status-gated source-owned runtime routing. This is not true
  parsed-result table-data routing; D5B is required if true parsed data routing
  needs to be tested.
- `phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate.md` - diagnostic
  D5A-N1 packet for direct source-owned baseline view return after parse gate.
- `phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read.md` - diagnostic
  D5A-N2 packet for direct source-owned baseline view return after removing parse-status
  hot-path reads from runtime resolver.
- `docs/calibration/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.md`
  - user-reported D5A-N1 hardware failure result; same disconnects as D5A,
    RF5/RF6/LT6 disconnect class reproduced, and parse-status hot-path read
    remains the primary suspect.
- `docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.json`
  - machine-readable D5A-N1 hardware failure fixture.
- `glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.md`
  - user-reported D2B hardware result pass; D2B retained full payload bytes
    and user reported pass, which reduces payload-only/static rodata
    suspicion. Next diagnostics should isolate parser static initialization and
    resolver path.
- `glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.md`
  - user-reported D3 hardware result pass; global/static parser initialization
    alone did not reproduce the RF5/RF6 disconnect. D2B, D3, and D4 each
    passed in isolation, so the next diagnostic should focus on controlled
    combinations rather than a single isolated component.
- `phase7a_diagnostic_d2_compiled_payload_header_only_build_report_2026-06-09.md` -
  D2 build report with artifact and size/hash delta metadata.
- `phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md` -
  D2B build report with retention verification metadata and size/hash deltas vs
  baseline and D2A.
- `phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md` -
  D3 build report with local artifact observations, retained payload scan, and
  guardrails for global/static parser initialization only.
- `phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.md` -
  D5A build report with local artifact observations, parse-status-gated
  source-owned runtime-routing guardrails, and explicit non-stable
  artifact-hash caveat.
- `phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.md` -
  D5A-N1 build report with local artifact observations for direct
  source-owned baseline view routing after parse status gate.
- `phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.md` -
  D5A-N2 build report with local artifact observations for direct
  source-owned baseline view routing after removing parse-status hot-path reads.
- `phase7a_diagnostic_d2_compiled_payload_header_only_hardware_plan_2026-06-09.md` -
  D2 diagnostic hardware plan template for required rows (all `NOT_TESTED`).
- `glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_plan_2026-06-09.md` -
  D2B hardware plan template (all `NOT_TESTED`) with payload-retention evidence
  intent.
- `glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.md` -
  D3 hardware plan template (all `NOT_TESTED`) for RF5/RF6 disconnect isolation
  with global/static parser initialization only.
- `glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.md` -
  D5A hardware plan template (all `NOT_TESTED`) for parse-status-gated
  source-owned runtime routing after D2B, D3, and D4 passed in isolation.
- `glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.md` -
  D5A-N1 hardware plan template (all `NOT_TESTED`) for direct source-owned
  view selection after parse-status gate.
- `glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.md` -
  D5A-N2 hardware plan template (all `NOT_TESTED`) for removing parse-status
  hot-path read from resolver path.
- `fixtures/phase7a_diagnostic_d2_compiled_payload_header_only_build_report_2026-06-09.json` -
  machine-readable D2 build report metadata and artifact deltas.
- `fixtures/phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.json` -
  machine-readable D2B build report metadata and artifact deltas.
- `fixtures/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.json` -
  machine-readable D3 build report metadata and artifact deltas.
- `fixtures/phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.json` -
  machine-readable D5A build report metadata with artifact hashes as local
  observations only.
- `fixtures/phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.json` -
  machine-readable D5A-N1 build report metadata with local artifact observations
  and non-checker artifact hashes.
- `fixtures/phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.json` -
  machine-readable D5A-N2 build report metadata with local artifact observations
  and non-checker artifact hashes.
- `tools/check_glyph_phase7a_diagnostic_d2_compiled_payload_header_only.py` - read-only
  checker for D2 packet/report/plan/header retention guardrails.
- `tools/check_glyph_phase7a_diagnostic_d2b_retained_payload_bytes.py` - read-only
  checker for D2B retention-in-firmware validation.
- `tools/check_glyph_phase7a_diagnostic_d3_global_parse_result_only.py` - read-only
  checker for D3 global/static parser initialization scope and no-runtime-routing
  guardrails.
- `tools/check_glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing.py` -
  read-only checker for D5A parse-status-gated source-owned routing source,
  docs, report, hardware-plan, and no storage/write/flashing guardrails.
- `tools/check_glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate.py` -
  read-only checker for D5A-N1 scope, resolver behavior, and guardrails.
- `tools/check_glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read.py` -
  read-only checker for D5A-N2 scope, resolver behavior, and guardrails.
- `tools/check_glyph_phase7a_diagnostic_d5a_n1_hardware_failure.py` - read-only
  checker for D5A-N1 hardware-failure result guardrails.
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
