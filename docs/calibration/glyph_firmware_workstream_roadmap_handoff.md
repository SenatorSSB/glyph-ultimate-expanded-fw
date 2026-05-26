# Glyph Firmware Workstream Roadmap Handoff - 2026-05-26

## Summary

This branch adds a consolidated roadmap/index for the Glyph firmware/configurator/backend workstream and a handoff companion file.

The roadmap consolidates status/navigation and points to canonical source docs; it does not replace those source docs.

## Changed Files

- `docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md`
- `docs/calibration/glyph_firmware_workstream_roadmap_handoff.md`
- `tools/check_glyph_firmware_workstream_roadmap.py`

## What Was Inspected

Core runtime/hardware:
- `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
- `docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`

Capability/source authority:
- `docs/calibration/glyph_full_capability_inventory_2026-05-26.md`
- `docs/calibration/glyph_remaining_functionality_gap_map_2026-05-26.md`
- `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`
- `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md`

Profile/config/export/adapter:
- `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`
- `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json`
- `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
- `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`

Physical/layout:
- `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`

Native table/runtime design:
- `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`
- `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`
- `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`
- `docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md`

Requirements/readiness/handoff:
- `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md`
- `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`
- `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`
- `docs/calibration/glyph_full_firmware_workstream_sequence_handoff_2026-05-26.md`
- `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md`

Referenced checkers/tools:
- `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- `tools/check_glyph_ultimate_tilt_hardware_result.py`
- `tools/check_glyph_ultimate_tilt_rc_manifest.py`
- `tools/check_glyph_profile_config_semantics.py`
- `tools/check_glyph_profile_config_export_corpus.py`
- `tools/check_glyph_profile_adapter_prewrite.py`
- `tools/list_glyph_physical_logical_layout_sources.py`
- `tools/check_glyph_ultimate_preservation_hardware_result.py`
- `tools/check_glyph_native_ultimate_table_fixture.py`
- `tools/check_glyph_native_ultimate_table_runtime_scope.py`
- `tools/run_glyph_next_runtime_change_readiness_checks.py`
- `tools/check_glyph_merged_state_consistency.py`

## What Was Not Inspected

- Firmware runtime files outside the roadmap-referenced scope (except source-backed claims already captured by the inspected docs/checkers).
- External configurator/browser-app source repositories.
- Any hardware result file for `docs/calibration/glyph_ultimate_preservation_hardware_result.md` (still absent).
- Any new captured export corpus under `docs/calibration/export_corpus/<corpus_id>/` (still absent).

## Behavior/Config Impact

- Behavior/config impact: none.
- Runtime/source/configurator behavior changed: no.
- SOCD/remap/profile schema/proto behavior changed: no.
- Artifacts/binaries committed: no.

## Verification Commands Run

- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py`
- `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py`
- `.venv/bin/python tools/check_glyph_profile_config_semantics.py`
- `.venv/bin/python tools/check_glyph_profile_config_export_corpus.py`
- `.venv/bin/python tools/check_glyph_profile_adapter_prewrite.py docs/sources/raw/GlyphUserProfiles.json`
- `.venv/bin/python tools/list_glyph_physical_logical_layout_sources.py`
- `.venv/bin/python tools/check_glyph_ultimate_preservation_hardware_result.py`
- `.venv/bin/python tools/check_glyph_native_ultimate_table_fixture.py docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`
- `.venv/bin/python tools/check_glyph_native_ultimate_table_runtime_scope.py`
- `.venv/bin/python tools/run_glyph_next_runtime_change_readiness_checks.py`
- `.venv/bin/python tools/check_glyph_merged_state_consistency.py`
- `.venv/bin/python tools/check_glyph_firmware_workstream_roadmap.py`
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true`
- `git diff --check`
- `git status --short`

## Next Recommended Branch

- `glyph/gfw2-current-tilt-table-fixture-seed`

## Required Caveats

- roadmap consolidates and points to docs; it does not replace source docs.
- some historical docs intentionally remain historical.
- preservation hardware result is still absent.
- export corpus still absent.
