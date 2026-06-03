#!/usr/bin/env python3
"""Validate the offline Glyph import/export compatibility boundary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from check_glyph_senscope_export_package_validator import (
    EXPORT_CONTRACT_PATH,
    GENERATED_CONFIG_CONTRACT_PATH,
    validate_contracts as validate_export_contracts,
    validate_doc as validate_export_package_doc,
    validate_export_package,
)
from glyph_runtime_config_candidate_validator import (
    HARDWARE_STATUS,
    NUNCHUK_STATUS,
    STATUS as RUNTIME_CANDIDATE_STATUS,
    validate_runtime_config_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_import_export_compatibility_validator_2026-06-03.md"
)
EXPECTATIONS_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_import_export_compatibility_expectations_2026-06-03.json"
)
DEFAULT_EXPORT_PACKAGE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json"
)
DEFAULT_RUNTIME_CANDIDATE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json"
)
DEFAULT_ACTIVE_PROFILE_PATH = (
    REPO_ROOT
    / "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
)
CONFIG_JSON_COMPATIBILITY_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json"
)

SCHEMA_NAME = "glyph_import_export_compatibility_expectations"
EXPECTATION_VERSION = 1
STATUS = "offline_import_export_compatibility_expectations"

REQUIRED_DOC_CAVEATS = (
    "offline import/export compatibility boundary only",
    "not official configurator source authority",
    "not webserial implementation",
    "not device write behavior",
    "not runtime-loaded config",
    "not hardware validation",
)
REQUIRED_CHECK_IDS = (
    "configurator_compatibility_source_registry_passes",
    "config_json_compatibility_fixtures_pass",
    "generated_export_artifact_round_trip_passes",
    "candidate_export_package_validates",
    "runtime_candidate_sample_validates",
    "active_profile_artifact_json_compatibility_cases_pass",
    "serial_dry_run_accepts_active_profile_artifact",
    "no_device_write_claim_in_export_package",
    "no_device_write_claim_in_compatibility_expectations",
    "no_official_configurator_claim_beyond_repo_fixtures",
    "no_runtime_loaded_config_claim",
    "no_hardware_or_nunchuk_validation_claim",
)
REQUIRED_ACTIVE_PROFILE_CASE_IDS = (
    "active_profile_artifact_json_parse",
    "active_profile_mode_ultimate_structure",
    "serial_dry_run_accepts_active_profile_artifact",
)
REQUIRED_SERIAL_DRY_RUN_PHRASES = (
    "mode=dry_run",
    "artifact_validated=true",
    "live_device_access=false",
    "active_device_profile_updated=false",
    "readback_verified=false",
    "firmware_flashing=false",
    "dry_run_serial_opened=false",
    "protocol_source_confirmed=true",
)


class ImportExportCompatibilityError(ValueError):
    """Raised when the compatibility boundary drifts from expectations."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ImportExportCompatibilityError(message)


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


def resolve_path(path_text: str) -> Path:
    candidate = Path(path_text)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current offline Glyph import/export compatibility "
            "boundary for a candidate export package and committed artifacts."
        )
    )
    parser.add_argument(
        "--export-package",
        default=str(DEFAULT_EXPORT_PACKAGE_PATH.relative_to(REPO_ROOT)),
        help="Repo-relative or absolute path to the candidate export package JSON.",
    )
    parser.add_argument(
        "--runtime-candidate",
        default=str(DEFAULT_RUNTIME_CANDIDATE_PATH.relative_to(REPO_ROOT)),
        help="Repo-relative or absolute path to the runtime candidate JSON fixture.",
    )
    parser.add_argument(
        "--active-profile-artifact",
        default=str(DEFAULT_ACTIVE_PROFILE_PATH.relative_to(REPO_ROOT)),
        help="Repo-relative or absolute path to the active profile artifact JSON.",
    )
    parser.add_argument(
        "--expectations",
        default=str(EXPECTATIONS_PATH.relative_to(REPO_ROOT)),
        help="Repo-relative or absolute path to the compatibility expectations JSON.",
    )
    return parser.parse_args()


