#!/usr/bin/env python3
"""Validate friend LT5/LF5 Up runtime semantics by source inspection."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
ULTIMATE_HEADER_PATH = REPO_ROOT / "include" / "modes" / "Ultimate.hpp"
CONFIG_SOURCE_PATH = REPO_ROOT / "config" / "glyph" / "common" / "src" / "config.cpp"


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


def require_snippets(text: str, snippets: tuple[str, ...], label: str) -> None:
    for snippet in snippets:
        if snippet not in text:
            raise AssertionError(f"{label}_missing:{snippet}")


def main() -> int:
    try:
        source = ULTIMATE_SOURCE_PATH.read_text(encoding="utf-8")
        header = ULTIMATE_HEADER_PATH.read_text(encoding="utf-8")
        config_source = CONFIG_SOURCE_PATH.read_text(encoding="utf-8")
        handle_socd_body = find_function_body(source, "Ultimate::HandleSocd")
        direction_body = find_function_body(source, "ResolveEffectiveDirections")
        xy_override_body = find_function_body(source, "ApplyFriendProfile3XYModifierOverrides")
        setup_body = find_function_body(config_source, "setup")
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    except AssertionError as exc:
        return fail(str(exc))

    try:
        require_snippets(
            header,
            (
                "void HandleSocd(InputState &inputs);",
                "socd::SocdState _friend_ultimate_socd_states[10] = {};",
            ),
            "ultimate_header",
        )
        require_snippets(
            handle_socd_body,
            (
                "pair.button_dir1 == BTN_LF5",
                "pair.button_dir2 == BTN_LF2",
                "pair.socd_type == SOCD_2IP",
                "button_dir1 = BTN_LT5;",
                "socd::second_input_priority(",
                "_friend_ultimate_socd_states[i]",
            ),
            "lt5_socd_override",
        )
        require_snippets(
            direction_body,
            (
                "const bool proper_up_active = inputs.lt5;",
                "const bool auxiliary_up_active = inputs.lf5 || inputs.rf6;",
                "state.force_up_active = false;",
                "state.up = proper_up_active || (auxiliary_up_active && !inputs.lf2);",
                "state.down = inputs.lf2;",
            ),
            "effective_directions",
        )
        require_snippets(
            xy_override_body,
            (
                "if (roles.x1_active)",
                "outputs.leftStickX = ApplyFriendProfile3AxisMagnitude(x_axis, kFriendProfile3X1Magnitude);",
                "if (roles.y1_active)",
                "outputs.leftStickY = ApplyFriendProfile3AxisMagnitude(y_axis, kFriendProfile3Y1Magnitude);",
            ),
            "xy_override",
        )
        require_snippets(
            source,
            (
                "constexpr uint8_t kFriendProfile3X1Magnitude = 30;",
                "constexpr uint8_t kFriendProfile3Y1Magnitude = 28;",
                "constexpr int8_t kFriendProfile3Tilt2FlipperXOffsetForRight = -59;",
                "constexpr uint8_t kFriendProfile3Tilt2FlipperYMagnitude = 40;",
                "state.tilt1_effective = inputs.rf4;",
                "state.tilt2_effective = inputs.rf3;",
                "state.tilt3_effective = inputs.rf4 && inputs.rf3;",
                "ApplyFriendProfile3Tilt2FlipperOverride(roles, directions.x, directions.y, outputs);",
                "ApplyFriendProfile3XYModifierOverrides(roles, directions.x, directions.y, outputs);",
            ),
            "runtime_preservation",
        )
        require_snippets(
            setup_body,
            (
                "ApplyFriendDefaultProfileOnce(config);",
                "persistence.LoadConfig(config)",
            ),
            "one_shot_profile",
        )
    except AssertionError as exc:
        return fail(str(exc))

    if "state.force_up_active = inputs.lf5 || inputs.lt5 || inputs.rf6;" in direction_body:
        return fail("old_force_up_aggregation_present")
    if "state.down = inputs.lf2 && !state.force_up_active;" in direction_body:
        return fail("down_still_suppressed_by_force_up")
    if re.search(r"force_up_active\s*=.*inputs\.lf5", direction_body):
        return fail("lf5_in_force_up_condition")
    if re.search(r"force_up_active\s*=.*inputs\.lt5", direction_body):
        return fail("lt5_in_force_up_condition")
    if re.search(r"force_up_active\s*=.*inputs\.rf6", direction_body):
        return fail("rf6_in_force_up_condition")
    if re.search(r"state\.down\s*=.*!", direction_body):
        return fail("down_uses_negated_force_or_up_condition")

    helper_call_index = setup_body.find("ApplyFriendDefaultProfileOnce(config);")
    load_index = setup_body.find("persistence.LoadConfig(config)")
    if helper_call_index < 0 or load_index < 0 or helper_call_index > load_index:
        return fail("one_shot_default_profile_not_before_load")

    print("status=PASS")
    print("target=friend_lt5_lf5_up_semantics")
    print("lt5_socd_2ip_source_helper=true")
    print("lf5_force_up_over_down=false")
    print("lf5_modifier_compatible_up_path=true")
    print("one_shot_default_profile_preserved=true")
    print("x1_y1_tilt_tilt2_preserved=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
