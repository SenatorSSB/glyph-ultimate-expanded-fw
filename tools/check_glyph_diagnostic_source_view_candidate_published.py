#!/usr/bin/env python3
"""Validate source-view-candidate-published diagnostic branch."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-diagnostic-source-view-candidate-published"
RESULT_BRANCH = "runtime-config-diagnostic-source-view-candidate-published-hardware-failure"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, RESULT_BRANCH, MERGED_BRANCH}

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
DOC_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_source_view_candidate_published.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_source_view_candidate_published.json"
BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_source_view_candidate_published_build_report_2026-06-10.md"
BUILD_REPORT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_source_view_candidate_published_build_report_2026-06-10.json"
HARDWARE_PLAN_PATH = REPO_ROOT / "docs/calibration/diagnostic_source_view_candidate_published_hardware_plan_2026-06-10.md"
HARDWARE_PLAN_FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/diagnostic_source_view_candidate_published_hardware_plan_2026-06-10.json"
HARDWARE_FAILURE_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_source_view_candidate_published_hardware_failure_2026-06-10.md"
HARDWARE_FAILURE_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_source_view_candidate_published_hardware_failure_2026-06-10.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"

IMPLEMENTATION_ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/check_glyph_diagnostic_source_view_candidate_published.py",
}
RESULT_ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/check_glyph_diagnostic_source_view_candidate_published.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")
OPTIONAL_HELPER_RE = re.compile(r"^src/modes/[^/]+\.(?:hpp|cpp|h)$")
FIRMWARE_SOURCE_PREFIXES = ("src/", "include/")
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
    "SOURCE-VIEW-CANDIDATE-MATERIALIZED-001",
    "CANDIDATE-EQUIVALENCE-001",
    "CANDIDATE-ACTIVE-PUBLICATION-001",
    "SOURCE-OWNED-FALLBACK-001",
    "HOT-PATH-001",
    "NO-PARSER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
]

EXPECTED_FAILURE_ROW_STATUSES = {
    "BOOT-001": "UNKNOWN",
    "BASELINE-001": "FAIL",
    "RF5-001": "UNKNOWN",
    "RF6-001": "UNKNOWN",
    "LT6-001": "UNKNOWN",
    "ORDINARY-DIR-001": "UNKNOWN",
    "NEUTRAL-001": "UNKNOWN",
    "UNRELATED-BUTTONS-001": "UNKNOWN",
    "MODIFIERS-001": "UNKNOWN",
    "SOURCE-VIEW-CANDIDATE-MATERIALIZED-001": "PASS",
    "CANDIDATE-EQUIVALENCE-001": "PASS",
    "CANDIDATE-ACTIVE-PUBLICATION-001": "FAIL",
    "SOURCE-OWNED-FALLBACK-001": "UNKNOWN",
    "HOT-PATH-001": "INVESTIGATE",
    "NO-PARSER-001": "PASS",
    "NO-STORAGE-001": "PASS",
    "NO-WRITE-001": "PASS",
    "NO-FLASH-001": "PASS",
    "NUNCHUK-001": "NOT_TESTED",
}


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
        fail(
            f"checker must run on {EXPECTED_BRANCH}, {RESULT_BRANCH}, "
            f"or {MERGED_BRANCH}, got {branch}"
        )
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


def changed_paths(branch: str) -> set[str]:
    paths: set[str] = set()
    if branch == EXPECTED_BRANCH:
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    elif branch == RESULT_BRANCH:
        paths.update(git_lines(["diff", "--name-only", f"{EXPECTED_BRANCH}...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status=True):
        path = status_line[3:].strip()
        if not path:
            continue
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return paths


def validate_changed_paths(paths: set[str], branch: str) -> None:
    allowed_exact = (
        RESULT_ALLOWED_EXACT_CHANGED_PATHS
        if branch == RESULT_BRANCH
        else IMPLEMENTATION_ALLOWED_EXACT_CHANGED_PATHS
    )
    for path in sorted(paths):
        if FORBIDDEN_CHANGED_RE.search(path):
            fail(f"forbidden HAL/backend/config.pb/storage/write/WebSerial/flashing path changed: {path}")
        if branch == MERGED_BRANCH:
            continue
        if branch == RESULT_BRANCH and path.startswith(FIRMWARE_SOURCE_PREFIXES):
            fail(f"firmware source changed on hardware result branch: {path}")
        if path in allowed_exact:
            continue
        if branch == EXPECTED_BRANCH and OPTIONAL_HELPER_RE.match(path):
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


def forbid_token(text: str, token: str, label: str) -> None:
    if token in text:
        fail(f"{label} contains forbidden token: {token}")


def called_function_names(function_body: str, function_names: set[str]) -> set[str]:
    body = strip_cpp_comments(function_body)
    return {
        name
        for name in function_names
        if re.search(rf"\b{re.escape(name)}\s*\(", body)
    }


def reachable_functions(functions: dict[str, str], start: str) -> set[str]:
    seen: set[str] = set()
    pending = [start]
    function_names = set(functions)
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        for called in called_function_names(functions[name], function_names):
            if called != name and called not in seen:
                pending.append(called)
    return seen


def validate_source(source: str, branch: str) -> None:
    active_source = strip_cpp_comments(source)
    for token in (
        "ParseUltimateRuntimeConfigPayload",
        "UltimateRuntimeConfigParser",
        "kDiagnosticSourceOwnedParsedPayload",
        "kPhase7AD3GlobalParseResult.status",
        "D2B",
    ):
        forbid_token(active_source, token, "Ultimate.cpp diagnostic source")

    for token in (
        "struct RuntimeConfigCandidateState",
        "struct DiagnosticSourceViewCandidatePublicationState",
        "RuntimeConfigCandidateStatus::SourceViewValid",
        "RuntimeConfigCandidateStatus::SourceViewEquivalent",
        "MaterializeRuntimeConfigCandidateFromSourceView",
        "kSourceOwnedCurrentBaselineRuntimeConfig",
        "ValidateRuntimeConfigCandidateState",
        "RuntimeConfigViewsHaveEquivalentPoints",
        "GetDiagnosticSourceViewCandidatePublicationState",
        "gDiagnosticSourceViewCandidatePublicationState",
        "gActiveRuntimeConfigState",
    ):
        require_token(active_source, token, "Ultimate.cpp diagnostic source")

    materialize_body = strip_cpp_comments(extract_function(source, "InitializeDiagnosticSourceViewCandidatePublicationState"))
    for token in (
        "MaterializeRuntimeConfigCandidateFromSourceView(",
        "kSourceOwnedCurrentBaselineRuntimeConfig",
        "state.validated = state.materialized && ValidateRuntimeConfigCandidateState(state.candidate);",
        "state.equivalent_to_source_owned_baseline = state.validated &&",
        "RuntimeConfigViewsHaveEquivalentPoints(",
        "RuntimeConfigCandidateStatus::SourceViewEquivalent",
    ):
        require_token(materialize_body, token, "candidate materialization")

    get_diagnostic_body = strip_cpp_comments(extract_function(source, "GetDiagnosticSourceViewCandidatePublicationState"))
    if "return gDiagnosticSourceViewCandidatePublicationState;" not in get_diagnostic_body:
        fail("GetDiagnosticSourceViewCandidatePublicationState must return namespace-scope diagnostic state only")
    if "static" in get_diagnostic_body:
        fail("GetDiagnosticSourceViewCandidatePublicationState must not use function-local static initialization")
    for forbidden in (
        "InitializeDiagnosticSourceViewCandidatePublicationState",
        "MaterializeRuntimeConfigCandidateFromSourceView",
        "RuntimeConfigViewsHaveEquivalentPoints",
        "ValidateRuntimeConfigCandidateState",
    ):
        forbid_token(get_diagnostic_body, forbidden, "GetDiagnosticSourceViewCandidatePublicationState")

    get_state_body = strip_cpp_comments(extract_function(source, "GetActiveRuntimeConfigState"))
    if "return gActiveRuntimeConfigState;" not in get_state_body:
        fail("GetActiveRuntimeConfigState must return namespace-scope active state only")
    if "static" in get_state_body:
        fail("GetActiveRuntimeConfigState must not use function-local static initialization")
    for forbidden in (
        "GetDiagnosticSourceViewCandidatePublicationState",
        "InitializeDiagnosticSourceViewCandidatePublicationState",
        "MaterializeRuntimeConfigCandidateFromSourceView",
        "RuntimeConfigViewsHaveEquivalentPoints",
        "ValidateRuntimeConfigCandidateState",
        "gDiagnosticSourceViewCandidatePublicationState",
        "candidate",
        "Candidate",
        "validated",
        "equivalent_to_source_owned_baseline",
    ):
        forbid_token(get_state_body, forbidden, "GetActiveRuntimeConfigState")

    for token in (
        "DiagnosticSourceViewCandidatePublicationState gDiagnosticSourceViewCandidatePublicationState =",
        "InitializeDiagnosticSourceViewCandidatePublicationState();",
        "const ActiveRuntimeConfigState gActiveRuntimeConfigState =",
        "gDiagnosticSourceViewCandidatePublicationState.validated &&",
        "gDiagnosticSourceViewCandidatePublicationState.equivalent_to_source_owned_baseline",
        "? &gDiagnosticSourceViewCandidatePublicationState.candidate.view",
        ": &kSourceOwnedCurrentBaselineRuntimeConfig",
        "? RuntimeConfigSource::SourceViewCandidate",
        ": RuntimeConfigSource::SourceOwnedBaseline",
        "? RuntimeConfigActivationStatus::CandidateViewSelected",
        ": RuntimeConfigActivationStatus::FallbackSelected",
    ):
        require_token(active_source, token, "namespace-scope active publication")

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    resolve_compact = re.sub(r"\s+", "", strip_cpp_comments(resolve_body))
    if resolve_compact != "ResolveActiveRuntimeConfig(){return*GetActiveRuntimeConfigState().active_view;}":
        fail("ResolveActiveRuntimeConfig must only dereference GetActiveRuntimeConfigState().active_view")

    functions = {
        name: strip_cpp_comments(extract_function(source, name))
        for name in (
            "ResolveActiveRuntimeConfig",
            "GetActiveRuntimeConfigState",
            "GetDiagnosticSourceViewCandidatePublicationState",
            "InitializeDiagnosticSourceViewCandidatePublicationState",
            "MaterializeRuntimeConfigCandidateFromSourceView",
            "RuntimeConfigViewsHaveEquivalentPoints",
            "ValidateRuntimeConfigCandidateState",
        )
    }
    reachable_from_resolver = reachable_functions(functions, "ResolveActiveRuntimeConfig")
    expected_chain = {"ResolveActiveRuntimeConfig", "GetActiveRuntimeConfigState"}
    if reachable_from_resolver != expected_chain:
        fail(
            "ResolveActiveRuntimeConfig reachable chain must be "
            "ResolveActiveRuntimeConfig -> GetActiveRuntimeConfigState only; got "
            + ", ".join(sorted(reachable_from_resolver))
        )
    for forbidden in (
        "InitializeDiagnosticSourceViewCandidatePublicationState",
        "MaterializeRuntimeConfigCandidateFromSourceView",
        "RuntimeConfigViewsHaveEquivalentPoints",
        "ValidateRuntimeConfigCandidateState",
    ):
        if forbidden in reachable_from_resolver:
            fail(f"ResolveActiveRuntimeConfig must not reach {forbidden}")
    for name in reachable_from_resolver:
        body = functions[name]
        if "static" in body and any(
            token in body
            for token in (
                "candidate",
                "Candidate",
                "DiagnosticSourceViewCandidatePublicationState",
                "InitializeDiagnosticSourceViewCandidatePublicationState",
                "MaterializeRuntimeConfigCandidateFromSourceView",
                "RuntimeConfigViewsHaveEquivalentPoints",
            )
        ):
            fail(f"{name} has function-local static candidate/materialization/publication state")

    update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in update_body:
        fail("UpdateAnalogOutputs must bind runtime_config through ResolveActiveRuntimeConfig()")
    for forbidden in (
        "candidate",
        "Candidate",
        "parser",
        "Parser",
        "Parse",
        "decision",
        "status",
        "load",
        "storage",
        "write",
        "flash",
        "RuntimeConfigCandidate",
        "GetActiveRuntimeConfigState",
        "GetDiagnosticSourceViewCandidatePublicationState",
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

    if branch == EXPECTED_BRANCH:
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
        "schema_name": "glyph_diagnostic_source_view_candidate_published",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "previous_source_owned_preselection_result": "HARDWARE_PASS",
        "previous_parsed_candidate_present_source_owned_published_result": "HARDWARE_PASS",
        "previous_parsed_candidate_opt_in_activation_result": "HARDWARE_FAIL",
        "candidate_materialization_source": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "source_owned_static_diagnostic_parsed_payload_present": False,
        "parser_payload_path_enabled": False,
        "parse_ultimate_runtime_config_payload_called": False,
        "parsed_payload_bytes_used": False,
        "candidate_materialization_present": True,
        "candidate_materialization_namespace_scope_initialized": True,
        "active_resolver_first_triggers_candidate_materialization": False,
        "candidate_state_validation_present": True,
        "candidate_equivalence_validation_present": True,
        "candidate_active_publication_enabled": True,
        "published_active_view_when_equivalent": "candidate.view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
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
    expected_chain = [
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "GetActiveRuntimeConfigState",
        "gActiveRuntimeConfigState.active_view",
    ]
    if payload.get("active_resolver_chain") != expected_chain:
        fail(f"diagnostic fixture active_resolver_chain mismatch: {payload.get('active_resolver_chain')!r}")


def validate_build_report_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_source_view_candidate_published_build_report",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "parser_payload_path_enabled": False,
        "parse_ultimate_runtime_config_payload_called": False,
        "source_owned_static_diagnostic_parsed_payload_present": False,
        "candidate_materialization_source": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "candidate_materialization_present": True,
        "candidate_materialization_namespace_scope_initialized": True,
        "active_resolver_first_triggers_candidate_materialization": False,
        "candidate_state_validation_present": True,
        "candidate_equivalence_validation_present": True,
        "candidate_active_publication_enabled": True,
        "published_active_view_when_equivalent": "candidate.view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "artifact_hashes_are_checker_gate": False,
        "hardware_result_claimed": False,
        "hardware_test_required": True,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"build report fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    expected_chain = [
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "GetActiveRuntimeConfigState",
        "gActiveRuntimeConfigState.active_view",
    ]
    if payload.get("active_resolver_chain") != expected_chain:
        fail(f"build report fixture active_resolver_chain mismatch: {payload.get('active_resolver_chain')!r}")
    if not isinstance(payload.get("artifact_hashes"), list):
        fail("build report fixture artifact_hashes must be a list")
    require_phrase(report_text, "Canonical command: pio run -e glyph_mk6", "build report")
    require_phrase(report_text, "Artifact hashes are local observations only, not checker gates.", "build report")
    require_phrase(report_text, "`artifact_hashes_are_checker_gate`: `false`", "build report")
    require_phrase(report_text, "Source-view candidate materialization/publication is namespace-scope initialized", "build report")
    require_phrase(report_text, "Active resolver chain does not first-trigger candidate materialization", "build report")
    require_phrase(report_text, "No hardware result is claimed", "build report")
    require_phrase(report_text, "Nunchuk remains NOT_TESTED", "build report")


def validate_hardware_plan_fixture(payload: dict[str, Any], plan_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_source_view_candidate_published_hardware_plan",
        "status": "HARDWARE_PLAN",
        "branch": EXPECTED_BRANCH,
        "branch_under_test": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "hardware_result_claimed": False,
        "overall_result": "NOT_TESTED",
        "nunchuk_status": "NOT_TESTED",
        "parser_payload_path_enabled": False,
        "candidate_materialization_source": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "candidate_active_publication_enabled": True,
        "published_active_view_when_equivalent": "candidate.view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"hardware plan fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail("hardware plan fixture rows must be a list")
    row_ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if row_ids != EXPECTED_HARDWARE_ROWS:
        fail(f"hardware plan rows mismatch: expected {EXPECTED_HARDWARE_ROWS!r}, got {row_ids!r}")
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware plan row must be an object")
        if row.get("status") != "NOT_TESTED":
            fail(f"hardware plan row {row.get('id')} must be NOT_TESTED")
        require_phrase(plan_text, f"| {row['id']} |", "hardware plan")
    for phrase in (
        "status: HARDWARE_PLAN",
        "overall_result: NOT_TESTED",
        "This is a hardware plan, not a result.",
        "All rows are NOT_TESTED.",
        "No hardware result is claimed.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(plan_text, phrase, "hardware plan")


def validate_hardware_failure_fixture(payload: dict[str, Any], result_text: str, label: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_source_view_candidate_published_hardware_failure",
        "status": "HARDWARE_FAIL",
        "overall_result": "HARDWARE_FAIL",
        "branch_under_test": EXPECTED_BRANCH,
        "result_branch": RESULT_BRANCH,
        "operator_report": "tested, failed. same disconnects happen. I reflashed an older working version for use.",
        "parser_payload_path_enabled": False,
        "parse_ultimate_runtime_config_payload_called": False,
        "ultimate_runtime_config_parser_included_or_used": False,
        "candidate_materialization_source": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "candidate_active_publication_enabled": True,
        "published_active_view_when_equivalent": "candidate.view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "source_view_candidate_publication_safe_for_merge": False,
        "candidate_backed_active_runtime_view_safe": False,
        "candidate_view_active_publication_reproduces_disconnect": True,
        "parser_payload_required_to_reproduce_disconnect": False,
        "candidate_materialization_presence_alone_sufficient_to_reproduce_disconnect": False,
        "source_owned_active_state_preselection_remains_repair_baseline": True,
        "parsed_candidate_presence_source_owned_published_remains_hardware_pass": True,
        "low_level_failure_mechanism_proven": False,
        "implementation_branch_merge_allowed": False,
        "requires_new_publication_model": True,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
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
        row_id = row.get("id")
        expected_status = EXPECTED_FAILURE_ROW_STATUSES.get(row_id)
        if row.get("status") != expected_status:
            fail(f"{label} row {row_id} must be {expected_status}, got {row.get('status')}")
        require_phrase(result_text, f"| {row_id} |", label)
        require_phrase(result_text, f"| {row_id} | {row['scope']} | {expected_status} |", label)

    for phrase in (
        "status: HARDWARE_FAIL",
        "overall_result: HARDWARE_FAIL",
        f"result_branch: `{RESULT_BRANCH}`",
        "tested, failed. same disconnects happen. I reflashed an older working version for use.",
        "candidate-backed active runtime view",
        "reproduces the disconnect class",
        "Parser payload parsing is not required to reproduce the failure.",
        "Candidate materialization presence alone is not sufficient",
        "prior parsed-candidate-present/source-owned-published",
        "`source_view_candidate_publication_safe_for_merge`: `false`",
        "`candidate_backed_active_runtime_view_safe`: `false`",
        "`parser_payload_required_to_reproduce_disconnect`: `false`",
        "`source_owned_active_state_preselection_remains_repair_baseline`: `true`",
        "`parsed_candidate_presence_source_owned_published_remains_hardware_pass`: `true`",
        "`implementation_branch_merge_allowed`: `false`",
        "`requires_new_publication_model`: `true`",
        "`low_level_failure_mechanism_proven`: `false`",
        "Runtime-loaded config is not implemented.",
        "Runtime-config storage is not implemented.",
        "WebSerial/device write is not implemented.",
        "backend/config.pb write path is not implemented.",
        "Firmware flashing automation is not implemented.",
        "The low-level failure mechanism is not proven.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(result_text, phrase, label)


def validate_docs_and_fixtures(branch: str) -> None:
    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    build_report = read_required(BUILD_REPORT_PATH)
    build_fixture = load_json_object(BUILD_REPORT_FIXTURE_PATH)
    hardware_plan = read_required(HARDWARE_PLAN_PATH)
    hardware_fixture = load_json_object(HARDWARE_PLAN_FIXTURE_PATH)
    readme = read_required(README_PATH)
    calibration_index = read_required(CALIBRATION_INDEX_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)

    result_mode = branch == RESULT_BRANCH or "status: HARDWARE_FAIL" in doc
    expected_doc_phrases = [
        "Parser payload activation is disabled and absent.",
        "ParseUltimateRuntimeConfigPayload(...) is not called.",
        "Candidate state is materialized from kSourceOwnedCurrentBaselineRuntimeConfig.",
        "Source-view candidate materialization/publication is namespace-scope initialized",
        "Candidate active publication is enabled only after materialization, validation, and source-owned equivalence pass.",
        "Published active view is candidate.view when the candidate is equivalent.",
        "Published active view falls back to kSourceOwnedCurrentBaselineRuntimeConfig",
        "Active resolver chain does not first-trigger candidate materialization.",
        "ResolveActiveRuntimeConfig() dereferences only the stable published ActiveRuntimeConfigState.active_view.",
        "UpdateAnalogOutputs(...) binds runtime config through ResolveActiveRuntimeConfig()",
        "Nunchuk remains NOT_TESTED.",
    ]
    if result_mode:
        expected_doc_phrases.extend(
            [
                "status: HARDWARE_FAIL",
                "overall_result: HARDWARE_FAIL",
                f"result_branch: `{RESULT_BRANCH}`",
                "tested, failed. same disconnects happen. I reflashed an older working version for use.",
                "publishing candidate-backed active runtime view/table pointers reproduces the disconnect class",
                "`parser_payload_required_to_reproduce_disconnect`: `false`",
                "`candidate_backed_active_runtime_view_safe`: `false`",
                "`implementation_branch_merge_allowed`: `false`",
                "`requires_new_publication_model`: `true`",
            ]
        )
    else:
        expected_doc_phrases.extend(
            [
                "status: WAITING_FOR_HARDWARE_TEST",
                "overall_result: NOT_TESTED",
                "No hardware result is claimed by this packet.",
            ]
        )
    for phrase in expected_doc_phrases:
        require_phrase(doc, phrase, "diagnostic doc")

    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
    ):
        require_phrase(text, "diagnostic_source_view_candidate_published", label)
        if result_mode:
            require_phrase(text, "HARDWARE_FAIL", label)
            require_phrase(text, "parser payload parsing is not required", label)
            require_phrase(text, "candidate-backed active runtime view", label)
        else:
            require_phrase(text, "WAITING_FOR_HARDWARE_TEST", label)

    validate_diagnostic_fixture(fixture)
    validate_build_report_fixture(build_fixture, build_report)
    if result_mode:
        hardware_failure = read_required(HARDWARE_FAILURE_PATH)
        hardware_failure_fixture = load_json_object(HARDWARE_FAILURE_FIXTURE_PATH)
        validate_hardware_failure_fixture(hardware_fixture, hardware_plan, "calibration hardware failure")
        validate_hardware_failure_fixture(hardware_failure_fixture, hardware_failure, "runtime config hardware failure")
    else:
        validate_hardware_plan_fixture(hardware_fixture, hardware_plan)


def main() -> None:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch), branch)
    validate_source(read_required(ULTIMATE_PATH), branch)
    validate_docs_and_fixtures(branch)
    print("diagnostic source-view candidate published checks passed")


if __name__ == "__main__":
    main()
