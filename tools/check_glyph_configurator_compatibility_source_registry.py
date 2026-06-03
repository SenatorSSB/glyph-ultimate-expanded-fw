#!/usr/bin/env python3
"""Validate the Glyph configurator compatibility source registry."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_configurator_compatibility_source_registry_2026-06-03.json"
)

SCHEMA_NAME = "glyph_configurator_compatibility_source_registry"
REGISTRY_VERSION = 1
STATUS = "docs_tools_source_registry"
HARDWARE_STATUS = "not_new_hardware_result"
SOURCE_CLASSES = (
    "repo_committed_source_authority",
    "repo_committed_compatibility_fixtures",
    "external_observed_non_authoritative",
    "deferred_source_authority",
)
REQUIRED_DOC_CAVEATS = (
    "external observations are non-authoritative",
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)
REQUIRED_DEFERRED_PHRASES = (
    "official Limit Labs configurator behavior",
    "official protobuf/schema source",
    "official WebSerial packet framing",
    "device-write transport",
    "runtime-loaded config storage",
)
REQUIRED_EXTERNAL_OBSERVED_SCOPE = (
    "browser-based Glyph configurator",
    "JSON import/export",
    "WebSerial load/save",
    "protobuf encode/decode",
    "RGB/profile/SOCD/profile-management UI",
    "custom profile/modifier claim from public post",
)


class SourceRegistryError(ValueError):
    """Raised when the source registry drifts from required boundaries."""


def fail(message: str) -> None:
    raise SourceRegistryError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_entry_list(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"{label}[{index}] must be an object")
        entries.append(item)
    if not entries:
        fail(f"{label} must not be empty")
    return entries


def validate_top_level(registry: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    expected = {
        "schema_name": SCHEMA_NAME,
        "registry_version": REGISTRY_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "external_sources_promoted_to_authority": False,
        "device_write_implemented": False,
        "runtime_loaded_config_implemented": False,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"{key} must be {value!r}")

    source_classes = require_object(registry.get("source_classes"), "source_classes")
    if set(source_classes) != set(SOURCE_CLASSES):
        fail("source_classes must contain exactly: " + ", ".join(SOURCE_CLASSES))

    return {
        name: require_entry_list(source_classes[name], f"source_classes.{name}")
        for name in SOURCE_CLASSES
    }


def validate_doc(registry: dict[str, Any]) -> None:
    caveats = require_string_list(registry, "doc_caveats")
    if caveats != list(REQUIRED_DOC_CAVEATS):
        fail("doc_caveats drifted from required source-registry caveats")

    text = DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_CAVEATS:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_repo_internal_paths(source_classes: dict[str, list[dict[str, Any]]]) -> None:
    for class_name in (
        "repo_committed_source_authority",
        "repo_committed_compatibility_fixtures",
    ):
        for entry in source_classes[class_name]:
            path = entry.get("path")
            if not isinstance(path, str):
                fail(f"{class_name}.{entry.get('id', '<unknown>')} must include path")
            if path.startswith("http://") or path.startswith("https://"):
                fail(f"{class_name}.{entry.get('id', '<unknown>')} must not use external URL authority")
            if not (REPO_ROOT / path).exists():
                fail(f"referenced repo-internal path does not exist: {path}")


def validate_external_observations(entries: list[dict[str, Any]]) -> None:
    observed: set[str] = set()
    url_count = 0
    for entry in entries:
        if entry.get("authority_status") != "non_authoritative_observation":
            fail(f"external entry {entry.get('id', '<unknown>')} must be non-authoritative")
        if entry.get("promoted_to_authority") is not False:
            fail(f"external entry {entry.get('id', '<unknown>')} must not be promoted to authority")

        url = entry.get("url")
        if url is not None:
            if not isinstance(url, str) or not url.startswith(("https://github.com/", "https://lyseste.com/")):
                fail(f"external entry {entry.get('id', '<unknown>')} has unsupported URL")
            url_count += 1

        scope = require_string_list(entry, "observed_scope")
        observed.update(scope)

    if url_count != 2:
        fail("external observations must record the public repo and app URLs only")

    missing = [phrase for phrase in REQUIRED_EXTERNAL_OBSERVED_SCOPE if phrase not in observed]
    if missing:
        fail("external observed scope missing: " + ", ".join(missing))


def validate_deferred_source_authority(entries: list[dict[str, Any]]) -> None:
    deferred = {
        entry.get("deferred_scope")
        for entry in entries
        if isinstance(entry.get("deferred_scope"), str)
    }
    missing = [phrase for phrase in REQUIRED_DEFERRED_PHRASES if phrase not in deferred]
    if missing:
        fail("deferred source authority missing: " + ", ".join(missing))


def main() -> int:
    print("glyph_configurator_compatibility_source_registry")
    try:
        registry = load_json_object(FIXTURE_PATH)
        source_classes = validate_top_level(registry)
        validate_repo_internal_paths(source_classes)
        validate_external_observations(source_classes["external_observed_non_authoritative"])
        validate_deferred_source_authority(source_classes["deferred_source_authority"])
        validate_doc(registry)
    except (OSError, json.JSONDecodeError, SourceRegistryError, ValueError) as exc:
        print("status=FAIL")
        print("source_classes=0")
        print("external_sources_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"source_classes={len(source_classes)}")
    print("external_sources_promoted_to_authority=false")
    print(f"hardware_status={registry['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
