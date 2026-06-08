#!/usr/bin/env python3
"""Validate the Step 17 flashing-automation safety boundary."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/runtime_config/runtime_config_flashing_automation_safety_boundary.md"
CHECKER_PATH = REPO_ROOT / "tools/check_glyph_runtime_config_flashing_automation_safety_boundary.py"
BASE_BRANCH = "configurator"

ALLOWED_CHANGED_PREFIXES = (
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/release/",
    "docs/export/",
    "docs/runtime_config/",
    "docs/calibration/",
    "tools/",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
    "lib/",
    "scripts/",
)

PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
    "src/modes/UltimateRuntimeConfigParser.hpp",
}

REQUIRED_HEADINGS = (
    "Purpose",
    "Inspected Files And Searches",
    "Source-Backed Safety Facts",
    "Forbidden Automation Classes",
    "Allowed Manual Guidance",
    "Required Future Gates Before Reconsideration",
    "Non-Claims",
    "Stop Conditions Hit",
)

REQUIRED_PHRASES = (
    "Status label: FORBIDDEN_NOT_APPROVED.",
    "This Step 17 packet sets the safety and source-authority boundary for any future",
    "firmware flashing automation is forbidden/not approved.",
    "This branch does not implement firmware flashing automation, firmware update automation, automatic UF2 upload, or hidden device write tooling.",
    "The current Step 17 boundary allows manual/operator-run flashing instructions only:",
    "manual/operator-run flashing instructions may be referenced only as manual recovery/update guidance",
    "manual paths must be visibly operator-run and do not turn manual instructions into automated tooling",
    "operator confirms target, artifact, and intent before any host-initiated flash attempt",
    "operator performs bootloader/RPI-RP2 hand-off manually",
    "no automatic fallback or background recovery write path is allowed",
    "this branch adds no automation for firmware update workflows",
    "Step 17 remains `FORBIDDEN_NOT_APPROVED` until all of these are satisfied by",
    "UF2 copy automation",
    "bootloader/RPI-RP2 automation",
    "PlatformIO upload automation",
    "picotool/openocd automation",
    "WebSerial/device write",
    "hidden device mutation",
    "automatic recovery writes",
    "manual/operator-run flashing instructions may be referenced only as manual recovery/update guidance",
    "do not turn manual instructions into automated tooling",
    "explicit product approval",
    "source/legal/safety review",
    "exact hardware target",
    "recovery/rollback plan",
    "hardware test matrix",
    "user confirmation/consent model",
    "no hidden write policy",
    "no flashing automation",
    "no WebSerial/device write",
    "no runtime-loaded config",
    "no hardware validation",
    "no nunchuk validation",
)

REQUIRED_SOURCE_BACKED_FACTS = (
    "scripts/build-glyph-mk6-quiet.sh",
    "./scripts/pio-local.sh run -e glyph_mk6",
    "platformio.ini",
    "docs/sources/raw/glyph_firmware_uf2/1.0.7/README.md",
    "docs/sources/raw/glyph_firmware_uf2/1.0.7/manifest.json",
    "docs/project/G12H_UF2_FORMAT_AND_FLASH_RANGE_ANALYSIS.md",
    "docs/project/G12K_SAFE_FIRST_CUSTOM_FLASH_DECISION_GATE.md",
    "build scripts may compile firmware if present",
    "manual firmware update guidance as user-provided source text",
    "read-only references for analysis and recovery planning",
    "does not authorize flashing or copy-to-device behavior from these artifacts",
    "manual firmware update guidance exists in the above source text with the RPI-RP2 drag-and-drop flow and explicit user confirmation",
    "read-only UF2 comparison",
    "read-only decision gate",
    "no source-backed firmware artifact upload command",
    "explicit user-driven bootloader entry paths",
    "read-only artifact-inspection utilities and do not write firmware",
)

REQUIRED_FUTURE_GATES = (
    "explicit product approval",
    "source/legal/safety review",
    "exact hardware target",
    "recovery/rollback plan",
    "hardware test matrix",
    "user confirmation/consent model",
    "no hidden write policy",
)

REQUIRED_NON_CLAIMS = (
    "no flashing automation is implemented or approved by this branch",
    "no uf2 copy automation is implemented or approved by this branch",
    "no bootloader automation is implemented or approved by this branch",
    "no rpi-rp2 mass-storage automation is implemented or approved by this branch",
    "no WebSerial/device write is implemented or claimed",
    "no runtime-loaded config is implemented or claimed",
    "no hardware validation is claimed",
    "no nunchuk validation is claimed",
)

DOC_ALLOWED_NON_AUTOMATION_PHRASES = (
    "not implemented",
    "unimplemented",
    "not approved",
    "forbidden",
    "does not implement",
    "manual only",
    "manual/operator-run",
    "manual recovery/update guidance",
    "do not turn manual instructions into automated tooling",
    "implementation stop line",
    "not an automation path",
    "no automation",
    "no firmware flashing automation",
    '"firmware_flashing_automation_created": false',
    '"no_firmware_flashing_automation": true',
    "read-only",
    "analysis and recovery planning",
)

FORBIDDEN_MARKERS = (
    "rpi-rp2",
    "bootloader",
    "bootsel",
    "shutil.copy",
    "copyfile(",
    "copy-to-device",
    "push-to-device",
    "save to device",
    "write to device",
    "pio run -t upload",
    "upload_protocol",
    "upload_port",
    "picotool",
    "openocd",
    "uf2 write",
    "diskutil",
    "hidden device write",
    "device mutation",
    "firmware flashing automation",
    "uf2 flashing automation",
    "automated recovery",
    "recovery write",
)


class FlashingAutomationSafetyBoundaryError(ValueError):
    """Raised when the Step 17 boundary drifts."""


def fail(message: str) -> None:
    raise FlashingAutomationSafetyBoundaryError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required doc: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def require_headings(text: str) -> None:
    lowered = text.lower()
    for heading in REQUIRED_HEADINGS:
        if f"## {heading.lower()}" not in lowered:
            fail(f"doc missing required section heading: {heading}")


def require_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    missing = [phrase for phrase in phrases if phrase.lower() not in lowered]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def changed_paths_against_base() -> list[str]:
    paths: set[str] = set()
    commands = (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    )
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line:
                paths.add(line[3:].strip())
    return sorted(paths)


def ensure_changed_scope() -> None:
    changed = changed_paths_against_base()
    forbidden = [
        path
        for path in changed
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES)
        and path not in PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS
    ]
    if forbidden:
        fail("forbidden firmware/source paths changed on Step 17 boundary branch: " + ", ".join(forbidden))

    out_of_scope = [
        path
        for path in changed
        if not path.startswith(ALLOWED_CHANGED_PREFIXES)
        and path not in PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS
    ]
    if out_of_scope:
        fail("Step 17 branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))
    scaffold_changed = [path for path in changed if path in PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS]
    if scaffold_changed:
        completed = subprocess.run(
            [sys.executable, "tools/check_glyph_runtime_config_firmware_parser_scaffold.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            fail(
                "Phase 7A firmware scaffold changed but scaffold guardrail failed: "
                + "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
            )


def ensure_no_automation_markers_in_changed_files() -> None:
    changed = changed_paths_against_base()
    doc_prefixes = (
        "README.md",
        "docs/CURRENT_STATE.md",
        "docs/ROADMAP.md",
        "docs/release/",
        "docs/export/",
        "docs/runtime_config/",
        "docs/calibration/",
    )
    for relpath in changed:
        if relpath in PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS:
            continue
        if relpath == "tools/check_glyph_runtime_config_flashing_automation_safety_boundary.py":
            continue
        if relpath.startswith("tools/"):
            continue

        path = REPO_ROOT / relpath
        if not path.exists() or not path.is_file():
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        hits = [marker for marker in FORBIDDEN_MARKERS if marker in lowered]
        if not hits:
            continue

        if relpath.startswith(doc_prefixes):
            if any(phrase in lowered for phrase in DOC_ALLOWED_NON_AUTOMATION_PHRASES):
                continue
            fail(
                "changed doc contains automation marker(s) without explicit non-automation language: "
                + relpath
                + " -> "
                + ", ".join(hits)
            )

        fail(
            "changed non-doc file contains automation marker(s): "
            + relpath
            + " -> "
            + ", ".join(hits)
        )


def ensure_positive_claims_absent(text: str) -> None:
    lowered = normalize(text)
    positive_patterns = (
        r"\bfirmware flashing automation is implemented\b",
        r"\bflash automation is implemented\b",
    )
    for pattern in positive_patterns:
        if re.search(pattern, lowered):
            fail(f"doc contains positive implementation claim matching {pattern}")


def main() -> int:
    print("glyph_runtime_config_flashing_automation_safety_boundary")
    try:
        text = read_required(DOC)
        require_headings(text)
        require_phrases(text, REQUIRED_PHRASES, label="safety boundary doc")
        require_phrases(text, REQUIRED_SOURCE_BACKED_FACTS, label="safety boundary doc")
        require_phrases(text, REQUIRED_FUTURE_GATES, label="safety boundary doc")
        require_phrases(text, REQUIRED_NON_CLAIMS, label="safety boundary doc")
        ensure_positive_claims_absent(text)
        ensure_changed_scope()
        ensure_no_automation_markers_in_changed_files()
    except (OSError, ValueError, FlashingAutomationSafetyBoundaryError) as exc:
        print("status=FAIL")
        print("status_label=FORBIDDEN_NOT_APPROVED")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("status_label=FORBIDDEN_NOT_APPROVED")
    print(f"doc={DOC.relative_to(REPO_ROOT)}")
    print("firmware_flashing_automation=false")
    print("uf2_copy_automation=false")
    print("bootloader_automation=false")
    print("webserial_device_write=false")
    print("runtime_loaded_config_write=false")
    print("hardware_validation_claim=false")
    print("nunchuk_validation_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
