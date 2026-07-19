#!/usr/bin/env python3
"""Strict source-owned candidate generation with explicit ownership."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from generate_source_owned_runtime_config import (
    EXPECTED_ARTIFACT_KIND,
    EXPECTED_AXES_PER_POINT,
    EXPECTED_POINTS_PER_TABLE,
    EXPECTED_SCHEMA_VERSION,
    GeneratorContractError,
    parse_source_owned_baseline_contract,
    parse_source_baseline_table_order,
    SOURCE_INTERPRETER,
    validate_tables,
    validate_shape,
)

EXPECTED_TABLE_COUNT = 28
MODES = {"full_replacement", "overlay_preserve", "reject_partial"}
PRODUCTION_FORBIDDEN_PROVENANCE = {"example", "demonstration", "fixture"}


class OverlayContractError(GeneratorContractError):
    """Raised when explicit generation policy or ownership is invalid."""


def fail(message: str) -> None:
    raise OverlayContractError(message)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def semantic_digest(tables: list[dict[str, Any]]) -> str:
    value = [
        {
            "table_id": table["table_id"],
            "table_symbol": table["table_symbol"],
            "points": table["points"],
        }
        for table in tables
    ]
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def baseline_contract() -> dict[str, Any]:
    baseline = parse_source_owned_baseline_contract()
    baseline["baseline_id"] = "current_source_owned_baseline"
    baseline["source_path"] = "src/modes/UltimateIdentityRuntimeTables.hpp"
    baseline["source_interpreter_path"] = "src/modes/UltimateRuntimeConfigInterpreter.hpp"
    baseline["semantic_digest"] = semantic_digest(baseline["tables"])
    return baseline


def _table_shape() -> dict[str, int]:
    return {
        "table_count": EXPECTED_TABLE_COUNT,
        "points_per_table": EXPECTED_POINTS_PER_TABLE,
        "axes_per_point": EXPECTED_AXES_PER_POINT,
    }


def _normalize_input_tables(payload: dict[str, Any], *, full: bool) -> list[dict[str, Any]]:
    tables = payload.get("tables")
    if not isinstance(tables, list):
        fail("tables must be a list")
    if full and len(tables) != EXPECTED_TABLE_COUNT:
        fail(f"full_replacement requires exactly {EXPECTED_TABLE_COUNT} tables")
    if not full and len(tables) > EXPECTED_TABLE_COUNT:
        fail("overlay tables exceed active table count")
    shape = _table_shape()
    if not full:
        normalized = []
        for index, table in enumerate(tables):
            if not isinstance(table, dict):
                fail(f"tables[{index}] must be an object")
            points = table.get("points")
            if not isinstance(points, list) or len(points) != EXPECTED_POINTS_PER_TABLE:
                fail(f"tables[{index}] must contain exactly {EXPECTED_POINTS_PER_TABLE} points")
            normalized_points = []
            for point_index, point in enumerate(points):
                if not isinstance(point, dict) or set(point) != {"x", "y"}:
                    fail(f"tables[{index}].points[{point_index}] must contain x and y only")
                if any(not isinstance(point[key], int) or isinstance(point[key], bool) or not 0 <= point[key] <= 255 for key in ("x", "y")):
                    fail(f"tables[{index}].points[{point_index}] must use integer byte coordinates")
                normalized_points.append({"x": point["x"], "y": point["y"]})
            normalized.append({"table_id": table.get("table_id"), "table_name": table.get("table_name"), "table_symbol": table.get("table_symbol"), "points": normalized_points})
    else:
        normalized = validate_tables({"tables": tables}, shape)
    symbols = parse_source_baseline_table_order(SOURCE_INTERPRETER.read_text(encoding="utf-8"))
    by_symbol: dict[str, dict[str, Any]] = {}
    for index, table in enumerate(normalized):
        table_id = table.get("table_id")
        if table_id is None:
            fail("every table must identify an explicit table_id")
        symbol = table.get("table_symbol") or symbols[table_id]
        if symbol != symbols[table_id]:
            fail(f"table {table_id} has unknown or mismatched table symbol: {symbol}")
        if symbol in by_symbol:
            fail(f"duplicate table symbol: {symbol}")
        table["table_symbol"] = symbol
        table["table_name"] = symbol.removeprefix("k").removesuffix("Table")
        by_symbol[symbol] = table
    return [by_symbol[symbol] for symbol in symbols if symbol in by_symbol]


def _validate_baseline_identity(identity: Any, baseline: dict[str, Any]) -> None:
    if not isinstance(identity, dict):
        fail("overlay_preserve requires baseline identity")
    required = {"baseline_id", "source_path", "semantic_digest", "table_count"}
    missing = sorted(required - set(identity))
    if missing:
        fail("baseline identity missing: " + ", ".join(missing))
    if identity["baseline_id"] != baseline["baseline_id"]:
        fail("baseline_id is not the current source-owned baseline")
    if identity["source_path"] != baseline["source_path"]:
        fail("baseline source_path is not the current source-owned table source")
    if identity["table_count"] != EXPECTED_TABLE_COUNT:
        fail(f"baseline table_count must be {EXPECTED_TABLE_COUNT}")
    if identity["semantic_digest"] != baseline["semantic_digest"]:
        fail("baseline semantic digest mismatch")


def _validate_provenance(payload: dict[str, Any], *, production: bool, test_only_override: bool) -> None:
    provenance = payload.get("provenance")
    profile_name = str(payload.get("profile_name", ""))
    example = profile_name.startswith("example_") or provenance in PRODUCTION_FORBIDDEN_PROVENANCE
    if production and example and not test_only_override:
        fail("production candidate rejects example/demonstration/fixture provenance")


def generate_overlay_payload(
    payload: dict[str, Any],
    *,
    production: bool = False,
    test_only_override: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    mode = payload.get("generation_mode")
    if mode not in MODES:
        fail("generation_mode must be one of full_replacement, overlay_preserve, reject_partial")
    _validate_provenance(payload, production=production, test_only_override=test_only_override)
    baseline = baseline_contract()
    if mode == "reject_partial":
        tables = payload.get("tables")
        if not isinstance(tables, list) or len(tables) != EXPECTED_TABLE_COUNT:
            fail("reject_partial refuses partial input before generation")
        fail("reject_partial refuses candidate generation")
    if mode == "full_replacement":
        if "owned_tables" in payload:
            fail("full_replacement must not use overlay ownership")
        tables = _normalize_input_tables(payload, full=True)
        owned = [table["table_symbol"] for table in tables]
        output_tables = tables
        action_for = lambda _symbol: "replace_explicit_owned"
        reason_for = lambda _symbol: "full replacement explicitly supplies every active table"
        ownership_source = "candidate_input_full_replacement"
    else:
        _validate_baseline_identity(payload.get("baseline"), baseline)
        owned = payload.get("owned_tables")
        if not isinstance(owned, list) or not owned:
            fail("overlay_preserve requires a non-empty owned_tables list")
        if len(set(owned)) != len(owned):
            fail("duplicate owned table")
        symbols = parse_source_baseline_table_order(SOURCE_INTERPRETER.read_text(encoding="utf-8"))
        unknown = sorted(set(owned) - set(symbols))
        if unknown:
            fail("unknown owned table symbols: " + ", ".join(unknown))
        supplied = _normalize_input_tables(payload, full=False)
        supplied_by_symbol = {table["table_symbol"]: table for table in supplied}
        if set(supplied_by_symbol) - set(owned):
            fail("table present but not explicitly owned")
        missing = sorted(set(owned) - set(supplied_by_symbol))
        if missing:
            fail("owned table missing input: " + ", ".join(missing))
        baseline_by_symbol = {table["table_symbol"]: table for table in baseline["tables"]}
        output_tables = [supplied_by_symbol.get(symbol, baseline_by_symbol[symbol]) for symbol in symbols]
        action_for = lambda symbol: "replace_explicit_owned" if symbol in owned else "preserve_source_owned_baseline"
        reason_for = lambda symbol: "explicit ownership permits replacement" if symbol in owned else "table is unowned and copied from selected baseline"
        ownership_source = "candidate_input_owned_tables" if owned else "none"
    manifest = []
    baseline_by_symbol = {table["table_symbol"]: table for table in baseline["tables"]}
    for table in output_tables:
        symbol = table["table_symbol"]
        base = baseline_by_symbol[symbol]
        changed = table["points"] != base["points"]
        if mode == "overlay_preserve" and not changed and symbol in owned:
            action = "replace_explicit_owned"
        else:
            action = action_for(symbol)
        if action == "preserve_source_owned_baseline" and changed:
            fail(f"unowned table changed from baseline: {symbol}")
        manifest.append({
            "table_id": table["table_id"],
            "table_symbol": symbol,
            "ownership_source": ownership_source if action == "replace_explicit_owned" else "current_source_owned_baseline",
            "baseline_semantic_digest": semantic_digest([base]),
            "candidate_semantic_digest": semantic_digest([table]),
            "changed": changed,
            "action": action,
            "reason": reason_for(symbol),
        })
    output = dict(payload)
    output["tables"] = output_tables
    output["table_shape"] = _table_shape()
    output["semantic_digest"] = semantic_digest(output_tables)
    output["baseline"] = {
        "baseline_id": baseline["baseline_id"],
        "source_path": baseline["source_path"],
        "semantic_digest": baseline["semantic_digest"],
        "table_count": EXPECTED_TABLE_COUNT,
    }
    return output, {"generation_mode": mode, "baseline": output["baseline"], "manifest": manifest, "output_semantic_digest": output["semantic_digest"]}
