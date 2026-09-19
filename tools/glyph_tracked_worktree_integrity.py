"""Directly compare tracked HEAD/index entries with working-tree bytes and modes."""

from __future__ import annotations

from pathlib import Path
import stat
import subprocess
import os


class TrackedWorktreeIntegrityError(ValueError):
    """Raised when Git cannot provide an unambiguous tracked-entry snapshot."""


def _git(repo_root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, capture_output=True, check=False
    )
    if result.returncode:
        raise TrackedWorktreeIntegrityError(
            f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}"
        )
    return result.stdout


def _tree(repo_root: Path) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    raw = _git(repo_root, "ls-tree", "-r", "-z", "HEAD")
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, path_bytes = record.split(b"\t", 1)
            mode, kind, blob = header.decode("ascii").split()
            path = path_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise TrackedWorktreeIntegrityError("invalid HEAD tree entry") from exc
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise TrackedWorktreeIntegrityError(f"unsupported tracked HEAD entry: {path}")
        if path in entries:
            raise TrackedWorktreeIntegrityError(f"duplicate tracked HEAD entry: {path}")
        entries[path] = (mode, blob)
    return entries


def _index(repo_root: Path) -> dict[str, tuple[str, int, str]]:
    entries: dict[str, tuple[str, int, str]] = {}
    raw = _git(repo_root, "ls-files", "--stage", "-z")
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, path_bytes = record.split(b"\t", 1)
            mode, blob, stage_text = header.decode("ascii").split()
            path = path_bytes.decode("utf-8")
            stage = int(stage_text)
        except (ValueError, UnicodeDecodeError) as exc:
            raise TrackedWorktreeIntegrityError("invalid index entry") from exc
        if stage != 0 or mode not in {"100644", "100755", "120000"}:
            raise TrackedWorktreeIntegrityError(f"unsupported or unmerged index entry: {path}")
        if path in entries:
            raise TrackedWorktreeIntegrityError(f"duplicate index entry: {path}")
        entries[path] = (mode, stage, blob)
    return entries


def _working_entry(path: Path, expected_mode: str, expected_data: bytes) -> tuple[str, bytes]:
    for parent in path.parents:
        if parent == path.anchor:
            break
        try:
            if parent.is_symlink():
                raise TrackedWorktreeIntegrityError(
                    f"tracked path has a symlinked parent: {path}"
                )
        except OSError as exc:
            raise TrackedWorktreeIntegrityError(
                f"unable to inspect tracked path parent: {path}"
            ) from exc
    try:
        info = path.lstat()
    except OSError as exc:
        raise TrackedWorktreeIntegrityError(f"tracked path is missing: {path}") from exc
    if stat.S_ISLNK(info.st_mode):
        if expected_mode != "120000":
            raise TrackedWorktreeIntegrityError(f"tracked path changed to symlink: {path}")
        try:
            data = os.readlink(os.fsencode(path))
        except OSError as exc:
            raise TrackedWorktreeIntegrityError(f"unable to read tracked symlink: {path}") from exc
        return expected_mode, data
    if not stat.S_ISREG(info.st_mode):
        raise TrackedWorktreeIntegrityError(f"tracked path is not a regular file: {path}")
    if expected_mode == "120000":
        raise TrackedWorktreeIntegrityError(f"tracked symlink changed to regular file: {path}")
    mode = "100755" if info.st_mode & 0o111 else "100644"
    try:
        with path.open("rb") as stream:
            return mode, stream.read()
    except OSError as exc:
        raise TrackedWorktreeIntegrityError(f"unable to read tracked path: {path}") from exc


def tracked_worktree_divergence(repo_root: Path) -> tuple[str, ...]:
    """Return sorted tracked paths whose HEAD, index, or working entry diverges."""
    repo_root = repo_root.resolve()
    head = _tree(repo_root)
    index = _index(repo_root)
    if set(head) != set(index):
        return tuple(sorted(set(head) ^ set(index)))
    divergent: set[str] = set()
    for path in sorted(head):
        head_mode, head_blob = head[path]
        index_mode, stage, index_blob = index[path]
        if stage != 0 or (head_mode, head_blob) != (index_mode, index_blob):
            divergent.add(path)
            continue
        expected_data = _git(repo_root, "cat-file", "blob", head_blob)
        work_mode, work_data = _working_entry(repo_root / path, head_mode, expected_data)
        if (work_mode, work_data) != (head_mode, expected_data):
            divergent.add(path)
    return tuple(sorted(divergent))
