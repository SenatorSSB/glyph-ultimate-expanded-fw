#!/usr/bin/env python3
"""Generate a source-owned runtime config C++ fixture from neutral JSON.

The generated text is an offline artifact contract only. The default CLI path
rejects active source destinations so this tool cannot accidentally write into
firmware runtime selection paths during docs/fixture use.

An explicit install mode may write only to the inert generated-source-owned
source artifact directory. That path is source-owned but not wired into active
runtime selection by this generator.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import load_source_tables


EXPECTED_SCHEMA_VERSION = 1
EXPECTED_ARTIFACT_KIND = "generated_source_owned_runtime_config_table"
EXPECTED_LAYOUT_SPEC_SCHEMA_VERSION = 1
EXPECTED_LAYOUT_SPEC_KIND = "generated_source_owned_layout_spec"
EXPECTED_TABLE_COUNT = 28
EXPECTED_POINTS_PER_TABLE = 9
EXPECTED_AXES_PER_POINT = 2
SPEC_INPUT_MODE = "--emit-from-layout-spec"
REPO_ROOT = Path(__file__).resolve().parents[1]
INERT_SOURCE_INSTALL_DIR = REPO_ROOT / "src/modes/runtime_config/generated_source_owned"
SOURCE_TABLES = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
SOURCE_INTERPRETER = REPO_ROOT / "src/modes/UltimateRuntimeConfigInterpreter.hpp"

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "artifact_kind",
    "controller_family",
    "profile_name",
    "revision",
}
REQUIRED_LAYOUT_SPEC_KEYS = {
    "schema_version",
    "layout_spec_kind",
    "layout_name",
    "controller_family",
    "profile_name",
    "revision",
    "table_shape",
    "tables",
}
REQUIRED_SHAPE_KEYS = {"table_count", "points_per_table", "axes_per_point"}
REQUIRED_LAYOUT_SPEC_TABLE_KEYS = {"table_id", "table_name", "table_symbol"}
REQUIRED_POINT_KEYS = {"x", "y"}

FORBIDDEN_OUTPUT_PATH_PARTS = {
    "HAL",
    "backend",
    "src",
}


class GeneratorContractError(ValueError):
    """Raised when the generator input or output path violates the contract."""


def fail(message: str) -> None:
    raise GeneratorContractError(message)


def reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            fail(f"duplicate JSON key: {key}")
        values[key] = value
    return values


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_object_pairs,
        )
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail("generator input must be a JSON object")
    return payload


def require_keys(label: str, value: dict[str, Any], required: set[str]) -> None:
    missing = sorted(required - set(value))
    if missing:
        fail(f"{label} missing required keys: {', '.join(missing)}")


def require_exact_keys(label: str, value: dict[str, Any], required: set[str]) -> None:
    require_keys(label, value, required)
    extra = sorted(set(value) - required)
    if extra:
        fail(f"{label} has unexpected keys: {', '.join(extra)}")


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


def validate_shape(payload: dict[str, Any], *, expected_table_count: int = EXPECTED_TABLE_COUNT) -> dict[str, int]:
    shape = payload.get("table_shape")
    if not isinstance(shape, dict):
        fail("table_shape must be an object")
    require_exact_keys("table_shape", shape, REQUIRED_SHAPE_KEYS)
    table_count = require_int("table_shape.table_count", shape["table_count"], minimum=0, maximum=255)
    points_per_table = require_int(
        "table_shape.points_per_table",
        shape["points_per_table"],
        minimum=0,
        maximum=255,
    )
    axes_per_point = require_int("table_shape.axes_per_point", shape["axes_per_point"], minimum=0, maximum=255)
    if table_count != expected_table_count:
        fail(f"table_shape.table_count must be {expected_table_count}")
    if points_per_table != EXPECTED_POINTS_PER_TABLE:
        fail(f"table_shape.points_per_table must be {EXPECTED_POINTS_PER_TABLE}")
    if axes_per_point != EXPECTED_AXES_PER_POINT:
        fail(f"table_shape.axes_per_point must be {EXPECTED_AXES_PER_POINT}")
    return {
        "table_count": table_count,
        "points_per_table": points_per_table,
        "axes_per_point": axes_per_point,
    }


def validate_layout_spec(
    payload: dict[str, Any],
    *,
    expected_table_count: int = EXPECTED_TABLE_COUNT,
) -> dict[str, Any]:
    layout_spec = payload.get("layout_spec")
    if layout_spec is None:
        fail("generator input requires layout_spec")
    if not isinstance(layout_spec, dict):
        fail("layout_spec must be an object")
    require_exact_keys("layout_spec", layout_spec, REQUIRED_LAYOUT_SPEC_KEYS)
    schema_version = require_int("layout_spec.schema_version", layout_spec["schema_version"], minimum=1, maximum=255)
    if schema_version != EXPECTED_LAYOUT_SPEC_SCHEMA_VERSION:
        fail(f"layout_spec.schema_version must be {EXPECTED_LAYOUT_SPEC_SCHEMA_VERSION}")
    layout_spec_kind = require_string("layout_spec.layout_spec_kind", layout_spec["layout_spec_kind"])
    if layout_spec_kind != EXPECTED_LAYOUT_SPEC_KIND:
        fail(f"layout_spec.layout_spec_kind must be {EXPECTED_LAYOUT_SPEC_KIND!r}")
    require_string("layout_spec.layout_name", layout_spec["layout_name"])
    require_string("layout_spec.controller_family", layout_spec["controller_family"])
    require_string("layout_spec.profile_name", layout_spec["profile_name"])
    require_int("layout_spec.revision", layout_spec["revision"], minimum=0)
    shape = validate_shape(layout_spec, expected_table_count=expected_table_count)
    expected_symbols = parse_source_baseline_table_order(SOURCE_INTERPRETER.read_text(encoding="utf-8"))
    if len(expected_symbols) != shape["table_count"]:
        fail(
            "layout_spec must mirror the current source-owned baseline table count"
        )
    tables = layout_spec.get("tables")
    if not isinstance(tables, list):
        fail("layout_spec.tables must be a list")
    if len(tables) != shape["table_count"]:
        fail(f"layout_spec.tables must contain exactly {shape['table_count']} entries")
    normalized_tables: list[dict[str, Any]] = []
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"layout_spec.tables[{table_index}] must be an object")
        require_exact_keys(f"layout_spec.tables[{table_index}]", table, REQUIRED_LAYOUT_SPEC_TABLE_KEYS)
        table_id = require_int(
            f"layout_spec.tables[{table_index}].table_id",
            table["table_id"],
            minimum=0,
            maximum=shape["table_count"] - 1,
        )
        table_name = require_string(f"layout_spec.tables[{table_index}].table_name", table["table_name"])
        table_symbol = require_string(f"layout_spec.tables[{table_index}].table_symbol", table["table_symbol"])
        expected_symbol = expected_symbols[table_index]
        expected_name = canonical_table_name(expected_symbol)
        if table_id != table_index:
            fail(f"layout_spec.tables[{table_index}].table_id must be {table_index}")
        if table_name != expected_name:
            fail(f"layout_spec.tables[{table_index}].table_name must be {expected_name!r}")
        if table_symbol != expected_symbol:
            fail(
                f"layout_spec.tables[{table_index}].table_symbol must be {expected_symbol!r}"
            )
        normalized_tables.append(
            {
                "table_id": table_id,
                "table_name": table_name,
                "table_symbol": table_symbol,
            }
        )
    normalized = {
        "schema_version": schema_version,
        "layout_spec_kind": layout_spec_kind,
        "layout_name": require_string("layout_spec.layout_name", layout_spec["layout_name"]),
        "controller_family": require_string("layout_spec.controller_family", layout_spec["controller_family"]),
        "profile_name": require_string("layout_spec.profile_name", layout_spec["profile_name"]),
        "revision": require_int("layout_spec.revision", layout_spec["revision"], minimum=0),
        "table_shape": shape,
        "tables": normalized_tables,
    }
    return normalized


def table_sort_key(table: dict[str, Any], *, max_table_id: int) -> tuple[int, int | str]:
    if "table_id" in table:
        return (0, require_int("tables[].table_id", table["table_id"], minimum=0, maximum=max_table_id))
    return (1, require_string("tables[].table_name", table.get("table_name")))


def canonical_table_name(value: str) -> str:
    if value.startswith("k") and value.endswith("Table") and len(value) > len("kTable"):
        return value[1:-5]
    return value


def validate_tables(
    payload: dict[str, Any],
    shape: dict[str, int],
    *,
    layout_spec_tables: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    tables = payload.get("tables")
    if not isinstance(tables, list):
        fail("tables must be a list")
    if len(tables) != shape["table_count"]:
        fail(f"tables must contain exactly {shape['table_count']} tables")

    normalized_tables: list[dict[str, Any]] = []
    seen_table_ids: set[int] = set()
    seen_table_names: set[str] = set()
    saw_table_id = False
    saw_table_name_only = False
    table_lookup_by_id: dict[int, dict[str, Any]] = {}
    table_lookup_by_name: dict[str, dict[str, Any]] = {}

    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"tables[{table_index}] must be an object")
        if "table_id" not in table and "table_name" not in table:
            fail(f"tables[{table_index}] must include table_id or table_name")
        if "table_id" in table:
            saw_table_id = True
            table_id = require_int(
                f"tables[{table_index}].table_id",
                table["table_id"],
                minimum=0,
                maximum=shape["table_count"] - 1,
            )
            if table_id in seen_table_ids:
                fail(f"duplicate table_id: {table_id}")
            seen_table_ids.add(table_id)
        else:
            saw_table_name_only = True
            table_id = None
        if "table_name" in table:
            table_name = require_string(f"tables[{table_index}].table_name", table["table_name"])
            if table_name in seen_table_names:
                fail(f"duplicate table_name: {table_name}")
            seen_table_names.add(table_name)
        else:
            table_name = f"table_{table_id}"

        points = table.get("points")
        if not isinstance(points, list):
            fail(f"tables[{table_index}].points must be a list")
        if len(points) != shape["points_per_table"]:
            fail(
                f"tables[{table_index}].points must contain exactly "
                f"{shape['points_per_table']} points"
            )
        normalized_points: list[dict[str, int]] = []
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                fail(f"tables[{table_index}].points[{point_index}] must be an object")
            require_keys(f"tables[{table_index}].points[{point_index}]", point, REQUIRED_POINT_KEYS)
            normalized_points.append(
                {
                    "x": require_int(
                        f"tables[{table_index}].points[{point_index}].x",
                        point["x"],
                        minimum=0,
                        maximum=255,
                    ),
                    "y": require_int(
                        f"tables[{table_index}].points[{point_index}].y",
                        point["y"],
                        minimum=0,
                        maximum=255,
                    ),
                }
            )
        normalized_tables.append(
            {
                "table_id": table_id,
                "table_name": table_name,
                "table_symbol": table.get("table_symbol"),
                "points": normalized_points,
            }
        )
        if table_id is not None:
            table_lookup_by_id[table_id] = normalized_tables[-1]
        table_lookup_by_name[table_name] = normalized_tables[-1]
        table_lookup_by_name.setdefault(canonical_table_name(table_name), normalized_tables[-1])

    if saw_table_id and saw_table_name_only:
        fail("tables must use table_id for all tables or table_name-only for all tables")
    if layout_spec_tables is not None:
        if len(layout_spec_tables) != len(normalized_tables):
            fail("layout_spec table order must match the generator table count")
        for table_index, (table, spec_table) in enumerate(zip(normalized_tables, layout_spec_tables)):
            spec_table_id = spec_table["table_id"]
            spec_table_name = spec_table["table_name"]
            spec_table_symbol = spec_table["table_symbol"]
            if table["table_id"] is None:
                fail(f"tables[{table_index}] must include table_id when layout_spec is present")
            if table["table_id"] != spec_table_id:
                fail(f"layout_spec table_id mismatch at entry {table_index}")
            if table["table_name"] != spec_table_name:
                fail(f"layout_spec table_name mismatch at entry {table_index}")
            if table["table_symbol"] is not None and table["table_symbol"] != spec_table_symbol:
                fail(f"layout_spec table_symbol mismatch at entry {table_index}")
        return normalized_tables
    return sorted(normalized_tables, key=lambda table: table_sort_key(table, max_table_id=shape["table_count"] - 1))


def validate_payload(payload: dict[str, Any], *, expected_table_count: int = EXPECTED_TABLE_COUNT) -> dict[str, Any]:
    require_keys("generator input", payload, REQUIRED_TOP_LEVEL_KEYS)
    schema_version = require_int("schema_version", payload["schema_version"], minimum=1, maximum=255)
    if schema_version != EXPECTED_SCHEMA_VERSION:
        fail(f"schema_version must be {EXPECTED_SCHEMA_VERSION}")
    artifact_kind = require_string("artifact_kind", payload["artifact_kind"])
    if artifact_kind != EXPECTED_ARTIFACT_KIND:
        fail(f"artifact_kind must be {EXPECTED_ARTIFACT_KIND!r}")
    controller_family = require_string("controller_family", payload["controller_family"])
    profile_name = require_string("profile_name", payload["profile_name"])
    revision = require_int("revision", payload["revision"], minimum=0)
    layout_spec = validate_layout_spec(payload, expected_table_count=expected_table_count)
    if layout_spec["controller_family"] != controller_family:
        fail("layout_spec.controller_family must match generator input controller_family")
    if layout_spec["profile_name"] != profile_name:
        fail("layout_spec.profile_name must match generator input profile_name")
    if layout_spec["revision"] != revision:
        fail("layout_spec.revision must match generator input revision")
    shape = validate_shape(payload, expected_table_count=expected_table_count)
    tables = validate_tables(payload, shape, layout_spec_tables=layout_spec["tables"])
    return {
        "schema_version": schema_version,
        "artifact_kind": artifact_kind,
        "controller_family": controller_family,
        "profile_name": profile_name,
        "revision": revision,
        "layout_spec": layout_spec,
        "table_shape": shape,
        "tables": tables,
    }


def cxx_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def emit_cpp_header(contract: dict[str, Any]) -> str:
    shape = contract["table_shape"]
    lines = [
        "#pragma once",
        "",
        "#include <cstdint>",
        "",
        "namespace glyph::runtime_config::generated_source_owned::fixtures {",
        "",
        "// generated source-owned runtime config artifact",
        "// inert generated-table placeholder",
        "// not wired into runtime selection",
        "// generated baseline equivalent to kSourceOwnedCurrentBaselineRuntimeConfig when checker-proven",
        "static constexpr std::uint32_t kGeneratedSourceOwnedRuntimeConfigSchemaVersion = "
        f"{contract['schema_version']}u;",
        "static constexpr char kGeneratedSourceOwnedRuntimeConfigArtifactKind[] = "
        f"{cxx_string(contract['artifact_kind'])};",
        "static constexpr char kGeneratedSourceOwnedRuntimeConfigControllerFamily[] = "
        f"{cxx_string(contract['controller_family'])};",
        "static constexpr char kGeneratedSourceOwnedRuntimeConfigProfileName[] = "
        f"{cxx_string(contract['profile_name'])};",
        "static constexpr std::uint32_t kGeneratedSourceOwnedRuntimeConfigRevision = "
        f"{contract['revision']}u;",
        "static constexpr std::uint8_t kGeneratedSourceOwnedRuntimeConfigTableCount = "
        f"{shape['table_count']}u;",
        "static constexpr std::uint8_t kGeneratedSourceOwnedRuntimeConfigPointsPerTable = "
        f"{shape['points_per_table']}u;",
        "static constexpr std::uint8_t kGeneratedSourceOwnedRuntimeConfigAxesPerPoint = "
        f"{shape['axes_per_point']}u;",
        "",
        "static constexpr std::uint8_t kGeneratedSourceOwnedRuntimeConfigTables["
        f"{shape['table_count']}][{shape['points_per_table']}][{shape['axes_per_point']}] = {{",
    ]
    for table in contract["tables"]:
        table_label = table.get("table_symbol") or table["table_name"]
        if table["table_id"] is not None:
            table_label = f"{table['table_id']} {table_label}"
        lines.append(f"    {{  // {table_label}")
        for point in table["points"]:
            lines.append(f"        {{{point['x']}u, {point['y']}u}},")
        lines.append("    },")
    lines.extend(
        [
            "};",
            "",
            "}  // namespace glyph::runtime_config::generated_source_owned::fixtures",
            "",
        ]
    )
    return "\n".join(lines)


def parse_source_owned_baseline_contract() -> dict[str, Any]:
    interpreter_text = SOURCE_INTERPRETER.read_text(encoding="utf-8")
    source_tables = load_source_tables()
    ordered_symbols = parse_source_baseline_table_order(interpreter_text)
    tables: list[dict[str, Any]] = []
    for table_id, symbol_name in enumerate(ordered_symbols):
        normalized_name = symbol_name.removeprefix("k").removesuffix("Table")
        points = source_tables.get(normalized_name)
        if points is None:
            fail(f"baseline table {symbol_name} is missing from {SOURCE_TABLES}")
        tables.append(
            {
                "table_id": table_id,
                "table_name": normalized_name,
                "table_symbol": symbol_name,
                "points": [{"x": x, "y": y} for x, y in points],
            }
        )
    table_count = len(ordered_symbols)
    layout_spec_tables = [
        {
            "table_id": table_id,
            "table_name": symbol_name.removeprefix("k").removesuffix("Table"),
            "table_symbol": symbol_name,
        }
        for table_id, symbol_name in enumerate(ordered_symbols)
    ]
    return validate_payload(
        {
            "schema_version": EXPECTED_SCHEMA_VERSION,
            "artifact_kind": EXPECTED_ARTIFACT_KIND,
            "controller_family": "glyph_mk6",
            "profile_name": "current_source_owned_baseline_runtime_config",
            "revision": 1,
            "layout_spec": {
                "schema_version": EXPECTED_LAYOUT_SPEC_SCHEMA_VERSION,
                "layout_spec_kind": EXPECTED_LAYOUT_SPEC_KIND,
                "layout_name": "current_source_owned_baseline_layout",
                "controller_family": "glyph_mk6",
                "profile_name": "current_source_owned_baseline_runtime_config",
                "revision": 1,
                "table_shape": {
                    "table_count": table_count,
                    "points_per_table": EXPECTED_POINTS_PER_TABLE,
                    "axes_per_point": EXPECTED_AXES_PER_POINT,
                },
                "tables": layout_spec_tables,
            },
            "table_shape": {
                "table_count": table_count,
                "points_per_table": EXPECTED_POINTS_PER_TABLE,
                "axes_per_point": EXPECTED_AXES_PER_POINT,
            },
            "tables": tables,
        },
        expected_table_count=table_count,
    )


def parse_source_stick_tables(text: str) -> dict[str, list[tuple[int, int]]]:
    table_re = re.compile(
        r"constexpr\s+StickPoint\s+(k[A-Za-z0-9_]+Table)\s*\[\s*9\s*\]\s*=\s*\{(?P<body>.*?)\};",
        re.DOTALL,
    )
    point_re = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")
    tables: dict[str, list[tuple[int, int]]] = {}
    for match in table_re.finditer(text):
        symbol_name = match.group(1)
        points = [(int(x), int(y)) for x, y in point_re.findall(match.group("body"))]
        if len(points) != EXPECTED_POINTS_PER_TABLE:
            fail(f"{symbol_name} must contain {EXPECTED_POINTS_PER_TABLE} points")
        for x, y in points:
            if not (0 <= x <= 255 and 0 <= y <= 255):
                fail(f"{symbol_name} contains out-of-byte-range point ({x}, {y})")
        if symbol_name in tables:
            fail(f"duplicate source table symbol: {symbol_name}")
        tables[symbol_name] = points
    if len(tables) < EXPECTED_TABLE_COUNT:
        fail(f"expected at least {EXPECTED_TABLE_COUNT} source tables, found {len(tables)}")
    return tables


def parse_source_baseline_table_order(text: str) -> list[str]:
    block_match = re.search(
        r"kSourceOwnedCurrentBaselineRuntimeTables\s*\[\s*[^\]]+\s*\]\s*=\s*\{(?P<body>.*?)\};",
        text,
        re.DOTALL,
    )
    if block_match is None:
        fail("could not find kSourceOwnedCurrentBaselineRuntimeTables")
    row_re = re.compile(
        r"\{\s*RuntimeTableId::[A-Za-z0-9_]+\s*,\s*\"(?P<symbol>k[A-Za-z0-9_]+Table)\"\s*,\s*(?P=symbol)\s*,"
    )
    symbols = [match.group("symbol") for match in row_re.finditer(block_match.group("body"))]
    if len(symbols) < EXPECTED_TABLE_COUNT:
        fail(f"baseline table order must contain at least {EXPECTED_TABLE_COUNT} tables, found {len(symbols)}")
    if len(set(symbols)) != len(symbols):
        fail("baseline table order contains duplicate symbols")
    return symbols


def assert_safe_output_path(output_path: Path) -> None:
    parts = set(output_path.parts)
    if parts & FORBIDDEN_OUTPUT_PATH_PARTS:
        fail("output path must not be under active source, HAL, or backend paths")


def normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def assert_inert_source_install_path(output_path: Path) -> None:
    resolved = normalize_repo_path(output_path)
    allowed_root = INERT_SOURCE_INSTALL_DIR.resolve()
    try:
        resolved.relative_to(allowed_root)
    except ValueError:
        fail("install output path must be under src/modes/runtime_config/generated_source_owned")
    if resolved.suffix not in {".h", ".hpp", ".hh", ".cc", ".cpp"}:
        fail("install output path must be a C++ source/header artifact")


def generate(
    input_path: Path,
    output_path: Path | None = None,
    *,
    allow_inert_source_install: bool = False,
) -> str:
    contract = validate_payload(load_json_object(input_path))
    output = emit_cpp_header(contract)
    if output_path is not None:
        if allow_inert_source_install:
            assert_inert_source_install_path(output_path)
        else:
            assert_safe_output_path(output_path)
        normalized_output_path = normalize_repo_path(output_path)
        normalized_output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized_output_path.write_text(output, encoding="utf-8")
    return output


def generate_from_layout_spec(
    input_path: Path,
    output_path: Path | None = None,
) -> str:
    contract = validate_payload(load_json_object(input_path))
    if contract["layout_spec"] is None:
        fail(f"{SPEC_INPUT_MODE} requires layout_spec")
    output = emit_cpp_header(contract)
    if output_path is not None:
        assert_safe_output_path(output_path)
        normalized_output_path = normalize_repo_path(output_path)
        normalized_output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized_output_path.write_text(output, encoding="utf-8")
    return output


def generate_current_source_owned_baseline(output_path: Path | None = None) -> str:
    output = emit_cpp_header(parse_source_owned_baseline_contract())
    if output_path is not None:
        assert_inert_source_install_path(output_path)
        normalized_output_path = normalize_repo_path(output_path)
        normalized_output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized_output_path.write_text(output, encoding="utf-8")
    return output


def main(argv: list[str]) -> int:
    baseline_mode = len(argv) in {2, 3} and argv[1] == "--emit-current-source-owned-baseline"
    spec_input_mode = len(argv) in {3, 4} and argv[1] == SPEC_INPUT_MODE
    install_mode = len(argv) == 4 and argv[1] == "--install-inert-source-artifact"
    if baseline_mode:
        output_path = Path(argv[2]) if len(argv) == 3 else None
    elif spec_input_mode:
        input_path = Path(argv[2])
        output_path = Path(argv[3]) if len(argv) == 4 else None
    elif install_mode:
        input_path = Path(argv[2])
        output_path = Path(argv[3])
    elif len(argv) in {2, 3}:
        input_path = Path(argv[1])
        output_path = Path(argv[2]) if len(argv) == 3 else None
    else:
        print(
            "usage: generate_source_owned_runtime_config.py INPUT_JSON [OUTPUT_HPP]\n"
            "       generate_source_owned_runtime_config.py "
            f"{SPEC_INPUT_MODE} INPUT_JSON [OUTPUT_HPP]\n"
            "       generate_source_owned_runtime_config.py "
            "--install-inert-source-artifact INPUT_JSON OUTPUT_HPP\n"
            "       generate_source_owned_runtime_config.py "
            "--emit-current-source-owned-baseline [OUTPUT_HPP]",
            file=sys.stderr,
        )
        return 2
    try:
        if baseline_mode:
            output = generate_current_source_owned_baseline(output_path)
        elif spec_input_mode:
            output = generate_from_layout_spec(input_path, output_path)
        else:
            output = generate(
                input_path,
                output_path,
                allow_inert_source_install=install_mode,
            )
    except GeneratorContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if output_path is None:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
