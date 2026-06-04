#!/usr/bin/env python3
"""Validate the committed offline remapper metadata diff report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_ARTIFACT_PATH = (
    REPO_ROOT
    / "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
)
EXPORTED_ARTIFACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_metadata_diff_report_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_metadata_diff_report_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_metadata_diff_report"
REPORT_VERSION = 1
STATUS = "docs_tools_metadata_diff"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_DOC_PHRASES = (
    "metadata diff only",
    "not gameplay/runtime validation",
    "not firmware behavior correctness",
    "not official configurator compatibility",
    "not hardware validation",
    "comparison summary",
)

GAME_MODE_FIELD_NAMES = (
    "modeId",
    "name",
    "socdPairs",
    "buttonRemapping",
    "rgbConfig",
    "layoutPlate",
    "applicableBackends",
    "menuButtonIcon",
    "keyboardModeConfig",
)


class OfflineRemapperMetadataDiffReportError(ValueError):
    """Raised when the committed metadata diff report drifts from expectations."""


def fail(message: str) -> None:
    raise OfflineRemapperMetadataDiffReportError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return sha256_bytes(encoded)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def require_list(payload: dict[str, Any], key: str, path: Path) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        fail(f"{display(path)} {key} must be a list")
    return value


def mode_signature(mode: dict[str, Any]) -> dict[str, Any]:
    return {
        "modeId": mode.get("modeId"),
        "name": mode.get("name"),
        "rgbConfig": mode.get("rgbConfig"),
        "layoutPlate": mode.get("layoutPlate"),
        "applicableBackends": mode.get("applicableBackends"),
        "menuButtonIcon": mode.get("menuButtonIcon"),
        "keyboardModeConfig": mode.get("keyboardModeConfig"),
    }


def collect_rgb_config_summary(
    payload: dict[str, Any], path: Path
) -> dict[str, Any]:
    rgb_configs = require_list(payload, "rgbConfigs", path)
    button_color_entries: list[dict[str, Any]] = []
    empty_object_entries = [
        index for index, entry in enumerate(rgb_configs) if entry == {}
    ]

    for rgb_index, config in enumerate(rgb_configs):
        if not isinstance(config, dict):
            fail(f"{display(path)} rgbConfigs[{rgb_index}] must be an object")
        button_colors = config.get("buttonColors")
        if not isinstance(button_colors, list):
            fail(
                f"{display(path)} rgbConfigs[{rgb_index}].buttonColors must be a list"
            )
        for button_index, entry in enumerate(button_colors):
            if isinstance(entry, dict) and "color" not in entry:
                button_color_entries.append(
                    {
                        "rgbConfig_index": rgb_index,
                        "buttonColors_index": button_index,
                        "entry": entry,
                    }
                )

    return {
        "input_count": len(rgb_configs),
        "sha256": sha256_json(rgb_configs),
        "exact_value_equality": True,
        "empty_object_entry_count": len(empty_object_entries),
        "empty_object_entries": empty_object_entries,
        "buttonColors_missing_color_entry_count": len(button_color_entries),
        "buttonColors_missing_color_entries": button_color_entries,
    }


def collect_game_mode_changes(
    input_modes: list[Any], exported_modes: list[Any]
) -> dict[str, Any]:
    if len(input_modes) != len(exported_modes):
        fail("gameModeConfigs counts must match before comparison")

    changed_entries: list[dict[str, Any]] = []
    preserved_field_names = {
        field_name
        for field_name in GAME_MODE_FIELD_NAMES
        if all(
            isinstance(input_mode, dict)
            and isinstance(exported_mode, dict)
            and input_mode.get(field_name) == exported_mode.get(field_name)
            for input_mode, exported_mode in zip(input_modes, exported_modes)
        )
    }

    for index, (input_mode, exported_mode) in enumerate(zip(input_modes, exported_modes)):
        if not isinstance(input_mode, dict):
            fail(f"input gameModeConfigs[{index}] must be an object")
        if not isinstance(exported_mode, dict):
            fail(f"exported gameModeConfigs[{index}] must be an object")

        changed_fields = [
            field_name
            for field_name in GAME_MODE_FIELD_NAMES
            if input_mode.get(field_name) != exported_mode.get(field_name)
        ]
        if changed_fields:
            changed_entries.append(
                {
                    "index": index,
                    "modeId": input_mode.get("modeId"),
                    "name": input_mode.get("name"),
                    "changed_fields": changed_fields,
                    "input_sha256": sha256_json(input_mode),
                    "exported_sha256": sha256_json(exported_mode),
                    "input_field_sha256": {
                        field_name: sha256_json(input_mode.get(field_name))
                        for field_name in changed_fields
                    },
                    "exported_field_sha256": {
                        field_name: sha256_json(exported_mode.get(field_name))
                        for field_name in changed_fields
                    },
                }
            )

    preserved_field_names.discard("keyboardModeConfig")

    return {
        "preserved_exact_field_names": sorted(preserved_field_names),
        "changed_by_external_app": changed_entries,
    }


def build_report() -> dict[str, Any]:
    input_payload = load_json_object(ACTIVE_ARTIFACT_PATH)
    exported_payload = load_json_object(EXPORTED_ARTIFACT_PATH)

    input_rgb_configs = require_list(input_payload, "rgbConfigs", ACTIVE_ARTIFACT_PATH)
    exported_rgb_configs = require_list(
        exported_payload, "rgbConfigs", EXPORTED_ARTIFACT_PATH
    )
    if len(input_rgb_configs) != len(exported_rgb_configs):
        fail("rgbConfigs counts must match before comparison")

    input_game_modes = require_list(
        input_payload, "gameModeConfigs", ACTIVE_ARTIFACT_PATH
    )
    exported_game_modes = require_list(
        exported_payload, "gameModeConfigs", EXPORTED_ARTIFACT_PATH
    )

    input_keyboard_modes = require_list(
        input_payload, "keyboardModes", ACTIVE_ARTIFACT_PATH
    )
    exported_keyboard_modes = require_list(
        exported_payload, "keyboardModes", EXPORTED_ARTIFACT_PATH
    )

    rgb_configs_summary = {
        "input_count": len(input_rgb_configs),
        "exported_count": len(exported_rgb_configs),
        "input_sha256": sha256_json(input_rgb_configs),
        "exported_sha256": sha256_json(exported_rgb_configs),
        "exact_value_equality": input_rgb_configs == exported_rgb_configs,
        "empty_object_entries": {
            "input": [
                index
                for index, entry in enumerate(input_rgb_configs)
                if entry == {}
            ],
            "exported": [
                index
                for index, entry in enumerate(exported_rgb_configs)
                if entry == {}
            ],
        },
        "buttonColors_missing_color_entries": {
            "input": collect_rgb_config_summary(
                input_payload, ACTIVE_ARTIFACT_PATH
            )["buttonColors_missing_color_entries"],
            "exported": collect_rgb_config_summary(
                exported_payload, EXPORTED_ARTIFACT_PATH
            )["buttonColors_missing_color_entries"],
        },
    }

    menu_button_icon_differences = []
    for index, (input_mode, exported_mode) in enumerate(
        zip(input_game_modes, exported_game_modes)
    ):
        if not isinstance(input_mode, dict):
            fail(f"input gameModeConfigs[{index}] must be an object")
        if not isinstance(exported_mode, dict):
            fail(f"exported gameModeConfigs[{index}] must be an object")
        if input_mode.get("menuButtonIcon") != exported_mode.get("menuButtonIcon"):
            menu_button_icon_differences.append(
                {
                    "index": index,
                    "modeId": input_mode.get("modeId"),
                    "name": input_mode.get("name"),
                    "input": input_mode.get("menuButtonIcon"),
                    "exported": exported_mode.get("menuButtonIcon"),
                }
            )

    game_mode_changes = collect_game_mode_changes(input_game_modes, exported_game_modes)

    return {
        "schema_name": SCHEMA_NAME,
        "report_version": REPORT_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "metadata_only": True,
        "firmware_behavior_validated": False,
        "hardware_validation_claimed": False,
        "input_artifact": {
            "path": display(ACTIVE_ARTIFACT_PATH),
            "sha256": sha256_bytes(ACTIVE_ARTIFACT_PATH.read_bytes()),
        },
        "exported_artifact": {
            "path": display(EXPORTED_ARTIFACT_PATH),
            "sha256": sha256_bytes(EXPORTED_ARTIFACT_PATH.read_bytes()),
        },
        "comparison_summary": {
            "summary": (
                "Metadata diff only: the top-level metadata and the RGB/menu/back-end "
                "settings stay equal, while a small set of game-mode metadata fields "
                "change in the exported artifact."
            ),
            "rgbConfigs": {
                "input_count": rgb_configs_summary["input_count"],
                "exported_count": rgb_configs_summary["exported_count"],
                "input_sha256": rgb_configs_summary["input_sha256"],
                "exported_sha256": rgb_configs_summary["exported_sha256"],
                "exact_value_equality": rgb_configs_summary["exact_value_equality"],
            },
            "rgbConfigs_empty_object_entries": {
                "input": rgb_configs_summary["empty_object_entries"]["input"],
                "exported": rgb_configs_summary["empty_object_entries"]["exported"],
                "exact_value_equality": (
                    rgb_configs_summary["empty_object_entries"]["input"]
                    == rgb_configs_summary["empty_object_entries"]["exported"]
                ),
            },
            "buttonColors_missing_color_entries": {
                "input_count": len(
                    rgb_configs_summary["buttonColors_missing_color_entries"]["input"]
                ),
                "exported_count": len(
                    rgb_configs_summary["buttonColors_missing_color_entries"][
                        "exported"
                    ]
                ),
                "exact_value_equality": (
                    rgb_configs_summary["buttonColors_missing_color_entries"][
                        "input"
                    ]
                    == rgb_configs_summary["buttonColors_missing_color_entries"][
                        "exported"
                    ]
                ),
                "input": rgb_configs_summary["buttonColors_missing_color_entries"][
                    "input"
                ],
                "exported": rgb_configs_summary["buttonColors_missing_color_entries"][
                    "exported"
                ],
            },
            "menuButtonIcon_differences_by_game_mode": {
                "modes_compared": len(input_game_modes),
                "difference_count": len(menu_button_icon_differences),
                "exact_value_equality": len(menu_button_icon_differences) == 0,
                "differences": menu_button_icon_differences,
            },
            "communicationBackendConfigs_differences": {
                "input_count": len(
                    require_list(
                        input_payload,
                        "communicationBackendConfigs",
                        ACTIVE_ARTIFACT_PATH,
                    )
                ),
                "exported_count": len(
                    require_list(
                        exported_payload,
                        "communicationBackendConfigs",
                        EXPORTED_ARTIFACT_PATH,
                    )
                ),
                "exact_value_equality": (
                    input_payload.get("communicationBackendConfigs")
                    == exported_payload.get("communicationBackendConfigs")
                ),
                "differences": [],
            },
            "defaultBackendConfig_defaultUsbBackendConfig": {
                "defaultBackendConfig": {
                    "input": input_payload.get("defaultBackendConfig"),
                    "exported": exported_payload.get("defaultBackendConfig"),
                    "exact_value_equality": (
                        input_payload.get("defaultBackendConfig")
                        == exported_payload.get("defaultBackendConfig")
                    ),
                },
                "defaultUsbBackendConfig": {
                    "input": input_payload.get("defaultUsbBackendConfig"),
                    "exported": exported_payload.get("defaultUsbBackendConfig"),
                    "exact_value_equality": (
                        input_payload.get("defaultUsbBackendConfig")
                        == exported_payload.get("defaultUsbBackendConfig")
                    ),
                },
            },
            "rgbBrightness": {
                "input": input_payload.get("rgbBrightness"),
                "exported": exported_payload.get("rgbBrightness"),
                "exact_value_equality": (
                    input_payload.get("rgbBrightness")
                    == exported_payload.get("rgbBrightness")
                ),
            },
            "defaultDashboardOption": {
                "input": input_payload.get("defaultDashboardOption"),
                "exported": exported_payload.get("defaultDashboardOption"),
                "exact_value_equality": (
                    input_payload.get("defaultDashboardOption")
                    == exported_payload.get("defaultDashboardOption")
                ),
            },
            "keyboardModes": {
                "input_count": len(input_keyboard_modes),
                "exported_count": len(exported_keyboard_modes),
                "input_sha256": sha256_json(input_keyboard_modes),
                "exported_sha256": sha256_json(exported_keyboard_modes),
                "exact_value_equality": input_keyboard_modes == exported_keyboard_modes,
            },
            "fields_preserved_exactly": {
                "top_level": [
                    "communicationBackendConfigs",
                    "defaultBackendConfig",
                    "defaultDashboardOption",
                    "defaultUsbBackendConfig",
                    "keyboardModes",
                    "rgbBrightness",
                    "rgbConfigs",
                ],
                "game_mode_fields": game_mode_changes["preserved_exact_field_names"],
            },
            "fields_changed_by_external_app": game_mode_changes["changed_by_external_app"],
        },
    }


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required caveat phrase: {phrase}")


def validate_fixture(report: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(report)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated report JSON")

    committed = load_json_object(FIXTURE_PATH)
    if committed != report:
        fail("committed fixture JSON object drifted from regenerated report")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the docs/tools-only metadata diff between the committed active "
            "Glyph profile artifact and the committed offline remapper export."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of validating the committed fixture.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_report()
        if args.json:
            print(canonical_json_text(report), end="")
            return 0

        validate_fixture(report)
        validate_doc()
    except (OSError, OfflineRemapperMetadataDiffReportError, ValueError) as exc:
        print("glyph_offline_remapper_metadata_diff_report")
        print("status=FAIL")
        print("metadata_only=true")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    summary = report["comparison_summary"]
    print("glyph_offline_remapper_metadata_diff_report")
    print("status=PASS")
    print("metadata_only=true")
    print(f"hardware_status={HARDWARE_STATUS}")
    print(
        "comparison_summary="
        f"{summary['summary']} "
        f"changed_fields={len(summary['fields_changed_by_external_app'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
