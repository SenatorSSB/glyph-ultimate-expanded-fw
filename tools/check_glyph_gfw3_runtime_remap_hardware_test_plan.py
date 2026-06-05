#!/usr/bin/env python3
"""Validate the GFW3 runtime remap hardware test plan packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_gfw3_runtime_remap_hardware_test_plan_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_test_plan_2026-06-04.json"
)

SCHEMA_NAME = "glyph_gfw3_runtime_remap_hardware_test_plan"
PLAN_VERSION = 1
STATUS = "planned_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

EXPECTED_TABLE = {
    "1": [69, 78],
    "2": [128, 78],
    "3": [187, 78],
    "4": [69, 128],
    "5": "unchanged_or_unset",
    "6": [187, 128],
    "7": [72, 172],
    "8": [128, 179],
    "9": [184, 172],
}

REQUIRED_ROW_IDS = (
    "boot_profile_sanity",
    "base_rf6_z_airdodge",
    "base_rf5_up_a",
    "scratched_rf11",
    "scratched_rf12",
    "scratched_rf15",
    "base_rf2_b",
    "base_rf3_x",
    "base_rf4_tilt1",
    "rf4_cstick_suppresses_base_tilt1",
    "base_rt1_tilt2",
    "rf3_rf4_no_tilt3",
    "rt1_rf4_custom_table",
    "rt1_rf4_cstick_custom_preserved",
    "rf4_rf2_minus41",
    "rf4_rf2_cstick_suppresses_minus41",
    "rf9_null_both_sticks",
    "rf9_rf4_null_disabled",
    "rf9_rf4_cstick_reenables_null",
    "rf9_rf3_suppresses_x",
    "rf9_rf3_cstick_restores_x",
    "lt1_l",
    "lt3_l_r",
    "lt4_x2_mx2",
    "lt5_x1_mx1",
    "lt2_base_y1_my1",
    "lt2_rf4_flipper",
    "lt2_rf4_cstick_suppresses_flipper",
    "lt2_rf3_b_normal_x",
    "lt2_rf3_rf4_b_flipper",
    "lt2_rf3_rf4_cstick_fallback_rf3",
    "lt2_rf2_forced_up",
    "lt2_rf1_x_cstick_suppression",
    "lf4_rf4_tilt1",
    "lf4_rf4_cstick_suppresses_tilt1",
    "lf4_rf3_forced_up",
    "lf4_rf2_x",
    "lf4_rf2_rf4_deactivates_rf4",
    "lf4_rf2_cstick_suppression",
    "lf4_overrides_lt2",
    "rf3_rt5_left_special",
    "rf3_rt5_right_special",
    "rf3_rt2_left_special",
    "rf3_rt2_right_special",
    "rf3_vertical_no_horizontal_preserves_normal",
    "rf3_horizontal_unaffected",
    "rf3_two_axis_cstick_preserved",
    "rf7_hard_up_b_unchanged",
    "rf13_ls_to_dpad_unchanged",
    "nunchuk_preserved_not_tested",
)

REQUIRED_DOC_PHRASES = (
    "This is not a hardware result.",
    "Hardware validation is not claimed by this plan.",
    "No runtime-loaded config is implemented or tested here.",
    "No WebSerial/device write workflow is implemented or tested here.",
    "Do not merge `glyph/gfw3-runtime-remap-rework` into `configurator`",
    "a separate hardware result document is recorded",
    "RT1+RF4 Raw Table",
    "unchanged/unset",
)


class HardwareTestPlanError(ValueError):
    """Raised when the hardware test plan packet drifts from constraints."""


def fail(message: str) -> None:
    raise HardwareTestPlanError(message)


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


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "plan_version": PLAN_VERSION,
        "status": STATUS,
        "firmware_branch": "glyph/gfw3-runtime-remap-rework",
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "hardware_result_recorded": False,
        "runtime_loaded_config_implemented": False,
        "webserial_write_implemented": False,
        "device_write_implemented": False,
        "profile_artifact_change_required": False,
        "nunchuk_status": "preserved_but_not_hardware_validated",
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")
    if fixture.get("configurator_merge_blocked_until") != [
        "user_hardware_test_passes",
        "hardware_result_doc_recorded",
    ]:
        fail("configurator merge gate drifted")


def validate_table(fixture: dict[str, Any]) -> None:
    if fixture.get("rt1_rf4_custom_table_raw") != EXPECTED_TABLE:
        fail("RT1+RF4 custom raw table drifted")


def validate_rows(fixture: dict[str, Any]) -> None:
    rows = fixture.get("test_rows")
    if not isinstance(rows, list):
        fail("test_rows must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            fail(f"test_rows[{index}] must be an object")
        row_id = row.get("row_id")
        if not isinstance(row_id, str) or not row_id:
            fail(f"test_rows[{index}].row_id must be a non-empty string")
        if row_id in by_id:
            fail(f"duplicate row_id: {row_id}")
        by_id[row_id] = row
        status = row.get("status")
        if row_id == "nunchuk_preserved_not_tested":
            if status != "not_executed_unavailable":
                fail("nunchuk row must remain not_executed_unavailable")
        elif status != "not_executed":
            fail(f"{row_id} must remain not_executed")
        for key in ("category", "input_condition", "directions", "expected_result"):
            if not isinstance(row.get(key), str) or not row[key]:
                fail(f"{row_id}.{key} must be a non-empty string")

    missing = [row_id for row_id in REQUIRED_ROW_IDS if row_id not in by_id]
    if missing:
        fail(f"missing required row IDs: {', '.join(missing)}")
    extra = sorted(set(by_id) - set(REQUIRED_ROW_IDS))
    if extra:
        fail(f"unexpected row IDs: {', '.join(extra)}")


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")
    for row_id in REQUIRED_ROW_IDS:
        if row_id not in text:
            fail(f"{display(DOC_PATH)} missing row ID: {row_id}")


def main() -> int:
    print("glyph_gfw3_runtime_remap_hardware_test_plan")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_table(fixture)
        validate_rows(fixture)
        validate_doc()
    except (OSError, HardwareTestPlanError, ValueError) as exc:
        print("status=FAIL")
        print(f"hardware_status={HARDWARE_STATUS}")
        print("hardware_validation_claimed=false")
        print("hardware_result_recorded=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("hardware_validation_claimed=false")
    print("hardware_result_recorded=false")
    print("runtime_loaded_config_implemented=false")
    print("webserial_write_implemented=false")
    print("device_write_implemented=false")
    print("configurator_merge_blocked=true")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
