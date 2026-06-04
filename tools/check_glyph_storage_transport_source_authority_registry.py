#!/usr/bin/env python3
"""Validate the Glyph storage/transport source-authority registry."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_storage_transport_source_authority_registry_2026-06-03.json"
)

SCHEMA_NAME = "glyph_storage_transport_source_authority_registry"
REGISTRY_VERSION = 1
STATUS = "docs_tools_source_authority_registry"
HARDWARE_STATUS = "not_new_hardware_result"
ALLOWED_AUTHORITY_CLASSES = {
    "repo_source_authority",
    "repo_fixture_evidence",
    "external_non_authoritative_observation",
    "official_source_authority_missing",
    "user_hardware_result",
    "blocked_pending_approval",
}
REQUIRED_CATEGORIES = (
    "config_json_shape",
    "protobuf_schema",
    "protobuf_encode_decode",
    "webserial_packet_framing",
    "device_write_path",
    "active_profile_artifact_path",
    "runtime_loaded_config_storage",
    "runtime_loaded_config_interpreter",
    "fallback_policy",
    "version_migration_policy",
    "latency_performance_evidence",
    "external_remapper_observations",
)
IMPLEMENTATION_MUST_BE_FALSE = {
    "protobuf_schema",
    "protobuf_encode_decode",
    "webserial_packet_framing",
    "device_write_path",
    "runtime_loaded_config_storage",
    "runtime_loaded_config_interpreter",
    "fallback_policy",
    "version_migration_policy",
    "latency_performance_evidence",
}
OFFICIAL_SOURCE_REQUIRED = {
    "config_json_shape",
    "protobuf_schema",
    "protobuf_encode_decode",
    "webserial_packet_framing",
    "device_write_path",
    "active_profile_artifact_path",
    "runtime_loaded_config_storage",
    "runtime_loaded_config_interpreter",
    "fallback_policy",
    "version_migration_policy",
    "latency_performance_evidence",
    "external_remapper_observations",
}
REQUIRED_DOC_PHRASES = (
    "not device write behavior",
    "not WebSerial implementation",
    "not runtime-loaded config",
    "not official configurator compatibility",
    "external observations non-authoritative",
    "not hardware validation",
)


class StorageTransportRegistryError(ValueError):
    """Raised when the storage/transport source registry drifts."""


def fail(message: str) -> None:
    raise StorageTransportRegistryError(message)


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


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    return value


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty string list")
    strings: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{label}[{index}] must be a non-empty string")
        strings.append(item)
    return strings


def require_categories(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    value = fixture.get("categories")
    if not isinstance(value, dict):
        fail("categories must be an object")
    if tuple(value.keys()) != REQUIRED_CATEGORIES:
        fail("categories must contain all required categories in stable order")

    categories: dict[str, dict[str, Any]] = {}
    for category_id in REQUIRED_CATEGORIES:
        entry = value.get(category_id)
        if not isinstance(entry, dict):
            fail(f"categories.{category_id} must be an object")
        categories[category_id] = entry
    return categories


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "registry_version": REGISTRY_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "device_write_implemented": False,
        "webserial_transport_implemented": False,
        "runtime_loaded_config_implemented": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_category(category_id: str, entry: dict[str, Any]) -> None:
    authority_class = entry.get("authority_class")
    if authority_class not in ALLOWED_AUTHORITY_CLASSES:
        fail(f"{category_id}.authority_class is unsupported: {authority_class!r}")

    require_string(entry.get("current_status"), f"{category_id}.current_status")
    known_sources = require_string_list(entry.get("known_sources"), f"{category_id}.known_sources")
    missing_sources = require_string_list(entry.get("missing_sources"), f"{category_id}.missing_sources")
    require_string_list(
        entry.get("required_before_implementation"),
        f"{category_id}.required_before_implementation",
    )
    require_string(entry.get("notes"), f"{category_id}.notes")

    if entry.get("implementation_allowed") is not False and category_id in IMPLEMENTATION_MUST_BE_FALSE:
        fail(f"{category_id}.implementation_allowed must be false")

    if category_id in OFFICIAL_SOURCE_REQUIRED:
        missing_text = " ".join(missing_sources).lower()
        if "official source authority" not in missing_text:
            fail(f"{category_id}.missing_sources must include official source authority")

    if category_id == "external_remapper_observations":
        if authority_class != "external_non_authoritative_observation":
            fail("external_remapper_observations must use external_non_authoritative_observation")
        notes = entry.get("notes", "").lower()
        if "non-authoritative" not in notes or "not promoted" not in notes:
            fail("external_remapper_observations.notes must preserve non-authority language")

    for source in known_sources:
        if source.startswith(("http://", "https://")):
            fail(f"{category_id}.known_sources must reference repo docs/tools paths, not URLs")
        if not (REPO_ROOT / source).exists():
            fail(f"{category_id}.known_sources references missing path: {source}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_storage_transport_source_authority_registry")
    category_count = 0
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        categories = require_categories(fixture)
        category_count = len(categories)
        for category_id, entry in categories.items():
            validate_category(category_id, entry)
        validate_doc()
    except (OSError, StorageTransportRegistryError, ValueError) as exc:
        print("status=FAIL")
        print(f"categories={category_count}")
        print("device_write_implemented=false")
        print("runtime_loaded_config_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"categories={category_count}")
    print("device_write_implemented=false")
    print("runtime_loaded_config_implemented=false")
    print(f"hardware_status={fixture['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
