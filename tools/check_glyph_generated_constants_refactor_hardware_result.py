#!/usr/bin/env python3
"""Validate the generated constants refactor hardware result record.

This checker is read-only and stdlib-only. It validates the branch-specific
hardware result fixture/doc for the generated constants refactor without making
hardware, runtime-loaded config, serial/device write, or nunchuk claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_generated_constants_refactor_hardware_result_2026-06-03.md"
)
RESULT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_generated_constants_refactor_hardware_result_2026-06-03.json"
)
MATRIX_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.json"
)

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_generated_constants_refactor_hardware_result",
    "result_version": 1,
    "result_date": "2026-06-03",
    "branch_under_test": "glyph/gfw2-generated-constants-refactor",
    "implementation_class": "generated_constants_firmware_refactor",
    "hardware_status": "hardware_result_with_user_accepted_risk",
    "nunchuk_status": "not_hardware_validated",
    "cstick_suppression_status": "not_tested_user_accepted_risk",
    "runtime_loaded_config_status": "not_implemented_not_validated",
    "serial_device_write_status": "not_implemented_not_validated",
    "profile_artifact_status": "no_regression_reported",
}
EXPECTED_SOURCE_MATRIX = "docs/calibration/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.md"
EXPECTED_PASS_EXCEPTIONS = {
    "CSUP-001": "NOT_TESTED_USER_ACCEPTED_RISK",
    "NUNCHUK-001": "NOT_TESTED",
}
EXPECTED_MERGE_GATE = {
    "generated_constants_refactor_hardware_gate": "satisfied_with_user_accepted_risk_for_csup_001",
    "must_not_claim_full_cstick_suppression_validation": True,
    "must_not_claim_nunchuk_hardware_validation": True,
    "future_cstick_behavior_changes_require_csup_test": True,
}
REQUIRED_DOC_PHRASES = (
    "not full C-stick suppression hardware validation",
    "not nunchuk hardware validation",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "user-accepted risk",
    "CSUP-001",
)


class HardwareResultError(AssertionError):
    """Raised when the hardware result record is not trustworthy."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise HardwareResultError(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON fixture {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON fixture must contain an object: {display(path)}")
    return payload


def require_top_level(result: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if result.get(key) != expected:
            fail(f"{key} must be {expected!r}")
    if result.get("source_matrix") != EXPECTED_SOURCE_MATRIX:
        fail(f"source_matrix must be {EXPECTED_SOURCE_MATRIX!r}")


def matrix_rows_by_id(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = matrix.get("test_rows")
    if not isinstance(rows, list):
        fail("matrix fixture test_rows must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("matrix fixture rows must be objects")
        row_id = row.get("row_id")
        category = row.get("category")
        if not isinstance(row_id, str) or not row_id:
            fail("matrix row missing row_id")
        if not isinstance(category, str) or not category:
            fail(f"matrix row {row_id} missing category")
        if row_id in by_id:
            fail(f"matrix contains duplicate row_id: {row_id}")
        by_id[row_id] = row
    return by_id


def result_rows_by_id(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = result.get("rows")
    if not isinstance(rows, list):
        fail("result fixture rows must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("result rows must be objects")
        row_id = row.get("row_id")
        category = row.get("category")
        status = row.get("status")
        notes = row.get("notes")
        if not isinstance(row_id, str) or not row_id:
            fail("result row missing row_id")
        if not isinstance(category, str) or not category:
            fail(f"result row {row_id} missing category")
        if not isinstance(status, str) or not status:
            fail(f"result row {row_id} missing status")
        if not isinstance(notes, str) or not notes:
            fail(f"result row {row_id} missing notes")
        if row_id in by_id:
            fail(f"result contains duplicate row_id: {row_id}")
        by_id[row_id] = row
    return by_id


def validate_row_coverage(matrix: dict[str, Any], result: dict[str, Any]) -> tuple[int, int]:
    matrix_rows = matrix_rows_by_id(matrix)
    result_rows = result_rows_by_id(result)

    matrix_ids = set(matrix_rows)
    result_ids = set(result_rows)
    missing = sorted(matrix_ids - result_ids)
    unexpected = sorted(result_ids - matrix_ids)
    if missing:
        fail("result missing row(s): " + ", ".join(missing))
    if unexpected:
        fail("result contains unexpected row(s): " + ", ".join(unexpected))

    passed_rows = 0
    not_tested_rows = 0
    for row_id in sorted(matrix_ids):
        matrix_category = matrix_rows[row_id]["category"]
        row = result_rows[row_id]
        if row.get("category") != matrix_category:
            fail(f"{row_id} category must match matrix category {matrix_category!r}")
        status = row["status"]
        expected_exception_status = EXPECTED_PASS_EXCEPTIONS.get(row_id)
        if expected_exception_status is None:
            if status != "PASS":
                fail(f"{row_id} must be PASS")
            passed_rows += 1
            continue
        if status != expected_exception_status:
            fail(f"{row_id} must be {expected_exception_status}")
        not_tested_rows += 1

    return passed_rows, not_tested_rows


def validate_merge_gate(result: dict[str, Any]) -> None:
    merge_gate = result.get("merge_gate_interpretation")
    if not isinstance(merge_gate, dict):
        fail("merge_gate_interpretation must be an object")
    for key, expected in EXPECTED_MERGE_GATE.items():
        if merge_gate.get(key) != expected:
            fail(f"merge_gate_interpretation.{key} must be {expected!r}")


def validate_doc_phrases() -> None:
    if not RESULT_DOC_PATH.exists():
        fail(f"missing result doc: {display(RESULT_DOC_PATH)}")
    doc_text = RESULT_DOC_PATH.read_text(encoding="utf-8")
    lowered = doc_text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"result doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_generated_constants_refactor_hardware_result")
    try:
        result = load_json(RESULT_FIXTURE_PATH)
        matrix = load_json(MATRIX_FIXTURE_PATH)
        require_top_level(result)
        passed_rows, not_tested_rows = validate_row_coverage(matrix, result)
        validate_merge_gate(result)
        validate_doc_phrases()
    except HardwareResultError as exc:
        print("status=FAIL")
        print("passed_rows=0")
        print("not_tested_rows=0")
        print("hardware_status=hardware_result_with_user_accepted_risk")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"passed_rows={passed_rows}")
    print(f"not_tested_rows={not_tested_rows}")
    print("hardware_status=hardware_result_with_user_accepted_risk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
