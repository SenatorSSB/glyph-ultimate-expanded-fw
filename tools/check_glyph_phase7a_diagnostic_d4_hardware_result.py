#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D4 runtime-resolver-only hardware result.

This checker is read-only and depends only on the Python standard library.
It validates the user-reported result packet, the branch scope, and the
navigation links without claiming any additional firmware behavior.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

RESULT_BRANCH = "phase7a-diagnostic-d4-runtime-resolver-only-hardware-result"
BASE_BRANCH = "phase7a-diagnostic-d4-runtime-resolver-only-clean"

RESULT_MD_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.md"
)
RESULT_JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.json"
)
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
RUNTIME_CONFIG_README_PATH = REPO_ROOT / "docs" / "runtime_config" / "README.md"

EXPECTED_STATUS_MD = "USER_REPORTED_PASS"
EXPECTED_STATUS_JSON = "user_reported_pass"
EXPECTED_RESULT_SOURCE = "user-reported"
EXPECTED_USER_REPORT_TEXT = "tested, everything works without issues"
EXPECTED_DATE = "2026-06-09"
EXPECTED_DIAGNOSTIC_BRANCH = "phase7a-diagnostic-d4-runtime-resolver-only-clean"
EXPECTED_RESULT_BRANCH = "phase7a-diagnostic-d4-runtime-resolver-only-hardware-result"
EXPECTED_INSTALL_METHOD = "manual Glyph firmware update"
EXPECTED_NUNCHUK_STATUS = "not_tested"

EXPECTED_HYPOTHESES = [
    "H3: reduced_likelihood",
    "H1: still_open",
    "H4: still_open",
    "H5: still_open_in_combination",
    "H6: still_open",
]
EXPECTED_NEXT_DIAGNOSTIC = ["D3 global parse result only"]

EXPECTED_TABLE_ROWS = {
    "BOOT-001": ("boot", "PASS", "user-reported pass"),
    "BASELINE-001": ("baseline", "PASS", "user-reported pass"),
    "RF5-001": ("rf5_paths", "PASS", "no disconnect reported"),
    "RF6-001": ("rf6_paths", "PASS", "no disconnect reported"),
    "ORDINARY-DIR-001": ("directions", "PASS", 'covered by "everything works"'),
    "NEUTRAL-001": ("neutral_state", "PASS", 'covered by "everything works"'),
    "UNRELATED-BUTTONS-001": ("buttons", "PASS", 'covered by "everything works"'),
    "MODIFIERS-001": ("modifiers", "PASS", 'covered by "everything works"'),
    "NO-PARSER-001": ("parser_behavior", "SOURCE_CHECKED", "parser not called by D4 source/checker"),
    "NO-PAYLOAD-001": ("runtime_payload", "SOURCE_CHECKED", "no compiled payload/payload retention in D4"),
    "NO-GLOBAL-PARSE-001": ("parser_lifecycle", "SOURCE_CHECKED", "no global ParseResult in D4"),
    "RESOLVER-001": ("runtime_resolver", "PRESENT", "D4 resolver wrapper present"),
    "NO-STORAGE-001": ("storage", "SOURCE_CHECKED", "no runtime storage"),
    "NO-WRITE-001": ("webserial_or_write", "SOURCE_CHECKED", "no WebSerial/device write"),
    "NO-FLASH-001": ("flashing_automation", "SOURCE_CHECKED", "no flashing automation"),
    "NUNCHUK-001": ("nunchuk_scope", "NOT_TESTED", "not tested"),
}

ALLOWED_CHANGED_PREFIXES = (
    "docs/calibration/",
    "docs/runtime_config/",
    "tools/",
)

