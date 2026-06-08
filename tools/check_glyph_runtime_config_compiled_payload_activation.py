#!/usr/bin/env python3
"""Validate Phase 7A compiled/test runtime-config payload activation."""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HEADER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayload.hpp"
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
FIXTURE_PATH = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_valid_baseline_runtime_config_payload.bin"
DOC_PATH = REPO_ROOT / "docs" / "runtime_config" / "phase7a_runtime_config_compiled_payload_activation.md"
HARDWARE_PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_runtime_config_compiled_payload_activation_hardware_plan_2026-06-08.md"
)

FORBIDDEN_SYMBOLS = (
    "Persistence",
    "config.bin",
    "LittleFS",
    "LoadConfig",
    "SaveConfig",
    "LoadRuntimeConfig",
    "SaveRuntimeConfig",
    "CMD_SET_RUNTIME_CONFIG",
    "CMD_GET_RUNTIME_CONFIG",
    "CMD_SET_RUNTIME",
    "CMD_GET_RUNTIME",
    "WebSerial",
    "device write",
    "boot external payload",
    "runtime-loaded user payload",
)


class CompiledPayloadActivationError(ValueError):
    """Raised when compiled payload activation guardrails drift."""


def fail(message: str) -> None:
    raise CompiledPayloadActivationError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def require_file(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def extract_payload(header_text: str) -> bytes:
    match = re.search(
        r"constexpr uint8_t kPhase7ACompiledPayload\[kPhase7ACompiledPayloadSize\]\s*=\s*\{(?P<body>.*?)\};",
        header_text,
        flags=re.DOTALL,
    )
    if not match:
        fail("compiled payload byte array not found")
    values = []
    for token in re.findall(r"0x[0-9a-fA-F]{2}|\b\d+\b", match.group("body")):
        value = ast.literal_eval(token)
        if not 0 <= value <= 255:
            fail(f"compiled payload byte outside range: {token}")
        values.append(value)
    return bytes(values)


def require_phrases(text: str, source: Path, phrases: tuple[str, ...]) -> None:
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        fail(f"{rel(source)} missing required phrases: " + ", ".join(missing))


def check_forbidden_runtime_symbols(text: str, source: Path) -> None:
    implementation_text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))
    for symbol in FORBIDDEN_SYMBOLS:
        if re.search(re.escape(symbol), implementation_text, flags=re.IGNORECASE):
            fail(f"{rel(source)} contains forbidden runtime-config activation symbol: {symbol}")


def main() -> int:
    header = require_file(HEADER_PATH)
    ultimate = require_file(ULTIMATE_PATH)
    doc = require_file(DOC_PATH)
    hardware_plan = require_file(HARDWARE_PLAN_PATH)
    if not FIXTURE_PATH.exists():
        fail(f"missing committed payload fixture: {rel(FIXTURE_PATH)}")

    payload = extract_payload(header)
    fixture = FIXTURE_PATH.read_bytes()
    if payload != fixture:
        fail("compiled payload header bytes must match committed Phase 7A valid baseline fixture")
    payload_sha = hashlib.sha256(payload).hexdigest()
    if payload_sha not in header:
        fail("compiled payload header must include fixture SHA-256")
    if f"kPhase7ACompiledPayloadSize = {len(fixture)}" not in header:
        fail("compiled payload header size must match fixture length")

    require_phrases(
        header,
        HEADER_PATH,
        (
            "source-owned test payload only",
            "not runtime-loaded user config",
            "not storage",
            "not device write",
            "not WebSerial",
            "not flashing automation",
        ),
    )
    require_phrases(
        ultimate,
        ULTIMATE_PATH,
        (
            '#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"',
            "ResolveActiveRuntimeConfig",
            "ParseUltimateRuntimeConfigPayload",
            "ParseStatus::Ok",
            "kSourceOwnedCurrentBaselineRuntimeConfig",
            "kKnownGoodRuntimeConfig",
        ),
    )
    if ultimate.count("ParseUltimateRuntimeConfigPayload") != 1:
        fail("Ultimate.cpp must parse the compiled payload exactly once in the activation boundary")
    if "return kKnownGoodRuntimeConfig;" not in ultimate:
        fail("Ultimate.cpp must keep deterministic known-good fallback")
    if "LookupRuntimeStickPoint(runtime_config" not in ultimate or "ApplyTableAnalogOutput(runtime_config" not in ultimate:
        fail("Ultimate.cpp must route active analog lookups through the resolved runtime config")

    check_forbidden_runtime_symbols(header, HEADER_PATH)
    check_forbidden_runtime_symbols(ultimate, ULTIMATE_PATH)

    require_phrases(
        doc,
        DOC_PATH,
        (
            "PHASE7A_COMPILED_PAYLOAD_RUNTIME_ACTIVE_PENDING_HARDWARE_RESULT",
            "validation-gated source-equivalent activation",
            "Payload-backed table lookup is deferred",
            "Runtime-loaded config is not implemented",
            "Runtime-config storage is not implemented",
            "Device write / WebSerial is not implemented",
            "Firmware flashing automation is not implemented",
            "No hardware result is recorded",
            "Nunchuk remains NOT_TESTED",
        ),
    )
    require_phrases(
        hardware_plan,
        HARDWARE_PLAN_PATH,
        (
            "BOOT-001",
            "BASELINE-001",
            "PARSER-001",
            "FALLBACK-001",
            "MODIFIERS-001",
            "SPECIAL-001",
            "OVERRIDE-001",
            "CSTICK-001",
            "NO-STORAGE-001",
            "NO-WRITE-001",
            "NO-FLASH-001",
            "PROFILE-REG-001",
            "NUNCHUK-001",
            "NOT_TESTED",
        ),
    )
    if "PASS" in hardware_plan or "hardware result" in hardware_plan.lower() and "not a hardware result" not in hardware_plan.lower():
        fail("hardware plan must remain a NOT_TESTED plan, not a result")

    print("status=PASS")
    print(f"compiled_payload={rel(HEADER_PATH)}")
    print(f"payload_sha256={payload_sha}")
    print("runtime_activation=validation_gated_source_equivalent")
    print("payload_backed_lookup=deferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
