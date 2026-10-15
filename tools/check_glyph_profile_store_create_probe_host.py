#!/usr/bin/env python3
"""Sanitized fake-MMIO proof of CREATE watchdog marker/recovery control flow."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT / "tools/fixtures/profile_store_create_probe_host"
def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="glyph-create-probe-") as directory:
            exe=Path(directory) / "probe"
            for command in (["c++", "-std=c++17", "-DARDUINO_ARCH_RP2040", "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g", "-I", str(HOST / "include"), "-I", str(ROOT / "include"), str(HOST / "probe_harness.cpp"), "-o", str(exe)], [str(exe)]):
                result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30,check=False,env={**os.environ,"UBSAN_OPTIONS":"halt_on_error=1:print_stacktrace=1"})
                if result.returncode: raise RuntimeError(" ".join(command)+"\n"+result.stdout+result.stderr)
                if result.stdout: print(result.stdout.strip())
        print("glyph_profile_store_create_probe_host: PASS asan=true ubsan=true fake_watchdog_mmio=true physical_watchdog=NOT_TESTED")
        return 0
    except (OSError,RuntimeError,subprocess.TimeoutExpired) as error:
        print(f"glyph_profile_store_create_probe_host: FAIL: {error}");return 1
if __name__=="__main__": raise SystemExit(main())
