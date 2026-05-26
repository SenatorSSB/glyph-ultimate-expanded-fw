#!/usr/bin/env python3
"""Read-only structure checker for the manual hardware owner checklist."""

from __future__ import annotations

import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKLIST_PATH = (
    REPO_ROOT / "docs" / "calibration" / "glyph_manual_hardware_owner_checklist_2026-05-27.md"
)

REQUIRED_PHRASES = [
    "aggregate dry-run checker passes",
    "`tools/check_glyph_no_forbidden_artifacts.py`",
    "no tracked generated firmware/build artifacts",
    "explicitly allowlisted source/reference firmware artifacts may exist",
    "new firmware artifacts from local builds are not committed",
    "`.pio` and `.venv` may exist but must not be committed",
    "`git status --short`",
    "`.venv/bin/python -m platformio run -e glyph_mk6`",
    "`tools/inspect_glyph_mk6_build_artifact.py`",
    "record artifact path, size, SHA-256",
    "manual only",
    "no repo script performs flashing or push-to-device",
    "`docs/calibration/glyph_ultimate_preservation_hardware_result.md`",
    "ambiguous rows should stay ambiguous",
    "RF5 negative remains NOT_TESTED_AMBIGUOUS",
    "`tools/check_glyph_ultimate_preservation_hardware_result.py`",
    "do not claim preservation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Glyph manual hardware owner checklist structure and required anchors."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_CHECKLIST_PATH),
        help=f"Checklist markdown path (default: {DEFAULT_CHECKLIST_PATH})",
    )
    return parser.parse_args()


def normalize_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def check_required_phrases(text: str, errors: list[str]) -> None:
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"missing required phrase: {phrase}")


def main() -> int:
    args = parse_args()
    checklist_path = normalize_path(args.path)
    errors: list[str] = []

    if not checklist_path.exists():
        errors.append("checklist file does not exist")
    else:
        text = checklist_path.read_text(encoding="utf-8")
        check_required_phrases(text, errors)

    if errors:
        print("status=FAIL")
        print(f"path={checklist_path}")
        for error in errors:
            print(f"error={error}")
        print("note=PASS means checklist structure/presence only")
        print("note=PASS must not be interpreted as hardware readiness")
        print("note=PASS must not be interpreted as flashing approval")
        print("note=PASS must not be interpreted as preservation verification")
        return 1

    print("status=PASS")
    print(f"path={checklist_path}")
    print("scope=structure_presence_only")
    print("note=PASS means checklist structure/presence only")
    print("note=PASS does not mean hardware readiness")
    print("note=PASS does not mean flashing approval")
    print("note=PASS does not mean preservation verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
