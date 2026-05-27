#!/usr/bin/env python3
"""Aggregate read-only prehardware dry-run checks for Glyph docs/tools."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
AGGREGATE_NAME = "glyph_prehardware_dry_run_checks"


@dataclass(frozen=True)
class CommandSpec:
    tool: str
    args: tuple[str, ...] = ()
    acceptable_caveat_statuses: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandResult:
    spec: CommandSpec
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    status: str | None
    accepted: bool


def default_commands() -> list[CommandSpec]:
    return [
        CommandSpec("tools/check_glyph_prehardware_rc_runbook.py"),
        CommandSpec("tools/inspect_glyph_mk6_build_artifact.py", acceptable_caveat_statuses=("NO_ARTIFACT",)),
        CommandSpec("tools/check_glyph_user_requirements_packet.py"),
        CommandSpec("tools/check_glyph_preservation_execution_packet.py"),
        CommandSpec("tools/check_glyph_preimplementation_blockers.py"),
        CommandSpec("tools/check_glyph_firmware_workstream_roadmap.py"),
        CommandSpec(
            "tools/check_glyph_native_ultimate_table_fixture.py",
            ("docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json",),
        ),
        CommandSpec(
            "tools/check_glyph_native_ultimate_table_fixture.py",
            ("docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json",),
        ),
        CommandSpec("tools/check_glyph_native_ultimate_table_runtime_scope.py"),
        CommandSpec("tools/check_glyph_ultimate_tilt3_runtime_source.py"),
        CommandSpec("tools/check_glyph_ultimate_lt3_profile_binding.py"),
        CommandSpec("tools/check_glyph_active_ultimate_lt3_config_artifact.py"),
        CommandSpec("tools/check_glyph_ultimate_dpad_profile_mapping.py"),
        CommandSpec("tools/check_glyph_serial_config_writer.py"),
        CommandSpec("tools/run_glyph_next_runtime_change_readiness_checks.py"),
        CommandSpec("tools/check_glyph_merged_state_consistency.py"),
        CommandSpec("tools/check_glyph_no_forbidden_artifacts.py"),
        CommandSpec(
            "tools/check_glyph_ultimate_preservation_hardware_result.py",
            acceptable_caveat_statuses=("NO_RESULT_FILE",),
        ),
    ]


def extract_status(stdout: str) -> str | None:
    for line in stdout.splitlines():
        if line.startswith("status="):
            return line.split("=", 1)[1].strip()
    return None


def run_command(spec: CommandSpec) -> CommandResult:
    command = [sys.executable, spec.tool, *spec.args]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    status = extract_status(completed.stdout)
    caveat_statuses = {"NO_ARTIFACT", "NO_RESULT_FILE"}
    accepted = completed.returncode == 0 and (
        status not in caveat_statuses or status in spec.acceptable_caveat_statuses
    )
    return CommandResult(
        spec=spec,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        status=status,
        accepted=accepted,
    )


def print_grouped_output(result: CommandResult) -> None:
    print("\n--- command ---")
    print(" ".join(result.command))
    print(f"exit_code={result.returncode}")
    print(f"reported_status={result.status if result.status is not None else 'NONE'}")
    print(f"accepted={'yes' if result.accepted else 'no'}")

    print("--- stdout ---")
    if result.stdout:
        print(result.stdout.rstrip())
    else:
        print("(empty)")

    print("--- stderr ---")
    if result.stderr:
        print(result.stderr.rstrip())
    else:
        print("(empty)")


def main() -> int:
    print(f"aggregate={AGGREGATE_NAME}")
    print(f"repo_root={REPO_ROOT}")
    print("mode=read_only_no_build_no_flash_no_device_copy_no_writes")

    results = [run_command(spec) for spec in default_commands()]
    for result in results:
        print_grouped_output(result)

    failures = [result for result in results if not result.accepted]
    observed_no_artifact = any(result.status == "NO_ARTIFACT" for result in results)
    observed_no_result_file = any(result.status == "NO_RESULT_FILE" for result in results)

    print("\n=== aggregate summary ===")
    print(f"commands_total={len(results)}")
    print(f"commands_failed={len(failures)}")
    print(f"observed_NO_ARTIFACT={'yes' if observed_no_artifact else 'no'}")
    print(f"observed_NO_RESULT_FILE={'yes' if observed_no_result_file else 'no'}")
    print("note=NO_ARTIFACT is acceptable for this dry-run because this checker does not build")
    print("note=NO_RESULT_FILE is acceptable for this dry-run because this checker does not create a hardware result")
    print("note=PASS means dry-run checker suite passed only")
    print("note=PASS does not mean hardware readiness")
    print("note=PASS does not mean firmware safety")
    print("note=PASS does not mean flashing approval")
    print("note=PASS does not mean preservation verification")

    if failures:
        print("final_status=FAIL")
        for result in failures:
            print(f"failed_command={' '.join(result.command)}")
        return 1

    print("final_status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
