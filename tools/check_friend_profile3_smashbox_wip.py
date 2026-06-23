#!/usr/bin/env python3
"""Validate the friend profile3 Smash Box WIP source-owned firmware fork."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from extract_glyph_identity_runtime_tables import TableExtractionError, load_source_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
ULTIMATE_SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
MATRIX_PATH = REPO_ROOT / "config" / "glyph" / "glyph_mk6" / "include" / "matrix_definition.hpp"
DOC_PATH = REPO_ROOT / "docs" / "friend-profile3-wip.md"

PHYSICAL_BUTTONS = {
    "BTN_LF4", "BTN_LF3", "BTN_LF2", "BTN_LF1", "BTN_LF5", "BTN_LF6", "BTN_LF7",
    "BTN_LT5", "BTN_LT1", "BTN_LT4", "BTN_LT3", "BTN_LT2",
    "BTN_RT1", "BTN_RT5", "BTN_RT4", "BTN_RT3", "BTN_RT2",
    "BTN_RF1", "BTN_RF2", "BTN_RF3", "BTN_RF4", "BTN_RF5", "BTN_RF6", "BTN_RF7",
    "BTN_RF8", "BTN_RF9", "BTN_RF10", "BTN_RF11", "BTN_RF12", "BTN_RF13",
    "BTN_RF15", "BTN_RF16",
}

EXPECTED_TABLES: dict[str, tuple[tuple[int, int], ...]] = {
    "Default": (
        (61, 51), (128, 51), (195, 51),
        (61, 128), (128, 128), (195, 128),
        (61, 195), (128, 195), (195, 195),
    ),
    "ModeDefault": (
        (128, 128), (128, 128), (128, 128),
        (128, 128), (128, 128), (128, 128),
        (128, 128), (128, 128), (128, 128),
    ),
    "X1": (
        (98, 51), (128, 51), (158, 51),
        (98, 128), (128, 128), (158, 128),
        (98, 195), (128, 195), (158, 195),
    ),
    "Y1": (
        (61, 100), (128, 100), (195, 100),
        (61, 128), (128, 128), (195, 128),
        (61, 156), (128, 156), (195, 156),
    ),
    "X2": (
        (81, 81), (128, 81), (175, 81),
        (81, 128), (128, 128), (175, 128),
        (81, 175), (128, 175), (175, 175),
    ),
    "MX1": (
        (92, 92), (128, 92), (164, 92),
        (92, 128), (128, 128), (164, 128),
        (92, 164), (128, 164), (164, 164),
    ),
    "MY1": (
        (92, 92), (128, 92), (164, 92),
        (92, 128), (128, 128), (164, 128),
        (92, 164), (128, 164), (164, 164),
    ),
    "MX2": (
        (71, 71), (128, 71), (185, 71),
        (71, 128), (128, 128), (185, 128),
        (71, 185), (128, 185), (185, 185),
    ),
    "Tilt1": (
        (69, 87), (128, 87), (187, 87),
        (69, 128), (128, 128), (187, 128),
        (69, 167), (128, 167), (187, 167),
    ),
    "Tilt2": (
        (187, 88), (128, 88), (69, 88),
        (187, 128), (128, 128), (69, 128),
        (187, 168), (128, 168), (69, 168),
    ),
    "Tilt3": (
        (92, 83), (128, 83), (164, 83),
        (92, 128), (128, 128), (164, 128),
        (92, 172), (128, 172), (164, 172),
    ),
    "MTilt1": (
        (87, 94), (128, 94), (169, 94),
        (87, 128), (128, 128), (169, 128),
        (87, 162), (128, 162), (169, 162),
    ),
    "MTilt2": (
        (87, 78), (128, 78), (169, 78),
        (87, 128), (128, 128), (169, 128),
        (87, 178), (128, 178), (169, 178),
    ),
    "MTilt3": (
        (101, 101), (128, 101), (155, 101),
        (101, 128), (128, 128), (155, 128),
        (101, 155), (128, 155), (155, 155),
    ),
}

REQUIRED_SOURCE_SNIPPETS = (
    "state.force_up_active = inputs.lf5 || inputs.lt5 || inputs.rf6;",
    "inputs.lf3 || inputs.rf8",
    "state.mode_active = inputs.rf5 || inputs.rf9;",
    "state.x1_active = inputs.lt4;",
    "state.x2_active = inputs.rf15 || inputs.rf12;",
    "state.y1_active = inputs.lt3;",
    "state.tilt1_effective = inputs.rf4;",
    "state.tilt2_effective = inputs.rf3;",
    "state.tilt3_effective = inputs.rf4 && inputs.rf3;",
    "kFriendProfile3Tilt2FlipperXOffsetForRight = -59",
    "kFriendProfile3Tilt2FlipperYMagnitude = 40",
    "ApplyFriendProfile3Tilt2FlipperOverride(roles, directions.x, directions.y, outputs);",
    "ApplyFriendProfile3XYModifierOverrides(roles, directions.x, directions.y, outputs);",
    "outputs.a = inputs.rt1 || inputs.lt2 || inputs.rf10;",
    "outputs.b = inputs.rf1 || inputs.lt2;",
    "outputs.x = inputs.rf7;",
    "outputs.y = inputs.rf2;",
    "outputs.buttonL = inputs.lf4 || inputs.rf10;",
    "outputs.buttonR = inputs.lt1;",
    "outputs.triggerRDigital = inputs.rf10 || inputs.rf16;",
    "outputs.start = inputs.mb7;",
    "outputs.dpadUp = inputs.rf13;",
    "outputs.dpadDown = inputs.rf11;",
    "outputs.dpadLeft = inputs.lf7;",
    "outputs.dpadRight = inputs.lf6;",
    "outputs.rightStickLeft = inputs.rt3;",
    "outputs.rightStickRight = inputs.rt5;",
    "outputs.rightStickDown = inputs.rt2;",
    "outputs.rightStickUp = inputs.rt4;",
    "outputs.rightStickX = mode_active ? 1 : 39;",
    "outputs.rightStickX = mode_active ? 255 : 217;",
    "outputs.rightStickY = 1;",
    "outputs.rightStickY = 255;",
)

REQUIRED_DOC_SNIPPETS = (
    "throwaway hardware-test branch",
    "Smash Box Designer",
    "Tilt2 X `197`",
    "signed offset `-59`",
    "raw `(69, 168)` displays as `-59 40`",
    "displays as `59 40`",
    "| rf16 | r |",
    "| mb7 | start |",
    "Standalone R is `rf16`; Start is `mb7`",
    "`rf10` also drives R only as part of the explicitly instructed",
    "X1 and Y1 alone do",
    "Light Shield L/R copied from Smash Box Designer values was not applied",
    "friend-profile3-smashbox-import-wip",
)


def fail(message: str) -> int:
    print("status=FAIL")
    print(f"failure={message}")
    return 1


def main() -> int:
    try:
        tables = load_source_tables(TABLE_SOURCE_PATH)
    except (OSError, TableExtractionError) as exc:
        return fail(str(exc))

    for name, expected in EXPECTED_TABLES.items():
        if tables.get(name) != expected:
            return fail(f"table_mismatch:{name}")

    matrix_text = MATRIX_PATH.read_text(encoding="utf-8")
    missing_buttons = sorted(button for button in PHYSICAL_BUTTONS if button not in matrix_text)
    if missing_buttons:
        return fail("missing_physical_buttons:" + ",".join(missing_buttons))

    source_text = ULTIMATE_SOURCE_PATH.read_text(encoding="utf-8")
    for snippet in REQUIRED_SOURCE_SNIPPETS:
        if snippet not in source_text:
            return fail(f"missing_source_snippet:{snippet}")
    if "outputs.start = inputs.rf16;" in source_text:
        return fail("rf16_must_not_be_double_bound_to_start")

    if re.search(r"triggerLAnalog\s*=\s*108|triggerRAnalog\s*=\s*108|triggerLAnalog\s*=\s*255|triggerRAnalog\s*=\s*255", source_text):
        return fail("light_shield_values_applied_without_confirmed_profile_fields")

    doc_text = DOC_PATH.read_text(encoding="utf-8")
    for snippet in REQUIRED_DOC_SNIPPETS:
        if snippet not in doc_text:
            return fail(f"missing_doc_snippet:{snippet}")

    print("status=PASS")
    print("profile=friend_profile3_smashbox_wip")
    print("branch=friend-profile3-smashbox-import-wip")
    print("coordinate_storage=absolute_raw_StickPoint_uint8")
    print("physical_buttons_validated=true")
    print("tilt2_flipper_raw_x=187/69")
    print("tilt2_source_x=197_signed_minus_59")
    print("light_shield_values=preserved_existing_wip_behavior")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
