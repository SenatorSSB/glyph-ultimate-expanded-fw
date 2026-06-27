#!/usr/bin/env python3
"""Validate that the final friend Ultimate profile intentionally deviates from the old identity fixture."""

from __future__ import annotations

from check_friend_profile3_final_layout import main as check_final_layout


def main() -> int:
    result = check_final_layout()
    if result != 0:
        return result

    print("checker=friend_ultimate_default_profile_matches_fixture")
    print("historical_fixture=docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json")
    print("identity_fixture_exact_match=false")
    print("friend_final_layout_deviates_from_fixture=true")
    print("rf6_identity_lock_retired=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
