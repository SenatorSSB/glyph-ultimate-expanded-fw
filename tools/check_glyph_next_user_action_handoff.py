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
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "next_user_action_required",
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

REQUIRED_BLOCKED_ITEMS = {
    "export_corpus_provision",
    "adapter_prewrite_source_authority",
    "physical_logical_rf5_resolution",
    "implementation_approval",
}

REQUIRED_ACTIONS = {
    "provide_export_corpus_artifacts_or_leave_blocked",
    "provide_source_authority_approval_before_write_capable_work",
    "provide_domain_input_or_hardware_source_evidence_for_rf5_if_resolution_is_needed",
    "provide_explicit_implementation_approval_before_firmware_behavior_change",
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
    "next_user_action_required",
    "preservation hardware result is recorded for applicable non-nunchuk scope",
    "nunchuk remains NOT_TESTED / unvalidated / unavailable",
    "has no nunchuk port available out of the box",
    "Export corpus capture",
    "blocked_missing_real_corpus_artifacts",
    "glyph/gfw5-export-corpus-final-blocker-status",
    "export corpus final blocker/status consolidation",
    "export corpus capture remains blocked by missing real corpus artifacts",
    "docs/calibration/glyph_export_corpus_final_blocker_status_2026-06-06.md",
    "docs/calibration/fixtures/glyph_export_corpus_final_blocker_status_2026-06-06.json",
    "tools/check_glyph_export_corpus_final_blocker_status.py",
    "Write-capable adapter / prewrite behavior",
    "adapter_prewrite_blocked",
    "Physical/logical/RF5 ambiguity",
    "requires_source_authority_hardware_result_or_user_domain_input",
    "No hardware result is recorded by this handoff",
    "No nunchuk hardware validation claim is made here",
    "No firmware behavior change is made here",
    "No runtime-loaded config is implemented here",
    "No WebSerial/device write is implemented here",
    "No external remapper adapter output is generated here",
    "No firmware implementation should start from this handoff alone",
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
    for key in (
        "hardware_testing_now_required",
        "corpus_artifacts_needed",
        "source_authority_or_domain_input_needed",
    ):
        if payload.get(key) is not True:
            fail(f"{key} must be true")


def validate_sequence_branches(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
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
        commit = raw.get("commit")
        if not isinstance(commit, str) or len(commit) != 12:
            fail(f"completed branch {branch} requires a 12-character commit")
        for field in ("doc_path", "fixture_path", "checker_path", "packet"):
            if not isinstance(raw.get(field), str) or not raw[field].strip():
                fail(f"completed branch {branch}.{field} must be a non-empty string")
        for field in ("doc_path", "fixture_path", "checker_path"):
            if not (REPO_ROOT / raw[field]).exists():
                fail(f"completed branch {branch}.{field} references missing path: {raw[field]}")
        branches[branch] = raw
    missing = sorted(REQUIRED_BRANCHES - set(branches))
    if missing:
        fail("sequence_branches_completed missing: " + ", ".join(missing))
    return branches


def validate_upstream_packet_statuses(branches: dict[str, dict[str, Any]]) -> None:
    preservation = load_json_object(REPO_ROOT / branches["glyph/gfw4-preservation-hardware-readiness"]["fixture_path"])
    if preservation.get("status") != "readiness_packet_only":
        fail("preservation readiness packet must remain readiness_packet_only")
    if preservation.get("preservation_hardware_status") != "blocked_pending_user_hardware_execution":
        fail("preservation hardware must remain blocked pending user execution")
    if preservation.get("result_recorded") is not False or preservation.get("hardware_validation_claimed") is not False:
        fail("preservation readiness must not record result or claim hardware validation")

    corpus = load_json_object(REPO_ROOT / branches["glyph/gfw4-export-corpus-readiness-status"]["fixture_path"])
    if corpus.get("status") != "blocked_missing_real_corpus_artifacts":
        fail("export corpus readiness status must remain blocked_missing_real_corpus_artifacts")
    if corpus.get("corpus_present") is not False or corpus.get("completion_allowed") is not False:
        fail("export corpus must not be marked present or complete")

    adapter = load_json_object(REPO_ROOT / branches["glyph/gfw4-adapter-prewrite-blocker-matrix"]["fixture_path"])
    if adapter.get("status") != "write_capable_adapter_blocked_docs_tools_matrix":
        fail("adapter blocker matrix status drifted")
    if adapter.get("matrix_status") != "adapter_prewrite_blocked":
        fail("adapter blocker matrix must remain adapter_prewrite_blocked")

    rf5 = load_json_object(REPO_ROOT / branches["glyph/gfw4-physical-logical-rf5-gap-index"]["fixture_path"])
    if rf5.get("old_rf5_smoke_result") != "NOT_TESTED_AMBIGUOUS":
        fail("RF5 gap index must preserve old RF5 NOT_TESTED_AMBIGUOUS status")
    if rf5.get("future_resolution_status") != "requires_source_authority_hardware_result_or_user_domain_input":
        fail("RF5 gap index future resolution status drifted")


def validate_remaining_blocked_items(payload: dict[str, Any]) -> None:
    raw_items = payload.get("remaining_blocked_items")
    if not isinstance(raw_items, list):
        fail("remaining_blocked_items must be a list")
    items: dict[str, dict[str, Any]] = {}
    for raw in raw_items:
        if not isinstance(raw, dict):
            fail("each remaining blocked item must be an object")
        item_id = raw.get("item_id")
        if not isinstance(item_id, str) or not item_id.strip():
            fail("each remaining blocked item requires item_id")
        if item_id in items:
            fail(f"duplicate remaining blocked item: {item_id}")
        for field in (
            "status",
            "requires_user_hardware",
            "requires_user_artifacts",
            "requires_source_authority_approval",
            "requires_domain_input",
            "required_next_action",
        ):
            if field not in raw:
                fail(f"remaining blocked item {item_id} missing {field}")
        if not isinstance(raw["required_next_action"], str) or not raw["required_next_action"].strip():
            fail(f"remaining blocked item {item_id}.required_next_action must be a non-empty string")
        items[item_id] = raw
    missing = sorted(REQUIRED_BLOCKED_ITEMS - set(items))
    if missing:
        fail("remaining_blocked_items missing: " + ", ".join(missing))
    if items["export_corpus_provision"]["requires_user_artifacts"] is not True:
        fail("export corpus provision must require user artifacts")
    if items["adapter_prewrite_source_authority"]["requires_source_authority_approval"] is not True:
        fail("adapter prewrite source authority must require source-authority approval")
    if items["physical_logical_rf5_resolution"]["requires_domain_input"] is not True:
        fail("RF5 resolution must require domain input when resolving ambiguity")
    if items["implementation_approval"]["status"] != "BLOCKED_IMPLEMENTATION_APPROVAL":
        fail("implementation approval must remain blocked")


def validate_actions_and_non_claims(payload: dict[str, Any]) -> None:
    actions = payload.get("next_user_required_actions")
    if not isinstance(actions, list) or not all(isinstance(action, str) for action in actions):
        fail("next_user_required_actions must be a list of strings")
    missing_actions = sorted(REQUIRED_ACTIONS - set(actions))
    if missing_actions:
        fail("next_user_required_actions missing: " + ", ".join(missing_actions))
    if payload.get("future_result_branch") != "glyph/gfw4-preservation-hardware-result":
        fail("future_result_branch must be glyph/gfw4-preservation-hardware-result")

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
    baseline = load_json_object(
        REPO_ROOT / "docs/calibration/fixtures/glyph_post_gfw3_configurator_baseline_2026-06-06.json"
    )
    if baseline.get("status") != "post_gfw3_configurator_baseline_recorded":
        fail("post-GFW3 baseline status drifted")
    for key in (
        "nunchuk_hardware_validated",
        "runtime_loaded_config_implemented",
        "webserial_write_implemented",
        "device_write_implemented",
        "external_remapper_adapter_implemented",
        "active_profile_artifact_changed",
    ):
        if baseline.get("non_claims", {}).get(key) is not False:
            fail(f"post-GFW3 baseline non_claims.{key} must be false")


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
        branches = validate_sequence_branches(payload)
        validate_upstream_packet_statuses(branches)
        validate_remaining_blocked_items(payload)
        validate_actions_and_non_claims(payload)
        validate_doc()
    except (OSError, NextUserActionHandoffError, ValueError) as exc:
        print("status=FAIL")
        print("handoff_status=next_user_action_required")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("handoff_status=next_user_action_required")
    print("hardware_testing_now_required=true")
    print("corpus_artifacts_needed=true")
    print("source_authority_or_domain_input_needed=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
