#!/usr/bin/env python3
"""Validate the committed offline remapper Ultimate profile diff report."""

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
    / "docs/calibration/glyph_offline_remapper_ultimate_diff_report_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_ultimate_diff_report_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_ultimate_diff_report"
REPORT_VERSION = 1
STATUS = "docs_tools_ultimate_profile_diff"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_DOC_PHRASES = (
    "mode_ultimate profile-level diff",
    "profile-level representation only",
    "runtime-owned behavior not represented",
    "not gameplay correctness",
    "not official compatibility",
    "not hardware validation",
)


class OfflineRemapperUltimateDiffReportError(ValueError):
    """Raised when the committed Ultimate diff report drifts from expectations."""


def fail(message: str) -> None:
    raise OfflineRemapperUltimateDiffReportError(message)


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


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def require_mode_ultimate(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    game_modes = payload.get("gameModeConfigs")
    if not isinstance(game_modes, list):
        fail(f"{display(path)} gameModeConfigs must be a list")

    matches = [
        entry
        for entry in game_modes
        if isinstance(entry, dict) and entry.get("modeId") == "MODE_ULTIMATE"
    ]
    if len(matches) != 1:
        fail(f"{display(path)} must contain exactly one MODE_ULTIMATE profile")
    return matches[0]


def count_disabled_entries(entries: list[Any]) -> int:
    return sum(
        1
        for entry in entries
        if isinstance(entry, dict) and entry.get("disabled") is True
    )


def count_entries_with_key(entries: list[Any], key: str) -> int:
    return sum(1 for entry in entries if isinstance(entry, dict) and key in entry)


def list_difference(source: list[Any], comparison: list[Any]) -> list[Any]:
    return [entry for entry in source if entry not in comparison]


def exact_value_summary(
    input_value: Any,
    exported_value: Any,
    *,
    input_label: str = "input",
    exported_label: str = "exported",
) -> dict[str, Any]:
    return {
        input_label: input_value,
        exported_label: exported_value,
        "exact_value_equality": input_value == exported_value,
    }


def build_report() -> dict[str, Any]:
    input_payload = load_json_object(ACTIVE_ARTIFACT_PATH)
    exported_payload = load_json_object(EXPORTED_ARTIFACT_PATH)
    input_mode = require_mode_ultimate(input_payload, ACTIVE_ARTIFACT_PATH)
    exported_mode = require_mode_ultimate(exported_payload, EXPORTED_ARTIFACT_PATH)

    input_socd_pairs = input_mode.get("socdPairs")
    exported_socd_pairs = exported_mode.get("socdPairs")
    if not isinstance(input_socd_pairs, list):
        fail("input MODE_ULTIMATE socdPairs must be a list")
    if not isinstance(exported_socd_pairs, list):
        fail("exported MODE_ULTIMATE socdPairs must be a list")

    input_button_remapping = input_mode.get("buttonRemapping")
    exported_button_remapping = exported_mode.get("buttonRemapping")
    if not isinstance(input_button_remapping, list):
        fail("input MODE_ULTIMATE buttonRemapping must be a list")
    if not isinstance(exported_button_remapping, list):
        fail("exported MODE_ULTIMATE buttonRemapping must be a list")

    input_only_fields = sorted(set(input_mode) - set(exported_mode))
    exported_only_fields = sorted(set(exported_mode) - set(input_mode))
    retains_profile_level_structure = (
        not input_only_fields
        and not exported_only_fields
        and input_mode.get("name") == exported_mode.get("name")
        and input_mode.get("rgbConfig") == exported_mode.get("rgbConfig")
        and input_mode.get("layoutPlate") == exported_mode.get("layoutPlate")
        and input_mode.get("applicableBackends")
        == exported_mode.get("applicableBackends")
        and input_mode.get("menuButtonIcon") == exported_mode.get("menuButtonIcon")
    )

    return {
        "schema_name": SCHEMA_NAME,
        "report_version": REPORT_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "official_configurator_compatibility_claimed": False,
        "firmware_behavior_validated": False,
        "profile_level_representation_only": True,
        "runtime_owned_behavior_represented": False,
        "input_artifact": {
            "path": display(ACTIVE_ARTIFACT_PATH),
            "sha256": sha256(ACTIVE_ARTIFACT_PATH),
        },
        "exported_artifact": {
            "path": display(EXPORTED_ARTIFACT_PATH),
            "sha256": sha256(EXPORTED_ARTIFACT_PATH),
        },
        "mode_ultimate_profile_diff": {
            "profile_presence": {
                "input": True,
                "exported": True,
            },
            "name": exact_value_summary(
                input_mode.get("name"), exported_mode.get("name")
            ),
            "socdPairs": {
                "input_count": len(input_socd_pairs),
                "exported_count": len(exported_socd_pairs),
                "exact_value_equality": input_socd_pairs == exported_socd_pairs,
                "missing_from_exported": list_difference(
                    input_socd_pairs, exported_socd_pairs
                ),
                "added_in_exported": list_difference(
                    exported_socd_pairs, input_socd_pairs
                ),
            },
            "buttonRemapping": {
                "input_count": len(input_button_remapping),
                "exported_count": len(exported_button_remapping),
                "exact_value_equality": (
                    input_button_remapping == exported_button_remapping
                ),
                "missing_from_exported": list_difference(
                    input_button_remapping, exported_button_remapping
                ),
                "added_in_exported": list_difference(
                    exported_button_remapping, input_button_remapping
                ),
            },
            "disabled_entries": {
                "input": count_disabled_entries(input_button_remapping),
                "exported": count_disabled_entries(exported_button_remapping),
            },
            "entries_with_activates": {
                "input": count_entries_with_key(input_button_remapping, "activates"),
                "exported": count_entries_with_key(
                    exported_button_remapping, "activates"
                ),
            },
            "rgbConfig": exact_value_summary(
                input_mode.get("rgbConfig"), exported_mode.get("rgbConfig")
            ),
            "layoutPlate": exact_value_summary(
                input_mode.get("layoutPlate"), exported_mode.get("layoutPlate")
            ),
            "applicableBackends": exact_value_summary(
                input_mode.get("applicableBackends"),
                exported_mode.get("applicableBackends"),
            ),
            "menuButtonIcon": exact_value_summary(
                input_mode.get("menuButtonIcon"),
                exported_mode.get("menuButtonIcon"),
            ),
            "extra_missing_fields": {
                "input_only_fields": input_only_fields,
                "exported_only_fields": exported_only_fields,
                "exact_value_equality": (
                    not input_only_fields and not exported_only_fields
                ),
            },
            "exported_profile_retains_profile_level_structure": (
                retains_profile_level_structure
            ),
            "exported_profile_can_represent_firmware_owned_runtime_behavior": False,
            "comparison_summary": {
                "matching_profile_level_fields": [
                    "name",
                    "rgbConfig",
                    "layoutPlate",
                    "applicableBackends",
                    "menuButtonIcon",
                    "extra_missing_fields",
                ],
                "differing_profile_level_fields": [
                    "socdPairs",
                    "buttonRemapping",
                    "entries_with_activates",
                ],
                "notes": [
                    "MODE_ULTIMATE is present in both artifacts.",
                    "The exported profile retains profile-level structure.",
                    "Profile-level representation only.",
                    "Runtime-owned behavior not represented.",
                    "Not gameplay correctness.",
                ],
            },
        },
    }


def validate_top_level(report: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "report_version": REPORT_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "official_configurator_compatibility_claimed": False,
        "firmware_behavior_validated": False,
        "profile_level_representation_only": True,
        "runtime_owned_behavior_represented": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_fixture(report: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(report)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated report JSON")

    committed = load_json_object(FIXTURE_PATH)
    if committed != report:
        fail("committed fixture JSON object drifted from regenerated report output")

    for label, artifact_path in (
        ("input_artifact", ACTIVE_ARTIFACT_PATH),
        ("exported_artifact", EXPORTED_ARTIFACT_PATH),
    ):
        artifact = committed.get(label)
        if not isinstance(artifact, dict):
            fail(f"{label} must be an object")
        if artifact.get("path") != display(artifact_path):
            fail(f"{label}.path must be {display(artifact_path)!r}")
        if artifact.get("sha256") != sha256(artifact_path):
            fail(f"{label}.sha256 mismatch")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the committed docs/tools-only MODE_ULTIMATE profile-level diff "
            "between the active Glyph profile artifact and the exported offline "
            "remapper JSON fixture."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of the concise validation summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_level_representation_only = "true"
    runtime_owned_behavior_represented = "false"
    try:
        report = build_report()
        if args.json:
            print(canonical_json_text(report), end="")
            return 0
        validate_top_level(report)
        validate_fixture(report)
        validate_doc()
    except (
        OSError,
        OfflineRemapperUltimateDiffReportError,
        ValueError,
    ) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print(
            "profile_level_representation_only="
            f"{profile_level_representation_only}"
        )
        print(
            "runtime_owned_behavior_represented="
            f"{runtime_owned_behavior_represented}"
        )
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print(f"profile_level_representation_only={profile_level_representation_only}")
    print(
        "runtime_owned_behavior_represented="
        f"{runtime_owned_behavior_represented}"
    )
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
