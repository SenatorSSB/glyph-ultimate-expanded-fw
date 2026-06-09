#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D2B hardware-result artifacts."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_BRANCH = "phase7a-diagnostic-d2b-retained-payload-bytes"
RESULT_BRANCH = "phase7a-diagnostic-d2b-retained-payload-bytes-hardware-result"
ALLOWED_BRANCHES = {BASE_BRANCH, RESULT_BRANCH}

RESULT_MD_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.md"
)
RESULT_JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.json"
)
INDEX_PATH = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
README_PATH = REPO_ROOT / "docs" / "runtime_config" / "README.md"

EXPECTED_STATUS_DOC = "USER_REPORTED_PASS"
EXPECTED_JSON_STATUS = "user_reported_pass"
EXPECTED_USER_REPORT = (
    "tested, everything works. Especially RF5-6 do not cause a disconnect."
)
EXPECTED_RESULT_SOURCE = "user-reported"
EXPECTED_RESULT_DATE = "2026-06-09"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_COMMIT_SHA = "bc0525dba8ecbdc62251a3b9d4bb2fc54a9a1a35"
EXPECTED_NUNCHUK_STATUS = "not_tested"
EXPECTED_HYPOTHESES = {
    "H2": "reduced_likelihood",
    "H1": "still_open",
    "H3": "still_open",
    "H4": "still_open",
    "H5": "still_open_in_combination",
    "H6": "still_open",
}
EXPECTED_NEXT_DIAGNOSTICS = (
    "D3 global parse result only",
    "D4 runtime resolver only",
)
EXPECTED_NON_CLAIMS = (
    "no root cause proven",
    "no parser safety proven",
    "no resolver safety proven",
    "no nunchuk validation",
    "no public release claim",
    "no release compatibility claim",
)
EXPECTED_SOURCE_BUILD_CHECKS = (
    "no parser call claim remains source/build-checked, not hardware-observed",
    "no resolver claim remains source/build-checked, not hardware-observed",
    "no storage/write/flashing claim remains source/build-checked, not hardware-observed",
)
EXPECTED_DIAGNOSTIC_INTERPRETATION = (
    "Retained payload bytes alone did not reproduce the RF5/RF6 disconnect.",
    "H2 static payload/rodata-only hypothesis is reduced in likelihood.",
    "H1 global/static parser initialization remains open.",
    "H3 runtime resolver/reference path remains open.",
    "H4 parser loop/static-init remains open.",
    "H5 RF5/RF6 path interaction remains open only in combination with parser/resolver changes.",
    "H6 latent/unrelated interaction remains open.",
    "Failed activation branch remains abandoned and must not merge.",
)
EXPECTED_RESULT_ROWS = {
    "BOOT-001": ("PASS", "User-reported pass."),
    "BASELINE-001": ("PASS", "User-reported pass."),
    "RF5-001": ("PASS", "No disconnect observed."),
    "RF6-001": ("PASS", "No disconnect observed."),
    "ORDINARY-DIR-001": ("PASS", 'Covered by "everything works".'),
    "NUNCHUK-001": ("NOT_TESTED", "No nunchuk validation claim."),
}
EXPECTED_ALLOWED_PREFIXES = (
    "docs/calibration/",
    "docs/runtime_config/",
    "tools/",
)


class Phase7AD2BHardwareResultError(ValueError):
    """Raised when the D2B hardware-result record is inconsistent."""


def fail(message: str) -> None:
    raise Phase7AD2BHardwareResultError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def git_lines(args: list[str], *, keep_whitespace: bool = False) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    lines = completed.stdout.splitlines()
    if keep_whitespace:
        return [line for line in lines if line.strip()]
    return [line.strip() for line in lines if line.strip()]


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


def require_exact_line(text: str, line: str, label: str) -> None:
    if line not in text.splitlines():
        fail(f"{label} missing required line: {line}")


def require_table_row(text: str, row_id: str, result: str, note_phrase: str) -> None:
    pattern = rf"\|\s*{re.escape(row_id)}\s*\|[^\n]*\|\s*{re.escape(result)}\s*\|[^\n]*"
    if not re.search(pattern, text, flags=re.IGNORECASE):
        fail(f"missing result table row for {row_id} with result {result}")
    if note_phrase not in text:
        fail(f"result table row for {row_id} missing note phrase: {note_phrase}")


def parse_git_status_path(line: str) -> str:
    parts = line.split(None, 1)
    if len(parts) != 2:
        return ""
    path = parts[1]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip()


