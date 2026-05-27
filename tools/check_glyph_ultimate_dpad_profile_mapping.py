#!/usr/bin/env python3
"""Read-only checker for Ultimate D-pad profile mapping in LT3 artifacts/fixtures."""

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

EXPECTED_DPAD_CLUSTER = {
    "BTN_RF13": "BTN_RF8",
    "BTN_RF10": "BTN_RF7",
    "BTN_LF6": "BTN_LF8",
    "BTN_RF11": "BTN_LF6",
}

EXPECTED_DPAD_LOGICAL_COUNTS = {
    "BTN_RF8": 1,
    "BTN_RF7": 1,
    "BTN_LF8": 1,
    "BTN_LF6": 1,
}

EXPECTED_TILT_BINDINGS = {
    "BTN_RF3": "BTN_LT1",
    "BTN_RF4": "BTN_LT2",
    "BTN_LT3": "BTN_LT3",
}


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

        activates = entry.get("activates")
        if activates is not None and not isinstance(activates, str):
            raise AssertionError(
                f"buttonRemapping[{index}].activates must be a string when present"
            )

        normalized.append({"physicalButton": physical, "activates": activates})
    return normalized


def _find(remaps: list[dict[str, str | None]], physical: str, logical: str) -> list[dict[str, str | None]]:
    return [
        remap
        for remap in remaps
        if remap["physicalButton"] == physical and remap["activates"] == logical
    ]


def _check_target_file(path: Path) -> tuple[list[str], str]:
    failures: list[str] = []

    try:
        payload = _load_json(path)
        mode = _ultimate_mode(payload)
        remaps = _normalized_remaps(mode)
    except (FileNotFoundError, json.JSONDecodeError, AssertionError) as exc:
        return [str(exc)], "UNAVAILABLE"

    cluster_render_parts: list[str] = []
    cluster_entries = [
        remap for remap in remaps if remap["physicalButton"] in EXPECTED_DPAD_CLUSTER
    ]

    for physical, expected_logical in EXPECTED_DPAD_CLUSTER.items():
        matches = [
            remap for remap in remaps if remap["physicalButton"] == physical
        ]
        if len(matches) != 1:
            failures.append(
                f"{_rel(path)} expected exactly one {physical} remap entry, found {len(matches)}"
            )
            cluster_render_parts.append(f"{physical}->AMBIGUOUS({len(matches)})")
            continue

        actual_logical = matches[0]["activates"]
        cluster_render_parts.append(f"{physical}->{actual_logical}")
        if actual_logical != expected_logical:
            failures.append(
                f"{_rel(path)} expected {physical} -> {expected_logical}, found {physical} -> {actual_logical}"
            )

    for logical, expected_count in EXPECTED_DPAD_LOGICAL_COUNTS.items():
        count = sum(1 for remap in remaps if remap["activates"] == logical)
        if count != expected_count:
            failures.append(
                f"{_rel(path)} expected exactly {expected_count} mapping(s) to {logical}, found {count}"
            )

    lf8_cluster_count = sum(
        1 for remap in cluster_entries if remap["activates"] == "BTN_LF8"
    )
    if lf8_cluster_count != 1:
        failures.append(
            f"{_rel(path)} expected exactly one BTN_LF8 mapping in D-pad cluster, found {lf8_cluster_count}"
        )

    for physical, logical in EXPECTED_TILT_BINDINGS.items():
        matches = _find(remaps, physical, logical)
        if len(matches) != 1:
            failures.append(
                f"{_rel(path)} expected exactly one {physical} -> {logical}, found {len(matches)}"
            )

    return failures, ", ".join(cluster_render_parts)


def main() -> int:
    failures: list[str] = []

    print("checker=ultimate_dpad_profile_mapping")
    print("mode=MODE_ULTIMATE")

    for path in TARGET_FILES:
        file_failures, cluster = _check_target_file(path)
        print(f"file={_rel(path)}")
        print(f"resolved_dpad_cluster={cluster}")
        failures.extend(file_failures)

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
