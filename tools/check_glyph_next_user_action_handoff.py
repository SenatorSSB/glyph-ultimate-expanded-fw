#!/usr/bin/env python3
"""Validate the Glyph next-user-action handoff packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_next_user_action_handoff_2026-06-06.md"
FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/glyph_next_user_action_handoff_2026-06-06.json"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_next_user_action_handoff",
    "schema_version": 2,
    "packet_date": "2026-06-06",
    "status": "next_user_action_required_for_specific_artifacts_priorities_or_approval",
    "configurator_status": "docs_tools_sequence_merged_to_configurator",
}

REQUIRED_BRANCHES = {
    "glyph/gfw4-preservation-hardware-readiness",
    "glyph/gfw4-preservation-result-template-hardening",
    "glyph/gfw4-export-corpus-readiness-status",
    "glyph/gfw5-export-corpus-final-blocker-status",
    "glyph/gfw4-adapter-prewrite-blocker-matrix",
    "glyph/gfw5-adapter-prewrite-implementation-gate",
    "glyph/gfw4-physical-logical-rf5-gap-index",
}

REQUIRED_ACTION_ITEMS = {
    "official_configurator_corpus_metadata",
    "engineering_source_research_prioritization",
    "adapter_prewrite_source_authority",
    "physical_logical_rf5_resolution",
    "risky_implementation_approval",
    "hardware_test_result_after_artifact",
}

REQUIRED_ACTIONS = {
    "provide_official_configurator_metadata_or_leave_unknown",
    "choose_or_prioritize_generated_cpp_export_runtime_config_or_transport_research",
    "approve_before_risky_implementation_begins",
    "provide_domain_input_only_if_rf5_ambiguity_must_be_resolved",
    "provide_hardware_test_results_only_after_test_artifact_exists",
}

REQUIRED_FALSE_NON_CLAIMS = {
    "hardware_result_recorded_by_handoff",
    "preservation_hardware_pass_fail_claimed",
    "nunchuk_hardware_validated",
    "firmware_behavior_changed",
    "active_profile_artifact_changed",
    "runtime_loaded_config_implemented",
    "webserial_write_implemented",
    "device_write_implemented",
    "protobuf_binary_write_implemented",
    "firmware_flashing_automation_implemented",
    "external_remapper_adapter_output_generated",
    "external_source_code_copied",
    "external_dependency_added",
    "official_configurator_compatibility_claimed",
    "senscope_browser_app_changed",
    "smash_ultimate_game_semantics_changed",
}

REQUIRED_DOC_PHRASES = (
    "next_user_action_required_for_specific_artifacts_priorities_or_approval",
    "Engineering/source research prioritization",
    "generated C++ constants path, export target contract, runtime-loaded config design, or transport source research",
    "Routine engineering design and",
    "source research are not user-domain-blocked",
    "Provide product approval before any firmware behavior implementation",
    "Provide hardware test results only after a test artifact exists",
    "No firmware implementation should start from this handoff alone",
    "No runtime-loaded config is implemented here",
    "No WebSerial/device write is implemented here",
    "No external remapper adapter output is generated here",
)


class NextUserActionHandoffError(AssertionError):
    """Raised when the next-user-action handoff packet drifts."""


def fail(message: str) -> None:
    raise NextUserActionHandoffError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")
    expected_flags = {
        "user_not_blocking_routine_engineering": True,
        "hardware_testing_now_required": False,
        "corpus_artifacts_needed": False,
        "official_configurator_corpus_present": True,
        "official_configurator_metadata_needed": True,
        "source_authority_or_domain_input_needed": False,
        "product_prioritization_needed": True,
        "product_approval_required_before_risky_implementation": True,
        "engineering_design_may_proceed_when_scoped": True,
        "source_research_may_proceed_when_scoped": True,
    }
    for key, expected in expected_flags.items():
        if payload.get(key) is not expected:
            fail(f"{key} must be {expected}")


def validate_sequence_branches(payload: dict[str, Any]) -> None:
    raw_branches = payload.get("sequence_branches_completed")
    if not isinstance(raw_branches, list):
        fail("sequence_branches_completed must be a list")
    branches: dict[str, dict[str, Any]] = {}
    for raw in raw_branches:
        if not isinstance(raw, dict):
            fail("each completed branch must be an object")
        branch = raw.get("branch")
        if not isinstance(branch, str) or not branch.strip():
            fail("each completed branch requires branch")
        if branch in branches:
            fail(f"duplicate completed branch: {branch}")
        for field in ("commit", "doc_path", "fixture_path", "checker_path", "packet"):
            if not isinstance(raw.get(field), str) or not raw[field].strip():
                fail(f"completed branch {branch}.{field} must be a non-empty string")
        for field in ("doc_path", "fixture_path", "checker_path"):
            if not (REPO_ROOT / raw[field]).exists():
                fail(f"completed branch {branch}.{field} references missing path: {raw[field]}")
        branches[branch] = raw
    missing = sorted(REQUIRED_BRANCHES - set(branches))
    if missing:
        fail("sequence_branches_completed missing: " + ", ".join(missing))


def validate_action_items(payload: dict[str, Any]) -> None:
    raw_items = payload.get("remaining_action_items")
    if not isinstance(raw_items, list):
        fail("remaining_action_items must be a list")
    items: dict[str, dict[str, Any]] = {}
    for raw in raw_items:
        if not isinstance(raw, dict):
            fail("each remaining action item must be an object")
        item_id = raw.get("item_id")
        if not isinstance(item_id, str) or not item_id.strip():
            fail("each remaining action item requires item_id")
        items[item_id] = raw
        for field in (
            "status",
            "requires_user_domain_input",
            "requires_user_product_approval",
            "requires_source_research",
            "requires_hardware_test",
            "requires_user_artifact",
            "required_next_action",
        ):
            if field not in raw:
                fail(f"remaining action item {item_id} missing {field}")
        for field in (
            "requires_user_domain_input",
            "requires_user_product_approval",
            "requires_source_research",
            "requires_hardware_test",
            "requires_user_artifact",
        ):
            if not isinstance(raw[field], bool):
                fail(f"remaining action item {item_id}.{field} must be bool")
    missing = sorted(REQUIRED_ACTION_ITEMS - set(items))
    if missing:
        fail("remaining_action_items missing: " + ", ".join(missing))
    if items["official_configurator_corpus_metadata"]["status"] != "WAITING_FOR_USER_ARTIFACT":
        fail("official configurator metadata must be WAITING_FOR_USER_ARTIFACT")
    if items["engineering_source_research_prioritization"]["status"] != "READY_FOR_USER_PRODUCT_DECISION":
        fail("engineering/source research prioritization status drifted")
    if items["risky_implementation_approval"]["requires_user_product_approval"] is not True:
        fail("risky implementation must require product approval")
    if items["hardware_test_result_after_artifact"]["requires_hardware_test"] is not True:
        fail("hardware result must be required only after artifact exists")
    for item_id in ("adapter_prewrite_source_authority", "physical_logical_rf5_resolution"):
        if items[item_id]["requires_user_domain_input"]:
            fail(f"{item_id} must not be a routine user-domain blocker")


def validate_actions_and_non_claims(payload: dict[str, Any]) -> None:
    actions = payload.get("next_user_required_actions")
    if not isinstance(actions, list) or not all(isinstance(action, str) for action in actions):
        fail("next_user_required_actions must be a list of strings")
    missing_actions = sorted(REQUIRED_ACTIONS - set(actions))
    if missing_actions:
        fail("next_user_required_actions missing: " + ", ".join(missing_actions))

    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("non_claims must be an object")
    missing = sorted(REQUIRED_FALSE_NON_CLAIMS - set(non_claims))
    if missing:
        fail("non_claims missing: " + ", ".join(missing))
    for key in sorted(REQUIRED_FALSE_NON_CLAIMS):
        if non_claims.get(key) is not False:
            fail(f"non_claims.{key} must be false")


def validate_baseline_and_roadmap_paths(payload: dict[str, Any]) -> None:
    for key in ("post_gfw3_baseline_path", "roadmap_next_work_index_path"):
        rel_path = payload.get(key)
        if not isinstance(rel_path, str) or not rel_path.strip():
            fail(f"{key} must be a non-empty string")
        if not (REPO_ROOT / rel_path).exists():
            fail(f"{key} references missing path: {rel_path}")


def validate_doc() -> None:
    if not DOC_PATH.exists():
        fail(f"missing doc: {display(DOC_PATH)}")
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_next_user_action_handoff")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        validate_baseline_and_roadmap_paths(payload)
        validate_sequence_branches(payload)
        validate_action_items(payload)
        validate_actions_and_non_claims(payload)
        validate_doc()
    except (OSError, NextUserActionHandoffError, ValueError) as exc:
        print("status=FAIL")
        print("handoff_status=precise_user_actions")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("handoff_status=precise_user_actions")
    print("routine_engineering_user_domain_blocked=false")
    print("hardware_testing_now_required=false")
    print("product_approval_required_before_risky_implementation=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
