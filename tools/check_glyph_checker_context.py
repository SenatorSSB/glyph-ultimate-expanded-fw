#!/usr/bin/env python3
"""Focused self-test for the fail-closed Glyph checker-context helper."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from glyph_checker_context import ScopeValidationError, collect_checker_context, validate_feature_scope


def run(root: Path, *args: str) -> None:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")


def output(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def expect_scope_failure(root: Path, base: str | None, needle: str) -> None:
    context = collect_checker_context(repo_root=root, base=base)
    try:
        validate_feature_scope(context, allowed_paths=("docs/",))
    except ScopeValidationError as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc!s}") from exc
    else:
        raise AssertionError(f"scope unexpectedly accepted case containing {needle!r}")


def fresh_repo(parent: Path) -> Path:
    root = parent / "repo"
    root.mkdir()
    run(root, "init", "-b", "configurator")
    run(root, "config", "user.name", "Glyph checker context test")
    run(root, "config", "user.email", "checker-context@example.invalid")
    write(root, "docs/baseline.md", "baseline\n")
    run(root, "add", "docs/baseline.md")
    run(root, "commit", "-m", "baseline")
    return root


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "renamed-feature-branch")
        write(root, "docs/allowed.md", "allowed\n")
        run(root, "add", "docs/allowed.md")
        run(root, "commit", "-m", "docs only")
        context = collect_checker_context(repo_root=root, base="configurator")
        validate_feature_scope(context, allowed_paths=("docs/",))

        write(root, "src/committed.cpp", "x\n")
        run(root, "add", "src/committed.cpp")
        run(root, "commit", "-m", "protected committed")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/committed.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-include")
        write(root, "include/committed.hpp", "x\n")
        run(root, "add", "include/committed.hpp")
        run(root, "commit", "-m", "protected include")
        expect_scope_failure(root, "configurator", "protected prefix changed: include/committed.hpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-staged")
        write(root, "src/staged.cpp", "x\n")
        run(root, "add", "src/staged.cpp")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/staged.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-unstaged")
        write(root, "src/unstaged.cpp", "x\n")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/unstaged.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-mixed")
        write(root, "docs/allowed.md", "allowed\n")
        write(root, "src/protected.cpp", "x\n")
        run(root, "add", "docs/allowed.md", "src/protected.cpp")
        run(root, "commit", "-m", "mixed paths")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/protected.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-case-variant")
        write(root, "SRC/case_variant.cpp", "x\n")
        run(root, "add", "SRC/case_variant.cpp")
        run(root, "commit", "-m", "case variant protected")
        expect_scope_failure(root, "configurator", "protected prefix changed: SRC/case_variant.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-renamed-path")
        write(root, "docs/rename-me.md", "x\n")
        run(root, "add", "docs/rename-me.md")
        run(root, "commit", "-m", "docs file")
        (root / "src").mkdir()
        run(root, "mv", "docs/rename-me.md", "src/renamed.cpp")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/renamed.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        original_base = output(root, "rev-parse", "HEAD")
        run(root, "switch", "-c", "feature-wrong-merge-base")
        write(root, "docs/feature.md", "feature\n")
        run(root, "add", "docs/feature.md")
        run(root, "commit", "-m", "feature")
        run(root, "switch", "configurator")
        write(root, "docs/base-advance.md", "base\n")
        run(root, "add", "docs/base-advance.md")
        run(root, "commit", "-m", "advance base")
        run(root, "switch", "feature-wrong-merge-base")
        run(root, "merge", "--no-edit", "configurator")
        context = collect_checker_context(
            repo_root=root, base="configurator", expected_merge_base=original_base
        )
        try:
            validate_feature_scope(context, allowed_paths=("docs/",))
        except ScopeValidationError as exc:
            if "unexpected feature merge base" not in str(exc):
                raise AssertionError(f"unexpected wrong-merge-base result: {exc!s}") from exc
        else:
            raise AssertionError("wrong expected merge base was accepted")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-base-not-ancestor")
        write(root, "docs/feature.md", "feature\n")
        run(root, "add", "docs/feature.md")
        run(root, "commit", "-m", "feature")
        run(root, "switch", "configurator")
        write(root, "docs/base.md", "base\n")
        run(root, "add", "docs/base.md")
        run(root, "commit", "-m", "advance base")
        run(root, "switch", "feature-base-not-ancestor")
        expect_scope_failure(root, "configurator", "is not an ancestor of HEAD")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-detached")
        run(root, "switch", "--detach")
        expect_scope_failure(root, None, "detached HEAD requires an explicit comparison base")
        context = collect_checker_context(repo_root=root, environ={"GLYPH_CHECKER_BASE": "configurator"})
        validate_feature_scope(context, allowed_paths=("docs/",))

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        write(root, "src/configurator_only.cpp", "x\n")
        context = collect_checker_context(repo_root=root, base="configurator")
        validate_feature_scope(context, allowed_paths=("docs/",))

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-outside-allowlist")
        write(root, "tools/not_allowed.py", "x\n")
        run(root, "add", "tools/not_allowed.py")
        run(root, "commit", "-m", "outside checker allowlist")
        expect_scope_failure(root, "configurator", "out-of-scope changed path: tools/not_allowed.py")

    historical = Path(__file__).with_name("check_glyph_source_owned_table_replacement_generator_contract.py")
    completed = subprocess.run(["python3", str(historical)], capture_output=True, text=True, check=False)
    if completed.returncode == 0 or "checker must run on" not in completed.stderr:
        raise AssertionError("historical exact-branch checker unexpectedly lost branch-specific policy")

    case_ids = (
        "CTX-01-valid-feature-branch",
        "CTX-02-renamed-feature-branch",
        "CTX-03-committed-src-rejected",
        "CTX-04-staged-src-rejected",
        "CTX-05-unstaged-src-rejected",
        "CTX-06-committed-include-rejected",
        "CTX-07-mixed-safe-protected-rejected",
        "CTX-08-case-variant-protected-rejected",
        "CTX-09-wrong-merge-base-rejected",
        "CTX-10-base-not-ancestor-rejected",
        "CTX-11-detached-explicit-base-accepted",
        "CTX-12-detached-missing-base-rejected",
        "CTX-13-configurator-content-accepted",
        "CTX-14-checker-allowlist-rejected",
        "CTX-15-historical-exact-branch-remains-specific",
    )
    print("glyph_checker_context: PASS; cases=" + ",".join(case_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
