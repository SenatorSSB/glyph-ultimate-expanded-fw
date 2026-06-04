#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter transform decision matrix."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_transform_decision_matrix"
STATUS = "decision_matrix_only_implementation_blocked"
VERSION = 1
HARDWARE_STATUS = "not_new_hardware_result"

ALLOWED_DECISION_STATUSES = ["unresolved", "blocked"]

SOURCE_PACKETS = {
    "adapter_blocker_escalation": {
        "doc_path": "docs/calibration/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.json",
        "checker_path": "tools/check_glyph_offline_remapper_adapter_blocker_escalation.py",
        "evidence_role": "source for adapter implementation and external JSON generation remaining blocked",
    },
    "export_loss_gate": {
        "doc_path": "docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json",
        "checker_path": "tools/check_glyph_offline_remapper_export_loss_gate.py",
        "evidence_role": "source for active profile round-trip remaining unsafe",
    },
    "transform_design_contract": {
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_design_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_contract_2026-06-04.json",
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_design_contract.py",
        "evidence_role": "source for no transform implementation and forbidden output boundaries",
    },
    "transform_rule_matrix": {
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.json",
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_rule_matrix.py",
        "evidence_role": "source for sidecar-only/out-of-scope transform planning categories",
    },
    "storage_transport_research_index": {
        "doc_path": "docs/calibration/glyph_storage_transport_research_index_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_storage_transport_research_index_2026-06-03.json",
        "checker_path": "tools/check_glyph_storage_transport_research_index.py",
        "evidence_role": "source for protobuf, WebSerial, device write, and runtime-loaded config blockers",
    },
}

DECISIONS = [
    {
        "decision_id": "adapter_target_import_only_not_round_trip",
        "question": "Whether the adapter target is import-only, not round-trip.",
        "status": "unresolved",
        "blocker": "Active profile round-trip is unsafe through the external remapper export, so target direction must be explicitly decided before implementation.",
        "required_before_implementation": "Document explicit approval for an import-only target, or document a different reviewed target with new source evidence.",
    },
    {
        "decision_id": "external_remapper_visual_editor_allowed",
        "question": "Whether the external remapper is allowed to be used as a visual editor.",
        "status": "unresolved",
        "blocker": "The external remapper export is not canonical for the active identity-runtime profile, so visual-editor use must be bounded before implementation.",
        "required_before_implementation": "Decide whether visual editing is allowed only with sidecar warnings, or is disallowed for identity-runtime profiles.",
    },
    {
        "decision_id": "runtime_owned_behavior_sidecar_only",
        "question": "Whether runtime-owned behavior is represented only in sidecar.",
        "status": "blocked",
        "blocker": "Runtime-owned behavior is not represented by external profile JSON in the current checked packets.",
        "required_before_implementation": "Approve a sidecar-only representation policy, or provide source authority for another representation.",
    },
    {
        "decision_id": "socd_policy_sidecar_or_profile_candidate",
        "question": "Whether SOCD policy should remain sidecar-only or become a profile-level candidate.",
        "status": "unresolved",
        "blocker": "SOCD drift is adapter-blocking and the transform rule matrix currently keeps SOCD policy sidecar-only.",
        "required_before_implementation": "Resolve SOCD policy placement with source-backed evidence and explicit approval.",
    },
    {
        "decision_id": "activates_bearing_bindings_regeneration_allowed",
        "question": "Whether activates-bearing bindings can ever be regenerated.",
        "status": "blocked",
        "blocker": "Exported profile JSON stripped activates-bearing bindings, and active profile round-trip is unsafe.",
        "required_before_implementation": "Provide source authority and review for any regeneration strategy, or keep regeneration disallowed.",
    },
    {
        "decision_id": "official_configurator_compatibility_scope",
        "question": "Whether official configurator compatibility is in scope.",
        "status": "blocked",
        "blocker": "No official configurator compatibility claim is made by the current packets.",
        "required_before_implementation": "Provide official source authority and explicit approval before any compatibility claim.",
    },
    {
        "decision_id": "protobuf_device_write_out_of_scope",
        "question": "Whether protobuf/device-write remains fully out of scope.",
        "status": "blocked",
        "blocker": "Protobuf binary generation, WebSerial transport, serial/device write behavior, and runtime-loaded config remain unimplemented and blocked.",
        "required_before_implementation": "Keep the scope fully out of implementation, or open a separate approved design with official source authority.",
    },
    {
        "decision_id": "repeat_no_device_experiment_required",
        "question": "Whether a repeated no-device experiment is required with browser/version recorded.",
        "status": "unresolved",
        "blocker": "Prior packets list repeated no-device experiment evidence with browser/version recorded as required future evidence.",
        "required_before_implementation": "Decide whether repeat experiment evidence is mandatory and define its required recording fields.",
    },
    {
        "decision_id": "source_audit_required_before_implementation",
        "question": "Whether source audit is required before implementation.",
        "status": "blocked",
        "blocker": "External source is not promoted to authority and transform rules remain planning-only.",
        "required_before_implementation": "Complete and review a source audit before any transform implementation or external JSON generation.",
    },
    {
        "decision_id": "license_review_required_before_code_reuse",
        "question": "Whether license review is required before any code reuse.",
        "status": "blocked",
        "blocker": "No external code has been copied and no external dependency has been added.",
        "required_before_implementation": "Complete license review before any external code reuse, dependency addition, or copied implementation detail.",
    },
    {
        "decision_id": "user_approval_required_before_implementation",
        "question": "Whether user approval is required before implementation.",
        "status": "blocked",
        "blocker": "Adapter implementation, transform implementation, and external JSON generation are not approved.",
        "required_before_implementation": "Obtain explicit user approval before adapter implementation, transform code, or external JSON generation.",
    },
]

