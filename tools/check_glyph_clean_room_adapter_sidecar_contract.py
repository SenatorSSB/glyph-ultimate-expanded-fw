#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter sidecar/caveat contract packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_clean_room_adapter_sidecar_contract_2026-06-04.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_sidecar_contract_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_sidecar_contract"
SCHEMA_VERSION = 1
STATUS = "sidecar_contract_only_adapter_not_implemented"
HARDWARE_STATUS = "not_new_hardware_result"

PRIOR_CLEAN_ROOM_PACKETS = {
    "branch_1_schema_contract": {
        "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_contract.py",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_candidate_schema_contract",
        "status": "schema_contract_only_adapter_not_implemented",
    },
    "branch_2_schema_validator": {
        "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_validator.py",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_SCHEMA_PLACEHOLDER_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_candidate_schema_validator",
        "status": "placeholder_only_no_adapter_output",
    },
}

REQUIRED_FLAGS = {
    "adapter_implemented": False,
    "external_json_generated": False,
    "hardware_status": HARDWARE_STATUS,
    "non_round_trip_warning_required": True,
    "runtime_owned_behavior_warning_required": True,
    "sidecar_required": True,
}

REQUIRED_SIDECAR_SECTIONS = [
    "runtime-owned behavior warning",
    "non-round-trip warning",
    "binding-loss warning",
    "SOCD-drift warning",
    "profile-level-only warning",
    "no official compatibility claim",
    "no device-write/WebSerial claim",
    "no hardware validation claim",
    "source-authority classification",
    "validation report",
]

WARNING_REQUIREMENTS = {
    "binding_loss_warning_required": True,
    "device_write_webserial_claim_warning_required": True,
    "hardware_validation_claim_warning_required": True,
    "non_round_trip_warning_required": True,
    "official_compatibility_claim_warning_required": True,
    "profile_level_only_warning_required": True,
    "runtime_owned_behavior_warning_required": True,
    "socd_drift_warning_required": True,
    "source_authority_classification_required": True,
    "validation_report_required": True,
}

FORBIDDEN_CAPABILITIES = {
    "active_profile_artifact_changed": False,
    "adapter_implemented": False,
    "device_write_implemented": False,
    "external_code_copied": False,
    "external_dependency_added": False,
    "external_json_generated": False,
    "external_remapper_compatible_json_generated": False,
    "exported_experiment_artifact_changed": False,
    "hardware_validation_claimed": False,
    "official_compatibility_claimed": False,
    "protobuf_binary_generation_implemented": False,
    "runtime_firmware_source_changed": False,
    "runtime_loaded_config_implemented": False,
    "serial_device_write_behavior_implemented": False,
    "webserial_transport_implemented": False,
}

REQUIRED_DOC_PHRASES = (
    "sidecar_contract_only_adapter_not_implemented",
    "external-remapper export is not round-trip safe",
    "cannot represent runtime-owned behavior",
    "sidecar_required = true",
    "runtime_owned_behavior_warning_required = true",
    "non_round_trip_warning_required = true",
    "adapter_implemented = false",
    "external_json_generated = false",
    "hardware_status = not_new_hardware_result",
    "runtime-owned behavior warning",
    "non-round-trip warning",
    "binding-loss warning",
    "SOCD-drift warning",
    "profile-level-only warning",
    "no official compatibility claim",
    "no device-write/WebSerial claim",
    "no hardware validation claim",
    "source-authority classification",
    "validation report",
    "no adapter implementation",
    "no external-remapper-compatible JSON generation",
    "no generated external JSON path",
    "not official compatibility",
    "not hardware validation",
    "no device write",
    "no serial/device write behavior",
    "no WebSerial transport",
    "no protobuf binary generation",
    "no runtime-loaded config",
    "no external code reuse",
    "no external dependency",
)

FORBIDDEN_FIXTURE_STRINGS = (
    "generated_external_json_path",
    "external_json_output_path",
    "output_path_to_generated_external_json",
    "external-remapper-compatible JSON payload",
)


