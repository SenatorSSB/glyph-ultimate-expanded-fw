#!/usr/bin/env python3
"""Validate docs/tools-only implementation planning packet artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "docs/calibration/fixtures"
DOC_DIR = REPO_ROOT / "docs/calibration"

GENERATED_CONSTANTS_PLAN_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.json"
)
RUNTIME_PLAN_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.json"
)
HARDWARE_PLAN_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.json"
)
INTERPRETER_SOURCE_BASELINE_PLAN_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_runtime_config_interpreter_source_baseline_hardware_plan_2026-06-07.json"
)
GO_NOGO_FIXTURE_PATH = FIXTURE_DIR / "glyph_preimplementation_go_nogo_index_2026-05-28.json"
RUNTIME_READINESS_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.json"
)
GENERATED_CONSTANTS_READINESS_FIXTURE_PATH = (
    FIXTURE_DIR / "glyph_generated_constants_refactor_readiness_packet_2026-05-28.json"
)

GENERATED_CONSTANTS_PLAN_DOC_PATH = (
    DOC_DIR / "glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.md"
)
RUNTIME_PLAN_DOC_PATH = DOC_DIR / "glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md"
HARDWARE_PLAN_DOC_PATH = (
    DOC_DIR / "glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md"
)
INTERPRETER_SOURCE_BASELINE_PLAN_DOC_PATH = (
    DOC_DIR / "glyph_runtime_config_interpreter_source_baseline_hardware_plan_2026-06-07.md"
)

EXPECTED_GENERATED_CONSTANTS_PLAN = {
    "schema_name": "glyph_generated_constants_refactor_implementation_plan",
    "plan_version": 1,
    "status": "plan_only_blocked_until_explicit_approval",
    "hardware_status": "not_new_hardware_result",
}
REQUIRED_GENERATED_CONSTANTS_INVARIANTS = {
    "all_25_tables_match_source",
    "behavior_evaluator_passes_current_cases",
    "generated_config_checker_passes",
    "generated_cpp_diff_checker_passes",
    "runtime_source_checker_passes",
    "no_forbidden_artifacts_checker_passes",
}
REQUIRED_GENERATED_CONSTANTS_FORBIDDEN_CHANGES = {
    "behavior_change",
    "table_value_change",
    "profile_artifact_change",
    "runtime_loaded_config",
    "serial_device_write_behavior",
    "hardware_validation_claim",
}

EXPECTED_RUNTIME_PLAN = {
    "schema_name": "glyph_runtime_loaded_config_implementation_plan",
    "plan_version": 1,
    "status": "plan_only_blocked_until_explicit_approval_and_design_resolution",
    "hardware_status": "not_new_hardware_result",
    "nunchuk_status": "preserved_but_not_hardware_validated",
}
REQUIRED_RUNTIME_ARCHITECTURE_DECISIONS = {
    "storage_location",
    "representation_format",
    "boot_time_validation",
    "fallback_behavior",
    "version_migration",
    "maximum_config_size",
    "profile_bound_vs_global_config",
    "update_transport_path",
    "official_configurator_source_authority",
    "hardware_validation_matrix",
    "nunchuk_handling",
}
REQUIRED_RUNTIME_FORBIDDEN_SHORTCUTS = {
    "skip_validator",
    "skip_fallback_policy",
    "accept_unknown_role_classes",
    "allow_scripts_macros_turbo",
    "mutate_phase_order_from_config",
    "claim_hardware_validation_without_test",
}

EXPECTED_HARDWARE_PLAN = {
    "schema_name": "glyph_identity_runtime_hardware_validation_and_rollback_plan",
    "plan_version": 1,
    "status": "planning_only_not_executed",
    "hardware_status": "not_new_hardware_result",
}
REQUIRED_CHANGE_CLASSES = {
    "behavior_preserving_source_refactor",
    "generated_constants_refactor",
    "runtime_behavior_change",
    "runtime_loaded_config_interpreter",
    "storage_transport_device_write_behavior",
    "nunchuk_behavior",
}
REQUIRED_ROLLBACK_PLAN = {
    "rollback_branch_or_commit",
    "restore_previous_firmware_artifact_if_applicable",
    "restore_previous_profile_artifact_if_applicable",
    "document_failure_and_scope",
}
REQUIRED_MERGE_GATE_POLICY = {
    "hardware_result_required_before_behavior_change_merge",
    "no_unsupported_hardware_claims",
    "rollback_plan_required",
    "checkers_must_pass",
}

GENERATED_CONSTANTS_DOC_PHRASES = (
    "does not edit firmware source",
    "does not implement generated constants",
    "does not change table values",
    "does not validate hardware",
)
RUNTIME_PLAN_DOC_PHRASES = (
    "does not implement runtime-loaded config",
    "does not implement storage",
    "does not implement serial/device write behavior",
    "does not change firmware behavior",
    "does not validate hardware",
)
HARDWARE_PLAN_DOC_PHRASES = (
    "does not execute hardware testing",
    "does not validate hardware",
    "not a hardware result",
    "does not change firmware runtime behavior",
)
INTERPRETER_SOURCE_BASELINE_PLAN_DOC_PHRASES = (
    "template_only",
    "behavior-preserving firmware-owned runtime-config interpreter boundary",
    "source-owned config-shaped baseline",
    "validate-before-use",
    "fallback-to-known-good",
    "no_runtime_loaded_storage",
    "no_webserial_or_device_write",
    "no_protobuf_binary_config_parser",
    "no_firmware_flashing_automation",
    "no_nunchuk_validation",
    "not a hardware result",
)

EXPECTED_INTERPRETER_SOURCE_BASELINE_PLAN = {
    "schema_name": "glyph_runtime_config_interpreter_source_baseline_hardware_plan",
    "plan_version": 1,
    "status": "TEMPLATE_ONLY",
    "branch": "runtime-config-interpreter-source-baseline",
    "build_command": "./scripts/build-glyph-mk6-quiet.sh",
    "hardware_result_recorded": False,
    "commit_sha_under_test": "unknown",
    "firmware_artifact_path": "unknown",
    "firmware_artifact_sha256": "unknown",
    "tester": "unknown",
    "test_date": "unknown",
}

EXPECTED_INTERPRETER_SOURCE_BASELINE_INTENT = {
    "description": "Behavior-preserving firmware-owned runtime-config interpreter boundary for the current source-owned baseline.",
    "scope": [
        "source-owned config-shaped baseline only",
        "validate-before-use",
        "explicit fallback to known-good source-owned baseline",
        "table lookup through interpreter path",
        "no runtime-loaded storage",
    ],
    "non_claims": [
        "no nunchuk validation claim",
    ],
}

EXPECTED_INTERPRETER_SOURCE_BASELINE_ROWS = {
    "BOOT-001": ("boot", "Normal boot after build reaches expected boot state"),
    "PROFILE-001": ("identity_profile", "Current identity/default profile remains usable"),
    "DEFAULT-001": ("default_table", "Default table outputs preserved"),
    "MODE-001": ("mode_default", "Mode default/center behavior preserved"),
    "XY-001": ("xy_modifiers", "Representative X/Y modifier outputs preserved"),
    "TILT-001": ("tilt_tables", "Tilt1/Tilt2/Tilt3 representative outputs preserved"),
    "LAYER-001": ("layer_tables", "Layer Normal-X / Flipper representative outputs preserved"),
    "SPECIAL-TABLE-001": (
        "special_tables",
        "Tilt1Minus41 / RT1RF4Custom / Lt1LowMagnitude preserved",
    ),
    "OVERRIDE-001": ("override_paths", "RF9 null / RF6 low magnitude / hard Up-B if applicable"),
    "CSTICK-001": ("cstick_interaction", "Existing C-stick interaction not regressed where doable"),
    "PROFILE-REG-001": ("profile_regression", "No profile regression observed"),
    "NUNCHUK-001": ("nunchuk_scope", "Explicitly mark nunchuk as not tested in this branch"),
}

EXPECTED_INTERPRETER_SOURCE_BASELINE_CAVEATS = {
    "no_runtime_loaded_storage",
    "no_webserial_or_device_write",
    "no_protobuf_binary_config_parser",
    "no_firmware_flashing_automation",
    "no_nunchuk_validation",
    "no_intentional_behavior_change",
}


class ImplementationPlanningPacketError(ValueError):
    """Raised when implementation planning packet artifacts drift."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ImplementationPlanningPacketError(message)


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


