#!/usr/bin/env python3
"""Read-only snapshot checker for native Ultimate analog static scanner output."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "tools" / "list_glyph_native_ultimate_analog_sources.py"
SNAPSHOT = REPO_ROOT / "docs" / "calibration" / "fixtures" / "native_ultimate_analog_static_snapshot.txt"

LINE_REF_RE = re.compile(r"^(-\s+[^\s:]+):\d+:(.*)$")


def _normalize(text: str) -> str:
    normalized_lines: list[str] = []
    for line in text.splitlines():
        match = LINE_REF_RE.match(line)
        if match:
            left, right = match.groups()
            normalized_lines.append(f"{left}:<line>:{right}")
        else:
            normalized_lines.append(line)
    return "\n".join(normalized_lines).strip()


def _load_snapshot() -> str:
    if not SNAPSHOT.exists():
        raise AssertionError(f"missing snapshot fixture: {SNAPSHOT}")
    return SNAPSHOT.read_text(encoding="utf-8", errors="replace")


def _run_scanner() -> str:
    result = subprocess.run(
        [sys.executable, str(SCANNER)],
        check=False,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            "scanner failed while generating comparison output:\n"
            + result.stdout
            + result.stderr
        )
    return result.stdout


def main() -> None:
    expected = _normalize(_load_snapshot())
    current = _normalize(_run_scanner())

    if expected != current:
        print("snapshot_check=FAIL")
        print("reason=normalized scanner output differs from fixture")
        raise SystemExit(1)

    print("snapshot_check=PASS")
    print("reason=normalized scanner output matches fixture")


if __name__ == "__main__":
    main()
