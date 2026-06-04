#!/usr/bin/env python3
"""Validate the offline remapper experiment readiness index."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_experiment_readiness_index_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_experiment_readiness_index_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_experiment_readiness_index"
INDEX_VERSION = 1
STATUS = "ready_for_manual_no_device_experiment"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_COMPONENTS = (
    {
        "component": "input_manifest",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_experiment_input_manifest_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_experiment_input_manifest_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_experiment_input_manifest.py",
        "checker_header": "glyph_offline_remapper_experiment_input_manifest",
    },
    {
        "component": "manual_procedure",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_manual_procedure_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_manual_procedure_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_manual_procedure.py",
        "checker_header": "glyph_offline_remapper_manual_procedure",
    },
    {
        "component": "result_template",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_result_template_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_result_TEMPLATE_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_result_template.py",
        "checker_header": "glyph_offline_remapper_result_template",
    },
    {
        "component": "adapter_target_contract",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_adapter_target_contract_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_adapter_target_contract_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_adapter_target_contract.py",
        "checker_header": "glyph_offline_remapper_adapter_target_contract",
    },
    {
        "component": "adapter_mapping_plan",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_adapter_mapping_plan.py",
        "checker_header": "glyph_offline_remapper_adapter_mapping_plan",
    },
    {
        "component": "adapter_gap_matrix",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_adapter_gap_matrix.py",
        "checker_header": "glyph_offline_remapper_adapter_gap_matrix",
    },
    {
        "component": "manual_experiment_packet",
        "status": "COMPLETE",
        "doc": "docs/calibration/glyph_offline_remapper_manual_experiment_packet_2026-06-03.md",
        "fixture": "docs/calibration/fixtures/glyph_offline_remapper_manual_experiment_packet_2026-06-03.json",
        "checker": "tools/check_glyph_offline_remapper_manual_experiment_packet.py",
        "checker_header": "glyph_offline_remapper_manual_experiment_packet",
    },
)

REQUIRED_MANUAL_GATE = (
    "manual no-device operator run must be performed later and recorded in a separate result packet",
    "experiment not executed",
    "adapter not implemented",
    "no live device",
    "no WebSerial access",
    "no Save to Device",
    "not hardware validation",
)
REQUIRED_FORBIDDEN_ACTION_TERMS = (
    "live device",
    "Connect",
    "WebSerial",
    "Save to Device",
    "firmware flashing",
    "official compatibility claim",
    "hardware validation claim",
)
REQUIRED_DOC_PHRASES = (
    "ready for manual no-device experiment",
    "experiment not executed",
    "adapter not implemented",
    "no live device",
    "no webserial access",
    "no save to device",
    "not hardware validation",
)


class OfflineRemapperExperimentReadinessIndexError(ValueError):
    """Raised when the readiness index drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperExperimentReadinessIndexError(message)


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
        "index_version": INDEX_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "ready_for_manual_no_device_experiment": True,
        "experiment_executed": False,
        "adapter_implemented": False,
        "device_write_allowed": False,
        "webserial_access_allowed": False,
        "save_to_device_allowed": False,
        "hardware_validation_claimed": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_component_packets(fixture: dict[str, Any]) -> None:
    entries = fixture.get("component_packets")
    if not isinstance(entries, list) or not entries:
        fail("component_packets must be a non-empty list")
    if len(entries) != len(REQUIRED_COMPONENTS):
        fail("component_packets drifted from required count")

    for index, expected in enumerate(REQUIRED_COMPONENTS):
        entry = entries[index]
        if not isinstance(entry, dict):
            fail(f"component_packets[{index}] must be an object")
        for key in ("component", "status", "doc", "fixture", "checker"):
            if entry.get(key) != expected[key]:
                fail(f"component_packets[{index}].{key} must be {expected[key]!r}")
        for ref_key in ("doc", "fixture", "checker"):
            ref_path = REPO_ROOT / expected[ref_key]
            if not ref_path.exists():
                fail(
                    f"component_packets[{index}] references missing {ref_key}: "
                    f"{expected[ref_key]}"
                )
        run_component_checker(expected["checker"], expected["checker_header"])


def run_component_checker(rel_checker_path: str, expected_header: str) -> None:
    completed = subprocess.run(
        [sys.executable, rel_checker_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(
        part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
    )
    if completed.returncode != 0:
        fail(f"component checker failed for {rel_checker_path}: {output}")
    if expected_header not in output:
        fail(f"component checker output missing header {expected_header!r}")
    if "status=PASS" not in output:
        fail(f"component checker output missing PASS for {rel_checker_path}")


def validate_ordered_string_list(
    fixture: dict[str, Any], key: str, expected_values: tuple[str, ...]
) -> None:
    values = require_string_list(fixture, key)
    if tuple(values) != expected_values:
        fail(f"{key} drifted from required stable order")


def validate_forbidden_actions(fixture: dict[str, Any]) -> None:
    values = require_string_list(fixture, "forbidden_actions")
    combined = " | ".join(values)
    for term in REQUIRED_FORBIDDEN_ACTION_TERMS:
        if term not in combined:
            fail(f"forbidden_actions missing required term: {term}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_experiment_readiness_index")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_component_packets(fixture)
        validate_ordered_string_list(
            fixture, "required_manual_gate", REQUIRED_MANUAL_GATE
        )
        validate_forbidden_actions(fixture)
        validate_doc()
    except (
        OSError,
        OfflineRemapperExperimentReadinessIndexError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print("ready_for_manual_no_device_experiment=true")
        print("experiment_executed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("ready_for_manual_no_device_experiment=true")
    print("experiment_executed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("adapter_implemented=false")
    print("device_write_allowed=false")
    print("webserial_access_allowed=false")
    print("save_to_device_allowed=false")
    print("hardware_validation_claimed=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
