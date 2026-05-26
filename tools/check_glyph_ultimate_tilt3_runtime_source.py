#!/usr/bin/env python3
"""Read-only source checker for the native Ultimate Tilt3 runtime patch."""

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
    "outputs.triggerLDigital",
    "outputs.triggerRDigital",
)

FORBIDDEN_TIMING_TOKENS = (
    "previous",
    "last",
    "timer",
    "millis",
    "toggle",
    "sleep",
    "delay",
)

OVERFLOW_PATTERNS = (
    r"\buint8_t\s+\w+\s*=\s*128\s*[+-]",
    r"\(\s*uint8_t\s*\)",
    r"\b255\s*-",
    r"\bwrap\b",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def extract_patch_block(source: str) -> str:
    begin_count = source.count(BEGIN_MARKER)
    end_count = source.count(END_MARKER)
    if begin_count != 1:
        fail(f"expected exactly one Tilt patch begin marker, found {begin_count}")
    if end_count != 1:
        fail(f"expected exactly one Tilt patch end marker, found {end_count}")
    begin = source.find(BEGIN_MARKER)
    end = source.find(END_MARKER, begin)
    if begin < 0 or end < 0 or end < begin:
        fail("Tilt patch markers are missing or out of order")
    return source[begin : end + len(END_MARKER)]


def extract_before_patch(source: str) -> str:
    begin = source.find(BEGIN_MARKER)
    if begin < 0:
        fail(f"missing begin marker: {BEGIN_MARKER}")
    return source[:begin]


def require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags) is None:
        fail(f"missing source evidence: {label}")


