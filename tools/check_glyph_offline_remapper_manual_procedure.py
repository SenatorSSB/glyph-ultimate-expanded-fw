#!/usr/bin/env python3
"""Validate the offline remapper manual procedure checklist."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_manual_procedure_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_manual_procedure_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_manual_procedure"
PROCEDURE_VERSION = 1
STATUS = "procedure_only_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_STEPS = (
    "open external app URL https://lyseste.com/glyph-remapper/",
    "ensure no Glyph/live device is connected",
    "record browser/environment",
    "record external app URL/version/commit if visible",
    "do not click Connect",
    "do not grant WebSerial device access",
    "do not click Save to Device",
    "import primary active profile artifact docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
    "record whether import succeeds/fails/blocks",
    "export JSON if import succeeds",
    "save exported JSON outside repo first",
    "compute/record exported artifact hash later in result fixture",
    "compare exported JSON only in later result-recording branch",
    "record screenshots/notes optionally",
    "do not change repo fixtures to fit external app",
    "do not claim official compatibility",
    "do not claim hardware validation",
)
REQUIRED_FORBIDDEN_ACTIONS = (
    "live device connected",
    "clicking Connect",
    "granting WebSerial device access",
    "clicking Save to Device",
    "serial/device write",
    "firmware flashing",
    "adapter implementation",
    "artifact transformation/generation",
    "protobuf binary generation",
    "runtime-loaded config implementation",
    "copying external source code",
    "changing repo fixtures to fit external app",
    "claiming official compatibility",
    "claiming hardware validation",
)
REQUIRED_OBSERVATIONS = (
    "no-device confirmation",
    "browser/environment",
    "external app URL/version/commit if visible",
    "primary active profile artifact path",
    "import succeeds/fails/blocks",
    "export JSON path outside repo if import succeeds",
    "exported artifact hash pending separate result fixture",
    "screenshots/notes optional",
    "not official compatibility",
    "not hardware validation",
)
REQUIRED_RESULT_OUTPUT_EXPECTATIONS = (
    "separate result doc/fixture only",
    "exported artifact hash computed later after saving outside repo first",
    "exported JSON comparison only in later result-recording branch",
    "repo fixtures unchanged to fit external app",
    "no official compatibility claim",
    "no hardware validation claim",
    "no source-authority promotion",
)
REQUIRED_DOC_PHRASES = (
    "procedure only",
    "not executed",
    "no live device",
    "do not click connect",
    "do not click save to device",
    "do not grant webserial",
    "not official compatibility",
    "not hardware validation",
)


class OfflineRemapperManualProcedureError(ValueError):
    """Raised when the manual procedure drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperManualProcedureError(message)


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
        "procedure_version": PROCEDURE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "experiment_executed": False,
        "device_write_allowed": False,
        "webserial_access_allowed": False,
        "save_to_device_allowed": False,
        "adapter_implemented": False,
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


def validate_no_device_transport_bounds(fixture: dict[str, Any]) -> None:
    steps = " | ".join(require_string_list(fixture, "steps")).lower()
    forbidden = " | ".join(require_string_list(fixture, "forbidden_actions")).lower()
    combined = f"{steps} | {forbidden}"
    required_terms = (
        "no glyph/live device",
        "do not click connect",
        "do not grant webserial device access",
        "do not click save to device",
        "serial/device write",
    )
    for term in required_terms:
        if term not in combined:
            fail(f"manual procedure missing no-device/transport guardrail: {term}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_manual_procedure")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_ordered_string_list(fixture, "steps", REQUIRED_STEPS)
        validate_ordered_string_list(
            fixture, "forbidden_actions", REQUIRED_FORBIDDEN_ACTIONS
        )
        validate_ordered_string_list(
            fixture, "required_observations", REQUIRED_OBSERVATIONS
        )
        validate_ordered_string_list(
            fixture,
            "result_output_expectations",
            REQUIRED_RESULT_OUTPUT_EXPECTATIONS,
        )
        validate_no_device_transport_bounds(fixture)
        validate_doc()
    except (
        OSError,
        OfflineRemapperManualProcedureError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print(f"steps={len(REQUIRED_STEPS)}")
        print("experiment_executed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"steps={len(REQUIRED_STEPS)}")
    print("experiment_executed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("device_write_allowed=false")
    print("webserial_access_allowed=false")
    print("save_to_device_allowed=false")
    print("adapter_implemented=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
