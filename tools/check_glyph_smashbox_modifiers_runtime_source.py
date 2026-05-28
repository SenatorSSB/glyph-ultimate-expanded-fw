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


def ensure_mode_ls_to_dpad_shape(source: str, block: str) -> None:
    require(r"mode_active\s*=\s*inputs\.rf8\s*;", block, "Mode source input rf8")
    require(r"ls_to_dpad_active\s*=\s*inputs\.rf7\s*;", block, "LS->DPad source input rf7")
    require(r"if\s*\(\s*ls_to_dpad_active\s*\)", source, "LS->DPad conditional branches present")
    require(r"outputs\.dpadUp\s*\|=\s*inputs\.rf4\s*;", source, "LS->DPad up mapping")
    require(r"outputs\.dpadDown\s*\|=\s*inputs\.lf2\s*;", source, "LS->DPad down mapping")
    require(r"outputs\.dpadLeft\s*\|=\s*inputs\.lf3\s*;", source, "LS->DPad left mapping")
    require(r"outputs\.dpadRight\s*\|=\s*inputs\.lf1\s*;", source, "LS->DPad right mapping")
    require(
        r"const\s+StickPoint\s+center\s*=\s*mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;",
        source,
        "LS->DPad analog center uses direction5 values",
    )


def ensure_l_button_path(source: str) -> None:
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


def ensure_runtime_doc_state() -> None:
    if not RUNTIME_DOC_PATH.exists():
        fail(f"missing runtime doc: {RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    require(r"Implementation is complete", text, "runtime doc completion state")
    for token in FORBIDDEN_STOP_CODES:
        if token in text:
            fail(f"runtime doc contains unresolved stop code token: {token}")


def main() -> int:
    if not SOURCE_PATH.exists():
        print("status=FAIL")
        print(f"failure=missing_source:{SOURCE_PATH.relative_to(REPO_ROOT)}")
        return 1

    source = SOURCE_PATH.read_text(encoding="utf-8")
    block = extract_marker_block(source)

    try:
        ensure_anchor_tokens(source)
        ensure_no_old_lt3_tilt3_shape(source, block)
        ensure_chord_shape(block)
        ensure_mode_ls_to_dpad_shape(source, block)
        ensure_l_button_path(source)
        ensure_no_forbidden_tokens(source, block)
        ensure_runtime_doc_state()
    except AssertionError as exc:
        print("status=FAIL")
        print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print(f"source={SOURCE_PATH.relative_to(REPO_ROOT)}")
    print(f"runtime_doc={RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    print("markers=present")
    print("lt3_role=Y2_not_tilt3")
    print("tilt3_role=rf3_and_rf4_chord")
    print("ls_to_dpad_role=rf7")
    print("mode_role=rf8")
    print("l_button_role=lt1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