REQUIRED_MD_PHRASES = (
    "Phase 7A Diagnostic D4 Runtime Resolver Only Hardware Result - 2026-06-09",
    "status: USER_REPORTED_PASS",
    "result source: user-reported",
    "exact user report text: `tested, everything works without issues`",
    "date: 2026-06-09",
    "diagnostic branch tested: `phase7a-diagnostic-d4-runtime-resolver-only-clean`",
    "result branch: `phase7a-diagnostic-d4-runtime-resolver-only-hardware-result`",
    "install method: manual Glyph firmware update",
    "build command: `./scripts/build-glyph-mk6-quiet.sh`",
    "## Result Identity",
    "## Source Authority",
    "## Local Build Observations",
    "## Hardware Result Table",
    "## Diagnostic Interpretation",
    "## Non-Claims",
    "no release/public compatibility claim",
    "no nunchuk validation",
    "no automated device telemetry",
)

REQUIRED_INDEX_PHRASES = (
    "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.md",
    "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.json",
)

REQUIRED_README_PHRASE = (
    "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result_2026-06-09.md",
)

FORBIDDEN_POSITIVE_PHRASES = (
    "release/public compatibility is claimed",
    "public release is claimed",
    "official configurator compatibility is claimed",
    "nunchuk validated",
    "nunchuk validation is confirmed",
    "automated device telemetry is used",
    "automated telemetry is used",
)


class HardwareResultError(ValueError):
    """Raised when the hardware result record drifts from its contract."""


def fail(message: str) -> None:
    raise HardwareResultError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must be a JSON object")
    return payload


def git_lines(args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def require_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    missing = [phrase for phrase in phrases if phrase.lower() not in lowered]
    if missing:
        fail(f"{label} missing required phrase(s): " + ", ".join(missing))


def forbid_positive_phrase(text: str, phrase: str, *, label: str) -> None:
    pattern = re.compile(rf"(?<!no )(?<!not )\b{re.escape(phrase)}\b", re.IGNORECASE)
    if pattern.search(text):
        fail(f"{label} contains positive claim phrase: {phrase}")


def parse_table(text: str) -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    header_seen = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] == "Row ID":
            header_seen = True
            continue
        if not header_seen:
            continue
        if set(cells[0]) == {"-"}:
            continue
        rows[cells[0]] = (cells[1], cells[2], cells[3])
    return rows


def validate_branch_scope() -> None:
    current_branch = git_lines(["branch", "--show-current"])[0]
    if current_branch != RESULT_BRANCH:
        fail(f"current branch must be {RESULT_BRANCH!r}, got {current_branch!r}")

    base_is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if base_is_ancestor.returncode != 0:
        fail(f"{BASE_BRANCH!r} must be an ancestor of HEAD")

    status_lines = git_lines(["status", "--porcelain"])
    if status_lines:
        fail("worktree must be clean: " + ", ".join(status_lines))

    changed_paths = git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"])
    if not changed_paths:
        fail("expected branch to contain result files")
    for path in changed_paths:
        if not path.startswith(ALLOWED_CHANGED_PREFIXES):
            fail(f"changed path outside allowed scope: {path}")
        if path.startswith("src/"):
            fail(f"source file changed on result branch: {path}")


