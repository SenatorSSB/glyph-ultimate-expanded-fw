#!/usr/bin/env python3
"""Validate the parser hot-path postmortem and next-boundary packet.

Read-only. Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-parser-hotpath-postmortem-and-next-boundary"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, MERGED_BRANCH}

DOC_PATH = REPO_ROOT / "docs/runtime_config/parser_hotpath_postmortem_and_next_boundary.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/parser_hotpath_postmortem_and_next_boundary.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
WORKFLOW_PATH = REPO_ROOT / "docs/WORKFLOW.md"
ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"

EXPECTED_GUARDRAIL = "Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver."
HOT_PATH_RESOLVER_CHAIN_GUARDRAIL = "No parser calls in hot path / resolver chain."
REPAIR_BASIS = "Source-owned active-state preselection is the repair architecture baseline."

EXPECTED_DIAGNOSTIC_MATRIX = {
    "D2B_retained_payload_bytes_only": "PASS",
    "D3_global_static_parse_result_only": "PASS",
    "D4_resolver_only": "PASS",
    "D5A_parse_status_gated_source_owned_routing": "FAIL",
    "D5A_N1_direct_source_view_after_parse_gate": "FAIL",
    "D5A_N2_resolver_without_parse_status_read": "PASS",
    "source_owned_active_state_preselection": "HARDWARE_PASS",
}

EXPECTED_CRITICAL_ROWS = {
    "RF5": "PASS_NO_DISCONNECT",
    "RF6": "PASS_NO_DISCONNECT",
    "LT6": "PASS_NO_DISCONNECT",
    "baseline_behavior": "PASS",
    "nunchuk": "NOT_TESTED",
}

EXPECTED_JSON_FIELDS = {
    "status": "design_accepted",
    "postmortem_id": "phase7a_parser_hotpath_failure",
    "accepted_guardrail_id": "runtime_hot_path_no_parser_result_state_read",
    "repair_architecture_baseline": "source_owned_active_state_preselection",
    "repair_architecture_hardware_status": "HARDWARE_PASS",
    "root_cause_mechanism_proven": False,
    "firmware_behavior_changed": False,
    "build_required": False,
}

ALLOWED_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "tools/check_glyph_active_runtime_config_state_contract.py",
    "tools/check_glyph_active_runtime_config_state_source_owned_preselection.py",
    "tools/check_glyph_hot_path_parse_status_guardrail.py",
    "tools/check_glyph_parser_hotpath_postmortem_and_next_boundary.py",
}
ALLOWED_CHANGED_PREFIXES = ("docs/runtime_config/",)
FIRMWARE_SOURCE_PREFIXES = ("src/", "include/", "HAL/", "lib/", "config/")

FORBIDDEN_ULTIMATE_TOKENS = (
    "D2BRetained",
    "RetainedD2B",
    "kPhase7AD2B",
    "retained_d2b",
    "retained_payload",
    "RetainedRuntimeConfigPayload",
    "RuntimeConfigStorage",
    "WebSerial",
    "DeviceWrite",
    "WriteRuntimeConfig",
    "FlashRuntimeConfig",
    "Flashing",
)

FORBIDDEN_DOC_CLAIMS = (
    r"\bruntime-loaded config (?:is |was |has been )?implemented\b",
    r"\bparsed table materialization (?:is |was |has been )?implemented\b",
    r"\bstorage (?:is |was |has been )?implemented\b",
    r"\bWebSerial/device write (?:is |was |has been )?implemented\b",
    r"\bdevice write (?:is |was |has been )?implemented\b",
    r"\bflashing automation (?:is |was |has been )?implemented\b",
    r"\bnunchuk (?:is |was |has been )?(?:tested|validated)\b",
    r"\bnunchuk (?:tested|validated|validation confirmed|hardware validated)\b",
    r"\bproduction release ready\b",
)
NEGATING_CONTEXT = (
    "no ",
    "not ",
    "not yet ",
    "remain not ",
    "remains not ",
    "without ",
    "does not ",
    "must not ",
    "deferred ",
    "remains deferred ",
    "is deferred ",
)


class ParserHotPathPostmortemError(AssertionError):
    """Raised when postmortem artifacts or branch scope drift."""


def fail(message: str) -> None:
    raise ParserHotPathPostmortemError(message)


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


def current_branch() -> str:
    branch = git_lines(["branch", "--show-current"])
    if not branch:
        fail("checker could not determine current branch")
    return branch[0]


def validate_branch(branch: str) -> None:
    if branch not in ALLOWED_BRANCHES:
        fail(f"checker must run on {EXPECTED_BRANCH} or {MERGED_BRANCH}, got {branch}")

    if branch == EXPECTED_BRANCH:
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
            fail(f"postmortem branch must not change firmware/source path: {path}")
        if path in ALLOWED_CHANGED_PATHS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES):
            continue
        fail(f"postmortem branch changed out-of-scope path: {path}")


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


def extract_function(text: str, name: str) -> str:
    pattern = rf"\b{re.escape(name)}\b\s*\([^\)]*\)\s*\{{"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing function: {name}()")

    pos = text.find("{", match.end() - 1)
    if pos == -1:
        fail(f"could not locate opening brace for {name}()")

    pos += 1
    brace = 1
    while pos < len(text):
        if text.startswith("//", pos):
            pos = text.find("\n", pos)
            if pos == -1:
                break
            pos += 1
            continue
        if text.startswith("/*", pos):
            end = text.find("*/", pos + 2)
            if end == -1:
                fail(f"unterminated block comment in {name}()")
            pos = end + 2
            continue
        if text[pos] == "{":
            brace += 1
        elif text[pos] == "}":
            brace -= 1
            if brace == 0:
                return text[match.start() : pos + 1]
        pos += 1

    fail(f"unterminated function body for {name}()")


def reject_patterns_in_body(function_name: str, body: str, patterns: tuple[tuple[str, str], ...]) -> None:
    for pattern, description in patterns:
        if re.search(pattern, body):
            fail(f"{function_name} violates {HOT_PATH_RESOLVER_CHAIN_GUARDRAIL}: {description}")


def validate_function_scope(source: str, function_name: str, patterns: tuple[tuple[str, str], ...]) -> str:
    body = strip_cpp_comments(extract_function(source, function_name))
    reject_patterns_in_body(function_name, body, patterns)
    return body


HOT_PATH_RESOLVER_CHAIN_FORBIDDEN_PATTERNS = (
    (r"\bParseUltimateRuntimeConfigPayload\s*\(", "ParseUltimateRuntimeConfigPayload"),
    (r"\bMaterializeRuntimeConfigCandidateFromParsedPayload\b", "MaterializeRuntimeConfigCandidateFromParsedPayload"),
    (r"\bInitializePublishedRuntimeConfigState\b", "InitializePublishedRuntimeConfigState"),
    (r"\bDecideRuntimeConfigActivation\b", "DecideRuntimeConfigActivation"),
    (r"\bPublishRuntimeConfigState\b", "PublishRuntimeConfigState"),
    (r"\bRuntimeConfigCandidateState\b", "RuntimeConfigCandidateState"),
    (r"\bRuntimeConfigCandidateStatus\b", "RuntimeConfigCandidateStatus"),
    (r"\bkPhase7AD3GlobalParseResult\.status\b", "kPhase7AD3GlobalParseResult.status"),
    (r"\bParseStatus\b", "ParseStatus"),
    (r"\bParse\b", "Parse"),
    (r"\bCandidate\b", "Candidate"),
    (r"\bcandidate\b", "candidate"),
    (r"\bdecision\b", "decision"),
    (r"\bstatus\b", "status"),
    (r"\bload\b", "load"),
    (r"\bstorage\b", "storage"),
    (r"\bwrite\b", "write"),
    (r"\bWebSerial\b", "WebSerial"),
    (r"\bflash\b", "flash"),
    (r"\bsource\b", "source"),
)

GET_ACTIVE_RUNTIME_CONFIG_STATE_FORBIDDEN_PATTERNS = (
    (r"\bParseUltimateRuntimeConfigPayload\s*\(", "ParseUltimateRuntimeConfigPayload"),
    (r"\bMaterializeRuntimeConfigCandidateFromParsedPayload\b", "MaterializeRuntimeConfigCandidateFromParsedPayload"),
    (r"\bInitializePublishedRuntimeConfigState\b", "InitializePublishedRuntimeConfigState"),
    (r"\bDecideRuntimeConfigActivation\b", "DecideRuntimeConfigActivation"),
    (r"\bPublishRuntimeConfigState\b", "PublishRuntimeConfigState"),
    (r"\bRuntimeConfigCandidateState\b", "RuntimeConfigCandidateState"),
    (r"\bRuntimeConfigCandidateStatus\b", "RuntimeConfigCandidateStatus"),
    (r"\bkPhase7AD3GlobalParseResult\.status\b", "kPhase7AD3GlobalParseResult.status"),
    (r"\bParseStatus\b", "ParseStatus"),
    (r"\bParse\b", "Parse"),
    (r"\bCandidate\b", "Candidate"),
    (r"\bcandidate\b", "candidate"),
    (r"\bdecision\b", "decision"),
    (r"\bload\b", "load"),
    (r"\bstorage\b", "storage"),
    (r"\bwrite\b", "write"),
    (r"\bWebSerial\b", "WebSerial"),
    (r"\bflash\b", "flash"),
)


def validate_ultimate_source_guardrail() -> None:
    source = read_required(ULTIMATE_PATH)
    active_source = strip_cpp_comments(source)

    validate_function_scope(source, "UpdateAnalogOutputs", HOT_PATH_RESOLVER_CHAIN_FORBIDDEN_PATTERNS)
    validate_function_scope(source, "ResolveActiveRuntimeConfig", HOT_PATH_RESOLVER_CHAIN_FORBIDDEN_PATTERNS)
    validate_function_scope(source, "GetActiveRuntimeConfigState", GET_ACTIVE_RUNTIME_CONFIG_STATE_FORBIDDEN_PATTERNS)

    for token in FORBIDDEN_ULTIMATE_TOKENS:
        if token in active_source:
            fail(f"Ultimate.cpp active source contains forbidden hot-path/transport token: {token}")


def validate_fixture(payload: dict[str, Any]) -> None:
    if payload.get("accepted_guardrail") != EXPECTED_GUARDRAIL:
        fail("fixture accepted_guardrail mismatch")
    for key, expected in EXPECTED_JSON_FIELDS.items():
        actual = payload.get(key)
        if actual != expected:
            fail(f"fixture {key!r} mismatch: expected {expected!r}, got {actual!r}")

    if payload.get("diagnostic_matrix") != EXPECTED_DIAGNOSTIC_MATRIX:
        fail("fixture diagnostic_matrix mismatch")
    if payload.get("critical_rows") != EXPECTED_CRITICAL_ROWS:
        fail("fixture critical_rows mismatch")

    next_boundary = payload.get("next_boundary")
    if not isinstance(next_boundary, dict):
        fail("fixture next_boundary must be an object")
    output_allowed = next_boundary.get("output_phase_allowed")
    if output_allowed != ["stable selected RuntimeConfigView via active_view"]:
        fail("fixture output_phase_allowed must allow only stable selected active_view")
    for forbidden in (
        "parser result state",
        "candidate parsed payload state",
        "CRC state",
        "load status",
        "storage status",
        "write status",
        "activation source",
        "activation status",
    ):
        if forbidden not in next_boundary.get("output_phase_forbidden", []):
            fail(f"fixture output_phase_forbidden missing: {forbidden}")


def validate_docs(doc: str, readme: str, current_state: str, roadmap: str, workflow: str) -> None:
    for phrase in (
        "status: DESIGN_ACCEPTED",
        "title: Parser Hot-Path Postmortem and Next Boundary",
        "This branch is docs/tools-only and changes no firmware behavior.",
        "D2B retained payload bytes only",
        "D3 global/static parse result only",
        "D4 resolver only",
        "D5A parse-status-gated source-owned routing",
        "D5A-N1 direct source-owned view after parse-status gate",
        "D5A-N2 resolver without parse-status hot-path read",
        "source-owned active runtime config state preselection",
        EXPECTED_GUARDRAIL,
        "HARDWARE_PASS",
        "RF5 did not disconnect",
        "RF6 did not disconnect",
        "LT6 did not disconnect",
        "baseline behavior remained intact",
        "nunchuk remains NOT_TESTED",
        REPAIR_BASIS,
        "parser/materialization/load may happen only before active-state publication",
        "output generation may consume only the already-selected RuntimeConfigView",
        "no parser status, CRC status, load status, storage status, write status",
        "pre-hot-path active-state publication scaffold",
        "parsed-payload materialization only into a candidate state, not into hot path",
        "activation validation outside the analog hot path",
        "true parsed table materialization remains deferred until a separate approved branch",
        "runtime-loaded config remains deferred",
        "storage remains deferred",
        "WebSerial/device write remains deferred",
        "flashing automation remains deferred",
        "nunchuk validation remains deferred",
        "do not reintroduce kPhase7AD3GlobalParseResult.status into ResolveActiveRuntimeConfig",
        "do not branch on parser status from UpdateAnalogOutputs",
        "do not materialize parsed tables directly in the analog hot path",
        "do not add storage/write/flashing/WebSerial paths under parser/materialization work",
        "do not claim runtime-loaded config before storage/load/activation is implemented and tested",
        "low-level failure mechanism remains unproven",
    ):
        require_phrase(doc, phrase, "postmortem doc")

    for filename in (
        "parser_hotpath_postmortem_and_next_boundary.md",
        "fixtures/parser_hotpath_postmortem_and_next_boundary.json",
    ):
        require_phrase(readme, filename, "runtime config README")

    require_phrase(current_state, "Parser hot-path postmortem / next-boundary state is accepted", "CURRENT_STATE")
    require_phrase(current_state, REPAIR_BASIS, "CURRENT_STATE")
    require_phrase(roadmap, "Accepted next boundary", "ROADMAP")
    require_phrase(roadmap, REPAIR_BASIS, "ROADMAP")
    require_phrase(workflow, "Parser/materialization/load work belongs before active-state publication", "WORKFLOW")


def has_negating_context(text: str, start: int) -> bool:
    window = text[max(0, start - 48) : start].lower()
    return any(marker in window for marker in NEGATING_CONTEXT)


def validate_no_unsupported_claims() -> None:
    for path in (DOC_PATH, README_PATH, CURRENT_STATE_PATH, ROADMAP_PATH, WORKFLOW_PATH):
        text = read_required(path)
        lowered = text.lower()
        for pattern in FORBIDDEN_DOC_CLAIMS:
            for match in re.finditer(pattern, lowered, flags=re.IGNORECASE):
                if has_negating_context(lowered, match.start()):
                    continue
                fail(f"unsupported claim in {rel(path)}: {match.group(0)!r}")


def main() -> int:
    branch = current_branch()
    validate_branch(branch)
    if branch == EXPECTED_BRANCH:
        validate_changed_paths(changed_paths())

    doc = read_required(DOC_PATH)
    readme = read_required(README_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)
    workflow = read_required(WORKFLOW_PATH)
    payload = load_json_object(FIXTURE_PATH)

    validate_fixture(payload)
    validate_docs(doc, readme, current_state, roadmap, workflow)
    validate_ultimate_source_guardrail()
    validate_no_unsupported_claims()

    print("parser hot-path postmortem and next-boundary checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
