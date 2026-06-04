#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter negative corpus contract packet."""

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
    / "docs/calibration/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_negative_corpus_contract"
SCHEMA_VERSION = 1
STATUS = "negative_corpus_contract_only"
TARGET = "future clean-room adapter candidate schema"
HARDWARE_STATUS = "not_new_hardware_result"

UPSTREAM_PACKETS = {
    "candidate_schema_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_candidate_schema_contract",
        "status": "schema_contract_only_adapter_not_implemented",
    },
    "candidate_schema_validator": {
        "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_validator.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_candidate_schema_validator_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_SCHEMA_PLACEHOLDER_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_candidate_placeholder",
        "status": "placeholder_only_no_adapter_output",
    },
    "sidecar_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_sidecar_contract.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_sidecar_contract_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_sidecar_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_sidecar_contract",
        "status": "sidecar_contract_only_adapter_not_implemented",
    },
    "schema_readiness_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_schema_readiness_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_schema_readiness_gate",
        "status": "schema_planning_complete_adapter_implementation_blocked",
    },
    "export_loss_gate": {
        "checker_path": "tools/check_glyph_offline_remapper_export_loss_gate.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_export_loss_gate",
        "status": "external_remapper_round_trip_not_safe_adapter_blocked",
    },
}

INVALID_CASE_CATEGORIES = [
    {
        "category": "missing_sidecar",
        "required_rejection": "sidecar is required",
    },
    {
        "category": "missing_runtime_owned_behavior_warning",
        "required_rejection": "runtime-owned behavior warning is required",
    },
    {
        "category": "missing_non_round_trip_warning",
        "required_rejection": "non-round-trip warning is required",
    },
    {
        "category": "claims_round_trip_safe",
        "required_rejection": "future candidate must not claim round-trip safe",
    },
    {
        "category": "claims_active_profile_round_trip_safe",
        "required_rejection": "active profile round-trip remains unsafe",
    },
    {
        "category": "claims_runtime_owned_behavior_represented_by_external_profile_json",
        "required_rejection": "runtime-owned behavior must not be represented directly by external profile JSON",
    },
    {
        "category": "adapter_implemented",
        "required_rejection": "no adapter output exists",
    },
    {
        "category": "external_json_generated",
        "required_rejection": "no external JSON generation exists",
    },
    {
        "category": "generated_external_json_output_path_present",
        "required_rejection": "generated external JSON output path present",
    },
    {
        "category": "device_write_allowed",
        "required_rejection": "device write allowed",
    },
    {
        "category": "webserial_allowed",
        "required_rejection": "WebSerial allowed",
    },
    {
        "category": "protobuf_binary_generation_allowed",
        "required_rejection": "protobuf binary generation allowed",
    },
    {
        "category": "runtime_loaded_config_allowed",
        "required_rejection": "runtime-loaded config allowed",
    },
    {
        "category": "official_compatibility_claimed",
        "required_rejection": "official compatibility claimed",
    },
    {
        "category": "hardware_validation_claimed",
        "required_rejection": "hardware validation claimed",
    },
    {
        "category": "external_source_promoted_to_authority",
        "required_rejection": "external source promoted to authority",
    },
    {
        "category": "copied_external_source_code",
        "required_rejection": "copied external source code",
    },
    {
        "category": "external_dependency_added",
        "required_rejection": "external dependency added",
    },
    {
        "category": "missing_source_authority_classification",
        "required_rejection": "source-authority classification is required",
    },
    {
        "category": "missing_validation_report",
        "required_rejection": "validation report is required",
    },
    {
        "category": "missing_loss_warnings",
        "required_rejection": "loss warnings are required",
    },
    {
        "category": "binding_loss_warning_suppressed",
        "required_rejection": "binding loss warning suppressed",
    },
    {
        "category": "socd_drift_warning_suppressed",
        "required_rejection": "SOCD drift warning suppressed",
    },
]

