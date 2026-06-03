#!/usr/bin/env python3
"""Validate the external Glyph remapper adapter boundary gap report."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_adapter_boundary_2026-06-03.json"
)

SCHEMA_NAME = "glyph_external_remapper_adapter_boundary"
BOUNDARY_VERSION = 1
STATUS = "external_non_authoritative_gap_report"
HARDWARE_STATUS = "not_new_hardware_result"
REQUIRED_EXTERNAL_URLS = (
    "https://github.com/lyseste/glyph-remapper",
    "https://lyseste.com/glyph-remapper/",
)
REQUIRED_OBSERVATION_IDS = (
    "browser_configurator",
    "profile_editing",
    "json_import_export",
    "rgb_color_palette",
    "socd_profile_management",
    "keyboard_capture",
    "webserial_load_save_claim",
    "custom_profile_modifier_support_claim_public_post",
)
ALLOWED_OBSERVATION_STATUSES = {
    "observed_from_public_post",
    "observed_from_external_repo_docs",
    "observed_from_external_code",
    "not_verified",
}
REQUIRED_FUTURE_COMPARISONS = (
    "need full source audit before adapter assumptions",
    "need profile JSON compatibility comparison",
    "need protobuf schema comparison",
    "need WebSerial packet-framing comparison",
    "need custom modifier representation comparison",
    "need import/export package compatibility experiment",
    "need license review before code reuse",
    "need user approval before depending on or integrating",
)
REQUIRED_FORBIDDEN_INTERPRETATIONS = (
    "firmware_authority",
    "official_configurator_authority",
    "imported_dependency",
    "device_write_implementation",
    "runtime_loaded_config_implementation",
    "hardware_validation",
)
REQUIRED_DOC_PHRASES = (
    "external observations are non-authoritative",
    "not firmware authority",
    "not official configurator authority",
    "no device-write implementation",
    "no runtime-loaded config implementation",
    "not hardware validation",
)


class ExternalRemapperBoundaryError(ValueError):
    """Raised when the external remapper boundary drifts."""


def fail(message: str) -> None:
    raise ExternalRemapperBoundaryError(message)


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


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        fail(f"{key} must be a non-empty string list")
    return value


def require_object_list(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{key} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"{key}[{index}] must be an object")
        result.append(item)
    return result


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "boundary_version": BOUNDARY_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "external_source_promoted_to_authority": False,
        "device_write_implemented": False,
        "runtime_loaded_config_implemented": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_external_references(fixture: dict[str, Any]) -> None:
    references = require_object_list(fixture, "external_references")
    urls = []
    for entry in references:
        url = entry.get("url")
        if not isinstance(url, str) or not url:
            fail("external_references entries must include non-empty url")
        urls.append(url)
        if entry.get("authority_status") != "non_authoritative_observation":
            fail(f"external reference {entry.get('id', '<unknown>')} must be non-authoritative")
        if entry.get("promoted_to_authority") is not False:
            fail(f"external reference {entry.get('id', '<unknown>')} must not be promoted to authority")

    for required_url in REQUIRED_EXTERNAL_URLS:
        if required_url not in urls:
            fail(f"missing external reference URL: {required_url}")


def validate_observations(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    observations = require_object_list(fixture, "observations")
    by_id: dict[str, dict[str, Any]] = {}
    statuses: set[str] = set()
    for entry in observations:
        observation_id = entry.get("id")
        status = entry.get("status")
        scope = entry.get("scope")
        if not isinstance(observation_id, str) or not observation_id:
            fail("observation id must be a non-empty string")
        if not isinstance(scope, str) or not scope:
            fail(f"observation {observation_id} must include scope")
        if status not in ALLOWED_OBSERVATION_STATUSES:
            fail(f"observation {observation_id} has unsupported status: {status!r}")
        if entry.get("authority_status") != "non_authoritative_observation":
            fail(f"observation {observation_id} must be non-authoritative")
        by_id[observation_id] = entry
        statuses.add(status)

    for required_id in REQUIRED_OBSERVATION_IDS:
        if required_id not in by_id:
            fail(f"missing required observation: {required_id}")

    for required_status in ALLOWED_OBSERVATION_STATUSES:
        if required_status not in statuses:
            fail(f"missing observation status coverage: {required_status}")

    return observations


def validate_future_comparisons(fixture: dict[str, Any]) -> None:
    comparisons = require_string_list(fixture, "required_future_comparisons")
    if tuple(comparisons) != REQUIRED_FUTURE_COMPARISONS:
        fail("required_future_comparisons drifted from required gap report")


def validate_forbidden_interpretations(fixture: dict[str, Any]) -> None:
    forbidden = require_string_list(fixture, "forbidden_interpretations")
    for item in REQUIRED_FORBIDDEN_INTERPRETATIONS:
        if item not in forbidden:
            fail(f"forbidden_interpretations missing: {item}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_adapter_boundary")
    observations_count = 0
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_external_references(fixture)
        observations = validate_observations(fixture)
        observations_count = len(observations)
        validate_future_comparisons(fixture)
        validate_forbidden_interpretations(fixture)
        validate_doc()
    except (OSError, ExternalRemapperBoundaryError, ValueError) as exc:
        print("status=FAIL")
        print(f"observations={observations_count}")
        print("external_source_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"observations={observations_count}")
    print("external_source_promoted_to_authority=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
