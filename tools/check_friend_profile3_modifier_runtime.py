#!/usr/bin/env python3
"""Validate friend Profile 3 modifier runtime wiring."""

from __future__ import annotations

import re
from pathlib import Path

from extract_glyph_identity_runtime_tables import TableExtractionError, load_source_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
TABLE_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
CONFIG_SOURCE_PATH = REPO_ROOT / "config" / "glyph" / "common" / "src" / "config.cpp"
HANDOFF_PATH = REPO_ROOT / "docs" / "calibration" / "friend_profile3_modifier_runtime_fix_handoff.md"
TILT2_HANDOFF_PATH = REPO_ROOT / "docs" / "calibration" / "friend_profile3_tilt2_flipper_fix_handoff.md"
WIP_DOC_PATH = REPO_ROOT / "docs" / "friend-profile3-wip.md"

BEGIN_MARKER = "// Senscope Glyph Smash Box runtime begin"
END_MARKER = "// Senscope Glyph Smash Box runtime end"

EXPECTED_X1_TABLE = (
    (98, 51), (128, 51), (158, 51),
    (98, 128), (128, 128), (158, 128),
    (98, 195), (128, 195), (158, 195),
)
EXPECTED_Y1_TABLE = (
    (61, 100), (128, 100), (195, 100),
    (61, 128), (128, 128), (195, 128),
    (61, 156), (128, 156), (195, 156),
)
EXPECTED_TILT1_TABLE = (
    (69, 87), (128, 87), (187, 87),
    (69, 128), (128, 128), (187, 128),
    (69, 167), (128, 167), (187, 167),
)
EXPECTED_TILT2_TABLE = (
    (187, 88), (128, 88), (69, 88),
    (187, 128), (128, 128), (69, 128),
    (187, 168), (128, 168), (69, 168),
)


def fail(message: str) -> int:
    print("status=FAIL")
    print(f"failure={message}")
    return 1


def find_balanced_block(text: str, open_brace_index: int) -> str:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index + 1 : index]

    raise ValueError("unclosed C++ block")


