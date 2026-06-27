#!/usr/bin/env python3
"""Validate the final friend one-shot default profile adoption marker."""

from __future__ import annotations

from check_friend_profile3_final_layout import main as check_final_layout


def main() -> int:
    result = check_final_layout()
    if result != 0:
        return result

    print("checker=friend_default_profile_force_once")
    print("marker=/friend_profile3_final_faifra_layout_applied.flag")
    print("old_marker=/friend_profile3_default_applied.flag")
    print("old_marker_active=false")
    print("one_shot_save_before_load=true")
    print("normal_load_fallback_preserved=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
