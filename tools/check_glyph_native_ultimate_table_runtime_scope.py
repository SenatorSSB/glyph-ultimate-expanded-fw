#!/usr/bin/env python3
"""Read-only source-shape checker for future native Ultimate table runtime scope.

This checker guards the current source shape before any arbitrary table runtime
patch exists. It does not require table runtime markers to be present yet.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
BEGIN_MARKER = "// Senscope Glyph Ultimate Tilt patch begin"
END_MARKER = "// Senscope Glyph Ultimate Tilt patch end"
TABLE_MARKER_PATTERNS = (
    "Native Ultimate table",
    "native ultimate table",
    "glyph_native_ultimate_table",
    "UltimateTable",
)
PUSH_FLASH_PATTERNS = (
    r"\bflash\b",
    r"\bbootloader\b",
    r"\buf2\b",
    r"push-to-device",
    r"push_to_device",
)
FORBIDDEN_PATCH_ASSIGNMENTS = (
    "outputs.rightStickX",
    "outputs.rightStickY",
    "outputs.triggerLAnalog",
    "outputs.triggerRAnalog",
    "outputs.triggerLDigital",
    "outputs.triggerRDigital",
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


def require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags) is None:
        fail(f"missing source evidence: {label}")


def forbid_patch_assignments(block: str) -> None:
    for field in FORBIDDEN_PATCH_ASSIGNMENTS:
        if re.search(rf"\b{re.escape(field)}\s*=", block):
            fail(f"Tilt patch block must not assign {field}")


def check_no_push_flashing(source: str) -> list[str]:
    matches: list[str] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        for pattern in PUSH_FLASH_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                matches.append(f"{ULTIMATE_PATH.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}")
    return matches


def formula_value_bounds() -> dict[str, tuple[int, int]]:
    # Current formulas use directions.x/y in {-1, 0, 1}. These ranges confirm
    # the resulting byte values stay within [0, 255] without overflow tricks.
    return {
        "tilt1_x": (128 - 59, 128 + 59),
        "tilt1_y": (128 - 41, 128 + 41),
        "tilt2_x": (128 - 40, 128 + 40),
        "tilt2_y": (128 - 49, 128 + 49),
    }


def main() -> int:
    source = ULTIMATE_PATH.read_text(encoding="utf-8")
    block = extract_patch_block(source)

    require(r"inputs\.lt1\s*&&\s*!inputs\.lt2", block, "lt1 exclusive branch")
    require(r"inputs\.lt2\s*&&\s*!inputs\.lt1", block, "lt2 exclusive branch")
    require(r"outputs\.leftStickX\s*=\s*128\s*-\s*\(directions\.x\s*\*\s*59\)", block, "Tilt1 leftStickX formula")
    require(r"outputs\.leftStickY\s*=\s*128\s*\+\s*\(directions\.y\s*\*\s*41\)", block, "Tilt1 leftStickY formula")
    require(r"outputs\.leftStickX\s*=\s*128\s*\+\s*\(directions\.x\s*\*\s*40\)", block, "Tilt2 leftStickX formula")
    require(r"outputs\.leftStickY\s*=\s*128\s*\+\s*\(directions\.y\s*\*\s*49\)", block, "Tilt2 leftStickY formula")
    forbid_patch_assignments(block)

    push_flash_matches = check_no_push_flashing(source)
    if push_flash_matches:
        fail("push/flashing terms found in checked runtime file: " + "; ".join(push_flash_matches))

    bounds = formula_value_bounds()
    out_of_bounds = [label for label, (low, high) in bounds.items() if low < 0 or high > 255]
    if out_of_bounds:
        fail("Tilt/Tilt2 formula ranges exceed byte range: " + ", ".join(out_of_bounds))

    table_markers = [marker for marker in TABLE_MARKER_PATTERNS if marker in source]

    print("glyph_native_ultimate_table_runtime_scope")
    print("status=PASS")
    print(f"source={ULTIMATE_PATH.relative_to(REPO_ROOT)}")
    print("tilt_patch_markers=present")
    print("push_flashing_code_in_checked_files=absent")
    print("tilt_tilt2_formulas_byte_safe=true")
    print(f"formula_ranges={bounds}")
    print(f"table_runtime_markers={'present:' + ','.join(table_markers) if table_markers else 'absent'}")
    print("lt1_exclusive=inputs.lt1 && !inputs.lt2")
    print("lt2_exclusive=inputs.lt2 && !inputs.lt1")
    print("right_stick_or_trigger_assignments_inside_tilt_patch=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
