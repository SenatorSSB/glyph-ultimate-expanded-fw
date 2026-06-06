#!/usr/bin/env python3
"""Validate the Glyph physical/logical/RF5 gap index packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_physical_logical_rf5_gap_index_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_physical_logical_rf5_gap_index_2026-06-06.json"
)

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_physical_logical_rf5_gap_index",
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "physical_logical_rf5_gap_index_docs_tools_only",
    "historical_rf5_row_status": "UNRESOLVED_HISTORICAL_ROW",
    "old_rf5_smoke_result": "NOT_TESTED_AMBIGUOUS",
    "future_resolution_status": "requires_source_authority_hardware_result_or_user_domain_input",
}

REQUIRED_SOURCE_KEYS = {
    "gfw3_hardware_result_doc",
    "gfw3_hardware_result_fixture",
    "historical_tilt_hardware_result",
    "identity_runtime_role_map_fixture",
    "merged_state_consistency_audit",
    "physical_logical_layout_map",
    "roadmap_next_work_index",
}

REQUIRED_LAYERS = {
    "printed_base_physical_marking",
    "matrix_display_source_facts",
    "historical_rf5_negative_smoke_row",
    "current_mvp_rf3_rf4_tilt_path",
    "later_gfw3_rf5_hardware_scope",
    "identity_runtime_role_map_fixture",
}

REQUIRED_FALSE_NON_CLAIMS = {
    "physical_id_mapping_changed",
    "firmware_behavior_changed",
    "active_profile_artifact_changed",
    "new_hardware_validation_claimed",
    "nunchuk_hardware_validated",
    "runtime_loaded_config_implemented",
    "webserial_write_implemented",
    "device_write_implemented",
    "external_remapper_adapter_output_generated",
    "smash_ultimate_game_semantics_changed",
    "old_rf5_ambiguity_resolved_by_inference",
}

REQUIRED_DOC_PHRASES = (
    "physical_logical_rf5_gap_index_docs_tools_only",
    "No physical ID mapping changes are made here",
    "No firmware behavior changes are made here",
    "No active profile artifact changes are made here",
    "No hardware validation claim is newly made here",
    "No nunchuk hardware validation claim is made here",
    "No old RF5 ambiguity is resolved by inference here",
    "The old RF5 negative check remains `NOT_TESTED_AMBIGUOUS`",
    "GFW3 result includes `base_rf5_up_a` as PASS in the GFW3 runtime remap scope",
    "requires_source_authority_hardware_result_or_user_domain_input",
)


class PhysicalLogicalRf5GapIndexError(AssertionError):
    """Raised when the RF5 gap index drifts."""


def fail(message: str) -> None:
    raise PhysicalLogicalRf5GapIndexError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_paths(payload: dict[str, Any]) -> dict[str, Path]:
    source_paths = payload.get("source_paths")
    if not isinstance(source_paths, dict):
        fail("source_paths must be an object")
    missing = sorted(REQUIRED_SOURCE_KEYS - set(source_paths))
    if missing:
        fail("source_paths missing: " + ", ".join(missing))
    resolved: dict[str, Path] = {}
    for key, rel_path in source_paths.items():
        if not isinstance(rel_path, str) or not rel_path.strip():
            fail(f"source_paths.{key} must be a non-empty string")
        path = REPO_ROOT / rel_path
        if not path.exists():
            fail(f"source_paths.{key} references missing path: {rel_path}")
        resolved[key] = path
    return resolved


def validate_source_content(paths: dict[str, Path]) -> None:
    physical_map = paths["physical_logical_layout_map"].read_text(encoding="utf-8")
    if "RF5 | Far-right upper button" not in physical_map:
        fail("physical/logical map must keep RF5 far-right upper transcription")
    if "Old hardware smoke check for RF5 remains `NOT_TESTED_AMBIGUOUS`" not in physical_map:
        fail("physical/logical map must preserve old RF5 ambiguity caveat")

    historical_result = paths["historical_tilt_hardware_result"].read_text(encoding="utf-8")
    if "NOT_TESTED_AMBIGUOUS" not in historical_result:
        fail("historical Tilt hardware result must preserve NOT_TESTED_AMBIGUOUS")
    if "not recorded as definitive RF5-negative verification" not in historical_result:
        fail("historical Tilt hardware result must preserve non-definitive RF5 note")

    audit = paths["merged_state_consistency_audit"].read_text(encoding="utf-8")
    if "The printed/base physical ID transcription records center-right / RF cluster, far-right upper button as RF5" not in audit:
        fail("merged-state audit must keep printed/base RF5 fact")
    if "historically `NOT_TESTED_AMBIGUOUS`" not in audit:
        fail("merged-state audit must keep historical ambiguity fact")

    gfw3 = load_json_object(paths["gfw3_hardware_result_fixture"])
    if gfw3.get("schema_name") != "glyph_gfw3_runtime_remap_hardware_result":
        fail("GFW3 fixture schema drifted")
    if gfw3.get("nunchuk_hardware_validated") is not False:
        fail("GFW3 fixture must not claim nunchuk hardware validation")
    rows = gfw3.get("rows")
    if not isinstance(rows, list):
        fail("GFW3 fixture rows must be a list")
    rf5_rows = [row for row in rows if isinstance(row, dict) and row.get("row_id") == "base_rf5_up_a"]
    if len(rf5_rows) != 1:
        fail("GFW3 fixture must contain exactly one base_rf5_up_a row")
    if rf5_rows[0].get("status") != "PASS":
        fail("GFW3 base_rf5_up_a row must remain PASS")

    role_map = load_json_object(paths["identity_runtime_role_map_fixture"])
    if role_map.get("schema_name") != "glyph_identity_runtime_role_map":
        fail("identity runtime role-map schema drifted")
    if role_map.get("nunchuk_status") != "preserved_but_not_hardware_validated":
        fail("identity runtime role-map must preserve nunchuk caveat")


def validate_layer_findings(payload: dict[str, Any]) -> None:
    findings = payload.get("layer_findings")
    if not isinstance(findings, list):
        fail("layer_findings must be a list")
    layers: dict[str, dict[str, Any]] = {}
    for finding in findings:
        if not isinstance(finding, dict):
            fail("each layer finding must be an object")
        layer = finding.get("layer")
        if not isinstance(layer, str) or not layer.strip():
            fail("each layer finding requires layer")
        if layer in layers:
            fail(f"duplicate layer finding: {layer}")
        for field in ("finding", "status", "caveat"):
            if not isinstance(finding.get(field), str) or not finding[field].strip():
                fail(f"layer_findings.{layer}.{field} must be a non-empty string")
        layers[layer] = finding
    missing = sorted(REQUIRED_LAYERS - set(layers))
    if missing:
        fail("layer_findings missing: " + ", ".join(missing))
    if layers["historical_rf5_negative_smoke_row"]["status"] != "UNRESOLVED_HISTORICAL_ROW":
        fail("historical RF5 layer must remain unresolved")


def validate_non_claims(payload: dict[str, Any]) -> None:
    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("non_claims must be an object")
    missing = sorted(REQUIRED_FALSE_NON_CLAIMS - set(non_claims))
    if missing:
        fail("non_claims missing: " + ", ".join(missing))
    for key in sorted(REQUIRED_FALSE_NON_CLAIMS):
        if non_claims.get(key) is not False:
            fail(f"non_claims.{key} must be false")


def validate_doc() -> None:
    if not DOC_PATH.exists():
        fail(f"missing doc: {display(DOC_PATH)}")
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_physical_logical_rf5_gap_index")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        paths = validate_paths(payload)
        validate_source_content(paths)
        validate_layer_findings(payload)
        validate_non_claims(payload)
        validate_doc()
    except (OSError, PhysicalLogicalRf5GapIndexError, ValueError) as exc:
        print("status=FAIL")
        print("historical_rf5_row_status=UNRESOLVED_HISTORICAL_ROW")
        print("old_rf5_smoke_result=NOT_TESTED_AMBIGUOUS")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("historical_rf5_row_status=UNRESOLVED_HISTORICAL_ROW")
    print("old_rf5_smoke_result=NOT_TESTED_AMBIGUOUS")
    print("future_resolution_status=requires_source_authority_hardware_result_or_user_domain_input")
    print("new_hardware_validation_claimed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
