#!/usr/bin/env python3
"""Validate Tilt button ID probe in historical remap mode or explicit identity baseline mode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from glyph_config_model import get_ultimate_mode, list_button_remapping, load_profile_json


REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json"
)
DOMAIN_SPEC = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_ultimate_tilt_domain_spec.json"


def _branch_claims_confirmation() -> bool:
    if not DOMAIN_SPEC.exists():
        return False
    try:
        payload = json.loads(DOMAIN_SPEC.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if not isinstance(payload, dict):
        return False
    confirmation = payload.get("button_id_confirmation")
    if not isinstance(confirmation, dict):
        return False
    return confirmation.get("status") == "CONFIRMED_FOR_UPLOADED_MVP_LAYOUT"


def _remap_map(profile_path: Path) -> dict[str, str | None]:
    profile: dict[str, Any] = load_profile_json(profile_path)
    ultimate = get_ultimate_mode(profile)
    return {entry.physical_button: entry.activates for entry in list_button_remapping(ultimate)}


def main() -> int:
    if not PROFILE_FIXTURE.exists():
        print(f"fixture={PROFILE_FIXTURE.relative_to(REPO_ROOT)}")
        print("status=BLOCKED_MISSING_FIXTURE")
        if _branch_claims_confirmation():
            return 1
        return 0

    remaps = _remap_map(PROFILE_FIXTURE)

    historical_expected = {
        "BTN_RF3": "BTN_LT1",
        "BTN_RF4": "BTN_LT2",
    }
    identity_expected = {
        "BTN_RF3": "BTN_RF3",
        "BTN_RF4": "BTN_RF4",
    }
    failures: list[str] = []

    historical_matches = all(
        remaps.get(physical_button) == logical_input
        for physical_button, logical_input in historical_expected.items()
    )
    identity_matches = all(
        remaps.get(physical_button) == logical_input
        for physical_button, logical_input in identity_expected.items()
    )

    semantic_remap_count = sum(
        1
        for physical, logical in remaps.items()
        if logical not in (None, "BTN_UNSPECIFIED", physical)
    )
    omitted_activates_count = sum(
        1 for logical in remaps.values() if logical in (None, "BTN_UNSPECIFIED")
    )

    profile_mode = "UNDETERMINED"
    if historical_matches:
        profile_mode = "HISTORICAL_LT3_DPAD_REMAP"
    elif identity_matches:
        profile_mode = "IDENTITY_BASELINE"
        if omitted_activates_count != 0:
            failures.append(
                "identity baseline expected explicit self-activates for MODE_ULTIMATE remap map"
            )
        if semantic_remap_count != 0:
            failures.append(
                "identity baseline expected no semantic remaps in MODE_ULTIMATE remap map"
            )
    else:
        for physical_button, logical_input in historical_expected.items():
            observed = remaps.get(physical_button)
            failures.append(f"{physical_button} expected {logical_input!r} or None, got {observed!r}")

    print("tilt1_physical_button=BTN_RF3")
    print(f"tilt1_logical_post_remap_input={remaps.get('BTN_RF3')}")
    print("tilt2_physical_button=BTN_RF4")
    print(f"tilt2_logical_post_remap_input={remaps.get('BTN_RF4')}")
    print(f"profile_mode={profile_mode}")
    print(f"omitted_activates_count={omitted_activates_count}")
    print(f"semantic_remap_count={semantic_remap_count}")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    if profile_mode == "IDENTITY_BASELINE":
        print("runtime_followup_required=true")
        print("status=PASS_IDENTITY_BASELINE")
    else:
        print("runtime_followup_required=false")
        print("status=PASS_HISTORICAL_REMAP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
