#!/usr/bin/env python3
"""Validate Glyph Ultimate preservation hardware result structure.

The real result file is intentionally absent before hardware testing. In that
prehardware state this checker reports NO_RESULT_FILE and exits successfully.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT = REPO_ROOT / "docs" / "calibration" / "glyph_ultimate_preservation_hardware_result.md"
TEMPLATE = REPO_ROOT / "docs" / "calibration" / "glyph_ultimate_preservation_hardware_result_TEMPLATE.md"
ALLOWED_DISPOSITIONS = {"PASS", "FAIL_ROLLBACK", "BLOCKED_NOT_TESTED", "NEEDS_FIRMWARE_FIX"}
REQUIRED_IDS = [f"UPRES-{index:03d}" for index in range(1, 13)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Ultimate preservation hardware result markdown.")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT, help="Path to real result markdown.")
    return parser.parse_args()


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def extract_final_disposition(text: str) -> str | None:
    match = re.search(r"final_disposition\s*:\s*`?([A-Z_]+)`?", text)
    return match.group(1) if match else None


def main() -> int:
    args = parse_args()
    result_path = args.result if args.result.is_absolute() else REPO_ROOT / args.result

    if not result_path.exists():
        template_state = "present" if TEMPLATE.exists() else "missing"
        print("glyph_ultimate_preservation_hardware_result")
        print("status=NO_RESULT_FILE")
        print(f"result_path={display(result_path)}")
        print(f"template={template_state}:{display(TEMPLATE)}")
        print("hardware_verified=false")
        return 0

    text = result_path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "TEMPLATE_ONLY" in text:
        errors.append("real result file must not be template-only")

    for test_id in REQUIRED_IDS:
        if test_id not in text:
            errors.append(f"missing required test id: {test_id}")

    disposition = extract_final_disposition(text)
    if disposition is None:
        errors.append("missing final_disposition")
    elif disposition not in ALLOWED_DISPOSITIONS:
        errors.append(
            "invalid final_disposition: "
            f"{disposition}; allowed={','.join(sorted(ALLOWED_DISPOSITIONS))}",
        )

    print("glyph_ultimate_preservation_hardware_result")
    print(f"status={'FAIL' if errors else 'PASS'}")
    print(f"result_path={display(result_path)}")
    print(f"final_disposition={disposition if disposition else '<missing>'}")
    print("hardware_verified=true")
    if errors:
        print("errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
