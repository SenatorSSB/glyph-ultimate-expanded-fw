#!/usr/bin/env python3
"""Check the offline Glyph runtime config candidate validator fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from glyph_runtime_config_candidate_validator import (
    ACCEPTED_DATA_CLASSES,
    APPROVED_PRIORITY_CLASSES,
    CANDIDATE_VERSION,
    GENERATED_CONFIG_CONTRACT,
    HARDWARE_STATUS,
    MODE_SCOPE,
    NUNCHUK_STATUS,
    REQUIRED_HARD_OVERRIDES,
    REQUIRED_NON_GOALS,
    REQUIRED_ROLE_BINDING_SECTIONS,
    REQUIRED_TABLES,
    REQUIRED_TOP_LEVEL_FIELDS,
    RUNTIME_VALIDATION_CONTRACT,
    SCHEMA_NAME,
    STATUS,
    load_json_object,
    validate_runtime_config_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json"
)
CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_validator_contract_v0_2026-06-03.json"
)
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_runtime_config_candidate_validator_v0_2026-06-03.md"
PROTOTYPE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
GENERATED_CONFIG_CONTRACT_PATH = REPO_ROOT / GENERATED_CONFIG_CONTRACT
RUNTIME_VALIDATION_CONTRACT_PATH = REPO_ROOT / RUNTIME_VALIDATION_CONTRACT

REQUIRED_DOC_PHRASES = (
    "offline validator only",
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)
REQUIRED_FORBIDDEN_CONTENT = {
    "firmware_source_patches",
    "serial_transport_payloads",
    "device_write_instructions",
    "macros",
    "turbo",
    "timing_automation",
    "one_shot_toggle_history_dependent_logic",
    "runtime_loaded_config_implementation_claims",
    "phase_order_mutation",
    "hardware_validation_claims_without_hardware_result_source",
    "nunchuk_hardware_validation_claims_without_hardware_result_source",
}


class CandidateValidatorCheckError(ValueError):
    """Raised when the candidate validator package drifts."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise CandidateValidatorCheckError(message)


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_superset(actual: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def validate_contract(contract: dict[str, Any]) -> None:
    expected = {
        "schema_name": "glyph_runtime_config_candidate_validator_contract",
        "contract_version": 1,
        "target_schema_name": SCHEMA_NAME,
        "target_candidate_version": CANDIDATE_VERSION,
        "status": "offline_validator_contract_not_runtime_loaded",
        "mode_scope": MODE_SCOPE,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
        "validator_tool": "tools/glyph_runtime_config_candidate_validator.py",
        "checker_tool": "tools/check_glyph_runtime_config_candidate_validator.py",
        "sample_candidate": "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json",
        "generated_config_contract": GENERATED_CONFIG_CONTRACT,
        "runtime_validation_contract": RUNTIME_VALIDATION_CONTRACT,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            fail(f"contract {key} must be {value!r}")

    if contract.get("required_top_level_fields") != list(REQUIRED_TOP_LEVEL_FIELDS):
        fail("contract required_top_level_fields drifted from validator")
    if contract.get("required_tables") != list(REQUIRED_TABLES):
        fail("contract required_tables drifted from validator")
    if contract.get("required_role_binding_sections") != list(REQUIRED_ROLE_BINDING_SECTIONS):
        fail("contract required_role_binding_sections drifted from validator")
    if contract.get("approved_priority_classes") != {
        key: list(value) for key, value in APPROVED_PRIORITY_CLASSES.items()
    }:
        fail("contract approved_priority_classes drifted from validator")
    if contract.get("accepted_data_classes") != list(ACCEPTED_DATA_CLASSES):
        fail("contract accepted_data_classes drifted from validator")
    if contract.get("required_hard_overrides") != REQUIRED_HARD_OVERRIDES:
        fail("contract required_hard_overrides drifted from validator")
    require_superset(
        require_string_list(contract, "required_non_goals"),
        REQUIRED_NON_GOALS,
        "contract.required_non_goals",
    )
    require_superset(
        require_string_list(contract, "forbidden_payload_content"),
        REQUIRED_FORBIDDEN_CONTENT,
        "contract.forbidden_payload_content",
    )


def validate_runtime_contract(runtime_contract: dict[str, Any]) -> None:
    accepted = require_string_list(runtime_contract, "accepted_data_classes")
    if accepted != list(ACCEPTED_DATA_CLASSES):
        fail("runtime validation contract accepted_data_classes drifted from candidate validator")


def validate_generated_contract(generated_contract: dict[str, Any]) -> None:
    if generated_contract.get("required_tables") != list(REQUIRED_TABLES):
        fail("generated-config contract required_tables drifted from candidate validator")
    if generated_contract.get("required_hard_overrides") != REQUIRED_HARD_OVERRIDES:
        fail("generated-config contract hard overrides drifted from candidate validator")


def validate_sample_derivation(sample: dict[str, Any], prototype: dict[str, Any]) -> None:
    if sample.get("tables") != prototype.get("tables"):
        fail("sample tables must match committed generated-config prototype tables")
    if sample.get("role_bindings") != prototype.get("role_bindings"):
        fail("sample role_bindings must match committed generated-config prototype role_bindings")
    if sample.get("hard_overrides") != prototype.get("hard_overrides"):
        fail("sample hard_overrides must match committed generated-config prototype hard_overrides")
    priority_model = prototype.get("priority_model")
    if not isinstance(priority_model, dict):
        fail("prototype priority_model must be an object")
    expected_priority = {
        "digital": priority_model.get("digital_effective_direction"),
        "analog": priority_model.get("analog"),
    }
    if sample.get("priority_references") != expected_priority:
        fail("sample priority_references must derive from committed generated-config prototype priority_model")
    if sample.get("suppression_rules") != prototype.get("suppression_rules"):
        fail("sample suppression_rules must derive from committed generated-config prototype suppression_rules")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_runtime_config_candidate_validator")
    try:
        sample = load_json_object(SAMPLE_PATH)
        contract = load_json_object(CONTRACT_PATH)
        prototype = load_json_object(PROTOTYPE_PATH)
        generated_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
        runtime_contract = load_json_object(RUNTIME_VALIDATION_CONTRACT_PATH)

        validate_contract(contract)
        validate_generated_contract(generated_contract)
        validate_runtime_contract(runtime_contract)
        validate_sample_derivation(sample, prototype)
        validate_doc()
        issues = validate_runtime_config_candidate(sample)
    except (OSError, ValueError, CandidateValidatorCheckError) as exc:
        print("status=FAIL")
        print("validated_schema=unknown")
        print("table_count=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    validated_schema = str(sample.get("schema_name", "unknown"))
    tables = sample.get("tables")
    table_count = len(tables) if isinstance(tables, dict) else 0
    print("status=PASS" if not issues else "status=FAIL")
    print(f"validated_schema={validated_schema}")
    print(f"table_count={table_count}")
    print(f"hardware_status={sample.get('hardware_status', HARDWARE_STATUS)}")
    if issues:
        for issue in issues:
            print(f"issue={issue.code} path={issue.path} message={issue.message}")
        return 1

    print(f"sample_candidate={display(SAMPLE_PATH)}")
    print(f"validator_contract={display(CONTRACT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
