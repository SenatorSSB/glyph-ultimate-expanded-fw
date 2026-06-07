#!/usr/bin/env python3
"""Validate Step 15 WebSerial/device-write source-authority guardrails."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/runtime_config/runtime_config_webserial_device_write_source_authority.md"
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
FORBIDDEN_CHANGED_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
    "lib/",
)

REQUIRED_PHRASES = (
    "DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false",
    "Step 16 WebSerial/device-write implementation is blocked",
    "Current Source-Backed Transport Mechanisms",
    "Current Command IDs And Payload Handling",
    "Current Config Get Set Behavior",
    "No Step 16 implementation is allowed by this audit",
    "WebSerial/device write is not implemented",
    "Runtime-loaded config is not implemented",
    "Firmware flashing automation is not implemented",
    "Nunchuk validation is not claimed",
)

REQUIRED_REFERENCES = (
    "HAL/pico/src/comms/ConfiguratorBackend.cpp",
    "HAL/pico/include/comms/ConfiguratorBackend.hpp",
    "HAL/pico/include/core/Persistence.hpp",
    "HAL/pico/src/core/Persistence.cpp",
    "HAL/pico/src/comms/backend_init.cpp",
    "config/glyph/common/src/config.cpp",
    "tools/glyph_serial_config_tool.py",
    "docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md",
)

FORBIDDEN_SOURCE_MARKERS = (
    "CMD_SET_RUNTIME_CONFIG",
    "CMD_GET_RUNTIME_CONFIG",
    "WebSerialDeviceWriter",
    "writeRuntimeConfig",
    "SaveRuntimeConfig",
    "LoadRuntimeConfigFromSerial",
)

FLASHING_MARKERS = (
    "RPI-RP2",
    "copyfile(",
    "shutil.copy",
    "dd if=",
    "uf2 write",
    "upload_port",
)


class WebSerialSourceAuthorityError(ValueError):
    """Raised when Step 15 source-authority guardrails drift."""


def fail(message: str) -> None:
    raise WebSerialSourceAuthorityError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required doc: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def changed_paths_against_base() -> list[str]:
    paths: set[str] = set()
    commands = (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    )
    for command in commands:
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())

    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line:
                paths.add(line[3:].strip())
    return sorted(paths)


def require_phrases(text: str) -> None:
    lowered = normalize(text)
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"source authority doc missing required phrase: {phrase}")
    for reference in REQUIRED_REFERENCES:
        if reference.lower() not in lowered:
            fail(f"source authority doc missing required reference: {reference}")


def ensure_flag_false(text: str) -> None:
    if "DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=true" in text:
        fail("device-write implementation flag must not be true on this branch")
    if "DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false" not in text:
        fail("device-write implementation flag must be explicitly false")


def ensure_no_positive_claims(text: str) -> None:
    lowered = normalize(text)
    positive_patterns = (
        r"\bwebserial/device write is implemented\b",
        r"\bwebserial implementation is implemented\b",
        r"\bdevice-write implementation is implemented\b",
        r"\bruntime-loaded config is implemented\b",
        r"\bfirmware flashing automation is implemented\b",
        r"\bhardware validation is claimed\b",
        r"\bnunchuk validation is claimed\b",
    )
    for pattern in positive_patterns:
        if re.search(pattern, lowered):
            fail(f"source authority doc contains positive implementation claim: {pattern}")


def ensure_changed_scope() -> None:
    changed = changed_paths_against_base()
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_CHANGED_PREFIXES)]
    if forbidden:
        fail("firmware/source/device paths changed while device-write implementation is blocked: " + ", ".join(forbidden))
    out_of_scope = [path for path in changed if not path.startswith(ALLOWED_CHANGED_PREFIXES)]
    if out_of_scope:
        fail("Step 15 branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))


def ensure_no_runtime_write_symbols_added() -> None:
    for root_name in ("src", "include", "HAL", "config"):
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".c", ".cc", ".cpp", ".h", ".hpp"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in FORBIDDEN_SOURCE_MARKERS:
                if marker in text:
                    fail(f"blocked runtime/device-write marker {marker!r} found in {path.relative_to(REPO_ROOT)}")


def ensure_no_flashing_automation_changed() -> None:
    changed = changed_paths_against_base()
    for relpath in changed:
        path = REPO_ROOT / relpath
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for marker in FLASHING_MARKERS:
            if marker.lower() in lowered and "not" not in lowered and "no " not in lowered:
                fail(f"potential flashing automation marker {marker!r} found in changed file {relpath}")


def main() -> int:
    print("glyph_runtime_config_webserial_device_write_source_authority")
    try:
        text = read_required(DOC)
        require_phrases(text)
        ensure_flag_false(text)
        ensure_no_positive_claims(text)
        ensure_changed_scope()
        ensure_no_runtime_write_symbols_added()
        ensure_no_flashing_automation_changed()
    except (OSError, ValueError, WebSerialSourceAuthorityError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("device_write_implementation_allowed_by_source_audit=false")
    print("webserial_device_write_implemented=false")
    print("firmware_flashing_automation_implemented=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
