#!/usr/bin/env python3
"""Validate generated Glyph identity runtime config as evaluator table input.

This is a tools/docs-only checker. It does not generate firmware source, load
runtime config, write a device, or validate hardware behavior.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
BEHAVIOR_CASES_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_identity_runtime_behavior_cases_2026-05-28.json"
)
PROTOTYPE_CHECKER_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_generated_config_prototype.py"
EVALUATOR_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_behavior_evaluator.py"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_identity_runtime_generated_config_prototype",
    "contract_version": 1,
    "mode_scope": "MODE_ULTIMATE",
    "source_status": "source_backed_prototype_not_runtime_loaded",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
}
REQUIRED_CONFIG_OBJECTS = ("tables", "role_bindings", "priority_model", "hard_overrides")

def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        fail(f"{display(path)} must contain a JSON object")
    return data


def load_evaluator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("glyph_identity_runtime_behavior_evaluator", EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        fail(f"could not load evaluator module from {display(EVALUATOR_PATH)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_prototype_checker() -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, str(PROTOTYPE_CHECKER_PATH.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode == 0, output


def validate_config_metadata(config: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if config.get(key) != expected:
            fail(f"{key} must be {expected}")

    for key in REQUIRED_CONFIG_OBJECTS:
        if not isinstance(config.get(key), dict) or not config[key]:
            fail(f"{key} must be a non-empty object")


def convert_tables(config: dict[str, Any], expected_names: set[str]) -> dict[str, tuple[tuple[int, int], ...]]:
    tables = config.get("tables")
    if not isinstance(tables, dict):
        fail("tables must be an object")

    actual_names = set(tables)
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        unexpected = sorted(actual_names - expected_names)
        fail(f"generated config table names mismatch missing={missing} unexpected={unexpected}")

    converted: dict[str, tuple[tuple[int, int], ...]] = {}
    for table_name in sorted(expected_names):
        table = tables[table_name]
        if not isinstance(table, list):
            fail(f"tables.{table_name} must be a list")
        if len(table) != 9:
            fail(f"tables.{table_name} must contain 9 points")

        points: list[tuple[int, int]] = []
        for point_index, point in enumerate(table):
            label = f"tables.{table_name}[{point_index}]"
            if not isinstance(point, list) or len(point) != 2:
                fail(f"{label} must be [int, int]")
            x, y = point
            if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, int) or not isinstance(y, int):
                fail(f"{label} must be [int, int] without booleans")
            if not 0 <= x <= 255 or not 0 <= y <= 255:
                fail(f"{label} coordinates must be in [0,255]")
            points.append((x, y))
        converted[table_name] = tuple(points)

    return converted


def evaluation_snapshot(evaluation: Any) -> dict[str, Any]:
    snapshot: dict[str, Any] = {"table_name": evaluation.table_name}
    for field in ("effective_directions", "roles", "outputs"):
        value = getattr(evaluation, field)
        if is_dataclass(value):
            snapshot[field] = asdict(value)
        else:
            snapshot[field] = value
    return snapshot


def format_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def print_mismatches(mismatches: list[Any]) -> None:
    if not mismatches:
        return

    print("mismatches:")
    for mismatch in mismatches:
        print(
            "- "
            f"case_id={mismatch.case_id} "
            f"field={mismatch.field} "
            f"expected={format_value(mismatch.expected)} "
            f"actual={format_value(mismatch.actual)}"
        )


def evaluate_cases_with_tables(
    evaluator: ModuleType,
    cases: list[dict[str, Any]],
    tables: dict[str, tuple[tuple[int, int], ...]],
) -> tuple[list[Any], dict[str, dict[str, Any]]]:
    mismatches: list[Any] = []
    snapshots: dict[str, dict[str, Any]] = {}
    original_tables = evaluator.TABLES
    evaluator.TABLES = tables
    try:
        for case in cases:
            case_id = case.get("case_id", "<unknown>")
            try:
                evaluation = evaluator.evaluate_case(case)
            except evaluator.EvaluationError as exc:
                mismatches.append(evaluator.Mismatch(case_id, "case", "evaluable source-backed input", str(exc)))
                continue
            mismatches.extend(evaluator.compare_expected(case, evaluation))
            snapshots[case_id] = evaluation_snapshot(evaluation)
    finally:
        evaluator.TABLES = original_tables
    return mismatches, snapshots


def main() -> int:
    print("glyph_identity_runtime_generated_config_evaluator_input")

    prototype_checker_passed, prototype_checker_output = run_prototype_checker()
    if not prototype_checker_passed:
        print("status=FAIL")
        print("cases_evaluated=0")
        print("config_table_count=0")
        print("prototype_checker_status=FAIL")
        print("hardware_status=not_new_hardware_result")
        print("nunchuk_status=preserved_but_not_hardware_validated")
        if prototype_checker_output:
            print("prototype_checker_output:")
            print(prototype_checker_output)
        return 1

    try:
        evaluator = load_evaluator_module()
        config = load_json(CONFIG_FIXTURE_PATH)
        fixture = load_json(BEHAVIOR_CASES_FIXTURE_PATH)
        cases = fixture.get("cases")
        if not isinstance(cases, list):
            fail("behavior cases fixture must contain cases list")

        validate_config_metadata(config)
        generated_tables = convert_tables(config, set(evaluator.TABLES))

        baseline_mismatches, baseline_snapshots = evaluate_cases_with_tables(evaluator, cases, evaluator.TABLES)
        generated_mismatches, generated_snapshots = evaluate_cases_with_tables(evaluator, cases, generated_tables)

        parity_mismatches: list[Any] = []
        for case in cases:
            case_id = case.get("case_id", "<unknown>")
            if generated_snapshots.get(case_id) != baseline_snapshots.get(case_id):
                parity_mismatches.append(
                    evaluator.Mismatch(
                        case_id,
                        "generated_config_evaluator_parity",
                        baseline_snapshots.get(case_id),
                        generated_snapshots.get(case_id),
                    )
                )
    except (AssertionError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print("cases_evaluated=0")
        print("config_table_count=0")
        print("prototype_checker_status=PASS")
        print("hardware_status=not_new_hardware_result")
        print("nunchuk_status=preserved_but_not_hardware_validated")
        print(f"error={exc}")
        return 1

    mismatches = baseline_mismatches + generated_mismatches + parity_mismatches
    print(f"status={'FAIL' if mismatches else 'PASS'}")
    print(f"cases_evaluated={len(cases)}")
    print(f"config_table_count={len(generated_tables)}")
    print("prototype_checker_status=PASS")
    print("hardware_status=not_new_hardware_result")
    print("nunchuk_status=preserved_but_not_hardware_validated")
    print_mismatches(mismatches)
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
