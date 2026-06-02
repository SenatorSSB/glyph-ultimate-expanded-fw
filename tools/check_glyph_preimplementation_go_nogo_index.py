#!/usr/bin/env python3
"""Validate docs/tools-only preimplementation go/no-go gate artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "docs/calibration/fixtures"

GO_NOGO_FIXTURE_PATH = FIXTURE_DIR / "glyph_preimplementation_go_nogo_index_2026-05-28.json"
GENERATED_CONSTANTS_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_generated_constants_refactor_readiness_packet_2026-05-28.json"
)
RUNTIME_IMPLEMENTATION_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.json"
)
RUNTIME_DESIGN_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_runtime_loaded_config_design_v0_2026-05-28.json"
)
RUNTIME_VALIDATION_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json"
)

GO_NOGO_DOC_PATH = REPO_ROOT / "docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md"
GENERATED_CONSTANTS_DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_generated_constants_refactor_readiness_packet_2026-05-28.md"
)
RUNTIME_IMPLEMENTATION_DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.md"
)

EXPECTED_GO_NOGO = {
    "schema_name": "glyph_preimplementation_go_nogo_index",
    "index_version": 1,
    "status": "docs_tools_gate_index",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
}
REQUIRED_GATES = {
    "generated_constants_firmware_refactor": "BLOCKED_EXPLICIT_APPROVAL",
    "runtime_loaded_config_interpreter_storage": "BLOCKED_EXPLICIT_APPROVAL",
    "device_write_serial_transport": "BLOCKED_SOURCE_AUTHORITY_AND_APPROVAL",
    "official_configurator_integration": "BLOCKED_SOURCE_AUTHORITY",
    "new_runtime_behavior_change": "BLOCKED_EXPLICIT_APPROVAL_AND_HARDWARE_TEST",
    "senscope_browser_app_export_implementation": "OUT_OF_SCOPE_FOR_REPO",
    "senscope_export_contract_drafting_checkers": "GO_DOCS_ONLY",
}
REQUIRED_FIRMWARE_PRECONDITIONS = {
    "explicit_user_approval",
    "source_backed_implementation_plan",
    "current_checkers_passing",
    "no_forbidden_artifacts",
    "hardware_test_plan",
    "rollback_plan",
    "no_unsupported_behavior_claims",
}
REQUIRED_RUNTIME_PRECONDITIONS = {
    "explicit_user_approval",
    "storage_representation_design",
    "validator_design",
    "fallback_policy",
    "version_migration_policy",
    "latency_performance_measurement_plan",
    "hardware_validation_plan",
    "source_authority_for_transport_storage_assumptions",
}
EXPECTED_GENERATED_CONSTANTS = {
    "schema_name": "glyph_generated_constants_refactor_readiness_packet",
    "packet_version": 1,
    "status": "blocked_until_explicit_approval",
    "hardware_status": "not_new_hardware_result",
}
REQUIRED_GENERATED_FORBIDDEN_CHANGES = {
    "behavior_change",
    "table_value_change",
    "profile_artifact_change",
    "runtime_loaded_config",
    "serial_device_write_behavior",
    "hardware_validation_claim",
}
REQUIRED_GENERATED_INVARIANTS = {
    "all_25_tables_match_source",
    "behavior_evaluator_passes_118_cases",
    "generated_config_checker_passes",
    "generated_cpp_diff_checker_passes",
    "no_forbidden_artifacts",
}
EXPECTED_RUNTIME_IMPLEMENTATION = {
    "schema_name": "glyph_runtime_loaded_config_implementation_readiness_packet",
    "packet_version": 1,
    "status": "blocked_until_explicit_approval_and_design_resolution",
    "hardware_status": "not_new_hardware_result",
}
REQUIRED_RUNTIME_DESIGN_DECISIONS = {
    "storage_location",
    "representation",
    "boot_time_validation",
    "fallback_behavior_if_config_invalid",
    "version_migration",
    "maximum_config_size",
    "profile_bound_vs_global_config",
    "transport_policy",
    "hardware_validation_plan",
}
REQUIRED_RUNTIME_FORBIDDEN_SHORTCUTS = {
    "skip_validator",
    "skip_fallback_policy",
    "accept_unknown_role_classes",
    "allow_scripts_macros_turbo",
    "mutate_phase_order_from_config",
    "claim_hardware_validation_without_test",
}
GO_NOGO_DOC_PHRASES = (
    "does not change firmware runtime behavior",
    "does not implement generated constants",
    "does not implement runtime-loaded config",
    "does not implement serial/device write behavior",
    "does not validate hardware",
)
GENERATED_CONSTANTS_DOC_PHRASES = (
    "does not edit firmware source",
    "does not implement generated constants",
    "does not change table values",
    "does not validate hardware",
)
RUNTIME_IMPLEMENTATION_DOC_PHRASES = (
    "does not implement runtime-loaded config",
    "does not implement storage",
    "does not implement serial/device write behavior",
    "does not change firmware behavior",
    "does not validate hardware",
)


class PreimplementationGoNoGoError(ValueError):
    """Raised when preimplementation gate artifacts drift from guardrails."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise PreimplementationGoNoGoError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be an object: {display(path)}")
    return payload


