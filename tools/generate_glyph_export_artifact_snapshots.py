#!/usr/bin/env python3
"""Generate canonical docs/tools-only Glyph export artifact snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from generate_glyph_runtime_config_validation_report import build_report
from glyph_generated_config_validator import load_json_object


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_WRITE_ROOT = REPO_ROOT / "docs/calibration/fixtures"
SNAPSHOT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_export_artifact_snapshots_2026-06-03.json"
)

GENERATED_CONFIG_PROTOTYPE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
RUNTIME_CONFIG_CANDIDATE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json"
)
SENSCOPE_EXPORT_PACKAGE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json"
)
RUNTIME_CONFIG_VALIDATION_REPORT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json"
)
GENERATED_CPP_TABLE_ARTIFACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt"
)
BEHAVIOR_CASES_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json"
)
GENERATED_CONFIG_INVALID_CORPUS_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_generated_config_invalid_corpus_2026-06-03.json"
)
RUNTIME_CONFIG_CANDIDATE_INVALID_CORPUS_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_invalid_corpus_2026-06-03.json"
)

SCHEMA_NAME = "glyph_export_artifact_snapshots"
SNAPSHOT_VERSION = 1
STATUS = "docs_tools_canonical_snapshots"
HARDWARE_STATUS = "not_new_hardware_result"
NUNCHUK_STATUS = "preserved_but_not_hardware_validated"

CPP_DECLARATION_PATTERN = re.compile(r"constexpr\s+StickPoint\s+k[A-Za-z0-9]+Table\s*\[9\]\s*=")


class ExportArtifactSnapshotsError(ValueError):
    """Raised when snapshot generation inputs are invalid."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ExportArtifactSnapshotsError(message)


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def canonical_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_canonical_json_artifact(path: Path) -> tuple[dict[str, Any], str]:
    payload = load_json_object(path)
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload, canonical_json_text(payload)


