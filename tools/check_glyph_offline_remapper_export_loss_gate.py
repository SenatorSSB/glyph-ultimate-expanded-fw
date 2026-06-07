#!/usr/bin/env python3
"""Validate the offline remapper export-loss aggregate gate packet."""

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
    / "docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_export_loss_gate"
REPORT_VERSION = 1
STATUS = "external_remapper_round_trip_not_safe_adapter_blocked"
HARDWARE_STATUS = "not_new_hardware_result"

SOURCE_PACKETS = {
    "experiment_result": {
        "checker_path": "tools/check_glyph_offline_remapper_experiment_result.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_experiment_result_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_experiment_result_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_experiment_result",
        "status": "manual_no_device_experiment_completed_with_warnings",
        "evidence_role": "manual no-device import/export experiment completed",
    },
    "binding_loss_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_binding_loss_classification.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_binding_loss_classification_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_binding_loss_classification",
        "status": "docs_tools_binding_loss_classification",
        "evidence_role": "binding-loss classification for active-profile round-trip safety",
    },
    "socd_drift_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_socd_drift_classification.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_socd_drift_classification_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_socd_drift_classification",
        "status": "docs_tools_socd_drift_classification",
        "evidence_role": "SOCD drift classification for external export drift",
    },
    "metadata_diff_report": {
        "checker_path": "tools/check_glyph_offline_remapper_metadata_diff_report.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_metadata_diff_report_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_metadata_diff_report_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_metadata_diff_report",
        "status": "docs_tools_metadata_diff",
        "evidence_role": "metadata diff report for non-runtime evidence only",
    },
    "export_diff_gate": {
        "checker_path": "tools/check_glyph_offline_remapper_export_diff_gate.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_export_diff_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_diff_gate_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_export_diff_gate",
        "status": "import_export_succeeded_with_warnings_adapter_blocked",
        "evidence_role": "aggregate export diff gate for blocked adapter interpretation",
    },
}

GATE_INTERPRETATION = [
    "manual no-device import/export experiment completed",
    "binding-loss classification is adapter-blocking",
    "SOCD drift classification is adapter-blocking",
    "metadata diff report remains metadata-only evidence",
    "export diff gate keeps runtime-owned behavior unrepresented",
    "active profile round-trip is not safe",
    "adapter implementation remains blocked",
    "external JSON generation remains blocked",
]

ALLOWED_NEXT_WORK = [
    "docs/tools-only adapter candidate schema planning with explicit non-round-trip caveat",
    "manual repeat experiment with browser/version recorded",
    "source audit of external remapper import/export code",
    "clean-room transform design, not implementation",
]

DISALLOWED_WITHOUT_APPROVAL = [
    "adapter implementation",
    "external-remapper-compatible JSON generation",
    "device write/WebSerial",
    "protobuf binary generation",
    "runtime-loaded config",
    "official compatibility claim",
    "hardware validation claim",
]

REQUIRED_DOC_PHRASES = (
    "external_remapper_round_trip_not_safe_adapter_blocked",
    "active_profile_round_trip_safe = false",
    "adapter_implementation_allowed = false",
    "external_json_generation_allowed = false",
    "manual_import_experiment_completed = true",
    "manual_export_round_trip_has_blocking_loss = true",
    "runtime_owned_behavior_represented = false",
    "docs/tools-only adapter candidate schema planning with explicit non-round-trip caveat",
    "manual repeat experiment with browser/version recorded",
    "source audit of external remapper import/export code",
    "clean-room transform design, not implementation",
    "adapter implementation",
    "external-remapper-compatible json generation",
    "device write/webserial",
    "protobuf binary generation",
    "runtime-loaded config",
    "official compatibility claim",
    "hardware validation claim",
    "not official compatibility",
    "not hardware validation",
)


class OfflineRemapperExportLossGateError(ValueError):
    """Raised when the aggregate export-loss gate drifts."""


def fail(message: str) -> None:
    raise OfflineRemapperExportLossGateError(message)


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


def without_embedded_hashes(payload: dict[str, Any]) -> dict[str, Any]:
    copied = json.loads(json.dumps(payload))
    reports = copied.get("source_packets", {})
    if isinstance(reports, dict):
        for report in reports.values():
            if isinstance(report, dict):
                report.pop("doc_sha256", None)
                report.pop("fixture_sha256", None)
    return copied


