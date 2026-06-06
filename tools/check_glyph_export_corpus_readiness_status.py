#!/usr/bin/env python3
"""Validate the Glyph export corpus readiness/status packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_export_corpus_readiness_status_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_export_corpus_readiness_status_2026-06-06.json"
)
EXPORT_CORPUS_ROOT = REPO_ROOT / "docs/calibration/export_corpus"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_export_corpus_readiness_status",
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "blocked_missing_real_corpus_artifacts",
    "roadmap_next_work_index_path": "docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md",
    "export_corpus_root": "docs/calibration/export_corpus",
    "corpus_present": False,
    "completion_allowed": False,
    "real_corpus_manifest_count": 0,
    "real_corpus_fixture_count": 0,
}

REQUIRED_SOURCE_PROTOCOL_PATHS = {
    "docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json",
    "tools/check_glyph_profile_config_export_corpus.py",
    "docs/calibration/export_corpus/README.md",
}

REQUIRED_FUTURE_ARTIFACT_CLASSES = {
    "filled_manifest_json",
    "captured_export_json_fixtures",
    "fixture_sha256_hashes",
    "configurator_source_or_version_reference",
    "firmware_source_commit_reference",
    "glyph_repo_commit_reference",
    "device_model_or_capture_context",
    "expected_semantic_feature_labels",
    "known_unknowns",
}

REQUIRED_NON_CLAIMS = {
    "official_configurator_authority_claimed",
    "device_write_claimed",
    "webserial_write_claimed",
    "hardware_validation_claimed",
    "adapter_implemented",
    "external_remapper_adapter_output_generated",
    "runtime_loaded_config_implemented",
    "firmware_behavior_changed",
    "active_profile_artifact_changed",
}

REQUIRED_DOC_PHRASES = (
    "blocked_missing_real_corpus_artifacts",
    "Corpus present: false",
    "Completion allowed: false",
    "docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json",
    "tools/check_glyph_profile_config_export_corpus.py",
    "docs/calibration/export_corpus/",
    "no real `manifest.json` corpus capture",
    "Current missing artifacts",
    "What counts as captured corpus",
    "Required hashes and records",
    "No official configurator authority claim is made here",
    "No device write or WebSerial claim is made here",
    "No hardware validation claim is made here",
    "No adapter implementation is made here",
    "No runtime-loaded config is implemented here",
)


class ExportCorpusReadinessError(AssertionError):
    """Raised when the export corpus readiness packet drifts."""


def fail(message: str) -> None:
    raise ExportCorpusReadinessError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def real_manifests() -> list[Path]:
    if not EXPORT_CORPUS_ROOT.exists():
        return []
    return sorted(path for path in EXPORT_CORPUS_ROOT.rglob("manifest.json") if path.is_file())


def real_fixtures() -> list[Path]:
    manifests = real_manifests()
    if not manifests:
        return []
    fixture_paths: list[Path] = []
    for manifest in manifests:
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        raw_files = payload.get("fixture_files")
        if not isinstance(raw_files, list):
            continue
        for raw_file in raw_files:
            if isinstance(raw_file, str) and raw_file.strip():
                candidate = manifest.parent / raw_file
                if candidate.exists() and candidate.is_file():
                    fixture_paths.append(candidate)
    return sorted(fixture_paths)


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_paths(payload: dict[str, Any]) -> None:
    for path in (DOC_PATH, FIXTURE_PATH):
        if not path.exists():
            fail(f"missing required path: {display(path)}")
    paths = payload.get("source_protocol_paths")
    if not isinstance(paths, list):
        fail("source_protocol_paths must be a list")
    missing = sorted(REQUIRED_SOURCE_PROTOCOL_PATHS - set(paths))
    if missing:
        fail("source_protocol_paths missing: " + ", ".join(missing))
    for rel_path in paths:
        if not isinstance(rel_path, str) or not rel_path.strip():
            fail("source_protocol_paths must contain non-empty strings")
        if not (REPO_ROOT / rel_path).exists():
            fail(f"source_protocol_paths references missing path: {rel_path}")


def validate_future_artifacts(payload: dict[str, Any]) -> None:
    values = payload.get("required_future_artifact_classes")
    if not isinstance(values, list):
        fail("required_future_artifact_classes must be a list")
    missing = sorted(REQUIRED_FUTURE_ARTIFACT_CLASSES - set(values))
    if missing:
        fail("required_future_artifact_classes missing: " + ", ".join(missing))


def validate_captured_definition(payload: dict[str, Any]) -> None:
    definition = payload.get("captured_corpus_definition")
    if not isinstance(definition, dict):
        fail("captured_corpus_definition must be an object")
    for key in (
        "requires_filled_manifest",
        "requires_listed_fixture_files",
        "requires_hashes",
        "requires_matched_version_provenance",
    ):
        if definition.get(key) is not True:
            fail(f"captured_corpus_definition.{key} must be true")
    for key in (
        "templates_or_readmes_count_as_corpus",
        "repo_example_fixtures_count_as_corpus",
        "external_remapper_observations_count_as_corpus",
        "generated_candidate_payloads_count_as_corpus",
    ):
        if definition.get(key) is not False:
            fail(f"captured_corpus_definition.{key} must be false")


def validate_non_claims(payload: dict[str, Any]) -> None:
    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("non_claims must be an object")
    missing = sorted(REQUIRED_NON_CLAIMS - set(non_claims))
    if missing:
        fail("non_claims missing: " + ", ".join(missing))
    for key in sorted(REQUIRED_NON_CLAIMS):
        if non_claims.get(key) is not False:
            fail(f"non_claims.{key} must be false")


def validate_no_completion_without_real_corpus(payload: dict[str, Any]) -> None:
    manifest_count = len(real_manifests())
    fixture_count = len(real_fixtures())
    if manifest_count == 0:
        if payload.get("corpus_present") is not False:
            fail("corpus_present must be false when no real manifest exists")
        if payload.get("completion_allowed") is not False:
            fail("completion_allowed must be false when no real manifest exists")
        if payload.get("real_corpus_manifest_count") != 0:
            fail("real_corpus_manifest_count must be 0 when no real manifest exists")
        if payload.get("real_corpus_fixture_count") != 0:
            fail("real_corpus_fixture_count must be 0 when no real manifest exists")
        return
    if payload.get("corpus_present") is not True:
        fail("corpus_present cannot be false when real manifests exist; inspect corpus before proceeding")
    if payload.get("real_corpus_manifest_count") != manifest_count:
        fail("real_corpus_manifest_count must match discovered manifests")
    if payload.get("real_corpus_fixture_count") != fixture_count:
        fail("real_corpus_fixture_count must match discovered fixture files")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_export_corpus_readiness_status")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        validate_paths(payload)
        validate_future_artifacts(payload)
        validate_captured_definition(payload)
        validate_non_claims(payload)
        validate_no_completion_without_real_corpus(payload)
        validate_doc()
    except (OSError, ExportCorpusReadinessError, ValueError) as exc:
        print("status=FAIL")
        print("packet_date=2026-06-06")
        print("corpus_present=false")
        print("completion_allowed=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("packet_date=2026-06-06")
    print("status_detail=blocked_missing_real_corpus_artifacts")
    print("corpus_present=false")
    print("completion_allowed=false")
    print("real_corpus_manifest_count=0")
    print("real_corpus_fixture_count=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