REQUIRED_DECISION_IDS = [decision["decision_id"] for decision in DECISIONS]

REQUIRED_DOC_PHRASES = (
    "decision_matrix_only_implementation_blocked",
    "All decisions are unresolved or blocked.",
    "No implementation decision is approved.",
    "implementation_decisions_approved=false",
    "adapter_implementation_allowed=false",
    "External JSON generation is not allowed.",
    "No adapter implementation is added.",
    "No transform code is added.",
    "No runtime source is changed.",
    "No active profile artifact is changed.",
    "No exported experiment artifact is changed.",
    "No runtime-loaded config is implemented.",
    "No serial/device write behavior is implemented.",
    "No WebSerial transport is implemented.",
    "No protobuf binary generation is implemented.",
    "No official configurator compatibility is claimed.",
    "No hardware validation is claimed.",
    "No external source is promoted to authority.",
    "No external code is copied and no dependency is added.",
    "whether the adapter target is import-only, not round-trip",
    "whether the external remapper is allowed to be used as a visual editor",
    "whether runtime-owned behavior is represented only in sidecar",
    "whether SOCD policy should remain sidecar-only or become a profile-level candidate",
    "whether activates-bearing bindings can ever be regenerated",
    "whether official configurator compatibility is in scope",
    "whether protobuf/device-write remains fully out of scope",
    "whether a repeated no-device experiment is required with browser/version recorded",
    "whether source audit is required before implementation",
    "whether license review is required before any code reuse",
    "whether user approval is required before implementation",
)


class DecisionMatrixError(ValueError):
    """Raised when the decision matrix drifts."""


def fail(message: str) -> None:
    raise DecisionMatrixError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path} must contain a JSON object")
    return payload


def validate_source_paths() -> dict[str, dict[str, str]]:
    source_packets: dict[str, dict[str, str]] = {}
    for key, packet in SOURCE_PACKETS.items():
        for field in ("doc_path", "fixture_path", "checker_path"):
            path = REPO_ROOT / packet[field]
            if not path.exists():
                fail(f"required source path missing: {packet[field]}")
        source_packets[key] = packet
    return source_packets


