#!/usr/bin/env python3
"""Read-only source checker for the GFW3 Smash Box runtime remap."""

from __future__ import annotations

import re
from pathlib import Path

from extract_glyph_identity_runtime_tables import load_source_text_with_generated_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
SPEC_PATH = REPO_ROOT / "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md"
BEGIN_MARKER = "// Senscope Glyph Smash Box runtime begin"
END_MARKER = "// Senscope Glyph Smash Box runtime end"

REQUIRED_SOURCE_SNIPPETS = (
    "constexpr StickPoint kTilt1Minus41Table[9]",
    "constexpr StickPoint kRT1RF4CustomTable[9]",
    "state.layer_left_active = false;",
    "state.layer_right_active = false;",
    "state.lf4_submode_active = inputs.lf4;",
    "state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;",
    "state.x1_active = inputs.lt5;",
    "state.x2_active = inputs.lt4;",
    "state.y1_active = inputs.lt2 && !inputs.lf4 && !lt2_sublayer_active;",
    "state.layer_rf3_normal_x_active = lt2_rf3_active;",
    "state.rf4_layer_flipper_active = lt2_rf4_active;",
    "state.rf4_modifier_suppressed_by_cstick = rf4_modifier_suppressed_by_cstick;",
    "state.rf4_behavior_available = rf4_behavior_available;",
    "state.rf3_x_suppressed_by_rf9 = rf3_x_suppressed_by_rf9;",
    "state.tilt3_effective = false;",
    "state.z_airdodge_override_active = inputs.rf6;",
    "state.null_modifier_active = inputs.rf9 && !state.rf4_behavior_available;",
    "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
    "outputs.b = base_rf2_b_active || inputs.lf4 || inputs.rf7 || (inputs.lt2 && !inputs.lf4 && inputs.rf3);",
    "outputs.x = (roles.base_rf3_x_active && !roles.rf3_x_suppressed_by_rf9) || lt2_rf1_x_active || lf4_rf2_x_active;",
    "outputs.buttonL = inputs.lt1 || inputs.lt3;",
    "outputs.buttonR = inputs.rf6;",
    "outputs.triggerLDigital = inputs.lt1 || inputs.lt3;",
    "outputs.triggerRDigital = inputs.rf16 || inputs.lt3;",
    "state.rt1_rf4_custom_active = rt1_rf4_custom_active;",
    "const bool rf4_rf2_minus41_active = roles.rf4_behavior_available && inputs.rf2 && !inputs.lt2 && !inputs.lf4 && !roles.rt1_rf4_custom_active;",
    "active_table = kTilt1Minus41Table;",
    "ApplyRF3VerticalCStickDiagonalOverride(inputs, effective_directions, directions, outputs);",
    "outputs.rightStickX = 128;",
    "outputs.rightStickY = 128;",
    "if (inputs.nunchuk_c)",
    "if (inputs.nunchuk_connected)",
)

REQUIRED_POINTS = (
    "{69, 78}", "{128, 78}", "{187, 78}",
    "{69, 128}", "{128, 128}", "{187, 128}",
    "{72, 172}", "{128, 179}", "{184, 172}",
    "{169, 47}", "{128, 47}", "{87, 47}",
    "{169, 128}", "{128, 128}", "{87, 128}",
    "{169, 209}", "{128, 209}", "{87, 209}",
)

FORBIDDEN_SOURCE_SNIPPETS = (
    "state.layer_left_active = inputs.lf8;",
    "state.layer_right_active = inputs.lf7;",
    "state.force_up_active = inputs.rf6 || inputs.rf12 || inputs.rf15",
    "state.z_airdodge_override_active = inputs.lt5 || inputs.rf11;",
    "outputs.buttonR = inputs.rt1 || inputs.lt5 || inputs.rf11;",
    "outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12 || inputs.rf15;",
    "outputs.buttonL = inputs.lt3;",
    "outputs.triggerLDigital = inputs.lt3;",
    "outputs.triggerRDigital = inputs.rf16;",
    "state.tilt3_effective = tilt1_pressed && tilt2_pressed;",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def marker_block(text: str) -> str:
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        fail("expected exactly one Smash Box runtime marker pair")
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER, begin)
    return text[begin : end + len(END_MARKER)]


def validate_spec() -> None:
    text = SPEC_PATH.read_text(encoding="utf-8")
    for phrase in (
        "RF6 becomes Z plus the existing low-magnitude",
        "RF5 becomes forced Up plus A",
        "RT1 + RF4 uses the custom table",
        "RF9 nulls both left stick and right stick inputs",
        "LF4 overrides LT2 behavior when both are held",
        "This spec is not a hardware result",
    ):
        if phrase not in text:
            fail(f"spec missing required phrase: {phrase}")


def validate_source(text: str) -> None:
    block = marker_block(text)
    for snippet in REQUIRED_SOURCE_SNIPPETS:
        if snippet not in text:
            fail(f"missing source evidence: {snippet}")
    for point in REQUIRED_POINTS:
        if point not in text:
            fail(f"missing required raw coordinate: {point}")
    for snippet in FORBIDDEN_SOURCE_SNIPPETS:
        if snippet in text:
            fail(f"forbidden stale source evidence present: {snippet}")
    if re.search(r"outputs\.(?!buttonR)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf6", text):
        fail("RF6 must not directly drive outputs other than Z")
    if re.search(r"outputs\.(?!leftStickX|leftStickY|rightStickX|rightStickY)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf9", text):
        fail("RF9 must not directly drive game/dpad outputs")
    if "ApplyNullOverride(outputs);" not in block:
        fail("RF9 null override must remain in runtime analog block")
    if block.find("if (directions.cx != 0 && directions.cy != 0)") > block.find("ApplyNullOverride(outputs);"):
        fail("RF9 null must run after C-stick ASDI analog adjustment")


def main() -> int:
    try:
        source = load_source_text_with_generated_tables(SOURCE_PATH)
        validate_spec()
        validate_source(source)
    except AssertionError as exc:
        print("status=FAIL")
        print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
    print("runtime_profile=gfw3_runtime_remap_rework")
    print("hardware_status=not_new_hardware_result")
    print("nunchuk_status=preserved_but_not_hardware_validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
