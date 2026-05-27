#!/usr/bin/env python3
"""Read-only checker for the active Ultimate LT3 config artifact."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "artifacts"
    / "glyph_ultimate_mvp_lt3_active_config_PROFILE.json"
)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _failures_for_ultimate_mode(payload: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    failures: list[str] = []
    raw_modes = payload.get("gameModeConfigs")
    if not isinstance(raw_modes, list):
        return ["gameModeConfigs must be a list"], []

    matched_modes: list[dict[str, Any]] = []
    for index, mode in enumerate(raw_modes):
        if not isinstance(mode, dict):
            failures.append(f"gameModeConfigs[{index}] must be an object")
            continue
        mode_id = mode.get("modeId")
        mode_name = mode.get("name")
        if mode_id == "MODE_ULTIMATE" or mode_name == "Ultimate":
            matched_modes.append(mode)

    if len(matched_modes) != 1:
        failures.append(
            "ambiguous Ultimate mode selection: "
            f"expected exactly one MODE_ULTIMATE/Ultimate entry, found {len(matched_modes)}"
        )
    return failures, matched_modes


def _extract_remaps(mode: dict[str, Any]) -> tuple[list[str], list[dict[str, str | None]]]:
    failures: list[str] = []
    raw_remaps = mode.get("buttonRemapping")
    if not isinstance(raw_remaps, list):
        return ["Ultimate buttonRemapping must be a list"], []

    remaps: list[dict[str, str | None]] = []
    for index, entry in enumerate(raw_remaps):
        if not isinstance(entry, dict):
            failures.append(f"buttonRemapping[{index}] must be an object")
            continue
        physical = entry.get("physicalButton")
        if not isinstance(physical, str) or not physical:
            failures.append(
                f"buttonRemapping[{index}].physicalButton must be a non-empty string"
            )
            continue
        activates = entry.get("activates")
        if activates is not None and not isinstance(activates, str):
            failures.append(f"buttonRemapping[{index}].activates must be a string when present")
            continue
        remaps.append({"physicalButton": physical, "activates": activates})
    return failures, remaps


def main() -> int:
    failures: list[str] = []

    physical_lt3_bound_to_logical_lt3 = False
    previous_lt3_to_lf4_binding_removed = False
    existing_tilt1_tilt2_bindings_preserved = False

    if not TARGET_ARTIFACT.exists():
        failures.append(f"missing target artifact: {_rel(TARGET_ARTIFACT)}")
    else:
        try:
            payload = json.loads(TARGET_ARTIFACT.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"invalid JSON in target artifact: {exc}")
            payload = None

        if payload is not None and not isinstance(payload, dict):
            failures.append("artifact root JSON value must be an object")
            payload = None

        if isinstance(payload, dict):
            mode_failures, modes = _failures_for_ultimate_mode(payload)
            failures.extend(mode_failures)

            if len(modes) == 1:
                remap_failures, remaps = _extract_remaps(modes[0])
                failures.extend(remap_failures)

                rf3_to_lt1 = [
                    remap
                    for remap in remaps
                    if remap["physicalButton"] == "BTN_RF3" and remap["activates"] == "BTN_LT1"
                ]
                rf4_to_lt2 = [
                    remap
                    for remap in remaps
                    if remap["physicalButton"] == "BTN_RF4" and remap["activates"] == "BTN_LT2"
                ]
                lt3_all = [
                    remap for remap in remaps if remap["physicalButton"] == "BTN_LT3"
                ]
                lt3_to_lt3 = [
                    remap for remap in lt3_all if remap["activates"] == "BTN_LT3"
                ]
                lt3_to_lf4 = [
                    remap for remap in lt3_all if remap["activates"] == "BTN_LF4"
                ]

                if len(rf3_to_lt1) != 1:
                    failures.append(
                        "expected exactly one BTN_RF3 -> BTN_LT1 mapping, "
                        f"found {len(rf3_to_lt1)}"
                    )
                if len(rf4_to_lt2) != 1:
                    failures.append(
                        "expected exactly one BTN_RF4 -> BTN_LT2 mapping, "
                        f"found {len(rf4_to_lt2)}"
                    )
                if len(lt3_all) != 1:
                    failures.append(
                        "expected exactly one BTN_LT3 physical remap entry, "
                        f"found {len(lt3_all)}"
                    )
                if len(lt3_to_lt3) != 1:
                    failures.append(
                        "expected exactly one BTN_LT3 -> BTN_LT3 mapping, "
                        f"found {len(lt3_to_lt3)}"
                    )
                if lt3_to_lf4:
                    failures.append("unexpected BTN_LT3 -> BTN_LF4 mapping present")

                physical_lt3_bound_to_logical_lt3 = len(lt3_all) == 1 and len(lt3_to_lt3) == 1
                previous_lt3_to_lf4_binding_removed = len(lt3_to_lf4) == 0
                existing_tilt1_tilt2_bindings_preserved = (
                    len(rf3_to_lt1) == 1 and len(rf4_to_lt2) == 1
                )

    print(f"target_file_checked={_rel(TARGET_ARTIFACT)}")
    print("implementation_kind=importable_config_profile_artifact")
    print("artifact_kind=profile_config_json_projection")
    print("requires_manual_import=true")
    print("applies_to_default_restore_only=false")
    print(
        "physical_lt3_bound_to_logical_lt3="
        f"{'true' if physical_lt3_bound_to_logical_lt3 else 'false'}"
    )
    print(
        "previous_lt3_to_lf4_binding_removed="
        f"{'true' if previous_lt3_to_lf4_binding_removed else 'false'}"
    )
    print(
        "existing_tilt1_tilt2_bindings_preserved="
        f"{'true' if existing_tilt1_tilt2_bindings_preserved else 'false'}"
    )
    print("active_device_profile_updated=false")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
