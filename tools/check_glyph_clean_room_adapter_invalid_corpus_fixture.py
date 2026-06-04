#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter invalid corpus fixture."""

from __future__ import annotations

import argparse
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
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_invalid_corpus_2026-06-04.json"
)
CONTRACT_CHECKER = "tools/check_glyph_clean_room_adapter_negative_corpus_contract.py"
CONTRACT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json"
)

SCHEMA_NAME = "glyph_clean_room_adapter_invalid_corpus"
CORPUS_VERSION = 1
STATUS = "docs_tools_invalid_corpus"
HARDWARE_STATUS = "not_new_hardware_result"

CASE_METADATA = {
    "missing_sidecar": {
        "case_id": "reject_missing_sidecar",
        "expected_error_codes": ["clean_room_candidate.sidecar.required"],
        "mutation_description": "Remove the required sidecar content from a future clean-room adapter candidate payload.",
    },
    "missing_runtime_owned_behavior_warning": {
        "case_id": "reject_missing_runtime_owned_behavior_warning",
        "expected_error_codes": ["clean_room_candidate.runtime_owned_behavior_warning.required"],
        "mutation_description": "Omit the required runtime-owned behavior warning from a future candidate sidecar/report.",
    },
    "missing_non_round_trip_warning": {
        "case_id": "reject_missing_non_round_trip_warning",
        "expected_error_codes": ["clean_room_candidate.non_round_trip_warning.required"],
        "mutation_description": "Omit the required non-round-trip warning from a future candidate sidecar/report.",
    },
    "claims_round_trip_safe": {
        "case_id": "reject_claimed_round_trip_safe",
        "expected_error_codes": ["clean_room_candidate.round_trip_safe.false_required"],
        "mutation_description": "Set a future candidate payload to claim round-trip safety even though the contract keeps it unsafe by default.",
    },
    "claims_active_profile_round_trip_safe": {
        "case_id": "reject_claimed_active_profile_round_trip_safe",
        "expected_error_codes": ["clean_room_candidate.active_profile_round_trip_safe.false_required"],
        "mutation_description": "Set a future candidate payload to claim the active profile artifact is round-trip safe.",
    },
    "claims_runtime_owned_behavior_represented_by_external_profile_json": {
        "case_id": "reject_runtime_owned_behavior_claimed_in_external_profile_json",
        "expected_error_codes": [
            "clean_room_candidate.runtime_owned_behavior_external_profile_json.false_required"
        ],
        "mutation_description": "Claim that runtime-owned behavior is represented directly by external profile JSON instead of sidecar-only warnings.",
    },
    "adapter_implemented": {
        "case_id": "reject_adapter_implemented_true",
        "expected_error_codes": ["clean_room_candidate.adapter_implemented.false_required"],
        "mutation_description": "Flip a future candidate payload to claim adapter implementation exists.",
    },
    "external_json_generated": {
        "case_id": "reject_external_json_generated_true",
        "expected_error_codes": ["clean_room_candidate.external_json_generated.false_required"],
        "mutation_description": "Flip a future candidate payload to claim external JSON generation exists.",
    },
    "generated_external_json_output_path_present": {
        "case_id": "reject_generated_external_json_output_path_present",
        "expected_error_codes": ["clean_room_candidate.external_json_output_path.forbidden"],
        "mutation_description": "Add a generated external JSON output path reference to a future candidate payload or validation report.",
    },
    "device_write_allowed": {
        "case_id": "reject_device_write_allowed_true",
        "expected_error_codes": ["clean_room_candidate.device_write_allowed.false_required"],
        "mutation_description": "Claim that device write behavior is allowed for the future candidate payload.",
    },
    "webserial_allowed": {
        "case_id": "reject_webserial_allowed_true",
        "expected_error_codes": ["clean_room_candidate.webserial_allowed.false_required"],
        "mutation_description": "Claim that WebSerial transport is allowed for the future candidate payload.",
    },
    "protobuf_binary_generation_allowed": {
        "case_id": "reject_protobuf_binary_generation_allowed_true",
        "expected_error_codes": ["clean_room_candidate.protobuf_binary_generation_allowed.false_required"],
        "mutation_description": "Claim that protobuf binary generation is allowed for the future candidate payload.",
    },
    "runtime_loaded_config_allowed": {
        "case_id": "reject_runtime_loaded_config_allowed_true",
        "expected_error_codes": ["clean_room_candidate.runtime_loaded_config_allowed.false_required"],
        "mutation_description": "Claim that runtime-loaded config is allowed for the future candidate payload.",
    },
    "official_compatibility_claimed": {
        "case_id": "reject_official_compatibility_claimed_true",
        "expected_error_codes": ["clean_room_candidate.official_compatibility_claimed.false_required"],
        "mutation_description": "Claim official configurator compatibility for the future candidate payload.",
    },
    "hardware_validation_claimed": {
        "case_id": "reject_hardware_validation_claimed_true",
        "expected_error_codes": ["clean_room_candidate.hardware_validation_claimed.false_required"],
        "mutation_description": "Claim hardware validation for the future candidate payload.",
    },
    "external_source_promoted_to_authority": {
        "case_id": "reject_external_source_promoted_to_authority_true",
        "expected_error_codes": ["clean_room_candidate.external_source_promoted_to_authority.false_required"],
        "mutation_description": "Promote external remapper output or external notes to source authority for the future candidate payload.",
    },
    "copied_external_source_code": {
        "case_id": "reject_copied_external_source_code_true",
        "expected_error_codes": ["clean_room_candidate.external_code_reuse.forbidden"],
        "mutation_description": "Claim copied external source code as part of the future candidate payload or validator context.",
    },
    "external_dependency_added": {
        "case_id": "reject_external_dependency_added_true",
        "expected_error_codes": ["clean_room_candidate.external_dependency_added.forbidden"],
        "mutation_description": "Claim that an external dependency was added for the future candidate payload or validator context.",
    },
    "missing_source_authority_classification": {
        "case_id": "reject_missing_source_authority_classification",
        "expected_error_codes": ["clean_room_candidate.source_authority_classification.required"],
        "mutation_description": "Remove the required source-authority classification from a future candidate payload or report.",
    },
    "missing_validation_report": {
        "case_id": "reject_missing_validation_report",
        "expected_error_codes": ["clean_room_candidate.validation_report.required"],
        "mutation_description": "Remove the required validation report from a future candidate payload.",
    },
    "missing_loss_warnings": {
        "case_id": "reject_missing_loss_warnings",
        "expected_error_codes": ["clean_room_candidate.loss_warnings.required"],
        "mutation_description": "Remove the required loss warnings from a future candidate payload or report.",
    },
    "binding_loss_warning_suppressed": {
        "case_id": "reject_binding_loss_warning_suppressed",
        "expected_error_codes": ["clean_room_candidate.binding_loss_warning.required"],
        "mutation_description": "Suppress the binding-loss warning that the sidecar contract requires for future candidates.",
    },
    "socd_drift_warning_suppressed": {
        "case_id": "reject_socd_drift_warning_suppressed",
        "expected_error_codes": ["clean_room_candidate.socd_drift_warning.required"],
        "mutation_description": "Suppress the SOCD-drift warning that the sidecar contract requires for future candidates.",
    },
}

