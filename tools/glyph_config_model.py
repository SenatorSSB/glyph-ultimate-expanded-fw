#!/usr/bin/env python3
"""Read-only model helpers for Glyph user profile JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GlyphButtonRemap:
    physical_button: str
    activates: str | None


@dataclass(frozen=True)
class GlyphSocdPair:
    button_dir_1: str
    button_dir_2: str
    socd_type: str | None


@dataclass(frozen=True)
class GlyphModeConfig:
    mode_id: str
    name: str
    layout_plate: str | None
    remaps: list[GlyphButtonRemap]
    socd_pairs: list[GlyphSocdPair]
    applicable_backends: list[str]


def load_profile_json(path: str | Path) -> dict[str, Any]:
    profile_path = Path(path)
    with profile_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"profile root must be an object: {profile_path}")
    return payload


def list_game_mode_configs(profile: dict[str, Any]) -> list[GlyphModeConfig]:
    game_modes = profile.get("gameModeConfigs")
    if game_modes is None:
        return []
    if not isinstance(game_modes, list):
        raise ValueError("gameModeConfigs must be a list when present")
    parsed: list[GlyphModeConfig] = []
    for index, mode_entry in enumerate(game_modes):
        if not isinstance(mode_entry, dict):
            raise ValueError(f"gameModeConfigs[{index}] must be an object")
        parsed.append(_parse_mode_config(mode_entry, index))
    return parsed


def find_mode_by_name(profile: dict[str, Any], mode_name: str) -> GlyphModeConfig | None:
    for mode in list_game_mode_configs(profile):
        if mode.name == mode_name:
            return mode
    return None


def find_mode_by_id(profile: dict[str, Any], mode_id: str) -> GlyphModeConfig | None:
    for mode in list_game_mode_configs(profile):
        if mode.mode_id == mode_id:
            return mode
    return None


def get_ultimate_mode(profile: dict[str, Any]) -> GlyphModeConfig:
    mode = find_mode_by_name(profile, "Ultimate")
    if mode is not None:
        return mode
    mode = find_mode_by_id(profile, "MODE_ULTIMATE")
    if mode is not None:
        return mode
    raise ValueError("could not find Ultimate mode (name=Ultimate or modeId=MODE_ULTIMATE)")


def list_button_remapping(mode: GlyphModeConfig) -> list[GlyphButtonRemap]:
    return list(mode.remaps)


def list_socd_pairs(mode: GlyphModeConfig) -> list[GlyphSocdPair]:
    return list(mode.socd_pairs)


def _parse_mode_config(mode_entry: dict[str, Any], index: int) -> GlyphModeConfig:
    mode_id = mode_entry.get("modeId")
    if mode_id is None:
        mode_id = ""
    if not isinstance(mode_id, str):
        raise ValueError(f"gameModeConfigs[{index}].modeId must be a string when present")

    name = mode_entry.get("name")
    if name is None:
        name = ""
    if not isinstance(name, str):
        raise ValueError(f"gameModeConfigs[{index}].name must be a string when present")

    layout_plate = mode_entry.get("layoutPlate")
    if layout_plate is not None and not isinstance(layout_plate, str):
        raise ValueError(f"gameModeConfigs[{index}].layoutPlate must be a string when present")

    remaps = _parse_button_remapping(mode_entry, index)
    socd_pairs = _parse_socd_pairs(mode_entry, index)
    applicable_backends = _parse_applicable_backends(mode_entry, index)

    return GlyphModeConfig(
        mode_id=mode_id,
        name=name,
        layout_plate=layout_plate,
        remaps=remaps,
        socd_pairs=socd_pairs,
        applicable_backends=applicable_backends,
    )


def _parse_button_remapping(mode_entry: dict[str, Any], mode_index: int) -> list[GlyphButtonRemap]:
    raw_remaps = mode_entry.get("buttonRemapping")
    if raw_remaps is None:
        return []
    if not isinstance(raw_remaps, list):
        raise ValueError(f"gameModeConfigs[{mode_index}].buttonRemapping must be a list when present")

    remaps: list[GlyphButtonRemap] = []
    for remap_index, remap_entry in enumerate(raw_remaps):
        if not isinstance(remap_entry, dict):
            raise ValueError(
                f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}] must be an object",
            )
        physical_button = remap_entry.get("physicalButton")
        if not isinstance(physical_button, str) or not physical_button:
            raise ValueError(
                f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}] "
                "missing physicalButton",
            )
        activates = remap_entry.get("activates")
        if activates is not None and not isinstance(activates, str):
            raise ValueError(
                f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}].activates "
                "must be a string when present",
            )
        remaps.append(GlyphButtonRemap(physical_button=physical_button, activates=activates))
    return remaps


def _parse_socd_pairs(mode_entry: dict[str, Any], mode_index: int) -> list[GlyphSocdPair]:
    raw_pairs = mode_entry.get("socdPairs")
    if raw_pairs is None:
        return []
    if not isinstance(raw_pairs, list):
        raise ValueError(f"gameModeConfigs[{mode_index}].socdPairs must be a list when present")

    pairs: list[GlyphSocdPair] = []
    for pair_index, pair_entry in enumerate(raw_pairs):
        if not isinstance(pair_entry, dict):
            raise ValueError(
                f"gameModeConfigs[{mode_index}].socdPairs[{pair_index}] must be an object",
            )
        button_dir_1 = pair_entry.get("buttonDir1")
        button_dir_2 = pair_entry.get("buttonDir2")
        if not isinstance(button_dir_1, str) or not isinstance(button_dir_2, str):
            raise ValueError(
                f"gameModeConfigs[{mode_index}].socdPairs[{pair_index}] "
                "missing buttonDir1/buttonDir2",
            )
        socd_type = pair_entry.get("socdType")
        if socd_type is not None and not isinstance(socd_type, str):
            raise ValueError(
                f"gameModeConfigs[{mode_index}].socdPairs[{pair_index}].socdType "
                "must be a string when present",
            )
        pairs.append(
            GlyphSocdPair(
                button_dir_1=button_dir_1,
                button_dir_2=button_dir_2,
                socd_type=socd_type,
            ),
        )
    return pairs


def _parse_applicable_backends(mode_entry: dict[str, Any], mode_index: int) -> list[str]:
    raw_backends = mode_entry.get("applicableBackends")
    if raw_backends is None:
        return []
    if not isinstance(raw_backends, list):
        raise ValueError(
            f"gameModeConfigs[{mode_index}].applicableBackends must be a list when present",
        )

    backends: list[str] = []
    for backend_index, backend in enumerate(raw_backends):
        if not isinstance(backend, str):
            raise ValueError(
                f"gameModeConfigs[{mode_index}].applicableBackends[{backend_index}] must be string",
            )
        backends.append(backend)
    return backends
