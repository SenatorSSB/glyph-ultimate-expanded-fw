#!/usr/bin/env python3
"""Read-only helper to list discovered Glyph BTN_* symbols from known sources."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = [
    REPO_ROOT / ".pio" / "libdeps" / "glyph_mk6" / "HayBox-proto" / "config.proto",
    REPO_ROOT / "config" / "glyph" / "common" / "include" / "glyph_overrides.hpp",
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "GlyphUserProfilesUlt-filled.json",
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "GlyphUltFilled2.json",
]

BUTTON_PATTERN = re.compile(r"\bBTN_(?:LF|LT|RF|RT|MB)\d+\b|\bBTN_UNSPECIFIED\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List BTN_* symbols discovered from known Glyph source/config files.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        type=Path,
        help="Optional file list override. Defaults to known proto/source/fixture files.",
    )
    return parser.parse_args()


def _symbol_sort_key(symbol: str) -> tuple[int, str, int]:
    if symbol == "BTN_UNSPECIFIED":
        return (0, "UNSPECIFIED", 0)
    match = re.fullmatch(r"BTN_([A-Z]+)(\d+)", symbol)
    if not match:
        return (99, symbol, 0)
    group, number_text = match.groups()
    return (1, group, int(number_text))


def main() -> None:
    args = parse_args()
    sources = args.files if args.files else DEFAULT_SOURCES

    discovered: set[str] = set()
    scanned = 0

    for source in sources:
        path = source if source.is_absolute() else REPO_ROOT / source
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        discovered.update(BUTTON_PATTERN.findall(text))
        scanned += 1

    print(f"scanned_files={scanned}")
    print(f"symbols={len(discovered)}")
    for symbol in sorted(discovered, key=_symbol_sort_key):
        print(symbol)


if __name__ == "__main__":
    main()
