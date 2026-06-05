#!/usr/bin/env python3
"""Read-only scope checker for native Ultimate identity-runtime table implementation."""

from __future__ import annotations

import re
from pathlib import Path

from extract_glyph_identity_runtime_tables import load_source_text_with_generated_tables


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
    "kTilt1Minus41Table",
    "kRT1RF4CustomTable",
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

TILT1_MINUS41_POINTS = (
    (169, 47),
    (128, 47),
    (87, 47),
    (169, 128),
    (128, 128),
    (87, 128),
    (169, 209),
    (128, 209),
    (87, 209),
)

RT1_RF4_CUSTOM_POINTS = (
    (69, 78),
    (128, 78),
    (187, 78),
    (69, 128),
    (128, 128),
    (187, 128),
    (72, 172),
    (128, 179),
    (184, 172),
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


def ensure_table_points(source: str, table_name: str, expected: tuple[tuple[int, int], ...]) -> None:
    require(rf"constexpr\s+StickPoint\s+{re.escape(table_name)}\[9\]", source, f"{table_name} declaration")
    actual = extract_table_values(source, table_name)
    if actual != list(expected):
        fail(f"{table_name} values changed: expected={expected} actual={tuple(actual)}")


def ensure_required_shapes(source: str, block: str) -> None:
    for helper_name in (
        "struct LayerState",
        "struct EffectiveDirectionState",
        "struct RoleState",
        "ResolveLayerState",
        "ResolveEffectiveDirections",
        "ResolveRoleState",
        "ApplyTableAnalogOutput",
        "ApplyDirectionPlusAOverride",
        "ApplyZAirdodgeOverride",
        "ApplyHardUpBOverride",
        "ApplyNullOverride",
    ):
        if helper_name not in source:
            fail(f"missing hardened runtime helper shape: {helper_name}")

    require(r"state\.mode_active\s*=\s*inputs\.rf8\s*;", source, "Mode anchor rf8")
    require(r"state\.x1_active\s*=\s*inputs\.lt5\s*;", source, "X1 moved to LT5")
    require(r"state\.x2_active\s*=\s*inputs\.lt4\s*;", source, "X2 moved to LT4")
    require(r"state\.y1_active\s*=\s*inputs\.lt2\s*&&\s*!inputs\.lf4\s*&&\s*!lt2_sublayer_active\s*;", source, "LT2 Y1 suppressed by LF4 or LT2 sublayer")
    require(r"state\.ls_to_dpad_active\s*=\s*inputs\.rf13\s*;", source, "LS->DPad anchor rf13")
    require(r"state\.null_modifier_active\s*=\s*inputs\.rf9\s*&&\s*!inputs\.rf4\s*;", source, "RF9 null disabled by RF4")
    require(r"state\.layer_left_active\s*=\s*false\s*;", source, "LF8 layer-left scratched")
    require(r"state\.layer_right_active\s*=\s*false\s*;", source, "LF7 layer-right scratched")
    require(r"state\.lf4_submode_active\s*=\s*inputs\.lf4\s*;", source, "LF4 sub-mode activation")
    require(r"state\.layer_transform_active\s*=\s*\(\s*inputs\.lt2\s*&&\s*!inputs\.lf4\s*\)\s*\|\|\s*state\.lf4_submode_active\s*;", source, "LT2/LF4 transform state")
    require(r"state\.c_stick_any_active\s*=\s*inputs\.rt2\s*\|\|\s*inputs\.rt3\s*\|\|\s*inputs\.rt4\s*\|\|\s*inputs\.rt5\s*;", source, "C-stick aggregation anchor")
    require(r"state\.rf2_suppressed_by_lf4_submode_cstick\s*=\s*state\.lf4_submode_active\s*&&\s*state\.c_stick_any_active\s*;", source, "LF4 RF2 C-stick suppression anchor")
    require(r"lt2_rf2_force_up_active\s*=\s*inputs\.lt2\s*&&\s*!inputs\.lf4\s*&&\s*inputs\.rf2\s*;", source, "LT2 RF2 forced-Up anchor")
    require(r"lf4_submode_rf3_force_up_active\s*=\s*inputs\.lf4\s*&&\s*inputs\.rf3\s*;", source, "LF4 RF3 forced-Up anchor")
    require(r"state\.force_up_active\s*=\s*inputs\.rf5\s*\|\|\s*lt2_rf2_force_up_active\s*\|\|\s*lf4_submode_rf3_force_up_active\s*;", source, "GFW3 forced-Up aggregation")
    require(r"state\.layer_rf3_normal_x_active\s*=\s*lt2_rf3_active\s*;", source, "LT2 RF3 normal-x anchor")
    require(r"state\.rf4_layer_flipper_active\s*=\s*lt2_rf4_active\s*;", source, "LT2 RF4 flipper anchor")
    require(r"state\.tilt3_effective\s*=\s*false\s*;", source, "RF3+RF4 Tilt3 fusion scratched")
    require(r"state\.z_airdodge_override_active\s*=\s*inputs\.rf6\s*;", source, "RF6 Z-airdodge anchor")
    require(r"const\s+bool\s+tilt1_pressed\s*=\s*inputs\.rf4\s*&&\s*\(\s*!inputs\.lt2\s*\|\|\s*inputs\.lf4\s*\)\s*&&\s*!inputs\.rt1\s*&&\s*!lf4_rf2_deactivates_rf4\s*;", source, "RF4 base/LF4-over-LT2 Tilt1 gate")
    require(r"const\s+bool\s+tilt2_pressed\s*=\s*inputs\.rt1\s*&&\s*!inputs\.rf4\s*;", source, "RT1 base Tilt2 gate")
    require(
        r"layer_normal_x_effective\s*=\s*layer_normal_x_active\s*&&\s*!layer_flipper_effective\s*;",
        source,
        "RF4 LT2 flipper precedence over RF3 normal-x",
    )

    require(r"outputs\.buttonL\s*=\s*inputs\.lt1\s*\|\|\s*inputs\.lt3\s*;", source, "LT1/LT3 mapped to L")
    require(r"outputs\.triggerLDigital\s*=\s*inputs\.lt1\s*\|\|\s*inputs\.lt3\s*;", source, "LT1/LT3 mapped to L trigger")
    require(r"outputs\.buttonR\s*=\s*inputs\.rf6\s*;", source, "RF6 mapped to Z")
    require(r"outputs\.triggerRDigital\s*=\s*inputs\.rf16\s*\|\|\s*inputs\.lt3\s*;", source, "LT3 mapped to R with RF16")
    require(r"outputs\.a\s*=\s*base_rf1_a_active\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf5\s*;", source, "RF5 Up+A carrier")
    require(r"outputs\.b\s*=\s*base_rf2_b_active\s*\|\|\s*inputs\.lf4\s*\|\|\s*inputs\.rf7\s*\|\|\s*\(\s*inputs\.lt2\s*&&\s*!inputs\.lf4\s*&&\s*inputs\.rf3\s*\)\s*;", source, "RF2/LF4/RF7/LT2 RF3 B paths")
    require(r"outputs\.x\s*=\s*base_rf3_x_active\s*\|\|\s*lt2_rf1_x_active\s*\|\|\s*lf4_rf2_x_active\s*;", source, "RF3/LT2 RF1/LF4 RF2 X paths")
    require(
        r"SelectStickTable\(\s*roles\.mode_active,\s*roles\.x1_active,\s*roles\.x2_active,\s*roles\.y1_active,\s*roles\.layer_rf3_normal_x_active,\s*roles\.rf4_layer_flipper_active,\s*rt1_rf4_custom_active\s*\|\|\s*\(roles\.tilt1_effective\s*&&\s*!rf4_rf2_minus41_active\),\s*rt1_rf4_custom_active\s*\|\|\s*roles\.tilt2_effective,\s*roles\.tilt3_effective",
        source,
        "table selection includes GFW3 RT1+RF4 and RF4+RF2 policy",
        flags=re.DOTALL,
    )
    require(r"if\s*\(\s*rf4_rf2_minus41_active\s*\)\s*\{\s*active_table\s*=\s*kTilt1Minus41Table\s*;", source, "RF4+RF2 -41 table selection", flags=re.DOTALL)
    require(r"if\s*\(\s*tilt1_effective\s*&&\s*tilt2_effective\s*\)\s*\{\s*return\s+kRT1RF4CustomTable\s*;", source, "RT1+RF4 custom table selection", flags=re.DOTALL)

    for stale in (
        r"state\.layer_left_active\s*=\s*inputs\.lf8\s*;",
        r"state\.layer_right_active\s*=\s*inputs\.lf7\s*;",
        r"state\.z_airdodge_override_active\s*=\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        r"state\.force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15",
        r"outputs\.buttonR\s*=\s*inputs\.rt1\s*\|\|\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        r"outputs\.a\s*=\s*inputs\.rf1\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        r"state\.tilt3_effective\s*=\s*tilt1_pressed\s*&&\s*tilt2_pressed\s*;",
    ):
        if re.search(stale, source):
            fail(f"stale pre-GFW3 source evidence present: {stale}")

    for token in ("y2_active", "EffectiveModifier::Y2", "kY2Table", "kMY2Table"):
        if token in source:
            fail(f"Y2/MY2 token must not remain active in runtime source: {token}")

    ensure_table_points(source, "kLt1LowMagnitudeTable", LT1_LOW_POINTS)
    ensure_table_points(source, "kTilt1Table", TILT1_POINTS)
    ensure_table_points(source, "kY1Tilt1Table", Y1_TILT1_POINTS)
    ensure_table_points(source, "kMY1Tilt1Table", MY1_TILT1_POINTS)
    ensure_table_points(source, "kModeDefaultTable", MODE_DEFAULT_POINTS)
    ensure_table_points(source, "kMX1Table", MX1_POINTS)
    ensure_table_points(source, "kMX2Table", MX2_POINTS)
    ensure_table_points(source, "kMY1Table", MY1_POINTS)
    ensure_table_points(source, "kLayerNormalXTable", LAYER_NORMAL_X_POINTS)
    ensure_table_points(source, "kMLayerNormalXTable", MLAYER_NORMAL_X_POINTS)
    ensure_table_points(source, "kY1LayerNormalXTable", Y1_LAYER_NORMAL_X_POINTS)
    ensure_table_points(source, "kMY1LayerNormalXTable", MY1_LAYER_NORMAL_X_POINTS)
    ensure_table_points(source, "kMTilt1Table", MTILT1_POINTS)
    ensure_table_points(source, "kMTilt2Table", MTILT2_POINTS)
    ensure_table_points(source, "kMTilt3Table", MTILT3_POINTS)
    ensure_table_points(source, "kTilt1Minus41Table", TILT1_MINUS41_POINTS)
    ensure_table_points(source, "kRT1RF4CustomTable", RT1_RF4_CUSTOM_POINTS)

    require(
        r"if\s*\(\s*roles\.ls_to_dpad_active\s*\)\s*\{\s*const\s+StickPoint\s+center\s*=\s*roles\.mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;\s*outputs\.leftStickX\s*=\s*center\.x\s*;\s*outputs\.leftStickY\s*=\s*center\.y\s*;\s*\}\s*else\s*\{",
        block,
        "LS->DPad centers analog and gates override to non-LS->DPad path",
        flags=re.DOTALL,
    )
    require(
        r"ApplyDirectionPlusAOverride\(roles,\s*outputs\).*?if\s*\(\s*roles\.z_airdodge_override_active\s*\).*?ApplyZAirdodgeOverride\(effective_directions,\s*outputs\);.*?if\s*\(\s*roles\.hard_up_b_active\s*\).*?ApplyHardUpBOverride\(effective_directions,\s*outputs\);.*?if\s*\(\s*directions\.cx\s*!=\s*0\s*&&\s*directions\.cy\s*!=\s*0\s*\).*?if\s*\(\s*roles\.null_modifier_active\s*\).*?ApplyNullOverride\(outputs\);",
        block,
        "RF9 null remains final after table, direction-plus-A, RF6, RF7, and C-stick ASDI",
        flags=re.DOTALL,
    )
    require(
        r"void\s+ApplyHardUpBOverride\(const\s+EffectiveDirectionState\s+&directions,\s*OutputState\s+&outputs\)\s*\{.*?directions\.left\s*==\s*directions\.right\s*\?\s*128\s*:\s*\(directions\.left\s*\?\s*77\s*:\s*179\).*?outputs\.leftStickY\s*=\s*172\s*;",
        source,
        "RF7 hard Up+B constants and horizontal policy",
        flags=re.DOTALL,
    )
    require(r"outputs\.leftStickX\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.x\s*;", source, "RF6 low-magnitude X")
    require(r"outputs\.leftStickY\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.y\s*;", source, "RF6 low-magnitude Y")
    require(
        r"void\s+ApplyNullOverride\(OutputState\s+&outputs\)\s*\{\s*outputs\.leftStickX\s*=\s*128\s*;\s*outputs\.leftStickY\s*=\s*128\s*;\s*outputs\.rightStickX\s*=\s*128\s*;\s*outputs\.rightStickY\s*=\s*128\s*;\s*\}",
        source,
        "RF9 nulls both sticks",
        flags=re.DOTALL,
    )
    if re.search(r"active_modifier_count\s*\+\+[^;]*null_modifier_active", source):
        fail("RF9 must not be part of modifier count logic")
    if re.search(r"SelectStickTable\s*\([^)]*null_modifier_active", source):
        fail("RF9 must not alter table selection arguments")
    if re.search(r"outputs\.(?!leftStickX|leftStickY|rightStickX|rightStickY)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf9", source):
        fail("RF9 must not drive game/dpad/menu outputs")
    if re.search(r"active_modifier_count\s*\+\+[^;]*inputs\.rf11", source):
        fail("RF11 must not be part of modifier count logic")
    if re.search(r"SelectStickTable\s*\([^)]*inputs\.rf11", source, flags=re.DOTALL):
        fail("RF11 must not alter table selection arguments")
    if re.search(r"outputs\.[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf11", source):
        fail("RF11 must not drive runtime outputs after GFW3 scratch")
    if re.search(r"const\s+bool\s+ls_to_dpad_active\s*=\s*inputs\.rf7\s*;", source):
        fail("RF7 must not activate LS->DPad")
    if re.search(r"force_up_active\s*=.*inputs\.rf7", source):
        fail("RF7 must not be included in forced-up aggregation")

    require(r"outputs\.rightStickRight\s*=\s*inputs\.rt4\s*;", source, "RT4 drives C-right")
    require(r"outputs\.rightStickUp\s*=\s*inputs\.rt5\s*;", source, "RT5 drives C-up")
    require(r"outputs\.dpadUp\s*=\s*inputs\.rt5\s*;", source, "nunchuk-C Up uses RT5")
    require(r"outputs\.dpadRight\s*=\s*inputs\.rt4\s*;", source, "nunchuk-C Right uses RT4")
    require(
        r"UpdateDirections\(\s*effective_directions\.left,\s*//\s*Left\s*\(LF3 with cancellation\)\s*effective_directions\.right,\s*//\s*Right\s*\(LF1 with cancellation\)\s*effective_directions\.down,\s*//\s*Down\s*\(LT6/LF5, suppressed by forced-Up\)\s*effective_directions\.up,\s*//\s*Up\s*\(RF5, LT2\+RF2, and LF4\+RF3 forced-Up\)\s*inputs\.rt3,\s*//\s*C-Left\s*inputs\.rt4,\s*//\s*C-Right\s*inputs\.rt2,\s*//\s*C-Down\s*inputs\.rt5,\s*//\s*C-Up",
        source,
        "UpdateDirections uses GFW3 effective LS directions and RT4/RT5 C-stick mapping",
        flags=re.DOTALL,
    )


def ensure_no_forbidden_tokens(source: str) -> None:
    lowered = source.lower()
    for token in FORBIDDEN_TOKENS:
        if token in lowered:
            fail(f"forbidden token present: {token}")


def main() -> int:
    try:
        source = load_source_text_with_generated_tables(ULTIMATE_PATH)
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
    print("lt1_role=L")
    print("lt3_role=L_plus_R")
    print("lt4_role=X2_MX2")
    print("lt5_role=X1_MX1")
    print("rf6_role=Z_plus_low_magnitude_override")
    print("z_role=rf6")
    print("r_role=rf16_or_lt3")
    print("y_role=rf10")
    print("forced_up_role=rf5_or_lt2_rf2_or_lf4_rf3")
    print("direction_plus_a_role=lt6_down_a_rf5_up_a")
    print("direction_plus_a_override_policy=hard_final_default_or_mode_default_then_rf6_low_override")
    print("y1_tilt1_special_composite=enabled")
    print("rt4_rt5_cstick_swap=enabled")
    print("rf9_null_modifier=left_and_right_sticks_with_rf4_exception")
    print("rt1_rf4_custom_modifier=enabled")
    print("rf4_rf2_minus41_modifier=enabled")
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