def validate_result_json(result: dict[str, Any]) -> None:
    expected_keys = {
        "schema_name",
        "status",
        "diagnostic_branch",
        "result_branch",
        "exact_user_report_text",
        "result_source",
        "result_date_local",
        "hardware_result_recorded",
        "d4_passed",
        "rf5_disconnect_observed",
        "rf6_disconnect_observed",
        "resolver_added",
        "parser_called",
        "global_parse_result_added",
        "compiled_payload_added",
        "payload_bytes_retained_in_firmware_image",
        "storage_added",
        "write_path_added",
        "flashing_automation_added",
        "runtime_behavior_changed_intended",
        "nunchuk_status",
        "root_cause_proven",
        "failed_activation_branch_merge_allowed",
        "hypothesis_updates",
        "next_recommended_diagnostic",
    }
    if set(result) != expected_keys:
        missing = sorted(expected_keys - set(result))
        unexpected = sorted(set(result) - expected_keys)
        parts = []
        if missing:
            parts.append("missing=" + ", ".join(missing))
        if unexpected:
            parts.append("unexpected=" + ", ".join(unexpected))
        fail("JSON keys do not match expected contract: " + "; ".join(parts))

    scalar_expectations = {
        "schema_name": "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_result",
        "status": EXPECTED_STATUS_JSON,
        "diagnostic_branch": EXPECTED_DIAGNOSTIC_BRANCH,
        "result_branch": EXPECTED_RESULT_BRANCH,
        "exact_user_report_text": EXPECTED_USER_REPORT_TEXT,
        "result_source": EXPECTED_RESULT_SOURCE,
        "result_date_local": EXPECTED_DATE,
        "hardware_result_recorded": True,
        "d4_passed": True,
        "rf5_disconnect_observed": False,
        "rf6_disconnect_observed": False,
        "resolver_added": True,
        "parser_called": False,
        "global_parse_result_added": False,
        "compiled_payload_added": False,
        "payload_bytes_retained_in_firmware_image": False,
        "storage_added": False,
        "write_path_added": False,
        "flashing_automation_added": False,
        "runtime_behavior_changed_intended": False,
        "nunchuk_status": EXPECTED_NUNCHUK_STATUS,
        "root_cause_proven": False,
        "failed_activation_branch_merge_allowed": False,
    }
    for key, expected in scalar_expectations.items():
        if result.get(key) != expected:
            fail(f"{key} must be {expected!r}")

    if result.get("hypothesis_updates") != EXPECTED_HYPOTHESES:
        fail("hypothesis_updates must preserve the D4 interpretation list")
    if result.get("next_recommended_diagnostic") != EXPECTED_NEXT_DIAGNOSTIC:
        fail("next_recommended_diagnostic must be D3 global parse result only")


def validate_markdown(text: str) -> None:
    require_phrases(text, REQUIRED_MD_PHRASES, label="result markdown")
    table_rows = parse_table(text)
    if set(table_rows) != set(EXPECTED_TABLE_ROWS):
        missing = sorted(set(EXPECTED_TABLE_ROWS) - set(table_rows))
        unexpected = sorted(set(table_rows) - set(EXPECTED_TABLE_ROWS))
        details = []
        if missing:
            details.append("missing=" + ", ".join(missing))
        if unexpected:
            details.append("unexpected=" + ", ".join(unexpected))
        fail("hardware result table rows do not match: " + "; ".join(details))

    for row_id, expected in EXPECTED_TABLE_ROWS.items():
        category, result, notes = table_rows[row_id]
        exp_category, exp_result, exp_notes = expected
        if (category, result, notes) != expected:
            fail(
                f"{row_id} row must be {(exp_category, exp_result, exp_notes)!r}, "
                f"got {(category, result, notes)!r}"
            )

    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        forbid_positive_phrase(text, phrase, label="result markdown")


def validate_navigation_links() -> None:
    index_text = read_required(CALIBRATION_INDEX_PATH)
    readme_text = read_required(RUNTIME_CONFIG_README_PATH)
    for phrase in REQUIRED_INDEX_PHRASES:
        if phrase not in index_text:
            fail(f"docs/calibration/INDEX.md missing required reference: {phrase}")
    for phrase in REQUIRED_README_PHRASE:
        if phrase not in readme_text:
            fail(f"docs/runtime_config/README.md missing required reference: {phrase}")


def main() -> int:
    try:
        validate_branch_scope()
        result_json = load_json(RESULT_JSON_PATH)
        validate_result_json(result_json)
        markdown_text = read_required(RESULT_MD_PATH)
        validate_markdown(markdown_text)
        validate_navigation_links()
    except (OSError, HardwareResultError, ValueError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"branch={RESULT_BRANCH}")
    print("hardware_result_recorded=true")
    print("d4_passed=true")
    print("rf5_disconnect_observed=false")
    print("rf6_disconnect_observed=false")
    print("resolver_added=true")
    print("parser_called=false")
    print("global_parse_result_added=false")
    print("compiled_payload_added=false")
    print("payload_bytes_retained_in_firmware_image=false")
    print("storage_added=false")
    print("write_path_added=false")
    print("flashing_automation_added=false")
    print("root_cause_proven=false")
    print("failed_activation_branch_merge_allowed=false")
    print("nunchuk_status=not_tested")
    print("next_recommended_diagnostic=D3 global parse result only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
