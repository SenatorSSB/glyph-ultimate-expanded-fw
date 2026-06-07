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
POST_GFW3_FIXTURE = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_post_gfw3_configurator_baseline_2026-06-06.json"
)
PRESERVATION_RESULT = REPO_ROOT / "docs/calibration/glyph_ultimate_preservation_hardware_result.md"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_roadmap_next_work_index",
    "schema_version": 2,
    "index_date": "2026-06-06",
    "baseline_source": "post_gfw3_configurator_baseline",
    "post_gfw3_baseline_path": "docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md",
    "roadmap_source_path": "docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md",
}

ALLOWED_STATUSES = {
    "COMPLETE",
    "CURRENT_BASELINE",
    "COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED",
    "READY_FOR_ENGINEERING_DESIGN",
    "READY_FOR_SOURCE_RESEARCH",
    "READY_FOR_PROTOTYPE",
    "READY_FOR_USER_PRODUCT_DECISION",
    "WAITING_FOR_USER_ARTIFACT",
    "WAITING_FOR_HARDWARE_TEST",
    "FUTURE_PHASE",
    "NOT_STARTED",
    "FORBIDDEN_BY_POLICY",
    "OFFICIAL_CORPUS_PRESENT_INITIAL",
    "OUT_OF_SCOPE",
}

REQUIREMENT_FIELDS = {
    "requires_user_domain_input",
    "requires_user_product_approval",
    "requires_source_research",
    "requires_hardware_test",
    "requires_user_artifact",
    "requires_firmware_change",
    "requires_safety_review",
    "requires_schema_decision",
    "requires_transport_authority",
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
    "preservation_hardware_matrix_execution",
    "generated_config_evaluator_bridge",
    "generated_cpp_constants_firmware_build_path",
    "offline_official_configurator_export_candidate",
    "stable_firmware_bounded_config_owned_modifier_data",
    "runtime_loaded_config_design_validation_contract",
    "runtime_loaded_config_implementation",
    "webserial_device_write",
    "protobuf_binary_write",
    "external_remapper_adapter_output",
    "firmware_flashing_automation",
    "external_source_code_reuse",
    "nunchuk_hardware_validation_claim",
    "senscope_browser_app_implementation_work",
}

