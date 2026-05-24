#!/usr/bin/env python3
"""Validate Glyph Ultimate calibration fixtures with stdlib-only checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "docs" / "calibration" / "fixtures"
CAL1_PATH = FIXTURE_DIR / "GlyphUserProfilesUlt-filled.json"
CAL2_PATH = FIXTURE_DIR / "GlyphUltFilled2.json"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing fixture: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"fixture root must be object: {path}")
    return data


def _find_ultimate_mode(config: dict[str, Any]) -> dict[str, Any]:
    game_modes = config.get("gameModeConfigs")
    if not isinstance(game_modes, list):
        raise AssertionError("gameModeConfigs must be a list")
    for mode in game_modes:
        if not isinstance(mode, dict):
            continue
        if mode.get("name") == "Ultimate" or mode.get("modeId") == "MODE_ULTIMATE":
            return mode
    raise AssertionError("could not find Ultimate mode (name=Ultimate or modeId=MODE_ULTIMATE)")


def _get_button_remaps(mode: dict[str, Any]) -> list[tuple[str, str | None]]:
    remapping = mode.get("buttonRemapping")
    if not isinstance(remapping, list):
        raise AssertionError("buttonRemapping must be a list")
    result: list[tuple[str, str | None]] = []
    for index, entry in enumerate(remapping):
        if not isinstance(entry, dict):
            raise AssertionError(f"buttonRemapping[{index}] must be an object")
        physical_button = entry.get("physicalButton")
        if not isinstance(physical_button, str) or not physical_button:
            raise AssertionError(f"buttonRemapping[{index}] missing physicalButton")
        activates = entry.get("activates")
        if activates is not None and not isinstance(activates, str):
            raise AssertionError(f"buttonRemapping[{index}].activates must be string when present")
        result.append((physical_button, activates))
    return result


def _get_socd_pairs(mode: dict[str, Any]) -> list[tuple[str, str, str | None]]:
    socd_pairs = mode.get("socdPairs")
    if not isinstance(socd_pairs, list):
        raise AssertionError("socdPairs must be a list")
    result: list[tuple[str, str, str | None]] = []
    for index, entry in enumerate(socd_pairs):
        if not isinstance(entry, dict):
            raise AssertionError(f"socdPairs[{index}] must be an object")
        first = entry.get("buttonDir1")
        second = entry.get("buttonDir2")
        if not isinstance(first, str) or not isinstance(second, str):
            raise AssertionError(f"socdPairs[{index}] missing buttonDir1/buttonDir2")
        socd_type = entry.get("socdType")
        if socd_type is not None and not isinstance(socd_type, str):
            raise AssertionError(f"socdPairs[{index}].socdType must be string when present")
        result.append((first, second, socd_type))
    return result


def _unordered_pair(first: str, second: str) -> tuple[str, str]:
    return tuple(sorted((first, second)))


def _assert_pairs_include(
    pairs: list[tuple[str, str, str | None]],
    expected_pairs: list[tuple[str, str]],
) -> None:
    observed = {_unordered_pair(first, second) for first, second, _ in pairs}
    missing = [pair for pair in expected_pairs if _unordered_pair(*pair) not in observed]
    if missing:
        raise AssertionError(f"missing expected SOCD pairs: {missing}")


def _assert_pairs_exclude(
    pairs: list[tuple[str, str, str | None]],
    forbidden_pairs: list[tuple[str, str]],
) -> None:
    observed = {_unordered_pair(first, second) for first, second, _ in pairs}
    present = [pair for pair in forbidden_pairs if _unordered_pair(*pair) in observed]
    if present:
        raise AssertionError(f"forbidden SOCD pairs unexpectedly present: {present}")


def _assert_remap(remaps: list[tuple[str, str | None]], physical_button: str, activates: str) -> None:
    for source_button, target_button in remaps:
        if source_button == physical_button:
            if target_button != activates:
                raise AssertionError(
                    f"expected remap {physical_button} -> {activates}, got {target_button!r}",
                )
            return
    raise AssertionError(f"missing remap entry for {physical_button}")


def _assert_omitted_activates(remaps: list[tuple[str, str | None]], physical_button: str) -> None:
    entries = [target for source, target in remaps if source == physical_button]
    if not entries:
        raise AssertionError(f"missing remap entry for {physical_button}")
    if entries[0] is not None:
        raise AssertionError(f"expected omitted activates for {physical_button}, got {entries[0]!r}")


def main() -> None:
    cal1 = _load_json(CAL1_PATH)
    cal2 = _load_json(CAL2_PATH)

    ultimate1 = _find_ultimate_mode(cal1)
    ultimate2 = _find_ultimate_mode(cal2)

    if ultimate1.get("layoutPlate") != "LAYOUT_PLATE_EVERYTHING":
        raise AssertionError("calibration 1 Ultimate layoutPlate mismatch")
    if ultimate2.get("layoutPlate") != "LAYOUT_PLATE_EVERYTHING":
        raise AssertionError("calibration 2 Ultimate layoutPlate mismatch")

    remaps1 = _get_button_remaps(ultimate1)
    remaps2 = _get_button_remaps(ultimate2)
    socd1 = _get_socd_pairs(ultimate1)
    socd2 = _get_socd_pairs(ultimate2)

    if len(socd1) != 6:
        raise AssertionError(f"calibration 1 SOCD pair count expected 6, got {len(socd1)}")
    if len(socd2) != 4:
        raise AssertionError(f"calibration 2 SOCD pair count expected 4, got {len(socd2)}")

    _assert_pairs_include(
        socd1,
        [
            ("BTN_LF3", "BTN_LF1"),
            ("BTN_LF2", "BTN_RF4"),
            ("BTN_RT3", "BTN_RT5"),
            ("BTN_RT2", "BTN_RT4"),
            ("BTN_LF8", "BTN_LF6"),
            ("BTN_RF7", "BTN_RF8"),
        ],
    )
    _assert_pairs_include(
        socd2,
        [
            ("BTN_LF3", "BTN_LF1"),
            ("BTN_RT3", "BTN_RT5"),
            ("BTN_RT2", "BTN_RT4"),
            ("BTN_LF8", "BTN_LF6"),
        ],
    )
    _assert_pairs_exclude(
        socd2,
        [
            ("BTN_LF2", "BTN_RF4"),
            ("BTN_RF7", "BTN_RF8"),
        ],
    )

    for physical_button in ("BTN_MB1", "BTN_MB2", "BTN_MB3"):
        _assert_omitted_activates(remaps1, physical_button)
        _assert_omitted_activates(remaps2, physical_button)

    for physical_button, activates in (
        ("BTN_LF2", "BTN_RF4"),
        ("BTN_LT3", "BTN_LF8"),
        ("BTN_LT4", "BTN_LF6"),
        ("BTN_RF13", "BTN_RF7"),
        ("BTN_RF14", "BTN_RF3"),
        ("BTN_RF15", "BTN_RF6"),
    ):
        _assert_remap(remaps1, physical_button, activates)

    for physical_button, activates in (
        ("BTN_LF1", "BTN_LF3"),
        ("BTN_LF2", "BTN_LF8"),
        ("BTN_RF12", "BTN_RT4"),
        ("BTN_RF11", "BTN_MB7"),
        ("BTN_RF13", "BTN_LT1"),
        ("BTN_RF14", "BTN_LT2"),
        ("BTN_RF16", "BTN_RF8"),
    ):
        _assert_remap(remaps2, physical_button, activates)

    print(
        "Calibration fixture checks passed: "
        f"cal1_socd={len(socd1)}, cal2_socd={len(socd2)}, "
        f"cal1_remaps={len(remaps1)}, cal2_remaps={len(remaps2)}",
    )


if __name__ == "__main__":
    main()
