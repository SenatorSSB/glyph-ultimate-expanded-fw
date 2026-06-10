#!/usr/bin/env python3
"""Validate parsed-candidate-present/source-owned-published diagnostic branch."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-diagnostic-parsed-candidate-present-source-owned-published"
RESULT_BRANCH = "runtime-config-diagnostic-parsed-candidate-present-source-owned-published-hardware-result"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, RESULT_BRANCH, MERGED_BRANCH}

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
DOC_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_parsed_candidate_present_source_owned_published.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_parsed_candidate_present_source_owned_published.json"
BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_parsed_candidate_present_source_owned_published_build_report_2026-06-10.md"
BUILD_REPORT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_parsed_candidate_present_source_owned_published_build_report_2026-06-10.json"
HARDWARE_PLAN_PATH = REPO_ROOT / "docs/calibration/diagnostic_parsed_candidate_present_source_owned_published_hardware_plan_2026-06-10.md"
HARDWARE_PLAN_FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/diagnostic_parsed_candidate_present_source_owned_published_hardware_plan_2026-06-10.json"
HARDWARE_RESULT_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.md"
HARDWARE_RESULT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/check_glyph_diagnostic_parsed_candidate_present_source_owned_published.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")
OPTIONAL_HELPER_RE = re.compile(r"^src/modes/[^/]+\.(?:hpp|cpp|h)$")
FORBIDDEN_CHANGED_RE = re.compile(
    r"(^|/)(?:hal|backend|config\.pb|storage|write|webserial|flash|flashing)(?:/|$)",
    re.I,
)

EXPECTED_HARDWARE_ROWS = [
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "UNRELATED-BUTTONS-001",
    "MODIFIERS-001",
    "PARSED-CANDIDATE-PRESENT-001",
    "SOURCE-OWNED-PUBLISHED-001",
    "HOT-PATH-001",
    "NO-CANDIDATE-ACTIVE-PUBLICATION-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
]


class DiagnosticCheckError(AssertionError):
    """Raised when diagnostic branch guardrails drift."""


def fail(message: str) -> None:
    raise DiagnosticCheckError(message)


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
            fail(f"duplicate JSON key: {key}")
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
        fail("could not determine current branch")
    return branch[0]


def validate_branch() -> str:
    branch = current_branch()
    if branch not in ALLOWED_BRANCHES:
        fail(f"checker must run on {EXPECTED_BRANCH}, {RESULT_BRANCH}, or {MERGED_BRANCH}, got {branch}")
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
    if branch == RESULT_BRANCH:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", EXPECTED_BRANCH, "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{EXPECTED_BRANCH} must be an ancestor of HEAD")
    return branch


def comparison_branch(branch: str) -> str:
    if branch == RESULT_BRANCH:
        return EXPECTED_BRANCH
    return BASE_BRANCH


def changed_paths(branch: str) -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{comparison_branch(branch)}...HEAD"]))
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
            fail(f"forbidden HAL/backend/config.pb/storage/write/WebSerial/flashing path changed: {path}")
        if branch == RESULT_BRANCH and path.startswith("src/"):
            fail(f"result branch must not change firmware source relative to {EXPECTED_BRANCH}: {path}")
        if branch == MERGED_BRANCH:
            continue
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if OPTIONAL_HELPER_RE.match(path):
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


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


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label} missing token: {token}")


def validate_source(source: str) -> None:
    active_source = strip_cpp_comments(source)
    if "kPhase7AD3GlobalParseResult.status" in active_source:
        fail("forbidden parser status token found: kPhase7AD3GlobalParseResult.status")

    for token in (
        "kDiagnosticSourceOwnedParsedPayload",
        "UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload",
        "RuntimeConfigCandidateStatus::ParsedPayloadValid",
        "RuntimeConfigCandidateStatus::ParsedPayloadEquivalent",
        "struct RuntimeConfigCandidateState",
        "struct DiagnosticParsedCandidateState",
        "MaterializeRuntimeConfigCandidateFromSourceView",
        "RuntimeConfigViewsHaveEquivalentPoints",
        "InitializeDiagnosticParsedCandidateState",
        "kDiagnosticParsedCandidateState",
    ):
        require_token(active_source, token, "Ultimate.cpp diagnostic source")

    get_state_body = strip_cpp_comments(extract_function(source, "GetActiveRuntimeConfigState"))
    for token in (
        "&kSourceOwnedCurrentBaselineRuntimeConfig",
        "RuntimeConfigSource::SourceOwnedBaseline",
        "RuntimeConfigActivationStatus::SourceOwnedSelected",
    ):
        require_token(get_state_body, token, "GetActiveRuntimeConfigState")
    for forbidden in ("candidate", "Candidate", "ParsedPayload", "ParseStatus", "kDiagnosticParsedCandidateState"):
        if forbidden in get_state_body:
            fail(f"GetActiveRuntimeConfigState must not publish parsed candidate state: {forbidden}")
    if "&kKnownGoodRuntimeConfig" in get_state_body:
        fail("GetActiveRuntimeConfigState must force source-owned baseline publication on this diagnostic branch")

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must return only GetActiveRuntimeConfigState().active_view")
    for forbidden in (
        "candidate",
        "Candidate",
        "parser",
        "Parse",
        "decision",
        "status",
        "source",
        "load",
        "storage",
        "write",
        "flash",
        "kDiagnosticParsedCandidateState",
    ):
        if forbidden in resolve_body:
            fail(f"ResolveActiveRuntimeConfig must not inspect {forbidden} state")

    update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in update_body:
        fail("UpdateAnalogOutputs must bind runtime_config through ResolveActiveRuntimeConfig()")
    for forbidden in (
        "candidate",
        "Candidate",
        "parser",
        "Parse",
        "decision",
        "status",
        "source",
        "load",
        "storage",
        "write",
        "flash",
        "RuntimeConfigCandidate",
        "kDiagnosticParsedCandidateState",
    ):
        if forbidden in update_body:
            fail(f"UpdateAnalogOutputs must not mention {forbidden}")

    for expr in (
        "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
        "state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;",
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "outputs.buttonR = inputs.rf6;",
        "state.z_airdodge_override_active = inputs.rf6;",
    ):
        require_token(source, expr, "RF5/RF6/LT6 source")

    baseline = baseline_ultimate_source()
    if normalize_block(extract_function(source, "UpdateDigitalOutputs")) != normalize_block(extract_function(baseline, "UpdateDigitalOutputs")):
        fail("UpdateDigitalOutputs changed relative to configurator")


def require_phrase(text: str, phrase: str, label: str) -> None:
    compact_text = re.sub(r"\s+", " ", text).strip().lower()
    compact_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
    if compact_phrase not in compact_text:
        fail(f"{label} missing phrase: {phrase}")


def validate_diagnostic_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_parsed_candidate_present_source_owned_published",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "previous_failing_branch": "runtime-config-parsed-candidate-opt-in-diagnostic-batch",
        "previous_hardware_result": "HARDWARE_FAIL",
        "parsed_candidate_opt_in_activation_safe_for_merge": False,
        "source_owned_static_diagnostic_parsed_payload_present": True,
        "candidate_parser_bridge_present": True,
        "candidate_materialization_present": True,
        "candidate_equivalence_validation_present": True,
        "candidate_view_published_active": False,
        "published_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "hardware_result_claimed": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"diagnostic fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")


def validate_build_report_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_parsed_candidate_present_source_owned_published_build_report",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "candidate_view_published_active": False,
        "published_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "artifact_hashes_are_checker_gate": False,
        "hardware_result_claimed": False,
        "hardware_test_required": True,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"build report fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    if not isinstance(payload.get("artifact_hashes"), list):
        fail("build report fixture artifact_hashes must be a list")
    require_phrase(report_text, "Canonical command: pio run -e glyph_mk6", "build report")
    require_phrase(report_text, "Artifact hashes are local observations only, not checker gates.", "build report")
    require_phrase(report_text, "`artifact_hashes_are_checker_gate`: `false`", "build report")
    require_phrase(report_text, "No hardware result is claimed", "build report")
    require_phrase(report_text, "Nunchuk remains NOT_TESTED", "build report")


def validate_hardware_result_fixture(payload: dict[str, Any], result_text: str, label: str) -> None:
    if payload.get("schema_name") != "glyph_diagnostic_parsed_candidate_present_source_owned_published_hardware_result":
        fail(f"{label} fixture schema_name mismatch")
    if payload.get("status") != "HARDWARE_PASS":
        fail(f"{label} fixture status must be HARDWARE_PASS")
    if payload.get("overall_result") != "HARDWARE_PASS":
        fail(f"{label} fixture overall_result must be HARDWARE_PASS")
    if payload.get("branch") != EXPECTED_BRANCH:
        if payload.get("branch_under_test") != EXPECTED_BRANCH:
            fail(f"{label} fixture branch_under_test mismatch")
    if payload.get("branch_under_test", EXPECTED_BRANCH) != EXPECTED_BRANCH:
        fail(f"{label} fixture branch_under_test mismatch")
    if payload.get("result_branch") != RESULT_BRANCH:
        fail(f"{label} fixture result_branch mismatch")
    if payload.get("hardware_result_claimed", True) is not True:
        fail(f"{label} fixture must claim recorded hardware result")
    if payload.get("operator_report") != "tested, everything works":
        fail(f"{label} fixture must preserve operator report text")
    if payload.get("nunchuk_status") != "NOT_TESTED":
        fail(f"{label} fixture nunchuk_status must be NOT_TESTED")
    expected_booleans = {
        "parsed_candidate_presence_safe_when_source_owned_published": True,
        "candidate_view_active_publication_remains_suspect": True,
        "parsed_candidate_opt_in_activation_safe_for_merge": False,
        "source_owned_active_state_preselection_remains_repair_baseline": True,
        "implementation_branch_merge_allowed": True,
        "failed_opt_in_activation_branch_merge_allowed": False,
        "low_level_failure_mechanism_proven": False,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "candidate_view_published_active": False,
    }
    for key, value in expected_booleans.items():
        if payload.get(key) != value:
            fail(f"{label} fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail(f"{label} fixture rows must be a list")
    row_ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if row_ids != EXPECTED_HARDWARE_ROWS:
        fail(f"{label} rows mismatch: expected {EXPECTED_HARDWARE_ROWS!r}, got {row_ids!r}")
    for row in rows:
        if not isinstance(row, dict):
            fail(f"{label} row must be an object")
        expected_status = "NOT_TESTED" if row.get("id") == "NUNCHUK-001" else "PASS"
        if row.get("status") != expected_status:
            fail(f"{label} row {row.get('id')} must be {expected_status}")
        require_phrase(result_text, f"| {row['id']} ", label)
        require_phrase(result_text, f"| {row['id']} |", label)
    for phrase in (
        "status: HARDWARE_PASS",
        "tested, everything works",
        "parsed_candidate_presence_safe_when_source_owned_published",
        "candidate_view_active_publication_remains_suspect",
        "parsed_candidate_opt_in_activation_safe_for_merge",
        "low_level_failure_mechanism_proven",
        "Runtime-loaded config is not implemented.",
        "Runtime-config storage is not implemented.",
        "WebSerial/device write is not implemented.",
        "backend/config.pb write path is not implemented.",
        "Firmware flashing automation is not implemented.",
        "Parsed candidate activation is not claimed safe.",
        "The low-level failure mechanism is not proven.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(result_text, phrase, label)


def validate_docs_and_fixtures() -> None:
    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    build_report = read_required(BUILD_REPORT_PATH)
    build_fixture = load_json_object(BUILD_REPORT_FIXTURE_PATH)
    hardware_plan = read_required(HARDWARE_PLAN_PATH)
    hardware_fixture = load_json_object(HARDWARE_PLAN_FIXTURE_PATH)
    hardware_result = read_required(HARDWARE_RESULT_PATH)
    hardware_result_fixture = load_json_object(HARDWARE_RESULT_FIXTURE_PATH)
    readme = read_required(README_PATH)
    calibration_index = read_required(CALIBRATION_INDEX_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)

    for phrase in (
        "status: HARDWARE_PASS",
        "parsed candidate machinery",
        "published active runtime view is forced to kSourceOwnedCurrentBaselineRuntimeConfig",
        "candidate.view is not published as the active runtime view",
        "ResolveActiveRuntimeConfig() returns only the stable published active view",
        "UpdateAnalogOutputs(...) does not read parser, candidate, decision, source, status, load, storage, write, or flash state",
        "tested, everything works",
        "Parsed candidate activation is not claimed safe.",
        "The low-level failure mechanism is not proven.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(doc, phrase, "diagnostic doc")

    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
    ):
        require_phrase(text, "diagnostic_parsed_candidate_present_source_owned_published", label)

    validate_diagnostic_fixture(fixture)
    validate_build_report_fixture(build_fixture, build_report)
    validate_hardware_result_fixture(hardware_fixture, hardware_plan, "calibration hardware result")
    validate_hardware_result_fixture(hardware_result_fixture, hardware_result, "runtime config hardware result")

    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
    ):
        require_phrase(text, "HARDWARE_PASS", label)


def main() -> None:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch), branch)
    validate_source(read_required(ULTIMATE_PATH))
    validate_docs_and_fixtures()
    print("diagnostic parsed candidate present/source-owned published checks passed")


if __name__ == "__main__":
    main()
