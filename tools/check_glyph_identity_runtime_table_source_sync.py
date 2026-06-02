#!/usr/bin/env python3
"""Check source-parsed Glyph identity runtime tables against evaluator mirrors."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from extract_glyph_identity_runtime_tables import (
    DEFAULT_SOURCE_PATH,
    TableExtractionError,
    load_source_tables,
    normalized_table_names,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_behavior_evaluator.py"


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

    try:
        source_tables = load_source_tables(DEFAULT_SOURCE_PATH)
        evaluator_tables = load_evaluator_tables(EVALUATOR_PATH)
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
