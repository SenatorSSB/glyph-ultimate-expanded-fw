#!/usr/bin/env python3
"""Read-only checker for Glyph Ultimate preservation hardware result markdown."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_ultimate_preservation_hardware_result.md"
TEMPLATE_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_ultimate_preservation_hardware_result_TEMPLATE.md"
TEMPLATE_FIXTURE_PATH = (
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_ultimate_preservation_hardware_result_TEMPLATE.json"
)
ALLOWED_FINAL_DISPOSITIONS = {
    "PASS",
    "FAIL",
    "BLOCKED",
    "USER_ACCEPTED_RISK",
}
ALLOWED_ROW_STATUSES = {
    "PASS",
    "FAIL",
    "NOT_TESTED",
    "BLOCKED",
    "USER_ACCEPTED_RISK",
}

REQUIRED_HEADINGS = [
    "## 1. Test Identity And Setup",
    "## 2. Baseline No-Modifier Checks",
    "## 3. Existing Tilt/Tilt2 Preservation",
    "## 4. C-Stick/Right-Stick Preservation",
    "## 5. Trigger Preservation",
    "## 6. SOCD/Opposite Direction Behavior",
    "## 7. RF5 Physical Identity / Negative Check",
    "## 8. Profile Preservation / Readback",
    "## 9. Optional Nunchuk",
    "## 10. Basic Button Regression",
    "## 11. Result Disposition",
]

REQUIRED_IDENTITY_FIELDS = [
    "Tester",
    "Test date (YYYY-MM-DD)",
    "Branch tested",
    "Commit SHA tested",
    "Firmware artifact path",
    "Firmware artifact hash (SHA-256)",
    "Profile/config used",
    "Controller model / hardware ID",
    "Flash method",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Glyph Ultimate preservation hardware result structure.")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_RESULT_PATH),
        help=f"Result markdown path (default: {DEFAULT_RESULT_PATH})",
    )
    return parser.parse_args()


def _extract_table_field(text: str, field_name: str) -> str | None:
    pattern = re.compile(rf"^\|\s*{re.escape(field_name)}\s*\|\s*(.*?)\s*\|\s*$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(1).strip()


def _extract_final_disposition(text: str) -> str | None:
    line_match = re.search(r"^final_disposition\s*:\s*`?([A-Z_]+)`?\s*$", text, re.MULTILINE)
    if line_match:
        return line_match.group(1)

    section_match = re.search(
        r"##\s+11\.\s+Result Disposition\n(?P<body>[\s\S]*)",
        text,
        re.MULTILINE,
    )
    if not section_match:
        return None

    checked = re.findall(r"^\s*[-*]\s*\[[xX]\]\s*([A-Z_]+)\s*$", section_match.group("body"), re.MULTILINE)
    unique = sorted(set(checked))
    if len(unique) == 1:
        return unique[0]
    return None


def _is_template_only(text: str) -> bool:
    return "TEMPLATE_ONLY" in text


def _display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"missing JSON fixture: {_display(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {_display(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{_display(path)} must contain a JSON object")
        return {}
    return payload


def _extract_row_statuses(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    pattern = re.compile(r"^\|\s*([A-Z0-9]+-\d{2})\s*\|[^|]*\|\s*([A-Z_]+)\s*\|", re.MULTILINE)
    for row_id, status in pattern.findall(text):
        rows[row_id] = status
    return rows


def _validate_template_fixture(payload: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "schema_name": "glyph_ultimate_preservation_hardware_result_template",
        "schema_version": 1,
        "template_date": "2026-06-06",
        "status": "template_only_not_executed",
        "result_recorded": False,
        "hardware_validation_claimed": False,
        "nunchuk_hardware_validated": False,
        "template_doc_path": "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
        "future_result_doc_path": "docs/calibration/glyph_ultimate_preservation_hardware_result.md",
        "checker_path": "tools/check_glyph_ultimate_preservation_hardware_result.py",
        "readiness_packet_path": "docs/calibration/glyph_preservation_hardware_readiness_packet_2026-06-06.md",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            errors.append(f"template fixture {key} must be {expected_value!r}")

    if payload.get("allowed_row_statuses") != sorted(ALLOWED_ROW_STATUSES):
        # Keep fixture order aligned with the readiness packet, not alphabetical.
        if payload.get("allowed_row_statuses") != ["PASS", "FAIL", "NOT_TESTED", "BLOCKED", "USER_ACCEPTED_RISK"]:
            errors.append("template fixture allowed_row_statuses drifted")
    if set(payload.get("allowed_final_dispositions", [])) != ALLOWED_FINAL_DISPOSITIONS:
        errors.append("template fixture allowed_final_dispositions drifted")

    required_row_ids = payload.get("required_row_ids")
    if not isinstance(required_row_ids, list) or not required_row_ids:
        errors.append("template fixture required_row_ids must be a non-empty list")
    elif not all(isinstance(row_id, str) and row_id.strip() for row_id in required_row_ids):
        errors.append("template fixture required_row_ids must contain non-empty strings")

    rules = payload.get("result_recording_rules")
    if not isinstance(rules, dict):
        errors.append("template fixture result_recording_rules must be an object")
    else:
        for key in (
            "not_tested_rows_do_not_validate_behavior",
            "failure_rows_require_notes",
            "blocked_rows_require_notes",
            "user_accepted_risk_rows_require_notes",
            "rollback_notes_required_if_needed",
            "user_report_source_required",
        ):
            if rules.get(key) is not True:
                errors.append(f"template fixture result_recording_rules.{key} must be true")

    non_claims = payload.get("explicit_non_claims")
    if not isinstance(non_claims, dict):
        errors.append("template fixture explicit_non_claims must be an object")
    else:
        for key in (
            "firmware_behavior_changed",
            "active_profile_artifact_changed",
            "runtime_loaded_config_implemented",
            "webserial_write_implemented",
            "device_write_implemented",
            "external_remapper_adapter_implemented",
            "nunchuk_hardware_validated",
        ):
            if non_claims.get(key) is not False:
                errors.append(f"template fixture explicit_non_claims.{key} must be false")


def _validate_template_doc(template_text: str, payload: dict[str, Any], errors: list[str]) -> None:
    if "TEMPLATE_ONLY" not in template_text:
        errors.append("template doc must remain TEMPLATE_ONLY")
    if "PASS_SMOKE_OBSERVED" in template_text:
        errors.append("template doc must not use PASS_SMOKE_OBSERVED")
    for status in ALLOWED_ROW_STATUSES:
        if status not in template_text:
            errors.append(f"template doc missing allowed row status: {status}")
    for disposition in ALLOWED_FINAL_DISPOSITIONS:
        if f"- [ ] {disposition}" not in template_text:
            errors.append(f"template doc missing final disposition: {disposition}")
    for phrase in (
        "Rows marked `NOT_TESTED` are not validated",
        "No nunchuk hardware validation is claimed unless nunchuk rows are executed and",
        "No external remapper adapter, runtime-loaded config, WebSerial write, or",
        "No active profile artifact change is claimed by this result",
        "Failure, blocked, or user-accepted-risk rows require notes",
        "Rollback notes are required if a failure indicates rollback is needed",
    ):
        if phrase not in template_text:
            errors.append(f"template doc missing required phrase: {phrase}")

    required_row_ids = payload.get("required_row_ids", [])
    if isinstance(required_row_ids, list):
        row_statuses = _extract_row_statuses(template_text)
        missing = sorted(set(required_row_ids) - set(row_statuses))
        if missing:
            errors.append("template doc missing row IDs: " + ", ".join(missing))
        for row_id in required_row_ids:
            if row_statuses.get(row_id) != "NOT_TESTED":
                errors.append(f"template row {row_id} must default to NOT_TESTED")


def _validate_template_contract(errors: list[str]) -> None:
    payload = _load_json_object(TEMPLATE_FIXTURE_PATH, errors)
    if not TEMPLATE_PATH.exists():
        errors.append(f"missing template doc: {_display(TEMPLATE_PATH)}")
        return
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    _validate_template_fixture(payload, errors)
    _validate_template_doc(template_text, payload, errors)


def _validate_section_presence(text: str, errors: list[str]) -> None:
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")


def _validate_required_sections(text: str, errors: list[str]) -> None:
    required_section_keywords = {
        "RF5 section": "## 7. RF5 Physical Identity / Negative Check",
        "C-stick/right-stick section": "## 4. C-Stick/Right-Stick Preservation",
        "Trigger section": "## 5. Trigger Preservation",
        "SOCD section": "## 6. SOCD/Opposite Direction Behavior",
        "Profile preservation section": "## 8. Profile Preservation / Readback",
    }
    for label, heading in required_section_keywords.items():
        if heading not in text:
            errors.append(f"missing {label}")


def _validate_identity_fields(text: str, errors: list[str]) -> None:
    for field in REQUIRED_IDENTITY_FIELDS:
        value = _extract_table_field(text, field)
        if value is None:
            errors.append(f"missing required field: {field}")
            continue
        if not value:
            errors.append(f"empty required field: {field}")


def _validate_final_disposition(text: str, errors: list[str]) -> str | None:
    disposition = _extract_final_disposition(text)
    if disposition is None:
        errors.append("missing final_disposition")
        return None
    if disposition not in ALLOWED_FINAL_DISPOSITIONS:
        allowed = ", ".join(sorted(ALLOWED_FINAL_DISPOSITIONS))
        errors.append(f"invalid final_disposition: {disposition}; allowed={allowed}")
    return disposition


def _validate_row_statuses(text: str, errors: list[str]) -> None:
    row_statuses = _extract_row_statuses(text)
    if not row_statuses:
        errors.append("no result rows found")
        return
    invalid = sorted(
        f"{row_id}={status}"
        for row_id, status in row_statuses.items()
        if status not in ALLOWED_ROW_STATUSES
    )
    if invalid:
        errors.append("invalid row statuses: " + ", ".join(invalid))


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.is_absolute():
        path = REPO_ROOT / path

    errors: list[str] = []
    _validate_template_contract(errors)

    if errors:
        print("status=FAIL")
        print(f"path={path}")
        print("template_contract=false")
        for error in errors:
            print(f"error={error}")
        return 1

    if not path.exists():
        print("status=NO_RESULT_FILE")
        print(f"path={path}")
        print("template_contract=true")
        return 0

    text = path.read_text(encoding="utf-8")
    template_only = _is_template_only(text)

    _validate_section_presence(text, errors)
    _validate_required_sections(text, errors)
    _validate_row_statuses(text, errors)

    disposition: str | None = None
    if not template_only:
        _validate_identity_fields(text, errors)
        disposition = _validate_final_disposition(text, errors)

    if errors:
        print("status=FAIL")
        print(f"path={path}")
        print(f"template_only={'true' if template_only else 'false'}")
        for error in errors:
            print(f"error={error}")
        return 1

    if template_only:
        print("status=TEMPLATE_ONLY")
        print(f"path={path}")
        print("template_only=true")
        return 0

    print("status=PASS")
    print(f"path={path}")
    print(f"final_disposition={disposition}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
