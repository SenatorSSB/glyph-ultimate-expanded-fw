#!/usr/bin/env python3
"""Create an offline diff/simulation report for the generated preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from glyph_official_configurator_corpus import (
    BACK_AND_FORTH_FIXTURE_PATH,
    DEFAULT_FIXTURE_PATH,
    compute_structural_diff,
    display,
    load_json_object,
    sha256_file,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_PREVIEW_PATH = (
    REPO_ROOT / "docs/export/fixtures/generated_official_configurator_candidate_preview.json"
)
DIFF_REPORT_JSON = (
    REPO_ROOT / "docs/export/fixtures/official_configurator_export_candidate_diff_report.json"
)
DIFF_REPORT_MD = REPO_ROOT / "docs/export/official_configurator_export_candidate_diff_report.md"


def changed_scalar_defaults(default: dict[str, Any], back: dict[str, Any]) -> list[str]:
    scalar_keys = [
        "defaultBackendConfig",
        "defaultUsbBackendConfig",
        "rgbBrightness",
        "defaultDashboardOption",
    ]
    return [key for key in scalar_keys if default.get(key) != back.get(key)]


def build_report() -> dict[str, Any]:
    default = load_json_object(DEFAULT_FIXTURE_PATH)
    back = load_json_object(BACK_AND_FORTH_FIXTURE_PATH)
    generated_preview = load_json_object(GENERATED_PREVIEW_PATH)
    structural = compute_structural_diff()

    return {
        "schema_name": "official_configurator_export_candidate_diff_report",
        "contract_version": 1,
        "status": "OFFLINE_DIFF_SIMULATION_ONLY",
        "inputs": {
            "official_default_fixture": display(DEFAULT_FIXTURE_PATH),
            "official_default_fixture_sha256": sha256_file(DEFAULT_FIXTURE_PATH),
            "official_back_and_forth_fixture": display(BACK_AND_FORTH_FIXTURE_PATH),
            "official_back_and_forth_fixture_sha256": sha256_file(BACK_AND_FORTH_FIXTURE_PATH),
            "generated_candidate_preview": display(GENERATED_PREVIEW_PATH),
            "generated_candidate_preview_sha256": sha256_file(GENERATED_PREVIEW_PATH),
        },
        "classification": {
            "stable_top_level_keys": structural["top_level_keys_default"],
            "stable_counts": generated_preview["source_backed_shape"]["counts"],
            "changed_gameModeConfigs_entries": structural["changed_game_mode_entries"],
            "changed_rgbConfigs_entries": structural["rgb"]["changed_rgb_config_indexes"],
            "changed_scalar_defaults": changed_scalar_defaults(default, back),
            "fields_unknown": generated_preview["unknowns"],
            "fields_unsupported": generated_preview["unsupported_fields"],
            "fields_unsafe_to_model": [
                "official configurator import acceptance",
                "official configurator export/back-and-forth success",
                "device write behavior",
                "runtime-loaded config behavior",
                "firmware flashing behavior",
                "gameplay semantics",
            ],
        },
        "non_claims": {
            "manual_official_configurator_app_interaction_occurred": False,
            "no_compatibility_claim": True,
            "no_production_export": True,
            "no_device_write": True,
            "no_runtime_loaded_config": True,
            "no_webserial": True,
            "no_firmware_flashing_automation": True,
            "no_nunchuk_validation": True,
        },
    }


def markdown_report(payload: dict[str, Any]) -> str:
    changed_modes = payload["classification"]["changed_gameModeConfigs_entries"]
    changed_rgb = payload["classification"]["changed_rgbConfigs_entries"]
    changed_scalars = payload["classification"]["changed_scalar_defaults"]
    return "\n".join(
        [
            "# Official Configurator Export Candidate Diff Report",
            "",
            "Status: `OFFLINE_DIFF_SIMULATION_ONLY`",
            "",
            "This report is an offline structural comparison between the official",
            "default fixture, the official back-and-forth fixture, and the generated",
            "offline candidate preview. No manual official configurator app",
            "interaction occurred.",
            "",
            "## Inputs",
            "",
            f"- official default fixture: `{payload['inputs']['official_default_fixture']}`",
            f"- official back-and-forth fixture: `{payload['inputs']['official_back_and_forth_fixture']}`",
            f"- generated candidate preview: `{payload['inputs']['generated_candidate_preview']}`",
            "",
            "## Classification",
            "",
            f"- stable top-level keys: {len(payload['classification']['stable_top_level_keys'])}",
            f"- stable counts: `{json.dumps(payload['classification']['stable_counts'], sort_keys=True)}`",
            f"- changed gameModeConfigs entries: {len(changed_modes)}",
            f"- changed rgbConfigs entries: `{changed_rgb}`",
            f"- changed scalar defaults: `{changed_scalars}`",
            "- fields unknown: exact app/version/route and import acceptance remain unknown",
            "- fields unsupported: unobserved fields, transport behavior, runtime behavior, and gameplay semantics",
            "- fields unsafe to model: official import/export success, device write, runtime-loaded config, flashing, gameplay semantics",
            "",
            "## Non-Claims",
            "",
            "- no compatibility claim",
            "- no production export",
            "- no device write",
            "- no WebSerial",
            "- no runtime-loaded config",
            "- no firmware flashing automation",
            "- no nunchuk validation",
            "",
        ]
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the diff report fixtures.")
    args = parser.parse_args()
    payload = build_report()
    if args.write:
        write_json(DIFF_REPORT_JSON, payload)
        DIFF_REPORT_MD.write_text(markdown_report(payload), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
