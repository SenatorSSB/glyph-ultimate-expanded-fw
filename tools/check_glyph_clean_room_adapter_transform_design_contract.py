#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter transform design contract packet."""

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
    / "docs/calibration/glyph_clean_room_adapter_transform_design_contract_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_contract_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_transform_design_contract"
REPORT_VERSION = 1
STATUS = "transform_design_contract_only"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_DESIGN_SECTIONS = [
    "input_artifacts",
    "profile_level_transform_scope",
    "runtime_owned_behavior_sidecar_scope",
    "socd_policy_sidecar_scope",
    "loss_warning_scope",
    "validation_report_scope",
    "forbidden_outputs",
    "source_authority",
    "approval_gates",
]

REQUIRED_INPUT_ARTIFACT_IDS = [
    "active_profile_artifact",
    "exported_experiment_artifact",
    "binding_loss_classification",
    "socd_drift_classification",
    "clean_room_schema_readiness_gate",
    "clean_room_negative_corpus_gate",
]

SOURCE_PACKETS = {
    "experiment_result": {
        "checker_path": "tools/check_glyph_offline_remapper_experiment_result.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_experiment_result_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_experiment_result_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_experiment_result",
        "status": "manual_no_device_experiment_completed_with_warnings",
        "evidence_role": "source for active profile and exported experiment artifact hashes",
    },
    "binding_loss_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_binding_loss_classification.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_binding_loss_classification_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_binding_loss_classification",
        "status": "docs_tools_binding_loss_classification",
        "evidence_role": "source for adapter-blocking binding-loss classification",
    },
    "socd_drift_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_socd_drift_classification.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_socd_drift_classification_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_socd_drift_classification",
        "status": "docs_tools_socd_drift_classification",
        "evidence_role": "source for adapter-blocking SOCD drift classification",
    },
    "clean_room_schema_readiness_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_schema_readiness_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_schema_readiness_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_schema_readiness_gate",
        "status": "schema_planning_complete_adapter_implementation_blocked",
        "evidence_role": "source for clean-room schema readiness gate",
    },
    "clean_room_negative_corpus_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_negative_corpus_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_negative_corpus_gate",
        "status": "negative_corpus_ready_adapter_implementation_blocked",
        "evidence_role": "source for clean-room negative corpus readiness gate",
    },
}

FORBIDDEN_OUTPUTS = [
    "external_json_payload",
    "external_json_output_path",
    "active_profile_round_trip_artifact",
    "exported_experiment_artifact_mutation",
    "runtime_source_change",
    "device_write_packet",
    "webserial_transport",
    "protobuf_binary",
    "runtime_loaded_config",
    "official_configurator_compatibility_claim",
    "hardware_validation_claim",
]

APPROVAL_GATES = [
    "adapter implementation",
    "transform implementation",
    "external JSON generation",
    "WebSerial/device write",
    "protobuf binary generation",
    "runtime-loaded config",
    "official configurator compatibility claim",
    "hardware validation claim",
    "active profile artifact mutation",
    "exported experiment artifact mutation",
]

REQUIRED_DOC_PHRASES = (
    "transform_design_contract_only",
    "transform implementation does not exist",
    "external json generation does not exist",
    "active profile round-trip remains unsafe",
    "sidecar is required",
    "runtime-owned behavior remains outside external profile json",
    "source data comes only from repo fixtures and accepted docs/tools evidence",
    "no external source code copied",
    "no external dependency",
    "no device write/webserial/protobuf/runtime-loaded config",
    "input_artifacts",
    "profile_level_transform_scope",
    "runtime_owned_behavior_sidecar_scope",
    "socd_policy_sidecar_scope",
    "loss_warning_scope",
    "validation_report_scope",
    "forbidden_outputs",
    "source_authority",
    "approval_gates",
    "active profile artifact",
    "exported experiment artifact",
    "binding-loss classification",
    "socd drift classification",
    "clean-room schema readiness gate",
    "clean-room negative corpus gate",
    "not official configurator compatibility",
    "not hardware validation",
)


