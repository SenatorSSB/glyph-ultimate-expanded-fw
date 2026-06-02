#!/usr/bin/env python3
"""Aggregate readiness checks before the next Glyph runtime change.

Read-only. Runs present checker tools and clearly skips optional tools that may
live on sibling branches until this branch sequence is merged.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    label: str
    path: Path
    args: tuple[str, ...] = ()
    optional_until_merged: bool = False
    accept_no_result_file: bool = False


@dataclass
class StepResult:
    step: Step
    status: str
    returncode: int | None = None
    output: str = ""


def step(label: str, relpath: str, *args: str, optional: bool = False, accept_no_result_file: bool = False) -> Step:
    return Step(
        label=label,
        path=REPO_ROOT / relpath,
        args=args,
        optional_until_merged=optional,
        accept_no_result_file=accept_no_result_file,
    )


def steps() -> list[Step]:
    return [
        step("ultimate tilt prehardware aggregate", "tools/run_glyph_ultimate_tilt_prehardware_checks.py"),
        step("ultimate tilt hardware result", "tools/check_glyph_ultimate_tilt_hardware_result.py"),
        step("ultimate tilt rc manifest", "tools/check_glyph_ultimate_tilt_rc_manifest.py"),
        step("profile config semantics", "tools/check_glyph_profile_config_semantics.py"),
        step("profile config export corpus", "tools/check_glyph_profile_config_export_corpus.py"),
        step(
            "profile adapter prewrite",
            "tools/check_glyph_profile_adapter_prewrite.py",
            "docs/sources/raw/GlyphUserProfiles.json",
            optional=True,
        ),
        step(
            "ultimate preservation hardware result",
            "tools/check_glyph_ultimate_preservation_hardware_result.py",
            optional=True,
            accept_no_result_file=True,
        ),
        step(
            "native ultimate table fixture",
            "tools/check_glyph_native_ultimate_table_fixture.py",
            "docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json",
            optional=True,
        ),
        step(
            "native ultimate table runtime scope",
            "tools/check_glyph_native_ultimate_table_runtime_scope.py",
            optional=True,
        ),
        step(
            "smashbox profile tables",
            "tools/check_glyph_smashbox_profile_tables.py",
            optional=True,
        ),
        step(
            "smashbox runtime source",
            "tools/check_glyph_smashbox_modifiers_runtime_source.py",
            optional=True,
        ),
        step(
            "smashbox identity runtime bindings",
            "tools/check_glyph_smashbox_identity_runtime_bindings.py",
            optional=True,
        ),
        step(
            "identity runtime behavior cases",
            "tools/check_glyph_identity_runtime_behavior_cases.py",
        ),
        step(
            "identity runtime table source sync",
            "tools/check_glyph_identity_runtime_table_source_sync.py",
        ),
        step(
            "identity runtime generated config prototype",
            "tools/check_glyph_identity_runtime_generated_config_prototype.py",
        ),
        step(
            "identity runtime generated config evaluator input",
            "tools/check_glyph_identity_runtime_generated_config_evaluator_input.py",
        ),
        step(
            "identity runtime generated cpp diff artifact",
            "tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py",
        ),
        step(
            "identity runtime behavior evaluator",
            "tools/check_glyph_identity_runtime_behavior_evaluator.py",
        ),
    ]


def run_step(item: Step) -> StepResult:
    if not item.path.exists():
        status = "SKIP_OPTIONAL_NOT_PRESENT" if item.optional_until_merged else "FAIL_MISSING_REQUIRED"
        return StepResult(step=item, status=status)

    command = [sys.executable, str(item.path.relative_to(REPO_ROOT)), *item.args]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)

    if completed.returncode == 0:
        if item.accept_no_result_file and "status=NO_RESULT_FILE" in output:
            return StepResult(step=item, status="PASS_EXPECTED_NO_RESULT_FILE", returncode=0, output=output)
        return StepResult(step=item, status="PASS", returncode=0, output=output)
    return StepResult(step=item, status="FAIL", returncode=completed.returncode, output=output)


def print_result(result: StepResult) -> None:
    print(f"\n=== {result.step.label} ===")
    print(f"tool={result.step.path.relative_to(REPO_ROOT)}")
    if result.step.args:
        print("args=" + " ".join(result.step.args))
    print(f"status={result.status}")
    if result.returncode is not None:
        print(f"returncode={result.returncode}")
    if result.output:
        print(result.output)


def main() -> int:
    results = [run_step(item) for item in steps()]

    print("glyph_next_runtime_change_readiness_checks")
    print(f"repo_root={REPO_ROOT}")
    for result in results:
        print_result(result)

    real_failures = [result for result in results if result.status.startswith("FAIL")]
    skipped_optional = [result for result in results if result.status == "SKIP_OPTIONAL_NOT_PRESENT"]
    expected_no_result = [result for result in results if result.status == "PASS_EXPECTED_NO_RESULT_FILE"]

    readiness: list[str] = ["READY_FOR_DESIGN_ONLY"]
    if skipped_optional:
        readiness.append("BLOCKED_NEEDS_USER_INPUT")
    if expected_no_result:
        readiness.append("BLOCKED_NEEDS_HARDWARE")
    else:
        # Current prehardware sequence still requires preservation hardware before runtime patch review.
        readiness.append("BLOCKED_NEEDS_HARDWARE")
    if real_failures:
        readiness.append("BLOCKED_CHECK_FAILURE")
    if not real_failures and not skipped_optional and not expected_no_result:
        readiness.append("READY_FOR_RUNTIME_PATCH_REVIEW")

    print("\n=== SUMMARY ===")
    print(f"checks_total={len(results)}")
    print(f"checks_failed={len(real_failures)}")
    print(f"optional_skipped={len(skipped_optional)}")
    print("readiness=" + ",".join(readiness))
    if skipped_optional:
        print("skipped_optional_tools:")
        for result in skipped_optional:
            print(f"- {result.step.path.relative_to(REPO_ROOT)}")
    if real_failures:
        print("failed_tools:")
        for result in real_failures:
            print(f"- {result.step.path.relative_to(REPO_ROOT)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
