#!/usr/bin/env python3
"""Superseded RF12 checker for the final friend Faifra layout."""

from __future__ import annotations

from check_friend_profile3_final_layout import main as check_final_layout


def main() -> int:
    result = check_final_layout()
    if result != 0:
        return result

    print("checker=friend_rf12_force_up_smash")
    print("superseded_by=friend_profile3_final_faifra_layout")
    print("old_rf12_force_up_smash=false")
    print("lt2=forced_up_plus_a")
    print("rf12=a_plus_b")
    print("rf12_x2=false")
    print("rf15_x2=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
