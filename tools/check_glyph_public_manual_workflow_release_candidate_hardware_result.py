#!/usr/bin/env python3
"""Validate the public/manual workflow release-candidate hardware result.

This checker is read-only and depends only on the Python standard library.
It validates the user-reported hardware result package without claiming
runtime-loaded config, device-write, flashing, or nunchuk validation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_PATH = REPO_ROOT / "docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md"
JSON_PATH = REPO_ROOT / "docs/calibration/fixtures/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.json"

EXPECTED_SCHEMA_NAME = "glyph_public_manual_workflow_release_candidate_hardware_result"
EXPECTED_STATUS_MD = "USER_REPORTED_PASS"
EXPECTED_STATUS_JSON = "user_reported_pass"
EXPECTED_RESULT_SOURCE = "user_reported"
EXPECTED_USER_REPORT_TEXT = "everything works as expected"
EXPECTED_RESULT_DATE = "2026-06-07"
EXPECTED_TESTED_BRANCH = "configurator"
EXPECTED_RESULT_BRANCH = "public-manual-workflow-release-candidate-hardware-result"
EXPECTED_COMMIT_SHA = "d085c0f80ea1578a378bce2ab75f8005727c2dde"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_FIRMWARE_ARTIFACT_PATH = "unknown"
EXPECTED_FIRMWARE_ARTIFACT_SHA256 = "unknown"
EXPECTED_PROFILE_FILE = "none"
EXPECTED_NEW_PROFILE_FILE_USED = False
EXPECTED_HARDWARE_RESULT_RECORDED = True
EXPECTED_NUNCHUK_STATUS = "not_tested"
EXPECTED_SCOPE = "applicable doable public/manual workflow release-candidate rows"

EXPECTED_CAVEATS = {
    "user-reported result",
    "manual/operator-run firmware update path only",
    "no new profile file used",
    "no runtime-loaded config",
    "no runtime-config storage",
    "no firmware binary/protobuf parser integration",
    "no WebSerial/device write",
    "no push-to-device",
    "no firmware flashing automation",
    "no hidden write",
    "no official configurator compatibility claim",
    "no public release claim yet",
    "no nunchuk validation",
    "no Senscope/game-semantic change",
}

EXPECTED_ROWS = {
    "BOOT-001": (
        "boot",
        "Normal boot after the manual workflow update path reaches expected boot state",
        "PASS",
        "User-reported pass under applicable doable public/manual workflow scope.",
    ),
    "PROFILE-001": (
        "profile",
        "Current profile remains usable after the workflow preparation",
        "PASS",
        "User-reported pass; no new profile file used.",
    ),
    "BASELINE-001": (
        "baseline",
        "Source-backed baseline outputs remain preserved",
        "PASS",
        "User-reported pass; baseline outputs preserved.",
    ),
    "MODIFIERS-001": (
        "modifiers",
        "Representative modifier tables remain preserved",
        "PASS",
        "User-reported pass; representative modifier tables preserved.",
    ),
    "SPECIAL-001": (
        "special_tables",
        "Special tables remain preserved",
        "PASS",
        "User-reported pass; special tables preserved.",
    ),
    "OVERRIDE-001": (
        "override_paths",
        "Representative override paths remain preserved",
        "PASS",
        "User-reported pass; representative override paths preserved.",
    ),
    "CSTICK-001": (
        "cstick_interaction",
        "C-stick interaction is not regressed where doable",
        "PASS",
        "PASS where doable / no regression observed.",
    ),
    "DOCS-001": (
        "docs_navigation",
        "Docs/navigation/checklist links remain synchronized",
        "PASS",
        "Docs/navigation/checklist links remained synchronized.",
    ),
    "NO-WRITE-001": (
        "no_write",
        "No hidden write, runtime-loaded config, or WebSerial/device write occurs",
        "PASS",
        "No hidden write, runtime-loaded config, push-to-device, or WebSerial/device write was used.",
    ),
    "NO-FLASH-AUTO-001": (
        "no_flash_automation",
        "No flashing automation, UF2 copy automation, or bootloader automation occurs",
        "PASS",
        "No flashing automation, UF2 copy automation, or bootloader automation was used.",
    ),
    "RECOVERY-001": (
        "recovery",
        "Manual recovery/rollback path remains operator-run only",
        "USER_ACCEPTED_RISK",
        "Manual recovery/rollback path was not directly exercised; operator-run docs are available, so this row is conservatively marked USER_ACCEPTED_RISK.",
    ),
    "PROFILE-REG-001": (
        "profile_regression",
        "No profile regression observed",
        "PASS",
        "PASS / no regression observed.",
    ),
    "NUNCHUK-001": (
        "nunchuk_scope",
        "Explicitly mark nunchuk as not tested in this branch",
        "NOT_TESTED",
        "No nunchuk validation was performed or claimed.",
    ),
}

FORBIDDEN_POSITIVE_PHRASES = (
    "runtime-loaded config is implemented",
    "runtime-loaded config was tested",
    "runtime-config storage is implemented",
    "runtime-config storage was tested",
    "firmware binary/protobuf parser integration is implemented",
    "webserial/device write is implemented",
    "push-to-device is implemented",
    "firmware flashing automation is implemented",
    "hidden write is used",
    "official configurator compatibility is claimed",
    "public release is claimed",
    "nunchuk validated",
    "nunchuk validation is confirmed",
    "senscope/game-semantic change",
)


class HardwareResultError(ValueError):
    """Raised when the hardware result record is not trustworthy."""


def fail(message: str) -> None:
    raise HardwareResultError(message)


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return payload


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def require_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    missing = [phrase for phrase in phrases if phrase.lower() not in lowered]
    if missing:
        fail(f"{label} missing required phrase(s): " + ", ".join(missing))


def forbid_positive_phrase(text: str, phrase: str, *, label: str) -> None:
    pattern = re.compile(rf"(?<!no )(?<!not )\b{re.escape(phrase)}\b", re.IGNORECASE)
    if pattern.search(text):
        fail(f"{label} contains positive claim phrase: {phrase}")


def parse_bullets(text: str) -> dict[str, str]:
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


def parse_table(text: str) -> dict[str, tuple[str, str, str, str]]:
    rows: dict[str, tuple[str, str, str, str]] = {}
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        if cells[0] == "Row ID":
            in_table = True
            continue
        if not in_table or set(cells[0]) == {"-"}:
            continue
        rows[cells[0]] = (cells[1], cells[2], cells[3], cells[4])
    return rows


def validate_markdown(text: str) -> None:
    require_phrases(
        text,
        (
            "Public / Manual Workflow Release Candidate Hardware Result - 2026-06-07",
            "This document records the user-reported hardware result",
            EXPECTED_USER_REPORT_TEXT,
            "status: USER_REPORTED_PASS",
            "result source: user-reported",
            "branch tested: configurator",
            "result branch: public-manual-workflow-release-candidate-hardware-result",
            EXPECTED_COMMIT_SHA,
            "build command: ./scripts/build-glyph-mk6-quiet.sh",
            "firmware artifact path/hash: unknown",
            "profile file: none / no new profile file used",
            "scope: applicable doable public/manual workflow release-candidate rows",
            "nunchuk: NOT_TESTED",
            "## Source Authority",
            "## Caveats",
            "## Hardware Result Table",
        ),
        label="markdown result packet",
    )

    table_rows = parse_table(text)
    if set(table_rows) != set(EXPECTED_ROWS):
        missing = sorted(set(EXPECTED_ROWS) - set(table_rows))
        unexpected = sorted(set(table_rows) - set(EXPECTED_ROWS))
        details = []
        if missing:
            details.append("missing=" + ", ".join(missing))
        if unexpected:
            details.append("unexpected=" + ", ".join(unexpected))
        fail("markdown result rows mismatch (" + "; ".join(details) + ")")

    for row_id, (expected_category, expected_planned_check, expected_result, expected_notes) in EXPECTED_ROWS.items():
        category, planned_check, result, notes = table_rows[row_id]
        if category != expected_category:
            fail(f"markdown row {row_id} category must be {expected_category!r}")
        if planned_check != expected_planned_check:
            fail(f"markdown row {row_id} planned check must match the hardware plan")
        if result != expected_result:
            fail(f"markdown row {row_id} result must be {expected_result!r}")
        if notes != expected_notes:
            fail(f"markdown row {row_id} notes must match the recorded conservative note")

    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        forbid_positive_phrase(text, phrase, label="markdown result packet")


def validate_json(data: dict[str, Any]) -> None:
    expected_fields = {
        "schema_name": EXPECTED_SCHEMA_NAME,
        "status": EXPECTED_STATUS_JSON,
        "result_source": EXPECTED_RESULT_SOURCE,
        "source_report_text": EXPECTED_USER_REPORT_TEXT,
        "result_date": EXPECTED_RESULT_DATE,
        "tested_branch": EXPECTED_TESTED_BRANCH,
        "result_branch": EXPECTED_RESULT_BRANCH,
        "commit_sha_under_test": EXPECTED_COMMIT_SHA,
        "build_command": EXPECTED_BUILD_COMMAND,
        "firmware_artifact_path": EXPECTED_FIRMWARE_ARTIFACT_PATH,
        "firmware_artifact_sha256": EXPECTED_FIRMWARE_ARTIFACT_SHA256,
        "profile_file": EXPECTED_PROFILE_FILE,
        "new_profile_file_used": EXPECTED_NEW_PROFILE_FILE_USED,
        "hardware_result_recorded": EXPECTED_HARDWARE_RESULT_RECORDED,
        "nunchuk_status": EXPECTED_NUNCHUK_STATUS,
        "scope": EXPECTED_SCOPE,
    }
    for key, expected in expected_fields.items():
        if data.get(key) != expected:
            fail(f"JSON {key} must be {expected!r}")

    caveats = data.get("caveats")
    if not isinstance(caveats, list) or not caveats:
        fail("JSON caveats must be a non-empty list")
    if any(not isinstance(item, str) or not item for item in caveats):
        fail("JSON caveats must contain only non-empty strings")
    missing = sorted(EXPECTED_CAVEATS - set(caveats))
    if missing:
        fail("JSON caveats missing required item(s): " + ", ".join(missing))

    rows = data.get("test_rows")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_ROWS):
        fail("JSON test_rows must contain all expected rows")

    seen_rows: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("JSON test_rows entries must be objects")
        row_id = row.get("row_id")
        category = row.get("category")
        result = row.get("result")
        notes = row.get("notes")
        if not isinstance(row_id, str) or not row_id:
            fail("JSON test_rows entries must include a row_id")
        if not isinstance(category, str) or not category:
            fail(f"JSON row {row_id} must include a category")
        if not isinstance(result, str) or not result:
            fail(f"JSON row {row_id} must include a result")
        if not isinstance(notes, str) or not notes:
            fail(f"JSON row {row_id} must include notes")
        seen_rows[row_id] = (category, result, notes)

    if set(seen_rows) != set(EXPECTED_ROWS):
        fail("JSON test_rows IDs mismatch")

    for row_id, (expected_category, _expected_planned_check, expected_result, expected_notes) in EXPECTED_ROWS.items():
        category, result, notes = seen_rows[row_id]
        if category != expected_category:
            fail(f"JSON row {row_id} category must be {expected_category!r}")
        if result != expected_result:
            fail(f"JSON row {row_id} result must be {expected_result!r}")
        if notes != expected_notes:
            fail(f"JSON row {row_id} notes must match the recorded conservative note")

    json_text = json.dumps(data, sort_keys=True)
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        forbid_positive_phrase(json_text, phrase, label="JSON result packet")


def main() -> int:
    print("glyph_public_manual_workflow_release_candidate_hardware_result")
    try:
        markdown_text = read_required(MARKDOWN_PATH)
        json_data = load_json_object(JSON_PATH)
        validate_markdown(markdown_text)
        validate_json(json_data)
    except (OSError, HardwareResultError, ValueError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"markdown={MARKDOWN_PATH.relative_to(REPO_ROOT)}")
    print(f"json={JSON_PATH.relative_to(REPO_ROOT)}")
    print("status=user_reported_pass")
    print("result_source=user_reported")
    print("no_runtime_loaded_config=true")
    print("no_runtime_config_storage=true")
    print("no_webserial_device_write=true")
    print("no_push_to_device=true")
    print("no_firmware_flashing_automation=true")
    print("no_official_configurator_compatibility_claim=true")
    print("no_public_release_claim=true")
    print("nunchuk_status=not_tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
