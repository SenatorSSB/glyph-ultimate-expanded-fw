#!/usr/bin/env python3
"""Read-only source checker for the native Ultimate Tilt runtime patch."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
BEGIN_MARKER = "// Senscope Glyph Ultimate Tilt patch begin"
END_MARKER = "// Senscope Glyph Ultimate Tilt patch end"
FORBIDDEN_ASSIGNMENTS = (
    "outputs.rightStickX",
    "outputs.rightStickY",
    "outputs.triggerLAnalog",
    "outputs.triggerRAnalog",
)


def _fail(message: str) -> None:
    raise AssertionError(message)


def _extract_patch_block(source: str) -> str:
    begin = source.find(BEGIN_MARKER)
    if begin == -1:
        _fail(f"missing begin marker: {BEGIN_MARKER}")
    end = source.find(END_MARKER, begin)
    if end == -1:
        _fail(f"missing end marker: {END_MARKER}")
    block = source[begin : end + len(END_MARKER)]
    if source.find(BEGIN_MARKER, begin + 1) != -1:
        _fail("multiple Tilt patch begin markers found")
    if source.find(END_MARKER, end + 1) != -1:
        _fail("multiple Tilt patch end markers found")
    return block


def _require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags) is None:
        _fail(f"missing evidence: {label}")


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

    for field in FORBIDDEN_ASSIGNMENTS:
        if re.search(rf"\b{re.escape(field)}\s*=", block):
            _fail(f"Tilt patch block must not assign {field}")

    print(
        "glyph_ultimate_tilt_runtime_source: PASS "
        "inputs=lt1/lt2 constants=59,41,40,49 left_stick_only=true "
        "raw_rf3_rf4_bypass=false"
    )


if __name__ == "__main__":
    main()
