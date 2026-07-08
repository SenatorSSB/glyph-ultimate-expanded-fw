#!/usr/bin/env python3
"""Validate the inert generated source-owned artifact install workflow."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-generated-source-owned-artifact-install"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
DOWNSTREAM_BASELINE_ARTIFACT_BRANCH = "runtime-config-generated-source-owned-baseline-artifact"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

INSTALL_DOC = REPO_ROOT / "docs/runtime_config/generated_source_owned_artifact_install.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_artifact_install.json"
INPUT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json"
LAYOUT_SPEC_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
GENERATOR = REPO_ROOT / "tools/generate_source_owned_runtime_config.py"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
SPEC_INPUT_MODE = "--emit-from-layout-spec"

INERT_SOURCE_PREFIX = "src/modes/runtime_config/generated_source_owned/"
INERT_SOURCE_RE = re.compile(
    r"^src/modes/runtime_config/generated_source_owned/[A-Za-z0-9_.-]+\.(?:h|hpp|hh|cc|cpp)$"
)

ALLOWED_EXACT_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "tools/generate_source_owned_runtime_config.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_diagnostic_active_storage_published.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_docs_agent_surface.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
}

FORBIDDEN_CHANGED_PATH_RE = re.compile(
    r"^(?:src/modes/Ultimate\.cpp|HAL/|backend/)|"
    r"(?:^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

REQUIRED_ARTIFACT_MARKERS = (
    "generated source-owned runtime config artifact",
    "inert generated-table placeholder",
    "not wired into runtime selection",
)
BASELINE_ARTIFACT = (
    "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
)

FORBIDDEN_ARTIFACT_TOKENS = (
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
    "artifact_install_only": True,
    "generated_artifact_installed_under_inert_source_path": True,
    "generated_tables_wired_active": False,
    "generated_artifacts_written_to_active_source_path_by_default": False,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

REQUIRED_DOC_PHRASES = (
    "generated_source_owned_generator_contract.md",
    "generated_source_owned_schema_scaffold.md",
    "--emit-from-layout-spec",
    "generated_source_owned_layout_spec.json",
    "active-storage `HARDWARE_FAIL` evidence",
    "Source-owned active-state preselection has recorded `HARDWARE_PASS` evidence",
    "Future hardware gate required before generated source-owned tables are selected active",
    "not included by `src/modes/Ultimate.cpp`",
    "not wired into runtime selection",
    "does not change active firmware behavior",
    "low-level failure mechanism remains unproven",
    "Nunchuk remains `NOT_TESTED`",
)

REQUIRED_INDEX_PHRASES = (
    "generated_source_owned_artifact_install.md",
    "fixtures/generated_source_owned_artifact_install.json",
    "generated_source_owned_generator_contract.md",
    "generated_source_owned_schema_scaffold.md",
    "--emit-from-layout-spec",
    "generated_source_owned_layout_spec.json",
    "active-storage `HARDWARE_FAIL` evidence",
    "source-owned active-state preselection `HARDWARE_PASS`",
    "future hardware gate required before generated source-owned tables are selected active",
)


class GeneratedSourceOwnedArtifactInstallError(AssertionError):
    """Raised when the generated source-owned artifact install contract drifts."""


def fail(message: str) -> None:
    raise GeneratedSourceOwnedArtifactInstallError(message)


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
    if branch not in {
        EXPECTED_BRANCH,
        "generator-source-owned-layout-spec-contract",
        "runtime-config-coordinate-native-profile-contract",
        DOWNSTREAM_BASELINE_ARTIFACT_BRANCH,
        MERGED_BRANCH,
        RECOVERY_BRANCH,
    }:
        fail(
            f"checker must run on {EXPECTED_BRANCH}, "
            f"{DOWNSTREAM_BASELINE_ARTIFACT_BRANCH}, or {MERGED_BRANCH}, got {branch}"
        )
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
    if branch in {EXPECTED_BRANCH, DOWNSTREAM_BASELINE_ARTIFACT_BRANCH, RECOVERY_BRANCH}:
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


def validate_artifact_text(path: str) -> None:
    if not INERT_SOURCE_RE.match(path):
        fail(f"generated artifact is outside inert source-owned artifact path: {path}")
    text = read_required(REPO_ROOT / path)
    for marker in REQUIRED_ARTIFACT_MARKERS:
        if marker not in text:
            fail(f"generated artifact missing marker {marker!r}: {path}")
    for token in FORBIDDEN_ARTIFACT_TOKENS:
        if token in text:
            fail(f"generated artifact contains active wiring token {token!r}: {path}")


def validate_changed_paths(paths: set[str], installed_artifacts: list[str]) -> None:
    for path in sorted(paths):
        if path in ALLOWED_EXACT_PATHS:
            continue
        if FORBIDDEN_CHANGED_PATH_RE.search(path):
            fail(f"forbidden runtime/storage/write/WebSerial/flashing/backend path changed: {path}")
        if path.startswith("docs/runtime_config/") or path.startswith("docs/agent_framework/"):
            continue
        if path.startswith(INERT_SOURCE_PREFIX):
            if path not in installed_artifacts and path != BASELINE_ARTIFACT:
                fail(f"inert source artifact changed but is not declared in fixture: {path}")
            validate_artifact_text(path)
            continue
        if path.startswith("docs/"):
            fail(f"out-of-scope docs path changed: {path}")
        if path.startswith("tools/"):
            fail(f"out-of-scope tool/checker path changed: {path}")
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


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"fixture {key} must be {expected!r}, got {actual!r}")
    generator = fixture.get("generator")
    if not isinstance(generator, dict):
        fail("fixture generator must be an object")
    if generator.get("script") != "tools/generate_source_owned_runtime_config.py":
        fail("fixture generator.script must point to the stdlib generator")
    if generator.get("stdlib_only") is not True:
        fail("fixture generator.stdlib_only must be true")
    if generator.get("default_output_to_active_source_path") is not False:
        fail("fixture generator.default_output_to_active_source_path must be false")
    if generator.get("explicit_install_mode") != "--install-inert-source-artifact":
        fail("fixture generator.explicit_install_mode must document install mode")
    if generator.get("spec_input_mode") != SPEC_INPUT_MODE:
        fail(f"fixture generator.spec_input_mode must be {SPEC_INPUT_MODE!r}")
    if generator.get("spec_input_fixture") != rel(LAYOUT_SPEC_FIXTURE):
        fail(f"fixture generator.spec_input_fixture must be {rel(LAYOUT_SPEC_FIXTURE)!r}")

    installed_artifacts = fixture.get("installed_artifacts")
    if not isinstance(installed_artifacts, list) or not all(isinstance(item, str) for item in installed_artifacts):
        fail("fixture installed_artifacts must be a list of strings")
    if not installed_artifacts:
        fail("fixture installed_artifacts must declare at least one artifact")
    for path in installed_artifacts:
        validate_artifact_text(path)
    return installed_artifacts


def validate_deterministic_generation(installed_artifacts: list[str]) -> None:
    if len(installed_artifacts) != 1:
        fail("deterministic install checker currently expects exactly one installed artifact")
    completed = subprocess.run(
        ["python3", str(GENERATOR), str(INPUT_FIXTURE)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("generator failed on example input: " + completed.stderr.strip())
    installed_text = read_required(REPO_ROOT / installed_artifacts[0])
    if completed.stdout != installed_text:
        fail("installed generated source artifact does not match deterministic generator output")
    spec_completed = subprocess.run(
        ["python3", str(GENERATOR), SPEC_INPUT_MODE, str(LAYOUT_SPEC_FIXTURE)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if spec_completed.returncode != 0:
        fail("spec-input generator failed on layout spec packet: " + spec_completed.stderr.strip())
    if spec_completed.stdout != installed_text:
        fail("spec-input generator output does not match installed generated source artifact")


def validate_docs() -> None:
    install_doc = read_required(INSTALL_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)
    require_phrases(rel(INSTALL_DOC), install_doc, REQUIRED_DOC_PHRASES)
    for path, text in (
        (README, readme),
        (CURRENT_STATE, current_state),
        (ROADMAP, roadmap),
    ):
        require_phrases(rel(path), text, REQUIRED_INDEX_PHRASES)


def main() -> int:
    branch = validate_branch()
    fixture = load_json_object(FIXTURE)
    installed_artifacts = validate_fixture(fixture)
    validate_changed_paths(changed_paths(branch), installed_artifacts)
    validate_deterministic_generation(installed_artifacts)
    validate_docs()
    print("glyph_generated_source_owned_artifact_install: PASS")
    print(f"- branch: {branch}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- installed artifact: {installed_artifacts[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
