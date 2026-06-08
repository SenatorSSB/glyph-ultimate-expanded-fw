#!/usr/bin/env python3
"""Validate the minimal Phase 7A activation repair guardrails.

This checker is intentionally conservative. The selected repair strategy is
Option A: source/build-time validation only, with no firmware runtime behavior
change and no compiled payload header on this branch.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPAIR_DOC_PATH = REPO_ROOT / "docs" / "runtime_config" / "phase7a_runtime_config_activation_repair_minimal.md"
SIZE_REPORT_PATH = REPO_ROOT / "docs" / "runtime_config" / "phase7a_activation_repair_build_size_report.md"
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
PARSER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"
COMPILED_PAYLOAD_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayload.hpp"

EXPECTED_BRANCH = "phase7a-runtime-config-activation-repair-minimal"
EXPECTED_STATUS = "PHASE7A_REPAIR_MINIMAL_BUILD_ONLY_NO_RUNTIME_BEHAVIOR_CHANGE"
EXPECTED_FAILED_BRANCH = "phase7a-runtime-config-compiled-payload-activation"

ALLOWED_CHANGED_PREFIXES = (
    "docs/runtime_config/",
    "docs/calibration/INDEX.md",
    "tools/check_glyph_phase7a_activation_repair_minimal.py",
    "tools/run_glyph_next_runtime_change_readiness_checks.py",
)

FORBIDDEN_BRANCH_PATH_PATTERNS = (
    r"docs/calibration/.*phase7a.*hardware.*result.*(?:\.md|\.json)$",
    r"docs/calibration/fixtures/.*phase7a.*hardware.*result.*\.json$",
)

FORBIDDEN_RUNTIME_SYMBOLS = (
    "Persistence",
    "config.bin",
    "LittleFS",
    "EEPROM",
    "LoadConfig",
    "SaveConfig",
    "LoadRuntimeConfig",
    "SaveRuntimeConfig",
    "CMD_SET_RUNTIME_CONFIG",
    "CMD_GET_RUNTIME_CONFIG",
    "CMD_SET_RUNTIME",
    "CMD_GET_RUNTIME",
    "WebSerial",
    "runtime-loaded user payload",
    "boot external payload",
    "reboot_bootloader",
    "flash_uf2",
)

FORBIDDEN_SOURCE_PATTERNS = (
    r"\bconst\s+UltimateRuntimeConfigParser::ParseResult\s+\w+\s*=\s*UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload\s*\(",
    r"\bUltimateRuntimeConfigParser::ParseResult\s+\w+\s*=\s*UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload\s*\(",
    r"\bkPhase7ACompiledPayloadParseResult\b",
    r"\bResolveActiveRuntimeConfig\s*\(",
    r"UltimateRuntimeConfigCompiledPayload\.hpp",
)

REQUIRED_DOC_PHRASES = (
    EXPECTED_STATUS,
    "Option A",
    "build-time/source-level validation only",
    EXPECTED_FAILED_BRANCH,
    "must not merge",
    "no global non-`constexpr` parse result",
    "no parser call from hot runtime/output path",
    "no storage read/write dependency",
    "no WebSerial input/output path",
    "no device write/flash command path",
    "no flashing automation",
    "Exact Firmware Changes",
    "None.",
    "runtime behavior unchanged",
    "no runtime-loaded config activation",
    "not executed in this branch because this strategy is source-level only",
    "no hardware-result claim",
    "map_size_artifact_unavailable: true",
)


class Phase7AActivationRepairMinimalError(ValueError):
    """Raised when the minimal repair branch crosses a guardrail."""


def fail(message: str) -> None:
    raise Phase7AActivationRepairMinimalError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def git_lines(args: list[str], *, preserve_status_prefix: bool = False) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    if preserve_status_prefix:
        return [line for line in completed.stdout.splitlines() if line.strip()]
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def changed_paths() -> set[str]:
    paths = set(git_lines(["diff", "--name-only", "configurator...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status_prefix=True):
        path = status_line[3:].strip()
        if path:
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            paths.add(path)
    return paths


def validate_branch_scope(paths: set[str]) -> None:
    current_branch = git_lines(["branch", "--show-current"])
    if current_branch and current_branch[0] != EXPECTED_BRANCH:
        fail(f"checker must run on {EXPECTED_BRANCH}, got {current_branch[0]}")

    for path in sorted(paths):
        if not any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES):
            fail(f"minimal repair branch changed out-of-scope path: {path}")
        for pattern in FORBIDDEN_BRANCH_PATH_PATTERNS:
            if re.search(pattern, path):
                fail(f"minimal repair branch must not record a hardware result packet: {path}")


def implementation_without_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        lines.append(line)
    return "\n".join(lines)


def validate_source_guardrails() -> None:
    ultimate = read_required(ULTIMATE_PATH)
    parser = read_required(PARSER_PATH)
    combined = "\n".join(
        (
            implementation_without_comments(ultimate),
            implementation_without_comments(parser),
        )
    )

    if COMPILED_PAYLOAD_PATH.exists():
        fail("compiled payload header must not be present in the Option A minimal repair branch")
    if '#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"' in ultimate:
        fail("Ultimate.cpp must not include the failed compiled payload header")
    if "ParseUltimateRuntimeConfigPayload" in implementation_without_comments(ultimate):
        fail("Ultimate.cpp must not call ParseUltimateRuntimeConfigPayload")
    if "ResolveActiveRuntimeConfig" in implementation_without_comments(ultimate):
        fail("Ultimate.cpp must not add ResolveActiveRuntimeConfig")
    if "const RuntimeConfigView &runtime_config = ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)" not in ultimate:
        fail("Ultimate.cpp must keep direct configurator runtime-config selection")
    if "? kSourceOwnedCurrentBaselineRuntimeConfig" not in ultimate or ": kKnownGoodRuntimeConfig" not in ultimate:
        fail("Ultimate.cpp must keep deterministic known-good fallback ternary")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, combined, flags=re.MULTILINE):
            fail(f"source contains forbidden failed-branch risk pattern: {pattern}")

    for symbol in FORBIDDEN_RUNTIME_SYMBOLS:
        if symbol in combined:
            fail(f"source contains forbidden runtime/storage/write/flash symbol: {symbol}")


def validate_repair_doc() -> None:
    doc = read_required(REPAIR_DOC_PATH)
    for phrase in REQUIRED_DOC_PHRASES:
        require_phrase(doc, phrase, "repair doc")
    if "PASS" in doc:
        fail("repair doc must not record a hardware PASS")
    if re.search(r"\bnunchuk (?:validated|validation confirmed|hardware validated)\b", doc, flags=re.IGNORECASE):
        fail("repair doc must not claim nunchuk validation")


def validate_size_report() -> None:
    report = read_required(SIZE_REPORT_PATH)
    for phrase in (
        "BUILD_ONLY_SOURCE_VALIDATION_NO_BUILD_ARTIFACT",
        "map_size_artifact_unavailable",
        "source-level-only",
    ):
        require_phrase(report, phrase, "size report")


def main() -> int:
    paths = changed_paths()
    validate_branch_scope(paths)
    validate_source_guardrails()
    validate_repair_doc()
    validate_size_report()

    print("status=PASS")
    print(f"repair_doc={rel(REPAIR_DOC_PATH)}")
    print("selected_strategy=Option A")
    print("runtime_behavior_changed=false")
    print("firmware_source_changed=false")
    print("hardware_required=false")
    print("compiled_payload_header=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
