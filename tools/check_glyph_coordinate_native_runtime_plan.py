#!/usr/bin/env python3
"""Validate the Glyph coordinate-native runtime plan packet."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "docs-glyph-coordinate-native-runtime-plan"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
DOCS_SURFACE_BRANCH = "docs-agent-surface-cleanup"
AGENT_FRAMEWORK_BRANCH = "docs-agent-framework-contracts"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCH_PREFIXES = ("codex/runtime-config-coordinate-native-", "docs-runtime-config-")

PLAN_DOC = REPO_ROOT / "docs/runtime_config/glyph_coordinate_native_runtime_plan.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/glyph_coordinate_native_runtime_plan.json"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_coordinate_native_runtime_plan.py"

ALLOWED_EXACT_CHANGED_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "docs/AGENT_CONTEXT.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/runtime_config/runtime_config_activation_alternatives_a_f.md",
    "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp",
    "tools/generate_source_owned_runtime_config.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_source_owned_table_symbol_map.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/dry_run_coordinate_native_runtime_profile.py",
    "tools/convert_coordinate_native_profile_to_source_owned_spec.py",
    CHECKER_REL,
    "tools/check_glyph_agent_framework_docs.py",
    "tools/check_glyph_docs_agent_surface.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_runtime_config_activation_alternatives.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "tools/extract_glyph_identity_runtime_tables.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/agent_framework/")
ALLOWED_EXISTING_CHECKERS: set[str] = set()

FORBIDDEN_SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)")
FORBIDDEN_SPECIAL_PATH_RE = re.compile(
    r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "docs_checker_only": True,
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "current_known_good_backend": "source_owned_firmware_realization",
    "future_target_backend": "coordinate_native_runtime_profile",
    "existing_scalar_custom_mode_is_canonical_model": False,
    "runtime_transport_persistence_considered_solvable_future_infrastructure": True,
    "canonical_profile_is_neutral_app_owned": True,
    "firmware_owns_game_semantics": False,
    "senscope_owns_game_semantics": True,
    "requires_direction_key_1_to_9": True,
    "requires_neutral_5": True,
    "requires_exact_raw_coordinates": True,
    "requires_explicit_routing_sublayers_priorities": True,
    "active_runtime_config_replacement_allowed": False,
    "runtime_config_view_replacement_allowed": False,
    "generated_active_wrapper_allowed": False,
    "candidate_view_active_allowed": False,
    "ram_backed_active_publication_allowed": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

EXPECTED_EVIDENCE: dict[str, Any] = {
    "source_owned_y2_layout": "HARDWARE_PASS",
    "rf5_forced_a_up_disconnect": False,
    "lt6_forced_a_down_disconnect": False,
    "y1_simple": True,
    "y2_owns_migrated_rf_sublayers": True,
    "active_runtime_config_view_selection_unchanged": True,
    "source_owned_current_baseline_published": True,
    "candidate_view_active_publication": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active_publication": "HARDWARE_FAIL",
    "dedicated_ram_backed_active_storage_publication": "HARDWARE_FAIL",
    "generated_source_owned_baseline_runtime_config_view_active_publication": "HARDWARE_FAIL",
}

REQUIRED_PHRASES = (
    "source-owned Y2 layout HARDWARE_PASS",
    "prior active-publication HARDWARE_FAIL evidence",
    "coordinate-native runtime profile",
    "source-owned firmware generation as v0",
    "browser/protobuf/persistence as future infrastructure",
    "neutral app-owned profile remains canonical",
)

REQUIRED_PLAN_PHRASES = (
    "Browser-to-device transport, protobuf-style config exchange, and persistence are likely solvable primitives",
    "future backend infrastructure, not as the canonical Senscope profile model",
    "Senscope's canonical profile model remains neutral, app-owned, and firmware-independent",
    "Glyph firmware should not know Super Smash Bros. Ultimate game semantics",
    "Senscope, its datasets, and its solver own game semantics",
    "Glyph firmware should become a deterministic coordinate-output backend",
    "active role/modifier state + resolved direction key 1..9 -> exact raw coordinate",
    "Neutral direction 5 must be supported",
    "Full 9-way asymmetry must be supported",
    "Sublayers, routing, and priority must be represented explicitly",
    "Y1/Y2/Tilt/Layer-style behavior requires profile-level routing primitives",
    "not only scalar axis multipliers",
    "Current v0 production work remains source-owned firmware generation as v0 until coordinate-native runtime profile support is hardware-proven",
)

FORBIDDEN_ATTRIBUTION_TERMS = (
    "SenatorSSB",
    "glyph-remapper",
    "HayBox Remapper",
)


class GlyphCoordinateNativeRuntimePlanError(AssertionError):
    """Raised when the coordinate-native runtime plan drifts."""


def fail(message: str) -> None:
    raise GlyphCoordinateNativeRuntimePlanError(message)


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
        DOCS_SURFACE_BRANCH,
        AGENT_FRAMEWORK_BRANCH,
        MERGED_BRANCH,
        RECOVERY_BRANCH,
        "runtime-config-alt-b-generated-table-alias-candidate",
    } and not any(branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES):
        fail(f"checker must run on {EXPECTED_BRANCH}, {DOCS_SURFACE_BRANCH}, {AGENT_FRAMEWORK_BRANCH}, or {MERGED_BRANCH}, got {branch}")
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
    if branch in {EXPECTED_BRANCH, DOCS_SURFACE_BRANCH, AGENT_FRAMEWORK_BRANCH, RECOVERY_BRANCH} or any(
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
        if FORBIDDEN_SOURCE_PATH_RE.search(path):
            fail(f"firmware/source path changed on docs/checker-only branch: {path}")
        if FORBIDDEN_SPECIAL_PATH_RE.search(path):
            fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
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


def reject_forbidden_attribution(label: str, text: str) -> None:
    for term in FORBIDDEN_ATTRIBUTION_TERMS:
        if term.lower() in text.lower():
            fail(f"{label} contains forbidden attribution or external repo name: {term}")


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("packet") != "glyph_coordinate_native_runtime_plan":
        fail("fixture packet must be glyph_coordinate_native_runtime_plan")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"fixture branch must be {EXPECTED_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"fixture {key} must be {expected!r}, got {actual!r}")
    evidence = fixture.get("accepted_evidence")
    if not isinstance(evidence, dict):
        fail("fixture accepted_evidence must be an object")
    for key, expected in EXPECTED_EVIDENCE.items():
        actual = evidence.get(key)
        if actual != expected:
            fail(f"fixture accepted_evidence.{key} must be {expected!r}, got {actual!r}")


def validate_docs() -> None:
    docs = (
        (PLAN_DOC, read_required(PLAN_DOC)),
        (README, read_required(README)),
        (CURRENT_STATE, read_required(CURRENT_STATE)),
        (ROADMAP, read_required(ROADMAP)),
    )
    for path, text in docs:
        reject_forbidden_attribution(rel(path), text)
        require_phrases(rel(path), text, REQUIRED_PHRASES)
    require_phrases(rel(PLAN_DOC), docs[0][1], REQUIRED_PLAN_PHRASES)


def main() -> int:
    branch = validate_branch()
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)
    if branch != DOCS_SURFACE_BRANCH:
        validate_changed_paths(changed_paths(branch))
    validate_docs()
    print("glyph_coordinate_native_runtime_plan: PASS")
    print(f"- branch: {branch}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- plan: {rel(PLAN_DOC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
