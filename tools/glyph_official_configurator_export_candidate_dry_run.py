#!/usr/bin/env python3
"""Generate an offline-only official configurator candidate preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from glyph_official_configurator_corpus import (
    BACK_AND_FORTH_FIXTURE_PATH,
    DEFAULT_FIXTURE_PATH,
    MANIFEST_PATH,
    display,
    load_json_object,
    sha256_file,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIEW_PATH = REPO_ROOT / "docs/export/fixtures/generated_official_configurator_candidate_preview.json"
REPORT_PATH = REPO_ROOT / "docs/export/fixtures/generated_official_configurator_candidate_preview_report.json"

LABELS = [
    "offline_preview_only",
    "not_production_export",
    "not_device_write",
    "not_webserial",
    "not_runtime_loaded_config",
    "not_official_compatibility_claim",
]

BLOCKED_CLAIMS = [
    "production export",
    "device write",
    "WebSerial",
    "runtime-loaded config",
    "firmware flashing automation",
    "official configurator compatibility claim",
    "universal compatibility claim",
    "nunchuk validation claim",
]


def key_sets(items: Any) -> list[list[str]]:
    if not isinstance(items, list):
        return []
    return sorted([sorted(item) for item in items if isinstance(item, dict)])


def summarize_fixture(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "top_level_keys": list(payload.keys()),
        "counts": {
            "gameModeConfigs": len(payload.get("gameModeConfigs", [])),
            "communicationBackendConfigs": len(payload.get("communicationBackendConfigs", [])),
            "keyboardModes": len(payload.get("keyboardModes", [])),
            "rgbConfigs": len(payload.get("rgbConfigs", [])),
        },
        "game_mode_shapes": [
            {
                "name": mode.get("name"),
                "modeId": mode.get("modeId"),
                "keys": sorted(mode),
            }
            for mode in payload.get("gameModeConfigs", [])
            if isinstance(mode, dict)
        ],
        "communication_backend_key_sets": key_sets(payload.get("communicationBackendConfigs")),
        "keyboard_mode_key_sets": key_sets(payload.get("keyboardModes")),
        "rgb_config_key_sets": key_sets(payload.get("rgbConfigs")),
        "scalar_defaults": {
            "defaultBackendConfig": payload.get("defaultBackendConfig"),
            "defaultUsbBackendConfig": payload.get("defaultUsbBackendConfig"),
            "rgbBrightness": payload.get("rgbBrightness"),
            "defaultDashboardOption": payload.get("defaultDashboardOption"),
        },
    }


def build_preview() -> dict[str, Any]:
    manifest = load_json_object(MANIFEST_PATH)
    default = load_json_object(DEFAULT_FIXTURE_PATH)
    back = load_json_object(BACK_AND_FORTH_FIXTURE_PATH)
    manifest_hash = sha256_file(MANIFEST_PATH)
    fixture_hashes = {
        display(DEFAULT_FIXTURE_PATH): sha256_file(DEFAULT_FIXTURE_PATH),
        display(BACK_AND_FORTH_FIXTURE_PATH): sha256_file(BACK_AND_FORTH_FIXTURE_PATH),
    }

    return {
        "schema_name": "generated_official_configurator_candidate_preview",
        "contract_version": 1,
        "status": "offline_preview_only",
        "preview_labels": LABELS,
        "source_authority": {
            "corpus_id": manifest.get("corpus_id"),
            "source_classification": manifest.get("source_classification"),
            "manifest_path": display(MANIFEST_PATH),
            "manifest_sha256": manifest_hash,
            "fixture_paths": [display(DEFAULT_FIXTURE_PATH), display(BACK_AND_FORTH_FIXTURE_PATH)],
            "fixture_hashes": fixture_hashes,
            "known_unknowns": manifest.get("known_unknowns", []),
        },
        "candidate_kind": "deterministic_offline_preview_metadata",
        "source_backed_shape": summarize_fixture(default),
        "comparison_fixture_shape": summarize_fixture(back),
        "unknowns": [
            "exact official configurator app version",
            "exact capture timestamp",
            "exact push/download route details",
            "whether generated metadata is importable by the official configurator",
            "whether any future export target should be profile-scoped, global, or mixed",
        ],
        "unsupported_fields": [
            "fields not observed in the official corpus fixtures",
            "gameplay semantics for nested values",
            "device transport behavior",
            "runtime-loaded config behavior",
        ],
        "blocked_claims": BLOCKED_CLAIMS,
        "output_boundary": {
            "production_export_created": False,
            "device_write_created": False,
            "webserial_created": False,
            "runtime_loaded_config_created": False,
            "official_compatibility_claimed": False,
            "firmware_flashing_automation_created": False,
            "nunchuk_validation_claimed": False,
        },
    }


def build_report(preview: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "generated_official_configurator_candidate_preview_report",
        "contract_version": 1,
        "status": "OFFLINE_DRY_RUN_REPORT_ONLY",
        "generated_preview": display(PREVIEW_PATH),
        "generator": "tools/glyph_official_configurator_export_candidate_dry_run.py",
        "deterministic": True,
        "preview_sha256": None,
        "labels": preview["preview_labels"],
        "blocked_claims": preview["blocked_claims"],
        "non_claims": preview["output_boundary"],
    }

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write generated preview/report fixtures.")
    args = parser.parse_args()

    preview = build_preview()
    if args.write:
        write_json(PREVIEW_PATH, preview)
        report = build_report(preview)
        report["preview_sha256"] = sha256_file(PREVIEW_PATH)
        write_json(REPORT_PATH, report)
    else:
        print(json.dumps(preview, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
