#!/usr/bin/env python3
"""Validate the source-owned table replacement design packet."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-source-owned-table-replacement-design"
GENERATOR_CONTRACT_BRANCH = "runtime-config-source-owned-table-replacement-generator-contract"
TABLE_CONTENT_DIAGNOSTIC_BRANCH = "runtime-config-diagnostic-source-owned-table-content-replacement"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

DESIGN_DOC = REPO_ROOT / "docs/runtime_config/source_owned_table_replacement_design.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_table_replacement_design.json"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_source_owned_table_replacement_design.py"
GENERATOR_CONTRACT_CHECKER_REL = "tools/check_glyph_source_owned_table_replacement_generator_contract.py"
GENERATOR_CONTRACT_TOOL_REL = "tools/generate_source_owned_table_replacement.py"

ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
    GENERATOR_CONTRACT_CHECKER_REL,
    GENERATOR_CONTRACT_TOOL_REL,
}
ALLOWED_PREFIXES = ("docs/runtime_config/",)
ALLOWED_EXISTING_CHECKERS = {
    "tools/check_glyph_diagnostic_generated_source_owned_baseline_active.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
}

FORBIDDEN_SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)")
FORBIDDEN_SPECIAL_PATH_RE = re.compile(
    r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "active_view_selection_changed": False,
    "runtime_config_view_replacement_allowed": False,
    "source_owned_table_content_replacement_design_only": True,
    "source_owned_table_content_replacement_wired": False,
    "ram_backed_active_table_publication_allowed": False,
    "generated_source_owned_baseline_active_publication_allowed": False,
    "candidate_view_published_active": False,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

EXPECTED_EVIDENCE: dict[str, str] = {
    "source_owned_active_state_preselection": "HARDWARE_PASS",
    "parsed_candidate_machinery_present_source_owned_active_view": "HARDWARE_PASS",
    "parsed_candidate_view_active": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active": "HARDWARE_FAIL",
    "dedicated_active_storage_published_active": "HARDWARE_FAIL",
    "generated_source_owned_baseline_active": "HARDWARE_FAIL",
}

REQUIRED_DOC_PHRASES = (
    "generated source-owned baseline active HARDWARE_FAIL",
    "dedicated active storage HARDWARE_FAIL",
    "source-owned active-state preselection HARDWARE_PASS",
    "source-owned table replacement does not change RuntimeConfigView selection",
    "future implementation changing table contents must be hardware-gated before merge if active behavior changes",
)

REQUIRED_DESIGN_PHRASES = (
    "existing kSourceOwnedCurrentBaselineRuntimeConfig symbol/path remains active",
    "existing active RuntimeConfigView remains unchanged",
    "existing active publication path remains unchanged",
    "existing RuntimeTableView array identity/shape remains unchanged",
    "does not introduce a new RuntimeConfigView",
    "runtime_config_view_replacement_allowed: false",
    "generated_source_owned_baseline_active_publication_allowed: false",
    "runtime_loaded_config_implemented: false",
    "persistent_storage_implemented: false",
    "webserial_device_write_implemented: false",
    "backend_config_pb_write_path_implemented: false",
    "flashing_automation_implemented: false",
    "nunchuk_status: NOT_TESTED",
    "root_cause_proven: false",
)


class SourceOwnedTableReplacementDesignError(AssertionError):
    """Raised when the source-owned table replacement design drifts."""


def fail(message: str) -> None:
    raise SourceOwnedTableReplacementDesignError(message)


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
    if branch not in {EXPECTED_BRANCH, GENERATOR_CONTRACT_BRANCH, TABLE_CONTENT_DIAGNOSTIC_BRANCH, MERGED_BRANCH}:
        fail(
            f"checker must run on {EXPECTED_BRANCH}, {GENERATOR_CONTRACT_BRANCH}, "
            f"{TABLE_CONTENT_DIAGNOSTIC_BRANCH}, "
            f"or {MERGED_BRANCH}, got {branch}"
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
    if branch in {EXPECTED_BRANCH, GENERATOR_CONTRACT_BRANCH}:
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if FORBIDDEN_SOURCE_PATH_RE.search(path):
            fail(f"firmware/source path changed on docs/checker-only branch: {path}")
        if FORBIDDEN_SPECIAL_PATH_RE.search(path):
            fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if path in ALLOWED_EXISTING_CHECKERS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("`", "").split())


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized_text = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized_text]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("packet") != "source_owned_table_replacement_design":
        fail("fixture packet must be source_owned_table_replacement_design")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"fixture branch must be {EXPECTED_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"fixture {key} must be {expected!r}, got {actual!r}")
    evidence = fixture.get("evidence")
    if not isinstance(evidence, dict):
        fail("fixture evidence must be an object")
    for key, expected in EXPECTED_EVIDENCE.items():
        actual = evidence.get(key)
        if actual != expected:
            fail(f"fixture evidence.{key} must be {expected!r}, got {actual!r}")


def validate_docs() -> None:
    design = read_required(DESIGN_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)

    require_phrases(rel(DESIGN_DOC), design, REQUIRED_DOC_PHRASES + REQUIRED_DESIGN_PHRASES)
    for path, text in (
        (README, readme),
        (CURRENT_STATE, current_state),
        (ROADMAP, roadmap),
    ):
        require_phrases(rel(path), text, REQUIRED_DOC_PHRASES)


def main() -> int:
    branch = validate_branch()
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)
    if branch != TABLE_CONTENT_DIAGNOSTIC_BRANCH:
        validate_changed_paths(changed_paths(branch))
    validate_docs()
    print("glyph_source_owned_table_replacement_design: PASS")
    print(f"- branch: {branch}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- design: {rel(DESIGN_DOC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
