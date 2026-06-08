#!/usr/bin/env python3
"""Validate Phase 7A activation failure root-cause analysis artifacts.

Read-only. Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/runtime_config/phase7a_activation_failure_root_cause_analysis_2026-06-09.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/phase7a_activation_failure_root_cause_analysis_2026-06-09.json"
MATRIX_PATH = REPO_ROOT / "docs/runtime_config/phase7a_activation_failure_diagnostic_build_matrix.md"

EXPECTED_STATUS_DOC = "ROOT_CAUSE_ANALYSIS_ONLY_NO_FIX_IMPLEMENTED"
EXPECTED_STATUS_JSON = "root_cause_analysis_only_no_fix_implemented"
EXPECTED_SCHEMA_NAME = "glyph_phase7a_activation_failure_root_cause_analysis"
EXPECTED_FAILED_BRANCH = "phase7a-runtime-config-compiled-payload-activation"
EXPECTED_FAILURE_RESULT_BRANCH = "phase7a-runtime-config-compiled-payload-activation-hardware-failure"
EXPECTED_KNOWN_GOOD_BRANCH = "configurator"
EXPECTED_BASELINE_BRANCH = "phase7a-build-size-and-map-baseline"
EXPECTED_FAILURE_REPORT = (
    "I dont know what happened after tests, but I was wrong. Some inputs completely cut the connection "
    "from the controller. At least pressing rf5 or rf6 disconnect it according to the game console"
)
EXPECTED_RECOVERY_REPORT = "i restored the previous fw, which works fine still"

ALLOWED_CHANGED_PREFIXES = ("docs/", "tools/")
FORBIDDEN_CHANGED_PREFIXES = ("src/", "include/", "HAL/", "lib/", "config/")
REQUIRED_HYPOTHESES = {"H1", "H2", "H3", "H4", "H5", "H6"}
REQUIRED_DIAGNOSTICS = {"D0", "D1", "D2", "D3", "D4", "D5", "D6"}
ALLOWED_CONFIDENCE = {
    "source-backed-high",
    "source-backed-medium",
    "plausible-low",
    "unknown",
}

FORBIDDEN_CLAIM_PATTERNS = (
    r"\bstatus:\s*(?:HARDWARE_PASS|USER_REPORTED_PASS)\b",
    r'"hardware_pass"\s*:\s*true',
    r"(?<!claim )\bhardware pass(?:ed)?\b(?![- ]claim)",
    r"\bnunchuk (?:validated|validation confirmed|hardware validated)\b",
    r"(?<!no )\bruntime-loaded config (?:is |was |has been )?implemented\b",
    r"(?<!no )\bruntime-config storage (?:is |was |has been )?implemented\b",
    r"(?<!no )\bWebSerial/device write (?:is |was |has been )?implemented\b",
    r"(?<!/)(?<!no )\bdevice write (?:is |was |has been )?implemented\b",
    r"(?<!no )\bfirmware flashing automation (?:is |was |has been )?implemented\b",
    r"(?<!firmware )(?<!no )\bflashing automation (?:is |was |has been )?implemented\b",
    r"\broot cause (?:is|was|proven):\s*(?!not proven|unknown)",
    r"\bdefinite low-level (?:crash cause|disconnect cause|cause)\b",
    r"\bcaused by (?:USB|usb|watchdog|panic|assert|reboot|stack|heap)\b",
)


class RootCauseAnalysisError(AssertionError):
    """Raised when the analysis packet violates guardrails."""


def fail(message: str) -> None:
    raise RootCauseAnalysisError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def require_no_forbidden_claims(text: str, label: str) -> None:
    lowered = text.lower()
    for pattern in FORBIDDEN_CLAIM_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            fail(f"{label} contains forbidden claim matching: {pattern}")


def require_json_value(payload: dict[str, Any], key: str, expected: Any) -> None:
    actual = payload.get(key)
    if actual != expected:
        fail(f"fixture {key!r} mismatch: expected {expected!r}, got {actual!r}")


def git_lines(args: list[str], *, preserve_status: bool = False) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    if preserve_status:
        return [line for line in completed.stdout.splitlines() if line.strip()]
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def validate_no_firmware_source_changed() -> None:
    changed: set[str] = set(git_lines(["diff", "--name-only", f"{EXPECTED_KNOWN_GOOD_BRANCH}...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status=True):
        parts = status_line.strip().split(maxsplit=1)
        if len(parts) == 2:
            changed.add(parts[1])

    for path in sorted(changed):
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES):
            fail(f"analysis branch must not change firmware/source path: {path}")
        if not path.startswith(ALLOWED_CHANGED_PREFIXES):
            fail(f"analysis branch changed non-docs/tools path: {path}")


def validate_doc(text: str) -> None:
    required_phrases = (
        f"status: {EXPECTED_STATUS_DOC}",
        EXPECTED_FAILED_BRANCH,
        EXPECTED_FAILURE_RESULT_BRANCH,
        EXPECTED_BASELINE_BRANCH,
        EXPECTED_FAILURE_REPORT,
        EXPECTED_RECOVERY_REPORT,
        "No required ref was missing.",
        "src/modes/Ultimate.cpp",
        "src/modes/UltimateRuntimeConfigParser.hpp",
        "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
        "global non-`constexpr` parse result",
        "parser call during static initialization",
        "ResolveActiveRuntimeConfig",
        "RF5",
        "RF6",
        "Root cause is not proven.",
        "failed activation branch must remain abandoned",
        "controlled diagnostic builds",
        "No fix is implemented on this branch.",
        "No hardware-pass claim is made.",
        "No nunchuk-validation claim is made.",
    )
    for phrase in required_phrases:
        require_phrase(text, phrase, "analysis doc")

    for hypothesis_id in REQUIRED_HYPOTHESES:
        require_phrase(text, f"{hypothesis_id}.", "analysis doc")

    require_no_forbidden_claims(text, "analysis doc")


def validate_fixture(payload: dict[str, Any]) -> None:
    require_json_value(payload, "schema_name", EXPECTED_SCHEMA_NAME)
    require_json_value(payload, "status", EXPECTED_STATUS_JSON)
    require_json_value(payload, "failed_branch", EXPECTED_FAILED_BRANCH)
    require_json_value(payload, "failure_result_branch", EXPECTED_FAILURE_RESULT_BRANCH)
    require_json_value(payload, "known_good_branch", EXPECTED_KNOWN_GOOD_BRANCH)
    require_json_value(payload, "failure_report_text", EXPECTED_FAILURE_REPORT)
    require_json_value(payload, "recovery_report_text", EXPECTED_RECOVERY_REPORT)
    require_json_value(payload, "root_cause_proven", False)
    require_json_value(payload, "failed_branch_merge_allowed", False)
    require_json_value(payload, "future_runtime_activation_requires_hardware", True)

    changed = payload.get("changed_files_in_failed_branch")
    if changed != [
        "src/modes/Ultimate.cpp",
        "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
        "src/modes/UltimateRuntimeConfigParser.hpp",
    ]:
        fail("fixture changed_files_in_failed_branch mismatch")

    refs = payload.get("refs_inspected")
    if not isinstance(refs, list) or len(refs) < 6:
        fail("fixture refs_inspected must include all required refs")
    missing = [item for item in refs if isinstance(item, dict) and item.get("available") is not True]
    if missing:
        fail(f"fixture records missing refs unexpectedly: {missing!r}")

    hypotheses = payload.get("hypotheses")
    if not isinstance(hypotheses, list):
        fail("fixture hypotheses must be a list")
    seen: set[str] = set()
    for item in hypotheses:
        if not isinstance(item, dict):
            fail("each hypothesis must be an object")
        hypothesis_id = item.get("id")
        if not isinstance(hypothesis_id, str):
            fail("each hypothesis must include string id")
        seen.add(hypothesis_id)
        confidence = item.get("confidence")
        if confidence not in ALLOWED_CONFIDENCE:
            fail(f"{hypothesis_id} confidence invalid: {confidence!r}")
        for key in ("title", "next_diagnostic"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                fail(f"{hypothesis_id} missing non-empty {key}")
        for key in ("evidence_for", "evidence_against"):
            value = item.get(key)
            if not isinstance(value, list) or not value or not all(isinstance(entry, str) for entry in value):
                fail(f"{hypothesis_id} {key} must be a non-empty string list")
    if seen != REQUIRED_HYPOTHESES:
        fail(f"fixture hypothesis IDs mismatch: expected {sorted(REQUIRED_HYPOTHESES)}, got {sorted(seen)}")

    non_claims = " ".join(str(item).lower() for item in payload.get("non_claims", []))
    for required in (
        "no fix implemented",
        "no firmware source changed",
        "no hardware pass claimed",
        "no nunchuk validation claimed",
        "no runtime-loaded config implemented",
        "no runtime-config storage implemented",
        "no webserial/device write implemented",
        "no firmware flashing automation implemented",
        "no definite low-level crash cause claimed",
    ):
        if required not in non_claims:
            fail(f"fixture non_claims missing: {required}")


def validate_matrix(text: str) -> None:
    require_phrase(text, "status: DIAGNOSTIC_PLAN_ONLY_NOT_IMPLEMENTED", "diagnostic matrix")
    require_phrase(text, "diagnostic branches are not merge candidates into `configurator`", "diagnostic matrix")
    require_phrase(text, "nunchuk status: `NOT_TESTED` unless explicitly tested", "diagnostic matrix")
    for diagnostic_id in REQUIRED_DIAGNOSTICS:
        require_phrase(text, diagnostic_id, "diagnostic matrix")
    for phrase in (
        "No diagnostic build is implemented by this plan.",
        "No firmware fix is implemented.",
        "No hardware-pass claim is made.",
        "No nunchuk-validation claim is made.",
        "No runtime-loaded config is implemented.",
        "No runtime-config storage is implemented.",
        "No WebSerial/device write is implemented.",
        "No firmware flashing automation is implemented.",
    ):
        require_phrase(text, phrase, "diagnostic matrix")
    require_no_forbidden_claims(text, "diagnostic matrix")


def main() -> int:
    doc_text = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    matrix_text = read_required(MATRIX_PATH)

    validate_doc(doc_text)
    validate_fixture(fixture)
    validate_matrix(matrix_text)
    validate_no_firmware_source_changed()

    print("glyph_phase7a_activation_failure_root_cause_analysis: PASS")
    print(f"- {rel(DOC_PATH)}")
    print(f"- {rel(FIXTURE_PATH)}")
    print(f"- {rel(MATRIX_PATH)}")
    print("root_cause_proven=false")
    print("failed_branch_merge_allowed=false")
    print("future_runtime_activation_requires_hardware=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
