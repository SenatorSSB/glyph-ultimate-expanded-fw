#!/usr/bin/env python3
"""Host-only pinned LittleFS C/RAM NOR proof; no Arduino or physical equivalence."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("GLYPH_ARDUINOPICO_FRAMEWORK", str(Path.home() / ".platformio/packages/framework-arduinopico")))


def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False, env={**os.environ, "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"})
    if result.returncode:
        raise RuntimeError(" ".join(command) + "\n" + result.stdout + result.stderr)
    return result.stdout


def main() -> int:
    try:
        if json.loads((FRAMEWORK / "package.json").read_text())["version"] != "1.30603.0":
            raise AssertionError("expected Arduino-Pico 3.6.3 package")
        library = FRAMEWORK / "libraries/LittleFS"
        flags = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
        with tempfile.TemporaryDirectory(prefix="glyph-littlefs-host-") as directory:
            temp = Path(directory)
            objects = []
            for name in ("lfs", "lfs_util"):
                target = temp / f"{name}.o"
                run(["cc", "-std=c11", *flags, "-c", str(library / "src" / f"{name}.c"), "-o", str(target)])
                objects.append(str(target))
            exe = temp / "littlefs-host"
            run(["c++", "-std=c++17", *flags, "-Wall", "-Wextra", "-Werror", "-DLFS_NAME_MAX=32", "-I", str(ROOT / "include"), "-I", str(library / "lib/littlefs"), str(ROOT / "tools/fixtures/profile_store_littlefs_host/littlefs_harness.cpp"), *objects, "-o", str(exe)])
            print(run([str(exe)]).strip())
        print("glyph_profile_store_littlefs_host: PASS asan=true ubsan=true framework=1.30603.0 ram_block_size=4096 ram_block_count=128 physical_multicore=NOT_TESTED")
        for relative in ("src/lfs.c", "src/lfs_util.c", "lib/littlefs/lfs.c", "lib/littlefs/lfs.h", "lib/littlefs/lfs_util.c", "lib/littlefs/lfs_util.h"):
            print(f"source_sha256 {relative} {hashlib.sha256((library / relative).read_bytes()).hexdigest()}")
        return 0
    except (OSError, ValueError, AssertionError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"glyph_profile_store_littlefs_host: FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