def run_python_tool(relpath: str, *args: str) -> str:
    tool_path = REPO_ROOT / relpath
    if not tool_path.exists():
        fail(f"missing tool: {relpath}")

    completed = subprocess.run(
        [sys.executable, str(tool_path.relative_to(REPO_ROOT)), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    if completed.returncode != 0:
        fail(f"{relpath} failed with returncode={completed.returncode}: {output}")
    if "status=PASS" not in output:
        fail(f"{relpath} did not report status=PASS")
    return output


def validate_doc(expectations: dict[str, Any]) -> None:
    caveats = require_string_list(expectations, "doc_caveats")
    if caveats != list(REQUIRED_DOC_CAVEATS):
        fail("doc_caveats drifted from required import/export compatibility caveats")

    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_CAVEATS:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_expected_checks(expectations: dict[str, Any]) -> list[dict[str, str]]:
    value = expectations.get("expected_checks")
    if not isinstance(value, list) or not value:
        fail("expected_checks must be a non-empty list")

    ids: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"expected_checks[{index}] must be an object")
        check_id = item.get("id")
        expectation = item.get("expectation")
        if not isinstance(check_id, str) or not check_id:
            fail(f"expected_checks[{index}].id must be a non-empty string")
        if not isinstance(expectation, str) or not expectation:
            fail(f"expected_checks[{index}].expectation must be a non-empty string")
        ids.append(check_id)

    if tuple(ids) != REQUIRED_CHECK_IDS:
        fail("expected_checks must contain the required ids in stable order")
    return value


def validate_expectations_top_level(expectations: dict[str, Any]) -> list[dict[str, str]]:
    expected = {
        "schema_name": SCHEMA_NAME,
        "expectation_version": EXPECTATION_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "official_configurator_compatibility_claimed": False,
        "device_write_implemented": False,
        "runtime_loaded_config_implemented": False,
    }
    for key, value in expected.items():
        if expectations.get(key) != value:
            fail(f"{key} must be {value!r}")

    path_keys = (
        "default_export_package",
        "runtime_candidate_sample",
        "active_profile_artifact",
        "config_json_compatibility_fixture",
    )
    for key in path_keys:
        relpath = expectations.get(key)
        if not isinstance(relpath, str) or not relpath:
            fail(f"{key} must be a non-empty string path")
        path = resolve_path(relpath)
        if not path.exists():
            fail(f"{key} references missing path: {relpath}")

    return validate_expected_checks(expectations)


def validate_config_json_fixture_boundaries() -> dict[str, Any]:
    fixture = load_json_object(CONFIG_JSON_COMPATIBILITY_FIXTURE_PATH)
    expected = {
        "schema_name": "glyph_config_json_compatibility_cases",
        "case_version": 1,
        "status": "repo_committed_fixture_compatibility_only",
        "hardware_status": HARDWARE_STATUS,
        "official_configurator_compatibility_claimed": False,
        "device_write_implemented": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{display(CONFIG_JSON_COMPATIBILITY_FIXTURE_PATH)} {key} must be {value!r}")

    cases_value = fixture.get("cases")
    if not isinstance(cases_value, list):
        fail(f"{display(CONFIG_JSON_COMPATIBILITY_FIXTURE_PATH)} cases must be a list")
    case_ids = [
        item.get("id")
        for item in cases_value
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    missing = [case_id for case_id in REQUIRED_ACTIVE_PROFILE_CASE_IDS if case_id not in case_ids]
    if missing:
        fail(
            f"{display(CONFIG_JSON_COMPATIBILITY_FIXTURE_PATH)} missing active-profile case id(s): "
            + ", ".join(missing)
        )
    return fixture


def validate_export_package_candidate(path: Path) -> dict[str, Any]:
    export_contract = load_json_object(EXPORT_CONTRACT_PATH)
    generated_config_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
    validate_export_contracts(export_contract, generated_config_contract)
    validate_export_package_doc()

    export_package = load_json_object(path)
    issues = validate_export_package(export_package, export_contract, generated_config_contract)
    if issues:
        first = issues[0]
        fail(
            "candidate export package failed validation: "
            f"{first.code} at {first.path}: {first.message}"
        )

    report = export_package.get("validation_report")
    if not isinstance(report, dict):
        fail(f"{display(path)} validation_report must be an object")
    confirmations = report.get("no_forbidden_behavior_confirmation")
    if not isinstance(confirmations, dict):
        fail(f"{display(path)} validation_report.no_forbidden_behavior_confirmation must be an object")

    required_flags = {
        "device_write_absent": True,
        "serial_transport_absent": True,
        "runtime_loaded_config_absent": True,
        "hardware_validation_claim_absent": True,
        "nunchuk_hardware_validation_claim_absent": True,
    }
    for key, value in required_flags.items():
        if confirmations.get(key) != value:
            fail(f"{display(path)} validation_report.no_forbidden_behavior_confirmation.{key} must be {value!r}")

    if export_package.get("hardware_status") != HARDWARE_STATUS:
        fail(f"{display(path)} hardware_status must be {HARDWARE_STATUS!r}")
    if export_package.get("nunchuk_status") != NUNCHUK_STATUS:
        fail(f"{display(path)} nunchuk_status must be {NUNCHUK_STATUS!r}")
    if export_package.get("hardware_status_caveat") != "Sample package only; not hardware validation.":
        fail(f"{display(path)} hardware_status_caveat drifted from the committed not-hardware-validation caveat")
    if export_package.get("nunchuk_status_caveat") != (
        "Nunchuk behavior is preserved but not hardware validated by this package."
    ):
        fail(f"{display(path)} nunchuk_status_caveat drifted from the committed non-validation caveat")

    return export_package


def validate_runtime_candidate_sample(path: Path) -> dict[str, Any]:
    payload = load_json_object(path)
    issues = validate_runtime_config_candidate(payload)
    if issues:
        first = issues[0]
        fail(
            "runtime candidate sample failed validation: "
            f"{first.code} at {first.path}: {first.message}"
        )

    if payload.get("status") != RUNTIME_CANDIDATE_STATUS:
        fail(f"{display(path)} status must be {RUNTIME_CANDIDATE_STATUS!r}")
    if payload.get("hardware_status") != HARDWARE_STATUS:
        fail(f"{display(path)} hardware_status must be {HARDWARE_STATUS!r}")
    if payload.get("nunchuk_status") != NUNCHUK_STATUS:
        fail(f"{display(path)} nunchuk_status must be {NUNCHUK_STATUS!r}")
    return payload


def ensure_serial_dry_run_accepts(path: Path) -> None:
    output = run_python_tool(
        "tools/glyph_serial_config_tool.py",
        "--dry-run",
        "--artifact",
        str(path.relative_to(REPO_ROOT)),
    )
    for phrase in REQUIRED_SERIAL_DRY_RUN_PHRASES:
        if phrase not in output:
            fail(f"tools/glyph_serial_config_tool.py dry-run output missing required phrase: {phrase}")


def main() -> int:
    print("glyph_import_export_compatibility")
    completed_checks = 0
    try:
        args = parse_args()
        expectations_path = resolve_path(args.expectations)
        export_package_path = resolve_path(args.export_package)
        runtime_candidate_path = resolve_path(args.runtime_candidate)
        active_profile_path = resolve_path(args.active_profile_artifact)

        expectations = load_json_object(expectations_path)
        expected_checks = validate_expectations_top_level(expectations)
        validate_doc(expectations)

        config_fixture = validate_config_json_fixture_boundaries()

        run_python_tool("tools/check_glyph_configurator_compatibility_source_registry.py")
        completed_checks += 1

        run_python_tool("tools/check_glyph_config_json_compatibility_fixtures.py")
        completed_checks += 1

        run_python_tool("tools/check_glyph_export_artifact_round_trip.py")
        completed_checks += 1

        export_package = validate_export_package_candidate(export_package_path)
        completed_checks += 1

        runtime_candidate = validate_runtime_candidate_sample(runtime_candidate_path)
        completed_checks += 1

        if config_fixture.get("status") != "repo_committed_fixture_compatibility_only":
            fail("config JSON compatibility fixture status drifted from repo-committed-only scope")
        completed_checks += 1

        ensure_serial_dry_run_accepts(active_profile_path)
        completed_checks += 1

        if export_package["validation_report"]["no_forbidden_behavior_confirmation"]["device_write_absent"] is not True:
            fail("candidate export package must preserve device_write_absent=true")
        completed_checks += 1

        if expectations.get("device_write_implemented") is not False:
            fail("compatibility expectations must preserve device_write_implemented=false")
        completed_checks += 1

        if (
            expectations.get("official_configurator_compatibility_claimed") is not False
            or config_fixture.get("official_configurator_compatibility_claimed") is not False
        ):
            fail("official configurator compatibility claims must stay false in compatibility fixtures")
        completed_checks += 1

        if expectations.get("runtime_loaded_config_implemented") is not False:
            fail("compatibility expectations must preserve runtime_loaded_config_implemented=false")
        if runtime_candidate.get("status") != RUNTIME_CANDIDATE_STATUS:
            fail("runtime candidate sample drifted from not-runtime-loaded status")
        if (
            export_package["validation_report"]["no_forbidden_behavior_confirmation"][
                "runtime_loaded_config_absent"
            ]
            is not True
        ):
            fail("candidate export package must preserve runtime_loaded_config_absent=true")
        completed_checks += 1

        confirmations = export_package["validation_report"]["no_forbidden_behavior_confirmation"]
        if confirmations["hardware_validation_claim_absent"] is not True:
            fail("candidate export package must preserve hardware_validation_claim_absent=true")
        if confirmations["nunchuk_hardware_validation_claim_absent"] is not True:
            fail("candidate export package must preserve nunchuk_hardware_validation_claim_absent=true")
        completed_checks += 1
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        ImportExportCompatibilityError,
    ) as exc:
        print("status=FAIL")
        print(f"checked_components={completed_checks}")
        print("official_configurator_compatibility_claimed=false")
        print("device_write_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"checked_components={len(expected_checks)}")
    print("official_configurator_compatibility_claimed=false")
    print("device_write_implemented=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print(f"fixture={display(expectations_path)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
