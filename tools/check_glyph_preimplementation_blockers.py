#!/usr/bin/env python3
"""Read-only presence checks for native Ultimate preimplementation blocker docs."""

from __future__ import annotations

from pathlib import Path
import sys


REQUIRED_NEW_DOCS = [
    "docs/calibration/glyph_controller_output_contract_v0_2026-05-27.md",
    "docs/calibration/glyph_native_ultimate_runtime_implementation_plan_v0_2026-05-27.md",
    "docs/calibration/glyph_user_requirements_input_packet_2026-05-27.md",
    "docs/calibration/glyph_preimplementation_blocker_index_2026-05-27.md",
    "docs/calibration/glyph_user_requirements_packet_checker_2026-05-27.md",
    "docs/calibration/glyph_preservation_hardware_execution_packet_2026-05-27.md",
    "tools/check_glyph_user_requirements_packet.py",
    "tools/check_glyph_preservation_execution_packet.py",
]

REQUIRED_EXISTING_ANCHORS = [
    "docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md",
    "docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md",
    "docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md",
    "docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md",
    "docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md",
    "docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md",
    "docs/calibration/glyph_profile_config_source_authority_2026-05-26.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_test_result.md",
    "docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json",
    "tools/check_glyph_native_ultimate_table_fixture.py",
    "tools/check_glyph_native_ultimate_table_runtime_scope.py",
    "tools/run_glyph_next_runtime_change_readiness_checks.py",
    "tools/check_glyph_merged_state_consistency.py",
]


def exists(repo_root: Path, rel_path: str) -> bool:
    return (repo_root / rel_path).exists()


def run_group(repo_root: Path, title: str, rel_paths: list[str]) -> list[str]:
    missing: list[str] = []
    print(f"[preimpl-blockers-check] verifying {title}")
    for rel in rel_paths:
        if exists(repo_root, rel):
            print(f"[preimpl-blockers-check] OK required={rel}")
        else:
            print(f"[preimpl-blockers-check] MISSING required={rel}")
            missing.append(rel)
    return missing


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    missing_new = run_group(repo_root, "new docs/checkers", REQUIRED_NEW_DOCS)
    missing_existing = run_group(repo_root, "existing anchor docs/checkers", REQUIRED_EXISTING_ANCHORS)

    missing_all = missing_new + missing_existing
    if missing_all:
        print(f"[preimpl-blockers-check] FAIL missing_required_count={len(missing_all)}")
        return 1

    print(
        "[preimpl-blockers-check] PASS "
        f"new_docs_count={len(REQUIRED_NEW_DOCS)} "
        f"existing_anchor_count={len(REQUIRED_EXISTING_ANCHORS)} "
        "presence_only=true"
    )
    print(
        "[preimpl-blockers-check] NOTE "
        "presence checks passed; blocker resolution and runtime readiness are intentionally not evaluated"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
