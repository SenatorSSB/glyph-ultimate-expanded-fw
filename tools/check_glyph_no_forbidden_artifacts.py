#!/usr/bin/env python3
"""Read-only checker for forbidden generated/build artifacts in git state."""

from __future__ import annotations

from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_COMPONENTS = {".venv", ".pio", "__pycache__"}
FORBIDDEN_EXTENSIONS = {".pyc", ".pyo", ".uf2", ".elf", ".map"}
FORBIDDEN_FILENAMES = {"firmware.uf2", "firmware.bin"}
ALLOWED_TRACKED_SOURCE_ARTIFACTS = {
    "docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2",
    "docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2",
}


def normalize_git_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def git_ls_files(args: list[str]) -> list[str]:
    command = ["git", *args]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise RuntimeError(f"{' '.join(command)}: {detail}")
    return [normalize_git_path(line) for line in completed.stdout.splitlines() if line.strip()]


def is_forbidden_generated_path(path: str) -> bool:
    normalized = normalize_git_path(path)
    components = [component for component in normalized.split("/") if component]
    if any(component in FORBIDDEN_COMPONENTS for component in components):
        return True

    filename = components[-1].lower() if components else normalized.lower()
    if filename in FORBIDDEN_FILENAMES:
        return True

    return Path(filename).suffix.lower() in FORBIDDEN_EXTENSIONS


def is_allowed_tracked_source_artifact(path: str) -> bool:
    return normalize_git_path(path) in ALLOWED_TRACKED_SOURCE_ARTIFACTS


def tracked_forbidden_paths(paths: list[str]) -> list[str]:
    return [
        path
        for path in paths
        if is_forbidden_generated_path(path) and not is_allowed_tracked_source_artifact(path)
    ]


def tracked_allowed_source_artifact_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if is_allowed_tracked_source_artifact(path)]


def print_notes() -> None:
    print("note=PASS does not mean hardware readiness")
    print("note=PASS does not mean firmware safety")
    print("note=PASS does not mean flashing approval")
    print("note=PASS does not mean preservation verification")


def main() -> int:
    try:
        tracked_files = git_ls_files(["ls-files"])
        untracked_files = git_ls_files(["ls-files", "--others", "--exclude-standard"])
    except (FileNotFoundError, RuntimeError) as exc:
        print("status=FAIL")
        print("tracked_forbidden_count=0")
        print("tracked_allowed_source_artifact_count=0")
        print("untracked_generated_count=0")
        print(f"error=unable to inspect git file state: {exc}")
        print_notes()
        return 1

    tracked_forbidden = tracked_forbidden_paths(tracked_files)
    tracked_allowed_source_artifacts = tracked_allowed_source_artifact_paths(tracked_files)
    untracked_generated = [path for path in untracked_files if is_forbidden_generated_path(path)]

    print("status=FAIL" if tracked_forbidden else "status=PASS")

    print(f"tracked_forbidden_count={len(tracked_forbidden)}")
    for path in tracked_forbidden:
        print(f"tracked_forbidden_path={path}")

    print(f"tracked_allowed_source_artifact_count={len(tracked_allowed_source_artifacts)}")
    for path in tracked_allowed_source_artifacts:
        print(f"tracked_allowed_source_artifact={path}")

    print(f"untracked_generated_count={len(untracked_generated)}")
    for path in untracked_generated:
        print(f"warning=untracked_generated_path={path}")

    if untracked_generated:
        print("warning=untracked artifacts must not be committed")

    print_notes()
    return 1 if tracked_forbidden else 0


if __name__ == "__main__":
    raise SystemExit(main())
