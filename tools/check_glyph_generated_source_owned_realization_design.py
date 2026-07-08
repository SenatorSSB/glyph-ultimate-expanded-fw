#!/usr/bin/env python3
"""Validate the generated source-owned runtime realization design packet."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-generated-source-owned-realization-design"
DOWNSTREAM_SCHEMA_SCAFFOLD_BRANCH = "runtime-config-generated-source-owned-schema-scaffold"
DOWNSTREAM_ARTIFACT_INSTALL_BRANCH = "runtime-config-generated-source-owned-artifact-install"
DOWNSTREAM_BASELINE_ARTIFACT_BRANCH = "runtime-config-generated-source-owned-baseline-artifact"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCH_PREFIXES = ("codex/runtime-config-coordinate-native-", "docs-runtime-config-")

DESIGN_DOC = REPO_ROOT / "docs/runtime_config/generated_source_owned_realization_design.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_realization_design.json"
SCHEMA_SCAFFOLD_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_schema_scaffold.json"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"

CHECKER_REL = "tools/check_glyph_generated_source_owned_realization_design.py"
ACTIVE_STORAGE_CHECKER_REL = "tools/check_glyph_diagnostic_active_storage_published.py"
SCHEMA_SCAFFOLD_CHECKER_REL = "tools/check_glyph_generated_source_owned_schema_scaffold.py"
ALLOWED_DOC_PATHS = {
    "docs/runtime_config/generated_source_owned_realization_design.md",
    "docs/runtime_config/fixtures/generated_source_owned_realization_design.json",
    "docs/runtime_config/generated_source_owned_schema_scaffold.md",
    "docs/runtime_config/fixtures/generated_source_owned_schema_scaffold.json",
    "docs/runtime_config/generated_source_owned_generator_contract.md",
    "docs/runtime_config/fixtures/generated_source_owned_generator_contract.json",
    "docs/runtime_config/generated_source_owned_layout_spec.md",
    "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json",
    "docs/runtime_config/fixtures/generated_source_owned_layout_spec.example.json",
    "docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json",
    "docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp",
    "docs/runtime_config/generated_source_owned_artifact_install.md",
    "docs/runtime_config/fixtures/generated_source_owned_artifact_install.json",
    "docs/runtime_config/generated_source_owned_baseline_artifact.md",
    "docs/runtime_config/fixtures/generated_source_owned_baseline_artifact.json",
    "docs/runtime_config/fixtures/coordinate_native_offline_artifact_bundle_manifest.json",
    "docs/runtime_config/fixtures/coordinate_native_offline_export_package.json",
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
    "docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_merge.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_neutral_5.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_cardinal_2.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_diagonal_7.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_merge_5.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_neutral_5.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_cardinal_2.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_diagonal_7.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_tilt3_8.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_missing_table.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_ambiguous_priority.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_invalid_direction_key.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_unresolved_role_state.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_missing_neutral_5.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_direction_key_outside_range.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_raw_coordinate_outside_byte_range.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_malformed_9way_table.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_duplicate_priority.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_missing_capability_metadata.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_runtime_loaded_claim.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge_invalid_extra_field.json",
    "docs/runtime_config/README.md",
    "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
    "docs/runtime_config/runtime_config_activation_alternatives_a_f.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
}
ALLOWED_CHECKER_PATHS = {
    CHECKER_REL,
    ACTIVE_STORAGE_CHECKER_REL,
    SCHEMA_SCAFFOLD_CHECKER_REL,
    "tools/check_glyph_docs_agent_surface.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/dry_run_coordinate_native_runtime_profile.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_runtime_config_activation_alternatives.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
    "tools/generate_source_owned_runtime_config.py",
    "tools/convert_coordinate_native_profile_to_source_owned_spec.py",
}

SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib)(?:/|$)")
FORBIDDEN_CHANGED_PATH_RE = re.compile(
    r"^(?:src/modes/Ultimate\.cpp|HAL/|backend/)|(?:^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
INERT_SOURCE_SCAFFOLD_RE = re.compile(
    r"^src/modes/runtime_config/generated_source_owned/[A-Za-z0-9_./-]+\.(?:h|hpp|hh|cc|cpp)$"
)
FORBIDDEN_SCAFFOLD_TOKENS = (
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

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "active_view_model": "source_owned_generated_tables",
    "ram_backed_active_table_publication_allowed": False,
    "candidate_view_published_active": False,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

REQUIRED_EVIDENCE = {
    "source_owned_active_state_preselection": "HARDWARE_PASS",
    "parsed_candidate_machinery_present_source_owned_active_view": "HARDWARE_PASS",
    "parsed_candidate_view_active": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active": "HARDWARE_FAIL",
    "dedicated_active_storage_published_active": "HARDWARE_FAIL",
}

REQUIRED_DOC_PHRASES = (
    "source-owned active-state preselection",
    "HARDWARE_PASS",
    "parsed/candidate machinery",
    "source-owned active view",
    "HARDWARE_FAIL",
    "diagnostic_active_storage_published_hardware_failure_2026-06-28.md",
    "Candidate-backed active `RuntimeConfigView` publication is unsafe",
    "RAM-backed active runtime table storage appears unsafe",
    "low-level failure mechanism remains unproven",
    "generated C++ source-owned immutable runtime tables",
    "active `RuntimeConfigView` would point to source-owned generated tables",
    "No parser payload path is introduced",
    "No runtime-loaded config is introduced",
    "No persistent storage is introduced",
    "No WebSerial/device write path is introduced",
    "No backend/config.pb write path is introduced",
    "No flashing automation is introduced",
    "No `candidate.view` active publication is introduced",
    "No RAM-backed active table publication is introduced",
    "No nunchuk validation is claimed",
    "Future implementation must be hardware-gated if active source selection behavior changes",
)

REQUIRED_INDEX_PHRASES = (
    "generated_source_owned_realization_design.md",
    "fixtures/generated_source_owned_realization_design.json",
    "source-owned active-state preselection `HARDWARE_PASS`",
    "active-storage",
    "`HARDWARE_FAIL`",
    "Future implementation must be hardware-gated if active source selection behavior changes",
)


class GeneratedSourceOwnedRealizationDesignError(AssertionError):
    """Raised when the generated source-owned design contract drifts."""


def fail(message: str) -> None:
    raise GeneratedSourceOwnedRealizationDesignError(message)


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
    if branch not in {
        EXPECTED_BRANCH,
        "generator-source-owned-layout-spec-contract",
        "runtime-config-coordinate-native-profile-contract",
        DOWNSTREAM_SCHEMA_SCAFFOLD_BRANCH,
        DOWNSTREAM_ARTIFACT_INSTALL_BRANCH,
        DOWNSTREAM_BASELINE_ARTIFACT_BRANCH,
        MERGED_BRANCH,
    } and not any(branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES):
        fail(
            f"checker must run on {EXPECTED_BRANCH}, "
            f"{DOWNSTREAM_SCHEMA_SCAFFOLD_BRANCH}, "
            f"{DOWNSTREAM_ARTIFACT_INSTALL_BRANCH}, "
            f"{DOWNSTREAM_BASELINE_ARTIFACT_BRANCH}, or {MERGED_BRANCH}, got {branch}"
        )
    if branch in {
        EXPECTED_BRANCH,
        DOWNSTREAM_SCHEMA_SCAFFOLD_BRANCH,
        DOWNSTREAM_ARTIFACT_INSTALL_BRANCH,
        DOWNSTREAM_BASELINE_ARTIFACT_BRANCH,
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
    return branch


def status_path(status_line: str) -> str:
    path = status_line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def changed_paths(branch: str) -> set[str]:
    paths: set[str] = set()
    if branch in {EXPECTED_BRANCH, DOWNSTREAM_SCHEMA_SCAFFOLD_BRANCH, DOWNSTREAM_ARTIFACT_INSTALL_BRANCH} or any(
        branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES
    ):
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path and path.endswith("/"):
            directory = REPO_ROOT / path
            if directory.is_dir():
                paths.update(rel(file_path) for file_path in directory.rglob("*") if file_path.is_file())
        elif path:
            paths.add(path)
    return paths


def source_scaffold_files(fixture: dict[str, Any]) -> list[str]:
    scaffold_files = fixture.get("inert_source_scaffold_files")
    if not isinstance(scaffold_files, list) or not all(isinstance(item, str) for item in scaffold_files):
        fail("fixture inert_source_scaffold_files must be a list of strings")
    return scaffold_files


def validate_inert_source_scaffold(path: str, fixture: dict[str, Any], branch: str) -> None:
    scaffold_files = source_scaffold_files(fixture)
    if branch == DOWNSTREAM_SCHEMA_SCAFFOLD_BRANCH and path not in scaffold_files:
        schema_fixture = load_json_object(SCHEMA_SCAFFOLD_FIXTURE)
        scaffold_files = source_scaffold_files(schema_fixture)
    if branch not in {DOWNSTREAM_ARTIFACT_INSTALL_BRANCH, DOWNSTREAM_BASELINE_ARTIFACT_BRANCH} and path not in scaffold_files:
        fail(f"source path changed but is not declared as inert source scaffold: {path}")
    if not INERT_SOURCE_SCAFFOLD_RE.match(path):
        fail(f"inert source scaffold path is outside allowed generated-source-owned area: {path}")
    text = read_required(REPO_ROOT / path)
    if "inert generated-table placeholder" not in text:
        fail(f"inert source scaffold missing explicit inert placeholder marker: {path}")
    for token in FORBIDDEN_SCAFFOLD_TOKENS:
        if token in text:
            fail(f"inert source scaffold contains active wiring token {token!r}: {path}")


def validate_changed_paths(paths: set[str], fixture: dict[str, Any], branch: str) -> None:
    for path in sorted(paths):
        if FORBIDDEN_CHANGED_PATH_RE.search(path):
            fail(f"forbidden HAL/backend/config.pb/storage/write/WebSerial/flashing path changed: {path}")
        if path in ALLOWED_DOC_PATHS or path in ALLOWED_CHECKER_PATHS:
            continue
        if SOURCE_PATH_RE.match(path):
            validate_inert_source_scaffold(path, fixture, branch)
            continue
        if path.startswith("docs/"):
            fail(f"out-of-scope docs path changed on this design branch: {path}")
        if path.startswith("tools/"):
            fail(f"out-of-scope checker/tool path changed on this design branch: {path}")
        fail(f"out-of-scope changed path: {path}")


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized_text = " ".join(text.lower().split())
    missing = [
        phrase
        for phrase in phrases
        if " ".join(phrase.lower().split()) not in normalized_text
    ]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_fixture(fixture: dict[str, Any]) -> None:
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"fixture {key} must be {expected!r}, got {actual!r}")
    evidence = fixture.get("evidence")
    if not isinstance(evidence, dict):
        fail("fixture evidence must be an object")
    for key, expected in REQUIRED_EVIDENCE.items():
        actual = evidence.get(key)
        if actual != expected:
            fail(f"fixture evidence.{key} must be {expected!r}, got {actual!r}")


def validate_docs() -> None:
    design = read_required(DESIGN_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)

    require_phrases(rel(DESIGN_DOC), design, REQUIRED_DOC_PHRASES)
    for path, text in (
        (README, readme),
        (CURRENT_STATE, current_state),
        (ROADMAP, roadmap),
    ):
        require_phrases(rel(path), text, REQUIRED_INDEX_PHRASES)


def main() -> int:
    branch = validate_branch()
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)
    validate_changed_paths(changed_paths(branch), fixture, branch)
    validate_docs()
    print("glyph_generated_source_owned_realization_design: PASS")
    print(f"- branch: {branch}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- design: {rel(DESIGN_DOC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
