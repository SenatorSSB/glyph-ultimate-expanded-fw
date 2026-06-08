# Calibration Index

Status label: CURRENT.

This grouped index lists key evidence packets. It is not an exhaustive manifest.
Use `find docs/calibration -maxdepth 3 -type f` or the checker scripts in
`tools/` for full discovery.

## Current Authoritative State Packets

- `glyph_post_gfw3_configurator_baseline_2026-06-06.md` - post-GFW3
  `configurator` baseline and non-claims.
- `glyph_roadmap_next_work_index_2026-06-06.md` - machine-checkable next-work
  triage index.
- `glyph_next_user_action_handoff_2026-06-06.md` - user/source-authority/action
  handoff after the docs/tools sequence.

## Public/Manual Workflow Release-Candidate Prep

- `docs/release/public_manual_workflow_release_candidate_plan.md` - plan-only
  public/manual workflow release-candidate boundary and non-claims.
- `docs/release/public_manual_workflow_release_candidate_checklist.md` - release-
  readiness checklist for the manual RC workflow.
- `glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.md`
  - manual RC hardware-test template; not a result.
- `fixtures/glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.json`
  - matching hardware-test template fixture.

## Hardware Result Packets

- `glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md` - user-reported GFW3
  runtime remap hardware pass.
- `glyph_ultimate_preservation_hardware_result.md` - user-reported preservation
  pass for applicable non-nunchuk scope.
- `glyph_generated_constants_phase3_integration_hardware_result_2026-06-07.md`
  - user-reported Phase 3 generated constants firmware-integration hardware
    result.
- `glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`
  - user-reported public/manual workflow release-candidate hardware result for
    applicable doable scope; nunchuk remains NOT_TESTED.
- `fixtures/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.json`
  - matching public/manual workflow RC hardware result fixture.
- `glyph_runtime_config_interpreter_source_baseline_hardware_result_2026-06-07.md`
  - user-reported runtime-config interpreter source-baseline hardware result.
- `glyph_ultimate_preservation_hardware_result_TEMPLATE.md` - future result
  template.

## Official Configurator Corpus And Source Correction

- `export_corpus/official_glyph_configurator_2026-06-06/manifest.json` -
  official configurator corpus manifest for user-provided JSON fixtures.
- `glyph_official_configurator_corpus_diff_2026-06-06.md` - official corpus
  diff packet.
- `glyph_external_remapper_misattribution_correction_2026-06-06.md` - source
  classification correction and external-remapper quarantine rule.

## Offline Official Configurator Export Target Contract

- `docs/export/README.md` - offline-only export-target docs index.
- `docs/export/official_configurator_export_source_authority.md` - source
  authority packet for the official configurator export target.
- `docs/export/official_configurator_export_target_contract.md` - offline
  target contract and stop lines.
- `docs/export/fixtures/official_configurator_export_candidate_preview.json` -
  offline preview fixture; not production export.
- `docs/export/fixtures/official_configurator_export_invalid_cases.json` -
  invalid corpus for the offline target contract.

## Generated-Config / Evaluator / Generated C++ Review Artifacts

- `glyph_identity_runtime_generated_config_prototype_2026-05-28.md` -
  generated-config prototype packet.
- `glyph_identity_runtime_generated_config_evaluator_input_2026-05-28.md` -
  evaluator input validation packet.
- `glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md` -
  generated C++ review artifact.
- `glyph_generated_constants_refactor_readiness_packet_2026-05-28.md` -
  generated constants readiness packet.
- `docs/generated_constants/phase3_generated_constants_contract.md` - Phase 3
  generated C++ constants target and source-diff checker contract.
- `docs/generated_constants/preview/gfw3_generated_constants_preview.json` -
  dry-run preview artifact for the current source-backed baseline.

## Runtime-Loaded Config Design And Blocker Packets

- `glyph_runtime_loaded_config_design_v0_2026-05-28.md` - design-only runtime
  config boundary.
- `glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md` - blocked
  implementation plan.
- `glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.md` - storage
  and interpreter blocker packet.
- `glyph_webserial_transport_blocker_packet_2026-06-03.md` - WebSerial
  transport blocker packet.
- `glyph_protobuf_config_schema_research_packet_2026-06-03.md` - protobuf
  schema research packet.
- `docs/runtime_config/runtime_config_semantics_evaluator_bridge.md` -
  evaluator bridge design-only baseline oracle and negative corpus boundary for
  source-backed docs/tools checks.
- `docs/runtime_config/runtime_loaded_config_schema_design.md` - design-only
  runtime-loaded config schema candidate.
- `docs/runtime_config/firmware_interpreter_architecture_spec.md` - future
  firmware interpreter architecture/spec boundary.
- `docs/runtime_config/fixtures/current_baseline_runtime_config_semantics_bridge.json`
  - metadata fixture for the bridge.
- `docs/runtime_config/fixtures/current_baseline_extracted_config_preview.json`
  - source-backed preview fixture for the current baseline.
- `docs/runtime_config/fixtures/current_baseline_runtime_config_interpreter_source_baseline.json`
  - dedicated source-owned interpreter baseline fixture.
- `docs/runtime_config/fixtures/invalid_runtime_config_semantics_cases.json` -
  offline negative corpus for bridge semantics.
- `docs/runtime_config/runtime_config_storage_fallback_source_authority.md` - Step 10
  source-authority audit packet.
