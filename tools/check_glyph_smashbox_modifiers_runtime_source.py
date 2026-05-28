#!/usr/bin/env python3
"""Read-only source/doc checker for identity-runtime Smash Box modifiers."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
RUNTIME_DOC_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md"

BEGIN_MARKER = "// Senscope Glyph Smash Box runtime begin"
END_MARKER = "// Senscope Glyph Smash Box runtime end"

ANCHORS = (
    "inputs.rf8",
    "inputs.lt5",
    "inputs.lt4",
    "inputs.lt2",
    "inputs.lt3",
    "inputs.rf7",
    "inputs.lt1",
    "inputs.rf3",
    "inputs.rf4",
    "inputs.rf6",
    "inputs.rf12",
    "inputs.lt6",
    "inputs.rf16",
)

FORBIDDEN_FLASH_TOKENS = (
    "flash",
    "flashing",
    "bootloader",
    "uf2",
    "push-to-device",
    "push_to_device",
)

FORBIDDEN_RAW_BYPASS_TOKENS = (
    "get_button(",
    "set_button(",
    "original_inputs",
    "physical_button",
    "BTN_",
)

FORBIDDEN_OVERFLOW_TOKENS = (
    "overflow",
    "wrap",
    "underflow",
)

FORBIDDEN_STOP_CODES = (
    "IDENTITY_PROFILE_BASELINE_NOT_ON_CONFIGURATOR",
    "UNRESOLVED_STOP_CODE",
    "status=STOP",
    "STOPPED_",
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


def ensure_anchor_tokens(source: str) -> None:
    for anchor in ANCHORS:
        if anchor not in source:
            fail(f"missing role anchor token: {anchor}")


def ensure_no_old_lt3_tilt3_shape(source: str, block: str) -> None:
    if "senscope_tilt3_active" in source:
        fail("legacy senscope_tilt3_active path must not remain")
    compact_block = re.sub(r"\s+", "", block)
    if "inputs.lt3||(inputs.lt1&&inputs.lt2)" in compact_block:
        fail("legacy LT3 or LT1+LT2 Tilt3 active expression must not remain")
    if re.search(r"tilt3[^\n]*inputs\.lt3|inputs\.lt3[^\n]*tilt3", block, flags=re.IGNORECASE):
        fail("marker block must not bind LT3 as Tilt3")


def ensure_chord_shape(block: str) -> None:
    require(r"tilt1_pressed\s*=\s*inputs\.rf3\s*;", block, "Tilt1 source input rf3")
    require(r"tilt2_pressed\s*=\s*inputs\.rf4\s*;", block, "Tilt2 source input rf4")
    require(
        r"tilt3_effective\s*=\s*tilt1_pressed\s*&&\s*tilt2_pressed\s*;",
        block,
        "Tilt3 chord uses rf3&&rf4",
    )


def ensure_direction_plus_a_direction_shape(source: str) -> None:
    require(
        r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*;",
        source,
        "forced-Up sources RF6 or RF12",
    )
    require(
        r"const\s+bool\s+effective_ls_up\s*=\s*inputs\.lf2\s*\|\|\s*force_up_active\s*;",
        source,
        "effective Up uses LF2 or forced-Up",
    )
    require(
        r"const\s+bool\s+effective_ls_down\s*=\s*\(\s*inputs\.lf5\s*\|\|\s*inputs\.lt6\s*\)\s*&&\s*!force_up_active\s*;",
        source,
        "effective Down uses LF5 or LT6 and is suppressed by forced-Up",
    )
    require(
        r"UpdateDirections\s*\(\s*inputs\.lf3\s*,\s*//\s*Left\s*\n\s*inputs\.lf1\s*,\s*//\s*Right\s*\n\s*effective_ls_down\s*,\s*//\s*Down\s*\n\s*effective_ls_up\s*,\s*//\s*Up\s*\(RF6/RF12 forced-Up\)",
        source,
        "UpdateDirections uses effective RF6/RF12-based Up and LT6/LF5 Down",
        flags=re.MULTILINE,
    )


def ensure_no_standalone_dpad_shape(source: str) -> None:
    forbidden_direct_dpad = (
        r"outputs\.dpadLeft\s*\|=\s*inputs\.lf8\s*;",
        r"outputs\.dpadRight\s*\|=\s*inputs\.lf6\s*;",
        r"outputs\.dpadUp\s*\|=\s*inputs\.rf13\s*;",
        r"outputs\.dpadDown\s*\|=\s*inputs\.rf10\s*;",
        r"outputs\.dpadLeft\s*=\s*inputs\.lf8\s*;",
        r"outputs\.dpadRight\s*=\s*inputs\.lf6\s*;",
    )
    for pattern in forbidden_direct_dpad:
        if re.search(pattern, source):
            fail("runtime source must not preserve old standalone/direct D-pad cluster outputs")


def ensure_rf4_not_up(source: str) -> None:
    if re.search(r"leftStickUp\s*=\s*inputs\.rf4\s*;", source):
        fail("RF4 must not directly drive leftStickUp")
    if re.search(r"inputs\.rf4\s*,\s*//\s*Up", source):
        fail("RF4 must not be passed as Up to UpdateDirections")


def ensure_ls_to_dpad_shape(source: str) -> None:
    require(r"ls_to_dpad_active\s*=\s*inputs\.rf7\s*;", source, "LS->DPad source input rf7")
    require(r"outputs\.dpadUp\s*\|=\s*effective_ls_up\s*;", source, "LS->DPad up uses effective Up")
    require(r"outputs\.dpadDown\s*\|=\s*effective_ls_down\s*;", source, "LS->DPad down uses effective Down")
    require(r"outputs\.dpadLeft\s*\|=\s*effective_ls_left\s*;", source, "LS->DPad left")
    require(r"outputs\.dpadRight\s*\|=\s*effective_ls_right\s*;", source, "LS->DPad right")
    require(r"outputs\.leftStickLeft\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_left\s*;", source, "LS->DPad suppresses digital leftStickLeft")
    require(r"outputs\.leftStickRight\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_right\s*;", source, "LS->DPad suppresses digital leftStickRight")
    require(r"outputs\.leftStickDown\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_down\s*;", source, "LS->DPad suppresses digital leftStickDown")
    require(r"outputs\.leftStickUp\s*=\s*ls_to_dpad_active\s*\?\s*false\s*:\s*effective_ls_up\s*;", source, "LS->DPad suppresses digital leftStickUp")
    require(
        r"const\s+StickPoint\s+center\s*=\s*mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;",
        source,
        "LS->DPad analog center uses direction5 values",
    )


def ensure_r_and_modx_policies(source: str, doc_text: str) -> None:
    if re.search(r"outputs\.buttonR\s*=\s*inputs\.rf3\s*;", source):
        fail("RF3 must not drive buttonR")
    if re.search(r"outputs\.modX\s*=\s*inputs\.lt1\s*;", source):
        if "source-confirmed harmless" not in doc_text:
            fail("LT1 must not drive modX unless doc marks it source-confirmed harmless")
    require(r"outputs\.buttonL\s*=\s*inputs\.lt1\s*;", source, "LT1 drives L button")
    require(r"outputs\.triggerLDigital\s*=\s*inputs\.lt1\s*;", source, "LT1 drives GameCube L trigger digital carrier")
    require(r"outputs\.triggerRDigital\s*=\s*inputs\.rf16\s*;", source, "RF16 drives GameCube R trigger digital carrier")
    require(r"outputs\.buttonR\s*=\s*inputs\.rt1\s*;", source, "RT1 drives source-confirmed GameCube/N64 Z carrier")
    if re.search(r"outputs\.triggerRDigital\s*=\s*inputs\.rf12\s*;", source):
        fail("RF12 must not drive R carrier")
    require(r"`?RF16`?\s+remains\s+`?R`?", doc_text, "runtime doc states RF16 remains R")


def ensure_y_and_mody_policies(source: str, doc_text: str) -> None:
    if re.search(r"outputs\.y\s*=\s*inputs\.rf6\s*;", source):
        fail("RF6 forced-Up must not drive game Y")
    if re.search(r"outputs\.modY\s*=\s*inputs\.lt2\s*;", source):
        if "source-confirmed harmless" not in doc_text:
            fail("LT2 (Y1 role) must not drive modY unless doc marks it source-confirmed harmless")

    require(r"outputs\.y\s*=\s*inputs\.rf10\s*;", source, "RF10 drives game Y")
    if re.search(r"outputs\.modY\s*=\s*false\s*;", source) is None:
        if "modY source-confirmed harmless" not in doc_text:
            fail("modY must be neutralized (outputs.modY=false) unless doc declares modY source-confirmed harmless")


def ensure_main_button_shape(source: str) -> None:
    require(
        r"outputs\.a\s*=\s*inputs\.rf1\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf12\s*;",
        source,
        "A is driven by RF1 or LT6 or RF12",
    )
    require(r"outputs\.b\s*=\s*inputs\.rf5\s*\|\|\s*inputs\.lf4\s*;", source, "RF5 or LF4 drives B")
    require(r"outputs\.x\s*=\s*inputs\.rf2\s*;", source, "RF2 drives X")
    require(r"outputs\.y\s*=\s*inputs\.rf10\s*;", source, "RF10 drives Y")
    if re.search(r"outputs\.triggerLDigital\s*=\s*inputs\.lf4\s*;", source):
        fail("LF4 must not be stolen by L trigger digital when LF4 is B")
    if re.search(r"outputs\.triggerRDigital\s*=\s*inputs\.rf5\s*;", source):
        fail("RF5 must not be stolen by R trigger digital when RF5 is B")


def ensure_direction_plus_a_not_modifiers(source: str, block: str) -> None:
    if re.search(r"(x1_active|x2_active|y1_active|y2_active|tilt1_effective|tilt2_effective|tilt3_effective)\s*=\s*inputs\.(lt6|rf12)", block):
        fail("LT6/RF12 must not be consumed as modifier activators")
    if re.search(r"SelectStickTable\s*\([^)]*inputs\.(lt6|rf12)", block, flags=re.DOTALL):
        fail("LT6/RF12 must not be passed into SelectStickTable modifier selection")
    require(
        r"outputs\.a\s*=\s*inputs\.rf1\s*\|\|\s*inputs\.lt6\s*\|\|\s*inputs\.rf12\s*;",
        source,
        "LT6/RF12 participate in A output",
    )
    require(
        r"const\s+bool\s+effective_ls_down\s*=\s*\(\s*inputs\.lf5\s*\|\|\s*inputs\.lt6\s*\)\s*&&\s*!force_up_active\s*;",
        source,
        "LT6 participates in effective Down logic",
    )
    require(
        r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*;",
        source,
        "RF12 participates in forced-Up logic",
    )


def ensure_no_forbidden_tokens(source: str, block: str) -> None:
    lowered_source = source.lower()
    lowered_block = block.lower()

    for token in FORBIDDEN_FLASH_TOKENS:
        if token in lowered_source:
            fail(f"forbidden flashing token found: {token}")

    for token in FORBIDDEN_RAW_BYPASS_TOKENS:
        if token in block:
            fail(f"forbidden raw bypass token found in marker block: {token}")

    for token in FORBIDDEN_OVERFLOW_TOKENS:
        if token in lowered_block:
            fail(f"forbidden overflow/wrap token found in marker block: {token}")

    if re.search(r"\buint8_t\b[^\n=]*=\s*128\s*[+-]", block):
        fail("marker block should not rely on uint8_t arithmetic formulas")


def read_runtime_doc() -> str:
    if not RUNTIME_DOC_PATH.exists():
        fail(f"missing runtime doc: {RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    require(r"Implementation is complete", text, "runtime doc completion state")
    require(r"RF6\s*=\s*forced Up", text, "runtime doc RF6 forced-Up role")
    require(r"LT6\s*=\s*Down\+A", text, "runtime doc LT6 direction-plus-A role")
    require(r"RF12\s*=\s*Up\+A", text, "runtime doc RF12 direction-plus-A role")
    require(r"`?RF4`?\s*is\s*Tilt2-only", text, "runtime doc RF4 Tilt2-only policy")
    require(r"`?RF6`?\s+is\s+forced-Up\s+only\s+and\s+no\s+longer\s+drives\s+game\s+Y", text, "runtime doc RF6 no longer game Y policy")
    require(r"`?LT2`?\s+remains\s+the\s+`?Y1`?\s+modifier\s+role\s+only", text, "runtime doc LT2 Y1-only policy")
    require(r"modY.*removed/neutralized|removed/neutralized.*modY", text, "runtime doc LT2/modY removal policy", flags=re.IGNORECASE)
    require(r"RF10\s*=\s*Y", text, "runtime doc RF10 game Y role")
    require(r"RT1\s*=\s*Z", text, "runtime doc RT1 Z role")
    require(r"RF16\s*=\s*R", text, "runtime doc RF16 R role")
    require(r"`?RF16`?\s+remains\s+`?R`?", text, "runtime doc RF16 remains R")
    require(r"not modifiers", text, "runtime doc direction-plus-A not modifiers policy", flags=re.IGNORECASE)
    if re.search(
        r"LS->DPad.*direction-plus-A.*(?:D-pad.*A|A.*D-pad)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ) is None:
        fail("missing source evidence: runtime doc LS->DPad direction-plus-A policy")
    require(r"no standalone D-pad", text, "runtime doc no standalone D-pad policy", flags=re.IGNORECASE)

    for token in FORBIDDEN_STOP_CODES:
        if token in text:
            fail(f"runtime doc contains unresolved stop code token: {token}")

    return text


def main() -> int:
    if not SOURCE_PATH.exists():
        print("status=FAIL")
        print(f"failure=missing_source:{SOURCE_PATH.relative_to(REPO_ROOT)}")
        return 1

    source = SOURCE_PATH.read_text(encoding="utf-8")
    block = extract_marker_block(source)

    try:
        doc_text = read_runtime_doc()
        ensure_anchor_tokens(source)
        ensure_no_old_lt3_tilt3_shape(source, block)
        ensure_chord_shape(block)
        ensure_direction_plus_a_direction_shape(source)
        ensure_main_button_shape(source)
        ensure_direction_plus_a_not_modifiers(source, block)
        ensure_rf4_not_up(source)
        ensure_ls_to_dpad_shape(source)
        ensure_no_standalone_dpad_shape(source)
        ensure_r_and_modx_policies(source, doc_text)
        ensure_y_and_mody_policies(source, doc_text)
        ensure_no_forbidden_tokens(source, block)
    except AssertionError as exc:
        print("status=FAIL")
        print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
    print(f"runtime_doc={RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    print("markers=present")
    print("forced_up_role=rf6_or_rf12")
    print("rf4_up_conflict=absent")
    print("direction_plus_a_role=lt6_down_a_rf12_up_a")
    print("direction_plus_a_modifier_conflict=absent")
    print("lt3_role=Y2_not_tilt3")
    print("tilt3_role=rf3_and_rf4_chord")
    print("ls_to_dpad_role=rf7")
    print("l_button_role=lt1")
    print("r_button_role=rf16")
    print("z_button_role=rt1_source_confirmed_buttonR_carrier")
    print("y_button_role=rf10")
    print("standalone_dpad=none")
    print("lt2_mody_conflict=absent")
    print("lt1_modx_conflict=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