REQUIRED_DOC_PHRASES = (
    "docs_tools_invalid_corpus",
    "schema_name = glyph_clean_room_adapter_invalid_corpus",
    "corpus_version = 1",
    "planning fixture validation only",
    "no mutation application",
    "no adapter candidate generation",
    "covers every category from the clean-room adapter negative corpus contract",
    "must_fail = true",
    "must_not_generate_external_json = true",
    "must_not_claim_official_compatibility = true",
    "must_not_claim_hardware_validation = true",
    "adapter_implemented = false",
    "external_json_generated = false",
    "hardware_status = not_new_hardware_result",
    "not official compatibility",
    "not hardware validation",
    "missing_sidecar",
    "missing_runtime_owned_behavior_warning",
    "missing_non_round_trip_warning",
    "claims_round_trip_safe",
    "claims_active_profile_round_trip_safe",
    "claims_runtime_owned_behavior_represented_by_external_profile_json",
    "adapter_implemented",
    "external_json_generated",
    "generated_external_json_output_path_present",
    "device_write_allowed",
    "webserial_allowed",
    "protobuf_binary_generation_allowed",
    "runtime_loaded_config_allowed",
    "official_compatibility_claimed",
    "hardware_validation_claimed",
    "external_source_promoted_to_authority",
    "copied_external_source_code",
    "external_dependency_added",
    "missing_source_authority_classification",
    "missing_validation_report",
    "missing_loss_warnings",
    "binding_loss_warning_suppressed",
    "socd_drift_warning_suppressed",
)

