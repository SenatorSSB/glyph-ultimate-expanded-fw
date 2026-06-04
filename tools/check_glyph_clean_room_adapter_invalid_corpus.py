#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter invalid corpus as a planning fixture."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_clean_room_adapter_invalid_corpus_2026-06-04.md"
)
CONTRACT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json"
)
INVALID_CORPUS_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_invalid_corpus_2026-06-04.json"
)
PLACEHOLDER_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_SCHEMA_PLACEHOLDER_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_invalid_corpus"
STATUS = "docs_tools_invalid_corpus"
HARDWARE_STATUS = "not_new_hardware_result"

DEPENDENCY_CHECKERS = (
    "tools/check_glyph_clean_room_adapter_negative_corpus_contract.py",
    "tools/check_glyph_clean_room_adapter_invalid_corpus_fixture.py",
    "tools/check_glyph_clean_room_adapter_candidate_schema_validator.py",
)

CASE_EXPECTED_ERROR_CODES = {
    "missing_sidecar": ["clean_room_candidate.sidecar.required"],
    "missing_runtime_owned_behavior_warning": [
        "clean_room_candidate.runtime_owned_behavior_warning.required"
    ],
    "missing_non_round_trip_warning": [
        "clean_room_candidate.non_round_trip_warning.required"
    ],
    "claims_round_trip_safe": ["clean_room_candidate.round_trip_safe.false_required"],
    "claims_active_profile_round_trip_safe": [
        "clean_room_candidate.active_profile_round_trip_safe.false_required"
    ],
    "claims_runtime_owned_behavior_represented_by_external_profile_json": [
        "clean_room_candidate.runtime_owned_behavior_external_profile_json.false_required"
    ],
    "adapter_implemented": ["clean_room_candidate.adapter_implemented.false_required"],
    "external_json_generated": [
        "clean_room_candidate.external_json_generated.false_required"
    ],
    "generated_external_json_output_path_present": [
        "clean_room_candidate.external_json_output_path.forbidden"
    ],
    "device_write_allowed": [
        "clean_room_candidate.device_write_allowed.false_required"
    ],
    "webserial_allowed": ["clean_room_candidate.webserial_allowed.false_required"],
    "protobuf_binary_generation_allowed": [
        "clean_room_candidate.protobuf_binary_generation_allowed.false_required"
    ],
    "runtime_loaded_config_allowed": [
        "clean_room_candidate.runtime_loaded_config_allowed.false_required"
    ],
    "official_compatibility_claimed": [
        "clean_room_candidate.official_compatibility_claimed.false_required"
    ],
    "hardware_validation_claimed": [
        "clean_room_candidate.hardware_validation_claimed.false_required"
    ],
    "external_source_promoted_to_authority": [
        "clean_room_candidate.external_source_promoted_to_authority.false_required"
    ],
    "copied_external_source_code": [
        "clean_room_candidate.external_code_reuse.forbidden"
    ],
    "external_dependency_added": [
        "clean_room_candidate.external_dependency_added.forbidden"
    ],
    "missing_source_authority_classification": [
        "clean_room_candidate.source_authority_classification.required"
    ],
    "missing_validation_report": [
        "clean_room_candidate.validation_report.required"
    ],
    "missing_loss_warnings": ["clean_room_candidate.loss_warnings.required"],
    "binding_loss_warning_suppressed": [
        "clean_room_candidate.binding_loss_warning.required"
    ],
    "socd_drift_warning_suppressed": [
        "clean_room_candidate.socd_drift_warning.required"
    ],
}

ALLOWED_CASE_KEYS = {
    "case_id",
    "category",
    "expected_error_codes",
    "must_fail",
    "must_not_claim_hardware_validation",
    "must_not_claim_official_compatibility",
    "must_not_generate_external_json",
    "mutation_description",
    "required_rejection_basis",
}

FORBIDDEN_OUTPUT_PATH_KEYS = {
    "external_json_output_path",
    "generated_external_json_path",
    "output_path_to_generated_external_json",
}

REQUIRED_DOC_PHRASES = (
    "tools/check_glyph_clean_room_adapter_invalid_corpus.py",
    "planning fixture validation only",
    "no mutation application",
    "no adapter candidate generation",
    "does not execute an adapter",
    "no case can be interpreted as a valid adapter output",
    "not official compatibility",
    "not hardware validation",
)

