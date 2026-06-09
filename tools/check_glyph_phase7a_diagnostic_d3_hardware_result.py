#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D3 hardware-result artifacts."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_BRANCH = "phase7a-diagnostic-d3-global-parse-result-only"
RESULT_BRANCH = "phase7a-diagnostic-d3-global-parse-result-only-hardware-result"

RESULT_MD_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.md"
)
RESULT_JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.json"
)
INDEX_PATH = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
README_PATH = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CHECKER_PATH = REPO_ROOT / "tools" / "check_glyph_phase7a_diagnostic_d3_hardware_result.py"

EXPECTED_USER_REPORT = "tested, everything works without issues"
EXPECTED_STATUS_DOC = "USER_REPORTED_PASS"
EXPECTED_STATUS_JSON = "user_reported_pass"
EXPECTED_RESULT_SOURCE_JSON = "user_reported"
EXPECTED_RESULT_SOURCE_MD = "user-reported"
EXPECTED_RESULT_DATE = "2026-06-09"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_BUILD_REPORT = (
    "docs/runtime_config/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md"
)
EXPECTED_NUNCHUK_STATUS = "not_tested"
EXPECTED_ALLOWED_PREFIXES = (
    "docs/calibration/",
    "docs/runtime_config/",
    "tools/",
)
EXPECTED_BOOL_FIELDS = {
    "hardware_result_recorded": True,
    "d3_passed": True,
    "rf5_disconnect_observed": False,
    "rf6_disconnect_observed": False,
    "payload_bytes_retained": True,
    "global_parse_result_added": True,
    "parser_called_by_global_static_initialization": True,
    "resolver_added": False,
    "runtime_output_routing_to_parsed_result": False,
    "update_analog_outputs_changed": False,
    "update_digital_outputs_changed": False,
    "rf5_rf6_source_expressions_changed": False,
    "storage_added": False,
    "write_path_added": False,
    "flashing_automation_added": False,
    "runtime_behavior_changed_intended": False,
    "root_cause_proven": False,
    "failed_activation_branch_merge_allowed": False,
}
EXPECTED_HYPOTHESIS_UPDATES = [
    "H1: reduced_likelihood",
    "H4: reduced_likelihood",
    "H2: previously_reduced_by_D2B",
    "H3: previously_reduced_by_D4",
    "H5: still_open_in_combination",
    "H6: still_open",
]
EXPECTED_ROWS = {
    "BOOT-001": ("PASS", "User-reported pass."),
    "BASELINE-001": ("PASS", "User-reported pass."),
    "RF5-001": ("PASS", "No disconnect reported."),
    "RF6-001": ("PASS", "No disconnect reported."),
    "ORDINARY-DIR-001": ("PASS", 'Covered by "everything works".'),
    "NEUTRAL-001": ("PASS", 'Covered by "everything works".'),
    "UNRELATED-BUTTONS-001": ("PASS", 'Covered by "everything works".'),
    "MODIFIERS-001": ("PASS", 'Covered by "everything works".'),
    "PAYLOAD-001": ("PRESENT", "D2B retained payload bytes present."),
    "GLOBAL-PARSE-001": ("PRESENT", "Global/static parse result present."),
    "PARSER-CALL-001": ("PRESENT", "Parser called by global/static initialization."),
    "NO-RESOLVER-001": ("SOURCE_CHECKED", "No runtime resolver added."),
    "NO-RUNTIME-ROUTING-001": ("SOURCE_CHECKED", "Parsed result not routed into output lookup."),
    "NO-STORAGE-001": ("SOURCE_CHECKED", "No runtime storage."),
    "NO-WRITE-001": ("SOURCE_CHECKED", "No WebSerial/device write."),
    "NO-FLASH-001": ("SOURCE_CHECKED", "No flashing automation."),
    "NUNCHUK-001": ("NOT_TESTED", "Not tested."),
}
REQUIRED_MARKDOWN_PHRASES = (
    "status: USER_REPORTED_PASS",
    f"Diagnostic branch tested: `{BASE_BRANCH}`",
    f"Result branch: `{RESULT_BRANCH}`",
    f"Result source: {EXPECTED_RESULT_SOURCE_MD}",
    f"Exact user report text: `{EXPECTED_USER_REPORT}`",
    f"Result date: `{EXPECTED_RESULT_DATE}`",
    "Install method: manual Glyph firmware update",
    f"Build command: `{EXPECTED_BUILD_COMMAND}`",
    EXPECTED_BUILD_REPORT,
    "Source/build provenance: local D3 branch and build process only",
    "Nunchuk: NOT_TESTED",
    "D3 passed.",
    "Global/static parser initialization alone did not reproduce the RF5/RF6",
    "H1 global/static parser initialization is reduced in likelihood.",
    "H4 parser loop/static-init is reduced in likelihood.",
    "D2B, D3, and D4 each passed in isolation.",
    "H5 remains open only in combination.",
    "H6 remains open.",
    "Root cause remains unproven.",
    "Failed activation branch remains abandoned and must not merge.",
    "controlled combinations rather than a single isolated component",
    "result is user-reported",
    "no automated device telemetry",
    "no nunchuk validation",
    "no public release claim",
    "no release compatibility claim",
    "no proof of root cause",
    "no claim that parser is generally safe in every activation design",
    "no claim that the failed branch is recoverable",
)


