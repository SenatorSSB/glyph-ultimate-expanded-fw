#!/usr/bin/env python3
"""Validate the Phase 7A bounded firmware parser scaffold."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PARSER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"

REQUIRED_PHRASES = (
    "Phase 7A compiled scaffold only.",
    "no storage; no device write; no WebSerial; no flashing automation.",
    "without mutating",
    "enum class ParseStatus",
    "ParseUltimateRuntimeConfigPayload",
)

FORBIDDEN_PATTERNS = (
    r"\bPersistence\b",
    r"\bLoadRuntimeConfig\b",
    r"\bSaveRuntimeConfig\b",
    r"\bCMD_SET_RUNTIME_CONFIG\b",
    r"\bCMD_GET_RUNTIME_CONFIG\b",
    r"\bWebSerial\b(?!; no WebSerial)",
    r"\bconfig\.bin\b",
    r"\bLittleFS\b",
    r"\bEEPROM\b",
    r"\bflash\b(?!ing automation)",
    r"\bwrite\b(?!; no device write|, writing storage)",
)


class FirmwareParserScaffoldError(ValueError):
    """Raised when the Phase 7A firmware parser scaffold crosses a boundary."""


def fail(message: str) -> None:
    raise FirmwareParserScaffoldError(message)


def main() -> int:
    if not PARSER_PATH.exists():
        fail("missing parser scaffold header")
    text = PARSER_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            fail(f"parser scaffold missing required phrase/symbol: {phrase}")
    implementation_text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, implementation_text, flags=re.IGNORECASE):
            fail(f"parser scaffold contains forbidden pattern: {pattern}")

    ultimate = ULTIMATE_PATH.read_text(encoding="utf-8")
    if '#include "modes/UltimateRuntimeConfigParser.hpp"' not in ultimate:
        fail("Ultimate.cpp must include parser header so the scaffold compiles")
    call_count = ultimate.count("ParseUltimateRuntimeConfigPayload")
    if call_count != 1:
        fail("Ultimate.cpp active source must validate exactly one compiled/test payload")
    if "ResolveActiveRuntimeConfig" not in ultimate:
        fail("Ultimate.cpp must isolate parser activation behind ResolveActiveRuntimeConfig")
    forbidden_ultimate_symbols = (
        "LoadRuntimeConfig",
        "SaveRuntimeConfig",
        "CMD_SET_RUNTIME_CONFIG",
        "CMD_GET_RUNTIME_CONFIG",
    )
    for symbol in forbidden_ultimate_symbols:
        if symbol in ultimate:
            fail(f"Ultimate.cpp contains forbidden runtime parser symbol: {symbol}")

    print("status=PASS")
    print(f"parser={PARSER_PATH.relative_to(REPO_ROOT)}")
    print("runtime_active=compiled_test_payload_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
