#!/usr/bin/env python3
"""Validate the offline remapper result template scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_result_template_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_result_TEMPLATE_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_result_template"
TEMPLATE_VERSION = 1
STATUS = "template_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_RESULT_FIELDS = (
    "browser/environment",
    "external app URL/version/commit if available",
    "input artifact hash",
    "import attempt result",
    "export attempt result",
    "JSON diff result",
    "accepted/rejected field list",
    "no-device confirmation",
    "no WebSerial access confirmation",
    "no Save to Device confirmation",
    "no source-authority promotion confirmation",
    "no official/hardware compatibility claims confirmation",
)
REQUIRED_RESULT_ROWS = (
    ("ENV-001", "browser/environment recorded"),
    ("SRC-001", "external app URL/version/commit recorded if available"),
    ("INPUT-001", "active profile artifact hash confirmed"),
    ("IMPORT-001", "active profile import attempt"),
    ("EXPORT-001", "export attempt if import succeeds"),
    ("DIFF-001", "JSON diff result"),
    ("FIELDS-001", "accepted/rejected field list"),
    ("DEVICE-001", "no live device confirmation"),
    ("WS-001", "no WebSerial access confirmation"),
    ("SAVE-001", "no Save to Device confirmation"),
    ("AUTH-001", "no source authority promotion"),
    ("CLAIM-001", "no official/hardware compatibility claims"),
)
REQUIRED_CAVEATS = (
    "result template only",
    "not executed",
    "no device connected",
    "no WebSerial access",
    "no Save to Device",
    "no device write attempted",
    "not official compatibility",
    "not hardware validation",
)
REQUIRED_DOC_PHRASES = tuple(phrase.lower() for phrase in REQUIRED_CAVEATS)


class OfflineRemapperResultTemplateError(ValueError):
    """Raised when the result template drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperResultTemplateError(message)


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


def validate_template_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "template_version": TEMPLATE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "experiment_executed": False,
        "device_connected": False,
        "webserial_access_granted": False,
        "save_to_device_clicked": False,
        "device_write_attempted": False,
        "firmware_flashing_attempted": False,
        "adapter_implemented": False,
        "official_compatibility_claimed": False,
        "hardware_validation_claimed": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_result_top_level(result: dict[str, Any], result_path: Path) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "template_version": TEMPLATE_VERSION,
        "hardware_status": HARDWARE_STATUS,
        "device_connected": False,
        "webserial_access_granted": False,
        "save_to_device_clicked": False,
        "device_write_attempted": False,
        "firmware_flashing_attempted": False,
        "adapter_implemented": False,
        "official_compatibility_claimed": False,
        "hardware_validation_claimed": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            fail(f"{display(result_path)} {key} must be {value!r}")


def validate_ordered_string_list(
    payload: dict[str, Any],
    key: str,
    expected_values: tuple[str, ...],
    path: Path,
) -> None:
    values = require_string_list(payload, key)
    if tuple(values) != expected_values:
        fail(f"{display(path)} {key} drifted from required stable order")


def validate_result_rows(payload: dict[str, Any], key: str, path: Path) -> None:
    rows = payload.get(key)
    if not isinstance(rows, list) or not rows:
        fail(f"{display(path)} {key} must be a non-empty list")
    if len(rows) != len(REQUIRED_RESULT_ROWS):
        fail(f"{display(path)} {key} drifted from required row count")

    for index, (required_id, required_prompt) in enumerate(REQUIRED_RESULT_ROWS):
        row = rows[index]
        if not isinstance(row, dict):
            fail(f"{display(path)} {key}[{index}] must be an object")
        if row.get("row_id") != required_id:
            fail(f"{display(path)} {key}[{index}].row_id must be {required_id!r}")
        if row.get("prompt") != required_prompt:
            fail(f"{display(path)} {key}[{index}].prompt must be {required_prompt!r}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result",
        type=Path,
        help="Optional result fixture path to validate against the same no-device/no-write bounds.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    print("glyph_offline_remapper_result_template")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_template_top_level(fixture)
        validate_ordered_string_list(
            fixture, "required_result_fields", REQUIRED_RESULT_FIELDS, FIXTURE_PATH
        )
        validate_result_rows(fixture, "result_rows_template", FIXTURE_PATH)
        validate_ordered_string_list(
            fixture, "required_caveats", REQUIRED_CAVEATS, FIXTURE_PATH
        )
        validate_doc()

        if args.result is not None:
            result_path = args.result
            if not result_path.is_absolute():
                result_path = REPO_ROOT / result_path
            result = load_json_object(result_path)
            validate_result_top_level(result, result_path)
            validate_ordered_string_list(
                result,
                "required_result_fields",
                REQUIRED_RESULT_FIELDS,
                result_path,
            )
            validate_result_rows(result, "result_rows_template", result_path)
            validate_ordered_string_list(
                result, "required_caveats", REQUIRED_CAVEATS, result_path
            )
    except (
        OSError,
        OfflineRemapperResultTemplateError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print(f"template_status={STATUS}")
        print("experiment_executed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"template_status={STATUS}")
    print("experiment_executed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    if args.result is not None:
        result_path = args.result if args.result.is_absolute() else REPO_ROOT / args.result
        print(f"result={display(result_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
