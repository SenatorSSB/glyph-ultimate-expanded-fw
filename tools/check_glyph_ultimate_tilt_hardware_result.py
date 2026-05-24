#!/usr/bin/env python3
"""Read-only structure checker for Glyph Ultimate Tilt hardware result markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_ultimate_tilt_hardware_test_result.md"
ALLOWED_RESULT_TOKENS = ("PASS", "FAIL", "BLOCKED")
ALLOWED_DISPOSITIONS = (
    "PASS",
    "FAIL_ROLLBACK",
    "BLOCKED_NOT_FLASHED",
    "NEEDS_FIRMWARE_FIX",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate structure of a filled Glyph Ultimate Tilt hardware result markdown file.",
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_RESULT_PATH),
        help=f"result markdown path (default: {DEFAULT_RESULT_PATH})",
    )
    return parser.parse_args()


def _fail(message: str) -> None:
    raise AssertionError(message)


def _extract_table_value(text: str, field_name: str) -> str:
    pattern = re.compile(rf"^\|\s*{re.escape(field_name)}\s*\|\s*(.*?)\s*\|\s*$", flags=re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        _fail(f"missing table row for '{field_name}'")
    value = match.group(1).strip()
    if not value:
        _fail(f"empty value for '{field_name}'")
    return value


def _extract_section(text: str, heading: str) -> str:
    start_pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", flags=re.MULTILINE)
    start_match = start_pattern.search(text)
    if start_match is None:
        _fail(f"missing section heading: ## {heading}")

    next_heading_pattern = re.compile(r"^##\s+", flags=re.MULTILINE)
    next_match = next_heading_pattern.search(text, start_match.end())
    end_index = next_match.start() if next_match else len(text)
    return text[start_match.end() : end_index]


def _validate_commit_sha(commit_sha: str) -> None:
    if re.fullmatch(r"[0-9a-fA-F]{7,40}", commit_sha) is None:
        _fail(f"commit SHA malformed: {commit_sha!r}")


def _validate_artifact_sha256(artifact_sha: str) -> None:
    if re.fullmatch(r"[0-9a-fA-F]{64}", artifact_sha) is None:
        _fail("artifact SHA-256 must be 64 hex characters")


def _validate_tilt_rows(text: str) -> None:
    for tilt_name in ("Tilt1 LT1", "Tilt2 LT2"):
        for direction in range(1, 10):
            label = f"{tilt_name} direction {direction} produces expected table value"
            value = _extract_table_value(text, label)
            if not any(token in value.upper() for token in ALLOWED_RESULT_TOKENS):
                _fail(
                    f"result field for '{label}' must include one of "
                    f"{ALLOWED_RESULT_TOKENS}, got {value!r}"
                )


def _validate_rollback_fields(text: str) -> None:
    for field in (
        "Rollback needed",
        "Rollback firmware restored",
        "Rollback profile/config restored",
    ):
        _extract_table_value(text, field)


def _validate_final_disposition(text: str) -> str:
    section = _extract_section(text, "Final Disposition")
    disposition_pattern = re.compile(
        r"^\s*(?:[-*]\s*)?(?:\[[xX]\]\s*)?(PASS|FAIL_ROLLBACK|BLOCKED_NOT_FLASHED|NEEDS_FIRMWARE_FIX)\s*$",
        flags=re.MULTILINE,
    )
    matches = disposition_pattern.findall(section)
    unique_matches = sorted(set(matches))

    if len(unique_matches) != 1:
        _fail(
            "final disposition must select exactly one of "
            + ", ".join(ALLOWED_DISPOSITIONS)
        )
    return unique_matches[0]


def run(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    branch = _extract_table_value(text, "Branch")
    commit_sha = _extract_table_value(text, "Commit SHA")
    artifact_sha = _extract_table_value(text, "Artifact SHA-256")

    _validate_commit_sha(commit_sha)
    _validate_artifact_sha256(artifact_sha)
    _validate_tilt_rows(text)
    _validate_rollback_fields(text)
    disposition = _validate_final_disposition(text)

    if not branch:
        _fail("branch must be non-empty")

    return disposition


def main() -> None:
    args = parse_args()
    result_path = Path(args.path)
    if not result_path.is_absolute():
        result_path = REPO_ROOT / result_path

    if not result_path.exists():
        print("status=NO_RESULT_FILE")
        print(f"path={result_path}")
        raise SystemExit(0)

    try:
        disposition = run(result_path)
    except AssertionError as exc:
        print("status=FAIL")
        print(f"reason={exc}")
        raise SystemExit(1)

    print("status=PASS")
    print(f"path={result_path}")
    print(f"final_disposition={disposition}")


if __name__ == "__main__":
    main()
