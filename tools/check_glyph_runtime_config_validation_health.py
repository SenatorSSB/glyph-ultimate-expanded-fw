#!/usr/bin/env python3
"""Validate the two-layer runtime-config validation-health record."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_health.json"
MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
CENSUS = ROOT / "docs/runtime_config/fixtures/glyph_checker_census.json"
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
        assert value["schema_version"] == 2
        census = value["repository_checker_census"]
        assert census["artifact"] == "docs/runtime_config/fixtures/glyph_checker_census.json"
        census_entries = json.loads(CENSUS.read_text(encoding="utf-8"), object_pairs_hook=pairs)["entries"]
        assert census["discovered_count"] == len(census_entries) and census["validated"] is True
        freshness = value["aggregate_census_freshness"]
        assert freshness == {
            "id": "checker_census_freshness",
            "path": "tools/check_glyph_checker_census.py",
            "load_bearing": True,
            "result": "PASS",
        }
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        entries = manifest["entries"]
        exclusions = manifest["strong_signal_exclusions"]
        scope = value["curated_runtime_config_scope"]
        assert scope == {
            "manifest_entry_count": len(entries),
            "current_load_bearing_count": sum(entry["applicability"] == "current" and entry["load_bearing"] for entry in entries),
            "historical_or_evidentiary_count": sum(entry["applicability"] == "historical_only" for entry in entries),
            "explicit_exclusion_count": len(exclusions),
        }
        found = {entry["id"]: entry for entry in value["checker_results"]}
        for item in DRIFT:
            assert found[item]["starting_configurator"]["exit_code"] == 1
            assert found[item]["feature_branch"]["result"] == "PASS"
        historical = {entry["id"]: entry for entry in value["historical_evidence"]}
        assert historical["identity_generated_evaluator_input"]["fixture"] == "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
        assert historical["identity_generated_evaluator_input"]["current_aggregate_pass"] is False
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"glyph_runtime_config_validation_health: FAIL: {exc}")
        return 1
    print(f"glyph_runtime_config_validation_health: PASS; census_count={len(census_entries)}; manifest_entries={len(entries)}; baseline={EXPECTED}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
