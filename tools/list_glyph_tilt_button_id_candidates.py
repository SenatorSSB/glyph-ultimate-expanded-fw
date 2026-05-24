#!/usr/bin/env python3
"""Read-only helper to surface confirmed Glyph Tilt1/Tilt2 button IDs."""

from __future__ import annotations

import re
from pathlib import Path

from glyph_config_model import get_ultimate_mode, list_button_remapping, load_profile_json


REPO_ROOT = Path(__file__).resolve().parents[1]
BUTTON_POSITIONS = REPO_ROOT / "config" / "glyph" / "glyph_mk6" / "include" / "button_positions.hpp"
MATRIX_DEFINITION = REPO_ROOT / "config" / "glyph" / "glyph_mk6" / "include" / "matrix_definition.hpp"
PROFILE_FIXTURE = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json"
)

GEOMETRY_PATTERN = re.compile(r"\b(?:BTN_RF1|BTN_RF2|BTN_RF3|BTN_RF4|BTN_RF5)\b")


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def _print_matching_lines(path: Path) -> None:
    rel_path = path.relative_to(REPO_ROOT)
    print(f"[{rel_path}]")
    if not path.exists():
        print("- missing")
        return

    for line_no, line in enumerate(_read_lines(path), start=1):
        if GEOMETRY_PATTERN.search(line):
            print(f"- {rel_path}:{line_no}: {line.rstrip()}")


def _profile_remaps() -> dict[str, str | None]:
    if not PROFILE_FIXTURE.exists():
        return {}
    profile = load_profile_json(PROFILE_FIXTURE)
    ultimate = get_ultimate_mode(profile)
    return {entry.physical_button: entry.activates for entry in list_button_remapping(ultimate)}


def main() -> None:
    print("status=CONFIRMED_FOR_UPLOADED_MVP_LAYOUT")
    print("tilt1_physical_button=BTN_RF3")
    print("tilt1_logical_post_remap_input=BTN_LT1")
    print("tilt1_future_runtime_input=inputs.lt1")
    print("tilt2_physical_button=BTN_RF4")
    print("tilt2_logical_post_remap_input=BTN_LT2")
    print("tilt2_future_runtime_input=inputs.lt2")
    print("rejected_button_id=BTN_RF5")
    print("runtime_semantics=post_remap_logical_inputs")
    print()

    _print_matching_lines(BUTTON_POSITIONS)
    print()
    _print_matching_lines(MATRIX_DEFINITION)
    print()

    remaps = _profile_remaps()
    print(f"[{PROFILE_FIXTURE.relative_to(REPO_ROOT)}]")
    if not remaps:
        print("- missing profile fixture")
    else:
        for physical_button in ("BTN_RF3", "BTN_RF4", "BTN_RF5"):
            activates = remaps.get(physical_button)
            print(f"- profile_remap {physical_button} -> {activates}")

    print()
    print("interpretation:")
    print("- BTN_RF3 is the physical/profile button for Tilt1 / TILT, replacing MX via BTN_LT1.")
    print("- BTN_RF4 is the physical/profile button for Tilt2, replacing MY via BTN_LT2.")
    print("- BTN_RF5 is rejected for this uploaded MVP layout.")
    print("- Future runtime code should use inputs.lt1 / inputs.lt2 after remap.")


if __name__ == "__main__":
    main()
