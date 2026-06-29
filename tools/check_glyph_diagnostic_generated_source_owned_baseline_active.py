#!/usr/bin/env python3
"""Validate the generated source-owned baseline active diagnostic branch."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-diagnostic-generated-source-owned-baseline-active"
RESULT_BRANCH = "runtime-config-diagnostic-generated-source-owned-baseline-active-hardware-failure"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
RESULT_BRANCH_BASE = EXPECTED_BRANCH

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
WRAPPER_PATH = (
    REPO_ROOT
    / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaselineActiveView.current.hpp"
)
ARTIFACT_PATH = (
    REPO_ROOT
    / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
)
DOC_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_generated_source_owned_baseline_active.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/diagnostic_generated_source_owned_baseline_active.json"
)
BUILD_REPORT_PATH = (
    REPO_ROOT
    / "docs/runtime_config/diagnostic_generated_source_owned_baseline_active_build_report_2026-06-29.md"
)
BUILD_REPORT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/diagnostic_generated_source_owned_baseline_active_build_report_2026-06-29.json"
)
HARDWARE_FAILURE_PATH = (
    REPO_ROOT
    / "docs/runtime_config/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md"
)
HARDWARE_FAILURE_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.json"
)
HARDWARE_PLAN_PATH = (
    REPO_ROOT
    / "docs/calibration/diagnostic_generated_source_owned_baseline_active_hardware_plan_2026-06-29.md"
)
HARDWARE_PLAN_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/diagnostic_generated_source_owned_baseline_active_hardware_plan_2026-06-29.json"
)
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
BASELINE_CHECKER = REPO_ROOT / "tools/check_glyph_generated_source_owned_baseline_artifact.py"

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/check_glyph_diagnostic_generated_source_owned_baseline_active.py",
    "tools/check_glyph_diagnostic_active_storage_published.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
}
ALLOWED_PREFIXES = (
    "docs/runtime_config/",
    "docs/calibration/",
    "src/modes/runtime_config/generated_source_owned/",
)
RESULT_BRANCH_ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/calibration/INDEX.md",
    "docs/runtime_config/README.md",
    "docs/runtime_config/diagnostic_generated_source_owned_baseline_active.md",
    "docs/runtime_config/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md",
    "docs/runtime_config/fixtures/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.json",
    "tools/check_glyph_diagnostic_generated_source_owned_baseline_active.py",
}
FORBIDDEN_CHANGED_RE = re.compile(
    r"(^|/)(?:HAL|hal|backend|config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
FORBIDDEN_SOURCE_CHANGED_RE = re.compile(
    r"^(?:src|lib|include|HAL|hal|backend)(?:/|$)|(?:^|/)config\.pb(?:/|$)"
)
GENERATED_SOURCE_RE = re.compile(
    r"^src/modes/runtime_config/generated_source_owned/[A-Za-z0-9_.-]+\.(?:h|hpp|hh|cc|cpp)$"
)

HOT_PATH_FORBIDDEN_TOKENS = (
    "candidate",
    "Candidate",
    "parser",
    "Parse",
    "decision",
    "status",
    "load",
    "storage",
    "Storage",
    "write",
    "Write",
    "WebSerial",
    "webserial",
    "flash",
    "Flash",
)
SOURCE_FORBIDDEN_TOKENS = (
    "UltimateRuntimeConfigParser",
    "ParseUltimateRuntimeConfigPayload",
    "kDiagnosticSourceOwnedParsedPayload",
    "kDiagnosticParsedCandidateState",
    "InitializeDiagnosticParsedCandidateState",
    "ParsedPayloadValid",
    "ParsedPayloadEquivalent",
)
GET_STATE_FORBIDDEN_TOKENS = (
    "candidate",
    "Candidate",
    "parser",
    "Parse",
    "decision",
    "Materialize",
    "status ==",
    ".status",
    "active_storage",
    "ActiveStorage",
)

EXPECTED_EVIDENCE_MATRIX = {
    "source_owned_active_state_preselection": "HARDWARE_PASS",
    "parsed_candidate_machinery_present_source_owned_active_view": "HARDWARE_PASS",
    "parsed_candidate_view_active": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active": "HARDWARE_FAIL",
    "dedicated_active_storage_published_active": "HARDWARE_FAIL",
}
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
    "GENERATED-SOURCE-OWNED-BASELINE-ACTIVE-001",
    "GENERATED-BASELINE-EQUIVALENT-001",
    "RAM-BACKED-ACTIVE-TABLE-NOT-USED-001",
    "CANDIDATE-NOT-ACTIVE-001",
    "HOT-PATH-001",
    "NO-PARSER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
]


class DiagnosticGeneratedSourceOwnedBaselineActiveError(AssertionError):
    """Raised when the generated source-owned active diagnostic drifts."""


def fail(message: str) -> None:
    raise DiagnosticGeneratedSourceOwnedBaselineActiveError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            fail(f"duplicate JSON key: {key}")
        values[key] = value
    return values


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=reject_duplicate_object_pairs)
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
    if branch not in {EXPECTED_BRANCH, RESULT_BRANCH, MERGED_BRANCH}:
        fail(f"checker must run on {EXPECTED_BRANCH}, {RESULT_BRANCH}, or {MERGED_BRANCH}, got {branch}")
    ancestor = RESULT_BRANCH_BASE if branch == RESULT_BRANCH else BASE_BRANCH
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{ancestor} must be an ancestor of HEAD")
    return branch


def status_path(status_line: str) -> str:
    path = status_line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def changed_paths(branch: str) -> set[str]:
    diff_base = RESULT_BRANCH_BASE if branch == RESULT_BRANCH else BASE_BRANCH
    paths = set(git_lines(["diff", "--name-only", f"{diff_base}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path:
            paths.add(path)
    if branch == MERGED_BRANCH and not paths:
        return set()
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    if current_branch() == RESULT_BRANCH:
        for path in sorted(paths):
            if FORBIDDEN_SOURCE_CHANGED_RE.search(path):
                fail(f"source path changed on failure-result branch: {path}")
            if FORBIDDEN_CHANGED_RE.search(path):
                fail(f"unsupported storage/write/WebSerial/flashing path changed on failure-result branch: {path}")
            if path not in RESULT_BRANCH_ALLOWED_EXACT_CHANGED_PATHS:
                fail(f"failure-result branch may change only docs/checker paths, got: {path}")
        return
    for path in sorted(paths):
        if FORBIDDEN_CHANGED_RE.search(path):
            fail(f"forbidden HAL/backend/config.pb/storage/write/WebSerial/flashing path changed: {path}")
        if path.startswith("src/modes/runtime_config/generated_source_owned/") and not GENERATED_SOURCE_RE.match(path):
            fail(f"generated source-owned path is outside allowed source shape: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
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
    pattern = rf"\b{re.escape(name)}\b\s*\([^\)]*\)\s*(?:const\s*)?\{{"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing function: {name}()")
    pos = text.find("{", match.end() - 1)
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


def forbid_tokens(text: str, tokens: tuple[str, ...], label: str) -> None:
    for token in tokens:
        if token in text:
            fail(f"{label} must not mention {token}")


def require_phrase(text: str, phrase: str, label: str) -> None:
    compact_text = re.sub(r"\s+", " ", text).strip().lower()
    compact_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
    if compact_phrase not in compact_text:
        fail(f"{label} missing phrase: {phrase}")


def validate_source() -> None:
    source = read_required(ULTIMATE_PATH)
    active_source = strip_cpp_comments(source)
    wrapper = strip_cpp_comments(read_required(WRAPPER_PATH))
    artifact = read_required(ARTIFACT_PATH)

    require_token(
        source,
        '#include "modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaselineActiveView.current.hpp"',
        "Ultimate.cpp",
    )
    require_token(wrapper, '#include "GeneratedRuntimeConfigBaseline.current.hpp"', rel(WRAPPER_PATH))
    for token in (
        "constexpr StickPoint kGeneratedSourceOwnedBaselineRuntimePoints",
        "constexpr RuntimeTableView kGeneratedSourceOwnedBaselineRuntimeTables",
        "constexpr RuntimeConfigView kGeneratedSourceOwnedBaselineRuntimeConfig",
        "ValidateRuntimeConfigView(kGeneratedSourceOwnedBaselineRuntimeConfig)",
    ):
        require_token(wrapper, token, rel(WRAPPER_PATH))
    for token in (
        "RuntimeConfigCandidateState",
        "RuntimeConfigActiveStorage",
        "CopyRuntimeConfigViewIntoActiveStorage",
    ):
        if re.search(rf"&(?:g|k)?{token}|active_view\s*=\s*[^;\n]*{token}", active_source):
            fail(f"{token} must not be assigned to active view")
    for token in SOURCE_FORBIDDEN_TOKENS:
        if token in active_source or token in wrapper:
            fail(f"forbidden parser/payload token present: {token}")
    if re.search(r"\bparser_payload\b|\bpayload_bytes\b|uint8_t\s+\w*Payload", active_source + "\n" + wrapper):
        fail("parser payload bytes must not be defined")

    get_state_body = strip_cpp_comments(extract_function(source, "GetActiveRuntimeConfigState"))
    require_token(get_state_body, "&kGeneratedSourceOwnedBaselineRuntimeConfig", "GetActiveRuntimeConfigState")
    forbid_tokens(get_state_body, GET_STATE_FORBIDDEN_TOKENS, "GetActiveRuntimeConfigState")
    if "&kSourceOwnedCurrentBaselineRuntimeConfig" in get_state_body:
        fail("GetActiveRuntimeConfigState must publish generated source-owned baseline view, not source baseline")

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must only dereference the active view")
    forbid_tokens(resolve_body, HOT_PATH_FORBIDDEN_TOKENS + ("source",), "ResolveActiveRuntimeConfig")

    update_analog_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    require_token(
        update_analog_body,
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "UpdateAnalogOutputs",
    )
    forbid_tokens(update_analog_body, HOT_PATH_FORBIDDEN_TOKENS, "UpdateAnalogOutputs")

    baseline = baseline_ultimate_source()
    if normalize_block(extract_function(source, "UpdateDigitalOutputs")) != normalize_block(
        extract_function(baseline, "UpdateDigitalOutputs")
    ):
        fail("UpdateDigitalOutputs changed relative to configurator")
    for expr in (
        "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
        "state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;",
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "outputs.buttonR = inputs.rf6;",
        "state.z_airdodge_override_active = inputs.rf6;",
    ):
        require_token(source, expr, "RF5/RF6/LT6 source")

    if re.search(r"active_view\s*=\s*&?[^;\n]*(?:candidate|Candidate|active_storage|ActiveStorage)", active_source):
        fail("candidate or RAM-backed active storage must not be published active")
    if re.search(r"&(?:candidate|Candidate)\.view|\.(?:active_view)\s*=\s*[^;\n]*(?:candidate|Candidate)", active_source):
        fail("candidate.view must never be active")
    if "static constexpr std::uint8_t kGeneratedSourceOwnedRuntimeConfigTables[27][9][2]" not in artifact:
        fail("generated baseline artifact must remain source-owned immutable static constexpr data")


def validate_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_generated_source_owned_baseline_active",
        "status": "hardware_gated_diagnostic",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "active_behavior_changed": True,
        "hardware_test_required_before_merge": True,
        "generated_source_owned_baseline_active": True,
        "generated_baseline_equivalent_to_source_owned_baseline": True,
        "ram_backed_active_table_publication": False,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "parser_payload_path_implemented": False,
        "runtime_loaded_config_implemented": False,
        "persistent_storage_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "hardware_result_claimed": False,
        "nunchuk_status": "NOT_TESTED",
        "root_cause_proven": False,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"diagnostic fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    if payload.get("evidence_matrix") != EXPECTED_EVIDENCE_MATRIX:
        fail("diagnostic fixture evidence_matrix mismatch")
    if payload.get("resolver_chain") != [
        "UpdateAnalogOutputs",
        "ResolveActiveRuntimeConfig",
        "GetActiveRuntimeConfigState",
        "active_view pointing to generated source-owned baseline RuntimeConfigView",
    ]:
        fail("diagnostic fixture resolver_chain mismatch")


def validate_build_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_generated_source_owned_baseline_active_build_report",
        "status": "local_build_report",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "fallback_build_command": "./scripts/build-glyph-mk6-quiet.sh",
        "local_build_result": "PASS",
        "build_completed": True,
        "build_exit_code": 0,
        "active_behavior_changed": True,
        "generated_source_owned_baseline_active": True,
        "generated_baseline_equivalent_to_source_owned_baseline": True,
        "ram_backed_active_table_publication": False,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "parser_payload_path_implemented": False,
        "runtime_loaded_config_implemented": False,
        "persistent_storage_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "artifact_hashes_are_rebuild_stable": False,
        "artifact_hashes_are_checker_gate": False,
        "hardware_result_claimed": False,
        "hardware_test_required_before_merge": True,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"build fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    hashes = payload.get("artifact_hashes")
    if not isinstance(hashes, list) or not hashes:
        fail("build fixture artifact_hashes must be a non-empty list after local build")
    for item in hashes:
        if not isinstance(item, dict):
            fail("artifact_hashes entries must be objects")
        if item.get("available") is not True:
            fail(f"artifact {item.get('path')} must be marked available")
        if not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            fail(f"artifact {item.get('path')} must have a SHA-256 hash")
    for phrase in (
        "Canonical command: pio run -e glyph_mk6",
        "Fallback command used: ./scripts/build-glyph-mk6-quiet.sh",
        "Artifact hashes are local observations only, not checker gates.",
        "`artifact_hashes_are_rebuild_stable`: `false`",
        "`artifact_hashes_are_checker_gate`: `false`",
        "Active behavior changed: `true`",
        "Generated source-owned baseline active: `true`",
        "No hardware result is claimed",
        "hardware_test_required_before_merge: true",
        "Nunchuk remains NOT_TESTED",
    ):
        require_phrase(report_text, phrase, "build report")


def validate_hardware_fixture(payload: dict[str, Any], plan_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_generated_source_owned_baseline_active_hardware_plan",
        "status": "PLAN_ONLY",
        "branch_under_test": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "hardware_result_claimed": False,
        "hardware_test_required_before_merge": True,
        "generated_source_owned_baseline_active": True,
        "generated_baseline_equivalent_to_source_owned_baseline": True,
        "ram_backed_active_table_publication": False,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "parser_payload_path_implemented": False,
        "runtime_loaded_config_implemented": False,
        "persistent_storage_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"hardware fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    if payload.get("evidence_matrix") != EXPECTED_EVIDENCE_MATRIX:
        fail("hardware fixture evidence_matrix mismatch")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail("hardware fixture rows must be a list")
    row_ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if row_ids != EXPECTED_HARDWARE_ROWS:
        fail(f"hardware rows mismatch: expected {EXPECTED_HARDWARE_ROWS!r}, got {row_ids!r}")
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware fixture row must be an object")
        if row.get("status") != "NOT_TESTED":
            fail(f"hardware row {row.get('id')} must be NOT_TESTED")
        require_phrase(plan_text, f"| {row['id']} |", "hardware plan")


def validate_failure_fixture(payload: dict[str, Any], failure_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_generated_source_owned_baseline_active_hardware_failure",
        "branch_under_test": EXPECTED_BRANCH,
        "result_branch": RESULT_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "overall_result": "HARDWARE_FAIL",
        "active_behavior_changed": True,
        "hardware_test_required_before_merge": True,
        "merge_approved": False,
        "implementation_branch_merge_allowed": False,
        "generated_source_owned_baseline_active": True,
        "generated_baseline_equivalent_to_source_owned_baseline": True,
        "ram_backed_active_table_publication": False,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "parser_payload_path_implemented": False,
        "runtime_loaded_config_implemented": False,
        "persistent_storage_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
        "root_cause_proven": False,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"hardware failure fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")

    expected_symptoms = [
        "forced A + Up disconnect",
        "forced A + Down disconnect",
        "initial two Up+A presses did not immediately disconnect",
        "reconnect sometimes stuck left stick fully down or fully up across failed diagnostics",
    ]
    if payload.get("failure_symptoms") != expected_symptoms:
        fail("hardware failure fixture failure_symptoms mismatch")

    expected_conclusions = [
        "generated source-owned baseline active diagnostic failed hardware test",
        "generated/source-owned/baseline-equivalent table data was not sufficient for safe active publication",
        "failure is not isolated to RAM-backed active table storage",
        "changing active RuntimeConfigView/table publication path remains unsafe under this diagnostic",
        "implementation branch must not merge",
    ]
    if payload.get("conclusion") != expected_conclusions:
        fail("hardware failure fixture conclusion mismatch")

    for phrase in (
        "status: HARDWARE_FAIL",
        "overall_result: HARDWARE_FAIL",
        EXPECTED_BRANCH,
        RESULT_BRANCH,
        "Forced A + Up still disconnects.",
        "Forced A + Down still disconnects.",
        "Initial two Up+A presses did not immediately disconnect",
        "left stick fully down or fully up",
        "`merge_approved`: `false`",
        "`nunchuk_status`: `NOT_TESTED`",
        "`root_cause_proven`: `false`",
        "Generated/source-owned/baseline-equivalent table data was not sufficient",
        "Failure is not isolated to RAM-backed active table storage.",
        "Changing active `RuntimeConfigView`/table publication path remains unsafe",
        "Source-owned active-state preselection remains the last known passing active-runtime boundary.",
        "Do not merge the failed implementation branch into `configurator`.",
        "Runtime-loaded config is not implemented.",
        "Runtime-config storage is not implemented.",
        "Persistent storage is not implemented.",
        "WebSerial/device write is not implemented.",
        "backend/config.pb write path is not implemented.",
        "Firmware flashing automation is not implemented.",
        "No push-to-device behavior is implemented or claimed.",
        "No nunchuk validation is claimed.",
        "Nunchuk remains NOT_TESTED.",
        "Root cause is not proven.",
    ):
        require_phrase(failure_text, phrase, "hardware failure doc")


def validate_failure_result_docs() -> None:
    failure_text = read_required(HARDWARE_FAILURE_PATH)
    failure_fixture = load_json_object(HARDWARE_FAILURE_FIXTURE_PATH)
    readme = read_required(README_PATH)
    calibration_index = read_required(CALIBRATION_INDEX_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)

    validate_failure_fixture(failure_fixture, failure_text)
    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
    ):
        require_phrase(text, "diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29", label)
        require_phrase(text, RESULT_BRANCH, label)
        require_phrase(text, "HARDWARE_FAIL", label)
        require_phrase(text, "Nunchuk remains NOT_TESTED", label)
        require_phrase(text, "implementation branch must not merge", label)


def validate_docs() -> None:
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

    for phrase in (
        "status: HARDWARE_GATED_DIAGNOSTIC",
        "generated source-owned baseline-equivalent artifact is selected active",
        "source-owned immutable data",
        "Do not call ParseUltimateRuntimeConfigPayload",
        "does not include `UltimateRuntimeConfigParser`",
        "does not publish `candidate.view`",
        "does not copy generated tables into RAM for active publication",
        "`active_behavior_changed`: `true`",
        "`hardware_test_required_before_merge`: `true`",
        "`generated_source_owned_baseline_active`: `true`",
        "`generated_baseline_equivalent_to_source_owned_baseline`: `true`",
        "`ram_backed_active_table_publication`: `false`",
        "`candidate_view_published_active`: `false`",
        "`nunchuk_status`: `NOT_TESTED`",
        "Runtime-loaded config is not implemented.",
        "Runtime-config storage is not implemented.",
        "WebSerial/device write is not implemented.",
        "backend/config.pb write path is not implemented.",
        "Firmware flashing automation is not implemented.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(doc, phrase, "diagnostic doc")

    validate_fixture(fixture)
    validate_build_fixture(build_fixture, build_report)
    validate_hardware_fixture(hardware_fixture, hardware_plan)
    if current_branch() == RESULT_BRANCH:
        validate_failure_result_docs()

    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
    ):
        require_phrase(text, "diagnostic_generated_source_owned_baseline_active", label)
        require_phrase(text, EXPECTED_BRANCH, label)
        require_phrase(text, "generated source-owned baseline", label)
        require_phrase(text, "hardware_test_required_before_merge", label)
        require_phrase(text, "Nunchuk remains NOT_TESTED", label)


def validate_merged_branch_hardware_gate(branch: str) -> None:
    if branch != MERGED_BRANCH:
        return
    source = read_required(ULTIMATE_PATH)
    if "kGeneratedSourceOwnedBaselineRuntimeConfig" not in source:
        return
    result = REPO_ROOT / "docs/calibration/diagnostic_generated_source_owned_baseline_active_hardware_result_2026-06-29.md"
    result_fixture = (
        REPO_ROOT
        / "docs/calibration/fixtures/diagnostic_generated_source_owned_baseline_active_hardware_result_2026-06-29.json"
    )
    if not result.exists() or not result_fixture.exists():
        fail("configurator may retain this active diagnostic source only with preserved HARDWARE_PASS result")
    payload = load_json_object(result_fixture)
    if payload.get("overall_result") != "HARDWARE_PASS":
        fail("merged active diagnostic source requires overall_result HARDWARE_PASS")


def validate_baseline_equivalence_checker() -> None:
    if current_branch() == RESULT_BRANCH:
        return
    completed = subprocess.run(
        ["python3", str(BASELINE_CHECKER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("generated baseline equivalence checker failed: " + completed.stderr.strip())


def main() -> None:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch))
    validate_source()
    validate_docs()
    validate_merged_branch_hardware_gate(branch)
    validate_baseline_equivalence_checker()
    print("glyph_diagnostic_generated_source_owned_baseline_active: PASS")
    print(f"branch={branch}")
    print("generated_source_owned_baseline_active=true")
    print("generated_baseline_equivalent_to_source_owned_baseline=true")
    print("ram_backed_active_table_publication=false")
    print("candidate_view_published_active=false")
    print("hardware_test_required_before_merge=true")
    print("nunchuk_status=NOT_TESTED")


if __name__ == "__main__":
    main()
