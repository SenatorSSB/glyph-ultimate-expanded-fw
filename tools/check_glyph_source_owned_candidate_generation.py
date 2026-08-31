#!/usr/bin/env python3
"""Validate the offline source-owned candidate-generation workflow."""

from __future__ import annotations

import json
import io
import hashlib
import os
import subprocess
import sys
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/prepare_source_owned_candidate_branch.py"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_candidate_generation_workflow.json"
PROFILE_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json"
LAYOUT_SPEC_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
INVALID_PROFILE_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_runtime_loaded_claim.json"

ALLOWED_TARGET_PATH = "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp"
ACTIVE_TARGET_PATH = "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
FORBIDDEN_CLAIMS = (
    "runtime_loaded_config_implemented",
    "persistent_storage_implemented",
    "webserial_device_write_implemented",
    "backend_config_pb_write_path_implemented",
    "flashing_automation_implemented",
)
EXPECTED_CANDIDATE_GENERATION_POLICY = {
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


class SourceOwnedCandidateGenerationError(AssertionError):
    """Raised when the candidate-generation workflow drifts."""


def fail(message: str) -> None:
    raise SourceOwnedCandidateGenerationError(message)


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(read_required(path))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must contain a JSON object")
    return payload


def parse_tool_json(output: str) -> dict[str, Any]:
    start = output.find("{")
    if start == -1:
        fail("tool output did not include JSON")
    payload = json.loads(output[start:])
    if not isinstance(payload, dict):
        fail("tool output must be a JSON object")
    return payload


def tracked_bytes_snapshot(root: Path) -> str:
    paths = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
    ).stdout.split(b"\0")
    records: list[str] = []
    for raw_path in paths:
        if not raw_path:
            continue
        relative = Path(raw_path.decode())
        path = root / relative
        if path.is_symlink():
            mode = "120000"
            content = os.readlink(path).encode()
        else:
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        records.append(f"{mode} {relative.as_posix()} {digest}")
    return "\n".join(records)


def canonical_snapshot() -> tuple[str, str, str, str]:
    def run(*command: str) -> str:
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        return completed.stdout

    return (
        run("git", "rev-parse", "HEAD"),
        run("git", "ls-files", "--stage"),
        tracked_bytes_snapshot(REPO_ROOT),
        run("git", "status", "--porcelain=v1", "-uall"),
    )


def temporary_repository(branch: str) -> tempfile.TemporaryDirectory[str]:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout
    directory = tempfile.TemporaryDirectory(prefix="glyph_candidate_generation_")
    root = Path(directory.name)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        tar.extractall(root)
    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout.split(b"\0")
    for raw_path in tracked:
        if not raw_path:
            continue
        relative = Path(raw_path.decode())
        source = REPO_ROOT / relative
        destination = root / relative
        if source.is_symlink():
            destination.unlink(missing_ok=True)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(source.readlink())
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    subprocess.run(["git", "init", "-b", branch], cwd=root, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", "Glyph checker"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "glyph-checker@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "--all"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "controlled checker snapshot"], cwd=root, capture_output=True, check=True)
    if tracked_bytes_snapshot(root) != tracked_bytes_snapshot(REPO_ROOT):
        directory.cleanup()
        fail("temporary repository does not match exact tracked stage-0 bytes")
    return directory


def run_tool_in_repository(root: Path, *args: str) -> tuple[int, dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, "tools/prepare_source_owned_candidate_branch.py", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    payload: dict[str, Any] = {}
    if output.strip().startswith("{"):
        payload = parse_tool_json(output)
    return completed.returncode, payload, output


def assert_rejected(root: Path, *args: str, reason: str) -> None:
    before = (subprocess.run(["git", "ls-files", "--stage"], cwd=root, capture_output=True, text=True, check=True).stdout,
              tracked_bytes_snapshot(root),
              subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=root, capture_output=True, text=True, check=True).stdout,
              (root / ALLOWED_TARGET_PATH).read_bytes())
    returncode, payload, output = run_tool_in_repository(root, *args)
    if returncode == 0 or payload or reason not in output:
        fail(f"{reason} refusal failed: {output}")
    after = (subprocess.run(["git", "ls-files", "--stage"], cwd=root, capture_output=True, text=True, check=True).stdout,
             tracked_bytes_snapshot(root),
             subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=root, capture_output=True, text=True, check=True).stdout,
             (root / ALLOWED_TARGET_PATH).read_bytes())
    if before != after:
        fail(f"{reason} refusal changed temporary repository state")


