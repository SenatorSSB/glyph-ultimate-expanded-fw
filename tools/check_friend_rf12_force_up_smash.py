#!/usr/bin/env python3
"""Validate friend RF12 forced Up Smash runtime wiring by source inspection."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
ULTIMATE_HEADER_PATH = REPO_ROOT / "include" / "modes" / "Ultimate.hpp"
CONFIG_SOURCE_PATH = REPO_ROOT / "config" / "glyph" / "common" / "src" / "config.cpp"
WIP_DOC_PATH = REPO_ROOT / "docs" / "friend-profile3-wip.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "calibration" / "friend_rf12_force_up_smash_handoff.md"


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
        wip_doc = WIP_DOC_PATH.read_text(encoding="utf-8")
        handoff = HANDOFF_PATH.read_text(encoding="utf-8")

        role_body = find_function_body(source, "ResolveRoleState")
        button_body = find_function_body(source, "ApplyDigitalButtonOutputs")
        digital_direction_body = find_function_body(source, "ApplyDigitalDirectionOutputs")
        direction_plus_a_body = find_function_body(source, "ApplyDirectionPlusAOverride")
        analog_body = find_function_body(source, "Ultimate::UpdateAnalogOutputs")
        effective_direction_body = find_function_body(source, "ResolveEffectiveDirections")
        xy_override_body = find_function_body(source, "ApplyFriendProfile3XYModifierOverrides")
        tilt2_body = find_function_body(source, "ApplyFriendProfile3Tilt2FlipperOverride")
        setup_body = find_function_body(config_source, "setup")
    except (OSError, ValueError) as exc:
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
            role_body,
            (
                "state.x2_active = inputs.rf15;",
                "state.rf12_force_up_smash_active = inputs.rf12;",
                "state.direction_plus_a_active = state.rf12_force_up_smash_active;",
                "state.direction_plus_a_force_up = state.rf12_force_up_smash_active;",
            ),
            "rf12_role",
        )
        require_snippets(
            button_body,
            (
                "outputs.a = inputs.rt1 || inputs.lt2 || inputs.rf10 || roles.rf12_force_up_smash_active;",
                "outputs.b = inputs.rf1 || inputs.lt2;",
                "outputs.triggerRDigital = inputs.rf10 || inputs.rf16;",
                "outputs.start = inputs.mb7;",
            ),
            "digital_outputs",
        )
        require_snippets(
            digital_direction_body,
            (
                "if (roles.rf12_force_up_smash_active)",
                "outputs.leftStickLeft = false;",
                "outputs.leftStickRight = false;",
                "outputs.leftStickDown = false;",
                "outputs.leftStickUp = true;",
            ),
            "digital_force_up",
        )
        require_snippets(
            direction_plus_a_body,
            (
                "if (!roles.direction_plus_a_active)",
                "roles.direction_plus_a_force_up",
                "? RuntimeTableId::Default",
                "roles.direction_plus_a_force_up ? kDirectionEightIndex : kDirectionTwoIndex",
                "outputs.leftStickX = direction_plus_a_point.x;",
                "outputs.leftStickY = direction_plus_a_point.y;",
            ),
            "analog_force_up",
        )
        require_snippets(
            analog_body,
            (
                "ApplyTableAnalogOutput(runtime_config, active_table_id, directions.x, directions.y, outputs);",
                "ApplyDirectionPlusAOverride(runtime_config, roles, outputs);",
                "ApplyFriendProfile3Tilt2FlipperOverride(roles, directions.x, directions.y, outputs);",
                "ApplyFriendProfile3XYModifierOverrides(roles, directions.x, directions.y, outputs);",
            ),
            "analog_preservation",
        )
        require_snippets(
            effective_direction_body,
            (
                "const bool proper_up_active = inputs.lt5;",
                "const bool auxiliary_up_active = inputs.lf5 || inputs.rf6;",
                "state.force_up_active = false;",
                "state.up = proper_up_active || (auxiliary_up_active && !inputs.lf2);",
                "state.down = inputs.lf2;",
            ),
            "lt5_lf5_semantics",
        )
        require_snippets(
            setup_body,
            (
                "ApplyFriendDefaultProfileOnce(config);",
                "persistence.LoadConfig(config)",
            ),
            "one_shot_default_profile",
        )
        require_snippets(
            xy_override_body,
            (
                "if (roles.x1_active)",
                "outputs.leftStickX = ApplyFriendProfile3AxisMagnitude(x_axis, kFriendProfile3X1Magnitude);",
                "if (roles.y1_active)",
                "outputs.leftStickY = ApplyFriendProfile3AxisMagnitude(y_axis, kFriendProfile3Y1Magnitude);",
            ),
            "x1_y1_preservation",
        )
        require_snippets(
            tilt2_body,
            (
                "roles.tilt2_effective",
                "kFriendProfile3Tilt2FlipperXOffsetForRight",
                "kFriendProfile3Tilt2FlipperYMagnitude",
            ),
            "tilt2_flipper_preservation",
        )
        require_snippets(
            source,
            (
                "state.tilt1_effective = inputs.rf4;",
                "state.tilt2_effective = inputs.rf3;",
                "state.tilt3_effective = inputs.rf4 && inputs.rf3;",
            ),
            "tilt_preservation",
        )
        require_snippets(
            wip_doc,
            (
                "| rf12 | forced Up Smash (Up + A) |",
                "| rf15 | x2 |",
                "RF12 is forced Up Smash",
                "remains X2; RF12 no longer participates in X2/Y2 modifier selection",
            ),
            "wip_doc",
        )
        require_snippets(
            handoff,
            (
                "Faifra wants `RF12` to be forced Up Smash",
                "Old RF12 Role",
                "`state.x2_active = inputs.rf15 || inputs.rf12;`",
                "`state.x2_active = inputs.rf15;`",
                "`state.rf12_force_up_smash_active = inputs.rf12;`",
                "A output",
                "Default-table Up",
                "Hardware retest is required",
                "It must not be merged into",
            ),
            "handoff_doc",
        )
    except AssertionError as exc:
        return fail(str(exc))

    if "state.x2_active = inputs.rf15 || inputs.rf12;" in role_body:
        return fail("rf12_still_part_of_x2_active")
    if re.search(r"state\.x2_active\s*=.*inputs\.rf12", role_body):
        return fail("rf12_still_in_x2_expression")
    if re.search(r"outputs\.a\s*=((?!;).)*inputs\.rf12", button_body):
        return fail("rf12_should_reach_a_through_explicit_role")
    if "outputs.start = inputs.rf16;" in source:
        return fail("rf16_must_not_be_double_bound_to_start")

    print("status=PASS")
    print("target=friend_rf12_force_up_smash")
    print("rf12_removed_from_x2=true")
    print("rf15_x2_preserved=true")
    print("rf12_outputs_a=true")
    print("rf12_forces_left_stick_up=true")
    print("lt5_lf5_semantics_preserved=true")
    print("one_shot_default_profile_preserved=true")
    print("x1_y1_tilt2_flipper_preserved=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
