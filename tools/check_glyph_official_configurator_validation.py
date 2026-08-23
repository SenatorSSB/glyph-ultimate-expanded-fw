#!/usr/bin/env python3
"""Run the current offline official-configurator validation lane.

This entrypoint deliberately excludes historical compatibility chains.  It
aggregates only the five current corpus/export checks whose evidence is backed
by the committed official configurator corpus.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION_FIXTURE = REPO_ROOT / "docs/export/fixtures/official_configurator_validation_lane.json"
CURRENT_CHECKS = (
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
    if payload.get("status") != "OFFLINE_CURRENT_LANE_CLASSIFICATION_ONLY":
        fail("classification status must remain offline current-lane-only")
    if payload.get("current_evidence_class") != "primary_official_configurator_corpus":
        fail("current evidence class must remain primary_official_configurator_corpus")
    if payload.get("historical_checker") != HISTORICAL_CHECK:
        fail("historical checker must remain explicitly excluded")
    if payload.get("historical_checker_status") != "HISTORICAL_ONLY_NOT_CURRENT_LANE":
        fail("historical checker status must remain excluded")
    current = payload.get("current_checks")
    if current != list(CURRENT_CHECKS):
        fail("current checks must match the bounded five-check lane")
    entries = payload.get("evidence_classes")
    if not isinstance(entries, list):
        fail("evidence_classes must be a list")
    required = {
        "primary_official_configurator_corpus": "current",
        "historical_generated_prototype": "historical_only",
        "external_remapper": "quarantined",
    }
    observed = {entry.get("id"): entry.get("classification") for entry in entries if isinstance(entry, dict)}
    if observed != required:
        fail("evidence class mapping must remain exact and fail closed")
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("classification"), str):
            fail("evidence class entries must contain string id and classification")
        if entry["classification"] != "current" and entry.get("eligible_for_current_lane") is not False:
            fail(f"non-current evidence is eligible for current lane: {entry.get('id')}")
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


def run_checker(path: str) -> tuple[str, int, str]:
    completed = subprocess.run(
        [sys.executable, path], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return path, completed.returncode, output


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_fixture()
        exercise_classification_mutations(payload)
        results = []
        for path in CURRENT_CHECKS:
            checked_path, exit_code, output = run_checker(path)
            results.append({"path": checked_path, "status": "PASS" if exit_code == 0 else "FAIL", "exit_code": exit_code, "last_output": output.splitlines()[-1:]})
        if any(result["status"] != "PASS" for result in results):
            raise ValidationLaneError("one or more current official-configurator checks failed")
    except (ValidationLaneError, OSError) as exc:
        print("glyph_official_configurator_validation")
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    report = {
        "status": "PASS",
        "current_lane": "offline_primary_official_configurator_corpus",
        "current_check_count": len(results),
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
        print("current_lane=offline_primary_official_configurator_corpus")
        print("current_check_count=5")
        print("historical_checker_status=HISTORICAL_ONLY_NOT_CURRENT_LANE")
        print("external_remapper_evidence=QUARANTINED")
        print("official_configurator_compatibility_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
