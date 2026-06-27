#!/usr/bin/env python3
"""Validate the final friend-specific Faifra Profile 3 layout."""

from __future__ import annotations

import re
from pathlib import Path

from extract_glyph_identity_runtime_tables import TableExtractionError, load_source_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
OVERRIDES_PATH = REPO_ROOT / "config" / "glyph" / "common" / "include" / "glyph_overrides.hpp"
CONFIG_PATH = REPO_ROOT / "config" / "glyph" / "common" / "src" / "config.cpp"
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
HEADER_PATH = REPO_ROOT / "include" / "modes" / "Ultimate.hpp"
WIP_DOC_PATH = REPO_ROOT / "docs" / "friend-profile3-wip.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "calibration" / "friend_profile3_final_faifra_layout_handoff.md"
OLD_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json"
)

OLD_MARKERS = (
    "/friend_profile3_default_applied.flag",
    "/friend_profile3_rf12_force_up_smash_applied.flag",
)
EXPECTED_MARKER = "/friend_profile3_final_faifra_layout_applied.flag"


EXPECTED_TABLE_POINTS: dict[str, tuple[int, int]] = {
    "X1": (158, 195),
    "Y1": (195, 156),
    "Tilt1": (187, 167),
    "Tilt2": (69, 168),
    "Tilt3": (164, 172),
}


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


def find_field_block(source: str, field_name: str) -> str:
    marker = f".{field_name}"
    marker_index = source.find(marker)
    if marker_index < 0:
        raise ValueError(f"missing field block: {field_name}")
    open_index = source.find("{", marker_index)
    if open_index < 0:
        raise ValueError(f"missing opening brace for field block: {field_name}")
    return find_balanced_block(source, open_index)


def parse_int_field(block: str, field_name: str) -> int:
    match = re.search(rf"\.{re.escape(field_name)}\s*=\s*(\d+)", block)
    if match is None:
        raise ValueError(f"missing integer field: {field_name}")
    return int(match.group(1))


def parse_game_mode_blocks(source: str) -> list[str]:
    game_modes_block = find_field_block(source, "game_mode_configs")
    blocks: list[str] = []
    search_index = 0
    marker = "GameModeConfig"
    while True:
        marker_index = game_modes_block.find(marker, search_index)
        if marker_index < 0:
            break
        open_index = game_modes_block.find("{", marker_index)
        if open_index < 0:
            raise ValueError("malformed GameModeConfig initializer")
        block = find_balanced_block(game_modes_block, open_index)
        blocks.append(block)
        search_index = open_index + len(block) + 2
    return blocks


def parse_button_remaps(block: str) -> dict[str, str]:
    remaps_block = find_field_block(block, "button_remapping")
    pattern = re.compile(
        r"ButtonRemap\s*\{\s*"
        r"\.physical_button\s*=\s*(BTN_[A-Z0-9]+)"
        r"\s*,\s*\.activates\s*=\s*(BTN_[A-Z0-9_]+)"
        r"\s*\}",
        re.DOTALL,
    )
    return {match.group(1): match.group(2) for match in pattern.finditer(remaps_block)}


def count_tokens(block: str, field_name: str, prefix: str) -> int:
    field_block = find_field_block(block, field_name)
    return len(re.findall(rf"\b{re.escape(prefix)}[A-Z0-9_]+\b", field_block))


def validate_default_profile() -> None:
    source = OVERRIDES_PATH.read_text(encoding="utf-8")
    blocks = parse_game_mode_blocks(source)
    expected_config_count = parse_int_field(source, "game_mode_configs_count")
    if len(blocks) != expected_config_count:
        raise AssertionError(f"game_mode_configs_count_mismatch:{len(blocks)}!={expected_config_count}")
    if not blocks or ".mode_id = MODE_ULTIMATE" not in blocks[0]:
        raise AssertionError("mode_ultimate_not_first_default_profile")

    ultimate = blocks[0]
    remaps = parse_button_remaps(ultimate)
    if remaps.get("BTN_LT5") != "BTN_LT5":
        raise AssertionError("lt5_not_available_as_proper_up")
    if remaps.get("BTN_RF6") != "BTN_LT5":
        raise AssertionError("rf6_not_profile_mapped_to_lt5")
    if remaps.get("BTN_RF6") == "BTN_RF6":
        raise AssertionError("rf6_still_identity_mapped")

    expected_counts = {
        "socd_pairs_count": count_tokens(ultimate, "socd_pairs", "SOCD_"),
        "button_remapping_count": len(remaps),
        "applicable_backends_count": count_tokens(ultimate, "applicable_backends", "COMMS_BACKEND_"),
        "menu_button_icon_count": count_tokens(ultimate, "menu_button_icon", "OUT_"),
    }
    for field_name, expected in expected_counts.items():
        actual = parse_int_field(ultimate, field_name)
        if actual != expected:
            raise AssertionError(f"{field_name}_mismatch:{actual}!={expected}")