- `docs/runtime_config/runtime_config_storage_fallback_architecture.md` - Step 10
  storage/fallback architecture design boundary.
- `docs/runtime_config/runtime_config_binary_representation_design.md` - Step 11
  offline-only binary representation design.
- `docs/runtime_config/fixtures/current_baseline_runtime_config_binary_preview.json` -
  offline baseline binary preview fixture.
- `docs/runtime_config/fixtures/invalid_runtime_config_binary_cases.json` - offline
  binary invalid-corpus fixture.
- `docs/runtime_config/fixtures/current_baseline_runtime_config_binary_preview.bin` -
  offline baseline binary artifact.
- `tools/glyph_runtime_config_binary_roundtrip.py` - Step 12 offline-only binary
  parser/serializer prototype.
- `tools/check_glyph_runtime_config_storage_fallback.py` - Step 10 fallback
  docs/tools guardrail checker.
- `tools/check_glyph_runtime_config_binary_offline_roundtrip.py` - Step 12
  offline binary round-trip and invalid-corpus checker.
- `docs/runtime_config/runtime_config_firmware_binary_parser_source_authority.md`
  - Step 13 firmware binary/protobuf parser source-authority packet.
- `docs/runtime_config/runtime_config_firmware_binary_parser_integration_plan.md`
  - Step 13 firmware binary/protobuf parser integration plan and stop line.
- `docs/calibration/glyph_runtime_config_firmware_binary_parser_hardware_plan_TEMPLATE.md`
  - future Step 13 hardware plan template; not a result.
- `tools/check_glyph_runtime_config_firmware_binary_parser_plan.py` - Step 13
  firmware binary/protobuf parser plan guardrail checker.
- `docs/runtime_config/runtime_config_webserial_device_write_source_authority.md`
  - Step 15 WebSerial/device-write source-authority packet and implementation
    stop line.
- `docs/runtime_config/runtime_config_manual_load_path_plan.md` - Step 14
  manual config-load source-authority/design packet and implementation stop
  line.
- `docs/runtime_config/runtime_config_device_write_safety_plan.md` - Step 16
  device-write safety plan and implementation stop line.
- `docs/runtime_config/runtime_config_flashing_automation_safety_boundary.md` - Step 17
  flashing safety boundary and implementation stop line.
- `tools/check_glyph_runtime_config_webserial_device_write_source_authority.py`
  - Step 15 WebSerial/device-write source-authority guardrail checker.
- `tools/check_glyph_runtime_config_manual_load_path_plan.py` - Step 14
  manual-load plan guardrail checker.
- `tools/check_glyph_runtime_config_device_write_safety_plan.py` - Step 16
  device-write safety-plan guardrail checker.

## Adapter / Prewrite Gates

- `glyph_adapter_prewrite_blocker_matrix_2026-06-06.md` - write-capable adapter
  blocker matrix.
- `glyph_adapter_prewrite_implementation_gate_2026-06-06.md` - implementation
  gate for adapter/prewrite work.
- `glyph_profile_adapter_prewrite_validation_2026-05-26.md` - read-only
  prewrite validation.

## External-Remapper Quarantined / Historical Docs

These records are quarantined historical evidence unless independently
source-backed.

- `glyph_external_remapper_misattribution_correction_2026-06-06.md` - current
  quarantine rule.
- `glyph_external_remapper_adapter_boundary_2026-06-03.md` - historical
  boundary snapshot.
- `glyph_offline_remapper_experiment_result_2026-06-04.md` - historical
  no-device experiment result, now non-authoritative for official corpus.
- `glyph_offline_remapper_export_loss_gate_2026-06-04.md` - historical
  adapter-blocking export-loss gate.
- `glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md` - clean-room
  planning gate, not implementation.

## Templates

- `glyph_profile_config_export_corpus_manifest_TEMPLATE.json` - export corpus
  manifest template.
- `glyph_ultimate_preservation_hardware_result_TEMPLATE.md` - preservation
  hardware result template.
- `fixtures/glyph_ultimate_preservation_hardware_result_TEMPLATE.json` -
  preservation hardware fixture template.
- `glyph_offline_remapper_result_template_2026-06-03.md` - historical external
  remapper result template.
- `glyph_generated_constants_phase3_integration_hardware_plan_2026-06-07.md` -
  phase 3 generated-constants integration hardware plan template.
- `glyph_runtime_config_interpreter_source_baseline_hardware_plan_2026-06-07.md`
  - Step 9 source-owned runtime-config interpreter hardware plan template.
- `glyph_runtime_config_firmware_binary_parser_hardware_plan_TEMPLATE.md` -
  future Step 13 firmware binary/protobuf parser hardware plan template.
- `fixtures/glyph_runtime_config_interpreter_source_baseline_hardware_plan_2026-06-07.json`
  - Step 9 hardware plan fixture template.
- `fixtures/glyph_runtime_config_interpreter_source_baseline_hardware_result_2026-06-07.json`
  - user-reported runtime-config interpreter hardware result fixture.

## Old Roadmap / Readiness Packets

- `glyph_firmware_workstream_roadmap_2026-05-26.md` - dated roadmap index with
  accumulated evidence rows.
- `glyph_next_runtime_change_readiness_index_2026-05-26.md` - older readiness
  index.
- `glyph_preimplementation_go_nogo_index_2026-05-28.md` - preimplementation
  go/no-go packet.
- `glyph_preservation_hardware_readiness_packet_2026-06-06.md` - preservation
  readiness packet.
