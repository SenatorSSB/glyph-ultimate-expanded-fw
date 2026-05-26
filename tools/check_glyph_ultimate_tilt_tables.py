#!/usr/bin/env python3
"""Read-only formula/table regression checker for Glyph Ultimate Tilt runtime."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_ultimate_tilt_domain_spec.json"
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
BEGIN_MARKER = "// Senscope Glyph Ultimate Tilt patch begin"
END_MARKER = "// Senscope Glyph Ultimate Tilt patch end"

DIRECTION_MAP = {
    "1": (-1, -1),
    "2": (0, -1),
    "3": (1, -1),
    "4": (-1, 0),
    "5": (0, 0),
    "6": (1, 0),
    "7": (-1, 1),
    "8": (0, 1),
    "9": (1, 1),
}


def _fail(message: str) -> None:
    raise AssertionError(message)


def _load_fixture() -> dict[str, object]:
    if not FIXTURE_PATH.exists():
        _fail(f"missing fixture: {FIXTURE_PATH}")
    try:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"invalid fixture JSON: {exc}")
    if not isinstance(payload, dict):
        _fail("fixture root must be an object")
    return payload


def _load_source() -> str:
    try:
        return SOURCE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        _fail(f"missing source file: {SOURCE_PATH}")
        raise exc


def _extract_patch_block(source: str) -> str:
    begin_count = source.count(BEGIN_MARKER)
    end_count = source.count(END_MARKER)
    if begin_count != 1 or end_count != 1:
        _fail(f"expected exactly one marked patch block, found begin={begin_count} end={end_count}")

    begin = source.find(BEGIN_MARKER)
    end = source.find(END_MARKER, begin)
    if begin == -1 or end == -1:
        _fail("missing marked patch block")
    return source[begin : end + len(END_MARKER)]


def _extract_macro(source: str, name: str) -> int:
    match = re.search(rf"#define\s+{re.escape(name)}\s+(\d+)", source)
    if match is None:
        _fail(f"missing macro: {name}")
    return int(match.group(1))


def _extract_formula_constants(block: str) -> dict[str, tuple[int, str, int, str]]:
    pattern = re.compile(
        r"if\s*\(\s*senscope_tilt3_active\s*\)\s*\{\s*"
        r"outputs\.leftStickX\s*=\s*(\d+)\s*([+-])\s*\(\s*directions\.x\s*\*\s*(\d+)\s*\)\s*;\s*"
        r"outputs\.leftStickY\s*=\s*(\d+)\s*([+-])\s*\(\s*directions\.y\s*\*\s*(\d+)\s*\)\s*;\s*"
        r"\}\s*else\s+if\s*\(\s*inputs\.lt1\s*\)\s*\{\s*"
        r"outputs\.leftStickX\s*=\s*(\d+)\s*([+-])\s*\(\s*directions\.x\s*\*\s*(\d+)\s*\)\s*;\s*"
        r"outputs\.leftStickY\s*=\s*(\d+)\s*([+-])\s*\(\s*directions\.y\s*\*\s*(\d+)\s*\)\s*;\s*"
        r"\}\s*else\s+if\s*\(\s*inputs\.lt2\s*\)\s*\{\s*"
        r"outputs\.leftStickX\s*=\s*(\d+)\s*([+-])\s*\(\s*directions\.x\s*\*\s*(\d+)\s*\)\s*;\s*"
        r"outputs\.leftStickY\s*=\s*(\d+)\s*([+-])\s*\(\s*directions\.y\s*\*\s*(\d+)\s*\)\s*;",
        flags=re.DOTALL,
    )
    match = pattern.search(block)
    if match is None:
        _fail("unable to parse Tilt1/Tilt2/Tilt3 formulas from marked patch block")

    groups = [int(value) if value.isdigit() else value for value in match.groups()]
    return {
        "tilt3": (groups[0], groups[1], groups[2], groups[4]),
        "tilt3_y": (groups[3], groups[4], groups[5], "y"),
        "tilt1": (groups[6], groups[7], groups[8], groups[10]),
        "tilt1_y": (groups[9], groups[10], groups[11], "y"),
        "tilt2": (groups[12], groups[13], groups[14], groups[16]),
        "tilt2_y": (groups[15], groups[16], groups[17], "y"),
    }


def _apply_axis(center: int, sign: str, direction: int, magnitude: int) -> int:
    if sign == "+":
        return center + (direction * magnitude)
    if sign == "-":
        return center - (direction * magnitude)
    _fail(f"unsupported sign token: {sign!r}")
    return 0


def _compute_tables(source: str, constants: dict[str, tuple[int, str, int, str]]) -> dict[str, dict[str, dict[str, int]]]:
    analog_min = _extract_macro(source, "ANALOG_STICK_MIN")
    analog_neutral = _extract_macro(source, "ANALOG_STICK_NEUTRAL")
    analog_max = _extract_macro(source, "ANALOG_STICK_MAX")

    tilt1_center_x, tilt1_x_sign, tilt1_x_mag, _ = constants["tilt1"]
    tilt2_center_x, tilt2_x_sign, tilt2_x_mag, _ = constants["tilt2"]
    tilt3_center_x, tilt3_x_sign, tilt3_x_mag, _ = constants["tilt3"]
    tilt1_center_y, tilt1_y_sign, tilt1_y_mag, _ = constants["tilt1_y"]
    tilt2_center_y, tilt2_y_sign, tilt2_y_mag, _ = constants["tilt2_y"]
    tilt3_center_y, tilt3_y_sign, tilt3_y_mag, _ = constants["tilt3_y"]

    if (tilt1_x_mag, tilt1_y_mag, tilt2_x_mag, tilt2_y_mag, tilt3_x_mag, tilt3_y_mag) != (59, 41, 40, 49, 53, 42):
        _fail(
            "runtime constants mismatch: expected Tilt1(59,41) Tilt2(40,49) Tilt3(53,42), got "
            f"Tilt1({tilt1_x_mag},{tilt1_y_mag}) Tilt2({tilt2_x_mag},{tilt2_y_mag}) "
            f"Tilt3({tilt3_x_mag},{tilt3_y_mag})"
        )
    if tilt1_x_sign != "-":
        _fail(f"Tilt1 X sign mismatch: expected '-', got {tilt1_x_sign!r}")
    if tilt1_y_sign != "+":
        _fail(f"Tilt1 Y sign mismatch: expected '+', got {tilt1_y_sign!r}")
    if tilt2_x_sign != "+":
        _fail(f"Tilt2 X sign mismatch: expected '+', got {tilt2_x_sign!r}")
    if tilt2_y_sign != "+":
        _fail(f"Tilt2 Y sign mismatch: expected '+', got {tilt2_y_sign!r}")
    if tilt3_x_sign != "+":
        _fail(f"Tilt3 X sign mismatch: expected '+', got {tilt3_x_sign!r}")
    if tilt3_y_sign != "+":
        _fail(f"Tilt3 Y sign mismatch: expected '+', got {tilt3_y_sign!r}")

    expected: dict[str, dict[str, dict[str, int]]] = {"base": {}, "tilt1": {}, "tilt2": {}, "tilt3": {}}

    for direction, (dx, dy) in DIRECTION_MAP.items():
        base_x = analog_min if dx == -1 else analog_max if dx == 1 else analog_neutral
        base_y = analog_min if dy == -1 else analog_max if dy == 1 else analog_neutral
        tilt1_x = _apply_axis(tilt1_center_x, tilt1_x_sign, dx, tilt1_x_mag)
        tilt1_y = _apply_axis(tilt1_center_y, tilt1_y_sign, dy, tilt1_y_mag)
        tilt2_x = _apply_axis(tilt2_center_x, tilt2_x_sign, dx, tilt2_x_mag)
        tilt2_y = _apply_axis(tilt2_center_y, tilt2_y_sign, dy, tilt2_y_mag)
        tilt3_x = _apply_axis(tilt3_center_x, tilt3_x_sign, dx, tilt3_x_mag)
        tilt3_y = _apply_axis(tilt3_center_y, tilt3_y_sign, dy, tilt3_y_mag)

        expected["base"][direction] = {"x": base_x, "y": base_y}
        expected["tilt1"][direction] = {"x": tilt1_x, "y": tilt1_y}
        expected["tilt2"][direction] = {"x": tilt2_x, "y": tilt2_y}
        expected["tilt3"][direction] = {"x": tilt3_x, "y": tilt3_y}

    return expected


def _normalize_table(table_name: str, table: object) -> dict[str, dict[str, int]]:
    if not isinstance(table, dict):
        _fail(f"{table_name} must be an object")

    normalized: dict[str, dict[str, int]] = {}
    for key in sorted(DIRECTION_MAP.keys(), key=int):
        point = table.get(key)
        if not isinstance(point, dict):
            _fail(f"{table_name}[{key}] must be an object")
        x = point.get("x")
        y = point.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            _fail(f"{table_name}[{key}] x/y must be integers")
        if not (0 <= x <= 255 and 0 <= y <= 255):
            _fail(f"{table_name}[{key}] out of byte range: ({x}, {y})")
        normalized[key] = {"x": x, "y": y}
    return normalized


def _assert_table_equal(name: str, observed: dict[str, dict[str, int]], expected: dict[str, dict[str, int]]) -> None:
    if observed != expected:
        _fail(f"{name} table mismatch")


def _assert_neutral(name: str, table: dict[str, dict[str, int]]) -> None:
    if table["5"] != {"x": 128, "y": 128}:
        _fail(f"{name}[5] must remain (128,128), got {table['5']}")


def run() -> None:
    fixture = _load_fixture()
    source = _load_source()
    block = _extract_patch_block(source)
    constants = _extract_formula_constants(block)
    computed_tables = _compute_tables(source, constants)

    tables = fixture.get("tables")
    if not isinstance(tables, dict):
        _fail("fixture missing tables object")

    observed_base = _normalize_table("tables.base", tables.get("base"))
    observed_tilt1 = _normalize_table("tables.tilt1", tables.get("tilt1"))
    observed_tilt2 = _normalize_table("tables.tilt2", tables.get("tilt2"))

    _assert_table_equal("base", observed_base, computed_tables["base"])
    _assert_table_equal("tilt1", observed_tilt1, computed_tables["tilt1"])
    _assert_table_equal("tilt2", observed_tilt2, computed_tables["tilt2"])
    _assert_table_equal(
        "tilt3",
        computed_tables["tilt3"],
        {
            "1": {"x": 75, "y": 86},
            "2": {"x": 128, "y": 86},
            "3": {"x": 181, "y": 86},
            "4": {"x": 75, "y": 128},
            "5": {"x": 128, "y": 128},
            "6": {"x": 181, "y": 128},
            "7": {"x": 75, "y": 170},
            "8": {"x": 128, "y": 170},
            "9": {"x": 181, "y": 170},
        },
    )

    _assert_neutral("base", observed_base)
    _assert_neutral("tilt1", observed_tilt1)
    _assert_neutral("tilt2", observed_tilt2)
    _assert_neutral("tilt3", computed_tables["tilt3"])


def main() -> None:
    try:
        run()
    except AssertionError as exc:
        print(f"glyph_ultimate_tilt_tables: FAIL {exc}")
        raise SystemExit(1)

    print("glyph_ultimate_tilt_tables: PASS tables=base,tilt1,tilt2,tilt3 directions=9 constants=59,41,40,49,53,42")


if __name__ == "__main__":
    main()
