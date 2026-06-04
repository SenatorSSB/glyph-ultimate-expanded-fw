#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter transform rule matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_transform_rule_matrix"
MATRIX_VERSION = 1
STATUS = "transform_rule_matrix_only"
HARDWARE_STATUS = "not_new_hardware_result"
ALLOWED_DISPOSITIONS = [
    "candidate_direct_profile_field",
    "sidecar_only",
    "blocked_requires_source_authority",
    "blocked_round_trip_unsafe",
    "out_of_scope",
]

SOURCE_PACKETS = {
    "mapping_plan": {
        "checker_path": "tools/check_glyph_offline_remapper_adapter_mapping_plan.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json",
        "evidence_role": "source for direct-candidate and manual-review category boundaries",
    },
    "gap_matrix": {
        "checker_path": "tools/check_glyph_offline_remapper_adapter_gap_matrix.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.json",
        "evidence_role": "source for blocked round-trip categories such as RGB shared-index behavior",
    },
    "transform_design_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_design_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_design_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_contract_2026-06-04.json",
        "evidence_role": "source for transform-planning-only, sidecar-required, and forbidden-output boundaries",
    },
    "sidecar_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_sidecar_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_sidecar_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_sidecar_contract_2026-06-04.json",
        "evidence_role": "source for runtime-owned behavior, loss warnings, and validation report staying sidecar-only",
    },
    "storage_transport_source_authority_registry": {
        "checker_path": "tools/check_glyph_storage_transport_source_authority_registry.py",
        "doc_path": "docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_storage_transport_source_authority_registry_2026-06-03.json",
        "evidence_role": "source for source-authority caveats staying explicit and non-transport",
    },
    "protobuf_config_schema_research_packet": {
        "checker_path": "tools/check_glyph_protobuf_config_schema_research_packet.py",
        "doc_path": "docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json",
        "evidence_role": "source for protobuf payload staying outside transform-rule scope",
    },
    "webserial_transport_blocker_packet": {
        "checker_path": "tools/check_glyph_webserial_transport_blocker_packet.py",
        "doc_path": "docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json",
        "evidence_role": "source for WebSerial/device write fields staying out of scope",
    },
    "runtime_storage_interpreter_blocker_packet": {
        "checker_path": "tools/check_glyph_runtime_storage_interpreter_blocker_packet.py",
        "doc_path": "docs/calibration/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.md",
        "fixture_path": "docs/calibration/fixtures/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.json",
        "evidence_role": "source for runtime-loaded config staying blocked and out of scope",
    },
}

