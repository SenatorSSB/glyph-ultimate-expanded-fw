import subprocess
from pathlib import Path
import re
import sys

Import("env")
ROOT = Path(env.subst("$PROJECT_DIR"))
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from glyph_tracked_worktree_integrity import (
    TrackedWorktreeIntegrityError,
    tracked_worktree_divergence,
)

_HEX_IDENTITY = re.compile(r"[0-9a-f]+")


def git_identity(repo_root=ROOT, runner=subprocess.run, integrity_checker=tracked_worktree_divergence):
    """Return the existing firmware version identity, or fail before publish."""
    common = ["git", "-c", "core.longpaths=true"]
    try:
        identity = runner(
            common + ["rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RuntimeError("unable to invoke Git for HEAD") from exc
    if identity.returncode != 0 or not isinstance(identity.stdout, str):
        raise RuntimeError("unable to resolve Git HEAD")
    lines = identity.stdout.splitlines()
    commit = identity.stdout.strip()
    if len(lines) != 1 or not _HEX_IDENTITY.fullmatch(commit):
        raise RuntimeError("Git HEAD identity is empty, multiline, or non-hex")

    try:
        status = runner(
            common + ["status", "--porcelain", "--untracked-files=normal"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RuntimeError("unable to invoke Git for status") from exc
    if status.returncode != 0 or not isinstance(status.stdout, str):
        raise RuntimeError("unable to resolve Git status")
    try:
        hidden_divergence = integrity_checker(repo_root)
    except TrackedWorktreeIntegrityError as exc:
        raise RuntimeError("unable to verify tracked working-tree integrity") from exc
    return commit + ("-DIRTY" if status.stdout or hidden_divergence else "")


def before_build():
    version_name = "\\\"" + git_identity() + "\\\""

    env.Append(CPPDEFINES=[
        ("FIRMWARE_VERSION", version_name)
    ])

before_build()
