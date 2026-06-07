#!/usr/bin/env python3
"""Shared helpers for the official Glyph configurator export corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ID = "official_glyph_configurator_2026-06-06"
CORPUS_DIR = REPO_ROOT / "docs/calibration/export_corpus" / CORPUS_ID
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
NOTES_PATH = CORPUS_DIR / "notes.md"
DEFAULT_FIXTURE_REL = (
    "fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json"
)
BACK_AND_FORTH_FIXTURE_REL = (
    "fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json"
)
DEFAULT_FIXTURE_PATH = CORPUS_DIR / DEFAULT_FIXTURE_REL
BACK_AND_FORTH_FIXTURE_PATH = CORPUS_DIR / BACK_AND_FORTH_FIXTURE_REL
DIFF_DOC_PATH = REPO_ROOT / "docs/calibration/glyph_official_configurator_corpus_diff_2026-06-06.md"
DIFF_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_official_configurator_corpus_diff_2026-06-06.json"
)

REQUIRED_TOP_LEVEL_KEYS = [
    "gameModeConfigs",
    "communicationBackendConfigs",
    "keyboardModes",
    "rgbConfigs",
    "defaultBackendConfig",
    "defaultUsbBackendConfig",
    "rgbBrightness",
    "defaultDashboardOption",
]

FORBIDDEN_NON_CLAIMS = {
    "not_external_remapper",
    "not_webserial_device_write_implementation",
    "not_runtime_loaded_config_implementation",
    "not_protobuf_binary_write",
    "not_firmware_behavior_change",
    "not_active_profile_artifact_change",
    "not_nunchuk_validation",
    "not_universal_official_compatibility_claim",
}


class CorpusError(AssertionError):
    """Raised when the official configurator corpus drifts."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise CorpusError(f"missing JSON object: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CorpusError(f"invalid JSON in {display(path)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CorpusError(f"{display(path)} must contain a JSON object")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_paths() -> dict[str, Path]:
    return {
        "default_profiles": DEFAULT_FIXTURE_PATH,
        "back_and_forth_custom_profile": BACK_AND_FORTH_FIXTURE_PATH,
    }


def load_fixtures() -> dict[str, dict[str, Any]]:
    return {role: load_json_object(path) for role, path in fixture_paths().items()}


def mode_key(mode: dict[str, Any]) -> str:
    return f"{mode.get('name', 'UNKNOWN_NAME')}::{mode.get('modeId', 'UNKNOWN_MODE_ID')}"


def modes_by_key(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        raise CorpusError("gameModeConfigs must be a list")
    result: dict[str, dict[str, Any]] = {}
    for mode in modes:
        if not isinstance(mode, dict):
            raise CorpusError("gameModeConfigs entries must be JSON objects")
        result[mode_key(mode)] = mode
    return result


def button_entries(mode: dict[str, Any], physical_button: str) -> list[dict[str, Any]]:
    remapping = mode.get("buttonRemapping", [])
    if not isinstance(remapping, list):
        return []
    return [
        entry
        for entry in remapping
        if isinstance(entry, dict) and entry.get("physicalButton") == physical_button
    ]


def socd_pair_exists(mode: dict[str, Any], button_dir_1: str, button_dir_2: str) -> bool:
    pairs = mode.get("socdPairs", [])
    if not isinstance(pairs, list):
        return False
    for pair in pairs:
        if not isinstance(pair, dict):
            continue
        if pair.get("buttonDir1") == button_dir_1 and pair.get("buttonDir2") == button_dir_2:
            return True
    return False


def compute_structural_diff() -> dict[str, Any]:
    fixtures = load_fixtures()
    default = fixtures["default_profiles"]
    back = fixtures["back_and_forth_custom_profile"]
    default_modes = modes_by_key(default)
    back_modes = modes_by_key(back)
    common_mode_keys = sorted(set(default_modes) & set(back_modes))
    changed_modes = [
        {
            "name": default_modes[key].get("name"),
            "modeId": default_modes[key].get("modeId"),
            "key": key,
            "changed_fields": sorted(
                set(default_modes[key]).union(back_modes[key])
                - {
                    field
                    for field in set(default_modes[key]).union(back_modes[key])
                    if default_modes[key].get(field) == back_modes[key].get(field)
                }
            ),
            "socdPairs_count_default": len(default_modes[key].get("socdPairs", [])),
            "socdPairs_count_back_and_forth": len(back_modes[key].get("socdPairs", [])),
            "buttonRemapping_count_default": len(default_modes[key].get("buttonRemapping", [])),
            "buttonRemapping_count_back_and_forth": len(back_modes[key].get("buttonRemapping", [])),
        }
        for key in common_mode_keys
        if default_modes[key] != back_modes[key]
    ]

    ultimate_key = next(key for key in common_mode_keys if key.endswith("::MODE_ULTIMATE"))
    brawl_key = next(key for key in common_mode_keys if key.startswith("Brawl::"))
    keyboard_key = next(key for key in common_mode_keys if key.endswith("::MODE_KEYBOARD"))
    default_ultimate = default_modes[ultimate_key]
    back_ultimate = back_modes[ultimate_key]
    default_brawl = default_modes[brawl_key]
    back_brawl = back_modes[brawl_key]
    default_keyboard = default_modes[keyboard_key]
    back_keyboard = back_modes[keyboard_key]

    changed_top_level_keys = [
        key for key in REQUIRED_TOP_LEVEL_KEYS if default.get(key) != back.get(key)
    ]

    return {
        "schema_name": "glyph_official_configurator_corpus_diff",
        "schema_version": 1,
        "packet_date": "2026-06-06",
        "corpus_id": CORPUS_ID,
        "source_classification": "primary_official_configurator_corpus",
        "evidence_type": "structural_json_evidence",
        "fixture_hashes": {
            role: sha256_file(path) for role, path in fixture_paths().items()
        },
        "fixture_files": {
            role: display(path) for role, path in fixture_paths().items()
        },
        "top_level_keys_default": list(default.keys()),
        "top_level_keys_back_and_forth": list(back.keys()),
        "stable_top_level_key_set": set(default.keys()) == set(back.keys()),
        "changed_top_level_keys": changed_top_level_keys,
        "game_mode_names_default": [mode.get("name") for mode in default.get("gameModeConfigs", [])],
        "game_mode_names_back_and_forth": [
            mode.get("name") for mode in back.get("gameModeConfigs", [])
        ],
        "game_mode_ids_default": [mode.get("modeId") for mode in default.get("gameModeConfigs", [])],
        "game_mode_ids_back_and_forth": [
            mode.get("modeId") for mode in back.get("gameModeConfigs", [])
        ],
        "changed_game_mode_entries": changed_modes,
        "ultimate": {
            "socdPairs_count_default": len(default_ultimate.get("socdPairs", [])),
            "socdPairs_count_back_and_forth": len(back_ultimate.get("socdPairs", [])),
            "buttonRemapping_count_default": len(default_ultimate.get("buttonRemapping", [])),
            "buttonRemapping_count_back_and_forth": len(
                back_ultimate.get("buttonRemapping", [])
            ),
            "BTN_LF6_entries_changed_structurally": button_entries(
                default_ultimate, "BTN_LF6"
            )
            != button_entries(back_ultimate, "BTN_LF6"),
            "BTN_LF8_entries_changed_structurally": button_entries(
                default_ultimate, "BTN_LF8"
            )
            != button_entries(back_ultimate, "BTN_LF8"),
            "BTN_LF8_BTN_LF6_socd_pair_added_structurally": (
                not socd_pair_exists(default_ultimate, "BTN_LF8", "BTN_LF6")
                and socd_pair_exists(back_ultimate, "BTN_LF8", "BTN_LF6")
            ),
            "BTN_RF7_BTN_RF8_socd_pair_added_structurally": (
                not socd_pair_exists(default_ultimate, "BTN_RF7", "BTN_RF8")
                and socd_pair_exists(back_ultimate, "BTN_RF7", "BTN_RF8")
            ),
        },
        "brawl": {
            "extra_BTN_RF7_BTN_RF8_pair_exists_in_back_and_forth": (
                not socd_pair_exists(default_brawl, "BTN_RF7", "BTN_RF8")
                and socd_pair_exists(back_brawl, "BTN_RF7", "BTN_RF8")
            )
        },
        "keyboard": {
            "socd_pair_ordering_changed_structurally": default_keyboard.get("socdPairs")
            != back_keyboard.get("socdPairs"),
        },
        "rgb": {
            "rgb_config_count_default": len(default.get("rgbConfigs", [])),
            "rgb_config_count_back_and_forth": len(back.get("rgbConfigs", [])),
            "changed_rgb_config_indexes": [
                index
                for index, (left, right) in enumerate(
                    zip(default.get("rgbConfigs", []), back.get("rgbConfigs", []))
                )
                if left != right
            ],
            "button_color_counts_default": [
                len(config.get("buttonColors", []))
                for config in default.get("rgbConfigs", [])
                if isinstance(config, dict)
            ],
            "button_color_counts_back_and_forth": [
                len(config.get("buttonColors", []))
                for config in back.get("rgbConfigs", [])
                if isinstance(config, dict)
            ],
            "partial_button_color_entries_detected_structurally": any(
                isinstance(config, dict)
                and isinstance(config.get("buttonColors"), list)
                and 0 < len(config.get("buttonColors", [])) < 33
                for config in back.get("rgbConfigs", [])
            ),
        },
        "explicit_non_claims": {
            "not_gameplay_semantics": True,
            "not_runtime_behavior_claim": True,
            "not_device_write_approval": True,
            "not_adapter_implementation_approval": True,
        },
    }

