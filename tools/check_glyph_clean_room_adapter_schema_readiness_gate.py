#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter schema readiness gate packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_schema_readiness_gate"
REPORT_VERSION = 1
STATUS = "schema_planning_complete_adapter_implementation_blocked"
HARDWARE_STATUS = "not_new_hardware_result"

COMPONENT_PACKETS = {
    "candidate_schema_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_candidate_schema_contract",
        "status": "schema_contract_only_adapter_not_implemented",
        "evidence_role": "schema planning contract for a future clean-room adapter candidate",
    },
    "candidate_schema_validator": {
        "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_validator.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_candidate_schema_validator_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_SCHEMA_PLACEHOLDER_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_candidate_placeholder",
        "status": "placeholder_only_no_adapter_output",
        "evidence_role": "placeholder validator showing no adapter output exists",
    },
    "sidecar_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_sidecar_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_sidecar_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_sidecar_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_sidecar_contract",
        "status": "sidecar_contract_only_adapter_not_implemented",
        "evidence_role": "sidecar requirements proving runtime-owned behavior stays outside external profile JSON",
    },
}

UPSTREAM_PACKET = {
    "checker_path": "tools/check_glyph_offline_remapper_export_loss_gate.py",
    "doc_path": "docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md",
    "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json",
    "schema_name": "glyph_offline_remapper_export_loss_gate",
    "status": "external_remapper_round_trip_not_safe_adapter_blocked",
    "evidence_role": "upstream export-loss gate keeping active profile round-trip unsafe",
}

ALLOWED_NEXT_WORK = [
    "docs/tools-only adapter transform design",
    "negative corpus for future adapter candidate schema",
    "repeated no-device experiment with browser/version recorded",
]

DISALLOWED_WITHOUT_APPROVAL = [
    "adapter implementation",
    "external JSON generation",
    "WebSerial/device write",
    "protobuf binary generation",
    "runtime-loaded config",
    "official compatibility claim",
    "hardware validation",
]

GATE_INTERPRETATION = [
    "schema planning complete",
    "adapter implementation blocked",
    "external JSON generation blocked",
    "active profile round-trip unsafe",
    "sidecar required",
    "runtime-owned behavior not represented by external profile JSON",
]

REQUIRED_DOC_PHRASES = (
    "schema_planning_complete_adapter_implementation_blocked",
    "schema planning complete",
    "adapter implementation blocked",
    "external json generation blocked",
    "active profile round-trip unsafe",
    "sidecar required",
    "runtime-owned behavior not represented by external profile json",
    "docs/tools-only adapter transform design",
    "negative corpus for future adapter candidate schema",
    "repeated no-device experiment with browser/version recorded",
    "adapter implementation",
    "external json generation",
    "webserial/device write",
    "protobuf binary generation",
    "runtime-loaded config",
    "official compatibility claim",
    "hardware validation",
    "not official compatibility",
    "not hardware validation",
    "no adapter implementation",
    "no external json generation",
    "no webserial/device write",
    "no protobuf binary generation",
    "no runtime-loaded config",
)

FORBIDDEN_FIXTURE_STRINGS = (
    "generated_external_json_path",
    "external_json_output_path",
    "output_path_to_generated_external_json",
    "external-remapper-compatible JSON payload",
)


