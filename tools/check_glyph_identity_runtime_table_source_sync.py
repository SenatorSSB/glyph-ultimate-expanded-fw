#!/usr/bin/env python3
"""Check source-parsed Glyph identity runtime tables against evaluator mirrors."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from extract_glyph_identity_runtime_tables import (
    CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
    CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
    CURRENT_BASELINE_CONFIG_FALLBACK_TABLE_ID,
    CURRENT_BASELINE_CONFIG_MODE_SCOPE,
    CURRENT_BASELINE_CONFIG_SCHEMA_NAME,
    CURRENT_BASELINE_CONFIG_SCHEMA_VERSION,
    CURRENT_BASELINE_CONFIG_STATUS,
    CURRENT_BASELINE_CONFIG_TABLE_FAMILY,
    DEFAULT_SOURCE_PATH,
    TableExtractionError,
    build_runtime_config_interpreter_source_baseline,
    load_source_tables,
    normalized_table_names,
    runtime_table_id_by_normalized_name,
    runtime_table_id_names,
    source_symbol_by_normalized_name,
    source_symbol_by_runtime_table_id,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_behavior_evaluator.py"
INTERPRETER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigInterpreter.hpp"
BASELINE_FIXTURE_PATH = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "current_baseline_runtime_config_semantics_bridge.json"

REQUIRED_INTERPRETER_PHRASES = (
    "source-owned runtime config interpreter boundary",
    "source-owned firmware constants, not runtime-loaded config",
    "validation-before-use",
    "fallback-to-known-good",
    "not generated at runtime",
    "do not treat this as serial/device write behavior",
    "values must remain source-synced with the checker suite",
)

_RUNTIME_TABLE_SYMBOL_NAMES_PATTERN = re.compile(
    r"constexpr\s+const\s+char\s*\*\s*"
    r"kRuntimeTableSymbolNames\s*\[\s*kRuntimeTableCount\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
_RUNTIME_TABLE_VIEW_PATTERN = re.compile(
    r"constexpr\s+RuntimeTableView\s+"
    r"(?P<symbol>k[A-Za-z0-9]+)\s*\[\s*(?P<size_token>kRuntimeTableCount|\d+)\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
_RUNTIME_TABLE_VIEW_ENTRY_PATTERN = re.compile(
    r"\{\s*RuntimeTableId::(?P<id>[A-Za-z0-9]+)\s*,\s*"
    r'"(?P<symbol_name>k[A-Za-z0-9]+Table)"\s*,\s*'
    r"(?P<table_symbol>k[A-Za-z0-9]+Table)\s*,\s*(?P<point_count_token>kRuntimeTablePointCount|\d+)\s*\}\s*,?",
)
@dataclass(frozen=True)
class TableMismatch:
    table_name: str
    detail: str
    source: object
    evaluator: object


def _relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_evaluator_tables(path: Path = EVALUATOR_PATH) -> dict[str, tuple[tuple[int, int], ...]]:
    module = _load_module(path, "glyph_identity_runtime_behavior_evaluator")
    tables = getattr(module, "TABLES", None)
    if not isinstance(tables, dict):
        raise RuntimeError("evaluator TABLES is missing or is not a dict")

    normalized: dict[str, tuple[tuple[int, int], ...]] = {}
    for name, table in tables.items():
        if not isinstance(name, str):
            raise RuntimeError(f"evaluator TABLES contains non-string name: {name!r}")
        try:
            normalized[name] = tuple((int(point[0]), int(point[1])) for point in table)
        except (TypeError, ValueError, IndexError) as exc:
            raise RuntimeError(f"evaluator table {name} is malformed") from exc
    return normalized


def load_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {_relative_path(path)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{_relative_path(path)} must contain a JSON object")
    return payload


def validate_interpreter_source_text(source_text: str) -> None:
    for required_string in (
        '#include "modes/UltimateRuntimeConfigInterpreter.hpp"',
        "SelectRuntimeTableId",
        "ValidateRuntimeConfigView",
        "LookupRuntimeTable",
        "LookupRuntimeStickPoint",
        "kSourceOwnedCurrentBaselineRuntimeConfig",
    ):
        if required_string not in source_text:
            raise RuntimeError(f"Ultimate.cpp missing required interpreter source string: {required_string}")


def validate_interpreter_header(
    interpreter_text: str,
    source_tables: dict[str, tuple[tuple[int, int], ...]],
    baseline_fixture: dict[str, object],
) -> None:
    lowered = interpreter_text.lower()
    for phrase in REQUIRED_INTERPRETER_PHRASES:
        if phrase not in lowered:
            raise RuntimeError(f"interpreter header missing required phrase: {phrase}")

    for required_symbol in (
        "kRuntimeConfigSchemaName",
        "kRuntimeTableSymbolNames",
        "RuntimeTableId",
        "RuntimeTableView",
        "RuntimeConfigView",
        "StringsEqual",
        "FindRuntimeTableView",
        "kSourceOwnedCurrentBaselineRuntimeTables",
        "kKnownGoodRuntimeConfig",
        "kSourceOwnedCurrentBaselineRuntimeConfig",
    ):
        if required_symbol not in interpreter_text:
            raise RuntimeError(f"interpreter header missing required symbol: {required_symbol}")

    symbol_names_match = _RUNTIME_TABLE_SYMBOL_NAMES_PATTERN.search(interpreter_text)
    if symbol_names_match is None:
        raise RuntimeError("interpreter header missing RuntimeTableSymbolNames array")
    parsed_symbol_names = re.findall(r'"([^"]+)"', symbol_names_match.group("body"))
    expected_symbol_names = [source_symbol_by_normalized_name()[name] for name in normalized_table_names()]
    if parsed_symbol_names != expected_symbol_names:
        raise RuntimeError("interpreter header runtime table symbol name array mismatch")

    table_view_match = _RUNTIME_TABLE_VIEW_PATTERN.search(interpreter_text)
    if table_view_match is None:
        raise RuntimeError("interpreter header missing RuntimeTableView baseline array")
    table_view_symbol = table_view_match.group("symbol")
    table_view_size_token = table_view_match.group("size_token")
    table_view_body = table_view_match.group("body")
    if table_view_size_token not in {"kRuntimeTableCount", str(CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT)}:
        raise RuntimeError("interpreter header RuntimeTableView array size must be kRuntimeTableCount")

    seen_ids: set[str] = set()
    seen_symbols: set[str] = set()
    parsed_entries = 0
    for entry_match in _RUNTIME_TABLE_VIEW_ENTRY_PATTERN.finditer(table_view_body):
        parsed_entries += 1
        table_id = entry_match.group("id")
        symbol_name = entry_match.group("symbol_name")
        table_symbol = entry_match.group("table_symbol")
        point_count_token = entry_match.group("point_count_token")

        if table_id in seen_ids:
            raise RuntimeError(f"interpreter header contains duplicate runtime table id: {table_id}")
        if table_symbol in seen_symbols:
            raise RuntimeError(f"interpreter header contains duplicate runtime table symbol: {table_symbol}")

        seen_ids.add(table_id)
        seen_symbols.add(table_symbol)

        expected_symbol = source_symbol_by_normalized_name().get(table_id)
        if expected_symbol is None:
            raise RuntimeError(f"interpreter header contains unexpected runtime table id: {table_id}")
        if symbol_name != expected_symbol:
            raise RuntimeError(f"interpreter header runtime table symbol-name mismatch for {table_id}")
        if table_symbol != expected_symbol:
            raise RuntimeError(f"interpreter header table symbol mismatch for {table_id}")
        if point_count_token not in {"kRuntimeTablePointCount", str(CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT)}:
            raise RuntimeError(f"interpreter header table {table_id} must contain 9 points")
        if source_tables.get(table_id) is None:
            raise RuntimeError(f"interpreter header table id missing from source baseline: {table_id}")

    if parsed_entries != CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT:
        raise RuntimeError(
            "interpreter header RuntimeTableView array declares "
            f"{CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT} entries but parsed {parsed_entries}"
        )

    expected_names = set(normalized_table_names())
    if seen_ids != expected_names:
        missing = sorted(expected_names - seen_ids)
        unexpected = sorted(seen_ids - expected_names)
        raise RuntimeError(
            "interpreter header runtime table id set mismatch "
            f"missing={missing} unexpected={unexpected}"
        )

    config_anchor = "constexpr RuntimeConfigView kKnownGoodRuntimeConfig = {"
    config_start = interpreter_text.find(config_anchor)
    if config_start < 0:
        raise RuntimeError("interpreter header missing RuntimeConfigView baseline")
    config_end = interpreter_text.find("};", config_start)
    if config_end < 0:
        raise RuntimeError("interpreter header missing RuntimeConfigView closing brace")
    config_block = interpreter_text[config_start:config_end]
    if "kRuntimeConfigSchemaName" not in config_block:
        raise RuntimeError("interpreter RuntimeConfigView baseline missing token: kRuntimeConfigSchemaName")
    if "kSourceOwnedCurrentBaselineRuntimeTables" not in config_block:
        raise RuntimeError("interpreter RuntimeConfigView baseline missing token: kSourceOwnedCurrentBaselineRuntimeTables")
    if "RuntimeTableId::Default" not in config_block:
        raise RuntimeError("interpreter RuntimeConfigView baseline missing token: RuntimeTableId::Default")
    if "kRuntimeConfigSchemaVersion" not in config_block and "1" not in config_block:
        raise RuntimeError("interpreter RuntimeConfigView baseline missing schema version")
    if "kRuntimeTableCount" not in config_block and "27" not in config_block:
        raise RuntimeError("interpreter RuntimeConfigView baseline missing table count")
    if "constexpr RuntimeConfigView kSourceOwnedCurrentBaselineRuntimeConfig = kKnownGoodRuntimeConfig;" not in interpreter_text:
        raise RuntimeError("interpreter source-owned baseline alias missing")
    if "kSourceOwnedCurrentBaselineRuntimeConfig" not in interpreter_text:
        raise RuntimeError("interpreter source-owned current baseline alias missing")

    interpreter_baseline = build_runtime_config_interpreter_source_baseline(source_tables)
    fixture_baseline = baseline_fixture.get("interpreter_source_baseline")
    if fixture_baseline != interpreter_baseline:
        raise RuntimeError("interpreter baseline fixture does not match extracted baseline")

    runtime_table_ids = fixture_baseline.get("runtime_table_ids") if isinstance(fixture_baseline, dict) else None
    if runtime_table_ids != list(runtime_table_id_names()):
        raise RuntimeError("interpreter baseline runtime_table_ids drifted from source order")

    table_references = fixture_baseline.get("table_references") if isinstance(fixture_baseline, dict) else None
    if not isinstance(table_references, list) or len(table_references) != CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT:
        raise RuntimeError("interpreter baseline table_references must contain 27 entries")
    for index, entry in enumerate(table_references):
        if not isinstance(entry, dict):
            raise RuntimeError(f"interpreter baseline table_references[{index}] must be an object")
        runtime_table_id = entry.get("runtime_table_id")
        source_symbol = entry.get("source_symbol")
        point_count = entry.get("point_count")
        shape = entry.get("shape")
        value_source = entry.get("value_source")
        expected_id = runtime_table_id_names()[index]
        if runtime_table_id != expected_id:
            raise RuntimeError(f"interpreter baseline table_references[{index}].runtime_table_id must be {expected_id!r}")
        if source_symbol != source_symbol_by_runtime_table_id()[runtime_table_id_by_normalized_name()[expected_id]]:
            raise RuntimeError(f"interpreter baseline table_references[{index}].source_symbol mismatch")
        if point_count != CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT:
            raise RuntimeError(f"interpreter baseline table_references[{index}].point_count must be 9")
        if shape != "StickPoint[9]":
            raise RuntimeError(f"interpreter baseline table_references[{index}].shape must be StickPoint[9]")
        if value_source != "src/modes/Ultimate.cpp":
            raise RuntimeError(f"interpreter baseline table_references[{index}].value_source must be src/modes/Ultimate.cpp")


def compare_tables(
    source_tables: dict[str, tuple[tuple[int, int], ...]],
    evaluator_tables: dict[str, tuple[tuple[int, int], ...]],
) -> list[TableMismatch]:
    mismatches: list[TableMismatch] = []
    expected_names = set(normalized_table_names())
    source_names = set(source_tables)
    evaluator_names = set(evaluator_tables)

    for missing in sorted(expected_names - source_names):
        mismatches.append(TableMismatch(missing, "missing_from_source", "required table", "missing"))
    for missing in sorted(expected_names - evaluator_names):
        mismatches.append(TableMismatch(missing, "missing_from_evaluator", "required table", "missing"))

    for unexpected in sorted(source_names - expected_names):
        mismatches.append(TableMismatch(unexpected, "unexpected_source_table", "unexpected", "not expected"))
    for unexpected in sorted(evaluator_names - expected_names):
        mismatches.append(TableMismatch(unexpected, "unexpected_evaluator_table", "not expected", "unexpected"))

    for name in normalized_table_names():
        source_table = source_tables.get(name)
        evaluator_table = evaluator_tables.get(name)
        if source_table is None or evaluator_table is None:
            continue
        if len(source_table) != len(evaluator_table):
            mismatches.append(TableMismatch(name, "length_differs", len(source_table), len(evaluator_table)))
            continue
        for index, (source_point, evaluator_point) in enumerate(zip(source_table, evaluator_table)):
            if source_point != evaluator_point:
                mismatches.append(
                    TableMismatch(
                        name,
                        f"point_{index}_differs",
                        list(source_point),
                        list(evaluator_point),
                    )
                )

    return mismatches


def print_mismatches(mismatches: list[TableMismatch]) -> None:
    if not mismatches:
        return
    print("mismatches:")
    for mismatch in mismatches:
        print(
            "- "
            f"table={mismatch.table_name} "
            f"detail={mismatch.detail} "
            f"source={mismatch.source!r} "
            f"evaluator={mismatch.evaluator!r}"
        )


def main() -> int:
    print("glyph_identity_runtime_table_source_sync")
    print(f"source_path={_relative_path(DEFAULT_SOURCE_PATH)}")
    print(f"evaluator_path={_relative_path(EVALUATOR_PATH)}")
    print(f"interpreter_path={_relative_path(INTERPRETER_PATH)}")
    print(f"baseline_fixture={_relative_path(BASELINE_FIXTURE_PATH)}")

    try:
        source_tables = load_source_tables(DEFAULT_SOURCE_PATH)
        evaluator_tables = load_evaluator_tables(EVALUATOR_PATH)
        source_text = Path(DEFAULT_SOURCE_PATH).read_text(encoding="utf-8")
        validate_interpreter_source_text(source_text)
        interpreter_text = INTERPRETER_PATH.read_text(encoding="utf-8")
        baseline_fixture = load_json_object(BASELINE_FIXTURE_PATH)
        validate_interpreter_header(interpreter_text, source_tables, baseline_fixture)
    except (OSError, RuntimeError, TableExtractionError) as exc:
        print("status=FAIL")
        print("compared_table_count=0")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1

    mismatches = compare_tables(source_tables, evaluator_tables)
    print(f"status={'FAIL' if mismatches else 'PASS'}")
    print(f"compared_table_count={len(normalized_table_names())}")
    print("hardware_status=not_new_hardware_result")
    print_mismatches(mismatches)
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
