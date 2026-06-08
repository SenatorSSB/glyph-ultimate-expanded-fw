#!/usr/bin/env python3
"""Validate the official configurator export validation report."""

from __future__ import annotations

import json
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


def validate_fixture() -> None:
    payload = load_json_object(REPORT_FIXTURE)
    if payload.get("status") != "OFFLINE_VALIDATION_REPORT_ONLY":
        fail("validation report fixture status must be OFFLINE_VALIDATION_REPORT_ONLY")
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


def validate_mutation_cases() -> None:
    payload = load_json_object(MUTATION_CASES)
    if payload.get("status") != "OFFLINE_MUTATION_CASES_ONLY":
        fail("mutation cases must remain offline-only")
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
