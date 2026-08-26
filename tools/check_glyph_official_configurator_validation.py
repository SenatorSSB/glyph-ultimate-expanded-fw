#!/usr/bin/env python3
"""Validate retired official-configurator historical evidence integrity.

The official app is not a current product dependency or progression gate. The
preserved corpus/export checks remain runnable only as historical integrity
checks; no operator capture is required.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION_FIXTURE = REPO_ROOT / "docs/export/fixtures/official_configurator_validation_lane.json"
HISTORICAL_INTEGRITY_CHECKS = (
    "tools/check_glyph_official_configurator_export_corpus.py",
    "tools/check_glyph_official_configurator_corpus_diff.py",
    "tools/check_glyph_official_configurator_export_target_contract.py",
    "tools/check_glyph_official_configurator_export_candidate_diff.py",
    "tools/check_glyph_official_configurator_export_validation_report.py",
)
HISTORICAL_CHECK = "tools/check_glyph_import_export_compatibility.py"


class ValidationLaneError(ValueError):
    """Raised when current-lane evidence or classification is unsafe."""


def fail(message: str) -> None:
    raise ValidationLaneError(message)


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        fail("classification fixture must be an object")
    if set(payload) != {
        "status", "current_evidence_class", "current_checks",
        "historical_integrity_checks", "historical_checker",
        "historical_checker_status", "official_configurator_product_dependency",
        "operator_capture_required", "reopen_requires_explicit_user_decision",
        "evidence_classes", "blocked_claims",
    }:
        fail("retired classification fixture fields must remain exact")
    if payload.get("status") != "RETIRED_HISTORICAL_EVIDENCE_ONLY":
        fail("classification status must remain retired historical evidence only")
    if payload.get("current_evidence_class") is not None or payload.get("current_checks") != []:
        fail("retired lane cannot retain a current evidence class or current checks")
    if payload.get("historical_integrity_checks") != list(HISTORICAL_INTEGRITY_CHECKS):
        fail("historical integrity checks must preserve the bounded five-check corpus")
    if payload.get("historical_checker") != HISTORICAL_CHECK:
        fail("historical checker must remain explicitly excluded")
    if payload.get("historical_checker_status") != "HISTORICAL_ONLY_NOT_CURRENT_LANE":
        fail("historical checker status must remain excluded")
    if payload.get("official_configurator_product_dependency") is not False:
        fail("official configurator must not be a current product dependency")
    if payload.get("operator_capture_required") is not False:
        fail("retired lane must not require an operator capture")
    if payload.get("reopen_requires_explicit_user_decision") is not True:
        fail("retired lane must require explicit user direction to reopen")
    entries = payload.get("evidence_classes")
    if not isinstance(entries, list):
        fail("evidence_classes must be a list")
    required = {
        "primary_official_configurator_corpus": "historical_only",
        "historical_generated_prototype": "historical_only",
        "external_remapper": "quarantined",
    }
    observed = {entry.get("id"): entry.get("classification") for entry in entries if isinstance(entry, dict)}
    if observed != required:
        fail("evidence class mapping must remain exact and fail closed")
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("classification"), str):
            fail("evidence class entries must contain string id and classification")
        if entry.get("eligible_for_current_lane") is not False:
            fail(f"retired evidence is eligible for a current lane: {entry.get('id')}")
    claims = payload.get("blocked_claims")
    if not isinstance(claims, list) or claims != [
        "official_configurator_compatibility",
        "universal_compatibility",
        "production_export",
        "device_write",
        "runtime_loaded_config",
        "firmware_flashing",
    ]:
        fail("blocked claims must preserve the current non-claim boundary")
    return payload


def load_fixture() -> dict[str, Any]:
    try:
        payload = json.loads(CLASSIFICATION_FIXTURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid classification fixture: {exc}")
    return validate_payload(payload)


def exercise_classification_mutations(payload: dict[str, Any]) -> None:
    mutated = json.loads(json.dumps(payload))
    for entry in mutated["evidence_classes"]:
        if entry["id"] == "external_remapper":
            entry["classification"] = "current"
            break
    try:
        original = payload["evidence_classes"]
        payload["evidence_classes"] = mutated["evidence_classes"]
        validate_payload(payload)
    except ValidationLaneError:
        return
    finally:
        payload["evidence_classes"] = original
    fail("external-remapper promotion mutation was not rejected")


def exercise_dependency_mutations(payload: dict[str, Any]) -> None:
    for field, value in (
        ("official_configurator_product_dependency", True),
        ("operator_capture_required", True),
        ("reopen_requires_explicit_user_decision", False),
    ):
        original = payload[field]
        payload[field] = value
        try:
            validate_payload(payload)
        except ValidationLaneError:
            pass
        else:
            fail(f"retired dependency mutation was accepted: {field}")
        finally:
            payload[field] = original


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_fixture()
        exercise_classification_mutations(payload)
        exercise_dependency_mutations(payload)
        results = [
            {"path": path, "status": "PRESERVED_NOT_EXECUTED_BY_RETIRED_AGGREGATE"}
            for path in HISTORICAL_INTEGRITY_CHECKS
        ]
        if any(not (REPO_ROOT / result["path"]).is_file() for result in results):
            raise ValidationLaneError("one or more preserved historical integrity checks is missing")
    except (ValidationLaneError, OSError) as exc:
        print("glyph_official_configurator_validation")
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    report = {
        "status": "PASS",
        "current_lane": None,
        "current_check_count": 0,
        "classification": "RETIRED_HISTORICAL_EVIDENCE_ONLY",
        "historical_integrity_check_count": len(results),
        "historical_checker": HISTORICAL_CHECK,
        "historical_checker_status": "HISTORICAL_ONLY_NOT_CURRENT_LANE",
        "external_remapper_evidence": "QUARANTINED",
        "official_compatibility_claim": False,
        "results": results,
    }
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print("glyph_official_configurator_validation")
        print("status=PASS")
        print("current_lane=none")
        print("current_check_count=0")
        print("classification=RETIRED_HISTORICAL_EVIDENCE_ONLY")
        print("historical_integrity_check_count=5")
        print("operator_capture_required=false")
        print("historical_checker_status=HISTORICAL_ONLY_NOT_CURRENT_LANE")
        print("external_remapper_evidence=QUARANTINED")
        print("official_configurator_compatibility_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
