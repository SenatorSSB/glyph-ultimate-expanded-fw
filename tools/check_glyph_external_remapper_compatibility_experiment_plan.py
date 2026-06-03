#!/usr/bin/env python3
"""Validate the external remapper compatibility experiment plan."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.json"
)

SCHEMA_NAME = "glyph_external_remapper_compatibility_experiment_plan"
PLAN_VERSION = 1
STATUS = "planned_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_PREREQUISITES = (
    "full source audit",
    "license review",
    "static JSON schema comparison",
    "safe sample config generation",
    "no live device connected",
    "no WebSerial write",
    "no firmware flashing",
)
REQUIRED_CANDIDATE_INPUTS = (
    "Senscope export package sample",
    "runtime config candidate sample",
    "active profile artifact",
)
REQUIRED_EXPECTED_OUTPUTS = (
    "external-remapper import test notes",
    "JSON diff report",
    "rejected/accepted field list",
    "no device write confirmation",
)
REQUIRED_FORBIDDEN_ACTIONS = (
    "connecting live device",
    "Save to Device",
    "WebSerial write",
    "firmware flashing",
    "claiming official compatibility",
    "claiming hardware validation",
    "copying external source code",
)
REQUIRED_RESULT_RECORDING_REQUIREMENTS = (
    "separate result doc/fixture",
    "external app/repo version or commit",
    "browser/environment notes",
    "exact sample artifact hash",
    "pass/fail/blocked rows",
    "no hardware validation caveat",
)
REQUIRED_DOC_PHRASES = (
    "planned_not_executed",
    "no live device",
    "no webserial write",
    "not device write behavior",
    "not official compatibility",
    "not hardware validation",
)


class ExternalRemapperCompatibilityExperimentPlanError(ValueError):
    """Raised when the compatibility experiment plan drifts from constraints."""


def fail(message: str) -> None:
    raise ExternalRemapperCompatibilityExperimentPlanError(message)


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
        "plan_version": PLAN_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "experiment_executed": False,
        "device_write_allowed": False,
        "webserial_write_allowed": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_required_lists(fixture: dict[str, Any]) -> None:
    expected_lists = {
        "required_prerequisites": REQUIRED_PREREQUISITES,
        "candidate_inputs": REQUIRED_CANDIDATE_INPUTS,
        "expected_outputs": REQUIRED_EXPECTED_OUTPUTS,
        "forbidden_actions": REQUIRED_FORBIDDEN_ACTIONS,
        "result_recording_requirements": REQUIRED_RESULT_RECORDING_REQUIREMENTS,
    }
    for key, required in expected_lists.items():
        values = require_string_list(fixture, key)
        if tuple(values) != required:
            fail(f"{key} drifted from required stable order")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_compatibility_experiment_plan")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_required_lists(fixture)
        validate_doc()
    except (OSError, ExternalRemapperCompatibilityExperimentPlanError, ValueError) as exc:
        print("status=FAIL")
        print("experiment_executed=false")
        print("device_write_allowed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("experiment_executed=false")
    print("device_write_allowed=false")
    print("webserial_write_allowed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("external_source_promoted_to_authority=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