REQUIRED_DOC_PHRASES = (
    "Legacy `BLOCKED_*` labels in older calibration packets may mean",
    "`READY_FOR_ENGINEERING_DESIGN`",
    "`READY_FOR_SOURCE_RESEARCH`",
    "`requires_user_domain_input`",
    "`requires_user_product_approval`",
    "Generated-config/evaluator bridge",
    "Generated C++ constants / firmware build path",
    "Offline official configurator export candidate",
    "Stable firmware + bounded config-owned modifier data",
    "Runtime-loaded config is not implemented and not user-domain-blocked",
    "WebSerial/device write is not implemented and not user-domain-blocked",
    "Nunchuk hardware validation claim",
    "Not a general implementation blocker",
    "Forbidden by policy: macros, turbo, timing automation, hidden device write",
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


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")
    taxonomy = payload.get("status_taxonomy")
    if not isinstance(taxonomy, list) or not ALLOWED_STATUSES.issubset(set(taxonomy)):
        fail("status_taxonomy must include the current status model")
    fields = payload.get("requirement_fields")
    if not isinstance(fields, list) or set(fields) != REQUIREMENT_FIELDS:
        fail("requirement_fields must exactly list the current requirement booleans")
    note = payload.get("legacy_status_note", "")
    if "Legacy BLOCKED_* labels" not in note or "separate status from requirement booleans" not in note:
        fail("legacy_status_note must explain legacy blocked labels")


def validate_item_shape(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        fail("each roadmap item must be an object")
    for field, expected_type in REQUIRED_ITEM_FIELDS.items():
        if field not in item:
            fail(f"roadmap item missing field: {field}")
        if not isinstance(item[field], expected_type):
            fail(f"roadmap item {item.get('item_id', '<unknown>')}.{field} must be {expected_type.__name__}")
    for field in REQUIREMENT_FIELDS:
        if not isinstance(item.get(field), bool):
            fail(f"roadmap item {item.get('item_id', '<unknown>')}.{field} must be bool")
    if item["current_status"] not in ALLOWED_STATUSES:
        fail(f"roadmap item {item['item_id']} has invalid status: {item['current_status']}")
    if not item["item_id"].strip() or not item["label"].strip():
        fail("roadmap item id and label must be non-empty")
    if not all(isinstance(path, str) and path.strip() for path in item["evidence_paths"]):
        fail(f"roadmap item {item['item_id']} evidence_paths must be non-empty strings")
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


def validate_evidence_paths(items: dict[str, dict[str, Any]]) -> None:
    for item in items.values():
        for rel_path in item["evidence_paths"]:
            if rel_path == "AGENTS.md":
                continue
            if not (REPO_ROOT / rel_path).exists():
                fail(f"roadmap item {item['item_id']} references missing evidence path: {rel_path}")


def validate_key_semantics(items: dict[str, dict[str, Any]]) -> None:
    preservation = items["preservation_hardware_matrix_execution"]
    if preservation["current_status"] != "COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED":
        fail("preservation hardware execution must record the user-reported completion status")
    if preservation["requires_hardware_test"] or preservation["requires_user_domain_input"] or preservation["blocked_by"]:
        fail("preservation hardware execution must not remain blocked after recorded result")
    if not PRESERVATION_RESULT.exists():
        fail("preservation hardware execution cannot be complete without a filled result file")

    generated_cpp = items["generated_cpp_constants_firmware_build_path"]
    if generated_cpp["current_status"] != "READY_FOR_ENGINEERING_DESIGN":
        fail("generated C++ constants path must be ready for engineering design")
    if generated_cpp["requires_user_domain_input"]:
        fail("generated C++ constants path must not require user domain input")
    if not generated_cpp["requires_user_product_approval"]:
        fail("generated C++ constants path must require product approval before firmware implementation")

    runtime = items["runtime_loaded_config_implementation"]
    if runtime["current_status"] != "FUTURE_PHASE":
        fail("runtime-loaded config implementation must be a future phase")
    if runtime["requires_user_domain_input"]:
        fail("runtime-loaded config must not be user-domain-blocked")
    if not runtime["requires_user_product_approval"] or not runtime["requires_source_research"]:
        fail("runtime-loaded config must require product approval and source/design research")

    webserial = items["webserial_device_write"]
    if webserial["current_status"] != "FUTURE_PHASE":
        fail("WebSerial/device write must be a future phase")
    if webserial["requires_user_domain_input"]:
        fail("WebSerial/device write must not be user-domain-blocked")
    if not webserial["requires_transport_authority"]:
        fail("WebSerial/device write must require transport authority")

    protobuf = items["protobuf_binary_write"]
    if protobuf["current_status"] != "FUTURE_PHASE":
        fail("protobuf binary write must be a future phase")
    if protobuf["requires_user_domain_input"]:
        fail("protobuf binary write must not be user-domain-blocked")

    adapter_output = items["external_remapper_adapter_output"]
    if adapter_output["current_status"] != "FUTURE_PHASE":
        fail("external-remapper adapter output must be a future phase")
    if adapter_output["requires_user_domain_input"]:
        fail("external-remapper adapter output must not be user-domain-blocked")

    nunchuk = items["nunchuk_hardware_validation_claim"]
    if nunchuk["current_status"] != "OUT_OF_SCOPE":
        fail("nunchuk must be out of scope for current hardware")
    if nunchuk["requires_hardware_test"] or nunchuk["requires_user_domain_input"]:
        fail("nunchuk must not be a general implementation blocker")

    for item_id in ("firmware_flashing_automation", "external_source_code_reuse"):
        if items[item_id]["current_status"] != "FORBIDDEN_BY_POLICY":
            fail(f"{item_id} must remain forbidden by policy")

    if items["senscope_browser_app_implementation_work"]["current_status"] != "OUT_OF_SCOPE":
        fail("Senscope browser-app implementation must remain OUT_OF_SCOPE")


def validate_global_policy(payload: dict[str, Any]) -> None:
    classes = payload.get("global_forbidden_classes")
    if not isinstance(classes, dict):
        fail("global_forbidden_classes must be an object")
    for class_id in (
        "runtime_loaded_config_implementation",
        "webserial_device_write",
        "protobuf_binary_write",
        "external_remapper_adapter_output",
    ):
        item = classes.get(class_id)
        if not isinstance(item, dict):
            fail(f"global_forbidden_classes.{class_id} must be an object")
        if item.get("status") != "FUTURE_PHASE":
            fail(f"global_forbidden_classes.{class_id}.status must be FUTURE_PHASE")
        if item.get("requires_user_domain_input") is not False:
            fail(f"global_forbidden_classes.{class_id} must not require user domain input")
        if item.get("requires_user_product_approval") is not True:
            fail(f"global_forbidden_classes.{class_id} must require product approval")
    for class_id in ("firmware_flashing_automation", "external_source_code_reuse"):
        if classes.get(class_id, {}).get("status") != "FORBIDDEN_BY_POLICY":
            fail(f"global_forbidden_classes.{class_id}.status must be FORBIDDEN_BY_POLICY")


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
    if not DOC_PATH.exists():
        fail(f"missing doc: {display(DOC_PATH)}")
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"roadmap next-work doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_roadmap_next_work_index")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        items = as_items_by_id(payload)
        validate_evidence_paths(items)
        validate_global_policy(payload)
        validate_key_semantics(items)
        validate_post_gfw3_fixture()
        validate_doc()
    except (OSError, RoadmapNextWorkIndexError, ValueError) as exc:
        print("status=FAIL")
        print("index_date=2026-06-06")
        print("runtime_loaded_config_user_domain_blocked=false")
        print("webserial_device_write_user_domain_blocked=false")
        print("nunchuk_general_implementation_blocker=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("index_date=2026-06-06")
    print("status_model=current_taxonomy_with_separate_requirements")
    print("runtime_loaded_config_user_domain_blocked=false")
    print("webserial_device_write_user_domain_blocked=false")
    print("generated_cpp_ready_for_engineering_design=true")
    print("nunchuk_general_implementation_blocker=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
