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
    "`RF8 = Mode`",
    "`LT5 = X1`",
    "`LT4 = X2`",
    "`LT2 = Y1`",
    "`LT3 = Y2`",
    "`RF7 = LS->DPad`",
    "`RF6 = forced Up`",
    "`LT1 = L`",
    "`RF3 = Tilt1`",
    "`RF4 = Tilt2`",
    "`RF3 + RF4 = Tilt3`",
)

SOURCE_ANCHORS = (
    "inputs.rf8",
    "inputs.lt5",
    "inputs.lt4",
    "inputs.lt2",
    "inputs.lt3",
    "inputs.rf7",
    "inputs.rf6",
    "inputs.lt1",
    "inputs.rf3",
    "inputs.rf4",
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


def semantic_remap_count(mode_config: dict[str, object], path: Path) -> int:
    remaps = mode_config.get("buttonRemapping")
    if not isinstance(remaps, list):
        fail(f"MODE_ULTIMATE.buttonRemapping must be a list in {path.relative_to(REPO_ROOT)}")

    count = 0
    for index, remap in enumerate(remaps):
        if not isinstance(remap, dict):
            fail(f"buttonRemapping[{index}] must be an object in {path.relative_to(REPO_ROOT)}")
        physical = remap.get("physicalButton")
        if not isinstance(physical, str):
            fail(f"buttonRemapping[{index}] missing physicalButton in {path.relative_to(REPO_ROOT)}")

        activates = remap.get("activates")
        if activates is None:
            continue
        if not isinstance(activates, str):
            fail(f"buttonRemapping[{index}] activates must be a string in {path.relative_to(REPO_ROOT)}")

        if activates not in (physical, "BTN_UNSPECIFIED"):
            count += 1

    return count


def require_runtime_doc() -> str:
    if not RUNTIME_DOC_PATH.exists():
        fail(f"missing runtime doc: {RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    for role_line in ROLE_LINES:
        if role_line not in text:
            fail(f"missing runtime role line: {role_line}")

    if "LT3 = Y2" not in text:
        fail("runtime doc must state LT3=Y2")
    if "RF3 + RF4 = Tilt3" not in text:
        fail("runtime doc must state RF3+RF4=Tilt3")
    if "RF6 = forced Up" not in text:
        fail("runtime doc must state RF6=forced Up")
    if "LT1 = L" not in text:
        fail("runtime doc must state LT1=L")
    if "RF4` is Tilt2-only" not in text and "RF4 is Tilt2-only" not in text:
        fail("runtime doc must state RF4 is Tilt2-only")
    if "R is intentionally left unassigned" not in text:
        fail("runtime doc must document unassigned R policy")
    if "outputs.modX = inputs.lt1" not in text or "removed/neutralized" not in text:
        fail("runtime doc must document LT1/modX removal policy")
    if "standalone `LT3 -> Tilt3` behavior is historical only" not in text:
        fail("runtime doc must mark standalone LT3->Tilt3 as historical only")

    return text


def require_runtime_source() -> str:
    if not SOURCE_PATH.exists():
        fail(f"missing runtime source: {SOURCE_PATH.relative_to(REPO_ROOT)}")
    text = SOURCE_PATH.read_text(encoding="utf-8")

    for anchor in SOURCE_ANCHORS:
        if anchor not in text:
            fail(f"missing runtime source anchor: {anchor}")

    if "outputs.buttonL = inputs.lt1;" not in text:
        fail("runtime source must assign LT1 to L button")
    if "outputs.modX = inputs.lt1;" in text:
        fail("runtime source must not assign LT1 to modX")
    if "outputs.buttonR = inputs.rf3;" in text:
        fail("runtime source must not assign RF3 to R")
    if "leftStickUp = inputs.rf4;" in text:
        fail("runtime source must not consume RF4 as Up")
    if re.search(r"inputs\.rf4\s*,\s*//\s*Up", text):
        fail("runtime source must not pass RF4 as Up into UpdateDirections")
    if re.search(r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*;", text) is None:
        fail("runtime source must define RF6 forced-Up source")
    if re.search(r"const\s+bool\s+effective_ls_up\s*=\s*force_up_active\s*;", text) is None:
        fail("runtime source must define effective Up from RF6")
    if re.search(r"const\s+bool\s+effective_ls_down\s*=\s*inputs\.lf2\s*&&\s*!force_up_active\s*;", text) is None:
        fail("runtime source must suppress Down when RF6 forced-Up is active")
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
        r"outputs\.dpadUp\s*\|=\s*effective_ls_up\s*;",
        text,
    ) is None:
        fail("runtime source must use effective Up for LS->DPad")

    if re.search(r"tilt3_effective\s*=\s*tilt1_pressed\s*&&\s*tilt2_pressed\s*;", text) is None:
        fail("runtime source must define Tilt3 as rf3&&rf4 chord")

    if "senscope_tilt3_active" in text:
        fail("legacy standalone LT3 tilt3 logic token still present")

    return text


def main() -> int:
    failures: list[str] = []

    try:
        artifact = load_json(ARTIFACT_PATH)
        fixture = load_json(FIXTURE_PATH)
        artifact_mode = get_ultimate_mode(artifact, ARTIFACT_PATH)
        fixture_mode = get_ultimate_mode(fixture, FIXTURE_PATH)

        artifact_semantic = semantic_remap_count(artifact_mode, ARTIFACT_PATH)
        fixture_semantic = semantic_remap_count(fixture_mode, FIXTURE_PATH)
        if artifact_semantic != 0:
            fail(f"artifact semantic_remap_count must be 0, got {artifact_semantic}")
        if fixture_semantic != 0:
            fail(f"fixture semantic_remap_count must be 0, got {fixture_semantic}")

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
    print("identity_semantic_remaps=0")
    print("forced_up_role=RF6")
    print("rf4_up_conflict=absent")
    print("lt3_role=Y2")
    print("tilt3_role=RF3+RF4")
    print("r_role=unassigned")
    print("l_role=LT1")
    print("lt1_modx_conflict=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
