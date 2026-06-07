#!/usr/bin/env python3
"""Validate the Glyph adapter/prewrite blocker matrix packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_adapter_prewrite_blocker_matrix_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_adapter_prewrite_blocker_matrix_2026-06-06.json"
)

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_adapter_prewrite_blocker_matrix",
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "write_capable_adapter_blocked_docs_tools_matrix",
    "hardware_status": "not_new_hardware_result",
    "matrix_status": "adapter_prewrite_blocked",
}

REQUIRED_SOURCE_PACKETS = {
    "configurator_source_registry",
    "export_corpus_readiness",
    "external_remapper_license_code_reuse_blocker",
    "offline_remapper_adapter_blocker_escalation",
    "offline_remapper_export_loss_gate",
    "protobuf_config_schema_research_packet",
    "roadmap_next_work_index",
    "runtime_storage_interpreter_blocker",
    "webserial_transport_blocker",
}

REQUIRED_BLOCKERS = {
    "official_corpus_present_metadata_missing",
    "missing_official_configurator_source_authority",
    "external_observations_non_authoritative",
    "runtime_owned_behavior_not_safely_represented_in_external_json",
    "active_profile_round_trip_unsafe",
    "webserial_device_write_blocked",
    "runtime_loaded_config_blocked",
    "protobuf_binary_write_blocked",
    "external_source_code_reuse_blocked",
    "adapter_output_generation_blocked",
}

REQUIRED_FALSE_NON_CLAIMS = {
    "adapter_implemented",
    "external_remapper_compatible_json_generated",
    "webserial_write_implemented",
    "device_write_implemented",
    "save_to_device_implemented",
    "protobuf_binary_generation_implemented",
    "protobuf_binary_write_implemented",
    "runtime_loaded_config_implemented",
    "storage_interpreter_implemented",
    "firmware_flashing_automation_implemented",
    "external_source_code_copied",
    "external_dependency_added",
    "official_configurator_compatibility_claimed",
    "hardware_validation_claimed",
    "nunchuk_hardware_validated",
    "firmware_behavior_changed",
    "active_profile_artifact_changed",
    "senscope_browser_app_changed",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "adapter implementation",
    "external-remapper-compatible JSON generation",
    "WebSerial write",
    "device write",
    "Save to Device",
    "protobuf binary generation",
    "protobuf binary write",
    "runtime-loaded config implementation",
    "storage interpreter implementation",
    "firmware flashing automation",
    "external source code reuse without approval",
    "external dependency addition without approval",
    "official configurator compatibility claim",
    "hardware validation claim",
    "nunchuk hardware validation claim",
    "Senscope browser-app change",
}

REQUIRED_DOC_PHRASES = (
    "write_capable_adapter_blocked_docs_tools_matrix",
    "Official corpus present, metadata missing",
    "official_configurator_corpus_present_initial",
    "Missing official configurator source authority",
    "External observations non-authoritative",
    "Runtime-owned behavior not safely represented in external JSON",
    "Active profile round-trip unsafe",
    "WebSerial/device write blocked",
    "Runtime-loaded config blocked",
    "Protobuf binary write blocked",
    "External source code reuse blocked",
    "Adapter output generation blocked",
    "No adapter output generation is made here",
    "No WebSerial or device write is implemented here",
    "No runtime-loaded config is implemented here",
    "No nunchuk hardware validation claim is made here",
)


class AdapterPrewriteBlockerMatrixError(AssertionError):
    """Raised when the adapter/prewrite blocker matrix drifts."""


def fail(message: str) -> None:
    raise AdapterPrewriteBlockerMatrixError(message)


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


def validate_source_packets(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    packets = payload.get("source_packets")
    if not isinstance(packets, dict):
        fail("source_packets must be an object")
    missing = sorted(REQUIRED_SOURCE_PACKETS - set(packets))
    if missing:
        fail("source_packets missing: " + ", ".join(missing))

    loaded: dict[str, dict[str, Any]] = {}
    for packet_id, packet in packets.items():
        if not isinstance(packet, dict):
            fail(f"source_packets.{packet_id} must be an object")
        for field in ("checker_path", "doc_path", "fixture_path", "schema_name", "required_status"):
            if not isinstance(packet.get(field), str) or not packet[field].strip():
                fail(f"source_packets.{packet_id}.{field} must be a non-empty string")
        for field in ("checker_path", "doc_path", "fixture_path"):
            if not (REPO_ROOT / packet[field]).exists():
                fail(f"source_packets.{packet_id}.{field} references missing path: {packet[field]}")
        if packet_id == "roadmap_next_work_index":
            loaded[packet_id] = load_json_object(REPO_ROOT / packet["fixture_path"])
            continue
        source_fixture = load_json_object(REPO_ROOT / packet["fixture_path"])
        if source_fixture.get("schema_name") != packet["schema_name"]:
            fail(f"source_packets.{packet_id}.schema_name does not match source fixture")
        if source_fixture.get("status") != packet["required_status"]:
            fail(f"source_packets.{packet_id}.required_status does not match source fixture")
        loaded[packet_id] = source_fixture
    return loaded


def validate_source_claims(sources: dict[str, dict[str, Any]]) -> None:
    corpus = sources["export_corpus_readiness"]
    if corpus.get("corpus_present") is not True or corpus.get("completion_allowed") is not False:
        fail("export corpus source must record official corpus present but completion disallowed")
    official = corpus.get("official_configurator_corpus")
    if not isinstance(official, dict) or official.get("not_external_remapper") is not True:
        fail("export corpus source must record official corpus as not external remapper")

    registry = sources["configurator_source_registry"]
    if registry.get("external_sources_promoted_to_authority") is not False:
        fail("configurator registry must not promote external sources to authority")

    blocker = sources["offline_remapper_adapter_blocker_escalation"]
    for key in (
        "adapter_implementation_blocked",
        "external_json_generation_blocked",
        "binding_loss_adapter_blocking",
        "socd_drift_adapter_blocking",
    ):
        if blocker.get(key) is not True:
            fail(f"offline adapter blocker escalation must keep {key}=true")
    for key in (
        "adapter_implemented",
        "external_remapper_compatible_json_generated",
        "external_source_promoted_to_authority",
        "official_compatibility_claimed",
        "hardware_validation_claimed",
        "round_trip_safe_for_active_profile",
    ):
        if blocker.get(key) is not False:
            fail(f"offline adapter blocker escalation must keep {key}=false")

    export_loss = sources["offline_remapper_export_loss_gate"]
    if export_loss.get("adapter_implementation_allowed") is not False:
        fail("export loss gate must keep adapter implementation disallowed")
    if export_loss.get("runtime_owned_behavior_represented") is not False:
        fail("export loss gate must keep runtime-owned behavior unrepresented")

    webserial = sources["webserial_transport_blocker"]
    for key in ("webserial_transport_implemented", "device_write_implemented"):
        if webserial.get(key) is not False:
            fail(f"WebSerial blocker must keep {key}=false")

    runtime_storage = sources["runtime_storage_interpreter_blocker"]
    for key in ("runtime_loaded_config_implemented", "storage_implemented", "interpreter_implemented"):
        if runtime_storage.get(key) is not False:
            fail(f"runtime storage blocker must keep {key}=false")

    protobuf = sources["protobuf_config_schema_research_packet"]
    for key in (
        "official_protobuf_schema_authority_present",
        "protobuf_binary_generation_implemented",
        "official_configurator_compatibility_claimed",
        "device_write_implemented",
        "external_source_promoted_to_authority",
    ):
        if protobuf.get(key) is not False:
            fail(f"protobuf source packet must keep {key}=false")

    license_blocker = sources["external_remapper_license_code_reuse_blocker"]
    for key in (
        "license_review_completed",
        "code_reuse_approved",
        "external_code_copied",
        "external_dependency_added",
        "adapter_implemented",
        "external_json_generated",
    ):
        if license_blocker.get(key) is not False:
            fail(f"license/code-reuse blocker must keep {key}=false")


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
        for field in ("source_packet_ids", "prevents"):
            if not isinstance(raw.get(field), list) or not raw[field]:
                fail(f"blocker {blocker_id}.{field} must be a non-empty list")
        if not isinstance(raw.get("required_future_resolution"), str) or not raw["required_future_resolution"].strip():
            fail(f"blocker {blocker_id}.required_future_resolution must be non-empty")
        blockers[blocker_id] = raw
    missing = sorted(REQUIRED_BLOCKERS - set(blockers))
    if missing:
        fail("blockers missing: " + ", ".join(missing))


def validate_forbidden_and_non_claims(payload: dict[str, Any]) -> None:
    forbidden = payload.get("forbidden_actions")
    if not isinstance(forbidden, list):
        fail("forbidden_actions must be a list")
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_ACTIONS - set(forbidden))
    if missing_forbidden:
        fail("forbidden_actions missing: " + ", ".join(missing_forbidden))

    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("non_claims must be an object")
    missing_non_claims = sorted(REQUIRED_FALSE_NON_CLAIMS - set(non_claims))
    if missing_non_claims:
        fail("non_claims missing: " + ", ".join(missing_non_claims))
    for key in sorted(REQUIRED_FALSE_NON_CLAIMS):
        if non_claims.get(key) is not False:
            fail(f"non_claims.{key} must be false")


def validate_doc() -> None:
    if not DOC_PATH.exists():
        fail(f"missing doc: {display(DOC_PATH)}")
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"doc missing required phrase: {phrase}")


def validate_component_checkers(payload: dict[str, Any]) -> None:
    packets = payload["source_packets"]
    for packet_id, packet in packets.items():
        if packet_id == "roadmap_next_work_index":
            continue
        completed = subprocess.run(
            [sys.executable, packet["checker_path"]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            output = "\n".join(
                part
                for part in (completed.stdout.strip(), completed.stderr.strip())
                if part
            )
            fail(f"component checker failed: {packet['checker_path']}: {output}")
        if "status=PASS" not in completed.stdout:
            fail(f"component checker did not report PASS: {packet['checker_path']}")


def main() -> int:
    print("glyph_adapter_prewrite_blocker_matrix")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_top_level(payload)
        sources = validate_source_packets(payload)
        validate_source_claims(sources)
        validate_blockers(payload)
        validate_forbidden_and_non_claims(payload)
        validate_doc()
        validate_component_checkers(payload)
    except (OSError, AdapterPrewriteBlockerMatrixError, ValueError) as exc:
        print("status=FAIL")
        print("matrix_status=adapter_prewrite_blocked")
        print("adapter_implemented=false")
        print("external_json_generated=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("matrix_status=adapter_prewrite_blocked")
    print("blockers=10")
    print("adapter_implemented=false")
    print("external_json_generated=false")
    print("webserial_device_write_allowed=false")
    print("runtime_loaded_config_implemented=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
