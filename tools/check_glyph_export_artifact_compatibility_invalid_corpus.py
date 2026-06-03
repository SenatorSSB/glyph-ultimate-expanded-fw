#!/usr/bin/env python3
"""Validate the offline invalid corpus for the Glyph export artifact bundle."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from check_glyph_senscope_export_package_validator import (
    EXPORT_CONTRACT_PATH,
    GENERATED_CONFIG_CONTRACT_PATH,
    validate_contracts,
    validate_export_package,
)
from generate_glyph_export_artifact_snapshots import canonical_text_hash
from glyph_generated_config_validator import (
    HARDWARE_STATUS,
    NUNCHUK_STATUS,
    load_json_object,
    validate_generated_config,
)
from glyph_runtime_config_candidate_validator import validate_runtime_config_candidate


REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_export_artifact_compatibility_invalid_corpus_2026-06-03.json"
)
DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_export_artifact_compatibility_invalid_corpus_2026-06-03.md"
)
GENERATED_CONFIG_PROTOTYPE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
RUNTIME_CONFIG_CANDIDATE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json"
)
SENSCOPE_EXPORT_PACKAGE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json"
)
RUNTIME_CONFIG_VALIDATION_REPORT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json"
)
BEHAVIOR_CASES_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json"
)
GENERATED_CPP_TABLE_ARTIFACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt"
)
SNAPSHOT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_export_artifact_snapshots_2026-06-03.json"
)

REQUIRED_DOC_PHRASES = (
    "docs/tools-only corpus",
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)
REQUIRED_REPORT_CAVEATS = (
    "offline_docs_tools_report_only",
    "not_runtime_loaded_config",
    "not_serial_device_write_behavior",
    "not_hardware_validation",
    "not_nunchuk_hardware_validation",
    "does_not_change_table_values_or_behavior",
)
ARTIFACT_KEYS = {
    "generated_config_prototype",
    "runtime_config_candidate_sample",
    "senscope_export_package_sample",
    "runtime_config_validation_report",
    "behavior_cases_fixture",
    "generated_cpp_table_artifact",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


class InvalidCorpusCheckError(ValueError):
    """Raised when the invalid corpus or bundle validation behavior drifts."""


def fail(message: str) -> None:
    raise InvalidCorpusCheckError(message)


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def add_issue(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code=code, path=path, message=message))


def load_corpus() -> dict[str, Any]:
    corpus = load_json_object(CORPUS_PATH)
    expected = {
        "schema_name": "glyph_export_artifact_compatibility_invalid_corpus",
        "corpus_version": 1,
        "status": "negative_compatibility_corpus",
        "hardware_status": HARDWARE_STATUS,
        "validator_tool": "tools/check_glyph_export_artifact_compatibility_invalid_corpus.py",
    }
    for key, value in expected.items():
        if corpus.get(key) != value:
            fail(f"corpus {key} must be {value!r}")
    return corpus


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{DOC_PATH.relative_to(REPO_ROOT)} missing required phrase: {phrase}")


def load_baseline_bundle() -> dict[str, Any]:
    export_contract = load_json_object(EXPORT_CONTRACT_PATH)
    generated_config_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
    validate_contracts(export_contract, generated_config_contract)
    return {
        "generated_config_prototype": load_json_object(GENERATED_CONFIG_PROTOTYPE_PATH),
        "runtime_config_candidate_sample": load_json_object(RUNTIME_CONFIG_CANDIDATE_PATH),
        "senscope_export_package_sample": load_json_object(SENSCOPE_EXPORT_PACKAGE_PATH),
        "runtime_config_validation_report": load_json_object(RUNTIME_CONFIG_VALIDATION_REPORT_PATH),
        "behavior_cases_fixture": load_json_object(BEHAVIOR_CASES_FIXTURE_PATH),
        "generated_cpp_table_artifact": GENERATED_CPP_TABLE_ARTIFACT_PATH.read_text(encoding="utf-8"),
        "export_artifact_snapshots": load_json_object(SNAPSHOT_PATH),
        "export_contract": export_contract,
        "generated_config_contract": generated_config_contract,
    }


def apply_path(container: Any, path: list[Any], value: Any) -> None:
    if not path:
        fail("mutation path must not be empty")
    current = container
    for segment in path[:-1]:
        if isinstance(current, dict) and isinstance(segment, str):
            if segment not in current:
                fail(f"mutation path missing object key {segment!r}")
            current = current[segment]
        elif isinstance(current, list) and isinstance(segment, int):
            if segment < 0 or segment >= len(current):
                fail(f"mutation path list index out of range: {segment}")
            current = current[segment]
        else:
            fail(f"mutation path segment {segment!r} is incompatible with current container")

    final = path[-1]
    if isinstance(current, dict) and isinstance(final, str):
        current[final] = value
        return
    if isinstance(current, list) and isinstance(final, int):
        if final < 0 or final >= len(current):
            fail(f"mutation path list index out of range: {final}")
        current[final] = value
        return
    fail(f"mutation path final segment {final!r} is incompatible with current container")


def delete_path(container: Any, path: list[Any]) -> None:
    if not path:
        fail("delete path must not be empty")
    current = container
    for segment in path[:-1]:
        if isinstance(current, dict) and isinstance(segment, str):
            if segment not in current:
                fail(f"delete path missing object key {segment!r}")
            current = current[segment]
        elif isinstance(current, list) and isinstance(segment, int):
            if segment < 0 or segment >= len(current):
                fail(f"delete path list index out of range: {segment}")
            current = current[segment]
        else:
            fail(f"delete path segment {segment!r} is incompatible with current container")

    final = path[-1]
    if isinstance(current, dict) and isinstance(final, str):
        if final not in current:
            fail(f"delete path missing object key {final!r}")
        del current[final]
        return
    if isinstance(current, list) and isinstance(final, int):
        if final < 0 or final >= len(current):
            fail(f"delete path list index out of range: {final}")
        del current[final]
        return
    fail(f"delete path final segment {final!r} is incompatible with current container")


def apply_mutation(bundle: dict[str, Any], mutation_ops: list[dict[str, Any]]) -> dict[str, Any]:
    mutated = copy.deepcopy(bundle)
    for op in mutation_ops:
        action = op.get("op")
        artifact = op.get("artifact")
        if artifact not in ARTIFACT_KEYS:
            fail(f"unsupported target artifact: {artifact!r}")

        if action == "replace_text":
            current = mutated[artifact]
            old = op.get("old")
            new = op.get("new")
            if not isinstance(current, str):
                fail(f"{artifact} does not support replace_text")
            if not isinstance(old, str) or not isinstance(new, str):
                fail("replace_text requires string old/new values")
            if old not in current:
                fail(f"replace_text old value not found in {artifact}")
            mutated[artifact] = current.replace(old, new, 1)
            continue

        path = require_list(op.get("path"), "mutation path")
        if not all(isinstance(segment, (str, int)) for segment in path):
            fail("mutation path segments must be strings or integers")
        container = mutated[artifact]
        if action == "set":
            apply_path(container, path, op.get("value"))
        elif action == "delete":
            delete_path(container, path)
        else:
            fail(f"unsupported mutation op: {action!r}")
    return mutated


def issue_drift_code(
    baseline_left: Any,
    baseline_right: Any,
    left: Any,
    right: Any,
    left_code: str,
    right_code: str,
    fallback_code: str,
) -> str:
    left_changed = left != baseline_left
    right_changed = right != baseline_right
    if left_changed and not right_changed:
        return left_code
    if right_changed and not left_changed:
        return right_code
    return fallback_code


def validate_validators(bundle: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for issue in validate_generated_config(bundle["generated_config_prototype"]):
        add_issue(issues, issue.code, f"generated_config_prototype:{issue.path}", issue.message)
    for issue in validate_runtime_config_candidate(bundle["runtime_config_candidate_sample"]):
        add_issue(issues, issue.code, f"runtime_config_candidate_sample:{issue.path}", issue.message)
    for issue in validate_export_package(
        bundle["senscope_export_package_sample"],
        bundle["export_contract"],
        bundle["generated_config_contract"],
    ):
        add_issue(issues, issue.code, f"senscope_export_package_sample:{issue.path}", issue.message)

    return issues


def validate_round_trip_invariants(
    bundle: dict[str, Any],
    baseline: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    prototype = require_object(bundle["generated_config_prototype"], "generated_config_prototype")
    candidate = require_object(bundle["runtime_config_candidate_sample"], "runtime_config_candidate_sample")
    export_package = require_object(bundle["senscope_export_package_sample"], "senscope_export_package_sample")
    report = require_object(bundle["runtime_config_validation_report"], "runtime_config_validation_report")

    prototype_tables = prototype.get("tables")
    candidate_tables = candidate.get("tables")
    if prototype_tables != candidate_tables:
        code = issue_drift_code(
            baseline["generated_config_prototype"].get("tables"),
            baseline["runtime_config_candidate_sample"].get("tables"),
            prototype_tables,
            candidate_tables,
            "E_GENERATED_CONFIG_TABLE_DRIFT",
            "E_RUNTIME_CANDIDATE_TABLE_DRIFT",
            "E_TABLE_COMPATIBILITY_DRIFT",
        )
        add_issue(
            issues,
            code,
            "$.tables",
            "generated-config tables must match runtime-candidate tables",
        )

    prototype_role_bindings = prototype.get("role_bindings")
    candidate_role_bindings = candidate.get("role_bindings")
    if prototype_role_bindings != candidate_role_bindings:
        add_issue(
            issues,
            "E_RUNTIME_CANDIDATE_ROLE_BINDING_DRIFT",
            "$.runtime_config_candidate_sample.role_bindings",
            "runtime-candidate role_bindings must match generated-config role_bindings",
        )

    prototype_hard_overrides = prototype.get("hard_overrides")
    candidate_hard_overrides = candidate.get("hard_overrides")
    if prototype_hard_overrides != candidate_hard_overrides:
        add_issue(
            issues,
            "E_RUNTIME_CANDIDATE_HARD_OVERRIDE_DRIFT",
            "$.runtime_config_candidate_sample.hard_overrides",
            "runtime-candidate hard_overrides must match generated-config hard_overrides",
        )

    priority_model = prototype.get("priority_model")
    if isinstance(priority_model, dict):
        expected_priority = {
            "digital": priority_model.get("digital_effective_direction"),
            "analog": priority_model.get("analog"),
        }
        if candidate.get("priority_references") != expected_priority:
            add_issue(
                issues,
                "E_RUNTIME_CANDIDATE_PRIORITY_REFERENCE_DRIFT",
                "$.runtime_config_candidate_sample.priority_references",
                "runtime-candidate priority_references must match generated-config priority_model",
            )

    if candidate.get("suppression_rules") != prototype.get("suppression_rules"):
        add_issue(
            issues,
            "E_RUNTIME_CANDIDATE_SUPPRESSION_RULE_DRIFT",
            "$.runtime_config_candidate_sample.suppression_rules",
            "runtime-candidate suppression_rules must match generated-config suppression_rules",
        )

    if export_package.get("glyph_generated_config_prototype") != prototype:
        add_issue(
            issues,
            "E_SENSCOPE_EXPORT_NESTED_GENERATED_CONFIG_DRIFT",
            "$.senscope_export_package_sample.glyph_generated_config_prototype",
            "Senscope export nested generated config must match the committed generated-config prototype",
        )

    candidate_tables_obj = candidate.get("tables")
    prototype_tables_obj = prototype.get("tables")
    if not isinstance(candidate_tables_obj, dict) or not isinstance(prototype_tables_obj, dict):
        return issues

    if report.get("table_count") != len(candidate_tables_obj) or report.get("table_count") != len(prototype_tables_obj):
        add_issue(
            issues,
            "E_VALIDATION_REPORT_TABLE_COUNT_DRIFT",
            "$.runtime_config_validation_report.table_count",
            "validation report table_count must match generated-config and runtime-candidate table counts",
        )

    caveats = report.get("caveats")
    if not isinstance(caveats, list) or any(item not in caveats for item in REQUIRED_REPORT_CAVEATS):
        add_issue(
            issues,
            "E_VALIDATION_REPORT_MISSING_CAVEAT",
            "$.runtime_config_validation_report.caveats",
            "validation report caveats must preserve the committed docs/tools caveats",
        )

    return issues


def validate_snapshot_invariants(bundle: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    snapshot = require_object(bundle["export_artifact_snapshots"], "export_artifact_snapshots")
    artifacts = require_object(snapshot.get("artifacts"), "export_artifact_snapshots.artifacts")

    cpp_snapshot = require_object(artifacts.get("generated_cpp_table_artifact"), "generated_cpp_table_artifact")
    expected_cpp_hash = cpp_snapshot.get("sha256")
    if not isinstance(expected_cpp_hash, str):
        fail("generated_cpp_table_artifact.sha256 must be a string")
    actual_cpp_hash = canonical_text_hash(bundle["generated_cpp_table_artifact"].replace("\r\n", "\n"))
    if actual_cpp_hash != expected_cpp_hash:
        add_issue(
            issues,
            "E_GENERATED_CPP_TABLE_HASH_DRIFT",
            "$.generated_cpp_table_artifact",
            "generated C++ table artifact hash must match the committed canonical snapshot",
        )

    behavior_snapshot = require_object(artifacts.get("behavior_cases_fixture"), "behavior_cases_fixture")
    behavior_summary = require_object(behavior_snapshot.get("summary"), "behavior_cases_fixture.summary")
    behavior_cases = require_list(bundle["behavior_cases_fixture"].get("cases"), "behavior_cases_fixture.cases")
    if behavior_summary.get("case_count") != len(behavior_cases):
        add_issue(
            issues,
            "E_BEHAVIOR_CASE_COUNT_DRIFT",
            "$.behavior_cases_fixture.cases",
            "behavior case count must match the committed canonical snapshot summary",
        )

    return issues


def validate_claim_caveats(bundle: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    export_package = require_object(bundle["senscope_export_package_sample"], "senscope_export_package_sample")

    hardware_status = export_package.get("hardware_status")
    if hardware_status != HARDWARE_STATUS:
        add_issue(
            issues,
            "E_HARDWARE_STATUS_VALIDATION_CLAIM",
            "$.senscope_export_package_sample.hardware_status",
            "sample export package hardware_status must stay not_new_hardware_result",
        )

    nunchuk_status = export_package.get("nunchuk_status")
    if nunchuk_status != NUNCHUK_STATUS:
        add_issue(
            issues,
            "E_NUNCHUK_STATUS_VALIDATION_CLAIM",
            "$.senscope_export_package_sample.nunchuk_status",
            "sample export package nunchuk_status must stay preserved_but_not_hardware_validated",
        )

    status = export_package.get("status")
    if isinstance(status, str) and "runtime_loaded_config" in status:
        add_issue(
            issues,
            "E_RUNTIME_LOADED_CONFIG_STATUS_CLAIM",
            "$.senscope_export_package_sample.status",
            "sample export package must not claim runtime-loaded config implementation",
        )

    validation_report = export_package.get("validation_report")
    if isinstance(validation_report, dict):
        confirmations = validation_report.get("no_forbidden_behavior_confirmation")
        if isinstance(confirmations, dict):
            if confirmations.get("runtime_loaded_config_absent") is not True:
                add_issue(
                    issues,
                    "E_RUNTIME_LOADED_CONFIG_STATUS_CLAIM",
                    "$.senscope_export_package_sample.validation_report.no_forbidden_behavior_confirmation.runtime_loaded_config_absent",
                    "sample export package must preserve runtime_loaded_config_absent=true",
                )
            if (
                confirmations.get("device_write_absent") is not True
                or confirmations.get("serial_transport_absent") is not True
            ):
                add_issue(
                    issues,
                    "E_SERIAL_DEVICE_WRITE_CLAIM",
                    "$.senscope_export_package_sample.validation_report.no_forbidden_behavior_confirmation",
                    "sample export package must preserve device_write_absent=true and serial_transport_absent=true",
                )

    return issues


def validate_bundle(bundle: dict[str, Any], baseline: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(validate_validators(bundle))
    issues.extend(validate_round_trip_invariants(bundle, baseline))
    issues.extend(validate_snapshot_invariants(bundle))
    issues.extend(validate_claim_caveats(bundle))
    return issues


def main() -> int:
    print("glyph_export_artifact_compatibility_invalid_corpus")
    try:
        corpus = load_corpus()
        validate_doc()
        baseline = load_baseline_bundle()
        baseline_issues = validate_bundle(baseline, baseline)
        if baseline_issues:
            first = baseline_issues[0]
            fail(f"baseline bundle must pass before mutations: {first.code} at {first.path}")

        cases = require_list(corpus.get("cases"), "corpus cases")
        if not cases:
            fail("corpus cases must not be empty")

        invalid_cases = 0
        for case in cases:
            case_obj = require_object(case, "corpus case")
            case_id = case_obj.get("case_id")
            mutation = case_obj.get("mutation")
            target_artifact = case_obj.get("target_artifact")
            expected_codes = require_list(case_obj.get("expected_error_codes"), f"{case_id}.expected_error_codes")
            mutation_ops = require_list(case_obj.get("payload"), f"{case_id}.payload")

            if not isinstance(case_id, str) or not case_id:
                fail("each corpus case must have a string case_id")
            if not isinstance(mutation, str) or not mutation:
                fail(f"{case_id} must have a string mutation")
            if target_artifact not in ARTIFACT_KEYS:
                fail(f"{case_id}.target_artifact must be one of the supported artifact keys")
            if not all(isinstance(code, str) for code in expected_codes):
                fail(f"{case_id}.expected_error_codes must be a string list")
            if not all(isinstance(op, dict) for op in mutation_ops):
                fail(f"{case_id}.payload must be a list of mutation objects")

            mutated = apply_mutation(baseline, mutation_ops)
            issues = validate_bundle(mutated, baseline)
            if not issues:
                fail(f"{case_id} unexpectedly passed compatibility validation")

            actual_codes = {issue.code for issue in issues}
            missing = sorted(set(expected_codes) - actual_codes)
            if missing:
                fail(f"{case_id} missing expected error code(s): {', '.join(missing)}")
            invalid_cases += 1

        print("status=PASS")
        print(f"invalid_cases={invalid_cases}")
        print(f"hardware_status={HARDWARE_STATUS}")
        return 0
    except (OSError, ValueError, InvalidCorpusCheckError) as exc:
        print("status=FAIL")
        print("invalid_cases=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