def require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        fail(f"{key} must be a list")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
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


def validate_generated_constants_plan(plan: dict[str, Any]) -> str:
    require_expected_values(plan, EXPECTED_GENERATED_CONSTANTS_PLAN, "generated_constants_plan")
    require_explicit_user_approval(plan, "generated_constants_plan")
    require_superset(
        require_string_list(plan, "required_invariants"),
        REQUIRED_GENERATED_CONSTANTS_INVARIANTS,
        "generated_constants_plan.required_invariants",
    )
    require_superset(
        require_string_list(plan, "forbidden_changes"),
        REQUIRED_GENERATED_CONSTANTS_FORBIDDEN_CHANGES,
        "generated_constants_plan.forbidden_changes",
    )
    return str(plan["status"])


def validate_runtime_plan(plan: dict[str, Any]) -> str:
    require_expected_values(plan, EXPECTED_RUNTIME_PLAN, "runtime_loaded_config_plan")
    require_explicit_user_approval(plan, "runtime_loaded_config_plan")
    require_superset(
        require_string_list(plan, "required_architecture_decisions"),
        REQUIRED_RUNTIME_ARCHITECTURE_DECISIONS,
        "runtime_loaded_config_plan.required_architecture_decisions",
    )
    require_superset(
        require_string_list(plan, "forbidden_shortcuts"),
        REQUIRED_RUNTIME_FORBIDDEN_SHORTCUTS,
        "runtime_loaded_config_plan.forbidden_shortcuts",
    )
    return str(plan["status"])


