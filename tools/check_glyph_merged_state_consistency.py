#!/usr/bin/env python3
"""Read-only merged-state consistency audit for Glyph calibration docs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs" / "calibration"


REQUIRED_FILES = (
    "docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md",
    "docs/calibration/glyph_merged_state_consistency_handoff.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_test_result.md",
    "docs/calibration/glyph_full_capability_inventory_2026-05-26.md",
    "docs/calibration/glyph_profile_config_source_authority_2026-05-26.md",
    "docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md",
    "docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json",
    "docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
    "docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md",
    "docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md",
    "docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json",
    "docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md",
    "docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md",
    "docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md",
    "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
    "tools/check_glyph_ultimate_tilt_hardware_result.py",
    "tools/check_glyph_profile_config_semantics.py",
    "tools/check_glyph_profile_config_export_corpus.py",
    "tools/check_glyph_profile_adapter_prewrite.py",
    "tools/list_glyph_physical_logical_layout_sources.py",
    "tools/check_glyph_ultimate_preservation_hardware_result.py",
    "tools/check_glyph_native_ultimate_table_fixture.py",
    "tools/check_glyph_native_ultimate_table_runtime_scope.py",
    "tools/run_glyph_next_runtime_change_readiness_checks.py",
)


CURRENT_BRANCH_DELIVERABLES = {
    "docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md",
    "docs/calibration/glyph_merged_state_consistency_handoff.md",
}


TEXT_SUFFIXES = {".md", ".json", ".txt"}


@dataclass(frozen=True)
class StalePattern:
    label: str
    pattern: re.Pattern[str]
    valid_context: re.Pattern[str]


STALE_PATTERNS = (
    StalePattern(
        label="pending transcription",
        pattern=re.compile(r"pending transcription|faceplate/base transcription pending", re.IGNORECASE),
        valid_context=re.compile(r"historical|obsolete|stale|avoid saying|should no longer", re.IGNORECASE),
    ),
    StalePattern(
        label="not yet performed",
        pattern=re.compile(r"not yet performed|hardware test not performed", re.IGNORECASE),
        valid_context=re.compile(
            r"historical|earlier|pre-result|preservation|future|manual hardware result|at that earlier step",
            re.IGNORECASE,
        ),
    ),
    StalePattern(
        label="adapter policy doc was not present",
        pattern=re.compile(r"adapter policy doc (?:was )?not present|adapter policy doc missing", re.IGNORECASE),
        valid_context=re.compile(r"historical|obsolete|stale|should no longer", re.IGNORECASE),
    ),
    StalePattern(
        label="RF5 remains unresolved",
        pattern=re.compile(
            r"RF5 (?:remains )?(?:unresolved|ambiguous)|RF5 physical identity resolution",
            re.IGNORECASE,
        ),
        valid_context=re.compile(
            r"historical|old|older|negative smoke|ambiguous|layer|transcription|future|avoid saying|which layer",
            re.IGNORECASE,
        ),
    ),
    StalePattern(
        label="NO_RESULT_FILE",
        pattern=re.compile(r"NO_RESULT_FILE"),
        valid_context=re.compile(r"template|checker|status|preservation|missing future|expected|until manual", re.IGNORECASE),
    ),
    StalePattern(
        label="TEMPLATE_ONLY",
        pattern=re.compile(r"TEMPLATE_ONLY"),
        valid_context=re.compile(r"template|fixture|status|source_status", re.IGNORECASE),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check merged Glyph calibration docs for required files and stale merged-state claims.",
    )
    parser.add_argument(
        "--scan-root",
        type=Path,
        default=DOCS_ROOT,
        help="Documentation root to scan for stale phrases.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def required_file_errors() -> list[str]:
    errors: list[str] = []
    for relpath in REQUIRED_FILES:
        path = REPO_ROOT / relpath
        if not path.exists():
            errors.append(f"missing required file: {relpath}")
    return errors


def context_for(lines: list[str], index: int) -> str:
    start = max(0, index - 4)
    end = min(len(lines), index + 5)
    return "\n".join(lines[start:end])


def scan_stale_phrases(scan_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in sorted(scan_root.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = text.splitlines()
        for line_index, line in enumerate(lines):
            for stale in STALE_PATTERNS:
                if stale.pattern.search(line) is None:
                    continue
                context = context_for(lines, line_index)
                location = f"{display_path(path)}:{line_index + 1}"
                if stale.valid_context.search(context):
                    warnings.append(f"{location}: contextual {stale.label}: {line.strip()}")
                elif display_path(path) in CURRENT_BRANCH_DELIVERABLES:
                    errors.append(f"{location}: current deliverable has uncontextualized {stale.label}: {line.strip()}")
                else:
                    warnings.append(f"{location}: needs review for {stale.label}: {line.strip()}")
    return errors, warnings


def main() -> int:
    args = parse_args()
    errors = required_file_errors()
    stale_errors, warnings = scan_stale_phrases(args.scan_root)
    errors.extend(stale_errors)

    print("glyph_merged_state_consistency")
    print(f"required_files={len(REQUIRED_FILES)}")
    print(f"missing_required_files={len([item for item in errors if item.startswith('missing required file:')])}")
    print(f"scan_root={display_path(args.scan_root)}")
    print(f"warnings={len(warnings)}")
    print(f"errors={len(errors)}")

    if warnings:
        print("\ncontextual_warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("\nerrors:")
        for error in errors:
            print(f"- {error}")
        print("status=FAIL")
        return 1

    print(f"status={'WARN' if warnings else 'PASS'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