def source_packet_reports() -> dict[str, dict[str, str]]:
    reports: dict[str, dict[str, str]] = {}
    for name, packet in SOURCE_PACKETS.items():
        checker_path = REPO_ROOT / packet["checker_path"]
        doc_path = REPO_ROOT / packet["doc_path"]
        fixture_path = REPO_ROOT / packet["fixture_path"]
        for path in (checker_path, doc_path, fixture_path):
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
            "doc_path": packet["doc_path"],
            "doc_sha256": sha256(doc_path),
            "evidence_role": packet["evidence_role"],
            "fixture_path": packet["fixture_path"],
            "fixture_sha256": sha256(fixture_path),
            "schema_name": packet["schema_name"],
            "status": packet["status"],
        }
    return reports


def validate_source_packets() -> tuple[dict[str, Any], ...]:
    experiment_result = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["experiment_result"]["fixture_path"]
    )
    binding_loss = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["binding_loss_classification"]["fixture_path"]
    )
    socd_drift = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["socd_drift_classification"]["fixture_path"]
    )
    metadata_diff = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["metadata_diff_report"]["fixture_path"]
    )
    export_diff_gate = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["export_diff_gate"]["fixture_path"]
    )

    if binding_loss.get("loss_severity") != "adapter_blocking_loss":
        fail("binding-loss classification must remain adapter_blocking_loss")
    if binding_loss.get("round_trip_safe_for_active_profile") is not False:
        fail("binding-loss classification must keep round-trip safety false")

    if socd_drift.get("drift_severity") != "adapter_blocking_drift":
        fail("SOCD drift classification must remain adapter_blocking_drift")

    if metadata_diff.get("metadata_only") is not True:
        fail("metadata diff report must remain metadata_only=true")
    if metadata_diff.get("firmware_behavior_validated") is not False:
        fail("metadata diff report must keep firmware_behavior_validated=false")

    if export_diff_gate.get("import_export_succeeded") is not True:
        fail("export diff gate must keep import_export_succeeded=true")
    if export_diff_gate.get("warnings_present") is not True:
        fail("export diff gate must keep warnings_present=true")
    if export_diff_gate.get("runtime_owned_behavior_represented") is not False:
        fail("export diff gate must keep runtime_owned_behavior_represented=false")
    if export_diff_gate.get("adapter_implemented") is not False:
        fail("export diff gate must keep adapter_implemented=false")

    experiment_flags = experiment_result.get("experiment_flags")
    if not isinstance(experiment_flags, dict):
        fail("experiment_result.experiment_flags must be an object")
    if experiment_flags.get("device_connected") is not False:
        fail("experiment result must keep device_connected=false")
    if experiment_flags.get("save_to_device_clicked") is not False:
        fail("experiment result must keep save_to_device_clicked=false")
    if experiment_flags.get("webserial_access_granted") is not False:
        fail("experiment result must keep webserial_access_granted=false")

    return experiment_result, binding_loss, socd_drift, metadata_diff, export_diff_gate


def build_gate_data() -> dict[str, Any]:
    (
        _experiment_result,
        binding_loss,
        socd_drift,
        metadata_diff,
        export_diff_gate,
    ) = validate_source_packets()

    return {
        "active_profile_round_trip_safe": False,
        "adapter_implementation_allowed": False,
        "allowed_next_work": ALLOWED_NEXT_WORK,
        "disallowed_without_approval": DISALLOWED_WITHOUT_APPROVAL,
        "export_diff_gate_summary": {
            "import_export_succeeded": export_diff_gate["import_export_succeeded"],
            "runtime_owned_behavior_represented": export_diff_gate[
                "runtime_owned_behavior_represented"
            ],
            "status": export_diff_gate["status"],
            "warnings_present": export_diff_gate["warnings_present"],
        },
        "external_json_generation_allowed": False,
        "gate_interpretation": GATE_INTERPRETATION,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "manual_export_round_trip_has_blocking_loss": True,
        "manual_import_experiment_completed": True,
        "metadata_diff_summary": {
            "comparison_summary_text": metadata_diff["comparison_summary"]["summary"],
            "firmware_behavior_validated": metadata_diff["firmware_behavior_validated"],
            "metadata_only": metadata_diff["metadata_only"],
            "status": metadata_diff["status"],
        },
        "official_compatibility_claimed": False,
        "report_version": REPORT_VERSION,
        "runtime_owned_behavior_represented": False,
        "schema_name": SCHEMA_NAME,
        "source_packets": source_packet_reports(),
        "status": STATUS,
        "supporting_classifications": {
            "binding_loss": {
                "loss_severity": binding_loss["loss_severity"],
                "round_trip_safe_for_active_profile": binding_loss[
                    "round_trip_safe_for_active_profile"
                ],
                "summary": binding_loss["binding_loss_summary"],
            },
            "socd_drift": {
                "drift_severity": socd_drift["drift_severity"],
                "summary": socd_drift["socd_drift_summary"],
            },
        },
    }