class CleanRoomAdapterSidecarContractError(ValueError):
    """Raised when the clean-room adapter sidecar contract drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterSidecarContractError(message)


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


def contract_inputs() -> dict[str, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, packet in PRIOR_CLEAN_ROOM_PACKETS.items():
        checker_path = REPO_ROOT / packet["checker_path"]
        fixture_path = REPO_ROOT / packet["fixture_path"]
        for path in (checker_path, fixture_path):
            if not path.exists():
                fail(f"required prior clean-room path is missing: {display(path)}")
        inputs[name] = {
            "checker_path": packet["checker_path"],
            "fixture_path": packet["fixture_path"],
            "fixture_sha256": sha256(fixture_path),
            "schema_name": packet["schema_name"],
            "status": packet["status"],
        }
    return inputs


def build_contract() -> dict[str, Any]:
    return {
        "contract_inputs": contract_inputs(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "required_flags": REQUIRED_FLAGS,
        "required_sidecar_sections": REQUIRED_SIDECAR_SECTIONS,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "source_authority_classification": {
            "classification_required_for_future_candidate": True,
            "external_remapper_export_authority": False,
            "external_source_promoted_to_authority": False,
            "no_external_code_reuse": True,
            "no_external_dependency": True,
            "source_basis": "repo docs, fixtures, and checker outputs only",
        },
        "status": STATUS,
        "validation_report": {
            "adapter_implemented": False,
            "checker_path": "tools/check_glyph_clean_room_adapter_sidecar_contract.py",
            "doc_path": "docs/calibration/glyph_clean_room_adapter_sidecar_contract_2026-06-04.md",
            "external_json_generated": False,
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_sidecar_contract_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "prior_clean_room_checkers_required_to_pass": True,
            "required_sidecar_sections_validated": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
        "warning_requirements": WARNING_REQUIREMENTS,
    }


def validate_prior_clean_room_checkers() -> None:
    for packet in PRIOR_CLEAN_ROOM_PACKETS.values():
        checker = packet["checker_path"]
        completed = subprocess.run(
            [sys.executable, checker],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            output = "\n".join(
                part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
            )
            fail(f"prior clean-room checker failed: {checker}: {output}")
        if "status=PASS" not in completed.stdout:
            fail(f"prior clean-room checker did not report PASS: {checker}")


def validate_contract_fields(contract: dict[str, Any]) -> None:
    if contract.get("schema_name") != SCHEMA_NAME:
        fail(f"schema_name must be {SCHEMA_NAME!r}")
    if contract.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION!r}")
    if contract.get("status") != STATUS:
        fail(f"status must be {STATUS!r}")
    if contract.get("required_flags") != REQUIRED_FLAGS:
        fail("required_flags drifted")
    if contract.get("required_sidecar_sections") != REQUIRED_SIDECAR_SECTIONS:
        fail("required_sidecar_sections drifted")
    if contract.get("warning_requirements") != WARNING_REQUIREMENTS:
        fail("warning_requirements drifted")
    if contract.get("forbidden_capabilities") != FORBIDDEN_CAPABILITIES:
        fail("forbidden_capabilities drifted")

    authority = contract.get("source_authority_classification")
    if not isinstance(authority, dict):
        fail("source_authority_classification must be an object")
    expected_authority = {
        "classification_required_for_future_candidate": True,
        "external_remapper_export_authority": False,
        "external_source_promoted_to_authority": False,
        "no_external_code_reuse": True,
        "no_external_dependency": True,
    }
    for key, value in expected_authority.items():
        if authority.get(key) != value:
            fail(f"source_authority_classification.{key} must be {value!r}")

    report = contract.get("validation_report")
    if not isinstance(report, dict):
        fail("validation_report must be an object")
    if report.get("adapter_implemented") is not False:
        fail("validation_report.adapter_implemented must be false")
    if report.get("external_json_generated") is not False:
        fail("validation_report.external_json_generated must be false")
    if report.get("hardware_status") != HARDWARE_STATUS:
        fail(f"validation_report.hardware_status must be {HARDWARE_STATUS!r}")
    if report.get("prior_clean_room_checkers_required_to_pass") is not True:
        fail("validation_report.prior_clean_room_checkers_required_to_pass must be true")


def validate_fixture(contract: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(contract)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated sidecar contract JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != contract:
        fail("committed fixture JSON object drifted from regenerated sidecar contract")

    lowered = committed_text.lower()
    for forbidden in FORBIDDEN_FIXTURE_STRINGS:
        if forbidden.lower() in lowered:
            fail(f"fixture must not contain generated external JSON output field: {forbidden}")
    if '"generated_external_json"' in lowered:
        fail("fixture must not contain a generated external JSON payload section")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the docs/tools-only Glyph clean-room adapter sidecar contract."
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
        validate_prior_clean_room_checkers()
    except (OSError, CleanRoomAdapterSidecarContractError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("sidecar_required=true")
        print("adapter_implemented=false")
        print("external_json_generated=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("sidecar_required=true")
    print("adapter_implemented=false")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
