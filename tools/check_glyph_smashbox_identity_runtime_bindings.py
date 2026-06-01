#!/usr/bin/env python3
"""Read-only checker for identity-baseline Smash Box runtime bindings."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "docs" / "calibration" / "artifacts" / "glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "tilt_button_id_probe" / "GlyphUserProfilesUltimateMVP01.json"
RUNTIME_DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md"
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"

ROLE_LINES = (
    "`RF1 = A`",
    "`LT6 = Down+A`",
    "`RF12 = Up+A`",
    "`RF15 = Up+A`",
    "`RF5 = B`",
    "`LF4 = B`",
    "`RF2 = X`",
    "`RF10 = Y`",
    "`LT5 = Z`",
    "`RF11 = Z`",
    "`RT1 = Z`",
    "`LT3 = L`",
    "`RF16 = R`",
    "`RF8 = Mode`",
    "`RF9 = null modifier`",
    "`LT4 = X1`",
    "`LT1 = X2`",
    "`LT2 = Y1`",
    "`RF7 = LS->DPad`",
    "`RF6 = forced Up`",
    "`RF3 = Tilt1`",
    "`RF4 = Tilt2`",
    "`RF3 + RF4 = Tilt3`",
    "`LF8 = layer-left button`",
    "`LF7 = layer-right button`",
)

SOURCE_ANCHORS = (
    "inputs.rf8",
    "inputs.rf9",
    "inputs.lt5",
    "inputs.lt4",
    "inputs.lt2",
    "inputs.rf7",
    "inputs.rf6",
    "inputs.rf12",
    "inputs.rf15",
    "inputs.lt6",
    "inputs.lt1",
    "inputs.rf11",
    "inputs.lt3",
    "inputs.rf16",
    "inputs.rf3",
    "inputs.rf4",
    "kLt1LowMagnitudeTable",
    "kY1Tilt1Table",
    "kMY1Tilt1Table",
)

RUNTIME_REQUIRED_SELF_ACTIVATES = (
    "BTN_RT1",
    "BTN_RF1",
    "BTN_RF2",
    "BTN_RF10",
    "BTN_RF6",
    "BTN_RF12",
    "BTN_RF15",
    "BTN_RF11",
    "BTN_LT1",
    "BTN_LT3",
    "BTN_LT6",
    "BTN_LF4",
    "BTN_RF5",
    "BTN_LF3",
    "BTN_LF1",
    "BTN_LF2",
    "BTN_RF7",
    "BTN_RF8",
    "BTN_RF9",
    "BTN_LF7",
    "BTN_LF8",
    "BTN_LT5",
    "BTN_LT4",
    "BTN_LT2",
    "BTN_RF3",
    "BTN_RF4",
    "BTN_RT3",
    "BTN_RT5",
    "BTN_RT2",
    "BTN_RT4",
    "BTN_RF16",
    "BTN_MB4",
    "BTN_MB5",
    "BTN_MB6",
    "BTN_MB7",
)

EMPTY_NO_OUTPUT_INPUTS = (
    "inputs.lf6",
    "inputs.rf13",
    "inputs.rf14",
    "inputs.mb1",
    "inputs.mb2",
    "inputs.mb3",
)

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

LAYER_NORMAL_X_POINTS = (
    "{87, 51}",
    "{128, 51}",
    "{169, 51}",
    "{87, 128}",
    "{128, 128}",
    "{169, 128}",
    "{87, 205}",
    "{128, 205}",
    "{169, 205}",
)

MLAYER_NORMAL_X_POINTS = (
    "{87, 87}",
    "{128, 87}",
    "{169, 87}",
    "{87, 169}",
    "{128, 169}",
    "{169, 169}",
    "{87, 169}",
    "{128, 169}",
    "{169, 169}",
)

Y1_LAYER_NORMAL_X_POINTS = (
    "{87, 99}",
    "{128, 99}",
    "{169, 99}",
    "{87, 128}",
    "{128, 128}",
    "{169, 128}",
    "{87, 157}",
    "{128, 157}",
    "{169, 157}",
)

MY1_LAYER_NORMAL_X_POINTS = (
    "{87, 179}",
    "{128, 179}",
    "{169, 179}",
    "{87, 169}",
    "{128, 169}",
    "{169, 169}",
    "{87, 77}",
    "{128, 77}",
    "{169, 77}",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        fail(f"missing file: {path.relative_to(REPO_ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be object: {path.relative_to(REPO_ROOT)}")
    return payload


def get_ultimate_mode(payload: dict[str, object], path: Path) -> dict[str, object]:
    configs = payload.get("gameModeConfigs")
    if not isinstance(configs, list):
        fail(f"missing gameModeConfigs list in {path.relative_to(REPO_ROOT)}")

    for config in configs:
        if isinstance(config, dict) and config.get("modeId") == "MODE_ULTIMATE":
            return config

    fail(f"missing MODE_ULTIMATE in {path.relative_to(REPO_ROOT)}")
    return {}


def explicit_self_activate_map(mode_config: dict[str, object], path: Path) -> dict[str, str]:
    remaps = mode_config.get("buttonRemapping")
    if not isinstance(remaps, list):
        fail(f"MODE_ULTIMATE.buttonRemapping must be a list in {path.relative_to(REPO_ROOT)}")

    mapping: dict[str, str] = {}
    for index, remap in enumerate(remaps):
        if not isinstance(remap, dict):
            fail(f"buttonRemapping[{index}] must be an object in {path.relative_to(REPO_ROOT)}")
        physical = remap.get("physicalButton")
        if not isinstance(physical, str) or not physical:
            fail(f"buttonRemapping[{index}] missing physicalButton in {path.relative_to(REPO_ROOT)}")
        if physical == "BTN_UNSPECIFIED":
            fail(f"buttonRemapping[{index}] uses forbidden BTN_UNSPECIFIED in {path.relative_to(REPO_ROOT)}")
        if physical in mapping:
            fail(
                "duplicate physicalButton entries in "
                f"{path.relative_to(REPO_ROOT)}: {physical}"
            )

        if "activates" not in remap:
            fail(f"buttonRemapping[{index}] must include activates in {path.relative_to(REPO_ROOT)}")
        activates = remap.get("activates")
        if not isinstance(activates, str) or not activates:
            fail(f"buttonRemapping[{index}] activates must be a string in {path.relative_to(REPO_ROOT)}")
        if activates == "BTN_UNSPECIFIED":
            fail(
                f"buttonRemapping[{index}] uses forbidden activates BTN_UNSPECIFIED in {path.relative_to(REPO_ROOT)}"
            )
        if activates != physical:
            fail(
                "MODE_ULTIMATE explicit identity violation in "
                f"{path.relative_to(REPO_ROOT)}: {physical} -> {activates}"
            )
        mapping[physical] = activates

    return mapping


def ensure_role_inputs_not_in_socd_pairs(mode_config: dict[str, object], path: Path) -> None:
    socd_pairs = mode_config.get("socdPairs")
    if not isinstance(socd_pairs, list):
        fail(f"MODE_ULTIMATE.socdPairs must be a list in {path.relative_to(REPO_ROOT)}")

    forbidden_socd_inputs = {"BTN_LT1", "BTN_LT4", "BTN_LT5", "BTN_RF11", "BTN_LF7", "BTN_LF8", "BTN_RF2", "BTN_RF3", "BTN_RF4"}
    for index, pair in enumerate(socd_pairs):
        if not isinstance(pair, dict):
            fail(f"socdPairs[{index}] must be an object in {path.relative_to(REPO_ROOT)}")
        left = pair.get("buttonDir1")
        right = pair.get("buttonDir2")
        if left in forbidden_socd_inputs or right in forbidden_socd_inputs:
            fail(
                "LT1/LT4/LT5/RF11/LF7/LF8/RF2/RF3/RF4 must not appear in MODE_ULTIMATE.socdPairs in "
                f"{path.relative_to(REPO_ROOT)}"
            )


def require_runtime_doc() -> str:
    if not RUNTIME_DOC_PATH.exists():
        fail(f"missing runtime doc: {RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    for role_line in ROLE_LINES:
        if role_line not in text:
            fail(f"missing runtime role line: {role_line}")

    if re.search(r"Y2/MY2.*scratched|scratched.*Y2/MY2", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must state Y2/MY2 scratched/inactive")
    if re.search(r"RF15\s*=\s*Up\+A", text) is None:
        fail("runtime doc must state RF15 aliases RF12 as Up+A")
    if re.search(r"LT4\s*=\s*X1", text) is None:
        fail("runtime doc must state LT4 is X1")
    if re.search(r"LT1\s*=\s*X2", text) is None:
        fail("runtime doc must state LT1 is X2")
    if re.search(r"LT5\s*=\s*Z", text) is None:
        fail("runtime doc must state LT5 is Z-airdodge")
    if re.search(r"RF11\s*=\s*Z", text) is None:
        fail("runtime doc must state RF11 aliases LT5 for Z-airdodge behavior")
    if re.search(r"RF11.*((alias|identic|same).*LT5|LT5.*(alias|identic|same))", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must state RF11 behaves identically to LT5 for Z-airdodge low-magnitude override")
    if re.search(r"RF9\s*=\s*null modifier", text) is None:
        fail("runtime doc must state RF9 is null modifier")
    if re.search(r"RF9.*final analog.*128,128", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must state RF9 final analog override to (128,128)")
    if re.search(r"Y1\+Tilt1.*special", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document Y1+Tilt1 special composite")
    if re.search(r"LF8\s*=\s*layer-left button", text) is None:
        fail("runtime doc must document LF8 as layer-left button")
    if re.search(r"LF7\s*=\s*layer-right button", text) is None:
        fail("runtime doc must document LF7 as layer-right button")
    if re.search(r"RF4.*flipper", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document RF4 layered flipper behavior")
    if re.search(r"RF3.*B", text) is None:
        fail("runtime doc must document RF3 layered B behavior")
    if re.search(r"RF3.*normal[\s-]*x", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document RF3 layered normal-x behavior")
    if re.search(r"RF4.*wins.*RF3|RF3.*RF4.*wins", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document RF4 layered precedence over RF3 normal-x")
    if re.search(r"LF4.*layer sub-?mode|layer sub-?mode.*LF4", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document LF4 layer sub-mode behavior")
    if re.search(r"LF4.*LT2.*suppres|suppres.*LT2.*LF4", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document LF4-held LT2/Y1 suppression")
    if re.search(r"LF4.*LT2.*sub-?mode|sub-?mode.*LF4.*LT2", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document LF4+LT2 LF4 sub-mode activation")
    if re.search(r"RF2.*forced Up|forced Up.*RF2", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document RF2 pure-layer forced-Up behavior")
    if re.search(r"LF4.*RF2.*X|RF2.*LF4.*X", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document LF4 sub-mode RF2 -> X behavior")
    if re.search(r"LF4.*RF3.*forced Up|RF3.*LF4.*forced Up", text, flags=re.IGNORECASE) is None:
        fail("runtime doc must document LF4 sub-mode RF3 forced-Up behavior")
    if re.search(r"RT4\s*=\s*C-Right", text) is None or re.search(r"RT5\s*=\s*C-Up", text) is None:
        fail("runtime doc must document RT4/RT5 C-stick swap")
    if "RT1 remains runtime-owned `Z`" not in text and "RT1 remains" not in text and "`RT1` remains" not in text:
        fail("runtime doc must state RT1 remains Z")
    if re.search(r"`?RF16`?\s+remains\s+`?R`?", text) is None:
        fail("runtime doc must state RF16 remains R")
    if "standalone `LT3 -> Tilt3` behavior is historical only" not in text:
        fail("runtime doc must mark standalone LT3->Tilt3 as historical only")
    if "no standalone D-pad" not in text:
        fail("runtime doc must document no standalone D-pad policy")

    return text


def require_runtime_source() -> str:
    if not SOURCE_PATH.exists():
        fail(f"missing runtime source: {SOURCE_PATH.relative_to(REPO_ROOT)}")
    text = SOURCE_PATH.read_text(encoding="utf-8")

    for anchor in SOURCE_ANCHORS:
        if anchor not in text:
            fail(f"missing runtime source anchor: {anchor}")

    expected_source_lines = (
        (
            "outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12 || inputs.rf15;",
            "runtime source must assign A from RF1 or LT6 or RF12 or RF15",
        ),
        (
            "outputs.b = inputs.rf5 || inputs.lf4 || (layer_direction_active && !inputs.lf4 && inputs.rf3);",
            "runtime source must assign layered RF3 to B only in pure LF7/LF8 layer with LF4 released",
        ),
        (
            "outputs.x = inputs.rf2 && (!layer_direction_active || inputs.lf4);",
            "runtime source must map RF2->X outside pure layer and inside LF4 sub-mode",
        ),
        ("outputs.y = inputs.rf10;", "runtime source must assign RF10 to Y"),
        ("outputs.buttonL = inputs.lt3;", "runtime source must assign LT3 to L button"),
        (
            "outputs.buttonR = inputs.rt1 || inputs.lt5 || inputs.rf11;",
            "runtime source must assign RT1/LT5/RF11 shared Z carrier",
        ),
        ("outputs.triggerLDigital = inputs.lt3;", "runtime source must assign LT3 to GameCube L carrier"),
        ("outputs.triggerRDigital = inputs.rf16;", "runtime source must assign RF16 to GameCube R carrier"),
        ("outputs.rightStickRight = inputs.rt4;", "runtime source must map RT4 to C-right"),
        ("outputs.rightStickUp = inputs.rt5;", "runtime source must map RT5 to C-up"),
        ("const bool null_modifier_active = inputs.rf9;", "runtime source must read RF9 null modifier input"),
        ("const bool x1_active = inputs.lt4;", "runtime source must assign LT4 to X1"),
        ("const bool x2_active = inputs.lt1;", "runtime source must assign LT1 to X2"),
        ("const bool layer_left_active = inputs.lf8;", "runtime source must read LF8 layer-left input"),
        ("const bool layer_right_active = inputs.lf7;", "runtime source must read LF7 layer-right input"),
        ("const bool layer_direction_active = layer_left_active || layer_right_active;", "runtime source must define layer_direction_active from LF8/LF7"),
        ("const bool lf4_submode_active = inputs.lf4 && (layer_direction_active || inputs.lt2);", "runtime source must define LF4 sub-mode activation from LF4 and (layer direction or LT2)"),
        ("const bool layer_transform_active = layer_direction_active || lf4_submode_active;", "runtime source must define layer_transform_active"),
        ("const bool pure_layer_rf2_force_up_active = layer_direction_active && !inputs.lf4 && inputs.rf2;", "runtime source must define pure-layer RF2 forced-Up"),
        ("const bool lf4_submode_rf3_force_up_active = lf4_submode_active && inputs.rf3;", "runtime source must define LF4-submode RF3 forced-Up"),
        ("const bool y1_active = inputs.lt2 && !inputs.lf4;", "runtime source must suppress Y1 while LF4 is held"),
    )
    for line, message in expected_source_lines:
        if line not in text:
            fail(message)

    forbidden_lines = (
        "outputs.buttonL = inputs.lt1;",
        "outputs.buttonR = inputs.rt1;",
        "outputs.buttonR = inputs.rt1 || inputs.lt1;",
        "outputs.buttonR = inputs.rt1 || inputs.lt1 || inputs.rf11;",
        "outputs.triggerLDigital = inputs.lt1;",
        "outputs.y = inputs.rf6;",
        "outputs.modY = inputs.lt2;",
        "outputs.modX = inputs.lt1;",
        "outputs.buttonR = inputs.rf3;",
        "outputs.triggerLDigital = inputs.lf4;",
        "outputs.triggerRDigital = inputs.rf5;",
        "outputs.triggerRDigital = inputs.rf12;",
        "outputs.rightStickRight = inputs.rt5;",
        "outputs.rightStickUp = inputs.rt4;",
        "const bool x1_active = inputs.lt5;",
        "const bool x2_active = inputs.lt4;",
    )
    for line in forbidden_lines:
        if line in text:
            fail(f"forbidden runtime source line present: {line}")

    if "outputs.modY = false;" not in text:
        fail("runtime source must neutralize modY for LT2 Y1-only policy")

    if re.search(r"\by2_active\b", text):
        fail("runtime source must not keep y2_active")
    if "EffectiveModifier::Y2" in text:
        fail("runtime source must not keep Y2 effective modifier path")
    if "kY2Table" in text or "kMY2Table" in text:
        fail("runtime source must not keep runtime-owned Y2/MY2 table constants")

    if re.search(r"inputs\.lt3[^\n]*y2|y2[^\n]*inputs\.lt3", text, flags=re.IGNORECASE):
        fail("runtime source must not use inputs.lt3 as Y2")

    for point in LT1_LOW_POINTS:
        if point not in text:
            fail(f"runtime source missing LT1 low-magnitude point: {point}")

    for point in TILT1_POINTS:
        if point not in text:
            fail(f"runtime source missing Tilt1 point: {point}")

    for point in Y1_TILT1_POINTS:
        if point not in text:
            fail(f"runtime source missing Y1+Tilt1 point: {point}")

    for point in MY1_TILT1_POINTS:
        if point not in text:
            fail(f"runtime source missing Mode Y1+Tilt1 point: {point}")

    if re.search(
        r"const\s+bool\s+y1_tilt1_special_active\s*=\s*y1_active\s*&&\s*tilt1_effective\s*&&\s*!x1_active\s*&&\s*!x2_active\s*&&\s*!tilt2_effective\s*&&\s*!tilt3_effective\s*;",
        text,
    ) is None:
        fail("runtime source must gate Y1+Tilt1 special composite to Y1+Tilt1 only")
    if re.search(
        r"if\s*\(\s*y1_tilt1_special_active\s*\)\s*\{\s*return\s+mode_active\s*\?\s*kMY1Tilt1Table\s*:\s*kY1Tilt1Table\s*;",
        text,
        flags=re.DOTALL,
    ) is None:
        fail("runtime source must select Y1+Tilt1 special composite tables")

    if re.search(
        r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*\|\|\s*pure_layer_rf2_force_up_active\s*\|\|\s*lf4_submode_rf3_force_up_active\s*;",
        text,
    ) is None:
        fail("runtime source must include pure-layer RF2 and LF4-submode RF3 in forced-up logic")
    if re.search(
        r"const\s+bool\s+up_a_active\s*=\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        text,
    ) is None:
        fail("runtime source must include RF15 in Up+A logic")
    if re.search(
        r"const\s+bool\s+lt1_force_up_active\s*=\s*force_up_active\s*;",
        text,
    ) is None:
        fail("runtime source must feed LT5/RF11 low-table forced-up from shared forced-up sources")
    if re.search(
        r"const\s+bool\s+z_airdodge_override_active\s*=\s*inputs\.lt5\s*\|\|\s*inputs\.rf11\s*;",
        text,
    ) is None:
        fail("runtime source must alias LT5/RF11 for shared low-magnitude Z-airdodge override")
    if re.search(
        r"const\s+bool\s+z_airdodge_override_active\s*=\s*inputs\.lt1\s*\|\|\s*inputs\.rf11\s*;",
        text,
    ):
        fail("runtime source must not use stale LT1/RF11 Z-airdodge activation")

    if re.search(r"outputs\.dpadUp\s*=\s*inputs\.rt5\s*;", text) is None:
        fail("runtime source must map nunchuk-C D-pad Up to RT5")
    if re.search(r"outputs\.dpadRight\s*=\s*inputs\.rt4\s*;", text) is None:
        fail("runtime source must map nunchuk-C D-pad Right to RT4")

    if re.search(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*z_airdodge_override_active\s*\)\s*\{",
        text,
        flags=re.DOTALL,
    ) is None:
        fail("runtime source must apply LT5/RF11 hard override after direction-plus-A override")

    if re.search(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*z_airdodge_override_active\s*\)\s*\{.*?\}\s*\}\s*if\s*\(\s*null_modifier_active\s*\)\s*\{",
        text,
        flags=re.DOTALL,
    ) is None:
        fail("runtime source must apply RF9 override after LT5/RF11 and direction-plus-A overrides")

    if re.search(r"outputs\.leftStickX\s*=\s*128\s*;", text) is None:
        fail("runtime source must assign RF9 final leftStickX override to 128")
    if re.search(r"outputs\.leftStickY\s*=\s*128\s*;", text) is None:
        fail("runtime source must assign RF9 final leftStickY override to 128")

    if re.search(r"outputs\.leftStickX\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.x\s*;", text) is None:
        fail("runtime source must assign LT1 low-magnitude leftStickX")
    if re.search(r"outputs\.leftStickY\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.y\s*;", text) is None:
        fail("runtime source must assign LT1 low-magnitude leftStickY")

    if re.search(
        r"outputs\.leftStickLeft\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_left\s*;",
        text,
    ) is None:
        fail("runtime source must suppress digital left-stick left during LS->DPad")
    if re.search(
        r"outputs\.leftStickRight\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_right\s*;",
        text,
    ) is None:
        fail("runtime source must suppress digital left-stick right during LS->DPad")
    if re.search(
        r"outputs\.leftStickDown\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_down\s*;",
        text,
    ) is None:
        fail("runtime source must suppress digital left-stick down during LS->DPad")
    if re.search(
        r"outputs\.leftStickUp\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_up\s*;",
        text,
    ) is None:
        fail("runtime source must suppress digital left-stick up during LS->DPad")

    if re.search(
        r"const\s+int8_t\s+horizontal_axis\s*=\s*ResolveHorizontalAxis\(inputs\.lf3,\s*inputs\.lf1,\s*layer_left_active,\s*layer_right_active\)\s*;",
        text,
    ) is None:
        fail("runtime source must include LF8/LF7 in effective horizontal direction resolution")

    if re.search(r"const\s+bool\s+tilt1_pressed\s*=\s*inputs\.rf3\s*&&\s*!layer_transform_active\s*;", text) is None:
        fail("runtime source must gate RF3 Tilt1 by !layer_transform_active")
    if re.search(r"const\s+bool\s+tilt2_pressed\s*=\s*inputs\.rf4\s*&&\s*!layer_transform_active\s*;", text) is None:
        fail("runtime source must gate RF4 Tilt2 by !layer_transform_active")
    if re.search(r"const\s+bool\s+rf4_layer_flipper_active\s*=\s*layer_transform_active\s*&&\s*inputs\.rf4\s*;", text) is None:
        fail("runtime source must define layered RF4 flipper activation for pure layer and LF4 sub-mode")
    if re.search(r"const\s+bool\s+layer_rf3_normal_x_active\s*=\s*layer_direction_active\s*&&\s*!inputs\.lf4\s*&&\s*inputs\.rf3\s*;", text) is None:
        fail("runtime source must define layered RF3 normal-x activation for pure layer only")
    if re.search(r"const\s+bool\s+layer_normal_x_effective\s*=\s*layer_normal_x_active\s*&&\s*!layer_flipper_effective\s*;", text) is None:
        fail("runtime source must enforce RF4-over-RF3 layered modifier precedence")
    if re.search(r"EffectiveModifier::LayerNormalX", text) is None:
        fail("runtime source must define layered RF3 normal-x effective modifier")
    if re.search(
        r"SelectStickTable\(\s*mode_active,\s*x1_active,\s*x2_active,\s*y1_active,\s*layer_rf3_normal_x_active,\s*rf4_layer_flipper_active,\s*tilt1_effective,\s*tilt2_effective,\s*tilt3_effective",
        text,
        flags=re.DOTALL,
    ) is None:
        fail("runtime source must pass layer RF3 normal-x and RF4 flipper into table selection")

    if re.search(r"constexpr\s+StickPoint\s+kLayerFlipperTable\[9\]", text) is None:
        fail("runtime source must define non-Mode layer RF4 flipper table")
    for point in LAYER_FLIPPER_POINTS:
        if point not in text:
            fail(f"runtime source missing layer RF4 flipper point: {point}")
    if re.search(r"constexpr\s+StickPoint\s+kMLayerFlipperTable\[9\]", text) is None:
        fail("runtime source must define Mode layer RF4 flipper table")
    for point in MLAYER_FLIPPER_POINTS:
        if point not in text:
            fail(f"runtime source missing Mode layer RF4 flipper point: {point}")

    if re.search(r"constexpr\s+StickPoint\s+kLayerNormalXTable\[9\]", text) is None:
        fail("runtime source must define non-Mode layer RF3 normal-x table")
    for point in LAYER_NORMAL_X_POINTS:
        if point not in text:
            fail(f"runtime source missing layer RF3 normal-x point: {point}")
    if re.search(r"constexpr\s+StickPoint\s+kMLayerNormalXTable\[9\]", text) is None:
        fail("runtime source must define Mode layer RF3 normal-x table")
    for point in MLAYER_NORMAL_X_POINTS:
        if point not in text:
            fail(f"runtime source missing Mode layer RF3 normal-x point: {point}")
    if re.search(r"constexpr\s+StickPoint\s+kY1LayerNormalXTable\[9\]", text) is None:
        fail("runtime source must define Y1 layer RF3 normal-x table")
    for point in Y1_LAYER_NORMAL_X_POINTS:
        if point not in text:
            fail(f"runtime source missing Y1 layer RF3 normal-x point: {point}")
    if re.search(r"constexpr\s+StickPoint\s+kMY1LayerNormalXTable\[9\]", text) is None:
        fail("runtime source must define Mode Y1 layer RF3 normal-x table")
    for point in MY1_LAYER_NORMAL_X_POINTS:
        if point not in text:
            fail(f"runtime source missing Mode Y1 layer RF3 normal-x point: {point}")

    if "outputs.dpadLeft |= inputs.lf8;" in text or "outputs.dpadRight |= inputs.lf6;" in text:
        fail("runtime source must not preserve old standalone D-pad direct inputs")

    for empty_input in EMPTY_NO_OUTPUT_INPUTS:
        if re.search(r"outputs\.[A-Za-z0-9_]+\s*(?:=|\|=)\s*" + re.escape(empty_input), text):
            fail(f"empty/no-output input drives a known game output: {empty_input}")
    if re.search(r"outputs\.(?!buttonR)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf11", text):
        fail("RF11 must not drive outputs other than the shared Z carrier")
    if re.search(r"active_modifier_count\s*\+\+[^;]*inputs\.rf11", text):
        fail("RF11 must not be counted as a modifier")
    if re.search(r"SelectStickTable\s*\([^)]*inputs\.rf11", text, flags=re.DOTALL):
        fail("RF11 must not alter modifier table selection")
    if re.search(r"outputs\.(?!leftStickX|leftStickY)[A-Za-z0-9_]+\s*(?:=|\|=)\s*inputs\.rf9", text):
        fail("RF9 must not drive game-button/dpad/right-stick/menu outputs")

    if re.search(r"tilt3_effective\s*=\s*tilt1_pressed\s*&&\s*tilt2_pressed\s*;", text) is None:
        fail("runtime source must define Tilt3 as rf3&&rf4 chord")

    return text


def main() -> int:
    failures: list[str] = []

    try:
        artifact = load_json(ARTIFACT_PATH)
        fixture = load_json(FIXTURE_PATH)
        artifact_mode = get_ultimate_mode(artifact, ARTIFACT_PATH)
        fixture_mode = get_ultimate_mode(fixture, FIXTURE_PATH)

        artifact_mapping = explicit_self_activate_map(artifact_mode, ARTIFACT_PATH)
        fixture_mapping = explicit_self_activate_map(fixture_mode, FIXTURE_PATH)
        ensure_role_inputs_not_in_socd_pairs(artifact_mode, ARTIFACT_PATH)
        ensure_role_inputs_not_in_socd_pairs(fixture_mode, FIXTURE_PATH)

        for button in RUNTIME_REQUIRED_SELF_ACTIVATES:
            if artifact_mapping.get(button) != button:
                fail(f"artifact missing explicit self-activates binding for {button}")
            if fixture_mapping.get(button) != button:
                fail(f"fixture missing explicit self-activates binding for {button}")

        require_runtime_doc()
        require_runtime_source()
    except AssertionError as exc:
        failures.append(str(exc))

    if failures:
        print("status=FAIL")
        for failure in failures:
            print(f"failure={failure}")
        return 1

    print("status=PASS")
    print(f"artifact={ARTIFACT_PATH.relative_to(REPO_ROOT)}")
    print(f"fixture={FIXTURE_PATH.relative_to(REPO_ROOT)}")
    print(f"runtime_doc={RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    print(f"runtime_source={SOURCE_PATH.relative_to(REPO_ROOT)}")
    print("identity_representation=explicit_self_activates")
    print("identity_semantic_remaps=0")
    print("runtime_required_inputs_explicit_self_activated=true")
    print("forced_up_role=RF6_or_RF12_or_RF15_or_pure_layer_RF2_or_lf4_submode_RF3")
    print("rf4_up_conflict=absent")
    print("lt3_role=L")
    print("tilt3_role=RF3+RF4_when_layer_inactive")
    print("lt5_rf11_role=Z_plus_low_magnitude_override_alias")
    print("z_role=RT1_or_LT5_or_RF11")
    print("r_role=RF16")
    print("y_role=RF10")
    print("b_role=RF5_or_LF4_or_pure_layer_RF3")
    print("l_role=LT3")
    print("rf15_role=Up+A_alias_of_RF12")
    print("rf9_role=null_modifier_final_analog_override")
    print("tilt1_non_mode_y_values=47_128_209")
    print("y1_tilt1_special_composite=enabled")
    print("rt4_rt5_cstick_swap=enabled")
    print("y2_my2_role=scratched_inactive")
    print("standalone_dpad=none")
    print("lt2_mody_conflict=absent")
    print("lt1_modx_conflict=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
