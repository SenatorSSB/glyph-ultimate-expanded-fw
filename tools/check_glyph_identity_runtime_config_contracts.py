#!/usr/bin/env python3
"""Validate docs-only generated-config and Senscope export contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_CONFIG_CONTRACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)
SENSCOPE_EXPORT_CONTRACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json"
)
GENERATED_CONFIG_PROTOTYPE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
GENERATED_CONFIG_CONTRACT_DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md"
)
SENSCOPE_EXPORT_CONTRACT_DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md"
)

EXPECTED_GENERATED_CONFIG_CONTRACT = {
    "schema_name": "glyph_identity_runtime_generated_config_contract",
    "contract_version": 1,
    "target_schema_name": "glyph_identity_runtime_generated_config_prototype",
    "target_contract_version": 1,
    "mode_scope": "MODE_ULTIMATE",
    "status": "docs_tools_contract_not_runtime_loaded",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
    "target_source_status": "source_backed_prototype_not_runtime_loaded",
    "target_direction_convention": "numpad",
}
EXPECTED_SENSCOPE_EXPORT_CONTRACT = {
    "schema_name": "glyph_senscope_to_glyph_export_contract_draft",
    "contract_version": 1,
    "status": "draft_docs_only_not_implemented",
    "hardware_status": "not_new_hardware_result",
}
REQUIRED_FORBIDDEN_INTERPRETATIONS = {
    "firmware_source",
    "runtime_loaded_config",
    "serial_device_write_path",
    "hardware_validation",
    "senscope_game_semantics",
    "macro_or_turbo_logic",
}
REQUIRED_EXPORT_PAYLOADS = {
    "neutral_senscope_profile",
    "glyph_generated_config_prototype",
    "table_source_metadata",
    "role_binding_metadata",
    "validation_report",
    "hardware_status_caveat",
    "nunchuk_status_caveat",
}
REQUIRED_VALIDATION_REPORT_SECTIONS = {
    "source_authority",
    "table_count",
    "role_binding_summary",
    "priority_model_summary",
    "hard_override_summary",
    "behavior_case_coverage_summary",
    "no_forbidden_behavior_confirmation",
    "not_hardware_validation_caveat",
    "open_questions",
}
REQUIRED_FORBIDDEN_SCOPE = {
    "device_write",
    "serial_transport",
    "runtime_loaded_config",
    "firmware_behavior_change",
    "profile_schema_change",
    "macro_or_turbo_logic",
    "hardware_validation_claim",
}
REQUIRED_GENERATED_CONFIG_DOC_PHRASES = (
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
)
REQUIRED_SENSCOPE_EXPORT_DOC_PHRASES = (
    "does not implement device writing",
    "does not implement serial transport",
    "does not implement runtime-loaded config",
    "does not implement firmware behavior changes",
    "does not implement profile schema changes",
)


class ContractCheckError(ValueError):
    """Raised when a docs/tools-only contract cannot be trusted."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ContractCheckError(message)


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


