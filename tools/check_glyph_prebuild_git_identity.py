#!/usr/bin/env python3
"""Check the fail-closed pre-build Git identity contract without building."""
from __future__ import annotations

import ast
import subprocess
import tempfile
from pathlib import Path


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
    namespace = {"__name__": "builder_contract", "ROOT": BUILDER.parents[1]}
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
    expect(identity(Path("/repo"), fake) == "abc1234", "fake clean identity changed")
    expect([call[0] for call in fake.calls] == [
        ["git", "-c", "core.longpaths=true", "rev-parse", "--short", "HEAD"],
        ["git", "-c", "core.longpaths=true", "status", "--porcelain", "--untracked-files=normal"],
    ], "Git argv/order contract changed")
    expect(all(call[1]["cwd"] == Path("/repo") for call in fake.calls), "Git cwd is not explicit")

    ignored = new_repo()
    (ignored / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(ignored), "add", ".gitignore"], check=True)
    subprocess.run(["git", "-C", str(ignored), "-c", "user.name=Glyph", "-c", "user.email=glyph@example.invalid", "commit", "-qm", "ignore"], check=True)
    (ignored / "ignored.txt").write_text("ignored\n", encoding="utf-8")
    expect(not identity(ignored).endswith("-DIRTY"), "ignored-only state marked dirty")

    def status_failure(argv, **kwargs):
        if argv[-1] == "HEAD":
            return subprocess.CompletedProcess(argv, 0, stdout="abc1234\n", stderr="")
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="failed")

    try:
        identity(Path("/repo"), status_failure)
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
            identity(Path("."), Fake(rev=bad))
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"accepted invalid identity {bad!r}")

    def fail_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="failed")
    try:
        identity(Path("."), fail_runner)
    except RuntimeError:
        pass
    else:
        raise AssertionError("accepted failed Git command")

    print("pre-build Git identity contract: PASS")


if __name__ == "__main__":
    main()
