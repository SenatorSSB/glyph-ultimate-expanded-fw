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

## Hardware Result Packets

- `glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md` - user-reported GFW3
  runtime remap hardware pass.
- `glyph_ultimate_preservation_hardware_result.md` - user-reported preservation
  pass for applicable non-nunchuk scope.
- `glyph_ultimate_preservation_hardware_result_TEMPLATE.md` - future result
  template.

## Official Configurator Corpus And Source Correction

- `export_corpus/official_glyph_configurator_2026-06-06/manifest.json` -
  official configurator corpus manifest for user-provided JSON fixtures.
- `glyph_official_configurator_corpus_diff_2026-06-06.md` - official corpus
  diff packet.
- `glyph_external_remapper_misattribution_correction_2026-06-06.md` - source
  classification correction and external-remapper quarantine rule.

## Generated-Config / Evaluator / Generated C++ Review Artifacts

- `glyph_identity_runtime_generated_config_prototype_2026-05-28.md` -
  generated-config prototype packet.
- `glyph_identity_runtime_generated_config_evaluator_input_2026-05-28.md` -
  evaluator input validation packet.
- `glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md` -
  generated C++ review artifact.
- `glyph_generated_constants_refactor_readiness_packet_2026-05-28.md` -
  generated constants readiness packet.

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

## Old Roadmap / Readiness Packets

- `glyph_firmware_workstream_roadmap_2026-05-26.md` - dated roadmap index with
  accumulated evidence rows.
- `glyph_next_runtime_change_readiness_index_2026-05-26.md` - older readiness
  index.
- `glyph_preimplementation_go_nogo_index_2026-05-28.md` - preimplementation
  go/no-go packet.
- `glyph_preservation_hardware_readiness_packet_2026-06-06.md` - preservation
  readiness packet.