def extract_dpad_layer_body(source: str) -> str:
    match = re.search(
        r"outputs\.dpadRight\s*=\s*0\s*;\s*(?P<body>.*?)outputs\.dpadUp\s*\|=",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        fail("unable to locate D-pad layer body")
    return match.group("body")


def extract_cstick_neutralization_body(source: str) -> str:
    match = re.search(
        r"//\s*Shut off C-stick when using D-Pad layer\.\s*"
        r"(?P<body>if\s*\([^)]*\)\s*\{[^}]*outputs\.rightStickX\s*=\s*128\s*;"
        r"[^}]*outputs\.rightStickY\s*=\s*128\s*;[^}]*\})",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        fail("unable to locate C-stick/right-stick neutralization body")
    return match.group("body")


def forbid_lt1_lt2_chord(text: str, label: str) -> None:
    compact = re.sub(r"\s+", "", text)
    if "inputs.lt1&&inputs.lt2" in compact:
        fail(f"{label} must not include LT1+LT2 chord")


def check_tilt3_active_gates_legacy_blocks(source: str, before_patch: str) -> None:
    active_match = re.search(
        r"const\s+bool\s+senscope_tilt3_active\s*=\s*"
        r"inputs\.lt3\s*\|\|\s*\(\s*inputs\.lt1\s*&&\s*inputs\.lt2\s*\)\s*;",
        source,
    )
    if active_match is None:
        fail("missing senscope_tilt3_active boolean with LT3 OR LT1+LT2")

    lt1_match = re.search(
        r"if\s*\(\s*inputs\.lt1\s*&&\s*!\s*senscope_tilt3_active\s*\)\s*\{",
        before_patch,
    )
    if lt1_match is None:
        fail("old LT1 prototype block must be gated by !senscope_tilt3_active")

    lt2_match = re.search(
        r"if\s*\(\s*inputs\.lt2\s*&&\s*!\s*senscope_tilt3_active\s*\)\s*\{",
        before_patch,
    )
    if lt2_match is None:
        fail("old LT2 prototype block must be gated by !senscope_tilt3_active")

    if not (active_match.start() < lt1_match.start() < lt2_match.start()):
        fail("senscope_tilt3_active must be computed before old LT1/LT2 prototype blocks")


def forbid_assignments(block: str) -> None:
    for field in FORBIDDEN_ASSIGNMENTS:
        if re.search(rf"\b{re.escape(field)}\s*=", block):
            fail(f"Tilt3 patch block must not assign {field}")


def forbid_timing_tokens(block: str) -> None:
    lower = block.lower()
    for token in FORBIDDEN_TIMING_TOKENS:
        if token in lower:
            fail(f"Tilt3 patch block must not include timing/toggle token: {token}")


def forbid_raw_physical_bypass(block: str) -> None:
    for token in ("inputs.rf", "inputs.lf", "inputs.rt", "inputs.mb"):
        if token in block:
            fail(f"Tilt3 patch block must not bypass remap with raw physical input token: {token}")


def forbid_overflow_patterns(block: str) -> None:
    for pattern in OVERFLOW_PATTERNS:
        if re.search(pattern, block, flags=re.IGNORECASE):
            fail(f"Tilt3 patch block contains obvious overflow/wrap pattern: {pattern}")


def main() -> int:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    block = extract_patch_block(source)
    before_patch = extract_before_patch(source)
    dpad_layer_body = extract_dpad_layer_body(source)
    cstick_neutralization_body = extract_cstick_neutralization_body(source)

    check_tilt3_active_gates_legacy_blocks(source, before_patch)
    require(r"if\s*\(\s*senscope_tilt3_active\s*\)", block, "Tilt3 priority branch uses shared active condition")
    require(r"else\s+if\s*\(\s*inputs\.lt1\s*\)", block, "Tilt1 branch after Tilt3")
    require(r"else\s+if\s*\(\s*inputs\.lt2\s*\)", block, "Tilt2 branch after Tilt3")
    require(r"outputs\.leftStickX\s*=\s*128\s*\+\s*\(\s*directions\.x\s*\*\s*53\s*\)", block, "Tilt3 X formula")
    require(r"outputs\.leftStickY\s*=\s*128\s*\+\s*\(\s*directions\.y\s*\*\s*42\s*\)", block, "Tilt3 Y formula")
    require(r"outputs\.leftStickX\s*=\s*128\s*-\s*\(\s*directions\.x\s*\*\s*59\s*\)", block, "Tilt1 X formula preserved")
    require(r"outputs\.leftStickY\s*=\s*128\s*\+\s*\(\s*directions\.y\s*\*\s*41\s*\)", block, "Tilt1 Y formula preserved")
    require(r"outputs\.leftStickX\s*=\s*128\s*\+\s*\(\s*directions\.x\s*\*\s*40\s*\)", block, "Tilt2 X formula preserved")
    require(r"outputs\.leftStickY\s*=\s*128\s*\+\s*\(\s*directions\.y\s*\*\s*49\s*\)", block, "Tilt2 Y formula preserved")
    require(r"if\s*\(\s*inputs\.nunchuk_c\s*\)", dpad_layer_body, "D-pad layer uses remaining nunchuk C condition")
    require(r"if\s*\(\s*inputs\.nunchuk_c\s*\)", cstick_neutralization_body, "C-stick/right-stick neutralization uses remaining nunchuk C condition")
    forbid_lt1_lt2_chord(dpad_layer_body, "D-pad layer condition")
    forbid_lt1_lt2_chord(cstick_neutralization_body, "C-stick/right-stick neutralization condition")

    forbid_raw_physical_bypass(block)
    forbid_assignments(block)
    forbid_timing_tokens(block)
    forbid_overflow_patterns(block)

    ranges = {
        "tilt1_x": (128 - 59, 128 + 59),
        "tilt1_y": (128 - 41, 128 + 41),
        "tilt2_x": (128 - 40, 128 + 40),
        "tilt2_y": (128 - 49, 128 + 49),
        "tilt3_x": (128 - 53, 128 + 53),
        "tilt3_y": (128 - 42, 128 + 42),
    }
    out_of_range = [label for label, (low, high) in ranges.items() if low < 0 or high > 255]
    if out_of_range:
        fail("Tilt formula ranges exceed byte range: " + ", ".join(out_of_range))

    print("glyph_ultimate_tilt3_runtime_source")
    print("status=PASS")
    print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
    print("senscope_tilt3_active=inputs.lt3 || (inputs.lt1 && inputs.lt2)")
    print("dedicated_tilt3_input=inputs.lt3")
    print("lt1_lt2_both_held_resolves_to_tilt3=true")
    print("legacy_lt1_block_gated_by_tilt3_active=true")
    print("legacy_lt2_block_gated_by_tilt3_active=true")
    print("lt1_lt2_dpad_layer_activation=false")
    print("lt1_lt2_cstick_neutralization=false")
    print("nunchuk_c_dpad_layer_preserved=true")
    print("left_stick_only=true")
    print("raw_physical_bypass=false")
    print("unsigned_overflow_dependency=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
