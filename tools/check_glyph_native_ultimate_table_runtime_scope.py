#!/usr/bin/env python3
"""Read-only scope checker for native Ultimate identity-runtime table implementation."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
BEGIN_MARKER = "// Senscope Glyph Smash Box runtime begin"
END_MARKER = "// Senscope Glyph Smash Box runtime end"

REQUIRED_TABLES = (
    "kDefaultTable",
    "kModeDefaultTable",
    "kX1Table",
    "kX2Table",
    "kMX1Table",
    "kMX2Table",
    "kY1Table",
    "kMY1Table",
    "kLayerNormalXTable",
    "kMLayerNormalXTable",
    "kY1LayerNormalXTable",
    "kMY1LayerNormalXTable",
    "kLayerFlipperTable",
    "kMLayerFlipperTable",
    "kY1Tilt1Table",
    "kMY1Tilt1Table",
    "kY1LayerFlipperTable",
    "kMY1LayerFlipperTable",
    "kTilt1Table",
    "kTilt2Table",
    "kTilt3Table",
    "kMTilt1Table",
    "kMTilt2Table",
    "kMTilt3Table",
    "kLt1LowMagnitudeTable",
)

LT1_LOW_POINTS = (
    (89, 89),
    (128, 79),
    (167, 89),
    (79, 128),
    (128, 128),
    (177, 128),
    (89, 167),
    (128, 177),
    (167, 167),
)

TILT1_POINTS = (
    (187, 47),
    (128, 47),
    (69, 47),
    (187, 128),
    (128, 128),
    (69, 128),
    (187, 209),
    (128, 209),
    (69, 209),
)

Y1_TILT1_POINTS = (
    (169, 99),
    (128, 99),
    (87, 99),
    (169, 128),
    (128, 128),
    (87, 128),
    (169, 157),
    (128, 157),
    (87, 157),
)

MY1_TILT1_POINTS = (
    (169, 179),
    (128, 179),
    (87, 179),
    (169, 169),
    (128, 169),
    (87, 169),
    (169, 77),
    (128, 77),
    (87, 77),
)

MODE_DEFAULT_POINTS = (
    (14, 87),
    (128, 87),
    (242, 87),
    (14, 169),
    (128, 169),
    (242, 169),
    (14, 169),
    (128, 169),
    (242, 169),
)

MX1_POINTS = (
    (78, 87),
    (128, 87),
    (178, 87),
    (78, 169),
    (128, 169),
    (178, 169),
    (78, 169),
    (128, 169),
    (178, 169),
)

MX2_POINTS = (
    (65, 87),
    (128, 87),
    (191, 87),
    (65, 169),
    (128, 169),
    (191, 169),
    (65, 169),
    (128, 169),
    (191, 169),
)

MY1_POINTS = (
    (14, 179),
    (128, 179),
    (242, 179),
    (14, 169),
    (128, 169),
    (242, 169),
    (14, 77),
    (128, 77),
    (242, 77),
)

MTILT1_POINTS = (
    (169, 88),
    (128, 88),
    (87, 88),
    (169, 169),
    (128, 169),
    (87, 169),
    (169, 168),
    (128, 168),
    (87, 168),
)

MTILT2_POINTS = (
    (96, 82),
    (128, 82),
    (160, 82),
    (96, 169),
    (128, 169),
    (160, 169),
    (96, 174),
    (128, 174),
    (160, 174),
)

MTILT3_POINTS = (
    (96, 86),
    (128, 86),
    (160, 86),
    (96, 169),
    (128, 169),
    (160, 169),
    (96, 170),
    (128, 170),
    (160, 170),
)

LAYER_FLIPPER_POINTS = (
    (169, 51),
    (128, 51),
    (87, 51),
    (169, 128),
    (128, 128),
    (87, 128),
    (169, 205),
    (128, 205),
    (87, 205),
)

MLAYER_FLIPPER_POINTS = (
    (169, 87),
    (128, 87),
    (87, 87),
    (169, 169),
    (128, 169),
    (87, 169),
    (169, 169),
    (128, 169),
    (87, 169),
)

LAYER_NORMAL_X_POINTS = (
    (87, 51),
    (128, 51),
    (169, 51),
    (87, 128),
    (128, 128),
    (169, 128),
    (87, 205),
    (128, 205),
    (169, 205),
)

MLAYER_NORMAL_X_POINTS = (
    (87, 87),
    (128, 87),
    (169, 87),
    (87, 169),
    (128, 169),
    (169, 169),
    (87, 169),
    (128, 169),
    (169, 169),
)

Y1_LAYER_NORMAL_X_POINTS = (
    (87, 99),
    (128, 99),
    (169, 99),
    (87, 128),
    (128, 128),
    (169, 128),
    (87, 157),
    (128, 157),
    (169, 157),
)

MY1_LAYER_NORMAL_X_POINTS = (
    (87, 179),
    (128, 179),
    (169, 179),
    (87, 169),
    (128, 169),
    (169, 169),
    (87, 77),
    (128, 77),
    (169, 77),
)

FORBIDDEN_TOKENS = (
    "flash",
    "bootloader",
    "uf2",
    "push-to-device",
    "push_to_device",
    "senscope_tilt3_active",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags=flags) is None:
        fail(f"missing source evidence: {label}")


def extract_marker_block(source: str) -> str:
    begin_count = source.count(BEGIN_MARKER)
    end_count = source.count(END_MARKER)
    if begin_count != 1 or end_count != 1:
        fail(f"expected exactly one marker block, found begin={begin_count} end={end_count}")
    begin = source.find(BEGIN_MARKER)
    end = source.find(END_MARKER, begin)
    if begin < 0 or end < 0 or end < begin:
        fail("runtime marker block missing or malformed")
    return source[begin : end + len(END_MARKER)]


def extract_table_values(source: str, table_name: str) -> list[tuple[int, int]]:
    match = re.search(
        rf"constexpr\s+StickPoint\s+{re.escape(table_name)}\[9\]\s*=\s*\{{(?P<body>.*?)\}};",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        fail(f"missing table definition: {table_name}")
    body = match.group("body")
    pairs = re.findall(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}", body)
    if len(pairs) != 9:
        fail(f"table {table_name} must contain 9 points, found {len(pairs)}")
    values = [(int(x), int(y)) for x, y in pairs]
    for x, y in values:
        if not (0 <= x <= 255 and 0 <= y <= 255):
            fail(f"table {table_name} has out-of-range value ({x}, {y})")
    return values


def ensure_required_shapes(source: str, block: str) -> None:
    require(r"mode_active\s*=\s*inputs\.rf8\s*;", block, "Mode anchor rf8")
    require(r"x1_active\s*=\s*inputs\.lt4\s*;", block, "X1 anchor lt4")
    require(r"x2_active\s*=\s*inputs\.lt1\s*;", block, "X2 anchor lt1")
    require(r"y1_active\s*=\s*inputs\.lt2\s*&&\s*!inputs\.lf4\s*;", block, "Y1 anchor lt2 with LF4 suppression")
    require(r"ls_to_dpad_active\s*=\s*inputs\.rf13\s*;", block, "LS->DPad anchor rf13")
    require(r"null_modifier_active\s*=\s*inputs\.rf9\s*;", block, "RF9 null-modifier anchor")
    require(r"layer_left_active\s*=\s*inputs\.lf8\s*;", source, "layer-left anchor lf8")
    require(r"layer_right_active\s*=\s*inputs\.lf7\s*;", source, "layer-right anchor lf7")
    require(r"layer_direction_active\s*=\s*layer_left_active\s*\|\|\s*layer_right_active\s*;", source, "layer direction active aggregation")
    require(
        r"lf4_submode_active\s*=\s*inputs\.lf4\s*&&\s*\(\s*layer_direction_active\s*\|\|\s*inputs\.lt2\s*\)\s*;",
        source,
        "LF4 sub-mode activation anchor",
    )
    require(r"c_stick_any_active\s*=\s*inputs\.rt2\s*\|\|\s*inputs\.rt3\s*\|\|\s*inputs\.rt4\s*\|\|\s*inputs\.rt5\s*;", source, "C-stick aggregation anchor")
    require(r"rf2_suppressed_by_lf4_submode_cstick\s*=\s*lf4_submode_active\s*&&\s*c_stick_any_active\s*;", source, "LF4-submode RF2 C-stick suppression anchor")
    require(r"layer_transform_active\s*=\s*layer_direction_active\s*\|\|\s*lf4_submode_active\s*;", source, "layer transform active aggregation")
    require(r"pure_layer_rf2_force_up_active\s*=\s*layer_direction_active\s*&&\s*!inputs\.lf4\s*&&\s*inputs\.rf2\s*&&\s*!rf2_suppressed_by_lf4_submode_cstick\s*;", source, "pure-layer RF2 forced-Up anchor")
    require(r"lf4_submode_rf3_force_up_active\s*=\s*lf4_submode_active\s*&&\s*inputs\.rf3\s*;", source, "LF4 sub-mode RF3 forced-Up anchor")
    require(r"layer_rf3_normal_x_active\s*=\s*layer_direction_active\s*&&\s*!inputs\.lf4\s*&&\s*inputs\.rf3\s*;", source, "layered RF3 normal-x anchor")
    require(r"rf4_layer_flipper_active\s*=\s*layer_transform_active\s*&&\s*inputs\.rf4\s*;", source, "layered RF4 flipper anchor")
    require(r"tilt1_pressed\s*=\s*inputs\.rf3\s*&&\s*!layer_transform_active\s*;", source, "RF3 tilt1 gate outside layer transform")
    require(r"tilt2_pressed\s*=\s*inputs\.rf4\s*&&\s*!layer_transform_active\s*;", source, "RF4 tilt2 gate outside layer transform")
    require(
        r"layer_normal_x_effective\s*=\s*layer_normal_x_active\s*&&\s*!layer_flipper_effective\s*;",
        source,
        "RF4 layered flipper precedence over RF3 normal-x",
    )
    require(r"EffectiveModifier::LayerNormalX", source, "layered RF3 normal-x effective modifier")

    require(r"outputs\.buttonL\s*=\s*inputs\.lt3\s*;", source, "LT3 mapped to L")
    require(r"outputs\.triggerLDigital\s*=\s*inputs\.lt3\s*;", source, "LT3 mapped to L carrier")
    require(
        r"outputs\.buttonR\s*=\s*inputs\.rt1\s*\|\|\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        source,
        "RT1/LT5/RF11 mapped to Z",
    )
    require(r"outputs\.triggerRDigital\s*=\s*inputs\.rf16\s*;", source, "RF16 mapped to R")
    require(
        r"outputs\.a\s*=\s*inputs\.rf1\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        source,
        "RF1/LT6/RF12/RF15 mapped to A",
    )
    require(
        r"outputs\.b\s*=\s*inputs\.rf5\s*\|\|\s*inputs\.lf4\s*\|\|\s*inputs\.rf7\s*\|\|\s*\(\s*layer_direction_active\s*&&\s*!inputs\.lf4\s*&&\s*inputs\.rf3\s*\)\s*;",
        source,
        "B output includes RF7 hard Up+B and layered RF3 in pure layer",
    )
    require(
        r"outputs\.x\s*=\s*inputs\.rf2\s*&&\s*!rf2_suppressed_by_lf4_submode_cstick\s*&&\s*\(\s*!layer_direction_active\s*\|\|\s*inputs\.lf4\s*\)\s*;",
        source,
        "X output includes RF2 non-layer/LF4-submode path with C-stick suppression",
    )
    require(
        r"SelectStickTable\(\s*mode_active,\s*x1_active,\s*x2_active,\s*y1_active,\s*layer_rf3_normal_x_active,\s*rf4_layer_flipper_active,\s*tilt1_effective,\s*tilt2_effective,\s*tilt3_effective",
        source,
        "table selection includes layer RF3 normal-x and RF4 flipper modifiers",
        flags=re.DOTALL,
    )

    if "outputs.buttonL = inputs.lt1;" in source:
        fail("LT1 must not map to L")
    if "outputs.buttonR = inputs.rt1;" in source:
        fail("RT1-only Z carrier is outdated")
    if "outputs.buttonR = inputs.rt1 || inputs.lt1;" in source:
        fail("RT1/LT1-only Z carrier is outdated")
    if "outputs.buttonR = inputs.rt1 || inputs.lt1 || inputs.rf11;" in source:
        fail("stale RT1/LT1/RF11 Z carrier is outdated")
    if re.search(r"const\s+bool\s+x1_active\s*=\s*inputs\.lt5\s*;", block):
        fail("stale X1 anchor lt5 must be removed")
    if re.search(r"const\s+bool\s+x2_active\s*=\s*inputs\.lt4\s*;", block):
        fail("stale X2 anchor lt4 must be removed")
    if re.search(r"const\s+bool\s+z_airdodge_override_active\s*=\s*inputs\.lt1\s*\|\|\s*inputs\.rf11\s*;", block):
        fail("stale LT1/RF11 Z-airdodge activation shape must be removed")

    # Y2/MY2 are scratched and removed from runtime source selection.
    for token in ("y2_active", "EffectiveModifier::Y2", "kY2Table", "kMY2Table"):
        if token in source:
            fail(f"Y2/MY2 token must not remain active in runtime source: {token}")

    require(r"direction_plus_a_active\s*=\s*down_a_active\s*\|\|\s*up_a_active\s*;", source, "hard direction-plus-A active flag")
    require(r"up_a_active\s*=\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;", source, "RF15 aliases RF12 for Up+A")
    require(
        r"direction_plus_a_force_up\s*=\s*direction_plus_a_active\s*&&\s*\(\s*up_a_active\s*\|\|\s*force_up_active\s*\)\s*;",
        source,
        "hard direction-plus-A Up override (RF12/RF15 or shared forced-up sources)",
    )
    require(
        r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*\|\|\s*pure_layer_rf2_force_up_active\s*\|\|\s*lf4_submode_rf3_force_up_active\s*;",
        source,
        "forced-up includes pure-layer RF2 and LF4 sub-mode RF3",
    )
    require(
        r"const\s+bool\s+lt1_force_up_active\s*=\s*force_up_active\s*;",
        source,
        "Z-airdodge forced-up includes layered RF2 source",
    )
    require(
        r"const\s+bool\s+z_airdodge_override_active\s*=\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        block,
        "LT5/RF11 shared low-magnitude override alias",
    )

    require(r"constexpr\s+StickPoint\s+kLt1LowMagnitudeTable\[9\]", source, "LT1 low table declaration")
    for x, y in LT1_LOW_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing LT1 low-magnitude point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kTilt1Table\[9\]", source, "Tilt1 table declaration")
    for x, y in TILT1_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing Tilt1 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kY1Tilt1Table\[9\]", source, "Y1+Tilt1 table declaration")
    for x, y in Y1_TILT1_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing Y1+Tilt1 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMY1Tilt1Table\[9\]", source, "Mode Y1+Tilt1 table declaration")
    for x, y in MY1_TILT1_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing Mode Y1+Tilt1 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kModeDefaultTable\[9\]", source, "Mode default table declaration")
    for x, y in MODE_DEFAULT_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing Mode default point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMX1Table\[9\]", source, "MX1 table declaration")
    for x, y in MX1_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing MX1 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMX2Table\[9\]", source, "MX2 table declaration")
    for x, y in MX2_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing MX2 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMY1Table\[9\]", source, "MY1 table declaration")
    for x, y in MY1_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing MY1 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kLayerNormalXTable\[9\]", source, "layer normal-x table declaration")
    for x, y in LAYER_NORMAL_X_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing layer normal-x point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMLayerNormalXTable\[9\]", source, "mode layer normal-x table declaration")
    for x, y in MLAYER_NORMAL_X_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing mode layer normal-x point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kY1LayerNormalXTable\[9\]", source, "Y1 layer normal-x table declaration")
    for x, y in Y1_LAYER_NORMAL_X_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing Y1 layer normal-x point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMY1LayerNormalXTable\[9\]", source, "mode Y1 layer normal-x table declaration")
    for x, y in MY1_LAYER_NORMAL_X_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing mode Y1 layer normal-x point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMTilt1Table\[9\]", source, "MTilt1 table declaration")
    for x, y in MTILT1_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing MTilt1 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMTilt2Table\[9\]", source, "MTilt2 table declaration")
    for x, y in MTILT2_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing MTilt2 point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMTilt3Table\[9\]", source, "MTilt3 table declaration")
    for x, y in MTILT3_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing MTilt3 point: ({x}, {y})")

    require(
        r"const\s+bool\s+y1_tilt1_special_active\s*=\s*y1_active\s*&&\s*tilt1_effective\s*&&\s*!x1_active\s*&&\s*!x2_active\s*&&\s*!tilt2_effective\s*&&\s*!tilt3_effective\s*;",
        source,
        "Y1+Tilt1-only special composite gating",
    )
    require(
        r"if\s*\(\s*y1_tilt1_special_active\s*\)\s*\{\s*return\s+mode_active\s*\?\s*kMY1Tilt1Table\s*:\s*kY1Tilt1Table\s*;",
        source,
        "Y1+Tilt1 special composite selection",
        flags=re.DOTALL,
    )

    require(
        r"if\s*\(\s*ls_to_dpad_active\s*\)\s*\{\s*const\s+StickPoint\s+center\s*=\s*mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;\s*outputs\.leftStickX\s*=\s*center\.x\s*;\s*outputs\.leftStickY\s*=\s*center\.y\s*;\s*\}\s*else\s*\{",
        block,
        "LS->DPad centers analog and gates override to non-LS->DPad path",
        flags=re.DOTALL,
    )

    require(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*z_airdodge_override_active\s*\)\s*\{",
        block,
        "LT5/RF11 override is final after direction-plus-A",
        flags=re.DOTALL,
    )
    require(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*z_airdodge_override_active\s*\)\s*\{.*?\}\s*if\s*\(\s*inputs\.rf7\s*\)\s*\{.*?\}\s*\}\s*if\s*\(\s*null_modifier_active\s*\)\s*\{",
        block,
        "RF9 override is final after LT5/RF11, direction-plus-A, and RF7 hard override",
        flags=re.DOTALL,
    )
    require(
        r"if\s*\(\s*inputs\.rf7\s*\)\s*\{\s*//\s*RF7\s+is\s+a\s+hard\s+Up\+B\s+analog\s+override.*?effective_ls_left\s*==\s*effective_ls_right\s*\?\s*128\s*:\s*\(effective_ls_left\s*\?\s*77\s*:\s*179\).*?outputs\.leftStickY\s*=\s*172\s*;",
        block,
        "RF7 hard Up+B constants and horizontal policy",
        flags=re.DOTALL,
    )
    require(r"outputs\.leftStickX\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.x\s*;", block, "LT1 final X")
    require(r"outputs\.leftStickY\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.y\s*;", block, "LT1 final Y")
    require(r"outputs\.leftStickX\s*=\s*128\s*;", block, "RF9 final X override")
    require(r"outputs\.leftStickY\s*=\s*128\s*;", block, "RF9 final Y override")
    if re.search(r"active_modifier_count\s*\+\+[^;]*null_modifier_active", source):
        fail("RF9 must not be part of modifier count logic")
    if re.search(r"SelectStickTable\s*\([^)]*null_modifier_active", source):
        fail("RF9 must not alter table selection arguments")
    if re.search(r"outputs\.(?!leftStickX|leftStickY)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf9", source):
        fail("RF9 must not drive game/dpad/right-stick/menu outputs")
    if re.search(r"active_modifier_count\s*\+\+[^;]*inputs\.rf11", source):
        fail("RF11 must not be part of modifier count logic")
    if re.search(r"SelectStickTable\s*\([^)]*inputs\.rf11", source, flags=re.DOTALL):
        fail("RF11 must not alter table selection arguments")
    if re.search(r"outputs\.(?!buttonR)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf11", source):
        fail("RF11 must not drive outputs other than the shared Z carrier")
    if re.search(r"const\s+bool\s+ls_to_dpad_active\s*=\s*inputs\.rf7\s*;", source):
        fail("RF7 must not activate LS->DPad")
    if re.search(r"force_up_active\s*=.*inputs\.rf7", source):
        fail("RF7 must not be included in forced-up aggregation")

    require(r"outputs\.rightStickRight\s*=\s*inputs\.rt4\s*;", source, "RT4 drives C-right")
    require(r"outputs\.rightStickUp\s*=\s*inputs\.rt5\s*;", source, "RT5 drives C-up")
    require(r"outputs\.dpadUp\s*=\s*inputs\.rt5\s*;", source, "nunchuk-C Up uses RT5")
    require(r"outputs\.dpadRight\s*=\s*inputs\.rt4\s*;", source, "nunchuk-C Right uses RT4")
    require(
        r"UpdateDirections\(\s*effective_ls_left,\s*//\s*Left\s*\(LF3 \+ LF8 layer-left contribution with cancellation\)\s*effective_ls_right,\s*//\s*Right\s*\(LF1 \+ LF7 layer-right contribution with cancellation\)\s*effective_ls_down,\s*//\s*Down\s*\(LT6/LF5, suppressed by forced-Up\)\s*effective_ls_up,\s*//\s*Up\s*\(RF6/RF12/RF15, pure-layer RF2, and LF4-submode RF3 forced-Up\)\s*inputs\.rt3,\s*//\s*C-Left\s*inputs\.rt4,\s*//\s*C-Right\s*inputs\.rt2,\s*//\s*C-Down\s*inputs\.rt5,\s*//\s*C-Up",
        source,
        "UpdateDirections uses layer-aware effective LS directions and RT4/RT5 C-stick mapping",
        flags=re.DOTALL,
    )


def ensure_no_forbidden_tokens(source: str) -> None:
    lowered = source.lower()
    for token in FORBIDDEN_TOKENS:
        if token in lowered:
            fail(f"forbidden token present: {token}")


def main() -> int:
    try:
        source = ULTIMATE_PATH.read_text(encoding="utf-8")
        block = extract_marker_block(source)

        ensure_required_shapes(source, block)
        ensure_no_forbidden_tokens(source)

        table_summaries: list[str] = []
        for table_name in REQUIRED_TABLES:
            values = extract_table_values(source, table_name)
            table_summaries.append(f"{table_name}:{values[0]}->{values[4]}->{values[8]}")
    except (AssertionError, FileNotFoundError) as exc:
        print("glyph_native_ultimate_table_runtime_scope")
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("glyph_native_ultimate_table_runtime_scope")
    print("status=PASS")
    print(f"source={ULTIMATE_PATH.relative_to(REPO_ROOT)}")
    print("runtime_markers=present")
    print(f"tables_validated={len(REQUIRED_TABLES)}")
    print("ls_to_dpad_role=rf13")
    print("rf7_role=hard_up_b")
    print("mode_role=rf8")
    print("lt3_role=L")
    print("lt5_rf11_role=Z_plus_low_magnitude_override_alias")
    print("z_role=rt1_or_lt5_or_rf11")
    print("r_role=rf16")
    print("y_role=rf10")
    print("forced_up_role=rf6_or_rf12_or_rf15_or_pure_layer_rf2_or_lf4_submode_rf3")
    print("direction_plus_a_role=lt6_down_a_rf12_or_rf15_up_a")
    print("direction_plus_a_override_policy=hard_final_default_or_mode_default_then_lt5_low_override")
    print("y1_tilt1_special_composite=enabled")
    print("rt4_rt5_cstick_swap=enabled")
    print("rf9_null_modifier=enabled")
    print("y2_my2_runtime_role=scratched_inactive")
    print("standalone_dpad=none")
    print("table_samples=" + ";".join(table_summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    require(r"constexpr\s+StickPoint\s+kLayerFlipperTable\[9\]", source, "layer flipper table declaration")
    for x, y in LAYER_FLIPPER_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing layer flipper point: ({x}, {y})")

    require(r"constexpr\s+StickPoint\s+kMLayerFlipperTable\[9\]", source, "mode layer flipper table declaration")
    for x, y in MLAYER_FLIPPER_POINTS:
        if f"{{{x}, {y}}}" not in source:
            fail(f"missing mode layer flipper point: ({x}, {y})")

    require(r"const\s+bool\s+tilt1_pressed\s*=\s*inputs\.rf3\s*&&\s*!layer_active\s*;", source, "RF3 tilt1 is layer-gated")
    require(r"const\s+bool\s+tilt2_pressed\s*=\s*inputs\.rf4\s*&&\s*!layer_active\s*;", source, "RF4 tilt2 is layer-gated")
    require(r"const\s+bool\s+rf4_layer_flipper_active\s*=\s*layer_active\s*&&\s*inputs\.rf4\s*;", source, "RF4 layer flipper flag")
    require(
        r"SelectStickTable\(\s*mode_active,\s*x1_active,\s*x2_active,\s*y1_active,\s*rf4_layer_flipper_active,\s*tilt1_effective,\s*tilt2_effective,\s*tilt3_effective",
        source,
        "table selection includes layer flipper modifier argument",
        flags=re.DOTALL,
    )
