#!/usr/bin/env python3
"""Read-only existence checks for the Glyph firmware workstream roadmap index."""

from __future__ import annotations

from pathlib import Path
import sys


REQUIRED_FILES = [
    "docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md",
    "docs/calibration/glyph_firmware_workstream_roadmap_handoff.md",
    "docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_test_result.md",
    "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
    "docs/calibration/glyph_full_capability_inventory_2026-05-26.md",
    "docs/calibration/glyph_remaining_functionality_gap_map_2026-05-26.md",
    "docs/calibration/glyph_profile_config_source_authority_2026-05-26.md",
    "docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json",
    "docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md",
    "docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md",
    "docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md",
    "docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md",
    "docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md",
    "docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json",
    "docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md",
    "docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md",
    "docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md",
    "docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md",
    "docs/calibration/glyph_full_firmware_workstream_sequence_handoff_2026-05-26.md",
    "docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md",
    "docs/calibration/glyph_controller_output_contract_v0_2026-05-27.md",
    "docs/calibration/glyph_native_ultimate_runtime_implementation_plan_v0_2026-05-27.md",
    "docs/calibration/glyph_user_requirements_input_packet_2026-05-27.md",
    "docs/calibration/glyph_preimplementation_blocker_index_2026-05-27.md",
    "docs/calibration/glyph_user_requirements_packet_checker_2026-05-27.md",
    "docs/calibration/glyph_preservation_hardware_execution_packet_2026-05-27.md",
    "docs/calibration/glyph_prehardware_rc_runbook_2026-05-27.md",
    "docs/calibration/glyph_prehardware_rc_runbook_checker_2026-05-27.md",
    "docs/calibration/glyph_prehardware_dry_run_checker_2026-05-27.md",
    "docs/calibration/glyph_no_forbidden_artifacts_checker_2026-05-27.md",
    "docs/calibration/glyph_manual_hardware_owner_checklist_2026-05-27.md",
    "docs/calibration/glyph_ultimate_tilt3_runtime_implementation_2026-05-27.md",
    "docs/calibration/glyph_ultimate_tilt3_hardware_test_plan_2026-05-27.md",
    "docs/calibration/glyph_smash_box_profile_output_tables_2026-05-27.md",
    "docs/calibration/glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md",
    "docs/calibration/glyph_smashbox_modifiers_hardware_test_plan_2026-05-27.md",
    "docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md",
    "docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md",
    "docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md",
    "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json",
    "docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md",
    "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json",
    "docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md",
    "docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json",
    "docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md",
    "docs/calibration/fixtures/glyph_runtime_loaded_config_design_v0_2026-05-28.json",
    "docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md",
    "docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json",
    "docs/calibration/glyph_ultimate_lt3_profile_binding_2026-05-27.md",
    "docs/calibration/glyph_active_ultimate_lt3_config_artifact_2026-05-27.md",
    "docs/calibration/glyph_ultimate_identity_profile_baseline_2026-05-27.md",
    "docs/calibration/glyph_ultimate_lt3_standalone_hardware_result_2026-05-27.md",
    "docs/calibration/glyph_ultimate_lt3_dpad_fix_hardware_result_2026-05-27.md",
    "docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md",
    "docs/calibration/glyph_senscope_workflow_and_config_migration_plan_2026-05-27.md",
    "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
    "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
    "tools/check_glyph_ultimate_tilt_hardware_result.py",
    "tools/check_glyph_ultimate_tilt_rc_manifest.py",
    "tools/check_glyph_profile_config_semantics.py",
    "tools/check_glyph_profile_config_export_corpus.py",
    "tools/check_glyph_profile_adapter_prewrite.py",
    "tools/list_glyph_physical_logical_layout_sources.py",
    "tools/check_glyph_ultimate_preservation_hardware_result.py",
    "tools/check_glyph_native_ultimate_table_fixture.py",
    "tools/check_glyph_native_ultimate_table_runtime_scope.py",
    "tools/run_glyph_next_runtime_change_readiness_checks.py",
    "tools/check_glyph_merged_state_consistency.py",
    "tools/check_glyph_preimplementation_blockers.py",
    "tools/check_glyph_user_requirements_packet.py",
    "tools/check_glyph_preservation_execution_packet.py",
    "tools/check_glyph_prehardware_rc_runbook.py",
    "tools/inspect_glyph_mk6_build_artifact.py",
    "tools/run_glyph_prehardware_dry_run_checks.py",
    "tools/check_glyph_no_forbidden_artifacts.py",
    "tools/check_glyph_manual_hardware_owner_checklist.py",
    "tools/check_glyph_ultimate_tilt3_runtime_source.py",
    "tools/check_glyph_smashbox_profile_tables.py",
    "tools/check_glyph_smashbox_modifiers_runtime_source.py",
    "tools/check_glyph_smashbox_identity_runtime_bindings.py",
    "tools/generate_glyph_identity_runtime_config_prototype.py",
    "tools/check_glyph_identity_runtime_generated_config_prototype.py",
    "tools/check_glyph_identity_runtime_config_contracts.py",
    "tools/check_glyph_runtime_loaded_config_design.py",
    "tools/check_glyph_ultimate_lt3_profile_binding.py",
    "tools/check_glyph_active_ultimate_lt3_config_artifact.py",
    "tools/check_glyph_ultimate_identity_profile_baseline.py",
    "tools/check_glyph_ultimate_dpad_profile_mapping.py",
    "tools/check_glyph_serial_config_writer.py",
    "tools/check_glyph_senscope_workflow_plan.py",
    "tools/glyph_serial_config_tool.py",
]

OPTIONAL_FUTURE_FILES = [
    "docs/calibration/glyph_ultimate_preservation_hardware_result.md",
    "docs/calibration/export_corpus",
]


def check_exists(repo_root: Path, rel_path: str) -> bool:
    return (repo_root / rel_path).exists()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    missing_required: list[str] = []
    missing_optional: list[str] = []

    print("[roadmap-check] verifying required roadmap references")
    for rel in REQUIRED_FILES:
        if check_exists(repo_root, rel):
            print(f"[roadmap-check] OK required={rel}")
        else:
            print(f"[roadmap-check] MISSING required={rel}")
            missing_required.append(rel)

    print("[roadmap-check] verifying optional future references")
    for rel in OPTIONAL_FUTURE_FILES:
        if check_exists(repo_root, rel):
            print(f"[roadmap-check] OK optional={rel}")
        else:
            print(f"[roadmap-check] WARNING optional_missing={rel}")
            missing_optional.append(rel)

    if missing_required:
        print(
            "[roadmap-check] FAIL missing_required_count="
            f"{len(missing_required)}"
        )
        return 1

    print(
        "[roadmap-check] PASS required_count="
        f"{len(REQUIRED_FILES)} optional_missing_count={len(missing_optional)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