def validate_plan_payload(payload: dict[str, Any], fixture: dict[str, Any], *, input_kind: str, repository_root: Path = REPO_ROOT) -> None:
    if payload.get("schema_version") != 1:
        fail("plan schema_version must be 1")
    if payload.get("packet") != "source_owned_candidate_generation_plan":
        fail("plan packet name drifted")
    if payload.get("status") != "dry_run_plan":
        fail("dry-run plan must stay dry_run_plan")
    if payload.get("candidate_branch_name") != fixture.get("candidate_branch_name"):
        fail("candidate branch name drifted")
    if payload.get("input_kind") != input_kind:
        fail("input kind drifted")
    expected_target = (repository_root / str(fixture.get("approved_target_source_path"))).resolve()
    if Path(payload.get("target_source_install_path", "")).resolve() != expected_target:
        fail("target source install path drifted")
    if payload.get("build_command") != fixture.get("build_command"):
        fail("build command drifted")
    if payload.get("hardware_gate_status") != fixture.get("hardware_gate_status"):
        fail("hardware gate status drifted")
    if payload.get("source_write_mode") is not False:
        fail("dry-run plan must not enable source write mode")
    if payload.get("validation_commands") != fixture.get("validation_commands"):
        fail("validation commands drifted")
    if payload.get("source_write_safeguards") != fixture.get("source_write_safeguards"):
        fail("source-write safeguards drifted")
    if payload.get("candidate_generation_policy") != fixture.get("candidate_generation_policy"):
        fail("candidate generation policy drifted")
    if payload.get("candidate_generation_without_table_change_manifest") != "reject":
        fail("plans must reject candidate generation without a table-by-table change manifest")
    if payload.get("explicit_profile_table_ownership_required") is not True:
        fail("plans must require explicit profile table ownership")
    if payload.get("current_source_preserve_policy_required_for_unspecified_tables") is not True:
        fail("plans must require current-source preserve policy for unspecified tables")
    for claim in FORBIDDEN_CLAIMS:
        if claim not in payload.get("forbidden_claims", []):
            fail(f"missing forbidden claim marker: {claim}")


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema_version") != 1:
        fail("fixture schema_version must be 1")
    if fixture.get("packet") != "source_owned_candidate_generation_workflow":
        fail("fixture packet drifted")
    if fixture.get("branch") != "runtime-config-install-workflow-candidate-generation":
        fail("fixture branch drifted")
    if fixture.get("candidate_branch_name") != "runtime-config-install-workflow-candidate-generation":
        fail("fixture candidate_branch_name drifted")
    if fixture.get("workflow_mode") != "dry_run_only":
        fail("fixture workflow_mode must be dry_run_only")
    if fixture.get("approved_target_source_path") != ALLOWED_TARGET_PATH:
        fail("fixture approved target path drifted")
    if fixture.get("hardware_gate_status") != "NOT_REQUIRED_FOR_DRY_RUN":
        fail("fixture hardware gate status drifted")
    if fixture.get("build_command") != "pio run -e glyph_mk6":
        fail("fixture build command drifted")
    if fixture.get("validation_commands") != [
        "python3 tools/check_glyph_source_owned_generator_modes.py",
        "python3 tools/check_glyph_source_owned_source_authority_intake.py",
        "python3 tools/check_glyph_source_owned_table_symbol_map.py",
        "python3 tools/check_glyph_docs_navigation.py",
        "python3 tools/check_glyph_docs_agent_surface.py",
        "python3 tools/check_glyph_generated_source_owned_generator_contract.py",
        "python3 tools/check_glyph_generated_source_owned_artifact_install.py",
        "python3 tools/check_glyph_generated_source_owned_baseline_artifact.py",
        "python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py --check-layout-spec-bridge",
    ]:
        fail("fixture validation_commands drifted")
    if fixture.get("source_write_safeguards") != [
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
    ]:
        fail("fixture source_write_safeguards drifted")
    if fixture.get("candidate_generation_policy") != EXPECTED_CANDIDATE_GENERATION_POLICY:
        fail("fixture candidate_generation_policy drifted")
    if fixture.get("candidate_generation_without_table_change_manifest") != "reject":
        fail("fixture must reject candidate generation without a table-by-table change manifest")
    if fixture.get("explicit_profile_table_ownership_required") is not True:
        fail("fixture must require explicit profile table ownership")
    if fixture.get("current_source_preserve_policy_required_for_unspecified_tables") is not True:
        fail("fixture must require current-source preserve policy for unspecified tables")
    if fixture.get("forbidden_claims") != list(FORBIDDEN_CLAIMS):
        fail("fixture forbidden_claims drifted")


