#!/usr/bin/env python3
"""Validate a docs-only draft Senscope-to-Glyph export package sample.

This checker validates a future package shape against committed docs/tools
contracts. It is not Senscope app code, not firmware, not runtime-loaded config,
not serial/device write behavior, and not hardware validation.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from glyph_generated_config_validator import load_json_object, validate_generated_config


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json"
)
GENERATED_CONFIG_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)
SAMPLE_PACKAGE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json"
)
INVALID_CORPUS_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_senscope_export_package_invalid_corpus_2026-06-03.json"
)
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_senscope_export_package_validator_draft_2026-06-03.md"

SCHEMA_NAME = "glyph_senscope_export_package"
PACKAGE_VERSION = 1
STATUS = "sample_docs_only_not_implemented"
HARDWARE_STATUS = "not_new_hardware_result"
NUNCHUK_STATUS = "preserved_but_not_hardware_validated"

REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_name",
    "package_version",
    "status",
    "hardware_status",
    "nunchuk_status",
    "neutral_senscope_profile",
    "glyph_generated_config_prototype",
    "table_source_metadata",
    "role_binding_metadata",
    "validation_report",
    "hardware_status_caveat",
    "nunchuk_status_caveat",
)
REQUIRED_DOC_PHRASES = (
    "draft validator only",
    "not senscope app implementation",
    "not firmware",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
)
FORBIDDEN_KEYS_TO_CODES = {
    "device_write_instruction": "E_DEVICE_WRITE_SCOPE",
    "device_write_payload": "E_DEVICE_WRITE_SCOPE",
    "serial_transport_payload": "E_SERIAL_TRANSPORT_SCOPE",
    "runtime_loaded_config_implementation": "E_RUNTIME_LOADED_CONFIG_IMPLEMENTATION_CLAIM",
    "firmware_source_patch": "E_FIRMWARE_BEHAVIOR_CHANGE_CLAIM",
    "firmware_behavior_change": "E_FIRMWARE_BEHAVIOR_CHANGE_CLAIM",
    "profile_schema_change": "E_PROFILE_SCHEMA_CHANGE_CLAIM",
    "macro_or_turbo_logic": "E_MACRO_TURBO_TIMING_SCOPE",
    "macro_logic": "E_MACRO_TURBO_TIMING_SCOPE",
    "turbo_logic": "E_MACRO_TURBO_TIMING_SCOPE",
    "timing_logic": "E_MACRO_TURBO_TIMING_SCOPE",
    "history_dependent_logic": "E_MACRO_TURBO_TIMING_SCOPE",
    "hardware_validation_result": "E_HARDWARE_VALIDATION_CLAIM_WITHOUT_RESULT",
    "nunchuk_hardware_validation_result": "E_NUNCHUK_HARDWARE_VALIDATION_CLAIM",
}


@dataclass(frozen=True)
class PackageIssue:
    code: str
    path: str
    message: str


class ExportPackageCheckError(ValueError):
    """Raised when the export package checker finds invalid fixture state."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ExportPackageCheckError(message)


