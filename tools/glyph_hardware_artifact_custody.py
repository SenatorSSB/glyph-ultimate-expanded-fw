#!/usr/bin/env python3
"""Preserve and verify exact Glyph hardware-test UF2 artifacts locally."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CUSTODY_ROOT = REPO_ROOT / "local_backups" / "hardware-artifacts"
FILENAME = "firmware.uf2"
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CustodyError(ValueError):
    """Raised when artifact custody cannot be proven without mutation."""


def require_candidate_sha(value: str) -> str:
    if not GIT_SHA_RE.fullmatch(value):
        raise CustodyError("candidate Git SHA must be 40 lowercase hexadecimal characters")
    return value


def require_artifact_sha256(value: str) -> str:
    if not SHA256_RE.fullmatch(value):
        raise CustodyError("artifact SHA-256 must be 64 lowercase hexadecimal characters")
    return value


def require_local_commit(candidate_sha: str, repo_root: Path = REPO_ROOT) -> None:
    candidate_sha = require_candidate_sha(candidate_sha)
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{candidate_sha}^{{commit}}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise CustodyError("candidate Git SHA is not an available local commit")


def require_clean_candidate_checkout(candidate_sha: str, repo_root: Path = REPO_ROOT) -> None:
    require_local_commit(candidate_sha, repo_root)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True,
        text=True, check=False,
    )
    if head.returncode or head.stdout.strip() != candidate_sha:
        raise CustodyError("preserve candidate must equal the checked-out HEAD")
    status_result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if status_result.returncode or status_result.stdout:
        raise CustodyError("preserve requires a clean candidate checkout")


def _ensure_real_directory(path: Path) -> None:
    """Create a directory without accepting a symlink at any created component."""
    absolute = path.absolute()
    missing: list[Path] = []
    cursor = absolute
    while not cursor.exists():
        missing.append(cursor)
        parent = cursor.parent
        if parent == cursor:
            raise CustodyError("custody root has no existing real ancestor")
        cursor = parent
    if cursor.is_symlink() or not cursor.is_dir():
        raise CustodyError("custody path ancestor must be a real directory")
    for component in reversed(missing):
        try:
            component.mkdir()
        except FileExistsError:
            pass
        mode = component.lstat().st_mode
        if not stat.S_ISDIR(mode) or component.is_symlink():
            raise CustodyError("custody path component must be a real directory")
    cursor = absolute
    while cursor != cursor.parent:
        mode = cursor.lstat().st_mode
        if not stat.S_ISDIR(mode) or cursor.is_symlink():
            raise CustodyError("custody path component must be a real directory")
        if cursor == absolute.anchor:
            break
        cursor = cursor.parent


def custody_path(root: Path, candidate_sha: str, artifact_sha256: str) -> Path:
    candidate_sha = require_candidate_sha(candidate_sha)
    artifact_sha256 = require_artifact_sha256(artifact_sha256)
    return root / candidate_sha / artifact_sha256 / FILENAME


def _hash_open_regular(path: Path) -> tuple[str, int]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise CustodyError(f"artifact is unavailable or not safely openable: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise CustodyError("artifact must be a regular file")
        digest = hashlib.sha256()
        size = 0
        while True:
            block = os.read(fd, 1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
        after = os.fstat(fd)
        identity = lambda value: (
            value.st_dev, value.st_ino, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns,
        )
        if identity(before) != identity(after) or size != after.st_size:
            raise CustodyError("artifact changed while it was being hashed")
        return digest.hexdigest(), size
    finally:
        os.close(fd)


def verify_preserved(
    root: Path,
    candidate_sha: str,
    artifact_sha256: str,
) -> tuple[Path, int]:
    target = custody_path(root, candidate_sha, artifact_sha256)
    _ensure_real_directory(root)
    relative_parent = target.parent.relative_to(root)
    cursor = root
    for component in relative_parent.parts:
        cursor = cursor / component
        if not cursor.exists():
            raise CustodyError("preserved artifact is missing")
        mode = cursor.lstat().st_mode
        if not stat.S_ISDIR(mode) or cursor.is_symlink():
            raise CustodyError("custody path contains a symlink or non-directory")
    observed, size = _hash_open_regular(target)
    if observed != artifact_sha256:
        raise CustodyError("preserved artifact hash does not match its content-addressed path")
    return target, size


def preserve(
    source: Path,
    candidate_sha: str,
    root: Path = DEFAULT_CUSTODY_ROOT,
) -> tuple[Path, str, int, str]:
    candidate_sha = require_candidate_sha(candidate_sha)
    source_sha256, source_size = _hash_open_regular(source)
    target = custody_path(root, candidate_sha, source_sha256)
    _ensure_real_directory(target.parent)

    if target.exists() or target.is_symlink():
        verified_target, verified_size = verify_preserved(root, candidate_sha, source_sha256)
        if verified_size != source_size:
            raise CustodyError("existing artifact size differs from source")
        return verified_target, source_sha256, source_size, "ALREADY_PRESENT_VERIFIED"

    stage_fd, stage_name = tempfile.mkstemp(prefix=".firmware.uf2.", dir=target.parent)
    stage = Path(stage_name)
    try:
        source_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            source_flags |= os.O_NOFOLLOW
        source_fd = os.open(source, source_flags)
        try:
            source_before = os.fstat(source_fd)
            if not stat.S_ISREG(source_before.st_mode):
                raise CustodyError("source artifact must be a regular file")
            copied_hash = hashlib.sha256()
            copied_size = 0
            while True:
                block = os.read(source_fd, 1024 * 1024)
                if not block:
                    break
                view = memoryview(block)
                while view:
                    written = os.write(stage_fd, view)
                    if written <= 0:
                        raise CustodyError("failed to write complete staged artifact")
                    view = view[written:]
                copied_hash.update(block)
                copied_size += len(block)
            source_after = os.fstat(source_fd)
            source_identity = lambda value: (
                value.st_dev, value.st_ino, value.st_size,
                value.st_mtime_ns, value.st_ctime_ns,
            )
            if source_identity(source_before) != source_identity(source_after):
                raise CustodyError("source artifact changed during preservation")
        finally:
            os.close(source_fd)
        os.fsync(stage_fd)
        os.close(stage_fd)
        stage_fd = -1
        if copied_hash.hexdigest() != source_sha256 or copied_size != source_size:
            raise CustodyError("staged bytes do not match the initially hashed source")
        try:
            os.link(stage, target, follow_symlinks=False)
        except FileExistsError:
            verified_target, verified_size = verify_preserved(root, candidate_sha, source_sha256)
            if verified_size != source_size:
                raise CustodyError("concurrent existing artifact differs from source")
            return verified_target, source_sha256, source_size, "ALREADY_PRESENT_VERIFIED"
        os.chmod(target, 0o444, follow_symlinks=False)
        verified_target, verified_size = verify_preserved(root, candidate_sha, source_sha256)
        if verified_size != source_size:
            raise CustodyError("preserved readback size differs from source")
        return verified_target, source_sha256, source_size, "PRESERVED_AND_VERIFIED"
    finally:
        if stage_fd >= 0:
            os.close(stage_fd)
        try:
            stage.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--preserve", type=Path, metavar="FIRMWARE_UF2")
    actions.add_argument("--verify", action="store_true")
    actions.add_argument("--pre-handoff-verify", action="store_true")
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--artifact-sha256")
    args = parser.parse_args()
    try:
        if args.preserve:
            require_clean_candidate_checkout(args.candidate_sha)
            if args.artifact_sha256 is not None:
                parser.error("--artifact-sha256 is derived during --preserve")
            path, digest, size, status_value = preserve(args.preserve, args.candidate_sha)
            require_clean_candidate_checkout(args.candidate_sha)
        else:
            require_local_commit(args.candidate_sha)
            if args.artifact_sha256 is None:
                parser.error("verification requires --artifact-sha256")
            path, size = verify_preserved(
                DEFAULT_CUSTODY_ROOT, args.candidate_sha, args.artifact_sha256
            )
            digest = require_artifact_sha256(args.artifact_sha256)
            status_value = (
                "PRE_HANDOFF_VERIFIED" if args.pre_handoff_verify else "VERIFIED"
            )
    except (CustodyError, OSError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    print(f"custody_status={status_value}")
    print(f"candidate_git_sha={args.candidate_sha}")
    print(f"firmware_artifact_sha256={digest}")
    print(f"preserved_firmware_artifact_locator={path.relative_to(REPO_ROOT).as_posix()}")
    print(f"size_bytes={size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
