#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter transform design gate packet."""

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
    / "docs/calibration/glyph_clean_room_adapter_transform_design_gate_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_gate_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_transform_design_gate"
REPORT_VERSION = 1
STATUS = "transform_design_ready_implementation_blocked"
HARDWARE_STATUS = "not_new_hardware_result"

COMPONENT_PACKETS = {
    "transform_design_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_design_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_design_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_transform_design_contract",
        "status": "transform_design_contract_only",
        "evidence_role": "source for the transform design contract boundary",
    },
    "transform_rule_matrix": {
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_rule_matrix.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_transform_rule_matrix",
        "status": "transform_rule_matrix_only",
        "evidence_role": "source for profile-field, sidecar-only, and out-of-scope transform rules",
    },
    "transform_decision_matrix": {
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_decision_matrix.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_transform_decision_matrix",
        "status": "decision_matrix_only_implementation_blocked",
        "evidence_role": "source for unresolved or blocked implementation decisions",
    },
    "schema_readiness_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_schema_readiness_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_schema_readiness_gate",
        "status": "schema_planning_complete_adapter_implementation_blocked",
        "evidence_role": "source for schema readiness and sidecar requirements",
    },
    "negative_corpus_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_negative_corpus_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_negative_corpus_gate",
        "status": "negative_corpus_ready_adapter_implementation_blocked",
        "evidence_role": "source for negative corpus readiness and unsafe-claim rejection coverage",
    },
}

ALLOWED_NEXT_WORK = [
    "repeated no-device experiment with browser/version recorded",
    "source audit plan for external remapper import/export behavior",
    "future implementation proposal requiring user approval",
]

DISALLOWED_WITHOUT_APPROVAL = [
    "transform implementation",
    "adapter implementation",
    "external JSON generation",
    "WebSerial/device write",
    "protobuf binary generation",
    "runtime-loaded config",
    "official compatibility claim",
    "hardware validation",
]

GATE_INTERPRETATION = [
    "transform design ready",
    "transform implementation blocked",
    "external JSON generation blocked",
    "active profile round-trip unsafe",
    "sidecar required",
    "runtime-owned behavior not represented by external profile JSON",
    "implementation decisions not approved",
    "no device/protobuf/runtime-loaded behavior",
]

REQUIRED_DOC_PHRASES = (
    "transform_design_ready_implementation_blocked",
    "transform design ready",
    "transform implementation blocked",
    "external json generation blocked",
    "active profile round-trip unsafe",
    "sidecar required",
    "runtime-owned behavior not represented by external profile json",
    "implementation decisions not approved",
    "no device/protobuf/runtime-loaded behavior",
    "repeated no-device experiment with browser/version recorded",
    "source audit plan for external remapper import/export behavior",
    "future implementation proposal requiring user approval",
    "transform implementation",
    "adapter implementation",
    "external json generation",
    "webserial/device write",
    "protobuf binary generation",
    "runtime-loaded config",
    "official compatibility claim",
    "hardware validation",
    "no device/protobuf/runtime-loaded behavior",
    "not official compatibility",
    "not hardware validation",
)

FORBIDDEN_FIXTURE_STRINGS = (
    "generated_external_json_path",
    "external_json_output_path",
    "output_path_to_generated_external_json",
    "external-remapper-compatible JSON payload",
)