def find_function_body(source: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*\([^)]*\)\s*\{{", source)
    if match is None:
        raise ValueError(f"missing function: {name}")
    open_index = source.find("{", match.start())
    return find_balanced_block(source, open_index)


def marker_block(text: str) -> str:
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise ValueError("expected exactly one friend runtime marker pair")
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER, begin)
    return text[begin : end + len(END_MARKER)]


def validate_tables() -> None:
    tables = load_source_tables(TABLE_SOURCE_PATH)
    if tables.get("X1") != EXPECTED_X1_TABLE:
        raise AssertionError("x1_table_not_axis_split")
    if tables.get("Y1") != EXPECTED_Y1_TABLE:
        raise AssertionError("y1_table_not_axis_split")
    if tables.get("X1") == tables.get("Y1"):
        raise AssertionError("x1_y1_tables_collapsed")
    if tables["X1"][8] != (158, 195):
        raise AssertionError("x1_up_right_must_preserve_base_y")
    if tables["Y1"][8] != (195, 156):
        raise AssertionError("y1_up_right_must_preserve_base_x")
    if tables.get("Tilt1") != EXPECTED_TILT1_TABLE:
        raise AssertionError("tilt1_table_drifted")
    if tables.get("Tilt2") != EXPECTED_TILT2_TABLE:
        raise AssertionError("tilt2_table_drifted")


def validate_runtime_source(source: str) -> None:
    required_snippets = (
        "state.x1_active = inputs.lt4;",
        "state.y1_active = inputs.lt3;",
        "state.rf4_layer_flipper_active = false;",
        "state.tilt1_effective = inputs.rf4;",
        "state.tilt2_effective = inputs.rf3;",
        "state.tilt3_effective = inputs.rf4 && inputs.rf3;",
        "constexpr uint8_t kFriendProfile3X1Magnitude = 30;",
        "constexpr uint8_t kFriendProfile3Y1Magnitude = 28;",
        "constexpr int8_t kFriendProfile3Tilt2FlipperXOffsetForRight = -59;",
        "constexpr uint8_t kFriendProfile3Tilt2FlipperYMagnitude = 40;",
        "ApplyFriendProfile3XYModifierOverrides(roles, directions.x, directions.y, outputs);",
        "ApplyFriendProfile3Tilt2FlipperOverride(roles, directions.x, directions.y, outputs);",
        "RF4 is Tilt1, RF3 is Tilt2/flipper, and RF4+RF3 is",
        "&kSourceOwnedCurrentBaselineRuntimeConfig",
    )
    for snippet in required_snippets:
        if snippet not in source:
            raise AssertionError(f"missing_runtime_snippet:{snippet}")
    if "no source-grounded flipper binding was provided" in source:
        raise AssertionError("stale_unresolved_flipper_runtime_comment")

    helper_body = find_function_body(source, "ApplyFriendProfile3XYModifierOverrides")
    if "if (roles.x1_active)" not in helper_body or "outputs.leftStickX" not in helper_body:
        raise AssertionError("x1_runtime_branch_missing")
    if "if (roles.y1_active)" not in helper_body or "outputs.leftStickY" not in helper_body:
        raise AssertionError("y1_runtime_branch_missing")
    x1_branch = helper_body.split("if (roles.x1_active)", 1)[1].split("if (roles.y1_active)", 1)[0]
    y1_branch = helper_body.split("if (roles.y1_active)", 1)[1]
    if "outputs.leftStickY" in x1_branch:
        raise AssertionError("x1_branch_must_not_assign_y")
    if "outputs.leftStickX" in y1_branch:
        raise AssertionError("y1_branch_must_not_assign_x")

    raw_offset_body = find_function_body(source, "ApplyFriendProfile3RawOffset")
    for snippet in (
        "const int raw_value = ANALOG_STICK_NEUTRAL + offset;",
        "return static_cast<uint8_t>(raw_value);",
    ):
        if snippet not in raw_offset_body:
            raise AssertionError(f"raw_offset_math_not_explicit:{snippet}")
    if re.search(r"uint8_t\s+raw_value\s*=", raw_offset_body):
        raise AssertionError("axis_math_must_not_accumulate_in_uint8")

    signed_axis_body = find_function_body(source, "ApplyFriendProfile3SignedAxisOffset")
    for snippet in (
        "const int signed_axis = ClampFriendProfile3Axis(axis);",
        "return ApplyFriendProfile3RawOffset(signed_axis * static_cast<int>(offset_for_positive_axis));",
    ):
        if snippet not in signed_axis_body:
            raise AssertionError(f"signed_axis_math_not_explicit:{snippet}")

    tilt2_body = find_function_body(source, "ApplyFriendProfile3Tilt2FlipperOverride")
    for snippet in (
        "!roles.mode_active",
        "!roles.x1_active",
        "!roles.y1_active",
        "!roles.tilt1_effective",
        "roles.tilt2_effective",
        "!roles.tilt3_effective",
        "outputs.leftStickX = ApplyFriendProfile3SignedAxisOffset(",
        "kFriendProfile3Tilt2FlipperXOffsetForRight",
        "outputs.leftStickY = ApplyFriendProfile3AxisMagnitude(",
        "kFriendProfile3Tilt2FlipperYMagnitude",
    ):
        if snippet not in tilt2_body:
            raise AssertionError(f"tilt2_flipper_runtime_missing:{snippet}")

    runtime_block = marker_block(source)
    if re.search(r"outputs\.leftStick[XY]\s*=\s*[^;\n]*inputs\.rf[34]", runtime_block):
        raise AssertionError("raw_rf3_rf4_left_stick_bypass")
    if "outputs.leftStickX = ApplyFriendProfile3AxisMagnitude(x_axis, kFriendProfile3X1Magnitude);" not in helper_body:
        raise AssertionError("x1_magnitude_assignment_drifted")
    if "outputs.leftStickY = ApplyFriendProfile3AxisMagnitude(y_axis, kFriendProfile3Y1Magnitude);" not in helper_body:
        raise AssertionError("y1_magnitude_assignment_drifted")


def validate_one_shot_default_profile() -> None:
    source = CONFIG_SOURCE_PATH.read_text(encoding="utf-8")
    helper_body = find_function_body(source, "ApplyFriendDefaultProfileOnce")
    setup_body = find_function_body(source, "setup")
    required_snippets = (
        "/friend_profile3_default_applied.flag",
        "LittleFS.exists(kFriendDefaultProfileAppliedMarker)",
        "persistence.SaveConfig(config)",
        "LittleFS.open(kFriendDefaultProfileAppliedMarker, \"w\")",
    )
    for snippet in required_snippets:
        if snippet not in helper_body and snippet not in source:
            raise AssertionError(f"one_shot_missing:{snippet}")
    if "ApplyFriendDefaultProfileOnce(config);" not in setup_body:
        raise AssertionError("setup_missing_one_shot_default_profile_call")
    if setup_body.find("ApplyFriendDefaultProfileOnce(config);") > setup_body.find("persistence.LoadConfig(config)"):
        raise AssertionError("one_shot_default_profile_must_run_before_load")


def validate_handoff_doc() -> None:
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for snippet in (
        "no modifier: 67 67",
        "Faifra's observed miniscreen/calibration values are center-relative/origo",
        "offsets, not raw absolute bytes",
        "miniscreen/display_x = raw_x - 128",
        "miniscreen/display_y = raw_y - 128",
        "raw (187, 167) | 59 39",
        "raw (158, 195) | 30 67",
        "raw (195, 156) | 67 28",
        "raw (158, 156) | 30 28",
        "LT4 -> X1",
        "LT3 -> Y1",
        "RF4 -> Tilt",
        "RF3 -> Tilt2",
        "RF4+RF3 -> Tilt3",
        "| no modifier + up/right | raw (195, 195) | 67 67 |",
        "| X1 + up/right | raw (158, 195) | 30 67 |",
        "| Y1 + up/right | raw (195, 156) | 67 28 |",
        "| X1+Y1 + up/right | raw (158, 156) | 30 28 |",
        "| RF4/Tilt1 + up/right | raw (187, 167) | 59 39 |",
        "| RF3/Tilt2/flipper + up/right | raw (69, 168) | -59 40 |",
        "| RF3/Tilt2/flipper + left/up | raw (187, 168) | 59 40 |",
        "The raw values are the firmware output expectations",
        "values are the hardware retest expectations",
        "Tilt2 X: `197`",
        "signed offset `-59`",
        "Tilt2 Y Up: `40`",
        "Tilt2 Y Down: `40`",
        "The previous unresolved status was wrong",
        "RF4+RF3 selects",
        "R remains pending",
        "hardware retest is required",
        "must not be merged into configurator",
    ):
        if snippet not in text:
            raise AssertionError(f"handoff_missing:{snippet}")
    if "Flipper remains unresolved" in text:
        raise AssertionError("handoff_still_marks_flipper_unresolved")
    if "-69 40" in text and "should not recur" not in text:
        raise AssertionError("handoff_allows_bad_tilt2_flipper_output")

    tilt2_text = TILT2_HANDOFF_PATH.read_text(encoding="utf-8")
    for snippet in (
        "previous unresolved flipper status was wrong",
        "RF3 | Tilt2/flipper",
        "Tilt2 X: `197`",
        "`197` is `-59`",
        "RF3/Tilt2/flipper + up/right | raw (69, 168) | -59 40",
        "RF3/Tilt2/flipper + left/up | raw (187, 168) | 59 40",
        "RF4+RF3/Tilt3 + up/right | raw (164, 172) | 36 44",
        "The prior bad field result `left+up with flipper -> -69 40` should not recur",
        "R Status",
        "Pending",
        "must not be merged into",
        "Hardware retest is required",
    ):
        if snippet not in tilt2_text:
            raise AssertionError(f"tilt2_handoff_missing:{snippet}")


def validate_wip_doc_display_note() -> None:
    text = WIP_DOC_PATH.read_text(encoding="utf-8")
    for snippet in (
        "absolute raw coordinates with center `(128, 128)`",
        "not Faifra's miniscreen/calibration display",
        "values. The observed miniscreen convention",
        "center-relative/origo display",
        "display_x = raw_x - 128",
        "display_y = raw_y - 128",
        "raw `(187, 167)` displays as `59 39`",
        "raw `(158, 195)` displays as `30 67`",
        "raw `(195, 156)` displays as `67 28`",
        "raw `(158, 156)` displays as",
        "`30 28`",
        "Tilt2 X `197`",
        "signed offset `-59`",
        "RF3/Tilt2",
        "raw `(69, 168)` displays as `-59 40`",
        "left/up raw",
        "displays as `59 40`",
    ):
        if snippet not in text:
            raise AssertionError(f"wip_doc_missing:{snippet}")
    if "Tilt2 X: 197 was resolved as absolute right-side raw X" in text:
        raise AssertionError("wip_doc_still_uses_bad_tilt2_absolute_interpretation")


def main() -> int:
    try:
        source = ULTIMATE_SOURCE_PATH.read_text(encoding="utf-8")
        validate_tables()
        validate_runtime_source(source)
        validate_one_shot_default_profile()
        validate_handoff_doc()
        validate_wip_doc_display_note()
    except (OSError, ValueError, AssertionError, TableExtractionError) as exc:
        return fail(str(exc))

    print("status=PASS")
    print(f"source={ULTIMATE_SOURCE_PATH.relative_to(REPO_ROOT)}")
    print("x1_input=LT4")
    print("y1_input=LT3")
    print("tilt_input=RF4")
    print("tilt2_input=RF3")
    print("flipper_status=implemented_source_grounded_tilt2")
    print("x1_up_right_raw=158,195")
    print("y1_up_right_raw=195,156")
    print("x1_y1_up_right_raw=158,156")
    print("tilt2_flipper_up_right_raw=69,168")
    print("tilt2_flipper_left_up_raw=187,168")
    print("tilt3_rf4_rf3_up_right_raw=164,172")
    print("tilt1_constants_preserved=true")
    print("tilt2_flipper_corrected=true")
    print("one_shot_default_profile_preserved=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
