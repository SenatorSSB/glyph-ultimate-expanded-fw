#!/usr/bin/env python3
"""Read-only structure checker for the preservation hardware execution packet."""

from __future__ import annotations

import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET_PATH = (
    REPO_ROOT / "docs" / "calibration" / "glyph_preservation_hardware_execution_packet_2026-05-27.md"
)

REQUIRED_PHRASES = [
    "manual hardware execution preparation only",
    "no flashing automation",
    "no push-to-device automation",
    "no result claim",
    "rollback firmware/profile readiness",
    "artifact SHA-256",
    "existing result template path",
    "hardware preservation claims remain blocked",
    "both-held behavior as observed-only unless explicitly promoted",
]

REQUIRED_REFERENCED_FILES = [
    "docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
    "tools/check_glyph_ultimate_preservation_hardware_result.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Glyph preservation execution packet structure and required references."
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


def _check_phrases(text: str, errors: list[str]) -> None:
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"missing required phrase: {phrase}")


def _check_referenced_files(errors: list[str]) -> None:
    for rel in REQUIRED_REFERENCED_FILES:
        if not (REPO_ROOT / rel).exists():
            errors.append(f"missing referenced file: {rel}")


def main() -> int:
    args = parse_args()
    path = _normalize_path(args.path)

    errors: list[str] = []
    if not path.exists():
        errors.append("packet file does not exist")
    else:
        text = path.read_text(encoding="utf-8")
        _check_phrases(text, errors)

    _check_referenced_files(errors)

    if errors:
        print("status=FAIL")
        print(f"path={path}")
        for error in errors:
            print(f"error={error}")
        print("note=PASS means packet structure/presence only")
        print("note=PASS must not be interpreted as hardware readiness")
        print("note=PASS must not be interpreted as firmware safety")
        print("note=PASS must not be interpreted as preservation verification")
        return 1

    print("status=PASS")
    print(f"path={path}")
    print("scope=structure_presence_only")
    print("note=PASS means packet structure/presence only")
    print("note=PASS does not mean hardware readiness")
    print("note=PASS does not mean firmware safety")
    print("note=PASS does not mean preservation verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
