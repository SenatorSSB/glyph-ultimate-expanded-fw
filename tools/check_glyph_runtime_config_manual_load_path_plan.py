#!/usr/bin/env python3
"""Validate Step 14 manual-load path plan guardrails."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/runtime_config/runtime_config_manual_load_path_plan.md"
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
)

PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigParser.hpp",
}

REQUIRED_PHRASES = (
    "MANUAL_LOAD_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false",
    "Step 14 firmware-consuming manual config-load implementation is blocked",
    "Offline fixture load in tools",
    "Compiled test fixture in firmware",
    "Runtime firmware loading from storage",
    "Serial/config command payload",
    "WebSerial/device-write path",
    "Step 14 manual firmware load is not implemented",
    "Runtime-loaded config is not implemented",
    "WebSerial/device write is not implemented",
    "Firmware flashing automation is not implemented",
    "Nunchuk validation is not claimed",
)

REQUIRED_REFERENCES = (
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp",
    "tools/glyph_runtime_config_binary_roundtrip.py",
    "docs/runtime_config/runtime_config_firmware_binary_parser_integration_plan.md",
    "docs/runtime_config/runtime_config_webserial_device_write_source_authority.md",
)

FORBIDDEN_SOURCE_MARKERS = (
    "LoadRuntimeConfig",
    "ManualRuntimeConfig",
    "RuntimeConfigFixture",
    "CMD_SET_RUNTIME_CONFIG",
    "CMD_GET_RUNTIME_CONFIG",
)


class ManualLoadPlanError(ValueError):
    """Raised when Step 14 manual-load guardrails drift."""


def fail(message: str) -> None:
    raise ManualLoadPlanError(message)


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


def require_phrases(text: str) -> None:
    lowered = normalize(text)
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"manual-load plan missing required phrase: {phrase}")
    for reference in REQUIRED_REFERENCES:
        if reference.lower() not in lowered:
            fail(f"manual-load plan missing required reference: {reference}")


def ensure_flag_false(text: str) -> None:
    if "MANUAL_LOAD_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=true" in text:
        fail("manual-load implementation flag must not be true on this branch")
    if "MANUAL_LOAD_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false" not in text:
        fail("manual-load implementation flag must be explicitly false")


def ensure_no_positive_claims(text: str) -> None:
    lowered = normalize(text)
    positive_patterns = (
        r"\bstep 14 manual firmware load is implemented\b",
        r"\bruntime-loaded config is implemented\b",
        r"\bruntime-config storage is implemented\b",
        r"\bfirmware parser implementation is implemented\b",
        r"\bwebserial/device write is implemented\b",
        r"\bfirmware flashing automation is implemented\b",
        r"\bnunchuk validation is claimed\b",
    )
    for pattern in positive_patterns:
        if re.search(pattern, lowered):
            fail(f"manual-load plan contains positive implementation claim: {pattern}")


def ensure_changed_scope() -> None:
    changed = changed_paths_against_base()
    forbidden = [
        path
        for path in changed
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES)
        and path not in PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS
    ]
    if forbidden:
        fail("firmware/source paths changed while manual-load implementation is blocked: " + ", ".join(forbidden))
    out_of_scope = [
        path
        for path in changed
        if not path.startswith(ALLOWED_CHANGED_PREFIXES)
        and path not in PHASE7A_ALLOWED_FIRMWARE_SCAFFOLD_PATHS
    ]
    if out_of_scope:
        fail("Step 14 branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))
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


def ensure_no_manual_load_symbols_added() -> None:
    for root_name in ("src", "include", "HAL", "config"):
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".c", ".cc", ".cpp", ".h", ".hpp"}:
                continue
            if str(path.relative_to(REPO_ROOT)) == "src/modes/UltimateRuntimeConfigParser.hpp":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in FORBIDDEN_SOURCE_MARKERS:
                if marker in text:
                    fail(f"blocked manual-load marker {marker!r} found in {path.relative_to(REPO_ROOT)}")


def main() -> int:
    print("glyph_runtime_config_manual_load_path_plan")
    try:
        text = read_required(DOC)
        require_phrases(text)
        ensure_flag_false(text)
        ensure_no_positive_claims(text)
        ensure_changed_scope()
        ensure_no_manual_load_symbols_added()
    except (OSError, ValueError, ManualLoadPlanError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("manual_load_implementation_allowed_by_source_audit=false")
    print("firmware_manual_load_implemented=false")
    print("runtime_loaded_config_implemented=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
