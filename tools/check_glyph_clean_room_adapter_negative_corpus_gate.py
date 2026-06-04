#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter negative corpus readiness gate packet."""

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
    / "docs/calibration/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_negative_corpus_gate"
REPORT_VERSION = 1
STATUS = "negative_corpus_ready_adapter_implementation_blocked"
HARDWARE_STATUS = "not_new_hardware_result"

COMPONENT_PACKETS = {
    "schema_readiness_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_schema_readiness_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_schema_readiness_gate",
        "status": "schema_planning_complete_adapter_implementation_blocked",
        "evidence_role": "schema readiness gate proving planning is complete while implementation stays blocked",
    },
    "negative_corpus_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_negative_corpus_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_negative_corpus_contract",
        "status": "negative_corpus_contract_only",
        "evidence_role": "negative corpus contract defining unsafe claims and required rejections",
    },
    "invalid_corpus_fixture": {
        "checker_path": "tools/check_glyph_clean_room_adapter_invalid_corpus_fixture.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_invalid_corpus_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_invalid_corpus_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_invalid_corpus",
        "status": "docs_tools_invalid_corpus",
        "evidence_role": "invalid corpus fixture covering every negative contract category",
    },
    "invalid_corpus_checker": {
        "checker_path": "tools/check_glyph_clean_room_adapter_invalid_corpus.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_invalid_corpus_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_invalid_corpus_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_invalid_corpus",
        "status": "docs_tools_invalid_corpus",
        "evidence_role": "planning-only invalid corpus checker guarding against unsafe candidate interpretation",
    },
}

ALLOWED_NEXT_WORK = [
    "docs/tools-only adapter transform design",
    "future validator mutation engine after a candidate schema exists",
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
    "negative corpus ready",
    "schema planning complete",
    "adapter implementation blocked",
    "external JSON generation blocked",
    "invalid cases cover unsafe claims and missing sidecars",
    "active profile round-trip unsafe",
    "sidecar required",
    "runtime-owned behavior not represented by external profile JSON",
]

