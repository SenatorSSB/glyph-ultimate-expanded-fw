#!/usr/bin/env python3
"""Validate the runtime-config candidate-state materialization scaffold."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-candidate-state-materialization-scaffold"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, MERGED_BRANCH}

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
DOC_PATH = REPO_ROOT / "docs/runtime_config/candidate_state_materialization_scaffold.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/candidate_state_materialization_scaffold.json"
BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/candidate_state_materialization_scaffold_build_report_2026-06-10.md"
BUILD_REPORT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/candidate_state_materialization_scaffold_build_report_2026-06-10.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
WORKFLOW_PATH = REPO_ROOT / "docs/WORKFLOW.md"

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigCandidate.hpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "tools/check_glyph_candidate_state_materialization_scaffold.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/",)
FORBIDDEN_CHANGED_RE = re.compile(r"(^|/)(hal|backend|config\.pb|write|flashing|storage)(/|$)", re.I)

FORBIDDEN_SOURCE_TOKENS = (
    "kPhase7AD3GlobalParseResult.status",
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
    r"\bruntime config storage (?:is |was |has been )?implemented\b",
    r"\bstorage (?:is |was |has been )?implemented\b",
    r"\bWebSerial/device write (?:is |was |has been )?implemented\b",
    r"\bdevice write (?:is |was |has been )?implemented\b",
    r"\bflashing automation (?:is |was |has been )?implemented\b",
    r"\bparsed runtime-loaded config (?:is |was |has been )?implemented\b",
    r"\bnunchuk (?:is |was |has been )?(?:tested|validated)\b",
    r"\bnunchuk (?:tested|validated|validation confirmed|hardware validated)\b",
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


class CandidateScaffoldError(AssertionError):
    """Raised when candidate-state scaffold guardrails are violated."""


def fail(message: str) -> None:
    raise CandidateScaffoldError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def no_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            fail(f"duplicate JSON key in payload: {key}")
        values[key] = value
    return values


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


def validate_branch() -> str:
    branch = current_branch()
    if branch not in ALLOWED_BRANCHES:
        fail(f"checker must run on {EXPECTED_BRANCH} or {MERGED_BRANCH}, got {branch}")
    if branch == EXPECTED_BRANCH:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{BASE_BRANCH} must be an ancestor of HEAD")
    return branch


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


def validate_changed_paths(paths: set[str], branch: str) -> None:
    for path in sorted(paths):
        if FORBIDDEN_CHANGED_RE.search(path):
            fail(f"forbidden HAL/backend/config.pb/write/flashing/storage path changed: {path}")
        if branch == MERGED_BRANCH:
            continue
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"candidate scaffold branch changed out-of-scope path: {path}")


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
    brace = 1
    pos += 1
    while pos < len(text):
        if text.startswith("//", pos):
            newline = text.find("\n", pos)
            if newline == -1:
                break
            pos = newline + 1
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


def normalize_block(text: str) -> str:
    return "".join(line.strip() for line in strip_cpp_comments(text).splitlines() if line.strip())


def baseline_ultimate_source() -> str:
    completed = subprocess.run(
        ["git", "show", f"{BASE_BRANCH}:src/modes/Ultimate.cpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail(f"could not read {BASE_BRANCH}:src/modes/Ultimate.cpp: {completed.stderr.strip()}")
    return completed.stdout


def validate_source(source: str) -> None:
    active_source = strip_cpp_comments(source)
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in active_source:
            fail(f"forbidden source token found in Ultimate.cpp: {token}")

    for token in (
        "enum class RuntimeConfigCandidateStatus",
        "RuntimeConfigCandidateStatus::Empty",
        "RuntimeConfigCandidateStatus::ParsedPayloadValid",
        "RuntimeConfigCandidateStatus::InvalidPayload",
        "struct RuntimeConfigCandidateState",
        "RuntimeConfigView view",
        "ResetRuntimeConfigCandidateState",
        "ValidateRuntimeConfigCandidateState",
        "MaterializeRuntimeConfigCandidateFromSourceView",
    ):
        if token not in active_source:
            fail(f"candidate-state scaffold source missing token: {token}")

    if "ParseUltimateRuntimeConfigPayload(" in active_source:
        update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
        if "ParseUltimateRuntimeConfigPayload(" in update_body:
            fail("UpdateAnalogOutputs must not call ParseUltimateRuntimeConfigPayload")

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must return only the stable active view")
    for token in ("Candidate", "Parse", "status", "source", "activation", "load", "storage", "write"):
        if token in resolve_body:
            fail(f"ResolveActiveRuntimeConfig must not inspect {token} state")

    update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in update_body:
        fail("UpdateAnalogOutputs must bind runtime_config through ResolveActiveRuntimeConfig()")
    for token in (
        "Candidate",
        "candidate",
        "Parse",
        "parser",
        "load",
        "storage",
        "write",
        "activation",
        "status",
        "RuntimeConfigCandidateState",
        "RuntimeConfigCandidateStatus",
        "MaterializeRuntimeConfigCandidateFromSourceView",
    ):
        if token in update_body:
            fail(f"UpdateAnalogOutputs must not mention candidate/parser/load/storage/write/activation status: {token}")

    for expr in (
        "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
        "state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;",
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "outputs.buttonR = inputs.rf6;",
        "state.z_airdodge_override_active = inputs.rf6;",
    ):
        if expr not in source:
            fail(f"expected RF5/RF6/LT6 expression missing: {expr}")

    baseline = baseline_ultimate_source()
    current_digital = extract_function(source, "UpdateDigitalOutputs")
    baseline_digital = extract_function(baseline, "UpdateDigitalOutputs")
    if normalize_block(current_digital) != normalize_block(baseline_digital):
        fail("UpdateDigitalOutputs changed relative to configurator")


def validate_doc_claims(paths: list[Path]) -> None:
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        if "nunchuk remains not_tested" not in lowered and path in (DOC_PATH, FIXTURE_PATH, BUILD_REPORT_PATH, BUILD_REPORT_FIXTURE_PATH, CURRENT_STATE_PATH):
            fail(f"{rel(path)} must preserve nunchuk remains NOT_TESTED wording")
        for pattern in FORBIDDEN_DOC_CLAIMS:
            for match in re.finditer(pattern, text, flags=re.I):
                prefix = text[max(0, match.start() - 40) : match.start()].lower()
                if not any(prefix.endswith(marker) or marker in prefix[-24:] for marker in NEGATING_CONTEXT):
                    fail(f"{rel(path)} contains forbidden positive claim: {match.group(0)!r}")


def require_phrase(text: str, phrase: str, label: str) -> None:
    compact_text = re.sub(r"\s+", " ", text).strip().lower()
    compact_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
    if compact_phrase not in compact_text:
        fail(f"{label} missing required phrase: {phrase}")


def validate_scaffold_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_candidate_state_materialization_scaffold",
        "status": "scaffold_ready",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "candidate_state_active": False,
        "active_runtime_output_path_consumes_candidate_state": False,
        "parser_status_read_in_analog_hot_path": False,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "flashing_automation_implemented": False,
        "hardware_test_required": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    allowed_output = payload.get("output_generation_allowed_inputs")
    if allowed_output != ["already-selected RuntimeConfigView"]:
        fail("fixture output_generation_allowed_inputs must allow only already-selected RuntimeConfigView")
    forbidden_output = payload.get("output_generation_forbidden_inputs")
    if not isinstance(forbidden_output, list):
        fail("fixture output_generation_forbidden_inputs must be a list")
    for token in ("candidate state", "parser status", "CRC status", "load status", "storage status", "write status", "source", "activation status"):
        if token not in forbidden_output:
            fail(f"fixture output_generation_forbidden_inputs missing {token!r}")


def validate_build_report_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected_strings = {
        "schema_name": "glyph_candidate_state_materialization_scaffold_build_report",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "build_command": "pio run -e glyph_mk6",
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected_strings.items():
        if payload.get(key) != value:
            fail(f"build fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    if payload.get("artifact_hashes_are_checker_gate") is not False:
        fail("artifact hashes must be recorded as local observations only, not checker gates")
    if payload.get("hardware_result_claimed") is not False:
        fail("build report must not claim hardware result")
    if "`pio run -e glyph_mk6`" not in report_text:
        fail("build report must record full canonical command `pio run -e glyph_mk6`")
    if "artifact_hashes_are_checker_gate" not in report_text or "`false`" not in report_text:
        fail("build report must state artifact hashes are not checker gates")


def validate_docs_and_fixtures() -> None:
    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    build_report = read_required(BUILD_REPORT_PATH)
    build_fixture = load_json_object(BUILD_REPORT_FIXTURE_PATH)
    readme = read_required(README_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)
    if WORKFLOW_PATH.exists():
        read_required(WORKFLOW_PATH)

    for phrase in (
        "status: IMPLEMENTATION_SCAFFOLD",
        "candidate state is not active",
        "Candidate materialization does not change the active runtime config.",
        "Output generation may consume only the already-selected RuntimeConfigView.",
        "ResolveActiveRuntimeConfig() remains stable active-view only.",
        "UpdateAnalogOutputs(...) must not read candidate state, parser status, CRC status, load status, storage status, write status, source, or activation status.",
        "No hardware test is required for this branch because candidate state is not active.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(doc, phrase, "candidate scaffold doc")

    require_phrase(readme, "candidate_state_materialization_scaffold.md", "runtime config README")
    require_phrase(current_state, "Candidate runtime config state materialization scaffold", "current state")
    require_phrase(roadmap, "candidate-state materialization scaffold", "roadmap")
    validate_scaffold_fixture(fixture)
    validate_build_report_fixture(build_fixture, build_report)
    validate_doc_claims([DOC_PATH, FIXTURE_PATH, BUILD_REPORT_PATH, BUILD_REPORT_FIXTURE_PATH, README_PATH, CURRENT_STATE_PATH, ROADMAP_PATH])


def main() -> None:
    branch = validate_branch()
    paths = changed_paths()
    validate_changed_paths(paths, branch)
    validate_source(read_required(ULTIMATE_PATH))
    validate_docs_and_fixtures()
    print("candidate-state materialization scaffold checks passed")


if __name__ == "__main__":
    main()
