"""Directly compare tracked HEAD/index entries with working-tree bytes and modes."""

from __future__ import annotations

from pathlib import Path
import stat
import subprocess
import os


CRITICAL_ROOTS = frozenset({
    "src", "include", "hal", "backend", "lib", "active", "storage", "config",
    "builder_scripts", "scripts", "boards", "variants", "patches", "proto",
})
CRITICAL_FILES = frozenset({
    "platformio.ini", "glyph_nuker", ".gitmodules", ".gitignore", ".gitattributes",
    "cmakelists.txt", "makefile", "sconstruct", "sconscript", "library.json",
    "library.properties", "requirements.txt", "platformio.lock",
})
IGNORED_ALLOWED_ROOTS = (".pio", ".platformio-home", ".venv", "local_backups")


def is_critical_path(path: str) -> bool:
    """Return whether a canonical Git path is in the audited critical inventory."""
    if (not isinstance(path, str) or not path or path.startswith("/")
            or "\\" in path or ":" in path
            or any(ord(char) < 32 or ord(char) == 127 for char in path)
            or any(part in {"", ".", ".."} for part in path.split("/"))):
        raise TrackedWorktreeIntegrityError(f"unsafe ignored Git path: {path!r}")
    folded = path.casefold()
    return (folded.split("/", 1)[0] in CRITICAL_ROOTS
            or folded in CRITICAL_FILES
            or folded.startswith(".github/workflows/")
            or "/.github/workflows/" in folded)


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


def ignored_critical_worktree_paths(repo_root: Path) -> tuple[str, ...]:
    """List ignored untracked entries in the finite firmware/build inventory.

    Git applies repository, info-exclude, and global excludes through
    ``--exclude-standard``.  The pathspecs intentionally omit disposable
    dependency caches and the owner-held custody root.
    """
    scope = sorted(CRITICAL_ROOTS | CRITICAL_FILES)
    workflow_scope = (
        ":(icase,glob).github/workflows/**",
        ":(icase,glob)**/.github/workflows/**",
    )
    excluded_roots = (
        ":(exclude,icase,glob).pio/**",
        ":(exclude,icase,glob).platformio-home/**",
        ":(exclude,icase,glob).venv/**",
        ":(exclude,icase,glob)local_backups/**",
    )
    raw = _git(
        repo_root,
        "ls-files", "--others", "--ignored", "--exclude-standard", "--full-name", "-z",
        "--", *(f":(icase){path}" for path in scope), *workflow_scope, *excluded_roots,
    )
    if raw and not raw.endswith(b"\0"):
        raise TrackedWorktreeIntegrityError("unterminated ignored Git path output")
    try:
        paths = tuple(sorted({part.decode("utf-8") for part in raw.split(b"\0") if part}))
    except UnicodeDecodeError as exc:
        raise TrackedWorktreeIntegrityError("non-UTF-8 ignored Git path") from exc
    paths = tuple(
        path for path in paths
        if not any(path == root or path.startswith(root + "/") for root in IGNORED_ALLOWED_ROOTS)
    )
    for path in paths:
        if not is_critical_path(path):
            raise TrackedWorktreeIntegrityError(f"ignored path escaped critical inventory: {path}")
    return paths


def untracked_critical_worktree_paths(repo_root: Path) -> tuple[str, ...]:
    """List ordinary untracked entries in the finite firmware/build inventory."""
    scope = sorted(CRITICAL_ROOTS | CRITICAL_FILES)
    workflow_scope = (
        ":(icase,glob).github/workflows/**",
        ":(icase,glob)**/.github/workflows/**",
    )
    excluded_roots = (
        ":(exclude,icase,glob).pio/**",
        ":(exclude,icase,glob).platformio-home/**",
        ":(exclude,icase,glob).venv/**",
        ":(exclude,icase,glob)local_backups/**",
    )
    raw = _git(
        repo_root,
        "ls-files", "--others", "--exclude-standard", "--full-name", "-z",
        "--", *(f":(icase){path}" for path in scope), *workflow_scope, *excluded_roots,
    )
    if raw and not raw.endswith(b"\0"):
        raise TrackedWorktreeIntegrityError("unterminated untracked Git path output")
    try:
        paths = tuple(sorted({part.decode("utf-8") for part in raw.split(b"\0") if part}))
    except UnicodeDecodeError as exc:
        raise TrackedWorktreeIntegrityError("non-UTF-8 untracked Git path") from exc
    for path in paths:
        if not is_critical_path(path):
            raise TrackedWorktreeIntegrityError(f"untracked path escaped critical inventory: {path}")
    return paths


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
    divergent: set[str] = set(ignored_critical_worktree_paths(repo_root))
    divergent.update(untracked_critical_worktree_paths(repo_root))
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
