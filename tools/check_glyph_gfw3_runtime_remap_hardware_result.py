#!/usr/bin/env python3
"""Validate the GFW3 runtime remap user-reported hardware result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_test_plan_2026-06-04.json"
)
RESULT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.json"
)
RESULT_DOC_PATH = REPO_ROOT / "docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_gfw3_runtime_remap_hardware_result",
    "result_version": 1,
    "result_date": "2026-06-06",
    "status": "user_reported_hardware_pass",
    "tested_branch": "glyph/gfw3-runtime-remap-rework",
    "hardware_status": "user_hardware_validated",
    "hardware_validation_claimed": True,
    "runtime_loaded_config_implemented": False,
    "webserial_write_implemented": False,
    "device_write_implemented": False,
    "profile_artifact_changed": False,
    "nunchuk_hardware_validated": False,
    "nunchuk_status": "not_tested_or_not_claimed",
}

EXPECTED_MERGE_GATE = {
    "gfw3_runtime_remap_hardware_gate": "satisfied_by_user_reported_hardware_pass",
    "unblocks_merge_to_configurator_if_checks_and_build_pass": True,
    "must_not_claim_nunchuk_hardware_validation": True,
    "must_not_claim_runtime_loaded_config": True,
    "must_not_claim_webserial_or_device_write": True,
    "must_not_claim_active_profile_artifact_change": True,
}

REQUIRED_DOC_PHRASES = (
    "user-reported hardware pass",
    "Branch tested: `glyph/gfw3-runtime-remap-rework`",
    "No active profile artifact change",
    "No runtime-loaded config",
    "No WebSerial write",
    "No serial/device write",
    "Nunchuk was not hardware-validated",
    "GFW3 runtime remap behavior only",
    "unblocks merge of `glyph/gfw3-runtime-remap-rework` into `configurator` if",
)


class HardwareResultError(AssertionError):
    """Raised when the hardware result packet drifts from its contract."""


def fail(message: str) -> None:
    raise HardwareResultError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def rows_by_id(fixture: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    rows = fixture.get(key)
    if not isinstance(rows, list):
        fail(f"{key} must be a list")

    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            fail(f"{key}[{index}] must be an object")
        row_id = row.get("row_id")
        if not isinstance(row_id, str) or not row_id:
            fail(f"{key}[{index}].row_id must be a non-empty string")
        if row_id in by_id:
            fail(f"{key} contains duplicate row_id: {row_id}")
        by_id[row_id] = row
    return by_id


def validate_top_level(result: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if result.get(key) != expected:
            fail(f"{key} must be {expected!r}")
    if result.get("user_report") != "everything passing as expected":
        fail("user_report must preserve the reported pass text")
    if result.get("validation_scope") != "GFW3 runtime remap behavior only":
        fail("validation_scope must be limited to GFW3 runtime remap behavior only")


def validate_merge_gate(result: dict[str, Any]) -> None:
    merge_gate = result.get("merge_gate_interpretation")
    if not isinstance(merge_gate, dict):
        fail("merge_gate_interpretation must be an object")
    for key, expected in EXPECTED_MERGE_GATE.items():
        if merge_gate.get(key) != expected:
            fail(f"merge_gate_interpretation.{key} must be {expected!r}")


def validate_rows(plan: dict[str, Any], result: dict[str, Any]) -> tuple[int, int]:
    plan_rows = rows_by_id(plan, "test_rows")
    result_rows = rows_by_id(result, "rows")

    missing = sorted(set(plan_rows) - set(result_rows))
    unexpected = sorted(set(result_rows) - set(plan_rows))
    if missing:
        fail("result missing row(s): " + ", ".join(missing))
    if unexpected:
        fail("result contains unexpected row(s): " + ", ".join(unexpected))

    passed_rows = 0
    not_tested_rows = 0
    for row_id in sorted(plan_rows):
        plan_row = plan_rows[row_id]
        result_row = result_rows[row_id]
        for key in ("category", "input_condition", "directions", "expected_result"):
            if result_row.get(key) != plan_row.get(key):
                fail(f"{row_id}.{key} must match the hardware test plan fixture")
        notes = result_row.get("notes")
        if not isinstance(notes, str) or not notes:
            fail(f"{row_id}.notes must be a non-empty string")

        plan_status = plan_row.get("status")
        result_status = result_row.get("status")
        if row_id == "nunchuk_preserved_not_tested":
            if plan_status != "not_executed_unavailable":
                fail("nunchuk row must remain unavailable in the source test plan")
            if result_status != "NOT_TESTED":
                fail("nunchuk row must remain NOT_TESTED unless explicitly reported")
            not_tested_rows += 1
            continue

        if plan_status != "not_executed":
            fail(f"{row_id} has unsupported source plan status {plan_status!r}")
        if result_status != "PASS":
            fail(f"{row_id} must be PASS under the accepted user report")
        passed_rows += 1

    return passed_rows, not_tested_rows


def validate_no_forbidden_claims(result: dict[str, Any]) -> None:
    forbidden_true_keys = (
        "runtime_loaded_config_implemented",
        "webserial_write_implemented",
        "device_write_implemented",
        "profile_artifact_changed",
        "generated_config_export_artifacts_changed",
        "nunchuk_hardware_validated",
    )
    for key in forbidden_true_keys:
        if result.get(key) is not False:
            fail(f"{key} must be false")


def validate_doc(plan: dict[str, Any]) -> None:
    if not RESULT_DOC_PATH.exists():
        fail(f"missing result doc: {display(RESULT_DOC_PATH)}")
    text = RESULT_DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"result doc missing required phrase: {phrase}")
    for row_id in rows_by_id(plan, "test_rows"):
        if row_id not in text:
            fail(f"result doc missing row ID: {row_id}")


def main() -> int:
    print("glyph_gfw3_runtime_remap_hardware_result")
    try:
        plan = load_json_object(PLAN_FIXTURE_PATH)
        result = load_json_object(RESULT_FIXTURE_PATH)
        validate_top_level(result)
        validate_merge_gate(result)
        validate_no_forbidden_claims(result)
        passed_rows, not_tested_rows = validate_rows(plan, result)
        validate_doc(plan)
    except (OSError, HardwareResultError, ValueError) as exc:
        print("status=FAIL")
        print("hardware_status=user_hardware_validated")
        print("hardware_validation_claimed=true")
        print("nunchuk_hardware_validated=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("hardware_status=user_hardware_validated")
    print("hardware_validation_claimed=true")
    print(f"passed_rows={passed_rows}")
    print(f"not_tested_rows={not_tested_rows}")
    print("nunchuk_hardware_validated=false")
    print("merge_gate=satisfied_if_checks_and_build_pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
