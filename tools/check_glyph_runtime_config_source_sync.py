#!/usr/bin/env python3
"""Fail-closed current source-owned runtime-config baseline sync check."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools"))

from extract_glyph_identity_runtime_tables import load_source_tables, runtime_table_id_names
from generate_source_owned_runtime_config import parse_source_owned_baseline_contract
from glyph_source_owned_overlay import semantic_digest

FIXTURES = (
    REPO_ROOT / "docs/runtime_config/fixtures/current_baseline_runtime_config_semantics_bridge.json",
    REPO_ROOT / "docs/runtime_config/fixtures/current_baseline_runtime_config_interpreter_source_baseline.json",
    REPO_ROOT / "docs/runtime_config/fixtures/current_baseline_extracted_config_preview.json",
)
EXPECTED_DIGEST = "b0082f068e0e552d479ec8ed8bf5867737a75a19e5e60aede55bafb72b883874"
EXPECTED_FINAL = "kLt1LowMagnitudeTable"


def load_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result
    payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(payload, dict):
        raise ValueError("fixture root must be an object")
    return payload


def main() -> int:
    try:
        source = load_source_tables()
        baseline = parse_source_owned_baseline_contract()
        tables = baseline["tables"]
        order = [table["table_symbol"] for table in tables]
        if len(source) != 28 or len(tables) != 28:
            raise ValueError("canonical extractor and baseline parser must each return 28 tables")
        if [table["table_name"] for table in tables] != list(runtime_table_id_names()):
            raise ValueError("canonical parser order disagrees with runtime table IDs")
        if order[-1] != EXPECTED_FINAL:
            raise ValueError("canonical final table drifted")
        if {table["table_name"]: tuple((p["x"], p["y"]) for p in table["points"]) for table in tables} != source:
            raise ValueError("canonical extractor and baseline parser points disagree")
        digest = semantic_digest(tables)
        if digest != EXPECTED_DIGEST:
            raise ValueError("canonical baseline digest drifted")
        for path in FIXTURES:
            fixture = load_json(path)
            if fixture.get("expected_table_count", fixture.get("table_count")) != 28:
                raise ValueError(f"{path.relative_to(REPO_ROOT)} is not a current 28-table fixture")
        print("glyph_runtime_config_source_sync: PASS")
        print(f"table_count={len(tables)}")
        print(f"semantic_digest={digest}")
        print(f"final_table={order[-1]}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("glyph_runtime_config_source_sync: FAIL")
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
