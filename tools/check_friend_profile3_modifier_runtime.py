#!/usr/bin/env python3
"""Validate final friend Profile 3 modifier runtime wiring."""

from __future__ import annotations

from check_friend_profile3_final_layout import main as check_final_layout


def main() -> int:
    result = check_final_layout()
    if result != 0:
        return result

    print("checker=friend_profile3_modifier_runtime")
    print("x1_input=LT4")
    print("y1_input=LT3")
    print("tilt_input=RF4")
    print("tilt2_input=RF3")
    print("tilt3_input=RF4+RF3")
    print("x1_up_right_raw=158,195")
    print("y1_up_right_raw=195,156")
    print("x1_y1_up_right_raw=158,156")
    print("tilt2_flipper_up_right_raw=69,168")
    print("tilt2_flipper_left_up_raw=187,168")
    print("tilt3_rf4_rf3_up_right_raw=164,172")
    print("standalone_r_input=LF8")
    print("start_input=MB7")
    print("one_shot_default_profile_marker=friend_profile3_final_faifra_layout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
