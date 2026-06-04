#!/usr/bin/env python3
"""Validate the external remapper source audit readiness gate packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_external_remapper_source_audit_readiness_gate_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/"
    "glyph_external_remapper_source_audit_readiness_gate_2026-06-04.json"
)

SCHEMA_NAME = "glyph_external_remapper_source_audit_readiness_gate"
GATE_VERSION = 1
STATUS = "ready_for_source_audit_planning_only"
HARDWARE_STATUS = "not_new_hardware_result"

COMPONENT_PACKETS = {
    "import_export_audit_scope": {
        "checker_path": "tools/check_glyph_external_remapper_import_export_audit_scope.py",
        "doc_path": "docs/calibration/glyph_external_remapper_import_export_audit_scope_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_external_remapper_import_export_audit_scope_2026-06-04.json",
        "schema_name": "glyph_external_remapper_import_export_audit_scope",
        "status": "source_audit_scope_only",
        "evidence_role": "source for audit target scope and non-authoritative external-source caveat",
    },
    "import_export_audit_checklist": {
        "checker_path": "tools/check_glyph_external_remapper_import_export_audit_checklist.py",
        "doc_path": "docs/calibration/glyph_external_remapper_import_export_audit_checklist_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_external_remapper_import_export_audit_checklist_2026-06-04.json",
        "schema_name": "glyph_external_remapper_import_export_audit_checklist",
        "status": "planned_not_executed",
        "evidence_role": "source for the stable audit item list and explicit audit-not-executed status",
    },
    "license_code_reuse_blocker": {
        "checker_path": "tools/check_glyph_external_remapper_license_code_reuse_blocker.py",
        "doc_path": "docs/calibration/glyph_external_remapper_license_code_reuse_blocker_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_external_remapper_license_code_reuse_blocker_2026-06-04.json",
        "schema_name": "glyph_external_remapper_license_code_reuse_blocker",
        "status": "code_reuse_blocked_pending_license_review_and_user_approval",
        "evidence_role": "source for no-code-copy, no-dependency, and license-review-not-completed blockers",
    },
    "clean_room_transform_design_gate": {
        "checker_path": "tools/check_glyph_clean_room_adapter_transform_design_gate.py",
        "doc_path": "docs/calibration/glyph_clean_room_adapter_transform_design_gate_2026-06-04.md",
        "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_gate_2026-06-04.json",
        "schema_name": "glyph_clean_room_adapter_transform_design_gate",
        "status": "transform_design_ready_implementation_blocked",
        "evidence_role": "source for clean-room transform-design readiness and implementation-blocked status",
    },
}

ALLOWED_NEXT_WORK = [
    "perform source audit and record non-authoritative findings",
    "repeat no-device experiment with browser/version recorded",
    "implementation proposal requiring explicit user approval",
]

DISALLOWED_WITHOUT_APPROVAL = [
    "code reuse",
    "adding dependency",
    "adapter implementation",
    "external JSON generation",
    "WebSerial/device write",
    "protobuf binary generation",
    "official compatibility claim",
    "hardware validation",
]

GATE_INTERPRETATION = [
    "source audit plan ready",
    "audit not executed",
    "external source not authority",
    "no code copied",
    "no dependency added",
    "license review not completed",
    "adapter implementation blocked",
    "external JSON generation blocked",
    "clean-room transform design remains docs/tools-only",
]

REQUIRED_DOC_PHRASES = (
    "ready_for_source_audit_planning_only",
    "Source audit plan ready.",
    "Audit not executed.",
    "External source not authority.",
    "No code copied.",
    "No dependency added.",
    "License review not completed.",
    "Adapter implementation blocked.",
    "External JSON generation blocked.",
    "Clean-room transform design remains docs/tools-only.",
    "perform source audit and record non-authoritative findings",
    "repeat no-device experiment with browser/version recorded",
    "implementation proposal requiring explicit user approval",
    "code reuse",
    "adding dependency",
    "adapter implementation",
    "external JSON generation",
    "WebSerial/device write",
    "protobuf binary generation",
    "official compatibility claim",
    "hardware validation",
    "This gate does not execute the source audit.",
    "This gate does not copy external source code.",
    "This gate does not add an external dependency.",
    "This gate does not implement an adapter.",
    "This gate does not generate external JSON.",
    "This gate does not add transform code.",
    "This gate does not implement runtime-loaded config.",
    "This gate does not implement serial/device write behavior.",
    "This gate does not implement WebSerial transport.",
    "This gate does not implement protobuf binary generation.",
    "This gate does not claim official configurator compatibility.",
    "This gate does not claim hardware validation.",
    "This gate does not promote external source to authority.",
)


class ExternalRemapperSourceAuditReadinessGateError(ValueError):
    """Raised when the source audit readiness gate drifts."""


def fail(message: str) -> None:
    raise ExternalRemapperSourceAuditReadinessGateError(message)


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
    scope = load_json_object(REPO_ROOT / COMPONENT_PACKETS["import_export_audit_scope"]["fixture_path"])
    checklist = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["import_export_audit_checklist"]["fixture_path"]
    )
    blocker = load_json_object(REPO_ROOT / COMPONENT_PACKETS["license_code_reuse_blocker"]["fixture_path"])
    transform_gate = load_json_object(
        REPO_ROOT / COMPONENT_PACKETS["clean_room_transform_design_gate"]["fixture_path"]
    )

    audit_targets = scope.get("audit_targets")
    if not isinstance(audit_targets, list) or len(audit_targets) != 17:
        fail("import/export audit scope must keep exactly 17 audit_targets")
    if scope.get("external_source_promoted_to_authority") is not False:
        fail("import/export audit scope must keep external_source_promoted_to_authority=false")

    checklist_items = checklist.get("checklist_items")
    if not isinstance(checklist_items, list) or len(checklist_items) != 17:
        fail("import/export audit checklist must keep exactly 17 items")
    if checklist.get("audit_executed") is not False:
        fail("import/export audit checklist must keep audit_executed=false")

    if blocker.get("code_reuse_approved") is not False:
        fail("license/code-reuse blocker must keep code_reuse_approved=false")
    if blocker.get("external_dependency_added") is not False:
        fail("license/code-reuse blocker must keep external_dependency_added=false")
    if blocker.get("license_review_completed") is not False:
        fail("license/code-reuse blocker must keep license_review_completed=false")

    if transform_gate.get("transform_design_ready") is not True:
        fail("clean-room transform design gate must keep transform_design_ready=true")
    if transform_gate.get("transform_implementation_blocked") is not True:
        fail(
            "clean-room transform design gate must keep transform_implementation_blocked=true"
        )
    if transform_gate.get("external_json_generation_blocked") is not True:
        fail(
            "clean-room transform design gate must keep external_json_generation_blocked=true"
        )

    return {
        "import_export_audit_scope_summary": {
            "audit_targets": len(audit_targets),
            "external_source_promoted_to_authority": False,
            "status": scope.get("status"),
        },
        "import_export_audit_checklist_summary": {
            "audit_executed": False,
            "checklist_items": len(checklist_items),
            "status": checklist.get("status"),
        },
        "license_code_reuse_blocker_summary": {
            "code_reuse_approved": False,
            "external_dependency_added": False,
            "license_review_completed": False,
            "status": blocker.get("status"),
        },
        "clean_room_transform_design_gate_summary": {
            "external_json_generation_blocked": True,
            "status": transform_gate.get("status"),
            "transform_design_ready": True,
            "transform_implementation_blocked": True,
        },
    }


def validate_fixture(fixture: dict[str, Any]) -> None:
    expected_scalars = {
        "schema_name": SCHEMA_NAME,
        "gate_version": GATE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "source_audit_plan_ready": True,
        "audit_executed": False,
        "code_reuse_approved": False,
        "external_dependency_added": False,
        "adapter_implementation_blocked": True,
        "external_json_generation_blocked": True,
        "external_source_promoted_to_authority": False,
        "official_configurator_compatibility_claimed": False,
        "hardware_validation_claimed": False,
        "license_review_completed": False,
        "clean_room_transform_design_docs_tools_only": True,
    }
    for key, value in expected_scalars.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")

    if fixture.get("allowed_next_work") != ALLOWED_NEXT_WORK:
        fail("allowed_next_work drifted from required stable order")
    if fixture.get("disallowed_without_approval") != DISALLOWED_WITHOUT_APPROVAL:
        fail("disallowed_without_approval drifted from required stable order")
    if fixture.get("gate_interpretation") != GATE_INTERPRETATION:
        fail("gate_interpretation drifted from required stable order")

    component_reports = component_packet_reports()
    if fixture.get("component_packets") != component_reports:
        fail("component_packets must match the current committed component packet reports")

    findings = supporting_findings()
    if fixture.get("supporting_findings") != findings:
        fail("supporting_findings must match the committed component packet summaries")

    report = fixture.get("validation_report")
    expected_report = {
        "checker_path": "tools/check_glyph_external_remapper_source_audit_readiness_gate.py",
        "component_checkers_required_to_pass": True,
        "doc_path": (
            "docs/calibration/"
            "glyph_external_remapper_source_audit_readiness_gate_2026-06-04.md"
        ),
        "fixture_path": (
            "docs/calibration/fixtures/"
            "glyph_external_remapper_source_audit_readiness_gate_2026-06-04.json"
        ),
        "hardware_status": HARDWARE_STATUS,
        "source_audit_plan_ready": True,
        "validation_scope": (
            "docs_tools_fixtures_only_external_remapper_source_audit_readiness_gate"
        ),
    }
    if report != expected_report:
        fail("validation_report must match the committed readiness gate metadata")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_source_audit_readiness_gate")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_fixture(fixture)
        validate_doc()
    except (
        OSError,
        ExternalRemapperSourceAuditReadinessGateError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print("source_audit_plan_ready=true")
        print("audit_executed=false")
        print("code_reuse_approved=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("source_audit_plan_ready=true")
    print("audit_executed=false")
    print("code_reuse_approved=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("external_dependency_added=false")
    print("adapter_implementation_blocked=true")
    print("external_json_generation_blocked=true")
    print("external_source_promoted_to_authority=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
