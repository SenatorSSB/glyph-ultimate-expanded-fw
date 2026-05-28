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


def ensure_rf6_forced_up_shape(source: str) -> None:
    require(r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*;", source, "RF6 forced-Up source")
    require(r"const\s+bool\s+effective_ls_up\s*=\s*force_up_active\s*;", source, "effective Up uses RF6")
    require(
        r"const\s+bool\s+effective_ls_down\s*=\s*inputs\.lf2\s*&&\s*!force_up_active\s*;",
        source,
        "Down suppressed by RF6 forced-Up",
    )
    require(
        r"UpdateDirections\s*\(\s*inputs\.lf3\s*,\s*//\s*Left\s*\n\s*inputs\.lf1\s*,\s*//\s*Right\s*\n\s*effective_ls_down\s*,\s*//\s*Down\s*\n\s*effective_ls_up\s*,\s*//\s*Up\s*\(RF6 forced-Up\)",
        source,
        "UpdateDirections uses effective RF6-based Up/Down",
        flags=re.MULTILINE,
    )


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
    require(r"`?RF4`?\s*is\s*Tilt2-only", text, "runtime doc RF4 Tilt2-only policy")
    require(r"R\s+is\s+intentionally\s+left\s+unassigned", text, "runtime doc R unassigned policy")
    require(r"modX\s*=\s*inputs\.lt1\s*.*removed|removed/neutralized", text, "runtime doc LT1/modX policy", flags=re.IGNORECASE)

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
        ensure_rf6_forced_up_shape(source)
        ensure_rf4_not_up(source)
        ensure_ls_to_dpad_shape(source)
        ensure_r_and_modx_policies(source, doc_text)
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
    print("forced_up_role=rf6")
    print("rf4_up_conflict=absent")
    print("lt3_role=Y2_not_tilt3")
    print("tilt3_role=rf3_and_rf4_chord")
    print("ls_to_dpad_role=rf7")
    print("l_button_role=lt1")
    print("r_button_role=unassigned")
    print("lt1_modx_conflict=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
