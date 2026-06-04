#!/usr/bin/env python3
"""Validate the offline remapper adapter mapping plan."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_adapter_mapping_plan"
PLAN_VERSION = 1
STATUS = "offline_adapter_plan_only"
HARDWARE_STATUS = "not_new_hardware_result"
ALLOWED_MAPPING_STATUSES = {
    "direct_candidate",
    "derived_candidate",
    "manual_review_required",
    "blocked_missing_source_authority",
    "out_of_scope",
}
REQUIRED_CATEGORY_IDS = (
    "profile_identity_name_metadata",
    "mode_backend_metadata",
    "button_remapping_entries",
    "explicit_disabled_button_entries",
    "socd_pairs",
    "rgb_config_references",
    "rgb_button_colors",
    "menu_button_icon_display_metadata",
    "keyboard_mode_metadata",
    "custom_modifier_metadata",
    "generated_config_tables",
    "validation_report",
    "source_authority_and_caveats",
    "non_goals",
    "protobuf_binary_payload",
    "webserial_device_write_fields",
)
REQUIRED_DOC_PHRASES = (
    "mapping plan only",
    "adapter not implemented",
    "no device write fields",
    "no webserial transport",
    "custom modifier representation requires source audit",
    "not protobuf binary generation",
    "not hardware validation",
)
REQUIRED_SIDECAR_FIELDS = (
    "sidecar.validationReport",
    "sidecar.sourceAuthority",
    "sidecar.nonGoals",
)
REQUIRED_OUT_OF_SCOPE_TARGETS = (
    "transport.webserial",
    "transport.deviceWrite",
    "transport.saveToDevice",
)


class OfflineRemapperAdapterMappingPlanError(ValueError):
    """Raised when the mapping plan drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperAdapterMappingPlanError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    return value


def require_bool(payload: dict[str, Any], key: str, expected: bool) -> None:
    if payload.get(key) is not expected:
        fail(f"{key} must be {expected!r}")


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "plan_version": PLAN_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")

    for key in (
        "adapter_implemented",
        "external_source_promoted_to_authority",
        "official_configurator_compatibility_claimed",
        "device_write_implemented",
        "webserial_transport_implemented",
        "protobuf_binary_generation_implemented",
        "runtime_loaded_config_implemented",
    ):
        require_bool(fixture, key, False)


def validate_source_inputs(fixture: dict[str, Any]) -> None:
    inputs = fixture.get("source_inputs")
    if not isinstance(inputs, list) or not inputs:
        fail("source_inputs must be a non-empty list")
    for index, item in enumerate(inputs):
        relpath = require_string(item, f"source_inputs[{index}]")
        if not (REPO_ROOT / relpath).exists():
            fail(f"source_inputs references missing path: {relpath}")


def validate_mappings(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    mappings = fixture.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        fail("mappings must be a non-empty list")

    seen: set[str] = set()
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict):
            fail(f"mappings[{index}] must be an object")
        for key in (
            "category_id",
            "source_artifact",
            "source_path_or_field",
            "future_target_field",
            "mapping_status",
            "authority_class",
            "notes",
        ):
            require_string(mapping.get(key), f"mappings[{index}].{key}")

        category_id = mapping["category_id"]
        if category_id in seen:
            fail(f"duplicate category_id in mappings: {category_id}")
        seen.add(category_id)

        status = mapping["mapping_status"]
        if status not in ALLOWED_MAPPING_STATUSES:
            fail(f"mappings[{index}].mapping_status must be allowed: {status}")

        source_artifact = Path(mapping["source_artifact"])
        if not (REPO_ROOT / source_artifact).exists():
            fail(f"mappings[{index}].source_artifact missing: {source_artifact}")

    missing = [category for category in REQUIRED_CATEGORY_IDS if category not in seen]
    if missing:
        fail(f"mappings missing required categories: {', '.join(missing)}")
    return mappings


def mapping_by_id(mappings: list[dict[str, Any]], category_id: str) -> dict[str, Any]:
    for mapping in mappings:
        if mapping["category_id"] == category_id:
            return mapping
    fail(f"missing mapping for {category_id}")


