#!/usr/bin/env python3
"""Read-only source/doc checker for identity-runtime Smash Box modifiers."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
RUNTIME_DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md"
ARTIFACT_PATH = REPO_ROOT / "docs" / "calibration" / "artifacts" / "glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "tilt_button_id_probe" / "GlyphUserProfilesUltimateMVP01.json"

BEGIN_MARKER = "// Senscope Glyph Smash Box runtime begin"
END_MARKER = "// Senscope Glyph Smash Box runtime end"

LT1_LOW_POINTS = (
    "{89, 89}",
    "{128, 79}",
    "{167, 89}",
    "{79, 128}",
    "{128, 128}",
    "{177, 128}",
    "{89, 167}",
    "{128, 177}",
    "{167, 167}",
)

TILT1_POINTS = (
    "{187, 47}",
    "{128, 47}",
    "{69, 47}",
    "{187, 128}",
    "{128, 128}",
    "{69, 128}",
    "{187, 209}",
    "{128, 209}",
    "{69, 209}",
)

Y1_TILT1_POINTS = (
    "{169, 99}",
    "{128, 99}",
    "{87, 99}",
    "{169, 128}",
    "{128, 128}",
    "{87, 128}",
    "{169, 157}",
    "{128, 157}",
    "{87, 157}",
)

MY1_TILT1_POINTS = (
    "{169, 179}",
    "{128, 179}",
    "{87, 179}",
    "{169, 169}",
    "{128, 169}",
    "{87, 169}",
    "{169, 77}",
    "{128, 77}",
    "{87, 77}",
)

MODE_DEFAULT_POINTS = (
    "{14, 87}",
    "{128, 87}",
    "{242, 87}",
    "{14, 169}",
    "{128, 169}",
    "{242, 169}",
    "{14, 169}",
    "{128, 169}",
    "{242, 169}",
)

MX1_POINTS = (
    "{78, 87}",
    "{128, 87}",
    "{178, 87}",
    "{78, 169}",
    "{128, 169}",
    "{178, 169}",
    "{78, 169}",
    "{128, 169}",
    "{178, 169}",
)

MX2_POINTS = (
    "{65, 87}",
    "{128, 87}",
    "{191, 87}",
    "{65, 169}",
    "{128, 169}",
    "{191, 169}",
    "{65, 169}",
    "{128, 169}",
    "{191, 169}",
)

MY1_POINTS = (
    "{14, 179}",
    "{128, 179}",
    "{242, 179}",
    "{14, 169}",
    "{128, 169}",
    "{242, 169}",
    "{14, 77}",
    "{128, 77}",
    "{242, 77}",
)

MTILT1_POINTS = (
    "{169, 88}",
    "{128, 88}",
    "{87, 88}",
    "{169, 169}",
    "{128, 169}",
    "{87, 169}",
    "{169, 168}",
    "{128, 168}",
    "{87, 168}",
)

MTILT2_POINTS = (
    "{96, 82}",
    "{128, 82}",
    "{160, 82}",
    "{96, 169}",
    "{128, 169}",
    "{160, 169}",
    "{96, 174}",
    "{128, 174}",
    "{160, 174}",
)

MTILT3_POINTS = (
    "{96, 86}",
    "{128, 86}",
    "{160, 86}",
    "{96, 169}",
    "{128, 169}",
    "{160, 169}",
    "{96, 170}",
    "{128, 170}",
    "{160, 170}",
)

LAYER_FLIPPER_POINTS = (
    "{169, 51}",
    "{128, 51}",
    "{87, 51}",
    "{169, 128}",
    "{128, 128}",
    "{87, 128}",
    "{169, 205}",
    "{128, 205}",
    "{87, 205}",
)

MLAYER_FLIPPER_POINTS = (
    "{169, 87}",
    "{128, 87}",
    "{87, 87}",
    "{169, 169}",
    "{128, 169}",
    "{87, 169}",
    "{169, 169}",
    "{128, 169}",
    "{87, 169}",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def require(pattern: str, text: str, label: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags=flags) is None:
        fail(f"missing source evidence: {label}")


def extract_marker_block(text: str) -> str:
    begin_count = text.count(BEGIN_MARKER)
    end_count = text.count(END_MARKER)
    if begin_count != 1 or end_count != 1:
        fail(f"expected exactly one marker pair, found begin={begin_count} end={end_count}")
    begin = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER, begin)
    if begin < 0 or end < 0 or end < begin:
        fail("runtime markers missing or out of order")
    return text[begin : end + len(END_MARKER)]


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        fail(f"missing profile file: {path.relative_to(REPO_ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"invalid JSON root in {path.relative_to(REPO_ROOT)}")
    return payload


def mode_ultimate(payload: dict[str, object], path: Path) -> dict[str, object]:
    raw_modes = payload.get("gameModeConfigs")
    if not isinstance(raw_modes, list):
        fail(f"missing gameModeConfigs list in {path.relative_to(REPO_ROOT)}")
    for mode in raw_modes:
        if isinstance(mode, dict) and mode.get("modeId") == "MODE_ULTIMATE":
            return mode
    fail(f"missing MODE_ULTIMATE in {path.relative_to(REPO_ROOT)}")
    return {}


def ensure_identity_profile_contract(path: Path) -> None:
    mode = mode_ultimate(load_json(path), path)
    remaps = mode.get("buttonRemapping")
    if not isinstance(remaps, list):
        fail(f"MODE_ULTIMATE.buttonRemapping must be a list in {path.relative_to(REPO_ROOT)}")

    required_self_activates = {"BTN_LT1", "BTN_LT4", "BTN_LT5", "BTN_RF11", "BTN_LF7", "BTN_LF8", "BTN_RF2", "BTN_RF3", "BTN_RF4"}
    observed_self_activates: set[str] = set()
    for index, remap in enumerate(remaps):
        if not isinstance(remap, dict):
            fail(f"buttonRemapping[{index}] must be object in {path.relative_to(REPO_ROOT)}")
        physical = remap.get("physicalButton")
        activates = remap.get("activates")
        if not isinstance(physical, str) or not physical:
            fail(f"buttonRemapping[{index}] missing physicalButton in {path.relative_to(REPO_ROOT)}")
        if not isinstance(activates, str) or not activates:
            fail(f"buttonRemapping[{index}] missing activates in {path.relative_to(REPO_ROOT)}")
        if activates != physical:
            fail(f"semantic remap present in MODE_ULTIMATE {path.relative_to(REPO_ROOT)}: {physical}->{activates}")
        if physical in required_self_activates:
            observed_self_activates.add(physical)

    missing_self_activates = sorted(required_self_activates - observed_self_activates)
    if missing_self_activates:
        fail(
            "missing required explicit self-activates in "
            f"{path.relative_to(REPO_ROOT)}: {', '.join(missing_self_activates)}"
        )

    socd_pairs = mode.get("socdPairs")
    if not isinstance(socd_pairs, list):
        fail(f"MODE_ULTIMATE.socdPairs must be a list in {path.relative_to(REPO_ROOT)}")
    forbidden_socd_inputs = {"BTN_LT1", "BTN_LT4", "BTN_LT5", "BTN_RF11", "BTN_LF7", "BTN_LF8", "BTN_RF2", "BTN_RF3", "BTN_RF4"}
    for index, pair in enumerate(socd_pairs):
        if not isinstance(pair, dict):
            fail(f"socdPairs[{index}] must be object in {path.relative_to(REPO_ROOT)}")
        left = pair.get("buttonDir1")
        right = pair.get("buttonDir2")
        if left in forbidden_socd_inputs or right in forbidden_socd_inputs:
            fail(
                "LT1/LT4/LT5/RF11 must not appear in MODE_ULTIMATE.socdPairs in "
                f"{path.relative_to(REPO_ROOT)}"
            )


def read_runtime_doc() -> str:
    if not RUNTIME_DOC_PATH.exists():
        fail(f"missing runtime doc: {RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    require(r"LT3\s*=\s*L", text, "runtime doc LT3=L")
    require(r"LT5\s*=\s*Z", text, "runtime doc LT5=Z")
    require(r"RF11\s*=\s*Z", text, "runtime doc RF11=Z alias")
    require(
        r"RF11.*((alias|identic|same).*LT5|LT5.*(alias|identic|same))",
        text,
        "runtime doc RF11 aliases LT5 behavior",
        flags=re.IGNORECASE,
    )
    require(r"LT4\s*=\s*X1", text, "runtime doc LT4=X1")
    require(r"LT1\s*=\s*X2", text, "runtime doc LT1=X2")
    require(r"RF15\s*=\s*Up\+A", text, "runtime doc RF15 Up+A alias")
    require(r"RF9\s*=\s*null modifier", text, "runtime doc RF9 null modifier role")
    require(r"RF9.*final analog.*128,128", text, "runtime doc RF9 final analog override", flags=re.IGNORECASE)
    require(r"Y2/MY2.*scratched|scratched.*Y2/MY2", text, "runtime doc marks Y2/MY2 scratched", flags=re.IGNORECASE)
    require(r"Y1\+Tilt1.*special", text, "runtime doc Y1+Tilt1 special composite", flags=re.IGNORECASE)
    require(r"LF8\s*=\s*layer-left button", text, "runtime doc LF8 layer-left role")
    require(r"LF7\s*=\s*layer-right button", text, "runtime doc LF7 layer-right role")
    require(r"RF4.*flipper", text, "runtime doc RF4 layered flipper role", flags=re.IGNORECASE)
    require(r"RF3.*B", text, "runtime doc RF3 layered B role")
    require(r"RF2.*forced Up|forced Up.*RF2", text, "runtime doc RF2 layered forced-Up role", flags=re.IGNORECASE)
    require(r"RT4\s*=\s*C-Right", text, "runtime doc RT4 C-right")
    require(r"RT5\s*=\s*C-Up", text, "runtime doc RT5 C-up")
    require(r"`?RT1`?\s*remains", text, "runtime doc RT1 remains Z")
    require(r"RF16\s*remains\s+runtime-owned\s+`?R`?|`?RF16`?\s+remains\s+`?R`?", text, "runtime doc RF16 remains R")

    return text


def ensure_runtime_shapes(source: str, block: str) -> None:
    # Core game output roles.
    require(
        r"outputs\.a\s*=\s*inputs\.rf1\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        source,
        "A role includes RF15 alias",
    )
    require(r"outputs\.buttonL\s*=\s*inputs\.lt3\s*;", source, "LT3 drives L")
    require(r"outputs\.triggerLDigital\s*=\s*inputs\.lt3\s*;", source, "LT3 drives L digital carrier")
    require(
        r"outputs\.buttonR\s*=\s*inputs\.rt1\s*\|\|\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        source,
        "RT1/LT5/RF11 shared Z carrier",
    )
    require(r"outputs\.triggerRDigital\s*=\s*inputs\.rf16\s*;", source, "RF16 remains R carrier")
    require(r"const\s+bool\s+null_modifier_active\s*=\s*inputs\.rf9\s*;", block, "RF9 null modifier input")
    require(
        r"const\s+bool\s+z_airdodge_override_active\s*=\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        block,
        "LT5/RF11 shared low-magnitude override alias",
    )
    require(r"const\s+bool\s+x1_active\s*=\s*inputs\.lt4\s*;", block, "X1 input is LT4")
    require(r"const\s+bool\s+x2_active\s*=\s*inputs\.lt1\s*;", block, "X2 input is LT1")
    require(r"const\s+bool\s+layer_left_active\s*=\s*inputs\.lf8\s*;", source, "LF8 layer-left source")
    require(r"const\s+bool\s+layer_right_active\s*=\s*inputs\.lf7\s*;", source, "LF7 layer-right source")
    require(r"const\s+bool\s+layer_active\s*=\s*layer_left_active\s*\|\|\s*layer_right_active\s*;", source, "layer_active aggregation")
    require(r"const\s+bool\s+layer_rf2_force_up_active\s*=\s*layer_active\s*&&\s*inputs\.rf2\s*;", source, "layered RF2 forced-Up source")
    if re.search(r"const\s+bool\s+x1_active\s*=\s*inputs\.lt5\s*;", block):
        fail("stale x1_active=inputs.lt5 runtime shape must be removed")
    if re.search(r"const\s+bool\s+x2_active\s*=\s*inputs\.lt4\s*;", block):
        fail("stale x2_active=inputs.lt4 runtime shape must be removed")
    if re.search(r"const\s+bool\s+z_airdodge_override_active\s*=\s*inputs\.lt1\s*\|\|\s*inputs\.rf11\s*;", block):
        fail("stale LT1/RF11 Z-airdodge activation shape must be removed")

    # Remove old LT1/LT3/Y2 shapes.
    if "outputs.buttonL = inputs.lt1;" in source:
        fail("LT1 must no longer drive L")
    if "outputs.triggerLDigital = inputs.lt1;" in source:
        fail("LT1 must no longer drive L digital carrier")
    if "outputs.buttonR = inputs.rt1;" in source:
        fail("Z carrier must include LT5 in addition to RT1")
    if "outputs.buttonR = inputs.rt1 || inputs.lt1 || inputs.rf11;" in source:
        fail("stale RT1/LT1/RF11 Z carrier must be removed")
    if re.search(r"\by2_active\b", source):
        fail("Y2 active runtime path must be removed")
    if "EffectiveModifier::Y2" in source:
        fail("Y2 effective modifier path must be removed")
    if "kY2Table" in source or "kMY2Table" in source:
        fail("Y2/MY2 runtime table constants should not remain in source")

    # Modifier composition excludes Y2.
    require(r"const\s+bool\s+y1_active\s*=\s*inputs\.lt2\s*;", block, "Y1 modifier input")
    if re.search(r"inputs\.lt3[^\n]*Y2|Y2[^\n]*inputs\.lt3", block, flags=re.IGNORECASE):
        fail("LT3 must not be consumed as Y2 modifier input")

    require(
        r"outputs\.b\s*=\s*inputs\.rf5\s*\|\|\s*inputs\.lf4\s*\|\|\s*\(\s*layer_active\s*&&\s*inputs\.rf3\s*\)\s*;",
        source,
        "layered RF3 contributes to B only under layer_active",
    )
    require(r"outputs\.x\s*=\s*inputs\.rf2\s*&&\s*!layer_active\s*;", source, "RF2->X gated by !layer_active")

    require(
        r"const\s+int8_t\s+horizontal_axis\s*=\s*ResolveHorizontalAxis\(inputs\.lf3,\s*inputs\.lf1,\s*layer_left_active,\s*layer_right_active\)\s*;",
        source,
        "effective horizontal direction includes LF8/LF7",
    )
    require(r"const\s+bool\s+tilt1_pressed\s*=\s*inputs\.rf3\s*&&\s*!layer_active\s*;", block, "RF3 Tilt1 gated by !layer_active")
    require(r"const\s+bool\s+tilt2_pressed\s*=\s*inputs\.rf4\s*&&\s*!layer_active\s*;", block, "RF4 Tilt2 gated by !layer_active")
    require(r"const\s+bool\s+rf4_layer_flipper_active\s*=\s*layer_active\s*&&\s*inputs\.rf4\s*;", block, "layered RF4 flipper active")
    require(
        r"SelectStickTable\(\s*mode_active,\s*x1_active,\s*x2_active,\s*y1_active,\s*rf4_layer_flipper_active,\s*tilt1_effective,\s*tilt2_effective,\s*tilt3_effective",
        source,
        "table selection includes layered RF4 flipper modifier",
        flags=re.DOTALL,
    )

    require(r"constexpr\s+StickPoint\s+kLayerFlipperTable\[9\]", source, "layer flipper table declaration")
    for point in LAYER_FLIPPER_POINTS:
        if point not in source:
            fail(f"missing layer RF4 flipper point: {point}")
    require(r"constexpr\s+StickPoint\s+kMLayerFlipperTable\[9\]", source, "mode layer flipper table declaration")
    for point in MLAYER_FLIPPER_POINTS:
        if point not in source:
            fail(f"missing mode layer RF4 flipper point: {point}")

    # Tilt1 table update and Y1+Tilt1 special composite tables.
    require(r"constexpr\s+StickPoint\s+kTilt1Table\[9\]", source, "Tilt1 table declaration")
    for point in TILT1_POINTS:
        if point not in source:
            fail(f"missing Tilt1 point: {point}")

    require(r"constexpr\s+StickPoint\s+kY1Tilt1Table\[9\]", source, "Y1+Tilt1 table declaration")
    for point in Y1_TILT1_POINTS:
        if point not in source:
            fail(f"missing Y1+Tilt1 point: {point}")

    require(r"constexpr\s+StickPoint\s+kMY1Tilt1Table\[9\]", source, "Mode Y1+Tilt1 table declaration")
    for point in MY1_TILT1_POINTS:
        if point not in source:
            fail(f"missing Mode Y1+Tilt1 point: {point}")

    require(r"constexpr\s+StickPoint\s+kModeDefaultTable\[9\]", source, "Mode default table declaration")
    for point in MODE_DEFAULT_POINTS:
        if point not in source:
            fail(f"missing Mode default point: {point}")

    require(r"constexpr\s+StickPoint\s+kMX1Table\[9\]", source, "MX1 table declaration")
    for point in MX1_POINTS:
        if point not in source:
            fail(f"missing MX1 point: {point}")

    require(r"constexpr\s+StickPoint\s+kMX2Table\[9\]", source, "MX2 table declaration")
    for point in MX2_POINTS:
        if point not in source:
            fail(f"missing MX2 point: {point}")

    require(r"constexpr\s+StickPoint\s+kMY1Table\[9\]", source, "MY1 table declaration")
    for point in MY1_POINTS:
        if point not in source:
            fail(f"missing MY1 point: {point}")

    require(r"constexpr\s+StickPoint\s+kMTilt1Table\[9\]", source, "MTilt1 table declaration")
    for point in MTILT1_POINTS:
        if point not in source:
            fail(f"missing MTilt1 point: {point}")

    require(r"constexpr\s+StickPoint\s+kMTilt2Table\[9\]", source, "MTilt2 table declaration")
    for point in MTILT2_POINTS:
        if point not in source:
            fail(f"missing MTilt2 point: {point}")

    require(r"constexpr\s+StickPoint\s+kMTilt3Table\[9\]", source, "MTilt3 table declaration")
    for point in MTILT3_POINTS:
        if point not in source:
            fail(f"missing MTilt3 point: {point}")

    require(
        r"const\s+bool\s+y1_tilt1_special_active\s*=\s*y1_active\s*&&\s*tilt1_effective\s*&&\s*!x1_active\s*&&\s*!x2_active\s*&&\s*!tilt2_effective\s*&&\s*!tilt3_effective\s*;",
        source,
        "Y1+Tilt1 special composite gating",
    )
    require(
        r"if\s*\(\s*y1_tilt1_special_active\s*\)\s*\{\s*return\s+mode_active\s*\?\s*kMY1Tilt1Table\s*:\s*kY1Tilt1Table\s*;",
        source,
        "Y1+Tilt1 special composite selection",
        flags=re.DOTALL,
    )

    # LT1 low-magnitude table exists.
    require(r"constexpr\s+StickPoint\s+kLt1LowMagnitudeTable\[9\]", source, "LT1 low table declaration")
    for point in LT1_LOW_POINTS:
        if point not in source:
            fail(f"missing LT1 low-magnitude point: {point}")

    # LT5 hard final override ordering.
    require(r"if\s*\(\s*direction_plus_a_active\s*\)", block, "direction-plus-A override block")
    require(r"if\s*\(\s*z_airdodge_override_active\s*\)", block, "LT5/RF11 hard override block")
    require(r"if\s*\(\s*null_modifier_active\s*\)", block, "RF9 null override block")
    require(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*z_airdodge_override_active\s*\)\s*\{.*?\}\s*\}\s*if\s*\(\s*null_modifier_active\s*\)\s*\{",
        block,
        "RF9 override occurs after LT5/RF11 and direction-plus-A overrides",
        flags=re.DOTALL,
    )
    require(r"outputs\.leftStickX\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.x\s*;", block, "LT1 final X override")
    require(r"outputs\.leftStickY\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.y\s*;", block, "LT1 final Y override")
    require(r"outputs\.leftStickX\s*=\s*128\s*;", block, "RF9 final X override")
    require(r"outputs\.leftStickY\s*=\s*128\s*;", block, "RF9 final Y override")

    # LS->DPad keeps analog centering and suppresses LT5 low-table override in that branch.
    require(
        r"if\s*\(\s*ls_to_dpad_active\s*\)\s*\{\s*const\s+StickPoint\s+center\s*=\s*mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;\s*outputs\.leftStickX\s*=\s*center\.x\s*;\s*outputs\.leftStickY\s*=\s*center\.y\s*;\s*\}\s*else\s*\{",
        block,
        "LS->DPad center branch with else-path override",
        flags=re.DOTALL,
    )
    if re.search(r"active_modifier_count\s*\+\+[^;]*null_modifier_active", source):
        fail("RF9 must not be counted as modifier")
    if re.search(r"SelectStickTable\s*\([^)]*null_modifier_active", source):
        fail("RF9 must not affect table selection")
    if re.search(r"outputs\.(?!leftStickX|leftStickY)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf9", source):
        fail("RF9 must not directly drive game/dpad/right-stick outputs")
    if re.search(r"active_modifier_count\s*\+\+[^;]*inputs\.rf11", source):
        fail("RF11 must not be counted as modifier")
    if re.search(r"SelectStickTable\s*\([^)]*inputs\.rf11", source, flags=re.DOTALL):
        fail("RF11 must not affect table selection")
    if re.search(r"outputs\.(?!buttonR)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf11", source):
        fail("RF11 must not drive outputs other than the shared Z carrier")

    # RF15 aliases RF12 across forced-up/direction-plus-A and LT5 direction resolution.
    require(
        r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*\|\|\s*layer_rf2_force_up_active\s*;",
        source,
        "forced-up includes layered RF2",
    )
    require(
        r"const\s+bool\s+up_a_active\s*=\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        block,
        "direction-plus-A up input includes RF15",
    )
    require(
        r"const\s+bool\s+lt1_force_up_active\s*=\s*force_up_active\s*;",
        block,
        "LT5 low-table forced-up includes shared layered forced-up sources",
    )

    # C-stick right/up swap and nunchuk-C passthrough consistency.
    require(r"outputs\.rightStickRight\s*=\s*inputs\.rt4\s*;", source, "RT4 drives C-right")
    require(r"outputs\.rightStickUp\s*=\s*inputs\.rt5\s*;", source, "RT5 drives C-up")
    require(r"outputs\.dpadUp\s*=\s*inputs\.rt5\s*;", source, "nunchuk-C Up uses RT5")
    require(r"outputs\.dpadRight\s*=\s*inputs\.rt4\s*;", source, "nunchuk-C Right uses RT4")

    # Direction-plus-A still part of A output and not modifiers.
    if re.search(r"SelectStickTable\s*\([^)]*inputs\.(lt6|rf12)", source, flags=re.DOTALL):
        fail("LT6/RF12 must not enter modifier selection")


def main() -> int:
    if not SOURCE_PATH.exists():
        print("status=FAIL")
        print(f"failure=missing_source:{SOURCE_PATH.relative_to(REPO_ROOT)}")
        return 1

    source = SOURCE_PATH.read_text(encoding="utf-8")

    try:
        block = extract_marker_block(source)
        read_runtime_doc()
        ensure_identity_profile_contract(ARTIFACT_PATH)
        ensure_identity_profile_contract(FIXTURE_PATH)
        ensure_runtime_shapes(source, block)
    except AssertionError as exc:
        print("status=FAIL")
        print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
    print(f"runtime_doc={RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    print("markers=present")
    print("forced_up_role=rf6_or_rf12_or_rf15_or_layered_rf2")
    print("direction_plus_a_role=lt6_down_a_rf12_or_rf15_up_a")
    print("lt3_role=L")
    print("lt5_rf11_role=Z_plus_low_magnitude_override_alias")
    print("z_button_role=rt1_or_lt5_or_rf11_shared_buttonR_carrier")
    print("r_button_role=rf16")
    print("y1_tilt1_special_composite=enabled")
    print("rt4_rt5_cstick_swap=enabled")
    print("rf9_null_modifier=enabled")
    print("lt1_lt4_lt5_rf11_profile_socd_semantic_remap_conflicts=absent")
    print("y2_my2_runtime_role=scratched_inactive")
    print("ls_to_dpad_role=rf7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
