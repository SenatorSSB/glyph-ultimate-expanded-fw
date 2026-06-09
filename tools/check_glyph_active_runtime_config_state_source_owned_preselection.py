#!/usr/bin/env python3
"""Validate source-owned active runtime-config preselection branches.

Read-only checker for the implementation branch, its recorded hardware-result
branch, and the merged configurator state.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BRANCH = "runtime-active-config-state-source-owned-preselection"
RESULT_BRANCH = "runtime-active-config-state-source-owned-preselection-hardware-result"
MERGED_BRANCH = "configurator"
BASE_BRANCH = MERGED_BRANCH
ALLOWED_BRANCHES = {IMPLEMENTATION_BRANCH, RESULT_BRANCH, MERGED_BRANCH}

DOC_PATH = REPO_ROOT / "docs/runtime_config/active_runtime_config_state_source_owned_preselection.md"
DOC_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.json"
DOC_BUILD_REPORT_PATH = REPO_ROOT / "docs/runtime_config/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md"
HARDWARE_PLAN_MD = REPO_ROOT / "docs/calibration/glyph_active_runtime_config_state_source_owned_preselection_hardware_plan_2026-06-10.md"
HARDWARE_PLAN_JSON = REPO_ROOT / "docs/calibration/fixtures/glyph_active_runtime_config_state_source_owned_preselection_hardware_plan_2026-06-10.json"
CURRENT_STATE_PATH = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_PATH = REPO_ROOT / "docs/ROADMAP.md"
ULTIMATE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"
CHECKER_PATH = REPO_ROOT / "tools/check_glyph_active_runtime_config_state_source_owned_preselection.py"

ALLOWED_CHANGED_PATHS = {
    "docs/runtime_config/active_runtime_config_state_source_owned_preselection.md",
    "docs/runtime_config/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md",
    "docs/runtime_config/fixtures/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.json",
    "docs/calibration/glyph_active_runtime_config_state_source_owned_preselection_hardware_plan_2026-06-10.md",
    "docs/calibration/fixtures/glyph_active_runtime_config_state_source_owned_preselection_hardware_plan_2026-06-10.json",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/check_glyph_active_runtime_config_state_source_owned_preselection.py",
}

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
    "HOT-PATH-001",
    "NO-PARSER-STATUS-READ-001",
    "NO-PARSED-TABLES-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}


class RuntimeConfigPreselectionError(AssertionError):
    """Raised when preselection branch guardrails are violated."""


def fail(message: str) -> None:
    raise RuntimeConfigPreselectionError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def no_duplicate_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    values: dict[str, object] = {}
    for key, value in pairs:
        if key in values:
            fail(f"duplicate JSON key in payload: {key}")
        values[key] = value
    return values


def load_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=no_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def git_lines(args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    return [line for line in completed.stdout.splitlines() if line.strip()]


def current_branch() -> str:
    branch = git_lines(["branch", "--show-current"])
    if not branch:
        fail("checker could not determine current branch")
    return branch[0]


def base_branch_for(branch: str) -> str:
    if branch == IMPLEMENTATION_BRANCH:
        return BASE_BRANCH
    if branch == RESULT_BRANCH:
        return IMPLEMENTATION_BRANCH
    if branch == MERGED_BRANCH:
        return MERGED_BRANCH
    fail(f"checker must run on {IMPLEMENTATION_BRANCH}, {RESULT_BRANCH}, or {MERGED_BRANCH}, got {branch}")


def validate_branch() -> tuple[str, str]:
    branch = current_branch()
    if branch not in ALLOWED_BRANCHES:
        fail(f"checker must run on {IMPLEMENTATION_BRANCH}, {RESULT_BRANCH}, or {MERGED_BRANCH}, got {branch}")

    base_branch = base_branch_for(branch)

    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_branch, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{base_branch} must be an ancestor of HEAD on this branch")

    return branch, base_branch


def changed_paths(base_branch: str) -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{base_branch}...HEAD"]))
    for status_line in git_lines(["status", "--short"]):
        path = status_line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return paths


def validate_changed_paths(paths: set[str], branch: str) -> None:
    allowed_changed_paths = set(ALLOWED_CHANGED_PATHS)
    if branch == IMPLEMENTATION_BRANCH:
        allowed_changed_paths.add("src/modes/Ultimate.cpp")

    for path in sorted(paths):
        if path in allowed_changed_paths:
            continue
        if path.startswith("docs/runtime_config/") or path.startswith("docs/calibration/"):
            continue
        if path.startswith("src/"):
            if branch == RESULT_BRANCH:
                fail(f"result branch may not change firmware source relative to {IMPLEMENTATION_BRANCH}: {path}")
            fail(f"unexpected source path changed for this branch: {path}")
        if path.startswith("tools/"):
            continue
        fail(f"preselection branch changed out-of-scope path: {path}")

    for path in sorted(paths):
        if path in allowed_changed_paths:
            continue
        if path.startswith("src/"):
            continue
        lowered = path.lower()
        if "hal" in lowered or "backend" in lowered or "write" in lowered or "flashing" in lowered or "storage" in lowered:
            fail(f"forbidden infra path change for firmware-boundary branch: {path}")


def strip_cpp_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    in_block = False
    while index < len(text):
        if in_block:
            end = text.find("*/", index)
            if end == -1:
                break
            in_block = False
            index = end + 2
            continue

        if text.startswith("//", index):
            newline = text.find("\n", index)
            if newline == -1:
                break
            index = newline + 1
            continue

        if text.startswith("/*", index):
            in_block = True
            index += 2
            continue

        result.append(text[index])
        index += 1

    return "".join(result)


def extract_function(text: str, name: str) -> str:
    pattern = rf"\b{re.escape(name)}\b\s*\([^\)]*\)\s*\{{"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing function: {name}()")
    start = match.start()
    brace = 0
    in_block = False

    # Start parsing from the opening brace of the function definition.
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


def assert_line_binding(source: str) -> None:
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in source:
        fail("UpdateAnalogOutputs must bind runtime_config via ResolveActiveRuntimeConfig()")


def validate_no_forbidden_source_patterns(source: str, active_no_comments: str) -> None:
    forbidden = (
        "kPhase7AD3GlobalParseResult.status",
        "ParseUltimateRuntimeConfigPayload",
        "kPhase7AD3GlobalParseResult",
        "kPhase7AD1",
        "D2B",
        "D3",
        "retained payload",
        "kPhase7ACompiledPayload",
        "UltimateRuntimeConfigCompiledPayload",
        "ParseUltimateRuntimeConfigPayload",
        "WebSerial",
        "flash",
        "write",
    )

    # Intentionally permit expected tokens in comments or historical docs; firmware source is strict.
    for token in forbidden:
        if token in active_no_comments:
            fail(f"forbidden firmware-source token found in Ultimate.cpp: {token}")

    # Ensure resolver path does not inspect parser/global parse status.
    resolve_body = extract_function(source, "ResolveActiveRuntimeConfig")
    if "kPhase7AD3GlobalParseResult" in resolve_body or "ParseUltimateRuntimeConfigPayload" in resolve_body:
        fail("ResolveActiveRuntimeConfig must not inspect parser result state")

    if "active_state" in resolve_body:
        if "*GetActiveRuntimeConfigState().active_view" not in resolve_body:
            fail("ResolveActiveRuntimeConfig must return active state via active_view")

    active_source = strip_cpp_comments(source)
    if "GetActiveRuntimeConfigState" not in active_source:
        fail("GetActiveRuntimeConfigState() must exist")

    if "source" in active_source and "source" in "source" and "GetActiveRuntimeConfigState" in active_source:
        # keep only basic check for explicit hot-path reads
        update_body = extract_function(source, "UpdateAnalogOutputs")
        if "active_config.source" in update_body or "active_state.source" in update_body or "status" in update_body:
            # narrow to explicit references
            if re.search(r"\bsource\s*\.\s*\w+", update_body) or re.search(r"\bstatus\s*\.\s*\w+", update_body):
                fail("UpdateAnalogOutputs may not inspect ActiveRuntimeConfigState.source or .status")


def validate_active_state_functions(source: str, active_source: str) -> None:
    # Ensure activation helper exists and selects fallback deterministically.
    if "enum class RuntimeConfigSource" not in active_source:
        fail("RuntimeConfigSource enum missing")
    if "enum class RuntimeConfigActivationStatus" not in active_source:
        fail("RuntimeConfigActivationStatus enum missing")
    if "struct ActiveRuntimeConfigState" not in active_source:
        fail("ActiveRuntimeConfigState struct missing")

    get_state_body = extract_function(source, "GetActiveRuntimeConfigState")
    for token in (
        "ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)",
        "&kSourceOwnedCurrentBaselineRuntimeConfig",
        "&kKnownGoodRuntimeConfig",
        "RuntimeConfigSource::SourceOwnedBaseline",
        "RuntimeConfigSource::KnownGoodFallback",
        "RuntimeConfigActivationStatus::SourceOwnedSelected",
        "RuntimeConfigActivationStatus::FallbackSelected",
    ):
        if token not in get_state_body:
            fail(f"GetActiveRuntimeConfigState missing token: {token}")

    resolve_body = extract_function(source, "ResolveActiveRuntimeConfig")
    if "*GetActiveRuntimeConfigState().active_view" not in resolve_body:
        fail("ResolveActiveRuntimeConfig must dereference GetActiveRuntimeConfigState().active_view")


def validate_hot_path_and_digital_comparison(current: str, baseline: str | None) -> None:
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in current:
        fail("hot path binding in UpdateAnalogOutputs must use ResolveActiveRuntimeConfig")

    for expr in (
        "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
        "state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;",
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "outputs.buttonR = inputs.rf6;",
    ):
        if expr not in current:
            fail(f"expected runtime expression missing in Ultimate.cpp: {expr}")
        if baseline is not None and expr not in baseline:
            fail(f"expected baseline runtime expression missing in configurator source: {expr}")

    if baseline is None:
        return

    block_pattern = re.compile(r"void\s+Ultimate::UpdateDigitalOutputs\([^\)]*\)\s*\{.*?\n\}\n", re.S)
    current_block_match = block_pattern.search(current)
    baseline_block_match = block_pattern.search(baseline)
    if not current_block_match or not baseline_block_match:
        fail("could not locate UpdateDigitalOutputs block in current or baseline source")

    norm = lambda text: "".join(line.strip() for line in text.splitlines() if line.strip())
    if norm(current_block_match.group(0)) != norm(baseline_block_match.group(0)):
        fail("UpdateDigitalOutputs changed in this branch; should remain unchanged")


def validate_rows(rows: object, expected_results: dict[str, str], result_label: str) -> None:
    if not isinstance(rows, list):
        fail(f"{result_label} rows must be an array")

    seen: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail(f"{result_label} row must be an object")
        row_id = row.get("row_id")
        if not isinstance(row_id, str):
            fail(f"{result_label} row_id must be a string")
        seen[row_id] = row

    if set(seen.keys()) != REQUIRED_HARDWARE_ROWS:
        missing = REQUIRED_HARDWARE_ROWS - seen.keys()
        extra = seen.keys() - REQUIRED_HARDWARE_ROWS
        if missing:
            fail(f"{result_label} missing row ids: {sorted(missing)!r}")
        if extra:
            fail(f"{result_label} has unexpected row ids: {sorted(extra)!r}")

    for row_id, expected_result in expected_results.items():
        row = seen[row_id]
        if row.get("result") != expected_result:
            fail(f"{result_label} row {row_id} must be {expected_result}, got {row.get('result')!r}")


def validate_implementation_hardware_plan(payload: dict[str, object]) -> None:
    if payload.get("schema_name") != "glyph_active_runtime_config_state_source_owned_preselection_hardware_plan":
        fail("implementation hardware fixture schema_name mismatch")
    if payload.get("plan_version") != 1:
        fail("implementation hardware fixture plan_version must be 1")
    if payload.get("status") != "plan_only":
        fail(f"implementation hardware fixture status mismatch: expected 'plan_only', got {payload.get('status')!r}")
    if payload.get("branch") != IMPLEMENTATION_BRANCH:
        fail("implementation hardware fixture branch mismatch")
    if payload.get("build_command") != "pio run -e glyph_mk6":
        fail("implementation hardware fixture must use canonical build command")
    if payload.get("hardware_result_recorded") is not False:
        fail("implementation hardware fixture hardware_result_recorded must be false")
    if payload.get("commit_sha_under_test") != "unknown":
        fail("implementation hardware fixture commit_sha_under_test must be unknown")
    if payload.get("firmware_artifact_path") != "unknown":
        fail("implementation hardware fixture firmware_artifact_path must be unknown")
    if payload.get("firmware_artifact_sha256") != "unknown":
        fail("implementation hardware fixture firmware_artifact_sha256 must be unknown")
    if payload.get("tester") != "unknown":
        fail("implementation hardware fixture tester must be unknown")
    if payload.get("test_date") != "unknown":
        fail("implementation hardware fixture test_date must be unknown")
    if payload.get("result_branch") is not None:
        fail("implementation hardware fixture must not record a result_branch")
    if payload.get("build_source") is not None:
        fail("implementation hardware fixture must not record build_source")
    if payload.get("build_report_path") is not None:
        fail("implementation hardware fixture must not record build_report_path")
    if payload.get("build_report_status") is not None:
        fail("implementation hardware fixture must not record build_report_status")
    if payload.get("result_source") is not None:
        fail("implementation hardware fixture must not record result_source")
    if payload.get("source_report_text") is not None:
        fail("implementation hardware fixture must not record source_report_text")
    if payload.get("result_date") is not None:
        fail("implementation hardware fixture must not record result_date")
    if payload.get("overall_result") is not None:
        fail("implementation hardware fixture must not record overall_result")
    if payload.get("firmware_source_changed_in_implementation_branch") is not None:
        fail("implementation hardware fixture must not record firmware_source_changed flags")
    if payload.get("parser_status_read_in_analog_hot_path") is not None:
        fail("implementation hardware fixture must not record parser hot-path flags")
    if payload.get("parser_call_added") is not None:
        fail("implementation hardware fixture must not record parser_call_added")
    if payload.get("parsed_table_materialization_added") is not None:
        fail("implementation hardware fixture must not record parsed_table_materialization_added")
    if payload.get("storage_write_webserial_flashing_added") is not None:
        fail("implementation hardware fixture must not record storage_write_webserial_flashing_added")
    if payload.get("nunchuk_status") is not None:
        fail("implementation hardware fixture must not record nunchuk_status")

    intent = payload.get("intent")
    if not isinstance(intent, dict):
        fail("implementation hardware fixture intent must be an object")
    if intent.get("description") != "Scaffold verification for source-owned active runtime config preselection.":
        fail("implementation hardware fixture intent description mismatch")
    if intent.get("scope") != [
        "source-owned preselection state",
        "active_view-only analog hot-path consumption",
        "no parsed table materialization",
        "no runtime-loaded parser/transport/storage integration",
    ]:
        fail("implementation hardware fixture intent scope mismatch")
    if intent.get("non_claims") != ["no nunchuk validation claim"]:
        fail("implementation hardware fixture intent non_claims mismatch")

    expected_results = {row_id: "NOT_TESTED" for row_id in REQUIRED_HARDWARE_ROWS}
    validate_rows(payload.get("test_rows"), expected_results, "implementation hardware fixture")


def validate_result_hardware_record(payload: dict[str, object]) -> None:
    if payload.get("schema_name") != "glyph_active_runtime_config_state_source_owned_preselection_hardware_result":
        fail("result hardware fixture schema_name mismatch")
    if payload.get("plan_version") != 1:
        fail("result hardware fixture plan_version must be 1")
    if payload.get("status") != "HARDWARE_PASS":
        fail(f"result hardware fixture status mismatch: expected 'HARDWARE_PASS', got {payload.get('status')!r}")
    if payload.get("branch") != IMPLEMENTATION_BRANCH:
        fail("result hardware fixture branch mismatch")
    if payload.get("result_branch") != RESULT_BRANCH:
        fail("result hardware fixture result_branch mismatch")
    if payload.get("build_command") != "pio run -e glyph_mk6":
        fail("result hardware fixture must use canonical build command")
    if payload.get("build_source") != "local build artifact already recorded in the build report":
        fail("result hardware fixture build_source mismatch")
    if payload.get("build_report_path") != "docs/runtime_config/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md":
        fail("result hardware fixture build_report_path mismatch")
    if payload.get("build_report_status") != "build_completed":
        fail("result hardware fixture build_report_status must be build_completed")
    if payload.get("hardware_result_recorded") is not True:
        fail("result hardware fixture hardware_result_recorded must be true")
    if payload.get("result_source") != "operator-recorded":
        fail("result hardware fixture result_source mismatch")
    if payload.get("source_report_text") != "All worked on branch runtime-active-config-state-source-owned-preselection when I built and flashed.":
        fail("result hardware fixture source_report_text mismatch")
    if payload.get("result_date") != "2026-06-10":
        fail("result hardware fixture result_date mismatch")
    if payload.get("commit_sha_under_test") != "unknown":
        fail("result hardware fixture commit_sha_under_test must be unknown")
    if payload.get("firmware_artifact_path") != "unknown":
        fail("result hardware fixture firmware_artifact_path must be unknown")
    if payload.get("firmware_artifact_sha256") != "unknown":
        fail("result hardware fixture firmware_artifact_sha256 must be unknown")
    if payload.get("tester") != "operator-recorded":
        fail("result hardware fixture tester mismatch")
    if payload.get("test_date") != "2026-06-10":
        fail("result hardware fixture test_date mismatch")
    if payload.get("overall_result") != "HARDWARE_PASS":
        fail("result hardware fixture overall_result must be HARDWARE_PASS")
    if payload.get("firmware_source_changed_in_implementation_branch") is not True:
        fail("result hardware fixture must record implementation-branch source changes as true")
    if payload.get("firmware_source_changed_in_result_branch") is not False:
        fail("result hardware fixture must record result-branch source changes as false")
    if payload.get("parser_status_read_in_analog_hot_path") is not False:
        fail("result hardware fixture parser_status_read_in_analog_hot_path must be false")
    if payload.get("parser_call_added") is not False:
        fail("result hardware fixture parser_call_added must be false")
    if payload.get("parsed_table_materialization_added") is not False:
        fail("result hardware fixture parsed_table_materialization_added must be false")
    if payload.get("storage_write_webserial_flashing_added") is not False:
        fail("result hardware fixture storage_write_webserial_flashing_added must be false")
    if payload.get("nunchuk_status") != "NOT_TESTED":
        fail("result hardware fixture nunchuk_status must be NOT_TESTED")

    intent = payload.get("intent")
    if not isinstance(intent, dict):
        fail("result hardware fixture intent must be an object")
    if intent.get("description") != "Hardware result record for source-owned active runtime config preselection.":
        fail("result hardware fixture intent description mismatch")
    if intent.get("scope") != [
        "source-owned preselection state",
        "active_view-only analog hot-path consumption",
        "no parsed table materialization",
        "no runtime-loaded parser/transport/storage integration",
    ]:
        fail("result hardware fixture intent scope mismatch")
    if intent.get("non_claims") != [
        "no runtime-loaded config implemented",
        "no parsed table materialization implemented",
        "no storage implemented",
        "no WebSerial/device write implemented",
        "no flashing automation implemented",
        "no nunchuk validation claim",
    ]:
        fail("result hardware fixture intent non_claims mismatch")

    expected_results = {row_id: "PASS" for row_id in REQUIRED_HARDWARE_ROWS if row_id != "NUNCHUK-001"}
    expected_results["NUNCHUK-001"] = "NOT_TESTED"
    validate_rows(payload.get("test_rows"), expected_results, "result hardware fixture")


def validate_build_fixture(payload: dict[str, object], build_report: str) -> None:
    if payload.get("schema_name") != "glyph_active_runtime_config_state_source_owned_preselection_build_report":
        fail("unexpected build fixture schema_name")
    if payload.get("canonical_build_command") != "pio run -e glyph_mk6":
        fail("build report fixture must use canonical build command")
    if payload.get("build_command") != "pio run -e glyph_mk6":
        fail("build report fixture legacy build_command must match canonical build command")
    if payload.get("branch") != IMPLEMENTATION_BRANCH:
        fail("build report fixture branch mismatch")
    if payload.get("baseline_branch") != BASE_BRANCH:
        fail("build report fixture baseline branch mismatch")
    if payload.get("build_completed") is not True:
        fail("build report fixture build_completed must be true")
    if payload.get("build_exit_code") != 0:
        fail("build report fixture build_exit_code must be 0")
    if payload.get("canonical_build_available_in_agent_environment") is not False:
        fail("build report fixture must record canonical build unavailable as False")
    if payload.get("actual_local_build_command") != "./scripts/build-glyph-mk6-quiet.sh":
        fail("build report fixture must record actual fallback build command")
    if payload.get("actual_local_build_completed") is not True:
        fail("build report fixture actual_local_build_completed must be true")
    if payload.get("artifact_hashes_are_rebuild_stable") is not False:
        fail("artifact_hashes_are_rebuild_stable must be false")
    if payload.get("artifact_hashes_are_checker_gate") is not False:
        fail("artifact_hashes_are_checker_gate must be false")
    if payload.get("hardware_result_claimed") is not False:
        fail("hardware_result_claimed must be false")

    if payload.get("build_artifacts") is None:
        fail("build_artifacts must be present")
    rows = payload.get("build_artifacts")
    if not isinstance(rows, list):
        fail("build_artifacts must be a list")
    if len(rows) != 3:
        fail("build_artifacts must include uf2, elf, and bin observations")

    seen_types = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            fail(f"build_artifacts[{idx}] must be an object")
        artifact_type = row.get("artifact_type")
        if artifact_type not in ("uf2", "elf", "bin"):
            fail(f"unexpected artifact_type {artifact_type!r} in build_artifacts")
        path = row.get("path")
        if not isinstance(path, str) or not path:
            fail("artifact observation must include non-empty path")
        if row.get("available") is not True:
            fail(f"{artifact_type} artifact must be available: {path}")
        size = row.get("size_bytes")
        if not isinstance(size, int) or size <= 0:
            fail(f"{artifact_type} artifact size_bytes must be positive")
        sha = row.get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            fail(f"{artifact_type} artifact sha256 must be 64-lowercase hex")
        seen_types.add(artifact_type)

    if seen_types != {"uf2", "elf", "bin"}:
        fail("build_artifacts must include exactly uf2, elf, and bin")

    if payload.get("nunchuk_status") != "NOT_TESTED":
        fail("build report fixture must leave nunchuk_status as NOT_TESTED")
    if payload.get("status") not in ("build_completed", "scaffold_ready", "scaffold_verified", "scaffold_with_build"):
        fail("build report fixture status is missing/invalid")

def validate_doc_contents(text: str, branch: str) -> None:
    required_phrases = (
        "runtime-active-config-state-source-owned-preselection",
        "GetActiveRuntimeConfigState",
        "ResolveActiveRuntimeConfig",
        "pio run -e glyph_mk6",
        "active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md",
    )
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"runtime preselection doc missing phrase: {phrase}")

    if branch in (RESULT_BRANCH, MERGED_BRANCH):
        for phrase in (
            "runtime-active-config-state-source-owned-preselection-hardware-result",
            "HARDWARE_PASS",
            "RF5 did not disconnect",
            "RF6 did not disconnect",
            "LT6 did not disconnect",
            "safe enough to become the repair architecture basis",
            "Nunchuk remains NOT_TESTED",
        ):
            if phrase not in text:
                fail(f"runtime result doc missing phrase: {phrase}")


def validate_main_docs(branch: str) -> None:
    doc_text = read_required(DOC_PATH)
    readme_text = read_required(DOC_FIXTURE_PATH)
    build_report_text = read_required(DOC_BUILD_REPORT_PATH)
    plan_text = read_required(HARDWARE_PLAN_MD)
    current_text = read_required(CURRENT_STATE_PATH)
    roadmap_text = read_required(ROADMAP_PATH)
    fixture = load_json_object(DOC_FIXTURE_PATH)
    plan = load_json_object(HARDWARE_PLAN_JSON)
    status = plan.get("status")

    validate_doc_contents(doc_text, branch)
    if branch == IMPLEMENTATION_BRANCH:
        if status == "plan_only":
            if "Hardware Plan" not in plan_text:
                fail("implementation hardware packet should still identify as a hardware plan")
            if "NOT_TESTED" not in plan_text:
                fail("implementation hardware packet must contain NOT_TESTED entries")
            validate_implementation_hardware_plan(plan)
        elif status == "HARDWARE_PASS":
            if "Hardware Result" not in plan_text:
                fail("implementation hardware packet should identify as a hardware result after preservation")
            if "HARDWARE_PASS" not in plan_text:
                fail("implementation hardware packet must record HARDWARE_PASS after preservation")
            if "safe enough to serve as the repair-architecture basis" not in current_text:
                fail("CURRENT_STATE.md must record the repair-architecture basis conclusion")
            if "HARDWARE_PASS" not in current_text:
                fail("CURRENT_STATE.md must mention HARDWARE_PASS")
            validate_result_hardware_record(plan)
        else:
            fail(f"unsupported implementation hardware fixture status: {status!r}")
        if IMPLEMENTATION_BRANCH not in roadmap_text:
            fail("ROADMAP.md must reference the implementation branch")
        if IMPLEMENTATION_BRANCH not in current_text:
            fail("CURRENT_STATE.md must reference the implementation branch")
    else:
        if "Hardware Result" not in plan_text:
            fail("result hardware packet must identify as a hardware result")
        if "HARDWARE_PASS" not in plan_text:
            fail("result hardware packet must record HARDWARE_PASS")
        if RESULT_BRANCH not in roadmap_text:
            fail("ROADMAP.md must reference the result branch")
        if RESULT_BRANCH not in current_text:
            fail("CURRENT_STATE.md must reference the result branch")
        if "safe enough to serve as the repair-architecture basis" not in current_text:
            fail("CURRENT_STATE.md must record the repair-architecture basis conclusion")
        if "HARDWARE_PASS" not in current_text:
            fail("CURRENT_STATE.md must mention HARDWARE_PASS")
        validate_result_hardware_record(plan)
    if "status: build_completed" not in build_report_text:
        fail("build report markdown must remain completed")
    if "`hardware_result_claimed`: `false`" not in build_report_text:
        fail("build report markdown must keep hardware_result_claimed false")
    validate_build_fixture(fixture, "")


def validate_no_forbidden_files_and_paths(base_branch: str, branch: str) -> None:
    # enforce parser call not present in Ultimate.cpp
    ultimate_source = read_required(ULTIMATE_PATH)
    active_source = strip_cpp_comments(ultimate_source)
    if "ParseUltimateRuntimeConfigPayload" in active_source:
        fail("Ultimate.cpp must not call ParseUltimateRuntimeConfigPayload")
    if "kPhase7AD3GlobalParseResult.status" in active_source:
        fail("Ultimate.cpp must not read kPhase7AD3GlobalParseResult.status")
    assert_line_binding(ultimate_source)
    validate_active_state_functions(ultimate_source, active_source)
    validate_no_forbidden_source_patterns(ultimate_source, active_source)
    if branch != MERGED_BRANCH:
        validate_hot_path_and_digital_comparison(
            read_required(ULTIMATE_PATH),
            subprocess.run(
                ["git", "show", f"{base_branch}:src/modes/Ultimate.cpp"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            ).stdout,
        )
    else:
        validate_hot_path_and_digital_comparison(read_required(ULTIMATE_PATH), None)


def main() -> int:
    branch, base_branch = validate_branch()
    if branch != MERGED_BRANCH:
        paths = changed_paths(base_branch)
        validate_changed_paths(paths, branch)
    else:
        paths = set()

    validate_no_forbidden_files_and_paths(base_branch, branch)
    validate_main_docs(branch)

    print("glyph_active_runtime_config_state_source_owned_preselection: PASS")
    print(f"- branch: {branch}")
    print(f"- base_branch: {base_branch}")
    print(f"- ultimate_cpp: {rel(ULTIMATE_PATH)}")
    print(f"- changed_paths: {len(paths)}")
    print(f"firmware_source_changed={'true' if branch == IMPLEMENTATION_BRANCH else 'false'}")
    print("runtime_behavior_change=equivalent")
    print("parser_call_present=false")
    print("parsed_table_materialization=false")
    print("storage=false")
    print("write=false")
    print("flashing=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
