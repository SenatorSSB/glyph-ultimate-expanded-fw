#!/usr/bin/env python3
"""Read-only structure checker for the Glyph user requirements input packet."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_user_requirements_input_packet_2026-05-27.md"

REQUIRED_SECTIONS = [
    "Current Confirmed Facts (Pre-Filled Only)",
    "Required Input Sections",
    "Desired physical buttons and printed/base IDs",
    "Desired logical roles",
    "Desired modifier names visible to user",
    "Exact 9-way raw coordinate tables for each modifier, if any",
    "Neutral behavior",
    "Both-held/chord behavior",
    "Conflict/exclusivity policy",
    "Preservation expectations",
    "Test matrix owner and hardware readiness",
    "Export/profile adapter expectations",
    "Disabled-remap policy: omitted activates vs explicit BTN_UNSPECIFIED",
    "Blocker Rule",
]

REQUIRED_FACT_PHRASES = [
    "RF3 -> logical LT1 -> Tilt1/TILT",
    "RF4 -> logical LT2 -> Tilt2",
    "RF5` printed/base location is now known",
    "NOT_TESTED_AMBIGUOUS",
]

BLOCKER_STATEMENT_PHRASES = [
    "blank/unfilled fields are blockers, not defaults",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Glyph user requirements packet structure and required prefilled anchors."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_PACKET_PATH),
        help=f"Packet markdown path (default: {DEFAULT_PACKET_PATH})",
    )
    return parser.parse_args()


def _normalize_path(input_path: str) -> Path:
    path = Path(input_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _check_required_sections(text: str, errors: list[str]) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing required section heading/anchor: {section}")


def _check_prefilled_facts(text: str, errors: list[str]) -> None:
    for phrase in REQUIRED_FACT_PHRASES:
        if phrase not in text:
            errors.append(f"missing required prefilled fact anchor: {phrase}")


def _check_blocker_statement(text: str, errors: list[str]) -> None:
    for phrase in BLOCKER_STATEMENT_PHRASES:
        if phrase not in text:
            errors.append(f"missing blocker statement phrase: {phrase}")


def _check_completion_boxes(text: str, errors: list[str]) -> None:
    unchecked = re.findall(r"^\s*-\s*\[\s\]\s+completed\s*$", text, flags=re.MULTILINE)
    checked = re.findall(r"^\s*-\s*\[[xX]\]\s+completed\s*$", text, flags=re.MULTILINE)

    if not unchecked:
        errors.append("missing unchecked completion boxes ('- [ ] completed')")
    if checked:
        errors.append("found pre-checked completion boxes ('- [x] completed')")


def main() -> int:
    args = parse_args()
    path = _normalize_path(args.path)

    if not path.exists():
        print("status=FAIL")
        print(f"path={path}")
        print("error=packet file does not exist")
        print("note=PASS means structure/presence only")
        print("note=PASS does not mean runtime readiness")
        return 1

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    _check_required_sections(text, errors)
    _check_prefilled_facts(text, errors)
    _check_blocker_statement(text, errors)
    _check_completion_boxes(text, errors)

    if errors:
        print("status=FAIL")
        print(f"path={path}")
        for error in errors:
            print(f"error={error}")
        print("note=PASS means structure/presence only")
        print("note=PASS does not mean runtime readiness")
        print("note=this checker does not decide whether user requirements are complete")
        print("note=this checker does not infer or create defaults")
        return 1

    print("status=PASS")
    print(f"path={path}")
    print("scope=structure_presence_only")
    print("note=PASS means structure/presence only")
    print("note=PASS does not mean runtime readiness")
    print("note=this checker does not decide whether user requirements are complete")
    print("note=this checker does not infer or create defaults")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
