#!/usr/bin/env python3
"""Validate the active-storage runtime config publication model scaffold."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-active-storage-publication-model"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, MERGED_BRANCH}

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
DOC_PATH = REPO_ROOT / "docs/runtime_config/active_storage_publication_model.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/active_storage_publication_model.json"
BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/active_storage_publication_model_build_report_2026-06-10.md"
BUILD_REPORT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/active_storage_publication_model_build_report_2026-06-10.json"
HARDWARE_PLAN_PATH = REPO_ROOT / "docs/calibration/active_storage_publication_model_hardware_plan_2026-06-10.md"
HARDWARE_PLAN_FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/active_storage_publication_model_hardware_plan_2026-06-10.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
WORKFLOW_PATH = REPO_ROOT / "docs/WORKFLOW.md"

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "tools/check_glyph_active_storage_publication_model.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")
OPTIONAL_MODE_HELPER_RE = re.compile(r"^src/modes/[^/]+\.(?:cpp|hpp|h)$")
FORBIDDEN_CHANGED_RE = re.compile(
    r"(^|/)(?:HAL|hal|backend|config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

EXPECTED_HARDWARE_ROWS = [
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "MODIFIERS-001",
    "DEDICATED-ACTIVE-STORAGE-001",
    "CANDIDATE-NOT-ACTIVE-001",
    "SOURCE-OWNED-FALLBACK-001",
    "HOT-PATH-001",
    "NO-PARSER-ACTIVE-PUBLICATION-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
]

EVIDENCE_MATRIX = {
    "source_owned_active_state_preselection": "HARDWARE_PASS",
    "parsed_candidate_present_source_owned_active_view": "HARDWARE_PASS",
    "parsed_candidate_view_active": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active": "HARDWARE_FAIL",
}

CONCLUSIONS = {
    "candidate_backed_active_runtime_view_safe": False,
    "candidate_buffer_may_validate_values": True,
    "candidate_buffer_must_not_be_active": True,
    "dedicated_active_storage_required": True,
    "low_level_failure_mechanism_proven": False,
    "runtime_loaded_config_implemented": False,
    "storage_implemented": False,
    "webserial_device_write_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
}


class ActiveStoragePublicationModelError(AssertionError):
    """Raised when active-storage publication model guardrails drift."""


def fail(message: str) -> None:
    raise ActiveStoragePublicationModelError(message)


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
            fail(f"forbidden HAL/backend/config.pb/storage/write/WebSerial/flashing path changed: {path}")
        if branch == MERGED_BRANCH:
            continue
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if OPTIONAL_MODE_HELPER_RE.match(path):
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


def forbid_tokens(text: str, tokens: tuple[str, ...], label: str) -> None:
    for token in tokens:
        if token in text:
            fail(f"{label} must not mention {token}")


def validate_parse_call_boundary(source: str, doc: str) -> None:
    active_source = strip_cpp_comments(source)
    if "ParseUltimateRuntimeConfigPayload(" not in active_source:
        return
    require_phrase(
        doc,
        "ParseUltimateRuntimeConfigPayload(...) remains inactive and outside active publication path.",
        "active-storage doc",
    )
    for function_name in (
        "GetActiveRuntimeConfigState",
        "ResolveActiveRuntimeConfig",
        "UpdateAnalogOutputs",
        "CopyRuntimeConfigViewIntoActiveStorage",
        "ValidateRuntimeConfigActiveStorage",
    ):
        body = strip_cpp_comments(extract_function(source, function_name))
        if "ParseUltimateRuntimeConfigPayload(" in body:
            fail(f"{function_name}() must not call ParseUltimateRuntimeConfigPayload")


def validate_source(source: str, doc: str) -> None:
    active_source = strip_cpp_comments(source)
    for token in (
        "enum class RuntimeConfigActiveStorageStatus",
        "RuntimeConfigActiveStorageStatus::Empty",
        "RuntimeConfigActiveStorageStatus::SourceOwnedEquivalent",
        "RuntimeConfigActiveStorageStatus::InvalidSourceView",
        "struct RuntimeConfigActiveStorage",
        "ResetRuntimeConfigActiveStorage",
        "ValidateRuntimeConfigActiveStorage",
        "CopyRuntimeConfigViewIntoActiveStorage",
    ):
        require_token(active_source, token, "Ultimate.cpp active-storage scaffold")

    if re.search(r"active_view\s*=\s*&?[^;\n]*(?:candidate|Candidate)", active_source):
        fail("candidate-backed active publication is forbidden")
    if re.search(r"\{[^{}]*(?:candidate|Candidate)[^{}]*RuntimeConfigSource::", extract_function(source, "GetActiveRuntimeConfigState"), re.S):
        fail("GetActiveRuntimeConfigState must not publish candidate-owned state")

    get_state_body = strip_cpp_comments(extract_function(source, "GetActiveRuntimeConfigState"))
    require_token(get_state_body, "&kSourceOwnedCurrentBaselineRuntimeConfig", "GetActiveRuntimeConfigState")
    require_token(get_state_body, "RuntimeConfigSource::SourceOwnedBaseline", "GetActiveRuntimeConfigState")
    require_token(get_state_body, "RuntimeConfigActivationStatus::SourceOwnedSelected", "GetActiveRuntimeConfigState")
    forbid_tokens(
        get_state_body,
        (
            "candidate",
            "Candidate",
            "Parse",
            "parser",
            "decision",
            "storage",
            "Storage",
            "Materialize",
            "CopyRuntimeConfigViewIntoActiveStorage",
            "kDiagnosticParsedCandidateState",
        ),
        "GetActiveRuntimeConfigState",
    )

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must only dereference the active view")
    forbid_tokens(
        resolve_body,
        (
            "candidate",
            "Candidate",
            "parser",
            "Parse",
            "decision",
            "status",
            "source",
            "storage",
            "write",
            "WebSerial",
            "flash",
            "load",
        ),
        "ResolveActiveRuntimeConfig",
    )

    update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    require_token(
        update_body,
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "UpdateAnalogOutputs",
    )
    forbid_tokens(
        update_body,
        (
            "candidate",
            "Candidate",
            "parser",
            "Parse",
            "decision",
            "status",
            "storage",
            "write",
            "WebSerial",
            "flash",
            "load",
        ),
        "UpdateAnalogOutputs",
    )

    for expr in (
        "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
        "state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;",
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "outputs.buttonR = inputs.rf6;",
        "state.z_airdodge_override_active = inputs.rf6;",
    ):
        require_token(source, expr, "RF5/RF6/LT6 source")

    baseline = baseline_ultimate_source()
    if normalize_block(extract_function(source, "UpdateDigitalOutputs")) != normalize_block(
        extract_function(baseline, "UpdateDigitalOutputs")
    ):
        fail("UpdateDigitalOutputs changed relative to configurator")

    validate_parse_call_boundary(source, doc)


def require_phrase(text: str, phrase: str, label: str) -> None:
    compact_text = re.sub(r"\s+", " ", text).strip().lower()
    compact_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
    if compact_phrase not in compact_text:
        fail(f"{label} missing phrase: {phrase}")


def validate_evidence_and_conclusions(payload: dict[str, Any], label: str) -> None:
    matrix = payload.get("evidence_matrix")
    if matrix != EVIDENCE_MATRIX:
        fail(f"{label} evidence_matrix mismatch: expected {EVIDENCE_MATRIX!r}, got {matrix!r}")
    conclusions = payload.get("conclusions")
    if not isinstance(conclusions, dict):
        fail(f"{label} conclusions must be an object")
    for key, expected in CONCLUSIONS.items():
        if conclusions.get(key) != expected:
            fail(f"{label} conclusions {key!r} mismatch: expected {expected!r}, got {conclusions.get(key)!r}")


def validate_model_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_active_storage_publication_model",
        "status": "inactive_scaffold",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "candidate_buffer_is_active_buffer": False,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "dedicated_active_storage_scaffolded": True,
        "dedicated_active_storage_published_active": False,
        "published_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "active_output_behavior_changed": False,
        "hardware_test_required_before_merge": False,
        "parser_payload_activation_implemented": False,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"model fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    validate_evidence_and_conclusions(payload, "model fixture")


def validate_build_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected = {
        "schema_name": "glyph_active_storage_publication_model_build_report",
        "status": "local_build_report",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "fallback_build_command": "./scripts/build-glyph-mk6-quiet.sh",
        "local_build_result": "PASS",
        "candidate_view_published_active": False,
        "dedicated_active_storage_published_active": False,
        "published_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "active_output_behavior_changed": False,
        "artifact_hashes_are_rebuild_stable": False,
        "artifact_hashes_are_checker_gate": False,
        "hardware_result_claimed": False,
        "hardware_test_required_before_merge": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"build fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    if not isinstance(payload.get("artifact_hashes"), list):
        fail("build fixture artifact_hashes must be a list")
    for phrase in (
        "Canonical command: pio run -e glyph_mk6",
        "Artifact hashes are local observations only, not checker gates.",
        "`artifact_hashes_are_rebuild_stable`: `false`",
        "`artifact_hashes_are_checker_gate`: `false`",
        "No hardware result is claimed",
        "hardware_test_required_before_merge: false",
        "Nunchuk remains NOT_TESTED",
    ):
        require_phrase(report_text, phrase, "build report")


def validate_hardware_fixture(payload: dict[str, Any], plan_text: str) -> None:
    expected = {
        "schema_name": "glyph_active_storage_publication_model_hardware_plan",
        "status": "PLAN_ONLY",
        "branch_under_test": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "hardware_result_claimed": False,
        "hardware_test_required_before_merge": False,
        "candidate_view_published_active": False,
        "dedicated_active_storage_published_active": False,
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"hardware fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    validate_evidence_and_conclusions(payload, "hardware fixture")
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


def validate_docs_and_fixtures() -> None:
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
    workflow = read_required(WORKFLOW_PATH)

    for phrase in (
        "status: INACTIVE_SCAFFOLD",
        "candidate buffer != active buffer",
        "candidate validates proposed values",
        "accepted values are copied into dedicated active storage",
        "active RuntimeConfigView points to dedicated active storage",
        "candidate.view is never active",
        "This branch keeps active output behavior source-owned baseline.",
        "Dedicated active storage is scaffolded but not activated.",
        "Candidate-backed active RuntimeConfigView publication is forbidden.",
        "Candidate-owned runtime table pointers must not be published active.",
        "ParseUltimateRuntimeConfigPayload(...) remains inactive and outside active publication path.",
        "hardware_test_required_before_merge: false",
        "The low-level failure mechanism is not proven.",
        "Runtime-loaded config is not implemented.",
        "Runtime-config storage is not implemented.",
        "WebSerial/device write is not implemented.",
        "backend/config.pb write path is not implemented.",
        "Firmware flashing automation is not implemented.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(doc, phrase, "active-storage doc")

    for phrase in (
        "source-owned active-state preselection: HARDWARE_PASS",
        "parsed/candidate present, source-owned active view: HARDWARE_PASS",
        "parsed candidate.view active: HARDWARE_FAIL",
        "source-owned-materialized candidate.view active: HARDWARE_FAIL",
    ):
        require_phrase(doc, phrase, "active-storage evidence matrix")

    validate_model_fixture(fixture)
    validate_build_fixture(build_fixture, build_report)
    validate_hardware_fixture(hardware_fixture, hardware_plan)

    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
        (workflow, "workflow"),
    ):
        require_phrase(text, "active_storage_publication_model", label)
        require_phrase(text, "candidate buffer != active buffer", label)


def main() -> None:
    branch = validate_branch()
    validate_changed_paths(changed_paths(), branch)
    doc = read_required(DOC_PATH)
    validate_source(read_required(ULTIMATE_PATH), doc)
    validate_docs_and_fixtures()
    print("active-storage publication model checks passed")


if __name__ == "__main__":
    main()
