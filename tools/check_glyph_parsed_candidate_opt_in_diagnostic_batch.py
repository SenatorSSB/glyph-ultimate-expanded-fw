#!/usr/bin/env python3
"""Validate the parsed candidate opt-in diagnostic batch."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-parsed-candidate-opt-in-diagnostic-batch"
RESULT_BRANCH = "runtime-config-parsed-candidate-opt-in-diagnostic-batch-hardware-failure"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, RESULT_BRANCH, MERGED_BRANCH}

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
DOC_PATH = REPO_ROOT / "docs/runtime_config/parsed_candidate_opt_in_diagnostic_batch.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/parsed_candidate_opt_in_diagnostic_batch.json"
BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/parsed_candidate_opt_in_diagnostic_batch_build_report_2026-06-10.md"
BUILD_REPORT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/parsed_candidate_opt_in_diagnostic_batch_build_report_2026-06-10.json"
HARDWARE_PLAN_PATH = REPO_ROOT / "docs/calibration/parsed_candidate_opt_in_diagnostic_batch_hardware_plan_2026-06-10.md"
HARDWARE_PLAN_FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/parsed_candidate_opt_in_diagnostic_batch_hardware_plan_2026-06-10.json"
HARDWARE_FAILURE_PATH = REPO_ROOT / "docs/runtime_config/parsed_candidate_opt_in_diagnostic_batch_hardware_failure_2026-06-10.md"
HARDWARE_FAILURE_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/parsed_candidate_opt_in_diagnostic_batch_hardware_failure_2026-06-10.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
WORKFLOW_PATH = REPO_ROOT / "docs/WORKFLOW.md"

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigCandidate.hpp",
    "src/modes/UltimateRuntimeConfigActivation.hpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "tools/check_glyph_parsed_candidate_opt_in_diagnostic_batch.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")
FORBIDDEN_CHANGED_RE = re.compile(r"(^|/)(hal|backend|config\.pb|storage|write|flashing)(/|$)", re.I)

REQUIRED_HARDWARE_ROWS = {
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "UNRELATED-BUTTONS-001",
    "MODIFIERS-001",
    "ACTIVE-STATE-001",
    "PUBLICATION-001",
    "CANDIDATE-BRIDGE-001",
    "CANDIDATE-EQUIVALENCE-001",
    "OPT-IN-ACTIVATION-001",
    "HOT-PATH-001",
    "NO-PARSER-STATUS-READ-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}

REQUIRED_FAILURE_ROWS = {
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "LT6-001",
    "OPT-IN-ACTIVATION-001",
    "HOT-PATH-001",
    "NO-PARSER-STATUS-READ-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}

EXPECTED_FAILURE_ROW_RESULTS = {
    "BOOT-001": "UNKNOWN",
    "BASELINE-001": "FAIL",
    "RF5-001": "UNKNOWN",
    "RF6-001": "UNKNOWN",
    "LT6-001": "UNKNOWN",
    "OPT-IN-ACTIVATION-001": "FAIL",
    "HOT-PATH-001": "INVESTIGATE",
    "NO-PARSER-STATUS-READ-001": "PASS",
    "NO-STORAGE-001": "PASS",
    "NO-WRITE-001": "PASS",
    "NO-FLASH-001": "PASS",
    "NUNCHUK-001": "NOT_TESTED",
}

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
    "new RuntimeConfig",
    "malloc(",
    "calloc(",
    "realloc(",
)

FORBIDDEN_DOC_CLAIMS = (
    r"\bruntime-loaded config (?:is |was |has been )?implemented\b",
    r"\bruntime config storage (?:is |was |has been )?implemented\b",
    r"\bstorage (?:is |was |has been )?implemented\b",
    r"\bWebSerial/device write (?:is |was |has been )?implemented\b",
    r"\bdevice write (?:is |was |has been )?implemented\b",
    r"\bbackend/config\.pb write (?:is |was |has been )?implemented\b",
    r"\bflashing automation (?:is |was |has been )?implemented\b",
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


class ParsedCandidateDiagnosticError(AssertionError):
    """Raised when parsed candidate diagnostic guardrails are violated."""


def fail(message: str) -> None:
    raise ParsedCandidateDiagnosticError(message)


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


def validate_branch() -> tuple[str, str]:
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
        return branch, BASE_BRANCH
    if branch == RESULT_BRANCH:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", EXPECTED_BRANCH, "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{EXPECTED_BRANCH} must be an ancestor of HEAD for the hardware failure result branch")
        return branch, EXPECTED_BRANCH
    return branch, BASE_BRANCH


def changed_paths(diff_base: str) -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{diff_base}...HEAD"]))
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
            fail(f"forbidden HAL/backend/config.pb/storage/write/flashing path changed: {path}")
        if branch == MERGED_BRANCH:
            continue
        if branch == RESULT_BRANCH and path.startswith("src/"):
            fail(f"hardware failure result branch must not change firmware source relative to {EXPECTED_BRANCH}: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"parsed candidate diagnostic branch changed out-of-scope path: {path}")


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

    required_tokens = (
        "kParsedCandidateOptInDiagnosticPayload",
        "UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload",
        "MaterializeRuntimeConfigCandidateFromParsedPayload",
        "RuntimeConfigActivationDecisionStatus::CandidateUnavailable",
        "RuntimeConfigActivationDecisionStatus::CandidateAccepted",
        "RuntimeConfigActivationDecisionStatus::CandidateRejected",
        "RuntimeConfigActivationDecisionStatus::SourceOwnedFallback",
        "struct RuntimeConfigActivationDecision",
        "RuntimeConfigViewsEquivalentEveryPoint",
        "PublishedRuntimeConfigState",
        "PublishRuntimeConfigState",
        "InitializePublishedRuntimeConfigState",
        "gParsedCandidateOptInDiagnosticCandidate",
        "gPublishedRuntimeConfigState",
        "gActiveRuntimeConfigState",
        "constexpr bool kEnableParsedCandidateActivationDiagnostic = true;",
    )
    for token in required_tokens:
        if token not in active_source:
            fail(f"parsed candidate diagnostic source missing token: {token}")

    bridge_body = strip_cpp_comments(extract_function(source, "MaterializeRuntimeConfigCandidateFromParsedPayload"))
    if "ParseUltimateRuntimeConfigPayload(payload, length)" not in bridge_body:
        fail("candidate parser bridge must parse the supplied payload before materialization")
    if "candidate.points[table_index][point_index]" not in bridge_body:
        fail("candidate parser bridge must materialize candidate points")

    equivalence_body = strip_cpp_comments(extract_function(source, "RuntimeConfigViewsEquivalentEveryPoint"))
    for token in (
        "candidate.table_count != source.table_count",
        "candidate.fallback_table_id != source.fallback_table_id",
        "table_index < kRuntimeTableCount",
        "point_index < kRuntimeTablePointCount",
        "candidate_point.x != source_point.x",
        "candidate_point.y != source_point.y",
        "candidate_table.point_count != source_table.point_count",
    ):
        if token not in equivalence_body:
            fail(f"inactive equivalence validation missing token: {token}")

    decision_body = strip_cpp_comments(extract_function(source, "DecideRuntimeConfigActivation"))
    if "RuntimeConfigViewsEquivalentEveryPoint(candidate.view, source_view)" not in decision_body:
        fail("candidate decision must require source-owned baseline equivalence")
    if "RuntimeConfigActivationDecisionStatus::CandidateAccepted" not in decision_body:
        fail("candidate decision must include accepted status")

    init_body = strip_cpp_comments(extract_function(source, "InitializePublishedRuntimeConfigState"))
    if "MaterializeRuntimeConfigCandidateFromParsedPayload" not in init_body:
        fail("publication initializer must materialize through parser bridge")
    if "DecideRuntimeConfigActivation" not in init_body or "PublishRuntimeConfigState" not in init_body:
        fail("candidate activation must go through decision/publication boundary")
    if (
        "const PublishedRuntimeConfigState gPublishedRuntimeConfigState =\n"
        "    InitializePublishedRuntimeConfigState(gParsedCandidateOptInDiagnosticCandidate);"
    ) not in active_source:
        fail("publication must be initialized at namespace scope, outside the hot-path resolver chain")
    if (
        "const ActiveRuntimeConfigState gActiveRuntimeConfigState = {\n"
        "    gPublishedRuntimeConfigState.active_view,"
    ) not in active_source:
        fail("active runtime config state must be namespace-scope state derived from published state")

    publish_body = strip_cpp_comments(extract_function(source, "PublishRuntimeConfigState"))
    if "RuntimeConfigActivationStatus::ParsedCandidateSelected" not in publish_body:
        fail("publication scaffold must publish parsed candidate diagnostic status")

    published_accessor_body = strip_cpp_comments(extract_function(source, "GetPublishedRuntimeConfigState"))
    if "return gPublishedRuntimeConfigState;" not in published_accessor_body:
        fail("GetPublishedRuntimeConfigState must return already-initialized namespace-scope state")
    for token in (
        "static",
        "InitializePublishedRuntimeConfigState",
        "MaterializeRuntimeConfigCandidateFromParsedPayload",
        "ParseUltimateRuntimeConfigPayload",
        "DecideRuntimeConfigActivation",
        "PublishRuntimeConfigState",
    ):
        if token in published_accessor_body:
            fail(f"GetPublishedRuntimeConfigState must not first-trigger publication work: {token}")

    active_accessor_body = strip_cpp_comments(extract_function(source, "GetActiveRuntimeConfigState"))
    if "return gActiveRuntimeConfigState;" not in active_accessor_body:
        fail("GetActiveRuntimeConfigState must return already-initialized namespace-scope active state")
    for token in (
        "static",
        "GetPublishedRuntimeConfigState",
        "InitializePublishedRuntimeConfigState",
        "MaterializeRuntimeConfigCandidateFromParsedPayload",
        "ParseUltimateRuntimeConfigPayload",
        "DecideRuntimeConfigActivation",
        "PublishRuntimeConfigState",
    ):
        if token in active_accessor_body:
            fail(f"GetActiveRuntimeConfigState must not first-trigger publication work: {token}")

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must return only the stable active view")
    for token in (
        "Parse",
        "Parser",
        "Candidate",
        "candidate",
        "Decision",
        "decision",
        "status",
        "source",
        "activation",
        "CRC",
        "load",
        "storage",
        "write",
    ):
        if token in resolve_body:
            fail(f"ResolveActiveRuntimeConfig must not inspect parser/candidate/decision state: {token}")

    hot_path_lazy_init_re = re.compile(
        r"static\s+(?:const\s+)?[A-Za-z0-9_:<>&*\s]+\s+[A-Za-z0-9_]+\s*=\s*"
        r"(?:InitializePublishedRuntimeConfigState|MaterializeRuntimeConfigCandidateFromParsedPayload|"
        r"ParseUltimateRuntimeConfigPayload|DecideRuntimeConfigActivation|PublishRuntimeConfigState)\b",
        flags=re.S,
    )
    for function_name in ("GetPublishedRuntimeConfigState", "GetActiveRuntimeConfigState", "ResolveActiveRuntimeConfig"):
        function_body = strip_cpp_comments(extract_function(source, function_name))
        if hot_path_lazy_init_re.search(function_body):
            fail(f"{function_name} has function-local static initialization that can first-trigger publication work")

    update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in update_body:
        fail("UpdateAnalogOutputs must bind runtime_config through ResolveActiveRuntimeConfig()")
    for token in (
        "parser",
        "Parser",
        "parse",
        "Parse",
        "candidate",
        "Candidate",
        "activation",
        "Activation",
        "decision",
        "Decision",
        "status",
        "Status",
        "CRC",
        "crc",
        "load",
        "Load",
        "storage",
        "Storage",
        "write",
        "Write",
        "WebSerial",
        "flash",
        "Flash",
    ):
        if token in update_body:
            fail(f"UpdateAnalogOutputs must not mention forbidden hot-path token: {token}")

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


def require_phrase(text: str, phrase: str, label: str) -> None:
    compact_text = re.sub(r"\s+", " ", text).strip().lower()
    compact_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
    if compact_phrase not in compact_text:
        fail(f"{label} missing required phrase: {phrase}")


def validate_doc_claims(paths: list[Path]) -> None:
    for path in paths:
        text = read_required(path)
        lowered = text.lower()
        if "nunchuk remains not_tested" not in lowered:
            fail(f"{rel(path)} must preserve nunchuk remains NOT_TESTED wording")
        for pattern in FORBIDDEN_DOC_CLAIMS:
            for match in re.finditer(pattern, text, flags=re.I):
                prefix = text[max(0, match.start() - 48) : match.start()].lower()
                if not any(prefix.endswith(marker) or marker in prefix[-32:] for marker in NEGATING_CONTEXT):
                    fail(f"{rel(path)} contains forbidden positive claim: {match.group(0)!r}")


def validate_main_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_parsed_candidate_opt_in_diagnostic_batch",
        "status": "hardware_test_ready",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "candidate_parser_bridge": "MaterializeRuntimeConfigCandidateFromParsedPayload",
        "candidate_fixture": "kParsedCandidateOptInDiagnosticPayload",
        "candidate_fixture_source": "source_owned_static_diagnostic_data",
        "diagnostic_opt_in_flag": "kEnableParsedCandidateActivationDiagnostic",
        "diagnostic_opt_in_enabled": True,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_implemented": False,
        "flashing_automation_implemented": False,
        "candidate_activation_can_affect_active_output": True,
        "hardware_test_required_before_merge": True,
        "hardware_result_recorded": False,
        "publication_boundary": "PublishedRuntimeConfigState",
        "publication_initialization": "namespace_scope_before_output_generation",
        "function_local_static_publication_in_hot_path_chain": False,
        "active_output_path_consumes_only_published_active_view": True,
        "update_analog_outputs_reads_parser_candidate_decision_state": False,
        "resolve_active_runtime_config_reads_parser_candidate_decision_state": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    requirements = payload.get("equivalence_requirements")
    if not isinstance(requirements, list):
        fail("fixture equivalence_requirements must be a list")
    for required in (
        "every runtime table",
        "every 9-way point",
        "candidate point equals source-owned baseline point",
        "table count and point count match",
        "fallback table id matches",
    ):
        if required not in requirements:
            fail(f"fixture equivalence_requirements missing {required!r}")
    expected_chain = [
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "GetActiveRuntimeConfigState",
        "gActiveRuntimeConfigState.active_view",
    ]
    if payload.get("hot_path_resolver_chain_after_fix") != expected_chain:
        fail("fixture hot_path_resolver_chain_after_fix does not match the fixed resolver chain")


def validate_result_main_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_parsed_candidate_opt_in_diagnostic_batch",
        "status": "hardware_fail_recorded",
        "branch": EXPECTED_BRANCH,
        "result_branch": RESULT_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "candidate_parser_bridge": "MaterializeRuntimeConfigCandidateFromParsedPayload",
        "candidate_fixture": "kParsedCandidateOptInDiagnosticPayload",
        "candidate_fixture_source": "source_owned_static_diagnostic_data",
        "diagnostic_opt_in_flag": "kEnableParsedCandidateActivationDiagnostic",
        "diagnostic_opt_in_enabled": True,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_implemented": False,
        "flashing_automation_implemented": False,
        "candidate_activation_can_affect_active_output": True,
        "hardware_test_required_before_merge": True,
        "hardware_result_recorded": True,
        "overall_result": "HARDWARE_FAIL",
        "operator_report": "tested, fails. disconnects happen",
        "implementation_branch_merge_allowed": False,
        "parsed_candidate_opt_in_activation_safe_for_merge": False,
        "publication_boundary": "PublishedRuntimeConfigState",
        "publication_initialization": "namespace_scope_before_output_generation",
        "function_local_static_publication_in_hot_path_chain": False,
        "active_output_path_consumes_only_published_active_view": True,
        "update_analog_outputs_reads_parser_candidate_decision_state": False,
        "resolve_active_runtime_config_reads_parser_candidate_decision_state": False,
        "source_owned_active_state_preselection_remains_repair_baseline": True,
        "candidate_materialization_inactive_path_remains_next_safe_baseline": True,
        "low_level_failure_mechanism_proven": False,
        "requires_new_root_cause_analysis": True,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"result fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    expected_chain = [
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "GetActiveRuntimeConfigState",
        "gActiveRuntimeConfigState.active_view",
    ]
    if payload.get("hot_path_resolver_chain_after_fix") != expected_chain:
        fail("result fixture hot_path_resolver_chain_after_fix does not match the fixed resolver chain")


def validate_build_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected = {
        "schema_name": "glyph_parsed_candidate_opt_in_diagnostic_batch_build_report",
        "status": "build_pass",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "canonical_command_available": False,
        "actual_local_build_command": "./scripts/build-glyph-mk6-quiet.sh",
        "build_exit_code": 0,
        "build_result": "PASS",
        "hardware_result_recorded": False,
        "hardware_test_required_before_merge": True,
        "publication_initialization": "namespace_scope_before_output_generation",
        "function_local_static_publication_in_hot_path_chain": False,
        "artifact_hashes_are_checker_gate": False,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"build fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    if "`pio run -e glyph_mk6`" not in report_text:
        fail("build report must record canonical command `pio run -e glyph_mk6`")
    if "local observations only and are not checker gates" not in report_text:
        fail("build report must state artifact hashes are local observations only")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or {item.get("kind") for item in artifacts if isinstance(item, dict)} != {"uf2", "elf", "bin"}:
        fail("build fixture must record uf2/elf/bin artifact observations")


def rows_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("test_rows")
    if not isinstance(rows, list):
        fail("hardware fixture must contain test_rows list")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware fixture rows must be objects")
        row_id = row.get("row_id")
        if not isinstance(row_id, str):
            fail("hardware fixture row missing string row_id")
        if row_id in result:
            fail(f"duplicate hardware row id: {row_id}")
        result[row_id] = row
    return result


def validate_hardware_plan(payload: dict[str, Any], plan_text: str) -> None:
    expected = {
        "schema_name": "glyph_parsed_candidate_opt_in_diagnostic_batch_hardware_plan",
        "status": "hardware_plan_not_tested",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "hardware_result_recorded": False,
        "hardware_test_required_before_merge": True,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"hardware fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    rows = rows_by_id(payload)
    if set(rows) != REQUIRED_HARDWARE_ROWS:
        fail(f"hardware rows mismatch: expected {sorted(REQUIRED_HARDWARE_ROWS)}, got {sorted(rows)}")
    for row_id, row in rows.items():
        if row.get("result") != "NOT_TESTED":
            fail(f"hardware row {row_id} must remain NOT_TESTED")
        if f"| {row_id} |" not in plan_text:
            fail(f"hardware plan markdown missing row {row_id}")
    if "| NUNCHUK-001 |" not in plan_text or "Nunchuk remains NOT_TESTED" not in plan_text:
        fail("hardware plan must preserve NUNCHUK-001 NOT_TESTED scope")


def validate_hardware_failure_fixture(payload: dict[str, Any], failure_text: str) -> None:
    expected = {
        "schema_name": "glyph_parsed_candidate_opt_in_diagnostic_batch_hardware_failure",
        "status": "hardware_fail",
        "overall_result": "HARDWARE_FAIL",
        "branch_under_test": EXPECTED_BRANCH,
        "result_branch": RESULT_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "operator_report": "tested, fails. disconnects happen",
        "diagnostic_opt_in_enabled": True,
        "publication_initialization": "namespace_scope_before_output_generation",
        "publication_first_triggered_from_resolve_active_runtime_config": False,
        "active_output_path_consumes_only_published_active_view": True,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_implemented": False,
        "flashing_automation_implemented": False,
        "hardware_result_recorded": True,
        "implementation_branch_merge_allowed": False,
        "parsed_candidate_opt_in_activation_safe_for_merge": False,
        "source_owned_active_state_preselection_remains_repair_baseline": True,
        "candidate_materialization_inactive_path_remains_next_safe_baseline": True,
        "low_level_failure_mechanism_proven": False,
        "requires_new_root_cause_analysis": True,
        "root_cause_not_claimed": "parser status hot-path read",
        "nunchuk_status": "NOT_TESTED",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"hardware failure fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    rows = rows_by_id(payload)
    if set(rows) != REQUIRED_FAILURE_ROWS:
        fail(f"hardware failure rows mismatch: expected {sorted(REQUIRED_FAILURE_ROWS)}, got {sorted(rows)}")
    for row_id, expected_result in EXPECTED_FAILURE_ROW_RESULTS.items():
        if rows[row_id].get("result") != expected_result:
            fail(f"hardware failure row {row_id} expected {expected_result}, got {rows[row_id].get('result')}")
        if f"| {row_id} |" not in failure_text:
            fail(f"hardware failure markdown missing row {row_id}")
    for phrase in (
        "operator_report: \"tested, fails. disconnects happen\"",
        "The implementation branch must not be merged into `configurator`.",
        "Parsed candidate publication/activation still triggers the disconnect class even",
        "Do not claim the root cause is parser status hot-path reads.",
        "low-level failure mechanism remains unproven",
        "Nunchuk remains NOT_TESTED",
    ):
        require_phrase(failure_text, phrase, "hardware failure packet")


def validate_result_hardware_plan(payload: dict[str, Any], plan_text: str) -> None:
    expected = {
        "schema_name": "glyph_parsed_candidate_opt_in_diagnostic_batch_hardware_plan",
        "status": "hardware_fail_recorded",
        "branch": EXPECTED_BRANCH,
        "branch_under_test": EXPECTED_BRANCH,
        "result_branch": RESULT_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "hardware_result_recorded": True,
        "overall_result": "HARDWARE_FAIL",
        "operator_report": "tested, fails. disconnects happen",
        "hardware_test_required_before_merge": True,
        "implementation_branch_merge_allowed": False,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
        "parsed_candidate_opt_in_activation_safe_for_merge": False,
        "source_owned_active_state_preselection_remains_repair_baseline": True,
        "candidate_materialization_inactive_path_remains_next_safe_baseline": True,
        "low_level_failure_mechanism_proven": False,
        "requires_new_root_cause_analysis": True,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"result hardware plan fixture {key!r} mismatch: expected {value!r}, got {payload.get(key)!r}")
    rows = rows_by_id(payload)
    if set(rows) != REQUIRED_HARDWARE_ROWS:
        fail(f"result hardware plan rows mismatch: expected {sorted(REQUIRED_HARDWARE_ROWS)}, got {sorted(rows)}")
    for row_id, expected_result in EXPECTED_FAILURE_ROW_RESULTS.items():
        if rows[row_id].get("result") != expected_result:
            fail(f"result hardware plan row {row_id} expected {expected_result}, got {rows[row_id].get('result')}")
    for phrase in (
        "status: HARDWARE_FAIL_RECORDED",
        "operator report: \"tested, fails. disconnects happen\"",
        "must not be merged into `configurator`",
        "Parsed candidate publication/activation still triggers the disconnect class",
        "low-level failure mechanism is not proven",
        "Nunchuk remains NOT_TESTED",
    ):
        require_phrase(plan_text, phrase, "hardware plan result")


def validate_docs_and_fixtures(branch: str) -> None:
    doc = read_required(DOC_PATH)
    fixture = load_json_object(FIXTURE_PATH)
    build_report = read_required(BUILD_REPORT_PATH)
    build_fixture = load_json_object(BUILD_REPORT_FIXTURE_PATH)
    hardware_plan = read_required(HARDWARE_PLAN_PATH)
    hardware_fixture = load_json_object(HARDWARE_PLAN_FIXTURE_PATH)
    hardware_failure = read_required(HARDWARE_FAILURE_PATH) if branch == RESULT_BRANCH else ""
    hardware_failure_fixture = load_json_object(HARDWARE_FAILURE_FIXTURE_PATH) if branch == RESULT_BRANCH else {}
    readme = read_required(README_PATH)
    calibration_index = read_required(CALIBRATION_INDEX_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)
    workflow = read_required(WORKFLOW_PATH)

    required_doc_phrases = [
        "kParsedCandidateOptInDiagnosticPayload",
        "MaterializeRuntimeConfigCandidateFromParsedPayload",
        "RuntimeConfigActivationDecision",
        "PublishedRuntimeConfigState",
        "gPublishedRuntimeConfigState",
        "gActiveRuntimeConfigState",
        "Parser/materialization/decision/publication work is not first-triggered by the analog hot-path resolver chain.",
        "UpdateAnalogOutputs -> ResolveActiveRuntimeConfig -> GetActiveRuntimeConfigState -> gActiveRuntimeConfigState.active_view",
        "constexpr bool kEnableParsedCandidateActivationDiagnostic = true;",
        "Nunchuk remains NOT_TESTED.",
    ]
    if branch == RESULT_BRANCH:
        required_doc_phrases.extend([
            "status: HARDWARE_FAIL_RECORDED",
            "Hardware testing failed on result branch",
            "The implementation branch must not be merged into `configurator`.",
            "Parsed candidate publication/activation still triggers the disconnect class",
            "Do not claim the root cause is parser status hot-path reads.",
        ])
    else:
        required_doc_phrases.extend([
            "status: HARDWARE_TEST_READY",
            "Hardware test is required before merge because parsed candidate opt-in activation can affect active output behavior.",
        ])
    for phrase in required_doc_phrases:
        require_phrase(doc, phrase, "parsed candidate diagnostic doc")
    navigation_requirements = [
        ("parsed_candidate_opt_in_diagnostic_batch.md", "runtime README"),
        ("parsed_candidate_opt_in_diagnostic_batch_hardware_plan_2026-06-10.md", "calibration index"),
        ("decision/publication boundary", "workflow"),
    ]
    if branch == RESULT_BRANCH:
        navigation_requirements.extend([
            ("parsed_candidate_opt_in_diagnostic_batch_hardware_failure_2026-06-10.md", "runtime README"),
            ("parsed_candidate_opt_in_diagnostic_batch_hardware_failure_2026-06-10.md", "calibration index"),
            ("HARDWARE_FAIL", "roadmap"),
            ("must not merge", "current state"),
        ])
    else:
        navigation_requirements.extend([
            ("WAITING_FOR_HARDWARE_TEST", "current state"),
            ("WAITING_FOR_HARDWARE_TEST", "roadmap"),
        ])
    for phrase, label in navigation_requirements:
        require_phrase(
            {
                "runtime README": readme,
                "calibration index": calibration_index,
                "current state": current_state,
                "roadmap": roadmap,
                "workflow": workflow,
            }[label],
            phrase,
            label,
        )

    if branch == RESULT_BRANCH:
        validate_result_main_fixture(fixture)
        validate_result_hardware_plan(hardware_fixture, hardware_plan)
        validate_hardware_failure_fixture(hardware_failure_fixture, hardware_failure)
    else:
        validate_main_fixture(fixture)
        validate_hardware_plan(hardware_fixture, hardware_plan)
    validate_build_fixture(build_fixture, build_report)
    doc_claim_paths = [
        DOC_PATH,
        FIXTURE_PATH,
        BUILD_REPORT_PATH,
        BUILD_REPORT_FIXTURE_PATH,
        HARDWARE_PLAN_PATH,
        HARDWARE_PLAN_FIXTURE_PATH,
        README_PATH,
        CALIBRATION_INDEX_PATH,
        CURRENT_STATE_PATH,
        ROADMAP_PATH,
        WORKFLOW_PATH,
    ]
    if branch == RESULT_BRANCH:
        doc_claim_paths.extend([HARDWARE_FAILURE_PATH, HARDWARE_FAILURE_FIXTURE_PATH])
    validate_doc_claims(doc_claim_paths)


def main() -> None:
    branch, diff_base = validate_branch()
    paths = changed_paths(diff_base)
    validate_changed_paths(paths, branch)
    validate_source(read_required(ULTIMATE_PATH))
    validate_docs_and_fixtures(branch)
    print("parsed candidate opt-in diagnostic batch checks passed")


if __name__ == "__main__":
    main()