REQUIRED_DOC_PHRASES = (
    "negative_corpus_contract_only",
    "target: future clean-room adapter candidate schema",
    "corpus rejects unsafe candidate payloads",
    "no adapter output exists",
    "no external JSON generation exists",
    "active profile round-trip remains unsafe",
    "sidecar is required",
    "runtime-owned behavior must not be represented directly by external profile JSON",
    "missing sidecar",
    "missing runtime-owned behavior warning",
    "missing non-round-trip warning",
    "claims round-trip safe",
    "claims active profile round-trip safe",
    "claims runtime-owned behavior represented by external profile JSON",
    "adapter implemented",
    "external JSON generated",
    "generated external JSON output path present",
    "device write allowed",
    "WebSerial allowed",
    "protobuf binary generation allowed",
    "runtime-loaded config allowed",
    "official compatibility claimed",
    "hardware validation claimed",
    "external source promoted to authority",
    "copied external source code",
    "external dependency added",
    "missing source-authority classification",
    "missing validation report",
    "missing loss warnings",
    "binding loss warning suppressed",
    "SOCD drift warning suppressed",
    "adapter_implemented=false",
    "external_json_generated=false",
    "hardware_status=not_new_hardware_result",
    "not official compatibility",
    "not hardware validation",
    "no external code reuse",
    "no external dependency",
    "no device write",
    "no WebSerial transport",
    "no protobuf binary generation",
    "no runtime-loaded config",
)

FORBIDDEN_OUTPUT_PATH_KEYS = {
    "external_json_output_path",
    "generated_external_json_path",
    "output_path_to_generated_external_json",
}


