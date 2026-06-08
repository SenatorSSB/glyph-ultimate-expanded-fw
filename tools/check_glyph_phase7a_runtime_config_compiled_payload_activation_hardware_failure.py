#!/usr/bin/env python3
"""Validate the Phase 7A compiled payload activation hardware failure packet.

This checker is read-only and uses only the Python standard library. It records
the user-reported failure boundary without diagnosing or fixing firmware.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.json"
)

EXPECTED_SCHEMA_NAME = "glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure"
EXPECTED_STATUS_MD = "HARDWARE_FAIL"
EXPECTED_STATUS_JSON = "hardware_fail"
EXPECTED_RESULT_SOURCE_MD = "user-reported"
EXPECTED_RESULT_SOURCE_JSON = "user_reported"
EXPECTED_TESTED_BRANCH = "phase7a-runtime-config-compiled-payload-activation"
EXPECTED_RESULT_BRANCH = "phase7a-runtime-config-compiled-payload-activation-hardware-failure"
EXPECTED_FAILURE_REPORT = (
    "I dont know what happened after tests, but I was wrong. Some inputs completely cut the connection "
    "from the controller. At least pressing rf5 or rf6 disconnect it according to the game console"
)
EXPECTED_RECOVERY_REPORT = "i restored the previous fw, which works fine still"
EXPECTED_COMMIT_SHA = "67e575b87147f1a6e2ce6474a59ac5b418bd1147"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_NUNCHUK_STATUS = "not_tested"

EXPECTED_CAVEATS = [
    "user-reported failure",
    "exact low-level disconnect cause unknown",
    "do not infer firmware crash mechanism without debugging",
    "previous configurator firmware restored and works fine",
    "branch must not merge",
    "no nunchuk validation",
    "no runtime-loaded config storage",
    "no config.bin runtime-config use",
    "no WebSerial/device write",
    "no runtime-config command IDs",
    "no firmware flashing automation",
    "no official configurator compatibility claim",
    "no Senscope/game-semantic change",
]

EXPECTED_ROWS = {
    "BOOT-001": ("normal boot", "UNKNOWN_OR_NOT_RELIABLY_COMPLETE"),
    "BASELINE-001": ("current baseline preserved", "FAIL"),
    "PARSER-001": ("compiled valid payload accepted", "INCONCLUSIVE"),
    "FALLBACK-001": ("invalid/failure path", "NOT_HARDWARE_EXERCISED"),
    "MODIFIERS-001": ("representative modifiers", "FAIL"),
    "SPECIAL-001": ("special tables", "NOT_RELIABLY_TESTED_AFTER_DISCONNECT"),
    "OVERRIDE-001": ("override paths", "FAIL"),
    "CSTICK-001": ("c-stick interaction", "NOT_RELIABLY_TESTED_AFTER_DISCONNECT"),
    "NO-STORAGE-001": ("no storage read/write", "PASS_BY_SOURCE_INSPECTION_ONLY"),
    "NO-WRITE-001": ("no device write/WebSerial", "PASS_BY_SOURCE_INSPECTION_ONLY"),
    "NO-FLASH-001": ("no flashing automation", "PASS_BY_SOURCE_INSPECTION_ONLY"),
    "PROFILE-REG-001": ("profile regression", "FAIL"),
    "NUNCHUK-001": ("nunchuk", "NOT_TESTED"),
}

FORBIDDEN_POSITIVE_CLAIMS = (
    "USER_REPORTED_PASS",
    "hardware pass",
    "hardware success",
    "all functions the same as before",
    "all functions worked",
    "nunchuk validated",
    "nunchuk validation confirmed",
    "runtime-loaded config storage implemented",
    "runtime-loaded config storage validated",
    "config.bin runtime-config use implemented",
    "config.bin runtime-config use validated",
    "WebSerial/device write implemented",
    "WebSerial/device write validated",
    "firmware flashing automation implemented",
    "firmware flashing automation validated",
    "official configurator compatibility claimed",
    "official configurator compatibility validated",
)


class HardwareFailureResultError(ValueError):
    """Raised when the failure result record drifts from its contract."""


def fail(message: str) -> None:
    raise HardwareFailureResultError(message)


def display(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {display(path)}")
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def parse_markdown_bullets(text: str) -> dict[str, str]:
    bullets: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        body = line[2:]
        if ": " not in body:
            continue
        key, value = body.split(": ", 1)
        bullets[key.strip().lower()] = value.strip().strip("`")
    return bullets


def parse_markdown_table(text: str) -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] == "Row ID":
            in_table = True
            continue
        if not in_table or set(cells[0]) == {"-"}:
            continue
        rows[cells[0]] = (cells[1], cells[2], cells[3])
    return rows


def validate_no_forbidden_claims(text: str, label: str) -> None:
    lowered = normalize(text)
    for phrase in FORBIDDEN_POSITIVE_CLAIMS:
        if normalize(phrase) in lowered:
            fail(f"{label} contains forbidden success/implementation claim: {phrase}")


def validate_markdown(text: str) -> None:
    bullets = parse_markdown_bullets(text)
    expected_bullets = {
        "status": EXPECTED_STATUS_MD,
        "result source": EXPECTED_RESULT_SOURCE_MD,
        "branch tested": EXPECTED_TESTED_BRANCH,
        "result branch": EXPECTED_RESULT_BRANCH,
        "commit sha under test": EXPECTED_COMMIT_SHA,
        "build command": EXPECTED_BUILD_COMMAND,
        "firmware artifact path/hash": "unknown",
        "exact failure report": EXPECTED_FAILURE_REPORT,
        "exact recovery report": EXPECTED_RECOVERY_REPORT,
        "nunchuk": "NOT_TESTED",
    }
    for key, expected in expected_bullets.items():
        require(bullets.get(key) == expected, f"markdown bullet {key!r} mismatch")

    for phrase in (
        "RF5 implicated",
        "RF6 implicated",
        "console/game reports controller disconnect",
        "Phase 7A compiled payload activation branch must not merge",
        "Previous configurator firmware remains known-good",
        "Failure is isolated to the Phase 7A activation branch",
        "Exact low-level disconnect cause is unknown",
    ):
        require_phrase(text, phrase, "markdown")

    for caveat in EXPECTED_CAVEATS:
        require_phrase(text, caveat, "markdown caveats")

    rows = parse_markdown_table(text)
    require(set(rows) == set(EXPECTED_ROWS), "markdown hardware failure table row IDs mismatch")
    for row_id, (expected_area, expected_result) in EXPECTED_ROWS.items():
        area, result, notes = rows[row_id]
        require(area == expected_area, f"markdown {row_id} area mismatch")
        require(result == expected_result, f"markdown {row_id} result mismatch")
        require(notes, f"markdown {row_id} notes must be non-empty")

    validate_no_forbidden_claims(text, "markdown")


def validate_json(data: dict[str, Any]) -> None:
    expected_fields: dict[str, Any] = {
        "schema_name": EXPECTED_SCHEMA_NAME,
        "status": EXPECTED_STATUS_JSON,
        "result_source": EXPECTED_RESULT_SOURCE_JSON,
        "tested_branch": EXPECTED_TESTED_BRANCH,
        "result_branch": EXPECTED_RESULT_BRANCH,
        "source_failure_report_text": EXPECTED_FAILURE_REPORT,
        "source_recovery_report_text": EXPECTED_RECOVERY_REPORT,
        "commit_sha_under_test": EXPECTED_COMMIT_SHA,
        "build_command": EXPECTED_BUILD_COMMAND,
        "firmware_artifact_path": "unknown",
        "firmware_artifact_sha256": "unknown",
        "hardware_result_recorded": True,
        "merge_allowed": False,
        "nunchuk_status": EXPECTED_NUNCHUK_STATUS,
    }
    for key, expected in expected_fields.items():
        require(data.get(key) == expected, f"JSON {key!r} mismatch")

    require(data.get("observed_failing_inputs") == ["RF5", "RF6"], "JSON observed_failing_inputs mismatch")
    require(
        data.get("observed_failure") == ["console_or_game_reports_controller_disconnect"],
        "JSON observed_failure mismatch",
    )
    require(
        data.get("recovery")
        == ["previous_configurator_firmware_restored", "previous_configurator_firmware_works_fine"],
        "JSON recovery mismatch",
    )
    require(data.get("caveats") == EXPECTED_CAVEATS, "JSON caveats mismatch")

    rows = data.get("test_rows")
    require(isinstance(rows, list) and rows, "JSON test_rows must be a non-empty list")
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, dict), "JSON test row must be an object")
        row_id = row.get("id")
        require(isinstance(row_id, str) and row_id, "JSON row id must be a non-empty string")
        require(row_id not in by_id, f"duplicate JSON row id: {row_id}")
        by_id[row_id] = row
    require(set(by_id) == set(EXPECTED_ROWS), "JSON test row IDs mismatch")
    for row_id, (expected_area, expected_result) in EXPECTED_ROWS.items():
        row = by_id[row_id]
        require(row.get("area") == expected_area, f"JSON {row_id} area mismatch")
        require(row.get("result") == expected_result, f"JSON {row_id} result mismatch")
        require(isinstance(row.get("notes"), str) and row["notes"], f"JSON {row_id} notes must be non-empty")

    validate_no_forbidden_claims(json.dumps(data, sort_keys=True), "JSON")


def main() -> int:
    print("glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure")
    try:
        markdown = read_required(MARKDOWN_PATH)
        fixture = load_json_object(JSON_PATH)
        validate_markdown(markdown)
        validate_json(fixture)
    except (OSError, HardwareFailureResultError) as exc:
        print("status=FAIL")
        print("hardware_result_recorded=true")
        print("merge_allowed=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("hardware_result_recorded=true")
    print("result_status=hardware_fail")
    print("merge_allowed=false")
    print("observed_failing_inputs=RF5,RF6")
    print("nunchuk_status=not_tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