class CleanRoomAdapterTransformDesignContractError(ValueError):
    """Raised when the clean-room adapter transform design contract drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterTransformDesignContractError(message)


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
        fail(f"source checker failed: {checker_path}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"source checker did not report PASS: {checker_path}")


def source_packet_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for name, packet in SOURCE_PACKETS.items():
        checker_path = REPO_ROOT / packet["checker_path"]
        doc_path = REPO_ROOT / packet["doc_path"]
        fixture_path = REPO_ROOT / packet["fixture_path"]
        for path in (checker_path, doc_path, fixture_path):
            if not path.exists():
                fail(f"referenced source path is missing: {display(path)}")

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


def validate_source_findings() -> dict[str, Any]:
    experiment = load_json_object(REPO_ROOT / SOURCE_PACKETS["experiment_result"]["fixture_path"])
    binding = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["binding_loss_classification"]["fixture_path"]
    )
    socd = load_json_object(REPO_ROOT / SOURCE_PACKETS["socd_drift_classification"]["fixture_path"])
    schema_gate = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["clean_room_schema_readiness_gate"]["fixture_path"]
    )
    negative_gate = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["clean_room_negative_corpus_gate"]["fixture_path"]
    )

    input_artifact = experiment.get("input_artifact")
    exported_artifact = experiment.get("exported_artifact")
    if not isinstance(input_artifact, dict):
        fail("experiment result input_artifact must be an object")
    if not isinstance(exported_artifact, dict):
        fail("experiment result exported_artifact must be an object")
    if input_artifact.get("label") != "active_profile_artifact":
        fail("experiment result input_artifact label must be active_profile_artifact")
    if exported_artifact.get("label") != "external_remapper_exported_GlyphUserProfiles":
        fail("experiment result exported_artifact label drifted")

    experiment_flags = experiment.get("experiment_flags")
    if not isinstance(experiment_flags, dict):
        fail("experiment result experiment_flags must be an object")
    expected_experiment_false_flags = {
        "adapter_implemented": False,
        "device_connected": False,
        "webserial_access_granted": False,
        "save_to_device_clicked": False,
        "device_write_attempted": False,
        "official_compatibility_claimed": False,
        "hardware_validation_claimed": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected_experiment_false_flags.items():
        if experiment_flags.get(key) != value:
            fail(f"experiment result flag {key} must be {value!r}")

    if binding.get("loss_severity") != "adapter_blocking_loss":
        fail("binding-loss classification must remain adapter_blocking_loss")
    if binding.get("round_trip_safe_for_active_profile") is not False:
        fail("binding-loss classification must keep round_trip_safe_for_active_profile=false")
    if binding.get("adapter_implemented") is not False:
        fail("binding-loss classification must keep adapter_implemented=false")

    if socd.get("drift_severity") != "adapter_blocking_drift":
        fail("SOCD drift classification must remain adapter_blocking_drift")
    if socd.get("adapter_implemented") is not False:
        fail("SOCD drift classification must keep adapter_implemented=false")

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
        "active_profile_artifact": {
            "path": input_artifact.get("path"),
            "sha256": input_artifact.get("sha256"),
        },
        "binding_loss_classification": {
            "loss_severity": binding.get("loss_severity"),
            "round_trip_safe_for_active_profile": False,
        },
        "clean_room_negative_corpus_gate": {
            "adapter_implementation_blocked": True,
            "external_json_generation_blocked": True,
            "negative_corpus_ready": True,
            "sidecar_required": True,
        },
        "clean_room_schema_readiness_gate": {
            "adapter_implementation_blocked": True,
            "external_json_generation_blocked": True,
            "schema_planning_complete": True,
            "sidecar_required": True,
        },
        "exported_experiment_artifact": {
            "path": exported_artifact.get("path"),
            "sha256": exported_artifact.get("sha256"),
        },
        "socd_drift_classification": {
            "drift_severity": socd.get("drift_severity"),
        },
    }


def build_contract() -> dict[str, Any]:
    source_reports = source_packet_reports()
    source_findings = validate_source_findings()
    return {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_added": False,
        "approval_gates": {
            "explicit_approval_required_for": APPROVAL_GATES,
            "implementation_requires_reviewed_contract_and_supervisor_approval": True,
        },
        "design_sections": REQUIRED_DESIGN_SECTIONS,
        "device_write_implemented": False,
        "external_code_copied": False,
        "external_dependency_added": False,
        "external_json_generated": False,
        "external_json_generation_exists": False,
        "external_source_promoted_to_authority": False,
        "forbidden_outputs": {
            "forbidden_output_ids": FORBIDDEN_OUTPUTS,
            "must_not_mutate_active_profile_artifact": True,
            "must_not_mutate_exported_experiment_artifact": True,
            "must_not_write_device_or_transport_payload": True,
        },
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "input_artifacts": [
            {
                "artifact_id": "active_profile_artifact",
                "required": True,
                "source": source_findings["active_profile_artifact"],
            },
            {
                "artifact_id": "exported_experiment_artifact",
                "required": True,
                "source": source_findings["exported_experiment_artifact"],
            },
            {
                "artifact_id": "binding_loss_classification",
                "required": True,
                "source": source_findings["binding_loss_classification"],
            },
            {
                "artifact_id": "socd_drift_classification",
                "required": True,
                "source": source_findings["socd_drift_classification"],
            },
            {
                "artifact_id": "clean_room_schema_readiness_gate",
                "required": True,
                "source": source_findings["clean_room_schema_readiness_gate"],
            },
            {
                "artifact_id": "clean_room_negative_corpus_gate",
                "required": True,
                "source": source_findings["clean_room_negative_corpus_gate"],
            },
        ],
        "loss_warning_scope": {
            "binding_loss_warning_required": True,
            "loss_warnings_required": True,
            "socd_drift_warning_required": True,
        },
        "official_configurator_compatibility_claimed": False,
        "profile_level_transform_scope": {
            "allowed_scope": "design_only_profile_level_mapping_description_after_approval",
            "active_profile_round_trip_safe": False,
            "external_json_generated": False,
            "transform_implemented": False,
        },
        "protobuf_binary_generation_implemented": False,
        "report_version": REPORT_VERSION,
        "runtime_loaded_config_implemented": False,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "runtime_owned_behavior_sidecar_scope": {
            "runtime_owned_behavior_external_profile_json": False,
            "runtime_owned_behavior_warning_required": True,
            "sidecar_required": True,
        },
        "schema_name": SCHEMA_NAME,
        "sidecar_required": True,
        "socd_policy_sidecar_scope": {
            "socd_drift_classification_required": True,
            "socd_drift_warning_required": True,
            "socd_policy_sidecar_required": True,
        },
        "source_authority": {
            "accepted_evidence_only": True,
            "external_code_copied": False,
            "external_dependency_added": False,
            "external_source_promoted_to_authority": False,
            "source_data_scope": "repo fixtures and accepted docs/tools evidence only",
            "source_packets": source_reports,
        },
        "status": STATUS,
        "transform_implementation_exists": False,
        "transform_implemented": False,
        "validation_report_scope": {
            "checker_path": "tools/check_glyph_clean_room_adapter_transform_design_contract.py",
            "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_design_contract_2026-06-04.md",
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_contract_2026-06-04.json",
            "required_sections": REQUIRED_DESIGN_SECTIONS,
            "source_checkers_required_to_pass": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
        "webserial_transport_implemented": False,
    }


def validate_contract(contract: dict[str, Any]) -> None:
    expected_flags = {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_added": False,
        "device_write_implemented": False,
        "external_code_copied": False,
        "external_dependency_added": False,
        "external_json_generated": False,
        "external_json_generation_exists": False,
        "external_source_promoted_to_authority": False,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "official_configurator_compatibility_claimed": False,
        "protobuf_binary_generation_implemented": False,
        "runtime_loaded_config_implemented": False,
        "runtime_owned_behavior_represented_by_external_profile_json": False,
        "schema_name": SCHEMA_NAME,
        "sidecar_required": True,
        "status": STATUS,
        "transform_implementation_exists": False,
        "transform_implemented": False,
        "webserial_transport_implemented": False,
    }
    for key, value in expected_flags.items():
        if contract.get(key) != value:
            fail(f"{key} must be {value!r}")

    if contract.get("design_sections") != REQUIRED_DESIGN_SECTIONS:
        fail("design_sections drifted")
    input_artifacts = contract.get("input_artifacts")
    if not isinstance(input_artifacts, list):
        fail("input_artifacts must be a list")
    artifact_ids = [entry.get("artifact_id") for entry in input_artifacts if isinstance(entry, dict)]
    if artifact_ids != REQUIRED_INPUT_ARTIFACT_IDS:
        fail("input_artifacts drifted")

    for section in REQUIRED_DESIGN_SECTIONS:
        if section not in contract:
            fail(f"contract missing design section: {section}")


def validate_fixture(contract: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(contract)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated transform design contract JSON")
    committed = load_json_object(FIXTURE_PATH)
    if committed != contract:
        fail("committed fixture JSON object drifted from regenerated contract")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the docs/tools-only Glyph clean-room adapter transform design contract."
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
        validate_contract(contract)
        validate_fixture(contract)
        validate_doc()
    except (OSError, CleanRoomAdapterTransformDesignContractError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("transform_implemented=false")
        print("external_json_generated=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("transform_implemented=false")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
