#!/usr/bin/env python3
"""Generate a docs/tools-only Glyph runtime config validation report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from glyph_runtime_config_candidate_validator import (
    HARDWARE_STATUS,
    NUNCHUK_STATUS,
    REQUIRED_NON_GOALS,
    SCHEMA_NAME as CANDIDATE_SCHEMA_NAME,
    load_json_object,
    validate_runtime_config_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_WRITE_ROOT = REPO_ROOT / "docs/calibration/fixtures"

SAMPLE_CANDIDATE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json"
)
VALIDATOR_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_validator_contract_v0_2026-06-03.json"
)
INVALID_CORPUS_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_invalid_corpus_2026-06-03.json"
)
GENERATED_CONFIG_VALIDATOR_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_offline_generated_config_validator_contract_v0_2026-06-03.json"
)
GENERATED_CONFIG_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json"
)
RUNTIME_VALIDATION_CONTRACT_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json"
)

REPORT_SCHEMA_NAME = "glyph_runtime_config_validation_report"
REPORT_VERSION = 1
REPORT_STATUS = "docs_tools_validation_report"
REPORT_CAVEATS = (
    "offline_docs_tools_report_only",
    "not_runtime_loaded_config",
    "not_serial_device_write_behavior",
    "not_hardware_validation",
    "not_nunchuk_hardware_validation",
    "does_not_change_table_values_or_behavior",
)


class RuntimeConfigValidationReportError(ValueError):
    """Raised when the report inputs or output contract drift."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise RuntimeConfigValidationReportError(message)


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def _write_json(path: Path, report: dict[str, Any]) -> None:
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved_root = ALLOWED_WRITE_ROOT.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise RuntimeConfigValidationReportError(
            "--write-json path must be under docs/calibration/fixtures/"
        ) from exc
    resolved_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report() -> dict[str, Any]:
    sample = load_json_object(SAMPLE_CANDIDATE_PATH)
    validator_contract = load_json_object(VALIDATOR_CONTRACT_PATH)
    invalid_corpus = load_json_object(INVALID_CORPUS_PATH)
    generated_config_validator_contract = load_json_object(GENERATED_CONFIG_VALIDATOR_CONTRACT_PATH)
    generated_config_contract = load_json_object(GENERATED_CONFIG_CONTRACT_PATH)
    runtime_validation_contract = load_json_object(RUNTIME_VALIDATION_CONTRACT_PATH)

    if sample.get("schema_name") != CANDIDATE_SCHEMA_NAME:
        fail("sample candidate schema_name drifted from validator target")
    if validator_contract.get("target_schema_name") != CANDIDATE_SCHEMA_NAME:
        fail("validator contract target_schema_name drifted from sample candidate schema")
    if generated_config_validator_contract.get("status") != "tooling_validator_only_not_runtime_loaded":
        fail("generated-config validator contract status drifted")
    if generated_config_contract.get("status") != "docs_tools_contract_not_runtime_loaded":
        fail("generated-config contract status drifted")
    if runtime_validation_contract.get("status") != "validation_contract_design_only_not_implemented":
        fail("runtime validation contract status drifted")

    issues = validate_runtime_config_candidate(sample)
    sample_status = "PASS" if not issues else "FAIL"
    invalid_cases = invalid_corpus.get("cases")
    if not isinstance(invalid_cases, list):
        fail("invalid corpus cases must be a list")
    tables = sample.get("tables")
    if not isinstance(tables, dict):
        fail("sample candidate tables must be an object")

    return {
        "caveats": list(REPORT_CAVEATS),
        "generated_config_context": {
            "generated_config_contract_status": generated_config_contract.get("status"),
            "generated_config_validator_contract_status": generated_config_validator_contract.get("status"),
            "generated_config_validator_target_schema_name": generated_config_validator_contract.get(
                "target_schema_name"
            ),
        },
        "hardware_status": HARDWARE_STATUS,
        "invalid_corpus_case_count": len(invalid_cases),
        "nunchuk_status": NUNCHUK_STATUS,
        "rejected_capability_summary": {
            "candidate_validator_forbidden_payload_content": require_string_list(
                validator_contract, "forbidden_payload_content"
            ),
            "generated_config_forbidden_interpretations": require_string_list(
                generated_config_contract, "forbidden_interpretations"
            ),
            "generated_config_validator_forbidden_payload_content": require_string_list(
                generated_config_validator_contract, "forbidden_payload_content"
            ),
            "runtime_loaded_validation_forbidden_payload_content": require_string_list(
                runtime_validation_contract, "forbidden_payload_content"
            ),
            "runtime_loaded_validation_required_rejection_rules": require_string_list(
                runtime_validation_contract, "required_rejection_rules"
            ),
        },
        "report_version": REPORT_VERSION,
        "required_non_goals": sorted(REQUIRED_NON_GOALS),
        "sample_candidate_validation_status": sample_status,
        "schema_name": REPORT_SCHEMA_NAME,
        "source_authority": {
            "generated_config_contract": display(GENERATED_CONFIG_CONTRACT_PATH),
            "generated_config_validator_contract": display(GENERATED_CONFIG_VALIDATOR_CONTRACT_PATH),
            "invalid_corpus": display(INVALID_CORPUS_PATH),
            "runtime_loaded_validation_contract": display(RUNTIME_VALIDATION_CONTRACT_PATH),
            "sample_candidate": display(SAMPLE_CANDIDATE_PATH),
            "validator_contract": display(VALIDATOR_CONTRACT_PATH),
        },
        "status": REPORT_STATUS,
        "table_count": len(tables),
        "validated_candidate_schema_name": sample.get("schema_name"),
        "validator_contract_status": validator_contract.get("status"),
    }


def print_text_summary(report: dict[str, Any], write_json_path: Path | None = None) -> None:
    print("glyph_runtime_config_validation_report")
    print("status=PASS")
    print(f"report_schema={report['schema_name']}")
    print(f"report_version={report['report_version']}")
    print(f"sample_candidate_validation_status={report['sample_candidate_validation_status']}")
    print(f"invalid_corpus_case_count={report['invalid_corpus_case_count']}")
    print(f"table_count={report['table_count']}")
    print(f"hardware_status={report['hardware_status']}")
    print(f"nunchuk_status={report['nunchuk_status']}")
    if write_json_path is not None:
        path = write_json_path if write_json_path.is_absolute() else REPO_ROOT / write_json_path
        print(f"wrote_json={display(path)}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print deterministic JSON")
    parser.add_argument("--write-json", type=Path, help="write report JSON under docs/calibration/fixtures/")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report()
        if args.write_json is not None:
            _write_json(args.write_json, report)
    except (OSError, ValueError, RuntimeConfigValidationReportError) as exc:
        print("glyph_runtime_config_validation_report")
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_summary(report, args.write_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
