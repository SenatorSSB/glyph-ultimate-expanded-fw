"""Classify an event diff conservatively for the firmware build job.

Validation always runs. Only regular Markdown prose under docs/ or in the
repository root is exempt from firmware compilation. Unknown modes and paths,
an unavailable base, and a first push without an event diff require a build.
"""
import json
import os
import re
import subprocess
from pathlib import Path


def needs_build(base, head):
    if not all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v) for v in (base, head)):
        return True
    result = subprocess.run(
        ["git", "diff", "--raw", "--no-renames", "-z", base, head, "--"],
        capture_output=True,
    )
    if result.returncode:
        return True
    fields = result.stdout.split(b"\0")
    if fields.pop() or len(fields) % 2:
        raise ValueError("malformed Git change record")
    for header, path in zip(fields[::2], fields[1::2]):
        match = re.fullmatch(rb":(\d{6}) (\d{6}) [0-9a-f]+ [0-9a-f]+ [AMD]", header)
        if not match or any(mode not in (b"000000", b"100644") for mode in match.groups()):
            return True
        if not path.endswith(b".md") or (b"/" in path and not path.startswith(b"docs/")):
            return True
    return False


if __name__ == "__main__":
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    base = event["pull_request"]["base"]["sha"] if "pull_request" in event else event.get("before")
    if (base == "0" * 40 and event.get("created") and
            os.environ.get("GITHUB_REF") != "refs/heads/configurator"):
        merged = subprocess.run(["git", "merge-base", "HEAD", "origin/configurator"],
                                capture_output=True, text=True)
        base = merged.stdout.strip() if merged.returncode == 0 else None
    print("firmware=" + str(needs_build(base, os.environ["GITHUB_SHA"])).lower())
