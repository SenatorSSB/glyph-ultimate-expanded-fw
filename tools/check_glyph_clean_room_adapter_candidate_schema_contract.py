#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter candidate schema contract packet."""

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
    / "docs/calibration/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_candidate_schema_contract"
SCHEMA_VERSION = 1
STATUS = "schema_contract_only_adapter_not_implemented"
TARGET = "future clean-room adapter candidate schema"
HARDWARE_STATUS = "not_new_hardware_result"

SOURCE_PACKETS = {
    "active_profile_artifact": {
        "path": "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
        "schema_name": "active_profile_artifact",
        "status": "repo_artifact",
        "evidence_role": "active profile artifact used in the no-device remapper experiment",
    },
    "exported_experiment_artifact": {
        "path": "docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json",
        "schema_name": "external_remapper_exported_GlyphUserProfiles",
        "status": "manual_no_device_export_artifact_with_warnings",
        "evidence_role": "exported experiment artifact, not canonical source authority",
    },
    "binding_loss_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_binding_loss_classification.py",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_binding_loss_classification",
        "status": "docs_tools_binding_loss_classification",
        "evidence_role": "adapter-blocking binding-loss classification",
    },
    "socd_drift_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_socd_drift_classification.py",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_socd_drift_classification",
        "status": "docs_tools_socd_drift_classification",
        "evidence_role": "adapter-blocking SOCD drift classification",
    },
    "export_loss_gate": {
        "checker_path": "tools/check_glyph_offline_remapper_export_loss_gate.py",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_export_loss_gate",
        "status": "external_remapper_round_trip_not_safe_adapter_blocked",
        "evidence_role": "aggregate export-loss gate blocking adapter implementation",
    },
}

REQUIRED_SECTIONS = [
    "schema_name",
    "schema_version",
    "status",
    "source_artifacts",
    "target_profile_metadata",
    "profile_level_bindings",
    "runtime_owned_behavior_sidecar",
    "socd_policy_sidecar",
    "loss_warnings",
    "non_round_trip_caveats",
    "source_authority",
    "forbidden_capabilities",
    "validation_report",
]

LOSS_WARNINGS = [
    "active profile round-trip is currently unsafe",
    "external remapper export is not canonical",
    "binding-loss classification is adapter-blocking",
    "SOCD drift classification is adapter-blocking",
    "target output is not generated",
    "target output is not round-trip safe by default",
]

NON_ROUND_TRIP_CAVEATS = [
    "active profile round-trip is currently unsafe",
    "target output is not generated",
    "target output is not round-trip safe by default",
    "external remapper export is not canonical",
    "adapter implementation remains blocked",
    "external JSON generation remains blocked",
    "official compatibility remains unclaimed",
]

FORBIDDEN_CAPABILITIES = {
    "adapter_implemented": False,
    "adapter_implementation_blocked": True,
    "device_write_implemented": False,
    "external_code_copied": False,
    "external_dependency_added": False,
    "external_json_generation_allowed": False,
    "external_json_generation_blocked": True,
    "external_remapper_compatible_json_generated": False,
    "hardware_validation_claimed": False,
    "official_compatibility_claimed": False,
    "protobuf_binary_generation_implemented": False,
    "runtime_loaded_config_implemented": False,
    "serial_device_write_behavior_implemented": False,
    "webserial_transport_implemented": False,
}

REQUIRED_DOC_PHRASES = (
    "schema_contract_only_adapter_not_implemented",
    "target: future clean-room adapter candidate schema",
    "target output is not generated",
    "target output is not round-trip safe by default",
    "active profile round-trip is currently unsafe",
    "external remapper export is not canonical",
    "adapter implementation remains blocked",
    "external JSON generation remains blocked",
    "official compatibility remains unclaimed",
    "no external code reuse",
    "no external dependency",
    "no device write/WebSerial/protobuf/runtime-loaded config",
    "no device write",
    "no WebSerial transport",
    "no protobuf binary generation",
    "no runtime-loaded config",
    "no external-remapper-compatible JSON generation",
    "not official compatibility",
    "not hardware validation",
)

FORBIDDEN_FIXTURE_STRINGS = (
    "generated_external_json_path",
    "external_json_output_path",
    "output_path_to_generated_external_json",
)