def validate_dry_run_outputs() -> None:
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)
    before = canonical_snapshot()
    with temporary_repository("feature-test") as directory:
        root = Path(directory)
        for argument, kind in (("docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json", "profile"),
                               ("docs/runtime_config/fixtures/generated_source_owned_layout_spec.json", "layout-spec")):
            option = "--profile" if kind == "profile" else "--layout-spec"
            returncode, payload, output = run_tool_in_repository(root, option, argument)
            if returncode != 0:
                fail(f"{kind} dry-run unexpectedly failed: {output}")
            validate_plan_payload(payload, fixture, input_kind=kind, repository_root=root)
            if not Path(payload["converted_or_validated_layout_spec_path"]).is_absolute() or not Path(payload["generated_source_artifact_path"]).is_absolute():
                fail(f"{kind} dry-run paths must be absolute")
    if canonical_snapshot() != before:
        fail("canonical repository changed during isolated dry-run")


def validate_path_guards() -> None:
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)

    forbidden_path = Path("/tmp/not-approved-path.hpp")

    before = canonical_snapshot()
    common = ("--layout-spec", "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json", "--write-source", "--candidate-branch", "feature-test")
    with temporary_repository("configurator") as directory:
        root = Path(directory)
        assert_rejected(root, *common, "--candidate-branch", "configurator", reason="configurator")
    with temporary_repository("feature-current") as directory:
        root = Path(directory)
        assert_rejected(root, "--layout-spec", "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json", "--write-source", "--candidate-branch", "feature-requested", reason="checked-out branch")
    with temporary_repository("feature-test") as directory:
        root = Path(directory)
        unsupported_returncode, unsupported_payload, unsupported_output = run_tool_in_repository(
            root, "--profile", "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_runtime_loaded_claim.json"
        )
        if unsupported_returncode == 0 or unsupported_payload or "error:" not in unsupported_output:
            fail("unsupported profile refusal failed: " + unsupported_output)
        assert_rejected(root, *common, "--target-source-path", str(root / ACTIVE_TARGET_PATH), reason="active compile-time table content")
        assert_rejected(root, *common, "--target-source-path", str(forbidden_path), reason="exact inert example artifact")
        assert_rejected(root, "--profile", "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_runtime_loaded_claim.json", "--write-source", "--candidate-branch", "feature-test", reason="runtime_loaded_config_implemented must be False")
        (root / "untracked.txt").write_text("dirty\n", encoding="utf-8")
        assert_rejected(root, *common, reason="working tree must be clean")
    if canonical_snapshot() != before:
        fail("canonical repository changed during isolated refusal tests")


def main() -> int:
    try:
        validate_dry_run_outputs()
        validate_path_guards()
        print("glyph_source_owned_candidate_generation: PASS")
        print(f"- fixture: {FIXTURE.relative_to(REPO_ROOT)}")
        print(f"- tool: {TOOL.relative_to(REPO_ROOT)}")
        print(f"- allowed target path: {ALLOWED_TARGET_PATH}")
        return 0
    except (SourceOwnedCandidateGenerationError, OSError, json.JSONDecodeError) as exc:
        print("glyph_source_owned_candidate_generation: FAIL")
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
