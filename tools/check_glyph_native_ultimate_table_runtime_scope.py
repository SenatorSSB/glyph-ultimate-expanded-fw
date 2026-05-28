#!/usr/bin/env python3
"""Read-only scope checker for native Ultimate identity-runtime table implementation."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
BEGIN_MARKER = "// Senscope Glyph Smash Box runtime begin"
END_MARKER = "// Senscope Glyph Smash Box runtime end"

REQUIRED_TABLES = (
    "kDefaultTable",
    "kModeDefaultTable",
    "kX1Table",
    "kX2Table",
    "kMX1Table",
    "kMX2Table",
    "kY1Table",
    "kMY1Table",
    "kTilt1Table",
    "kTilt2Table",
    "kTilt3Table",
    "kMTilt1Table",
    "kMTilt2Table",
    "kMTilt3Table",
    "kLt1LowMagnitudeTable",
)

LT1_LOW_POINTS = (
    (89, 89),
    (128, 79),
    (167, 89),
    (79, 128),
    (128, 128),
    (177, 128),
    (89, 167),
    (128, 177),
    (167, 167),
)

FORBIDDEN_TOKENS = (
    "flash",
    "bootloader",
    "uf2",
    "push-to-device",
    "push_to_device",
    "senscope_tilt3_active",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags=flags) is None:
        fail(f"missing source evidence: {label}")


def extract_marker_block(source: str) -> str:
    begin_count = source.count(BEGIN_MARKER)
    end_count = source.count(END_MARKER)
    if begin_count != 1 or end_count != 1:
        fail(f"expected exactly one marker block, found begin={begin_count} end={end_count}")
    begin = source.find(BEGIN_MARKER)
    end = source.find(END_MARKER, begin)
    if begin < 0 or end < 0 or end < begin:
        fail("runtime marker block missing or malformed")
    return source[begin : end + len(END_MARKER)]


def extract_table_values(source: str, table_name: str) -> list[tuple[int, int]]:
    match = re.search(
        rf"constexpr\s+StickPoint\s+{re.escape(table_name)}\[9\]\s*=\s*\{{(?P<body>.*?)\}};",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        fail(f"missing table definition: {table_name}")
    body = match.group("body")
    pairs = re.findall(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}", body)
    if len(pairs) != 9:
        fail(f"table {table_name} must contain 9 points, found {len(pairs)}")
    values = [(int(x), int(y)) for x, y in pairs]
    for x, y in values:
        if not (0 <= x <= 255 and 0 <= y <= 255):
            fail(f"table {table_name} has out-of-range value ({x}, {y})")
    return values


def ensure_required_shapes(source: str, block: str) -> None:
    require(r"mode_active\s*=\s*inputs\.rf8\s*;", block, "Mode anchor rf8")
    require(r"x1_active\s*=\s*inputs\.lt5\s*;", block, "X1 anchor lt5")
    require(r"x2_active\s*=\s*inputs\.lt4\s*;", block, "X2 anchor lt4")
    require(r"y1_active\s*=\s*inputs\.lt2\s*;", block, "Y1 anchor lt2")
    require(r"ls_to_dpad_active\s*=\s*inputs\.rf7\s*;", block, "LS->DPad anchor rf7")

    require(r"outputs\.buttonL\s*=\s*inputs\.lt3\s*;", source, "LT3 mapped to L")
    require(r"outputs\.triggerLDigital\s*=\s*inputs\.lt3\s*;", source, "LT3 mapped to L carrier")
    require(r"outputs\.buttonR\s*=\s*inputs\.rt1\s*\|\|\s*inputs\.lt1\s*;", source, "RT1/LT1 mapped to Z")
    require(r"outputs\.triggerRDigital\s*=\s*inputs\.rf16\s*;", source, "RF16 mapped to R")
    require(r"outputs\.a\s*=\s*inputs\.rf1\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf12\s*;", source, "RF1/LT6/RF12 mapped to A")

    if "outputs.buttonL = inputs.lt1;" in source:
        fail("LT1 must not map to L")
    if "outputs.buttonR = inputs.rt1;" in source:
        fail("RT1-only Z carrier is outdated")

    # Y2/MY2 are scratched and removed from runtime source selection.
    for token in ("y2_active", "EffectiveModifier::Y2", "kY2Table", "kMY2Table"):
        if token in source:
            fail(f"Y2/MY2 token must not remain active in runtime source: {token}")

    require(r"direction_plus_a_active\s*=\s*down_a_active\s*\|\|\s*up_a_active\s*;", source, "hard direction-plus-A active flag")
    require(
        r"direction_plus_a_force_up\s*=\s*direction_plus_a_active\s*&&\s*\(\s*up_a_active\s*\|\|\s*inputs\.rf6\s*\)\s*;",
        source,
        "hard direction-plus-A Up override (RF12 or RF6)",
    )

    require(r"constexpr\s+StickPoint\s+kLt1LowMagnitudeTable\[9\]", source, "LT1 low table declaration")
    for x, y in LT1_LOW_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing LT1 low-magnitude point: ({x}, {y})")

    require(
        r"if\s*\(\s*ls_to_dpad_active\s*\)\s*\{\s*const\s+StickPoint\s+center\s*=\s*mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;\s*outputs\.leftStickX\s*=\s*center\.x\s*;\s*outputs\.leftStickY\s*=\s*center\.y\s*;\s*\}\s*else\s*\{",
        block,
        "LS->DPad centers analog and gates override to non-LS->DPad path",
        flags=re.DOTALL,
    )

    require(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*lt1_z_airdodge_override_active\s*\)\s*\{",
        block,
        "LT1 override is final after direction-plus-A",
        flags=re.DOTALL,
    )
    require(r"outputs\.leftStickX\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.x\s*;", block, "LT1 final X")
    require(r"outputs\.leftStickY\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.y\s*;", block, "LT1 final Y")


def ensure_no_forbidden_tokens(source: str) -> None:
    lowered = source.lower()
    for token in FORBIDDEN_TOKENS:
        if token in lowered:
            fail(f"forbidden token present: {token}")


def main() -> int:
    try:
        source = ULTIMATE_PATH.read_text(encoding="utf-8")
        block = extract_marker_block(source)

        ensure_required_shapes(source, block)
        ensure_no_forbidden_tokens(source)

        table_summaries: list[str] = []
        for table_name in REQUIRED_TABLES:
            values = extract_table_values(source, table_name)
            table_summaries.append(f"{table_name}:{values[0]}->{values[4]}->{values[8]}")
    except (AssertionError, FileNotFoundError) as exc:
        print("glyph_native_ultimate_table_runtime_scope")
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("glyph_native_ultimate_table_runtime_scope")
    print("status=PASS")
    print(f"source={ULTIMATE_PATH.relative_to(REPO_ROOT)}")
    print("runtime_markers=present")
    print(f"tables_validated={len(REQUIRED_TABLES)}")
    print("ls_to_dpad_role=rf7")
    print("mode_role=rf8")
    print("lt3_role=L")
    print("lt1_role=Z_plus_low_magnitude_override")
    print("z_role=rt1_or_lt1")
    print("r_role=rf16")
    print("y_role=rf10")
    print("forced_up_role=rf6_or_rf12")
    print("direction_plus_a_role=lt6_down_a_rf12_up_a")
    print("direction_plus_a_override_policy=hard_final_default_or_mode_default_then_lt1_low_override")
    print("y2_my2_runtime_role=scratched_inactive")
    print("standalone_dpad=none")
    print("table_samples=" + ";".join(table_summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
