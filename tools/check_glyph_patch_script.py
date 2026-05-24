#!/usr/bin/env python3
"""Validate the Ultimate JSON patch prototype against calibration fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from glyph_config_model import get_ultimate_mode, list_button_remapping, load_profile_json
from patch_glyph_ultimate_profile import apply_patch_to_profile, load_json, save_json


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "docs" / "calibration" / "fixtures"
INPUT_PROFILE_PATH = FIXTURE_DIR / "GlyphUltFilled2.json"
PATCH_PATH = FIXTURE_DIR / "example_ultimate_patch.json"


def _mode_is_ultimate(mode: dict[str, Any]) -> bool:
    return mode.get("name") == "Ultimate" or mode.get("modeId") == "MODE_ULTIMATE"


def _extract_modes(profile: dict[str, Any]) -> list[dict[str, Any]]:
    game_modes = profile.get("gameModeConfigs")
    if not isinstance(game_modes, list):
        raise AssertionError("gameModeConfigs must be a list")
    for index, entry in enumerate(game_modes):
        if not isinstance(entry, dict):
            raise AssertionError(f"gameModeConfigs[{index}] must be an object")
    return game_modes


def _assert_only_ultimate_changed(before: dict[str, Any], after: dict[str, Any]) -> None:
    before_modes = _extract_modes(before)
    after_modes = _extract_modes(after)

    if len(before_modes) != len(after_modes):
        raise AssertionError("mode count changed unexpectedly")

    for index, (before_mode, after_mode) in enumerate(zip(before_modes, after_modes)):
        if _mode_is_ultimate(before_mode):
            continue
        if before_mode != after_mode:
            raise AssertionError(f"non-Ultimate mode changed at index {index}")


def _assert_requested_remaps_changed(
    patched_profile: dict[str, Any],
    patch_spec: dict[str, Any],
) -> None:
    patch_remaps = patch_spec.get("ultimateRemaps", [])
    if not isinstance(patch_remaps, list):
        raise AssertionError("ultimateRemaps must be a list")

    ultimate = get_ultimate_mode(patched_profile)
    remap_lookup = {
        remap.physical_button: remap.activates
        for remap in list_button_remapping(ultimate)
    }

    for entry in patch_remaps:
        if not isinstance(entry, dict):
            raise AssertionError("patch remap entry must be an object")
        physical_button = entry.get("physicalButton")
        activates = entry.get("activates")
        if remap_lookup.get(physical_button) != activates:
            raise AssertionError(
                f"patched remap mismatch for {physical_button}: "
                f"expected {activates!r}, got {remap_lookup.get(physical_button)!r}",
            )


def _assert_omitted_btn_mb1_still_omitted(profile: dict[str, Any]) -> None:
    ultimate = get_ultimate_mode(profile)
    for remap in list_button_remapping(ultimate):
        if remap.physical_button == "BTN_MB1":
            if remap.activates is not None:
                raise AssertionError(f"BTN_MB1 activates should remain omitted, got {remap.activates!r}")
            return
    raise AssertionError("BTN_MB1 remap entry missing")


def main() -> None:
    input_profile = load_profile_json(INPUT_PROFILE_PATH)
    patch_spec = load_json(PATCH_PATH)
    patched_profile, summary = apply_patch_to_profile(input_profile, patch_spec)

    with tempfile.TemporaryDirectory(prefix="glyph_patch_check_") as temp_dir:
        output_path = Path(temp_dir) / "patched_profile.json"
        save_json(output_path, patched_profile)
        reloaded_profile = load_profile_json(output_path)

    _assert_only_ultimate_changed(input_profile, reloaded_profile)
    _assert_requested_remaps_changed(reloaded_profile, patch_spec)
    _assert_omitted_btn_mb1_still_omitted(reloaded_profile)

    # Ensure parser sanity still holds after patch output round-trip.
    ultimate = get_ultimate_mode(reloaded_profile)
    if ultimate.layout_plate != "LAYOUT_PLATE_EVERYTHING":
        raise AssertionError("patched Ultimate layoutPlate changed unexpectedly")

    print("Patch script checks passed:")
    for line in summary:
        print(f"- {line}")


if __name__ == "__main__":
    main()
