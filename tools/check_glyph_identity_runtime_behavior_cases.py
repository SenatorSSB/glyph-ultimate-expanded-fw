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
    "runtime_tables": "src/modes/UltimateIdentityRuntimeTables.hpp",
    "runtime_config_interpreter": "src/modes/UltimateRuntimeConfigInterpreter.hpp",
    "gfw3_spec_doc": "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md",
    "gfw3_spec_fixture": "docs/calibration/fixtures/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.json",
    "architecture_hardening": "docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md",
}

ALLOWED_SOURCE_REFS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp",
    "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md",
    "docs/calibration/fixtures/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.json",
    "docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md",
}

REQUIRED_CATEGORIES = {
    "base_role",
    "custom_modifier",
    "rf9_null",
    "lt_physical_move_cycle",
    "lf8_lf7_removed",
    "lt2_sublayer",
    "lf4_submode",
    "c_stick_suppression",
    "preservation",
}

REQUIRED_CASE_IDS = {
    "gfw3_rf6_z_airdodge_neutral",
    "gfw3_rf5_forced_up_a",
    "gfw3_rf15_scratched",
    "gfw3_rf12_scratched",
    "gfw3_rf11_scratched",
    "gfw3_rf3_base_x",
    "gfw3_rf2_base_b",
    "gfw3_rf4_base_tilt1",
    "gfw3_rf4_rt2_suppresses_tilt1",
    "gfw3_rt1_base_tilt2",
    "gfw3_mode_rf4_mode_default",
    "gfw3_mode_rf4_rt2_suppressed_mode_default",
    "gfw3_mode_rt1_mtilt2",
    "gfw3_mode_rt1_rf4_custom",
    "gfw3_rf3_rf4_no_tilt3",
    "gfw3_rt1_rf4_rt2_custom_preserved",
    "gfw3_rt1_rf4_custom_1",
    "gfw3_rt1_rf4_custom_2",
    "gfw3_rt1_rf4_custom_3",
    "gfw3_rt1_rf4_custom_4",
    "gfw3_rt1_rf4_custom_6",
    "gfw3_rt1_rf4_custom_7",
    "gfw3_rt1_rf4_custom_8",
    "gfw3_rt1_rf4_custom_9",
    "gfw3_rf4_rf2_base_minus41",
    "gfw3_rf4_rf2_rt2_suppresses_minus41",
    "gfw3_rf9_nulls_left_and_right_stick",
    "gfw3_rf9_rf4_disables_null",
    "gfw3_rf9_rf4_rt4_null_reenabled",
    "gfw3_rf9_rf3_suppresses_x",
    "gfw3_rf9_rf3_rt2_restores_x",
    "gfw3_rf9_rf3_rt5_restores_x_cstick_active",
    "gfw3_rf9_rf3_lf3_rt5_cstick_up_left_special",
    "gfw3_rf9_rf3_lf3_rt2_cstick_down_left_special",
    "gfw3_rf9_rf3_rf4_suppresses_rf4_no_full_null",
    "gfw3_rf9_rf3_rf4_rt5_restores_x_cstick_active",
    "gfw3_rf9_rf3_rt1_rf4_suppresses_custom_no_full_null",
    "gfw3_rf9_rf4_rt5_without_rf3_full_null_preserved",
    "gfw3_lt1_l",
    "gfw3_lt4_x2",
    "gfw3_lt5_x1",
    "gfw3_lt3_l_plus_r",
    "gfw3_lf8_no_layer_left",
    "gfw3_lf7_no_layer_right",
    "gfw3_lt2_base_y1",
    "gfw3_lt2_rf4_flipper",
    "gfw3_lt2_rf4_rt2_suppresses_flipper",
    "gfw3_lt2_rf3_b_normal_x",
    "gfw3_lt2_rf3_rf4_b_flipper",
    "gfw3_lt2_rf3_rf4_rt2_falls_back_to_rf3",
    "gfw3_lt2_rf2_forced_up",
    "gfw3_lt2_rf1_x",
    "gfw3_lt2_rf1_rt2_suppresses_x",
    "gfw3_lt2_rf9_rf3_remains_b_not_x_full_null",
    "gfw3_lt2_rf9_rf3_rt2_remains_b_not_x",
    "gfw3_lf4_rf4_tilt1",
    "gfw3_lf4_rf4_rt2_suppresses_tilt1",
    "gfw3_lf4_rf3_forced_up",
    "gfw3_lf4_rf9_rf3_remains_forced_up_not_x_full_null",
    "gfw3_lf4_rf9_rf3_rt2_remains_forced_up_not_x",
    "gfw3_lf4_rf2_x",
    "gfw3_lf4_rf2_rf4_deactivates_rf4",
    "gfw3_lf4_rf2_rt2_suppresses_x_deactivates_rf4",
    "gfw3_lf4_lt2_uses_lf4_behavior",
    "gfw3_lf4_lt2_rf4_tilt1",
    "gfw3_lf4_lt2_rf2_rf4_deactivates_rf4",
    "gfw3_lf4_lt2_rf2_rf4_rt2_suppresses_x_deactivates_rf4",
    "gfw3_rf3_lf3_rt5_cstick_up_left_special",
    "gfw3_rf3_lf1_rt5_cstick_up_right_special",
    "gfw3_rf3_lf3_rt2_cstick_down_left_special",
    "gfw3_rf3_lf1_rt2_cstick_down_right_special",
    "gfw3_rf3_rt5_no_horizontal_normal_cup",
    "gfw3_rf3_rt2_no_horizontal_normal_cdown",
    "gfw3_rf3_lf1_rt4_normal_cright",
    "gfw3_rf3_lf1_rt5_rt4_preserves_two_axis_cstick",
    "gfw3_rf7_hard_up_b_preserved",
    "gfw3_rf13_ls_to_dpad_preserved",
    "nunchuk_c_rt5_dpad_up_right_stick_neutral",
    "nunchuk_connected_left_stick_override",
}

