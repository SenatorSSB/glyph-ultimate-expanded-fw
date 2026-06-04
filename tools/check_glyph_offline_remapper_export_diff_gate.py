#!/usr/bin/env python3
"""Validate the offline remapper export diff gate packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_offline_remapper_export_diff_gate_2026-06-04.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_export_diff_gate_2026-06-04.json"
)
EXPORTED_ARTIFACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_export_diff_gate"
GATE_VERSION = 1
STATUS = "import_export_succeeded_with_warnings_adapter_blocked"
HARDWARE_STATUS = "not_new_hardware_result"

COMPONENTS = {
    "experiment_result": {
        "checker_path": "tools/check_glyph_offline_remapper_experiment_result.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_experiment_result_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_experiment_result_2026-06-04.json",
        "evidence_role": "import/export succeeded with warnings and no-device boundary",
        "status": "manual_no_device_experiment_completed_with_warnings",
    },
    "structural_diff": {
        "checker_path": "tools/check_glyph_offline_remapper_export_structural_diff.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_export_structural_diff_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_export_structural_diff_2026-06-04.json",
        "evidence_role": "structural diff exists",
        "status": "docs_tools_structural_diff",
    },
    "ultimate_diff_report": {
        "checker_path": "tools/check_glyph_offline_remapper_ultimate_diff_report.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_ultimate_diff_report_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_ultimate_diff_report_2026-06-04.json",
        "evidence_role": "Ultimate profile diff exists",
        "status": "docs_tools_ultimate_profile_diff",
    },
    "metadata_diff_report": {
        "checker_path": "tools/check_glyph_offline_remapper_metadata_diff_report.py",
        "doc_path": "docs/calibration/glyph_offline_remapper_metadata_diff_report_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_offline_remapper_metadata_diff_report_2026-06-04.json",
        "evidence_role": "metadata diff exists",
        "status": "docs_tools_metadata_diff",
    },
}

EXPECTED_FLAGS = {
    "adapter_generation_allowed_without_approval": False,
    "adapter_implemented": False,
    "device_write_allowed": False,
    "hardware_validation_claimed": False,
    "import_export_succeeded": True,
    "no_device_boundary_preserved": True,
    "official_configurator_compatibility_claimed": False,
    "protobuf_binary_generation_allowed": False,
    "runtime_loaded_config_allowed": False,
    "runtime_owned_behavior_represented": False,
    "webserial_allowed": False,
    "warnings_present": True,
}

ALLOWED_NEXT_WORK = [
    "docs/tools-only adapter candidate schema planning",
    "no-device adapter prototype planning, not implementation",
    "further structural diff improvements",
    "manual repeated experiment with browser/OS/version recorded",
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

GATE_INTERPRETATION = [
    "import/export succeeded with warnings",
    "no-device boundary preserved",
    "exported artifact recorded",
    "structural diff exists",
    "Ultimate profile diff exists",
    "metadata diff exists",
    "runtime-owned identity behavior is not represented by external remapper profile-level JSON",
    "adapter implementation remains blocked",
    "official configurator compatibility remains unclaimed",
    "device write/WebSerial remains blocked",
    "protobuf binary generation remains blocked",
    "runtime-loaded config remains blocked",
]

REQUIRED_DOC_PHRASES = (
    "import/export succeeded with warnings",
    "adapter remains blocked",
    "runtime-owned behavior not represented",
    "not official compatibility",
    "not device write",
    "not WebSerial",
    "not protobuf binary generation",
    "not hardware validation",
)


class OfflineRemapperExportDiffGateError(ValueError):
    """Raised when the export diff gate drifts from required boundaries."""


def fail(message: str) -> None:
    raise OfflineRemapperExportDiffGateError(message)


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


def component_reports() -> dict[str, dict[str, str]]:
    reports: dict[str, dict[str, str]] = {}
    for name, component in COMPONENTS.items():
        checker_path = REPO_ROOT / component["checker_path"]
        doc_path = REPO_ROOT / component["doc_path"]
        fixture_path = REPO_ROOT / component["fixture_path"]
        for path in (checker_path, doc_path, fixture_path):
            if not path.exists():
                fail(f"referenced component path is missing: {display(path)}")
        reports[name] = {
            "checker_path": component["checker_path"],
            "doc_path": component["doc_path"],
            "doc_sha256": sha256(doc_path),
            "evidence_role": component["evidence_role"],
            "fixture_path": component["fixture_path"],
            "fixture_sha256": sha256(fixture_path),
            "status": component["status"],
        }
    return reports


def build_gate_data() -> dict[str, Any]:
    if not EXPORTED_ARTIFACT_PATH.exists():
        fail(f"exported artifact is missing: {display(EXPORTED_ARTIFACT_PATH)}")
    return {
        "adapter_generation_allowed_without_approval": False,
        "adapter_implemented": False,
        "allowed_next_work": ALLOWED_NEXT_WORK,
        "component_reports": component_reports(),
        "device_write_allowed": False,
        "disallowed_without_approval": DISALLOWED_WITHOUT_APPROVAL,
        "exported_artifact": {
            "path": display(EXPORTED_ARTIFACT_PATH),
            "sha256": sha256(EXPORTED_ARTIFACT_PATH),
        },
        "gate_interpretation": GATE_INTERPRETATION,
        "gate_version": GATE_VERSION,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "import_export_succeeded": True,
        "metadata_diff_exists": True,
        "no_device_boundary_preserved": True,
        "official_configurator_compatibility_claimed": False,
        "protobuf_binary_generation_allowed": False,
        "runtime_loaded_config_allowed": False,
        "runtime_owned_behavior_represented": False,
        "schema_name": SCHEMA_NAME,
        "status": STATUS,
        "structural_diff_exists": True,
        "ultimate_profile_diff_exists": True,
        "warnings_present": True,
        "webserial_allowed": False,
    }


def validate_top_level(gate: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "gate_version": GATE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "structural_diff_exists": True,
        "ultimate_profile_diff_exists": True,
        "metadata_diff_exists": True,
    }
    for key, value in expected.items():
        if gate.get(key) != value:
            fail(f"{key} must be {value!r}")
    for key, value in EXPECTED_FLAGS.items():
        if gate.get(key) != value:
            fail(f"{key} must be {value!r}")
    if gate.get("allowed_next_work") != ALLOWED_NEXT_WORK:
        fail("allowed_next_work drifted")
    if gate.get("disallowed_without_approval") != DISALLOWED_WITHOUT_APPROVAL:
        fail("disallowed_without_approval drifted")
    if gate.get("gate_interpretation") != GATE_INTERPRETATION:
        fail("gate_interpretation drifted")


def validate_component_reports(gate: dict[str, Any]) -> None:
    reports = gate.get("component_reports")
    if not isinstance(reports, dict):
        fail("component_reports must be an object")
    if set(reports) != set(COMPONENTS):
        fail("component_reports keys drifted")
    for name, component in COMPONENTS.items():
        report = reports.get(name)
        if not isinstance(report, dict):
            fail(f"component_reports.{name} must be an object")
        for field in ("checker_path", "doc_path", "fixture_path"):
            expected = component[field]
            if report.get(field) != expected:
                fail(f"component_reports.{name}.{field} must be {expected!r}")
            if not (REPO_ROOT / expected).exists():
                fail(f"referenced path is missing: {expected}")
        if report.get("status") != component["status"]:
            fail(f"component_reports.{name}.status drifted")


def validate_fixture(gate: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(gate)
    if committed_text != expected_text:
        fail("committed gate fixture does not exactly match regenerated gate data")
    committed = load_json_object(FIXTURE_PATH)
    if committed != gate:
        fail("committed gate fixture JSON object drifted")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_component_checkers() -> None:
    for component in COMPONENTS.values():
        checker = component["checker_path"]
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


def main() -> int:
    print(SCHEMA_NAME)
    try:
        gate = build_gate_data()
        validate_top_level(gate)
        validate_component_reports(gate)
        validate_fixture(gate)
        validate_doc()
        validate_component_checkers()
    except (OSError, OfflineRemapperExportDiffGateError, ValueError) as exc:
        print("status=FAIL")
        print("import_export_succeeded=true")
        print("warnings_present=true")
        print("adapter_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("import_export_succeeded=true")
    print("warnings_present=true")
    print("adapter_implemented=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
