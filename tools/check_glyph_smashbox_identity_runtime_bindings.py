#!/usr/bin/env python3
"""Read-only checker for GFW3 identity-runtime binding boundaries."""

from __future__ import annotations

import json
from pathlib import Path

from extract_glyph_identity_runtime_tables import load_source_text_with_generated_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
FIXTURE_PATH = REPO_ROOT / "docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json"
SOURCE_PATH = REPO_ROOT / "src/modes/Ultimate.cpp"

REQUIRED_SELF_ACTIVATES = {
    "BTN_RT1", "BTN_RF1", "BTN_RF2", "BTN_RF3", "BTN_RF4", "BTN_RF5", "BTN_RF6",
    "BTN_RF7", "BTN_RF8", "BTN_RF9", "BTN_RF10", "BTN_RF11", "BTN_RF12",
    "BTN_RF13", "BTN_RF15", "BTN_RF16", "BTN_LT1", "BTN_LT2", "BTN_LT3",
    "BTN_LT4", "BTN_LT5", "BTN_LT6", "BTN_LF4", "BTN_LF7", "BTN_LF8",
}

FORBIDDEN_SOCD_INPUTS = {
    "BTN_LT1", "BTN_LT2", "BTN_LT3", "BTN_LT4", "BTN_LT5",
    "BTN_RF2", "BTN_RF3", "BTN_RF4", "BTN_RF5", "BTN_RF6",
}

REQUIRED_SOURCE_ANCHORS = (
    "outputs.buttonR = inputs.rf6;",
    "outputs.buttonL = inputs.lt1 || inputs.lt3;",
    "outputs.triggerRDigital = inputs.rf16 || inputs.lt3;",
    "state.x1_active = inputs.lt5;",
    "state.x2_active = inputs.lt4;",
    "state.z_airdodge_override_active = inputs.rf6;",
    "state.rf4_behavior_available = rf4_behavior_available;",
    "state.rf3_x_suppressed_by_rf9 = rf3_x_suppressed_by_rf9;",
    "state.null_modifier_active = inputs.rf9 && !state.rf4_behavior_available;",
    "state.ls_to_dpad_active = inputs.rf13;",
    "state.hard_up_b_active = inputs.rf7;",
    "if (inputs.nunchuk_c)",
    "if (inputs.nunchuk_connected)",
)

FORBIDDEN_SOURCE_ANCHORS = (
    "outputs.buttonR = inputs.rt1 || inputs.lt5 || inputs.rf11;",
    "state.layer_left_active = inputs.lf8;",
    "state.layer_right_active = inputs.lf7;",
    "state.z_airdodge_override_active = inputs.lt5 || inputs.rf11;",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must contain a JSON object")
    return payload


def ultimate_mode(path: Path) -> dict[str, object]:
    payload = load_json(path)
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        fail(f"{path.relative_to(REPO_ROOT)} missing gameModeConfigs list")
    for mode in modes:
        if isinstance(mode, dict) and mode.get("modeId") == "MODE_ULTIMATE":
            return mode
    fail(f"{path.relative_to(REPO_ROOT)} missing MODE_ULTIMATE")
    return {}


def validate_identity_profile(path: Path) -> None:
    mode = ultimate_mode(path)
    remaps = mode.get("buttonRemapping")
    if not isinstance(remaps, list):
        fail(f"{path.relative_to(REPO_ROOT)} MODE_ULTIMATE.buttonRemapping must be a list")

    observed: set[str] = set()
    for index, remap in enumerate(remaps):
        if not isinstance(remap, dict):
            fail(f"{path.relative_to(REPO_ROOT)} buttonRemapping[{index}] must be an object")
        physical = remap.get("physicalButton")
        activates = remap.get("activates")
        if not isinstance(physical, str) or not isinstance(activates, str):
            fail(f"{path.relative_to(REPO_ROOT)} buttonRemapping[{index}] must include string physicalButton/activates")
        if physical != activates:
            fail(f"{path.relative_to(REPO_ROOT)} profile semantic remap present: {physical}->{activates}")
        if physical in REQUIRED_SELF_ACTIVATES:
            observed.add(physical)

    missing = sorted(REQUIRED_SELF_ACTIVATES - observed)
    if missing:
        fail(f"{path.relative_to(REPO_ROOT)} missing self-activate entries: {', '.join(missing)}")

    socd_pairs = mode.get("socdPairs")
    if not isinstance(socd_pairs, list):
        fail(f"{path.relative_to(REPO_ROOT)} MODE_ULTIMATE.socdPairs must be a list")
    for index, pair in enumerate(socd_pairs):
        if not isinstance(pair, dict):
            fail(f"{path.relative_to(REPO_ROOT)} socdPairs[{index}] must be an object")
        if pair.get("buttonDir1") in FORBIDDEN_SOCD_INPUTS or pair.get("buttonDir2") in FORBIDDEN_SOCD_INPUTS:
            fail(f"{path.relative_to(REPO_ROOT)} GFW3 runtime role input leaked into SOCD pair")


def validate_source() -> None:
    text = load_source_text_with_generated_tables(SOURCE_PATH)
    for anchor in REQUIRED_SOURCE_ANCHORS:
        if anchor not in text:
            fail(f"missing runtime source anchor: {anchor}")
    for anchor in FORBIDDEN_SOURCE_ANCHORS:
        if anchor in text:
            fail(f"forbidden stale runtime source anchor: {anchor}")


def main() -> int:
    try:
        validate_identity_profile(ARTIFACT_PATH)
        validate_identity_profile(FIXTURE_PATH)
        validate_source()
    except (AssertionError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print("binding_model=identity_profile_runtime_rework")
    print("profile_artifact_changed=false")
    print("hardware_status=not_new_hardware_result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
