#!/usr/bin/env python3
"""Validate the post-GFW3 configurator baseline packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_post_gfw3_configurator_baseline_2026-06-06.json"
)

GFW3_RESULT_DOC = REPO_ROOT / "docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md"
GFW3_RESULT_FIXTURE = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.json"
)
GFW3_RESULT_CHECKER = REPO_ROOT / "tools/check_glyph_gfw3_runtime_remap_hardware_result.py"

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_post_gfw3_configurator_baseline",
    "schema_version": 1,
    "baseline_date": "2026-06-06",
    "status": "post_gfw3_configurator_baseline_recorded",
    "configurator_baseline_status": "gfw3_merged_and_ready_for_next_docs_tools_gate",
    "merged_integration_branch": "glyph/gfw3-runtime-remap-rework",
    "source_result_doc_path": "docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md",
    "source_result_fixture_path": (
        "docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.json"
    ),
    "source_result_checker_path": "tools/check_glyph_gfw3_runtime_remap_hardware_result.py",
    "source_result_status": "user_reported_hardware_pass",
    "user_report": "everything passing as expected",
}

REQUIRED_FALSE_NON_CLAIMS = {
    "nunchuk_hardware_validated",
    "runtime_loaded_config_implemented",
    "webserial_write_implemented",
    "device_write_implemented",
    "external_remapper_adapter_implemented",
    "external_remapper_json_generated",
    "active_profile_artifact_changed",
    "senscope_game_semantics_changed",
}

REQUIRED_WORKFLOW_GATES = {
    "own_behavior_change_branch",
    "source_backed_spec",
    "deterministic_checker_or_fixture",
    "firmware_build",
    "build_artifact_inspection",
    "hardware_test_plan",
    "user_hardware_result_recording",
    "post_result_inspection",
    "rollback_plan",
    "merge_gate_before_configurator_merge",
}

REQUIRED_BLOCKED_ITEMS = {
    "runtime_loaded_config",
    "WebSerial/device write",
    "protobuf binary write",
    "firmware flashing automation",
    "external remapper adapter output",
}

REQUIRED_CHECKS = {
    "tools/check_glyph_gfw3_runtime_remap_hardware_result.py",
    "tools/check_glyph_identity_runtime_behavior_evaluator.py",
    "tools/check_glyph_firmware_workstream_roadmap.py",
    "tools/run_glyph_next_runtime_change_readiness_checks.py",
    "tools/check_glyph_no_forbidden_artifacts.py",
    ".venv/bin/python -m platformio run -e glyph_mk6",
    "tools/inspect_glyph_mk6_build_artifact.py",
}

REQUIRED_DOC_PHRASES = (
    "GFW3 runtime remap work is complete on `configurator`",
    "The merged integration branch was",
    "`glyph/gfw3-runtime-remap-rework`",
    "user-reported as \"everything passing as expected\"",
    "Nunchuk hardware validation was not claimed",
    "Runtime-loaded config was not implemented",
    "WebSerial write was not implemented",
    "Serial/device write behavior was not implemented",
    "External remapper adapter implementation was not started",
    "Active profile artifact change was not required",
    "Any next behavior-changing firmware work still needs its own branch",
    "Runtime-loaded config, WebSerial/device write, protobuf binary write, firmware flashing automation, and external-remapper adapter output remain blocked",
)


class PostGfw3BaselineError(AssertionError):
    """Raised when the post-GFW3 baseline packet drifts from guardrails."""


def fail(message: str) -> None:
    raise PostGfw3BaselineError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_superset(actual: Any, required: set[str], label: str) -> None:
    if not isinstance(actual, list) or not all(isinstance(item, str) for item in actual):
        fail(f"{label} must be a string list")
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def validate_required_paths() -> None:
    for path in (DOC_PATH, FIXTURE_PATH, GFW3_RESULT_DOC, GFW3_RESULT_FIXTURE, GFW3_RESULT_CHECKER):
        if not path.exists():
            fail(f"missing required path: {display(path)}")


def validate_fixture(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")

    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("non_claims must be an object")
    for key in sorted(REQUIRED_FALSE_NON_CLAIMS):
        if non_claims.get(key) is not False:
            fail(f"non_claims.{key} must be false")

    require_superset(
        payload.get("required_future_behavior_changing_workflow_gates"),
        REQUIRED_WORKFLOW_GATES,
        "required_future_behavior_changing_workflow_gates",
    )
    require_superset(
        payload.get("blocked_without_future_source_authority_and_approval"),
        REQUIRED_BLOCKED_ITEMS,
        "blocked_without_future_source_authority_and_approval",
    )
    require_superset(
        payload.get("key_checks_expected_to_pass"),
        REQUIRED_CHECKS,
        "key_checks_expected_to_pass",
    )


def validate_gfw3_result_fixture() -> None:
    result = load_json_object(GFW3_RESULT_FIXTURE)
    if result.get("status") != "user_reported_hardware_pass":
        fail("GFW3 result fixture must remain user_reported_hardware_pass")
    if result.get("tested_branch") != "glyph/gfw3-runtime-remap-rework":
        fail("GFW3 result fixture must identify glyph/gfw3-runtime-remap-rework")
    if result.get("nunchuk_hardware_validated") is not False:
        fail("GFW3 result fixture must not claim nunchuk hardware validation")
    for key in (
        "runtime_loaded_config_implemented",
        "webserial_write_implemented",
        "device_write_implemented",
        "profile_artifact_changed",
    ):
        if result.get(key) is not False:
            fail(f"GFW3 result fixture {key} must be false")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"baseline doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_post_gfw3_configurator_baseline")
    try:
        validate_required_paths()
        payload = load_json_object(FIXTURE_PATH)
        validate_fixture(payload)
        validate_gfw3_result_fixture()
        validate_doc()
    except (OSError, PostGfw3BaselineError, ValueError) as exc:
        print("status=FAIL")
        print("baseline_status=post_gfw3_configurator_baseline_recorded")
        print("nunchuk_hardware_validated=false")
        print("runtime_loaded_config_implemented=false")
        print("webserial_write_implemented=false")
        print("device_write_implemented=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("baseline_status=post_gfw3_configurator_baseline_recorded")
    print("merged_integration_branch=glyph/gfw3-runtime-remap-rework")
    print("source_result_status=user_reported_hardware_pass")
    print("nunchuk_hardware_validated=false")
    print("runtime_loaded_config_implemented=false")
    print("webserial_write_implemented=false")
    print("device_write_implemented=false")
    print("external_remapper_adapter_implemented=false")
    print("active_profile_artifact_changed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