def git_changed_paths(base_branch: str) -> set[str]:
    changed = set(git_lines(["diff", "--name-only", f"{base_branch}...HEAD"]))
    for status_line in git_lines(["status", "--short"], keep_whitespace=True):
        path = parse_git_status_path(status_line)
        if path:
            changed.add(path)
    return {path for path in changed if path}


def validate_branch_scope() -> None:
    branch = git_lines(["branch", "--show-current"])[0]
    if branch not in ALLOWED_BRANCHES:
        fail(f"unexpected branch: {branch!r}, expected one of {sorted(ALLOWED_BRANCHES)!r}")

    if branch == RESULT_BRANCH:
        changed_paths = git_changed_paths(BASE_BRANCH)
        if not changed_paths:
            fail("no changed paths detected for hardware result branch")

        required_paths = {
            rel(RESULT_MD_PATH),
            rel(RESULT_JSON_PATH),
            rel(INDEX_PATH),
            rel(README_PATH),
            rel(REPO_ROOT / "tools" / "check_glyph_phase7a_diagnostic_d2b_hardware_result.py"),
        }
        missing_required = required_paths - changed_paths
        if missing_required:
            fail("missing expected changed paths: " + ", ".join(sorted(missing_required)))

        for path in sorted(changed_paths):
            if not any(path.startswith(prefix) for prefix in EXPECTED_ALLOWED_PREFIXES):
                fail(f"changed path outside allowed hardware-result scope: {path}")
        return

    status_paths = set(
        filter(None, (parse_git_status_path(line) for line in git_lines(["status", "--short"], keep_whitespace=True)))
    )
    for path in sorted(status_paths):
        if not any(path.startswith(prefix) for prefix in EXPECTED_ALLOWED_PREFIXES):
            fail(f"uncommitted path outside allowed post-merge scope: {path}")


def validate_markdown() -> None:
    text = read_required(RESULT_MD_PATH)
    require_exact_line(text, "status: USER_REPORTED_PASS", "hardware result markdown")
    require_phrase(
        text,
        "Diagnostic branch tested: `phase7a-diagnostic-d2b-retained-payload-bytes`",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "Result branch: `phase7a-diagnostic-d2b-retained-payload-bytes-hardware-result`",
        "hardware result markdown",
    )
    require_phrase(
        text,
        f"Exact user report text: `{EXPECTED_USER_REPORT}`",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "Result source: user-reported",
        "hardware result markdown",
    )
    require_phrase(
        text,
        f"Build command: `{EXPECTED_BUILD_COMMAND}`",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "retained payload bytes alone did not reproduce the RF5/RF6 disconnect",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "H2 static payload/rodata-only hypothesis is reduced in likelihood",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "H1 global/static parser initialization remains open",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "H3 runtime resolver/reference path remains open",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "H4 parser loop/static-init remains open",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "H5 RF5/RF6 path interaction remains open only in combination with parser/resolver changes",
        "hardware result markdown",
    )
    require_phrase(
        text,
        "Failed activation branch remains abandoned and must not merge",
        "hardware result markdown",
    )
    for phrase in (
        "no parser call claim remains source/build-checked, not hardware-observed",
        "no resolver claim remains source/build-checked, not hardware-observed",
        "no storage/write/flashing claim remains source/build-checked, not hardware-observed",
        "result is user-reported",
        "no automated device telemetry",
        "no nunchuk validation",
        "no public release claim",
        "no release compatibility claim",
        "no proof of root cause",
        "no parser safety proven",
        "no resolver safety proven",
    ):
        require_phrase(text, phrase, "hardware result markdown")

    require_table_row(text, "BOOT-001", "PASS", "User-reported pass.")
    require_table_row(text, "BASELINE-001", "PASS", "User-reported pass.")
    require_table_row(text, "RF5-001", "PASS", "No disconnect observed.")
    require_table_row(text, "RF6-001", "PASS", "No disconnect observed.")
    require_table_row(text, "ORDINARY-DIR-001", "PASS", 'Covered by "everything works".')
    require_table_row(text, "NUNCHUK-001", "NOT_TESTED", "No nunchuk validation claim.")


