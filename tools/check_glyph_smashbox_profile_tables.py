#!/usr/bin/env python3
"""Read-only checker for Smash Box profile output table markdown."""

from __future__ import annotations

import re
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_smash_box_profile_output_tables_2026-05-27.md"
)

REQUIRED_TABLES = [
    "Default",
    "Mode default",
    "X1",
    "X2",
    "MX1",
    "MX2",
    "Y1",
    "Y2",
    "MY1",
    "MY2",
    "Tilt1",
    "Tilt2",
    "Tilt3",
    "MTilt1",
    "MTilt2",
    "MTilt3",
]

EXPECTED_FLIPPER = {
    "MY1": {
        1: (1, 184),
        2: (128, 184),
        3: (255, 184),
        4: (1, 172),
        5: (128, 172),
        6: (255, 172),
        7: (1, 72),
        8: (128, 72),
        9: (255, 72),
    },
    "MY2": {
        1: (1, 165),
        2: (128, 165),
        3: (255, 165),
        4: (1, 172),
        5: (128, 172),
        6: (255, 172),
        7: (1, 91),
        8: (128, 91),
        9: (255, 91),
    },
}

EXPECTED_TILT = {
    "Tilt1": {
        1: (187, 87),
        2: (128, 87),
        3: (69, 87),
        4: (187, 128),
        5: (128, 128),
        6: (69, 128),
        7: (187, 169),
        8: (128, 169),
        9: (69, 169),
    },
    "Tilt2": {
        1: (88, 79),
        2: (128, 79),
        3: (168, 79),
        4: (88, 128),
        5: (128, 128),
        6: (168, 128),
        7: (88, 177),
        8: (128, 177),
        9: (168, 177),
    },
    "Tilt3": {
        1: (75, 86),
        2: (128, 86),
        3: (181, 86),
        4: (75, 128),
        5: (128, 128),
        6: (181, 128),
        7: (75, 170),
        8: (128, 170),
        9: (181, 170),
    },
}

HEADER_RE = re.compile(r"^###\s+(?P<name>.+?)\s*$")
ROW_RE = re.compile(r"^\|\s*(?P<dir>[1-9])\s*\|\s*`?\((?P<x>\d+),\s*(?P<y>\d+)\)`?\s*\|\s*$")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_tables(text: str) -> dict[str, dict[int, tuple[int, int]]]:
    tables: dict[str, dict[int, tuple[int, int]]] = {}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        header = HEADER_RE.match(line)
        if header:
            current = header.group("name")
            tables.setdefault(current, {})
            continue

        if current is None:
            continue

        row = ROW_RE.match(line)
        if not row:
            continue

        direction = int(row.group("dir"))
        x = int(row.group("x"))
        y = int(row.group("y"))
        tables[current][direction] = (x, y)

    return tables


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOC
    failures: list[str] = []

    if not path.exists():
        failures.append(f"missing table doc: {rel(path)}")
        print(f"table_doc={rel(path)}")
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        failures.append(f"failed to read table doc: {exc}")
        print(f"table_doc={rel(path)}")
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    tables = parse_tables(text)

    for table_name in REQUIRED_TABLES:
        if table_name not in tables:
            failures.append(f"missing required table: {table_name}")
            continue
        directions = sorted(tables[table_name].keys())
        if directions != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            failures.append(
                f"table {table_name} must contain exactly directions 1..9; found {directions}"
            )
            continue
        for direction, (x, y) in tables[table_name].items():
            if not (0 <= x <= 255 and 0 <= y <= 255):
                failures.append(
                    f"table {table_name} direction {direction} has out-of-range byte ({x},{y})"
                )

    mode_default = tables.get("Mode default", {})
    if mode_default.get(5) != (128, 172):
        failures.append(
            "Mode default direction 5 must be (128,172)"
        )

    for table_name, expected_rows in EXPECTED_FLIPPER.items():
        actual_rows = tables.get(table_name, {})
        if actual_rows != expected_rows:
            failures.append(f"{table_name} flipper table mismatch")

    for table_name, expected_rows in EXPECTED_TILT.items():
        actual_rows = tables.get(table_name, {})
        if actual_rows != expected_rows:
            failures.append(f"{table_name} changed from expected table values")

    print(f"table_doc={rel(path)}")
    print(f"required_tables_count={len(REQUIRED_TABLES)}")
    print("mode_default_center_expected=(128,172)")
    print("my_flipper_tables_expected=MY1,MY2")
    print("tilt_tables_expected=Tilt1,Tilt2,Tilt3")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
