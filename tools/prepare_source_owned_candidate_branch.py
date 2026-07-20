#!/usr/bin/env python3
"""Prepare an offline source-owned candidate-branch plan.

This wrapper stays offline by default. It validates a coordinate-native
profile or inert layout-spec fixture, converts when needed, generates the
source-owned artifact in a temporary location, and emits a machine-readable
plan for the hardware-test candidate branch.

An explicit ``--write-source`` mode may materialize the generated artifact into
the approved inert Alternative B source path, but it refuses dirty worktrees
and refuses direct writes on ``configurator``. The tool never touches device
write, persistent storage, flashing automation, or active publication code.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from check_glyph_coordinate_native_runtime_profile_contract import (
    CoordinateNativeRuntimeProfileContractError,
    load_json_object as load_profile_json,
    validate_profile_fixture,
)
from generate_source_owned_runtime_config import (
    GeneratorContractError,
    assert_inert_source_install_path,
    generate_from_layout_spec,
    load_json_object,
)
from glyph_source_owned_overlay import OverlayContractError, generate_overlay_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_BRANCH = "runtime-config-install-workflow-candidate-generation"
DEFAULT_TARGET_SOURCE_PATH = (
    REPO_ROOT / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
)
VALIDATION_COMMANDS = [
    "python3 tools/check_glyph_source_owned_generator_modes.py",
    "python3 tools/check_glyph_source_owned_source_authority_intake.py",
    "python3 tools/check_glyph_source_owned_table_symbol_map.py",
    "python3 tools/check_glyph_docs_navigation.py",
    "python3 tools/check_glyph_docs_agent_surface.py",
    "python3 tools/check_glyph_generated_source_owned_generator_contract.py",
    "python3 tools/check_glyph_generated_source_owned_artifact_install.py",
    "python3 tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py --check-layout-spec-bridge",
]
BUILD_COMMAND = "pio run -e glyph_mk6"
HARDWARE_GATE_STATUS = "NOT_REQUIRED_FOR_DRY_RUN"
GENERATION_POLICY = {
    "allowed_modes": [
        "full_replacement",
        "overlay_preserve",
        "reject",
    ],
    "current_mode": "reject",
    "full_replacement_requirement": "every active table must be explicitly specified and validated",
    "overlay_preserve_requirement": "only explicitly owned tables may change; unspecified tables must be copied from the current source-owned baseline",
    "reject_requirement": "partial input without an explicit overlay/preserve policy must fail",
    "unspecified_table_policy": "reject_without_explicit_overlay_preserve",
    "silent_canonical_default_fill_allowed": False,
    "example_profile_production_candidate_allowed_without_explicit_approval": False,
    "table_by_table_change_manifest_required": True,
    "preserved_tables_must_match_current_source_semantically": True,
}


class SourceOwnedCandidateBranchPreparationError(RuntimeError):
    """Raised when the candidate-branch preparation workflow rejects input."""


def fail(message: str) -> None:
    raise SourceOwnedCandidateBranchPreparationError(message)


def rel(path: Path) -> str:
    return str(path.resolve())


def resolve_input_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required input: {path}")
    return path.read_text(encoding="utf-8")


def git_current_branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git branch --show-current failed: " + completed.stderr.strip())
    branch = completed.stdout.strip()
    if not branch:
        fail("could not determine current git branch")
    return branch


def git_status_short() -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git status --short failed: " + completed.stderr.strip())
    return [line for line in completed.stdout.splitlines() if line.strip()]


def ensure_clean_worktree() -> None:
    if git_status_short():
        fail("candidate source write refused: working tree must be clean")


def ensure_not_configurator(target_branch: str) -> None:
    if target_branch == "configurator":
        fail("candidate source write refused: direct writes on configurator are not allowed")


def ensure_allowed_target_path(target_path: Path) -> None:
    assert_inert_source_install_path(target_path)


def parse_layout_spec_from_profile(profile_path: Path) -> tuple[Path, dict[str, Any]]:
    profile_path = resolve_input_path(profile_path)
    try:
        fixture = load_profile_json(profile_path)
        validate_profile_fixture(
            fixture,
            label=str(profile_path),
            require_selection_semantics=True,
        )
    except CoordinateNativeRuntimeProfileContractError as exc:
        fail(str(exc))

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/convert_coordinate_native_profile_to_source_owned_spec.py"),
            "--profile",
            str(profile_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("profile-to-layout-spec conversion failed: " + (completed.stderr.strip() or completed.stdout.strip()))
    try:
        layout_spec = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(f"converter output was not valid JSON: {exc}")
    if not isinstance(layout_spec, dict):
        fail("converter output must be a JSON object")

    temp_dir = Path(tempfile.mkdtemp(prefix="glyph_source_owned_candidate_layout_spec_"))
    layout_spec_path = temp_dir / "candidate.layout_spec.json"
    layout_spec_path.write_text(json.dumps(layout_spec, indent=2) + "\n", encoding="utf-8")
    return layout_spec_path, layout_spec


def parse_layout_spec(layout_spec_path: Path) -> tuple[Path, dict[str, Any]]:
    layout_spec_path = resolve_input_path(layout_spec_path)
    layout_spec = load_json_object(layout_spec_path)
    temp_dir = Path(tempfile.mkdtemp(prefix="glyph_source_owned_candidate_layout_spec_"))
    mirrored_path = temp_dir / "candidate.layout_spec.json"
    mirrored_path.write_text(json.dumps(layout_spec, indent=2) + "\n", encoding="utf-8")
    return mirrored_path, layout_spec


def generate_source_artifact(layout_spec_path: Path) -> tuple[Path, str]:
    try:
        generated_text = generate_from_layout_spec(layout_spec_path)
    except GeneratorContractError as exc:
        fail(str(exc))
    temp_dir = layout_spec_path.parent
    source_artifact_path = temp_dir / "candidate.GeneratedRuntimeConfigBaseline.current.hpp"
    source_artifact_path.write_text(generated_text, encoding="utf-8")
    return source_artifact_path, generated_text


def build_plan(
    *,
    input_kind: str,
    input_path: Path,
    layout_spec_path: Path,
    source_artifact_path: Path,
    target_source_path: Path,
    target_branch: str,
    write_source: bool,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "packet": "source_owned_candidate_generation_plan",
        "status": "dry_run_plan" if not write_source else "materialization_plan",
        "candidate_branch_name": target_branch,
        "input_kind": input_kind,
        "input_path": rel(input_path),
        "converted_or_validated_layout_spec_path": rel(layout_spec_path),
        "generated_source_artifact_path": rel(source_artifact_path),
        "target_source_install_path": rel(target_source_path),
        "validation_commands": VALIDATION_COMMANDS,
        "build_command": BUILD_COMMAND,
        "hardware_gate_status": HARDWARE_GATE_STATUS,
        "source_write_mode": write_source,
        "candidate_generation_policy": GENERATION_POLICY,
        "candidate_generation_without_table_change_manifest": "reject",
        "explicit_profile_table_ownership_required": True,
        "current_source_preserve_policy_required_for_unspecified_tables": True,
        "source_write_safeguards": [
            "clean working tree required",
            "direct writes on configurator refused",
            "approved inert Alternative B source path only",
            "table-by-table change manifest required before hardware",
            "example profile metadata cannot create production candidates without explicit approval",
            "partial input without overlay/preserve policy rejected",
            "no device write",
            "no persistent storage",
            "no flashing automation",
            "no active publication changes",
        ],
        "forbidden_claims": [
            "runtime_loaded_config_implemented",
            "webserial_device_write_implemented",
            "persistent_storage_implemented",
            "backend_config_pb_write_path_implemented",
            "flashing_automation_implemented",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--profile", type=Path, help="coordinate-native runtime profile JSON fixture")
    input_group.add_argument("--layout-spec", type=Path, help="inert generated source-owned layout-spec fixture")
    parser.add_argument(
        "--candidate-branch",
        default=DEFAULT_CANDIDATE_BRANCH,
        help="candidate branch name to record in the dry-run plan",
    )
    parser.add_argument(
        "--target-source-path",
        type=Path,
        default=DEFAULT_TARGET_SOURCE_PATH,
        help="approved inert Alternative B source path to materialize",
    )
    parser.add_argument(
        "--write-source",
        action="store_true",
        help="materialize the generated artifact into the approved inert source path",
    )
    args = parser.parse_args(argv)

    try:
        ensure_allowed_target_path(args.target_source_path)
        current_branch = git_current_branch()
        if args.write_source:
            ensure_not_configurator(args.candidate_branch)
            ensure_not_configurator(current_branch)
            ensure_clean_worktree()

        if args.profile is not None:
            layout_spec_path, _ = parse_layout_spec_from_profile(args.profile)
            input_kind = "profile"
            input_path = resolve_input_path(args.profile)
        else:
            layout_spec_path, _ = parse_layout_spec(args.layout_spec)
            input_kind = "layout-spec"
            input_path = resolve_input_path(args.layout_spec)

        if args.write_source:
            try:
                payload = load_json_object(input_path)
                generate_overlay_payload(payload, production=True)
            except (GeneratorContractError, OverlayContractError, OSError) as exc:
                fail("production source preparation requires explicit safe generation semantics: " + str(exc))

        source_artifact_path, generated_text = generate_source_artifact(layout_spec_path)
        plan = build_plan(
            input_kind=input_kind,
            input_path=input_path,
            layout_spec_path=layout_spec_path,
            source_artifact_path=source_artifact_path,
            target_source_path=args.target_source_path,
            target_branch=args.candidate_branch,
            write_source=args.write_source,
        )

        if args.write_source:
            args.target_source_path.parent.mkdir(parents=True, exist_ok=True)
            args.target_source_path.write_text(generated_text, encoding="utf-8")
            plan["materialized_source_write"] = rel(args.target_source_path)

        json.dump(plan, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    except (SourceOwnedCandidateBranchPreparationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
