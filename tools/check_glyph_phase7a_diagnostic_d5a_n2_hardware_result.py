#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D5A-N2 hardware-result artifacts."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_BRANCH = "phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read"
RESULT_BRANCH = "phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read-hardware-result"

RESULT_MD_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.md"
)
RESULT_JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.json"
)
INDEX_PATH = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
README_PATH = REPO_ROOT / "docs" / "runtime_config" / "README.md"
ROOT_CAUSE_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "phase7a_activation_failure_root_cause_analysis_2026-06-09.md"
)
BUILD_MATRIX_PATH = REPO_ROOT / "docs" / "runtime_config" / "phase7a_activation_failure_diagnostic_build_matrix.md"

ALLOWED_PREFIXES = ("docs/calibration/", "docs/runtime_config/", "tools/")
EXPECTED_USER_REPORT = "flashed n2. It works. No disconnects anymore."
EXPECTED_RESULT_SOURCE = "user-reported"
EXPECTED_JSON_RESULT_SOURCE = "user_reported"
EXPECTED_RESULT_DATE = "2026-06-09"
EXPECTED_INSTALL_METHOD = "manual Glyph firmware update"
EXPECTED_NUNCHUK_STATUS = "not_tested"
EXPECTED_LIKELY_TRIGGER = "runtime hot-path read/branch on kPhase7AD3GlobalParseResult.status"
EXPECTED_FUTURE_CONSTRAINT = (
    "Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver."
)

EXPECTED_MARKDOWN_PHRASES = (
    "status: USER_REPORTED_PASS",
    f"Diagnostic branch tested: `{BASE_BRANCH}`",
    f"Result branch: `{RESULT_BRANCH}`",
    f"Result source: {EXPECTED_RESULT_SOURCE}",
    f"Exact user report text: `{EXPECTED_USER_REPORT}`",
    f"Install method: {EXPECTED_INSTALL_METHOD}",
    "Nunchuk: NOT_TESTED",
    "D5A-N2 passed.",
    "RF5/RF6/LT6 disconnects were not observed.",
    "parse-status hot-path read/branch on `kPhase7AD3GlobalParseResult.status` is the likely trigger.",
    "The low-level root cause mechanism is not proven.",
    "Failed activation branch must not merge.",
    "Future runtime activation must not read parser result state from",
    "UpdateAnalogOutputs(...) or the analog hot-path resolver.",
)

EXPECTED_RESULT_ROWS: dict[str, tuple[str, str]] = {
    "BOOT-001": ("PASS", "User-reported pass."),
    "BASELINE-001": ("PASS", "User-reported pass."),
    "RF5-001": ("PASS", "No disconnect reported."),
    "RF6-001": ("PASS", "No disconnect reported."),
    "LT6-001": ("PASS", "No disconnect reported."),
    "ORDINARY-DIR-001": ("UNKNOWN", "Not separately reported."),
    "NEUTRAL-001": ("UNKNOWN", "Not separately reported."),
    "UNRELATED-BUTTONS-001": ("UNKNOWN", "Not separately reported."),
    "MODIFIERS-001": ("UNKNOWN", "Not separately reported."),
    "PAYLOAD-001": ("SOURCE_CHECKED", "D2B retained payload bytes remain present."),
    "GLOBAL-PARSE-001": ("SOURCE_CHECKED", "Global/static parse result present."),
    "PARSER-CALL-001": ("SOURCE_CHECKED", "Parser called by global/static initialization."),
    "RESOLVER-001": ("SOURCE_CHECKED", "Resolver call remains in `UpdateAnalogOutputs(...)`."),
    "PARSE-STATUS-READ-001": ("SOURCE_CHECKED", "Parse-status hot-path read removed from runtime hot path."),
    "SOURCE-OWNED-ROUTING-001": (
        "SOURCE_CHECKED",
        "Canonical source-owned runtime config return remains in place.",
    ),
    "FALLBACK-001": (
        "SOURCE_CHECKED",
        "Fallback remains source-owned current baseline or known-good runtime config.",
    ),
    "NO-PARSED-TABLES-001": ("SOURCE_CHECKED", "No parsed table materialization added."),
    "NO-STORAGE-001": ("SOURCE_CHECKED", "No runtime-config storage."),
    "NO-WRITE-001": ("SOURCE_CHECKED", "No WebSerial/device write."),
    "NO-FLASH-001": ("SOURCE_CHECKED", "No firmware flashing automation."),
    "NUNCHUK-001": ("NOT_TESTED", "Not tested."),
}

