#!/usr/bin/env python3
"""Validate the docs/tools-only Glyph export artifact round trip."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from check_glyph_senscope_export_package_validator import (
    EXPORT_CONTRACT_PATH,
    GENERATED_CONFIG_CONTRACT_PATH,
    validate_contracts as validate_export_contracts,
    validate_doc as validate_export_package_doc,
    validate_export_package,
)
from generate_glyph_runtime_config_validation_report import build_report
from glyph_generated_config_validator import (
    HARDWARE_STATUS,
    NUNCHUK_STATUS,
    load_json_object,
    validate_generated_config,
)
from glyph_runtime_config_candidate_validator import validate_runtime_config_candidate


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_export_artifact_round_trip_expectations_2026-06-03.json"
)
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_export_artifact_round_trip_2026-06-03.md"
REPORT_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json"
)


class ExportArtifactRoundTripError(ValueError):
    """Raised when committed round-trip artifacts drift."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ExportArtifactRoundTripError(message)


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def run_checker(path: Path) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode, output


def validate_doc(expectations: dict[str, Any]) -> None:
    required_phrases = require_string_list(expectations, "required_doc_caveats")
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in required_phrases:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_expectations_top_level(expectations: dict[str, Any]) -> list[dict[str, str]]:
    expected = {
        "schema_name": "glyph_export_artifact_round_trip_expectations",
        "contract_version": 1,
        "status": "docs_tools_round_trip_expectations",
        "mode_scope": "MODE_ULTIMATE",
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected.items():
        if expectations.get(key) != value:
            fail(f"{key} must be {value!r}")

    checked_artifacts = expectations.get("checked_artifacts")
    if not isinstance(checked_artifacts, list) or not checked_artifacts:
        fail("checked_artifacts must be a non-empty list")
    for index, artifact in enumerate(checked_artifacts):
        if not isinstance(artifact, dict):
            fail(f"checked_artifacts[{index}] must be an object")
        name = artifact.get("name")
        rel_path = artifact.get("path")
        if not isinstance(name, str) or not name:
            fail(f"checked_artifacts[{index}].name must be a non-empty string")
        if not isinstance(rel_path, str) or not rel_path:
            fail(f"checked_artifacts[{index}].path must be a non-empty string")
        if not (REPO_ROOT / rel_path).exists():
            fail(f"checked_artifacts[{index}] references missing path: {rel_path}")

    invariants = expectations.get("round_trip_invariants")
    if not isinstance(invariants, list) or not all(isinstance(item, str) and item for item in invariants):
        fail("round_trip_invariants must be a non-empty string list")

    return checked_artifacts


def artifact_paths_by_name(artifacts: list[dict[str, str]]) -> dict[str, Path]:
    return {artifact["name"]: REPO_ROOT / artifact["path"] for artifact in artifacts}


def validate_generated_config_round_trip(paths: dict[str, Path]) -> dict[str, Any]:
    prototype = load_json_object(paths["generated_config_prototype"])
    issues = validate_generated_config(prototype)
    if issues:
        first = issues[0]
        fail(
            "generated-config prototype failed validation: "
            f"{first.code} at {first.path}: {first.message}"
        )
    return prototype


def validate_runtime_candidate_round_trip(paths: dict[str, Path], prototype: dict[str, Any]) -> dict[str, Any]:
    candidate = load_json_object(paths["runtime_config_candidate_sample"])
    issues = validate_runtime_config_candidate(candidate)
    if issues:
        first = issues[0]
        fail(
            "runtime-candidate sample failed validation: "
            f"{first.code} at {first.path}: {first.message}"
        )

    if candidate.get("tables") != prototype.get("tables"):
        fail("runtime-candidate tables do not exactly match generated-config tables")
    if candidate.get("role_bindings") != prototype.get("role_bindings"):
        fail("runtime-candidate role_bindings do not exactly match generated-config role_bindings")
    if candidate.get("hard_overrides") != prototype.get("hard_overrides"):
        fail("runtime-candidate hard_overrides do not exactly match generated-config hard_overrides")

    priority_mapping = load_json_object(FIXTURE_PATH).get("expected_priority_reference_mapping")
    if not isinstance(priority_mapping, dict):
        fail("expected_priority_reference_mapping must be an object")
    priority_model = prototype.get("priority_model")
    if not isinstance(priority_model, dict):
        fail("generated-config priority_model must be an object")
    expected_priority = {
        candidate_key: priority_model.get(prototype_key)
        for candidate_key, prototype_key in priority_mapping.items()
    }
    if candidate.get("priority_references") != expected_priority:
        fail("runtime-candidate priority_references do not exactly match generated-config priority lists")
    if candidate.get("suppression_rules") != prototype.get("suppression_rules"):
        fail("runtime-candidate suppression_rules do not exactly match generated-config suppression_rules")
    return candidate


def validate_export_package_round_trip(paths: dict[str, Path], prototype: dict[str, Any]) -> dict[str, Any]:
    export_contract = load_json_object(EXPORT_CONTRACT_PATH)
    generated_config_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
    validate_export_contracts(export_contract, generated_config_contract)
    validate_export_package_doc()

    export_package = load_json_object(paths["senscope_export_package_sample"])
    issues = validate_export_package(export_package, export_contract, generated_config_contract)
    if issues:
        first = issues[0]
        fail(
            "senscope export package sample failed validation: "
            f"{first.code} at {first.path}: {first.message}"
        )
    if export_package.get("glyph_generated_config_prototype") != prototype:
        fail("nested generated config in Senscope export package does not match the committed prototype")
    return export_package


def validate_runtime_report_round_trip(
    expectations: dict[str, Any],
    paths: dict[str, Path],
    candidate: dict[str, Any],
    prototype: dict[str, Any],
) -> dict[str, Any]:
    regenerated = build_report()
    expected_text = json.dumps(regenerated, indent=2, sort_keys=True) + "\n"
    committed_text = REPORT_FIXTURE_PATH.read_text(encoding="utf-8")
    if committed_text != expected_text:
        fail("runtime config validation report fixture does not exactly match regenerated output")

    committed = load_json_object(paths["runtime_config_validation_report"])
    if committed != regenerated:
        fail("runtime config validation report JSON object drifted from regenerated report")

    expected_summary = expectations.get("expected_report_summary")
    if not isinstance(expected_summary, dict):
        fail("expected_report_summary must be an object")
    for key, value in expected_summary.items():
        if committed.get(key) != value:
            fail(f"runtime config validation report {key} must be {value!r}")

    if committed.get("validated_candidate_schema_name") != candidate.get("schema_name"):
        fail("runtime config validation report validated_candidate_schema_name drifted from the candidate schema")
    if committed.get("table_count") != len(candidate.get("tables", {})):
        fail("runtime config validation report table_count drifted from runtime-candidate tables")
    if committed.get("table_count") != len(prototype.get("tables", {})):
        fail("runtime config validation report table_count drifted from generated-config tables")
    return committed


def require_string_members(
    payload: dict[str, Any],
    key: str,
    required_members: list[str],
    label: str,
) -> None:
    actual = payload.get(key)
    if not isinstance(actual, list) or not all(isinstance(item, str) for item in actual):
        fail(f"{label}.{key} must be a string list")
    missing = [item for item in required_members if item not in actual]
    if missing:
        fail(f"{label}.{key} missing required value(s): " + ", ".join(missing))


def validate_caveat_preservation(
    expectations: dict[str, Any],
    prototype: dict[str, Any],
    candidate: dict[str, Any],
    export_package: dict[str, Any],
    report: dict[str, Any],
) -> None:
    expected_hardware = expectations["hardware_status"]
    expected_nunchuk = expectations["nunchuk_status"]
    for label, payload in (
        ("generated_config_prototype", prototype),
        ("runtime_config_candidate_sample", candidate),
        ("senscope_export_package_sample", export_package),
        ("runtime_config_validation_report", report),
    ):
        if payload.get("hardware_status") != expected_hardware:
            fail(f"{label}.hardware_status must stay {expected_hardware!r}")
        if payload.get("nunchuk_status") != expected_nunchuk:
            fail(f"{label}.nunchuk_status must stay {expected_nunchuk!r}")

    required_non_goals = expectations.get("required_non_goal_markers")
    if not isinstance(required_non_goals, dict):
        fail("required_non_goal_markers must be an object")
    require_string_members(
        prototype,
        "non_goals",
        required_non_goals["generated_config_prototype"],
        "generated_config_prototype",
    )
    require_string_members(
        candidate,
        "non_goals",
        required_non_goals["runtime_config_candidate_sample"],
        "runtime_config_candidate_sample",
    )
    require_string_members(
        report,
        "caveats",
        required_non_goals["runtime_config_validation_report"],
        "runtime_config_validation_report",
    )

    export_expectations = expectations.get("required_export_caveats")
    if not isinstance(export_expectations, dict):
        fail("required_export_caveats must be an object")
    if export_package.get("hardware_status_caveat") != export_expectations.get("hardware_status_caveat"):
        fail("senscope_export_package_sample.hardware_status_caveat drifted")
    if export_package.get("nunchuk_status_caveat") != export_expectations.get("nunchuk_status_caveat"):
        fail("senscope_export_package_sample.nunchuk_status_caveat drifted")

    validation_report = export_package.get("validation_report")
    if not isinstance(validation_report, dict):
        fail("senscope_export_package_sample.validation_report must be an object")
    confirmations = validation_report.get("no_forbidden_behavior_confirmation")
    if not isinstance(confirmations, dict):
        fail("senscope_export_package_sample.validation_report.no_forbidden_behavior_confirmation must be an object")
    if confirmations.get("runtime_loaded_config_absent") is not True:
        fail("senscope export package must preserve runtime_loaded_config_absent=true")
    if confirmations.get("serial_transport_absent") is not True:
        fail("senscope export package must preserve serial_transport_absent=true")


def validate_checker_backed_artifacts(paths: dict[str, Path]) -> None:
    for name in ("generated_config_evaluator_input_checker", "generated_cpp_diff_checker"):
        returncode, output = run_checker(paths[name])
        if returncode != 0 or "status=PASS" not in output:
            fail(f"{name} no longer passes its committed checker")


def main() -> int:
    print("glyph_export_artifact_round_trip")
    try:
        expectations = load_json_object(FIXTURE_PATH)
        checked_artifacts = validate_expectations_top_level(expectations)
        validate_doc(expectations)
        paths = artifact_paths_by_name(checked_artifacts)
        prototype = validate_generated_config_round_trip(paths)
        candidate = validate_runtime_candidate_round_trip(paths, prototype)
        export_package = validate_export_package_round_trip(paths, prototype)
        report = validate_runtime_report_round_trip(expectations, paths, candidate, prototype)
        validate_caveat_preservation(expectations, prototype, candidate, export_package, report)
        validate_checker_backed_artifacts(paths)
    except (OSError, ValueError, json.JSONDecodeError, ExportArtifactRoundTripError) as exc:
        print("status=FAIL")
        print("checked_artifacts=0")
        print("round_trip_invariants=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"checked_artifacts={len(expectations['checked_artifacts'])}")
    print(f"round_trip_invariants={len(expectations['round_trip_invariants'])}")
    print(f"hardware_status={expectations['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