def validate_one_shot() -> None:
    source = CONFIG_PATH.read_text(encoding="utf-8")
    helper_body = find_function_body(source, "ApplyFriendDefaultProfileOnce")
    setup_body = find_function_body(source, "setup")

    if EXPECTED_MARKER not in source:
        raise AssertionError("final_marker_missing")
    for old_marker in OLD_MARKERS:
        if old_marker in source:
            raise AssertionError(f"old_marker_still_active:{old_marker}")
    for snippet in (
        "LittleFS.exists(kFriendDefaultProfileAppliedMarker)",
        "persistence.SaveConfig(config)",
        "LittleFS.open(kFriendDefaultProfileAppliedMarker, \"w\")",
        "friend_profile3_final_faifra_layout_applied",
    ):
        if snippet not in helper_body and snippet not in source:
            raise AssertionError(f"one_shot_missing:{snippet}")

    helper_index = setup_body.find("ApplyFriendDefaultProfileOnce(config);")
    load_index = setup_body.find("persistence.LoadConfig(config)")
    if helper_index < 0 or load_index < 0 or helper_index > load_index:
        raise AssertionError("one_shot_not_before_load")

    fallback_pattern = re.compile(
        r"if\s*\(\s*!\s*persistence\.LoadConfig\s*\(\s*config\s*\)\s*\)\s*\{\s*"
        r"persistence\.SaveConfig\s*\(\s*config\s*\)\s*;\s*"
        r"\}",
        re.DOTALL,
    )
    setup_without_fallback = fallback_pattern.sub("", setup_body)
    if "persistence.SaveConfig(config)" in setup_without_fallback:
        raise AssertionError("setup_contains_unconditional_profile_save")
    if len(re.findall(r"\bpersistence\.SaveConfig\s*\(\s*config\s*\)", source)) != 2:
        raise AssertionError("unexpected_save_config_call_count")


def require_snippets(text: str, snippets: tuple[str, ...], label: str) -> None:
    for snippet in snippets:
        if snippet not in text:
            raise AssertionError(f"{label}_missing:{snippet}")


def reject_patterns(text: str, patterns: tuple[str, ...], label: str) -> None:
    for pattern in patterns:
        if re.search(pattern, text):
            raise AssertionError(f"{label}_rejected:{pattern}")


def validate_runtime() -> None:
    source = ULTIMATE_PATH.read_text(encoding="utf-8")
    header = HEADER_PATH.read_text(encoding="utf-8")
    handle_socd_body = find_function_body(source, "Ultimate::HandleSocd")
    direction_body = find_function_body(source, "ResolveEffectiveDirections")
    role_body = find_function_body(source, "ResolveRoleState")
    digital_body = find_function_body(source, "ApplyDigitalButtonOutputs")
    digital_direction_body = find_function_body(source, "ApplyDigitalDirectionOutputs")
    analog_body = find_function_body(source, "Ultimate::UpdateAnalogOutputs")

    require_snippets(
        header,
        (
            "void HandleSocd(InputState &inputs);",
            "socd::SocdState _friend_ultimate_socd_states[10] = {};",
        ),
        "header",
    )
    require_snippets(
        handle_socd_body,
        (
            "pair.button_dir1 == BTN_LF5",
            "pair.button_dir2 == BTN_LF2",
            "pair.socd_type == SOCD_2IP",
            "button_dir1 = BTN_LT5;",
            "socd::second_input_priority(",
        ),
        "lt5_socd",
    )
    require_snippets(
        direction_body,
        (
            "const bool proper_up_active = inputs.lt5;",
            "const bool auxiliary_up_active = inputs.lf5;",
            "state.up = proper_up_active || (auxiliary_up_active && !inputs.lf2);",
            "state.down = inputs.lf2;",
        ),
        "directions",
    )
    reject_patterns(
        direction_body,
        (
            r"auxiliary_up_active\s*=.*inputs\.rf6",
            r"force_up_active\s*=.*inputs\.(lf5|lt5|rf6)",
            r"state\.down\s*=.*!",
        ),
        "directions",
    )
    require_snippets(
        role_body,
        (
            "state.x1_active = inputs.lt4;",
            "state.x2_active = inputs.rf15;",
            "state.y1_active = inputs.lt3;",
            "state.lt2_force_up_smash_active = inputs.lt2;",
            "state.direction_plus_a_active = state.lt2_force_up_smash_active;",
            "state.direction_plus_a_force_up = state.lt2_force_up_smash_active;",
            "state.tilt1_effective = inputs.rf4;",
            "state.tilt2_effective = inputs.rf3;",
            "state.tilt3_effective = inputs.rf4 && inputs.rf3;",
        ),
        "roles",
    )
    reject_patterns(
        role_body,
        (
            r"x2_active\s*=.*inputs\.rf12",
            r"force_up_smash_active\s*=\s*inputs\.rf12",
            r"direction_plus_a_(?:active|force_up)\s*=.*rf12",
        ),
        "roles",
    )
    require_snippets(
        digital_body,
        (
            "outputs.a = inputs.rt1 || inputs.rf12 || inputs.rf10 || roles.lt2_force_up_smash_active;",
            "outputs.b = inputs.rf1 || inputs.rf12;",
            "outputs.x = inputs.rf7;",
            "outputs.y = inputs.rf2;",
            "outputs.buttonL = inputs.lf4 || inputs.rf10;",
            "outputs.buttonR = inputs.lt1;",
            "outputs.triggerRDigital = inputs.rf10 || inputs.lf8;",
            "outputs.start = inputs.mb7;",
        ),
        "digital_outputs",
    )
    reject_patterns(
        digital_body,
        (
            r"outputs\.a\s*=.*inputs\.lt2",
            r"outputs\.b\s*=.*inputs\.lt2",
            r"triggerRDigital\s*=.*inputs\.rf16",
            r"outputs\.start\s*=.*inputs\.rf16",
        ),
        "digital_outputs",
    )
    require_snippets(
        digital_direction_body,
        (
            "if (roles.lt2_force_up_smash_active)",
            "outputs.leftStickUp = true;",
        ),
        "digital_force_up",
    )
    require_snippets(
        analog_body,
        (
            "effective_directions.down, // Down (LF2, SOCD-governed against LT5)",
            "effective_directions.up, // Up (LT5 proper, LF5 auxiliary)",
            "ApplyDirectionPlusAOverride(runtime_config, roles, outputs);",
            "ApplyFriendProfile3Tilt2FlipperOverride(roles, directions.x, directions.y, outputs);",
            "ApplyFriendProfile3XYModifierOverrides(roles, directions.x, directions.y, outputs);",
            "ApplyFriendProfileCStickRawOutputs(roles.mode_active, directions, outputs);",
        ),
        "analog_preservation",
    )


