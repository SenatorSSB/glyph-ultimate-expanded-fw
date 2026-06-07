#!/usr/bin/env python3
"""Validate the runtime-config interpreter source-baseline hardware result packet.

This checker is intentionally read-only and depends only on the Python standard
library.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_PATH = REPO_ROOT / "docs/calibration/glyph_runtime_config_interpreter_source_baseline_hardware_result_2026-06-07.md"
JSON_PATH = REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_interpreter_source_baseline_hardware_result_2026-06-07.json"

EXPECTED_BRANCH = "runtime-config-interpreter-source-baseline"
EXPECTED_RESULT_BRANCH = "runtime-config-interpreter-source-baseline-hardware-result"
EXPECTED_STATUS_MD = "USER_REPORTED_PASS"
EXPECTED_STATUS_JSON = "user_reported_pass"
EXPECTED_RESULT_SOURCE = "user_reported"
EXPECTED_FINAL_REPORT = "rebuilt the fw and all worked still"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_SCOPE = "applicable doable non-nunchuk planned checks"
EXPECTED_NUNCHUK_STATUS = "not_tested"
EXPECTED_COMMIT_SHA = "269e32a710b917cdaa033ff28f3b24e1b721e53f"

EXPECTED_CAVEATS = [
    "user-reported result",
    "no nunchuk validation",
    "no runtime-loaded storage",
    "no runtime-loaded config consumed from storage",
    "no WebSerial/device write",
    "no protobuf binary config parser",
    "no firmware flashing automation",
    "no profile import/export",
    "no universal official configurator compatibility claim",
    "no intentional firmware behavior change claim",
    "no Senscope/game-semantic change",
]

EXPECTED_ROWS = {
    "BOOT-001": ("PASS", "Applied doable non-nunchuk scope."),
    "PROFILE-001": ("PASS", "Applied doable non-nunchuk scope."),
    "DEFAULT-001": ("PASS", "Applied doable non-nunchuk scope."),
    "MODE-001": ("PASS", "Applied doable non-nunchuk scope."),
    "XY-001": ("PASS", "Applied doable non-nunchuk scope."),
    "TILT-001": ("PASS", "Applied doable non-nunchuk scope."),
    "LAYER-001": ("PASS", "Applied doable non-nunchuk scope."),
    "SPECIAL-TABLE-001": ("PASS", "Applied doable non-nunchuk scope."),
    "OVERRIDE-001": ("PASS", "Applied doable non-nunchuk scope."),
    "CSTICK-001": ("PASS", "PASS where doable / no regression observed."),
    "PROFILE-REG-001": ("PASS", "PASS / no regression observed."),
    "NUNCHUK-001": ("NOT_TESTED", "No nunchuk validation."),
}

class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"Missing JSON fixture: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"Expected top-level object in {path}")
    return data


def load_text(path: Path) -> str:
    if not path.exists():
        fail(f"Missing markdown result packet: {path}")
    return path.read_text(encoding="utf-8")


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


def parse_markdown_table(text: str) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue
        if cells[0] == "Test ID":
            in_table = True
            continue
        if not in_table or set(cells[0]) == {"-"}:
            continue
        rows[cells[0]] = (cells[1], cells[2])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def forbid_positive_phrase(text: str, phrase: str, where: str) -> None:
    pattern = re.compile(rf"(?<!no )(?<!not ){re.escape(phrase)}", re.IGNORECASE)
    if pattern.search(text):
        fail(f"Forbidden positive claim phrase detected in {where}: {phrase}")


def validate_markdown(text: str) -> None:
    bullets = parse_markdown_bullets(text)
    require(bullets.get("status") == EXPECTED_STATUS_MD, "Markdown status must be USER_REPORTED_PASS.")
    require(bullets.get("branch tested") == EXPECTED_BRANCH, "Markdown tested branch mismatch.")
    require(bullets.get("result branch") == EXPECTED_RESULT_BRANCH, "Markdown result branch mismatch.")
    require(bullets.get("commit sha under test") == EXPECTED_COMMIT_SHA, "Markdown commit SHA mismatch.")
    require(bullets.get("build command") == EXPECTED_BUILD_COMMAND, "Markdown build command mismatch.")
    require(bullets.get("tester/source") == "user-reported", "Markdown tester/source must be user-reported.")
    require(bullets.get("exact final user report text") == EXPECTED_FINAL_REPORT, "Markdown final user report text mismatch.")
    require(bullets.get("scope") == EXPECTED_SCOPE, "Markdown scope mismatch.")
    require(bullets.get("nunchuk") == "NOT_TESTED", "Markdown nunchuk status must be NOT_TESTED.")

    for caveat in EXPECTED_CAVEATS:
        require(caveat in text, f"Missing required caveat in markdown: {caveat}")
    require("hardware result packet" in text.lower(), "Markdown packet intro is missing.")
    require("pre-correction report was" in text.lower(), "Markdown should preserve the pre-correction context note.")

    table_rows = parse_markdown_table(text)
    for row_id, (expected_result, expected_notes) in EXPECTED_ROWS.items():
        require(row_id in table_rows, f"Missing markdown table row: {row_id}")
        result, notes = table_rows[row_id]
        require(result == expected_result, f"Unexpected markdown result for {row_id}: {result}")
        require(notes == expected_notes, f"Unexpected markdown notes for {row_id}: {notes}")

    for phrase in [
        "nunchuk validated",
        "runtime-loaded storage",
        "runtime-loaded config consumed from storage",
        "WebSerial/device write",
        "protobuf binary config parser",
        "firmware flashing automation",
        "universal official configurator compatibility",
        "intentional firmware behavior change",
    ]:
        forbid_positive_phrase(text, phrase, "markdown")


def validate_json(data: dict[str, Any]) -> None:
    require(data.get("schema_name") == "glyph_runtime_config_interpreter_source_baseline_hardware_result", "JSON schema_name mismatch.")
    require(data.get("status") == EXPECTED_STATUS_JSON, "JSON status mismatch.")
    require(data.get("result_source") == EXPECTED_RESULT_SOURCE, "JSON result_source mismatch.")
    require(data.get("source_report_text") == EXPECTED_FINAL_REPORT, "JSON source_report_text mismatch.")
    require(data.get("prior_report_text") == "Everything still works as expected", "JSON prior_report_text mismatch.")
    require(data.get("tested_branch") == EXPECTED_BRANCH, "JSON tested_branch mismatch.")
    require(data.get("result_branch") == EXPECTED_RESULT_BRANCH, "JSON result_branch mismatch.")
    require(data.get("commit_sha_under_test") == EXPECTED_COMMIT_SHA, "JSON commit_sha_under_test mismatch.")
    require(data.get("build_command") == EXPECTED_BUILD_COMMAND, "JSON build_command mismatch.")
    require(data.get("firmware_artifact_path") == "unknown", "JSON firmware_artifact_path must be unknown.")
    require(data.get("firmware_artifact_sha256") == "unknown", "JSON firmware_artifact_sha256 must be unknown.")
    require(data.get("hardware_result_recorded") is True, "JSON hardware_result_recorded must be true.")
    require(data.get("scope") == EXPECTED_SCOPE, "JSON scope mismatch.")
    require(data.get("nunchuk_status") == EXPECTED_NUNCHUK_STATUS, "JSON nunchuk_status mismatch.")

    caveats = data.get("caveats")
    require(isinstance(caveats, list) and caveats, "JSON caveats must be a non-empty list.")
    require(caveats == EXPECTED_CAVEATS, "JSON caveats list mismatch.")

    rows = data.get("test_rows")
    require(isinstance(rows, list) and rows, "JSON test_rows must be a non-empty list.")
    seen_rows: dict[str, tuple[str, str]] = {}
    for row in rows:
        require(isinstance(row, dict), "Each JSON test row must be an object.")
        row_id = row.get("id")
        row_result = row.get("result")
        row_notes = row.get("notes")
        require(isinstance(row_id, str), "JSON test row id must be a string.")
        require(isinstance(row_result, str), "JSON test row result must be a string.")
        require(isinstance(row_notes, str), "JSON test row notes must be a string.")
        seen_rows[row_id] = (row_result, row_notes)

    require(set(seen_rows) == set(EXPECTED_ROWS), "JSON test_rows IDs mismatch.")
    for row_id, (expected_result, expected_notes) in EXPECTED_ROWS.items():
        result, notes = seen_rows[row_id]
        require(result == expected_result, f"Unexpected JSON result for {row_id}: {result}")
        require(notes == expected_notes, f"Unexpected JSON notes for {row_id}: {notes}")

    json_text = json.dumps(data, sort_keys=True)
    for phrase in [
        "nunchuk validated",
        "runtime-loaded storage",
        "runtime-loaded config consumed from storage",
        "WebSerial/device write",
        "protobuf binary config parser",
        "firmware flashing automation",
        "universal official configurator compatibility",
        "intentional firmware behavior change",
    ]:
        forbid_positive_phrase(json_text, phrase, "JSON")


def main() -> int:
    try:
        markdown_text = load_text(MARKDOWN_PATH)
        json_data = load_json(JSON_PATH)
        validate_markdown(markdown_text)
        validate_json(json_data)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("OK: runtime-config interpreter source-baseline hardware result packet validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
