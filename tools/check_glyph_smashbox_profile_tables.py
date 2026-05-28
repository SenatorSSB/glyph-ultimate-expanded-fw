#!/usr/bin/env python3
"""Read-only checker for Glyph Smash Box profile output tables doc."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_smash_box_profile_output_tables_2026-05-27.md"
RUNTIME_DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md"

EXPECTED: dict[str, dict[str, tuple[int, int]]] = {
    "Default": {
        "1": (61, 51), "2": (128, 51), "3": (195, 51),
        "4": (61, 128), "5": (128, 128), "6": (195, 128),
        "7": (61, 205), "8": (128, 205), "9": (195, 205),
    },
    "Mode default": {
        "1": (14, 87), "2": (128, 87), "3": (242, 87),
        "4": (14, 169), "5": (128, 169), "6": (242, 169),
        "7": (14, 169), "8": (128, 169), "9": (242, 169),
    },
    "X1": {
        "1": (93, 51), "2": (128, 51), "3": (163, 51),
        "4": (93, 128), "5": (128, 128), "6": (163, 128),
        "7": (93, 205), "8": (128, 205), "9": (163, 205),
    },
    "X2": {
        "1": (82, 51), "2": (128, 51), "3": (174, 51),
        "4": (82, 128), "5": (128, 128), "6": (174, 128),
        "7": (82, 205), "8": (128, 205), "9": (174, 205),
    },
    "MX1": {
        "1": (78, 87), "2": (128, 87), "3": (178, 87),
        "4": (78, 169), "5": (128, 169), "6": (178, 169),
        "7": (78, 169), "8": (128, 169), "9": (178, 169),
    },
    "MX2": {
        "1": (65, 87), "2": (128, 87), "3": (191, 87),
        "4": (65, 169), "5": (128, 169), "6": (191, 169),
        "7": (65, 169), "8": (128, 169), "9": (191, 169),
    },
    "Y1": {
        "1": (61, 99), "2": (128, 99), "3": (195, 99),
        "4": (61, 128), "5": (128, 128), "6": (195, 128),
        "7": (61, 157), "8": (128, 157), "9": (195, 157),
    },
    "Y2": {
        "1": (61, 82), "2": (128, 82), "3": (195, 82),
        "4": (61, 128), "5": (128, 128), "6": (195, 128),
        "7": (61, 174), "8": (128, 174), "9": (195, 174),
    },
    "MY1": {
        "1": (14, 179), "2": (128, 179), "3": (242, 179),
        "4": (14, 169), "5": (128, 169), "6": (242, 169),
        "7": (14, 77), "8": (128, 77), "9": (242, 77),
    },
    "MY2": {
        "1": (1, 165), "2": (128, 165), "3": (255, 165),
        "4": (1, 172), "5": (128, 172), "6": (255, 172),
        "7": (1, 91), "8": (128, 91), "9": (255, 91),
    },
    "Tilt1": {
        "1": (187, 47), "2": (128, 47), "3": (69, 47),
        "4": (187, 128), "5": (128, 128), "6": (69, 128),
        "7": (187, 209), "8": (128, 209), "9": (69, 209),
    },
    "Tilt2": {
        "1": (88, 79), "2": (128, 79), "3": (168, 79),
        "4": (88, 128), "5": (128, 128), "6": (168, 128),
        "7": (88, 177), "8": (128, 177), "9": (168, 177),
    },
    "Tilt3": {
        "1": (75, 86), "2": (128, 86), "3": (181, 86),
        "4": (75, 128), "5": (128, 128), "6": (181, 128),
        "7": (75, 170), "8": (128, 170), "9": (181, 170),
    },
    "MTilt1": {
        "1": (169, 88), "2": (128, 88), "3": (87, 88),
        "4": (169, 169), "5": (128, 169), "6": (87, 169),
        "7": (169, 168), "8": (128, 168), "9": (87, 168),
    },
    "MTilt2": {
        "1": (96, 82), "2": (128, 82), "3": (160, 82),
        "4": (96, 169), "5": (128, 169), "6": (160, 169),
        "7": (96, 174), "8": (128, 174), "9": (160, 174),
    },
    "MTilt3": {
        "1": (96, 86), "2": (128, 86), "3": (160, 86),
        "4": (96, 169), "5": (128, 169), "6": (160, 169),
        "7": (96, 170), "8": (128, 170), "9": (160, 170),
    },
}


def fail(message: str) -> None:
    raise AssertionError(message)


def extract_table_block(text: str, table_name: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(table_name)}:\s*$\n^`(?P<line>[^`]+)`\s*$",
        flags=re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        fail(f"missing table block: {table_name}")
    return match.group("line")


def parse_table_line(line: str) -> dict[str, tuple[int, int]]:
    pairs = re.findall(r"([1-9])\s*=\s*\((\d+),\s*(\d+)\)", line)
    if len(pairs) != 9:
        fail(f"expected 9 direction entries, found {len(pairs)} in line: {line}")

    table: dict[str, tuple[int, int]] = {}
    for direction, x_str, y_str in pairs:
        x = int(x_str)
        y = int(y_str)
        if not (0 <= x <= 255 and 0 <= y <= 255):
            fail(f"out-of-range coordinate for direction {direction}: ({x}, {y})")
        table[direction] = (x, y)

    if sorted(table.keys(), key=int) != [str(value) for value in range(1, 10)]:
        fail("table directions must include exactly 1..9")

    return table


def main() -> int:
    if not DOC_PATH.exists():
        print(f"status=FAIL")
        print(f"failure=missing_doc:{DOC_PATH.relative_to(REPO_ROOT)}")
        return 1
    if not RUNTIME_DOC_PATH.exists():
        print("status=FAIL")
        print(f"failure=missing_runtime_doc:{RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
        return 1

    text = DOC_PATH.read_text(encoding="utf-8")
    runtime_doc_text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    failures: list[str] = []
    for table_name, expected_values in EXPECTED.items():
        try:
            line = extract_table_block(text, table_name)
            observed = parse_table_line(line)
            if observed != expected_values:
                failures.append(f"table_mismatch:{table_name}")
        except AssertionError as exc:
            failures.append(str(exc))

    # Historical table values should remain documented while runtime marks Y2/MY2 inactive.
    if re.search(r"Y2/MY2 runtime policy|historical table values retained", text, flags=re.IGNORECASE) is None:
        failures.append("doc_missing_y2_my2_historical_policy")
    if re.search(r"Y2/MY2.*scratched|scratched.*Y2/MY2", runtime_doc_text, flags=re.IGNORECASE) is None:
        failures.append("runtime_doc_missing_y2_my2_scratched_policy")

    if failures:
        print("status=FAIL")
        print(f"doc={DOC_PATH.relative_to(REPO_ROOT)}")
        print(f"runtime_doc={RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
        for failure in failures:
            print(f"failure={failure}")
        return 1

    print("status=PASS")
    print(f"doc={DOC_PATH.relative_to(REPO_ROOT)}")
    print(f"runtime_doc={RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    print(f"tables_validated={len(EXPECTED)}")
    print("directions_validated=1..9")
    print("y2_my2_table_values=historical_preserved")
    print("y2_my2_runtime_role=scratched_inactive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
