#!/usr/bin/env python3
"""Validate the Phase 3 generated constants integration hardware result.

This checker is read-only and stdlib-only. It validates the branch-specific
hardware result record for the Phase 3 generated constants firmware-integration
branch without making runtime-loaded config, device-write, flashing, or
nunchuk-validation claims.
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
    / "glyph_generated_constants_phase3_integration_hardware_result_2026-06-07.md"
)
RESULT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_generated_constants_phase3_integration_hardware_result_2026-06-07.json"
)

EXPECTED_SCHEMA_NAME = "glyph_generated_constants_phase3_integration_hardware_result"
EXPECTED_STATUS = "user_reported_pass"
EXPECTED_RESULT_SOURCE = "user_reported"
EXPECTED_SOURCE_REPORT_TEXT = "all test doable work as expected"
EXPECTED_TESTED_BRANCH = "phase3-generated-constants-firmware-integration"
EXPECTED_RESULT_BRANCH = "phase3-generated-constants-hardware-result"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_NUNCHUK_STATUS = "not_tested"
EXPECTED_RESULT_DATE = "2026-06-07"
EXPECTED_COMMIT_SHA = "76e4f6c234b88a12ba311f2c8076fa3303ffd711"
EXPECTED_CAVEATS = {
    "user-reported result",
    "no nunchuk validation",
    "no runtime-loaded config",
    "no WebSerial/device write",
    "no protobuf binary write",
    "no firmware flashing automation",
    "no universal official configurator compatibility claim",
    "no intentional firmware behavior change claim",
    "no Senscope/game-semantic change",
}
EXPECTED_ROWS = {
    "BOOT-001": "PASS",
    "PROFILE-001": "PASS",
    "DEFAULT-001": "PASS",
    "MODES-001": "PASS",
    "MODS-001": "PASS",
    "RT1RF4-001": "PASS",
    "LT5-001": "PASS",
    "NULL-001": "PASS",
    "PROFILE-REG-001": "PASS",
    "NUNCHUK-001": "NOT_TESTED",
}
EXPECTED_ROW_CATEGORIES = {
    "BOOT-001": "boot",
    "PROFILE-001": "identity_profile",
    "DEFAULT-001": "default_table",
    "MODES-001": "mode_default",
    "MODS-001": "modifier_tables",
    "RT1RF4-001": "custom_modifier_table",
    "LT5-001": "low_magnitude",
    "NULL-001": "null_override",
    "PROFILE-REG-001": "profile_regression",
    "NUNCHUK-001": "nunchuk_scope",
}
FORBIDDEN_POSITIVE_CLAIMS = (
    "nunchuk validation is confirmed",
    "runtime-loaded config is implemented",
    "webserial/device write is implemented",
    "protobuf binary write is implemented",
    "firmware flashing automation is implemented",
    "universal official configurator compatibility is validated",
    "intentional firmware behavior change is claimed",
)


class HardwareResultError(AssertionError):
    """Raised when the hardware result record is not trustworthy."""


def fail(message: str) -> None:
    raise HardwareResultError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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


def validate_top_level(result: dict[str, Any]) -> None:
    expected_fields = {
        "schema_name": EXPECTED_SCHEMA_NAME,
        "status": EXPECTED_STATUS,
        "result_source": EXPECTED_RESULT_SOURCE,
        "source_report_text": EXPECTED_SOURCE_REPORT_TEXT,
        "tested_branch": EXPECTED_TESTED_BRANCH,
        "result_branch": EXPECTED_RESULT_BRANCH,
        "commit_sha_under_test": EXPECTED_COMMIT_SHA,
        "build_command": EXPECTED_BUILD_COMMAND,
        "firmware_artifact_path": "unknown",
        "firmware_artifact_sha256": "unknown",
        "hardware_result_recorded": True,
        "nunchuk_status": EXPECTED_NUNCHUK_STATUS,
        "result_date": EXPECTED_RESULT_DATE,
    }
    for key, expected in expected_fields.items():
        if result.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_caveats(result: dict[str, Any]) -> None:
    caveats = result.get("caveats")
    if not isinstance(caveats, list):
        fail("caveats must be a list")
    if any(not isinstance(item, str) or not item for item in caveats):
        fail("caveats must contain only non-empty strings")
    missing = sorted(EXPECTED_CAVEATS - set(caveats))
    if missing:
        fail("missing caveat(s): " + ", ".join(missing))
    for forbidden in FORBIDDEN_POSITIVE_CLAIMS:
        if forbidden in caveats:
            fail(f"caveats must not contain forbidden claim: {forbidden}")


def validate_rows(result: dict[str, Any]) -> None:
    rows = result.get("test_rows")
    if not isinstance(rows, list):
        fail("test_rows must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("test_rows entries must be objects")
        row_id = row.get("row_id")
        category = row.get("category")
        status = row.get("result")
        notes = row.get("notes")
        if not isinstance(row_id, str) or not row_id:
            fail("row missing row_id")
        if not isinstance(category, str) or not category:
            fail(f"row {row_id} missing category")
        if not isinstance(status, str) or not status:
            fail(f"row {row_id} missing result")
        if not isinstance(notes, str) or not notes:
            fail(f"row {row_id} missing notes")
        if row_id in by_id:
            fail(f"duplicate row_id: {row_id}")
        by_id[row_id] = row

    if set(by_id) != set(EXPECTED_ROWS):
        missing = sorted(set(EXPECTED_ROWS) - set(by_id))
        unexpected = sorted(set(by_id) - set(EXPECTED_ROWS))
        if missing:
            fail("missing row(s): " + ", ".join(missing))
        if unexpected:
            fail("unexpected row(s): " + ", ".join(unexpected))

    for row_id, expected_status in EXPECTED_ROWS.items():
        row = by_id[row_id]
        if row["category"] != EXPECTED_ROW_CATEGORIES[row_id]:
            fail(
                f"{row_id} category must be {EXPECTED_ROW_CATEGORIES[row_id]!r}"
            )
        if row["result"] != expected_status:
            fail(f"{row_id} must be {expected_status}")


def validate_doc() -> None:
    if not RESULT_DOC_PATH.exists():
        fail(f"missing result doc: {display(RESULT_DOC_PATH)}")
    doc_text = RESULT_DOC_PATH.read_text(encoding="utf-8")
    lowered = doc_text.lower()
    required_phrases = (
        EXPECTED_STATUS,
        EXPECTED_RESULT_SOURCE,
        EXPECTED_SOURCE_REPORT_TEXT,
        EXPECTED_TESTED_BRANCH,
        EXPECTED_RESULT_BRANCH,
        "no nunchuk validation claim",
        "no runtime-loaded config",
        "no webserial/device write",
        "no protobuf binary write",
        "no firmware flashing automation",
        "no universal official configurator compatibility claim",
        "no intentional firmware behavior change claim",
        "no senscope/game-semantic change",
    )
    for phrase in required_phrases:
        if phrase.lower() not in lowered:
            fail(f"result doc missing required phrase: {phrase}")
    for forbidden in FORBIDDEN_POSITIVE_CLAIMS:
        if forbidden in lowered:
            fail(f"result doc must not imply forbidden claim: {forbidden}")


def main() -> int:
    print("glyph_generated_constants_phase3_integration_hardware_result")
    try:
        result = load_json(RESULT_FIXTURE_PATH)
        validate_top_level(result)
        validate_caveats(result)
        validate_rows(result)
        validate_doc()
    except HardwareResultError as exc:
        print("status=FAIL")
        print("hardware_result_recorded=true")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("hardware_result_recorded=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
