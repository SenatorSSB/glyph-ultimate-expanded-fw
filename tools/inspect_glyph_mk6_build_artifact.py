#!/usr/bin/env python3
"""Read-only inspector for the glyph_mk6 UF2 build artifact."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_PATH = REPO_ROOT / ".pio" / "build" / "glyph_mk6" / "firmware.uf2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a glyph_mk6 UF2 artifact path.")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_ARTIFACT_PATH),
        help=f"Artifact path (default: {DEFAULT_ARTIFACT_PATH})",
    )
    return parser.parse_args()


def normalize_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    artifact_path = normalize_path(args.path)

    if not artifact_path.exists():
        print("status=NO_ARTIFACT")
        print(f"path={artifact_path}")
        print("note=build with `.venv/bin/python -m platformio run -e glyph_mk6` to create artifact")
        return 0

    if not artifact_path.is_file():
        print("status=FAIL")
        print(f"path={artifact_path}")
        print("error=path exists but is not a file")
        return 1

    try:
        size_bytes = artifact_path.stat().st_size
        sha256 = file_sha256(artifact_path)
    except OSError as exc:
        print("status=FAIL")
        print(f"path={artifact_path}")
        print(f"error=unable to read artifact: {exc}")
        return 1

    print("status=FOUND")
    print(f"path={artifact_path}")
    print(f"size_bytes={size_bytes}")
    print(f"sha256={sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
