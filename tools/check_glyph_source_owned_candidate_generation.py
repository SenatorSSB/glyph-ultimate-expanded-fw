#!/usr/bin/env python3
"""Validate the offline source-owned candidate-generation workflow."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/prepare_source_owned_candidate_branch.py"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_candidate_generation_workflow.json"
PROFILE_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json"
LAYOUT_SPEC_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
INVALID_PROFILE_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_runtime_loaded_claim.json"

ALLOWED_TARGET_PATH = "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
FORBIDDEN_CLAIMS = (
    "runtime_loaded_config_implemented",
    "persistent_storage_implemented",
    "webserial_device_write_implemented",
    "backend_config_pb_write_path_implemented",
    "flashing_automation_implemented",
)


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


def run_tool(*args: str) -> tuple[int, dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, str(TOOL.relative_to(REPO_ROOT)), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    payload: dict[str, Any] = {}
    if output.strip().startswith("{"):
        payload = parse_tool_json(output)
    return completed.returncode, payload, output


def validate_plan_payload(payload: dict[str, Any], fixture: dict[str, Any], *, input_kind: str) -> None:
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
    expected_target = (REPO_ROOT / str(fixture.get("approved_target_source_path"))).resolve()
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
        "no device write",
        "no persistent storage",
        "no flashing automation",
        "no active publication changes",
    ]:
        fail("fixture source_write_safeguards drifted")
    if fixture.get("forbidden_claims") != list(FORBIDDEN_CLAIMS):
        fail("fixture forbidden_claims drifted")


def validate_dry_run_outputs() -> None:
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)

    profile_returncode, profile_payload, profile_output = run_tool(
        "--profile",
        str(PROFILE_FIXTURE.relative_to(REPO_ROOT)),
    )
    if profile_returncode != 0:
        fail("profile dry-run unexpectedly failed: " + profile_output)
    validate_plan_payload(profile_payload, fixture, input_kind="profile")
    if not Path(profile_payload["converted_or_validated_layout_spec_path"]).is_absolute():
        fail("profile dry-run layout-spec path must be absolute")
    if not Path(profile_payload["generated_source_artifact_path"]).is_absolute():
        fail("profile dry-run generated artifact path must be absolute")

    layout_returncode, layout_payload, layout_output = run_tool(
        "--layout-spec",
        str(LAYOUT_SPEC_FIXTURE.relative_to(REPO_ROOT)),
    )
    if layout_returncode != 0:
        fail("layout-spec dry-run unexpectedly failed: " + layout_output)
    validate_plan_payload(layout_payload, fixture, input_kind="layout-spec")


def validate_path_guards() -> None:
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)

    unsupported_returncode, unsupported_payload, unsupported_output = run_tool(
        "--profile",
        str(INVALID_PROFILE_FIXTURE.relative_to(REPO_ROOT)),
    )
    if unsupported_returncode == 0:
        fail("unsupported profile fixture unexpectedly succeeded")
    if unsupported_payload:
        fail("unsupported profile fixture must not emit a plan")
    if "error:" not in unsupported_output:
        fail("unsupported profile refusal must report an error")

    allowed_path = Path(REPO_ROOT / fixture["approved_target_source_path"])
    if not allowed_path.is_absolute():
        fail("approved target path must resolve to an absolute path")
    forbidden_path = Path("/tmp/not-approved-path.hpp")

    completed = subprocess.run(
        [sys.executable, str(TOOL.relative_to(REPO_ROOT)), "--layout-spec", str(LAYOUT_SPEC_FIXTURE.relative_to(REPO_ROOT)), "--candidate-branch", "configurator", "--write-source", "--target-source-path", str(allowed_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        fail("direct configurator source write unexpectedly succeeded")
    if "configurator" not in completed.stderr:
        fail("configurator refusal must mention the branch guard")

    completed = subprocess.run(
        [sys.executable, str(TOOL.relative_to(REPO_ROOT)), "--layout-spec", str(LAYOUT_SPEC_FIXTURE.relative_to(REPO_ROOT)), "--write-source", "--target-source-path", str(forbidden_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        fail("forbidden target path unexpectedly succeeded")
    if "install output path must be under" not in completed.stderr:
        fail("forbidden target path refusal must mention the allow-list")


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