EXPECTED_RULES = [
    {
        "category": "profile name/identity metadata",
        "disposition": "blocked_requires_source_authority",
        "evidence_keys": ["mapping_plan"],
        "planning_note": "Top-level profile identity/name derivation is still blocked pending reviewed source authority for a future clean-room candidate.",
    },
    {
        "category": "mode/backend metadata",
        "disposition": "candidate_direct_profile_field",
        "evidence_keys": ["mapping_plan"],
        "planning_note": "Committed profile JSON already carries mode IDs, mode names, applicable backends, and backend defaults.",
    },
    {
        "category": "profile-level button remapping",
        "disposition": "candidate_direct_profile_field",
        "evidence_keys": ["mapping_plan"],
        "planning_note": "Committed profile JSON already carries list-shaped button remapping entries keyed by physicalButton.",
    },
    {
        "category": "activates-bearing bindings",
        "disposition": "blocked_round_trip_unsafe",
        "evidence_keys": ["transform_design_contract"],
        "planning_note": "Exported profile JSON stripped activates-bearing bindings, so active profile round-trip remains unsafe.",
    },
    {
        "category": "disabled/visibility entries",
        "disposition": "blocked_round_trip_unsafe",
        "evidence_keys": ["mapping_plan"],
        "planning_note": "Explicit disable serialization still needs review and must not be treated as round-trip safe transform output.",
    },
    {
        "category": "SOCD policy",
        "disposition": "sidecar_only",
        "evidence_keys": ["transform_design_contract", "sidecar_contract"],
        "planning_note": "SOCD drift remains warning/sidecar scope instead of a direct clean-room profile-field claim.",
    },
    {
        "category": "RGB metadata",
        "disposition": "blocked_round_trip_unsafe",
        "evidence_keys": ["gap_matrix"],
        "planning_note": "RGB shared-index behavior remains review-only, so RGB metadata stays blocked from round-trip-safe transform treatment.",
    },
    {
        "category": "menu icon metadata",
        "disposition": "blocked_requires_source_authority",
        "evidence_keys": ["mapping_plan"],
        "planning_note": "Menu icon and display wiring are not source-audited as stable clean-room target authority.",
    },
    {
        "category": "keyboard mode metadata",
        "disposition": "candidate_direct_profile_field",
        "evidence_keys": ["mapping_plan"],
        "planning_note": "Committed profile JSON exposes keyboard mode references and button-to-keycode mappings directly.",
    },
    {
        "category": "runtime-owned behavior",
        "disposition": "sidecar_only",
        "evidence_keys": ["transform_design_contract", "sidecar_contract"],
        "planning_note": "Runtime-owned behavior remains outside external profile JSON and must stay in sidecar/report scope.",
    },
    {
        "category": "validation report",
        "disposition": "sidecar_only",
        "evidence_keys": ["mapping_plan", "sidecar_contract"],
        "planning_note": "Validation report content belongs in sidecar/report scope, not a transformed profile payload.",
    },
    {
        "category": "source-authority caveats",
        "disposition": "sidecar_only",
        "evidence_keys": [
            "mapping_plan",
            "sidecar_contract",
            "storage_transport_source_authority_registry"
        ],
        "planning_note": "Source-authority caveats belong in sidecar/report scope so authority boundaries stay explicit.",
    },
    {
        "category": "loss warnings",
        "disposition": "sidecar_only",
        "evidence_keys": ["transform_design_contract", "sidecar_contract"],
        "planning_note": "Binding-loss and SOCD-drift warnings belong in sidecar/report scope before any future transform review.",
    },
    {
        "category": "external JSON output path",
        "disposition": "out_of_scope",
        "evidence_keys": ["transform_design_contract"],
        "planning_note": "No generated external JSON output path exists on this branch, and transform planning does not add one.",
    },
    {
        "category": "WebSerial/device write fields",
        "disposition": "out_of_scope",
        "evidence_keys": ["webserial_transport_blocker_packet"],
        "planning_note": "Transport/write fields remain out of scope for this planning-only matrix.",
    },
    {
        "category": "protobuf binary payload",
        "disposition": "out_of_scope",
        "evidence_keys": ["protobuf_config_schema_research_packet"],
        "planning_note": "Protobuf binary generation is blocked and is not part of transform-rule planning.",
    },
    {
        "category": "runtime-loaded config payload",
        "disposition": "out_of_scope",
        "evidence_keys": ["runtime_storage_interpreter_blocker_packet"],
        "planning_note": "Runtime-loaded config remains blocked and is not part of transform-rule planning.",
    }
]

REQUIRED_DOC_PHRASES = (
    "transform_rule_matrix_only",
    "Transform implementation does not exist.",
    "External JSON generation does not exist.",
    "The rules are planning-only and do not implement transform code.",
    "Runtime-owned behavior remains sidecar-only.",
    "No device write/WebSerial/protobuf/runtime-loaded config.",
    "This packet is not official configurator compatibility and not hardware validation.",
    "candidate_direct_profile_field",
    "sidecar_only",
    "blocked_requires_source_authority",
    "blocked_round_trip_unsafe",
    "out_of_scope",
    "profile name/identity metadata",
    "mode/backend metadata",
    "profile-level button remapping",
    "activates-bearing bindings",
    "disabled/visibility entries",
    "SOCD policy",
    "RGB metadata",
    "menu icon metadata",
    "keyboard mode metadata",
    "runtime-owned behavior",
    "validation report",
    "source-authority caveats",
    "loss warnings",
    "external JSON output path",
    "WebSerial/device write fields",
    "protobuf binary payload",
    "runtime-loaded config payload",
    "not official configurator compatibility",
    "not hardware validation"
)


class TransformRuleMatrixError(ValueError):
    """Raised when the transform rule matrix drifts."""


