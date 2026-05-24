#!/usr/bin/env python3
"""Validate uploaded MVP profile remaps for Tilt1/Tilt2 button ID confirmation."""

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

    expected = {
        "BTN_RF3": "BTN_LT1",
        "BTN_RF4": "BTN_LT2",
    }
    failures: list[str] = []
    for physical_button, logical_input in expected.items():
        observed = remaps.get(physical_button)
        if observed != logical_input:
            failures.append(f"{physical_button} expected {logical_input}, got {observed!r}")

    print("tilt1_physical_button=BTN_RF3")
    print(f"tilt1_logical_post_remap_input={remaps.get('BTN_RF3')}")
    print("tilt2_physical_button=BTN_RF4")
    print(f"tilt2_logical_post_remap_input={remaps.get('BTN_RF4')}")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
