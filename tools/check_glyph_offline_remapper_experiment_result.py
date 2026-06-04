#!/usr/bin/env python3
"""Validate the offline remapper manual no-device experiment result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_experiment_result_2026-06-04.md"
)
RESULT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_experiment_result_2026-06-04.json"
)
EXPORTED_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json"
)
ACTIVE_INPUT_PATH = (
    REPO_ROOT
    / "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
)
READINESS_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_experiment_readiness_index_2026-06-03.json"
)
TEMPLATE_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_result_TEMPLATE_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_experiment_result"
RESULT_VERSION = 1
RESULT_DATE = "2026-06-04"
STATUS = "manual_no_device_experiment_completed_with_warnings"
HARDWARE_STATUS = "not_new_hardware_result"
WARNING_STATUS = "warning_not_faithful_to_firmware_owned_runtime_behavior"

EXPECTED_FLAGS = {
    "experiment_executed": True,
    "adapter_implemented": False,
    "device_connected": False,
    "connect_clicked": False,
    "webserial_access_granted": False,
    "save_to_device_clicked": False,
    "device_write_attempted": False,
    "firmware_flashing_attempted": False,
    "official_compatibility_claimed": False,
    "hardware_validation_claimed": False,
    "external_source_promoted_to_authority": False,
}

EXPECTED_ROW_STATUSES = {
    "ENV-001": "PARTIAL",
    "SRC-001": "PARTIAL",
    "INPUT-001": "PASS",
    "IMPORT-001": "PASS_WITH_WARNINGS",
    "EXPORT-001": "PASS",
    "DIFF-001": "PENDING",
    "FIELDS-001": "PENDING",
    "DEVICE-001": "PASS",
    "WS-001": "PASS",
    "SAVE-001": "PASS",
    "AUTH-001": "PASS",
    "CLAIM-001": "PASS",
}

REQUIRED_DOC_PHRASES = (
    "manual no-device external-remapper import/export experiment",
    "not hardware validation",
    "not official configurator compatibility",
    "not adapter implementation",
    "not WebSerial/device write behavior",
    "not runtime-loaded config",
    "no Glyph was connected",
    "Save to Device was not clicked",
    "not faithful to firmware-owned identity-runtime custom behavior",
)


class OfflineRemapperExperimentResultError(ValueError):
    """Raised when the manual experiment result drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperExperimentResultError(message)


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_path(rel_path: str) -> Path:
    path = REPO_ROOT / rel_path
    if not path.exists():
        fail(f"referenced path is missing: {rel_path}")
    return path


def validate_result_top_level(result: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "result_version": RESULT_VERSION,
        "result_date": RESULT_DATE,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_experiment_flags(result: dict[str, Any]) -> None:
    flags = result.get("experiment_flags")
    if not isinstance(flags, dict):
        fail("experiment_flags must be an object")
    for key, value in EXPECTED_FLAGS.items():
        if flags.get(key) != value:
            fail(f"experiment_flags.{key} must be {value!r}")


def validate_artifact_hash(artifact: Any, expected_path: Path, label: str) -> str:
    if not isinstance(artifact, dict):
        fail(f"{label} must be an object")
    rel_path = artifact.get("path")
    if not isinstance(rel_path, str) or not rel_path:
        fail(f"{label}.path must be a non-empty string")
    actual_path = require_path(rel_path)
    if actual_path != expected_path:
        fail(f"{label}.path must be {display(expected_path)!r}")
    expected_hash = artifact.get("sha256")
    if not isinstance(expected_hash, str) or not expected_hash:
        fail(f"{label}.sha256 must be a non-empty string")
    actual_hash = sha256(actual_path)
    if actual_hash != expected_hash:
        fail(f"{label}.sha256 mismatch: expected {expected_hash}, got {actual_hash}")
    return actual_hash


def validate_exported_json(exported: dict[str, Any]) -> None:
    for key in ("gameModeConfigs", "communicationBackendConfigs", "rgbConfigs"):
        if key not in exported:
            fail(f"exported artifact missing {key}")

    game_modes = exported.get("gameModeConfigs")
    if not isinstance(game_modes, list):
        fail("exported artifact gameModeConfigs must be a list")
    if not any(
        isinstance(entry, dict) and entry.get("modeId") == "MODE_ULTIMATE"
        for entry in game_modes
    ):
        fail("exported artifact missing gameModeConfigs entry with modeId MODE_ULTIMATE")


def validate_result_rows(result: dict[str, Any]) -> None:
    rows = result.get("result_rows")
    if not isinstance(rows, list):
        fail("result_rows must be a list")
    seen: dict[str, str] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            fail(f"result_rows[{index}] must be an object")
        row_id = row.get("row_id")
        status = row.get("status")
        if not isinstance(row_id, str) or not row_id:
            fail(f"result_rows[{index}].row_id must be a non-empty string")
        if not isinstance(status, str) or not status:
            fail(f"result_rows[{index}].status must be a non-empty string")
        if row_id in seen:
            fail(f"duplicate result row: {row_id}")
        seen[row_id] = status

    for row_id, expected_status in EXPECTED_ROW_STATUSES.items():
        if row_id not in seen:
            fail(f"missing result row: {row_id}")
        if seen[row_id] != expected_status:
            fail(f"{row_id} status must be {expected_status!r}")


def validate_functional_warning(result: dict[str, Any]) -> None:
    warning = result.get("functional_representation_warning")
    if not isinstance(warning, dict):
        fail("functional_representation_warning must be an object")
    if warning.get("status") != WARNING_STATUS:
        fail(f"functional_representation_warning.status must be {WARNING_STATUS!r}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_readiness_and_template() -> None:
    readiness = load_json_object(READINESS_FIXTURE_PATH)
    template = load_json_object(TEMPLATE_FIXTURE_PATH)
    if readiness.get("schema_name") != "glyph_offline_remapper_experiment_readiness_index":
        fail("readiness fixture schema_name drifted")
    if readiness.get("status") != "ready_for_manual_no_device_experiment":
        fail("readiness fixture status drifted")
    if template.get("schema_name") != "glyph_offline_remapper_result_template":
        fail("result template fixture schema_name drifted")
    if template.get("status") != "template_not_executed":
        fail("result template fixture status drifted")


def main() -> int:
    print("glyph_offline_remapper_experiment_result")
    exported_hash = "unknown"
    result_status = STATUS
    try:
        result = load_json_object(RESULT_FIXTURE_PATH)
        exported = load_json_object(EXPORTED_FIXTURE_PATH)
        load_json_object(ACTIVE_INPUT_PATH)
        validate_readiness_and_template()
        validate_result_top_level(result)
        result_status = result["status"]
        validate_experiment_flags(result)
        validate_artifact_hash(result.get("input_artifact"), ACTIVE_INPUT_PATH, "input_artifact")
        exported_hash = validate_artifact_hash(
            result.get("exported_artifact"), EXPORTED_FIXTURE_PATH, "exported_artifact"
        )
        validate_exported_json(exported)
        validate_result_rows(result)
        validate_functional_warning(result)
        validate_doc()
    except (OSError, OfflineRemapperExperimentResultError, ValueError) as exc:
        print("status=FAIL")
        print(f"result_status={result_status}")
        print(f"exported_artifact_sha256={exported_hash}")
        print("device_connected=false")
        print("webserial_access_granted=false")
        print("save_to_device_clicked=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"result_status={result_status}")
    print(f"exported_artifact_sha256={exported_hash}")
    print("device_connected=false")
    print("webserial_access_granted=false")
    print("save_to_device_clicked=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
