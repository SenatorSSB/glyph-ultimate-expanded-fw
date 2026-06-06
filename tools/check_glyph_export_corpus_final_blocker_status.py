#!/usr/bin/env python3
"""Validate the Glyph export corpus final blocker/status packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_export_corpus_final_blocker_status_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_export_corpus_final_blocker_status_2026-06-06.json"
)
EXPORT_CORPUS_ROOT = REPO_ROOT / "docs/calibration/export_corpus"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_export_corpus_final_blocker_status",
    "schema_version": 1,
    "packet_date": "2026-06-06",
}

REQUIRED_SOURCE_PROTOCOL_PATHS = {
    "docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md",
    "docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json",
    "tools/check_glyph_profile_config_export_corpus.py",
    "docs/calibration/export_corpus/README.md",
    "docs/calibration/glyph_export_corpus_readiness_status_2026-06-06.md",
    "docs/calibration/fixtures/glyph_export_corpus_readiness_status_2026-06-06.json",
    "tools/check_glyph_export_corpus_readiness_status.py",
}

REQUIRED_MISSING_ARTIFACT_CLASSES = {
    "filled_manifest_json",
    "captured_export_json_fixtures",
    "fixture_sha256_hashes",
    "glyph_repo_commit_reference",
    "firmware_source_commit_reference",
    "configurator_source_reference",
    "configurator_version_label",
    "device_model_or_capture_context",
    "expected_semantic_feature_labels",
    "known_unknowns",
}

REQUIRED_FUTURE_ARTIFACTS = REQUIRED_MISSING_ARTIFACT_CLASSES

REQUIRED_NON_CLAIMS = {
    "official_configurator_authority_claimed",
    "webserial_write_implemented",
    "device_write_implemented",
    "runtime_loaded_config_implemented",
    "adapter_output_implemented",
    "hardware_validation_claimed",
    "external_source_promoted_to_authority",
    "firmware_behavior_changed",
    "active_profile_artifact_changed",
}

BLOCKED_DOC_PHRASES = (
    "blocked_missing_real_corpus_artifacts",
    "Corpus present: false",
    "Completion allowed: false",
    "real `manifest.json` corpus capture",
    "real corpus means matched-version export captures",
    "Template files, README guidance, repo examples, generated candidate payloads, and external observations do not count as captured corpus",
    "No official configurator authority claim is made here unless source-backed",
    "No device write or WebSerial claim is made here",
    "No runtime-loaded config is implemented here",
    "No adapter implementation is made here",
    "No hardware validation claim is made here",
    "No external source authority promotion is made here",
)

COMPLETE_DOC_PHRASES = (
    "complete_corpus_present",
    "Corpus present: true",
    "Completion allowed: true",
)


class ExportCorpusFinalBlockerStatusError(AssertionError):
    """Raised when the export corpus final blocker packet drifts."""


def fail(message: str) -> None:
    raise ExportCorpusFinalBlockerStatusError(message)


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
    if payload.get("status") not in {"blocked_missing_real_corpus_artifacts", "complete_corpus_present"}:
        fail("status must be blocked_missing_real_corpus_artifacts or complete_corpus_present")
    if not isinstance(payload.get("corpus_present"), bool):
        fail("corpus_present must be a boolean")
    if not isinstance(payload.get("completion_allowed"), bool):
        fail("completion_allowed must be a boolean")


def validate_path_list(payload: dict[str, Any]) -> None:
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


def validate_required_artifact_lists(payload: dict[str, Any]) -> None:
    for field_name, required in (
        ("missing_artifact_classes", REQUIRED_MISSING_ARTIFACT_CLASSES),
        ("required_future_artifacts", REQUIRED_FUTURE_ARTIFACTS),
    ):
        values = payload.get(field_name)
        if not isinstance(values, list):
            fail(f"{field_name} must be a list")
        missing = sorted(required - set(values))
        if missing:
            fail(f"{field_name} missing: " + ", ".join(missing))


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


def validate_doc(payload: dict[str, Any]) -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    text_lower = text.lower()
    if payload.get("status") == "complete_corpus_present":
        phrases = COMPLETE_DOC_PHRASES
    else:
        phrases = BLOCKED_DOC_PHRASES
    for phrase in phrases:
        if phrase.lower() not in text_lower:
            fail(f"doc missing required phrase: {phrase}")


def validate_blocked_state(payload: dict[str, Any]) -> None:
    manifest_count = len(real_manifests())
    fixture_count = len(real_fixtures())
    if manifest_count != 0:
        fail("blocked state cannot coexist with real corpus manifests")
    if fixture_count != 0:
        fail("blocked state cannot coexist with real corpus fixtures")
    if payload.get("corpus_present") is not False:
        fail("corpus_present must be false while the corpus is blocked")
    if payload.get("completion_allowed") is not False:
        fail("completion_allowed must be false while the corpus is blocked")


def validate_complete_state(payload: dict[str, Any]) -> None:
    manifest_count = len(real_manifests())
    fixture_count = len(real_fixtures())
    if manifest_count == 0:
        fail("complete_corpus_present requires real corpus manifests")
    if fixture_count == 0:
        fail("complete_corpus_present requires real corpus fixtures")
    if payload.get("corpus_present") is not True:
        fail("corpus_present must be true when the corpus is complete")
    if payload.get("completion_allowed") is not True:
        fail("completion_allowed must be true when the corpus is complete")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/check_glyph_profile_config_export_corpus.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stdout.strip() or completed.stderr.strip() or "export corpus checker failed"
        fail(detail)


def main() -> int:
    print("glyph_export_corpus_final_blocker_status")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        validate_path_list(payload)
        validate_required_artifact_lists(payload)
        validate_non_claims(payload)
        if payload.get("status") == "complete_corpus_present":
            validate_complete_state(payload)
        else:
            validate_blocked_state(payload)
        validate_doc(payload)
    except (OSError, ExportCorpusFinalBlockerStatusError, ValueError) as exc:
        print("status=FAIL")
        print("corpus_present=false")
        print("completion_allowed=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"status_detail={payload['status']}")
    print(f"corpus_present={str(payload['corpus_present']).lower()}")
    print(f"completion_allowed={str(payload['completion_allowed']).lower()}")
    print(f"real_corpus_manifest_count={len(real_manifests())}")
    print(f"real_corpus_fixture_count={len(real_fixtures())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
