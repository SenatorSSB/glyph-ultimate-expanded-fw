#!/usr/bin/env python3
"""Validate the agent-facing Glyph documentation surface cleanup."""

from __future__ import annotations

import re
import subprocess
import json
from pathlib import Path

from glyph_hardware_correspondence import CorrespondenceError, verify_correspondence

from glyph_checker_context import (
    DEFAULT_PROTECTED_PREFIXES,
    CheckerContextError,
    CheckerContext,
    collect_checker_context,
    validate_feature_scope,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "docs-agent-surface-cleanup"
CONTRACT_BRANCH = "runtime-config-coordinate-native-profile-contract"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
AGENT_FRAMEWORK_BRANCH = "docs-agent-framework-contracts"
INTAKE_BRANCH = "runtime-config-source-authority-intake-workflow"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCH_PREFIXES = ("codex/runtime-config-coordinate-native-", "docs-runtime-config-")

AGENT_CONTEXT = REPO_ROOT / "docs/AGENT_CONTEXT.md"
BOUNDARY = REPO_ROOT / "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
RUNTIME_README = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs/calibration/INDEX.md"
ARCHIVE_INDEX = REPO_ROOT / "docs/archive/README.md"
QUEUE_PATH = "docs/project/ACTIVE_AGENT_QUEUE.md"
GP005_CANDIDATE = "437f87e8086a50f0dfbd834176b80d245c1ed307"
GP005_TREE = "4b9e2f1eb56add78ff880321730eb15ed22ce72f"
GP005_BRANCH = "glyph/gp-config-005-transactional-setconfig"
GP005_BASE = "9550a1bf1309383e351f4f9e66663562fc9f13ac"
GP005_ARTIFACT = "650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44"
GP005_HAL_PATH = "HAL/pico/src/comms/ConfiguratorBackend.cpp"
GP_CONFIG_010_BRANCH = "glyph/gp-config-010-mode-activation-capacity"
GP_CONFIG_010_SOURCE_PATH = "src/core/mode_selection.cpp"

CHECKER_REL = "tools/check_glyph_docs_agent_surface.py"
ALLOWED_EXACT_CHANGED_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp",
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "tools/extract_glyph_identity_runtime_tables.py",
    CHECKER_REL,
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_source_owned_table_symbol_map.py",
    "tools/check_glyph_diagnostic_active_storage_published.py",
    "tools/generate_source_owned_runtime_config.py",
    "tools/convert_coordinate_native_profile_to_source_owned_spec.py",
    "tools/install_generated_source_owned_runtime_config.py",
    "tools/check_glyph_source_owned_candidate_generation.py",
    "tools/prepare_source_owned_candidate_branch.py",
    "tools/check_glyph_agent_framework_docs.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_runtime_config_activation_alternatives.py",
    "tools/dry_run_coordinate_native_runtime_profile.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
    "tools/check_glyph_source_owned_candidate_generation_diff.py",
    "tools/source_owned_source_authority_intake.py",
    "tools/manage_source_owned_source_authority_intake.py",
    "tools/check_glyph_source_owned_source_authority_intake.py",
    "tools/check_glyph_source_owned_table_replacement_generator_contract.py",
    "tools/generate_source_owned_table_replacement.py",
    "docs/runtime_config/fixtures/source_owned_candidate_generation_workflow.json",
    "builder_scripts/arduino_pico.py",
    "tools/glyph_tracked_worktree_integrity.py",
    "tools/glyph_hardware_artifact_custody.py",
    "tools/check_glyph_prebuild_git_identity.py",
    "tools/check_glyph_hardware_artifact_custody.py",
    "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
    "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
    "docs/runtime_config/fixtures/glyph_checker_census.json",
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

FORBIDDEN_ACTIVE_CLAIMS = (
    "generated artifact is active",
    "generated runtimeconfigview wrapper is safe",
    "generated runtimeconfigview wrapper safe",
    "generated source-owned tables are active",
)


class AgentSurfaceError(AssertionError):
    """Raised when the agent-facing docs surface drifts."""


def fail(message: str) -> None:
    raise AgentSurfaceError(message)


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode:
        fail(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def is_ancestor(root: Path, earlier: str, later: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", earlier, later],
        cwd=root, capture_output=True, check=False,
    ).returncode == 0


def exact_gp005_integration(context: CheckerContext) -> bool:
    """Authorize only the immutable, canonically validated HAL merge delta."""

    root = context.repo_root
    if GP005_HAL_PATH not in context.committed_paths:
        return False
    if any(
        path != GP005_HAL_PATH
        and not (path.startswith("docs/") or path.startswith("tools/") or path in {"README.md", "AGENTS.md", "CLAUDE.md"})
        for path in context.changed_paths
    ):
        return False
    if GP005_HAL_PATH in (context.staged_paths | context.unstaged_paths):
        return False
    if not context.base_commit or context.base_commit != git_output(root, "rev-parse", "origin/configurator"):
        return False
    if is_ancestor(root, GP005_CANDIDATE, context.base_commit):
        return False
    if not is_ancestor(root, GP005_CANDIDATE, context.head):
        return False
    if git_output(root, "rev-list", "--parents", "-n", "1", GP005_CANDIDATE).split() != [GP005_CANDIDATE, GP005_BASE]:
        return False
    merges = git_output(root, "rev-list", "--merges", "--parents", f"{context.base_commit}..{context.head}")
    if not any(
        len(parts := line.split()) >= 3
        and parts[2:] == [GP005_CANDIDATE]
        and is_ancestor(root, context.base_commit, parts[1])
        for line in merges.splitlines()
    ):
        return False

    queue_text = git_output(root, "show", f"{context.base_commit}:{QUEUE_PATH}")
    match = re.search(r"<!-- queue-state:start -->\s*```json\s*(.*?)\s*```", queue_text, re.S)
    if not match:
        return False
    try:
        items = json.loads(match.group(1))["items"]
        item, = [entry for entry in items if entry.get("id") == "GP-CONFIG-005"]
    except (ValueError, KeyError, TypeError):
        return False
    evidence_ref = item.get("hardware_evidence_record", "")
    if not isinstance(evidence_ref, str) or not evidence_ref.startswith("git-json:"):
        return False
    try:
        _, evidence_commit, evidence_path = evidence_ref.split(":", 2)
        if not re.fullmatch(r"[0-9a-f]{40}", evidence_commit) or not is_ancestor(root, evidence_commit, context.base_commit):
            return False
        evidence = json.loads(git_output(root, "show", f"{evidence_commit}:{evidence_path}"))
    except (ValueError, KeyError, TypeError, AgentSurfaceError):
        return False
    identity = {
        "candidate_git_sha": GP005_CANDIDATE,
        "candidate_base_configurator_sha": GP005_BASE,
        "firmware_artifact_sha256": GP005_ARTIFACT,
    }
    if any(item.get(key) != value or evidence.get(key) != value for key, value in identity.items()):
        return False
    if (item.get("status") != "HARDWARE_VALIDATED" or item.get("hardware_result") != "PASS"
            or item.get("hardware_evidence_gaps") != [] or evidence.get("work_order_id") != "GP-CONFIG-005"
            or evidence.get("result") != "PASS" or evidence.get("evidence_gaps") != []):
        return False

    if git_output(root, "rev-parse", f"{GP005_CANDIDATE}^{{tree}}") != GP005_TREE:
        return False
    refs = git_output(root, "for-each-ref", "--format=%(objectname)",
                      f"refs/heads/{GP005_BRANCH}", f"refs/remotes/origin/{GP005_BRANCH}").splitlines()
    if not refs or any(ref != GP005_CANDIDATE for ref in refs):
        return False
    try:
        verify_correspondence(root, GP005_CANDIDATE, GP005_BASE, context.head, integrated=True)
    except CorrespondenceError:
        return False

    return True


def exact_gp_config_010_source_candidate(context: CheckerContext) -> bool:
    """Authorize only the bounded pre-hardware GP-CONFIG-010 source seam."""

    if context.branch != GP_CONFIG_010_BRANCH or GP_CONFIG_010_SOURCE_PATH not in context.changed_paths:
        return False
    if any(
        path != GP_CONFIG_010_SOURCE_PATH
        and not (path.startswith("docs/") or path.startswith("tools/") or path in {"README.md", "AGENTS.md", "CLAUDE.md"})
        for path in context.changed_paths
    ):
        return False
    source = (context.repo_root / GP_CONFIG_010_SOURCE_PATH).read_text(encoding="utf-8")
    return all(
        anchor in source
        for anchor in (
            "kModeActivationMaskCapacity = 30",
            "std::extent_v<decltype(Config::game_mode_configs)>",
            "if (mode_configs_count > kModeActivationMaskCapacity)",
            "if (config.game_mode_configs_count > kModeActivationMaskCapacity)",
        )
    )


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
        "runtime-config-install-workflow-candidate-generation",
        AGENT_FRAMEWORK_BRANCH,
        MERGED_BRANCH,
        RECOVERY_BRANCH,
        "runtime-config-source-owned-install-workflow",
        "runtime-config-alt-b-generated-table-alias-candidate",
        INTAKE_BRANCH,
        "runtime-config-literal-table-contract-supersession",
    } and not any(branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES):
        fail(f"checker must run on {EXPECTED_BRANCH}, {AGENT_FRAMEWORK_BRANCH}, or {MERGED_BRANCH}, got {branch}")
    if branch in {EXPECTED_BRANCH, CONTRACT_BRANCH, AGENT_FRAMEWORK_BRANCH} or any(
        branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES
    ):
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
    if branch in {
        EXPECTED_BRANCH,
        CONTRACT_BRANCH,
        "runtime-config-install-workflow-candidate-generation",
        AGENT_FRAMEWORK_BRANCH,
        RECOVERY_BRANCH,
        "runtime-config-source-owned-install-workflow",
        INTAKE_BRANCH,
        "runtime-config-literal-table-contract-supersession",
    } or any(
        branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES
    ):
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
        reject_phrases(rel(path), docs[path], FORBIDDEN_ACTIVE_CLAIMS)

    validate_agent_context(docs[AGENT_CONTEXT])
    validate_boundary(docs[BOUNDARY])
    validate_current_state(docs[CURRENT_STATE])
    validate_roadmap(docs[ROADMAP])
    validate_runtime_readme(docs[RUNTIME_README])
    validate_calibration_index(docs[CALIBRATION_INDEX])
    validate_archive_index(docs[ARCHIVE_INDEX])


def validate_surface_scope(context: CheckerContext) -> None:
    authorized_hal = exact_gp005_integration(context) if GP005_HAL_PATH in context.changed_paths else False
    authorized_gp_config_010 = exact_gp_config_010_source_candidate(context)
    validate_feature_scope(
        context,
        allowed_paths=("docs/", "tools/", "builder_scripts/", ".github/workflows/build.yml", "README.md", "AGENTS.md", "CLAUDE.md", "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp", *((GP005_HAL_PATH,) if authorized_hal else ()), *((GP_CONFIG_010_SOURCE_PATH,) if authorized_gp_config_010 else ())),
        protected_prefixes=tuple(prefix for prefix in DEFAULT_PROTECTED_PREFIXES if prefix != "src/" and (not authorized_hal or prefix.casefold() != "hal/")),
    )


def main() -> int:
    try:
        context = collect_checker_context(repo_root=REPO_ROOT)
        validate_surface_scope(context)
    except CheckerContextError as exc:
        fail(str(exc))
    branch = context.branch or "detached HEAD"
    validate_docs()
    print("glyph_docs_agent_surface: PASS")
    print(f"- branch: {branch}")
    print(f"- agent context: {rel(AGENT_CONTEXT)}")
    print(f"- implementation boundary: {rel(BOUNDARY)}")
    print(f"- archive index: {rel(ARCHIVE_INDEX)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
