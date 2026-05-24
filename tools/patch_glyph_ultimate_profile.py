#!/usr/bin/env python3
"""Apply an illustrative, read-only-safe patch to Ultimate mode profile JSON."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def save_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def find_ultimate_mode_entry(profile: dict[str, Any]) -> dict[str, Any]:
    game_modes = profile.get("gameModeConfigs")
    if not isinstance(game_modes, list):
        raise ValueError("gameModeConfigs must be a list")
    for mode in game_modes:
        if not isinstance(mode, dict):
            continue
        if mode.get("name") == "Ultimate" or mode.get("modeId") == "MODE_ULTIMATE":
            return mode
    raise ValueError("could not find Ultimate mode (name=Ultimate or modeId=MODE_ULTIMATE)")


def apply_patch_to_profile(
    profile: dict[str, Any],
    patch_spec: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    patched = copy.deepcopy(profile)
    summary: list[str] = []

    ultimate_mode = find_ultimate_mode_entry(patched)

    remap_updates = patch_spec.get("ultimateRemaps", [])
    remap_summary = apply_ultimate_remap_updates(ultimate_mode, remap_updates)
    summary.extend(remap_summary)

    socd_ops = patch_spec.get("ultimateSocdPairs")
    socd_summary = apply_ultimate_socd_updates(ultimate_mode, socd_ops)
    summary.extend(socd_summary)

    return patched, summary


def apply_ultimate_remap_updates(mode_entry: dict[str, Any], remap_updates: Any) -> list[str]:
    if remap_updates is None:
        return []
    if not isinstance(remap_updates, list):
        raise ValueError("ultimateRemaps must be a list when present")

    remap_entries = mode_entry.get("buttonRemapping")
    if remap_entries is None:
        remap_entries = []
        mode_entry["buttonRemapping"] = remap_entries
    if not isinstance(remap_entries, list):
        raise ValueError("Ultimate buttonRemapping must be a list")

    updated = 0
    added = 0

    for index, update in enumerate(remap_updates):
        if not isinstance(update, dict):
            raise ValueError(f"ultimateRemaps[{index}] must be an object")
        physical_button = update.get("physicalButton")
        activates = update.get("activates")
        if not isinstance(physical_button, str) or not physical_button:
            raise ValueError(f"ultimateRemaps[{index}] missing physicalButton")
        if not isinstance(activates, str) or not activates:
            raise ValueError(f"ultimateRemaps[{index}] missing activates")

        matched = False
        for remap_entry in remap_entries:
            if not isinstance(remap_entry, dict):
                continue
            if remap_entry.get("physicalButton") == physical_button:
                remap_entry["activates"] = activates
                matched = True
        if matched:
            updated += 1
            continue

        remap_entries.append(
            {
                "physicalButton": physical_button,
                "activates": activates,
            },
        )
        added += 1

    return [
        f"ultimateRemaps updated={updated}",
        f"ultimateRemaps added={added}",
    ]


def apply_ultimate_socd_updates(mode_entry: dict[str, Any], socd_ops: Any) -> list[str]:
    if socd_ops is None:
        return ["ultimateSocdPairs unchanged"]
    if not isinstance(socd_ops, dict):
        raise ValueError("ultimateSocdPairs must be an object when present")

    socd_pairs = mode_entry.get("socdPairs")
    if socd_pairs is None:
        socd_pairs = []
        mode_entry["socdPairs"] = socd_pairs
    if not isinstance(socd_pairs, list):
        raise ValueError("Ultimate socdPairs must be a list")

    replace_pairs = socd_ops.get("replace")
    add_pairs = socd_ops.get("add")
    remove_pairs = socd_ops.get("remove")

    if replace_pairs is not None:
        if not isinstance(replace_pairs, list):
            raise ValueError("ultimateSocdPairs.replace must be a list when present")
        socd_pairs[:] = [_normalize_socd_pair(entry, context="ultimateSocdPairs.replace") for entry in replace_pairs]
        return [f"ultimateSocdPairs replaced={len(socd_pairs)}"]

    removed = 0
    if remove_pairs is not None:
        if not isinstance(remove_pairs, list):
            raise ValueError("ultimateSocdPairs.remove must be a list when present")
        normalized_remove = [
            _normalize_socd_pair(entry, context="ultimateSocdPairs.remove")
            for entry in remove_pairs
        ]
        kept: list[dict[str, Any]] = []
        for existing in socd_pairs:
            if not isinstance(existing, dict):
                continue
            if _matches_any_socd_pair(existing, normalized_remove):
                removed += 1
                continue
            kept.append(existing)
        socd_pairs[:] = kept

    added = 0
    if add_pairs is not None:
        if not isinstance(add_pairs, list):
            raise ValueError("ultimateSocdPairs.add must be a list when present")
        for entry in add_pairs:
            normalized = _normalize_socd_pair(entry, context="ultimateSocdPairs.add")
            if _matches_any_socd_pair(normalized, socd_pairs):
                continue
            socd_pairs.append(normalized)
            added += 1

    return [
        f"ultimateSocdPairs removed={removed}",
        f"ultimateSocdPairs added={added}",
    ]


def _normalize_socd_pair(entry: Any, context: str) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError(f"{context} entry must be an object")
    button_dir_1 = entry.get("buttonDir1")
    button_dir_2 = entry.get("buttonDir2")
    if not isinstance(button_dir_1, str) or not isinstance(button_dir_2, str):
        raise ValueError(f"{context} entry missing buttonDir1/buttonDir2")
    normalized: dict[str, Any] = {
        "buttonDir1": button_dir_1,
        "buttonDir2": button_dir_2,
    }
    socd_type = entry.get("socdType")
    if socd_type is not None:
        if not isinstance(socd_type, str):
            raise ValueError(f"{context} entry socdType must be a string when present")
        normalized["socdType"] = socd_type
    return normalized


def _matches_any_socd_pair(pair: dict[str, Any], candidates: list[dict[str, Any]]) -> bool:
    for candidate in candidates:
        if _socd_pair_matches(pair, candidate):
            return True
    return False


def _socd_pair_matches(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_pair = {left.get("buttonDir1"), left.get("buttonDir2")}
    right_pair = {right.get("buttonDir1"), right.get("buttonDir2")}
    if left_pair != right_pair:
        return False

    right_socd_type = right.get("socdType")
    if right_socd_type is None:
        return True
    return left.get("socdType") == right_socd_type


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply a limited Ultimate mode JSON patch to a Glyph user profile. "
            "Writes only when --output is provided."
        ),
    )
    parser.add_argument("--input", required=True, type=Path, help="Input profile JSON path")
    parser.add_argument("--patch", required=True, type=Path, help="Patch JSON path")
    parser.add_argument("--output", type=Path, help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    profile = load_json(args.input)
    patch_spec = load_json(args.patch)
    patched, summary = apply_patch_to_profile(profile, patch_spec)

    if args.output is not None:
        save_json(args.output, patched)
        print(f"wrote output: {args.output}")
    else:
        print("no output path provided; no file written")

    print("changes:")
    for line in summary:
        print(f"- {line}")


if __name__ == "__main__":
    main()
