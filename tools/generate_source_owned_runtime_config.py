#!/usr/bin/env python3
"""Generate a source-owned runtime config C++ fixture from neutral JSON.

The generated text is an offline artifact contract only. The default CLI path
rejects active source destinations so this tool cannot accidentally write into
firmware runtime selection paths during docs/fixture use.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_VERSION = 1
EXPECTED_ARTIFACT_KIND = "generated_source_owned_runtime_config_table"
EXPECTED_TABLE_COUNT = 27
EXPECTED_POINTS_PER_TABLE = 9
EXPECTED_AXES_PER_POINT = 2

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "artifact_kind",
    "controller_family",
    "profile_name",
    "revision",
    "table_shape",
    "tables",
}
REQUIRED_SHAPE_KEYS = {"table_count", "points_per_table", "axes_per_point"}
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
    points_per_table = require_int(
        "table_shape.points_per_table",
        shape["points_per_table"],
        minimum=0,
        maximum=255,
    )
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


def table_sort_key(table: dict[str, Any]) -> tuple[int, int | str]:
    if "table_id" in table:
        return (0, require_int("tables[].table_id", table["table_id"], minimum=0, maximum=EXPECTED_TABLE_COUNT - 1))
    return (1, require_string("tables[].table_name", table.get("table_name")))


def validate_tables(payload: dict[str, Any], shape: dict[str, int]) -> list[dict[str, Any]]:
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
                "points": normalized_points,
            }
        )

    if saw_table_id and saw_table_name_only:
        fail("tables must use table_id for all tables or table_name-only for all tables")
    return sorted(normalized_tables, key=table_sort_key)


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
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
    shape = validate_shape(payload)
    tables = validate_tables(payload, shape)
    return {
        "schema_version": schema_version,
        "artifact_kind": artifact_kind,
        "controller_family": controller_family,
        "profile_name": profile_name,
        "revision": revision,
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
        "static constexpr std::uint8_t kGeneratedSourceOwnedRuntimeConfigTables[27][9][2] = {",
    ]
    for table in contract["tables"]:
        table_label = table["table_name"]
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


def assert_safe_output_path(output_path: Path) -> None:
    parts = set(output_path.parts)
    if parts & FORBIDDEN_OUTPUT_PATH_PARTS:
        fail("output path must not be under active source, HAL, or backend paths")


def generate(input_path: Path, output_path: Path | None = None) -> str:
    contract = validate_payload(load_json_object(input_path))
    output = emit_cpp_header(contract)
    if output_path is not None:
        assert_safe_output_path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    return output


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print(
            "usage: generate_source_owned_runtime_config.py INPUT_JSON [OUTPUT_HPP]",
            file=sys.stderr,
        )
        return 2
    try:
        output = generate(Path(argv[1]), Path(argv[2]) if len(argv) == 3 else None)
    except GeneratorContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if len(argv) == 2:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
