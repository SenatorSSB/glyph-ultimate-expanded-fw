#!/usr/bin/env python3
"""Compare the baked Ultimate default profile against the friend fixture."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json"
)
TARGET_PATH = REPO_ROOT / "config" / "glyph" / "common" / "include" / "glyph_overrides.hpp"


def fail(message: str) -> int:
    print("status=FAIL")
    print(f"failure={message}")
    return 1


def load_fixture_ultimate() -> dict[str, Any]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        raise ValueError("fixture missing gameModeConfigs list")
    for mode in modes:
        if isinstance(mode, dict) and mode.get("modeId") == "MODE_ULTIMATE":
            return mode
    raise ValueError("fixture missing MODE_ULTIMATE")


def find_balanced_block(text: str, open_brace_index: int) -> str:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index + 1 : index]

    raise ValueError("unclosed C++ initializer block")


def find_field_block(source: str, field_name: str) -> str:
    marker = f".{field_name}"
    marker_index = source.find(marker)
    if marker_index < 0:
        raise ValueError(f"missing field block: {field_name}")
    open_index = source.find("{", marker_index)
    if open_index < 0:
        raise ValueError(f"missing opening brace for field block: {field_name}")
    return find_balanced_block(source, open_index)


def find_ultimate_cpp_block(source: str) -> str:
    marker = "GameModeConfig"
    search_index = 0
    while True:
        match_index = source.find(marker, search_index)
        if match_index < 0:
            raise ValueError("target missing GameModeConfig MODE_ULTIMATE block")
        open_index = source.find("{", match_index)
        if open_index < 0:
            raise ValueError("target contains malformed GameModeConfig block")
        block = find_balanced_block(source, open_index)
        if re.search(r"\.mode_id\s*=\s*MODE_ULTIMATE\b", block):
            return block
        search_index = open_index + len(block) + 2


def parse_scalar_string(block: str, field_name: str) -> str:
    pattern = re.compile(rf"\.{re.escape(field_name)}\s*=\s*\"(?P<value>[^\"]*)\"")
    match = pattern.search(block)
    if match is None:
        raise ValueError(f"missing string field: {field_name}")
    return match.group("value")


def parse_scalar_token(block: str, field_name: str) -> str:
    pattern = re.compile(rf"\.{re.escape(field_name)}\s*=\s*(?P<value>[A-Z0-9_]+)")
    match = pattern.search(block)
    if match is None:
        raise ValueError(f"missing token field: {field_name}")
    return match.group("value")


def parse_scalar_int(block: str, field_name: str) -> int:
    pattern = re.compile(rf"\.{re.escape(field_name)}\s*=\s*(?P<value>\d+)")
    match = pattern.search(block)
    if match is None:
        raise ValueError(f"missing integer field: {field_name}")
    return int(match.group("value"))


def parse_socd_pairs(block: str) -> list[dict[str, str]]:
    pairs_block = find_field_block(block, "socd_pairs")
    pattern = re.compile(
        r"SocdPair\s*\{\s*"
        r"\.button_dir1\s*=\s*(?P<button_dir1>BTN_[A-Z0-9]+)\s*,\s*"
        r"\.button_dir2\s*=\s*(?P<button_dir2>BTN_[A-Z0-9]+)\s*,\s*"
        r"\.socd_type\s*=\s*(?P<socd_type>SOCD_[A-Z0-9_]+)\s*"
        r"\}",
        re.DOTALL,
    )
    return [
        {
            "buttonDir1": match.group("button_dir1"),
            "buttonDir2": match.group("button_dir2"),
            "socdType": match.group("socd_type"),
        }
        for match in pattern.finditer(pairs_block)
    ]


def parse_button_remaps(block: str) -> list[dict[str, str]]:
    remaps_block = find_field_block(block, "button_remapping")
    pattern = re.compile(
        r"ButtonRemap\s*\{\s*"
        r"\.physical_button\s*=\s*(?P<physical>BTN_[A-Z0-9]+)"
        r"(?:\s*,\s*\.activates\s*=\s*(?P<activates>BTN_[A-Z0-9]+))?\s*"
        r"\}",
        re.DOTALL,
    )
    remaps: list[dict[str, str]] = []
    for match in pattern.finditer(remaps_block):
        entry = {"physicalButton": match.group("physical")}
        activates = match.group("activates")
        if activates is not None:
            entry["activates"] = activates
        remaps.append(entry)
    return remaps


def parse_token_list(block: str, field_name: str, prefix: str) -> list[str]:
    field_block = find_field_block(block, field_name)
    return re.findall(rf"\b{re.escape(prefix)}[A-Z0-9_]+\b", field_block)


def parse_cpp_ultimate() -> dict[str, Any]:
    source = TARGET_PATH.read_text(encoding="utf-8")
    block = find_ultimate_cpp_block(source)
    socd_pairs = parse_socd_pairs(block)
    button_remapping = parse_button_remaps(block)
    applicable_backends = parse_token_list(block, "applicable_backends", "COMMS_BACKEND_")
    menu_button_icon = parse_token_list(block, "menu_button_icon", "OUT_")

    parsed = {
        "modeId": parse_scalar_token(block, "mode_id"),
        "name": parse_scalar_string(block, "name"),
        "socdPairs": socd_pairs,
        "buttonRemapping": button_remapping,
        "rgbConfig": parse_scalar_int(block, "rgb_config"),
        "layoutPlate": parse_scalar_token(block, "layout_plate"),
        "applicableBackends": applicable_backends,
        "menuButtonIcon": menu_button_icon,
        "counts": {
            "socdPairs": parse_scalar_int(block, "socd_pairs_count"),
            "buttonRemapping": parse_scalar_int(block, "button_remapping_count"),
            "applicableBackends": parse_scalar_int(block, "applicable_backends_count"),
            "menuButtonIcon": parse_scalar_int(block, "menu_button_icon_count"),
        },
    }
    return parsed


def normalized_fixture_subset(mode: dict[str, Any]) -> dict[str, Any]:
    return {
        "modeId": mode.get("modeId"),
        "name": mode.get("name"),
        "socdPairs": mode.get("socdPairs"),
        "buttonRemapping": mode.get("buttonRemapping"),
        "rgbConfig": mode.get("rgbConfig"),
        "layoutPlate": mode.get("layoutPlate"),
        "applicableBackends": mode.get("applicableBackends"),
        "menuButtonIcon": mode.get("menuButtonIcon"),
    }


def main() -> int:
    try:
        fixture = normalized_fixture_subset(load_fixture_ultimate())
        target = parse_cpp_ultimate()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(str(exc))

    target_without_counts = {key: value for key, value in target.items() if key != "counts"}
    if target_without_counts != fixture:
        print("status=FAIL")
        for key in fixture:
            if target_without_counts.get(key) != fixture.get(key):
                print(f"mismatch={key}")
                print(f"expected={fixture.get(key)!r}")
                print(f"actual={target_without_counts.get(key)!r}")
        return 1

    count_expectations = {
        "socdPairs": len(target["socdPairs"]),
        "buttonRemapping": len(target["buttonRemapping"]),
        "applicableBackends": len(target["applicableBackends"]),
        "menuButtonIcon": len(target["menuButtonIcon"]),
    }
    if target["counts"] != count_expectations:
        print("status=FAIL")
        print(f"mismatch=counts")
        print(f"expected={count_expectations!r}")
        print(f"actual={target['counts']!r}")
        return 1

    for index, remap in enumerate(target["buttonRemapping"]):
        if remap.get("physicalButton") != remap.get("activates"):
            return fail(f"button_remapping[{index}] is not physical/logical 1-to-1")

    print("status=PASS")
    print(f"fixture={FIXTURE_PATH.relative_to(REPO_ROOT)}")
    print(f"target={TARGET_PATH.relative_to(REPO_ROOT)}")
    print("mode_id=MODE_ULTIMATE")
    print(f"socd_pairs_count={target['counts']['socdPairs']}")
    print(f"button_remapping_count={target['counts']['buttonRemapping']}")
    print(f"applicable_backends_count={target['counts']['applicableBackends']}")
    print(f"menu_button_icon_count={target['counts']['menuButtonIcon']}")
    print("identity_button_remapping=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