def build_matrix() -> dict[str, Any]:
    return {
        "adapter_implementation_added": False,
        "adapter_implementation_allowed": False,
        "active_profile_artifact_changed": False,
        "decisions": DECISIONS,
        "external_code_copied": False,
        "external_dependency_added": False,
        "external_json_generated": False,
        "external_json_generation_allowed": False,
        "external_source_promoted_to_authority": False,
        "exported_experiment_artifact_changed": False,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "implementation_decisions_approved": False,
        "official_configurator_compatibility_claimed": False,
        "protobuf_binary_generation_implemented": False,
        "runtime_loaded_config_implemented": False,
        "runtime_source_changed": False,
        "schema_name": SCHEMA_NAME,
        "serial_device_write_implemented": False,
        "source_packets": validate_source_paths(),
        "status": STATUS,
        "transform_code_added": False,
        "transform_implementation_added": False,
        "validation_report": {
            "checker_path": "tools/check_glyph_clean_room_adapter_transform_decision_matrix.py",
            "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.md",
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.json",
            "validation_scope": "docs_tools_fixtures_only",
        },
        "version": VERSION,
        "webserial_transport_implemented": False,
    }


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    missing = [phrase for phrase in REQUIRED_DOC_PHRASES if phrase not in text]
    if missing:
        fail("doc is missing required phrases: " + ", ".join(missing))


def validate_fixture(matrix: dict[str, Any]) -> None:
    fixture = load_json_object(FIXTURE_PATH)
    if fixture != matrix:
        fail("fixture JSON object drifted from the expected decision matrix")

    if fixture.get("schema_name") != SCHEMA_NAME:
        fail(f"schema_name must be {SCHEMA_NAME!r}")
    if fixture.get("status") != STATUS:
        fail(f"status must be {STATUS!r}")
    if fixture.get("version") != VERSION:
        fail(f"version must be {VERSION}")

    false_flags = [
        "adapter_implementation_added",
        "adapter_implementation_allowed",
        "active_profile_artifact_changed",
        "external_code_copied",
        "external_dependency_added",
        "external_json_generated",
        "external_json_generation_allowed",
        "external_source_promoted_to_authority",
        "exported_experiment_artifact_changed",
        "hardware_validation_claimed",
        "implementation_decisions_approved",
        "official_configurator_compatibility_claimed",
        "protobuf_binary_generation_implemented",
        "runtime_loaded_config_implemented",
        "runtime_source_changed",
        "serial_device_write_implemented",
        "transform_code_added",
        "transform_implementation_added",
        "webserial_transport_implemented",
    ]
    for flag in false_flags:
        if fixture.get(flag) is not False:
            fail(f"{flag} must be false")

    if fixture.get("hardware_status") != HARDWARE_STATUS:
        fail(f"hardware_status must be {HARDWARE_STATUS!r}")

    decisions = fixture.get("decisions")
    if not isinstance(decisions, list):
        fail("decisions must be a list")
    if [decision.get("decision_id") for decision in decisions] != REQUIRED_DECISION_IDS:
        fail("decision order or IDs drifted")

    for decision in decisions:
        if decision.get("status") not in ALLOWED_DECISION_STATUSES:
            fail(f"decision status must be unresolved or blocked: {decision}")
        if decision.get("status") == "approved":
            fail(f"decision must not be approved: {decision}")


def print_summary(status: str) -> None:
    print(SCHEMA_NAME)
    print(f"status={status}")
    print("implementation_decisions_approved=false")
    print("adapter_implementation_allowed=false")
    print(f"hardware_status={HARDWARE_STATUS}")


def main() -> int:
    try:
        validate_doc()
        matrix = build_matrix()
        validate_fixture(matrix)
    except (OSError, DecisionMatrixError) as exc:
        print_summary("FAIL")
        print(f"reason={exc}")
        return 1

    print_summary("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
