#!/usr/bin/env python3
"""Patch source-owned StickPoint table contents as an offline text artifact.

This generator reads the current source-owned table file and a replacement JSON
fixture, then emits patched UltimateIdentityRuntimeTables.hpp text. It does not
modify active source by default; callers must pass an explicit output path or
read stdout.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_VERSION = 1
EXPECTED_REPLACEMENT_KIND = "source_owned_table_content_replacement"
EXPECTED_TARGET_FILE = "src/modes/UltimateIdentityRuntimeTables.hpp"
EXPECTED_TABLE_COUNT = 27
EXPECTED_POINTS_PER_TABLE = 9
EXPECTED_AXES_PER_POINT = 2

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_TABLES = REPO_ROOT / EXPECTED_TARGET_FILE
GENERATED_OUTPUTS_DIR = REPO_ROOT / "docs/runtime_config/fixtures/generated_outputs"

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "replacement_kind",
    "target_file",
    "table_shape",
    "tables",
}
REQUIRED_SHAPE_KEYS = {"table_count", "points_per_table", "axes_per_point"}
REQUIRED_TABLE_KEYS = {"table_symbol", "points"}
REQUIRED_POINT_KEYS = {"x", "y"}

TABLE_RE = re.compile(
    r"constexpr\s+StickPoint\s+(?P<symbol>k[A-Za-z0-9_]+Table)\s*\[\s*9\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
POINT_RE = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")


class SourceOwnedTableReplacementError(ValueError):
    """Raised when input or generated output violates the replacement contract."""


@dataclass(frozen=True)
class TableBlock:
    symbol: str
    body_start: int
    body_end: int
    points: tuple[tuple[int, int], ...]


def fail(message: str) -> None:
    raise SourceOwnedTableReplacementError(message)


def reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            fail(f"duplicate JSON key: {key}")
        values[key] = value
    return values


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail("replacement input must be a JSON object")
    return payload


def require_keys(label: str, value: dict[str, Any], required: set[str]) -> None:
    missing = sorted(required - set(value))
    if missing:
        fail(f"{label} missing required keys: {', '.join(missing)}")


def require_int(label: str, value: Any, *, minimum: int | None = None, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        fail(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        fail(f"{label} must be >= {minimum}")
    if maximum is not None and value > maximum:
        fail(f"{label} must be <= {maximum}")
    return value


def require_string(label: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    return value


def validate_shape(payload: dict[str, Any]) -> dict[str, int]:
    shape = payload.get("table_shape")
    if not isinstance(shape, dict):
        fail("table_shape must be an object")
    require_keys("table_shape", shape, REQUIRED_SHAPE_KEYS)
    table_count = require_int("table_shape.table_count", shape["table_count"], minimum=0, maximum=255)
    points_per_table = require_int("table_shape.points_per_table", shape["points_per_table"], minimum=0, maximum=255)
    axes_per_point = require_int("table_shape.axes_per_point", shape["axes_per_point"], minimum=0, maximum=255)
    if table_count != EXPECTED_TABLE_COUNT:
        fail(f"table_shape.table_count must be {EXPECTED_TABLE_COUNT}")
    if points_per_table != EXPECTED_POINTS_PER_TABLE:
        fail(f"table_shape.points_per_table must be {EXPECTED_POINTS_PER_TABLE}")
    if axes_per_point != EXPECTED_AXES_PER_POINT:
        fail(f"table_shape.axes_per_point must be {EXPECTED_AXES_PER_POINT}")
    return {
        "table_count": table_count,
        "points_per_table": points_per_table,
        "axes_per_point": axes_per_point,
    }


def parse_source_tables(text: str) -> list[TableBlock]:
    blocks: list[TableBlock] = []
    seen: set[str] = set()
    for match in TABLE_RE.finditer(text):
        symbol = match.group("symbol")
        if symbol in seen:
            fail(f"duplicate source table symbol: {symbol}")
        seen.add(symbol)
        points = tuple((int(x), int(y)) for x, y in POINT_RE.findall(match.group("body")))
        if len(points) != EXPECTED_POINTS_PER_TABLE:
            fail(f"{symbol} must contain {EXPECTED_POINTS_PER_TABLE} points")
        for x, y in points:
            if not (0 <= x <= 255 and 0 <= y <= 255):
                fail(f"{symbol} contains out-of-byte-range point ({x}, {y})")
        blocks.append(TableBlock(symbol, match.start("body"), match.end("body"), points))
    if len(blocks) != EXPECTED_TABLE_COUNT:
        fail(f"source must contain exactly {EXPECTED_TABLE_COUNT} StickPoint tables, found {len(blocks)}")
    return blocks


def validate_payload(payload: dict[str, Any], source_symbols: set[str]) -> dict[str, list[tuple[int, int]]]:
    require_keys("replacement input", payload, REQUIRED_TOP_LEVEL_KEYS)
    schema_version = require_int("schema_version", payload["schema_version"], minimum=1, maximum=255)
    if schema_version != EXPECTED_SCHEMA_VERSION:
        fail(f"schema_version must be {EXPECTED_SCHEMA_VERSION}")
    replacement_kind = require_string("replacement_kind", payload["replacement_kind"])
    if replacement_kind != EXPECTED_REPLACEMENT_KIND:
        fail(f"replacement_kind must be {EXPECTED_REPLACEMENT_KIND!r}")
    target_file = require_string("target_file", payload["target_file"])
    if target_file != EXPECTED_TARGET_FILE:
        fail(f"target_file must be {EXPECTED_TARGET_FILE!r}")
    shape = validate_shape(payload)

    tables = payload.get("tables")
    if not isinstance(tables, list):
        fail("tables must be a list")
    if len(tables) != shape["table_count"]:
        fail(f"tables must contain exactly {shape['table_count']} tables")

    replacements: dict[str, list[tuple[int, int]]] = {}
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"tables[{table_index}] must be an object")
        require_keys(f"tables[{table_index}]", table, REQUIRED_TABLE_KEYS)
        symbol = require_string(f"tables[{table_index}].table_symbol", table["table_symbol"])
        if symbol in replacements:
            fail(f"duplicate table_symbol: {symbol}")
        if symbol not in source_symbols:
            fail(f"table_symbol does not exist in source: {symbol}")
        points = table.get("points")
        if not isinstance(points, list):
            fail(f"tables[{table_index}].points must be a list")
        if len(points) != shape["points_per_table"]:
            fail(f"tables[{table_index}].points must contain exactly {shape['points_per_table']} points")
        normalized_points: list[tuple[int, int]] = []
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                fail(f"tables[{table_index}].points[{point_index}] must be an object")
            require_keys(f"tables[{table_index}].points[{point_index}]", point, REQUIRED_POINT_KEYS)
            normalized_points.append(
                (
                    require_int(
                        f"tables[{table_index}].points[{point_index}].x",
                        point["x"],
                        minimum=0,
                        maximum=255,
                    ),
                    require_int(
                        f"tables[{table_index}].points[{point_index}].y",
                        point["y"],
                        minimum=0,
                        maximum=255,
                    ),
                )
            )
        replacements[symbol] = normalized_points
    if set(replacements) != source_symbols:
        missing = sorted(source_symbols - set(replacements))
        extra = sorted(set(replacements) - source_symbols)
        fail(f"replacement symbols must exactly match source symbols; missing={missing}, extra={extra}")
    return replacements


def emit_table_body(points: list[tuple[int, int]]) -> str:
    lines = [""]
    for row_start in range(0, EXPECTED_POINTS_PER_TABLE, 3):
        row = points[row_start : row_start + 3]
        rendered = ", ".join(f"{{{x}, {y}}}" for x, y in row)
        lines.append(f"    {rendered},")
    lines.append("")
    return "\n".join(lines)


def strip_table_bodies(text: str) -> str:
    parts: list[str] = []
    cursor = 0
    for block in parse_source_tables(text):
        parts.append(text[cursor:block.body_start])
        parts.append("<StickPoint table body>")
        cursor = block.body_end
    parts.append(text[cursor:])
    return "".join(parts)


def assert_only_table_bodies_changed(source_text: str, output_text: str) -> None:
    source_blocks = parse_source_tables(source_text)
    output_blocks = parse_source_tables(output_text)
    source_symbols = [block.symbol for block in source_blocks]
    output_symbols = [block.symbol for block in output_blocks]
    if output_symbols != source_symbols:
        fail("output must preserve table symbol order")
    if strip_table_bodies(output_text) != strip_table_bodies(source_text):
        fail("output changed non-table source text")


def patch_source_text(source_text: str, replacements: dict[str, list[tuple[int, int]]]) -> str:
    blocks = parse_source_tables(source_text)
    output_parts: list[str] = []
    cursor = 0
    for block in blocks:
        output_parts.append(source_text[cursor:block.body_start])
        output_parts.append(emit_table_body(replacements[block.symbol]))
        cursor = block.body_end
    output_parts.append(source_text[cursor:])
    output_text = "".join(output_parts)
    assert_only_table_bodies_changed(source_text, output_text)
    return output_text


def normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def assert_safe_output_path(output_path: Path) -> None:
    resolved = normalize_repo_path(output_path)
    active_source = SOURCE_TABLES.resolve()
    if resolved == active_source:
        fail("generator must not write the active source table file")
    try:
        resolved.relative_to((REPO_ROOT / "src").resolve())
    except ValueError:
        pass
    else:
        fail("generator must not write under active source paths")
    try:
        resolved.relative_to((REPO_ROOT / "include").resolve())
    except ValueError:
        pass
    else:
        fail("generator must not write under active include paths")


def generate(input_path: Path, output_path: Path | None = None) -> str:
    source_text = SOURCE_TABLES.read_text(encoding="utf-8")
    blocks = parse_source_tables(source_text)
    replacements = validate_payload(load_json_object(input_path), {block.symbol for block in blocks})
    output_text = patch_source_text(source_text, replacements)
    if output_path is not None:
        assert_safe_output_path(output_path)
        resolved = normalize_repo_path(output_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(output_text, encoding="utf-8")
    return output_text


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print(
            "usage: generate_source_owned_table_replacement.py INPUT_JSON [OUTPUT_HPP]",
            file=sys.stderr,
        )
        return 2
    input_path = Path(argv[1])
    output_path = Path(argv[2]) if len(argv) == 3 else None
    try:
        output = generate(input_path, output_path)
    except SourceOwnedTableReplacementError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if output_path is None:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
