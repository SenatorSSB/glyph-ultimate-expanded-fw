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
    "{169, 184}",
    "{128, 184}",
    "{87, 184}",
    "{169, 172}",
    "{128, 172}",
    "{87, 172}",
    "{169, 72}",
    "{128, 72}",
    "{87, 72}",
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


def read_runtime_doc() -> str:
    if not RUNTIME_DOC_PATH.exists():
        fail(f"missing runtime doc: {RUNTIME_DOC_PATH.relative_to(REPO_ROOT)}")
    text = RUNTIME_DOC_PATH.read_text(encoding="utf-8")

    require(r"LT3\s*=\s*L", text, "runtime doc LT3=L")
    require(r"LT1\s*=\s*Z", text, "runtime doc LT1=Z")
    require(r"RF15\s*=\s*Up\+A", text, "runtime doc RF15 Up+A alias")
    require(r"Y2/MY2.*scratched|scratched.*Y2/MY2", text, "runtime doc marks Y2/MY2 scratched", flags=re.IGNORECASE)
    require(r"Y1\+Tilt1.*special", text, "runtime doc Y1+Tilt1 special composite", flags=re.IGNORECASE)
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
    require(r"outputs\.buttonR\s*=\s*inputs\.rt1\s*\|\|\s*inputs\.lt1\s*;", source, "RT1/LT1 shared Z carrier")
    require(r"outputs\.triggerRDigital\s*=\s*inputs\.rf16\s*;", source, "RF16 remains R carrier")

    # Remove old LT1/LT3/Y2 shapes.
    if "outputs.buttonL = inputs.lt1;" in source:
        fail("LT1 must no longer drive L")
    if "outputs.triggerLDigital = inputs.lt1;" in source:
        fail("LT1 must no longer drive L digital carrier")
    if "outputs.buttonR = inputs.rt1;" in source:
        fail("Z carrier must include LT1 in addition to RT1")
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

    # LT1 hard final override ordering.
    require(r"if\s*\(\s*direction_plus_a_active\s*\)", block, "direction-plus-A override block")
    require(r"if\s*\(\s*lt1_z_airdodge_override_active\s*\)", block, "LT1 hard override block")
    require(
        r"if\s*\(\s*direction_plus_a_active\s*\)\s*\{.*?\}\s*if\s*\(\s*lt1_z_airdodge_override_active\s*\)\s*\{",
        block,
        "LT1 override occurs after direction-plus-A override",
        flags=re.DOTALL,
    )
    require(r"outputs\.leftStickX\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.x\s*;", block, "LT1 final X override")
    require(r"outputs\.leftStickY\s*=\s*kLt1LowMagnitudeTable\[lt1_direction_index\]\.y\s*;", block, "LT1 final Y override")

    # LS->DPad keeps analog centering and suppresses LT1 low-table override in that branch.
    require(
        r"if\s*\(\s*ls_to_dpad_active\s*\)\s*\{\s*const\s+StickPoint\s+center\s*=\s*mode_active\s*\?\s*kModeDefaultTable\[kDirectionFiveIndex\]\s*:\s*kDefaultTable\[kDirectionFiveIndex\]\s*;\s*outputs\.leftStickX\s*=\s*center\.x\s*;\s*outputs\.leftStickY\s*=\s*center\.y\s*;\s*\}\s*else\s*\{",
        block,
        "LS->DPad center branch with else-path override",
        flags=re.DOTALL,
    )

    # RF15 aliases RF12 across forced-up/direction-plus-A and LT1 direction resolution.
    require(
        r"const\s+bool\s+force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        source,
        "digital forced-up includes RF15",
    )
    require(
        r"const\s+bool\s+up_a_active\s*=\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        block,
        "direction-plus-A up input includes RF15",
    )
    require(
        r"const\s+bool\s+lt1_force_up_active\s*=\s*inputs\.rf6\s*\|\|\s*inputs\.rf12\s*\|\|\s*inputs\.rf15\s*;",
        block,
        "LT1 low-table forced-up includes RF15",
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
    print("forced_up_role=rf6_or_rf12_or_rf15")
    print("direction_plus_a_role=lt6_down_a_rf12_or_rf15_up_a")
    print("lt3_role=L")
    print("lt1_role=Z_plus_low_magnitude_override")
    print("z_button_role=rt1_or_lt1_shared_buttonR_carrier")
    print("r_button_role=rf16")
    print("y1_tilt1_special_composite=enabled")
    print("rt4_rt5_cstick_swap=enabled")
    print("y2_my2_runtime_role=scratched_inactive")
    print("ls_to_dpad_role=rf7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