EXPECTED_JSON_STRINGS = {
    "schema_name": "glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result",
    "status": "user_reported_pass",
    "diagnostic_branch": BASE_BRANCH,
    "result_branch": RESULT_BRANCH,
    "exact_user_report_text": EXPECTED_USER_REPORT,
    "result_source": EXPECTED_JSON_RESULT_SOURCE,
    "result_date_local": EXPECTED_RESULT_DATE,
    "nunchuk_status": EXPECTED_NUNCHUK_STATUS,
    "likely_trigger": EXPECTED_LIKELY_TRIGGER,
}

EXPECTED_JSON_BOOLEANS = {
    "hardware_result_recorded": True,
    "d5a_n2_passed": True,
    "rf5_disconnect_observed": False,
    "rf6_disconnect_observed": False,
    "lt6_disconnect_observed": False,
    "parse_status_hot_path_read_removed": True,
    "global_parse_result_added": True,
    "resolver_added": True,
    "resolver_called_from_update_analog_outputs": True,
    "runtime_output_routing_to_parsed_result": False,
    "parsed_table_materialization_added": False,
    "storage_added": False,
    "write_path_added": False,
    "flashing_automation_added": False,
    "root_cause_mechanism_proven": False,
    "failed_activation_branch_merge_allowed": False,
}

EXPECTED_HYPOTHESIS_UPDATES = [
    "parse_status_hot_path_read: elevated_likely_trigger",
    "separate_runtime_config_alias: reduced_likelihood",
    "global_parse_result_alone: previously_reduced_by_D3",
    "resolver_alone: previously_reduced_by_D4",
    "resolver_without_parse_status_read: passed_by_D5A_N2",
    "H5: narrowed_to_parse_status_hot_path_read",
    "H6: still_open_for_low_level_mechanism",
]

EXPECTED_FUTURE_DESIGN_CONSTRAINTS = [
    "Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver.",
    "Resolve active runtime config outside analog hot path before using it in output generation.",
    "Keep failed activation branch abandoned.",
    "Do not merge diagnostic implementation branches into configurator as production code.",
]


class D5AN2HardwareResultError(ValueError):
    """Raised when D5A-N2 hardware-result guardrails drift."""


def fail(message: str) -> None:
    raise D5AN2HardwareResultError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    return completed


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
    changed = set(run_git(["diff", "--name-only", f"{base_branch}...HEAD"]).stdout.splitlines())
    for status_line in run_git(["status", "--short"]).stdout.splitlines():
        path = parse_git_status_path(status_line)
        if path:
            changed.add(path)
    return {path for path in changed if path}


def validate_branch_scope() -> None:
    branch = run_git(["branch", "--show-current"]).stdout.strip()
    if branch != RESULT_BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {RESULT_BRANCH!r}")

    if run_git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False).returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")

    changed_paths = git_changed_paths(BASE_BRANCH)
    if not changed_paths:
        fail("no changed paths detected for hardware-result branch")

    required_paths = {
        rel(RESULT_MD_PATH),
        rel(RESULT_JSON_PATH),
        rel(INDEX_PATH),
        rel(README_PATH),
        rel(ROOT_CAUSE_PATH),
        rel(BUILD_MATRIX_PATH),
        rel(Path(__file__).resolve()),
    }
    missing_required = required_paths - changed_paths
    if missing_required:
        fail("missing expected changed paths: " + ", ".join(sorted(missing_required)))

    for path in sorted(changed_paths):
        if path.startswith("src/"):
            fail(f"firmware source path changed on result branch: {path}")
        if not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            fail(f"changed path outside allowed result scope: {path}")


def validate_markdown() -> None:
    text = read_required(RESULT_MD_PATH)
    for phrase in EXPECTED_MARKDOWN_PHRASES:
        require_phrase(text, phrase, "hardware result markdown")
    for row_id, (result, note_phrase) in EXPECTED_RESULT_ROWS.items():
        require_table_row(text, row_id, result, note_phrase)


