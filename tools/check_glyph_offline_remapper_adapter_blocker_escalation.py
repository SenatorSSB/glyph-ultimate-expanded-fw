#!/usr/bin/env python3
"""Validate the offline remapper adapter blocker escalation packet."""

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
    / "docs/calibration/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_adapter_blocker_escalation"
REPORT_VERSION = 1
STATUS = "docs_tools_adapter_blocker_escalation"
HARDWARE_STATUS = "not_new_hardware_result"

SOURCE_PACKETS = {
    "export_diff_gate": {
        "checker_path": "tools/check_glyph_offline_remapper_export_diff_gate.py",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_diff_gate_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_export_diff_gate",
        "status": "import_export_succeeded_with_warnings_adapter_blocked",
    },
    "binding_loss_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_binding_loss_classification.py",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_binding_loss_classification",
        "status": "docs_tools_binding_loss_classification",
    },
    "socd_drift_classification": {
        "checker_path": "tools/check_glyph_offline_remapper_socd_drift_classification.py",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json",
        "schema_name": "glyph_offline_remapper_socd_drift_classification",
        "status": "docs_tools_socd_drift_classification",
    },
}

BLOCKER_INTERPRETATION = [
    "adapter implementation remains blocked",
    "external-remapper-compatible JSON generation remains blocked",
    "active profile artifact is not round-trip safe through external remapper export",
    "binding-loss and SOCD drift are adapter-blocking until source audit and transformation strategy exist",
    "no external source authority promotion",
]

FUTURE_ADAPTER_DECISIONS = [
    "target external remapper import only, not export round-trip",
    "use sidecar reports for runtime-owned behavior",
    "avoid using external remapper as a canonical editor for identity-runtime profiles",
]

REQUIRED_FALSE_FLAGS = {
    "adapter_implemented": False,
    "external_remapper_compatible_json_generated": False,
    "external_source_promoted_to_authority": False,
    "hardware_validation_claimed": False,
    "official_compatibility_claimed": False,
    "round_trip_safe_for_active_profile": False,
}

REQUIRED_TRUE_FLAGS = {
    "adapter_implementation_blocked": True,
    "binding_loss_adapter_blocking": True,
    "external_json_generation_blocked": True,
    "socd_drift_adapter_blocking": True,
}

REQUIRED_DOC_PHRASES = (
    "Adapter implementation remains blocked.",
    "External-remapper-compatible JSON generation remains blocked.",
    "Active profile artifact is not round-trip safe through external remapper export.",
    "Binding-loss and SOCD drift are adapter-blocking until source audit and transformation strategy exist.",
    "target external remapper import only, not export round-trip",
    "use sidecar reports for runtime-owned behavior",
    "avoid using external remapper as a canonical editor for identity-runtime profiles",
    "No external source authority promotion.",
    "not official compatibility",
    "not hardware validation",
)


class OfflineRemapperAdapterBlockerEscalationError(ValueError):
    """Raised when the committed adapter blocker escalation drifts."""


def fail(message: str) -> None:
    raise OfflineRemapperAdapterBlockerEscalationError(message)


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
                report.pop("fixture_sha256", None)
    return copied


def source_packet_reports() -> dict[str, dict[str, str]]:
    reports: dict[str, dict[str, str]] = {}
    for name, packet in SOURCE_PACKETS.items():
        checker_path = REPO_ROOT / packet["checker_path"]
        fixture_path = REPO_ROOT / packet["fixture_path"]
        for path in (checker_path, fixture_path):
            if not path.exists():
                fail(f"referenced source packet path is missing: {display(path)}")

        fixture = load_json_object(fixture_path)
        if fixture.get("schema_name") != packet["schema_name"]:
            fail(f"{name} schema_name must be {packet['schema_name']!r}")
        if fixture.get("status") != packet["status"]:
            fail(f"{name} status must be {packet['status']!r}")
        if fixture.get("hardware_status") != HARDWARE_STATUS:
            fail(f"{name} hardware_status must be {HARDWARE_STATUS!r}")

        reports[name] = {
            "checker_path": packet["checker_path"],
            "fixture_path": packet["fixture_path"],
            "fixture_sha256": sha256(fixture_path),
            "schema_name": packet["schema_name"],
            "status": packet["status"],
        }
    return reports