def validate_json() -> None:
    payload = load_json(RESULT_JSON_PATH)
    if payload.get("schema_name") != "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result":
        fail("unexpected schema_name")
    if payload.get("status") != EXPECTED_JSON_STATUS:
        fail("unexpected JSON status")
    if payload.get("diagnostic_branch") != BASE_BRANCH:
        fail("diagnostic_branch mismatch")
    if payload.get("result_branch") != RESULT_BRANCH:
        fail("result_branch mismatch")
    if payload.get("user_report_text") != EXPECTED_USER_REPORT:
        fail("user_report_text mismatch")
    if payload.get("result_source") != EXPECTED_RESULT_SOURCE:
        fail("result_source mismatch")
    if payload.get("result_date_local") != EXPECTED_RESULT_DATE:
        fail("result_date_local mismatch")
    if payload.get("build_command") != EXPECTED_BUILD_COMMAND:
        fail("build_command mismatch")
    if payload.get("build_report_reference") != (
        "docs/runtime_config/phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md"
    ):
        fail("build_report_reference mismatch")
    if payload.get("commit_sha_under_test") != EXPECTED_COMMIT_SHA:
        fail("commit_sha_under_test mismatch")
    if payload.get("hardware_result_recorded") is not True:
        fail("hardware_result_recorded must be true")
    if payload.get("rf5_disconnect_observed") is not False:
        fail("rf5_disconnect_observed must be false")
    if payload.get("rf6_disconnect_observed") is not False:
        fail("rf6_disconnect_observed must be false")
    if payload.get("retained_payload_bytes_tested") is not True:
        fail("retained_payload_bytes_tested must be true")
    if payload.get("parser_called") is not False:
        fail("parser_called must be false")
    if payload.get("global_parse_result_added") is not False:
        fail("global_parse_result_added must be false")
    if payload.get("runtime_resolver_added") is not False:
        fail("runtime_resolver_added must be false")
    if payload.get("ultimate_cpp_changed") is not False:
        fail("ultimate_cpp_changed must be false")
    if payload.get("runtime_behavior_changed_intended") is not False:
        fail("runtime_behavior_changed_intended must be false")
    if payload.get("nunchuk_status") != EXPECTED_NUNCHUK_STATUS:
        fail("nunchuk_status mismatch")
    if payload.get("root_cause_proven") is not False:
        fail("root_cause_proven must be false")
    if payload.get("failed_activation_branch_merge_allowed") is not False:
        fail("failed_activation_branch_merge_allowed must be false")

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

    if set(seen_rows) != set(EXPECTED_RESULT_ROWS):
        fail("result_rows row_id set mismatch")
    for row_id, (expected_result, expected_note) in EXPECTED_RESULT_ROWS.items():
        row = seen_rows[row_id]
        if row.get("result") != expected_result:
            fail(f"result row {row_id} result mismatch")
        if expected_note not in str(row.get("notes", "")):
            fail(f"result row {row_id} notes mismatch")

    source_build_checks = payload.get("source_build_checks_retained")
    if source_build_checks != list(EXPECTED_SOURCE_BUILD_CHECKS):
        fail("source_build_checks_retained mismatch")

    diagnostic_interpretation = payload.get("diagnostic_interpretation")
    if diagnostic_interpretation != list(EXPECTED_DIAGNOSTIC_INTERPRETATION):
        fail("diagnostic_interpretation mismatch")

    hypotheses = payload.get("hypotheses_updated")
    if not isinstance(hypotheses, dict):
        fail("hypotheses_updated must be an object")
    if {k: hypotheses.get(k) for k in EXPECTED_HYPOTHESES} != EXPECTED_HYPOTHESES:
        fail("hypotheses_updated mismatch")

    next_diagnostics = payload.get("next_recommended_diagnostic")
    if next_diagnostics != list(EXPECTED_NEXT_DIAGNOSTICS):
        fail("next_recommended_diagnostic mismatch")

    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, list):
        fail("non_claims must be a list")
    for claim in EXPECTED_NON_CLAIMS:
        if claim not in non_claims:
            fail(f"non_claims missing: {claim}")


def validate_supporting_docs() -> None:
    index_text = read_required(INDEX_PATH)
    require_phrase(
        index_text,
        "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.md",
        "calibration index",
    )
    require_phrase(
        index_text,
        "fixtures/glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.json",
        "calibration index",
    )

    readme_text = read_required(README_PATH)
    require_phrase(
        readme_text,
        "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.md",
        "runtime-config README",
    )
    require_phrase(
        readme_text,
        "reduces payload-only/static rodata suspicion",
        "runtime-config README",
    )
    require_phrase(
        readme_text,
        "Next diagnostics should isolate parser static initialization and resolver path.",
        "runtime-config README",
    )


def main() -> None:
    validate_branch_scope()
    if not RESULT_MD_PATH.exists():
        fail(f"missing hardware result markdown: {rel(RESULT_MD_PATH)}")
    if not RESULT_JSON_PATH.exists():
        fail(f"missing hardware result JSON: {rel(RESULT_JSON_PATH)}")
    validate_markdown()
    validate_json()
    validate_supporting_docs()
    print("Phase 7A Diagnostic D2B hardware-result validation passed.")


if __name__ == "__main__":
    main()
