#!/usr/bin/env python3
"""Validate the friend-only one-shot default profile adoption path."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "glyph" / "common" / "src" / "config.cpp"
DOC_PATH = REPO_ROOT / "docs" / "calibration" / "friend_default_profile_force_once_handoff.md"

MARKER = "/friend_profile3_default_applied.flag"


def fail(message: str) -> int:
    print("status=FAIL")
    print(f"failure={message}")
    return 1


def find_balanced_block(text: str, open_brace_index: int) -> str:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index + 1 : index]

    raise ValueError("unclosed C++ block")


def find_function_body(source: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*\([^)]*\)\s*\{{", source)
    if match is None:
        raise ValueError(f"missing function: {name}")
    open_index = source.find("{", match.start())
    return find_balanced_block(source, open_index)


def main() -> int:
    try:
        source = CONFIG_PATH.read_text(encoding="utf-8")
        doc = DOC_PATH.read_text(encoding="utf-8")
        helper_body = find_function_body(source, "ApplyFriendDefaultProfileOnce")
        setup_body = find_function_body(source, "setup")
    except (OSError, ValueError) as exc:
        return fail(str(exc))

    if MARKER not in source:
        return fail("marker_filename_missing")

    if "LittleFS.exists(kFriendDefaultProfileAppliedMarker)" not in helper_body:
        return fail("marker_existence_guard_missing")

    if "persistence.SaveConfig(config)" not in helper_body:
        return fail("one_shot_save_missing")

    marker_guard_index = helper_body.find("LittleFS.exists(kFriendDefaultProfileAppliedMarker)")
    one_shot_save_index = helper_body.find("persistence.SaveConfig(config)")
    if one_shot_save_index < marker_guard_index:
        return fail("one_shot_save_precedes_marker_guard")

    if "LittleFS.open(kFriendDefaultProfileAppliedMarker, \"w\")" not in helper_body:
        return fail("marker_creation_missing")

    if "ApplyFriendDefaultProfileOnce(config);" not in setup_body:
        return fail("setup_does_not_call_one_shot_helper")

    load_index = setup_body.find("persistence.LoadConfig(config)")
    helper_call_index = setup_body.find("ApplyFriendDefaultProfileOnce(config);")
    if load_index < 0:
        return fail("load_config_missing")
    if helper_call_index < 0 or helper_call_index > load_index:
        return fail("one_shot_helper_not_before_load_config")

    fallback_pattern = re.compile(
        r"if\s*\(\s*!\s*persistence\.LoadConfig\s*\(\s*config\s*\)\s*\)\s*\{\s*"
        r"persistence\.SaveConfig\s*\(\s*config\s*\)\s*;\s*"
        r"\}",
        re.DOTALL,
    )
    if fallback_pattern.search(setup_body) is None:
        return fail("load_config_fallback_save_missing")

    setup_without_fallback = fallback_pattern.sub("", setup_body)
    if "persistence.SaveConfig(config)" in setup_without_fallback:
        return fail("setup_contains_unconditional_or_extra_save")

    if len(re.findall(r"\bpersistence\.SaveConfig\s*\(\s*config\s*\)", source)) != 2:
        return fail("unexpected_save_config_call_count")

    doc_lower = doc.lower()
    for snippet in (
        "old LittleFS config.bin survived flashing",
        "first boot overwrites saved config with baked compiled default",
        "marker prevents repeated overwrites",
        "friend-branch only",
        "must not be merged to configurator",
        "no flashing automation added",
        "no Tilt/Tilt2 runtime formulas changed",
    ):
        if snippet.lower() not in doc_lower:
            return fail(f"handoff_missing_snippet:{snippet}")

    print("status=PASS")
    print(f"target={CONFIG_PATH.relative_to(REPO_ROOT)}")
    print(f"marker={MARKER}")
    print("one_shot_save_before_load=true")
    print("normal_load_fallback_preserved=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
