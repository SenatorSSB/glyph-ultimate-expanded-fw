#!/usr/bin/env python3
"""Read-only scope checker for future Glyph Ultimate tilt runtime patch branches."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "configurator"

DEFAULT_ALLOW_PREFIXES = ("docs/calibration/", "tools/")
DEFAULT_ALLOW_EXACT = ("src/modes/Ultimate.cpp",)

DOCS_ONLY_ALLOW_PREFIXES = ("docs/", "tools/")

SOCD_RE = re.compile(r"(^|/|_)(socd)(/|_|\.|$)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether changed files stay within expected future tilt patch scope.",
    )
    parser.add_argument(
        "--base",
        default=DEFAULT_BASE,
        help=f"base ref for git diff comparison (default: {DEFAULT_BASE})",
    )
    parser.add_argument(
        "--mode",
        choices=("default", "docs-only"),
        default="default",
        help="scope mode: default (future runtime patch) or docs-only",
    )
    parser.add_argument(
        "--allow-docs-tools-only",
        action="store_true",
        help="alias for --mode docs-only",
    )
    return parser.parse_args()


def run_git_diff_name_only(base_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        check=False,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("status=FAIL")
        print(f"reason=git diff failed for base ref {base_ref!r}")
        stderr = result.stderr.strip()
        if stderr:
            print(f"git_stderr={stderr}")
        raise SystemExit(2)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_allowed(path: str, mode: str) -> bool:
    if mode == "docs-only":
        return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in DOCS_ONLY_ALLOW_PREFIXES)
    if path in DEFAULT_ALLOW_EXACT:
        return True
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in DEFAULT_ALLOW_PREFIXES)


def collect_special_path_flags(path: str) -> list[str]:
    flags: list[str] = []
    normalized = path.replace("\\", "/")

    if normalized in {
        "platformio.ini",
        "config/glyph/env.ini",
        "config/glyph/common/include/glyph_overrides.hpp",
        "src/core/InputMode.cpp",
        "src/core/ControllerMode.cpp",
    }:
        flags.append("explicit-risk-path")

    if normalized.startswith("proto/generated/"):
        flags.append("proto-generated-config")

    if SOCD_RE.search(normalized):
        flags.append("socd-related-path")

    if (
        normalized.startswith("persistence/")
        or normalized.startswith("configurator/")
        or normalized.startswith("backend/")
        or "/persistence/" in normalized
        or "/configurator/" in normalized
        or "/backend/" in normalized
    ):
        flags.append("persistence-configurator-backend-path")

    if normalized == ".DS_Store" or normalized.endswith("/.DS_Store"):
        flags.append("artifact-ds-store")

    if normalized == ".venv" or normalized.startswith(".venv/") or "/.venv/" in normalized:
        flags.append("artifact-venv")

    return flags


def main() -> None:
    args = parse_args()
    mode = "docs-only" if args.allow_docs_tools_only else args.mode
    changed_files = run_git_diff_name_only(args.base)

    disallowed = [path for path in changed_files if not is_allowed(path, mode)]
    flagged: list[tuple[str, list[str]]] = []
    forbidden_artifacts: list[str] = []

    for path in changed_files:
        reasons = collect_special_path_flags(path)
        if reasons:
            flagged.append((path, reasons))
            if "artifact-ds-store" in reasons or "artifact-venv" in reasons:
                forbidden_artifacts.append(path)

    print(f"mode={mode}")
    print(f"base={args.base}")
    print(f"changed_file_count={len(changed_files)}")
    print("changed_files:")
    if changed_files:
        for path in changed_files:
            print(f"- {path}")
    else:
        print("- <none>")

    if flagged:
        print(f"special_flags={len(flagged)}")
        for path, reasons in flagged:
            print(f"- {path}: {', '.join(reasons)}")

    if disallowed:
        print(f"disallowed_file_count={len(disallowed)}")
        for path in disallowed:
            print(f"- {path}")

    if forbidden_artifacts:
        print("status=FAIL")
        print("reason=forbidden artifact paths detected (.DS_Store/.venv)")
        raise SystemExit(2)

    if disallowed or flagged:
        print("status=WARN")
        print("reason=scope includes non-allowlisted or risk-flagged paths")
        raise SystemExit(1)

    print("status=PASS")
    print("reason=all changed files are allowlisted and no forbidden artifact paths were found")


if __name__ == "__main__":
    main()
