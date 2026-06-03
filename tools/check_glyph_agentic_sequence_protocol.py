#!/usr/bin/env python3
"""Validate the Glyph agentic sequence protocol docs/fixture pair."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_agentic_sequence_protocol_2026-06-03.md"
FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/glyph_agentic_sequence_protocol_2026-06-03.json"

EXPECTED_USER_INTERVENTION_GATES = 8

REQUIRED_DOC_PHRASES = [
    "workflow protocol only",
    "not implementation",
    "not hardware validation",
    "not authorization to bypass user gates",
    "supervisor role",
    "subagent role",
    "one branch per issue",
    "start from current `origin/configurator`",
    "stop if the target branch already exists locally or remotely",
    "one conceptual change per branch",
    "merge after each successful branch",
    "run standard checks after each branch and merge",
    "no continuation after failed checks",
    "user intervention is required only for",
    "final summary must report",
]

EXPECTED_LISTS = {
    "supervisor_responsibilities": {
        "define_branch_objective_and_scope",
        "confirm_start_from_current_origin_configurator",
        "confirm_target_branch_absent_locally_and_remotely",
        "review_checker_output_before_continuation",
        "require_user_intervention_when_a_stop_gate_is_hit",
        "keep_branch_history_separate_and_bounded",
    },
    "subagent_responsibilities": {
        "work_exactly_one_branch_at_a_time",
        "make_one_conceptual_change_per_branch",
        "stay_within_docs_tools_fixtures_scope",
        "run_required_checks_after_each_branch_and_merge",
        "stop_immediately_on_failed_checks",
        "report_final_summary_in_required_format",
    },
    "required_stop_conditions": {
        "source_authority_ambiguity",
        "target_branch_exists_locally_or_remotely",
        "failed_checks",
        "unsupported_behavior_claims",
        "firmware_source_approval_required",
        "hardware_testing_required",
        "profile_artifact_approval_required",
        "runtime_loaded_config_approval_required",
        "serial_device_write_approval_required",
    },
    "user_intervention_required_for": {
        "source_authority_ambiguity",
        "firmware_source_approval",
        "hardware_testing",
        "profile_artifact_approval",
        "runtime_loaded_config_approval",
        "serial_device_write_approval",
        "unsupported_behavior_claims",
        "checker_or_build_failures_not_automatically_correctable",
    },
    "forbidden_autonomous_actions": {
        "firmware_source_changes_without_approval",
        "hardware_validation_claims",
        "serial_device_write_behavior",
        "runtime_loaded_config_implementation",
        "profile_artifact_changes",
        "schema_protobuf_changes",
        "unsupported_behavior_claims",
    },
    "required_branch_lifecycle": {
        "start_from_current_origin_configurator",
        "one_branch_per_issue",
        "stop_if_target_branch_exists_locally_or_remotely",
        "one_conceptual_change_per_branch",
        "merge_after_each_successful_branch",
        "do_not_merge_to_configurator_from_subagent",
    },
    "required_verification_lifecycle": {
        "run_standard_checks_after_each_branch_and_merge",
        "stop_on_failed_checks",
        "no_continuation_after_failed_checks",
        "do_not_treat_failed_checks_as_automatically_correctable",
    },
}


class ProtocolValidationError(ValueError):
    """Raised when the protocol docs or fixture drift."""


def fail(message: str) -> None:
    raise ProtocolValidationError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path.relative_to(REPO_ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be an object: {path.relative_to(REPO_ROOT)}")
    return payload


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_superset(actual: list[str], required: set[str], key: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{key} missing required value(s): {', '.join(missing)}")


def validate_doc() -> None:
    try:
        text = DOC_PATH.read_text(encoding="utf-8").lower()
    except FileNotFoundError:
        fail(f"missing file: {DOC_PATH.relative_to(REPO_ROOT)}")
    missing = [phrase for phrase in REQUIRED_DOC_PHRASES if phrase not in text]
    if missing:
        fail("doc missing required phrase(s): " + ", ".join(missing))


def validate_fixture() -> dict[str, Any]:
    payload = load_json_object(FIXTURE_PATH)

    expected_fields = {
        "schema_name": "glyph_agentic_sequence_protocol",
        "protocol_version": 1,
        "status": "workflow_protocol_only",
        "hardware_status": "not_new_hardware_result",
    }
    for key, expected in expected_fields.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")

    for key, required in EXPECTED_LISTS.items():
        require_superset(require_string_list(payload, key), required, key)

    return payload


def main() -> int:
    try:
        validate_doc()
        payload = validate_fixture()
        gate_count = len(require_string_list(payload, "user_intervention_required_for"))
        print(
            "glyph_agentic_sequence_protocol; "
            f"status=PASS; user_intervention_gates={gate_count}; "
            "hardware_status=not_new_hardware_result"
        )
        return 0
    except ProtocolValidationError as exc:
        print(
            "glyph_agentic_sequence_protocol; "
            f"status=FAIL; user_intervention_gates={EXPECTED_USER_INTERVENTION_GATES}; "
            "hardware_status=not_new_hardware_result"
        )
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