CASE_INVALIDATION_RULES = {
    "missing_sidecar": [("placeholder", ("runtime_owned_behavior_sidecar_required",), True)],
    "missing_runtime_owned_behavior_warning": [
        ("contract", ("negative_corpus_rules", "runtime_owned_behavior_warning_required"), True)
    ],
    "missing_non_round_trip_warning": [
        ("contract", ("negative_corpus_rules", "validation_report_required"), True),
        ("contract", ("supporting_findings", "non_round_trip_warning_required"), True),
    ],
    "claims_round_trip_safe": [("placeholder", ("round_trip_safe",), False)],
    "claims_active_profile_round_trip_safe": [
        ("placeholder", ("active_profile_round_trip_safe",), False)
    ],
    "claims_runtime_owned_behavior_represented_by_external_profile_json": [
        ("placeholder", ("runtime_owned_behavior_represented_in_external_profile",), False)
    ],
    "adapter_implemented": [("placeholder", ("adapter_implemented",), False)],
    "external_json_generated": [("placeholder", ("external_json_generated",), False)],
    "generated_external_json_output_path_present": [
        ("placeholder", ("external_json_generated",), False)
    ],
    "device_write_allowed": [("placeholder", ("device_write_allowed",), False)],
    "webserial_allowed": [("placeholder", ("webserial_allowed",), False)],
    "protobuf_binary_generation_allowed": [
        ("placeholder", ("protobuf_binary_generation_allowed",), False)
    ],
    "runtime_loaded_config_allowed": [
        ("placeholder", ("runtime_loaded_config_allowed",), False)
    ],
    "official_compatibility_claimed": [
        ("placeholder", ("official_compatibility_claimed",), False)
    ],
    "hardware_validation_claimed": [("corpus", ("hardware_status",), HARDWARE_STATUS)],
    "external_source_promoted_to_authority": [
        ("contract", ("source_authority", "external_source_promoted_to_authority"), False),
        ("corpus", ("source_authority", "external_source_promoted_to_authority"), False),
    ],
    "copied_external_source_code": [
        ("contract", ("source_authority", "no_external_code_reuse"), True),
        ("corpus", ("source_authority", "no_external_code_reuse"), True),
    ],
    "external_dependency_added": [
        ("contract", ("source_authority", "no_external_dependency"), True),
        ("corpus", ("source_authority", "no_external_dependency"), True),
    ],
    "missing_source_authority_classification": [
        ("contract", ("negative_corpus_rules", "source_authority_classification_required"), True)
    ],
    "missing_validation_report": [
        ("contract", ("negative_corpus_rules", "validation_report_required"), True)
    ],
    "missing_loss_warnings": [("placeholder", ("loss_warnings_required",), True)],
    "binding_loss_warning_suppressed": [
        ("contract", ("supporting_findings", "binding_loss_warning_required"), True)
    ],
    "socd_drift_warning_suppressed": [
        ("contract", ("supporting_findings", "socd_drift_warning_required"), True)
    ],
}


