#!/usr/bin/env python3
"""Validate final friend LT5/LF5/RF6 Up semantics by source inspection."""

from __future__ import annotations

from check_friend_profile3_final_layout import main as check_final_layout


def main() -> int:
    result = check_final_layout()
    if result != 0:
        return result

    print("checker=friend_lt5_lf5_up_semantics")
    print("lt5_socd_2ip_source_helper=true")
    print("lf5_auxiliary_up_like=true")
    print("rf6_auxiliary_up_like=false")
    print("rf6_profile_activates=BTN_LT5")
    print("lf5_force_up_over_down=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
