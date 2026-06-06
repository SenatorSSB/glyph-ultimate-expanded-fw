#!/usr/bin/env python3
"""Validate the Glyph GFW3 runtime remap rework spec packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.json"
)

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_gfw3_runtime_remap_rework_spec",
    "spec_version": 1,
    "status": "firmware_behavior_change_spec_only",
    "mode_scope": "MODE_ULTIMATE",
    "hardware_status": "not_hardware_validated",
    "firmware_implementation_status": "not_yet_claimed",
    "profile_artifact_change": "forbidden",
    "nunchuk_status": "preserved_but_not_hardware_validated",
    "runtime_loaded_config": "not_implemented",
    "webserial_device_write": "not_implemented",
}

REQUIRED_DOC_PHRASES = (
    "firmware behavior change requested",
    "firmware implementation not yet claimed",
    "hardware validation not claimed",
    "final merge to `configurator` blocked",
    "RF6 becomes Z plus the existing low-magnitude",
    "RF5 becomes forced Up plus A",
    "RF3 + RF4 must not activate Tilt3",
    "RF4 + RF2 changes only the RF4 modifier X offset to -41",
    "RF4 mirrored/flipper/modifier behavior is suppressed while any C-stick button",
    "RT1 + RF4 custom table is exempt from RF4 C-stick suppression",
    "RT1 base role becomes the current Tilt2 table",
    "Mode + RT1 uses MTilt2",
    "RF9 full-null mode nulls both left stick and right stick inputs",
    "RF9 + RF4 disables all RF9 nullification",
    "RF9 + RF4 + C-stick suppresses RF4 behavior",
    "RF9 + RF3 enters a base-RF3-X suppression mode",
    "does not full-null left stick or right stick/C-stick output",
    "RF9 + RF3 + C-stick restores base RF3 X",
    "RF4 behavior is suppressed/nullified while RF9 base-RF3-X suppression mode is",
    "direction source is the resolved digital left/right state",
    "RF3 + RT5 + resolved left: right stick `(95,165)`",
    "existing C-stick horizontal or two-axis diagonal/ASDI behavior is preserved",
    "LT1 = old LT3 = L",
    "LT4 = old LT1 = X2 / MX2",
    "LT5 = old LT4 = X1 / MX1",
    "LT3 = new L + R role",
    "LF8 layer-left and LF7 layer-right are scratched",
    "LF4 overrides LT2 behavior when both are held",
    "This spec is not a hardware result",
)

EXPECTED_BASE_ROLES = {
    "RF6": {"Z", "low_magnitude_z_airdodge_override"},
    "RF5": {"A", "forced_up"},
    "RF15": {"scratched_hard_up_a"},
    "RF12": {"scratched_hard_up_a"},
    "RF11": {"scratched_z_airdodge"},
    "RF3": {"X"},
    "RF2": {"B"},
    "RF4": {"Tilt1"},
    "RT1": {"Tilt2"},
    "RT1_RF4": {"CustomRT1RF4"},
    "RF7": {"preserve_hard_up_b"},
    "RF13": {"preserve_ls_to_dpad"},
}

EXPECTED_SCRATCHED = {
    "RF3_RF4_Tilt3_fusion",
    "RF15_hard_up_a",
    "RF12_hard_up_a",
    "RF11_z_airdodge",
    "RT1_z_carrier",
    "LT5_z_airdodge",
    "LF8_layer_left",
    "LF7_layer_right",
    "pure_layer_RF2_RF3_RF4_behavior",
}

EXPECTED_LT_CYCLE = {
    "LT1": "L",
    "LT4": "X2_MX2",
    "LT5": "X1_MX1",
    "LT3": "L_plus_R",
}

EXPECTED_RT1_RF4_TABLE = {
    "1": [69, 78],
    "2": [128, 78],
    "3": [187, 78],
    "4": [69, 128],
    "5": None,
    "6": [187, 128],
    "7": [72, 172],
    "8": [128, 179],
    "9": [184, 172],
}

EXPECTED_LT2_NORMAL_X = {
    "1": [87, 51],
    "2": [128, 51],
    "3": [169, 51],
    "4": [87, 128],
    "5": [128, 128],
    "6": [169, 128],
    "7": [87, 205],
    "8": [128, 205],
    "9": [169, 205],
}

EXPECTED_LT2_FLIPPER = {
    "1": [169, 51],
    "2": [128, 51],
    "3": [87, 51],
    "4": [169, 128],
    "5": [128, 128],
    "6": [87, 128],
    "7": [169, 205],
    "8": [128, 205],
    "9": [87, 205],
}

REQUIRED_FORBIDDEN_CLAIMS = {
    "hardware_validation",
    "firmware_implementation_complete",
    "runtime_loaded_config",
    "WebSerial_device_write",
    "active_profile_artifact_change",
    "nunchuk_behavior_change",
    "macro_turbo_timing_automation",
}

REQUIRED_PRIORITY = {
    "LF4_submode_overrides_LT2_sublayer",
    "RT1_RF4_custom_overrides_RF4_Tilt1_and_RT1_Tilt2",
    "RF4_RF2_base_minus_41_inactive_under_LF4_or_LT2",
    "RF9_full_null_last_except_behaviorally_available_RF9_RF4_disables_null_and_RF9_base_RF3_X_mode",
    "RT1_RF4_custom_exempt_from_RF4_cstick_suppression",
    "RF4_modifier_behavior_suppressed_by_cstick_outside_custom_exception",
    "existing_cstick_two_axis_asdi_preserved_outside_RF3_vertical_special",
    "RF3_vertical_cstick_special_before_RF9_null",
    "nunchuk_preserved_after_runtime_overrides",
}


class Gfw3RuntimeRemapSpecError(ValueError):
    """Raised when the GFW3 runtime remap spec packet drifts."""


def fail(message: str) -> None:
    raise Gfw3RuntimeRemapSpecError(message)


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


def require_object(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        fail(f"{key} must be an object")
    return value


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_superset(actual: list[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{label} missing required value(s): " + ", ".join(missing))


def require_table(payload: dict[str, Any], key: str, expected: dict[str, list[int] | None]) -> None:
    table = require_object(payload, "custom_tables").get(key)
    if table != expected:
        fail(f"custom_tables.{key} does not match expected raw coordinates")


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_source_authority(payload: dict[str, Any]) -> None:
    source_authority = require_object(payload, "source_authority")
    required = {"user_requirements", "runtime_source", "runtime_tables", "architecture_hardening"}
    missing = sorted(required - set(source_authority))
    if missing:
        fail("source_authority missing required key(s): " + ", ".join(missing))
    if source_authority["runtime_source"] != "src/modes/Ultimate.cpp":
        fail("source_authority.runtime_source must be src/modes/Ultimate.cpp")


def validate_roles(payload: dict[str, Any]) -> None:
    base_roles = require_object(payload, "base_role_changes")
    for button, expected in EXPECTED_BASE_ROLES.items():
        actual = base_roles.get(button)
        if not isinstance(actual, list) or set(actual) != expected:
            fail(f"base_role_changes.{button} must be {sorted(expected)!r}")
    require_superset(require_string_list(payload, "scratched_roles"), EXPECTED_SCRATCHED, "scratched_roles")


def validate_fixture(payload: dict[str, Any]) -> None:
    validate_top_level(payload)
    validate_source_authority(payload)
    validate_roles(payload)
    if require_object(payload, "lt_physical_move_cycle") != EXPECTED_LT_CYCLE:
        fail("lt_physical_move_cycle does not match required LT move cycle")
    expected_mode = {
        "mode_exists": True,
        "Mode_RT1": "MTilt2",
        "MTilt1": "may_be_scratched",
        "mode_can_win_over_RF4_Tilt1": True,
        "RT1_RF4_mode_table": "same_as_non_mode",
    }
    if require_object(payload, "mode_behavior") != expected_mode:
        fail("mode_behavior does not match expected mode policy")
    require_table(payload, "RT1_RF4", EXPECTED_RT1_RF4_TABLE)
    require_table(payload, "LT2_RF3_normal_x", EXPECTED_LT2_NORMAL_X)
    require_table(payload, "LT2_RF4_flipper", EXPECTED_LT2_FLIPPER)

    rf9 = require_object(payload, "rf9_null_behavior")
    if rf9.get("full_null_mode_when") != "RF9_and_not_RF9_base_RF3_X_mode":
        fail("RF9 full-null mode predicate drifted")
    if rf9.get("nulls_left_stick") is not True or rf9.get("nulls_right_stick") is not True:
        fail("RF9 full-null mode must null both sticks")
    if rf9.get("exception") != "RF9_plus_behaviorally_available_RF4_disables_all_RF9_nullification":
        fail("RF9 exception must be behaviorally available RF4")
    if rf9.get("exception_presses_extra_button") is not False:
        fail("RF9+RF4 exception must not press an extra button")
    if rf9.get("rf4_cstick_suppressed_exception") != "RF9_plus_RF4_plus_Cstick_reenables_RF9_nullification":
        fail("RF9+RF4+C-stick must re-enable RF9 nullification")

    rf4_cstick = require_object(payload, "rf4_cstick_suppression")
    if rf4_cstick.get("cstick_buttons") != ["RT2", "RT3", "RT4", "RT5"]:
        fail("RF4 C-stick suppression button set drifted")
    require_superset(
        rf4_cstick.get("suppresses", []),
        {
            "base_RF4_Tilt1",
            "base_RF4_RF2_Tilt1_minus_41",
            "LT2_RF4_flipper",
            "LF4_RF4_Tilt1",
        },
        "rf4_cstick_suppression.suppresses",
    )
    if rf4_cstick.get("rt1_rf4_custom_exception") is not True:
        fail("RT1+RF4 custom must be exempt from RF4 C-stick suppression")
    if rf4_cstick.get("lt2_rf3_rf4_cstick_fallback") != "LT2_RF3_B_plus_normal_x":
        fail("LT2+RF3+RF4+C-stick fallback drifted")
    if rf4_cstick.get("rf9_rf4_cstick_reenables_null") is not True:
        fail("RF9+RF4+C-stick must re-enable null")

    rf9_rf3 = require_object(payload, "rf9_rf3_x_behavior")
    if rf9_rf3.get("base_rf3_x_active_when") != ["RF3", "not_LT2", "not_LF4"]:
        fail("base RF3 X scope drifted")
    if rf9_rf3.get("rf9_base_rf3_x_mode_active_when") != ["RF9", "RF3", "not_LT2", "not_LF4"]:
        fail("RF9 base RF3 X mode predicate drifted")
    if rf9_rf3.get("rf9_suppresses_base_rf3_x_without_cstick") is not True:
        fail("RF9 must suppress base RF3 X without C-stick")
    if rf9_rf3.get("cstick_restores_base_rf3_x_under_rf9") is not True:
        fail("C-stick must restore base RF3 X under RF9")
    if rf9_rf3.get("full_nulls_left_stick") is not False:
        fail("RF9 base RF3 X mode must not full-null left stick")
    if rf9_rf3.get("full_nulls_right_stick") is not False:
        fail("RF9 base RF3 X mode must not full-null right stick")
    if rf9_rf3.get("cstick_output_remains_active") is not True:
        fail("RF9 base RF3 X mode must keep C-stick output active")
    if rf9_rf3.get("rf4_behavior_available_in_mode") is not False:
        fail("RF4 behavior must be unavailable in RF9 base RF3 X mode")
    if rf9_rf3.get("rt1_rf4_custom_available_in_mode") is not False:
        fail("RT1+RF4 custom must be unavailable in RF9 base RF3 X mode")
    if rf9_rf3.get("restoration_scope") != "base_RF3_X_only":
        fail("RF9+RF3 X restoration scope drifted")
    require_superset(
        rf9_rf3.get("does_not_convert", []),
        {"LT2_RF3_B_normal_x", "LF4_RF3_forced_up"},
        "rf9_rf3_x_behavior.does_not_convert",
    )

    rf3_cstick = require_object(payload, "rf3_vertical_cstick_special")
    if rf3_cstick.get("direction_source") != "EffectiveDirectionState.left_right":
        fail("RF3 vertical C-stick direction source must be resolved digital left/right")
    expected_coordinates = {
        "RF3_RT5_resolved_left": [95, 165],
        "RF3_RT5_resolved_right": [161, 165],
        "RF3_RT2_resolved_left": [95, 91],
        "RF3_RT2_resolved_right": [161, 91],
    }
    if rf3_cstick.get("coordinates") != expected_coordinates:
        fail("RF3 vertical C-stick coordinates drifted")
    if rf3_cstick.get("neutral_horizontal") != "preserve_normal_cstick_vertical":
        fail("RF3 vertical C-stick neutral-horizontal behavior drifted")
    if rf3_cstick.get("rt3_rt4_active") != "preserve_existing_cstick_horizontal_or_two_axis_asdi":
        fail("RF3 vertical C-stick RT3/RT4 preservation drifted")

    lt2 = require_object(payload, "lt2_sublayer")
    if lt2.get("base_without_sublayer") != "Y1_MY1" or lt2.get("LF4_overrides_LT2") is not True:
        fail("LT2 sublayer base/override policy drifted")
    if lt2.get("RF4") != "minus_41_flipper_modifier" or lt2.get("RF2") != "forced_up":
        fail("LT2 sublayer RF4/RF2 behavior drifted")
    if lt2.get("RF1") != "X" or lt2.get("RF1_cstick") != "suppress_X_only":
        fail("LT2 RF1/C-stick behavior drifted")

    expected_lf4 = {
        "LF4": "B",
        "overrides_LT2": True,
        "RF4": "Tilt1",
        "RF3": "forced_up",
        "RF2": "X",
        "RF2_RF4": "RF2_deactivates_RF4_modifier",
        "RF2_cstick": "suppress_X_but_still_deactivate_RF4",
        "cstick_buttons": ["RT2", "RT3", "RT4", "RT5"],
    }
    if require_object(payload, "lf4_submode") != expected_lf4:
        fail("lf4_submode does not match requested LF4 override behavior")

    require_superset(require_string_list(payload, "priority"), REQUIRED_PRIORITY, "priority")
    require_superset(
        require_string_list(payload, "forbidden_claims"),
        REQUIRED_FORBIDDEN_CLAIMS,
        "forbidden_claims",
    )


def validate_docs() -> None:
    lower_text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lower_text:
            fail(f"missing required doc phrase: {phrase}")
    forbidden_positive_claims = (
        "hardware validation passed",
        "hardware validated",
        "firmware implementation complete",
        "runtime-loaded config implemented",
        "webserial implemented",
    )
    for phrase in forbidden_positive_claims:
        if phrase in lower_text:
            fail(f"forbidden positive claim in doc: {phrase}")


def main() -> int:
    try:
        if not DOC_PATH.exists():
            fail(f"missing doc: {display(DOC_PATH)}")
        if not FIXTURE_PATH.exists():
            fail(f"missing fixture: {display(FIXTURE_PATH)}")
        validate_docs()
        validate_fixture(load_json_object(FIXTURE_PATH))
    except Gfw3RuntimeRemapSpecError as exc:
        print(f"status=FAIL {exc}")
        return 1

    print(
        "status=PASS "
        f"doc={display(DOC_PATH)} fixture={display(FIXTURE_PATH)} "
        "hardware_status=not_hardware_validated firmware_implementation_status=not_yet_claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
