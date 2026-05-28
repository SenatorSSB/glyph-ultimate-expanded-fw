#!/usr/bin/env python3
"""Aggregate prehardware checks for Glyph Ultimate Tilt deliverables.

This helper is intentionally automation-only:
- it runs existing read-only check scripts;
- optional flags can include a local build and artifact/result checks;
- it does not flash firmware, push to device, or mutate runtime behavior.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CheckStep:
    label: str
    command: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Glyph Ultimate Tilt prehardware checks as one command.",
    )
    parser.add_argument(
        "--base",
        default="configurator",
        help="base ref for future tilt patch scope checks (default: configurator)",
    )
    parser.add_argument(
        "--include-build",
        action="store_true",
        help="include '.venv/bin/python -m platformio run -e glyph_mk6'",
    )
    parser.add_argument(
        "--check-artifact",
        action="store_true",
        help="include strict local glyph_mk6 artifact inspection",
    )
    parser.add_argument(
        "--check-hardware-result",
        action="store_true",
        help="include hardware result markdown structure check",
    )
    return parser.parse_args()


def _python_step(label: str, *argv: str) -> CheckStep:
    return CheckStep(label=label, command=[sys.executable, *argv])


def _runtime_file_changed(base_ref: str) -> bool:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", "src/modes/Ultimate.cpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0 and bool(completed.stdout.strip())


def _base_steps(base_ref: str) -> list[CheckStep]:
    steps = [
        _python_step("check fixtures", "tools/check_glyph_calibration_fixtures.py"),
        _python_step("check patch script", "tools/check_glyph_patch_script.py"),
        _python_step("list modifier symbols", "tools/list_glyph_modifier_symbols.py"),
        _python_step("list tilt runtime gate sources", "tools/list_glyph_tilt_runtime_gate_sources.py"),
        _python_step("list native ultimate analog sources", "tools/list_glyph_native_ultimate_analog_sources.py"),
        _python_step("check native ultimate snapshot", "tools/check_glyph_native_ultimate_snapshot.py"),
        _python_step(
            "check future tilt patch scope runtime-implementation",
            "tools/check_glyph_future_tilt_patch_scope.py",
            "--base",
            base_ref,
            "--mode",
            "runtime-implementation",
        ),
        _python_step("check ultimate tilt domain spec", "tools/check_glyph_ultimate_tilt_domain_spec.py"),
        _python_step("list tilt button id candidates", "tools/list_glyph_tilt_button_id_candidates.py"),
        _python_step("check tilt button id probe", "tools/check_glyph_tilt_button_id_probe.py"),
        _python_step("check native ultimate runtime scope", "tools/check_glyph_native_ultimate_table_runtime_scope.py"),
        _python_step("check smashbox profile tables", "tools/check_glyph_smashbox_profile_tables.py"),
        _python_step("check smashbox runtime source", "tools/check_glyph_smashbox_modifiers_runtime_source.py"),
        _python_step("check smashbox identity runtime bindings", "tools/check_glyph_smashbox_identity_runtime_bindings.py"),
        _python_step("check ultimate tilt rc manifest", "tools/check_glyph_ultimate_tilt_rc_manifest.py"),
        _python_step(
            "check ultimate tilt docs consistency",
            "tools/check_glyph_ultimate_tilt_docs_consistency.py",
        ),
    ]
    if not _runtime_file_changed(base_ref):
        steps.insert(
            6,
            _python_step(
                "check future tilt patch scope docs-only",
                "tools/check_glyph_future_tilt_patch_scope.py",
                "--base",
                base_ref,
                "--mode",
                "docs-only",
            ),
        )
    return steps


def _optional_steps(args: argparse.Namespace) -> list[CheckStep]:
    optional_steps: list[CheckStep] = []

    if args.check_artifact:
        optional_steps.append(
            _python_step(
                "inspect glyph mk6 build artifact (strict)",
                "tools/inspect_glyph_mk6_build_artifact.py",
                "--strict",
            )
        )

    if args.check_hardware_result:
        optional_steps.append(
            _python_step(
                "check ultimate tilt hardware result",
                "tools/check_glyph_ultimate_tilt_hardware_result.py",
            )
        )

    if args.include_build:
        optional_steps.append(
            CheckStep(
                label="platformio build glyph_mk6",
                command=[sys.executable, "-m", "platformio", "run", "-e", "glyph_mk6"],
            )
        )

    return optional_steps


def _run_step(step: CheckStep) -> tuple[bool, str]:
    completed = subprocess.run(
        step.command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output_lines: list[str] = []
    if completed.stdout.strip():
        output_lines.append(completed.stdout.strip())
    if completed.stderr.strip():
        output_lines.append(completed.stderr.strip())

    joined_output = "\n".join(output_lines)
    return completed.returncode == 0, joined_output


def run(args: argparse.Namespace) -> int:
    steps = _base_steps(args.base)
    steps.extend(_optional_steps(args))

    print("glyph_ultimate_tilt_prehardware_checks")
    print(f"repo_root={REPO_ROOT}")
    print(f"step_count={len(steps)}")
    print(f"base_ref={args.base}")
    print(f"include_build={args.include_build}")
    print(f"check_artifact={args.check_artifact}")
    print(f"check_hardware_result={args.check_hardware_result}")

    failures: list[str] = []

    for step in steps:
        command_text = " ".join(step.command)
        print(f"\n=== RUN {step.label} ===")
        print(f"command={command_text}")

        passed, output = _run_step(step)
        status = "PASS" if passed else "FAIL"
        print(f"status={status}")
        if output:
            print(output)

        if not passed:
            failures.append(step.label)

    print("\n=== SUMMARY ===")
    print(f"failed_steps={len(failures)}")
    if failures:
        for label in failures:
            print(f"- {label}")
        print("overall_status=FAIL")
        return 1

    print("overall_status=PASS")
    return 0


def main() -> int:
    args = parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
