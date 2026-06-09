#!/usr/bin/env python3
"""Validate Phase 7A Diagnostic D5A hardware-failure artifacts."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d5a-parse-status-gated-routing-hardware-failure"
BASE_BRANCH = "phase7a-diagnostic-d5-parsed-result-runtime-routing"

MD_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.json"
)
INDEX_PATH = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
README_PATH = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CHECKER_PATH = REPO_ROOT / "tools" / "check_glyph_phase7a_diagnostic_d5a_hardware_failure.py"

EXPECTED_STATUS_DOC = "USER_REPORTED_FAIL"
EXPECTED_STATUS_JSON = "user_reported_fail"
EXPECTED_USER_REPORT = (
    "tested, failed. RF5 and RF6 caused disconnect. Because LT6 had been similarly coded I tested that too, and same disconnect happened. "
    "Likely was an issue already at the same time."
)

ALLOWED_PREFIXES = (
    "docs/calibration/",
    "docs/runtime_config/",
    "tools/",
)

FORBIDDEN_CLAIM_PATTERNS = (
    r"(?<!no )(?<!not )\bpublic release(?: compatibility)?\b.*\bclaim\b",
    r"(?<!no )(?<!not )\brelease compatibility\b",
)


class D5AHardwareFailureError(ValueError):
    """Raised when D5A hardware-failure artifacts violate guardrails."""


def fail(message: str) -> None:
    raise D5AHardwareFailureError(message)


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


def parse_git_status_path(line: str) -> str:
    parts = line.strip().split(None, 1)
    if len(parts) != 2:
        return ""
    path = parts[1]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip()


def changed_paths(base_ref: str) -> set[str]:
    diff_paths = set(
        run_git(["diff", "--name-only", f"{base_ref}...HEAD"]).stdout.splitlines()
    )
    for status_line in run_git(["status", "--short"]).stdout.splitlines():
        path = parse_git_status_path(status_line)
        if path:
            diff_paths.add(path)
    return {path for path in diff_paths if path.strip()}


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


def require_regex(pattern: str, text: str, label: str) -> None:
    if re.search(pattern, text, flags=re.IGNORECASE):
        fail(f"{label} contains forbidden claim pattern: {pattern}")


def require_markdown_status_row(text: str, row_id: str, result: str, note: str) -> None:
    for line in text.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith("|"):
            continue
        parts = [piece.strip() for piece in stripped_line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        if parts[0] != row_id:
            continue
        if len(parts) > 3 and parts[3] == result:
            if note and normalize(note) not in normalize(stripped_line):
                fail(f"markdown row {row_id} does not include expected note text")
            return
    fail(f"missing markdown status row for {row_id} with result {result}")


def validate_branch_scope() -> None:
    branch = run_git(["branch", "--show-current"]).stdout.strip()
    if branch != BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {BRANCH!r}")

    if run_git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False).returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")

    changed = changed_paths(BASE_BRANCH)
    required_paths = {
        rel(MD_PATH),
        rel(JSON_PATH),
        rel(INDEX_PATH),
        rel(README_PATH),
        rel(CHECKER_PATH),
    }

    missing = required_paths - changed
    if missing:
        fail("missing expected changed paths: " + ", ".join(sorted(missing)))

    for path in sorted(changed):
        if path.startswith("src/"):
            fail(f"firmware source must not change on this result branch: {path}")
        if not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            fail(f"changed path outside allowed result scope: {path}")


def validate_markdown() -> None:
    text = read_required(MD_PATH)
    require_phrase(text, f"status: {EXPECTED_STATUS_DOC}", "result markdown")
    require_phrase(text, f"Diagnostic branch tested: `{BASE_BRANCH}`", "result markdown")
    require_phrase(text, f"Result branch: `{BRANCH}`", "result markdown")
    require_phrase(text, "Result source: user-reported", "result markdown")
    require_phrase(text, f"Exact user report text: `{EXPECTED_USER_REPORT}`", "result markdown")
    require_phrase(text, "Install method: manual Glyph firmware update", "result markdown")
    require_phrase(text, "Nunchuk: NOT_TESTED", "result markdown")
    require_phrase(text, "no automated device telemetry", "result markdown")
    require_phrase(text, "no public release claim", "result markdown")
    require_phrase(text, "no release compatibility claim", "result markdown")
    require_phrase(
        text,
        "Failed activation branch remains abandoned and must not merge.",
        "result markdown",
    )
    require_phrase(text, "D5A-N1 direct canonical source-owned view after parse-status gate", "result markdown")

    for row_id, result, note in (
        ("BOOT-001", "UNKNOWN", "Not explicitly reported"),
        ("BASELINE-001", "FAIL_OR_PARTIAL", "disconnect occurred"),
        ("RF5-001", "FAIL", "User report says RF5 caused disconnect"),
        ("RF6-001", "FAIL", "User report says RF6 caused disconnect"),
        ("LT6-001", "FAIL", "User report says LT6 caused disconnect"),
        ("ORDINARY-DIR-001", "UNKNOWN", "Not explicitly reported"),
        ("NEUTRAL-001", "UNKNOWN", "Not explicitly reported"),
        ("UNRELATED-BUTTONS-001", "UNKNOWN", "Not explicitly reported"),
        ("MODIFIERS-001", "UNKNOWN", "Not explicitly reported"),
        ("PAYLOAD-001", "SOURCE_CHECKED", "D2B retained payload evidence"),
        ("GLOBAL-PARSE-001", "SOURCE_CHECKED", "Global/static parse result"),
        ("PARSER-CALL-001", "SOURCE_CHECKED", "Parser call is present"),
        ("RESOLVER-001", "SOURCE_CHECKED", "`ResolveActiveRuntimeConfig()`"),
        ("PARSE-STATUS-GATE-001", "SOURCE_CHECKED", "parse-status"),
        ("SOURCE-OWNED-ROUTING-001", "SOURCE_CHECKED", "`kPhase7AD5AParseStatusGatedRuntimeConfigView`"),
        ("NO-PARSED-TABLES-001", "SOURCE_CHECKED", "deferred"),
        ("NO-STORAGE-001", "SOURCE_CHECKED", "No runtime storage"),
        ("NO-WRITE-001", "SOURCE_CHECKED", "No runtime write path or WebSerial behavior change"),
        ("NO-FLASH-001", "SOURCE_CHECKED", "No firmware flashing automation"),
        ("NUNCHUK-001", "NOT_TESTED", "Not tested in this report"),
    ):
        require_markdown_status_row(text, row_id, result, note)

    for pattern in FORBIDDEN_CLAIM_PATTERNS:
        require_regex(pattern, text, "result markdown")


def validate_json() -> None:
    payload = load_json(JSON_PATH)
    expected_pairs = {
        "status": EXPECTED_STATUS_JSON,
        "diagnostic_branch": BASE_BRANCH,
        "result_branch": BRANCH,
        "exact_user_report_text": EXPECTED_USER_REPORT,
        "result_source": "user_reported",
        "result_date_local": "2026-06-09",
        "hardware_result_recorded": True,
        "d5a_failed": True,
        "rf5_disconnect_observed": True,
        "rf6_disconnect_observed": True,
        "lt6_disconnect_observed": True,
        "ordinary_direction_status": "unknown",
        "neutral_status": "unknown",
        "unrelated_buttons_status": "unknown",
        "nunchuk_status": "not_tested",
        "payload_bytes_retained": True,
        "global_parse_result_added": True,
        "parser_called_by_global_static_initialization": True,
        "resolver_added": True,
        "parse_status_gated_routing_added": True,
        "source_owned_runtime_view_routed_after_parse_ok": True,
        "parsed_table_materialization_added": False,
        "true_parsed_result_routing_deferred": True,
        "storage_added": False,
        "write_path_added": False,
        "flashing_automation_added": False,
        "root_cause_proven": False,
        "failed_activation_branch_merge_allowed": False,
    }

    for key, expected in expected_pairs.items():
        if payload.get(key) != expected:
            fail(f"JSON field {key!r} must be {expected!r}")

    if payload.get("schema_name") != "glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure":
        fail("schema_name mismatch")

    if payload.get("hypothesis_updates") != [
        "H5: elevated_combination_suspect",
        "H1: previously_reduced_by_D3",
        "H2: previously_reduced_by_D2B",
        "H3: previously_reduced_by_D4",
        "H4: previously_reduced_by_D3",
        "H6: still_open",
    ]:
        fail("hypothesis_updates mismatch")

    if payload.get("next_recommended_diagnostic") != [
        "D5A-N1 direct canonical source-owned view after parse-status gate",
    ]:
        fail("next_recommended_diagnostic mismatch")


def validate_navigation_links() -> None:
    index_text = read_required(INDEX_PATH)
    require_phrase(
        index_text,
        "glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.md",
        "calibration index",
    )
    require_phrase(
        index_text,
        "fixtures/glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.json",
        "calibration index",
    )

    readme_text = read_required(README_PATH)
    require_phrase(
        readme_text,
        "glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.md",
        "runtime-config README",
    )
    require_phrase(
        readme_text,
        "fixtures/glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.json",
        "runtime-config README",
    )


def main() -> int:
    validate_branch_scope()
    validate_markdown()
    validate_json()
    validate_navigation_links()
    print("check_glyph_phase7a_diagnostic_d5a_hardware_failure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