def fail(message: str) -> None:
    raise TransformRuleMatrixError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path} must contain a JSON object")
    return payload


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
        fail(f"source checker failed: {checker_path}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"source checker did not report PASS: {checker_path}")


def resolved_source_packets() -> dict[str, dict[str, Any]]:
    packets: dict[str, dict[str, Any]] = {}
    for key, packet in SOURCE_PACKETS.items():
        for relpath_key in ("checker_path", "doc_path", "fixture_path"):
            if not (REPO_ROOT / packet[relpath_key]).exists():
                fail(f"required source path missing: {packet[relpath_key]}")
        validate_checker_passes(packet["checker_path"])
        packets[key] = {
            "checker_path": packet["checker_path"],
            "doc_path": packet["doc_path"],
            "evidence_role": packet["evidence_role"],
            "fixture_path": packet["fixture_path"],
        }
    return packets


def build_matrix() -> dict[str, Any]:
    return {
        "allowed_dispositions": ALLOWED_DISPOSITIONS,
        "external_json_generated": False,
        "hardware_status": HARDWARE_STATUS,
        "matrix_version": MATRIX_VERSION,
        "rules": EXPECTED_RULES,
        "schema_name": SCHEMA_NAME,
        "source_packets": resolved_source_packets(),
        "status": STATUS,
        "transform_implemented": False,
        "validation_report": {
            "checker_path": "tools/check_glyph_clean_room_adapter_transform_rule_matrix.py",
            "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.md",
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.json",
            "source_checkers_required_to_pass": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
    }


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    missing = [phrase for phrase in REQUIRED_DOC_PHRASES if phrase not in text]
    if missing:
        fail("doc is missing required phrases: " + ", ".join(missing))


def validate_fixture(matrix: dict[str, Any]) -> None:
    fixture = load_json_object(FIXTURE_PATH)
    if fixture != matrix:
        fail("fixture JSON object drifted from the expected transform rule matrix")
    if fixture.get("schema_name") != SCHEMA_NAME:
        fail(f"schema_name must be {SCHEMA_NAME!r}")
    if fixture.get("matrix_version") != MATRIX_VERSION:
        fail(f"matrix_version must be {MATRIX_VERSION}")
    if fixture.get("status") != STATUS:
        fail(f"status must be {STATUS!r}")
    if fixture.get("transform_implemented") is not False:
        fail("transform_implemented must remain false")
    if fixture.get("external_json_generated") is not False:
        fail("external_json_generated must remain false")
    if fixture.get("hardware_status") != HARDWARE_STATUS:
        fail(f"hardware_status must be {HARDWARE_STATUS!r}")

    rules = fixture.get("rules")
    if not isinstance(rules, list):
        fail("rules must be a list")
    if len(rules) != len(EXPECTED_RULES):
        fail(f"rules must contain {len(EXPECTED_RULES)} entries")

    by_category = {rule["category"]: rule for rule in rules}
    required_dispositions = {
        "runtime-owned behavior": "sidecar_only",
        "validation report": "sidecar_only",
        "source-authority caveats": "sidecar_only",
        "loss warnings": "sidecar_only",
        "activates-bearing bindings": "blocked_round_trip_unsafe",
        "SOCD policy": "sidecar_only",
        "external JSON output path": "out_of_scope",
        "WebSerial/device write fields": "out_of_scope",
        "protobuf binary payload": "out_of_scope",
        "runtime-loaded config payload": "out_of_scope",
    }
    for category, disposition in required_dispositions.items():
        if by_category.get(category, {}).get("disposition") != disposition:
            fail(f"{category!r} must keep disposition {disposition!r}")

    for rule in rules:
        if rule.get("disposition") not in ALLOWED_DISPOSITIONS:
            fail(f"rule has unsupported disposition: {rule}")


def print_summary(status: str) -> None:
    print(SCHEMA_NAME)
    print(f"status={status}")
    print(f"rules={len(EXPECTED_RULES)}")
    print("transform_implemented=false")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")


def main() -> int:
    try:
        validate_doc()
        matrix = build_matrix()
        validate_fixture(matrix)
    except TransformRuleMatrixError as exc:
        print_summary("FAIL")
        print(f"reason={exc}")
        return 1

    print_summary("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