REQUIRED_DOC_PHRASES = (
    "negative_corpus_ready_adapter_implementation_blocked",
    "negative corpus ready",
    "schema planning complete",
    "adapter implementation blocked",
    "external json generation blocked",
    "invalid cases cover unsafe claims and missing sidecars",
    "active profile round-trip unsafe",
    "sidecar required",
    "runtime-owned behavior not represented by external profile json",
    "docs/tools-only adapter transform design",
    "future validator mutation engine after a candidate schema exists",
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


class CleanRoomAdapterNegativeCorpusGateError(ValueError):
    """Raised when the clean-room adapter negative corpus gate drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterNegativeCorpusGateError(message)


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


def supporting_findings() -> dict[str, Any]:
    schema_gate = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["schema_readiness_gate"]["fixture_path"]
    )
    negative_contract = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["negative_corpus_contract"]["fixture_path"]
    )
    invalid_corpus = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["invalid_corpus_fixture"]["fixture_path"]
    )

    if schema_gate.get("schema_planning_complete") is not True:
        fail("schema readiness gate must keep schema_planning_complete=true")
    if schema_gate.get("adapter_implementation_blocked") is not True:
        fail("schema readiness gate must keep adapter_implementation_blocked=true")
    if schema_gate.get("external_json_generation_blocked") is not True:
        fail("schema readiness gate must keep external_json_generation_blocked=true")
    if schema_gate.get("sidecar_required") is not True:
        fail("schema readiness gate must keep sidecar_required=true")
    if schema_gate.get("runtime_owned_behavior_represented_by_external_profile_json") is not False:
        fail(
            "schema readiness gate must keep runtime_owned_behavior_represented_by_external_profile_json=false"
        )

    contract_scope = negative_contract.get("contract_scope")
    if not isinstance(contract_scope, dict):
        fail("negative corpus contract contract_scope must be an object")
    if contract_scope.get("corpus_rejects_unsafe_candidate_payloads") is not True:
        fail("negative corpus contract must reject unsafe candidate payloads")
    if contract_scope.get("adapter_output_exists") is not False:
        fail("negative corpus contract must keep adapter_output_exists=false")
    if contract_scope.get("external_json_generation_exists") is not False:
        fail("negative corpus contract must keep external_json_generation_exists=false")

    negative_rules = negative_contract.get("negative_corpus_rules")
    if not isinstance(negative_rules, dict):
        fail("negative corpus contract negative_corpus_rules must be an object")
    if negative_rules.get("sidecar_required") is not True:
        fail("negative corpus contract must keep sidecar_required=true")
    if (
        negative_rules.get(
            "runtime_owned_behavior_must_not_be_represented_directly_by_external_profile_json"
        )
        is not True
    ):
        fail("negative corpus contract must keep runtime-owned behavior out of external profile JSON")

    invalid_cases = invalid_corpus.get("cases")
    if not isinstance(invalid_cases, list) or not invalid_cases:
        fail("invalid corpus fixture cases must be a non-empty list")

    categories = {entry.get("category") for entry in invalid_cases if isinstance(entry, dict)}
    if "missing_sidecar" not in categories:
        fail("invalid corpus fixture must cover missing_sidecar")
    unsafe_claim_categories = {
        "claims_round_trip_safe",
        "claims_active_profile_round_trip_safe",
        "claims_runtime_owned_behavior_represented_by_external_profile_json",
        "official_compatibility_claimed",
        "hardware_validation_claimed",
        "external_source_promoted_to_authority",
    }
    if not unsafe_claim_categories.issubset(categories):
        missing = sorted(unsafe_claim_categories - categories)
        fail(f"invalid corpus fixture missing unsafe-claim categories: {missing}")

    return {
        "invalid_corpus_summary": {
            "case_count": len(invalid_cases),
            "covers_missing_sidecar": True,
            "covers_unsafe_claim_categories": True,
            "must_fail_all_cases": True,
            "status": invalid_corpus["status"],
        },
        "negative_corpus_contract_summary": {
            "adapter_output_exists": False,
            "external_json_generation_exists": False,
            "rejects_unsafe_candidate_payloads": True,
            "runtime_owned_behavior_represented_by_external_profile_json": False,
            "sidecar_required": True,
            "status": negative_contract["status"],
        },
        "schema_readiness_gate_summary": {
            "adapter_implementation_blocked": True,
            "external_json_generation_blocked": True,
            "schema_planning_complete": True,
            "sidecar_required": True,
            "status": schema_gate["status"],
        },
    }


def build_gate() -> dict[str, Any]:
    return {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_blocked": True,
        "adapter_implemented": False,
        "allowed_next_work": ALLOWED_NEXT_WORK,
        "component_packets": component_packet_reports(),
        "disallowed_without_approval": DISALLOWED_WITHOUT_APPROVAL,
        "external_json_generation_blocked": True,
        "external_json_generated": False,
        "gate_interpretation": GATE_INTERPRETATION,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "negative_corpus_ready": True,
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
            "checker_path": "tools/check_glyph_clean_room_adapter_negative_corpus_gate.py",
            "component_checkers_required_to_pass": True,
            "doc_path": "docs/calibration/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.md",
            "external_json_generation_blocked": True,
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "negative_corpus_ready": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
    }


def validate_gate(gate: dict[str, Any]) -> None:
    expected_flags = {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_blocked": True,
        "adapter_implemented": False,
        "external_json_generation_blocked": True,
        "external_json_generated": False,
        "hardware_status": HARDWARE_STATUS,
        "negative_corpus_ready": True,
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
        fail("committed fixture does not exactly match regenerated negative corpus gate JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != gate:
        fail("committed fixture JSON object drifted from regenerated negative corpus gate")

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
        description="Validate the docs/tools-only Glyph clean-room adapter negative corpus readiness gate."
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
    except (OSError, CleanRoomAdapterNegativeCorpusGateError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("negative_corpus_ready=true")
        print("adapter_implementation_blocked=true")
        print("external_json_generation_blocked=true")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("negative_corpus_ready=true")
    print("adapter_implementation_blocked=true")
    print("external_json_generation_blocked=true")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