class CleanRoomAdapterInvalidCorpusError(ValueError):
    """Raised when the clean-room adapter invalid corpus drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterInvalidCorpusError(message)


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


def validate_checker_passes(checker_path: str) -> None:
    completed = subprocess.run(
        [sys.executable, checker_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        output = "\n".join(
            part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
        )
        fail(f"dependency checker failed: {checker_path}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"dependency checker did not report PASS: {checker_path}")


def get_nested(payload: dict[str, Any], path: tuple[str, ...], label: str) -> Any:
    current: Any = payload
    walked: list[str] = []
    for segment in path:
        walked.append(segment)
        if not isinstance(current, dict) or segment not in current:
            fail(f"{label} missing required path: {'.'.join(walked)}")
        current = current[segment]
    return current


def contract_category_entries(contract: dict[str, Any]) -> list[dict[str, str]]:
    categories = contract.get("invalid_case_categories")
    if not isinstance(categories, list) or not categories:
        fail("contract invalid_case_categories must be a non-empty list")

    entries: list[dict[str, str]] = []
    for index, entry in enumerate(categories):
        if not isinstance(entry, dict):
            fail(f"contract invalid_case_categories[{index}] must be an object")
        category = entry.get("category")
        required_rejection = entry.get("required_rejection")
        if not isinstance(category, str) or not category:
            fail(f"contract invalid_case_categories[{index}].category must be a non-empty string")
        if not isinstance(required_rejection, str) or not required_rejection:
            fail(
                "contract invalid_case_categories"
                f"[{index}].required_rejection must be a non-empty string"
            )
        entries.append(
            {
                "category": category,
                "required_rejection": required_rejection,
            }
        )
    return entries


def validate_contract(contract: dict[str, Any]) -> list[dict[str, str]]:
    if contract.get("schema_name") != "glyph_clean_room_adapter_negative_corpus_contract":
        fail("contract schema_name drifted")
    if contract.get("status") != "negative_corpus_contract_only":
        fail("contract status drifted")
    if contract.get("hardware_status") != HARDWARE_STATUS:
        fail(f"contract hardware_status must be {HARDWARE_STATUS!r}")
    return contract_category_entries(contract)


def validate_placeholder(placeholder: dict[str, Any]) -> None:
    expected_fields = {
        "schema_name": "glyph_clean_room_adapter_candidate_placeholder",
        "schema_version": 1,
        "status": "placeholder_only_no_adapter_output",
        "placeholder_only": True,
        "adapter_implemented": False,
        "active_profile_round_trip_safe": False,
        "device_write_allowed": False,
        "external_json_generated": False,
        "hardware_status": HARDWARE_STATUS,
        "loss_warnings_required": True,
        "official_compatibility_claimed": False,
        "protobuf_binary_generation_allowed": False,
        "round_trip_safe": False,
        "runtime_loaded_config_allowed": False,
        "runtime_owned_behavior_represented_in_external_profile": False,
        "runtime_owned_behavior_sidecar_required": True,
        "socd_policy_sidecar_required": True,
        "source_authority_promoted": False,
        "webserial_allowed": False,
    }
    for key, value in expected_fields.items():
        if placeholder.get(key) != value:
            fail(f"placeholder {key} must be {value!r}")

    for key in placeholder:
        lowered = key.lower()
        if lowered in FORBIDDEN_OUTPUT_PATH_KEYS or "path" in lowered:
            fail(f"placeholder must not contain output-path key: {key}")


def validate_corpus_top_level(corpus: dict[str, Any]) -> None:
    expected_fields = {
        "schema_name": SCHEMA_NAME,
        "corpus_version": 1,
        "status": STATUS,
        "adapter_implemented": False,
        "external_json_generated": False,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected_fields.items():
        if corpus.get(key) != value:
            fail(f"corpus {key} must be {value!r}")

    contract_source = corpus.get("contract_source")
    if not isinstance(contract_source, dict):
        fail("corpus contract_source must be an object")
    if contract_source.get("schema_name") != "glyph_clean_room_adapter_negative_corpus_contract":
        fail("corpus contract_source.schema_name drifted")
    if contract_source.get("status") != "negative_corpus_contract_only":
        fail("corpus contract_source.status drifted")

    source_authority = corpus.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("corpus source_authority must be an object")
    if source_authority.get("external_source_promoted_to_authority") is not False:
        fail("corpus must keep external_source_promoted_to_authority=false")
    if source_authority.get("no_external_code_reuse") is not True:
        fail("corpus must keep no_external_code_reuse=true")
    if source_authority.get("no_external_dependency") is not True:
        fail("corpus must keep no_external_dependency=true")

    validation_report = corpus.get("validation_report")
    if not isinstance(validation_report, dict):
        fail("corpus validation_report must be an object")
    if validation_report.get("no_mutation_application") is not True:
        fail("corpus validation_report.no_mutation_application must be true")
    if validation_report.get("no_adapter_candidate_generation") is not True:
        fail("corpus validation_report.no_adapter_candidate_generation must be true")
    if validation_report.get("validation_scope") != "docs_tools_fixtures_only":
        fail("corpus validation_report.validation_scope must be docs_tools_fixtures_only")


def walk_case_for_forbidden_paths(case_id: str, value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_OUTPUT_PATH_KEYS:
                fail(f"{case_id} must not contain generated external JSON output key: {key}")
            if "path" in key.lower():
                fail(f"{case_id} must not contain path-like key: {key}")
            walk_case_for_forbidden_paths(case_id, nested)
        return
    if isinstance(value, list):
        for nested in value:
            walk_case_for_forbidden_paths(case_id, nested)
        return
    if isinstance(value, str):
        lowered = value.lower()
        looks_like_repo_path = "docs/" in lowered or "tools/" in lowered or value.startswith("/")
        if looks_like_repo_path or value.endswith(".json"):
            fail(f"{case_id} must remain metadata-only and path-free")


def validate_case_invalidation(
    case: dict[str, Any],
    contract: dict[str, Any],
    corpus: dict[str, Any],
    placeholder: dict[str, Any],
) -> None:
    category = case["category"]
    rules = CASE_INVALIDATION_RULES.get(category)
    if rules is None:
        fail(f"{case['case_id']} category has no invalidation rule: {category}")

    sources = {
        "contract": contract,
        "corpus": corpus,
        "placeholder": placeholder,
    }
    for source_name, path, expected in rules:
        actual = get_nested(sources[source_name], path, f"{case['case_id']} {source_name}")
        if actual != expected:
            fail(
                f"{case['case_id']} invalidation source drifted at "
                f"{source_name}.{'.'.join(path)}: expected {expected!r}, got {actual!r}"
            )


def validate_cases(
    corpus: dict[str, Any],
    contract_entries: list[dict[str, str]],
    contract: dict[str, Any],
    placeholder: dict[str, Any],
) -> int:
    cases = corpus.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("corpus cases must be a non-empty list")

    expected_category_order = [entry["category"] for entry in contract_entries]
    expected_rejections = {
        entry["category"]: entry["required_rejection"] for entry in contract_entries
    }

    seen_categories: list[str] = []
    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"corpus cases[{index}] must be an object")
        case_id = case.get("case_id")
        category = case.get("category")
        expected_error_codes = case.get("expected_error_codes")

        if not isinstance(case_id, str) or not case_id:
            fail(f"corpus cases[{index}].case_id must be a non-empty string")
        if case_id in seen_case_ids:
            fail(f"duplicate case_id in corpus: {case_id}")
        seen_case_ids.add(case_id)

        if set(case) != ALLOWED_CASE_KEYS:
            unexpected = sorted(set(case) - ALLOWED_CASE_KEYS)
            missing = sorted(ALLOWED_CASE_KEYS - set(case))
            details: list[str] = []
            if unexpected:
                details.append("unexpected=" + ",".join(unexpected))
            if missing:
                details.append("missing=" + ",".join(missing))
            fail(f"{case_id} must remain metadata-only with fixed keys: {' '.join(details)}")

        if not isinstance(category, str) or not category:
            fail(f"{case_id}.category must be a non-empty string")
        if category not in expected_rejections:
            fail(f"{case_id} has unknown category: {category}")
        seen_categories.append(category)

        if expected_error_codes != CASE_EXPECTED_ERROR_CODES.get(category):
            fail(f"{case_id}.expected_error_codes drifted for category {category}")
        if case.get("required_rejection_basis") != expected_rejections[category]:
            fail(f"{case_id}.required_rejection_basis drifted for category {category}")
        if case.get("must_fail") is not True:
            fail(f"{case_id}.must_fail must be true")
        if case.get("must_not_generate_external_json") is not True:
            fail(f"{case_id}.must_not_generate_external_json must be true")
        if case.get("must_not_claim_official_compatibility") is not True:
            fail(f"{case_id}.must_not_claim_official_compatibility must be true")
        if case.get("must_not_claim_hardware_validation") is not True:
            fail(f"{case_id}.must_not_claim_hardware_validation must be true")
        if not isinstance(case.get("mutation_description"), str) or not case["mutation_description"]:
            fail(f"{case_id}.mutation_description must be a non-empty string")

        walk_case_for_forbidden_paths(case_id, case)
        validate_case_invalidation(case, contract, corpus, placeholder)

    if seen_categories != expected_category_order:
        fail("corpus case category order must match the negative corpus contract order")
    if set(seen_categories) != set(expected_category_order):
        fail("corpus must contain every required contract category exactly once")
    return len(cases)


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print(SCHEMA_NAME)
    try:
        for checker in DEPENDENCY_CHECKERS:
            validate_checker_passes(checker)
        contract = load_json_object(CONTRACT_FIXTURE_PATH)
        corpus = load_json_object(INVALID_CORPUS_FIXTURE_PATH)
        placeholder = load_json_object(PLACEHOLDER_FIXTURE_PATH)

        contract_entries = validate_contract(contract)
        validate_placeholder(placeholder)
        validate_corpus_top_level(corpus)
        invalid_cases = validate_cases(corpus, contract_entries, contract, placeholder)
        validate_doc()
    except (OSError, CleanRoomAdapterInvalidCorpusError, ValueError) as exc:
        print("status=FAIL")
        print("invalid_cases=0")
        print("adapter_implemented=false")
        print("external_json_generated=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"invalid_cases={invalid_cases}")
    print("adapter_implemented=false")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