def validate_top_level(gate: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "report_version": REPORT_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "active_profile_round_trip_safe": False,
        "adapter_implementation_allowed": False,
        "external_json_generation_allowed": False,
        "manual_import_experiment_completed": True,
        "manual_export_round_trip_has_blocking_loss": True,
        "runtime_owned_behavior_represented": False,
        "official_compatibility_claimed": False,
        "hardware_validation_claimed": False,
        "gate_interpretation": GATE_INTERPRETATION,
        "allowed_next_work": ALLOWED_NEXT_WORK,
        "disallowed_without_approval": DISALLOWED_WITHOUT_APPROVAL,
    }
    for key, value in expected.items():
        if gate.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_source_packet_reports(gate: dict[str, Any]) -> None:
    reports = gate.get("source_packets")
    if not isinstance(reports, dict):
        fail("source_packets must be an object")
    if set(reports) != set(SOURCE_PACKETS):
        fail("source_packets keys drifted")
    for name, packet in SOURCE_PACKETS.items():
        report = reports.get(name)
        if not isinstance(report, dict):
            fail(f"source_packets.{name} must be an object")
        for field in ("checker_path", "doc_path", "fixture_path", "schema_name", "status"):
            if report.get(field) != packet[field]:
                fail(f"source_packets.{name}.{field} must be {packet[field]!r}")
        if report.get("evidence_role") != packet["evidence_role"]:
            fail(f"source_packets.{name}.evidence_role drifted")


def validate_supporting_sections(gate: dict[str, Any]) -> None:
    export_summary = gate.get("export_diff_gate_summary")
    if not isinstance(export_summary, dict):
        fail("export_diff_gate_summary must be an object")
    expected_export = {
        "status": SOURCE_PACKETS["export_diff_gate"]["status"],
        "import_export_succeeded": True,
        "warnings_present": True,
        "runtime_owned_behavior_represented": False,
    }
    for key, value in expected_export.items():
        if export_summary.get(key) != value:
            fail(f"export_diff_gate_summary.{key} must be {value!r}")

    metadata_summary = gate.get("metadata_diff_summary")
    if not isinstance(metadata_summary, dict):
        fail("metadata_diff_summary must be an object")
    if metadata_summary.get("status") != SOURCE_PACKETS["metadata_diff_report"]["status"]:
        fail("metadata_diff_summary.status drifted")
    if not isinstance(metadata_summary.get("comparison_summary_text"), str):
        fail("metadata_diff_summary.comparison_summary_text must be a string")
    if metadata_summary.get("metadata_only") is not True:
        fail("metadata_diff_summary.metadata_only must be true")
    if metadata_summary.get("firmware_behavior_validated") is not False:
        fail("metadata_diff_summary.firmware_behavior_validated must be false")

    supporting = gate.get("supporting_classifications")
    if not isinstance(supporting, dict):
        fail("supporting_classifications must be an object")
    if set(supporting) != {"binding_loss", "socd_drift"}:
        fail("supporting_classifications keys drifted")

    binding_loss = supporting.get("binding_loss")
    if not isinstance(binding_loss, dict):
        fail("supporting_classifications.binding_loss must be an object")
    if binding_loss.get("loss_severity") != "adapter_blocking_loss":
        fail("supporting_classifications.binding_loss.loss_severity drifted")
    if binding_loss.get("round_trip_safe_for_active_profile") is not False:
        fail(
            "supporting_classifications.binding_loss.round_trip_safe_for_active_profile must be false"
        )

    socd_drift = supporting.get("socd_drift")
    if not isinstance(socd_drift, dict):
        fail("supporting_classifications.socd_drift must be an object")
    if socd_drift.get("drift_severity") != "adapter_blocking_drift":
        fail("supporting_classifications.socd_drift.drift_severity drifted")


def validate_fixture(gate: dict[str, Any]) -> None:
    committed = load_json_object(FIXTURE_PATH)
    if without_embedded_hashes(committed) != without_embedded_hashes(gate):
        fail("committed fixture JSON object drifted outside embedded source hashes")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_component_checkers() -> None:
    for packet in SOURCE_PACKETS.values():
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
            "Validate the committed offline remapper export-loss aggregate gate "
            "against the existing experiment, diff, and classification packets."
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
        gate = build_gate_data()
        if args.json:
            print(canonical_json_text(gate), end="")
            return 0
        validate_top_level(gate)
        validate_source_packet_reports(gate)
        validate_supporting_sections(gate)
        validate_fixture(gate)
        validate_doc()
        validate_component_checkers()
    except (OSError, OfflineRemapperExportLossGateError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print("active_profile_round_trip_safe=false")
        print("adapter_implementation_allowed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print("active_profile_round_trip_safe=false")
    print("adapter_implementation_allowed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
