#!/usr/bin/env python3
"""Validate the external remapper license/code-reuse blocker packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_external_remapper_license_code_reuse_blocker_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/"
    "glyph_external_remapper_license_code_reuse_blocker_2026-06-04.json"
)

SCHEMA_NAME = "glyph_external_remapper_license_code_reuse_blocker"
STATUS = "code_reuse_blocked_pending_license_review_and_user_approval"
HARDWARE_STATUS = "not_new_hardware_result"

FALSE_FLAGS = (
    "active_profile_artifact_changed",
    "adapter_implemented",
    "code_reuse_approved",
    "external_code_copied",
    "external_dependency_added",
    "external_json_generated",
    "external_source_promoted_to_authority",
    "exported_experiment_artifact_changed",
    "license_review_completed",
    "official_configurator_compatibility_claimed",
    "protobuf_binary_generation_implemented",
    "runtime_loaded_config_implemented",
    "runtime_source_changed",
    "serial_device_write_behavior_implemented",
    "transform_code_added",
    "vendored_source_added",
    "webserial_transport_implemented",
)

TRUE_FLAGS = (
    "approval_required_before_code_reuse_or_dependency",
    "clean_room_required",
    "clean_room_transform_design_independent",
    "implementation_requiring_external_code_blocked",
)

REQUIRED_FORBIDDEN_INTERPRETATIONS = (
    "external source code copied",
    "external dependency added",
    "vendored source added",
    "code reuse approved",
    "license review completed",
    "adapter implemented",
    "external JSON generated",
    "transform code added",
    "runtime-loaded config implemented",
    "serial/device write behavior implemented",
    "WebSerial transport implemented",
    "protobuf binary generation implemented",
    "official configurator compatibility claimed",
    "hardware validation claimed",
    "external source promoted to authority",
    "firmware runtime behavior changed",
    "active profile artifact changed",
    "exported experiment artifact changed",
)

REQUIRED_DOC_PHRASES = (
    "code_reuse_blocked_pending_license_review_and_user_approval",
    "No external source copied.",
    "No external dependency added.",
    "No vendoring.",
    "No code reuse approved.",
    "License review not completed.",
    "Implementation requiring external code is blocked.",
    "Clean-room transform design remains independent.",
    "Future approval required before any code reuse/dependency.",
    "license_review_completed=false",
    "code_reuse_approved=false",
    "external_code_copied=false",
    "external_dependency_added=false",
    "vendored_source_added=false",
    "clean_room_required=true",
    "hardware_status=not_new_hardware_result",
    "This packet does not implement an adapter.",
    "This packet does not generate external JSON.",
    "This packet does not add transform code.",
    "This packet does not implement runtime-loaded config.",
    "This packet does not implement serial/device write behavior.",
    "This packet does not implement WebSerial transport.",
    "This packet does not implement protobuf binary generation.",
    "This packet does not claim official configurator compatibility.",
    "This packet does not claim hardware validation.",
    "This packet does not promote external source to authority.",
)


class ExternalRemapperLicenseCodeReuseBlockerError(ValueError):
    """Raised when the license/code-reuse blocker packet drifts."""


def fail(message: str) -> None:
    raise ExternalRemapperLicenseCodeReuseBlockerError(message)


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


def validate_fixture(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")
    for key in FALSE_FLAGS:
        if fixture.get(key) is not False:
            fail(f"{key} must be false")
    for key in TRUE_FLAGS:
        if fixture.get(key) is not True:
            fail(f"{key} must be true")

    require_exact_string_list(
        fixture,
        "forbidden_interpretations",
        REQUIRED_FORBIDDEN_INTERPRETATIONS,
    )

    report = fixture.get("validation_report")
    if not isinstance(report, dict):
        fail("validation_report must be an object")
    expected_report = {
        "checker_path": "tools/check_glyph_external_remapper_license_code_reuse_blocker.py",
        "doc_path": (
            "docs/calibration/"
            "glyph_external_remapper_license_code_reuse_blocker_2026-06-04.md"
        ),
        "fixture_path": (
            "docs/calibration/fixtures/"
            "glyph_external_remapper_license_code_reuse_blocker_2026-06-04.json"
        ),
        "hardware_status": HARDWARE_STATUS,
        "validation_scope": "docs_tools_fixtures_only_license_code_reuse_blocker",
    }
    for key, value in expected_report.items():
        if report.get(key) != value:
            fail(f"validation_report.{key} must be {value!r}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_license_code_reuse_blocker")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_fixture(fixture)
        validate_doc()
    except (
        OSError,
        ExternalRemapperLicenseCodeReuseBlockerError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print("code_reuse_approved=false")
        print("external_dependency_added=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("code_reuse_approved=false")
    print("external_dependency_added=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("license_review_completed=false")
    print("external_code_copied=false")
    print("vendored_source_added=false")
    print("clean_room_required=true")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
