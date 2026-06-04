#!/usr/bin/env python3
"""Summarize the committed offline remapper export structural diff."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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

SCHEMA_NAME = "glyph_offline_remapper_export_structural_diff"
ANALYSIS_VERSION = 1
STATUS = "docs_tools_structural_diff"
HARDWARE_STATUS = "not_new_hardware_result"
CAVEATS = (
    "structural diff only",
    "not official configurator compatibility",
    "not adapter implementation",
    "not hardware validation",
    "not firmware behavior validation",
    "not device write behavior",
)


class OfflineRemapperExportDiffError(ValueError):
    """Raised when the committed artifacts cannot be summarized safely."""


def fail(message: str) -> None:
    raise OfflineRemapperExportDiffError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_list(payload: dict[str, Any], key: str, path: Path) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        fail(f"{display(path)} {key} must be a list")
    return value


def count_summary(
    input_payload: dict[str, Any],
    exported_payload: dict[str, Any],
    key: str,
) -> dict[str, int]:
    return {
        "input": len(require_list(input_payload, key, ACTIVE_ARTIFACT_PATH)),
        "exported": len(require_list(exported_payload, key, EXPORTED_ARTIFACT_PATH)),
    }


def mode_summary(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    game_modes = require_list(payload, "gameModeConfigs", path)
    matches: list[tuple[int, dict[str, Any]]] = []
    for index, entry in enumerate(game_modes):
        if isinstance(entry, dict) and entry.get("modeId") == "MODE_ULTIMATE":
            matches.append((index, entry))

    if len(matches) > 1:
        fail(f"{display(path)} contains multiple MODE_ULTIMATE entries")

    if not matches:
        return {"present": False, "index": None, "name": None, "communication_backend_id": None}

    index, entry = matches[0]
    return {
        "present": True,
        "index": index,
        "name": entry.get("name"),
        "communication_backend_id": entry.get("communicationBackendId"),
    }


def build_summary() -> dict[str, Any]:
    input_path = ACTIVE_ARTIFACT_PATH
    exported_path = EXPORTED_ARTIFACT_PATH
    input_bytes = input_path.read_bytes()
    exported_bytes = exported_path.read_bytes()
    input_payload = load_json_object(input_path)
    exported_payload = load_json_object(exported_path)

    input_mode = mode_summary(input_payload, input_path)
    exported_mode = mode_summary(exported_payload, exported_path)
    input_keys = set(input_payload)
    exported_keys = set(exported_payload)

    return {
        "schema_name": SCHEMA_NAME,
        "analysis_version": ANALYSIS_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "input_artifact": {
            "path": display(input_path),
            "sha256": hashlib.sha256(input_bytes).hexdigest(),
        },
        "exported_artifact": {
            "path": display(exported_path),
            "sha256": hashlib.sha256(exported_bytes).hexdigest(),
        },
        "top_level_keys": {
            "added": sorted(exported_keys - input_keys),
            "removed": sorted(input_keys - exported_keys),
            "common": sorted(input_keys & exported_keys),
        },
        "collection_counts": {
            "gameModeConfigs": count_summary(input_payload, exported_payload, "gameModeConfigs"),
            "communicationBackendConfigs": count_summary(
                input_payload, exported_payload, "communicationBackendConfigs"
            ),
            "keyboardModes": count_summary(input_payload, exported_payload, "keyboardModes"),
            "rgbConfigs": count_summary(input_payload, exported_payload, "rgbConfigs"),
        },
        "mode_ultimate": {
            "present_in_input": input_mode["present"],
            "present_in_exported": exported_mode["present"],
            "input": input_mode,
            "exported": exported_mode,
        },
        "byte_hashes_equal": input_bytes == exported_bytes,
        "objects_equal": input_payload == exported_payload,
        "caveats": list(CAVEATS),
    }


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize the docs/tools-only structural diff between the committed "
            "active Glyph profile artifact and the committed offline remapper export."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of the concise text summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = build_summary()
    except (OSError, OfflineRemapperExportDiffError, ValueError) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    if args.json:
        print(canonical_json_text(summary), end="")
        return 0

    mode = summary["mode_ultimate"]
    print(SCHEMA_NAME)
    print(f"status={summary['status']}")
    print(f"hardware_status={summary['hardware_status']}")
    print(f"input_path={summary['input_artifact']['path']}")
    print(f"input_sha256={summary['input_artifact']['sha256']}")
    print(f"exported_path={summary['exported_artifact']['path']}")
    print(f"exported_sha256={summary['exported_artifact']['sha256']}")
    print(
        "top_level_keys="
        f"added:{len(summary['top_level_keys']['added'])} "
        f"removed:{len(summary['top_level_keys']['removed'])} "
        f"common:{len(summary['top_level_keys']['common'])}"
    )
    for key, counts in summary["collection_counts"].items():
        print(f"{key}={counts['input']}->{counts['exported']}")
    print(
        "mode_ultimate="
        f"input:{mode['present_in_input']}@{mode['input']['index']}:{mode['input']['name']} "
        f"exported:{mode['present_in_exported']}@{mode['exported']['index']}:{mode['exported']['name']}"
    )
    print(f"objects_equal={str(summary['objects_equal']).lower()}")
    print(f"byte_hashes_equal={str(summary['byte_hashes_equal']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
