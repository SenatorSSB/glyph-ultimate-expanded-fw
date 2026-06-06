#!/usr/bin/env python3
"""Validate the Glyph roadmap next-work index packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_roadmap_next_work_index_2026-06-06.json"
)
POST_GFW3_DOC = REPO_ROOT / "docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md"
POST_GFW3_FIXTURE = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_post_gfw3_configurator_baseline_2026-06-06.json"
)
POST_GFW3_CHECKER = REPO_ROOT / "tools/check_glyph_post_gfw3_configurator_baseline.py"
ROADMAP_SOURCE = REPO_ROOT / "docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md"
PRESERVATION_RESULT = REPO_ROOT / "docs/calibration/glyph_ultimate_preservation_hardware_result.md"
EXPORT_CORPUS_ROOT = REPO_ROOT / "docs/calibration/export_corpus"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_roadmap_next_work_index",
    "schema_version": 1,
    "index_date": "2026-06-06",
    "baseline_source": "post_gfw3_configurator_baseline",
    "post_gfw3_baseline_path": "docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md",
    "roadmap_source_path": "docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md",
}

ALLOWED_STATUSES = {
    "COMPLETE",
    "COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED",
    "READY_DOCS_TOOLS",
    "READY_CORPUS_CAPTURE",
    "BLOCKED_HARDWARE",
    "BLOCKED_USER_INPUT",
    "BLOCKED_SOURCE_AUTHORITY",
    "BLOCKED_IMPLEMENTATION_APPROVAL",
    "BLOCKED_EXTERNAL_AUDIT",
    "FORBIDDEN_WITHOUT_FUTURE_APPROVAL",
    "OUT_OF_SCOPE",
}

REQUIRED_ITEM_FIELDS = {
    "item_id": str,
    "label": str,
    "current_status": str,
    "category": str,
    "evidence_paths": list,
    "allowed_next_action": str,
    "blocked_by": list,
    "requires_user_input": bool,
    "requires_hardware": bool,
    "requires_source_audit": bool,
    "requires_corpus": bool,
    "requires_firmware_change": bool,
    "forbidden_without_future_approval": bool,
    "notes": str,
}

REQUIRED_ITEMS = {
    "native_ultimate_tilt_runtime_baseline",
    "tilt_tilt2_hardware_smoke_evidence",
    "preservation_hardware_matrix_execution",
    "capability_source_authority_mapping",
    "identity_runtime_role_case_canonicalization",
    "export_corpus_capture",
    "export_corpus_final_blocker_status",
    "adapter_policy_prewrite_validation",
    "physical_logical_mapping_rf5_transcription",
    "identity_runtime_generated_config_prototype",
    "runtime_config_candidate_validator",
    "runtime_loaded_config_design_validation_contract",
    "external_remapper_boundary_snapshot_shape_feasibility_mapping_gap_experiment",
    "gfw3_runtime_remap_hardware_result",
    "post_gfw3_configurator_baseline_readiness",
    "runtime_patch_implementation_branch",
    "senscope_browser_app_implementation_work",
    "nunchuk_hardware_validation_claim",
    "runtime_loaded_config_implementation",
    "webserial_device_write",
    "protobuf_binary_write",
    "firmware_flashing_automation",
    "external_remapper_adapter_output",
    "external_source_code_reuse",
}

REQUIRED_GLOBAL_FORBIDDEN_CLASSES = {
    "runtime_loaded_config_implementation",
    "webserial_device_write",
    "protobuf_binary_write",
    "firmware_flashing_automation",
    "external_remapper_adapter_output",
    "external_source_code_reuse",
    "nunchuk_hardware_validation_claim",
}

REQUIRED_DOC_PHRASES = (
    "Nunchuk hardware validation not claimed",
    "Runtime-loaded config not implemented",
    "WebSerial/device write not implemented",
    "External remapper adapter implementation not started",
    "Active profile artifact change not required",
    "Future behavior-changing workflow gate",
    "Runtime-loaded config, WebSerial/device write, protobuf binary write, firmware flashing automation, and external-remapper adapter output remain blocked",
    "Senscope browser-app implementation work",
    "Forbidden until future source authority and explicit approval",
    "COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED",
    "User-reported pass is recorded for all applicable non-nunchuk preservation rows",
    "nunchuk remains NOT_TESTED/unvalidated because the controller has no nunchuk port available out of the box",
    "No runtime-loaded config, WebSerial/device write, external remapper adapter, or active profile artifact change is claimed",
    "Export corpus final blocker/status consolidation",
    "Final blocker packet records that export corpus capture remains blocked by missing real corpus artifacts",
)


class RoadmapNextWorkIndexError(AssertionError):
    """Raised when the next-work index packet drifts from guardrails."""


def fail(message: str) -> None:
    raise RoadmapNextWorkIndexError(message)


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


def require_paths() -> None:
    for path in (DOC_PATH, FIXTURE_PATH, POST_GFW3_DOC, POST_GFW3_FIXTURE, POST_GFW3_CHECKER, ROADMAP_SOURCE):
        if not path.exists():
            fail(f"missing required path: {display(path)}")


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_global_forbidden_classes(payload: dict[str, Any]) -> None:
    classes = payload.get("global_forbidden_classes")
    if not isinstance(classes, dict):
        fail("global_forbidden_classes must be an object")
    missing = sorted(REQUIRED_GLOBAL_FORBIDDEN_CLASSES - set(classes))
    if missing:
        fail("global_forbidden_classes missing: " + ", ".join(missing))

    for class_id in sorted(REQUIRED_GLOBAL_FORBIDDEN_CLASSES):
        item = classes.get(class_id)
        if not isinstance(item, dict):
            fail(f"global_forbidden_classes.{class_id} must be an object")
        if item.get("forbidden_without_future_approval") is not True:
            fail(f"global_forbidden_classes.{class_id}.forbidden_without_future_approval must be true")
        if item.get("allowed_now") is not False:
            fail(f"global_forbidden_classes.{class_id}.allowed_now must be false")
        if item.get("implemented") is not False:
            fail(f"global_forbidden_classes.{class_id}.implemented must be false")


def validate_item_shape(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        fail("each roadmap item must be an object")
    for field, expected_type in REQUIRED_ITEM_FIELDS.items():
        if field not in item:
            fail(f"roadmap item missing field: {field}")
        if not isinstance(item[field], expected_type):
            fail(f"roadmap item {item.get('item_id', '<unknown>')}.{field} must be {expected_type.__name__}")
    if item["current_status"] not in ALLOWED_STATUSES:
        fail(f"roadmap item {item['item_id']} has invalid status: {item['current_status']}")
    if not item["item_id"].strip():
        fail("roadmap item_id must be non-empty")
    if not item["label"].strip():
        fail(f"roadmap item {item['item_id']} label must be non-empty")
    if not all(isinstance(path, str) and path.strip() for path in item["evidence_paths"]):
        fail(f"roadmap item {item['item_id']} evidence_paths must be non-empty strings")
    if not all(isinstance(blocker, str) and blocker.strip() for blocker in item["blocked_by"]):
        fail(f"roadmap item {item['item_id']} blocked_by must contain strings")
    return item


def as_items_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_items = payload.get("roadmap_items")
    if not isinstance(raw_items, list):
        fail("roadmap_items must be a list")
    items: dict[str, dict[str, Any]] = {}
    for raw_item in raw_items:
        item = validate_item_shape(raw_item)
        item_id = item["item_id"]
        if item_id in items:
            fail(f"duplicate roadmap item_id: {item_id}")
        items[item_id] = item
    missing = sorted(REQUIRED_ITEMS - set(items))
    if missing:
        fail("roadmap_items missing: " + ", ".join(missing))
    return items


def has_real_export_corpus() -> bool:
    if not EXPORT_CORPUS_ROOT.exists():
        return False
    return any(path.is_file() for path in EXPORT_CORPUS_ROOT.rglob("manifest.json"))


def require_not_complete_without_artifacts(items: dict[str, dict[str, Any]]) -> None:
    preservation = items["preservation_hardware_matrix_execution"]
    preservation_complete_statuses = {
        "COMPLETE",
        "COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED",
    }
    if preservation["current_status"] in preservation_complete_statuses and not PRESERVATION_RESULT.exists():
        fail("preservation hardware execution cannot be marked complete without a filled result file")

    export_corpus = items["export_corpus_capture"]
    if export_corpus["current_status"] == "COMPLETE" and not has_real_export_corpus():
        fail("export corpus capture cannot be COMPLETE without real corpus manifests")

    export_corpus_blocker = items["export_corpus_final_blocker_status"]
    if export_corpus_blocker["current_status"] != "COMPLETE":
        fail("export corpus final blocker/status consolidation must remain COMPLETE")
    if export_corpus_blocker["allowed_next_action"] != "preserve_with_docs_tools_only":
        fail("export corpus final blocker/status consolidation must preserve docs/tools-only scope")
    for rel_path in (
        "docs/calibration/glyph_export_corpus_final_blocker_status_2026-06-06.md",
        "docs/calibration/fixtures/glyph_export_corpus_final_blocker_status_2026-06-06.json",
        "tools/check_glyph_export_corpus_final_blocker_status.py",
    ):
        if rel_path not in export_corpus_blocker["evidence_paths"]:
            fail(f"export corpus final blocker/status consolidation evidence must include {rel_path}")
    notes = export_corpus_blocker["notes"].lower()
    for phrase in (
        "blocked by missing real corpus artifacts",
        "readme guidance",
        "no real manifest or fixture set",
    ):
        if phrase not in notes:
            fail(f"export corpus final blocker/status consolidation notes missing phrase: {phrase}")


def require_blocked_nonclaims(items: dict[str, dict[str, Any]]) -> None:
    runtime_loaded = items["runtime_loaded_config_implementation"]
    if runtime_loaded["current_status"] != "FORBIDDEN_WITHOUT_FUTURE_APPROVAL":
        fail("runtime-loaded config implementation must remain forbidden")
    if runtime_loaded["allowed_next_action"] != "none_in_this_branch":
        fail("runtime-loaded config implementation must not be marked allowed")

    webserial = items["webserial_device_write"]
    if webserial["current_status"] != "FORBIDDEN_WITHOUT_FUTURE_APPROVAL":
        fail("WebSerial/device write must remain forbidden")
    if webserial["allowed_next_action"] != "none_in_this_branch":
        fail("WebSerial/device write must not be marked allowed")

    adapter_output = items["external_remapper_adapter_output"]
    if adapter_output["current_status"] != "FORBIDDEN_WITHOUT_FUTURE_APPROVAL":
        fail("external-remapper adapter output must remain forbidden")
    if "implemented" in adapter_output["notes"].lower() and "not implemented" not in adapter_output["notes"].lower():
        fail("external-remapper adapter output must not be marked implemented")

    nunchuk = items["nunchuk_hardware_validation_claim"]
    if nunchuk["current_status"] == "COMPLETE" or not nunchuk["requires_hardware"]:
        fail("nunchuk hardware validation must not be claimed")

    senscope = items["senscope_browser_app_implementation_work"]
    if senscope["current_status"] != "OUT_OF_SCOPE":
        fail("Senscope browser-app implementation must remain OUT_OF_SCOPE")


def validate_evidence_paths(items: dict[str, dict[str, Any]]) -> None:
    for item in items.values():
        for rel_path in item["evidence_paths"]:
            if rel_path == "AGENTS.md":
                continue
            path = REPO_ROOT / rel_path
            if not path.exists():
                fail(f"roadmap item {item['item_id']} references missing evidence path: {rel_path}")


def validate_preservation_item(items: dict[str, dict[str, Any]]) -> None:
    preservation = items["preservation_hardware_matrix_execution"]
    if preservation["current_status"] != "COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED":
        fail("preservation hardware execution must record the user-reported completion status")
    if preservation["allowed_next_action"] != "preserve_result_scope_only":
        fail("preservation hardware execution must preserve result scope only")
    if preservation["requires_hardware"] is not False:
        fail("preservation hardware execution must not require hardware after the result is recorded")
    if preservation["blocked_by"]:
        fail("preservation hardware execution must not remain blocked")
    for rel_path in (
        "docs/calibration/glyph_ultimate_preservation_hardware_result.md",
        "docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result.json",
    ):
        if rel_path not in preservation["evidence_paths"]:
            fail(f"preservation hardware execution evidence must include {rel_path}")
    notes = preservation["notes"].lower()
    for phrase in (
        "user-reported pass is recorded for all applicable non-nunchuk preservation rows",
        "nunchuk remains not_tested/unvalidated because the controller has no nunchuk port available out of the box",
        "no runtime-loaded config, webserial/device write, external remapper adapter, or active profile artifact change is claimed",
    ):
        if phrase not in notes:
            fail(f"preservation hardware execution notes missing phrase: {phrase}")


def validate_post_gfw3_fixture() -> None:
    baseline = load_json_object(POST_GFW3_FIXTURE)
    non_claims = baseline.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("post-GFW3 baseline non_claims must be an object")
    for key in (
        "nunchuk_hardware_validated",
        "runtime_loaded_config_implemented",
        "webserial_write_implemented",
        "device_write_implemented",
        "external_remapper_adapter_implemented",
        "external_remapper_json_generated",
        "active_profile_artifact_changed",
    ):
        if non_claims.get(key) is not False:
            fail(f"post-GFW3 baseline non_claims.{key} must be false")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"roadmap next-work doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_roadmap_next_work_index")
    try:
        require_paths()
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        validate_global_forbidden_classes(payload)
        items = as_items_by_id(payload)
        validate_evidence_paths(items)
        validate_preservation_item(items)
        validate_post_gfw3_fixture()
        require_not_complete_without_artifacts(items)
        require_blocked_nonclaims(items)
        validate_doc()
    except (OSError, RoadmapNextWorkIndexError, ValueError) as exc:
        print("status=FAIL")
        print("index_date=2026-06-06")
        print("runtime_loaded_config_allowed=false")
        print("webserial_device_write_allowed=false")
        print("external_remapper_adapter_output_implemented=false")
        print("nunchuk_hardware_validation_claimed=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("index_date=2026-06-06")
    print("baseline_source=post_gfw3_configurator_baseline")
    print("runtime_loaded_config_allowed=false")
    print("webserial_device_write_allowed=false")
    print("external_remapper_adapter_output_implemented=false")
    print("nunchuk_hardware_validation_claimed=false")
    print("senscope_browser_app_implementation=out_of_scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
