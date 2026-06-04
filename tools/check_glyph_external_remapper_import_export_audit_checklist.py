#!/usr/bin/env python3
"""Validate the external remapper import/export audit checklist packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_external_remapper_import_export_audit_checklist_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/"
    "glyph_external_remapper_import_export_audit_checklist_2026-06-04.json"
)

SCHEMA_NAME = "glyph_external_remapper_import_export_audit_checklist"
CHECKLIST_VERSION = 1
STATUS = "planned_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

EXPECTED_ITEMS = (
    {
        "item_id": "locate_import_handler",
        "category": "locate import handler",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record the exact import entrypoint file(s), function(s), and "
            "unresolved gaps after source inspection."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "locate_export_handler",
        "category": "locate export handler",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record the exact export entrypoint file(s), function(s), and "
            "unresolved gaps after source inspection."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "identify_json_parse_serialize_behavior",
        "category": "identify JSON parse/serialize behavior",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record parse/serialize library usage, strictness, defaults, and "
            "unknowns from inspected source."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "identify_normalization_sanitization_behavior",
        "category": "identify normalization/sanitization behavior",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record normalization, sanitization, coercion, and validation "
            "behavior from inspected source."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_button_remapping_import_export",
        "category": "trace buttonRemapping import/export",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record how buttonRemapping is parsed, normalized, serialized, "
            "preserved, or dropped."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_activates_preservation_or_stripping",
        "category": "trace activates preservation or stripping",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record whether activates data is preserved, transformed, "
            "stripped, or unsupported."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_socd_pair_import_export",
        "category": "trace SOCD pair import/export",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record how SOCD pair structures are parsed, normalized, "
            "serialized, and whether drift occurs."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_rgb_config_import_export",
        "category": "trace RGB config import/export",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record how RGB config data is parsed, normalized, serialized, "
            "preserved, or stripped."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_menu_icon_default_metadata_handling",
        "category": "trace menu icon/default metadata handling",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record how menu icon and default metadata are imported, "
            "serialized, preserved, or stripped."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_protobuf_encode_decode_boundaries",
        "category": "trace protobuf encode/decode boundaries",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record protobuf-related source boundaries, message names, and "
            "unknowns without copying code."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_webserial_load_save_boundaries",
        "category": "trace WebSerial load/save boundaries",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record WebSerial load/save entrypoints, transport boundaries, "
            "and unresolved gaps."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "trace_custom_profile_modifier_representation",
        "category": "trace custom profile/modifier representation",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record how custom profile or modifier structures are represented "
            "and where fidelity limits appear."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "identify_tests_if_any",
        "category": "identify tests, if any",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record exact test files, test scopes, or note that no relevant "
            "tests were found."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "record_exact_commit_audited",
        "category": "record exact commit audited",
        "status": STATUS,
        "requires_source_file": False,
        "result_placeholder": (
            "Record the exact external commit, tag, or immutable revision "
            "audited, or state unknown."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "record_files_inspected",
        "category": "record files inspected",
        "status": STATUS,
        "requires_source_file": True,
        "result_placeholder": (
            "Record the exact file paths, URLs, or UI surfaces inspected "
            "during the audit."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "record_non_authority_caveat",
        "category": "record non-authority caveat",
        "status": STATUS,
        "requires_source_file": False,
        "result_placeholder": (
            "Record that external observations remain non-authoritative "
            "unless explicitly promoted later."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
    {
        "item_id": "record_no_code_copy_caveat",
        "category": "record no-code-copy caveat",
        "status": STATUS,
        "requires_source_file": False,
        "result_placeholder": (
            "Record that no external source code is copied into this "
            "repository as audit evidence."
        ),
        "must_not_copy_code": True,
        "must_not_promote_authority": True,
    },
)

REQUIRED_DOC_PHRASES = (
    "planned_not_executed",
    "audit_executed=false",
    "hardware_status=not_new_hardware_result",
    "must_not_copy_code=true",
    "must_not_promote_authority=true",
    "locate import handler",
    "locate export handler",
    "identify JSON parse/serialize behavior",
    "identify normalization/sanitization behavior",
    "trace buttonRemapping import/export",
    "trace activates preservation or stripping",
    "trace SOCD pair import/export",
    "trace RGB config import/export",
    "trace menu icon/default metadata handling",
    "trace protobuf encode/decode boundaries",
    "trace WebSerial load/save boundaries",
    "trace custom profile/modifier representation",
    "identify tests, if any",
    "record exact commit audited",
    "record files inspected",
    "record non-authority caveat",
    "record no-code-copy caveat",
    "This checklist does not promote external source to authority.",
    "This checklist does not copy external source code into this repository.",
    "This checklist does not claim official configurator compatibility.",
    "This checklist does not claim hardware validation.",
)


class ExternalRemapperImportExportAuditChecklistError(ValueError):
    """Raised when the import/export audit checklist drifts."""


def fail(message: str) -> None:
    raise ExternalRemapperImportExportAuditChecklistError(message)


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


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "checklist_version": CHECKLIST_VERSION,
        "status": STATUS,
        "audit_executed": False,
        "hardware_status": HARDWARE_STATUS,
        "external_source_promoted_to_authority": False,
        "code_copied_into_repo": False,
        "official_configurator_compatibility_claimed": False,
        "hardware_validation_claimed": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_checklist_items(fixture: dict[str, Any]) -> None:
    items = fixture.get("checklist_items")
    if not isinstance(items, list):
        fail("checklist_items must be a list")
    if len(items) != len(EXPECTED_ITEMS):
        fail("checklist_items length drifted")

    required_keys = set(EXPECTED_ITEMS[0].keys())
    for index, expected in enumerate(EXPECTED_ITEMS):
        item = items[index]
        if not isinstance(item, dict):
            fail(f"checklist_items[{index}] must be an object")
        if set(item.keys()) != required_keys:
            fail(f"checklist_items[{index}] keys drifted from required shape")
        for key, value in expected.items():
            if item.get(key) != value:
                fail(f"checklist_items[{index}].{key} must be {value!r}")


def validate_report(fixture: dict[str, Any]) -> None:
    report = fixture.get("validation_report")
    if not isinstance(report, dict):
        fail("validation_report must be an object")
    expected = {
        "checker_path": "tools/check_glyph_external_remapper_import_export_audit_checklist.py",
        "doc_path": "docs/calibration/glyph_external_remapper_import_export_audit_checklist_2026-06-04.md",
        "fixture_path": (
            "docs/calibration/fixtures/"
            "glyph_external_remapper_import_export_audit_checklist_2026-06-04.json"
        ),
        "hardware_status": HARDWARE_STATUS,
        "validation_scope": "docs_tools_fixtures_only_import_export_audit_checklist",
    }
    for key, value in expected.items():
        if report.get(key) != value:
            fail(f"validation_report.{key} must be {value!r}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_import_export_audit_checklist")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_checklist_items(fixture)
        validate_report(fixture)
        validate_doc()
    except (
        OSError,
        ExternalRemapperImportExportAuditChecklistError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print("checklist_items=0")
        print("audit_executed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"checklist_items={len(EXPECTED_ITEMS)}")
    print("audit_executed=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