class Phase7AD3HardwareResultError(ValueError):
    """Raised when the D3 hardware-result record is inconsistent."""


def fail(message: str) -> None:
    raise Phase7AD3HardwareResultError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def git_lines(args: list[str], *, check: bool = True) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    return [line for line in completed.stdout.splitlines() if line.strip()]


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
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def require_table_row(text: str, row_id: str, result: str, note_phrase: str) -> None:
    pattern = rf"\|\s*{re.escape(row_id)}\s*\|[^\n]*\|\s*{re.escape(result)}\s*\|[^\n]*"
    if not re.search(pattern, text, flags=re.IGNORECASE):
        fail(f"missing result table row for {row_id} with result {result}")
    if note_phrase not in text:
        fail(f"result table row for {row_id} missing note phrase: {note_phrase}")


def parse_git_status_path(line: str) -> str:
    parts = line.strip().split(None, 1)
    if len(parts) != 2:
        return ""
    path = parts[1]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip()


def git_changed_paths(base_branch: str) -> set[str]:
    changed = set(git_lines(["diff", "--name-only", f"{base_branch}...HEAD"]))
    for status_line in git_lines(["status", "--short"]):
        path = parse_git_status_path(status_line)
        if path:
            changed.add(path)
    return {path for path in changed if path}


def validate_branch_scope() -> None:
    branch_lines = git_lines(["branch", "--show-current"])
    branch = branch_lines[0].strip() if branch_lines else ""
    if branch != RESULT_BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {RESULT_BRANCH!r}")

    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if ancestor.returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")

    changed_paths = git_changed_paths(BASE_BRANCH)
    if not changed_paths:
        fail("no changed paths detected for hardware result branch")

    required_paths = {
        rel(RESULT_MD_PATH),
        rel(RESULT_JSON_PATH),
        rel(INDEX_PATH),
        rel(README_PATH),
        rel(CHECKER_PATH),
    }
    missing_required = required_paths - changed_paths
    if missing_required:
        fail("missing expected changed paths: " + ", ".join(sorted(missing_required)))

    for path in sorted(changed_paths):
        if path.startswith("src/"):
            fail(f"firmware source path changed on result branch: {path}")
        if not any(path.startswith(prefix) for prefix in EXPECTED_ALLOWED_PREFIXES):
            fail(f"changed path outside allowed hardware-result scope: {path}")


def validate_markdown() -> None:
    text = read_required(RESULT_MD_PATH)
    for phrase in REQUIRED_MARKDOWN_PHRASES:
        require_phrase(text, phrase, "hardware result markdown")
    for row_id, (result, note) in EXPECTED_ROWS.items():
        require_table_row(text, row_id, result, note)
    validate_no_forbidden_claims(text, label="hardware result markdown")


