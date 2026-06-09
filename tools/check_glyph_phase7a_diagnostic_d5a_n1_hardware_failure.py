#!/usr/bin/env python3
"""Validate Phase 7A Diagnostic D5A-N1 hardware-failure guardrails."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate-hardware-failure"
BASE_BRANCH = "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate"

RESULT_MD = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.md"
)
RESULT_JSON = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.json"
)
RUNTIME_README = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs" / "calibration" / "INDEX.md"

EXPECTED_README_LINKS = (
    "docs/calibration/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.md",
    "docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.json",
)
EXPECTED_INDEX_LINKS = (
    "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.md",
    "fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.json",
)
EXPECTED_MARKDOWN_PHRASES = (
    "status: USER_REPORTED_FAIL",
    "Diagnostic branch tested: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`",
    "Result branch: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate-hardware-failure`",
    "Result source: user-reported",
    "Exact user report text: `flashed, same disconnects happen`",
    "Install method: manual Glyph firmware update",
    "Nunchuk: NOT_TESTED",
    "D5A-N1 failed.",
    "Same disconnects as D5A.",
    "RF5/RF6/LT6 disconnect class reproduced.",
    "separate RuntimeConfigView alias is reduced as suspect",
    "parse-status hot-path read remains primary suspect",
    "Root cause remains unproven.",
    "Failed activation branch remains abandoned and must not merge.",
    "Next diagnostic: D5A-N2 resolver without parse-status hot-path read.",
)
EXPECTED_JSON_STRINGS = {
    "schema_name": "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure",
    "status": "user_reported_fail",
    "diagnostic_branch": "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate",
    "result_branch": "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate-hardware-failure",
    "exact_user_report_text": "flashed, same disconnects happen",
    "result_source": "user_reported",
    "result_date_local": "2026-06-09",
    "nunchuk_status": "not_tested",
}
EXPECTED_JSON_BOOLEANS = {
    "hardware_result_recorded": True,
    "d5a_n1_failed": True,
    "same_disconnects_as_d5a": True,
    "rf5_disconnect_observed": True,
    "rf6_disconnect_observed": True,
    "lt6_disconnect_observed": True,
    "separate_runtime_config_alias_removed": True,
    "direct_source_owned_view_returned_after_parse_ok": True,
    "parse_status_gate_present": True,
    "global_parse_result_added": True,
    "resolver_added": True,
    "runtime_output_routing_to_parsed_result": False,
    "parsed_table_materialization_added": False,
    "storage_added": False,
    "write_path_added": False,
    "flashing_automation_added": False,
    "root_cause_proven": False,
    "failed_activation_branch_merge_allowed": False,
}
EXPECTED_HYPOTHESIS_UPDATES = [
    "separate_runtime_config_alias: reduced_likelihood",
    "parse_status_hot_path_read: elevated_suspect",
    "H5: elevated_combination_suspect",
    "H6: still_open",
]
EXPECTED_NEXT_DIAGNOSTIC = ["D5A-N2 resolver without parse-status hot-path read"]
EXPECTED_ROWS = {
    "BOOT-001": "PASS",
    "BASELINE-001": "FAIL",
    "RF5-001": "FAIL",
    "RF6-001": "FAIL",
    "LT6-001": "FAIL",
    "NUNCHUK-001": "NOT_TESTED",
}
EXPECTED_ALLOWED_PREFIXES = ("docs/calibration/", "docs/runtime_config/", "tools/")


class D5A_N1HardwareFailureError(ValueError):
    """Raised when D5A-N1 hardware-failure guardrails drift."""


def fail(message: str) -> None:
    raise D5A_N1HardwareFailureError(message)


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
    return " ".join(text.split()).lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def parse_status_path(line: str) -> str:
    parts = line.strip().split(None, 1)
    if len(parts) != 2:
        return ""
    path = parts[1]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip()


def changed_paths() -> set[str]:
    paths = set(run_git(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]).stdout.splitlines())
    for line in run_git(["status", "--short"]).stdout.splitlines():
        path = parse_status_path(line)
        if path:
            paths.add(path)
    return {path for path in paths if path}


def validate_branch_scope() -> None:
    branch = run_git(["branch", "--show-current"]).stdout.strip()
    if branch != BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {BRANCH!r}")
    if run_git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False).returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")

    paths = changed_paths()
    if not paths:
        fail("no changed paths detected on hardware-failure branch")

    required_paths = {
        rel(RESULT_MD),
        rel(RESULT_JSON),
        rel(RUNTIME_README),
        rel(CALIBRATION_INDEX),
        rel(Path(__file__).resolve()),
    }
    missing_required = required_paths - paths
    if missing_required:
        fail("missing expected changed paths: " + ", ".join(sorted(missing_required)))

    for path in sorted(paths):
        if path.startswith("src/"):
            fail(f"no src files may change on the hardware-failure branch: {path}")
        if not any(path.startswith(prefix) for prefix in EXPECTED_ALLOWED_PREFIXES):
            fail(f"changed path outside allowed scope: {path}")


def validate_markdown() -> None:
    text = read_required(RESULT_MD)
    for phrase in EXPECTED_MARKDOWN_PHRASES:
        require_phrase(text, phrase, "hardware failure markdown")


def validate_json() -> None:
    payload = load_json(RESULT_JSON)
    for key, expected in EXPECTED_JSON_STRINGS.items():
        if payload.get(key) != expected:
            fail(f"JSON field {key} must be {expected!r}")
    for key, expected in EXPECTED_JSON_BOOLEANS.items():
        if payload.get(key) is not expected:
            fail(f"JSON field {key} must be {expected!r}")

    hypotheses = payload.get("hypothesis_updates")
    if hypotheses != EXPECTED_HYPOTHESIS_UPDATES:
        fail("hypothesis_updates mismatch")

    next_diag = payload.get("next_recommended_diagnostic")
    if next_diag != EXPECTED_NEXT_DIAGNOSTIC:
        fail("next_recommended_diagnostic mismatch")

    rows = payload.get("result_rows")
    if not isinstance(rows, list):
        fail("result_rows must be a list")
    row_results = {
        row.get("row_id"): row.get("result")
        for row in rows
        if isinstance(row, dict)
    }
    for row_id, expected_result in EXPECTED_ROWS.items():
        if row_results.get(row_id) != expected_result:
            fail(f"result_rows entry {row_id} must be {expected_result}")

    if payload.get("diagnostic_interpretation") != [
        "D5A-N1 failed.",
        "Same disconnects as D5A.",
        "RF5/RF6/LT6 disconnect class reproduced.",
        "The separate RuntimeConfigView alias is reduced as suspect.",
        "parse-status hot-path read inside ResolveActiveRuntimeConfig() remains the primary suspect.",
        "D3 global parse result alone passed.",
        "D4 resolver alone passed.",
        "D5A and D5A-N1 both failed.",
        "Root cause remains unproven.",
        "Failed activation branch remains abandoned and must not merge.",
        "Next diagnostic: D5A-N2 resolver without parse-status hot-path read.",
    ]:
        fail("diagnostic_interpretation mismatch")

    if payload.get("non_claims") != [
        "result is user-reported",
        "no automated device telemetry",
        "no nunchuk validation",
        "no public release claim",
        "no release compatibility claim",
        "no proof of root cause",
        "no claim that the failed branch is recoverable",
    ]:
        fail("non_claims mismatch")


def validate_doc_indexes() -> None:
    readme = read_required(RUNTIME_README)
    index = read_required(CALIBRATION_INDEX)
    for link in EXPECTED_README_LINKS:
        if link not in readme:
            fail(f"runtime_config/README.md missing link/reference: {link}")
    for link in EXPECTED_INDEX_LINKS:
        if link not in index:
            fail(f"calibration/INDEX.md missing link/reference: {link}")


def main() -> None:
    validate_branch_scope()
    validate_markdown()
    validate_json()
    validate_doc_indexes()
    print("glyph_phase7a_diagnostic_d5a_n1_hardware_failure: ok")


if __name__ == "__main__":
    main()
