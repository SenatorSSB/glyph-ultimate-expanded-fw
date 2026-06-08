#!/usr/bin/env python3
"""Validate the official configurator export validation report."""

from __future__ import annotations

import json
import copy
import re
import subprocess
import sys
from pathlib import Path

from glyph_official_configurator_corpus import (
    BACK_AND_FORTH_FIXTURE_PATH,
    DEFAULT_FIXTURE_PATH,
    MANIFEST_PATH,
    CorpusError,
    display,
    load_json_object,
    sha256_file,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DOC = REPO_ROOT / "docs/export/official_configurator_export_validation_report.md"
REPORT_FIXTURE = REPO_ROOT / "docs/export/fixtures/official_configurator_export_validation_report.json"
MUTATION_CASES = REPO_ROOT / "docs/export/fixtures/official_configurator_export_mutation_cases.json"
CONTRACT_CHECKER = REPO_ROOT / "tools/check_glyph_official_configurator_export_target_contract.py"
CONTRACT_DOC = REPO_ROOT / "docs/export/official_configurator_export_target_contract.md"
PREVIEW_FIXTURE = REPO_ROOT / "docs/export/fixtures/official_configurator_export_candidate_preview.json"
INVALID_CORPUS = REPO_ROOT / "docs/export/fixtures/official_configurator_export_invalid_cases.json"
SOURCE_AUTHORITY_DOCS_USED = [
    "docs/export/official_configurator_export_source_authority.md",
    "docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md",
    "docs/calibration/glyph_official_configurator_corpus_diff_2026-06-06.md",
]
REQUIRED_PREVIEW_LABELS = [
    "offline_preview_only",
    "not_production_export",
    "not_device_write",
    "not_webserial",
    "not_runtime_loaded_config",
    "not_official_compatibility_claim",
]

REQUIRED_MUTATION_CASE_IDS = {
    "missing_manifest_path",
    "wrong_manifest_hash",
    "wrong_default_fixture_hash",
    "wrong_back_and_forth_fixture_hash",
    "missing_preview_labels",
    "unknown_field_claimed_source_backed",
    "external_remapper_evidence_promoted_as_official",
    "official_compatibility_claim",
    "universal_compatibility_claim",
    "production_export_claim",
    "device_write_flag",
    "webserial_flag",
    "runtime_loaded_config_claim",
    "firmware_flashing_automation_claim",
    "nunchuk_validation_claim",
}


def fail(message: str) -> None:
    raise CorpusError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def validate_doc() -> None:
    text = REPORT_DOC.read_text(encoding="utf-8")
    for phrase in (
        "OFFLINE_VALIDATION_REPORT_ONLY",
        "not production export output",
        "not official configurator compatibility",
        "not device write",
        "not WebSerial",
        "not runtime-loaded config",
        "not firmware flashing automation",
        "not nunchuk validation",
        "preview fixture checked: yes",
        "invalid corpus checked: yes",
        "mutation cases checked: yes",
        "contract checker reused: yes",
    ):
        if phrase.lower() not in text.lower():
            fail(f"{display(REPORT_DOC)} missing required phrase: {phrase}")
    validate_no_positive_claims(text)


def validate_no_positive_claims(text: str) -> None:
    lowered = normalize(text)
    for marker in (
        "production export output is compatible",
        "production export output is implemented",
        "official configurator compatibility is claimed",
        "universal compatibility is claimed",
        "device write is implemented",
        "webserial is implemented",
        "runtime-loaded config is implemented",
        "firmware flashing automation is implemented",
        "nunchuk validation is claimed",
    ):
        if marker in lowered:
            fail(f"{display(REPORT_DOC)} contains forbidden positive claim: {marker}")


def validate_fixture_payload(payload: dict[str, object]) -> None:
    if payload.get("status") != "OFFLINE_VALIDATION_REPORT_ONLY":
        fail("validation report fixture status must be OFFLINE_VALIDATION_REPORT_ONLY")
    if payload.get("source_authority_docs_used") != SOURCE_AUTHORITY_DOCS_USED:
        fail("validation report source_authority_docs_used drifted")
    if payload.get("contract_doc_used") != display(CONTRACT_DOC):
        fail("validation report contract_doc_used must match the target contract")
    if payload.get("preview_fixture_checked") != display(PREVIEW_FIXTURE):
        fail("validation report preview_fixture_checked must match the preview fixture")
    if payload.get("required_preview_labels_checked") != REQUIRED_PREVIEW_LABELS:
        fail("validation report required_preview_labels_checked must preserve offline labels")
    if payload.get("invalid_corpus_checked") != display(INVALID_CORPUS):
        fail("validation report invalid_corpus_checked must match the invalid corpus")
    if payload.get("mutation_cases_checked") != display(MUTATION_CASES):
        fail("validation report mutation_cases_checked must match the mutation cases fixture")
    if payload.get("contract_checker_reused") != display(CONTRACT_CHECKER):
        fail("validation report contract_checker_reused must point to the contract checker")
    if payload.get("unknown_field_policy") != "unknown_fields_must_remain_unknown_or_unsupported":
        fail("validation report unknown field policy must fail closed")
    if payload.get("external_remapper_evidence") != "quarantined_not_primary_authority":
        fail("validation report external-remapper evidence must remain quarantined")
    manifest = payload.get("manifest")
    if not isinstance(manifest, dict):
        fail("validation report manifest entry must be an object")
    if manifest.get("path") != display(MANIFEST_PATH):
        fail("validation report manifest path must match the official manifest")
    if manifest.get("sha256") != sha256_file(MANIFEST_PATH):
        fail("validation report manifest hash must match the committed manifest")
    hashes = payload.get("fixture_hashes")
    if not isinstance(hashes, dict):
        fail("validation report fixture_hashes must be an object")
    expected_hashes = {
        display(DEFAULT_FIXTURE_PATH): sha256_file(DEFAULT_FIXTURE_PATH),
        display(BACK_AND_FORTH_FIXTURE_PATH): sha256_file(BACK_AND_FORTH_FIXTURE_PATH),
    }
    if hashes != expected_hashes:
        fail("validation report fixture hashes must match committed official fixtures")
    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("validation report non_claims must be an object")
    for key in (
        "no_production_export",
        "no_official_compatibility_claim",
        "no_device_write",
        "no_webserial",
        "no_runtime_loaded_config",
        "no_firmware_flashing_automation",
        "no_nunchuk_validation",
        "external_remapper_evidence_quarantined",
    ):
        if non_claims.get(key) is not True:
            fail(f"validation report non-claim {key} must be true")


def validate_fixture() -> None:
    validate_fixture_payload(load_json_object(REPORT_FIXTURE))


def validate_mutation_cases_payload(payload: dict[str, object]) -> None:
    if payload.get("status") != "OFFLINE_MUTATION_CASES_ONLY":
        fail("mutation cases must remain offline-only")
    if payload.get("validator_tool") != display(CONTRACT_CHECKER).replace(
        "check_glyph_official_configurator_export_target_contract.py",
        "check_glyph_official_configurator_export_validation_report.py",
    ):
        fail("mutation cases validator_tool must point to the validation report checker")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        fail("mutation cases must be a list")
    found = set()
    for case in cases:
        if not isinstance(case, dict):
            fail("mutation case entries must be objects")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            fail("mutation case_id must be a non-empty string")
        if not isinstance(case.get("expected_rejection"), str) or not case["expected_rejection"]:
            fail(f"{case_id} must include expected_rejection")
        found.add(case_id)
    missing = sorted(REQUIRED_MUTATION_CASE_IDS - found)
    if missing:
        fail("mutation cases missing required case_id(s): " + ", ".join(missing))


def validate_mutation_cases() -> None:
    payload = load_json_object(MUTATION_CASES)
    validate_mutation_cases_payload(payload)
    exercise_mutation_cases(payload)


def expect_rejected(case_id: str, payload: dict[str, object]) -> None:
    try:
        validate_fixture_payload(payload)
    except CorpusError:
        return
    fail(f"mutation case did not fail closed: {case_id}")


def exercise_mutation_cases(mutation_payload: dict[str, object]) -> None:
    report = load_json_object(REPORT_FIXTURE)
    cases = {case.get("case_id") for case in mutation_payload.get("cases", []) if isinstance(case, dict)}
    mutations = {
        "missing_manifest_path": lambda data: data["manifest"].pop("path", None),
        "wrong_manifest_hash": lambda data: data["manifest"].update({"sha256": "0" * 64}),
        "wrong_default_fixture_hash": lambda data: data["fixture_hashes"].update(
            {display(DEFAULT_FIXTURE_PATH): "0" * 64}
        ),
        "wrong_back_and_forth_fixture_hash": lambda data: data["fixture_hashes"].update(
            {display(BACK_AND_FORTH_FIXTURE_PATH): "0" * 64}
        ),
        "missing_preview_labels": lambda data: data.pop("required_preview_labels_checked", None),
        "unknown_field_claimed_source_backed": lambda data: data.update(
            {"unknown_field_policy": "unknown_fields_claimed_source_backed"}
        ),
        "external_remapper_evidence_promoted_as_official": lambda data: data.update(
            {"external_remapper_evidence": "promoted_as_official"}
        ),
        "official_compatibility_claim": lambda data: data["non_claims"].update(
            {"no_official_compatibility_claim": False}
        ),
        "universal_compatibility_claim": lambda data: data.update(
            {"external_remapper_evidence": "universal_compatibility_claim"}
        ),
        "production_export_claim": lambda data: data["non_claims"].update({"no_production_export": False}),
        "device_write_flag": lambda data: data["non_claims"].update({"no_device_write": False}),
        "webserial_flag": lambda data: data["non_claims"].update({"no_webserial": False}),
        "runtime_loaded_config_claim": lambda data: data["non_claims"].update(
            {"no_runtime_loaded_config": False}
        ),
        "firmware_flashing_automation_claim": lambda data: data["non_claims"].update(
            {"no_firmware_flashing_automation": False}
        ),
        "nunchuk_validation_claim": lambda data: data["non_claims"].update({"no_nunchuk_validation": False}),
    }
    if set(mutations) != cases:
        fail("mutation exercise table must match mutation case IDs exactly")
    for case_id, mutate in mutations.items():
        mutated = copy.deepcopy(report)
        mutate(mutated)
        expect_rejected(case_id, mutated)


def run_contract_checker() -> None:
    completed = subprocess.run(
        [sys.executable, str(CONTRACT_CHECKER.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("contract checker failed while validating report: " + completed.stdout + completed.stderr)


def main() -> int:
    print("glyph_official_configurator_export_validation_report")
    try:
        validate_doc()
        validate_fixture()
        validate_mutation_cases()
        run_contract_checker()
    except (CorpusError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print("offline_validation_report_only=true")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("offline_validation_report_only=true")
    print("production_export=false")
    print("official_configurator_compatibility_claim=false")
    print("device_write=false")
    print("webserial=false")
    print("runtime_loaded_config=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
