#!/usr/bin/env python3
"""Read-only checker for Ultimate MVP historical LT3 or explicit identity baseline binding."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json"
)


def fail(message: str) -> None:
    print(f"failure={message}")


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise AssertionError(f"missing source file: {path.relative_to(REPO_ROOT)}")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON in source file: {exc}") from exc
    if not isinstance(payload, dict):
        raise AssertionError("root JSON type must be object")
    return payload


def get_ultimate_mode(payload: dict) -> dict:
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        raise AssertionError("gameModeConfigs must be a list")
    for mode in modes:
        if not isinstance(mode, dict):
            continue
        if mode.get("modeId") == "MODE_ULTIMATE" or mode.get("name") == "Ultimate":
            return mode
    raise AssertionError("could not locate Ultimate mode in gameModeConfigs")


def extract_remaps(mode: dict) -> list[dict]:
    remaps = mode.get("buttonRemapping")
    if not isinstance(remaps, list):
        raise AssertionError("Ultimate buttonRemapping must be a list")
    normalized: list[dict] = []
    for index, remap in enumerate(remaps):
        if not isinstance(remap, dict):
            raise AssertionError(f"buttonRemapping[{index}] is not an object")
        physical = remap.get("physicalButton")
        if not isinstance(physical, str):
            raise AssertionError(f"buttonRemapping[{index}].physicalButton missing or not a string")
        activates = remap.get("activates")
        if activates is not None and not isinstance(activates, str):
            raise AssertionError(f"buttonRemapping[{index}].activates must be a string when present")
        normalized.append({"physicalButton": physical, "activates": activates})
    return normalized


def main() -> int:
    rel_source = SOURCE_FILE.relative_to(REPO_ROOT)
    print(f"source_file_checked={rel_source}")

    profile_mode = "UNDETERMINED"
    physical_lt3_bound_to_logical_lt3 = False
    previous_lt3_to_lf4_binding_removed = True
    existing_tilt1_tilt2_bindings_preserved = False

    failures: list[str] = []

    try:
        payload = load_json(SOURCE_FILE)
        ultimate_mode = get_ultimate_mode(payload)
        remaps = extract_remaps(ultimate_mode)
    except AssertionError as exc:
        fail(str(exc))
        print("physical_lt3_bound_to_logical_lt3=false")
        print("previous_lt3_to_lf4_binding_removed=false")
        print("existing_tilt1_tilt2_bindings_preserved=false")
        print("status=FAIL")
        return 1

    rf3_matches = [r for r in remaps if r["physicalButton"] == "BTN_RF3" and r["activates"] == "BTN_LT1"]
    rf4_matches = [r for r in remaps if r["physicalButton"] == "BTN_RF4" and r["activates"] == "BTN_LT2"]
    lt3_all = [r for r in remaps if r["physicalButton"] == "BTN_LT3"]
    lt3_to_lt3 = [r for r in lt3_all if r["activates"] == "BTN_LT3"]
    lt3_to_lf4 = [r for r in lt3_all if r["activates"] == "BTN_LF4"]

    if len(lt3_all) != 1:
        failures.append(f"expected exactly one BTN_LT3 physical mapping, found {len(lt3_all)}")
    if lt3_to_lf4:
        failures.append("found removed binding BTN_LT3 -> BTN_LF4")

    omitted_activates_count = sum(1 for remap in remaps if remap["activates"] is None)
    semantic_remap_count = sum(
        1
        for remap in remaps
        if remap["activates"] is not None and remap["activates"] != remap["physicalButton"]
    )
    explicit_self_activates_count = sum(
        1 for remap in remaps if remap["activates"] == remap["physicalButton"]
    )
    historical_mode = len(rf3_matches) == 1 and len(rf4_matches) == 1 and len(lt3_to_lt3) == 1
    identity_mode = (
        omitted_activates_count == 0
        and semantic_remap_count == 0
        and explicit_self_activates_count == len(remaps)
    )

    if omitted_activates_count > 0 and not historical_mode:
        failures.append(
            "identity baseline requires explicit activates; "
            f"found {omitted_activates_count} omitted activates entries"
        )

    if historical_mode and identity_mode:
        failures.append("ambiguous profile mode: both historical and identity conditions matched")
    elif historical_mode:
        profile_mode = "HISTORICAL_LT3_DPAD_REMAP"
        physical_lt3_bound_to_logical_lt3 = len(lt3_to_lt3) == 1 and len(lt3_all) == 1
        existing_tilt1_tilt2_bindings_preserved = True
    elif identity_mode:
        profile_mode = "IDENTITY_BASELINE"
        physical_lt3_bound_to_logical_lt3 = len(lt3_all) == 1 and len(lt3_to_lt3) == 1
        existing_tilt1_tilt2_bindings_preserved = False
    else:
        failures.append(
            "unsupported MODE_ULTIMATE mapping state: expected either historical LT3 remap mode "
            "or explicit self-activates identity baseline mode"
        )

    previous_lt3_to_lf4_binding_removed = len(lt3_to_lf4) == 0

    print(f"profile_mode={profile_mode}")
    print(f"physical_lt3_bound_to_logical_lt3={'true' if physical_lt3_bound_to_logical_lt3 else 'false'}")
    print(
        "previous_lt3_to_lf4_binding_removed="
        f"{'true' if previous_lt3_to_lf4_binding_removed else 'false'}"
    )
    print(
        "existing_tilt1_tilt2_bindings_preserved="
        f"{'true' if existing_tilt1_tilt2_bindings_preserved else 'false'}"
    )

    if failures:
        for item in failures:
            fail(item)
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
