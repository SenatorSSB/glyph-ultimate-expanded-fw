#!/usr/bin/env python3
"""Validate the agent-facing Glyph documentation surface cleanup."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "docs-agent-surface-cleanup"
CONTRACT_BRANCH = "runtime-config-coordinate-native-profile-contract"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
AGENT_FRAMEWORK_BRANCH = "docs-agent-framework-contracts"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

AGENT_CONTEXT = REPO_ROOT / "docs/AGENT_CONTEXT.md"
BOUNDARY = REPO_ROOT / "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
RUNTIME_README = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs/calibration/INDEX.md"
ARCHIVE_INDEX = REPO_ROOT / "docs/archive/README.md"

CHECKER_REL = "tools/check_glyph_docs_agent_surface.py"
ALLOWED_EXACT_CHANGED_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp",
    CHECKER_REL,
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/generate_source_owned_runtime_config.py",
    "tools/check_glyph_agent_framework_docs.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
}
ALLOWED_PREFIXES = ("docs/",)

FORBIDDEN_CHANGED_PATH_RE = re.compile(
    r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)|(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
FORBIDDEN_ATTRIBUTION_TERMS = (
    "SenatorSSB",
    "glyph-remapper",
    "HayBox Remapper",
    "github.com/",
)


class AgentSurfaceError(AssertionError):
    """Raised when the agent-facing docs surface drifts."""


def fail(message: str) -> None:
    raise AgentSurfaceError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).lower()


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def reject_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized = normalize(text)
    present = [phrase for phrase in phrases if normalize(phrase) in normalized]
    if present:
        fail(f"{label} foregrounds obsolete current-work phrases: " + ", ".join(present))


def reject_forbidden_attribution(label: str, text: str) -> None:
    lower = text.lower()
    for term in FORBIDDEN_ATTRIBUTION_TERMS:
        if term.lower() in lower:
            fail(f"{label} contains forbidden community or external repo name: {term}")


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
        CONTRACT_BRANCH,
        "generator-source-owned-layout-spec-contract",
        AGENT_FRAMEWORK_BRANCH,
        MERGED_BRANCH,
        RECOVERY_BRANCH,
    }:
        fail(f"checker must run on {EXPECTED_BRANCH}, {AGENT_FRAMEWORK_BRANCH}, or {MERGED_BRANCH}, got {branch}")
    if branch in {EXPECTED_BRANCH, CONTRACT_BRANCH, AGENT_FRAMEWORK_BRANCH}:
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            fail(f"{BASE_BRANCH} must be an ancestor of HEAD")
    return branch


def status_path(status_line: str) -> str:
    path = status_line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def changed_paths(branch: str) -> set[str]:
    paths: set[str] = set()
    if branch in {EXPECTED_BRANCH, CONTRACT_BRANCH, AGENT_FRAMEWORK_BRANCH, RECOVERY_BRANCH}:
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if FORBIDDEN_CHANGED_PATH_RE.search(path):
            fail(f"forbidden firmware/source/backend/storage/write/WebSerial/flashing path changed: {path}")
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


def validate_agent_context(text: str) -> None:
    require_phrases(
        rel(AGENT_CONTEXT),
        text,
        (
            "current known-good branch state",
            "latest Y2 layout source-owned port",
            "latest Y2 layout HARDWARE_PASS",
            "source-owned table/routing source",
            "Active RuntimeConfigView selection is unchanged",
            "candidate.view is not active",
            "RAM-backed active table publication is not used",
            "Forbidden",
            "coordinate-native runtime profile",
            "Nunchuk remains NOT_TESTED",
            "root cause remains unproven",
        ),
    )


def validate_boundary(text: str) -> None:
    require_phrases(
        rel(BOUNDARY),
        text,
        (
            "candidate.view active publication is forbidden",
            "active_storage.view active publication is forbidden",
            "Generated active RuntimeConfigView wrapper publication is forbidden",
            "RuntimeConfigView replacement as the customization mechanism is forbidden",
            "Runtime-loaded profile claims are forbidden without separate design",
            "coordinate-native runtime profile contract scaffold",
            "design-only and inactive",
            "browser/protobuf/persistence work may be future infrastructure",
            "hardware proof",
        ),
    )


def validate_current_state(text: str) -> None:
    require_phrases(
        rel(CURRENT_STATE),
        text,
        (
            "docs/AGENT_CONTEXT.md",
            "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
            "source-owned Y2 layout HARDWARE_PASS",
            "Active RuntimeConfigView selection remains unchanged",
            "Forbidden current active-publication paths",
            "coordinate-native runtime profile contract scaffolding",
            "coordinate_native_runtime_profile_contract.json",
            "Nunchuk remains NOT_TESTED",
            "root cause remains unproven",
        ),
    )
    if len(text.splitlines()) > 120:
        fail(f"{rel(CURRENT_STATE)} should remain concise")


def validate_roadmap(text: str) -> None:
    require_phrases(
        rel(ROADMAP),
        text,
        (
            "source-owned realization generator",
            "coordinate-native runtime profile contract scaffolding",
            "future browser/protobuf/persistence backend",
            "after the runtime model exists",
        ),
    )


def validate_runtime_readme(text: str) -> None:
    require_phrases(
        rel(RUNTIME_README),
        text,
        (
            "Current Known-Good State",
            "Safe Source-Owned Realization Path",
            "Forbidden Active Publication Paths",
            "Coordinate-Native Runtime Profile Contract",
            "Archived Diagnostics",
            "coordinate_native_runtime_profile_contract.md",
            "coordinate_native_runtime_profile_contract.json",
            "python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py",
        ),
    )
    before_archive = text.split("## Archived Diagnostics", 1)[0]
    reject_phrases(
        rel(RUNTIME_README),
        before_archive,
        (
            "diagnostic_active_storage_published_hardware_failure",
            "diagnostic_generated_source_owned_baseline_active_hardware_failure",
            "glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure",
        ),
    )


def validate_calibration_index(text: str) -> None:
    require_phrases(
        rel(CALIBRATION_INDEX),
        text,
        (
            "Current Merge-Gating Hardware PASS",
            "Archived Failed Diagnostics",
            "Untested Nunchuk Scope",
            "latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md",
            "Nunchuk remains NOT_TESTED",
        ),
    )


def validate_archive_index(text: str) -> None:
    require_phrases(
        rel(ARCHIVE_INDEX),
        text,
        (
            "historical diagnostics",
            "diagnostic_active_storage_published_hardware_failure_2026-06-28.md",
            "diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md",
            "glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.md",
            "latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md",
        ),
    )


def validate_docs() -> None:
    docs = {
        AGENT_CONTEXT: read_required(AGENT_CONTEXT),
        BOUNDARY: read_required(BOUNDARY),
        CURRENT_STATE: read_required(CURRENT_STATE),
        ROADMAP: read_required(ROADMAP),
        RUNTIME_README: read_required(RUNTIME_README),
        CALIBRATION_INDEX: read_required(CALIBRATION_INDEX),
        ARCHIVE_INDEX: read_required(ARCHIVE_INDEX),
    }
    for path in (AGENT_CONTEXT, BOUNDARY, CURRENT_STATE, ROADMAP, RUNTIME_README, ARCHIVE_INDEX):
        reject_forbidden_attribution(rel(path), docs[path])

    validate_agent_context(docs[AGENT_CONTEXT])
    validate_boundary(docs[BOUNDARY])
    validate_current_state(docs[CURRENT_STATE])
    validate_roadmap(docs[ROADMAP])
    validate_runtime_readme(docs[RUNTIME_README])
    validate_calibration_index(docs[CALIBRATION_INDEX])
    validate_archive_index(docs[ARCHIVE_INDEX])


def main() -> int:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch))
    validate_docs()
    print("glyph_docs_agent_surface: PASS")
    print(f"- branch: {branch}")
    print(f"- agent context: {rel(AGENT_CONTEXT)}")
    print(f"- implementation boundary: {rel(BOUNDARY)}")
    print(f"- archive index: {rel(ARCHIVE_INDEX)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
