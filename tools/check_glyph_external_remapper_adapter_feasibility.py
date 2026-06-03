#!/usr/bin/env python3
"""Validate the external remapper future adapter feasibility report."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_external_remapper_adapter_feasibility_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_adapter_feasibility_2026-06-03.json"
)

SCHEMA_NAME = "glyph_external_remapper_adapter_feasibility"
FEASIBILITY_VERSION = 1
STATUS = "future_adapter_feasibility_report"
HARDWARE_STATUS = "not_new_hardware_result"
FEASIBILITY_STATUS = "feasible_for_future_offline_json_adapter_after_source_audit"

REQUIRED_NOT_FEASIBLE_YET = (
    "WebSerial/device write",
    "protobuf binary generation",
    "runtime-loaded config",
    "custom modifier representation",
    "official configurator compatibility claims",
)
REQUIRED_BLOCKED_DECISIONS = (
    "full source audit",
    "license review",
    "JSON schema comparison",
    "protobuf schema comparison",
    "custom profile/modifier representation comparison",
    "manual import/export experiment",
    "user approval before integration",
)
REQUIRED_POSSIBLE_INPUTS = (
    "Senscope export package sample",
    "runtime config candidate",
    "generated config prototype",
    "validation report",
)
REQUIRED_POSSIBLE_OUTPUTS = (
    "external-remapper-compatible JSON candidate, not device-writeable",
    "compatibility report",
)
REQUIRED_DOC_PHRASES = (
    "future adapter only",
    "adapter not implemented",
    "not device write behavior",
    "not runtime-loaded config",
    "not hardware validation",
    "external source not authority",
)


class ExternalRemapperAdapterFeasibilityError(ValueError):
    """Raised when the feasibility report drifts from the allowed boundary."""


def fail(message: str) -> None:
    raise ExternalRemapperAdapterFeasibilityError(message)


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
        "feasibility_version": FEASIBILITY_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "external_source_promoted_to_authority": False,
        "adapter_implemented": False,
        "device_write_implemented": False,
        "runtime_loaded_config_implemented": False,
        "feasibility_status": FEASIBILITY_STATUS,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_required_lists(fixture: dict[str, Any]) -> None:
    expected_lists = {
        "possible_future_inputs": REQUIRED_POSSIBLE_INPUTS,
        "possible_future_outputs": REQUIRED_POSSIBLE_OUTPUTS,
        "not_feasible_yet": REQUIRED_NOT_FEASIBLE_YET,
        "blocked_decisions": REQUIRED_BLOCKED_DECISIONS,
    }
    for key, required in expected_lists.items():
        values = require_string_list(fixture, key)
        if tuple(values) != required:
            fail(f"{key} drifted from required stable order")

    required_approvals = require_string_list(fixture, "required_approvals")
    if "user approval before integration" not in required_approvals:
        fail("required_approvals must include user approval before integration")

    forbidden = require_string_list(fixture, "forbidden_interpretations")
    for item in (
        "external source authority",
        "official configurator compatibility claim",
        "adapter implemented",
        "device write behavior implemented",
        "runtime-loaded config implemented",
        "hardware validation claimed",
    ):
        if item not in forbidden:
            fail(f"forbidden_interpretations missing: {item}")


def validate_source_inputs(fixture: dict[str, Any]) -> None:
    for relpath in require_string_list(fixture, "source_inputs"):
        if not (REPO_ROOT / relpath).exists():
            fail(f"source_inputs references missing path: {relpath}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    if FEASIBILITY_STATUS not in lowered:
        fail(f"{display(DOC_PATH)} missing feasibility status")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_adapter_feasibility")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_required_lists(fixture)
        validate_source_inputs(fixture)
        validate_doc()
    except (OSError, ExternalRemapperAdapterFeasibilityError, ValueError) as exc:
        print("status=FAIL")
        print("adapter_implemented=false")
        print("external_source_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("adapter_implemented=false")
    print("external_source_promoted_to_authority=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("device_write_implemented=false")
    print("runtime_loaded_config_implemented=false")
    print(f"feasibility_status={FEASIBILITY_STATUS}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