def require_superset(actual: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def require_expected_values(payload: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{label}.{key} must be {value!r}")


def validate_point(point: Any, label: str) -> None:
    if (
        not isinstance(point, list)
        or len(point) != 2
        or any(isinstance(coord, bool) or not isinstance(coord, int) for coord in point)
    ):
        fail(f"{label} must be [int, int]")
    if not all(0 <= coord <= 255 for coord in point):
        fail(f"{label} coordinates must be in [0,255]")


def validate_table_shape(name: str, table: Any) -> None:
    if not isinstance(table, list):
        fail(f"tables.{name} must be a list")
    if len(table) != 9:
        fail(f"tables.{name} must contain exactly 9 points")
    for index, point in enumerate(table):
        validate_point(point, f"tables.{name}[{index}]")


def validate_generated_config_contract(contract: dict[str, Any], prototype: dict[str, Any]) -> None:
    require_expected_values(contract, EXPECTED_GENERATED_CONFIG_CONTRACT, "generated_config_contract")

    required_top_level_fields = require_string_list(contract, "required_top_level_fields")
    require_superset(
        required_top_level_fields,
        {key for key in prototype},
        "generated_config_contract.required_top_level_fields",
    )

    required_tables = require_string_list(contract, "required_tables")
    tables = prototype.get("tables")
    if not isinstance(tables, dict):
        fail("prototype.tables must be an object")
    if set(required_tables) != set(tables):
        missing = sorted(set(tables) - set(required_tables))
        unexpected = sorted(set(required_tables) - set(tables))
        fail(f"required_tables mismatch missing_from_contract={missing} unexpected_in_contract={unexpected}")
    if len(required_tables) != 25:
        fail("required_tables must contain exactly 25 table names")

    for name in required_tables:
        validate_table_shape(name, tables.get(name))

    required_priority_keys = require_string_list(contract, "required_priority_keys")
    priority_model = prototype.get("priority_model")
    if not isinstance(priority_model, dict):
        fail("prototype.priority_model must be an object")
    require_superset(required_priority_keys, set(priority_model), "generated_config_contract.required_priority_keys")

    required_hard_overrides = contract.get("required_hard_overrides")
    if not isinstance(required_hard_overrides, dict):
        fail("required_hard_overrides must be an object")
    if required_hard_overrides != prototype.get("hard_overrides"):
        fail("required_hard_overrides must match prototype.hard_overrides exactly")

    forbidden = require_string_list(contract, "forbidden_interpretations")
    require_superset(
        forbidden,
        REQUIRED_FORBIDDEN_INTERPRETATIONS,
        "generated_config_contract.forbidden_interpretations",
    )


def validate_generated_config_prototype(contract: dict[str, Any], prototype: dict[str, Any]) -> None:
    for field in require_string_list(contract, "required_top_level_fields"):
        if field not in prototype:
            fail(f"prototype missing required top-level field: {field}")

    expected_values = {
        "schema_name": contract["target_schema_name"],
        "contract_version": contract["target_contract_version"],
        "mode_scope": contract["mode_scope"],
        "source_status": contract["target_source_status"],
        "hardware_status": contract["hardware_status"],
        "nunchuk_status": contract["nunchuk_status"],
        "direction_convention": contract["target_direction_convention"],
    }
    require_expected_values(prototype, expected_values, "prototype")

    tables = prototype.get("tables")
    if not isinstance(tables, dict):
        fail("prototype.tables must be an object")
    if set(tables) != set(contract["required_tables"]):
        fail("prototype table names must match contract.required_tables")

    if prototype.get("hard_overrides") != contract.get("required_hard_overrides"):
        fail("prototype hard_overrides must match contract.required_hard_overrides")


def validate_senscope_export_contract(export: dict[str, Any]) -> None:
    require_expected_values(export, EXPECTED_SENSCOPE_EXPORT_CONTRACT, "senscope_export_contract")
    expected_target = display(GENERATED_CONFIG_CONTRACT_PATH)
    if export.get("target_generated_config_contract") != expected_target:
        fail("senscope_export_contract.target_generated_config_contract points to the wrong fixture")

    payloads = require_string_list(export, "required_export_payloads")
    require_superset(payloads, REQUIRED_EXPORT_PAYLOADS, "senscope_export_contract.required_export_payloads")

    report_sections = require_string_list(export, "validation_report_required_sections")
    require_superset(
        report_sections,
        REQUIRED_VALIDATION_REPORT_SECTIONS,
        "senscope_export_contract.validation_report_required_sections",
    )

    forbidden_scope = require_string_list(export, "forbidden_scope")
    require_superset(forbidden_scope, REQUIRED_FORBIDDEN_SCOPE, "senscope_export_contract.forbidden_scope")


def validate_doc_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    lowered = path.read_text(encoding="utf-8").lower()
    for phrase in phrases:
        if phrase not in lowered:
            fail(f"{display(path)} missing required caveat phrase: {phrase}")


def validate_contracts() -> tuple[int, int]:
    generated_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
    senscope_export_contract = load_json_object(SENSCOPE_EXPORT_CONTRACT_PATH)
    prototype = load_json_object(GENERATED_CONFIG_PROTOTYPE_PATH)

    validate_generated_config_contract(generated_contract, prototype)
    validate_generated_config_prototype(generated_contract, prototype)
    validate_senscope_export_contract(senscope_export_contract)
    validate_doc_phrases(GENERATED_CONFIG_CONTRACT_DOC_PATH, REQUIRED_GENERATED_CONFIG_DOC_PHRASES)
    validate_doc_phrases(SENSCOPE_EXPORT_CONTRACT_DOC_PATH, REQUIRED_SENSCOPE_EXPORT_DOC_PHRASES)

    return len(generated_contract["required_tables"]), len(senscope_export_contract["required_export_payloads"])


def main() -> int:
    print("glyph_identity_runtime_config_contracts")
    try:
        table_count, payload_count = validate_contracts()
    except (ContractCheckError, OSError, KeyError) as exc:
        print("status=FAIL")
        print("generated_config_required_tables=0")
        print("export_required_payloads=0")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"generated_config_required_tables={table_count}")
    print(f"export_required_payloads={payload_count}")
    print("hardware_status=not_new_hardware_result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
