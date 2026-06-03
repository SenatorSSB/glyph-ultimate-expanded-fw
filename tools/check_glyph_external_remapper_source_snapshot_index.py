#!/usr/bin/env python3
"""Validate the external Glyph remapper source snapshot index."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json"
)

SCHEMA_NAME = "glyph_external_remapper_source_snapshot_index"
SNAPSHOT_VERSION = 1
STATUS = "external_non_authoritative_snapshot_index"
HARDWARE_STATUS = "not_new_hardware_result"
REQUIRED_EXTERNAL_URLS = (
    "https://github.com/lyseste/glyph-remapper",
    "https://lyseste.com/glyph-remapper/",
)
REQUIRED_TOP_LEVEL = {
    "schema_name": SCHEMA_NAME,
    "snapshot_version": SNAPSHOT_VERSION,
    "status": STATUS,
    "hardware_status": HARDWARE_STATUS,
    "external_source_promoted_to_authority": False,
    "code_copied_into_repo": False,
    "device_write_implemented": False,
    "runtime_loaded_config_implemented": False,
}
REQUIRED_FEATURE_CATEGORIES = (
    "browser configurator",
    "visual layout",
    "per-button remap",
    "profile management",
    "RGB/color palette",
    "SOCD",
    "keyboard capture",
    "JSON import/export",
    "protobuf encode/decode",
    "WebSerial load/save",
    "custom profile/modifier support claim",
)
REQUIRED_FILE_KINDS = (
    "readme_docs",
    "app_script_js",
    "index_html",
    "css",
    "protobuf_schema_inline",
    "default_config_payload",
)
ALLOWED_PROVENANCE = {
    "observed_from_public_post",
    "observed_from_external_repo_docs",
    "observed_from_external_code_excerpt",
    "not_verified",
}
REQUIRED_FORBIDDEN_INTERPRETATIONS = (
    "firmware_source_authority",
    "official_configurator_authority",
    "copied_source",
    "imported_dependency",
    "device_write_implementation",
    "runtime_loaded_config_implementation",
    "hardware_validation",
)
REQUIRED_DOC_PHRASES = (
    "non-authoritative snapshot",
    "no external source copied",
    "not firmware source authority",
    "not official configurator authority",
    "not device write behavior",
    "not runtime-loaded config",
    "not hardware validation",
)


class ExternalRemapperSnapshotError(ValueError):
    """Raised when the external remapper snapshot index drifts."""


def fail(message: str) -> None:
    raise ExternalRemapperSnapshotError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{key} must be a non-empty list")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{key}[{index}] must be a non-empty string")
    return value


def require_object_list(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{key} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"{key}[{index}] must be an object")
        result.append(item)
    return result


def validate_top_level(fixture: dict[str, Any]) -> None:
    for key, value in REQUIRED_TOP_LEVEL.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")

    for key in ("snapshot_date", "inspected_date"):
        value = fixture.get(key)
        if not isinstance(value, str) or not value:
            fail(f"{key} must be a non-empty string")

    require_string_list(fixture, "access_method")


def validate_external_references(fixture: dict[str, Any]) -> None:
    references = require_object_list(fixture, "external_references")
    urls: list[str] = []
    for entry in references:
        url = entry.get("url")
        if not isinstance(url, str) or not url:
            fail("external_references entries must include non-empty url")
        urls.append(url)
        if entry.get("authority_status") != "non_authoritative_observation":
            fail(f"external reference {entry.get('id', '<unknown>')} must be non-authoritative")
        if entry.get("promoted_to_authority") is not False:
            fail(f"external reference {entry.get('id', '<unknown>')} must not be promoted")

    for required_url in REQUIRED_EXTERNAL_URLS:
        if required_url not in urls:
            fail(f"missing external reference URL: {required_url}")


def validate_provenance(value: Any, label: str) -> str:
    if value not in ALLOWED_PROVENANCE:
        fail(f"{label} has unsupported provenance: {value!r}")
    return str(value)


def validate_observed_files(fixture: dict[str, Any]) -> None:
    files = require_object_list(fixture, "observed_files")
    kinds: set[str] = set()
    for entry in files:
        path = entry.get("path")
        kind = entry.get("kind")
        if not isinstance(path, str) or not path:
            fail("observed_files entries must include path")
        if not isinstance(kind, str) or not kind:
            fail(f"observed file {path} must include kind")
        validate_provenance(entry.get("provenance"), f"observed file {path}")
        kinds.add(kind)

    for required_kind in REQUIRED_FILE_KINDS:
        if required_kind not in kinds:
            fail(f"missing observed file kind: {required_kind}")


def validate_observed_features(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    features = require_object_list(fixture, "observed_features")
    by_category: dict[str, dict[str, Any]] = {}
    for entry in features:
        category = entry.get("category")
        if not isinstance(category, str) or not category:
            fail("observed_features entries must include category")
        validate_provenance(entry.get("provenance"), f"feature {category}")
        if entry.get("authority_status") != "non_authoritative_observation":
            fail(f"feature {category} must be non-authoritative")
        evidence = entry.get("evidence")
        if not isinstance(evidence, str) or not evidence:
            fail(f"feature {category} must include evidence")
        by_category[category] = entry

    for required_category in REQUIRED_FEATURE_CATEGORIES:
        if required_category not in by_category:
            fail(f"missing observed feature category: {required_category}")

    return features


def validate_access_gaps(fixture: dict[str, Any]) -> None:
    gaps = require_object_list(fixture, "access_gaps")
    for entry in gaps:
        gap_id = entry.get("id")
        if not isinstance(gap_id, str) or not gap_id:
            fail("access_gaps entries must include id")
        validate_provenance(entry.get("provenance"), f"access gap {gap_id}")


def validate_forbidden_interpretations(fixture: dict[str, Any]) -> None:
    forbidden = require_string_list(fixture, "forbidden_interpretations")
    for item in REQUIRED_FORBIDDEN_INTERPRETATIONS:
        if item not in forbidden:
            fail(f"forbidden_interpretations missing: {item}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_source_snapshot_index")
    observed_features_count = 0
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_external_references(fixture)
        validate_observed_files(fixture)
        features = validate_observed_features(fixture)
        observed_features_count = len(features)
        validate_access_gaps(fixture)
        validate_forbidden_interpretations(fixture)
        validate_doc()
    except (OSError, ExternalRemapperSnapshotError, ValueError) as exc:
        print("status=FAIL")
        print(f"observed_features={observed_features_count}")
        print("external_source_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"observed_features={observed_features_count}")
    print("external_source_promoted_to_authority=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("code_copied_into_repo=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
