#!/usr/bin/env python3
"""Inspect likely local glyph_mk6 build artifacts and print checksums.

This helper is intentionally read-only. It locates candidate firmware artifacts
from local PlatformIO build output and does not flash, copy, or mutate files.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_SUFFIXES = (".uf2", ".bin", ".elf", ".hex")
LIKELY_BUILD_DIRS = (
    REPO_ROOT / ".pio" / "build" / "glyph_mk6",
)


def _repo_display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_artifacts() -> list[Path]:
    artifacts: list[Path] = []
    for build_dir in LIKELY_BUILD_DIRS:
        if not build_dir.is_dir():
            continue
        for path in build_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in ARTIFACT_SUFFIXES:
                artifacts.append(path)
    return sorted(artifacts, key=lambda path: _repo_display_path(path))


def _print_missing_artifact() -> None:
    print("glyph_mk6_build_artifact_inspection")
    print("status: missing-artifact")
    print("blocked: no local glyph_mk6 firmware artifact was found")
    print("searched:")
    for build_dir in LIKELY_BUILD_DIRS:
        print(f"- {_repo_display_path(build_dir)}")
    print("candidate_suffixes:")
    for suffix in ARTIFACT_SUFFIXES:
        print(f"- {suffix}")


def _print_artifacts(artifacts: list[Path]) -> None:
    print("glyph_mk6_build_artifact_inspection")
    print("status: ok")
    for artifact in artifacts:
        stat = artifact.stat()
        print(f"artifact: {_repo_display_path(artifact)}")
        print(f"size_bytes: {stat.st_size}")
        print(f"sha256: {_sha256(artifact)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect local glyph_mk6 build artifacts and print sha256 checksums.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when no candidate build artifact is found.",
    )
    args = parser.parse_args()

    artifacts = _find_artifacts()
    if not artifacts:
        _print_missing_artifact()
        return 2 if args.strict else 0

    _print_artifacts(artifacts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
