#!/usr/bin/env python3
"""Validate committed docs/tools-only Glyph export artifact snapshots."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from generate_glyph_export_artifact_snapshots import (
    GENERATED_CONFIG_INVALID_CORPUS_PATH,
    RUNTIME_CONFIG_CANDIDATE_INVALID_CORPUS_PATH,
    SCHEMA_NAME,
    SNAPSHOT_PATH,
    STATUS,
    HARDWARE_STATUS,
    NUNCHUK_STATUS,
    build_snapshot_payload,
    canonical_json_text,
    load_canonical_json_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ARTIFACT_KEYS = {
    "generated_config_prototype",
    "runtime_config_candidate_sample",
    "senscope_export_package_sample",
    "runtime_config_validation_report",
    "generated_cpp_table_artifact",
    "behavior_cases_fixture",
}


class ExportArtifactSnapshotsCheckError(ValueError):
    """Raised when committed snapshot artifacts drift."""


def fail(message: str) -> None:
    raise ExportArtifactSnapshotsCheckError(message)


def load_snapshot_fixture() -> dict[str, Any]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail("committed snapshot fixture must be a JSON object")
    return payload


def validate_top_level(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected = {
        "schema_name": SCHEMA_NAME,
        "snapshot_version": 1,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected.items():
        if snapshot.get(key) != value:
            fail(f"{key} must be {value!r}")

    artifacts = snapshot.get("artifacts")
    if not isinstance(artifacts, dict):
        fail("artifacts must be an object")

    if set(artifacts) != EXPECTED_ARTIFACT_KEYS:
        fail("artifacts keys drifted from the committed snapshot schema")
    return artifacts


def validate_paths_exist(artifacts: dict[str, dict[str, Any]]) -> None:
    for artifact_name, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            fail(f"{artifact_name} must be an object")
        rel_path = artifact.get("path")
        if not isinstance(rel_path, str) or not rel_path:
            fail(f"{artifact_name}.path must be a non-empty string")
        if not (REPO_ROOT / rel_path).exists():
            fail(f"{artifact_name}.path does not exist: {rel_path}")
        sha256 = artifact.get("sha256")
        if not isinstance(sha256, str) or len(sha256) != 64:
            fail(f"{artifact_name}.sha256 must be a 64-character hex string")
        summary = artifact.get("summary")
        if not isinstance(summary, dict):
            fail(f"{artifact_name}.summary must be an object")


def validate_determinism(snapshot: dict[str, Any]) -> None:
    regenerated_once = build_snapshot_payload()
    regenerated_twice = build_snapshot_payload()
    if regenerated_once != regenerated_twice:
        fail("snapshot payload is not deterministic across repeated generation")
    if canonical_json_text(regenerated_once) != canonical_json_text(regenerated_twice):
        fail("snapshot canonical JSON text is not deterministic")
    if regenerated_once != snapshot:
        fail("committed snapshot fixture does not exactly match regenerated output")


def validate_summary_counts(artifacts: dict[str, dict[str, Any]]) -> None:
    generated_summary = artifacts["generated_config_prototype"]["summary"]
    runtime_summary = artifacts["runtime_config_candidate_sample"]["summary"]
    export_summary = artifacts["senscope_export_package_sample"]["summary"]
    report_summary = artifacts["runtime_config_validation_report"]["summary"]
    cpp_summary = artifacts["generated_cpp_table_artifact"]["summary"]
    behavior_summary = artifacts["behavior_cases_fixture"]["summary"]

    if generated_summary.get("table_count") != 27:
        fail("generated_config_prototype.summary.table_count must be 27")
    if runtime_summary.get("table_count") != 27:
        fail("runtime_config_candidate_sample.summary.table_count must be 27")
    if export_summary.get("nested_generated_config_table_count") != 27:
        fail("senscope_export_package_sample.summary.nested_generated_config_table_count must be 27")
    if cpp_summary.get("table_declaration_count") != 27:
        fail("generated_cpp_table_artifact.summary.table_declaration_count must be 27")

    behavior_cases_fixture, _ = load_canonical_json_artifact(REPO_ROOT / artifacts["behavior_cases_fixture"]["path"])
    behavior_cases = behavior_cases_fixture.get("cases")
    if not isinstance(behavior_cases, list):
        fail("behavior cases fixture must contain a cases list")
    if behavior_summary.get("case_count") != len(behavior_cases):
        fail("behavior_cases_fixture.summary.case_count drifted from the committed fixture")

    generated_invalid_corpus, _ = load_canonical_json_artifact(GENERATED_CONFIG_INVALID_CORPUS_PATH)
    runtime_invalid_corpus, _ = load_canonical_json_artifact(RUNTIME_CONFIG_CANDIDATE_INVALID_CORPUS_PATH)
    generated_cases = generated_invalid_corpus.get("cases")
    runtime_cases = runtime_invalid_corpus.get("cases")
    if not isinstance(generated_cases, list) or not isinstance(runtime_cases, list):
        fail("invalid corpus fixtures must contain cases lists")
    if report_summary.get("generated_config_invalid_corpus_case_count") != len(generated_cases):
        fail("generated config invalid corpus count drifted from the committed fixture")
    if report_summary.get("runtime_candidate_invalid_corpus_case_count") != len(runtime_cases):
        fail("runtime candidate invalid corpus count drifted from the committed fixture")
    if report_summary.get("reported_invalid_corpus_case_count") != len(runtime_cases):
        fail("validation report invalid corpus count drifted from the runtime candidate invalid corpus fixture")


def main() -> int:
    print(SCHEMA_NAME)
    try:
        snapshot = load_snapshot_fixture()
        artifacts = validate_top_level(snapshot)
        validate_paths_exist(artifacts)
        validate_determinism(snapshot)
        validate_summary_counts(artifacts)
    except (OSError, ValueError, ExportArtifactSnapshotsCheckError) as exc:
        print("status=FAIL")
        print("artifact_count=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"artifact_count={len(EXPECTED_ARTIFACT_KEYS)}")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
