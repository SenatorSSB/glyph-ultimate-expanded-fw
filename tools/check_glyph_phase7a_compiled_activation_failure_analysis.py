#!/usr/bin/env python3
"""Validate the Phase 7A compiled activation failure analysis packet.

Read-only. Uses only the Python standard library. This checker validates the
analysis boundary and scans the current branch diff for forbidden firmware
source edits.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "phase7a_compiled_activation_failure_analysis_2026-06-08.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "fixtures"
    / "phase7a_compiled_activation_failure_analysis_2026-06-08.json"
)
REPAIR_PLAN_PATH = REPO_ROOT / "docs" / "runtime_config" / "phase7a_safer_activation_repair_plan.md"

EXPECTED_STATUS_DOC = "FAILURE_ANALYSIS_ONLY_NO_FIX_IMPLEMENTED"
EXPECTED_STATUS_JSON = "failure_analysis_only_no_fix_implemented"
EXPECTED_SCHEMA_NAME = "glyph_phase7a_compiled_activation_failure_analysis"
EXPECTED_FAILED_BRANCH = "phase7a-runtime-config-compiled-payload-activation"
EXPECTED_FAILURE_RESULT_BRANCH = "phase7a-runtime-config-compiled-payload-activation-hardware-failure"
EXPECTED_BASELINE_BRANCH = "configurator"
EXPECTED_NEXT_BRANCH = "phase7a-runtime-config-activation-repair-minimal"
EXPECTED_FAILURE_REPORT = (
    "I dont know what happened after tests, but I was wrong. Some inputs completely cut the connection "
    "from the controller. At least pressing rf5 or rf6 disconnect it according to the game console"
)
EXPECTED_RECOVERY_REPORT = "i restored the previous fw, which works fine still"

ALLOWED_BRANCH_PREFIXES = (
    "docs/",
    "tools/",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "src/",
    "include/",
    "lib/",
    "config/",
    "HAL/",
)
FORBIDDEN_POSITIVE_PATTERNS = (
    r"\bstatus:\s*(HARDWARE_PASS|PASS|USER_REPORTED_PASS)\b",
    r'"hardware_pass"\s*:\s*true',
    r'"hardware_result"\s*:\s*"(?:pass|hardware_pass|user_reported_pass)"',
    r"\bhardware result:\s*(?:PASS|HARDWARE_PASS|USER_REPORTED_PASS)\b",
    r"\bnunchuk (?:validated|validation confirmed|hardware validated)\b",
    r"\bruntime-loaded config storage (?:is now |was successfully |has been )implemented\b",
    r"\bruntime-config storage (?:is now |was successfully |has been )implemented\b",
    r"\bimplemented runtime-config storage\b",
    r"\bWebSerial/device write (?:is now |was successfully |has been )implemented\b",
    r"\bdevice write (?:is now |was successfully |has been )implemented\b",
    r"\bimplemented device write\b",
    r"\bfirmware flashing automation (?:is now |was successfully |has been )implemented\b",
    r"\bimplemented firmware flashing automation\b",
    r"\bofficial configurator compatibility (?:is now |was successfully |has been )claimed\b",
    r"\broot cause:\s*(?!unknown\b)",
    r"\bdefinite low-level (?:cause|crash cause)\b",
    r"\bcaused by (?:stack|heap|watchdog|USB|usb|memory|parser)\b",
)
REQUIRED_DOC_PHRASES = (
    "status: FAILURE_ANALYSIS_ONLY_NO_FIX_IMPLEMENTED",
    f"failed branch:\n  `{EXPECTED_FAILED_BRANCH}`",
    f"failure result branch:\n  `{EXPECTED_FAILURE_RESULT_BRANCH}`",
    EXPECTED_FAILURE_REPORT,
    EXPECTED_RECOVERY_REPORT,
    "tested baseline status: configurator restored and works fine",
    "compiled payload header added",
    "global parse result added",
    "ResolveActiveRuntimeConfig",
    "runtime path now depends on the compiled payload parse result",
    "payload-backed lookup was deferred",
    "runtime still uses the source-owned current baseline view",
    "RF5 is source-confirmed as a forced-Up and direction-plus-A path",
    "RF6 is source-confirmed as a z-airdodge / low-magnitude override path",
    "Global/static initialization or const parse-result memory/runtime interaction",
    "Static memory/layout pressure from the 530-byte compiled payload or parser code",
    "Activation boundary changed lifetime/reference behavior",
    "Parser validation path triggered unexpected embedded-runtime behavior",
    "Unrelated but activation-branch-specific interaction",
    "Abandon the failed activation branch",
    "Do not continue implementation directly from it",
    "Avoid a global non-`constexpr` parse result if possible",
    "hardware gate before merge",
    "No fix is implemented on this branch",
)
REQUIRED_REPAIR_PHRASES = (
    "status: REPAIR_PLAN_ONLY_NOT_IMPLEMENTED",
    EXPECTED_NEXT_BRANCH,
    "no global runtime `ParseResult` object unless proven safe",
    "keep the parser scaffold compiled",
    "use build-time/generated equivalence checks as much as possible",
    "wrap it in an explicit local function",
    "no storage/write/WebSerial/flashing",
    "hardware result before merge",
)


class FailureAnalysisError(ValueError):
    """Raised when the failure analysis guardrails drift."""


def fail(message: str) -> None:
    raise FailureAnalysisError(message)


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


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def require_no_forbidden_claims(text: str, label: str) -> None:
    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"{label} contains forbidden positive/diagnostic claim: {pattern}")


def require_json_value(payload: dict[str, Any], key: str, expected: Any) -> None:
    actual = payload.get(key)
    if actual != expected:
        fail(f"fixture {key!r} mismatch: expected {expected!r}, got {actual!r}")


def require_list_contains(payload: dict[str, Any], key: str, expected: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or expected not in value:
        fail(f"fixture {key!r} must include {expected!r}")


def validate_hypotheses(payload: dict[str, Any]) -> None:
    hypotheses = payload.get("hypotheses")
    if not isinstance(hypotheses, list) or len(hypotheses) < 5:
        fail("fixture must contain at least five hypotheses")

    expected_ids = {"H1", "H2", "H3", "H4", "H5"}
    seen_ids: set[str] = set()
    for item in hypotheses:
        if not isinstance(item, dict):
            fail("each hypothesis must be an object")
        hypothesis_id = item.get("id")
        if not isinstance(hypothesis_id, str):
            fail("each hypothesis must include string id")
        seen_ids.add(hypothesis_id)
        if item.get("confidence") not in {"low", "medium"}:
            fail(f"{hypothesis_id} confidence must remain low/medium for failure analysis")
        if item.get("classification") not in {"plausible_but_unproven", "unknown"}:
            fail(f"{hypothesis_id} classification overclaims beyond available evidence")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            fail(f"{hypothesis_id} must include evidence")
        if not isinstance(item.get("proposed_next_check"), str) or not item["proposed_next_check"]:
            fail(f"{hypothesis_id} must include proposed_next_check")

    if not expected_ids.issubset(seen_ids):
        fail(f"fixture missing expected hypotheses: {sorted(expected_ids - seen_ids)}")


def git_lines(args: list[str], *, preserve_status_prefix: bool = False) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    if preserve_status_prefix:
        return [line for line in completed.stdout.splitlines() if line.strip()]
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def validate_no_firmware_source_changed() -> None:
    changed = set(git_lines(["diff", "--name-only", f"{EXPECTED_BASELINE_BRANCH}...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status_prefix=True):
        status_line = status_line.strip()
        if not status_line:
            continue
        parts = status_line.split(maxsplit=1)
        if len(parts) < 2:
            continue
        path = parts[1].strip()
        if path:
            changed.add(path)

    for path in sorted(changed):
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES):
            fail(f"analysis branch must not change firmware/source path: {path}")
        if not path.startswith(ALLOWED_BRANCH_PREFIXES):
            fail(f"analysis branch changed non-docs/tools path: {path}")


def validate_doc(text: str) -> None:
    for phrase in REQUIRED_DOC_PHRASES:
        require_phrase(text, phrase, "analysis doc")
    require_no_forbidden_claims(text, "analysis doc")
    if "unknown" not in normalize(text):
        fail("analysis doc must state that the low-level cause is unknown")


def validate_repair_plan(text: str) -> None:
    for phrase in REQUIRED_REPAIR_PHRASES:
        require_phrase(text, phrase, "repair plan")
    require_no_forbidden_claims(text, "repair plan")


def validate_fixture(payload: dict[str, Any]) -> None:
    require_json_value(payload, "schema_name", EXPECTED_SCHEMA_NAME)
    require_json_value(payload, "status", EXPECTED_STATUS_JSON)
    require_json_value(payload, "failed_branch", EXPECTED_FAILED_BRANCH)
    require_json_value(payload, "failure_result_branch", EXPECTED_FAILURE_RESULT_BRANCH)
    require_json_value(payload, "baseline_branch", EXPECTED_BASELINE_BRANCH)
    require_json_value(payload, "failure_report_text", EXPECTED_FAILURE_REPORT)
    require_json_value(payload, "recovery_report_text", EXPECTED_RECOVERY_REPORT)
    require_json_value(payload, "merge_allowed", False)
    require_json_value(payload, "recommended_next_branch", EXPECTED_NEXT_BRANCH)
    validate_hypotheses(payload)

    require_list_contains(payload, "caveats", "exact low-level disconnect cause unknown")
    require_list_contains(payload, "caveats", "analysis branch implements no fix")
    require_list_contains(payload, "caveats", "future runtime activation requires hardware gate")
    require_list_contains(payload, "non_claims", "no hardware pass")
    require_list_contains(payload, "non_claims", "no nunchuk validation")
    require_list_contains(payload, "non_claims", "no runtime-loaded config storage")
    require_list_contains(payload, "non_claims", "no WebSerial/device write")
    require_list_contains(payload, "non_claims", "no firmware flashing automation")
    require_list_contains(payload, "non_claims", "no definite low-level crash cause")


def main() -> int:
    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    repair_plan = read_required(REPAIR_PLAN_PATH)

    validate_doc(doc)
    validate_fixture(fixture)
    validate_repair_plan(repair_plan)
    validate_no_firmware_source_changed()

    print("status=PASS")
    print(f"analysis_doc={display(DOC_PATH)}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"repair_plan={display(REPAIR_PLAN_PATH)}")
    print("firmware_source_changed=false")
    print("fix_implemented=false")
    print("hardware_gate_required=true")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FailureAnalysisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
