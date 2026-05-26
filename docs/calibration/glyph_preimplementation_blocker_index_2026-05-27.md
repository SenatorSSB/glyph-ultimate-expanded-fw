# Glyph Preimplementation Blocker Index - 2026-05-27

Purpose: consolidated blocker index for the next native Ultimate runtime implementation step.

Scope: docs/checker planning only. No runtime behavior changes.

## Blocker Ledger

### USER_REQUIREMENTS_MISSING

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`
  - `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md`
  - `docs/calibration/glyph_user_requirements_input_packet_2026-05-27.md`
- what would unblock it: user/domain completes required packet fields with explicit target behavior.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `YES`
- blocks hardware preservation claims: `YES` (for any new runtime behavior)
- blocks write-capable adapter work: `YES`

### PRESERVATION_HARDWARE_RESULT_MISSING

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
  - `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
  - `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`
- what would unblock it: completed manual preservation hardware result file with reviewed outcomes.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `NO` (design/docs can proceed)
- blocks hardware preservation claims: `YES`
- blocks write-capable adapter work: `NO`

### EXPORT_CORPUS_ABSENT

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`
  - `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`
  - `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
- what would unblock it: captured corpus manifest/artifacts from target configurator/proto revision.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `NO`
- blocks hardware preservation claims: `NO`
- blocks write-capable adapter work: `YES`

### WRITE_CAPABLE_ADAPTER_NOT_APPROVED

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
  - `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`
- what would unblock it: explicit user/domain approval plus corpus-backed write-policy decision.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `NO`
- blocks hardware preservation claims: `NO`
- blocks write-capable adapter work: `YES`

### DISABLED_REMAP_POLICY_UNRESOLVED

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
  - `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`
  - `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`
- what would unblock it: explicit policy for omitted `activates` vs explicit `BTN_UNSPECIFIED` and preservation rules.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `NO` (unless adapter coupling is required)
- blocks hardware preservation claims: `NO`
- blocks write-capable adapter work: `YES`

### BOTH_HELD_POLICY_NOT_PROMOTED

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
  - `docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json`
  - `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`
- what would unblock it: explicit reviewed design decision promoting both-held behavior to contract status.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `YES`
- blocks hardware preservation claims: `YES` (for claimed both-held contract behavior)
- blocks write-capable adapter work: `NO`

### NEXT_RUNTIME_PATCH_NOT_APPROVED

- status: `BLOCKED`
- source doc anchors:
  - `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`
  - `docs/calibration/glyph_full_firmware_workstream_sequence_handoff_2026-05-26.md`
  - `docs/calibration/glyph_native_ultimate_runtime_implementation_plan_v0_2026-05-27.md`
- what would unblock it: explicit user approval for exact runtime patch scope.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `YES`
- blocks hardware preservation claims: `YES` (for new runtime behavior)
- blocks write-capable adapter work: `NO`

### HARDWARE_TEST_REQUIRED_AFTER_RUNTIME_PATCH

- status: `BLOCKED_PENDING_FUTURE_PATCH`
- source doc anchors:
  - `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
  - `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`
  - `docs/calibration/glyph_native_ultimate_runtime_implementation_plan_v0_2026-05-27.md`
- what would unblock it: execute manual post-patch hardware packet and ingest result.
- blocks docs/checker work: `NO`
- blocks runtime implementation: `NO` (implementation can proceed after approval)
- blocks hardware preservation claims: `YES`
- blocks write-capable adapter work: `NO`

## Notes

- This index does not claim any blocker is resolved.
- This index is a planning and review control surface only.
