#!/usr/bin/env python3
"""Validate the committed static Glyph checker census without executing checks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from generate_glyph_checker_census import ARTIFACT, SCHEMA_VERSION, generate, rendered  # noqa: E402


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main() -> int:
    try:
        committed_text = ARTIFACT.read_text(encoding="utf-8")
        committed = json.loads(committed_text, object_pairs_hook=pairs)
        expected = generate()
        entries = committed.get("entries")
        if not isinstance(entries, list) or committed.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("invalid census schema")
        ids = [item.get("checker_id") for item in entries if isinstance(item, dict)]
        paths = [item.get("path") for item in entries if isinstance(item, dict)]
        if len(ids) != len(entries) or len(ids) != len(set(ids)):
            raise ValueError("duplicate or invalid checker ID")
        if len(paths) != len(entries) or len(paths) != len(set(paths)):
            raise ValueError("duplicate or invalid checker path")
        if paths != sorted(paths):
            raise ValueError("census paths are not in canonical order")
        if any(item.get("parse_error") for item in entries):
            raise ValueError("syntax-invalid checker recorded in census")
        if committed_text != rendered(expected):
            raise ValueError("artifact drift; run tools/generate_glyph_checker_census.py")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"glyph_checker_census: FAIL: {exc}")
        return 1
    print(f"glyph_checker_census: PASS; entries={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
