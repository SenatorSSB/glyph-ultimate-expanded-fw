#!/usr/bin/env python3
"""Validate dedicated active-storage publication diagnostics and evidence."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-diagnostic-active-storage-published"
RESULT_BRANCH = "runtime-config-diagnostic-active-storage-published-hardware-failure"
EVIDENCE_BRANCH = "runtime-config-active-storage-failure-evidence"
GENERATED_SOURCE_OWNED_DESIGN_BRANCH = "runtime-config-generated-source-owned-realization-design"
GENERATED_SOURCE_OWNED_SCHEMA_SCAFFOLD_BRANCH = "runtime-config-generated-source-owned-schema-scaffold"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
RESULT_BRANCH_BASE = EXPECTED_BRANCH
ALLOWED_BRANCHES = {
    EXPECTED_BRANCH,
    RESULT_BRANCH,
    EVIDENCE_BRANCH,
    GENERATED_SOURCE_OWNED_DESIGN_BRANCH,
    GENERATED_SOURCE_OWNED_SCHEMA_SCAFFOLD_BRANCH,
    MERGED_BRANCH,
}

ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
DOC_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_active_storage_published.md"
FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_active_storage_published.json"
BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_active_storage_published_build_report_2026-06-10.md"
BUILD_REPORT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_active_storage_published_build_report_2026-06-10.json"
HARDWARE_PLAN_PATH = REPO_ROOT / "docs/calibration/diagnostic_active_storage_published_hardware_plan_2026-06-10.md"
HARDWARE_PLAN_FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/diagnostic_active_storage_published_hardware_plan_2026-06-10.json"
HARDWARE_RESULT_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_active_storage_published_hardware_result_2026-06-10.md"
HARDWARE_RESULT_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_active_storage_published_hardware_result_2026-06-10.json"
HARDWARE_FAILURE_PATH = REPO_ROOT / "docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md"
HARDWARE_FAILURE_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_active_storage_published_hardware_failure_2026-06-28.json"
README_PATH = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX_PATH = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/check_glyph_diagnostic_active_storage_published.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")
ALLOWED_ARCHIVED_EVIDENCE_SOURCE_SCAFFOLD_PATHS = {
    "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigSchema.hpp",
    "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigExample.hpp",
}
RESULT_BRANCH_ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/calibration/INDEX.md",
    "docs/runtime_config/README.md",
    "docs/runtime_config/diagnostic_active_storage_published.md",
    "docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md",
    "docs/runtime_config/fixtures/diagnostic_active_storage_published_hardware_failure_2026-06-28.json",
    "tools/check_glyph_diagnostic_active_storage_published.py",
}
OPTIONAL_MODE_HELPER_RE = re.compile(r"^src/modes/[^/]+\.(?:cpp|hpp|h)$")
FORBIDDEN_CHANGED_RE = re.compile(
    r"(^|/)(?:HAL|hal|backend|config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
FORBIDDEN_SOURCE_CHANGED_RE = re.compile(r"^(?:src|HAL|hal|backend|config\.pb)(?:/|$)")
SOURCE_CHANGED_RE = re.compile(r"^(?:src|lib|include|HAL|hal|backend)(?:/|$)|(?:^|/)config\.pb(?:/|$)")

EXPECTED_EVIDENCE_MATRIX = {
    "source_owned_active_state_preselection": "HARDWARE_PASS",
    "parsed_candidate_machinery_present_source_owned_active_view": "HARDWARE_PASS",
    "parsed_candidate_view_active": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active": "HARDWARE_FAIL",
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
    "DEDICATED-ACTIVE-STORAGE-MATERIALIZED-001",
    "DEDICATED-ACTIVE-STORAGE-EQUIVALENT-001",
    "DEDICATED-ACTIVE-STORAGE-PUBLISHED-001",
    "CANDIDATE-NOT-ACTIVE-001",
    "SOURCE-OWNED-FALLBACK-001",
    "HOT-PATH-001",
    "NO-PARSER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
]

FORBIDDEN_SOURCE_TOKENS = (
    "UltimateRuntimeConfigParser",
    "ParseUltimateRuntimeConfigPayload",
    "kDiagnosticSourceOwnedParsedPayload",
    "kDiagnosticParsedCandidateState",
    "InitializeDiagnosticParsedCandidateState",
    "ParsedPayloadValid",
    "ParsedPayloadEquivalent",
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

FORBIDDEN_INERT_SCAFFOLD_TOKENS = (
    "GetActiveRuntimeConfigState",
    "ResolveActiveRuntimeConfig",
    "UpdateAnalogOutputs",
    "active_view =",
    "candidate.view",
    "RuntimeConfigStorage",
    "WebSerial",
    "config.pb",
    "flash",
    "flashing",
)


class DiagnosticActiveStoragePublishedError(AssertionError):
    """Raised when the diagnostic active-storage publication contract drifts."""


def fail(message: str) -> None:
    raise DiagnosticActiveStoragePublishedError(message)


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
        fail(
            "checker must run on "
            f"{EXPECTED_BRANCH}, {RESULT_BRANCH}, {EVIDENCE_BRANCH}, "
            f"{GENERATED_SOURCE_OWNED_DESIGN_BRANCH}, "
            f"{GENERATED_SOURCE_OWNED_SCHEMA_SCAFFOLD_BRANCH}, or {MERGED_BRANCH}, got {branch}"
        )
    if branch in {
        EXPECTED_BRANCH,
        EVIDENCE_BRANCH,
        GENERATED_SOURCE_OWNED_DESIGN_BRANCH,
        GENERATED_SOURCE_OWNED_SCHEMA_SCAFFOLD_BRANCH,
    }:
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
            ["git", "merge-base", "--is-ancestor", RESULT_BRANCH_BASE, "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{RESULT_BRANCH_BASE} must be an ancestor of HEAD")
    return branch


def branch_mode(branch: str) -> str:
    if branch == EXPECTED_BRANCH:
        return "implementation"
    if branch == RESULT_BRANCH:
        return "failure_result"
    if branch in {
        EVIDENCE_BRANCH,
        GENERATED_SOURCE_OWNED_DESIGN_BRANCH,
        GENERATED_SOURCE_OWNED_SCHEMA_SCAFFOLD_BRANCH,
        MERGED_BRANCH,
    }:
        return "archived_evidence"
    fail(f"unsupported branch mode for {branch}")


def changed_paths(diff_base: str) -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{diff_base}...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status=True):
        path = status_line[3:].strip()
        if not path:
            continue
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.endswith("/"):
            directory = REPO_ROOT / path
            if directory.is_dir():
                paths.update(rel(file_path) for file_path in directory.rglob("*") if file_path.is_file())
        else:
            paths.add(path)
    return paths


def validate_inert_source_scaffold(path: str) -> None:
    text = read_required(REPO_ROOT / path)
    if "inert generated-table placeholder" not in text:
        fail(f"inert source scaffold missing explicit marker: {path}")
    for token in FORBIDDEN_INERT_SCAFFOLD_TOKENS:
        if token in text:
            fail(f"inert source scaffold contains active wiring token {token!r}: {path}")


def validate_changed_paths(paths: set[str], mode: str) -> None:
    if mode == "failure_result":
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
            fail(f"forbidden HAL/backend/config.pb/persistent-storage/write/WebSerial/flashing path changed: {path}")
        if mode == "archived_evidence" and SOURCE_CHANGED_RE.search(path):
            if path in ALLOWED_ARCHIVED_EVIDENCE_SOURCE_SCAFFOLD_PATHS:
                validate_inert_source_scaffold(path)
                continue
            fail(f"source path changed in archived-evidence mode: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            if mode == "archived_evidence" and path == "src/modes/Ultimate.cpp":
                fail("archived-evidence mode must not change src/modes/Ultimate.cpp")
            continue
        if mode == "implementation" and OPTIONAL_MODE_HELPER_RE.match(path):
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


def require_phrase(text: str, phrase: str, label: str) -> None:
    compact_text = re.sub(r"\s+", " ", text).strip().lower()
    compact_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
    if compact_phrase not in compact_text:
        fail(f"{label} missing phrase: {phrase}")


def validate_no_parser_payload_path(source: str) -> None:
    active_source = strip_cpp_comments(source)
    forbid_tokens(active_source, FORBIDDEN_SOURCE_TOKENS, "Ultimate.cpp")
    if re.search(r"\bparser_payload\b|\bpayload_bytes\b|uint8_t\s+\w*Payload", active_source):
        fail("Ultimate.cpp must not define parser payload bytes")


def validate_active_storage_publication_source(source: str) -> None:
    active_source = strip_cpp_comments(source)
    validate_no_parser_payload_path(source)
    for token in (
        "enum class RuntimeConfigActiveStorageStatus",
        "RuntimeConfigActiveStorageStatus::Empty",
        "RuntimeConfigActiveStorageStatus::SourceOwnedEquivalent",
        "RuntimeConfigActiveStorageStatus::InvalidSourceView",
        "struct RuntimeConfigActiveStorage",
        "ResetRuntimeConfigActiveStorage",
        "ValidateRuntimeConfigActiveStorage",
        "CopyRuntimeConfigViewIntoActiveStorage",
        "PublishDedicatedActiveStorageOrFallback",
        "RuntimeConfigSource::DedicatedActiveStorage",
        "RuntimeConfigActivationStatus::DedicatedActiveStorageSelected",
    ):
        require_token(active_source, token, "Ultimate.cpp active-storage diagnostic")

    copy_body = strip_cpp_comments(extract_function(source, "CopyRuntimeConfigViewIntoActiveStorage"))
    require_token(copy_body, "ResetRuntimeConfigActiveStorage(active_storage);", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "ValidateRuntimeConfigView(source_view)", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "active_storage.points[table_index][point_index] = source_table.table[point_index];", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "active_storage.tables", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "active_storage.view", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "RuntimeConfigViewsHaveEquivalentPoints", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "kSourceOwnedCurrentBaselineRuntimeConfig", "CopyRuntimeConfigViewIntoActiveStorage")
    require_token(copy_body, "ValidateRuntimeConfigActiveStorage(active_storage)", "CopyRuntimeConfigViewIntoActiveStorage")

    validate_storage_body = strip_cpp_comments(extract_function(source, "ValidateRuntimeConfigActiveStorage"))
    require_token(validate_storage_body, "RuntimeConfigActiveStorageStatus::SourceOwnedEquivalent", "ValidateRuntimeConfigActiveStorage")
    require_token(validate_storage_body, "ValidateRuntimeConfigView(active_storage.view)", "ValidateRuntimeConfigActiveStorage")
    require_token(validate_storage_body, "RuntimeConfigViewsHaveEquivalentPoints(active_storage.view, kSourceOwnedCurrentBaselineRuntimeConfig)", "ValidateRuntimeConfigActiveStorage")

    publish_body = strip_cpp_comments(extract_function(source, "PublishDedicatedActiveStorageOrFallback"))
    require_token(publish_body, "CopyRuntimeConfigViewIntoActiveStorage(kSourceOwnedCurrentBaselineRuntimeConfig, active_storage)", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "ValidateRuntimeConfigActiveStorage(active_storage)", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "RuntimeConfigViewsHaveEquivalentPoints(active_storage.view, kSourceOwnedCurrentBaselineRuntimeConfig)", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "&active_storage.view", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "RuntimeConfigSource::DedicatedActiveStorage", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "RuntimeConfigActivationStatus::DedicatedActiveStorageSelected", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "&kSourceOwnedCurrentBaselineRuntimeConfig", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "RuntimeConfigSource::KnownGoodFallback", "PublishDedicatedActiveStorageOrFallback")
    require_token(publish_body, "RuntimeConfigActivationStatus::FallbackSelected", "PublishDedicatedActiveStorageOrFallback")
    if publish_body.find("if (active_storage_ready)") > publish_body.find("&active_storage.view"):
        fail("dedicated active storage must be published only after validation/equivalence success")

    require_token(active_source, "RuntimeConfigActiveStorage gDedicatedActiveRuntimeConfigStorage;", "Ultimate.cpp active-storage diagnostic")
    require_token(active_source, "const ActiveRuntimeConfigState gActiveRuntimeConfigState", "Ultimate.cpp active-storage diagnostic")
    require_token(active_source, "PublishDedicatedActiveStorageOrFallback(gDedicatedActiveRuntimeConfigStorage)", "Ultimate.cpp active-storage diagnostic")

    get_state_body = strip_cpp_comments(extract_function(source, "GetActiveRuntimeConfigState"))
    require_token(get_state_body, "return gActiveRuntimeConfigState;", "GetActiveRuntimeConfigState")
    forbid_tokens(
        get_state_body,
        (
            "candidate",
            "Candidate",
            "parser",
            "Parse",
            "decision",
            "Materialize",
            "status ==",
            ".status",
        ),
        "GetActiveRuntimeConfigState",
    )

    resolve_body = strip_cpp_comments(extract_function(source, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must only dereference the active view")
    forbid_tokens(resolve_body, HOT_PATH_FORBIDDEN_TOKENS + ("source",), "ResolveActiveRuntimeConfig")

    update_body = strip_cpp_comments(extract_function(source, "UpdateAnalogOutputs"))
    require_token(
        update_body,
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "UpdateAnalogOutputs",
    )
    forbid_tokens(update_body, HOT_PATH_FORBIDDEN_TOKENS, "UpdateAnalogOutputs")

    for expr in (
        "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
        "state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;",
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "outputs.buttonR = inputs.rf6;",
        "state.z_airdodge_override_active = inputs.rf6;",
    ):
        require_token(source, expr, "RF5/RF6/LT6 source")

    if re.search(r"active_view\s*=\s*&?[^;\n]*(?:candidate|Candidate)", active_source):
        fail("candidate-backed active publication is forbidden")
    if re.search(r"&(?:candidate|Candidate)\.view|\.(?:active_view)\s*=\s*[^;\n]*(?:candidate|Candidate)", active_source):
        fail("candidate.view must never be active")
    if re.search(r"active_view[^;\n]*(?:candidate|Candidate).*tables|active_view[^;\n]*(?:candidate|Candidate).*points", active_source):
        fail("candidate-owned table pointers must never be active")

    baseline = baseline_ultimate_source()
    if normalize_block(extract_function(source, "UpdateDigitalOutputs")) != normalize_block(
        extract_function(baseline, "UpdateDigitalOutputs")
    ):
        fail("UpdateDigitalOutputs changed relative to configurator")


def validate_diagnostic_fixture(payload: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_active_storage_published",
        "status": "hardware_gated_diagnostic",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "active_behavior_changed": True,
        "hardware_test_required_before_merge": True,
        "source_view_copied_into_dedicated_active_storage": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "dedicated_active_storage_scaffolded": True,
        "dedicated_active_storage_active": True,
        "dedicated_active_storage_validated": True,
        "dedicated_active_storage_equivalence_validated": True,
        "published_active_view_when_equivalent": "dedicated active storage view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "parser_payload_path_implemented": False,
        "parse_ultimate_runtime_config_payload_called": False,
        "ultimate_runtime_config_parser_included": False,
        "runtime_loaded_config_implemented": False,
        "persistent_storage_implemented": False,
        "storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "hardware_result_claimed": False,
        "nunchuk_status": "NOT_TESTED",
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
        "gActiveRuntimeConfigState.active_view",
    ]:
        fail("diagnostic fixture resolver_chain mismatch")


def validate_build_fixture(payload: dict[str, Any], report_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_active_storage_published_build_report",
        "status": "local_build_report",
        "branch": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "canonical_build_command": "pio run -e glyph_mk6",
        "fallback_build_command": "./scripts/build-glyph-mk6-quiet.sh",
        "local_build_result": "PASS",
        "build_completed": True,
        "build_exit_code": 0,
        "dedicated_active_storage_active": True,
        "dedicated_active_storage_published_active": True,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "published_active_view_when_equivalent": "dedicated active storage view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
        "active_behavior_changed": True,
        "parser_payload_path_implemented": False,
        "artifact_hashes_are_rebuild_stable": False,
        "artifact_hashes_are_checker_gate": False,
        "hardware_result_claimed": False,
        "hardware_test_required_before_merge": True,
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
        "Artifact hashes are local observations only, not checker gates.",
        "`artifact_hashes_are_rebuild_stable`: `false`",
        "`artifact_hashes_are_checker_gate`: `false`",
        "Active behavior changed: `true`",
        "Parser payload path implemented: `false`",
        "No hardware result is claimed",
        "hardware_test_required_before_merge: true",
        "Nunchuk remains NOT_TESTED",
    ):
        require_phrase(report_text, phrase, "build report")


def validate_hardware_fixture(payload: dict[str, Any], plan_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_active_storage_published_hardware_plan",
        "status": "PLAN_ONLY",
        "branch_under_test": EXPECTED_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "hardware_result_claimed": False,
        "hardware_test_required_before_merge": True,
        "dedicated_active_storage_active": True,
        "dedicated_active_storage_published_active": True,
        "candidate_view_published_active": False,
        "candidate_owned_table_pointer_published_active": False,
        "published_active_view_when_equivalent": "dedicated active storage view",
        "fallback_active_view": "kSourceOwnedCurrentBaselineRuntimeConfig",
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


def require_false(payload: dict[str, Any], key: str, label: str) -> None:
    if payload.get(key) is not False:
        fail(f"{label} {key!r} must be false, got {payload.get(key)!r}")


def forbid_unsupported_claims(text: str, label: str) -> None:
    compact = re.sub(r"\s+", " ", text).strip().lower()
    forbidden_phrases = (
        "`runtime_loaded_config_implemented`: `true`",
        '"runtime_loaded_config_implemented": true',
        "runtime-loaded config is implemented",
        "`persistent_storage_implemented`: `true`",
        '"persistent_storage_implemented": true',
        "persistent storage is implemented",
        "`storage_implemented`: `true`",
        '"storage_implemented": true',
        "runtime-config storage is implemented",
        "`webserial_device_write_implemented`: `true`",
        '"webserial_device_write_implemented": true',
        "webserial/device write is implemented",
        "`backend_config_pb_write_path_implemented`: `true`",
        '"backend_config_pb_write_path_implemented": true',
        "backend/config.pb write path is implemented",
        "`flashing_automation_implemented`: `true`",
        '"flashing_automation_implemented": true',
        "firmware flashing automation is implemented",
        "`root_cause_proven`: `true`",
        '"root_cause_proven": true',
        "root cause is proven",
        "nunchuk: pass",
    )
    for phrase in forbidden_phrases:
        if phrase in compact:
            fail(f"{label} contains unsupported claim: {phrase}")


def validate_failure_fixture(payload: dict[str, Any], result_text: str) -> None:
    expected = {
        "schema_name": "glyph_diagnostic_active_storage_published_hardware_failure",
        "branch_under_test": EXPECTED_BRANCH,
        "result_branch": RESULT_BRANCH,
        "baseline_branch": BASE_BRANCH,
        "overall_result": "HARDWARE_FAIL",
        "active_behavior_changed": True,
        "hardware_test_required_before_merge": True,
        "merge_approved": False,
        "implementation_branch_merge_allowed": False,
        "dedicated_active_storage_active": True,
        "dedicated_active_storage_published_active": True,
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
            fail(f"failure fixture {key!r} mismatch: expected {expected_value!r}, got {payload.get(key)!r}")
    for key in (
        "runtime_loaded_config_implemented",
        "persistent_storage_implemented",
        "storage_implemented",
        "webserial_device_write_implemented",
        "backend_config_pb_write_path_implemented",
        "flashing_automation_implemented",
        "root_cause_proven",
    ):
        require_false(payload, key, "failure fixture")
    if payload.get("failure_symptoms") != [
        "forced A + Up disconnect",
        "forced A + Down disconnect",
    ]:
        fail("failure fixture failure_symptoms mismatch")
    conclusions = payload.get("conclusion")
    if not isinstance(conclusions, list):
        fail("failure fixture conclusion must be a list")
    for expected_conclusion in (
        "dedicated active storage published active is unsafe under this diagnostic",
        "RAM-backed active table storage is unsafe as an active publication target under this test",
        "low-level mechanism remains unproven",
        "implementation branch must not merge",
    ):
        if expected_conclusion not in conclusions:
            fail(f"failure fixture conclusion missing: {expected_conclusion}")
    for phrase in (
        "status: HARDWARE_FAIL",
        "overall_result: HARDWARE_FAIL",
        f"branch_under_test: `{EXPECTED_BRANCH}`",
        f"result_branch: `{RESULT_BRANCH}`",
        "forced A + Up",
        "forced A + Down",
        "controller disconnect still happens",
        "`merge_approved`: `false`",
        "`nunchuk_status`: `NOT_TESTED`",
        "`root_cause_proven`: `false`",
        "Dedicated active storage publication failed hardware testing.",
        "Dedicated active storage published active is unsafe under this diagnostic.",
        "Dedicated active storage published as the active `RuntimeConfigView` is not safe",
        "RAM-backed active table storage is unsafe as an active publication target under this test.",
        "RAM-backed active runtime table storage appears unsafe",
        "The low-level mechanism remains unproven.",
        "Candidate-backed active view remains forbidden.",
        "Dedicated active storage may remain as archived diagnostic evidence only",
        "The implementation branch must not merge into `configurator`.",
        "Do not merge the failed implementation branch.",
        "compile-time/generated immutable source-owned tables",
        "source-owned table replacement / generated firmware artifacts",
        "no runtime-loaded publication until a safer active-storage model is proven",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(result_text, phrase, "failure result")
    forbid_unsupported_claims(result_text, "failure result")


def validate_failure_result_branch_docs() -> None:
    result_text = read_required(HARDWARE_FAILURE_PATH)
    result_fixture = load_json_object(HARDWARE_FAILURE_FIXTURE_PATH)
    readme = read_required(README_PATH)
    calibration_index = read_required(CALIBRATION_INDEX_PATH)
    current_state = read_required(CURRENT_STATE_PATH)
    roadmap = read_required(ROADMAP_PATH)
    diagnostic_doc = read_required(DOC_PATH)

    validate_failure_fixture(result_fixture, result_text)
    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
        (diagnostic_doc, "diagnostic doc"),
    ):
        require_phrase(text, "diagnostic_active_storage_published_hardware_failure_2026-06-28", label)
        require_phrase(text, "HARDWARE_FAIL", label)
        require_phrase(text, "forced A + Up", label)
        require_phrase(text, "forced A + Down", label)
        require_phrase(text, "must not merge", label)
        require_phrase(text, "Do not merge the failed implementation branch", label)
        require_phrase(text, "low-level mechanism remains unproven", label)
        require_phrase(text, "Nunchuk remains NOT_TESTED", label)
        forbid_unsupported_claims(text, label)
    for phrase in (
        "Dedicated active storage published active is unsafe under this diagnostic",
        "RAM-backed active table storage is unsafe as an active publication target under this test",
        "RAM-backed active runtime table storage appears unsafe",
        "low-level mechanism remains unproven",
        "candidate-backed active view remains forbidden",
        "future strategy should pivot away from RAM-backed active table pointer publication",
    ):
        require_phrase(current_state + "\n" + roadmap + "\n" + readme + "\n" + result_text, phrase, "failure conclusion docs")


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

    for phrase in (
        "status: HARDWARE_GATED_DIAGNOSTIC",
        "Do not call ParseUltimateRuntimeConfigPayload",
        "does not include `UltimateRuntimeConfigParser`",
        "does not publish `candidate.view`",
        "Dedicated active storage is copied from",
        "Dedicated active storage is validated",
        "point/table equivalence",
        "`candidate.view` is never active",
        "Candidate-owned table pointers are never assigned to the active view",
    ):
        require_phrase(doc, phrase, "diagnostic doc")
    for phrase in (
        "`active_behavior_changed`: `true`",
        "`hardware_test_required_before_merge`: `true`",
        "`dedicated_active_storage_active`: `true`",
        "`candidate_view_published_active`: `false`",
        "`candidate_owned_table_pointer_published_active`: `false`",
        "`published_active_view_when_equivalent`: `dedicated active storage view`",
        "`fallback_active_view`: `kSourceOwnedCurrentBaselineRuntimeConfig`",
        "`nunchuk_status`: `NOT_TESTED`",
        "Runtime-loaded config is not implemented.",
        "Runtime-config storage is not implemented.",
        "WebSerial/device write is not implemented.",
        "backend/config.pb write path is not implemented.",
        "Firmware flashing automation is not implemented.",
        "Nunchuk remains NOT_TESTED.",
    ):
        require_phrase(doc, phrase, "diagnostic doc")

    validate_diagnostic_fixture(fixture)
    validate_build_fixture(build_fixture, build_report)
    validate_hardware_fixture(hardware_fixture, hardware_plan)

    for text, label in (
        (readme, "runtime config README"),
        (calibration_index, "calibration index"),
        (current_state, "current state"),
        (roadmap, "roadmap"),
    ):
        require_phrase(text, "diagnostic_active_storage_published", label)
        require_phrase(text, "dedicated active storage", label)
        require_phrase(text, "hardware", label)
        require_phrase(text, "candidate", label)


def main() -> None:
    branch = validate_branch()
    mode = branch_mode(branch)
    diff_base = RESULT_BRANCH_BASE if branch == RESULT_BRANCH else BASE_BRANCH
    paths = changed_paths(diff_base)
    validate_changed_paths(paths, mode)
    if mode in {"implementation", "failure_result"}:
        validate_active_storage_publication_source(read_required(ULTIMATE_PATH))
    validate_docs_and_fixtures()
    if mode in {"failure_result", "archived_evidence"}:
        validate_failure_result_branch_docs()
    print("glyph_diagnostic_active_storage_published: PASS")
    print(f"mode={mode}")
    if mode in {"failure_result", "archived_evidence"}:
        print("hardware_failure_result=HARDWARE_FAIL")
        print(f"result_branch={RESULT_BRANCH}")
        print("merge_approved=false")
    print("dedicated_active_storage_active=true")
    print("dedicated_active_storage_published_active=true")
    print("candidate_view_published_active=false")
    print("candidate_owned_table_pointer_published_active=false")
    print("fallback_active_view=kSourceOwnedCurrentBaselineRuntimeConfig")
    if mode == "archived_evidence":
        print("active_source_changes_required=false")
    print("hardware_test_required_before_merge=true")
    print("nunchuk_status=NOT_TESTED")


if __name__ == "__main__":
    main()
