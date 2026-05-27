#!/usr/bin/env python3
"""Read-only checker for Ultimate identity profile baseline artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
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


def _normalized_remaps(mode: dict[str, Any]) -> list[dict[str, str | None]]:
    remaps = mode.get("buttonRemapping")
    if not isinstance(remaps, list):
        raise AssertionError("MODE_ULTIMATE buttonRemapping must be a list")

    normalized: list[dict[str, str | None]] = []
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

        activates = entry.get("activates")
        if activates is not None:
            if not isinstance(activates, str):
                raise AssertionError(
                    f"buttonRemapping[{index}].activates must be a string when present"
                )
            if activates == "BTN_UNSPECIFIED":
                raise AssertionError(f"buttonRemapping[{index}] uses forbidden activates BTN_UNSPECIFIED")

        normalized.append({"physicalButton": physical, "activates": activates})
    return normalized


def _identity_representation(remaps: list[dict[str, str | None]]) -> str | None:
    omitted_count = sum(1 for remap in remaps if remap["activates"] is None)
    explicit_self_count = sum(
        1
        for remap in remaps
        if remap["activates"] is not None and remap["activates"] == remap["physicalButton"]
    )
    semantic_count = sum(
        1
        for remap in remaps
        if remap["activates"] is not None and remap["activates"] != remap["physicalButton"]
    )

    if semantic_count > 0:
        return None
    if omitted_count == len(remaps):
        return "omitted_activates"
    if explicit_self_count == len(remaps):
        return "explicit_self_activates"
    return None


def _check_file(path: Path) -> tuple[list[str], str | None, int, int]:
    failures: list[str] = []

    try:
        payload = _load_json(path)
        mode = _ultimate_mode(payload)
        remaps = _normalized_remaps(mode)
    except (FileNotFoundError, json.JSONDecodeError, AssertionError) as exc:
        return [f"{_rel(path)}: {exc}"], None, 0, 0

    physicals = [remap["physicalButton"] for remap in remaps]
    duplicates = sorted(
        {
            physical
            for physical in physicals
            if physicals.count(physical) > 1
        }
    )
    if duplicates:
        failures.append(f"{_rel(path)} duplicate physicalButton entries: {', '.join(duplicates)}")

    expected_set = set(EXPECTED_PHYSICAL_BUTTONS)
    actual_set = set(physicals)
    missing = sorted(expected_set - actual_set)
    extras = sorted(actual_set - expected_set)
    if missing:
        failures.append(f"{_rel(path)} missing expected physicalButton(s): {', '.join(missing)}")
    if extras:
        failures.append(f"{_rel(path)} unexpected physicalButton(s): {', '.join(extras)}")

    identity_representation = _identity_representation(remaps)
    if identity_representation is None:
        failures.append(
            f"{_rel(path)} identity representation is inconsistent or contains semantic remaps"
        )

    semantic_remap_count = sum(
        1
        for remap in remaps
        if remap["activates"] is not None and remap["activates"] != remap["physicalButton"]
    )
    if semantic_remap_count > 0:
        failures.append(
            f"{_rel(path)} semantic remaps remain in MODE_ULTIMATE: {semantic_remap_count}"
        )

    return failures, identity_representation, semantic_remap_count, len(physicals)


def main() -> int:
    failures: list[str] = []
    representations: list[str] = []
    semantic_remap_total = 0
    physical_counts: list[int] = []

    for path in TARGET_FILES:
        file_failures, representation, semantic_remap_count, physical_count = _check_file(path)
        failures.extend(file_failures)
        semantic_remap_total += semantic_remap_count
        physical_counts.append(physical_count)
        if representation is not None:
            representations.append(representation)

    if representations and len(set(representations)) != 1:
        failures.append(
            "identity representation mismatch across files: "
            + ", ".join(sorted(set(representations)))
        )

    resolved_representation = "unknown"
    if representations and len(set(representations)) == 1:
        resolved_representation = representations[0]

    print("files_checked=" + ",".join(_rel(path) for path in TARGET_FILES))
    print(f"identity_representation={resolved_representation}")
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
