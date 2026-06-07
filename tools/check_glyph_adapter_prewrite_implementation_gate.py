#!/usr/bin/env python3
"""Validate the Glyph adapter/prewrite implementation gate packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_adapter_prewrite_implementation_gate_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_adapter_prewrite_implementation_gate_2026-06-06.json"
)

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_adapter_prewrite_implementation_gate",
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "adapter_implementation_blocked",
    "implementation_allowed": False,
    "adapter_output_generated": False,
    "device_write_allowed": False,
    "webserial_allowed": False,
    "external_source_reuse_allowed": False,
    "runtime_loaded_config_allowed": False,
    "protobuf_binary_write_allowed": False,
    "firmware_flashing_automation_allowed": False,
    "official_compatibility_claimed": False,
    "hardware_validation_claimed": False,
    "active_profile_round_trip_safe": False,
}

REQUIRED_BLOCKER_IDS = {
    "official_corpus_present_metadata_missing",
    "missing_official_configurator_source_authority",
    "external_observations_non_authoritative",
    "active_profile_round_trip_unsafe",
    "runtime_owned_behavior_not_safely_represented_in_external_json",
    "webserial_device_write_blocked",
    "runtime_loaded_config_blocked",
    "protobuf_binary_write_blocked",
    "external_source_code_reuse_blocked",
    "adapter_output_generation_blocked",
    "implementation_approval_missing",
}

REQUIRED_UNBLOCK_REQUIREMENTS = {
    "docs/tools-only source audit",
    "official corpus exists; missing metadata provision",
    "explicit user approval after source authority exists",
    "official source authority for configurator, packet framing, schema, and transport",
    "active-profile round-trip strategy",
    "license review and approval for any reuse or dependency",
    "explicit implementation approval",
}

REQUIRED_ALLOWED_NEXT_ACTIONS = {
    "docs/tools-only source audit",
    "official corpus metadata provision",
    "explicit user approval after source authority exists",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "adapter output generation",
    "device write",
    "WebSerial",
    "external code reuse",
    "official compatibility claim",
    "runtime-loaded config implementation",
    "protobuf binary write",
    "firmware flashing automation",
    "Save to Device",
}

REQUIRED_SOURCE_PACKET_PATHS = {
    "docs/calibration/glyph_export_corpus_final_blocker_status_2026-06-06.md",
    "docs/calibration/fixtures/glyph_export_corpus_final_blocker_status_2026-06-06.json",
    "tools/check_glyph_export_corpus_final_blocker_status.py",
    "docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json",
    "docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/notes.md",
    "tools/check_glyph_official_configurator_export_corpus.py",
    "docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md",
    "docs/calibration/fixtures/glyph_external_remapper_misattribution_correction_2026-06-06.json",
    "tools/check_glyph_external_remapper_misattribution_correction.py",
    "docs/calibration/glyph_adapter_prewrite_blocker_matrix_2026-06-06.md",
    "docs/calibration/fixtures/glyph_adapter_prewrite_blocker_matrix_2026-06-06.json",
    "tools/check_glyph_adapter_prewrite_blocker_matrix.py",
    "docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md",
    "docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md",
    "tools/check_glyph_profile_adapter_prewrite.py",
    "docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md",
    "docs/calibration/fixtures/glyph_configurator_compatibility_source_registry_2026-06-03.json",
    "tools/check_glyph_configurator_compatibility_source_registry.py",
    "docs/calibration/glyph_external_remapper_source_audit_readiness_gate_2026-06-04.md",
    "docs/calibration/fixtures/glyph_external_remapper_source_audit_readiness_gate_2026-06-04.json",
    "tools/check_glyph_external_remapper_source_audit_readiness_gate.py",
    "docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md",
    "docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json",
    "tools/check_glyph_offline_remapper_export_loss_gate.py",
    "docs/calibration/glyph_offline_remapper_binding_loss_classification_2026-06-04.md",
    "docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json",
    "tools/check_glyph_offline_remapper_binding_loss_classification.py",
    "docs/calibration/glyph_offline_remapper_socd_drift_classification_2026-06-04.md",
    "docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json",
    "tools/check_glyph_offline_remapper_socd_drift_classification.py",
    "docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md",
    "docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json",
    "tools/check_glyph_webserial_transport_blocker_packet.py",
    "docs/calibration/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.md",
    "docs/calibration/fixtures/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.json",
    "tools/check_glyph_runtime_storage_interpreter_blocker_packet.py",
    "docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md",
    "docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json",
    "tools/check_glyph_protobuf_config_schema_research_packet.py",
    "docs/calibration/glyph_external_remapper_license_code_reuse_blocker_2026-06-04.md",
    "docs/calibration/fixtures/glyph_external_remapper_license_code_reuse_blocker_2026-06-04.json",
    "tools/check_glyph_external_remapper_license_code_reuse_blocker.py",
    "docs/calibration/glyph_import_export_compatibility_validator_2026-06-03.md",
    "tools/check_glyph_import_export_compatibility.py",
    "docs/calibration/glyph_active_profile_binding_path_trace_2026-05-27.md",
    "tools/check_glyph_active_profile_binding_path.py",
    "docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md",
    "tools/check_glyph_merged_state_consistency.py",
    "docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md",
    "docs/calibration/fixtures/glyph_preimplementation_go_nogo_index_2026-05-28.json",
    "tools/check_glyph_preimplementation_go_nogo_index.py",
}

REQUIRED_DOC_PHRASES = (
    "adapter_implementation_blocked",
    "implementation_allowed: false",
    "write-capable adapter implementation is not approved unless all blockers are cleared",
    "docs/tools-only source audit",
    "official corpus metadata provision",
    "explicit user approval after source authority exists",
    "The official configurator corpus exists and is primary export-shape evidence",
    "external source code reuse",
    "official compatibility claim",
    "No adapter output is generated here",
    "No hardware validation claim is made here",
)

SOURCE_CHECKERS = (
    "tools/check_glyph_export_corpus_final_blocker_status.py",
    "tools/check_glyph_official_configurator_export_corpus.py",
    "tools/check_glyph_external_remapper_misattribution_correction.py",
    "tools/check_glyph_adapter_prewrite_blocker_matrix.py",
    "tools/check_glyph_configurator_compatibility_source_registry.py",
    "tools/check_glyph_offline_remapper_adapter_blocker_escalation.py",
    "tools/check_glyph_offline_remapper_export_loss_gate.py",
    "tools/check_glyph_webserial_transport_blocker_packet.py",
    "tools/check_glyph_runtime_storage_interpreter_blocker_packet.py",
    "tools/check_glyph_protobuf_config_schema_research_packet.py",
    "tools/check_glyph_external_remapper_license_code_reuse_blocker.py",
    "tools/check_glyph_import_export_compatibility.py",
    "tools/check_glyph_active_profile_binding_path.py",
    "tools/check_glyph_preimplementation_go_nogo_index.py",
)


class AdapterPrewriteImplementationGateError(ValueError):
    """Raised when the adapter/prewrite implementation gate drifts."""


def fail(message: str) -> None:
    raise AdapterPrewriteImplementationGateError(message)


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


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty string list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{label}[{index}] must be a non-empty string")
        result.append(item)
    return result


def require_subset(values: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(values))
    if missing:
        fail(f"{label} is missing required entries: " + ", ".join(missing))


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_blockers(payload: dict[str, Any]) -> None:
    raw_blockers = payload.get("blockers")
    if not isinstance(raw_blockers, list):
        fail("blockers must be a list")

    blockers: dict[str, dict[str, Any]] = {}
    for raw in raw_blockers:
        if not isinstance(raw, dict):
            fail("each blocker must be an object")
        blocker_id = raw.get("blocker_id")
        if not isinstance(blocker_id, str) or not blocker_id.strip():
            fail("each blocker requires blocker_id")
        if blocker_id in blockers:
            fail(f"duplicate blocker_id: {blocker_id}")
        if raw.get("status") != "BLOCKED":
            fail(f"blocker {blocker_id} must have status BLOCKED")
        for field in ("source_packet_paths", "prevents"):
            if not isinstance(raw.get(field), list) or not raw[field]:
                fail(f"blocker {blocker_id}.{field} must be a non-empty list")
        if not isinstance(raw.get("required_future_resolution"), str) or not raw["required_future_resolution"].strip():
            fail(f"blocker {blocker_id}.required_future_resolution must be non-empty")
        for relpath in raw["source_packet_paths"]:
            if not isinstance(relpath, str) or not relpath.strip():
                fail(f"blocker {blocker_id}.source_packet_paths must contain strings")
            if not (REPO_ROOT / relpath).exists():
                fail(f"blocker {blocker_id}.source_packet_paths references missing path: {relpath}")
        blockers[blocker_id] = raw

    missing = sorted(REQUIRED_BLOCKER_IDS - set(blockers))
    if missing:
        fail("blockers missing: " + ", ".join(missing))


def validate_lists(payload: dict[str, Any]) -> None:
    unblock_requirements = require_string_list(payload.get("unblock_requirements"), "unblock_requirements")
    allowed_next_actions = require_string_list(payload.get("allowed_next_actions"), "allowed_next_actions")
    forbidden_actions = require_string_list(payload.get("forbidden_actions"), "forbidden_actions")
    source_packet_paths = require_string_list(payload.get("source_packet_paths"), "source_packet_paths")

    require_subset(unblock_requirements, REQUIRED_UNBLOCK_REQUIREMENTS, "unblock_requirements")
    require_subset(allowed_next_actions, REQUIRED_ALLOWED_NEXT_ACTIONS, "allowed_next_actions")
    require_subset(forbidden_actions, REQUIRED_FORBIDDEN_ACTIONS, "forbidden_actions")
    require_subset(source_packet_paths, REQUIRED_SOURCE_PACKET_PATHS, "source_packet_paths")

    for relpath in source_packet_paths:
        if relpath.startswith(("http://", "https://")):
            fail(f"source_packet_paths must reference repo files only: {relpath}")
        if not (REPO_ROOT / relpath).exists():
            fail(f"source_packet_paths references missing path: {relpath}")


def validate_doc() -> None:
    if not DOC_PATH.exists():
        fail(f"missing doc: {display(DOC_PATH)}")
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"doc missing required phrase: {phrase}")


def run_source_checkers() -> None:
    for relpath in SOURCE_CHECKERS:
        completed = subprocess.run(
            [sys.executable, relpath],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
        if completed.returncode != 0:
            fail(f"component checker failed: {relpath}: {output}")
        if "status=PASS" not in completed.stdout:
            fail(f"component checker did not report PASS: {relpath}")


def main() -> int:
    print("glyph_adapter_prewrite_implementation_gate")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        validate_blockers(payload)
        validate_lists(payload)
        validate_doc()
        run_source_checkers()
    except (OSError, AdapterPrewriteImplementationGateError, ValueError) as exc:
        print("status=FAIL")
        print("adapter_implementation_blocked=true")
        print("implementation_allowed=false")
        print("adapter_output_generated=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("adapter_implementation_blocked=true")
    print("implementation_allowed=false")
    print("adapter_output_generated=false")
    print("device_write_allowed=false")
    print("webserial_allowed=false")
    print("official_compatibility_claimed=false")
    print("hardware_validation_claimed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
