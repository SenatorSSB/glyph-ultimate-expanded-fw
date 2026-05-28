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
    "kY2Table",
    "kMY1Table",
    "kMY2Table",
    "kTilt1Table",
    "kTilt2Table",
    "kTilt3Table",
    "kMTilt1Table",
    "kMTilt2Table",
    "kMTilt3Table",
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
    require(r"y2_active\s*=\s*inputs\.lt3\s*;", block, "Y2 anchor lt3")
    require(r"ls_to_dpad_active\s*=\s*inputs\.rf7\s*;", block, "LS->DPad anchor rf7")
    require(r"force_up_active\s*=\s*inputs\.rf6\s*;", source, "forced-Up anchor rf6")
    require(r"tilt1_pressed\s*=\s*inputs\.rf3\s*;", block, "Tilt1 anchor rf3")
    require(r"tilt2_pressed\s*=\s*inputs\.rf4\s*;", block, "Tilt2 anchor rf4")
    require(
        r"tilt3_effective\s*=\s*tilt1_pressed\s*&&\s*tilt2_pressed\s*;",
        block,
        "Tilt3 chord shape",
    )
    require(r"outputs\.buttonL\s*=\s*inputs\.lt1\s*;", source, "LT1 mapped to L")
    require(r"if\s*\(\s*ls_to_dpad_active\s*\)\s*\{[^}]*outputs\.leftStickX\s*=\s*center\.x\s*;[^}]*outputs\.leftStickY\s*=\s*center\.y\s*;", source, "LS->DPad neutralizes left stick")
    require(r"if\s*\(\s*ls_to_dpad_active\s*\)\s*\{[^}]*outputs\.dpadUp\s*\|=\s*effective_ls_up\s*;", source, "LS->DPad up uses effective Up")
    require(r"outputs\.leftStickLeft\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_left\s*;", source, "LS->DPad suppresses digital leftStickLeft")
    require(r"outputs\.leftStickRight\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_right\s*;", source, "LS->DPad suppresses digital leftStickRight")
    require(r"outputs\.leftStickDown\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_down\s*;", source, "LS->DPad suppresses digital leftStickDown")
    require(r"outputs\.leftStickUp\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_up\s*;", source, "LS->DPad suppresses digital leftStickUp")
    require(r"outputs\.buttonR\s*=\s*false\s*;", source, "RF3 no longer drives R")
    require(r"outputs\.modX\s*=\s*false\s*;", source, "LT1 no longer drives modX")
    if re.search(r"leftStickUp\s*=\s*inputs\.rf4\s*;", source):
        fail("RF4 must not directly drive Up")


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

        if "inputs.lt3 ||" in source:
            fail("legacy standalone LT3 Tilt3 expression must not remain")
    except (AssertionError, FileNotFoundError) as exc:
        print("glyph_native_ultimate_table_runtime_scope")
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("glyph_native_ultimate_table_runtime_scope")
    print("status=PASS")
    print(f"source={ULTIMATE_PATH.relative_to(REPO_ROOT)}")
    print("runtime_markers=present")
    print("tables_validated=16")
    print("ls_to_dpad_role=rf7")
    print("mode_role=rf8")
    print("lt3_role=y2")
    print("tilt3_role=rf3_and_rf4")
    print("l_role=lt1")
    print("table_samples=" + ";".join(table_summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
