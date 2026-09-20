#!/usr/bin/env python3
"""Extract Glyph identity runtime stick tables from Ultimate.cpp.

This extractor is the source-literal boundary for StickPoint[9] tables. It enforces
literal parseability and byte-range for coordinates so malformed source tables fail fast
before they can reach firmware merge or checker comparison.

This is a source-sync guardrail for the bounded Python behavior evaluator. It
does not compile firmware, generate artifacts, or validate hardware behavior.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from enum import Enum
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
INTERPRETER_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigInterpreter.hpp"
GENERATED_LIKE_TABLES_INCLUDE = '#include "modes/UltimateIdentityRuntimeTables.hpp"'
GENERATED_LIKE_TABLES_PATH = REPO_ROOT / "src" / "modes" / "UltimateIdentityRuntimeTables.hpp"
GENERATED_BASELINE_INCLUDE = '#include "runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"'
GENERATED_BASELINE_PATH = (
    REPO_ROOT
    / "src"
    / "modes"
    / "runtime_config"
    / "generated_source_owned"
    / "GeneratedRuntimeConfigBaseline.current.hpp"
)
REQUIRED_GENERATED_LIKE_TABLES_CAVEATS = (
    "Generated-like identity runtime table constants.",
    "Source-owned firmware constants, not runtime-loaded config.",
    "Values are source-authored, not generated at runtime.",
    "Do not treat this as serial/device write behavior.",
    "Values must remain source-synced with the generated-config/tooling checks.",
)


class RuntimeTableId(str, Enum):
    Default = "Default"
    ModeDefault = "ModeDefault"
    X1 = "X1"
    X2 = "X2"
    MX1 = "MX1"
    MX2 = "MX2"
    Y1 = "Y1"
    Y2 = "Y2"
    MY1 = "MY1"
    LayerNormalX = "LayerNormalX"
    MLayerNormalX = "MLayerNormalX"
    LayerFlipper = "LayerFlipper"
    MLayerFlipper = "MLayerFlipper"
    Y1Tilt1 = "Y1Tilt1"
    MY1Tilt1 = "MY1Tilt1"
    Y1LayerFlipper = "Y1LayerFlipper"
    MY1LayerFlipper = "MY1LayerFlipper"
    Y1LayerNormalX = "Y1LayerNormalX"
    MY1LayerNormalX = "MY1LayerNormalX"
    Tilt1 = "Tilt1"
    Tilt2 = "Tilt2"
    Tilt3 = "Tilt3"
    Tilt1Minus41 = "Tilt1Minus41"
    RT1RF4Custom = "RT1RF4Custom"
    MTilt1 = "MTilt1"
    MTilt2 = "MTilt2"
    MTilt3 = "MTilt3"
    Lt1LowMagnitude = "Lt1LowMagnitude"


CURRENT_BASELINE_CONFIG_SCHEMA_NAME = "glyph_runtime_config_interpreter_source_baseline"
CURRENT_BASELINE_CONFIG_SCHEMA_VERSION = 1
CURRENT_BASELINE_CONFIG_STATUS = "source_owned_current_baseline_not_runtime_loaded"
CURRENT_BASELINE_CONFIG_MODE_SCOPE = "MODE_ULTIMATE"
CURRENT_BASELINE_CONFIG_TABLE_FAMILY = "StickPoint"
CURRENT_BASELINE_CONFIG_FALLBACK_TABLE_ID = RuntimeTableId.Default.value

TABLE_SYMBOL_TO_NAME: tuple[tuple[str, str], ...] = (
    ("kDefaultTable", "Default"),
    ("kModeDefaultTable", "ModeDefault"),
    ("kX1Table", "X1"),
    ("kX2Table", "X2"),
    ("kMX1Table", "MX1"),
    ("kMX2Table", "MX2"),
    ("kY1Table", "Y1"),
    ("kY2Table", "Y2"),
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
CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT = len(RuntimeTableId)
CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT = EXPECTED_POINT_COUNT

_TABLE_PATTERN = re.compile(
    r"constexpr\s+StickPoint\s+"
    r"(?P<symbol>k[A-Za-z0-9]+Table)"
    r"\s*\[\s*(?P<size>\d+)\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
_POINT_PATTERN = re.compile(r"\{\s*(?P<x>\d+)\s*,\s*(?P<y>\d+)\s*\}")
_GENERATED_RAW_TABLE_PATTERN = re.compile(
    r"static\s+constexpr\s+std::uint8_t\s+"
    r"kGeneratedSourceOwnedRuntimeConfigTables\s*\[\s*\d+\s*\]\s*\[\s*\d+\s*\]\s*\[\s*2\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
_GENERATED_RAW_ROW_PATTERN = re.compile(
    r"\{\s*//\s*(?P<index>\d+)\s+(?P<symbol>k[A-Za-z0-9_]+Table)\s*(?P<body>.*?)\n\s*\},",
    re.DOTALL,
)
_GENERATED_RAW_POINT_PATTERN = re.compile(r"\{\s*(?P<x>\d+)u?\s*,\s*(?P<y>\d+)u?\s*\}")
_SOURCE_OWNED_POINT_MACRO_PATTERN = re.compile(
    r"#define\s+SOURCE_OWNED_GENERATED_TABLE_POINT\s*\(\s*TABLE_INDEX\s*,\s*POINT_INDEX\s*\)"
    r"(?P<body>.*?)(?=\n#define\s+SOURCE_OWNED_GENERATED_TABLE\s*\(|\Z)",
    re.DOTALL,
)
_SOURCE_OWNED_TABLE_MACRO_PATTERN = re.compile(
    r"#define\s+SOURCE_OWNED_GENERATED_TABLE\s*\(\s*TABLE_SYMBOL\s*,\s*TABLE_INDEX\s*\)"
    r"(?P<body>.*?)(?=\nSOURCE_OWNED_GENERATED_TABLE\s*\(|\n#undef\s+SOURCE_OWNED_GENERATED_TABLE\s*\(|\Z)",
    re.DOTALL,
)
_SOURCE_OWNED_TABLE_INVOCATION_PATTERN = re.compile(
    r"(?m)^\s*SOURCE_OWNED_GENERATED_TABLE\(\s*(?P<symbol>k[A-Za-z0-9_]+Table)\s*,\s*(?P<index>\d+)\s*\)\s*;\s*$"
)
_SOURCE_OWNED_RAW_ARRAY = (
    "glyph::runtime_config::generated_source_owned::fixtures::"
    "kGeneratedSourceOwnedRuntimeConfigTables"
)


class TableExtractionError(ValueError):
    """Raised when source table extraction cannot be trusted."""


def parse_source_owned_adapter_correspondence(source_text: str) -> tuple[tuple[str, int], ...]:
    """Validate the active generated-table adapter grammar and return its aliases.

    This is deliberately a correspondence parser, not a second table-semantic
    authority: table order remains TABLE_SYMBOL_TO_NAME and point values remain
    owned by the canonical raw generated array.
    """

    namespace_matches = list(
        re.finditer(r"namespace\s+glyph::runtime_config::generated_source_owned::fixtures\s*\{", source_text)
    )
    namespace_openings = re.findall(r"namespace\s+[A-Za-z0-9_:]+\s*\{", source_text)
    if len(namespace_matches) != 1 or len(namespace_openings) != 1:
        raise TableExtractionError("generated adapter must contain the canonical generated-source namespace exactly once")
    raw_array_pattern = re.compile(
        r"static\s+constexpr\s+std::uint8_t\s+kGeneratedSourceOwnedRuntimeConfigTables"
        r"\s*\[\s*28\s*\]\s*\[\s*9\s*\]\s*\[\s*2\s*\]"
    )
    raw_array_matches = list(raw_array_pattern.finditer(source_text))
    if len(raw_array_matches) != 1:
        raise TableExtractionError("generated adapter must contain exactly one canonical raw table array")
    namespace_close = re.search(
        r"\n}\s*//\s*namespace\s+glyph::runtime_config::generated_source_owned::fixtures\b",
        source_text[namespace_matches[0].end() :],
        re.DOTALL,
    )
    if namespace_close is None:
        raise TableExtractionError("canonical generated-source namespace is not closed exactly")
    namespace_end = namespace_matches[0].end() + namespace_close.start()
    if not namespace_matches[0].end() <= raw_array_matches[0].start() < namespace_end:
        raise TableExtractionError("canonical raw table array must be declared inside its canonical namespace")

    point_macros = _SOURCE_OWNED_POINT_MACRO_PATTERN.findall(source_text)
    if len(point_macros) != 1:
        raise TableExtractionError("generated adapter point macro is missing")
    point_body = point_macros[0]
    point_body_compact = re.sub(r"\s+", "", point_body).replace("\\", "")
    expected_point_body = (
        "{"
        + _SOURCE_OWNED_RAW_ARRAY
        + "[TABLE_INDEX][POINT_INDEX][0],"
        + _SOURCE_OWNED_RAW_ARRAY
        + "[TABLE_INDEX][POINT_INDEX][1],"
        + "}"
    )
    if point_body_compact != expected_point_body:
        raise TableExtractionError("generated adapter point macro must expand x then y from the canonical raw array")

    table_macro_matches = list(_SOURCE_OWNED_TABLE_MACRO_PATTERN.finditer(source_text))
    if len(table_macro_matches) != 1:
        raise TableExtractionError("generated adapter table macro is missing")
    table_macro_match = table_macro_matches[0]
    table_macro_body = table_macro_match.group("body")
    table_body_compact = re.sub(r"\s+", "", table_macro_body).replace("\\", "")
    expected_table_body = (
        "constexprStickPointTABLE_SYMBOL[9]={"
        + "".join(
            f"SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX,{index}),"
            for index in range(EXPECTED_POINT_COUNT)
        )
        + "}"
    )
    if table_body_compact != expected_table_body:
        raise TableExtractionError("generated adapter table macro body contains extra or malformed tokens")
    expected_point_calls = [str(index) for index in range(EXPECTED_POINT_COUNT)]
    point_calls = re.findall(
        r"SOURCE_OWNED_GENERATED_TABLE_POINT\s*\(\s*TABLE_INDEX\s*,\s*(\d+)\s*\)\s*,?",
        table_macro_body,
    )
    if point_calls != expected_point_calls:
        raise TableExtractionError("generated adapter table macro must expand point indices 0 through 8 in order")
    all_point_calls = re.findall(
        r"SOURCE_OWNED_GENERATED_TABLE_POINT\s*\(\s*TABLE_INDEX\s*,\s*(\d+)\s*\)",
        source_text,
    )
    if all_point_calls != expected_point_calls:
        raise TableExtractionError("generated adapter contains extra or malformed point invocations")

    undef_match = re.search(
        r"\n#undef\s+SOURCE_OWNED_GENERATED_TABLE\s*$",
        source_text[table_macro_match.end() :],
        re.MULTILINE,
    )
    if undef_match is None:
        raise TableExtractionError("generated adapter table macro is not closed by its undefinition")
    adapter_tail = source_text[table_macro_match.end() : table_macro_match.end() + undef_match.start()]
    invocations_list: list[tuple[str, int]] = []
    for line in adapter_tail.splitlines():
        if "SOURCE_OWNED_GENERATED_TABLE_POINT" in line:
            raise TableExtractionError("generated adapter contains a point invocation outside its table macro")
        if "SOURCE_OWNED_GENERATED_TABLE" not in line:
            continue
        invocation = _SOURCE_OWNED_TABLE_INVOCATION_PATTERN.fullmatch(line.strip())
        if invocation is None:
            raise TableExtractionError("generated adapter contains a malformed table alias invocation")
        invocations_list.append((invocation.group("symbol"), int(invocation.group("index"))))
    invocations = tuple(invocations_list)
    expected = tuple((symbol, index) for index, (symbol, _name) in enumerate(TABLE_SYMBOL_TO_NAME))
    if invocations != expected:
        raise TableExtractionError(
            "generated adapter table aliases must exactly match the canonical 28-symbol order and indices"
        )
    return invocations


def required_table_symbols() -> tuple[str, ...]:
    return tuple(symbol for symbol, _name in TABLE_SYMBOL_TO_NAME)


def normalized_table_names() -> tuple[str, ...]:
    return tuple(name for _symbol, name in TABLE_SYMBOL_TO_NAME)


def runtime_table_ids() -> tuple[RuntimeTableId, ...]:
    return tuple(RuntimeTableId)


def runtime_table_id_names() -> tuple[str, ...]:
    return tuple(runtime_table_id.value for runtime_table_id in runtime_table_ids())


def source_symbol_by_normalized_name() -> dict[str, str]:
    return {name: symbol for symbol, name in TABLE_SYMBOL_TO_NAME}


def source_symbol_by_runtime_table_id() -> dict[RuntimeTableId, str]:
    source_symbols = source_symbol_by_normalized_name()
    return {
        runtime_table_id: source_symbols[runtime_table_id.value]
        for runtime_table_id in runtime_table_ids()
    }


def runtime_table_id_by_normalized_name() -> dict[str, RuntimeTableId]:
    return {runtime_table_id.value: runtime_table_id for runtime_table_id in runtime_table_ids()}


def build_runtime_config_interpreter_source_baseline(
    tables: dict[str, tuple[tuple[int, int], ...]],
    *,
    source_path: Path = DEFAULT_SOURCE_PATH,
) -> dict[str, object]:
    """Build the source-owned config-shaped baseline for the interpreter boundary."""

    table_references = []
    for runtime_table_id, normalized_name in zip(runtime_table_ids(), normalized_table_names()):
        table_references.append(
            {
                "runtime_table_id": runtime_table_id.value,
                "source_symbol": source_symbol_by_normalized_name()[normalized_name],
                "point_count": len(tables[normalized_name]),
                "shape": f"{CURRENT_BASELINE_CONFIG_TABLE_FAMILY}[{CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT}]",
                "value_source": _relative_path(source_path),
            }
        )

    return {
        "schema_name": CURRENT_BASELINE_CONFIG_SCHEMA_NAME,
        "schema_version": CURRENT_BASELINE_CONFIG_SCHEMA_VERSION,
        "status": CURRENT_BASELINE_CONFIG_STATUS,
        "mode_scope": CURRENT_BASELINE_CONFIG_MODE_SCOPE,
        "source_path": _relative_path(source_path),
        "interpreter_source_path": _relative_path(INTERPRETER_SOURCE_PATH),
        "source_owned": True,
        "runtime_loaded_config": False,
        "consumed_by_firmware": False,
        "validation_before_use": True,
        "fallback_policy": "known_good_source_owned_baseline",
        "fallback_table_id": CURRENT_BASELINE_CONFIG_FALLBACK_TABLE_ID,
        "table_family": CURRENT_BASELINE_CONFIG_TABLE_FAMILY,
        "table_count": len(tables),
        "expected_table_count": CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        "point_count_per_table": CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        "expected_point_count_per_table": CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        "runtime_table_ids": list(runtime_table_id_names()),
        "table_references": table_references,
        "caveats": [
            "not_runtime_loaded_config",
            "not_device_write",
            "not_protobuf_binary_write",
            "not_flashing_automation",
            "not_transport_payload",
            "not_storage_behavior",
            "source_owned_current_baseline_only",
            "validate_before_use",
            "fallback_to_known_good_if_validation_fails",
        ],
    }


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
        # Source boundary: StickPoint values are expected to be byte literals.
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


def _parse_generated_raw_tables(source_text: str) -> dict[str, tuple[tuple[int, int], ...]]:
    match = _GENERATED_RAW_TABLE_PATTERN.search(source_text)
    if match is None:
        return {}

    symbol_to_name = {symbol: name for symbol, name in TABLE_SYMBOL_TO_NAME}
    parsed: dict[str, tuple[tuple[int, int], ...]] = {}
    seen_indexes: set[int] = set()
    for row_match in _GENERATED_RAW_ROW_PATTERN.finditer(match.group("body")):
        index = int(row_match.group("index"))
        symbol = row_match.group("symbol")
        if symbol not in symbol_to_name:
            continue
        if index in seen_indexes:
            raise TableExtractionError(f"generated raw table array contains duplicate index {index}")
        seen_indexes.add(index)
        points = [
            (int(point.group("x")), int(point.group("y")))
            for point in _GENERATED_RAW_POINT_PATTERN.finditer(row_match.group("body"))
        ]
        if len(points) != EXPECTED_POINT_COUNT:
            raise TableExtractionError(f"{symbol} contains {len(points)} points, expected {EXPECTED_POINT_COUNT}")
        if any(not 0 <= x <= 255 or not 0 <= y <= 255 for x, y in points):
            raise TableExtractionError(f"{symbol} contains out-of-range generated table point")
        parsed[symbol_to_name[symbol]] = tuple(points)

    if len(parsed) != len(TABLE_SYMBOL_TO_NAME):
        return {}
    return parsed


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
    if not missing and len(parsed_symbols) == len(TABLE_SYMBOL_TO_NAME):
        return {name: parsed_symbols[symbol] for symbol, name in TABLE_SYMBOL_TO_NAME}

    generated_raw_tables = _parse_generated_raw_tables(source_text)
    if generated_raw_tables:
        return generated_raw_tables

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
    source_text = source_text.replace(GENERATED_LIKE_TABLES_INCLUDE, include_text, 1)
    if GENERATED_BASELINE_INCLUDE in source_text:
        source_text = source_text.replace(GENERATED_BASELINE_INCLUDE, GENERATED_BASELINE_PATH.read_text(encoding="utf-8"), 1)
    return source_text


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
