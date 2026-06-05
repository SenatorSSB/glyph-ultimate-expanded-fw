#!/usr/bin/env python3
"""Offline validator for Glyph runtime config candidate payloads.

This module validates a future candidate payload shape for docs/tools review.
It is not firmware source, not runtime-loaded config, not serial/device write
behavior, and not hardware validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_NAME = "glyph_runtime_config_candidate"
CANDIDATE_VERSION = 1
STATUS = "candidate_docs_only_not_runtime_loaded"
MODE_SCOPE = "MODE_ULTIMATE"
HARDWARE_STATUS = "not_new_hardware_result"
NUNCHUK_STATUS = "preserved_but_not_hardware_validated"
GENERATED_CONFIG_CONTRACT = (
    "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)
RUNTIME_VALIDATION_CONTRACT = (
    "docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json"
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_name",
    "candidate_version",
    "status",
    "mode_scope",
    "hardware_status",
    "nunchuk_status",
    "source_authority",
    "generated_config_contract",
    "runtime_validation_contract",
    "tables",
    "role_bindings",
    "priority_references",
    "hard_overrides",
    "suppression_rules",
    "metadata",
    "non_goals",
)
REQUIRED_TABLES = (
    "Default",
    "ModeDefault",
    "X1",
    "X2",
    "MX1",
    "MX2",
    "Y1",
    "MY1",
    "LayerNormalX",
    "MLayerNormalX",
    "LayerFlipper",
    "MLayerFlipper",
    "Y1Tilt1",
    "MY1Tilt1",
    "Y1LayerFlipper",
    "MY1LayerFlipper",
    "Y1LayerNormalX",
    "MY1LayerNormalX",
    "Tilt1",
    "Tilt2",
    "Tilt3",
    "MTilt1",
    "MTilt2",
    "MTilt3",
    "Lt1LowMagnitude",
    "Tilt1Minus41",
    "RT1RF4Custom",
)
REQUIRED_ROLE_BINDING_SECTIONS = (
    "buttons",
    "directional",
    "c_stick",
    "modifiers",
    "special_functions",
)
APPROVED_PRIORITY_CLASSES = {
    "digital": (
        "physical_inputs",
        "lf4_submode_active",
        "lt2_sublayer_active",
        "forced_up_resolution",
        "button_carriers",
        "ls_to_dpad_routing",
    ),
    "analog": (
        "table_output",
        "direction_plus_a",
        "rf6_low_magnitude_za",
        "rf7_hard_up_b",
        "c_stick_asdi",
        "rf9_null",
        "nunchuk_override",
    ),
}
ACCEPTED_DATA_CLASSES = (
    "ButtonOutput",
    "DirectionContribution",
    "CStickContribution",
    "TableModifier",
    "CompositeModifier",
    "LayerOverride",
    "SubmodeOverride",
    "HardAnalogOverride",
    "LowMagnitudeOverride",
    "NullAnalogOverride",
    "LsToDpad",
    "SuppressionRule",
    "ForcedDirection",
    "RoleOverride",
)
REQUIRED_HARD_OVERRIDES = {
    "rf7_hard_up_b": {
        "left": [77, 172],
        "center": [128, 172],
        "right": [179, 172],
    },
    "rf9_null": [128, 128],
    "rf6_low_magnitude_table": "Lt1LowMagnitude",
}
REQUIRED_NON_GOALS = {
    "not_firmware_source",
    "not_runtime_loaded",
    "not_serial_device_write",
    "not_hardware_validation",
    "not_nunchuk_hardware_validation",
    "not_senscope_game_semantics",
    "does_not_change_table_values_or_behavior",
}
FORBIDDEN_PAYLOAD_KEYS = {
    "firmware_source_patch",
    "serial_transport_payload",
    "device_write_instruction",
    "device_write_instructions",
    "macro",
    "macros",
    "turbo",
    "timing_automation",
    "timing_or_history_logic",
    "one_shot",
    "one_shot_behavior",
    "toggle",
    "toggles",
    "history_dependent_logic",
    "history_dependent_input_logic",
    "runtime_loaded_config_implementation",
    "phase_order_mutation",
}
FORBIDDEN_VALUE_PHRASES = (
    "firmware source patch",
    "serial transport payload",
    "device write instruction",
    "device-write instruction",
    "write to device",
    "device writing instructions",
    "push-to-device",
    "flash device",
    "macro/turbo",
    "macro or turbo",
    "timing automation",
    "one-shot",
    "one shot",
    "toggle behavior",
    "history-dependent",
    "history dependent",
    "runtime-loaded config implementation",
    "runtime loaded config implementation",
    "phase-order mutation",
    "phase order mutation",
)
ARBITRARY_CODE_PATTERNS = (
    "<script",
    "eval(",
    "function(",
    "function (",
    "=>",
    "#include",
    "constexpr ",
    "void ",
    "import os",
    "subprocess.",
)


@dataclass(frozen=True)
class ValidationIssue:
    """A structured runtime config candidate validation issue."""

    code: str
    path: str
    message: str


class RuntimeConfigCandidateValidationError(ValueError):
    """Raised when validate_runtime_config_candidate_or_raise finds issues."""

    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        summary = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        super().__init__(summary)


def load_json_object(path: Path) -> dict:
    """Load a JSON object from path."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def validate_runtime_config_candidate(payload: dict) -> list[ValidationIssue]:
    """Return all validation issues for a runtime config candidate payload."""

    if not isinstance(payload, dict):
        return [
            ValidationIssue(
                "E_ROOT_NOT_OBJECT",
                "$",
                "runtime config candidate payload must be an object",
            )
        ]

    issues: list[ValidationIssue] = []
    _validate_required_top_level(payload, issues)
    _validate_expected_scalars(payload, issues)
    _validate_source_authority(payload, issues)
    _validate_contract_references(payload, issues)
    _validate_tables(payload, issues)
    _validate_role_bindings(payload, issues)
    _validate_priority_references(payload, issues)
    _validate_hard_overrides(payload, issues)
    _validate_suppression_rules(payload, issues)
    _validate_metadata(payload, issues)
    _validate_non_goals(payload, issues)
    _validate_forbidden_payload_content(payload, issues)
    return issues


