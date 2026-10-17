#!/usr/bin/env python3
"""Compile and execute the deterministic ProfileStore root-interruption seam."""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/fixtures/profile_store_atomic_commit_host.cpp"

def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        raise SystemExit("profile-store atomic-commit: FAIL: C++ compiler unavailable")
    with tempfile.TemporaryDirectory(prefix="profile-store-atomic-") as directory:
        executable = Path(directory) / "harness"
        command = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-I", str(ROOT / "include"), str(SOURCE), "-o", str(executable)]
        subprocess.run(command, check=True)
        subprocess.run([str(executable)], check=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