def validate_json() -> None:
    payload = load_json(RESULT_JSON_PATH)
    if payload.get("schema_name") != "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result":
        fail("unexpected schema_name")
    if payload.get("status") != EXPECTED_STATUS_JSON:
        fail("unexpected JSON status")
    if payload.get("diagnostic_branch") != BASE_BRANCH:
        fail("diagnostic_branch mismatch")
    if payload.get("result_branch") != RESULT_BRANCH:
        fail("result_branch mismatch")
    if payload.get("exact_user_report_text") != EXPECTED_USER_REPORT:
        fail("exact_user_report_text mismatch")
    if payload.get("result_source") != EXPECTED_RESULT_SOURCE_JSON:
        fail("result_source mismatch")
    if payload.get("result_date_local") != EXPECTED_RESULT_DATE:
        fail("result_date_local mismatch")
    if payload.get("build_command") != EXPECTED_BUILD_COMMAND:
        fail("build_command mismatch")
    if payload.get("build_report_reference") != EXPECTED_BUILD_REPORT:
        fail("build_report_reference mismatch")
    if payload.get("install_method") != "manual Glyph firmware update":
        fail("install_method mismatch")
    if payload.get("source_build_provenance") != "local D3 branch and build process only":
        fail("source_build_provenance mismatch")
    if payload.get("nunchuk_status") != EXPECTED_NUNCHUK_STATUS:
        fail("nunchuk_status mismatch")
    for key, expected in EXPECTED_BOOL_FIELDS.items():
        if payload.get(key) is not expected:
            fail(f"{key} must be {expected!r}")
    if payload.get("hypothesis_updates") != EXPECTED_HYPOTHESIS_UPDATES:
        fail("hypothesis_updates mismatch")
    if payload.get("next_recommended_diagnostic") != ["controlled combination diagnostic"]:
        fail("next_recommended_diagnostic mismatch")
    validate_json_rows(payload)
    validate_no_forbidden_claims(json.dumps(payload, sort_keys=True), label="hardware result JSON")


def validate_json_rows(payload: dict[str, Any]) -> None:
    result_rows = payload.get("result_rows")
    if not isinstance(result_rows, list):
        fail("result_rows must be a list")
    seen_rows: dict[str, dict[str, Any]] = {}
    for row in result_rows:
        if not isinstance(row, dict):
            fail("result_rows entries must be objects")
        row_id = row.get("row_id")
        if not isinstance(row_id, str):
            fail("result row missing row_id")
        if row_id in seen_rows:
            fail(f"duplicate result row: {row_id}")
        seen_rows[row_id] = row

    if set(seen_rows) != set(EXPECTED_ROWS):
        fail("result_rows row_id set mismatch")
    for row_id, (expected_result, expected_note) in EXPECTED_ROWS.items():
        row = seen_rows[row_id]
        if row.get("result") != expected_result:
            fail(f"result row {row_id} result mismatch")
        if expected_note not in str(row.get("notes", "")):
            fail(f"result row {row_id} notes mismatch")


def validate_navigation() -> None:
    index_text = read_required(INDEX_PATH)
    require_phrase(
        index_text,
        "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.md",
        "calibration index",
    )
    require_phrase(
        index_text,
        "fixtures/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.json",
        "calibration index",
    )

    readme_text = read_required(README_PATH)
    require_phrase(
        readme_text,
        "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.md",
        "runtime-config README",
    )
    require_phrase(
        readme_text,
        "global/static parser initialization alone did not reproduce the RF5/RF6 disconnect",
        "runtime-config README",
    )
    require_phrase(
        readme_text,
        "D2B, D3, and D4 each passed in isolation",
        "runtime-config README",
    )


def validate_no_forbidden_claims(text: str, *, label: str) -> None:
    positive_patterns = (
        r"(?<!no )(?<!not )\bpublic release(?: is)? claimed\b",
        r"(?<!no )(?<!not )\brelease compatibility(?: is)? claimed\b",
        r"(?<!no )(?<!not )\bnunchuk validation(?: is)? (?:claimed|confirmed|passed)\b",
        r"\bnunchuk(?: is)? validated\b",
        r"(?<!no )(?<!not )\broot cause(?: is)? (?:proven|confirmed)\b",
    )
    for pattern in positive_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"{label} contains forbidden positive claim: {pattern}")


def main() -> int:
    validate_branch_scope()
    if not RESULT_MD_PATH.exists():
        fail(f"missing hardware result markdown: {rel(RESULT_MD_PATH)}")
    if not RESULT_JSON_PATH.exists():
        fail(f"missing hardware result JSON: {rel(RESULT_JSON_PATH)}")
    validate_markdown()
    validate_json()
    validate_navigation()
    print("glyph_phase7a_diagnostic_d3_hardware_result: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
