#!/usr/bin/env python3
"""Validate the Glyph protobuf/config schema research packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json"
)

SCHEMA_NAME = "glyph_protobuf_config_schema_research_packet"
PACKET_VERSION = 1
STATUS = "docs_tools_research_packet"
HARDWARE_STATUS = "not_new_hardware_result"
KNOWN_SHAPE_IDS = (
    "active_profile_artifact_json_shape",
    "generated_config_runtime_candidate_shape",
    "senscope_export_package_shape",
    "serial_dry_run_behavior",
    "repo_internal_protobuf_config_assumptions",
)
EXTERNAL_OBSERVATION_IDS = (
    "external_remapper_protobuf_encode_decode_claim",
    "external_remapper_webserial_load_save_claim",
    "external_remapper_configurator_compatibility_claim",
)
ALLOWED_KNOWN_AUTHORITY_STATUS = {
    "repo_fixture_evidence",
    "repo_docs_tools_boundary",
}
EXTERNAL_AUTHORITY_STATUS = "non_authoritative_external_observation"
REQUIRED_MISSING_AUTHORITY = {
    "official protobuf/schema source",
    "official configurator compatibility source",
}
REQUIRED_BLOCKED_IMPLEMENTATIONS = {
    "protobuf binary generation",
    "device write",
    "WebSerial transport",
    "runtime-loaded config",
}
REQUIRED_DOC_PHRASES = (
    "official protobuf/schema source authority missing",
    "not protobuf binary generation",
    "not official configurator compatibility",
    "not device write behavior",
    "external observations non-authoritative",
    "not hardware validation",
)


class ResearchPacketError(ValueError):
    """Raised when the protobuf/config schema research packet drifts."""


def fail(message: str) -> None:
    raise ResearchPacketError(message)


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
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{label}[{index}] must be a non-empty string")
        result.append(item)
    return result


def require_object_list(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty object list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"{label}[{index}] must be an object")
        result.append(item)
    return result


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "packet_version": PACKET_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "official_protobuf_schema_authority_present": False,
        "protobuf_binary_generation_implemented": False,
        "official_configurator_compatibility_claimed": False,
        "device_write_implemented": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_known_repo_internal_shapes(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    shapes = require_object_list(
        fixture.get("known_repo_internal_shapes"),
        "known_repo_internal_shapes",
    )
    ids: list[str] = []
    for index, entry in enumerate(shapes):
        shape_id = require_string(entry.get("shape_id"), f"known_repo_internal_shapes[{index}].shape_id")
        ids.append(shape_id)
        authority_status = entry.get("authority_status")
        if authority_status not in ALLOWED_KNOWN_AUTHORITY_STATUS:
            fail(f"{shape_id}.authority_status is unsupported: {authority_status!r}")
        repo_paths = require_string_list(entry.get("repo_paths"), f"{shape_id}.repo_paths")
        require_string(entry.get("observed_shape"), f"{shape_id}.observed_shape")
        for relpath in repo_paths:
            if relpath.startswith(("http://", "https://")):
                fail(f"{shape_id}.repo_paths must reference repo files only: {relpath}")
            if not (REPO_ROOT / relpath).exists():
                fail(f"{shape_id}.repo_paths references missing path: {relpath}")

    if tuple(ids) != KNOWN_SHAPE_IDS:
        fail("known_repo_internal_shapes must preserve the required shape ids in stable order")
    return shapes


def validate_external_observations(fixture: dict[str, Any]) -> None:
    observations = require_object_list(
        fixture.get("external_observations"),
        "external_observations",
    )
    ids: list[str] = []
    for index, entry in enumerate(observations):
        observation_id = require_string(
            entry.get("observation_id"),
            f"external_observations[{index}].observation_id",
        )
        ids.append(observation_id)
        if entry.get("authority_status") != EXTERNAL_AUTHORITY_STATUS:
            fail(f"{observation_id}.authority_status must be {EXTERNAL_AUTHORITY_STATUS!r}")
        if entry.get("promoted_to_authority") is not False:
            fail(f"{observation_id}.promoted_to_authority must be false")
        repo_paths = require_string_list(entry.get("repo_paths"), f"{observation_id}.repo_paths")
        summary = require_string(entry.get("summary"), f"{observation_id}.summary")
        if "non-authoritative" not in summary.lower():
            fail(f"{observation_id}.summary must preserve non-authoritative language")
        for relpath in repo_paths:
            if relpath.startswith(("http://", "https://")):
                fail(f"{observation_id}.repo_paths must reference repo files only: {relpath}")
            if not (REPO_ROOT / relpath).exists():
                fail(f"{observation_id}.repo_paths references missing path: {relpath}")

    if tuple(ids) != EXTERNAL_OBSERVATION_IDS:
        fail("external_observations must preserve the required observation ids in stable order")


def validate_missing_authority(fixture: dict[str, Any]) -> None:
    missing_authority = set(require_string_list(fixture.get("missing_authority"), "missing_authority"))
    missing = sorted(REQUIRED_MISSING_AUTHORITY - missing_authority)
    if missing:
        fail("missing_authority is missing required entries: " + ", ".join(missing))


def validate_blocked_implementation_classes(fixture: dict[str, Any]) -> None:
    blocked = set(
        require_string_list(
            fixture.get("blocked_implementation_classes"),
            "blocked_implementation_classes",
        )
    )
    missing = sorted(REQUIRED_BLOCKED_IMPLEMENTATIONS - blocked)
    if missing:
        fail("blocked_implementation_classes is missing required entries: " + ", ".join(missing))


def validate_doc(fixture: dict[str, Any]) -> None:
    doc_caveats = require_string_list(fixture.get("doc_caveats"), "doc_caveats")
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")
    for phrase in doc_caveats:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing fixture-declared caveat phrase: {phrase}")


def main() -> int:
    print("glyph_protobuf_config_schema_research_packet")
    known_shapes_count = 0
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        known_shapes = validate_known_repo_internal_shapes(fixture)
        known_shapes_count = len(known_shapes)
        validate_external_observations(fixture)
        validate_missing_authority(fixture)
        validate_blocked_implementation_classes(fixture)
        validate_doc(fixture)
    except (OSError, ResearchPacketError, ValueError) as exc:
        print("status=FAIL")
        print(f"known_repo_internal_shapes={known_shapes_count}")
        print("official_protobuf_schema_authority_present=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"known_repo_internal_shapes={known_shapes_count}")
    print("official_protobuf_schema_authority_present=false")
    print(f"hardware_status={fixture['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
