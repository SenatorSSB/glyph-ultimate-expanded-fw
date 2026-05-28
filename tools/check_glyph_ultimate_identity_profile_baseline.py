#!/usr/bin/env python3
"""Read-only checker for Ultimate explicit self-activates identity baseline artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_FILES = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "artifacts"
    / "glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json",
)

# Baseline physical button list from the prior active Ultimate LT3 artifact path.
EXPECTED_PHYSICAL_BUTTONS = (
    "BTN_LF2",
    "BTN_LF4",
    "BTN_LT1",
    "BTN_RF1",
    "BTN_RF3",
    "BTN_RF4",
    "BTN_RF5",
    "BTN_RF6",
    "BTN_RT1",
    "BTN_LF5",
    "BTN_LT6",
    "BTN_RF13",
    "BTN_LF6",
    "BTN_RF11",
    "BTN_RF10",
    "BTN_LT3",
    "BTN_LF7",
    "BTN_LF8",
    "BTN_LT2",
    "BTN_LT4",
    "BTN_LT5",
    "BTN_RF9",
    "BTN_RF12",
    "BTN_RF14",
    "BTN_RF15",
    "BTN_RF16",
    "BTN_MB1",
    "BTN_MB2",
    "BTN_MB3",
    "BTN_MB4",
    "BTN_MB5",
    "BTN_MB6",
    "BTN_MB7",
    "BTN_RF2",
    "BTN_LF3",
    "BTN_LF1",
    "BTN_RF7",
    "BTN_RF8",
    "BTN_RT3",
    "BTN_RT5",
    "BTN_RT2",
    "BTN_RT4",
)

EXPECTED_ULTIMATE_SOCD_PAIRS = (
    ("BTN_LF3", "BTN_LF1", "SOCD_2IP"),
    ("BTN_LF5", "BTN_LF2", "SOCD_2IP"),
    ("BTN_RT3", "BTN_RT5", "SOCD_2IP"),
    ("BTN_RT2", "BTN_RT4", "SOCD_2IP"),
)

FORBIDDEN_ULTIMATE_SOCD_PAIRS = (
    ("BTN_LF2", "BTN_RF4"),
    ("BTN_LF8", "BTN_LF6"),
    ("BTN_RF7", "BTN_RF8"),
)

REQUIRED_RUNTIME_DIRECTION_PLUS_A_INPUTS = (
    "BTN_LT6",
    "BTN_RF12",
    "BTN_RF16",
)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("root JSON value must be an object")
    return payload


def _ultimate_mode(payload: dict[str, Any]) -> dict[str, Any]:
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        raise AssertionError("gameModeConfigs must be a list")

    matches: list[dict[str, Any]] = []
    for mode in modes:
        if not isinstance(mode, dict):
            continue
        if mode.get("modeId") == "MODE_ULTIMATE" or mode.get("name") == "Ultimate":
            matches.append(mode)

    if len(matches) != 1:
        raise AssertionError(
            f"expected exactly one MODE_ULTIMATE/Ultimate mode, found {len(matches)}"
        )
    return matches[0]


def _normalized_remaps(mode: dict[str, Any]) -> list[dict[str, str]]:
    remaps = mode.get("buttonRemapping")
    if not isinstance(remaps, list):
        raise AssertionError("MODE_ULTIMATE buttonRemapping must be a list")

    normalized: list[dict[str, str]] = []
    for index, entry in enumerate(remaps):
        if not isinstance(entry, dict):
            raise AssertionError(f"buttonRemapping[{index}] must be an object")

        physical = entry.get("physicalButton")
        if not isinstance(physical, str) or not physical:
            raise AssertionError(
                f"buttonRemapping[{index}].physicalButton must be a non-empty string"
            )
        if physical == "BTN_UNSPECIFIED":
            raise AssertionError(f"buttonRemapping[{index}] uses forbidden BTN_UNSPECIFIED")

        if "activates" not in entry:
            raise AssertionError(f"buttonRemapping[{index}] must include activates")
        activates = entry.get("activates")
        if not isinstance(activates, str) or not activates:
            raise AssertionError(
                f"buttonRemapping[{index}].activates must be a non-empty string"
            )
        if activates == "BTN_UNSPECIFIED":
            raise AssertionError(f"buttonRemapping[{index}] uses forbidden activates BTN_UNSPECIFIED")
        if activates != physical:
            raise AssertionError(
                f"buttonRemapping[{index}] must be explicit identity ({physical} -> {physical}), got {physical} -> {activates}"
            )

        normalized.append({"physicalButton": physical, "activates": activates})
    return normalized


def _normalized_socd_pairs(mode: dict[str, Any]) -> list[tuple[str, str, str | None]]:
    pairs = mode.get("socdPairs")
    if not isinstance(pairs, list):
        raise AssertionError("MODE_ULTIMATE socdPairs must be a list")

    normalized: list[tuple[str, str, str | None]] = []
    for index, entry in enumerate(pairs):
        if not isinstance(entry, dict):
            raise AssertionError(f"socdPairs[{index}] must be an object")
        left = entry.get("buttonDir1")
        right = entry.get("buttonDir2")
        socd_type = entry.get("socdType")
        if not isinstance(left, str) or not isinstance(right, str):
            raise AssertionError(f"socdPairs[{index}] buttonDir1/buttonDir2 must be strings")
        if socd_type is not None and not isinstance(socd_type, str):
            raise AssertionError(f"socdPairs[{index}].socdType must be a string when present")
        normalized.append((left, right, socd_type))
    return normalized


def _check_file(path: Path) -> tuple[list[str], int, int]:
    failures: list[str] = []

    try:
        payload = _load_json(path)
        mode = _ultimate_mode(payload)
        remaps = _normalized_remaps(mode)
        socd_pairs = _normalized_socd_pairs(mode)
    except (FileNotFoundError, json.JSONDecodeError, AssertionError) as exc:
        return [f"{_rel(path)}: {exc}"], 0, 0

    physicals = [remap["physicalButton"] for remap in remaps]
    seen: set[str] = set()
    duplicates: set[str] = set()
    for physical in physicals:
        if physical in seen:
            duplicates.add(physical)
        seen.add(physical)
    duplicates_sorted = sorted(duplicates)
    if duplicates_sorted:
        failures.append(
            f"{_rel(path)} duplicate physicalButton entries: {', '.join(duplicates_sorted)}"
        )

    expected_set = set(EXPECTED_PHYSICAL_BUTTONS)
    actual_set = set(physicals)
    missing = sorted(expected_set - actual_set)
    extras = sorted(actual_set - expected_set)
    if missing:
        failures.append(f"{_rel(path)} missing expected physicalButton(s): {', '.join(missing)}")
    if extras:
        failures.append(f"{_rel(path)} unexpected physicalButton(s): {', '.join(extras)}")

    semantic_remap_count = sum(1 for remap in remaps if remap["activates"] != remap["physicalButton"])
    if semantic_remap_count > 0:
        failures.append(
            f"{_rel(path)} semantic remaps remain in MODE_ULTIMATE: {semantic_remap_count}"
        )

    remap_map = {remap["physicalButton"]: remap["activates"] for remap in remaps}
    for button in REQUIRED_RUNTIME_DIRECTION_PLUS_A_INPUTS:
        if remap_map.get(button) != button:
            failures.append(
                f"{_rel(path)} missing explicit self-activates runtime input: {button}"
            )

    actual_socd_set = set(socd_pairs)
    for expected_pair in EXPECTED_ULTIMATE_SOCD_PAIRS:
        if expected_pair not in actual_socd_set:
            failures.append(
                f"{_rel(path)} missing expected MODE_ULTIMATE SOCD pair: {expected_pair}"
            )
    for forbidden_left, forbidden_right in FORBIDDEN_ULTIMATE_SOCD_PAIRS:
        if any(
            left == forbidden_left and right == forbidden_right
            for left, right, _socd_type in socd_pairs
        ):
            failures.append(
                f"{_rel(path)} forbidden legacy MODE_ULTIMATE SOCD pair remains: "
                f"{forbidden_left} vs {forbidden_right}"
            )

    return failures, semantic_remap_count, len(physicals)


def main() -> int:
    failures: list[str] = []
    semantic_remap_total = 0
    physical_counts: list[int] = []

    for path in TARGET_FILES:
        file_failures, semantic_remap_count, physical_count = _check_file(path)
        failures.extend(file_failures)
        semantic_remap_total += semantic_remap_count
        physical_counts.append(physical_count)

    print("files_checked=" + ",".join(_rel(path) for path in TARGET_FILES))
    print("identity_representation=explicit_self_activates")
    print(
        "required_runtime_direction_plus_a_inputs="
        + ",".join(REQUIRED_RUNTIME_DIRECTION_PLUS_A_INPUTS)
    )
    print(f"semantic_remap_count={semantic_remap_total}")
    # Both files should carry the same MODE_ULTIMATE physical button count.
    unique_counts = sorted(set(physical_counts))
    if len(unique_counts) == 1:
        print(f"physical_button_count={unique_counts[0]}")
    else:
        print("physical_button_count=" + ",".join(str(count) for count in unique_counts))

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