def load_canonical_text_artifact(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def build_generated_config_snapshot() -> dict[str, Any]:
    payload, canonical_text = load_canonical_json_artifact(GENERATED_CONFIG_PROTOTYPE_PATH)
    tables = payload.get("tables")
    coverage = payload.get("coverage_metadata")
    categories = coverage.get("categories") if isinstance(coverage, dict) else None
    if not isinstance(tables, dict):
        fail("generated_config_prototype.tables must be an object")
    if not isinstance(coverage, dict):
        fail("generated_config_prototype.coverage_metadata must be an object")
    if not isinstance(categories, list):
        fail("generated_config_prototype.coverage_metadata.categories must be a list")
    return {
        "path": display(GENERATED_CONFIG_PROTOTYPE_PATH),
        "sha256": canonical_text_hash(canonical_text),
        "status": payload.get("source_status"),
        "hardware_status": payload.get("hardware_status"),
        "summary": {
            "table_count": len(tables),
            "coverage_case_count": coverage.get("case_count"),
            "coverage_category_count": len(categories),
        },
    }


def build_runtime_candidate_snapshot() -> dict[str, Any]:
    payload, canonical_text = load_canonical_json_artifact(RUNTIME_CONFIG_CANDIDATE_PATH)
    tables = payload.get("tables")
    priority_references = payload.get("priority_references")
    required_non_goals = payload.get("non_goals")
    if not isinstance(tables, dict):
        fail("runtime_config_candidate_sample.tables must be an object")
    if not isinstance(priority_references, dict):
        fail("runtime_config_candidate_sample.priority_references must be an object")
    if not isinstance(required_non_goals, list):
        fail("runtime_config_candidate_sample.non_goals must be a list")
    return {
        "path": display(RUNTIME_CONFIG_CANDIDATE_PATH),
        "sha256": canonical_text_hash(canonical_text),
        "status": payload.get("status"),
        "hardware_status": payload.get("hardware_status"),
        "summary": {
            "table_count": len(tables),
            "priority_reference_count": len(priority_references),
            "non_goal_count": len(required_non_goals),
        },
    }


def build_export_package_snapshot() -> dict[str, Any]:
    payload, canonical_text = load_canonical_json_artifact(SENSCOPE_EXPORT_PACKAGE_PATH)
    nested_generated_config = payload.get("glyph_generated_config_prototype")
    if not isinstance(nested_generated_config, dict):
        fail("senscope_export_package_sample.glyph_generated_config_prototype must be an object")
    nested_tables = nested_generated_config.get("tables")
    nested_coverage = nested_generated_config.get("coverage_metadata")
    if not isinstance(nested_tables, dict):
        fail("senscope_export_package_sample nested tables must be an object")
    if not isinstance(nested_coverage, dict):
        fail("senscope_export_package_sample nested coverage_metadata must be an object")
    return {
        "path": display(SENSCOPE_EXPORT_PACKAGE_PATH),
        "sha256": canonical_text_hash(canonical_text),
        "status": payload.get("status"),
        "hardware_status": payload.get("hardware_status"),
        "summary": {
            "nested_generated_config_table_count": len(nested_tables),
            "nested_behavior_case_count": nested_coverage.get("case_count"),
            "neutral_profile_field_count": len(payload.get("neutral_senscope_profile", {})),
        },
    }


def build_runtime_validation_report_snapshot() -> dict[str, Any]:
    payload, canonical_text = load_canonical_json_artifact(RUNTIME_CONFIG_VALIDATION_REPORT_PATH)
    regenerated_report = build_report()
    generated_config_invalid_corpus, _ = load_canonical_json_artifact(GENERATED_CONFIG_INVALID_CORPUS_PATH)
    runtime_candidate_invalid_corpus, _ = load_canonical_json_artifact(RUNTIME_CONFIG_CANDIDATE_INVALID_CORPUS_PATH)
    generated_cases = generated_config_invalid_corpus.get("cases")
    runtime_cases = runtime_candidate_invalid_corpus.get("cases")
    required_non_goals = payload.get("required_non_goals")
    if not isinstance(generated_cases, list):
        fail("generated_config_invalid_corpus.cases must be a list")
    if not isinstance(runtime_cases, list):
        fail("runtime_config_candidate_invalid_corpus.cases must be a list")
    if not isinstance(required_non_goals, list):
        fail("runtime_config_validation_report.required_non_goals must be a list")
    return {
        "path": display(RUNTIME_CONFIG_VALIDATION_REPORT_PATH),
        "sha256": canonical_text_hash(canonical_text),
        "status": payload.get("status"),
        "hardware_status": payload.get("hardware_status"),
        "summary": {
            "table_count": payload.get("table_count"),
            "generated_config_invalid_corpus_case_count": len(generated_cases),
            "runtime_candidate_invalid_corpus_case_count": len(runtime_cases),
            "reported_invalid_corpus_case_count": payload.get("invalid_corpus_case_count"),
            "required_non_goal_count": len(required_non_goals),
            "regenerated_report_sha256": canonical_text_hash(canonical_json_text(regenerated_report)),
        },
    }


def build_generated_cpp_snapshot() -> dict[str, Any]:
    canonical_text = load_canonical_text_artifact(GENERATED_CPP_TABLE_ARTIFACT_PATH)
    declaration_count = len(CPP_DECLARATION_PATTERN.findall(canonical_text))
    return {
        "path": display(GENERATED_CPP_TABLE_ARTIFACT_PATH),
        "sha256": canonical_text_hash(canonical_text),
        "status": "docs_tools_review_only_not_firmware_source",
        "hardware_status": HARDWARE_STATUS,
        "summary": {
            "table_declaration_count": declaration_count,
            "line_count": len(canonical_text.splitlines()),
        },
    }


def build_behavior_cases_snapshot() -> dict[str, Any]:
    payload, canonical_text = load_canonical_json_artifact(BEHAVIOR_CASES_FIXTURE_PATH)
    cases = payload.get("cases")
    if not isinstance(cases, list):
        fail("behavior_cases_fixture.cases must be a list")
    categories = {case.get("category") for case in cases if isinstance(case, dict)}
    return {
        "path": display(BEHAVIOR_CASES_FIXTURE_PATH),
        "sha256": canonical_text_hash(canonical_text),
        "status": payload.get("source_status"),
        "hardware_status": payload.get("hardware_status"),
        "summary": {
            "case_count": len(cases),
            "category_count": len(categories),
        },
    }


def build_snapshot_payload() -> dict[str, Any]:
    artifacts = {
        "generated_config_prototype": build_generated_config_snapshot(),
        "runtime_config_candidate_sample": build_runtime_candidate_snapshot(),
        "senscope_export_package_sample": build_export_package_snapshot(),
        "runtime_config_validation_report": build_runtime_validation_report_snapshot(),
        "generated_cpp_table_artifact": build_generated_cpp_snapshot(),
        "behavior_cases_fixture": build_behavior_cases_snapshot(),
    }
    return {
        "artifacts": artifacts,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
        "schema_name": SCHEMA_NAME,
        "snapshot_version": SNAPSHOT_VERSION,
        "source_authority": {
            "generated_cpp_artifact_checker": "tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py",
            "round_trip_checker": "tools/check_glyph_export_artifact_round_trip.py",
            "snapshot_doc": "docs/calibration/glyph_export_artifact_canonical_snapshots_2026-06-03.md",
            "validation_report_generator": "tools/generate_glyph_runtime_config_validation_report.py",
        },
        "status": STATUS,
    }


def render_snapshot_payload(payload: dict[str, Any]) -> str:
    return canonical_json_text(payload)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved_root = ALLOWED_WRITE_ROOT.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ExportArtifactSnapshotsError(
            "--write-json path must be under docs/calibration/fixtures/"
        ) from exc
    resolved_path.write_text(render_snapshot_payload(payload), encoding="utf-8")


def print_text_summary(payload: dict[str, Any], write_json_path: Path | None = None) -> None:
    print(SCHEMA_NAME)
    print("status=PASS")
    print(f"artifact_count={len(payload['artifacts'])}")
    print(f"hardware_status={payload['hardware_status']}")
    if write_json_path is not None:
        path = write_json_path if write_json_path.is_absolute() else REPO_ROOT / write_json_path
        print(f"wrote_json={display(path)}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print deterministic JSON")
    parser.add_argument("--write-json", type=Path, help="write JSON under docs/calibration/fixtures/")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        payload = build_snapshot_payload()
        if args.write_json is not None:
            _write_json(args.write_json, payload)
    except (OSError, ValueError, ExportArtifactSnapshotsError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("artifact_count=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    if args.json:
        print(render_snapshot_payload(payload), end="")
    else:
        print_text_summary(payload, args.write_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
