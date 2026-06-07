#!/usr/bin/env python3
"""Validate Step 16 device-write safety-plan guardrails."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/runtime_config/runtime_config_device_write_safety_plan.md"
SOURCE_DOC = REPO_ROOT / "docs/runtime_config/runtime_config_webserial_device_write_source_authority.md"
MANUAL_DOC = REPO_ROOT / "docs/runtime_config/runtime_config_manual_load_path_plan.md"
HARDWARE_PLAN = (
    REPO_ROOT / "docs/calibration/glyph_runtime_config_manual_load_device_write_hardware_plan_2026-06-07.md"
)
BASE_BRANCH = "configurator"

ALLOWED_CHANGED_PREFIXES = (
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/release/",
    "docs/runtime_config/",
    "docs/calibration/",
    "tools/",
)
IMPLEMENTATION_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
)
DEVICE_TOOL_PATHS = (
    "tools/glyph_serial_config_tool.py",
)

REQUIRED_PHRASES = (
    "DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false",
    "Device-write implementation is stopped in this branch",
    "Explicit User Action Requirement",
    "No Hidden Writes",
    "Payload Validation Before Write",
    "Readback Round Trip Validation",
    "Backup Rollback And Recovery Plan",
    "Failure Modes",
    "Hardware Test Matrix",
    "Device-write implementation is not implemented",
    "WebSerial implementation is not implemented",
    "Firmware flashing automation is not implemented",
    "Hardware validation is not claimed",
    "Nunchuk validation is not claimed",
)

REQUIRED_HARDWARE_ROWS = (
    "Boot",
    "No runtime config baseline",
    "Valid manual-loaded config if implemented",
    "Invalid payload rejected",
    "No hidden write",
    "Readback/round-trip if implemented",
    "Recovery/rollback",
    "Profile regression",
    "NOT_TESTED",
)


class DeviceWriteSafetyPlanError(ValueError):
    """Raised when Step 16 safety-plan guardrails drift."""


def fail(message: str) -> None:
    raise DeviceWriteSafetyPlanError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required doc: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def changed_paths_against_base() -> list[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    ):
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())
    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line:
                paths.add(line[3:].strip())
    return sorted(paths)


def source_flag_false() -> bool:
    if not SOURCE_DOC.exists():
        return False
    return "DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false" in SOURCE_DOC.read_text(encoding="utf-8")


def manual_flag_false() -> bool:
    if not MANUAL_DOC.exists():
        return False
    return "MANUAL_LOAD_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false" in MANUAL_DOC.read_text(encoding="utf-8")


def require_phrases(text: str) -> None:
    lowered = normalize(text)
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"safety plan missing required phrase: {phrase}")
    for phrase in REQUIRED_HARDWARE_ROWS:
        if phrase.lower() not in lowered:
            fail(f"safety plan missing required hardware row phrase: {phrase}")


def ensure_no_positive_claims(text: str) -> None:
    lowered = normalize(text)
    positive_patterns = (
        r"\bdevice-write implementation is implemented\b",
        r"\bwebserial implementation is implemented\b",
        r"\bruntime-loaded config is implemented\b",
        r"\bstep 14 manual firmware load is implemented\b",
        r"\bfirmware parser implementation is implemented\b",
        r"\bruntime-config storage is implemented\b",
        r"\bhidden device write is implemented\b",
        r"\bfirmware flashing automation is implemented\b",
        r"\bhardware validation is claimed\b",
        r"\bnunchuk validation is claimed\b",
    )
    for pattern in positive_patterns:
        if re.search(pattern, lowered):
            fail(f"safety plan contains positive implementation claim: {pattern}")


def ensure_changed_scope_and_hardware_plan() -> None:
    changed = changed_paths_against_base()
    out_of_scope = [path for path in changed if not path.startswith(ALLOWED_CHANGED_PREFIXES)]
    if out_of_scope:
        fail("Step 16 branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))

    implementation_changed = [
        path
        for path in changed
        if path.startswith(IMPLEMENTATION_PREFIXES) or path in DEVICE_TOOL_PATHS
    ]
    if source_flag_false() and implementation_changed:
        fail(
            "device-write or firmware/source files changed while source audit blocks implementation: "
            + ", ".join(implementation_changed)
        )
    if implementation_changed and not HARDWARE_PLAN.exists():
        fail(
            "hardware plan is required when firmware or device-write implementation files change: "
            f"{HARDWARE_PLAN.relative_to(REPO_ROOT)}"
        )


def ensure_gates_block_step16() -> None:
    if not source_flag_false():
        fail("Step 16 source-authority doc must keep device-write implementation flag false")
    if not manual_flag_false():
        fail("Step 14 manual-load doc must keep manual-load implementation flag false")


def main() -> int:
    print("glyph_runtime_config_device_write_safety_plan")
    try:
        text = read_required(DOC)
        require_phrases(text)
        ensure_no_positive_claims(text)
        ensure_gates_block_step16()
        ensure_changed_scope_and_hardware_plan()
    except (OSError, ValueError, DeviceWriteSafetyPlanError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("device_write_implementation_allowed_by_source_audit=false")
    print("device_write_implemented=false")
    print("webserial_implemented=false")
    print("firmware_flashing_automation_implemented=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
