#!/usr/bin/env python3
"""List source-backed Glyph physical/logical layout mapping signals.

Read-only helper for docs/calibration layout work. It parses simple matrix and
button-position source shapes where practical, then prints grep-style runtime and
fixture lines relevant to the current Ultimate MVP Tilt mapping.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "config" / "glyph" / "glyph_mk6" / "include" / "matrix_definition.hpp"
POSITIONS_PATH = REPO_ROOT / "config" / "glyph" / "glyph_mk6" / "include" / "button_positions.hpp"
ULTIMATE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
MVP_FIXTURE = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json"
)
TRACKED_BUTTONS = ["BTN_RF3", "BTN_RF4", "BTN_RF5", "BTN_LT1", "BTN_LT2", "BTN_LF3", "BTN_LF1", "BTN_LF2"]


def display_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def parse_matrix() -> dict[str, str]:
    lines = read_lines(MATRIX_PATH)
    result: dict[str, str] = {}
    row_index = 0
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped.startswith("{") or "BTN_" not in stripped:
            continue
        tokens = re.findall(r"\b(?:BTN_[A-Z0-9_]+|NA)\b", stripped)
        for col_index, token in enumerate(tokens):
            if token == "NA":
                continue
            result[token] = f"row={row_index}, col={col_index}, line={line_number}"
        row_index += 1
    return result


def parse_positions() -> dict[str, list[str]]:
    lines = read_lines(POSITIONS_PATH)
    positions: dict[str, list[str]] = {}
    current_layout = "<unknown>"
    for line_number, line in enumerate(lines, start=1):
        layout_match = re.match(r"InputViewerButton\s+(\w+)\[\]\s*=", line.strip())
        if layout_match:
            current_layout = layout_match.group(1)
            continue
        entry_match = re.search(r"\{\s*(BTN_[A-Z0-9_]+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,", line)
        if not entry_match:
            continue
        button, x_value, y_value = entry_match.groups()
        positions.setdefault(button, []).append(
            f"{current_layout}:x={x_value},y={y_value},line={line_number}",
        )
    return positions


def grep_lines(path: Path, patterns: Iterable[str]) -> list[str]:
    compiled = [re.compile(pattern) for pattern in patterns]
    matches: list[str] = []
    for line_number, line in enumerate(read_lines(path), start=1):
        if any(pattern.search(line) for pattern in compiled):
            matches.append(f"{display_path(path)}:{line_number}: {line.rstrip()}")
    return matches


def load_mvp_remaps() -> list[tuple[str, str]]:
    payload = json.loads(MVP_FIXTURE.read_text(encoding="utf-8"))
    remaps: list[tuple[str, str]] = []
    for mode in payload.get("gameModeConfigs", []):
        if mode.get("modeId") != "MODE_ULTIMATE":
            continue
        for remap in mode.get("buttonRemapping", []):
            physical = remap.get("physicalButton")
            activates = remap.get("activates")
            if physical in {"BTN_RF3", "BTN_RF4", "BTN_RF5"}:
                remaps.append((physical, activates if isinstance(activates, str) else "<omitted>"))
    return remaps


def main() -> int:
    matrix = parse_matrix()
    positions = parse_positions()

    print("glyph_physical_logical_layout_sources")
    print("source_files:")
    for path in (MATRIX_PATH, POSITIONS_PATH, ULTIMATE_PATH, MVP_FIXTURE):
        print(f"- {display_path(path)}")

    print("\ntracked_button_matrix_positions:")
    for button in TRACKED_BUTTONS:
        print(f"- {button}: {matrix.get(button, 'not_found')}")

    print("\ntracked_button_display_positions:")
    for button in TRACKED_BUTTONS:
        entries = positions.get(button, [])
        rendered = "; ".join(entries) if entries else "not_found"
        print(f"- {button}: {rendered}")

    print("\nmvp_profile_remaps:")
    for physical, activates in load_mvp_remaps():
        print(f"- {physical} -> {activates}")

    print("\nultimate_runtime_input_lines:")
    runtime_patterns = [
        r"outputs\.leftStick(Left|Right|Down|Up)",
        r"outputs\.rightStick(Left|Right|Down|Up)",
        r"outputs\.mod[XY]",
        r"outputs\.trigger[LR]Digital",
        r"trigger[LR]Analog",
        r"UpdateDirections\(",
        r"inputs\.lt1|inputs\.lt2|inputs\.rf5|inputs\.rf4|inputs\.lf[1234]",
    ]
    for line in grep_lines(ULTIMATE_PATH, runtime_patterns):
        print(f"- {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
