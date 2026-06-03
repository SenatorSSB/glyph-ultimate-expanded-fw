#!/usr/bin/env python3
"""Validate repo-committed Glyph config JSON compatibility fixtures."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_config_json_compatibility_fixtures_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json"
)
ACTIVE_ARTIFACT_PATH = (
    REPO_ROOT
    / "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
)
FIXTURE_ARTIFACT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json"
)

SCHEMA_NAME = "glyph_config_json_compatibility_cases"
CASE_VERSION = 1
STATUS = "repo_committed_fixture_compatibility_only"
HARDWARE_STATUS = "not_new_hardware_result"
REQUIRED_CASE_IDS = (
    "active_profile_artifact_json_parse",
    "active_profile_mode_ultimate_structure",
    "fixture_profile_artifact_json_parse",
    "fixture_profile_mode_ultimate_structure",
    "explicit_identity_bindings_preserved",
    "explicit_disable_entries_shape_if_present",
    "serial_dry_run_tooling_guard_present",
    "serial_dry_run_accepts_active_profile_artifact",
    "serial_dry_run_accepts_fixture_profile_artifact",
    "no_profile_artifact_change_introduced_by_branch",
)
REQUIRED_DOC_CAVEATS = (
    "repo-committed fixture compatibility only",
    "not official configurator source authority",
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
)


class CompatibilityError(ValueError):
    """Raised when the compatibility fixture drifts from required boundaries."""


def fail(message: str) -> None:
    raise CompatibilityError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def require_case_map(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases_value = fixture.get("cases")
    if not isinstance(cases_value, list):
        fail("cases must be a list")

    case_map: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(cases_value):
        if not isinstance(item, dict):
            fail(f"cases[{index}] must be an object")
        case_id = item.get("id")
        if not isinstance(case_id, str) or not case_id:
            fail(f"cases[{index}].id must be a non-empty string")
        if case_id in case_map:
            fail(f"duplicate case id: {case_id}")
        case_map[case_id] = item

    if tuple(case_map) != REQUIRED_CASE_IDS:
        fail("cases must contain the required ids in stable order")
    return case_map


def validate_fixture_top_level(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected = {
        "schema_name": SCHEMA_NAME,
        "case_version": CASE_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "official_configurator_compatibility_claimed": False,
        "device_write_implemented": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")

    caveats = require_string_list(fixture, "doc_caveats")
    if caveats != list(REQUIRED_DOC_CAVEATS):
        fail("doc_caveats drifted from required compatibility caveats")

    return require_case_map(fixture)


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_CAVEATS:
        if phrase.lower() not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_profile_json(path: Path) -> dict[str, Any]:
    payload = load_json_object(path)
    modes = payload.get("gameModeConfigs")
    if modes is not None and not isinstance(modes, list):
        fail(f"{display(path)} gameModeConfigs must be a list when present")
    return payload


def find_mode_ultimate(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        fail(f"{display(path)} gameModeConfigs must be a list")
    matches = [
        mode
        for mode in modes
        if isinstance(mode, dict)
        and (mode.get("modeId") == "MODE_ULTIMATE" or mode.get("name") == "Ultimate")
    ]
    if len(matches) != 1:
        fail(f"{display(path)} expected exactly one MODE_ULTIMATE/Ultimate mode, found {len(matches)}")
    return matches[0]


def validate_mode_ultimate_lists(mode: dict[str, Any], path: Path) -> None:
    button_remapping = mode.get("buttonRemapping")
    if not isinstance(button_remapping, list):
        fail(f"{display(path)} MODE_ULTIMATE buttonRemapping must be a list")
    socd_pairs = mode.get("socdPairs")
    if not isinstance(socd_pairs, list):
        fail(f"{display(path)} MODE_ULTIMATE socdPairs must be a list")


def validate_disable_entries_shape(payload: dict[str, Any], path: Path) -> int:
    disable_count = 0
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        fail(f"{display(path)} gameModeConfigs must be a list")
    for mode_index, mode in enumerate(modes):
        if not isinstance(mode, dict):
            continue
        remaps = mode.get("buttonRemapping")
        if remaps is None:
            continue
        if not isinstance(remaps, list):
            fail(f"{display(path)} gameModeConfigs[{mode_index}].buttonRemapping must be a list")
        for remap_index, entry in enumerate(remaps):
            if not isinstance(entry, dict):
                fail(
                    f"{display(path)} gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}] must be an object"
                )
            if "activates" in entry:
                continue
            physical = entry.get("physicalButton")
            if not isinstance(physical, str) or not physical:
                fail(
                    f"{display(path)} physicalButton-only remap at gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}] must include a non-empty physicalButton"
                )
            disable_count += 1
    return disable_count


def run_python_tool(relpath: str, *args: str) -> str:
    tool_path = REPO_ROOT / relpath
    if not tool_path.exists():
        fail(f"missing tool: {relpath}")
    completed = subprocess.run(
        [sys.executable, str(tool_path.relative_to(REPO_ROOT)), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    if completed.returncode != 0:
        fail(f"{relpath} failed with returncode={completed.returncode}: {output}")
    if "status=PASS" not in output:
        fail(f"{relpath} did not report status=PASS")
    return output


def ensure_serial_dry_run_accepts(relpath: str) -> None:
    output = run_python_tool("tools/glyph_serial_config_tool.py", "--dry-run", "--artifact", relpath)
    required_phrases = (
        "mode=dry_run",
        "artifact_validated=true",
        "live_device_access=false",
        "active_device_profile_updated=false",
        "readback_verified=false",
        "firmware_flashing=false",
        "dry_run_serial_opened=false",
        "protocol_source_confirmed=true",
    )
    for phrase in required_phrases:
        if phrase not in output:
            fail(f"tools/glyph_serial_config_tool.py dry-run output missing required phrase: {phrase}")


def ensure_unchanged_from_base(relpath: str, base_ref: str) -> None:
    completed = subprocess.run(
        ["git", "diff", "--quiet", base_ref, "--", relpath],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return
    if completed.returncode == 1:
        fail(f"{relpath} differs from {base_ref}")
    details = "\n".join(
        part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
    )
    fail(f"git diff check failed for {relpath} vs {base_ref}: {details}")


def main() -> int:
    print("glyph_config_json_compatibility_fixtures")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        cases = validate_fixture_top_level(fixture)
        validate_doc()

        active_payload = validate_profile_json(ACTIVE_ARTIFACT_PATH)
        fixture_payload = validate_profile_json(FIXTURE_ARTIFACT_PATH)

        validate_mode_ultimate_lists(
            find_mode_ultimate(active_payload, ACTIVE_ARTIFACT_PATH),
            ACTIVE_ARTIFACT_PATH,
        )
        validate_mode_ultimate_lists(
            find_mode_ultimate(fixture_payload, FIXTURE_ARTIFACT_PATH),
            FIXTURE_ARTIFACT_PATH,
        )

        for relpath in (
            "tools/check_glyph_ultimate_identity_profile_baseline.py",
            "tools/check_glyph_smashbox_identity_runtime_bindings.py",
            "tools/check_glyph_active_profile_binding_path.py",
            "tools/check_glyph_serial_config_writer.py",
        ):
            run_python_tool(relpath)

        disable_count = 0
        disable_count += validate_disable_entries_shape(active_payload, ACTIVE_ARTIFACT_PATH)
        disable_count += validate_disable_entries_shape(fixture_payload, FIXTURE_ARTIFACT_PATH)
        if disable_count <= 0:
            fail("expected at least one committed physicalButton-only remap entry across the loaded profile JSON artifacts")

        ensure_serial_dry_run_accepts(
            "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
        )
        ensure_serial_dry_run_accepts(
            "docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json"
        )

        base_ref = cases["no_profile_artifact_change_introduced_by_branch"].get("git_base_ref")
        if not isinstance(base_ref, str) or not base_ref:
            fail("no_profile_artifact_change_introduced_by_branch.git_base_ref must be a non-empty string")
        ensure_unchanged_from_base(
            "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
            base_ref,
        )
        ensure_unchanged_from_base(
            "docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json",
            base_ref,
        )
    except (OSError, json.JSONDecodeError, CompatibilityError, ValueError) as exc:
        print("status=FAIL")
        print("cases=0")
        print("official_configurator_compatibility_claimed=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"cases={len(REQUIRED_CASE_IDS)}")
    print("official_configurator_compatibility_claimed=false")
    print(f"hardware_status={fixture['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