def validate_source_blockers() -> None:
    export_gate = load_json_object(REPO_ROOT / SOURCE_PACKETS["export_diff_gate"]["fixture_path"])
    binding_loss = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["binding_loss_classification"]["fixture_path"]
    )
    socd_drift = load_json_object(
        REPO_ROOT / SOURCE_PACKETS["socd_drift_classification"]["fixture_path"]
    )

    if export_gate.get("adapter_implemented") is not False:
        fail("export diff gate must keep adapter_implemented=false")
    if export_gate.get("runtime_owned_behavior_represented") is not False:
        fail("export diff gate must keep runtime_owned_behavior_represented=false")
    if "external-remapper-compatible JSON generation" not in export_gate.get(
        "disallowed_without_approval", []
    ):
        fail("export diff gate must keep external JSON generation disallowed")

    if binding_loss.get("loss_severity") != "adapter_blocking_loss":
        fail("binding-loss classification must remain adapter_blocking_loss")
    if binding_loss.get("round_trip_safe_for_active_profile") is not False:
        fail("binding-loss classification must keep round-trip safety false")
    if binding_loss.get("external_source_promoted_to_authority") is not False:
        fail("binding-loss classification must not promote external source authority")

    if socd_drift.get("drift_severity") != "adapter_blocking_drift":
        fail("SOCD drift classification must remain adapter_blocking_drift")
    if socd_drift.get("external_source_promoted_to_authority") is not False:
        fail("SOCD drift classification must not promote external source authority")


def build_escalation() -> dict[str, Any]:
    validate_source_blockers()
    return {
        "adapter_implementation_blocked": True,
        "adapter_implemented": False,
        "binding_loss_adapter_blocking": True,
        "blocker_interpretation": BLOCKER_INTERPRETATION,
        "external_json_generation_blocked": True,
        "external_remapper_compatible_json_generated": False,
        "external_source_promoted_to_authority": False,
        "future_adapter_decisions": FUTURE_ADAPTER_DECISIONS,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "official_compatibility_claimed": False,
        "report_version": REPORT_VERSION,
        "round_trip_safe_for_active_profile": False,
        "schema_name": SCHEMA_NAME,
        "socd_drift_adapter_blocking": True,
        "source_packets": source_packet_reports(),
        "status": STATUS,
    }


def validate_top_level(escalation: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "report_version": REPORT_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "blocker_interpretation": BLOCKER_INTERPRETATION,
        "future_adapter_decisions": FUTURE_ADAPTER_DECISIONS,
    }
    for key, value in expected.items():
        if escalation.get(key) != value:
            fail(f"{key} must be {value!r}")
    for key, value in REQUIRED_TRUE_FLAGS.items():
        if escalation.get(key) != value:
            fail(f"{key} must be {value!r}")
    for key, value in REQUIRED_FALSE_FLAGS.items():
        if escalation.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_source_packets(escalation: dict[str, Any]) -> None:
    source_packets = escalation.get("source_packets")
    if not isinstance(source_packets, dict):
        fail("source_packets must be an object")
    if set(source_packets) != set(SOURCE_PACKETS):
        fail("source_packets keys drifted")
    for name, packet in SOURCE_PACKETS.items():
        report = source_packets.get(name)
        if not isinstance(report, dict):
            fail(f"source_packets.{name} must be an object")
        expected = {
            "checker_path": packet["checker_path"],
            "fixture_path": packet["fixture_path"],
            "schema_name": packet["schema_name"],
            "status": packet["status"],
        }
        for key, value in expected.items():
            if report.get(key) != value:
                fail(f"source_packets.{name}.{key} must be {value!r}")


def validate_fixture(escalation: dict[str, Any]) -> None:
    committed = load_json_object(FIXTURE_PATH)
    if without_embedded_hashes(committed) != without_embedded_hashes(escalation):
        fail("committed fixture JSON object drifted outside embedded source hashes")


def validate_doc() -> None:
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in doc_text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_source_checkers() -> None:
    for packet in SOURCE_PACKETS.values():
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
            fail(f"source checker failed: {packet['checker_path']}: {output}")
        if "status=PASS" not in completed.stdout:
            fail(f"source checker did not report PASS: {packet['checker_path']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the committed docs/tools-only offline remapper adapter "
            "blocker escalation packet."
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
        escalation = build_escalation()
        if args.json:
            print(canonical_json_text(escalation), end="")
            return 0
        validate_top_level(escalation)
        validate_source_packets(escalation)
        validate_fixture(escalation)
        validate_doc()
        validate_source_checkers()
    except (
        OSError,
        OfflineRemapperAdapterBlockerEscalationError,
        ValueError,
    ) as exc:
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
