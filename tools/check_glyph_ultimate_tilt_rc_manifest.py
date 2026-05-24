#!/usr/bin/env python3
"""Read-only checker for the Glyph Ultimate Tilt RC manifest markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_REL = Path("docs/calibration/glyph_ultimate_tilt_rc_manifest.md")
DEFAULT_MANIFEST_PATH = REPO_ROOT / DEFAULT_MANIFEST_REL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate structure and required fields in the Glyph Ultimate Tilt RC manifest.",
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_MANIFEST_REL),
        help=f"manifest path (default: {DEFAULT_MANIFEST_REL.as_posix()})",
    )
    return parser.parse_args()


def _fail(message: str) -> None:
    raise AssertionError(message)


def _require(pattern: str, text: str, label: str) -> None:
    if re.search(pattern, text, flags=re.MULTILINE) is None:
        _fail(f"missing {label}")


def _extract_scalar(field: str, text: str) -> str:
    match = re.search(rf"^\s*-\s*{re.escape(field)}:\s*(.+)\s*$", text, flags=re.MULTILINE)
    if match is None:
        _fail(f"missing {field}")
    return match.group(1).strip()


def _resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _validate_sha256_values(text: str) -> None:
    matches = re.findall(r"artifact_\d+_sha256:\s*`([^`]+)`", text)
    for value in matches:
        if re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
            _fail(f"artifact SHA-256 malformed: {value!r}")


def run(path: Path) -> None:
    if not path.exists():
        _fail(f"manifest not found: {path}")
    text = path.read_text(encoding="utf-8")

    _require(r"^#\s+Glyph Ultimate Tilt RC Manifest\s*$", text, "title")
    _require(
        r"manifest_generated_from_branch:\s*`[^`]+`",
        text,
        "manifest_generated_from_branch",
    )
    _require(
        r"firmware_source_commit_sha:\s*`[0-9a-fA-F]{40}`",
        text,
        "firmware_source_commit_sha",
    )
    _require(r"manifest_generation_note:\s*.+", text, "manifest_generation_note")
    _require(r"^##\s+Artifact Candidates\s*$", text, "artifact section")
    _require(r"artifact_status:\s*(FOUND|MISSING)", text, "artifact status")
    _require(r"hardware_test_status:\s*NOT_TESTED", text, "hardware test status NOT_TESTED")
    _require(r"flashing_automation:\s*NOT_INCLUDED", text, "flashing automation NOT_INCLUDED")
    _require(r"git_dirty_state:\s*(CLEAN|DIRTY)", text, "git_dirty_state")
    _require(
        r"firmware_relevant_dirty_state:\s*(CLEAN|DIRTY)",
        text,
        "firmware_relevant_dirty_state",
    )
    _require(r"^##\s+Tilt Input Summary\s*$", text, "Tilt input summary section")
    _require(r"inputs\.lt1", text, "Tilt1 logical input summary")
    _require(r"inputs\.lt2", text, "Tilt2 logical input summary")
    _require(r"^##\s+Verification Commands\s*$", text, "verification commands section")

    git_dirty_state = _extract_scalar("git_dirty_state", text)
    firmware_relevant_dirty_state = _extract_scalar("firmware_relevant_dirty_state", text)

    if git_dirty_state not in {"CLEAN", "DIRTY"}:
        _fail(f"git_dirty_state must be CLEAN or DIRTY, got {git_dirty_state!r}")
    if firmware_relevant_dirty_state not in {"CLEAN", "DIRTY"}:
        _fail(
            "firmware_relevant_dirty_state must be CLEAN or DIRTY, "
            f"got {firmware_relevant_dirty_state!r}"
        )
    if firmware_relevant_dirty_state == "DIRTY":
        _fail("firmware_relevant_dirty_state must be CLEAN for RC validation")

    _validate_sha256_values(text)


def main() -> int:
    args = parse_args()
    path = _resolve_path(args.path)

    try:
        run(path)
    except AssertionError as exc:
        print(f"glyph_ultimate_tilt_rc_manifest: FAIL {exc}")
        return 1

    try:
        display_path = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        display_path = str(path)
    print(f"glyph_ultimate_tilt_rc_manifest: PASS {display_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
