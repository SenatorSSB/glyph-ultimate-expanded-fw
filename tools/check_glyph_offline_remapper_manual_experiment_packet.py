#!/usr/bin/env python3
"""Validate the offline remapper manual experiment packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_manual_experiment_packet_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_manual_experiment_packet_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_manual_experiment_packet"
PACKET_VERSION = 1
STATUS = "planned_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_SCOPE = (
    "no-device import/export compatibility check",
    "external remapper app/repo version recording",
    "sample input artifact hashes",
    "import attempt",
    "export attempt",
    "JSON diff report",
    "accepted/rejected field list",
    "screenshots/notes optional",
)
REQUIRED_PREREQUISITES = (
    "source audit snapshot current",
    "gap matrix current",
    "license review status recorded",
    "no live device connected",
    "browser/environment noted",
    "input artifacts checksummed",
)
REQUIRED_FORBIDDEN_ACTIONS = (
    "connecting live Glyph",
    "WebSerial write",
    "Save to Device",
    "firmware flashing",
    "claiming official compatibility",
    "claiming hardware validation",
    "copying external source code",
    "changing repo fixtures to fit external app",
)
REQUIRED_RESULT_RECORDING_REQUIREMENTS = (
    "separate result doc/fixture",
    "external app URL/version/commit if available",
    "browser/environment",
    "input artifact hash",
    "exported artifact hash",
    "pass/fail/blocked rows",
    "no-device confirmation",
    "no hardware validation caveat",
    "no source-authority promotion caveat",
)
REQUIRED_CANDIDATE_INPUTS = (
    (
        "Senscope export package sample",
        "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json",
        "3497ce3150620a60838c50f58438250f472c121b3ce9623d3223ea5f780717a1",
    ),
    (
        "Runtime config candidate sample",
        "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json",
        "e4e9b0e47b36f9f8585b37ac0e9f3cba2b6ae2833d79121e99af602c9d48543f",
    ),
    (
        "Active profile artifact",
        "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
        "0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707",
    ),
)
REQUIRED_DOC_PHRASES = (
    "planned not executed",
    "no live device",
    "no webserial write",
    "no save to device",
    "adapter not implemented",
    "not official compatibility",
    "not hardware validation",
)


class OfflineRemapperManualExperimentPacketError(ValueError):
    """Raised when the manual experiment packet drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperManualExperimentPacketError(message)


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
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{key}[{index}] must be a non-empty string")
        result.append(item)
    return result


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "packet_version": PACKET_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "experiment_executed": False,
        "adapter_implemented": False,
        "device_write_allowed": False,
        "webserial_write_allowed": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_ordered_string_list(
    fixture: dict[str, Any], key: str, expected_values: tuple[str, ...]
) -> None:
    values = require_string_list(fixture, key)
    if tuple(values) != expected_values:
        fail(f"{key} drifted from required stable order")


def sha256_for(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_candidate_inputs(fixture: dict[str, Any]) -> None:
    entries = fixture.get("candidate_inputs")
    if not isinstance(entries, list) or not entries:
        fail("candidate_inputs must be a non-empty list")
    if len(entries) != len(REQUIRED_CANDIDATE_INPUTS):
        fail("candidate_inputs drifted from required count")

    for index, (label, relpath, expected_sha) in enumerate(REQUIRED_CANDIDATE_INPUTS):
        entry = entries[index]
        if not isinstance(entry, dict):
            fail(f"candidate_inputs[{index}] must be an object")
        if entry.get("label") != label:
            fail(f"candidate_inputs[{index}].label must be {label!r}")
        if entry.get("path") != relpath:
            fail(f"candidate_inputs[{index}].path must be {relpath!r}")
        if entry.get("sha256") != expected_sha:
            fail(f"candidate_inputs[{index}].sha256 must be {expected_sha!r}")

        input_path = REPO_ROOT / relpath
        if not input_path.exists():
            fail(f"candidate_inputs[{index}] references missing path: {relpath}")
        actual_sha = sha256_for(input_path)
        if actual_sha != expected_sha:
            fail(
                f"candidate_inputs[{index}] sha256 mismatch for {relpath}: "
                f"expected {expected_sha}, got {actual_sha}"
            )


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_manual_experiment_packet")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_ordered_string_list(fixture, "experiment_scope", REQUIRED_SCOPE)
        validate_ordered_string_list(
            fixture, "required_prerequisites", REQUIRED_PREREQUISITES
        )
        validate_candidate_inputs(fixture)
        validate_ordered_string_list(
            fixture, "forbidden_actions", REQUIRED_FORBIDDEN_ACTIONS
        )
        validate_ordered_string_list(
            fixture,
            "result_recording_requirements",
            REQUIRED_RESULT_RECORDING_REQUIREMENTS,
        )
        validate_doc()
    except (
        OSError,
        OfflineRemapperManualExperimentPacketError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print("experiment_executed=false")
        print("adapter_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("experiment_executed=false")
    print("adapter_implemented=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("device_write_allowed=false")
    print("webserial_write_allowed=false")
    print("external_source_promoted_to_authority=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