class CleanRoomAdapterCandidateSchemaContractError(ValueError):
    """Raised when the committed clean-room adapter schema contract drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterCandidateSchemaContractError(message)


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


def source_artifact_reports() -> dict[str, dict[str, Any]]:
    experiment_result = load_json_object(
        REPO_ROOT
        / "docs/calibration/fixtures/glyph_offline_remapper_experiment_result_2026-06-04.json"
    )
    active_profile = experiment_result.get("input_artifact")
    exported_artifact = experiment_result.get("exported_artifact")
    if not isinstance(active_profile, dict):
        fail("experiment_result.input_artifact must be an object")
    if not isinstance(exported_artifact, dict):
        fail("experiment_result.exported_artifact must be an object")

    expected_active_path = SOURCE_PACKETS["active_profile_artifact"]["path"]
    expected_exported_path = SOURCE_PACKETS["exported_experiment_artifact"]["path"]
    if active_profile.get("path") != expected_active_path:
        fail("active profile artifact path drifted from experiment result")
    if exported_artifact.get("path") != expected_exported_path:
        fail("exported experiment artifact path drifted from experiment result")

    reports: dict[str, dict[str, Any]] = {}
    for name, packet in SOURCE_PACKETS.items():
        if "fixture_path" in packet:
            fixture_path = REPO_ROOT / packet["fixture_path"]
            checker_path = REPO_ROOT / packet["checker_path"]
            for path in (fixture_path, checker_path):
                if not path.exists():
                    fail(f"referenced source path is missing: {display(path)}")
            fixture = load_json_object(fixture_path)
            if fixture.get("schema_name") != packet["schema_name"]:
                fail(f"{name} schema_name must be {packet['schema_name']!r}")
            if fixture.get("status") != packet["status"]:
                fail(f"{name} status must be {packet['status']!r}")
            if fixture.get("hardware_status") != HARDWARE_STATUS:
                fail(f"{name} hardware_status must be {HARDWARE_STATUS!r}")
            reports[name] = {
                "checker_path": packet["checker_path"],
                "evidence_role": packet["evidence_role"],
                "fixture_path": packet["fixture_path"],
                "fixture_sha256": sha256(fixture_path),
                "schema_name": packet["schema_name"],
                "status": packet["status"],
            }
            continue

        path = REPO_ROOT / packet["path"]
        if not path.exists():
            fail(f"referenced source artifact is missing: {display(path)}")
        reports[name] = {
            "evidence_role": packet["evidence_role"],
            "path": packet["path"],
            "schema_name": packet["schema_name"],
            "sha256": sha256(path),
            "status": packet["status"],
        }

    if reports["active_profile_artifact"]["sha256"] != active_profile.get("sha256"):
        fail("active profile artifact sha256 drifted from experiment result")
    if reports["exported_experiment_artifact"]["sha256"] != exported_artifact.get("sha256"):
        fail("exported experiment artifact sha256 drifted from experiment result")

    return reports


def validate_source_blockers() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    binding_loss = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["binding_loss_classification"]["fixture_path"]
    )
    socd_drift = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["socd_drift_classification"]["fixture_path"]
    )
    export_loss_gate = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["export_loss_gate"]["fixture_path"]
    )

    if binding_loss.get("loss_severity") != "adapter_blocking_loss":
        fail("binding-loss classification must remain adapter_blocking_loss")
    if binding_loss.get("round_trip_safe_for_active_profile") is not False:
        fail("binding-loss classification must keep round-trip safety false")
    if binding_loss.get("adapter_implemented") is not False:
        fail("binding-loss classification must keep adapter_implemented=false")
    if binding_loss.get("external_source_promoted_to_authority") is not False:
        fail("binding-loss classification must not promote external source authority")

    if socd_drift.get("drift_severity") != "adapter_blocking_drift":
        fail("SOCD drift classification must remain adapter_blocking_drift")
    if socd_drift.get("adapter_implemented") is not False:
        fail("SOCD drift classification must keep adapter_implemented=false")
    if socd_drift.get("external_source_promoted_to_authority") is not False:
        fail("SOCD drift classification must not promote external source authority")

    expected_gate_flags = {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_allowed": False,
        "external_json_generation_allowed": False,
        "runtime_owned_behavior_represented": False,
        "official_compatibility_claimed": False,
        "hardware_validation_claimed": False,
    }
    for key, value in expected_gate_flags.items():
        if export_loss_gate.get(key) != value:
            fail(f"export-loss gate {key} must be {value!r}")

    return binding_loss, socd_drift, export_loss_gate


def build_contract() -> dict[str, Any]:
    binding_loss, socd_drift, _export_loss_gate = validate_source_blockers()
    return {
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "loss_warnings": LOSS_WARNINGS,
        "non_round_trip_caveats": NON_ROUND_TRIP_CAVEATS,
        "profile_level_bindings": {
            "binding_loss_classification": "adapter_blocking_loss",
            "binding_loss_summary": binding_loss["binding_loss_summary"],
            "external_remapper_export_canonical": False,
            "round_trip_safe_for_active_profile": False,
            "source_artifact_key": "active_profile_artifact",
            "target_output_generated": False,
        },
        "runtime_owned_behavior_sidecar": {
            "required_for_future_candidate": True,
            "runtime_owned_behavior_represented_by_external_profile_json": False,
            "sidecar_only": True,
            "target_output_generated": False,
        },
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "socd_policy_sidecar": {
            "drift_classification": "adapter_blocking_drift",
            "socd_drift_summary": socd_drift["socd_drift_summary"],
            "source_artifact_key": "socd_drift_classification",
            "target_output_generated": False,
        },
        "source_artifacts": source_artifact_reports(),
        "source_authority": {
            "external_remapper_export_authority": False,
            "external_source_promoted_to_authority": False,
            "no_external_code_reuse": True,
            "no_external_dependency": True,
            "repo_source_artifacts_are_contract_inputs": True,
            "source_behavior_claim_basis": "repo docs, fixtures, and checker outputs only",
        },
        "status": STATUS,
        "target_profile_metadata": {
            "active_profile_round_trip_currently_safe": False,
            "adapter_implemented": False,
            "external_json_generation_allowed": False,
            "external_remapper_export_canonical": False,
            "hardware_status": HARDWARE_STATUS,
            "official_compatibility_claimed": False,
            "target": TARGET,
            "target_output_generated": False,
            "target_output_round_trip_safe_by_default": False,
        },
        "validation_report": {
            "adapter_implemented": False,
            "checker_path": "tools/check_glyph_clean_room_adapter_candidate_schema_contract.py",
            "doc_path": "docs/calibration/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.md",
            "external_json_generation_allowed": False,
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "required_sections": REQUIRED_SECTIONS,
            "source_artifacts_validated": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
    }


def validate_sections(contract: dict[str, Any]) -> None:
    if list(contract) != sorted(REQUIRED_SECTIONS):
        fail("top-level sections must match required canonical section order")
    if set(contract) != set(REQUIRED_SECTIONS):
        fail("top-level sections drifted")

    expected_top_level = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "loss_warnings": LOSS_WARNINGS,
        "non_round_trip_caveats": NON_ROUND_TRIP_CAVEATS,
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
    }
    for key, value in expected_top_level.items():
        if contract.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_contract_fields(contract: dict[str, Any]) -> None:
    metadata = contract.get("target_profile_metadata")
    if not isinstance(metadata, dict):
        fail("target_profile_metadata must be an object")
    expected_metadata = {
        "target": TARGET,
        "target_output_generated": False,
        "target_output_round_trip_safe_by_default": False,
        "active_profile_round_trip_currently_safe": False,
        "external_remapper_export_canonical": False,
        "adapter_implemented": False,
        "external_json_generation_allowed": False,
        "official_compatibility_claimed": False,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected_metadata.items():
        if metadata.get(key) != value:
            fail(f"target_profile_metadata.{key} must be {value!r}")

    source_authority = contract.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("source_authority must be an object")
    expected_authority = {
        "external_remapper_export_authority": False,
        "external_source_promoted_to_authority": False,
        "no_external_code_reuse": True,
        "no_external_dependency": True,
        "repo_source_artifacts_are_contract_inputs": True,
    }
    for key, value in expected_authority.items():
        if source_authority.get(key) != value:
            fail(f"source_authority.{key} must be {value!r}")

    validation = contract.get("validation_report")
    if not isinstance(validation, dict):
        fail("validation_report must be an object")
    if validation.get("adapter_implemented") is not False:
        fail("validation_report.adapter_implemented must be false")
    if validation.get("external_json_generation_allowed") is not False:
        fail("validation_report.external_json_generation_allowed must be false")
    if validation.get("hardware_status") != HARDWARE_STATUS:
        fail(f"validation_report.hardware_status must be {HARDWARE_STATUS!r}")
    if validation.get("required_sections") != REQUIRED_SECTIONS:
        fail("validation_report.required_sections drifted")


def validate_source_artifacts(contract: dict[str, Any]) -> None:
    artifacts = contract.get("source_artifacts")
    if not isinstance(artifacts, dict):
        fail("source_artifacts must be an object")
    if set(artifacts) != set(SOURCE_PACKETS):
        fail("source_artifacts keys drifted")
    expected = source_artifact_reports()
    if artifacts != expected:
        fail("source_artifacts drifted from regenerated source artifact reports")


def validate_no_generated_external_json_path(contract: dict[str, Any]) -> None:
    fixture_text = canonical_json_text(contract)
    lowered = fixture_text.lower()
    for forbidden in FORBIDDEN_FIXTURE_STRINGS:
        if forbidden.lower() in lowered:
            fail(f"fixture must not contain generated external JSON output path field: {forbidden}")
    if '"generated_external_json"' in lowered:
        fail("fixture must not contain a generated external JSON payload section")


def validate_fixture(contract: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(contract)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated contract JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != contract:
        fail("committed fixture JSON object drifted from regenerated contract output")
    validate_no_generated_external_json_path(committed)


def validate_doc() -> None:
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    lowered = doc_text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_component_checkers() -> None:
    for packet in SOURCE_PACKETS.values():
        checker = packet.get("checker_path")
        if checker is None:
            continue
        completed = subprocess.run(
            [sys.executable, checker],
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
            fail(f"component checker failed: {checker}: {output}")
        if "status=PASS" not in completed.stdout:
            fail(f"component checker did not report PASS: {checker}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the committed docs/tools-only Glyph clean-room adapter "
            "candidate schema contract."
        )
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
        validate_sections(contract)
        validate_contract_fields(contract)
        validate_source_artifacts(contract)
        validate_fixture(contract)
        validate_doc()
        validate_component_checkers()
    except (
        OSError,
        CleanRoomAdapterCandidateSchemaContractError,
        ValueError,
    ) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("adapter_implemented=false")
        print("external_json_generation_allowed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("adapter_implemented=false")
    print("external_json_generation_allowed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
