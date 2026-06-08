#!/usr/bin/env python3
"""Validate the manual official configurator import/export test plan."""

from __future__ import annotations

import json
from pathlib import Path

from glyph_official_configurator_corpus import CorpusError, display, load_json_object


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_DOC = REPO_ROOT / "docs/export/official_configurator_manual_import_export_test_plan.md"
PLAN_FIXTURE = REPO_ROOT / "docs/export/fixtures/official_configurator_manual_import_export_test_plan.json"
TEMPLATE_DOC = REPO_ROOT / "docs/export/official_configurator_manual_import_export_result_TEMPLATE.md"
PLACEHOLDER = "UNKNOWN_TO_BE_FILLED_BY_OPERATOR"


def fail(message: str) -> None:
    raise CorpusError(message)


def validate_doc() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    for phrase in (
        "MANUAL_TEST_PLAN_ONLY_NOT_A_RESULT",
        "does not record a result",
        "UNKNOWN_TO_BE_FILLED_BY_OPERATOR",
        "no device write",
        "no WebSerial",
        "no runtime-loaded config",
        "no firmware flashing automation",
        "no hardware behavior validation",
        "no official compatibility claim until a result is recorded and inspected",
        "no nunchuk validation",
    ):
        if phrase.lower() not in text.lower():
            fail(f"{display(PLAN_DOC)} missing required phrase: {phrase}")
    template = TEMPLATE_DOC.read_text(encoding="utf-8")
    if "TEMPLATE_ONLY_NOT_A_RESULT" not in template:
        fail("manual import/export result template must remain template-only")


def validate_fixture() -> None:
    payload = load_json_object(PLAN_FIXTURE)
    if payload.get("status") != "MANUAL_TEST_PLAN_ONLY_NOT_A_RESULT":
        fail("manual test-plan fixture status must be plan-only")
    fields = payload.get("operator_fields")
    if not isinstance(fields, dict):
        fail("manual test-plan operator_fields must be an object")
    for key, value in fields.items():
        if value != PLACEHOLDER:
            fail(f"manual test-plan operator field {key} must remain an unknown placeholder")
    rows = payload.get("future_result_rows")
    if not isinstance(rows, list) or not rows:
        fail("manual test-plan must include future result rows")
    for row in rows:
        if not isinstance(row, dict):
            fail("manual test-plan result rows must be objects")
        if row.get("pass") is not False:
            fail("manual test-plan must not mark any future result row pass")
        if row.get("status") != "UNKNOWN_NOT_EXECUTED":
            fail("manual test-plan future rows must remain not executed")
    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail("manual test-plan non_claims must be an object")
    for key in (
        "no_device_write",
        "no_webserial",
        "no_runtime_loaded_config",
        "no_firmware_flashing_automation",
        "no_hardware_behavior_validation",
        "no_official_compatibility_claim_until_result_recorded_and_inspected",
        "no_nunchuk_validation",
        "not_a_result_packet",
    ):
        if non_claims.get(key) is not True:
            fail(f"manual test-plan non-claim {key} must be true")


def main() -> int:
    print("glyph_official_configurator_manual_import_export_test_plan")
    try:
        validate_doc()
        validate_fixture()
    except (CorpusError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print("manual_test_plan_only=true")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("manual_test_plan_only=true")
    print("result_recorded=false")
    print("official_configurator_compatibility_claim=false")
    print("device_write=false")
    print("hardware_behavior_validation=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
