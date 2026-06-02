#!/usr/bin/env python3
"""Validate generated constants refactor execution packet artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = REPO_ROOT / "docs/calibration"
FIXTURE_DIR = DOC_DIR / "fixtures"

EXECUTION_PACKET_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_generated_constants_refactor_execution_packet_2026-05-28.json"
)
HARDWARE_MATRIX_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.json"
)
IMPLEMENTATION_PLAN_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.json"
)
GO_NOGO_FIXTURE_PATH = FIXTURE_DIR / "glyph_preimplementation_go_nogo_index_2026-05-28.json"

EXECUTION_PACKET_DOC_PATH = (
    DOC_DIR / "glyph_generated_constants_refactor_execution_packet_2026-05-28.md"
)
AGENT_PROMPT_DOC_PATH = (
    DOC_DIR / "glyph_generated_constants_refactor_agent_prompt_2026-05-28.md"
)
HARDWARE_MATRIX_DOC_PATH = (
    DOC_DIR / "glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.md"
)

EXPECTED_EXECUTION_PACKET = {
    "schema_name": "glyph_generated_constants_refactor_execution_packet",
    "packet_version": 1,
    "status": "blocked_until_explicit_user_approval",
    "hardware_status": "not_new_hardware_result",
    "implementation_class": "generated_constants_firmware_refactor",
}
REQUIRED_APPROVAL = {
    "explicit_user_approval_for_firmware_source_touch",
    "approval_limited_to_generated_constants_refactor",
}
REQUIRED_ALLOWED_TOUCHES = {
    "src/modes/Ultimate.cpp",
    "relevant_tools_checkers_docs",
}
REQUIRED_FORBIDDEN_TOUCHES = {
    ".pio",
    ".uf2",
    ".bin",
    ".elf",
    ".map",
    "profile_artifacts_without_explicit_approval",
    "serial_writer_behavior",
    "profile_config_protobuf_schema_files",
    "hal_device_transport_paths",
}
REQUIRED_INVARIANTS = {
    "all_25_source_parsed_tables_unchanged",
    "generated_cpp_review_artifact_matches_generated_output",
    "generated_config_prototype_matches_source_tables",
    "behavior_evaluator_passes_current_cases",
    "identity_runtime_source_checker_passes",
    "no_forbidden_artifacts_checker_passes",
    "no_profile_artifacts_changed",
    "no_serial_device_write_behavior_changed",
    "no_runtime_loaded_config_added",
    "no_hardware_validation_claim_without_result_doc",
}
REQUIRED_HARDWARE_GATE = {
    "hardware_test_matrix_must_be_executed_before_merge",
    "hardware_result_doc_required_before_merge",
    "rollback_required_on_failure",
}

EXPECTED_HARDWARE_MATRIX = {
    "schema_name": "glyph_generated_constants_refactor_hardware_test_matrix",
    "matrix_version": 1,
    "status": "template_not_executed",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
}
REQUIRED_TEST_CATEGORIES = {
    "boot",
    "identity_profile",
    "default_table",
    "mode_default",
    "x_modifiers",
    "y_modifiers",
    "tilt_modifiers",
    "z_airdodge_low_magnitude",
    "hard_up_b",
    "null_override",
    "ls_to_dpad",
    "pure_layer",
    "lf4_submode",
    "cstick_suppression",
    "direction_plus_a",
    "right_stick",
    "system_buttons",
    "profile_regression",
    "nunchuk_scope",
}

EXECUTION_PACKET_DOC_PHRASES = (
    "does not edit firmware source",
    "does not implement generated constants",
    "does not change table values",
    "does not change firmware runtime behavior",
    "does not validate hardware",
)
AGENT_PROMPT_DOC_PHRASES = (
    "do not run without explicit user approval",
    "hardware testing before merge",
    "do not implement runtime-loaded config",
    "do not implement serial/device write behavior",
)
HARDWARE_MATRIX_DOC_PHRASES = (
    "not executed",
    "not a hardware result",
    "does not validate hardware",
    "result must be recorded separately",
)


class GeneratedConstantsExecutionPacketError(ValueError):
    """Raised when generated constants execution packet artifacts drift."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise GeneratedConstantsExecutionPacketError(message)


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


