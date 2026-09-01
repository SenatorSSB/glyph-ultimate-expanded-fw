#!/usr/bin/env python3
"""Validate the exact, source-correspondent runtime-config health record."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_health.json"
MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
CENSUS = ROOT / "docs/runtime_config/fixtures/glyph_checker_census.json"
MARKDOWN = ROOT / "docs/runtime_config/runtime_config_validation_health.md"
EXPECTED = "116d34322837fe1f6f724c820b49ccb0d24d6787"
TOP_KEYS = ["schema_version", "starting_commit", "canonical_baseline", "repository_checker_census", "aggregate_census_freshness", "curated_runtime_config_scope", "checker_results", "known_preexisting_failures", "historical_evidence"]
SUMMARY = re.compile(r"<!-- validation-health-summary:start -->\nCurrent summary: manifest entries = (?P<manifest>\d+); current load-bearing checks = (?P<load_bearing>\d+)\.\n<!-- validation-health-summary:end -->")


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def exact(value: Any, keys: list[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or list(value) != keys:
        raise ValueError(f"{label} must have exact keys in reviewed order")
    return value


def string(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")


def integer(value: Any, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")


def boolean(value: Any, label: str) -> None:
    if type(value) is not bool:
        raise ValueError(f"{label} must be a boolean")


def validate_types(value: dict[str, Any]) -> None:
    integer(value["schema_version"], "schema_version")
    string(value["starting_commit"], "starting_commit")
    baseline = exact(value["canonical_baseline"], ["semantic_digest", "table_count", "final_table"], "canonical_baseline")
    string(baseline["semantic_digest"], "canonical_baseline.semantic_digest")
    integer(baseline["table_count"], "canonical_baseline.table_count")
    string(baseline["final_table"], "canonical_baseline.final_table")
    census = exact(value["repository_checker_census"], ["artifact", "discovered_count", "validated"], "repository_checker_census")
    string(census["artifact"], "repository_checker_census.artifact")
    integer(census["discovered_count"], "repository_checker_census.discovered_count")
    boolean(census["validated"], "repository_checker_census.validated")
    aggregate = exact(value["aggregate_census_freshness"], ["id", "path", "load_bearing", "result"], "aggregate_census_freshness")
    string(aggregate["id"], "aggregate_census_freshness.id")
    string(aggregate["path"], "aggregate_census_freshness.path")
    boolean(aggregate["load_bearing"], "aggregate_census_freshness.load_bearing")
    string(aggregate["result"], "aggregate_census_freshness.result")
    scope = exact(value["curated_runtime_config_scope"], ["manifest_entry_count", "current_load_bearing_count", "historical_or_evidentiary_count", "explicit_exclusion_count"], "curated_runtime_config_scope")
    for key in scope:
        integer(scope[key], f"curated_runtime_config_scope.{key}")
    if not isinstance(value["checker_results"], list) or not isinstance(value["known_preexisting_failures"], list) or not isinstance(value["historical_evidence"], list):
        raise ValueError("health record collections must be lists")
    for index, item in enumerate(value["checker_results"]):
        if not isinstance(item, dict):
            raise ValueError(f"checker_results[{index}] must be an object")
        record = exact(item, ["id", "path", "classification", "starting_configurator", "feature_branch"], f"checker_results[{index}]")
        for key in ("id", "path", "classification"):
            string(record[key], f"checker_results[{index}].{key}")
        starting = exact(record["starting_configurator"], ["exit_code", "error"], f"checker_results[{index}].starting_configurator")
        integer(starting["exit_code"], f"checker_results[{index}].starting_configurator.exit_code")
        string(starting["error"], f"checker_results[{index}].starting_configurator.error")
        feature = exact(record["feature_branch"], ["result"], f"checker_results[{index}].feature_branch")
        string(feature["result"], f"checker_results[{index}].feature_branch.result")
    for index, item in enumerate(value["known_preexisting_failures"]):
        if not isinstance(item, dict):
            raise ValueError(f"known_preexisting_failures[{index}] must be an object")
        record = exact(item, ["id", "result", "starting_configurator_exit_code"], f"known_preexisting_failures[{index}]")
        string(record["id"], f"known_preexisting_failures[{index}].id")
        string(record["result"], f"known_preexisting_failures[{index}].result")
        integer(record["starting_configurator_exit_code"], f"known_preexisting_failures[{index}].starting_configurator_exit_code")
    for index, item in enumerate(value["historical_evidence"]):
        if not isinstance(item, dict):
            raise ValueError(f"historical_evidence[{index}] must be an object")
        has_fixture = isinstance(item, dict) and item.get("id") == "identity_generated_evaluator_input"
        keys = ["id", "path", "fixture", "classification", "current_aggregate_pass"] if has_fixture else ["id", "path", "classification", "current_aggregate_pass"]
        record = exact(item, keys, f"historical_evidence[{index}]")
        string(record["id"], f"historical_evidence[{index}].id")
        string(record["path"], f"historical_evidence[{index}].path")
        if has_fixture:
            string(record["fixture"], f"historical_evidence[{index}].fixture")
        string(record["classification"], f"historical_evidence[{index}].classification")
        boolean(record["current_aggregate_pass"], f"historical_evidence[{index}].current_aggregate_pass")


def validate_summary(text: str, expected: tuple[int, int]) -> None:
    if text.count("<!-- validation-health-summary:start -->") != 1 or text.count("<!-- validation-health-summary:end -->") != 1:
        raise ValueError("Markdown must contain exactly one summary marker pair")
    matches = SUMMARY.findall(text)
    if len(matches) != 1 or (int(matches[0][0]), int(matches[0][1])) != expected:
        raise ValueError("Markdown summary does not match derived counts")


def validate_health(value: dict[str, Any], census_value: dict[str, Any], manifest: dict[str, Any]) -> None:
    exact(value, TOP_KEYS, "health record")
    validate_types(value)
    if value["schema_version"] != 3 or value["starting_commit"] != EXPECTED:
        raise ValueError("health schema or starting commit is incorrect")
    if value["canonical_baseline"] != {"semantic_digest": "b0082f068e0e552d479ec8ed8bf5867737a75a19e5e60aede55bafb72b883874", "table_count": 28, "final_table": "kLt1LowMagnitudeTable"}:
        raise ValueError("canonical baseline does not match source-owned baseline")
    if value["repository_checker_census"] != {"artifact": "docs/runtime_config/fixtures/glyph_checker_census.json", "discovered_count": len(census_value["entries"]), "validated": True}:
        raise ValueError("checker census correspondence is stale")
    if value["aggregate_census_freshness"] != {"id": "checker_census_freshness", "path": "tools/check_glyph_checker_census.py", "load_bearing": True, "result": "PASS"}:
        raise ValueError("aggregate census freshness is stale")
    entries, exclusions = manifest["entries"], manifest["strong_signal_exclusions"]
    expected_scope = {"manifest_entry_count": len(entries), "current_load_bearing_count": sum(e["applicability"] == "current" and e["load_bearing"] for e in entries), "historical_or_evidentiary_count": sum(e["applicability"] == "historical_only" for e in entries), "explicit_exclusion_count": len(exclusions)}
    if value["curated_runtime_config_scope"] != expected_scope:
        raise ValueError("curated scope is stale")
    expected_results = [
        {"id": "identity_table_source_sync", "path": "tools/check_glyph_identity_runtime_table_source_sync.py", "classification": "repaired_current_load_bearing_source_sync_checker", "starting_configurator": {"exit_code": 1, "error": "stale 27-table interpreter bridge fixture"}, "feature_branch": {"result": "PASS"}},
        {"id": "runtime_semantics_evaluator_bridge", "path": "tools/check_glyph_runtime_config_semantics_evaluator_bridge.py", "classification": "repaired_current_load_bearing_evaluator_bridge_checker", "starting_configurator": {"exit_code": 1, "error": "stale Ultimate.cpp SHA and 27-table bridge lineage"}, "feature_branch": {"result": "PASS"}},
    ]
    if value["checker_results"] != expected_results:
        raise ValueError("checker result correspondence is stale")
    census_paths = {item["path"] for item in census_value["entries"]}
    manifest_records = {item["id"]: item for item in entries}
    exclusion_records = {item["id"]: item for item in exclusions}
    for record in expected_results:
        source = manifest_records.get(record["id"])
        if source is None or source["path"] != record["path"] or source["applicability"] != "current" or source["load_bearing"] is not True or record["path"] not in census_paths:
            raise ValueError("current checker result source correspondence is stale")
    if value["known_preexisting_failures"] != [{"id": e["id"], "result": "PRE_EXISTING_FIXTURE_DRIFT", "starting_configurator_exit_code": 1} for e in expected_results]:
        raise ValueError("known pre-existing failure correspondence is stale")
    expected_historical = [
        {"id": "identity_generated_evaluator_input", "path": "tools/check_glyph_identity_runtime_generated_config_evaluator_input.py", "fixture": "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json", "classification": "HISTORICAL_BRANCH_EVIDENCE", "current_aggregate_pass": False},
        {"id": "reconstructed_authority", "path": "tools/check_glyph_reconstructed_source_authority_evidence.py", "classification": "HISTORICAL_BRANCH_EVIDENCE", "current_aggregate_pass": False},
        {"id": "table_replacement_contract", "path": "tools/check_glyph_source_owned_table_replacement_generator_contract.py", "classification": "SUPERSEDED_CONTRACT", "current_aggregate_pass": False},
        {"id": "latest_y2_hardware_evidence", "path": "tools/check_glyph_latest_y2_layout_source_owned_port.py", "classification": "HARDWARE_RESULT_EVIDENCE", "current_aggregate_pass": False},
    ]
    if value["historical_evidence"] != expected_historical:
        raise ValueError("historical evidence correspondence is stale")
    for record in expected_historical:
        source = manifest_records.get(record["id"]) or exclusion_records.get(record["id"])
        if (source is not None and source["path"] != record["path"]) or record["path"] not in census_paths:
            raise ValueError("historical evidence source correspondence is stale")


def validate_adversarial_cases(value: dict[str, Any], census: dict[str, Any], manifest: dict[str, Any]) -> None:
    mutations = []
    unknown = copy.deepcopy(value); unknown["unknown"] = True; mutations.append(("unknown top-level field", unknown))
    missing = copy.deepcopy(value); del missing["schema_version"]; mutations.append(("missing top-level field", missing))
    reordered = copy.deepcopy(value); reordered["canonical_baseline"] = {"table_count": 28, "semantic_digest": value["canonical_baseline"]["semantic_digest"], "final_table": "kLt1LowMagnitudeTable"}; mutations.append(("reordered nested fields", reordered))
    mistyped = copy.deepcopy(value); mistyped["repository_checker_census"]["validated"] = 1; mutations.append(("boolean-as-integer", mistyped))
    missing_result = copy.deepcopy(value); missing_result["checker_results"].pop(); mutations.append(("missing checker result", missing_result))
    extra_result = copy.deepcopy(value); extra_result["checker_results"].append(copy.deepcopy(extra_result["checker_results"][0])); mutations.append(("extra checker result", extra_result))
    stale_count = copy.deepcopy(value); stale_count["curated_runtime_config_scope"]["manifest_entry_count"] += 1; mutations.append(("stale derived count", stale_count))
    census_identity = copy.deepcopy(value); census_identity["repository_checker_census"]["artifact"] = "wrong.json"; mutations.append(("stale census identity", census_identity))
    duplicate_exclusion = copy.deepcopy(value); duplicate_exclusion["strong_signal_exclusions"] = []; mutations.append(("reintroduced duplicate exclusion authority", duplicate_exclusion))
    null_nested = copy.deepcopy(value); null_nested["checker_results"][0]["feature_branch"]["result"] = None; mutations.append(("null nested field", null_nested))
    malformed_nested = copy.deepcopy(value); malformed_nested["known_preexisting_failures"][0]["starting_configurator_exit_code"] = "1"; mutations.append(("malformed nested primitive", malformed_nested))
    manifest_path = copy.deepcopy(manifest); next(item for item in manifest_path["entries"] if item["id"] == "identity_table_source_sync")["path"] = "tools/check_glyph_wrong.py"; mutations.append(("manifest path drift", (copy.deepcopy(value), census, manifest_path)))
    census_path = copy.deepcopy(census); next(item for item in census_path["entries"] if item["path"] == "tools/check_glyph_identity_runtime_table_source_sync.py")["path"] = "tools/check_glyph_wrong.py"; mutations.append(("census path drift", (copy.deepcopy(value), census_path, manifest)))
    try:
        json.loads('{"schema_version":3,"schema_version":3}', object_pairs_hook=pairs)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate JSON key was accepted")
    for label, mutated in mutations:
        try:
            if isinstance(mutated, tuple):
                validate_health(*mutated)
            else:
                validate_health(mutated, census, manifest)
        except ValueError:
            continue
        raise AssertionError(f"adversarial health mutation was accepted: {label}")


def main() -> int:
    try:
        value = json.loads(PATH.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        census = json.loads(CENSUS.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        validate_health(value, census, manifest)
        validate_adversarial_cases(value, census, manifest)
        validate_summary(MARKDOWN.read_text(encoding="utf-8"), (len(manifest["entries"]), value["curated_runtime_config_scope"]["current_load_bearing_count"]))
    except (OSError, AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"glyph_runtime_config_validation_health: FAIL: {exc}")
        return 1
    print(f"glyph_runtime_config_validation_health: PASS; census_count={len(census['entries'])}; manifest_entries={len(manifest['entries'])}; baseline={EXPECTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
