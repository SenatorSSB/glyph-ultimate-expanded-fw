#!/usr/bin/env python3
"""Read-only checker for Glyph Ultimate preservation hardware result markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_ultimate_preservation_hardware_result.md"
ALLOWED_FINAL_DISPOSITIONS = {
    "PASS",
    "FAIL_ROLLBACK",
    "BLOCKED_NOT_TESTED",
    "NEEDS_FIRMWARE_FIX",
}

REQUIRED_HEADINGS = [
    "## 1. Test Identity And Setup",
    "## 2. Baseline No-Modifier Checks",
    "## 3. Existing Tilt/Tilt2 Preservation",
    "## 4. C-Stick/Right-Stick Preservation",
    "## 5. Trigger Preservation",
    "## 6. SOCD/Opposite Direction Behavior",
    "## 7. RF5 Physical Identity / Negative Check",
    "## 8. Profile Preservation / Readback",
    "## 9. Optional Nunchuk",
    "## 10. Basic Button Regression",
    "## 11. Result Disposition",
]

REQUIRED_IDENTITY_FIELDS = [
    "Branch tested",
    "Commit SHA tested",
    "Firmware artifact path",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Glyph Ultimate preservation hardware result structure.")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_RESULT_PATH),
        help=f"Result markdown path (default: {DEFAULT_RESULT_PATH})",
    )
    return parser.parse_args()


def _extract_table_field(text: str, field_name: str) -> str | None:
    pattern = re.compile(rf"^\|\s*{re.escape(field_name)}\s*\|\s*(.*?)\s*\|\s*$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(1).strip()


def _extract_final_disposition(text: str) -> str | None:
    line_match = re.search(r"^final_disposition\s*:\s*`?([A-Z_]+)`?\s*$", text, re.MULTILINE)
    if line_match:
        return line_match.group(1)

    section_match = re.search(
        r"##\s+11\.\s+Result Disposition\n(?P<body>[\s\S]*)",
        text,
        re.MULTILINE,
    )
    if not section_match:
        return None

    checked = re.findall(r"^\s*[-*]\s*\[[xX]\]\s*([A-Z_]+)\s*$", section_match.group("body"), re.MULTILINE)
    unique = sorted(set(checked))
    if len(unique) == 1:
        return unique[0]
    return None


def _is_template_only(text: str) -> bool:
    return "TEMPLATE_ONLY" in text


def _validate_section_presence(text: str, errors: list[str]) -> None:
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")


def _validate_required_sections(text: str, errors: list[str]) -> None:
    required_section_keywords = {
        "RF5 section": "## 7. RF5 Physical Identity / Negative Check",
        "C-stick/right-stick section": "## 4. C-Stick/Right-Stick Preservation",
        "Trigger section": "## 5. Trigger Preservation",
        "SOCD section": "## 6. SOCD/Opposite Direction Behavior",
        "Profile preservation section": "## 8. Profile Preservation / Readback",
    }
    for label, heading in required_section_keywords.items():
        if heading not in text:
            errors.append(f"missing {label}")


def _validate_identity_fields(text: str, errors: list[str]) -> None:
    for field in REQUIRED_IDENTITY_FIELDS:
        value = _extract_table_field(text, field)
        if value is None:
            errors.append(f"missing required field: {field}")
            continue
        if not value:
            errors.append(f"empty required field: {field}")


def _validate_final_disposition(text: str, errors: list[str]) -> str | None:
    disposition = _extract_final_disposition(text)
    if disposition is None:
        errors.append("missing final_disposition")
        return None
    if disposition not in ALLOWED_FINAL_DISPOSITIONS:
        allowed = ", ".join(sorted(ALLOWED_FINAL_DISPOSITIONS))
        errors.append(f"invalid final_disposition: {disposition}; allowed={allowed}")
    return disposition


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.is_absolute():
        path = REPO_ROOT / path

    if not path.exists():
        print("status=NO_RESULT_FILE")
        print(f"path={path}")
        return 0

    text = path.read_text(encoding="utf-8")
    template_only = _is_template_only(text)

    errors: list[str] = []
    _validate_section_presence(text, errors)
    _validate_required_sections(text, errors)

    disposition: str | None = None
    if not template_only:
        _validate_identity_fields(text, errors)
        disposition = _validate_final_disposition(text, errors)

    if errors:
        print("status=FAIL")
        print(f"path={path}")
        print(f"template_only={'true' if template_only else 'false'}")
        for error in errors:
            print(f"error={error}")
        return 1

    if template_only:
        print("status=TEMPLATE_ONLY")
        print(f"path={path}")
        print("template_only=true")
        return 0

    print("status=PASS")
    print(f"path={path}")
    print(f"final_disposition={disposition}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
