#!/usr/bin/env python3
"""Validate the external remapper import/export source audit scope packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_external_remapper_import_export_audit_scope_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_import_export_audit_scope_2026-06-04.json"
)

SCHEMA_NAME = "glyph_external_remapper_import_export_audit_scope"
SCOPE_VERSION = 1
STATUS = "source_audit_scope_only"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_AUDIT_TARGETS = (
    "repository metadata",
    "license",
    "README/docs",
    "file inventory",
    "JSON import path",
    "JSON export path",
    "profile normalization logic",
    "buttonRemapping handling",
    "activates handling",
    "SOCD pair handling",
    "RGB config handling",
    "menu icon/default metadata handling",
    "protobuf encode/decode path",
    "WebSerial load/save path",
    "custom profile/modifier representation",
    "default config payload provenance",
    "browser storage/localStorage behavior",
)

REQUIRED_FORBIDDEN_INTERPRETATIONS = (
    "external source authority",
    "official configurator compatibility claim",
    "hardware validation claimed",
    "external source code copied into repo",
    "external dependency added",
    "adapter implemented",
    "external JSON generated",
    "transform code added",
    "runtime-loaded config implemented",
    "serial/device write behavior implemented",
    "WebSerial transport implemented",
    "protobuf binary generation implemented",
    "firmware runtime behavior changed",
    "active profile artifact changed",
    "exported experiment artifact changed",
)

FALSE_FLAGS = (
    "active_profile_artifact_changed",
    "adapter_implemented",
    "code_copied_into_repo",
    "external_dependency_added",
    "external_json_generated",
    "external_source_promoted_to_authority",
    "exported_experiment_artifact_changed",
    "official_configurator_compatibility_claimed",
    "protobuf_binary_generation_implemented",
    "runtime_loaded_config_implemented",
    "runtime_source_changed",
    "serial_device_write_behavior_implemented",
    "transform_code_added",
    "webserial_transport_implemented",
)

REQUIRED_DOC_PHRASES = (
    "source_audit_scope_only",
    "repository metadata",
    "JSON import path",
    "JSON export path",
    "buttonRemapping handling",
    "activates handling",
    "SOCD pair handling",
    "RGB config handling",
    "menu icon/default metadata handling",
    "protobuf encode/decode path",
    "WebSerial load/save path",
    "custom profile/modifier representation",
    "default config payload provenance",
    "browser storage/localStorage behavior",
    "This packet does not promote external source to authority.",
    "This packet does not copy external source code into this repository.",
    "This packet does not add an external dependency.",
    "This packet does not implement an adapter.",
    "This packet does not generate external JSON.",
    "This packet does not add transform code.",
    "This packet does not implement runtime-loaded config.",
    "This packet does not implement serial/device write behavior.",
    "This packet does not implement WebSerial transport.",
    "This packet does not implement protobuf binary generation.",
    "This packet does not claim official configurator compatibility.",
    "This packet does not claim hardware validation.",
)


class ExternalRemapperImportExportAuditScopeError(ValueError):
    """Raised when the import/export audit scope drifts."""


def fail(message: str) -> None:
    raise ExternalRemapperImportExportAuditScopeError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_exact_string_list(payload: dict[str, Any], key: str, expected: tuple[str, ...]) -> None:
    value = payload.get(key)
    if not isinstance(value, list):
        fail(f"{key} must be a list")
    if tuple(value) != expected:
        fail(f"{key} drifted from required stable order")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{key}[{index}] must be a non-empty string")


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "scope_version": SCOPE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")
    for key in FALSE_FLAGS:
        if fixture.get(key) is not False:
            fail(f"{key} must be false")


def validate_fixture(fixture: dict[str, Any]) -> None:
    validate_top_level(fixture)
    require_exact_string_list(fixture, "audit_targets", REQUIRED_AUDIT_TARGETS)
    require_exact_string_list(
        fixture,
        "forbidden_interpretations",
        REQUIRED_FORBIDDEN_INTERPRETATIONS,
    )

    report = fixture.get("validation_report")
    if not isinstance(report, dict):
        fail("validation_report must be an object")
    expected_report_paths = {
        "checker_path": "tools/check_glyph_external_remapper_import_export_audit_scope.py",
        "doc_path": "docs/calibration/glyph_external_remapper_import_export_audit_scope_2026-06-04.md",
        "fixture_path": (
            "docs/calibration/fixtures/"
            "glyph_external_remapper_import_export_audit_scope_2026-06-04.json"
        ),
        "hardware_status": HARDWARE_STATUS,
        "validation_scope": "docs_tools_fixtures_only_source_audit_scope",
    }
    for key, value in expected_report_paths.items():
        if report.get(key) != value:
            fail(f"validation_report.{key} must be {value!r}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_import_export_audit_scope")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_fixture(fixture)
        validate_doc()
    except (OSError, ExternalRemapperImportExportAuditScopeError, ValueError) as exc:
        print("status=FAIL")
        print("audit_targets=0")
        print("external_source_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"audit_targets={len(REQUIRED_AUDIT_TARGETS)}")
    print("external_source_promoted_to_authority=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("code_copied_into_repo=false")
    print("external_dependency_added=false")
    print("adapter_implemented=false")
    print("external_json_generated=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
