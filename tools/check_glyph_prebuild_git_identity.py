#!/usr/bin/env python3
"""Check the fail-closed pre-build Git identity contract without building."""
from __future__ import annotations

import ast
import os
import subprocess
import tempfile
from pathlib import Path

from glyph_tracked_worktree_integrity import (
    TrackedWorktreeIntegrityError,
    ignored_critical_worktree_paths,
    tracked_worktree_divergence,
)


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "builder_scripts/arduino_pico.py"


def load_builder():
    source = BUILDER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    # The PlatformIO script calls Import() at module load, so execute only the
    # helper definition in a normal checker process.
    helper = ast.Module(
        body=[node for node in tree.body if (
            isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))
            and getattr(node, "name", None) != "before_build"
        ) or (
            isinstance(node, ast.Assign)
            and not any(isinstance(target, ast.Name) and target.id == "ROOT" for target in node.targets)
        )],
        type_ignores=[],
    )
    namespace = {
        "__name__": "builder_contract",
        "__file__": str(BUILDER),
        "ROOT": BUILDER.parents[1],
    }
    exec(compile(helper, str(BUILDER), "exec"), namespace)
    return namespace["git_identity"]


def new_repo() -> Path:
    path = Path(tempfile.mkdtemp(prefix="glyph-prebuild-git-"))
    subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True, capture_output=True)
    (path / "tracked.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=Glyph", "-c", "user.email=glyph@example.invalid", "commit", "-qm", "base"], check=True)
    return path


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    expect("git_identity" in source and "--untracked-files=normal" in source, "helper/status contract missing")
    expect("--global" not in source, "global Git configuration mutation remains")
    expect('version_name = "\\\\\\\"" + git_identity() + "\\\\\\\""' in source, "version quoting changed")
    before_build = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "before_build")
    before_calls = [node for node in ast.walk(before_build) if isinstance(node, ast.Call)]
    expect(any(isinstance(call.func, ast.Name) and call.func.id == "git_identity" for call in before_calls), "before_build does not validate identity")
    append = next(call for call in before_calls if isinstance(call.func, ast.Attribute) and call.func.attr == "Append")
    identity_call = next(call for call in before_calls if isinstance(call.func, ast.Name) and call.func.id == "git_identity")
    expect(append.lineno > identity_call.lineno, "env.Append precedes identity validation")

    identity = load_builder()
    repo = new_repo()
    clean = identity(repo)
    expect(clean == clean.lower() and clean.isalnum(), "clean identity format changed")
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    expect(identity(repo).endswith("-DIRTY"), "unstaged change not dirty")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
    expect(identity(repo).endswith("-DIRTY"), "staged change not dirty")
    (repo / "untracked.txt").write_text("new\n", encoding="utf-8")
    expect(identity(repo).endswith("-DIRTY"), "untracked change not dirty")

    class Fake:
        def __init__(self, rev="abc1234\n", status=""):
            self.rev, self.status = rev, status
            self.calls = []

        def __call__(self, argv, **kwargs):
            self.calls.append((argv, kwargs))
            stdout = self.rev if len(self.calls) == 1 else self.status
            return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr="")

    fake = Fake()
    expect(identity(Path("/repo"), fake, lambda _root: ()) == "abc1234", "fake clean identity changed")
    expect([call[0] for call in fake.calls] == [
        ["git", "-c", "core.longpaths=true", "rev-parse", "--short", "HEAD"],
        ["git", "-c", "core.longpaths=true", "status", "--porcelain", "--untracked-files=normal"],
    ], "Git argv/order contract changed")
    expect(all(call[1]["cwd"] == Path("/repo") for call in fake.calls), "Git cwd is not explicit")

    ignored = new_repo()
    (ignored / ".gitignore").write_text(
        "ignored.txt\nsrc/ghost.cpp\nplatformio.ini\n.github/workflows/ghost.yml\n"
        "docs/.github/workflows/ghost.yml\n"
        ".git/info-exclude-placeholder\n.pio/\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(ignored), "add", ".gitignore"], check=True)
    subprocess.run(["git", "-C", str(ignored), "-c", "user.name=Glyph", "-c", "user.email=glyph@example.invalid", "commit", "-qm", "ignore"], check=True)
    (ignored / "ignored.txt").write_text("ignored\n", encoding="utf-8")
    (ignored / "src").mkdir()
    (ignored / "src/ghost.cpp").write_text("compiler input\n", encoding="utf-8")
    (ignored / "platformio.ini").write_text("build control\n", encoding="utf-8")
    (ignored / ".github/workflows").mkdir(parents=True)
    (ignored / ".github/workflows/ghost.yml").write_text("workflow\n", encoding="utf-8")
    (ignored / "docs/.github/workflows").mkdir(parents=True)
    (ignored / "docs/.github/workflows/ghost.yml").write_text("nested workflow\n", encoding="utf-8")
    expect(identity(ignored).endswith("-DIRTY"), "ignored critical source was accepted")
    (ignored / "src/ghost.cpp").unlink()
    (ignored / "platformio.ini").unlink()
    (ignored / ".github/workflows/ghost.yml").unlink()
    (ignored / "docs/.github/workflows/ghost.yml").unlink()
    (ignored / ".git/info/exclude").write_text("include/ghost.hpp\n", encoding="utf-8")
    (ignored / "include").mkdir()
    (ignored / "include/ghost.hpp").write_text("compiler input\n", encoding="utf-8")
    expect(identity(ignored).endswith("-DIRTY"), "ignored info-exclude source was accepted")
    (ignored / "include/ghost.hpp").unlink()
    global_excludes = ignored.parent / "global-excludes"
    global_excludes.write_text("config/ghost.ini\n", encoding="utf-8")
    global_config = ignored.parent / "global-gitconfig"
    global_config.write_text(f"[core]\n\texcludesFile = {global_excludes}\n", encoding="utf-8")
    previous_global = os.environ.get("GIT_CONFIG_GLOBAL")
    os.environ["GIT_CONFIG_GLOBAL"] = str(global_config)
    (ignored / "config").mkdir()
    (ignored / "config/ghost.ini").write_text("compiler input\n", encoding="utf-8")
    expect(identity(ignored).endswith("-DIRTY"), "ignored global-exclude source was accepted")
    (ignored / "config/ghost.ini").unlink()
    if previous_global is None:
        os.environ.pop("GIT_CONFIG_GLOBAL", None)
    else:
        os.environ["GIT_CONFIG_GLOBAL"] = previous_global
    (ignored / ".pio").mkdir()
    (ignored / ".pio/cache.bin").write_text("dependency cache\n", encoding="utf-8")
    expect(not identity(ignored).endswith("-DIRTY"), "ignored cache was rejected")
    expect(ignored_critical_worktree_paths(ignored) == (), "ignored cache entered critical inventory")

    def status_failure(argv, **kwargs):
        if argv[-1] == "HEAD":
            return subprocess.CompletedProcess(argv, 0, stdout="abc1234\n", stderr="")
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="failed")

    try:
        identity(Path("/repo"), status_failure, lambda _root: ())
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted failed Git status")

    try:
        identity(Path("/definitely/missing/repository"))
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted missing repository")

    for bad in ("", "abc\ndef\n", "ABC123\n", "not-hex\n"):
        try:
            identity(Path("."), Fake(rev=bad), lambda _root: ())
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"accepted invalid identity {bad!r}")

    def fail_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="failed")
    try:
        identity(Path("."), fail_runner, lambda _root: ())
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted failed Git command")

    hidden = new_repo()
    (hidden / "tracked.txt").write_text("hidden change\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(hidden), "update-index", "--assume-unchanged", "tracked.txt"], check=True)
    expect(identity(hidden).endswith("-DIRTY"), "assume-unchanged hid tracked bytes")
    subprocess.run(["git", "-C", str(hidden), "update-index", "--no-assume-unchanged", "tracked.txt"], check=True)
    (hidden / "tracked.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(hidden), "update-index", "--skip-worktree", "tracked.txt"], check=True)
    (hidden / "tracked.txt").write_text("skip-worktree change\n", encoding="utf-8")
    expect(identity(hidden).endswith("-DIRTY"), "skip-worktree hid tracked bytes")
    subprocess.run(["git", "-C", str(hidden), "update-index", "--no-skip-worktree", "tracked.txt"], check=True)
    (hidden / "tracked.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(hidden), "config", "core.filemode", "false"], check=True)
    (hidden / "tracked.txt").chmod(0o755)
    expect(identity(hidden).endswith("-DIRTY"), "core.filemode hid executable-bit change")

    hidden.chmod(0o755)
    subprocess.run(["git", "-C", str(hidden), "config", "core.filemode", "true"], check=True)
    (hidden / "tracked.txt").chmod(0o755)
    expect(identity(hidden).endswith("-DIRTY"), "owner executable-bit change was missed")

    same_size = new_repo()
    same_path = same_size / "tracked.txt"
    previous = same_path.stat()
    same_path.write_text("same\n", encoding="utf-8")
    os.utime(same_path, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    expect(identity(same_size).endswith("-DIRTY"), "same-size restored-mtime change was missed")

    missing = new_repo()
    (missing / "tracked.txt").unlink()
    try:
        identity(missing)
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted missing tracked file")

    symlink_repo = new_repo()
    (symlink_repo / "target").write_text("target\n", encoding="utf-8")
    (symlink_repo / "link").symlink_to("./target")
    subprocess.run(["git", "-C", str(symlink_repo), "add", "target", "link"], check=True)
    subprocess.run(["git", "-C", str(symlink_repo), "-c", "user.name=Glyph", "-c", "user.email=glyph@example.invalid", "commit", "-qm", "symlink"], check=True)
    expect(not identity(symlink_repo).endswith("-DIRTY"), "clean raw symlink target was rejected")
    (symlink_repo / "link").unlink()
    (symlink_repo / "link").symlink_to("target")
    expect(identity(symlink_repo).endswith("-DIRTY"), "symlink target change was missed")
    (symlink_repo / "link").unlink()
    (symlink_repo / "link").symlink_to("./target")
    raw_link = symlink_repo / "raw-link"
    os.symlink(b"\xff-target", os.fsencode(raw_link))
    subprocess.run(["git", "-C", str(symlink_repo), "add", "raw-link"], check=True)
    subprocess.run(["git", "-C", str(symlink_repo), "commit", "-qm", "raw symlink"], check=True)
    expect(not identity(symlink_repo).endswith("-DIRTY"), "clean non-UTF-8 symlink target was rejected")
    raw_link.unlink()
    os.symlink(b"\xfe-target", os.fsencode(raw_link))
    expect(identity(symlink_repo).endswith("-DIRTY"), "non-UTF-8 symlink target change was missed")

    conflicted = new_repo()
    subprocess.run(["git", "-C", str(conflicted), "switch", "-c", "feature"], check=True)
    (conflicted / "tracked.txt").write_text("feature\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(conflicted), "commit", "-qam", "feature"], check=True)
    subprocess.run(["git", "-C", str(conflicted), "switch", "main"], check=True)
    (conflicted / "tracked.txt").write_text("main\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(conflicted), "commit", "-qam", "main"], check=True)
    subprocess.run(["git", "-C", str(conflicted), "merge", "feature"], check=False)
    try:
        identity(conflicted)
    except TrackedWorktreeIntegrityError:
        pass
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted unmerged tracked index")

    gitlink = new_repo()
    nested = gitlink / "nested"
    nested.mkdir()
    subprocess.run(["git", "-C", str(nested), "init", "-q"], check=True)
    (nested / "nested.txt").write_text("nested\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(nested), "add", "nested.txt"], check=True)
    subprocess.run(["git", "-C", str(nested), "-c", "user.name=Glyph", "-c", "user.email=glyph@example.invalid", "commit", "-qm", "nested"], check=True)
    subprocess.run(["git", "-C", str(gitlink), "add", "nested"], check=True)
    subprocess.run(["git", "-C", str(gitlink), "-c", "user.name=Glyph", "-c", "user.email=glyph@example.invalid", "commit", "-qm", "gitlink"], check=True)
    try:
        identity(gitlink)
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted unsupported gitlink entry")

    print("pre-build Git identity contract: PASS")


if __name__ == "__main__":
    main()
