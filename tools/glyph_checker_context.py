#!/usr/bin/env python3
"""Fail-closed Git context helpers for runtime-config docs/tooling checkers.

This module is deliberately limited to repository state inspection.  It does
not edit files, create candidates, invoke generators, or call the network.
Checkers may use it to separate content validation from feature-branch scope
validation without using a branch name as a proxy for safe changed paths.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


DEFAULT_BASE_ENV = "GLYPH_CHECKER_BASE"
DEFAULT_EXPECTED_MERGE_BASE_ENV = "GLYPH_CHECKER_EXPECTED_MERGE_BASE"
DEFAULT_PROTECTED_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "hal/",
    "backend/",
    "lib/",
    "active/",
    "storage/",
)
DEFAULT_PROTECTED_COMPONENTS = (
    "config.pb",
    "storage",
    "write",
    "WebSerial",
    "webserial",
    "flash",
    "flashing",
)


class CheckerContextError(RuntimeError):
    """Base error for an unavailable or unsafe checker context."""


class ScopeValidationError(CheckerContextError):
    """Raised when a feature-branch scope check fails closed."""


@dataclass(frozen=True)
class CheckerContext:
    """A single, immutable view of the current repository state."""

    repo_root: Path
    branch: str | None
    head: str
    base: str | None
    base_commit: str | None
    expected_merge_base: str | None
    merge_base: str | None
    base_is_ancestor: bool | None
    committed_paths: frozenset[str]
    staged_paths: frozenset[str]
    unstaged_paths: frozenset[str]

    @property
    def detached(self) -> bool:
        return self.branch is None

    @property
    def changed_paths(self) -> frozenset[str]:
        return self.committed_paths | self.staged_paths | self.unstaged_paths

    @property
    def dirty(self) -> bool:
        return bool(self.staged_paths or self.unstaged_paths)


def _git(repo_root: Path, args: Sequence[str], *, allow_failure: bool = False) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo_root, capture_output=True, text=True, check=False
    )
    if completed.returncode and not allow_failure:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise CheckerContextError(f"git {' '.join(args)} failed: {message}")
    return completed.stdout


def _git_returncode(repo_root: Path, args: Sequence[str]) -> int:
    return subprocess.run(
        ["git", *args], cwd=repo_root, capture_output=True, text=True, check=False
    ).returncode


def _resolve_commit(repo_root: Path, revision: str) -> str:
    return _git(repo_root, ["rev-parse", "--verify", f"{revision}^{{commit}}"]).strip()


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if not normalized or normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        raise CheckerContextError(f"unsafe changed path reported by git: {path!r}")
    return normalized


def _name_status_paths(repo_root: Path, args: Sequence[str]) -> frozenset[str]:
    """Return every side of each changed path, including renames/copies."""

    raw = _git(repo_root, [*args, "--name-status", "-z", "--find-renames"])
    fields = raw.split("\0")
    paths: set[str] = set()
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not status:
            continue
        if index >= len(fields):
            raise CheckerContextError(f"malformed NUL name-status output after {status!r}")
        if status[0] in {"R", "C"}:
            if index + 1 >= len(fields):
                raise CheckerContextError(f"malformed rename/copy status {status!r}")
            paths.add(_normalize_path(fields[index]))
            paths.add(_normalize_path(fields[index + 1]))
            index += 2
        else:
            paths.add(_normalize_path(fields[index]))
            index += 1
    return frozenset(paths)


def _untracked_paths(repo_root: Path) -> frozenset[str]:
    raw = _git(repo_root, ["ls-files", "--others", "--exclude-standard", "-z"])
    return frozenset(_normalize_path(path) for path in raw.split("\0") if path)


def _branch(repo_root: Path) -> str | None:
    value = _git(repo_root, ["symbolic-ref", "--quiet", "--short", "HEAD"], allow_failure=True).strip()
    return value or None


def collect_checker_context(
    *,
    repo_root: Path | str | None = None,
    base: str | None = None,
    expected_merge_base: str | None = None,
    default_branch: str = "configurator",
    environ: Mapping[str, str] | None = None,
) -> CheckerContext:
    """Collect state without deciding whether a checker needs scope validation.

    `base` or ``GLYPH_CHECKER_BASE`` supplies the comparison revision.  A
    caller that wants to pin an expected feature base separately from a moving
    remote ref may provide `expected_merge_base` (or its environment form).
    Missing bases are represented in the returned snapshot so callers can
    fail closed only when scope validation is actually required.
    """

    root = Path(repo_root or Path.cwd()).resolve()
    environment = os.environ if environ is None else environ
    branch = _branch(root)
    # A normal local feature branch can use the already-fetched remote base.
    # Detached CI deliberately does not get this convenience: it must state
    # the comparison base explicitly so scope validation cannot be ambiguous.
    selected_base = base or environment.get(DEFAULT_BASE_ENV)
    if selected_base is None and branch not in {None, default_branch}:
        selected_base = f"origin/{default_branch}"
    expected = expected_merge_base or environment.get(DEFAULT_EXPECTED_MERGE_BASE_ENV)
    head = _resolve_commit(root, "HEAD")
    base_commit = _resolve_commit(root, selected_base) if selected_base else None
    expected_commit = _resolve_commit(root, expected) if expected else None
    merge_base: str | None = None
    base_is_ancestor: bool | None = None
    committed: frozenset[str] = frozenset()
    if base_commit:
        base_is_ancestor = _git_returncode(root, ["merge-base", "--is-ancestor", base_commit, head]) == 0
        merge_base = _git(root, ["merge-base", base_commit, head]).strip()
        committed = _name_status_paths(root, ["diff", f"{merge_base}..{head}"])
    staged = _name_status_paths(root, ["diff", "--cached"])
    # `git diff` omits untracked files; include them because a feature-scope
    # guard must not permit a protected source addition merely because it has
    # not been staged yet.
    unstaged = _name_status_paths(root, ["diff"]) | _untracked_paths(root)
    return CheckerContext(
        repo_root=root,
        branch=branch,
        head=head,
        base=selected_base,
        base_commit=base_commit,
        expected_merge_base=expected_commit,
        merge_base=merge_base,
        base_is_ancestor=base_is_ancestor,
        committed_paths=committed,
        staged_paths=staged,
        unstaged_paths=unstaged,
    )


def _matches_allowlist(path: str, allowed_paths: Iterable[str]) -> bool:
    folded_path = path.casefold()
    for allowed in allowed_paths:
        folded_allowed = allowed.replace("\\", "/").casefold()
        if folded_allowed.endswith("/") and folded_path.startswith(folded_allowed):
            return True
        if folded_path == folded_allowed:
            return True
    return False


def _protected_reason(
    path: str,
    protected_prefixes: Iterable[str],
    protected_components: Iterable[str],
) -> str | None:
    folded_path = path.casefold()
    if any(folded_path.startswith(prefix.casefold()) for prefix in protected_prefixes):
        return "protected prefix"
    components = {component.casefold() for component in path.split("/")}
    hit = sorted(components & {component.casefold() for component in protected_components})
    if hit:
        return f"protected component {hit[0]!r}"
    return None


def validate_feature_scope(
    context: CheckerContext,
    *,
    allowed_paths: Iterable[str] | None = None,
    default_branch: str = "configurator",
    protected_prefixes: Iterable[str] = DEFAULT_PROTECTED_PREFIXES,
    protected_components: Iterable[str] = DEFAULT_PROTECTED_COMPONENTS,
    require_scope: bool = True,
) -> None:
    """Fail closed for a feature branch, while allowing base content checks.

    `configurator` intentionally skips feature changed-path enforcement.  For
    any other branch, including detached HEAD, a base is mandatory when
    `require_scope` is true.  Protected paths are checked before the optional
    checker-specific allowlist, so an allowlist cannot authorize active source
    changes accidentally.
    """

    if not require_scope or context.branch == default_branch:
        return
    if not context.base_commit or not context.merge_base or context.base_is_ancestor is None:
        location = "detached HEAD" if context.detached else f"feature branch {context.branch!r}"
        raise ScopeValidationError(
            f"{location} requires an explicit comparison base via --base or {DEFAULT_BASE_ENV}"
        )
    if not context.base_is_ancestor:
        raise ScopeValidationError(f"comparison base {context.base!r} is not an ancestor of HEAD")
    expected = context.expected_merge_base or context.base_commit
    if context.merge_base != expected:
        raise ScopeValidationError(
            f"unexpected feature merge base: {context.merge_base}; expected {expected}"
        )
    for path in sorted(context.changed_paths):
        reason = _protected_reason(path, protected_prefixes, protected_components)
        if reason:
            raise ScopeValidationError(f"{reason} changed: {path}")
        if allowed_paths is not None and not _matches_allowlist(path, allowed_paths):
            raise ScopeValidationError(f"out-of-scope changed path: {path}")
