#!/usr/bin/env python3
"""Validate the active runtime config state contract.

Read-only. Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-active-config-state-contract"
MERGED_BRANCH = "configurator"
CONSOLIDATION_BRANCH = "runtime-config-parser-hotpath-postmortem-and-next-boundary"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, MERGED_BRANCH, CONSOLIDATION_BRANCH}

DOC_PATH = REPO_ROOT / "docs/runtime_config/active_runtime_config_state_contract.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/active_runtime_config_state_contract.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
WORKFLOW_PATH = REPO_ROOT / "docs/WORKFLOW.md"
ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"

EXPECTED_INVARIANT = "Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver."
ACTIVE_VIEW_INVARIANT = "Analog output generation may consume only ActiveRuntimeConfigState.active_view."
NO_SOURCE_STATUS_BRANCH_INVARIANT = (
    "Analog output generation must not branch on ActiveRuntimeConfigState.source or ActiveRuntimeConfigState.status."
)

ALLOWED_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "tools/check_glyph_active_runtime_config_state_contract.py",
}
ALLOWED_CHANGED_PREFIXES = ("docs/runtime_config/",)
FIRMWARE_SOURCE_PREFIXES = ("src/", "include/", "HAL/", "lib/", "config/")

FORBIDDEN_DOC_CLAIMS = (
    r"\bfirmware behavior changed\b",
    r"\bparsed table materialization (?:is |was |has been )?implemented\b",
    r"\bruntime-loaded config (?:is |was |has been )?implemented\b",
    r"\bstorage (?:is |was |has been )?implemented\b",
    r"\bWebSerial/device write (?:is |was |has been )?implemented\b",
    r"\bdevice write (?:is |was |has been )?implemented\b",
    r"\bflashing automation (?:is |was |has been )?implemented\b",
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
)


class ActiveRuntimeConfigStateContractError(AssertionError):
    """Raised when the active runtime config contract drifts."""


def fail(message: str) -> None:
    raise ActiveRuntimeConfigStateContractError(message)


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
        fail(f"checker must run on {', '.join(sorted(ALLOWED_BRANCHES))}, got {branch}")

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
            fail(f"contract branch must not change firmware/source path: {path}")
        if path in ALLOWED_CHANGED_PATHS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES):
            continue
        fail(f"contract branch changed out-of-scope path: {path}")


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
    if "kPhase7AD3GlobalParseResult.status" in active_source:
        fail("Ultimate.cpp must not read kPhase7AD3GlobalParseResult.status outside comments")

    unsafe_symbols = (
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "kPhase7AD3GlobalParseResult.status",
    )
    if all(symbol in active_source for symbol in unsafe_symbols):
        fail(
            "Ultimate.cpp contains the unsafe active hot-path pattern: "
            "UpdateAnalogOutputs, ResolveActiveRuntimeConfig, and "
            "kPhase7AD3GlobalParseResult.status in active source"
        )


def validate_fixture(payload: dict[str, Any]) -> None:
    expected_values = {
        "status": "design_accepted",
        "contract_id": "active_runtime_config_state",
        "depends_on_guardrail_id": "runtime_hot_path_no_parser_result_state_read",
        "required_hot_path_invariant": EXPECTED_INVARIANT,
        "firmware_behavior_changed": False,
        "build_required": False,
        "nunchuk_status": "not_tested",
        "failed_activation_branch_merge_allowed": False,
    }
    for key, expected in expected_values.items():
        actual = payload.get(key)
        if actual != expected:
            fail(f"fixture {key!r} mismatch: expected {expected!r}, got {actual!r}")

    shape = payload.get("active_state_shape")
    expected_shape = {
        "active_view": "const RuntimeConfigView*",
        "source": "RuntimeConfigSource",
        "status": "RuntimeConfigActivationStatus",
    }
    if shape != expected_shape:
        fail(f"fixture active_state_shape mismatch: expected {expected_shape!r}, got {shape!r}")


def validate_docs(doc: str, readme: str, current_state: str, roadmap: str, workflow: str) -> None:
    for phrase in (
        "status: DESIGN_ACCEPTED",
        "title: Active Runtime Config State Contract",
        "This branch is docs/tools-only and changes no firmware behavior.",
        EXPECTED_INVARIANT,
        "activation / selection phase",
        "output generation phase",
        "enum class RuntimeConfigSource",
        "enum class RuntimeConfigActivationStatus",
        "struct ActiveRuntimeConfigState",
        ACTIVE_VIEW_INVARIANT,
        NO_SOURCE_STATUS_BRANCH_INVARIANT,
        "ResolveActiveRuntimeConfig() may return a stable preselected view, but must not inspect parser result state.",
        "Parser/materialization/load status may be used only before active-state publication.",
        "True parsed table materialization remains deferred.",
        "Runtime-loaded config remains deferred.",
        "Storage/write/WebSerial/flashing remain not implemented.",
        "Nunchuk remains not tested.",
        "failed activation branch remains abandoned and must not merge",
        "No firmware source changes.",
        "No build required.",
        "No runtime-loaded config.",
        "No parsed table materialization.",
        "No storage.",
        "No WebSerial/device write.",
        "No flashing automation.",
        "No nunchuk validation claim.",
    ):
        require_phrase(doc, phrase, "contract doc")

    for phrase in (
        "active_runtime_config_state_contract.md",
        "fixtures/active_runtime_config_state_contract.json",
    ):
        require_phrase(readme, phrase, "runtime config README")

    require_phrase(current_state, "Active runtime config state contract is accepted", "CURRENT_STATE")
    require_phrase(current_state, ACTIVE_VIEW_INVARIANT, "CURRENT_STATE")
    require_phrase(current_state, NO_SOURCE_STATUS_BRANCH_INVARIANT, "CURRENT_STATE")
    require_phrase(roadmap, "Active Runtime Config State Contract", "ROADMAP")
    require_phrase(workflow, "Activation/selection may validate parser/materialization/load status before active-state publication", "WORKFLOW")


def iter_claim_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def validate_no_forbidden_doc_claims(docs: dict[str, str]) -> None:
    for label, text in docs.items():
        for sentence in iter_claim_sentences(text):
            lowered = sentence.lower()
            if any(context in lowered for context in NEGATING_CONTEXT):
                continue
            for pattern in FORBIDDEN_DOC_CLAIMS:
                if re.search(pattern, lowered):
                    fail(f"{label} appears to make a forbidden claim: {sentence}")


def main() -> int:
    branch = current_branch()
    validate_branch(branch)
    if branch == EXPECTED_BRANCH:
        paths = changed_paths()
        validate_changed_paths(paths)

    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    readme = read_required(README_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)
    workflow = read_required(WORKFLOW_PATH)

    validate_fixture(fixture)
    validate_docs(doc, readme, current_state, roadmap, workflow)
    validate_no_forbidden_doc_claims(
        {
            rel(DOC_PATH): doc,
            rel(README_PATH): readme,
            rel(CURRENT_STATE_PATH): current_state,
            rel(ROADMAP_PATH): roadmap,
            rel(WORKFLOW_PATH): workflow,
        }
    )
    validate_ultimate_source_guardrail()

    print("glyph_active_runtime_config_state_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- {rel(DOC_PATH)}")
    print(f"- {rel(FIXTURE_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