def validate_json() -> None:
    payload = load_json(RESULT_JSON_PATH)
    for key, expected in EXPECTED_JSON_STRINGS.items():
        if payload.get(key) != expected:
            fail(f"JSON field {key} must be {expected!r}")
    for key, expected in EXPECTED_JSON_BOOLEANS.items():
        if payload.get(key) is not expected:
            fail(f"JSON field {key} must be {expected!r}")

    if payload.get("hypothesis_updates") != EXPECTED_HYPOTHESIS_UPDATES:
        fail("hypothesis_updates mismatch")

    if payload.get("future_design_constraints") != EXPECTED_FUTURE_DESIGN_CONSTRAINTS:
        fail("future_design_constraints mismatch")

    rows = payload.get("result_rows")
    if not isinstance(rows, list):
        fail("result_rows must be a list")

    row_map: dict[str, tuple[Any, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("result_rows entries must be objects")
        row_id = row.get("row_id")
        row_result = row.get("result")
        row_note = row.get("notes")
        if not isinstance(row_id, str) or not isinstance(row_result, str) or not isinstance(row_note, str):
            fail("result_rows entries must include row_id, result, and notes strings")
        row_map[row_id] = (row_result, row_note)

    for row_id, (expected_result, note_phrase) in EXPECTED_RESULT_ROWS.items():
        actual = row_map.get(row_id)
        if actual is None:
            fail(f"missing result_rows entry: {row_id}")
        if actual[0] != expected_result:
            fail(f"result_rows entry {row_id} must be {expected_result!r}")
        if note_phrase not in actual[1]:
            fail(f"result_rows entry {row_id} missing note phrase: {note_phrase}")

    if payload.get("failed_activation_branch_merge_allowed") is not False:
        fail("failed_activation_branch_merge_allowed must be false")

    if payload.get("likely_trigger") != EXPECTED_LIKELY_TRIGGER:
        fail("likely_trigger mismatch")

    if payload.get("nunchuk_status") != EXPECTED_NUNCHUK_STATUS:
        fail("nunchuk_status mismatch")


def validate_supporting_docs() -> None:
    index_text = read_required(INDEX_PATH)
    require_phrase(
        index_text,
        "glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.md",
        "docs/calibration/INDEX.md",
    )
    require_phrase(
        index_text,
        "fixtures/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.json",
        "docs/calibration/INDEX.md",
    )

    readme_text = read_required(README_PATH)
    require_phrase(
        readme_text,
        "docs/calibration/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.md",
        "docs/runtime_config/README.md",
    )
    require_phrase(
        readme_text,
        "docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.json",
        "docs/runtime_config/README.md",
    )

    root_cause_text = read_required(ROOT_CAUSE_PATH)
    for phrase in (
        "D5A-N2 hardware result recorded.",
        "Result source: user-reported",
        f"Exact user report text: `{EXPECTED_USER_REPORT}`",
        f"Diagnostic branch tested: `{BASE_BRANCH}`",
        f"Result branch: `{RESULT_BRANCH}`",
        "RF5/RF6/LT6 disconnects were not observed.",
        "D5A-N2 passed.",
        "The parse-status hot-path read/branch on",
        "kPhase7AD3GlobalParseResult.status",
        "is the likely trigger.",
        "The low-level root cause mechanism is not proven.",
        "Failed activation branch must not merge.",
        "Future runtime activation must not read parser result state from",
        "UpdateAnalogOutputs(...) or analog hot-path resolver.",
        "Nunchuk: NOT_TESTED",
    ):
        require_phrase(root_cause_text, phrase, "root-cause analysis doc")

    matrix_text = read_required(BUILD_MATRIX_PATH)
    for phrase in (
        "D5A-N2 hardware result recorded.",
        "Result source: user-reported",
        f"Exact user report text: `{EXPECTED_USER_REPORT}`",
        f"Diagnostic branch tested: `{BASE_BRANCH}`",
        f"Result branch: `{RESULT_BRANCH}`",
        "RF5/RF6/LT6 disconnects were not observed.",
        "D5A-N2 passed.",
        "The parse-status hot-path read/branch on",
        "kPhase7AD3GlobalParseResult.status",
        "is the likely trigger.",
        "The low-level root cause mechanism is not proven.",
        "Failed activation branch must not merge.",
        "Future runtime activation must not read parser result state from",
        "UpdateAnalogOutputs(...) or analog hot-path resolver.",
        "Nunchuk: NOT_TESTED",
    ):
        require_phrase(matrix_text, phrase, "diagnostic build matrix")


def main() -> int:
    validate_branch_scope()
    validate_markdown()
    validate_json()
    validate_supporting_docs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