class CleanRoomAdapterSchemaReadinessGateError(ValueError):
    """Raised when the clean-room adapter schema readiness gate drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterSchemaReadinessGateError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def validate_checker_passes(checker_path: str) -> None:
    completed = subprocess.run(
        [sys.executable, checker_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        output = "\n".join(
            part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
        )
        fail(f"component checker failed: {checker_path}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"component checker did not report PASS: {checker_path}")


def component_packet_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for name, packet in COMPONENT_PACKETS.items():
        checker_path = REPO_ROOT / packet["checker_path"]
        doc_path = REPO_ROOT / packet["doc_path"]
        fixture_path = REPO_ROOT / packet["fixture_path"]
        for path in (checker_path, doc_path, fixture_path):
            if not path.exists():
                fail(f"referenced component path is missing: {display(path)}")

        validate_checker_passes(packet["checker_path"])
        fixture = load_json_object(fixture_path)
        if fixture.get("schema_name") != packet["schema_name"]:
            fail(f"{name} schema_name must be {packet['schema_name']!r}")
        if fixture.get("status") != packet["status"]:
            fail(f"{name} status must be {packet['status']!r}")

        reports[name] = {
            "checker_path": packet["checker_path"],
            "doc_path": packet["doc_path"],
            "doc_sha256": sha256(doc_path),
            "evidence_role": packet["evidence_role"],
            "fixture_path": packet["fixture_path"],
            "fixture_sha256": sha256(fixture_path),
            "schema_name": packet["schema_name"],
            "status": packet["status"],
        }
    return reports


def upstream_packet_report() -> dict[str, Any]:
    checker_path = REPO_ROOT / UPSTREAM_PACKET["checker_path"]
    doc_path = REPO_ROOT / UPSTREAM_PACKET["doc_path"]
    fixture_path = REPO_ROOT / UPSTREAM_PACKET["fixture_path"]
    for path in (checker_path, doc_path, fixture_path):
        if not path.exists():
            fail(f"referenced upstream path is missing: {display(path)}")

    fixture = load_json_object(fixture_path)
    if fixture.get("schema_name") != UPSTREAM_PACKET["schema_name"]:
        fail(f"upstream schema_name must be {UPSTREAM_PACKET['schema_name']!r}")
    if fixture.get("status") != UPSTREAM_PACKET["status"]:
        fail(f"upstream status must be {UPSTREAM_PACKET['status']!r}")
    if fixture.get("hardware_status") != HARDWARE_STATUS:
        fail(f"upstream hardware_status must be {HARDWARE_STATUS!r}")

    expected_flags = {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_allowed": False,
        "external_json_generation_allowed": False,
        "runtime_owned_behavior_represented": False,
    }
    for key, value in expected_flags.items():
        if fixture.get(key) != value:
            fail(f"upstream export-loss gate {key} must be {value!r}")

    return {
        "checker_path": UPSTREAM_PACKET["checker_path"],
        "doc_path": UPSTREAM_PACKET["doc_path"],
        "doc_sha256": sha256(doc_path),
        "evidence_role": UPSTREAM_PACKET["evidence_role"],
        "fixture_path": UPSTREAM_PACKET["fixture_path"],
        "fixture_sha256": sha256(fixture_path),
        "schema_name": UPSTREAM_PACKET["schema_name"],
        "status": UPSTREAM_PACKET["status"],
    }


def supporting_findings() -> dict[str, Any]:
    contract = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["candidate_schema_contract"]["fixture_path"]
    )
    validator = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["candidate_schema_validator"]["fixture_path"]
    )
    sidecar = load_json_object(REPO_ROOT / COMPONENT_PACKETS["sidecar_contract"]["fixture_path"])
    export_loss_gate = load_json_object(REPO_ROOT / UPSTREAM_PACKET["fixture_path"])

    target_profile_metadata = contract.get("target_profile_metadata")
    if not isinstance(target_profile_metadata, dict):
        fail("candidate schema contract target_profile_metadata must be an object")
    if target_profile_metadata.get("active_profile_round_trip_currently_safe") is not False:
        fail("candidate schema contract must keep active profile round-trip unsafe")
    if target_profile_metadata.get("external_json_generation_allowed") is not False:
        fail("candidate schema contract must keep external JSON generation disallowed")
    if target_profile_metadata.get("adapter_implemented") is not False:
        fail("candidate schema contract must keep adapter_implemented=false")

    runtime_sidecar = contract.get("runtime_owned_behavior_sidecar")
    if not isinstance(runtime_sidecar, dict):
        fail("candidate schema contract runtime_owned_behavior_sidecar must be an object")
    if runtime_sidecar.get("required_for_future_candidate") is not True:
        fail("candidate schema contract must require a sidecar for future candidates")
    if runtime_sidecar.get("runtime_owned_behavior_represented_by_external_profile_json") is not False:
        fail("candidate schema contract must keep runtime-owned behavior out of external profile JSON")

    if validator.get("round_trip_safe") is not False:
        fail("candidate schema validator must keep round_trip_safe=false")
    if validator.get("runtime_owned_behavior_sidecar_required") is not True:
        fail("candidate schema validator must keep runtime_owned_behavior_sidecar_required=true")
    if validator.get("external_json_generated") is not False:
        fail("candidate schema validator must keep external_json_generated=false")

    required_flags = sidecar.get("required_flags")
    if not isinstance(required_flags, dict):
        fail("sidecar contract required_flags must be an object")
    if required_flags.get("sidecar_required") is not True:
        fail("sidecar contract must keep sidecar_required=true")
    if required_flags.get("runtime_owned_behavior_warning_required") is not True:
        fail("sidecar contract must keep runtime_owned_behavior_warning_required=true")
    if required_flags.get("non_round_trip_warning_required") is not True:
        fail("sidecar contract must keep non_round_trip_warning_required=true")

    return {
        "candidate_schema_contract_summary": {
            "active_profile_round_trip_safe": False,
            "adapter_implemented": False,
            "external_json_generation_allowed": False,
            "runtime_owned_behavior_represented_by_external_profile_json": False,
            "sidecar_required_for_future_candidate": True,
            "status": contract["status"],
        },
        "candidate_schema_validator_summary": {
            "external_json_generated": False,
            "placeholder_only": True,
            "round_trip_safe": False,
            "runtime_owned_behavior_sidecar_required": True,
            "status": validator["status"],
        },
        "export_loss_gate_summary": {
            "active_profile_round_trip_safe": export_loss_gate["active_profile_round_trip_safe"],
            "external_json_generation_allowed": export_loss_gate["external_json_generation_allowed"],
            "runtime_owned_behavior_represented": export_loss_gate["runtime_owned_behavior_represented"],
            "status": export_loss_gate["status"],
        },
        "sidecar_contract_summary": {
            "non_round_trip_warning_required": True,
            "runtime_owned_behavior_warning_required": True,
            "sidecar_required": True,
            "status": sidecar["status"],
        },
    }


def build_gate() -> dict[str, Any]:
    return {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_blocked": True,
        "allowed_next_work": ALLOWED_NEXT_WORK,
        "component_packets": {
            **component_packet_reports(),
            "upstream_export_loss_gate": upstream_packet_report(),
        },
        "disallowed_without_approval": DISALLOWED_WITHOUT_APPROVAL,
        "external_json_generation_blocked": True,
        "gate_interpretation": GATE_INTERPRETATION,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "official_compatibility_claimed": False,
        "report_version": REPORT_VERSION,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "schema_name": SCHEMA_NAME,
        "schema_planning_complete": True,
        "sidecar_required": True,
        "status": STATUS,
        "supporting_findings": supporting_findings(),
        "validation_report": {
            "adapter_implementation_blocked": True,
            "checker_path": "tools/check_glyph_clean_room_adapter_schema_readiness_gate.py",
            "component_checkers_required_to_pass": True,
            "doc_path": "docs/calibration/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md",
            "external_json_generation_blocked": True,
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "validation_scope": "docs_tools_fixtures_only",
        },
    }


def validate_gate(gate: dict[str, Any]) -> None:
    expected_flags = {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_blocked": True,
        "external_json_generation_blocked": True,
        "hardware_status": HARDWARE_STATUS,
        "official_compatibility_claimed": False,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "schema_name": SCHEMA_NAME,
        "schema_planning_complete": True,
        "sidecar_required": True,
        "status": STATUS,
    }
    for key, value in expected_flags.items():
        if gate.get(key) != value:
            fail(f"{key} must be {value!r}")

    if gate.get("allowed_next_work") != ALLOWED_NEXT_WORK:
        fail("allowed_next_work drifted")
    if gate.get("disallowed_without_approval") != DISALLOWED_WITHOUT_APPROVAL:
        fail("disallowed_without_approval drifted")
    if gate.get("gate_interpretation") != GATE_INTERPRETATION:
        fail("gate_interpretation drifted")


def validate_fixture(gate: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(gate)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated readiness gate JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != gate:
        fail("committed fixture JSON object drifted from regenerated readiness gate")

    lowered = committed_text.lower()
    for forbidden in FORBIDDEN_FIXTURE_STRINGS:
        if forbidden.lower() in lowered:
            fail(f"fixture must not contain generated external JSON output field: {forbidden}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the docs/tools-only Glyph clean-room adapter schema readiness gate."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of the concise validation summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        gate = build_gate()
        if args.json:
            print(canonical_json_text(gate), end="")
            return 0
        validate_gate(gate)
        validate_fixture(gate)
        validate_doc()
    except (OSError, CleanRoomAdapterSchemaReadinessGateError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("adapter_implementation_blocked=true")
        print("external_json_generation_blocked=true")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("adapter_implementation_blocked=true")
    print("external_json_generation_blocked=true")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
