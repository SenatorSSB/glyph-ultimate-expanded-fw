#!/usr/bin/env python3
"""Validate docs-only runtime-loaded config design contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_loaded_config_design_v0_2026-05-28.json"
)
VALIDATION_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json"
)
GENERATED_CONFIG_CONTRACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)
SENSCOPE_EXPORT_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json"
)
DESIGN_DOC_PATH = REPO_ROOT / "docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md"
VALIDATION_DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md"
)

EXPECTED_DESIGN = {
    "schema_name": "glyph_runtime_loaded_config_design",
    "design_version": 1,
    "status": "design_only_not_implemented",
    "mode_scope": "MODE_ULTIMATE",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
}
EXPECTED_VALIDATION = {
    "schema_name": "glyph_runtime_loaded_config_validation_contract",
    "contract_version": 1,
    "status": "validation_contract_design_only_not_implemented",
    "mode_scope": "MODE_ULTIMATE",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
}
REQUIRED_FIRMWARE_OWNS = {
    "primitive_evaluator",
    "priority_model_semantics",
    "allowed_role_classes",
    "deterministic_current_input_resolver",
    "bounds_checks",
    "unsupported_role_rejection",
}
REQUIRED_CONFIG_MAY_OWN = {
    "physical_button_role_bindings",
    "table_ids_and_table_data",
    "layer_definitions",
    "submode_definitions",
    "hard_override_constants",
    "metadata_and_source_authority",
}
REQUIRED_FORBIDDEN_CAPABILITIES = {
    "arbitrary_scripting",
    "macros",
    "turbo",
    "timing_automation",
    "one_shot_behavior",
    "toggles",
    "history_dependent_input_logic",
    "dynamic_code_execution",
    "evaluator_phase_order_mutation",
}
REQUIRED_STORAGE_BOUNDARIES = {
    "no_storage_implementation",
    "no_serial_write_protocol",
    "no_device_push_path",
    "no_limit_labs_configurator_dependency_assumed",
}
REQUIRED_ACCEPTED_DATA_CLASSES = {
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
}
REQUIRED_REJECTION_RULES = {
    "unknown_schema_version",
    "unknown_mode_scope",
    "missing_required_tables",
    "malformed_table_point",
    "coordinate_outside_0_255",
    "boolean_coordinate_values",
    "unknown_role_class",
    "unknown_priority_class",
    "unsupported_phase_order_mutation",
    "arbitrary_script_code_text",
    "macro_turbo_timing_automation",
    "one_shot_toggle_history_dependent_behavior",
    "missing_source_authority",
    "hardware_validation_claim_without_hardware_result_source",
    "nunchuk_hardware_validation_claim_without_hardware_result_source",
    "device_write_instructions",
    "serial_transport_payloads",
    "firmware_source_patches_embedded_in_config",
}
REQUIRED_TABLE_RULES = {
    "required_tables_present",
    "nine_points_per_table",
    "point_is_two_non_boolean_ints",
    "coordinates_in_0_255",
}
REQUIRED_FORBIDDEN_PAYLOAD_CONTENT = {
    "firmware_source_patch",
    "serial_transport_payload",
    "device_write_instruction",
    "macro_or_turbo_logic",
    "timing_or_history_logic",
}
REQUIRED_SENSCOPE_FORBIDDEN_SCOPE = {
    "device_write",
    "serial_transport",
    "runtime_loaded_config",
    "firmware_behavior_change",
    "profile_schema_change",
    "macro_or_turbo_logic",
    "hardware_validation_claim",
}
REQUIRED_DESIGN_DOC_PHRASES = (
    "does not implement runtime-loaded config",
    "does not implement serial writing",
    "does not implement device writing",
    "does not alter firmware runtime behavior",
    "does not validate hardware",
)
REQUIRED_VALIDATION_DOC_PHRASES = (
    "design-only",
    "not implemented",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
)
GENERATED_CONFIG_CONTRACT_REL = (
    "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)


class RuntimeLoadedConfigDesignError(ValueError):
    """Raised when runtime-loaded config design docs drift from guardrails."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise RuntimeLoadedConfigDesignError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be an object: {display(path)}")
    return payload


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_object(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        fail(f"{key} must be an object")
    return value


def require_superset(actual: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def require_expected_values(payload: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{label}.{key} must be {value!r}")


def validate_source_authority(payload: dict[str, Any], label: str) -> None:
    source_authority = require_object(payload, "source_authority")
    if source_authority.get("generated_config_contract_fixture") != GENERATED_CONFIG_CONTRACT_REL:
        fail(f"{label}.source_authority must reference generated-config contract fixture")


def validate_design_fixture(design: dict[str, Any]) -> tuple[int, int]:
    require_expected_values(design, EXPECTED_DESIGN, "runtime_loaded_design")
    validate_source_authority(design, "runtime_loaded_design")

    firmware_owns = require_string_list(design, "firmware_owns")
    require_superset(firmware_owns, REQUIRED_FIRMWARE_OWNS, "runtime_loaded_design.firmware_owns")

    config_may_own = require_string_list(design, "future_config_may_own")
    require_superset(config_may_own, REQUIRED_CONFIG_MAY_OWN, "runtime_loaded_design.future_config_may_own")

    forbidden = require_string_list(design, "forbidden_config_capabilities")
    require_superset(
        forbidden,
        REQUIRED_FORBIDDEN_CAPABILITIES,
        "runtime_loaded_design.forbidden_config_capabilities",
    )

    storage_boundaries = require_string_list(design, "storage_transport_boundaries")
    require_superset(
        storage_boundaries,
        REQUIRED_STORAGE_BOUNDARIES,
        "runtime_loaded_design.storage_transport_boundaries",
    )

    return len(firmware_owns), len(config_may_own)


def validate_validation_fixture(validation: dict[str, Any]) -> tuple[int, int]:
    require_expected_values(validation, EXPECTED_VALIDATION, "runtime_loaded_validation_contract")
    validate_source_authority(validation, "runtime_loaded_validation_contract")

    accepted_classes = require_string_list(validation, "accepted_data_classes")
    require_superset(
        accepted_classes,
        REQUIRED_ACCEPTED_DATA_CLASSES,
        "runtime_loaded_validation_contract.accepted_data_classes",
    )

    rejection_rules = require_string_list(validation, "required_rejection_rules")
    require_superset(
        rejection_rules,
        REQUIRED_REJECTION_RULES,
        "runtime_loaded_validation_contract.required_rejection_rules",
    )

    table_rules = require_string_list(validation, "table_validation_rules")
    require_superset(
        table_rules,
        REQUIRED_TABLE_RULES,
        "runtime_loaded_validation_contract.table_validation_rules",
    )

    forbidden_payload = require_string_list(validation, "forbidden_payload_content")
    require_superset(
        forbidden_payload,
        REQUIRED_FORBIDDEN_PAYLOAD_CONTENT,
        "runtime_loaded_validation_contract.forbidden_payload_content",
    )

    return len(accepted_classes), len(rejection_rules)


def validate_generated_config_contract(contract: dict[str, Any]) -> None:
    if contract.get("mode_scope") != "MODE_ULTIMATE":
        fail("generated-config contract mode_scope must be MODE_ULTIMATE")
    if contract.get("hardware_status") != "not_new_hardware_result":
        fail("generated-config contract hardware_status must be not_new_hardware_result")

    source_authority = require_object(contract, "source_authority")
    for key in ("runtime", "generated_config_doc", "generated_config_fixture"):
        if key not in source_authority:
            fail(f"generated-config contract source_authority missing {key}")


def validate_senscope_export_contract(export: dict[str, Any]) -> None:
    if export.get("status") != "draft_docs_only_not_implemented":
        fail("Senscope export draft status must remain draft_docs_only_not_implemented")

    forbidden_scope = require_string_list(export, "forbidden_scope")
    require_superset(
        forbidden_scope,
        REQUIRED_SENSCOPE_FORBIDDEN_SCOPE,
        "senscope_export_contract.forbidden_scope",
    )


def validate_doc_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    lowered = path.read_text(encoding="utf-8").lower()
    for phrase in phrases:
        if phrase not in lowered:
            fail(f"{display(path)} missing required caveat phrase: {phrase}")


def validate_contracts() -> tuple[int, int, int, int]:
    design = load_json_object(DESIGN_FIXTURE_PATH)
    validation = load_json_object(VALIDATION_FIXTURE_PATH)
    generated_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
    senscope_export = load_json_object(SENSCOPE_EXPORT_CONTRACT_PATH)

    firmware_owns_count, config_may_own_count = validate_design_fixture(design)
    accepted_classes_count, rejection_rules_count = validate_validation_fixture(validation)
    validate_generated_config_contract(generated_contract)
    validate_senscope_export_contract(senscope_export)
    validate_doc_phrases(DESIGN_DOC_PATH, REQUIRED_DESIGN_DOC_PHRASES)
    validate_doc_phrases(VALIDATION_DOC_PATH, REQUIRED_VALIDATION_DOC_PHRASES)

    return (
        firmware_owns_count,
        config_may_own_count,
        accepted_classes_count,
        rejection_rules_count,
    )


def main() -> int:
    print("glyph_runtime_loaded_config_design")
    try:
        (
            firmware_owns_count,
            config_may_own_count,
            accepted_classes_count,
            rejection_rules_count,
        ) = validate_contracts()
    except (RuntimeLoadedConfigDesignError, OSError, KeyError) as exc:
        print("status=FAIL")
        print("firmware_owned_responsibilities=0")
        print("future_config_may_own=0")
        print("accepted_data_classes=0")
        print("required_rejection_rules=0")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"firmware_owned_responsibilities={firmware_owns_count}")
    print(f"future_config_may_own={config_may_own_count}")
    print(f"accepted_data_classes={accepted_classes_count}")
    print(f"required_rejection_rules={rejection_rules_count}")
    print("hardware_status=not_new_hardware_result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
