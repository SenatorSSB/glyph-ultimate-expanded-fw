#!/usr/bin/env python3
"""Validate source-backed Glyph identity runtime behavior case matrix."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import load_source_text_with_generated_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_identity_runtime_behavior_cases_2026-05-28.md"
FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_identity_runtime_behavior_cases_2026-05-28.json"
ROLE_MAP_DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_identity_runtime_role_map_2026-05-28.md"
ROLE_MAP_FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_identity_runtime_role_map_2026-05-28.json"
HARDWARE_RESULT_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md"
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"

EXPECTED_SOURCE_AUTHORITY = {
    "runtime": "src/modes/Ultimate.cpp",
    "role_map_doc": "docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md",
    "role_map_fixture": "docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json",
    "hardware_result": "docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md",
}

ALLOWED_SOURCE_REFS = {
    "src/modes/Ultimate.cpp",
    "docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md",
    "docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json",
    "docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md",
    "docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md",
    "docs/calibration/glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md",
    "docs/calibration/glyph_smashbox_modifiers_hardware_test_plan_2026-05-27.md",
}

REQUIRED_CATEGORIES = {
    "digital_button_carrier",
    "base_direction",
    "default_analog_table",
    "mode_default_analog_table",
    "single_modifier_table_selection",
    "mode_modifier_table_selection",
    "multi_modifier_fallback",
    "composite_table",
    "pure_layer",
    "lf4_sub_mode",
    "c_stick_suppression",
    "direction_plus_a_override",
    "z_airdodge_low_magnitude_override",
    "rf7_hard_up_b",
    "rf9_null_override",
    "rf13_ls_to_dpad",
    "right_stick_c_stick",
    "nunchuk_source_preservation",
}

REQUIRED_CASE_IDS = {
    "digital_rf1_a_carrier",
    "digital_rf5_b_carrier",
    "digital_lf4_b_carrier",
    "digital_rf10_y_carrier",
    "digital_rt1_z_carrier",
    "digital_lt5_z_carrier",
    "digital_rf11_z_carrier",
    "digital_lt3_l_carrier",
    "digital_rf16_r_carrier",
    "digital_mb4_capture_carrier",
    "digital_mb5_home_carrier",
    "digital_mb6_select_minus_carrier",
    "digital_mb7_start_plus_carrier",
    "base_lf3_effective_left",
    "base_lf1_effective_right",
    "base_lf2_effective_up",
    "base_lf5_effective_down",
    "base_lf3_lf1_horizontal_cancel",
    "base_rf6_forced_up",
    "base_rf6_lf5_forced_up_suppresses_down",
    "default_direction_5_neutral",
    "default_direction_4_left",
    "default_direction_6_right",
    "default_direction_2_down",
    "default_direction_8_up",
    "default_direction_1_left_down",
    "default_direction_3_right_down",
    "default_direction_7_left_up",
    "default_direction_9_right_up",
    "mode_default_direction_5_neutral",
    "mode_default_direction_4_left",
    "mode_default_direction_6_right",
    "mode_default_direction_2_down",
    "mode_default_direction_8_up",
    "mode_default_direction_1_left_down",
    "mode_default_direction_3_right_down",
    "single_x1_neutral",
    "single_x1_right",
    "single_x2_neutral",
    "single_x2_right",
    "single_y1_neutral",
    "single_y1_up",
    "single_y1_down",
    "single_tilt1_neutral",
    "single_tilt1_right",
    "single_tilt2_neutral",
    "single_tilt2_right",
    "single_tilt3_neutral",
    "single_tilt3_right",
    "mode_modifier_mx1_neutral",
    "mode_modifier_mx2_neutral",
    "mode_modifier_my1_neutral",
    "mode_modifier_mtilt1_neutral",
    "mode_modifier_mtilt2_neutral",
    "mode_modifier_mtilt3_neutral",
    "fallback_x1_x2_default_neutral",
    "fallback_mode_x1_x2_mode_default_neutral",
    "fallback_y1_tilt2_default_right",
    "fallback_guard_tilt3_not_fallback_right",
    "composite_y1_tilt1_neutral",
    "composite_y1_tilt1_right",
    "composite_mode_y1_tilt1_neutral",
    "composite_mode_y1_tilt1_right",
    "composite_y1_layer_normal_x_left",
    "composite_y1_layer_flipper_left",
    "composite_mode_y1_layer_normal_x_left",
    "composite_mode_y1_layer_flipper_left",
    "composite_layer_rf4_flipper_wins_over_rf3_normal_x",
    "pure_layer_lf8_layer_left",
    "pure_layer_lf7_layer_right",
    "pure_layer_lf8_rf2_forced_up_no_x",
    "pure_layer_lf7_rf2_forced_up_no_x",
    "lf4_submode_lf4_lt2_y1_suppressed_default_neutral",
    "lf4_submode_lf4_lt2_rf2_x_no_forced_up",
    "lf4_submode_lf4_lt2_rf3_forced_up",
    "cstick_suppression_lf4_lt2_rf2_rt2_no_x",
    "cstick_suppression_lf4_lt2_rf2_rt3_no_x",
    "cstick_suppression_lf4_lt2_rf2_rt4_no_x",
    "cstick_suppression_lf4_lt2_rf2_rt5_no_x",
    "direction_plus_a_lt6_down_a_default",
    "direction_plus_a_rf12_up_a_default",
    "direction_plus_a_rf15_up_a_default",
    "direction_plus_a_mode_lt6_down_a",
    "direction_plus_a_mode_rf12_up_a",
    "z_airdodge_lt5_neutral_low_magnitude",
    "z_airdodge_lt5_left_low_magnitude",
    "z_airdodge_rf11_right_up_low_magnitude",
    "z_airdodge_lt5_rf12_forced_up_low_magnitude",
    "rf7_hard_up_b_neutral",
    "rf7_hard_up_b_left",
    "rf7_hard_up_b_right",
    "rf9_null_neutral",
    "rf9_null_overrides_rf7_hard_up_b",
    "rf13_left_to_dpad_center_left_stick",
    "rf13_mode_left_to_dpad_mode_center",
    "rf13_lf8_rf2_dpad_up_left_no_x",
    "right_stick_rt3_c_left",
    "right_stick_rt4_c_right",
    "right_stick_rt5_c_up",
    "right_stick_rt2_c_down",
    "nunchuk_c_rt5_dpad_up_right_stick_neutral",
    "nunchuk_connected_left_stick_override",
}

C_STICK_SUPPRESSION_DIRECT_CASES = {
    "cstick_suppression_lf4_lt2_rf2_rt2_no_x": ("RT2", "down"),
    "cstick_suppression_lf4_lt2_rf2_rt3_no_x": ("RT3", "left"),
    "cstick_suppression_lf4_lt2_rf2_rt4_no_x": ("RT4", "right"),
    "cstick_suppression_lf4_lt2_rf2_rt5_no_x": ("RT5", "up"),
}

REQUIRED_DOC_HEADINGS = (
    "## Purpose and status",
    "## Source authority",
    "## Case schema explanation",
    "## Digital button carrier cases",
    "## Base direction cases",
    "## Modifier table-selection cases",
    "## Mode table-selection cases",
    "## Composite table cases",
    "## Pure layer cases",
    "## LF4 sub-mode cases",
    "## C-stick suppression cases",
    "## Direction-plus-A override cases",
    "## LT5/RF11 low-magnitude Z-airdodge override cases",
    "## RF7 hard Up+B cases",
    "## RF9 null override cases",
    "## RF13 LS->DPad cases",
    "## Right-stick / C-stick cases",
    "## Nunchuk source-preservation cases",
    "## Future harness migration notes",
)

SOURCE_ANCHORS = (
    "constexpr StickPoint kDefaultTable[9]",
    "constexpr StickPoint kModeDefaultTable[9]",
    "constexpr StickPoint kX1Table[9]",
    "constexpr StickPoint kX2Table[9]",
    "constexpr StickPoint kY1Table[9]",
    "constexpr StickPoint kTilt1Table[9]",
    "constexpr StickPoint kTilt2Table[9]",
    "constexpr StickPoint kTilt3Table[9]",
    "constexpr StickPoint kY1Tilt1Table[9]",
    "constexpr StickPoint kMY1Tilt1Table[9]",
    "constexpr StickPoint kY1LayerNormalXTable[9]",
    "constexpr StickPoint kY1LayerFlipperTable[9]",
    "constexpr StickPoint kLt1LowMagnitudeTable[9]",
    "ResolveHorizontalAxis(inputs.lf3, inputs.lf1, layer.layer_left_active, layer.layer_right_active)",
    "state.layer_left_active = inputs.lf8;",
    "state.layer_right_active = inputs.lf7;",
    "state.lf4_submode_active = inputs.lf4 && (state.layer_direction_active || inputs.lt2);",
    "state.rf2_suppressed_by_lf4_submode_cstick = state.lf4_submode_active && state.c_stick_any_active;",
    "state.force_up_active = inputs.rf6 || inputs.rf12 || inputs.rf15 || pure_layer_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
    "state.y1_active = inputs.lt2 && !inputs.lf4;",
    "state.z_airdodge_override_active = inputs.lt5 || inputs.rf11;",
    "state.null_modifier_active = inputs.rf9;",
    "state.hard_up_b_active = inputs.rf7;",
    "state.ls_to_dpad_active = inputs.rf13;",
    "outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12 || inputs.rf15;",
    "outputs.b = inputs.rf5 || inputs.lf4 || inputs.rf7 || (layer.layer_direction_active && !inputs.lf4 && inputs.rf3);",
    "outputs.x = inputs.rf2 && !layer.rf2_suppressed_by_lf4_submode_cstick && (!layer.layer_direction_active || inputs.lf4);",
    "outputs.buttonR = inputs.rt1 || inputs.lt5 || inputs.rf11;",
    "outputs.buttonL = inputs.lt3;",
    "outputs.triggerRDigital = inputs.rf16;",
    "outputs.rightStickRight = inputs.rt4;",
    "outputs.rightStickUp = inputs.rt5;",
    "outputs.dpadUp = inputs.rt5;",
    "outputs.dpadRight = inputs.rt4;",
    "ApplyDirectionPlusAOverride(roles, outputs);",
    "ApplyZAirdodgeOverride(effective_directions, outputs);",
    "ApplyHardUpBOverride(effective_directions, outputs);",
    "ApplyNullOverride(outputs);",
    "if (inputs.nunchuk_c)",
    "if (inputs.nunchuk_connected)",
)

ROLE_MAP_ANCHORS = (
    '"schema_name": "glyph_identity_runtime_role_map"',
    '"nunchuk_status": "preserved_but_not_hardware_validated"',
    '"RF1": "A"',
    '"RF13": "LS->DPad"',
    '"RF7": "HardUpB"',
    '"special_composite_priority"',
)


class DuplicateKeyTracker:
    def __init__(self) -> None:
        self.duplicates: list[str] = []

    def hook(self, pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        counts: dict[str, int] = defaultdict(int)
        result: dict[str, Any] = {}
        for key, value in pairs:
            counts[key] += 1
            if counts[key] > 1:
                self.duplicates.append(key)
            result[key] = value
        return result


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise AssertionError(message)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {display(path)}")
    if path.resolve() == SOURCE_PATH.resolve():
        return load_source_text_with_generated_tables(path)
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    tracker = DuplicateKeyTracker()
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=tracker.hook)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be object: {display(path)}")
    return payload, tracker.duplicates


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    if not all(isinstance(item, str) and item for item in value):
        fail(f"{label} must contain only non-empty strings")
    return value


def require_bool_direction(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    expected_keys = {"left", "right", "up", "down"}
    keys = set(value)
    if keys != expected_keys:
        fail(f"{label} must have keys left/right/up/down, got {sorted(keys)}")
    for key in expected_keys:
        if not isinstance(value[key], bool):
            fail(f"{label}.{key} must be boolean")


def require_bool_map_or_null(value: Any, label: str) -> None:
    if value is None:
        return
    require_bool_direction(value, label)


def require_stick_or_null(value: Any, label: str) -> None:
    if value is None:
        return
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(coord, bool) or not isinstance(coord, int) for coord in value)
    ):
        fail(f"{label} must be null or [int, int]")
    x, y = value
    if not 0 <= x <= 255 or not 0 <= y <= 255:
        fail(f"{label} coordinates must be in [0,255], got {value}")


def validate_case(case: Any, index: int, source: str) -> tuple[str, str]:
    if not isinstance(case, dict):
        fail(f"cases[{index}] must be object")
    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        fail(f"cases[{index}].case_id must be non-empty string")
    category = case.get("category")
    if not isinstance(category, str) or not category:
        fail(f"{case_id}.category must be non-empty string")
    require_string_list(case.get("input_buttons"), f"{case_id}.input_buttons")

    if "input_state" in case and not isinstance(case["input_state"], dict):
        fail(f"{case_id}.input_state must be object when present")

    expected = case.get("expected")
    if not isinstance(expected, dict):
        fail(f"{case_id}.expected must be object")
    require_string_list(expected.get("digital_buttons"), f"{case_id}.expected.digital_buttons")
    require_bool_direction(expected.get("effective_direction"), f"{case_id}.expected.effective_direction")
    require_bool_map_or_null(expected.get("dpad"), f"{case_id}.expected.dpad")
    require_bool_map_or_null(expected.get("right_stick_digital"), f"{case_id}.expected.right_stick_digital")
    require_bool_map_or_null(expected.get("left_stick_digital"), f"{case_id}.expected.left_stick_digital")
    require_stick_or_null(expected.get("left_stick"), f"{case_id}.expected.left_stick")
    require_stick_or_null(expected.get("right_stick"), f"{case_id}.expected.right_stick")

    analog_source = expected.get("analog_source")
    if analog_source is not None and (not isinstance(analog_source, str) or not analog_source):
        fail(f"{case_id}.expected.analog_source must be null or non-empty string")
    table_id = expected.get("table_id")
    if table_id is not None and (not isinstance(table_id, str) or not table_id):
        fail(f"{case_id}.expected.table_id must be null or non-empty string")
    direction_index = expected.get("direction_index")
    if direction_index is not None and (
        isinstance(direction_index, bool) or not isinstance(direction_index, int) or not 1 <= direction_index <= 9
    ):
        fail(f"{case_id}.expected.direction_index must be null or integer 1..9")

    source_refs = require_string_list(case.get("source_refs"), f"{case_id}.source_refs")
    for source_ref in source_refs:
        if source_ref not in ALLOWED_SOURCE_REFS:
            fail(f"{case_id}.source_refs contains unsupported source: {source_ref}")
    if "src/modes/Ultimate.cpp" not in source_refs:
        fail(f"{case_id}.source_refs must include src/modes/Ultimate.cpp")

    notes = case.get("notes")
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        fail(f"{case_id}.notes must be a list of strings")

    left_stick = expected.get("left_stick")
    if table_id is not None and left_stick is not None:
        x, y = left_stick
        point = f"{{{x}, {y}}}"
        if point not in source:
            fail(f"{case_id}.expected.left_stick {point} is not present in runtime source table constants")

    return case_id, category


def validate_direct_cstick_suppression_cases(cases_by_id: dict[str, dict[str, Any]]) -> None:
    c_stick_buttons = {"RT2", "RT3", "RT4", "RT5"}
    for case_id, (c_stick_button, right_stick_direction) in C_STICK_SUPPRESSION_DIRECT_CASES.items():
        case = cases_by_id.get(case_id)
        if case is None:
            fail(f"missing direct LF4 sub-mode C-stick suppression case: {case_id}")
        if case.get("category") != "c_stick_suppression":
            fail(f"{case_id}.category must be c_stick_suppression")

        input_buttons = set(require_string_list(case.get("input_buttons"), f"{case_id}.input_buttons"))
        expected_input_buttons = {"LF4", "LT2", "RF2", c_stick_button}
        if input_buttons != expected_input_buttons:
            fail(
                f"{case_id}.input_buttons must be exactly "
                + ", ".join(sorted(expected_input_buttons))
                + f"; got {', '.join(sorted(input_buttons))}"
            )
        if len(input_buttons & c_stick_buttons) != 1:
            fail(f"{case_id}.input_buttons must include exactly one C-stick input")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            fail(f"{case_id}.expected must be object")
        digital_buttons = require_string_list(expected.get("digital_buttons"), f"{case_id}.expected.digital_buttons")
        suppressed_buttons = require_string_list(expected.get("suppressed_buttons"), f"{case_id}.expected.suppressed_buttons")
        if "B" not in digital_buttons:
            fail(f"{case_id}.expected.digital_buttons must include B")
        if "X" in digital_buttons:
            fail(f"{case_id}.expected.digital_buttons must not include X")
        if "X" not in suppressed_buttons:
            fail(f"{case_id}.expected.suppressed_buttons must include X")

        effective_direction = expected.get("effective_direction")
        if not isinstance(effective_direction, dict):
            fail(f"{case_id}.expected.effective_direction must be object")
        if effective_direction.get("up") is True:
            fail(f"{case_id}.expected.effective_direction.up must not be true from RF2")
        if any(effective_direction.get(direction) is True for direction in ("left", "right", "up", "down")):
            fail(f"{case_id}.expected.effective_direction must not include RF2-owned directional LS phase")

        right_stick = expected.get("right_stick_digital")
        if not isinstance(right_stick, dict):
            fail(f"{case_id}.expected.right_stick_digital must be object")
        for direction in ("left", "right", "up", "down"):
            expected_value = direction == right_stick_direction
            if right_stick.get(direction) is not expected_value:
                fail(f"{case_id}.expected.right_stick_digital.{direction} must be {expected_value}")

        source_refs = require_string_list(case.get("source_refs"), f"{case_id}.source_refs")
        if "src/modes/Ultimate.cpp" not in source_refs:
            fail(f"{case_id}.source_refs must include src/modes/Ultimate.cpp")


def validate_doc(doc: str) -> None:
    for heading in REQUIRED_DOC_HEADINGS:
        if heading not in doc:
            fail(f"behavior case doc missing heading: {heading}")
    for phrase in (
        "Docs/fixture/checker-only",
        "No runtime behavior change.",
        "No generated config.",
        "No runtime-loaded config.",
        "No serial writing.",
        "No new hardware claim.",
        "No Senscope browser app semantic claim.",
        "No case should be treated as a new hardware validation result.",
        "Cases are representative, not exhaustive.",
        "Nunchuk behavior is source-present",
    ):
        if phrase not in doc:
            fail(f"behavior case doc missing required caveat phrase: {phrase}")


def validate_payload(payload: dict[str, Any], duplicate_keys: list[str], source: str) -> tuple[int, int]:
    if duplicate_keys:
        fail("duplicate JSON object keys detected: " + ", ".join(sorted(set(duplicate_keys))))
    if payload.get("behavior_case_contract_version") != 1:
        fail("behavior_case_contract_version must be 1")
    if payload.get("schema_name") != "glyph_identity_runtime_behavior_cases":
        fail("schema_name must be glyph_identity_runtime_behavior_cases")
    if payload.get("mode_scope") != "MODE_ULTIMATE":
        fail("mode_scope must be MODE_ULTIMATE")
    if payload.get("source_status") != "source_backed_expected_behavior_cases":
        fail("source_status must be source_backed_expected_behavior_cases")
    if payload.get("hardware_status") != "cases_derive_from_hardware_verified_role_map_but_are_not_new_hardware_results":
        fail("hardware_status must preserve no-new-hardware-result caveat")
    if payload.get("source_authority") != EXPECTED_SOURCE_AUTHORITY:
        fail("source_authority does not match expected behavior-case authority set")
    if payload.get("nunchuk_status") != "preserved_but_not_hardware_validated":
        fail("nunchuk_status must be preserved_but_not_hardware_validated")
    if payload.get("direction_convention") != "numpad":
        fail("direction_convention must be numpad")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("cases must be a non-empty list")

    seen_case_ids: set[str] = set()
    categories: set[str] = set()
    cases_by_id: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(cases):
        case_id, category = validate_case(case, index, source)
        if case_id in seen_case_ids:
            fail(f"duplicate case_id: {case_id}")
        seen_case_ids.add(case_id)
        categories.add(category)
        if isinstance(case, dict):
            cases_by_id[case_id] = case

    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        fail("missing required behavior categories: " + ", ".join(missing_categories))

    missing_cases = sorted(REQUIRED_CASE_IDS - seen_case_ids)
    if missing_cases:
        fail("missing required behavior case IDs: " + ", ".join(missing_cases))

    validate_direct_cstick_suppression_cases(cases_by_id)

    return len(cases), len(categories)


def validate_sources(source: str, role_map_fixture: str, role_map_doc: str, hardware_result: str) -> None:
    for anchor in SOURCE_ANCHORS:
        if anchor not in source:
            fail(f"runtime source missing anchor: {anchor}")
    for anchor in ROLE_MAP_ANCHORS:
        if anchor not in role_map_fixture:
            fail(f"role-map fixture missing anchor: {anchor}")
    for phrase in (
        "Source-backed canonical documentation",
        "Nunchuk behavior remains preserved in source but not hardware-validated.",
        "RF13 = LS->DPad",
        "RF7 = hard Up+B",
    ):
        if phrase not in role_map_doc:
            fail(f"role-map doc missing anchor phrase: {phrase}")
    for phrase in (
        "PASS_IDENTITY_RUNTIME_SMASHBOX_LATEST_PROFILE",
        "nunchuk | NOT_TESTED_UNAVAILABLE",
    ):
        if phrase not in hardware_result:
            fail(f"hardware result missing anchor phrase: {phrase}")


def main() -> int:
    try:
        source = read_text(SOURCE_PATH)
        role_map_fixture = read_text(ROLE_MAP_FIXTURE_PATH)
        role_map_doc = read_text(ROLE_MAP_DOC_PATH)
        hardware_result = read_text(HARDWARE_RESULT_PATH)
        doc = read_text(DOC_PATH)
        payload, duplicate_keys = load_json(FIXTURE_PATH)
        validate_sources(source, role_map_fixture, role_map_doc, hardware_result)
        validate_doc(doc)
        case_count, category_count = validate_payload(payload, duplicate_keys, source)
    except AssertionError as exc:
        print("glyph_identity_runtime_behavior_cases")
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("glyph_identity_runtime_behavior_cases")
    print("status=PASS")
    print(f"doc={display(DOC_PATH)}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"source={display(SOURCE_PATH)}")
    print(f"cases={case_count}")
    print(f"categories={category_count}")
    print("hardware_status=not_new_hardware_result")
    print("nunchuk_status=preserved_but_not_hardware_validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
