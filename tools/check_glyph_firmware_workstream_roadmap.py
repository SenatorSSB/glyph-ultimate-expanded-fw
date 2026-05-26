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
