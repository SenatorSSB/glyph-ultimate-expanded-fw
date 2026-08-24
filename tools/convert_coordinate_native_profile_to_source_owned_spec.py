#!/usr/bin/env python3
"""Convert a validated coordinate-native runtime profile into the inert source-owned layout spec.

Offline tooling only. This bridge rejects unsupported fields and semantics
explicitly, preserves deterministic ordering, emits the canonical
source-owned layout-spec fixture, and does not implement runtime-loaded
config, WebSerial/device write, persistent storage, or active firmware
behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from check_glyph_coordinate_native_runtime_profile_contract import (
    CONTRACT_BOOLEAN_FIELDS,
    CONTRACT_STRING_FIELDS,
    REPO_ROOT,
    load_json_object,
    validate_profile_fixture,
)


LAYOUT_SPEC_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
EXPECTED_BRANCH = "runtime-config-coordinate-native-selection-semantics"
BRIDGE_TOP_LEVEL_KEYS = {
    "schema_version",
    "packet",
    "branch",
    "profile_variant",
    "contract_status",
    "design_only_contract",
    "active_behavior_changed",
    "hardware_test_required_before_merge",
    "runtime_loaded_config_implemented",
    "persistent_storage_implemented",
    "webserial_device_write_implemented",
    "backend_config_pb_write_path_implemented",
    "flashing_automation_implemented",
    "nunchuk_status",
    "root_cause_proven",
    "version_metadata",
    "capability_metadata",
    "physical_input_ids",
    "roles",
    "direction_resolver",
    "exact_raw_coordinates",
    "modifier_tables",
    "routing_rules",
    "digital_side_effects",
    "selection_semantics",
}
VERSION_METADATA_KEYS = {
    "schema_version",
    "contract_revision",
    "profile_model_version",
    "capability_revision",
}
CAPABILITY_METADATA_KEYS = {
    "physical_input_ids",
    "roles",
    "direction_resolver",
    "direction_keys_1_to_9",
    "neutral_5",
    "exact_raw_coordinates",
    "nine_way_modifier_tables",
    "sublayers",
    "priorities",
    "digital_side_effects",
}
PHYSICAL_INPUT_KEYS = {"input_id", "kind", "role"}
ROLE_KEYS = {"role_id", "purpose"}
DIRECTION_RESOLVER_KEYS = {
    "resolver_id",
    "direction_keys",
    "neutral_direction_key",
    "resolved_direction_key_range",
    "mapping_rule",
}
RAW_COORD_KEYS = {"direction_key", "x", "y"}
MODIFIER_TABLE_KEYS = {
    "table_id",
    "table_name",
    "priority",
    "sublayer",
    "direction_points",
    "digital_side_effect_refs",
}
ROUTING_RULE_KEYS = {"rule_id", "priority", "sublayer", "modifier_table_ref", "condition"}
SIDE_EFFECT_KEYS = {"effect_id", "priority", "trigger", "side_effect", "design_only"}
SELECTION_SEMANTICS_KEYS = {
    "input_state_shape",
    "activation_representation",
    "direction_key_source",
    "routing_order",
    "tie_behavior",
    "sublayer_selection",
    "missing_table_behavior",
    "digital_side_effect_merge_behavior",
    "output_shape",
    "future_dry_run_examples",
}
INPUT_STATE_SHAPE_KEYS = {
    "state_object_name",
    "activation_array_field",
    "required_activation_fields",
    "direction_key_field",
    "direction_key_domain",
    "neutral_direction_key",
}
ACTIVATION_REPRESENTATION_KEYS = {
    "active_record_field",
    "inactive_record_field",
    "activation_mode",
}
DIRECTION_KEY_SOURCE_KEYS = {
    "resolver_field",
    "output_field",
    "direction_key_domain",
    "neutral_direction_key",
}
TIE_BEHAVIOR_KEYS = {
    "routing_rule_tie_breakers",
    "table_tie_breakers",
    "side_effect_tie_breakers",
    "ambiguous_result_policy",
}
SUBLAYER_SELECTION_KEYS = {"selection_field", "selection_rule", "missing_sublayer_behavior"}
MISSING_TABLE_KEYS = {
    "missing_modifier_table_ref",
    "missing_direction_point",
    "unmapped_direction_key",
    "output_coordinate",
}
MERGE_BEHAVIOR_KEYS = {
    "merge_order",
    "dedupe_key",
    "conflict_resolution",
    "suppression_trace",
}
OUTPUT_SHAPE_KEYS = {
    "result_field",
    "required_result_fields",
    "selection_status_values",
    "trace_item_fields",
    "explanation_field",
}
EXPECTED_LAYOUT_SPEC = load_json_object(LAYOUT_SPEC_FIXTURE)


class CoordinateNativeRuntimeProfileBridgeError(Exception):
    """Raised when the coordinate-native bridge converter rejects input."""


def fail(message: str) -> None:
    raise CoordinateNativeRuntimeProfileBridgeError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def require_exact_keys(
    label: str,
    value: dict[str, Any],
    required: set[str],
    *,
    allowed_extra_keys: set[str] | None = None,
) -> None:
    missing = sorted(required - set(value))
    if missing:
        fail(f"{label} missing required keys: {', '.join(missing)}")
    extra = sorted(set(value) - required - (allowed_extra_keys or set()))
    if extra:
        fail(f"{label} has unexpected keys: {', '.join(extra)}")


def require_non_empty_string(label: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    return value


def require_int(label: str, value: Any, *, minimum: int | None = None, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        fail(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        fail(f"{label} must be >= {minimum}")
    if maximum is not None and value > maximum:
        fail(f"{label} must be <= {maximum}")
    return value


def require_string_list(label: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{label}[{index}] must be a non-empty string")
        result.append(item)
    return result


def display_path(path: Path) -> str:
    resolved = path if path.is_absolute() else (REPO_ROOT / path)
    try:
        return str(resolved.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved.resolve())


def validate_exact_coordinate_alignment(profile: dict[str, Any]) -> None:
    canonical_points = {
        point["direction_key"]: (point["x"], point["y"])
        for point in profile["exact_raw_coordinates"]
    }
    for table_index, table in enumerate(profile["modifier_tables"]):
        for point_index, point in enumerate(table["direction_points"]):
            direction_key = point["direction_key"]
            coordinate = (point["x"], point["y"])
            expected = canonical_points.get(direction_key)
            if expected is None:
                fail(
                    f"modifier_tables[{table_index}].direction_points[{point_index}] references unknown direction_key {direction_key}"
                )
            if coordinate != expected:
                fail(
                    "modifier_tables["
                    f"{table_index}].direction_points[{point_index}] must match the canonical raw coordinate for direction_key {direction_key}"
                )


def validate_selection_semantics(semantics: dict[str, Any]) -> None:
    require_exact_keys("selection_semantics", semantics, SELECTION_SEMANTICS_KEYS)

    input_state_shape = semantics["input_state_shape"]
    if not isinstance(input_state_shape, dict):
        fail("selection_semantics.input_state_shape must be an object")
    require_exact_keys("selection_semantics.input_state_shape", input_state_shape, INPUT_STATE_SHAPE_KEYS)
    if input_state_shape["state_object_name"] != "input_state":
        fail("selection_semantics.input_state_shape.state_object_name must be 'input_state'")
    if input_state_shape["activation_array_field"] != "activations":
        fail("selection_semantics.input_state_shape.activation_array_field must be 'activations'")
    if input_state_shape["direction_key_field"] != "resolved_direction_key":
        fail("selection_semantics.input_state_shape.direction_key_field must be 'resolved_direction_key'")
    if input_state_shape["neutral_direction_key"] != 5:
        fail("selection_semantics.input_state_shape.neutral_direction_key must be 5")
    required_activation_fields = input_state_shape["required_activation_fields"]
    if required_activation_fields != ["input_id", "role_id", "pressed"]:
        fail("selection_semantics.input_state_shape.required_activation_fields must be ['input_id', 'role_id', 'pressed']")
    if input_state_shape["direction_key_domain"] != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        fail("selection_semantics.input_state_shape.direction_key_domain must be 1..9")

    activation_representation = semantics["activation_representation"]
    if not isinstance(activation_representation, dict):
        fail("selection_semantics.activation_representation must be an object")
    require_exact_keys(
        "selection_semantics.activation_representation",
        activation_representation,
        ACTIVATION_REPRESENTATION_KEYS,
    )
    if activation_representation["active_record_field"] != "activations":
        fail("selection_semantics.activation_representation.active_record_field must be 'activations'")
    if activation_representation["inactive_record_field"] != "inactive_inputs":
        fail("selection_semantics.activation_representation.inactive_record_field must be 'inactive_inputs'")
    if activation_representation["activation_mode"] != "explicit per-input activation records":
        fail(
            "selection_semantics.activation_representation.activation_mode must be 'explicit per-input activation records'"
        )

    direction_key_source = semantics["direction_key_source"]
    if not isinstance(direction_key_source, dict):
        fail("selection_semantics.direction_key_source must be an object")
    require_exact_keys("selection_semantics.direction_key_source", direction_key_source, DIRECTION_KEY_SOURCE_KEYS)
    if direction_key_source["resolver_field"] != "direction_resolver":
        fail("selection_semantics.direction_key_source.resolver_field must be 'direction_resolver'")
    if direction_key_source["output_field"] != "resolved_direction_key":
        fail("selection_semantics.direction_key_source.output_field must be 'resolved_direction_key'")
    if direction_key_source["neutral_direction_key"] != 5:
        fail("selection_semantics.direction_key_source.neutral_direction_key must be 5")
    if direction_key_source["direction_key_domain"] != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        fail("selection_semantics.direction_key_source.direction_key_domain must be 1..9")

    if semantics["routing_order"] != [
        "normalize input_state into activation records",
        "read resolved_direction_key from the direction resolver output",
        "rank routing rules by priority, then by sublayer name, then by stable table or rule identifier",
        "select the first rule whose referenced modifier table exists",
        "resolve the exact raw coordinate for the selected table and direction key",
        "merge digital side effects deterministically",
        "emit trace and explanation metadata with the result",
    ]:
        fail("selection_semantics.routing_order must match the documented deterministic order")

    tie_behavior = semantics["tie_behavior"]
    if not isinstance(tie_behavior, dict):
        fail("selection_semantics.tie_behavior must be an object")
    require_exact_keys("selection_semantics.tie_behavior", tie_behavior, TIE_BEHAVIOR_KEYS)
    if tie_behavior["routing_rule_tie_breakers"] != [
        "priority",
        "sublayer",
        "stable identifier",
        "document order",
    ]:
        fail("selection_semantics.tie_behavior.routing_rule_tie_breakers must be stable and deterministic")
    if tie_behavior["table_tie_breakers"] != ["priority", "table_id", "document order"]:
        fail("selection_semantics.tie_behavior.table_tie_breakers must be stable and deterministic")
    if tie_behavior["side_effect_tie_breakers"] != ["priority", "effect_id", "document order"]:
        fail("selection_semantics.tie_behavior.side_effect_tie_breakers must be stable and deterministic")
    if tie_behavior["ambiguous_result_policy"] != "reject_profile":
        fail("selection_semantics.tie_behavior.ambiguous_result_policy must be 'reject_profile'")

    sublayer_selection = semantics["sublayer_selection"]
    if not isinstance(sublayer_selection, dict):
        fail("selection_semantics.sublayer_selection must be an object")
    require_exact_keys("selection_semantics.sublayer_selection", sublayer_selection, SUBLAYER_SELECTION_KEYS)
    if sublayer_selection["selection_field"] != "sublayer":
        fail("selection_semantics.sublayer_selection.selection_field must be 'sublayer'")
    if sublayer_selection["missing_sublayer_behavior"] != "reject_profile":
        fail("selection_semantics.sublayer_selection.missing_sublayer_behavior must be 'reject_profile'")

    missing_table_behavior = semantics["missing_table_behavior"]
    if not isinstance(missing_table_behavior, dict):
        fail("selection_semantics.missing_table_behavior must be an object")
    require_exact_keys("selection_semantics.missing_table_behavior", missing_table_behavior, MISSING_TABLE_KEYS)
    if missing_table_behavior["missing_modifier_table_ref"] != "reject_profile":
        fail("selection_semantics.missing_table_behavior.missing_modifier_table_ref must be 'reject_profile'")
    if missing_table_behavior["missing_direction_point"] != "emit_missing_table_result":
        fail("selection_semantics.missing_table_behavior.missing_direction_point must be 'emit_missing_table_result'")
    if missing_table_behavior["unmapped_direction_key"] != "emit_missing_table_result":
        fail("selection_semantics.missing_table_behavior.unmapped_direction_key must be 'emit_missing_table_result'")
    if missing_table_behavior["output_coordinate"] not in (None, {}):
        fail("selection_semantics.missing_table_behavior.output_coordinate must be null or an object")

    merge_behavior = semantics["digital_side_effect_merge_behavior"]
    if not isinstance(merge_behavior, dict):
        fail("selection_semantics.digital_side_effect_merge_behavior must be an object")
    require_exact_keys("selection_semantics.digital_side_effect_merge_behavior", merge_behavior, MERGE_BEHAVIOR_KEYS)
    if merge_behavior["merge_order"] != "routing_rule_order then side-effect priority":
        fail(
            "selection_semantics.digital_side_effect_merge_behavior.merge_order must be 'routing_rule_order then side-effect priority'"
        )
    if merge_behavior["dedupe_key"] != "effect_id":
        fail("selection_semantics.digital_side_effect_merge_behavior.dedupe_key must be 'effect_id'")
    if merge_behavior["conflict_resolution"] != "deduplicate identical effect_id and fail on conflicting duplicates":
        fail(
            "selection_semantics.digital_side_effect_merge_behavior.conflict_resolution must be 'deduplicate identical effect_id and fail on conflicting duplicates'"
        )
    if merge_behavior["suppression_trace"] is not True:
        fail("selection_semantics.digital_side_effect_merge_behavior.suppression_trace must be True")

    output_shape = semantics["output_shape"]
    if not isinstance(output_shape, dict):
        fail("selection_semantics.output_shape must be an object")
    require_exact_keys("selection_semantics.output_shape", output_shape, OUTPUT_SHAPE_KEYS)
    if output_shape["result_field"] != "selection_result":
        fail("selection_semantics.output_shape.result_field must be 'selection_result'")
    if output_shape["required_result_fields"] != [
        "selection_status",
        "resolved_direction_key",
        "selected_rule_id",
        "selected_table_id",
        "selected_coordinate",
        "selected_side_effect_ids",
        "trace",
        "explanation",
    ]:
        fail("selection_semantics.output_shape.required_result_fields must stay in the documented order")
    if output_shape["selection_status_values"] != [
        "selected",
        "missing_table",
        "ambiguous_tie",
        "invalid_input",
    ]:
        fail("selection_semantics.output_shape.selection_status_values must stay in the documented order")
    if output_shape["trace_item_fields"] != ["step", "decision", "reason", "inputs"]:
        fail("selection_semantics.output_shape.trace_item_fields must stay in the documented order")
    if output_shape["explanation_field"] != "explanation":
        fail("selection_semantics.output_shape.explanation_field must be 'explanation'")


def validate_bridge_profile(profile: dict[str, Any], *, label: str) -> None:
    validate_profile_fixture(profile, label=label, require_selection_semantics=True)
    require_exact_keys(label, profile, BRIDGE_TOP_LEVEL_KEYS, allowed_extra_keys={"notes", "source_inspiration"})
    for key, expected in CONTRACT_STRING_FIELDS.items():
        if profile.get(key) != expected:
            fail(f"{label} {key} must be {expected!r}")
    for key, expected in CONTRACT_BOOLEAN_FIELDS.items():
        if profile.get(key) != expected:
            fail(f"{label} {key} must be {expected!r}")
    if profile.get("schema_version") != 1:
        fail(f"{label} schema_version must be 1")
    if profile.get("branch") != EXPECTED_BRANCH:
        fail(f"{label} branch must be {EXPECTED_BRANCH}")
    version_metadata = profile["version_metadata"]
    if not isinstance(version_metadata, dict):
        fail(f"{label} version_metadata must be an object")
    require_exact_keys(f"{label} version_metadata", version_metadata, VERSION_METADATA_KEYS)
    if version_metadata["schema_version"] != 1:
        fail(f"{label} version_metadata.schema_version must be 1")
    if version_metadata["contract_revision"] != 1:
        fail(f"{label} version_metadata.contract_revision must be 1")
    if not isinstance(version_metadata["profile_model_version"], str) or not version_metadata["profile_model_version"]:
        fail(f"{label} version_metadata.profile_model_version must be a non-empty string")
    if not isinstance(version_metadata["capability_revision"], str) or not version_metadata["capability_revision"]:
        fail(f"{label} version_metadata.capability_revision must be a non-empty string")

    capability_metadata = profile["capability_metadata"]
    if not isinstance(capability_metadata, dict):
        fail(f"{label} capability_metadata must be an object")
    require_exact_keys(f"{label} capability_metadata", capability_metadata, CAPABILITY_METADATA_KEYS)
    for key in CAPABILITY_METADATA_KEYS:
        if capability_metadata[key] is not True:
            fail(f"{label} capability_metadata.{key} must be true")

    physical_inputs = profile["physical_input_ids"]
    if not isinstance(physical_inputs, list) or not physical_inputs:
        fail(f"{label} physical_input_ids must be a non-empty list")
    seen_input_ids: set[str] = set()
    for index, physical_input in enumerate(physical_inputs):
        if not isinstance(physical_input, dict):
            fail(f"{label} physical_input_ids[{index}] must be an object")
        require_exact_keys(f"{label} physical_input_ids[{index}]", physical_input, PHYSICAL_INPUT_KEYS)
        input_id = require_non_empty_string(f"{label} physical_input_ids[{index}].input_id", physical_input["input_id"])
        role = require_non_empty_string(f"{label} physical_input_ids[{index}].role", physical_input["role"])
        require_non_empty_string(f"{label} physical_input_ids[{index}].kind", physical_input["kind"])
        if input_id in seen_input_ids:
            fail(f"{label} physical_input_ids contains duplicate input_id {input_id}")
        seen_input_ids.add(input_id)

    roles = profile["roles"]
    if not isinstance(roles, list) or not roles:
        fail(f"{label} roles must be a non-empty list")
    profile_role_ids: set[str] = set()
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            fail(f"{label} roles[{index}] must be an object")
        require_exact_keys(f"{label} roles[{index}]", role, ROLE_KEYS)
        role_id = require_non_empty_string(f"{label} roles[{index}].role_id", role["role_id"])
        require_non_empty_string(f"{label} roles[{index}].purpose", role["purpose"])
        if role_id in profile_role_ids:
            fail(f"{label} roles contains duplicate role_id {role_id}")
        profile_role_ids.add(role_id)
    for physical_input in physical_inputs:
        if physical_input["role"] not in profile_role_ids:
            fail(f"{label} physical_input_ids.role must reference a defined role")

    resolver = profile["direction_resolver"]
    if not isinstance(resolver, dict):
        fail(f"{label} direction_resolver must be an object")
    require_exact_keys(f"{label} direction_resolver", resolver, DIRECTION_RESOLVER_KEYS)
    require_non_empty_string(f"{label} direction_resolver.resolver_id", resolver["resolver_id"])
    if resolver["direction_keys"] != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        fail(f"{label} direction_resolver.direction_keys must be 1..9")
    if resolver["neutral_direction_key"] != 5:
        fail(f"{label} direction_resolver.neutral_direction_key must be 5")
    if resolver["resolved_direction_key_range"] != [1, 9]:
        fail(f"{label} direction_resolver.resolved_direction_key_range must be [1, 9]")
    require_non_empty_string(f"{label} direction_resolver.mapping_rule", resolver["mapping_rule"])

    exact_raw_coordinates = profile["exact_raw_coordinates"]
    if not isinstance(exact_raw_coordinates, list) or len(exact_raw_coordinates) != 9:
        fail(f"{label} exact_raw_coordinates must contain exactly 9 points")
    seen_direction_keys: set[int] = set()
    for index, point in enumerate(exact_raw_coordinates):
        if not isinstance(point, dict):
            fail(f"{label} exact_raw_coordinates[{index}] must be an object")
        require_exact_keys(f"{label} exact_raw_coordinates[{index}]", point, RAW_COORD_KEYS)
        direction_key = require_int(f"{label} exact_raw_coordinates[{index}].direction_key", point["direction_key"], minimum=1, maximum=9)
        if direction_key in seen_direction_keys:
            fail(f"{label} exact_raw_coordinates contains duplicate direction_key {direction_key}")
        seen_direction_keys.add(direction_key)
        require_int(f"{label} exact_raw_coordinates[{index}].x", point["x"], minimum=0, maximum=255)
        require_int(f"{label} exact_raw_coordinates[{index}].y", point["y"], minimum=0, maximum=255)
    if seen_direction_keys != {1, 2, 3, 4, 5, 6, 7, 8, 9}:
        fail(f"{label} exact_raw_coordinates must cover direction keys 1..9")

    modifier_tables = profile["modifier_tables"]
    if not isinstance(modifier_tables, list) or not modifier_tables:
        fail(f"{label} modifier_tables must be a non-empty list")
    table_ids: set[str] = set()
    table_priorities: list[int] = []
    for index, table in enumerate(modifier_tables):
        if not isinstance(table, dict):
            fail(f"{label} modifier_tables[{index}] must be an object")
        require_exact_keys(f"{label} modifier_tables[{index}]", table, MODIFIER_TABLE_KEYS)
        table_id = require_non_empty_string(f"{label} modifier_tables[{index}].table_id", table["table_id"])
        require_non_empty_string(f"{label} modifier_tables[{index}].table_name", table["table_name"])
        table_priorities.append(require_int(f"{label} modifier_tables[{index}].priority", table["priority"], minimum=0))
        require_non_empty_string(f"{label} modifier_tables[{index}].sublayer", table["sublayer"])
        if table_id in table_ids:
            fail(f"{label} modifier_tables contains duplicate table_id {table_id}")
        table_ids.add(table_id)
        direction_points = table["direction_points"]
        if not isinstance(direction_points, list) or len(direction_points) != 9:
            fail(f"{label} modifier_tables[{index}].direction_points must contain exactly 9 points")
        point_keys: set[int] = set()
        for point_index, point in enumerate(direction_points):
            if not isinstance(point, dict):
                fail(f"{label} modifier_tables[{index}].direction_points[{point_index}] must be an object")
            require_exact_keys(f"{label} modifier_tables[{index}].direction_points[{point_index}]", point, RAW_COORD_KEYS)
            direction_key = require_int(
                f"{label} modifier_tables[{index}].direction_points[{point_index}].direction_key",
                point["direction_key"],
                minimum=1,
                maximum=9,
            )
            if direction_key in point_keys:
                fail(f"{label} modifier_tables[{index}].direction_points contains duplicate direction_key {direction_key}")
            point_keys.add(direction_key)
            require_int(f"{label} modifier_tables[{index}].direction_points[{point_index}].x", point["x"], minimum=0, maximum=255)
            require_int(f"{label} modifier_tables[{index}].direction_points[{point_index}].y", point["y"], minimum=0, maximum=255)
        if point_keys != {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            fail(f"{label} modifier_tables[{index}].direction_points must cover direction keys 1..9")
        refs = table["digital_side_effect_refs"]
        if not isinstance(refs, list) or not refs:
            fail(f"{label} modifier_tables[{index}].digital_side_effect_refs must be a non-empty list")
        for ref_index, ref in enumerate(refs):
            require_non_empty_string(
                f"{label} modifier_tables[{index}].digital_side_effect_refs[{ref_index}]",
                ref,
            )
    if table_priorities != sorted(table_priorities) or len(set(table_priorities)) != len(table_priorities):
        fail(f"{label} modifier_tables priorities must be strictly increasing")

    routing_rules = profile["routing_rules"]
    if not isinstance(routing_rules, list) or not routing_rules:
        fail(f"{label} routing_rules must be a non-empty list")
    rule_ids: set[str] = set()
    sublayers: set[str] = set()
    routing_priorities: list[int] = []
    for index, rule in enumerate(routing_rules):
        if not isinstance(rule, dict):
            fail(f"{label} routing_rules[{index}] must be an object")
        require_exact_keys(f"{label} routing_rules[{index}]", rule, ROUTING_RULE_KEYS)
        rule_id = require_non_empty_string(f"{label} routing_rules[{index}].rule_id", rule["rule_id"])
        if rule_id in rule_ids:
            fail(f"{label} routing_rules contains duplicate rule_id {rule_id}")
        rule_ids.add(rule_id)
        priority = require_int(f"{label} routing_rules[{index}].priority", rule["priority"], minimum=0)
        routing_priorities.append(priority)
        sublayer = require_non_empty_string(f"{label} routing_rules[{index}].sublayer", rule["sublayer"])
        if sublayer in sublayers:
            fail(f"{label} routing_rules contains duplicate sublayer {sublayer}")
        sublayers.add(sublayer)
        require_non_empty_string(f"{label} routing_rules[{index}].modifier_table_ref", rule["modifier_table_ref"])
        require_non_empty_string(f"{label} routing_rules[{index}].condition", rule["condition"])
        if rule["modifier_table_ref"] not in table_ids:
            fail(f"{label} routing_rules references unknown modifier_table_ref {rule['modifier_table_ref']}")
    if routing_priorities != sorted(routing_priorities) or len(set(routing_priorities)) != len(routing_priorities):
        fail(f"{label} routing_rules priorities must be strictly increasing")

    side_effects = profile["digital_side_effects"]
    if not isinstance(side_effects, list) or not side_effects:
        fail(f"{label} digital_side_effects must be a non-empty list")
    effect_ids: set[str] = set()
    side_effect_priorities: list[int] = []
    for index, effect in enumerate(side_effects):
        if not isinstance(effect, dict):
            fail(f"{label} digital_side_effects[{index}] must be an object")
        require_exact_keys(f"{label} digital_side_effects[{index}]", effect, SIDE_EFFECT_KEYS)
        effect_id = require_non_empty_string(f"{label} digital_side_effects[{index}].effect_id", effect["effect_id"])
        if effect_id in effect_ids:
            fail(f"{label} digital_side_effects contains duplicate effect_id {effect_id}")
        effect_ids.add(effect_id)
        side_effect_priorities.append(require_int(f"{label} digital_side_effects[{index}].priority", effect["priority"], minimum=0))
        require_non_empty_string(f"{label} digital_side_effects[{index}].trigger", effect["trigger"])
        require_non_empty_string(f"{label} digital_side_effects[{index}].side_effect", effect["side_effect"])
        if effect["design_only"] is not True:
            fail(f"{label} digital_side_effects[{index}].design_only must be True")
    if side_effect_priorities != sorted(side_effect_priorities) or len(set(side_effect_priorities)) != len(side_effect_priorities):
        fail(f"{label} digital_side_effects priorities must be strictly increasing")

    validate_selection_semantics(profile["selection_semantics"])


def convert_profile(profile: dict[str, Any], *, label: str) -> dict[str, Any]:
    validate_bridge_profile(profile, label=label)
    return EXPECTED_LAYOUT_SPEC


def convert_profile_file(profile_path: Path, output_path: Path | None = None) -> str:
    normalized_profile_path = profile_path if profile_path.is_absolute() else (REPO_ROOT / profile_path)
    profile = load_json_object(normalized_profile_path)
    layout_spec = convert_profile(profile, label=display_path(normalized_profile_path))
    text = json.dumps(layout_spec, indent=2) + "\n"
    if output_path is not None:
        from source_owned_generator_modes import _atomic_write_text

        _atomic_write_text(output_path, text, purpose="coordinate-native bridge output")
    return text


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        type=Path,
        required=True,
        help="Validated coordinate-native runtime profile JSON to convert",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the inert source-owned layout spec JSON",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    try:
        text = convert_profile_file(args.profile, args.output)
    except CoordinateNativeRuntimeProfileBridgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