class CleanRoomAdapterTransformDesignGateError(ValueError):
    """Raised when the clean-room adapter transform design gate drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterTransformDesignGateError(message)


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
        if fixture.get("hardware_status") != HARDWARE_STATUS:
            fail(f"{name} hardware_status must be {HARDWARE_STATUS!r}")

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


def supporting_findings() -> dict[str, Any]:
    contract = load_json_object(REPO_ROOT / COMPONENT_PACKETS["transform_design_contract"]["fixture_path"])
    rule_matrix = load_json_object(REPO_ROOT / COMPONENT_PACKETS["transform_rule_matrix"]["fixture_path"])
    decision_matrix = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["transform_decision_matrix"]["fixture_path"]
    )
    schema_gate = load_json_object(REPO_ROOT / COMPONENT_PACKETS["schema_readiness_gate"]["fixture_path"])
    negative_gate = load_json_object(REPO_ROOT / COMPONENT_PACKETS["negative_corpus_gate"]["fixture_path"])

    if contract.get("transform_implemented") is not False:
        fail("transform design contract must keep transform_implemented=false")
    if contract.get("external_json_generated") is not False:
        fail("transform design contract must keep external_json_generated=false")
    if contract.get("active_profile_round_trip_safe") is not False:
        fail("transform design contract must keep active_profile_round_trip_safe=false")
    if contract.get("sidecar_required") is not True:
        fail("transform design contract must keep sidecar_required=true")
    if contract.get("runtime_owned_behavior_represented_by_external_profile_json") is not False:
        fail(
            "transform design contract must keep runtime_owned_behavior_represented_by_external_profile_json=false"
        )

    rules = rule_matrix.get("rules")
    if not isinstance(rules, list) or not rules:
        fail("transform rule matrix rules must be a non-empty list")
    dispositions = {entry.get("disposition") for entry in rules if isinstance(entry, dict)}
    if "candidate_direct_profile_field" not in dispositions:
        fail("transform rule matrix must include candidate_direct_profile_field")
    if "sidecar_only" not in dispositions:
        fail("transform rule matrix must include sidecar_only")
    if rule_matrix.get("transform_implemented") is not False:
        fail("transform rule matrix must keep transform_implemented=false")
    if rule_matrix.get("external_json_generated") is not False:
        fail("transform rule matrix must keep external_json_generated=false")

    decisions = decision_matrix.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        fail("transform decision matrix decisions must be a non-empty list")
    decision_statuses = {entry.get("status") for entry in decisions if isinstance(entry, dict)}
    if decision_statuses - {"blocked", "unresolved"}:
        fail("transform decision matrix decisions must remain blocked or unresolved")
    if decision_matrix.get("implementation_decisions_approved") is not False:
        fail("transform decision matrix must keep implementation_decisions_approved=false")
    if decision_matrix.get("adapter_implementation_allowed") is not False:
        fail("transform decision matrix must keep adapter_implementation_allowed=false")
    if decision_matrix.get("external_json_generation_allowed") is not False:
        fail("transform decision matrix must keep external_json_generation_allowed=false")

    if schema_gate.get("schema_planning_complete") is not True:
        fail("schema readiness gate must keep schema_planning_complete=true")
    if schema_gate.get("adapter_implementation_blocked") is not True:
        fail("schema readiness gate must keep adapter_implementation_blocked=true")
    if schema_gate.get("external_json_generation_blocked") is not True:
        fail("schema readiness gate must keep external_json_generation_blocked=true")
    if schema_gate.get("sidecar_required") is not True:
        fail("schema readiness gate must keep sidecar_required=true")

    if negative_gate.get("negative_corpus_ready") is not True:
        fail("negative corpus gate must keep negative_corpus_ready=true")
    if negative_gate.get("adapter_implementation_blocked") is not True:
        fail("negative corpus gate must keep adapter_implementation_blocked=true")
    if negative_gate.get("external_json_generation_blocked") is not True:
        fail("negative corpus gate must keep external_json_generation_blocked=true")
    if negative_gate.get("sidecar_required") is not True:
        fail("negative corpus gate must keep sidecar_required=true")

    return {
        "transform_design_contract_summary": {
            "active_profile_round_trip_safe": False,
            "external_json_generated": False,
            "sidecar_required": True,
            "status": contract["status"],
            "transform_implemented": False,
        },
        "transform_rule_matrix_summary": {
            "external_json_generated": False,
            "rule_count": len(rules),
            "sidecar_only_rules_present": True,
            "status": rule_matrix["status"],
            "transform_implemented": False,
        },
        "transform_decision_matrix_summary": {
            "adapter_implementation_allowed": False,
            "external_json_generation_allowed": False,
            "implementation_decisions_approved": False,
            "decision_count": len(decisions),
            "status": decision_matrix["status"],
        },
        "schema_readiness_gate_summary": {
            "adapter_implementation_blocked": True,
            "external_json_generation_blocked": True,
            "schema_planning_complete": True,
            "sidecar_required": True,
            "status": schema_gate["status"],
        },
        "negative_corpus_gate_summary": {
            "adapter_implementation_blocked": True,
            "external_json_generation_blocked": True,
            "negative_corpus_ready": True,
            "sidecar_required": True,
            "status": negative_gate["status"],
        },
    }


def build_gate() -> dict[str, Any]:
    return {
        "active_profile_round_trip_safe": False,
        "allowed_next_work": ALLOWED_NEXT_WORK,
        "component_packets": component_packet_reports(),
        "disallowed_without_approval": DISALLOWED_WITHOUT_APPROVAL,
        "external_json_generation_blocked": True,
        "external_json_generated": False,
        "gate_interpretation": GATE_INTERPRETATION,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "implementation_decisions_approved": False,
        "official_compatibility_claimed": False,
        "report_version": REPORT_VERSION,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "schema_name": SCHEMA_NAME,
        "sidecar_required": True,
        "status": STATUS,
        "supporting_findings": supporting_findings(),
        "transform_design_ready": True,
        "transform_implementation_blocked": True,
        "validation_report": {
            "checker_path": "tools/check_glyph_clean_room_adapter_transform_design_gate.py",
            "component_checkers_required_to_pass": True,
            "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_design_gate_2026-06-04.md",
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_gate_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "transform_design_ready": True,
            "transform_implementation_blocked": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
    }


def validate_gate(gate: dict[str, Any]) -> None:
    expected_flags = {
        "active_profile_round_trip_safe": False,
        "external_json_generation_blocked": True,
        "external_json_generated": False,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "implementation_decisions_approved": False,
        "official_compatibility_claimed": False,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "schema_name": SCHEMA_NAME,
        "sidecar_required": True,
        "status": STATUS,
        "transform_design_ready": True,
        "transform_implementation_blocked": True,
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
        fail("committed fixture does not exactly match regenerated transform design gate JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != gate:
        fail("committed fixture JSON object drifted from regenerated transform design gate")

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
        description="Validate the docs/tools-only Glyph clean-room adapter transform design gate."
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
    except (OSError, CleanRoomAdapterTransformDesignGateError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("transform_design_ready=true")
        print("transform_implementation_blocked=true")
        print("external_json_generation_blocked=true")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("transform_design_ready=true")
    print("transform_implementation_blocked=true")
    print("external_json_generation_blocked=true")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