def add_issue(issues: list[PackageIssue], code: str, path: str, message: str) -> None:
    issues.append(PackageIssue(code, path, message))


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def validate_contracts(export_contract: dict[str, Any], generated_config_contract: dict[str, Any]) -> None:
    expected_export_contract = {
        "schema_name": "glyph_senscope_to_glyph_export_contract_draft",
        "contract_version": 1,
        "status": "draft_docs_only_not_implemented",
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
        "target_generated_config_contract": display(GENERATED_CONFIG_CONTRACT_PATH),
    }
    for key, value in expected_export_contract.items():
        if export_contract.get(key) != value:
            fail(f"export contract {key} must be {value!r}")

    required_payloads = require_string_list(export_contract, "required_export_payloads")
    if required_payloads != list(REQUIRED_TOP_LEVEL_FIELDS[5:]):
        fail("export contract required_export_payloads drifted from package validator")
    required_sections = require_string_list(export_contract, "validation_report_required_sections")
    if not required_sections:
        fail("export contract validation_report_required_sections must not be empty")

    required_forbidden_scope = {
        "device_write",
        "serial_transport",
        "runtime_loaded_config",
        "firmware_behavior_change",
        "profile_schema_change",
        "macro_or_turbo_logic",
        "hardware_validation_claim",
    }
    missing_forbidden = sorted(required_forbidden_scope - set(require_string_list(export_contract, "forbidden_scope")))
    if missing_forbidden:
        fail("export contract forbidden_scope missing: " + ", ".join(missing_forbidden))

    expected_generated_contract = {
        "schema_name": "glyph_identity_runtime_generated_config_contract",
        "contract_version": 1,
        "target_schema_name": "glyph_identity_runtime_generated_config_prototype",
        "target_contract_version": 1,
        "status": "docs_tools_contract_not_runtime_loaded",
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected_generated_contract.items():
        if generated_config_contract.get(key) != value:
            fail(f"generated-config contract {key} must be {value!r}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_export_package(
    payload: Any,
    export_contract: dict[str, Any],
    generated_config_contract: dict[str, Any],
) -> list[PackageIssue]:
    issues: list[PackageIssue] = []
    if not isinstance(payload, dict):
        return [PackageIssue("E_ROOT_NOT_OBJECT", "$", "export package root must be an object")]

    for key in REQUIRED_TOP_LEVEL_FIELDS:
        if key not in payload:
            add_issue(issues, "E_MISSING_REQUIRED_FIELD", f"$.{key}", "missing required top-level field")

    expected_scalars = {
        "schema_name": SCHEMA_NAME,
        "package_version": PACKAGE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected_scalars.items():
        if payload.get(key) != value:
            add_issue(issues, f"E_INVALID_{key.upper()}", f"$.{key}", f"must be {value!r}")

    contract_payloads = require_string_list(export_contract, "required_export_payloads")
    for key in contract_payloads:
        if key not in payload:
            add_issue(issues, "E_MISSING_EXPORT_PAYLOAD", f"$.{key}", "missing required export payload")

    _validate_neutral_profile(payload.get("neutral_senscope_profile"), issues)
    _validate_generated_config(payload.get("glyph_generated_config_prototype"), generated_config_contract, issues)
    _validate_metadata(payload, issues)
    _validate_validation_report(payload.get("validation_report"), export_contract, issues)
    _validate_caveats(payload, issues)
    _validate_forbidden_scope(payload, issues)
    return issues


def _validate_neutral_profile(value: Any, issues: list[PackageIssue]) -> None:
    if not isinstance(value, dict):
        add_issue(issues, "E_NEUTRAL_PROFILE_NOT_OBJECT", "$.neutral_senscope_profile", "must be an object")
        return
    if value.get("schema_status") != "placeholder_deferred_to_senscope":
        add_issue(
            issues,
            "E_NEUTRAL_PROFILE_SCHEMA_NOT_DEFERRED",
            "$.neutral_senscope_profile.schema_status",
            "must explicitly defer the actual Senscope schema to Senscope",
        )
    if value.get("senscope_schema_authority") != "deferred_to_senscope":
        add_issue(
            issues,
            "E_NEUTRAL_PROFILE_SCHEMA_NOT_DEFERRED",
            "$.neutral_senscope_profile.senscope_schema_authority",
            "must not define Senscope app-owned schema authority in this repo",
        )


def _validate_generated_config(
    value: Any,
    generated_config_contract: dict[str, Any],
    issues: list[PackageIssue],
) -> None:
    if not isinstance(value, dict):
        add_issue(
            issues,
            "E_GENERATED_CONFIG_NOT_OBJECT",
            "$.glyph_generated_config_prototype",
            "must be an object",
        )
        return
    if value.get("schema_name") != generated_config_contract.get("target_schema_name"):
        add_issue(
            issues,
            "E_GENERATED_CONFIG_CONTRACT_MISMATCH",
            "$.glyph_generated_config_prototype.schema_name",
            "must match generated-config contract target_schema_name",
        )
    if value.get("contract_version") != generated_config_contract.get("target_contract_version"):
        add_issue(
            issues,
            "E_GENERATED_CONFIG_CONTRACT_MISMATCH",
            "$.glyph_generated_config_prototype.contract_version",
            "must match generated-config contract target_contract_version",
        )
    generated_issues = validate_generated_config(value)
    if generated_issues:
        first = generated_issues[0]
        add_issue(
            issues,
            "E_INVALID_GENERATED_CONFIG",
            "$.glyph_generated_config_prototype",
            f"nested generated config failed validation: {first.code} at {first.path}",
        )


def _validate_metadata(payload: dict[str, Any], issues: list[PackageIssue]) -> None:
    table_source_metadata = payload.get("table_source_metadata")
    if not isinstance(table_source_metadata, dict):
        add_issue(issues, "E_TABLE_SOURCE_METADATA_NOT_OBJECT", "$.table_source_metadata", "must be an object")
    else:
        if table_source_metadata.get("export_contract") != display(EXPORT_CONTRACT_PATH):
            add_issue(
                issues,
                "E_INVALID_TABLE_SOURCE_METADATA",
                "$.table_source_metadata.export_contract",
                "must cite the export contract fixture",
            )
        if table_source_metadata.get("generated_config_contract") != display(GENERATED_CONFIG_CONTRACT_PATH):
            add_issue(
                issues,
                "E_INVALID_TABLE_SOURCE_METADATA",
                "$.table_source_metadata.generated_config_contract",
                "must cite the generated-config contract fixture",
            )

    role_binding_metadata = payload.get("role_binding_metadata")
    if not isinstance(role_binding_metadata, dict):
        add_issue(issues, "E_ROLE_BINDING_METADATA_NOT_OBJECT", "$.role_binding_metadata", "must be an object")
    else:
        if role_binding_metadata.get("status") != "source_backed_metadata_only":
            add_issue(
                issues,
                "E_INVALID_ROLE_BINDING_METADATA",
                "$.role_binding_metadata.status",
                "must be source_backed_metadata_only",
            )


def _validate_validation_report(
    value: Any,
    export_contract: dict[str, Any],
    issues: list[PackageIssue],
) -> None:
    if not isinstance(value, dict):
        add_issue(issues, "E_VALIDATION_REPORT_NOT_OBJECT", "$.validation_report", "must be an object")
        return
    for section in require_string_list(export_contract, "validation_report_required_sections"):
        if section not in value:
            add_issue(
                issues,
                "E_MISSING_VALIDATION_REPORT_SECTION",
                f"$.validation_report.{section}",
                "missing validation report section",
            )


def _validate_caveats(payload: dict[str, Any], issues: list[PackageIssue]) -> None:
    if payload.get("hardware_status_caveat") != "Sample package only; not hardware validation.":
        add_issue(
            issues,
            "E_INVALID_HARDWARE_STATUS_CAVEAT",
            "$.hardware_status_caveat",
            "must preserve the not-hardware-validation caveat",
        )
    if payload.get("nunchuk_status_caveat") != "Nunchuk behavior is preserved but not hardware validated by this package.":
        add_issue(
            issues,
            "E_INVALID_NUNCHUK_STATUS_CAVEAT",
            "$.nunchuk_status_caveat",
            "must preserve the nunchuk non-validation caveat",
        )


def _validate_forbidden_scope(payload: dict[str, Any], issues: list[PackageIssue]) -> None:
    for path, key, value in walk(payload):
        normalized_key = key.lower() if isinstance(key, str) else ""
        code = FORBIDDEN_KEYS_TO_CODES.get(normalized_key)
        if code is not None:
            add_issue(issues, code, path, f"forbidden export package key {key!r}")
        if normalized_key == "device_writeable" and value is True:
            add_issue(issues, "E_DEVICE_WRITE_SCOPE", path, "sample package must not claim device-writeability")
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        if contains_positive_claim(lowered, ("device write instruction", "device-writeable", "device writeable")):
            add_issue(issues, "E_DEVICE_WRITE_SCOPE", path, "device write scope is forbidden")
        if contains_positive_claim(lowered, ("serial transport payload", "serial transport implementation")):
            add_issue(issues, "E_SERIAL_TRANSPORT_SCOPE", path, "serial transport scope is forbidden")
        if contains_positive_claim(
            lowered,
            ("runtime-loaded config implemented", "runtime loaded config implemented"),
        ):
            add_issue(
                issues,
                "E_RUNTIME_LOADED_CONFIG_IMPLEMENTATION_CLAIM",
                path,
                "runtime-loaded config implementation claims are forbidden",
            )
        if contains_positive_claim(lowered, ("firmware behavior change implemented", "firmware behavior changed")):
            add_issue(
                issues,
                "E_FIRMWARE_BEHAVIOR_CHANGE_CLAIM",
                path,
                "firmware behavior change claims are forbidden",
            )
        if contains_positive_claim(lowered, ("profile schema change implemented", "profile schema changed")):
            add_issue(
                issues,
                "E_PROFILE_SCHEMA_CHANGE_CLAIM",
                path,
                "profile schema change claims are forbidden",
            )
        if contains_positive_claim(
            lowered,
            ("macro/turbo", "macro or turbo logic", "timing automation", "history-dependent behavior"),
        ):
            add_issue(
                issues,
                "E_MACRO_TURBO_TIMING_SCOPE",
                path,
                "macro, turbo, timing, or history-dependent scope is forbidden",
            )
        if is_nunchuk_hardware_validation_claim(lowered):
            add_issue(
                issues,
                "E_NUNCHUK_HARDWARE_VALIDATION_CLAIM",
                path,
                "nunchuk hardware validation claims are forbidden",
            )
        elif is_hardware_validation_claim(lowered):
            add_issue(
                issues,
                "E_HARDWARE_VALIDATION_CLAIM_WITHOUT_RESULT",
                path,
                "hardware validation claims are forbidden without a hardware result",
            )


def contains_positive_claim(value: str, phrases: tuple[str, ...]) -> bool:
    if not any(phrase in value for phrase in phrases):
        return False
    negations = (
        "not ",
        "no ",
        "without ",
        "does not ",
        "must not ",
        "non-",
        "absent",
        "forbidden",
    )
    return not any(negation + phrase in value for phrase in phrases for negation in negations)


def is_hardware_validation_claim(value: str) -> bool:
    if "hardware validation" not in value and "hardware-validated" not in value:
        return False
    negations = (
        "not hardware validation",
        "no hardware validation",
        "not hardware-validated",
        "not hardware validated",
        "without hardware validation",
        "does not validate hardware",
        "non-validation",
    )
    return not any(negation in value for negation in negations)


def is_nunchuk_hardware_validation_claim(value: str) -> bool:
    return "nunchuk" in value and is_hardware_validation_claim(value)


def walk(value: Any, path: str = "$", key: str = "") -> list[tuple[str, str, Any]]:
    entries = [(path, key, value)]
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            child_path = f"{path}.{child_key}" if isinstance(child_key, str) else f"{path}.{child_key!r}"
            entries.extend(walk(child_value, child_path, str(child_key)))
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            entries.extend(walk(child_value, f"{path}[{index}]", key))
    return entries


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


def apply_mutation(payload: dict[str, Any], mutation_ops: list[dict[str, Any]]) -> dict[str, Any]:
    mutated = copy.deepcopy(payload)
    for op in mutation_ops:
        action = op.get("op")
        path = require_list(op.get("path"), "mutation path")
        if not all(isinstance(segment, (str, int)) for segment in path):
            fail("mutation path segments must be strings or integers")
        if action == "set":
            apply_path(mutated, path, op.get("value"))
        elif action == "delete":
            delete_path(mutated, path)
        else:
            fail(f"unsupported mutation op: {action!r}")
    return mutated


def validate_invalid_corpus(
    corpus: dict[str, Any],
    baseline: dict[str, Any],
    export_contract: dict[str, Any],
    generated_config_contract: dict[str, Any],
) -> int:
    expected = {
        "schema_name": "glyph_senscope_export_package_invalid_corpus",
        "corpus_version": 1,
        "status": "negative_validator_corpus",
        "hardware_status": HARDWARE_STATUS,
        "validator_tool": "tools/check_glyph_senscope_export_package_validator.py",
        "baseline_fixture": display(SAMPLE_PACKAGE_PATH),
    }
    for key, value in expected.items():
        if corpus.get(key) != value:
            fail(f"invalid corpus {key} must be {value!r}")

    cases = require_list(corpus.get("cases"), "invalid corpus cases")
    if not cases:
        fail("invalid corpus cases must not be empty")

    invalid_cases = 0
    for case in cases:
        case_obj = require_object(case, "invalid corpus case")
        case_id = case_obj.get("case_id")
        mutation = case_obj.get("mutation")
        expected_codes = require_list(case_obj.get("expected_error_codes"), f"{case_id}.expected_error_codes")
        mutation_ops = require_list(case_obj.get("payload"), f"{case_id}.payload")
        if not isinstance(case_id, str) or not case_id:
            fail("each invalid corpus case must have a string case_id")
        if not isinstance(mutation, str) or not mutation:
            fail(f"{case_id} must have a string mutation")
        if not all(isinstance(code, str) for code in expected_codes):
            fail(f"{case_id}.expected_error_codes must be a string list")
        if not all(isinstance(op, dict) for op in mutation_ops):
            fail(f"{case_id}.payload must be a list of mutation objects")

        mutated = apply_mutation(baseline, mutation_ops)
        issues = validate_export_package(mutated, export_contract, generated_config_contract)
        if not issues:
            fail(f"{case_id} unexpectedly passed validation")
        actual_codes = {issue.code for issue in issues}
        missing = sorted(set(expected_codes) - actual_codes)
        if missing:
            fail(f"{case_id} missing expected error code(s): {', '.join(missing)}")
        invalid_cases += 1
    return invalid_cases


def main() -> int:
    print("glyph_senscope_export_package_validator")
    sample_validated = False
    invalid_cases = 0
    try:
        export_contract = load_json_object(EXPORT_CONTRACT_PATH)
        generated_config_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
        sample = load_json_object(SAMPLE_PACKAGE_PATH)
        corpus = load_json_object(INVALID_CORPUS_PATH)
        validate_contracts(export_contract, generated_config_contract)
        validate_doc()

        issues = validate_export_package(sample, export_contract, generated_config_contract)
        if issues:
            print("status=FAIL")
            print("sample_validated=false")
            print("invalid_cases=0")
            print(f"hardware_status={HARDWARE_STATUS}")
            for issue in issues:
                print(f"issue={issue.code} path={issue.path} message={issue.message}")
            return 1
        sample_validated = True
        invalid_cases = validate_invalid_corpus(corpus, sample, export_contract, generated_config_contract)
    except (OSError, ValueError, ExportPackageCheckError) as exc:
        print("status=FAIL")
        print(f"sample_validated={str(sample_validated).lower()}")
        print(f"invalid_cases={invalid_cases}")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("sample_validated=true")
    print(f"invalid_cases={invalid_cases}")
    print(f"hardware_status={HARDWARE_STATUS}")
    print(f"sample_package={display(SAMPLE_PACKAGE_PATH)}")
    print(f"invalid_corpus={display(INVALID_CORPUS_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
