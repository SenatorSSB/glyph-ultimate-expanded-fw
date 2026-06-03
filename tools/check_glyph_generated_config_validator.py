#!/usr/bin/env python3
"""Check the offline Glyph generated-config validator against committed fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from glyph_generated_config_validator import (
    CONTRACT_VERSION,
    DIRECTION_CONVENTION,
    HARDWARE_STATUS,
    MODE_SCOPE,
    NUNCHUK_STATUS,
    REQUIRED_HARD_OVERRIDES,
    REQUIRED_PRIORITY_KEYS,
    REQUIRED_ROLE_BINDING_SECTIONS,
    REQUIRED_TABLES,
    REQUIRED_TOP_LEVEL_FIELDS,
    SCHEMA_NAME,
    SOURCE_STATUS,
    load_json_object,
    validate_generated_config,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
GENERATED_CONFIG_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)
RUNTIME_VALIDATION_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json"
)
OFFLINE_VALIDATOR_CONTRACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_generated_config_validator_contract_v0_2026-06-03.json"
)
OFFLINE_VALIDATOR_DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_offline_generated_config_validator_v0_2026-06-03.md"
)

REQUIRED_RUNTIME_VALIDATION_REJECTION_RULES = {
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
REQUIRED_RUNTIME_FORBIDDEN_PAYLOAD = {
    "firmware_source_patch",
    "serial_transport_payload",
    "device_write_instruction",
    "macro_or_turbo_logic",
    "timing_or_history_logic",
}
REQUIRED_DOC_PHRASES = (
    "offline validator only",
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)


class ValidatorCheckError(ValueError):
    """Raised when the offline validator checker finds drift."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ValidatorCheckError(message)


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_superset(actual: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def validate_generated_config_contract(contract: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_identity_runtime_generated_config_contract",
        "contract_version": CONTRACT_VERSION,
        "target_schema_name": SCHEMA_NAME,
        "target_contract_version": CONTRACT_VERSION,
        "mode_scope": MODE_SCOPE,
        "status": "docs_tools_contract_not_runtime_loaded",
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
        "target_source_status": SOURCE_STATUS,
        "target_direction_convention": DIRECTION_CONVENTION,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            fail(f"generated-config contract {key} must be {value!r}")
    if contract.get("required_top_level_fields") != list(REQUIRED_TOP_LEVEL_FIELDS):
        fail("generated-config contract required_top_level_fields drifted from validator")
    if contract.get("required_tables") != list(REQUIRED_TABLES):
        fail("generated-config contract required_tables drifted from validator")
    if contract.get("required_priority_keys") != list(REQUIRED_PRIORITY_KEYS):
        fail("generated-config contract required_priority_keys drifted from validator")
    if contract.get("required_role_binding_sections") != list(REQUIRED_ROLE_BINDING_SECTIONS):
        fail("generated-config contract required_role_binding_sections drifted from validator")
    if contract.get("required_hard_overrides") != REQUIRED_HARD_OVERRIDES:
        fail("generated-config contract required_hard_overrides drifted from validator")


def validate_runtime_validation_contract(contract: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_runtime_loaded_config_validation_contract",
        "contract_version": CONTRACT_VERSION,
        "status": "validation_contract_design_only_not_implemented",
        "mode_scope": MODE_SCOPE,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            fail(f"runtime-loaded validation contract {key} must be {value!r}")
    require_superset(
        require_string_list(contract, "required_rejection_rules"),
        REQUIRED_RUNTIME_VALIDATION_REJECTION_RULES,
        "runtime-loaded validation contract required_rejection_rules",
    )
    require_superset(
        require_string_list(contract, "forbidden_payload_content"),
        REQUIRED_RUNTIME_FORBIDDEN_PAYLOAD,
        "runtime-loaded validation contract forbidden_payload_content",
    )


def validate_offline_validator_contract(contract: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_offline_generated_config_validator_contract",
        "contract_version": CONTRACT_VERSION,
        "status": "tooling_validator_only_not_runtime_loaded",
        "mode_scope": MODE_SCOPE,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
        "validator_tool": "tools/glyph_generated_config_validator.py",
        "checker_tool": "tools/check_glyph_generated_config_validator.py",
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            fail(f"offline validator contract {key} must be {value!r}")
    if contract.get("target_schema_name") != SCHEMA_NAME:
        fail("offline validator contract target_schema_name drifted")
    if contract.get("target_contract_version") != CONTRACT_VERSION:
        fail("offline validator contract target_contract_version drifted")
    if contract.get("required_tables") != list(REQUIRED_TABLES):
        fail("offline validator contract required_tables drifted from validator")
    if contract.get("required_priority_keys") != list(REQUIRED_PRIORITY_KEYS):
        fail("offline validator contract required_priority_keys drifted from validator")
    if contract.get("required_role_binding_sections") != list(REQUIRED_ROLE_BINDING_SECTIONS):
        fail("offline validator contract required_role_binding_sections drifted from validator")
    if contract.get("required_hard_overrides") != REQUIRED_HARD_OVERRIDES:
        fail("offline validator contract required_hard_overrides drifted from validator")


def validate_doc() -> None:
    lowered = OFFLINE_VALIDATOR_DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(OFFLINE_VALIDATOR_DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_generated_config_validator")
    try:
        prototype = load_json_object(PROTOTYPE_FIXTURE_PATH)
        generated_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
        runtime_validation_contract = load_json_object(RUNTIME_VALIDATION_CONTRACT_PATH)
        offline_validator_contract = load_json_object(OFFLINE_VALIDATOR_CONTRACT_PATH)
        validate_generated_config_contract(generated_contract)
        validate_runtime_validation_contract(runtime_validation_contract)
        validate_offline_validator_contract(offline_validator_contract)
        validate_doc()
        issues = validate_generated_config(prototype)
    except (OSError, ValueError, ValidatorCheckError) as exc:
        print("status=FAIL")
        print("validated_schema=unknown")
        print("table_count=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    validated_schema = str(prototype.get("schema_name", "unknown"))
    tables = prototype.get("tables")
    table_count = len(tables) if isinstance(tables, dict) else 0
    print(f"validated_schema={validated_schema}")
    print(f"table_count={table_count}")
    print(f"hardware_status={prototype.get('hardware_status', HARDWARE_STATUS)}")
    if issues:
        print("status=FAIL")
        for issue in issues:
            print(f"issue={issue.code} path={issue.path} message={issue.message}")
        return 1

    print("status=PASS")
    print(f"prototype_fixture={display(PROTOTYPE_FIXTURE_PATH)}")
    print(f"generated_config_contract={display(GENERATED_CONFIG_CONTRACT_PATH)}")
    print(f"runtime_validation_contract={display(RUNTIME_VALIDATION_CONTRACT_PATH)}")
    print(f"offline_validator_contract={display(OFFLINE_VALIDATOR_CONTRACT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
