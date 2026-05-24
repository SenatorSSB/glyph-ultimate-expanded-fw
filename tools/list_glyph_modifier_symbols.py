#!/usr/bin/env python3
"""Read-only helper to list Glyph modifier-related symbols from known sources."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

KNOWN_FILES = [
    REPO_ROOT / "platformio.ini",
    REPO_ROOT / "config" / "glyph" / "env.ini",
    REPO_ROOT / ".pio" / "libdeps" / "glyph_mk6" / "HayBox-proto" / "config.proto",
    REPO_ROOT / ".pio" / "libdeps" / "glyph_mk6" / "HayBox-proto" / "config.options",
    REPO_ROOT / ".pio" / "build" / "glyph_mk6" / "nanopb" / "generated-src" / "config.pb.h",
    REPO_ROOT / "src" / "modes" / "CustomControllerMode.cpp",
    REPO_ROOT / "include" / "modes" / "CustomControllerMode.hpp",
    REPO_ROOT / "src" / "modes" / "Ultimate.cpp",
    REPO_ROOT / "src" / "core" / "mode_selection.cpp",
    REPO_ROOT / "HAL" / "pico" / "include" / "util" / "state_util.hpp",
    REPO_ROOT / "include" / "core" / "state.hpp",
    REPO_ROOT / "config" / "glyph" / "common" / "include" / "glyph_overrides.hpp",
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "GlyphUserProfilesUlt-filled.json",
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "GlyphUltFilled2.json",
    REPO_ROOT / "docs" / "sources" / "raw" / "GlyphUserProfiles.json",
]

PATTERNS = {
    "proto messages/fields": re.compile(
        r"\b(?:message|enum)\s+([A-Za-z_][A-Za-z0-9_]*)\b|"
        r"\b(?:repeated\s+)?(?:Button|AnalogAxis|AnalogTrigger|DigitalOutput|"
        r"ModifierCombinationMode|uint32|float)\s+([a-z][A-Za-z0-9_]*)\s*=",
    ),
    "OUT_* logical outputs": re.compile(r"\bOUT_[A-Z0-9_]+\b"),
    "modifier-related symbols": re.compile(
        r"\b(?:AnalogModifier|AnalogTriggerMapping|CustomModeConfig|"
        r"ModifierCombinationMode|COMBINATION_MODE_[A-Z_]+|AXIS_[A-Z_]+|"
        r"SD_[A-Z_]+|stick_range|modifiers|modifier|multiplier|"
        r"combination_mode|analog_trigger_mappings|stick_direction_mappings|"
        r"button_combo_mappings|digital_button_mappings)\b",
    ),
    "candidate runtime functions/files": re.compile(
        r"\b(?:CustomControllerMode::SetConfig|CustomControllerMode::UpdateAnalogOutputs|"
        r"CustomControllerMode::UpdateDigitalOutputs|axis_pointer|set_mode|"
        r"Ultimate::UpdateAnalogOutputs|UpdateDirections|all_buttons_held)\b",
    ),
}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None


def main() -> None:
    scanned_files = 0
    missing_files: list[str] = []
    groups: dict[str, set[str]] = defaultdict(set)
    sources: dict[str, set[str]] = defaultdict(set)

    for path in KNOWN_FILES:
        text = _read_text(path)
        if text is None:
            missing_files.append(str(path.relative_to(REPO_ROOT)))
            continue
        scanned_files += 1
        relative = str(path.relative_to(REPO_ROOT))
        for group_name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                values = [part for part in match.groups() if part]
                if not values:
                    values = [match.group(0)]
                for value in values:
                    groups[group_name].add(value)
                    sources[f"{group_name}:{value}"].add(relative)

    print(f"scanned_files={scanned_files}")
    if missing_files:
        print("missing_files_tolerated=" + str(len(missing_files)))
        for path in missing_files:
            print(f"- {path}")

    for group_name in PATTERNS:
        print()
        print(f"{group_name}:")
        for symbol in sorted(groups[group_name]):
            source_list = ", ".join(sorted(sources[f"{group_name}:{symbol}"]))
            print(f"- {symbol} [{source_list}]")


if __name__ == "__main__":
    main()
