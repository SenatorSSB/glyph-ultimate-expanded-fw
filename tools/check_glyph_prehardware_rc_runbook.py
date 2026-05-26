#!/usr/bin/env python3
"""Read-only structure checker for the prehardware RC runbook packet."""

from __future__ import annotations

import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNBOOK_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_prehardware_rc_runbook_2026-05-27.md"

REQUIRED_PHRASES = [
    "manual prehardware preparation only",
    "no firmware runtime change",
    "no flashing automation",
    "no push-to-device automation",
    "no result claim",
    "no preservation claim",
    "`.venv/bin/python -m platformio run -e glyph_mk6`",
    "`.pio/build/glyph_mk6/firmware.uf2`",
    "`tools/inspect_glyph_mk6_build_artifact.py`",
    "`docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`",
    "`docs/calibration/glyph_ultimate_preservation_hardware_result.md`",
    "both-held observed-only unless explicitly promoted",
    "RF5 negative remains NOT_TESTED_AMBIGUOUS",
    "preservation claims require reviewed filled result file",
]

REQUIRED_REFERENCED_FILES = [
    "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md",
    "tools/check_glyph_ultimate_preservation_hardware_result.py",
    "tools/inspect_glyph_mk6_build_artifact.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Glyph prehardware RC runbook structure and reference anchors."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_RUNBOOK_PATH),
        help=f"Runbook markdown path (default: {DEFAULT_RUNBOOK_PATH})",
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


def check_referenced_files(errors: list[str]) -> None:
    for rel_path in REQUIRED_REFERENCED_FILES:
        if not (REPO_ROOT / rel_path).exists():
            errors.append(f"missing referenced file: {rel_path}")


def main() -> int:
    args = parse_args()
    runbook_path = normalize_path(args.path)
    errors: list[str] = []

    if not runbook_path.exists():
        errors.append("runbook file does not exist")
    else:
        text = runbook_path.read_text(encoding="utf-8")
        check_required_phrases(text, errors)

    check_referenced_files(errors)

    if errors:
        print("status=FAIL")
        print(f"path={runbook_path}")
        for error in errors:
            print(f"error={error}")
        print("note=PASS means runbook structure/presence only")
        print("note=PASS must not be interpreted as hardware readiness")
        print("note=PASS must not be interpreted as firmware safety")
        print("note=PASS must not be interpreted as flashing approval")
        print("note=PASS must not be interpreted as preservation verification")
        return 1

    print("status=PASS")
    print(f"path={runbook_path}")
    print("scope=structure_presence_only")
    print("note=PASS means runbook structure/presence only")
    print("note=PASS does not mean hardware readiness")
    print("note=PASS does not mean firmware safety")
    print("note=PASS does not mean flashing approval")
    print("note=PASS does not mean preservation verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