C_STICK_SUPPRESSION_DIRECT_CASES = {
    "gfw3_lt2_rf1_rt2_suppresses_x": ("LT2", "RF1", "RT2", "down"),
    "gfw3_lf4_rf2_rt2_suppresses_x_deactivates_rf4": ("LF4", "RF2", "RT2", "down"),
}

REQUIRED_DOC_HEADINGS = (
    "## Purpose and status",
    "## Source authority",
    "## Case schema explanation",
    "## Base role cases",
    "## Custom modifier cases",
    "## RF9 null cases",
    "## LT physical move cycle cases",
    "## LF8/LF7 removal cases",
    "## LT2 sublayer cases",
    "## LF4 submode cases",
    "## Preservation cases",
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
    "constexpr StickPoint kTilt1Minus41Table[9]",
    "constexpr StickPoint kRT1RF4CustomTable[9]",
    "constexpr StickPoint kY1Tilt1Table[9]",
    "constexpr StickPoint kMY1Tilt1Table[9]",
    "constexpr StickPoint kY1LayerNormalXTable[9]",
    "constexpr StickPoint kY1LayerFlipperTable[9]",
    "constexpr StickPoint kLt1LowMagnitudeTable[9]",
    "ResolveHorizontalAxis(inputs.lf3, inputs.lf1, layer.layer_left_active, layer.layer_right_active)",
    "state.layer_left_active = false;",
    "state.layer_right_active = false;",
    "state.lf4_submode_active = inputs.lf4;",
    "state.rf2_suppressed_by_lf4_submode_cstick = state.lf4_submode_active && state.c_stick_any_active;",
    "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
    "state.y1_active = inputs.lt2 && !inputs.lf4 && !lt2_sublayer_active;",
    "state.rf4_modifier_suppressed_by_cstick = rf4_modifier_suppressed_by_cstick;",
    "state.rf4_behavior_available = rf4_behavior_available;",
    "state.rf9_base_rf3_x_mode_active = rf9_base_rf3_x_mode_active;",
    "state.rf4_suppressed_by_rf9_rf3_mode = rf4_suppressed_by_rf9_rf3_mode;",
    "state.rf3_x_suppressed_by_rf9 = rf3_x_suppressed_by_rf9;",
    "state.z_airdodge_override_active = inputs.rf6;",
    "state.null_modifier_active = inputs.rf9 && !state.rf9_base_rf3_x_mode_active && !state.rf4_behavior_available;",
    "state.hard_up_b_active = inputs.rf7;",
    "state.ls_to_dpad_active = inputs.rf13;",
    "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
    "outputs.b = base_rf2_b_active || inputs.lf4 || inputs.rf7 || (inputs.lt2 && !inputs.lf4 && inputs.rf3);",
    "outputs.x = (roles.base_rf3_x_active && !roles.rf3_x_suppressed_by_rf9) || lt2_rf1_x_active || lf4_rf2_x_active;",
    "outputs.buttonR = inputs.rf6;",
    "outputs.buttonL = inputs.lt1 || inputs.lt3;",
    "outputs.triggerRDigital = inputs.rf16 || inputs.lt3;",
    "outputs.rightStickRight = inputs.rt4;",
    "outputs.rightStickUp = inputs.rt5;",
    "outputs.dpadUp = inputs.rt5;",
    "outputs.dpadRight = inputs.rt4;",
    '#include "modes/UltimateRuntimeConfigInterpreter.hpp"',
    "SelectRuntimeTableId(",
    "ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)",
    "LookupRuntimeTable(runtime_config, active_table_id)",
    "LookupRuntimeStickPoint(runtime_config, center_table_id, kDirectionFiveIndex)",
    "ApplyTableAnalogOutput(runtime_config, active_table_id, directions.x, directions.y, outputs);",
    "ApplyDirectionPlusAOverride(runtime_config, roles, outputs);",
    "ApplyZAirdodgeOverride(runtime_config, effective_directions, outputs);",
    "ApplyHardUpBOverride(effective_directions, outputs);",
    "ApplyRF3VerticalCStickDiagonalOverride(inputs, effective_directions, directions, outputs);",
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

    return case_id, category


def validate_direct_cstick_suppression_cases(cases_by_id: dict[str, dict[str, Any]]) -> None:
    for case_id, (submode_button, primary_button, c_stick_button, right_stick_direction) in C_STICK_SUPPRESSION_DIRECT_CASES.items():
        case = cases_by_id.get(case_id)
        if case is None:
            fail(f"missing direct C-stick suppression case: {case_id}")
        if case.get("category") != "c_stick_suppression":
            fail(f"{case_id}.category must be c_stick_suppression")

        input_buttons = set(require_string_list(case.get("input_buttons"), f"{case_id}.input_buttons"))
        expected_input_buttons = {submode_button, primary_button, c_stick_button}
        if input_buttons != expected_input_buttons:
            fail(
                f"{case_id}.input_buttons must be exactly "
                + ", ".join(sorted(expected_input_buttons))
                + f"; got {', '.join(sorted(input_buttons))}"
            )

        expected = case.get("expected")
        if not isinstance(expected, dict):
            fail(f"{case_id}.expected must be object")
        digital_buttons = require_string_list(expected.get("digital_buttons"), f"{case_id}.expected.digital_buttons")
        suppressed_buttons = require_string_list(expected.get("suppressed_buttons"), f"{case_id}.expected.suppressed_buttons")
        if "X" in digital_buttons:
            fail(f"{case_id}.expected.digital_buttons must not include X")
        if "X" not in suppressed_buttons:
            fail(f"{case_id}.expected.suppressed_buttons must include X")

        effective_direction = expected.get("effective_direction")
        if not isinstance(effective_direction, dict):
            fail(f"{case_id}.expected.effective_direction must be object")
        if primary_button == "RF2" and effective_direction.get("up") is True:
            fail(f"{case_id}.expected.effective_direction.up must not be true from LF4+RF2")

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
        "Docs/fixture/checker-only evaluator update",
        "Firmware source implementation is not claimed",
        "No generated config.",
        "No runtime-loaded config.",
        "No serial writing.",
        "No new hardware claim.",
        "No Senscope browser app semantic claim.",
        "Cases are representative, not exhaustive.",
        "hardware validation result",
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
    if payload.get("source_status") != "gfw3_requested_expected_behavior_cases":
        fail("source_status must be gfw3_requested_expected_behavior_cases")
    if payload.get("hardware_status") != "not_new_hardware_result":
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


def validate_sources(source: str, spec_fixture: str, spec_doc: str) -> None:
    for anchor in SOURCE_ANCHORS:
        if anchor not in source:
            fail(f"runtime source missing anchor: {anchor}")
    for anchor in (
        '"schema_name": "glyph_gfw3_runtime_remap_rework_spec"',
        '"hardware_status": "not_hardware_validated"',
        '"firmware_implementation_status": "not_yet_claimed"',
        '"RF6":',
        '"RT1_RF4":',
    ):
        if anchor not in spec_fixture:
            fail(f"GFW3 spec fixture missing anchor: {anchor}")
    for phrase in (
        "firmware implementation not yet claimed",
        "hardware validation not claimed",
        "RF9 full-null mode nulls both left stick and right stick inputs",
        "RF9 base-RF3-X suppression mode suppresses base RF3 X",
        "does not full-null left stick or right stick/C-stick output",
        "LF4 overrides LT2 behavior when both are held",
    ):
        if phrase not in spec_doc:
            fail(f"GFW3 spec doc missing anchor phrase: {phrase}")


def main() -> int:
    try:
        source = read_text(SOURCE_PATH)
        spec_fixture = read_text(REPO_ROOT / "docs/calibration/fixtures/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.json")
        spec_doc = read_text(REPO_ROOT / "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md")
        doc = read_text(DOC_PATH)
        payload, duplicate_keys = load_json(FIXTURE_PATH)
        validate_sources(source, spec_fixture, spec_doc)
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
