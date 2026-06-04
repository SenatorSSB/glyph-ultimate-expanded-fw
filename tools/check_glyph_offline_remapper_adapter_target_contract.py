#!/usr/bin/env python3
"""Validate the offline remapper adapter target contract."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_adapter_target_contract_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_adapter_target_contract_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_adapter_target_contract"
CONTRACT_VERSION = 1
STATUS = "offline_adapter_plan_only"
HARDWARE_STATUS = "not_new_hardware_result"
FUTURE_TARGET_ARTIFACT = "external-remapper-compatible JSON candidate"

REQUIRED_AUTHORITY = (
    "non-authoritative external comparison",
    "repo fixtures",
)
REQUIRED_FUTURE_INPUTS = (
    (
        "Senscope export package sample",
        "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json",
    ),
    (
        "runtime config candidate sample",
        "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json",
    ),
    (
        "generated config prototype",
        "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json",
    ),
    (
        "validation report",
        "docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json",
    ),
    (
        "active profile artifact",
        "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
    ),
)
REQUIRED_FUTURE_OUTPUTS = (
    "JSON candidate intended for no-device import/export experiment only",
    "compatibility report",
)
REQUIRED_FORBIDDEN_INTERPRETATIONS = (
    "adapter implemented",
    "official configurator compatibility claimed",
    "external source authority",
    "device write behavior",
    "WebSerial transport",
    "protobuf binary generation",
    "runtime-loaded config",
    "hardware validation",
)
REQUIRED_DOC_PHRASES = (
    "offline adapter plan only",
    "adapter not implemented",
    "external source not authority",
    "not official configurator compatibility",
    "not device write behavior",
    "not webserial transport",
    "not protobuf binary generation",
    "not runtime-loaded config",
    "not hardware validation",
)


class OfflineRemapperAdapterTargetContractError(ValueError):
    """Raised when the target contract drifts from the allowed boundary."""


def fail(message: str) -> None:
    raise OfflineRemapperAdapterTargetContractError(message)


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
    if not isinstance(value, list) or not value:
        fail(f"{key} must be a non-empty list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{key}[{index}] must be a non-empty string")
        result.append(item)
    return result


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "contract_version": CONTRACT_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "external_source_promoted_to_authority": False,
        "adapter_implemented": False,
        "official_configurator_compatibility_claimed": False,
        "device_write_implemented": False,
        "webserial_transport_implemented": False,
        "protobuf_binary_generation_implemented": False,
        "runtime_loaded_config_implemented": False,
        "future_target_artifact": FUTURE_TARGET_ARTIFACT,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_authority(fixture: dict[str, Any]) -> None:
    authority = require_string_list(fixture, "target_authority")
    if tuple(authority) != REQUIRED_AUTHORITY:
        fail("target_authority drifted from required stable order")


def validate_future_inputs(fixture: dict[str, Any]) -> None:
    inputs = fixture.get("required_future_inputs")
    if not isinstance(inputs, list) or len(inputs) != len(REQUIRED_FUTURE_INPUTS):
        fail("required_future_inputs must contain the required stable input set")

    for index, (item, (expected_name, expected_path)) in enumerate(
        zip(inputs, REQUIRED_FUTURE_INPUTS, strict=True)
    ):
        if not isinstance(item, dict):
            fail(f"required_future_inputs[{index}] must be an object")
        if item.get("name") != expected_name:
            fail(f"required_future_inputs[{index}].name must be {expected_name!r}")
        if item.get("repo_artifact") != expected_path:
            fail(
                f"required_future_inputs[{index}].repo_artifact must be "
                f"{expected_path!r}"
            )
        if not (REPO_ROOT / expected_path).exists():
            fail(f"required_future_inputs references missing path: {expected_path}")


def validate_future_outputs(fixture: dict[str, Any]) -> None:
    outputs = fixture.get("future_outputs")
    if not isinstance(outputs, list) or len(outputs) != len(REQUIRED_FUTURE_OUTPUTS):
        fail("future_outputs must contain the required stable output set")

    for index, (item, expected_name) in enumerate(
        zip(outputs, REQUIRED_FUTURE_OUTPUTS, strict=True)
    ):
        if not isinstance(item, dict):
            fail(f"future_outputs[{index}] must be an object")
        if item.get("name") != expected_name:
            fail(f"future_outputs[{index}].name must be {expected_name!r}")
        if item.get("status") != "plan_only_not_generated":
            fail(f"future_outputs[{index}].status must be plan_only_not_generated")
        if item.get("generated") is not False:
            fail(f"future_outputs[{index}].generated must be false")
        if "repo_artifact" in item or "path" in item:
            fail(f"future_outputs[{index}] must not reference a generated artifact path")


def validate_forbidden_and_approvals(fixture: dict[str, Any]) -> None:
    forbidden = require_string_list(fixture, "forbidden_interpretations")
    for item in REQUIRED_FORBIDDEN_INTERPRETATIONS:
        if item not in forbidden:
            fail(f"forbidden_interpretations missing: {item}")

    approvals = require_string_list(fixture, "required_approvals")
    for item in (
        "user approval before generating an external-remapper-compatible JSON candidate",
        "user approval before running any no-device import/export experiment",
        "user approval before adapter implementation",
        "user approval before device transport or WebSerial work",
        "user approval before protobuf/config/schema behavior changes",
        "user approval before runtime-loaded config implementation",
    ):
        if item not in approvals:
            fail(f"required_approvals missing: {item}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_adapter_target_contract")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_authority(fixture)
        validate_future_inputs(fixture)
        validate_future_outputs(fixture)
        validate_forbidden_and_approvals(fixture)
        validate_doc()
    except (OSError, OfflineRemapperAdapterTargetContractError, ValueError) as exc:
        print("status=FAIL")
        print("adapter_implemented=false")
        print("external_source_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("adapter_implemented=false")
    print("external_source_promoted_to_authority=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("official_configurator_compatibility_claimed=false")
    print("device_write_implemented=false")
    print("webserial_transport_implemented=false")
    print("protobuf_binary_generation_implemented=false")
    print("runtime_loaded_config_implemented=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
