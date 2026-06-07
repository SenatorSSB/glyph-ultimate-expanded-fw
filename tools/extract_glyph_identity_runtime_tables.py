#!/usr/bin/env python3
"""Extract Glyph identity runtime stick tables from Ultimate.cpp.

This is a source-sync guardrail for the bounded Python behavior evaluator. It
does not compile firmware, generate artifacts, or validate hardware behavior.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
GENERATED_LIKE_TABLES_INCLUDE = '#include "modes/UltimateIdentityRuntimeTables.hpp"'
GENERATED_LIKE_TABLES_PATH = REPO_ROOT / "src" / "modes" / "UltimateIdentityRuntimeTables.hpp"
REQUIRED_GENERATED_LIKE_TABLES_CAVEATS = (
    "Generated-like identity runtime table constants.",
    "Source-owned firmware constants, not runtime-loaded config.",
    "Values are source-authored, not generated at runtime.",
    "Do not treat this as serial/device write behavior.",
    "Values must remain source-synced with the generated-config/tooling checks.",
)

TABLE_SYMBOL_TO_NAME: tuple[tuple[str, str], ...] = (
    ("kDefaultTable", "Default"),
    ("kModeDefaultTable", "ModeDefault"),
    ("kX1Table", "X1"),
    ("kX2Table", "X2"),
    ("kMX1Table", "MX1"),
    ("kMX2Table", "MX2"),
    ("kY1Table", "Y1"),
    ("kMY1Table", "MY1"),
    ("kLayerNormalXTable", "LayerNormalX"),
    ("kMLayerNormalXTable", "MLayerNormalX"),
    ("kLayerFlipperTable", "LayerFlipper"),
    ("kMLayerFlipperTable", "MLayerFlipper"),
    ("kY1Tilt1Table", "Y1Tilt1"),
    ("kMY1Tilt1Table", "MY1Tilt1"),
    ("kY1LayerFlipperTable", "Y1LayerFlipper"),
    ("kMY1LayerFlipperTable", "MY1LayerFlipper"),
    ("kY1LayerNormalXTable", "Y1LayerNormalX"),
    ("kMY1LayerNormalXTable", "MY1LayerNormalX"),
    ("kTilt1Table", "Tilt1"),
    ("kTilt2Table", "Tilt2"),
    ("kTilt3Table", "Tilt3"),
    ("kTilt1Minus41Table", "Tilt1Minus41"),
    ("kRT1RF4CustomTable", "RT1RF4Custom"),
    ("kMTilt1Table", "MTilt1"),
    ("kMTilt2Table", "MTilt2"),
    ("kMTilt3Table", "MTilt3"),
    ("kLt1LowMagnitudeTable", "Lt1LowMagnitude"),
)

EXPECTED_POINT_COUNT = 9

_TABLE_PATTERN = re.compile(
    r"constexpr\s+StickPoint\s+"
    r"(?P<symbol>k[A-Za-z0-9]+Table)"
    r"\s*\[\s*(?P<size>\d+)\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
_POINT_PATTERN = re.compile(r"\{\s*(?P<x>\d+)\s*,\s*(?P<y>\d+)\s*\}")


class TableExtractionError(ValueError):
    """Raised when source table extraction cannot be trusted."""


def required_table_symbols() -> tuple[str, ...]:
    return tuple(symbol for symbol, _name in TABLE_SYMBOL_TO_NAME)


def normalized_table_names() -> tuple[str, ...]:
    return tuple(name for _symbol, name in TABLE_SYMBOL_TO_NAME)


def source_symbol_by_normalized_name() -> dict[str, str]:
    return {name: symbol for symbol, name in TABLE_SYMBOL_TO_NAME}


def _relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _parse_table_points(symbol: str, declared_size: str, body: str) -> tuple[tuple[int, int], ...]:
    try:
        size = int(declared_size)
    except ValueError as exc:
        raise TableExtractionError(f"{symbol} has non-integer array size: {declared_size}") from exc

    if size != EXPECTED_POINT_COUNT:
        raise TableExtractionError(f"{symbol} declares {size} points, expected {EXPECTED_POINT_COUNT}")

    points: list[tuple[int, int]] = []
    for match in _POINT_PATTERN.finditer(body):
        x = int(match.group("x"))
        y = int(match.group("y"))
        if not 0 <= x <= 255 or not 0 <= y <= 255:
            raise TableExtractionError(f"{symbol} contains out-of-range point ({x}, {y})")
        points.append((x, y))

    remainder = _POINT_PATTERN.sub("", body)
    if re.sub(r"[\s,]", "", remainder):
        raise TableExtractionError(f"{symbol} contains malformed table body")

    if len(points) != EXPECTED_POINT_COUNT:
        raise TableExtractionError(f"{symbol} contains {len(points)} points, expected {EXPECTED_POINT_COUNT}")

    return tuple(points)


def extract_tables_from_source(source_text: str) -> dict[str, tuple[tuple[int, int], ...]]:
    """Return normalized table names mapped to parsed source points."""

    required = source_symbol_by_normalized_name()
    symbol_to_name = {symbol: name for symbol, name in TABLE_SYMBOL_TO_NAME}
    parsed_symbols: dict[str, tuple[tuple[int, int], ...]] = {}

    for match in _TABLE_PATTERN.finditer(source_text):
        symbol = match.group("symbol")
        if symbol not in symbol_to_name:
            continue
        if symbol in parsed_symbols:
            raise TableExtractionError(f"{symbol} appears more than once")
        parsed_symbols[symbol] = _parse_table_points(symbol, match.group("size"), match.group("body"))

    missing = [symbol for symbol in required.values() if symbol not in parsed_symbols]
    if missing:
        raise TableExtractionError("missing required source table(s): " + ", ".join(missing))

    return {name: parsed_symbols[symbol] for symbol, name in TABLE_SYMBOL_TO_NAME}


def _validate_generated_like_tables_caveats(include_text: str) -> None:
    for caveat in REQUIRED_GENERATED_LIKE_TABLES_CAVEATS:
        if caveat not in include_text:
            raise TableExtractionError(f"generated-like tables include missing caveat: {caveat}")


def load_source_text_with_generated_tables(path: Path = DEFAULT_SOURCE_PATH) -> str:
    source_text = path.read_text(encoding="utf-8")
    if path.resolve() != DEFAULT_SOURCE_PATH.resolve():
        return source_text

    include_count = source_text.count(GENERATED_LIKE_TABLES_INCLUDE)
    if include_count > 1:
        raise TableExtractionError(
            f"generated-like tables include appears {include_count} times in {_relative_path(path)}"
        )
    if include_count == 0:
        return source_text

    include_text = GENERATED_LIKE_TABLES_PATH.read_text(encoding="utf-8")
    _validate_generated_like_tables_caveats(include_text)
    return source_text.replace(GENERATED_LIKE_TABLES_INCLUDE, include_text, 1)


def load_source_tables(path: Path = DEFAULT_SOURCE_PATH) -> dict[str, tuple[tuple[int, int], ...]]:
    return extract_tables_from_source(load_source_text_with_generated_tables(path))


def build_json_payload(path: Path, tables: dict[str, tuple[tuple[int, int], ...]]) -> dict[str, object]:
    return {
        "schema_name": "glyph_identity_runtime_source_tables",
        "source_path": _relative_path(path),
        "tables": {name: [list(point) for point in tables[name]] for name in normalized_table_names()},
        "source_symbols": source_symbol_by_normalized_name(),
    }


def print_text_summary(path: Path, tables: dict[str, tuple[tuple[int, int], ...]]) -> None:
    print("glyph_identity_runtime_table_extractor")
    print("status=PASS")
    print(f"source_path={_relative_path(path)}")
    print(f"table_count={len(tables)}")
    for symbol, name in TABLE_SYMBOL_TO_NAME:
        print(f"- symbol={symbol} normalized_name={name} point_count={len(tables[name])}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print deterministic JSON instead of a text summary")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH, help="path to Ultimate.cpp")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    source_path = args.source

    try:
        tables = load_source_tables(source_path)
    except (OSError, TableExtractionError) as exc:
        print("glyph_identity_runtime_table_extractor")
        print("status=FAIL")
        print(f"source_path={_relative_path(source_path)}")
        print(f"error={exc}")
        return 1

    if args.json:
        print(json.dumps(build_json_payload(source_path, tables), indent=2, sort_keys=True))
    else:
        print_text_summary(source_path, tables)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
