#!/usr/bin/env python3
"""Validate the committed, pinned runtime-config validation-health inventory."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_health.json"
EXPECTED = "116d34322837fe1f6f724c820b49ccb0d24d6787"
DRIFT = {"identity_table_source_sync", "runtime_semantics_evaluator_bridge"}

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def main() -> int:
    try:
        value = json.loads(PATH.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        assert value["starting_commit"] == EXPECTED
        baseline = value["canonical_baseline"]
        assert baseline == {"semantic_digest": "9ea314bd17680d8353198ac174e59faf84c419fcd95a4ef3db24b3bd7e0f2970", "table_count": 28, "final_table": "kLt1LowMagnitudeTable"}
        entries = value["checker_inventory"]
        assert isinstance(entries, list) and len(entries) >= 17
        ids = [entry["id"] for entry in entries]
        assert len(ids) == len(set(ids))
        found = {entry["id"]: entry for entry in entries}
        for item in DRIFT:
            assert found[item]["result"] == "PRE_EXISTING_FIXTURE_DRIFT"
            assert found[item]["load_bearing"] is True
        for entry in entries:
            assert (ROOT / entry["path"]).is_file()
            assert entry["result"] != "PASS" or entry["classification"] not in {"UNSAFE_OR_MUTATING", "HISTORICAL_BRANCH_EVIDENCE_CHECK", "HARDWARE_RESULT_CHECK"}
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"glyph_runtime_config_validation_health: FAIL: {exc}")
        return 1
    print(f"glyph_runtime_config_validation_health: PASS; inventory_count={len(entries)}; baseline={EXPECTED}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