def validate_runtime_config_candidate_or_raise(payload: dict) -> None:
    """Raise RuntimeConfigCandidateValidationError if payload is invalid."""

    issues = validate_runtime_config_candidate(payload)
    if issues:
        raise RuntimeConfigCandidateValidationError(issues)


def _add(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code, path, message))


def _validate_required_top_level(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    for key in REQUIRED_TOP_LEVEL_FIELDS:
        if key not in payload:
            _add(issues, "E_MISSING_REQUIRED_FIELD", f"$.{key}", "missing required top-level field")


def _validate_expected_scalars(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "candidate_version": CANDIDATE_VERSION,
        "status": STATUS,
        "mode_scope": MODE_SCOPE,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            _add(issues, f"E_INVALID_{key.upper()}", f"$.{key}", f"must be {value!r}")


def _validate_source_authority(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    source_authority = payload.get("source_authority")
    if not isinstance(source_authority, dict):
        _add(issues, "E_SOURCE_AUTHORITY_NOT_OBJECT", "$.source_authority", "must be an object")


def _validate_contract_references(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    expected = {
        "generated_config_contract": GENERATED_CONFIG_CONTRACT,
        "runtime_validation_contract": RUNTIME_VALIDATION_CONTRACT,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            _add(issues, f"E_INVALID_{key.upper()}", f"$.{key}", f"must be {value!r}")


def _validate_tables(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    tables = payload.get("tables")
    if not isinstance(tables, dict):
        _add(issues, "E_TABLES_NOT_OBJECT", "$.tables", "must be an object")
        return

    actual = set(tables)
    required = set(REQUIRED_TABLES)
    for name in sorted(required - actual):
        _add(issues, "E_MISSING_REQUIRED_TABLE", f"$.tables.{name}", "missing required table")
    for name in sorted(actual - required):
        _add(issues, "E_UNKNOWN_TABLE", f"$.tables.{name}", "unexpected table")
    if len(tables) != len(REQUIRED_TABLES):
        _add(issues, "E_INVALID_TABLE_COUNT", "$.tables", f"must contain exactly {len(REQUIRED_TABLES)} tables")

    for table_name in REQUIRED_TABLES:
        table = tables.get(table_name)
        if not isinstance(table, list):
            _add(issues, "E_TABLE_NOT_LIST", f"$.tables.{table_name}", "must be a list")
            continue
        if len(table) != 9:
            _add(issues, "E_INVALID_TABLE_POINT_COUNT", f"$.tables.{table_name}", "must contain exactly 9 points")
        for index, point in enumerate(table):
            _validate_point(point, issues, f"$.tables.{table_name}[{index}]")


def _validate_point(point: Any, issues: list[ValidationIssue], path: str) -> None:
    if not isinstance(point, list) or len(point) != 2:
        _add(issues, "E_MALFORMED_TABLE_POINT", path, "point must be [int, int]")
        return
    for coord_index, coord in enumerate(point):
        coord_path = f"{path}[{coord_index}]"
        if isinstance(coord, bool) or not isinstance(coord, int):
            _add(issues, "E_INVALID_POINT_COORDINATE_TYPE", coord_path, "coordinate must be a non-boolean integer")
            continue
        if coord < 0 or coord > 255:
            _add(issues, "E_COORDINATE_OUT_OF_RANGE", coord_path, "coordinate must be in [0,255]")


def _validate_role_bindings(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    role_bindings = payload.get("role_bindings")
    if not isinstance(role_bindings, dict):
        _add(issues, "E_ROLE_BINDINGS_NOT_OBJECT", "$.role_bindings", "must be an object")
        return

    actual = set(role_bindings)
    required = set(REQUIRED_ROLE_BINDING_SECTIONS)
    for section in sorted(required - actual):
        _add(issues, "E_MISSING_ROLE_BINDING_SECTION", f"$.role_bindings.{section}", "missing required section")
    for section in sorted(actual - required):
        _add(issues, "E_UNKNOWN_ROLE_BINDING_SECTION", f"$.role_bindings.{section}", "unknown role binding section")
    for section in REQUIRED_ROLE_BINDING_SECTIONS:
        bindings = role_bindings.get(section)
        if not isinstance(bindings, dict):
            _add(issues, "E_ROLE_BINDING_SECTION_NOT_OBJECT", f"$.role_bindings.{section}", "must be an object")
            continue
        for key, value in bindings.items():
            if not isinstance(key, str) or not isinstance(value, str):
                _add(
                    issues,
                    "E_INVALID_ROLE_BINDING_METADATA",
                    f"$.role_bindings.{section}",
                    "role bindings are bounded string metadata only",
                )


def _validate_priority_references(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    priority_references = payload.get("priority_references")
    if not isinstance(priority_references, dict):
        _add(issues, "E_PRIORITY_REFERENCES_NOT_OBJECT", "$.priority_references", "must be an object")
        return
    for key in APPROVED_PRIORITY_CLASSES:
        value = priority_references.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            _add(issues, "E_INVALID_PRIORITY_REFERENCE_LIST", f"$.priority_references.{key}", "must be a string list")
            continue
        allowed = set(APPROVED_PRIORITY_CLASSES[key])
        for index, item in enumerate(value):
            if item not in allowed:
                _add(
                    issues,
                    "E_UNKNOWN_PRIORITY_CLASS",
                    f"$.priority_references.{key}[{index}]",
                    f"unknown priority class {item!r}",
                )
    for key in sorted(set(priority_references) - set(APPROVED_PRIORITY_CLASSES)):
        _add(issues, "E_UNKNOWN_PRIORITY_REFERENCE_GROUP", f"$.priority_references.{key}", "unknown priority group")


def _validate_hard_overrides(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    if payload.get("hard_overrides") != REQUIRED_HARD_OVERRIDES:
        _add(
            issues,
            "E_INVALID_HARD_OVERRIDES",
            "$.hard_overrides",
            "must match the generated-config contract hard overrides",
        )


def _validate_suppression_rules(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    suppression_rules = payload.get("suppression_rules")
    if not isinstance(suppression_rules, list) or not all(isinstance(item, str) for item in suppression_rules):
        _add(issues, "E_SUPPRESSION_RULES_NOT_STRING_LIST", "$.suppression_rules", "must be a string list")


def _validate_metadata(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        _add(issues, "E_METADATA_NOT_OBJECT", "$.metadata", "must be an object")
        return
    accepted = metadata.get("accepted_data_classes")
    if accepted is not None:
        if not isinstance(accepted, list) or not all(isinstance(item, str) for item in accepted):
            _add(issues, "E_ACCEPTED_DATA_CLASSES_NOT_STRING_LIST", "$.metadata.accepted_data_classes", "must be a string list")
        else:
            unknown = sorted(set(accepted) - set(ACCEPTED_DATA_CLASSES))
            for item in unknown:
                _add(
                    issues,
                    "E_UNKNOWN_ACCEPTED_DATA_CLASS",
                    "$.metadata.accepted_data_classes",
                    f"unknown accepted data class {item!r}",
                )


def _validate_non_goals(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    non_goals = payload.get("non_goals")
    if not isinstance(non_goals, list) or not all(isinstance(item, str) for item in non_goals):
        _add(issues, "E_NON_GOALS_NOT_STRING_LIST", "$.non_goals", "must be a string list")
        return
    for item in sorted(REQUIRED_NON_GOALS - set(non_goals)):
        _add(issues, "E_MISSING_NON_GOAL", "$.non_goals", f"missing required non-goal {item!r}")


def _validate_forbidden_payload_content(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    has_hardware_result_source = _has_hardware_result_source(payload)
    for path, key, value in _walk(payload):
        normalized_key = key.lower() if isinstance(key, str) else ""
        if normalized_key in FORBIDDEN_PAYLOAD_KEYS or "phase_order_mutation" in normalized_key:
            _add(issues, "E_FORBIDDEN_PAYLOAD_CONTENT", path, f"forbidden key {key!r}")
        if normalized_key in {"data_class", "role_class", "class", "class_name"} and isinstance(value, str):
            if value not in ACCEPTED_DATA_CLASSES:
                _add(issues, "E_UNKNOWN_ACCEPTED_DATA_CLASS", path, f"unknown accepted data class {value!r}")
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        for phrase in FORBIDDEN_VALUE_PHRASES:
            if phrase in lowered:
                _add(issues, "E_FORBIDDEN_PAYLOAD_CONTENT", path, f"forbidden phrase {phrase!r}")
        if any(pattern in lowered for pattern in ARBITRARY_CODE_PATTERNS):
            _add(issues, "E_ARBITRARY_SCRIPT_CODE_TEXT", path, "arbitrary script/code text is not allowed")
        if _is_hardware_validation_claim(lowered) and not has_hardware_result_source:
            _add(
                issues,
                "E_HARDWARE_VALIDATION_CLAIM_WITHOUT_RESULT_SOURCE",
                path,
                "hardware validation claims require an explicit result source",
            )
        if _is_nunchuk_hardware_validation_claim(lowered) and not has_hardware_result_source:
            _add(
                issues,
                "E_NUNCHUK_HARDWARE_VALIDATION_CLAIM_WITHOUT_RESULT_SOURCE",
                path,
                "nunchuk hardware validation claims require an explicit result source",
            )


def _walk(value: Any, path: str = "$", key: str = "") -> list[tuple[str, str, Any]]:
    entries = [(path, key, value)]
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            child_path = f"{path}.{child_key}" if isinstance(child_key, str) else f"{path}.{child_key!r}"
            entries.extend(_walk(child_value, child_path, str(child_key)))
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            entries.extend(_walk(child_value, f"{path}[{index}]", key))
    return entries


def _has_hardware_result_source(payload: dict[str, Any]) -> bool:
    source_authority = payload.get("source_authority")
    if not isinstance(source_authority, dict):
        return False
    return any(key in source_authority for key in ("hardware_result_source", "hardware_result", "hardware_result_fixture"))


def _is_hardware_validation_claim(value: str) -> bool:
    if "hardware validation" not in value and "hardware-validated" not in value:
        return False
    negations = (
        "not hardware validation",
        "not_hardware_validation",
        "not hardware-validated",
        "not_hardware_validated",
        "no hardware validation",
        "without hardware validation",
        "does not validate hardware",
    )
    return not any(negation in value for negation in negations)


def _is_nunchuk_hardware_validation_claim(value: str) -> bool:
    if "nunchuk" not in value:
        return False
    return _is_hardware_validation_claim(value)