class CleanRoomAdapterNegativeCorpusContractError(ValueError):
    """Raised when the clean-room adapter negative corpus contract drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterNegativeCorpusContractError(message)


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
        fail(f"upstream checker failed: {checker_path}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"upstream checker did not report PASS: {checker_path}")


def upstream_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for name, packet in UPSTREAM_PACKETS.items():
        checker_path = REPO_ROOT / packet["checker_path"]
        doc_path = REPO_ROOT / packet["doc_path"]
        fixture_path = REPO_ROOT / packet["fixture_path"]
        for path in (checker_path, doc_path, fixture_path):
            if not path.exists():
                fail(f"referenced upstream path is missing: {display(path)}")

        fixture = load_json_object(fixture_path)
        if fixture.get("schema_name") != packet["schema_name"]:
            fail(f"{name} schema_name must be {packet['schema_name']!r}")
        if fixture.get("status") != packet["status"]:
            fail(f"{name} status must be {packet['status']!r}")

        reports[name] = {
            "checker_path": packet["checker_path"],
            "doc_path": packet["doc_path"],
            "doc_sha256": sha256(doc_path),
            "fixture_path": packet["fixture_path"],
            "fixture_sha256": sha256(fixture_path),
            "schema_name": packet["schema_name"],
            "status": packet["status"],
        }
    return reports


def supporting_findings() -> dict[str, Any]:
    schema_contract = load_json_object(
        REPO_ROOT / UPSTREAM_PACKETS["candidate_schema_contract"]["fixture_path"]
    )
    validator = load_json_object(
        REPO_ROOT / UPSTREAM_PACKETS["candidate_schema_validator"]["fixture_path"]
    )
    sidecar = load_json_object(REPO_ROOT / UPSTREAM_PACKETS["sidecar_contract"]["fixture_path"])
    readiness_gate = load_json_object(
        REPO_ROOT / UPSTREAM_PACKETS["schema_readiness_gate"]["fixture_path"]
    )
    export_loss_gate = load_json_object(
        REPO_ROOT / UPSTREAM_PACKETS["export_loss_gate"]["fixture_path"]
    )

    expected_false_flags = {
        "validator.adapter_implemented": validator.get("adapter_implemented"),
        "validator.external_json_generated": validator.get("external_json_generated"),
        "validator.round_trip_safe": validator.get("round_trip_safe"),
        "validator.active_profile_round_trip_safe": validator.get(
            "active_profile_round_trip_safe"
        ),
        "readiness_gate.active_profile_round_trip_safe": readiness_gate.get(
            "active_profile_round_trip_safe"
        ),
        "readiness_gate.runtime_owned_behavior_represented_by_external_profile_json": readiness_gate.get(
            "runtime_owned_behavior_represented_by_external_profile_json"
        ),
        "export_loss_gate.active_profile_round_trip_safe": export_loss_gate.get(
            "active_profile_round_trip_safe"
        ),
        "export_loss_gate.external_json_generation_allowed": export_loss_gate.get(
            "external_json_generation_allowed"
        ),
        "export_loss_gate.runtime_owned_behavior_represented": export_loss_gate.get(
            "runtime_owned_behavior_represented"
        ),
    }
    for label, value in expected_false_flags.items():
        if value is not False:
            fail(f"{label} must remain false")

    required_flags = sidecar.get("required_flags")
    if not isinstance(required_flags, dict):
        fail("sidecar required_flags must be an object")
    for key in (
        "sidecar_required",
        "runtime_owned_behavior_warning_required",
        "non_round_trip_warning_required",
    ):
        if required_flags.get(key) is not True:
            fail(f"sidecar required_flags.{key} must remain true")

    target_profile_metadata = schema_contract.get("target_profile_metadata")
    if not isinstance(target_profile_metadata, dict):
        fail("schema contract target_profile_metadata must be an object")
    if target_profile_metadata.get("adapter_implemented") is not False:
        fail("schema contract must keep adapter_implemented=false")
    if target_profile_metadata.get("external_json_generation_allowed") is not False:
        fail("schema contract must keep external JSON generation disallowed")
    if target_profile_metadata.get("active_profile_round_trip_currently_safe") is not False:
        fail("schema contract must keep active profile round-trip unsafe")

    runtime_sidecar = schema_contract.get("runtime_owned_behavior_sidecar")
    if not isinstance(runtime_sidecar, dict):
        fail("schema contract runtime_owned_behavior_sidecar must be an object")
    if runtime_sidecar.get("runtime_owned_behavior_represented_by_external_profile_json") is not False:
        fail("schema contract must keep runtime-owned behavior out of external profile JSON")

    return {
        "active_profile_round_trip_safe": False,
        "adapter_implemented": False,
        "binding_loss_warning_required": True,
        "external_json_generated": False,
        "external_json_generation_allowed": False,
        "non_round_trip_warning_required": True,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "runtime_owned_behavior_warning_required": True,
        "sidecar_required": True,
        "socd_drift_warning_required": True,
    }


def build_contract() -> dict[str, Any]:
    return {
        "contract_scope": {
            "adapter_output_exists": False,
            "corpus_rejects_unsafe_candidate_payloads": True,
            "external_json_generation_exists": False,
            "runtime_source_changed": False,
            "target": TARGET,
            "validation_scope": "docs_tools_fixtures_only",
        },
        "forbidden_capabilities": {
            "adapter_implemented": False,
            "copied_external_source_code": False,
            "device_write_allowed": False,
            "external_dependency_added": False,
            "external_json_generated": False,
            "hardware_validation_claimed": False,
            "official_compatibility_claimed": False,
            "protobuf_binary_generation_allowed": False,
            "runtime_loaded_config_allowed": False,
            "serial_device_write_behavior_implemented": False,
            "webserial_allowed": False,
        },
        "hardware_status": HARDWARE_STATUS,
        "invalid_case_categories": INVALID_CASE_CATEGORIES,
        "negative_corpus_rules": {
            "active_profile_round_trip_remains_unsafe": True,
            "loss_warnings_required": True,
            "runtime_owned_behavior_warning_required": True,
            "runtime_owned_behavior_must_not_be_represented_directly_by_external_profile_json": True,
            "sidecar_required": True,
            "source_authority_classification_required": True,
            "validation_report_required": True,
        },
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "source_authority": {
            "external_remapper_export_authority": False,
            "external_source_promoted_to_authority": False,
            "no_external_code_reuse": True,
            "no_external_dependency": True,
            "source_basis": "repo docs, fixtures, and checker outputs only",
        },
        "status": STATUS,
        "supporting_findings": supporting_findings(),
        "upstream_packets": upstream_reports(),
        "validation_report": {
            "adapter_implemented": False,
            "checker_path": "tools/check_glyph_clean_room_adapter_negative_corpus_contract.py",
            "doc_path": "docs/calibration/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.md",
            "external_json_generated": False,
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "invalid_case_categories": len(INVALID_CASE_CATEGORIES),
            "upstream_checkers_required_to_pass": True,
        },
    }


def validate_contract_fields(contract: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            fail(f"{key} must be {value!r}")

    scope = contract.get("contract_scope")
    if not isinstance(scope, dict):
        fail("contract_scope must be an object")
    expected_scope = {
        "adapter_output_exists": False,
        "corpus_rejects_unsafe_candidate_payloads": True,
        "external_json_generation_exists": False,
        "runtime_source_changed": False,
        "target": TARGET,
        "validation_scope": "docs_tools_fixtures_only",
    }
    if scope != expected_scope:
        fail("contract_scope drifted")

    categories = contract.get("invalid_case_categories")
    if categories != INVALID_CASE_CATEGORIES:
        fail("invalid_case_categories drifted")
    category_names = [item["category"] for item in INVALID_CASE_CATEGORIES]
    if len(category_names) != len(set(category_names)):
        fail("invalid_case_categories contains duplicate categories")

    rules = contract.get("negative_corpus_rules")
    if not isinstance(rules, dict):
        fail("negative_corpus_rules must be an object")
    for key, value in rules.items():
        if value is not True:
            fail(f"negative_corpus_rules.{key} must be true")

    forbidden = contract.get("forbidden_capabilities")
    if not isinstance(forbidden, dict):
        fail("forbidden_capabilities must be an object")
    for key, value in forbidden.items():
        if value is not False:
            fail(f"forbidden_capabilities.{key} must be false")

    authority = contract.get("source_authority")
    if not isinstance(authority, dict):
        fail("source_authority must be an object")
    expected_authority = {
        "external_remapper_export_authority": False,
        "external_source_promoted_to_authority": False,
        "no_external_code_reuse": True,
        "no_external_dependency": True,
    }
    for key, value in expected_authority.items():
        if authority.get(key) != value:
            fail(f"source_authority.{key} must be {value!r}")

    report = contract.get("validation_report")
    if not isinstance(report, dict):
        fail("validation_report must be an object")
    if report.get("adapter_implemented") is not False:
        fail("validation_report.adapter_implemented must be false")
    if report.get("external_json_generated") is not False:
        fail("validation_report.external_json_generated must be false")
    if report.get("hardware_status") != HARDWARE_STATUS:
        fail(f"validation_report.hardware_status must be {HARDWARE_STATUS!r}")
    if report.get("invalid_case_categories") != len(INVALID_CASE_CATEGORIES):
        fail("validation_report.invalid_case_categories drifted")


def validate_no_output_path_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_OUTPUT_PATH_KEYS:
                fail(f"fixture must not contain generated external JSON output field: {key}")
            validate_no_output_path_keys(child)
    elif isinstance(value, list):
        for child in value:
            validate_no_output_path_keys(child)


def validate_fixture(contract: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(contract)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated negative corpus contract JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != contract:
        fail("committed fixture JSON object drifted from regenerated negative corpus contract")
    validate_no_output_path_keys(committed)


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_upstream_checkers() -> None:
    for packet in UPSTREAM_PACKETS.values():
        validate_checker_passes(packet["checker_path"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the docs/tools-only Glyph clean-room adapter negative corpus contract."
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
        contract = build_contract()
        if args.json:
            print(canonical_json_text(contract), end="")
            return 0
        validate_contract_fields(contract)
        validate_fixture(contract)
        validate_doc()
        validate_upstream_checkers()
    except (OSError, CleanRoomAdapterNegativeCorpusContractError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print(f"invalid_case_categories={len(INVALID_CASE_CATEGORIES)}")
        print("adapter_implemented=false")
        print("external_json_generated=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print(f"invalid_case_categories={len(INVALID_CASE_CATEGORIES)}")
    print("adapter_implemented=false")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