def validate_execution_packet(packet: dict[str, Any]) -> str:
    require_expected_values(packet, EXPECTED_EXECUTION_PACKET, "execution_packet")
    require_superset(
        require_string_list(packet, "required_approval"),
        REQUIRED_APPROVAL,
        "execution_packet.required_approval",
    )
    require_superset(
        require_string_list(packet, "allowed_file_touch_set_if_approved"),
        REQUIRED_ALLOWED_TOUCHES,
        "execution_packet.allowed_file_touch_set_if_approved",
    )
    require_superset(
        require_string_list(packet, "forbidden_file_touch_set"),
        REQUIRED_FORBIDDEN_TOUCHES,
        "execution_packet.forbidden_file_touch_set",
    )
    require_superset(
        require_string_list(packet, "required_invariants"),
        REQUIRED_INVARIANTS,
        "execution_packet.required_invariants",
    )
    require_superset(
        require_string_list(packet, "required_hardware_gate"),
        REQUIRED_HARDWARE_GATE,
        "execution_packet.required_hardware_gate",
    )
    return str(packet["status"])


def validate_hardware_matrix(matrix: dict[str, Any]) -> int:
    require_expected_values(matrix, EXPECTED_HARDWARE_MATRIX, "hardware_matrix")
    if matrix.get("result_recording_required") is not True:
        fail("hardware_matrix.result_recording_required must be true")
    if matrix.get("rollback_required_on_failure") is not True:
        fail("hardware_matrix.rollback_required_on_failure must be true")

    rows = matrix.get("test_rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        fail("hardware_matrix.test_rows must be a list of objects")
    categories = {row.get("category") for row in rows}
    if not all(isinstance(category, str) for category in categories):
        fail("hardware_matrix.test_rows categories must be strings")
    missing = sorted(REQUIRED_TEST_CATEGORIES - categories)
    if missing:
        fail("hardware_matrix.test_rows missing required category value(s): " + ", ".join(missing))
    return len(rows)


def validate_cross_checks(
    implementation_plan: dict[str, Any],
    go_nogo_index: dict[str, Any],
) -> None:
    if implementation_plan.get("status") != "plan_only_blocked_until_explicit_approval":
        fail("generated constants implementation plan must remain plan_only_blocked_until_explicit_approval")

    gates = require_object(go_nogo_index, "gates")
    if gates.get("generated_constants_firmware_refactor") != "BLOCKED_EXPLICIT_APPROVAL":
        fail("go/no-go generated constants firmware refactor gate must remain BLOCKED_EXPLICIT_APPROVAL")
    if gates.get("new_runtime_behavior_change") != "BLOCKED_EXPLICIT_APPROVAL_AND_HARDWARE_TEST":
        fail("go/no-go new runtime behavior gate must remain blocked by approval and hardware test")


def validate_doc_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    lowered = path.read_text(encoding="utf-8").lower()
    for phrase in phrases:
        if phrase not in lowered:
            fail(f"{display(path)} missing required caveat phrase: {phrase}")


def validate_contracts() -> tuple[str, str, int]:
    execution_packet = load_json_object(EXECUTION_PACKET_FIXTURE_PATH)
    hardware_matrix = load_json_object(HARDWARE_MATRIX_FIXTURE_PATH)
    implementation_plan = load_json_object(IMPLEMENTATION_PLAN_FIXTURE_PATH)
    go_nogo_index = load_json_object(GO_NOGO_FIXTURE_PATH)

    execution_status = validate_execution_packet(execution_packet)
    hardware_status = str(hardware_matrix.get("hardware_status"))
    matrix_rows = validate_hardware_matrix(hardware_matrix)
    validate_cross_checks(implementation_plan, go_nogo_index)

    validate_doc_phrases(EXECUTION_PACKET_DOC_PATH, EXECUTION_PACKET_DOC_PHRASES)
    validate_doc_phrases(AGENT_PROMPT_DOC_PATH, AGENT_PROMPT_DOC_PHRASES)
    validate_doc_phrases(HARDWARE_MATRIX_DOC_PATH, HARDWARE_MATRIX_DOC_PHRASES)

    return execution_status, hardware_status, matrix_rows


def main() -> int:
    print("glyph_generated_constants_refactor_execution_packet")
    try:
        execution_status, hardware_status, matrix_rows = validate_contracts()
    except (GeneratedConstantsExecutionPacketError, OSError, KeyError) as exc:
        print("status=FAIL")
        print("hardware_matrix_rows=UNKNOWN")
        print("execution_status=UNKNOWN")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"hardware_matrix_rows={matrix_rows}")
    print(f"execution_status={execution_status}")
    print(f"hardware_status={hardware_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
