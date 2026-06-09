#!/usr/bin/env python3
"""Validate source-owned active runtime-config preselection branch.

Read-only checker for the source-owned active runtime config scaffold branch.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-active-config-state-source-owned-preselection"
BASE_BRANCH = "configurator"

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
    "src/modes/Ultimate.cpp",
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


def validate_branch() -> None:
    branch = current_branch()
    if branch != EXPECTED_BRANCH:
        fail(f"checker must run on {EXPECTED_BRANCH}, got {branch}")

    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD on this branch")


def changed_paths() -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for status_line in git_lines(["status", "--short"]):
        path = status_line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path in ALLOWED_CHANGED_PATHS:
            continue
        if path.startswith("docs/runtime_config/") or path.startswith("docs/calibration/"):
            continue
        if path.startswith("src/"):
            fail(f"unexpected source path changed for this branch: {path}")
        if path.startswith("tools/"):
            continue
        fail(f"preselection branch changed out-of-scope path: {path}")

    for path in sorted(paths):
        if path in ALLOWED_CHANGED_PATHS:
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


def validate_hot_path_and_digital_comparison(current: str, baseline: str) -> None:
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
        if expr not in baseline:
            fail(f"expected baseline runtime expression missing in configurator source: {expr}")

    block_pattern = re.compile(r"void\s+Ultimate::UpdateDigitalOutputs\([^\)]*\)\s*\{.*?\n\}\n", re.S)
    current_block_match = block_pattern.search(current)
    baseline_block_match = block_pattern.search(baseline)
    if not current_block_match or not baseline_block_match:
        fail("could not locate UpdateDigitalOutputs block in current or baseline source")

    norm = lambda text: "".join(line.strip() for line in text.splitlines() if line.strip())
    if norm(current_block_match.group(0)) != norm(baseline_block_match.group(0)):
        fail("UpdateDigitalOutputs changed in this branch; should remain unchanged")


def validate_plan_payload(payload: dict[str, object], expected_status: str) -> None:
    if payload.get("status") != expected_status:
        fail(f"hardware plan fixture status mismatch: expected {expected_status!r}, got {payload.get('status')!r}")
    if payload.get("build_command") != "pio run -e glyph_mk6":
        fail("hardware plan fixture must use canonical build command")

    rows = payload.get("test_rows")
    if not isinstance(rows, list):
        fail("hardware plan fixture test_rows must be an array")

    seen: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware plan row must be an object")
        row_id = row.get("row_id")
        if not isinstance(row_id, str):
            fail("hardware row_id must be a string")
        seen[row_id] = row

    if set(seen.keys()) != REQUIRED_HARDWARE_ROWS:
        missing = REQUIRED_HARDWARE_ROWS - seen.keys()
        extra = seen.keys() - REQUIRED_HARDWARE_ROWS
        if missing:
            fail(f"hardware plan fixture missing row ids: {sorted(missing)!r}")
        if extra:
            fail(f"hardware plan fixture has unexpected row ids: {sorted(extra)!r}")

    for row_id, row in seen.items():
        if row.get("result") != "NOT_TESTED":
            fail(f"hardware plan row {row_id} must be NOT_TESTED in this branch")


def validate_build_fixture(payload: dict[str, object], build_report: str) -> None:
    if payload.get("schema_name") != "glyph_active_runtime_config_state_source_owned_preselection_build_report":
        fail("unexpected build fixture schema_name")
    if payload.get("canonical_build_command") != "pio run -e glyph_mk6":
        fail("build report fixture must use canonical build command")
    if payload.get("build_command") != "pio run -e glyph_mk6":
        fail("build report fixture legacy build_command must match canonical build command")
    if payload.get("branch") != EXPECTED_BRANCH:
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

def validate_doc_contents(text: str, build_report: str) -> None:
    required_phrases = (
        "runtime-active-config-state-source-owned-preselection",
        "GetActiveRuntimeConfigState",
        "ResolveActiveRuntimeConfig",
        "pio run -e glyph_mk6",
    )
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"runtime preselection doc missing phrase: {phrase}")

    if build_report not in text:
        fail("runtime doc should mention build report file")


def validate_main_docs() -> None:
    doc_text = read_required(DOC_PATH)
    readme_text = read_required(DOC_FIXTURE_PATH)
    plan_text = read_required(HARDWARE_PLAN_MD)
    current_text = read_required(CURRENT_STATE_PATH)
    roadmap_text = read_required(ROADMAP_PATH)
    fixture = load_json_object(DOC_FIXTURE_PATH)
    plan = load_json_object(HARDWARE_PLAN_JSON)

    validate_doc_contents(doc_text, "active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md")
    if "Active Runtime Config State Source-Owned Preselection" not in plan_text:
        fail("hardware plan md missing title text")
    if "NOT_TESTED" not in plan_text:
        fail("hardware plan md must contain NOT_TESTED entries")
    if EXPECTED_BRANCH not in roadmap_text:
        fail("ROADMAP.md must reference the current preselection branch")
    if EXPECTED_BRANCH not in current_text:
        fail("CURRENT_STATE.md must reference the current preselection branch")
    validate_plan_payload(plan, "plan_only")
    validate_build_fixture(fixture, "")


def validate_no_forbidden_files_and_paths() -> None:
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
    validate_hot_path_and_digital_comparison(
        read_required(ULTIMATE_PATH),
        subprocess.run(
            ["git", "show", f"{BASE_BRANCH}:src/modes/Ultimate.cpp"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout,
    )


def main() -> int:
    validate_branch()
    paths = changed_paths()
    validate_changed_paths(paths)

    validate_no_forbidden_files_and_paths()
    validate_main_docs()

    print("glyph_active_runtime_config_state_source_owned_preselection: PASS")
    print(f"- branch: {EXPECTED_BRANCH}")
    print(f"- ultimate_cpp: {rel(ULTIMATE_PATH)}")
    print(f"- changed_paths: {len(paths)}")
    print("firmware_source_changed=true")
    print("runtime_behavior_change=equivalent")
    print("parser_call_present=false")
    print("parsed_table_materialization=false")
    print("storage=false")
    print("write=false")
    print("flashing=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
