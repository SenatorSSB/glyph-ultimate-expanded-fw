#!/usr/bin/env python3
"""Validate the Glyph storage/transport research index."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_storage_transport_research_index_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_storage_transport_research_index_2026-06-03.json"
)

SCHEMA_NAME = "glyph_storage_transport_research_index"
INDEX_VERSION = 1
STATUS = "docs_tools_research_index"
HARDWARE_STATUS = "not_new_hardware_result"
REQUIRED_PACKET_IDS = (
    "storage_transport_source_authority_registry",
    "protobuf_config_schema_research_packet",
    "webserial_transport_blocker_packet",
    "runtime_storage_interpreter_blocker_packet",
)
REQUIRED_BLOCKED_IMPLEMENTATION_CLASSES = {
    "protobuf binary generation",
    "WebSerial transport",
    "device write",
    "runtime-loaded storage",
    "runtime-loaded interpreter",
    "official configurator compatibility claims",
}
REQUIRED_ALLOWED_NEXT_WORK = {
    "docs/tools validators",
    "offline JSON adapter planning",
    "manual no-device import/export experiment planning",
    "source audits",
}
REQUIRED_DISALLOWED_WITHOUT_APPROVAL = {
    "firmware source changes",
    "device write",
    "WebSerial",
    "runtime-loaded config",
    "profile artifact changes",
    "hardware validation claims",
}
REQUIRED_DOC_PHRASES = (
    "docs/tools research index",
    "all implementation classes blocked",
    "not device write behavior",
    "not webserial implementation",
    "not runtime-loaded config",
    "external observations non-authoritative",
    "not hardware validation",
)


class ResearchIndexError(ValueError):
    """Raised when the storage/transport research index drifts."""


def fail(message: str) -> None:
    raise ResearchIndexError(message)


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
        "index_version": INDEX_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "all_implementation_classes_blocked": True,
        "protobuf_binary_generation_implemented": False,
        "device_write_implemented": False,
        "webserial_transport_implemented": False,
        "runtime_loaded_storage_implemented": False,
        "runtime_loaded_interpreter_implemented": False,
        "runtime_loaded_config_implemented": False,
        "official_configurator_compatibility_claimed": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_component_packets(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    packets = require_object_list(
        fixture.get("required_component_packets"),
        "required_component_packets",
    )
    packet_ids: list[str] = []
    for index, packet in enumerate(packets):
        packet_id = require_string(packet.get("packet_id"), f"required_component_packets[{index}].packet_id")
        packet_ids.append(packet_id)
        require_string(packet.get("status_summary"), f"{packet_id}.status_summary")
        for key in ("doc_path", "fixture_path", "checker_path"):
            relpath = require_string(packet.get(key), f"{packet_id}.{key}")
            if relpath.startswith(("http://", "https://")):
                fail(f"{packet_id}.{key} must reference a repo path, not a URL")
            if not (REPO_ROOT / relpath).exists():
                fail(f"{packet_id}.{key} references missing path: {relpath}")
    if tuple(packet_ids) != REQUIRED_PACKET_IDS:
        fail("required_component_packets must preserve the required packet ids in stable order")
    return packets


def validate_required_subset(fixture: dict[str, Any], key: str, required: set[str]) -> None:
    observed = set(require_string_list(fixture.get(key), key))
    missing = sorted(required - observed)
    if missing:
        fail(f"{key} is missing required entries: " + ", ".join(missing))


def validate_doc(fixture: dict[str, Any]) -> None:
    doc_caveats = require_string_list(fixture.get("doc_caveats"), "doc_caveats")
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")
    for phrase in doc_caveats:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing fixture-declared caveat phrase: {phrase}")


def run_checker(path: Path) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode, output


def validate_component_checkers(packets: list[dict[str, Any]]) -> None:
    for packet in packets:
        checker_relpath = packet["checker_path"]
        returncode, output = run_checker(REPO_ROOT / checker_relpath)
        if returncode != 0:
            fail(f"component checker failed for {checker_relpath}: {output}")


def main() -> int:
    print("glyph_storage_transport_research_index")
    component_packets = 0
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        packets = validate_component_packets(fixture)
        component_packets = len(packets)
        validate_required_subset(
            fixture,
            "blocked_implementation_classes",
            REQUIRED_BLOCKED_IMPLEMENTATION_CLASSES,
        )
        validate_required_subset(fixture, "allowed_next_work", REQUIRED_ALLOWED_NEXT_WORK)
        validate_required_subset(
            fixture,
            "disallowed_without_approval",
            REQUIRED_DISALLOWED_WITHOUT_APPROVAL,
        )
        validate_doc(fixture)
        validate_component_checkers(packets)
    except (OSError, ResearchIndexError, ValueError) as exc:
        print("status=FAIL")
        print(f"component_packets={component_packets}")
        print("all_implementation_classes_blocked=true")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"component_packets={component_packets}")
    print("all_implementation_classes_blocked=true")
    print(f"hardware_status={fixture['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
