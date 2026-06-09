#!/usr/bin/env python3
"""Validate the Phase 7A runtime hot-path parse-status guardrail.

Read-only. Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase7a-runtime-hot-path-parse-status-guardrail"
BASE_BRANCH = "configurator"

DOC_PATH = REPO_ROOT / "docs/runtime_config/hot_path_parse_status_guardrail.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/hot_path_parse_status_guardrail.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
WORKFLOW_PATH = REPO_ROOT / "docs/WORKFLOW.md"
ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"

EXPECTED_INVARIANT = "Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver."
EXPECTED_EVIDENCE = {
    "D2B_retained_payload_bytes_only": "pass",
    "D3_global_static_parse_result_only": "pass",
    "D4_resolver_only": "pass",
    "D5A_parse_status_gated_source_owned_routing": "fail",
    "D5A_N1_direct_source_view_after_parse_gate": "fail",
    "D5A_N2_resolver_without_parse_status_read": "pass",
}

ALLOWED_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "tools/check_glyph_hot_path_parse_status_guardrail.py",
}
ALLOWED_CHANGED_PREFIXES = ("docs/runtime_config/",)
FIRMWARE_SOURCE_PREFIXES = ("src/", "include/", "HAL/", "lib/", "config/")

FORBIDDEN_DOC_CLAIMS = (
    r"\broot cause mechanism (?:is |was |has been )?proven\b",
    r"\bstorage (?:is |was |has been )?implemented\b",
    r"\bWebSerial/device write (?:is |was |has been )?implemented\b",
    r"\bdevice write (?:is |was |has been )?implemented\b",
    r"\bflashing automation (?:is |was |has been )?implemented\b",
    r"\bparsed table materialization (?:is |was |has been )?implemented\b",
    r"\bnunchuk (?:tested|validated|validation confirmed|hardware validated)\b",
    r"\bproduction release ready\b",
    r"\bpublic release (?:ready|approved|complete)\b",
)
NEGATING_CONTEXT = ("no ", "not ", "not yet ", "remain not ", "remains not ", "without ")


class HotPathParseStatusGuardrailError(AssertionError):
    """Raised when the guardrail artifacts or branch scope drift."""


def fail(message: str) -> None:
    raise HotPathParseStatusGuardrailError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def no_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key in fixture: {key}")
        result[key] = value
    return result


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=no_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must contain a JSON object")
    return payload


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


def validate_branch() -> None:
    branch = git_lines(["branch", "--show-current"])
    if not branch or branch[0] != EXPECTED_BRANCH:
        actual = branch[0] if branch else "<detached>"
        fail(f"checker must run on {EXPECTED_BRANCH}, got {actual}")

    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")


def changed_paths() -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status=True):
        path = status_line[3:].strip()
        if not path:
            continue
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path.startswith(FIRMWARE_SOURCE_PREFIXES):
            fail(f"guardrail branch must not change firmware/source path: {path}")
        if path in ALLOWED_CHANGED_PATHS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES):
            continue
        fail(f"guardrail branch changed out-of-scope path: {path}")


def strip_cpp_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    in_block = False
    while index < len(text):
        if in_block:
            if text.startswith("*/", index):
                in_block = False
                index += 2
            else:
                if text[index] == "\n":
                    result.append("\n")
                index += 1
            continue
        if text.startswith("/*", index):
            in_block = True
            index += 2
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index)
            if newline == -1:
                break
            result.append("\n")
            index = newline + 1
            continue
        result.append(text[index])
        index += 1
    return "".join(result)


def validate_ultimate_source_guardrail() -> None:
    active_source = strip_cpp_comments(read_required(ULTIMATE_PATH))
    unsafe_symbols = (
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "kPhase7AD3GlobalParseResult.status",
    )
    if all(symbol in active_source for symbol in unsafe_symbols):
        fail(
            "Ultimate.cpp contains the unsafe active hot-path pattern: "
            "UpdateAnalogOutputs -> ResolveActiveRuntimeConfig -> kPhase7AD3GlobalParseResult.status"
        )
    if "kPhase7AD3GlobalParseResult.status" in active_source:
        fail("Ultimate.cpp must not read kPhase7AD3GlobalParseResult.status outside comments")


def validate_fixture(payload: dict[str, Any]) -> None:
    expected_values = {
        "status": "accepted_guardrail",
        "guardrail_id": "runtime_hot_path_no_parser_result_state_read",
        "root_cause_mechanism_proven": False,
        "failed_activation_branch_merge_allowed": False,
        "required_invariant": EXPECTED_INVARIANT,
    }
    for key, expected in expected_values.items():
        actual = payload.get(key)
        if actual != expected:
            fail(f"fixture {key!r} mismatch: expected {expected!r}, got {actual!r}")

    evidence = payload.get("evidence")
    if evidence != EXPECTED_EVIDENCE:
        fail(f"fixture evidence mismatch: expected {EXPECTED_EVIDENCE!r}, got {evidence!r}")


def validate_docs(doc: str, readme: str, current_state: str) -> None:
    for phrase in (
        "status: ACCEPTED_GUARDRAIL",
        "Runtime Hot-Path Parse-Status Guardrail",
        "UpdateAnalogOutputs(...) -> ResolveActiveRuntimeConfig() -> kPhase7AD3GlobalParseResult.status",
        EXPECTED_INVARIANT,
        "low-level mechanism is not proven",
        "production repair must avoid parser-status reads in the analog hot path",
        "True parsed table materialization remains deferred",
        "Runtime-loaded config, storage, WebSerial/device write, and flashing remain not implemented",
        "failed activation branch remains abandoned and must not merge",
        "activation phase computes stable active runtime config state outside the hot path",
        "analog output phase consumes only the stable selected view",
        "no storage",
        "no WebSerial/device write",
        "no flashing automation",
        "no parsed table materialization in this branch",
        "no firmware behavior change in this branch",
        "no public release claim",
        "no nunchuk validation claim",
    ):
        require_phrase(doc, phrase, "guardrail doc")

    for diagnostic, result in (
        ("D2B", "PASS"),
        ("D3", "PASS"),
        ("D4", "PASS"),
        ("D5A", "FAIL"),
        ("D5A-N1", "FAIL"),
        ("D5A-N2", "PASS"),
    ):
        require_phrase(doc, diagnostic, "guardrail doc")
        require_phrase(doc, result, "guardrail doc")

    require_phrase(readme, "hot_path_parse_status_guardrail.md", "runtime_config README")
    require_phrase(readme, "fixtures/hot_path_parse_status_guardrail.json", "runtime_config README")
    require_phrase(current_state, "Phase 7A hot-path parse-status guardrail is accepted", "CURRENT_STATE")
    require_phrase(current_state, EXPECTED_INVARIANT, "CURRENT_STATE")


def validate_no_forbidden_doc_claims() -> None:
    docs_to_scan = (
        DOC_PATH,
        README_PATH,
        CURRENT_STATE_PATH,
        ROADMAP_PATH,
        WORKFLOW_PATH,
    )
    for path in docs_to_scan:
        text = read_required(path)
        for pattern in FORBIDDEN_DOC_CLAIMS:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                prefix = text[max(0, match.start() - 80) : match.start()].lower()
                if any(negation in prefix for negation in NEGATING_CONTEXT):
                    continue
                fail(f"{rel(path)} contains forbidden claim matching: {pattern}")


def main() -> int:
    validate_branch()
    paths = changed_paths()
    validate_changed_paths(paths)

    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    readme = read_required(README_PATH)
    current_state = read_required(CURRENT_STATE_PATH)

    validate_docs(doc, readme, current_state)
    validate_fixture(fixture)
    validate_ultimate_source_guardrail()
    validate_no_forbidden_doc_claims()

    print("glyph_hot_path_parse_status_guardrail: PASS")
    print(f"- {rel(DOC_PATH)}")
    print(f"- {rel(FIXTURE_PATH)}")
    print("runtime_hot_path_no_parser_result_state_read=true")
    print("firmware_source_changed=false")
    print("root_cause_mechanism_proven=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