def validate_hardware_plan(plan: dict[str, Any]) -> str:
    require_expected_values(plan, EXPECTED_HARDWARE_PLAN, "hardware_validation_plan")
    require_superset(
        require_string_list(plan, "required_for_change_classes"),
        REQUIRED_CHANGE_CLASSES,
        "hardware_validation_plan.required_for_change_classes",
    )
    require_superset(
        require_string_list(plan, "required_rollback_plan"),
        REQUIRED_ROLLBACK_PLAN,
        "hardware_validation_plan.required_rollback_plan",
    )
    require_superset(
        require_string_list(plan, "merge_gate_policy"),
        REQUIRED_MERGE_GATE_POLICY,
        "hardware_validation_plan.merge_gate_policy",
    )
    return str(plan["status"])


def validate_interpreter_source_baseline_plan(plan: dict[str, Any]) -> str:
    require_expected_values(
        plan,
        EXPECTED_INTERPRETER_SOURCE_BASELINE_PLAN,
        "runtime_config_interpreter_source_baseline_plan",
    )

    intent = require_object(plan, "intent")
    if (
        require_string(
            intent.get("description"),
            "runtime_config_interpreter_source_baseline_plan.intent.description",
        )
        != EXPECTED_INTERPRETER_SOURCE_BASELINE_INTENT["description"]
    ):
        fail("runtime_config_interpreter_source_baseline_plan.intent.description drifted")
    if (
        require_string_list(intent, "scope")
        != EXPECTED_INTERPRETER_SOURCE_BASELINE_INTENT["scope"]
    ):
        fail("runtime_config_interpreter_source_baseline_plan.intent.scope drifted")
    if (
        require_string_list(intent, "non_claims")
        != EXPECTED_INTERPRETER_SOURCE_BASELINE_INTENT["non_claims"]
    ):
        fail("runtime_config_interpreter_source_baseline_plan.intent.non_claims drifted")

    rows = require_list(plan, "test_rows")
    if len(rows) != len(EXPECTED_INTERPRETER_SOURCE_BASELINE_ROWS):
        fail(
            "runtime_config_interpreter_source_baseline_plan.test_rows must contain "
            f"{len(EXPECTED_INTERPRETER_SOURCE_BASELINE_ROWS)} rows"
        )

    seen_row_ids: set[str] = set()
    expected_order = list(EXPECTED_INTERPRETER_SOURCE_BASELINE_ROWS)
    for index, row_obj in enumerate(rows):
        if not isinstance(row_obj, dict):
            fail(
                "runtime_config_interpreter_source_baseline_plan.test_rows["
                f"{index}] must be an object"
            )
        row = row_obj
        row_id = require_string(
            row.get("row_id"),
            f"runtime_config_interpreter_source_baseline_plan.test_rows[{index}].row_id",
        )
        category = require_string(
            row.get("category"),
            f"runtime_config_interpreter_source_baseline_plan.test_rows[{index}].category",
        )
        planned_check = require_string(
            row.get("planned_check"),
            f"runtime_config_interpreter_source_baseline_plan.test_rows[{index}].planned_check",
        )
        result = require_string(
            row.get("result"),
            f"runtime_config_interpreter_source_baseline_plan.test_rows[{index}].result",
        )
        if row_id in seen_row_ids:
            fail(f"runtime_config_interpreter_source_baseline_plan contains duplicate row_id: {row_id}")
        seen_row_ids.add(row_id)

        expected = EXPECTED_INTERPRETER_SOURCE_BASELINE_ROWS.get(row_id)
        if expected is None:
            fail(f"runtime_config_interpreter_source_baseline_plan contains unexpected row_id: {row_id}")
        expected_category, expected_check = expected
        if row_id != expected_order[index]:
            fail("runtime_config_interpreter_source_baseline_plan.test_rows order drifted")
        if category != expected_category:
            fail(f"{row_id} category must be {expected_category!r}")
        if planned_check != expected_check:
            fail(f"{row_id} planned_check drifted")
        if result != "NOT_TESTED":
            fail(f"{row_id} must remain NOT_TESTED")

    missing_rows = sorted(set(EXPECTED_INTERPRETER_SOURCE_BASELINE_ROWS) - seen_row_ids)
    if missing_rows:
        fail(
            "runtime_config_interpreter_source_baseline_plan missing row(s): "
            + ", ".join(missing_rows)
        )

    caveats = require_string_list(plan, "caveats")
    if set(caveats) != EXPECTED_INTERPRETER_SOURCE_BASELINE_CAVEATS:
        fail("runtime_config_interpreter_source_baseline_plan.caveats drifted")

    return str(plan["status"])


