#!/usr/bin/env python3
"""Read-only source checker for the native Ultimate Tilt runtime patch."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
BEGIN_MARKER = "// Senscope Glyph Ultimate Tilt patch begin"
END_MARKER = "// Senscope Glyph Ultimate Tilt patch end"

FORBIDDEN_ANALOG_ASSIGNMENTS = (
    "outputs.rightStickX",
    "outputs.rightStickY",
    "outputs.triggerLAnalog",
    "outputs.triggerRAnalog",
)

FORBIDDEN_DIGITAL_ASSIGNMENTS = (
    "outputs.a",
    "outputs.b",
    "outputs.x",
    "outputs.y",
    "outputs.buttonL",
    "outputs.buttonR",
    "outputs.triggerLDigital",
    "outputs.triggerRDigital",
    "outputs.start",
    "outputs.select",
    "outputs.home",
    "outputs.capture",
    "outputs.leftStickClick",
    "outputs.rightStickClick",
    "outputs.dpadUp",
    "outputs.dpadDown",
    "outputs.dpadLeft",
    "outputs.dpadRight",
    "outputs.leftStickLeft",
    "outputs.leftStickRight",
    "outputs.leftStickDown",
    "outputs.leftStickUp",
)

FORBIDDEN_TIMING_TOKENS = (
    "static",
    "previous",
    "last",
    "timer",
    "millis",
    "toggle",
    "sleep",
    "delay",
)


def _fail(message: str) -> None:
    raise AssertionError(message)


def _extract_patch_block(source: str) -> str:
    begin_count = source.count(BEGIN_MARKER)
    end_count = source.count(END_MARKER)
    if begin_count != 1:
        _fail(f"expected exactly one begin marker, found {begin_count}")
    if end_count != 1:
        _fail(f"expected exactly one end marker, found {end_count}")

    begin = source.find(BEGIN_MARKER)
    end = source.find(END_MARKER, begin)
    if begin == -1:
        _fail(f"missing begin marker: {BEGIN_MARKER}")
    if end == -1:
        _fail(f"missing end marker: {END_MARKER}")
    if end < begin:
        _fail("end marker appears before begin marker")

    return source[begin : end + len(END_MARKER)]


def _require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags) is None:
        _fail(f"missing evidence: {label}")


def _forbid_assignments(fields: tuple[str, ...], block: str) -> None:
    for field in fields:
        if re.search(rf"\b{re.escape(field)}\s*=", block):
            _fail(f"Tilt patch block must not assign {field}")


def _forbid_tokens(tokens: tuple[str, ...], block: str) -> None:
    lower_block = block.lower()
    for token in tokens:
        if token.lower() in lower_block:
            _fail(f"Tilt patch block must not include timing/toggle token: {token}")


def main() -> None:
    try:
        source = SOURCE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"missing source file: {SOURCE_PATH}") from exc

    block = _extract_patch_block(source)

    _require(r"\binputs\.lt1\b", block, "inputs.lt1")
    _require(r"\binputs\.lt2\b", block, "inputs.lt2")
    _require(r"\b59\b", block, "Tilt1 X magnitude 59")
    _require(r"\b41\b", block, "Tilt1 Y magnitude 41")
    _require(r"\b40\b", block, "Tilt2 X magnitude 40")
    _require(r"\b49\b", block, "Tilt2 Y magnitude 49")
    _require(r"post-remap|logical", block, "post-remap/logical wording", flags=re.IGNORECASE)
    _require(r"RF3/RF4|RF3|RF4", block, "physical RF3/RF4 mapping comment")
    _require(r"overflow|flipper", block, "overflow/flipper safety comment", flags=re.IGNORECASE)
    _require(r"outputs\.leftStickX\s*=", block, "leftStickX assignment")
    _require(r"outputs\.leftStickY\s*=", block, "leftStickY assignment")
    _require(r"inputs\.lt1\s*&&\s*!inputs\.lt2", block, "Tilt1 exclusive activation")
    _require(r"inputs\.lt2\s*&&\s*!inputs\.lt1", block, "Tilt2 exclusive activation")

    if "inputs.rf3" in block or "inputs.rf4" in block:
        _fail("Tilt patch block must not bypass remap with inputs.rf3/inputs.rf4")

    _forbid_assignments(FORBIDDEN_ANALOG_ASSIGNMENTS, block)
    _forbid_assignments(FORBIDDEN_DIGITAL_ASSIGNMENTS, block)
    _forbid_tokens(FORBIDDEN_TIMING_TOKENS, block)

    print(
        "glyph_ultimate_tilt_runtime_source: PASS "
        "patch_block_count=1 inputs=lt1/lt2 constants=59,41,40,49 "
        "left_stick_only=true raw_rf3_rf4_bypass=false no_timing_tokens=true"
    )


if __name__ == "__main__":
    main()