FORBIDDEN_OUTPUT_PATH_KEYS = {
    "external_json_output_path",
    "generated_external_json_path",
    "output_path_to_generated_external_json",
}


class CleanRoomAdapterInvalidCorpusFixtureError(ValueError):
    """Raised when the clean-room adapter invalid corpus fixture drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterInvalidCorpusFixtureError(message)


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


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def validate_contract_checker() -> dict[str, Any]:
    checker_path = REPO_ROOT / CONTRACT_CHECKER
    if not checker_path.exists():
        fail(f"missing contract checker: {CONTRACT_CHECKER}")

    completed = subprocess.run(
        [sys.executable, CONTRACT_CHECKER],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        output = "\n".join(
            part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
        )
        fail(f"contract checker failed: {CONTRACT_CHECKER}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"contract checker did not report PASS: {CONTRACT_CHECKER}")

    contract = load_json_object(CONTRACT_FIXTURE_PATH)
    if contract.get("schema_name") != "glyph_clean_room_adapter_negative_corpus_contract":
        fail("contract fixture schema_name drifted")
    if contract.get("status") != "negative_corpus_contract_only":
        fail("contract fixture status drifted")
    if contract.get("hardware_status") != HARDWARE_STATUS:
        fail(f"contract fixture hardware_status must be {HARDWARE_STATUS!r}")
    return contract


def contract_categories(contract: dict[str, Any]) -> list[dict[str, str]]:
    raw_categories = contract.get("invalid_case_categories")
    if not isinstance(raw_categories, list) or not raw_categories:
        fail("contract invalid_case_categories must be a non-empty list")

    categories: list[dict[str, str]] = []
    for index, entry in enumerate(raw_categories):
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
        categories.append(
            {
                "category": category,
                "required_rejection": required_rejection,
            }
        )
    return categories


def build_fixture(contract: dict[str, Any]) -> dict[str, Any]:
    categories = contract_categories(contract)
    cases: list[dict[str, Any]] = []
    for entry in categories:
        category = entry["category"]
        metadata = CASE_METADATA.get(category)
        if metadata is None:
            fail(f"missing invalid-corpus case metadata for contract category: {category}")
        cases.append(
            {
                "case_id": metadata["case_id"],
                "category": category,
                "expected_error_codes": metadata["expected_error_codes"],
                "must_fail": True,
                "must_not_claim_hardware_validation": True,
                "must_not_claim_official_compatibility": True,
                "must_not_generate_external_json": True,
                "mutation_description": metadata["mutation_description"],
                "required_rejection_basis": entry["required_rejection"],
            }
        )

    return {
        "adapter_implemented": False,
        "cases": cases,
        "contract_source": {
            "checker_path": CONTRACT_CHECKER,
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json",
            "invalid_category_count": len(categories),
            "schema_name": contract["schema_name"],
            "status": contract["status"],
        },
        "corpus_version": CORPUS_VERSION,
        "external_json_generated": False,
        "hardware_status": HARDWARE_STATUS,
        "schema_name": SCHEMA_NAME,
        "source_authority": {
            "external_source_promoted_to_authority": False,
            "no_external_code_reuse": True,
            "no_external_dependency": True,
            "source_basis": "repo docs, fixtures, and checker outputs only",
        },
        "status": STATUS,
        "validation_report": {
            "checker_path": "tools/check_glyph_clean_room_adapter_invalid_corpus_fixture.py",
            "contract_categories_covered": True,
            "contract_checker_required_to_pass": True,
            "doc_path": "docs/calibration/glyph_clean_room_adapter_invalid_corpus_2026-06-04.md",
            "fixture_path": "docs/calibration/fixtures/glyph_clean_room_adapter_invalid_corpus_2026-06-04.json",
            "hardware_status": HARDWARE_STATUS,
            "invalid_case_count": len(cases),
            "no_adapter_candidate_generation": True,
            "no_mutation_application": True,
            "validation_scope": "docs_tools_fixtures_only",
        },
    }


def validate_fixture(payload: dict[str, Any], contract: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(payload)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated canonical JSON")

    committed = load_json_object(FIXTURE_PATH)
    if committed != payload:
        fail("committed fixture JSON object drifted from regenerated invalid corpus")

    if committed.get("schema_name") != SCHEMA_NAME:
        fail(f"fixture schema_name must be {SCHEMA_NAME!r}")
    if committed.get("corpus_version") != CORPUS_VERSION:
        fail(f"fixture corpus_version must be {CORPUS_VERSION!r}")
    if committed.get("status") != STATUS:
        fail(f"fixture status must be {STATUS!r}")
    if committed.get("hardware_status") != HARDWARE_STATUS:
        fail(f"fixture hardware_status must be {HARDWARE_STATUS!r}")
    if committed.get("adapter_implemented") is not False:
        fail("fixture must keep adapter_implemented=false")
    if committed.get("external_json_generated") is not False:
        fail("fixture must keep external_json_generated=false")

    cases = committed.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("fixture cases must be a non-empty list")

    seen_case_ids: set[str] = set()
    seen_categories: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"fixture cases[{index}] must be an object")
        case_id = case.get("case_id")
        category = case.get("category")
        expected_error_codes = case.get("expected_error_codes")
        required_rejection_basis = case.get("required_rejection_basis")

        if not isinstance(case_id, str) or not case_id:
            fail(f"fixture cases[{index}].case_id must be a non-empty string")
        if case_id in seen_case_ids:
            fail(f"duplicate case_id in fixture: {case_id}")
        seen_case_ids.add(case_id)

        if not isinstance(category, str) or not category:
            fail(f"fixture cases[{index}].category must be a non-empty string")
        if category in seen_categories:
            fail(f"duplicate category in fixture: {category}")
        seen_categories.add(category)

        if not isinstance(expected_error_codes, list) or not expected_error_codes:
            fail(f"{case_id}.expected_error_codes must be a non-empty list")
        if not all(isinstance(code, str) and code for code in expected_error_codes):
            fail(f"{case_id}.expected_error_codes must contain non-empty strings")
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
        if not isinstance(required_rejection_basis, str) or not required_rejection_basis:
            fail(f"{case_id}.required_rejection_basis must be a non-empty string")

    contract_category_entries = contract_categories(contract)
    contract_category_names = [entry["category"] for entry in contract_category_entries]
    if [case["category"] for case in cases] != contract_category_names:
        fail("fixture case category order must match the committed negative corpus contract")

    contract_categories_set = set(contract_category_names)
    if seen_categories != contract_categories_set:
        missing = sorted(contract_categories_set - seen_categories)
        extras = sorted(seen_categories - contract_categories_set)
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extras:
            details.append("unexpected=" + ",".join(extras))
        fail("fixture categories must exactly cover the negative corpus contract: " + " ".join(details))

    contract_rejection_map = {
        entry["category"]: entry["required_rejection"] for entry in contract_category_entries
    }
    for case in cases:
        category = case["category"]
        if case["required_rejection_basis"] != contract_rejection_map[category]:
            fail(f"{case['case_id']} required_rejection_basis drifted from contract for {category}")

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in FORBIDDEN_OUTPUT_PATH_KEYS:
                    fail(f"fixture must not contain generated external JSON output key: {key}")
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(committed)


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the docs/tools-only Glyph clean-room adapter invalid corpus fixture."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of the concise validation summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = validate_contract_checker()
        payload = build_fixture(contract)
        if args.json:
            print(canonical_json_text(payload), end="")
            return 0
        validate_fixture(payload, contract)
        validate_doc()
    except (OSError, CleanRoomAdapterInvalidCorpusFixtureError, ValueError) as exc:
        print("glyph_clean_room_adapter_invalid_corpus_fixture")
        print("status=FAIL")
        print("invalid_cases=0")
        print("external_json_generated=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("glyph_clean_room_adapter_invalid_corpus_fixture")
    print("status=PASS")
    print(f"invalid_cases={len(payload['cases'])}")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