def require_object(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        fail(f"{key} must be an object")
    return value


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_expected_values(payload: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{label}.{key} must be {value!r}")


def require_superset(actual: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def require_explicit_user_approval(payload: dict[str, Any], label: str) -> None:
    required_approval = require_string_list(payload, "required_approval")
    if "explicit_user_approval" not in required_approval:
        fail(f"{label}.required_approval must include explicit_user_approval")


def validate_go_nogo_index(index: dict[str, Any]) -> int:
    require_expected_values(index, EXPECTED_GO_NOGO, "go_nogo_index")

    gates = require_object(index, "gates")
    for gate, expected_status in REQUIRED_GATES.items():
        if gates.get(gate) != expected_status:
            fail(f"go_nogo_index.gates.{gate} must be {expected_status!r}")

    firmware_preconditions = require_string_list(
        index, "required_preconditions_before_firmware_source_changes"
    )
    require_superset(
        firmware_preconditions,
        REQUIRED_FIRMWARE_PRECONDITIONS,
        "go_nogo_index.required_preconditions_before_firmware_source_changes",
    )

    runtime_preconditions = require_string_list(
        index, "required_preconditions_before_runtime_loaded_config_implementation"
    )
    require_superset(
        runtime_preconditions,
        REQUIRED_RUNTIME_PRECONDITIONS,
        "go_nogo_index.required_preconditions_before_runtime_loaded_config_implementation",
    )

    return len(gates)


def validate_generated_constants_packet(packet: dict[str, Any]) -> str:
    require_expected_values(packet, EXPECTED_GENERATED_CONSTANTS, "generated_constants_packet")
    require_explicit_user_approval(packet, "generated_constants_packet")

    forbidden_changes = require_string_list(packet, "forbidden_changes")
    require_superset(
        forbidden_changes,
        REQUIRED_GENERATED_FORBIDDEN_CHANGES,
        "generated_constants_packet.forbidden_changes",
    )

    required_invariants = require_string_list(packet, "required_invariants")
    require_superset(
        required_invariants,
        REQUIRED_GENERATED_INVARIANTS,
        "generated_constants_packet.required_invariants",
    )

    return str(packet["status"])


def validate_runtime_implementation_packet(packet: dict[str, Any]) -> str:
    require_expected_values(packet, EXPECTED_RUNTIME_IMPLEMENTATION, "runtime_implementation_packet")
    require_explicit_user_approval(packet, "runtime_implementation_packet")

    design_decisions = require_string_list(packet, "required_design_decisions")
    require_superset(
        design_decisions,
        REQUIRED_RUNTIME_DESIGN_DECISIONS,
        "runtime_implementation_packet.required_design_decisions",
    )

    forbidden_shortcuts = require_string_list(packet, "forbidden_implementation_shortcuts")
    require_superset(
        forbidden_shortcuts,
        REQUIRED_RUNTIME_FORBIDDEN_SHORTCUTS,
        "runtime_implementation_packet.forbidden_implementation_shortcuts",
    )

    return str(packet["status"])


def validate_runtime_design_contracts(
    runtime_design: dict[str, Any],
    runtime_validation: dict[str, Any],
    index: dict[str, Any],
) -> None:
    if runtime_design.get("status") != "design_only_not_implemented":
        fail("runtime-loaded design fixture status must remain design_only_not_implemented")
    if runtime_validation.get("status") != "validation_contract_design_only_not_implemented":
        fail(
            "runtime-loaded validation contract status must remain "
            "validation_contract_design_only_not_implemented"
        )

    gates = require_object(index, "gates")
    if gates.get("runtime_loaded_config_interpreter_storage") != "BLOCKED_EXPLICIT_APPROVAL":
        fail("go/no-go index must block runtime-loaded implementation")


def validate_doc_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    lowered = path.read_text(encoding="utf-8").lower()
    for phrase in phrases:
        if phrase not in lowered:
            fail(f"{display(path)} missing required caveat phrase: {phrase}")


def validate_contracts() -> tuple[int, str, str]:
    index = load_json_object(GO_NOGO_FIXTURE_PATH)
    generated_constants = load_json_object(GENERATED_CONSTANTS_FIXTURE_PATH)
    runtime_implementation = load_json_object(RUNTIME_IMPLEMENTATION_FIXTURE_PATH)
    runtime_design = load_json_object(RUNTIME_DESIGN_FIXTURE_PATH)
    runtime_validation = load_json_object(RUNTIME_VALIDATION_FIXTURE_PATH)

    gates_count = validate_go_nogo_index(index)
    generated_constants_status = validate_generated_constants_packet(generated_constants)
    runtime_loaded_config_status = validate_runtime_implementation_packet(runtime_implementation)
    validate_runtime_design_contracts(runtime_design, runtime_validation, index)
    validate_doc_phrases(GO_NOGO_DOC_PATH, GO_NOGO_DOC_PHRASES)
    validate_doc_phrases(GENERATED_CONSTANTS_DOC_PATH, GENERATED_CONSTANTS_DOC_PHRASES)
    validate_doc_phrases(RUNTIME_IMPLEMENTATION_DOC_PATH, RUNTIME_IMPLEMENTATION_DOC_PHRASES)

    return gates_count, generated_constants_status, runtime_loaded_config_status


def main() -> int:
    print("glyph_preimplementation_go_nogo_index")
    try:
        gates_count, generated_constants_status, runtime_loaded_config_status = validate_contracts()
    except (PreimplementationGoNoGoError, OSError, KeyError) as exc:
        print("status=FAIL")
        print("gates=0")
        print("generated_constants_status=UNKNOWN")
        print("runtime_loaded_config_status=UNKNOWN")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"gates={gates_count}")
    print(f"generated_constants_status={generated_constants_status}")
    print(f"runtime_loaded_config_status={runtime_loaded_config_status}")
    print("hardware_status=not_new_hardware_result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