def validate_tables() -> None:
    tables = load_source_tables(ULTIMATE_PATH)
    for table_name, expected_point in EXPECTED_TABLE_POINTS.items():
        if tables.get(table_name, ())[8] != expected_point:
            raise AssertionError(f"table_9_mismatch:{table_name}")
    if tables.get("X1", ())[8] != (158, 195) or tables.get("Y1", ())[8] != (195, 156):
        raise AssertionError("x1_y1_up_right_outputs_drifted")


def validate_docs() -> None:
    wip = WIP_DOC_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")
    require_snippets(
        wip,
        (
            "RF6 duplicates LT5 proper SOCD Up",
            "| lt2 | forced Up Smash (Up + A) |",
            "| rf12 | a+b |",
            "| lf8 | r |",
            "| rf16 | unassigned / no standalone runtime role |",
            "| mb7 | start |",
            "Ultimate is first/default profile",
            "deviates from the previous physical/logical identity fixture",
        ),
        "wip_doc",
    )
    require_snippets(
        handoff,
        (
            "duplicate LT5 proper SOCD Up to RF6",
            "swap LT2 AB with RF12 Up+A",
            "move R from RF16 to LF8",
            "make Ultimate first/default profile",
            "Profile-owned",
            "Runtime-owned",
            EXPECTED_MARKER,
            "Hardware retest is required",
            "must not be merged into `configurator`",
        ),
        "handoff_doc",
    )


def validate_identity_fixture_retired() -> None:
    if not OLD_FIXTURE_PATH.exists():
        raise AssertionError("historical_identity_fixture_missing")
    checker = (REPO_ROOT / "tools" / "check_friend_ultimate_default_profile_matches_fixture.py").read_text(
        encoding="utf-8"
    )
    require_snippets(
        checker,
        (
            "identity_fixture_exact_match=false",
            "friend_final_layout_deviates_from_fixture=true",
        ),
        "identity_fixture_checker",
    )


def main() -> int:
    try:
        validate_default_profile()
        validate_one_shot()
        validate_runtime()
        validate_tables()
        validate_docs()
        validate_identity_fixture_retired()
    except (OSError, ValueError, AssertionError, TableExtractionError) as exc:
        return fail(str(exc))

    print("status=PASS")
    print("target=friend_profile3_final_faifra_layout")
    print("mode_ultimate_first=true")
    print("rf6_profile_activates=BTN_LT5")
    print(f"one_shot_marker={EXPECTED_MARKER}")
    print("lt2=forced_up_plus_a")
    print("rf12=a_plus_b")
    print("lf8=triggerRDigital")
    print("rf16_r=false")
    print("rf16_start=false")
    print("mb7=start")
    print("rf12_x2=false")
    print("rf15_x2=true")
    print("identity_fixture_exact_match=false")
    print("friend_final_layout_deviates_from_fixture=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
