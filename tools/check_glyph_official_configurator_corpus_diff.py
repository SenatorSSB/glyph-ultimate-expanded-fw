#!/usr/bin/env python3
"""Validate the official Glyph configurator corpus structural diff packet."""

from __future__ import annotations

import json

from glyph_official_configurator_corpus import (
    CORPUS_ID,
    DIFF_DOC_PATH,
    DIFF_FIXTURE_PATH,
    CorpusError,
    compute_structural_diff,
    load_json_object,
)


def fail(message: str) -> None:
    raise CorpusError(message)


def validate_doc(payload: dict[str, object]) -> None:
    if not DIFF_DOC_PATH.exists():
        fail("missing diff Markdown doc")
    text = DIFF_DOC_PATH.read_text(encoding="utf-8")
    required_phrases = [
        "structural JSON evidence, not gameplay semantics",
        "does not claim runtime behavior",
        "does not approve device write",
        "does not approve adapter implementation",
        "Stable top-level key set: true",
        "Changed top-level keys: `gameModeConfigs`, `rgbConfigs`",
        "`Ultimate` / `MODE_ULTIMATE`",
        "`Brawl` / `MODE_PROJECT_M`",
        "`Keyboard` / `MODE_KEYBOARD`",
        "Partial button-color entries are detected structurally",
    ]
    for phrase in required_phrases:
        if phrase.lower() not in text.lower():
            fail(f"diff doc missing required phrase: {phrase}")

    changed_keys = payload.get("changed_top_level_keys")
    if changed_keys != ["gameModeConfigs", "rgbConfigs"]:
        fail("changed_top_level_keys must match recomputed official corpus diff")


def main() -> int:
    print("glyph_official_configurator_corpus_diff")
    try:
        committed = load_json_object(DIFF_FIXTURE_PATH)
        recomputed = compute_structural_diff()
        if committed != recomputed:
            fail("committed diff fixture does not match recomputed structural diff")
        validate_doc(committed)
    except (CorpusError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print(f"corpus_id={CORPUS_ID}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"corpus_id={CORPUS_ID}")
    print("top_level_keys_stable=true")
    print("changed_top_level_keys=gameModeConfigs,rgbConfigs")
    print("structural_json_evidence=true")
    print("device_write_approved=false")
    print("adapter_implementation_approved=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
