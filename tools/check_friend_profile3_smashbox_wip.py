#!/usr/bin/env python3
"""Compatibility entry point for the final friend Profile 3 Faifra layout checker."""

from __future__ import annotations

from check_friend_profile3_final_layout import main as check_final_layout


def main() -> int:
    result = check_final_layout()
    if result != 0:
        return result

    print("checker=friend_profile3_smashbox_wip")
    print("superseded_by=friend_profile3_final_faifra_layout")
    print("wip_identity_fixture_target=false")
    print("final_friend_layout=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