def validate_go_nogo_index(index: dict[str, Any]) -> None:
    gates = require_object(index, "gates")
    expected = {
        "generated_constants_firmware_refactor": "BLOCKED_EXPLICIT_APPROVAL",
        "runtime_loaded_config_interpreter_storage": "BLOCKED_EXPLICIT_APPROVAL",
        "new_runtime_behavior_change": "BLOCKED_EXPLICIT_APPROVAL_AND_HARDWARE_TEST",
        "device_write_serial_transport": "BLOCKED_SOURCE_AUTHORITY_AND_APPROVAL",
    }
    for gate, status in expected.items():
        if gates.get(gate) != status:
            fail(f"go_nogo_index.gates.{gate} must be {status!r}")


def validate_readiness_packets(
    generated_constants_readiness: dict[str, Any],
    runtime_readiness: dict[str, Any],
) -> None:
    if generated_constants_readiness.get("status") != "blocked_until_explicit_approval":
        fail("generated constants readiness packet must remain blocked until explicit approval")
    if runtime_readiness.get("status") != "blocked_until_explicit_approval_and_design_resolution":
        fail(
            "runtime-loaded config readiness packet must remain blocked until "
            "approval/design resolution"
        )


def validate_doc_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    lowered = path.read_text(encoding="utf-8").lower()
    for phrase in phrases:
        if phrase not in lowered:
            fail(f"{display(path)} missing required caveat phrase: {phrase}")


def validate_contracts() -> tuple[str, str, str, str]:
    generated_constants_plan = load_json_object(GENERATED_CONSTANTS_PLAN_FIXTURE_PATH)
    runtime_plan = load_json_object(RUNTIME_PLAN_FIXTURE_PATH)
    hardware_plan = load_json_object(HARDWARE_PLAN_FIXTURE_PATH)
    interpreter_source_baseline_plan = load_json_object(
        INTERPRETER_SOURCE_BASELINE_PLAN_FIXTURE_PATH
    )
    go_nogo_index = load_json_object(GO_NOGO_FIXTURE_PATH)
    runtime_readiness = load_json_object(RUNTIME_READINESS_FIXTURE_PATH)
    generated_constants_readiness = load_json_object(GENERATED_CONSTANTS_READINESS_FIXTURE_PATH)

    generated_constants_status = validate_generated_constants_plan(generated_constants_plan)
    runtime_loaded_config_status = validate_runtime_plan(runtime_plan)
    hardware_plan_status = validate_hardware_plan(hardware_plan)
    runtime_config_interpreter_source_baseline_status = validate_interpreter_source_baseline_plan(
        interpreter_source_baseline_plan
    )
    validate_go_nogo_index(go_nogo_index)
    validate_readiness_packets(generated_constants_readiness, runtime_readiness)
    validate_doc_phrases(GENERATED_CONSTANTS_PLAN_DOC_PATH, GENERATED_CONSTANTS_DOC_PHRASES)
    validate_doc_phrases(RUNTIME_PLAN_DOC_PATH, RUNTIME_PLAN_DOC_PHRASES)
    validate_doc_phrases(HARDWARE_PLAN_DOC_PATH, HARDWARE_PLAN_DOC_PHRASES)
    validate_doc_phrases(
        INTERPRETER_SOURCE_BASELINE_PLAN_DOC_PATH,
        INTERPRETER_SOURCE_BASELINE_PLAN_DOC_PHRASES,
    )

    return (
        generated_constants_status,
        runtime_loaded_config_status,
        hardware_plan_status,
        runtime_config_interpreter_source_baseline_status,
    )


def main() -> int:
    print("glyph_implementation_planning_packets")
    try:
        (
            generated_constants_status,
            runtime_loaded_config_status,
            hardware_plan_status,
            runtime_config_interpreter_source_baseline_status,
        ) = validate_contracts()
    except (ImplementationPlanningPacketError, OSError, KeyError) as exc:
        print("status=FAIL")
        print("generated_constants_status=UNKNOWN")
        print("runtime_loaded_config_status=UNKNOWN")
        print("hardware_plan_status=UNKNOWN")
        print("runtime_config_interpreter_source_baseline_status=UNKNOWN")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"generated_constants_status={generated_constants_status}")
    print(f"runtime_loaded_config_status={runtime_loaded_config_status}")
    print(f"hardware_plan_status={hardware_plan_status}")
    print(
        "runtime_config_interpreter_source_baseline_status="
        f"{runtime_config_interpreter_source_baseline_status}"
    )
    print("hardware_status=not_new_hardware_result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