def validate_required_statuses(mappings: list[dict[str, Any]]) -> None:
    custom_modifier = mapping_by_id(mappings, "custom_modifier_metadata")
    if custom_modifier["mapping_status"] not in {
        "manual_review_required",
        "blocked_missing_source_authority",
    }:
        fail("custom_modifier_metadata must be blocked or manual review required")

    protobuf = mapping_by_id(mappings, "protobuf_binary_payload")
    if protobuf["mapping_status"] != "blocked_missing_source_authority":
        fail("protobuf_binary_payload must be blocked_missing_source_authority")

    webserial = mapping_by_id(mappings, "webserial_device_write_fields")
    if webserial["mapping_status"] != "out_of_scope":
        fail("webserial_device_write_fields must be out_of_scope")

    generated_tables = mapping_by_id(mappings, "generated_config_tables")
    if generated_tables["mapping_status"] == "direct_candidate":
        fail("generated_config_tables must not be direct_candidate")

    validation_report = mapping_by_id(mappings, "validation_report")
    if validation_report["mapping_status"] != "derived_candidate":
        fail("validation_report must be derived_candidate")
    if "sidecar" not in validation_report["future_target_field"]:
        fail("validation_report must target a sidecar field")

    authority_caveats = mapping_by_id(mappings, "source_authority_and_caveats")
    if authority_caveats["mapping_status"] != "derived_candidate":
        fail("source_authority_and_caveats must be derived_candidate")
    if "sidecar" not in authority_caveats["future_target_field"]:
        fail("source_authority_and_caveats must target a sidecar field")


def validate_blocked_mappings(fixture: dict[str, Any]) -> None:
    blocked = fixture.get("blocked_mappings")
    if not isinstance(blocked, list) or not blocked:
        fail("blocked_mappings must be a non-empty list")
    seen: set[str] = set()
    for index, item in enumerate(blocked):
        if not isinstance(item, dict):
            fail(f"blocked_mappings[{index}] must be an object")
        category_id = require_string(item.get("category_id"), f"blocked_mappings[{index}].category_id")
        require_string(item.get("reason"), f"blocked_mappings[{index}].reason")
        blocking_source = require_string(
            item.get("blocking_source"), f"blocked_mappings[{index}].blocking_source"
        )
        if not (REPO_ROOT / blocking_source).exists():
            fail(f"blocked_mappings[{index}].blocking_source missing: {blocking_source}")
        seen.add(category_id)

    for required in ("custom_modifier_metadata", "protobuf_binary_payload"):
        if required not in seen:
            fail(f"blocked_mappings missing {required}")


def validate_sidecar_outputs(fixture: dict[str, Any]) -> None:
    sidecars = fixture.get("sidecar_outputs")
    if not isinstance(sidecars, list) or not sidecars:
        fail("sidecar_outputs must be a non-empty list")
    future_fields: set[str] = set()
    for index, item in enumerate(sidecars):
        if not isinstance(item, dict):
            fail(f"sidecar_outputs[{index}] must be an object")
        require_string(item.get("output_id"), f"sidecar_outputs[{index}].output_id")
        future_field = require_string(
            item.get("future_target_field"),
            f"sidecar_outputs[{index}].future_target_field",
        )
        require_string(
            item.get("source_category_id"),
            f"sidecar_outputs[{index}].source_category_id",
        )
        require_string(item.get("notes"), f"sidecar_outputs[{index}].notes")
        future_fields.add(future_field)

    for required in REQUIRED_SIDECAR_FIELDS:
        if required not in future_fields:
            fail(f"sidecar_outputs missing {required}")


def validate_out_of_scope_targets(fixture: dict[str, Any]) -> None:
    items = fixture.get("out_of_scope_targets")
    if not isinstance(items, list) or not items:
        fail("out_of_scope_targets must be a non-empty list")
    fields: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"out_of_scope_targets[{index}] must be an object")
        require_string(item.get("target_id"), f"out_of_scope_targets[{index}].target_id")
        future_field = require_string(
            item.get("future_target_field"),
            f"out_of_scope_targets[{index}].future_target_field",
        )
        reason = require_string(item.get("reason"), f"out_of_scope_targets[{index}].reason")
        if "out_of_scope" not in reason:
            fail(f"out_of_scope_targets[{index}].reason must describe out_of_scope")
        fields.add(future_field)

    for required in REQUIRED_OUT_OF_SCOPE_TARGETS:
        if required not in fields:
            fail(f"out_of_scope_targets missing {required}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_adapter_mapping_plan")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_source_inputs(fixture)
        mappings = validate_mappings(fixture)
        validate_required_statuses(mappings)
        validate_blocked_mappings(fixture)
        validate_sidecar_outputs(fixture)
        validate_out_of_scope_targets(fixture)
        validate_doc()
    except (OSError, OfflineRemapperAdapterMappingPlanError, ValueError) as exc:
        print("status=FAIL")
        print("mappings=0")
        print("adapter_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"mappings={len(fixture['mappings'])}")
    print("adapter_implemented=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("external_source_promoted_to_authority=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
