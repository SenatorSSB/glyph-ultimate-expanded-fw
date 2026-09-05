import subprocess
from pathlib import Path
import re

Import("env")

ROOT = Path(env.subst("$PROJECT_DIR"))
_HEX_IDENTITY = re.compile(r"[0-9a-f]+")


def git_identity(repo_root=ROOT, runner=subprocess.run):
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
    return commit + ("-DIRTY" if status.stdout else "")


def before_build():
    version_name = "\\\"" + git_identity() + "\\\""

    env.Append(CPPDEFINES=[
        ("FIRMWARE_VERSION", version_name)
    ])

before_build()
