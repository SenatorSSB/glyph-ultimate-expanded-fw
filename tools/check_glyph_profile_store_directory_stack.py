#!/usr/bin/env python3
"""Prove the ProfileStore directory-commit callback stays below the RP2040 stack budget.

The production Pico image uses setup1()/loop1().  On the pinned Arduino-Pico
3.6.3 build the linked ELF exposes two 0x800-byte default stack reservations.
This checker deliberately compiles the old F6 callback reconstruction and the
current direct-buffer callback with the same pinned ARM compiler, Cortex-M0+
target and O3 optimisation used by glyph_mk6.  It reads GCC's -fstack-usage
output: the old local 2620-byte copy must exceed the deployed 2048-byte stack,
while the repaired shape must remain at or below 128 bytes.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_STORE = ROOT / "HAL/pico/src/core/ProfileStore.cpp"
PLATFORMIO = ROOT / "platformio.ini"
FRAMEWORK_MAIN = Path.home() / ".platformio/packages/framework-arduinopico/cores/rp2040/main.cpp"
TOOLCHAIN = Path.home() / ".platformio/packages/toolchain-rp2040-earlephilhower/bin/arm-none-eabi-g++"
DIRECT_LIMIT = 128
DEPLOYED_STACK_BYTES = 2048


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def stack_usage(source: str, name: str, directory: Path) -> int:
    path = directory / f"{name}.cpp"
    path.write_text(source, encoding="utf-8")
    compiler = TOOLCHAIN if TOOLCHAIN.is_file() else Path(shutil.which("arm-none-eabi-g++") or "")
    require(compiler.is_file(), "pinned arm-none-eabi-g++ unavailable")
    subprocess.run([str(compiler), "-std=gnu++17", "-mcpu=cortex-m0plus", "-mthumb", "-O3",
                    "-ffunction-sections", "-fdata-sections", "-fstack-usage", "-c", str(path),
                    "-o", str(directory / f"{name}.o")], check=True)
    su = path.with_suffix(".su")
    require(su.is_file(), f"missing stack-usage output for {name}")
    match = re.search(rf"DecodeDirectoryCommit{name.capitalize()}.*\t(\d+)\t", su.read_text(encoding="utf-8"))
    require(match is not None, f"missing callback stack record for {name}")
    return int(match.group(1))


def callback_source(name: str, old_copy: bool) -> str:
    body = """
    unsigned char copy[kDirectoryWireBytes];
    __builtin_memcpy(copy, bytes, sizeof(copy));
    return DecodeDirectory(copy, length, directory);
""" if old_copy else """
    return DecodeDirectory(bytes, length, directory);
"""
    return f"""
    #include <stddef.h>
    #include <stdint.h>
    constexpr size_t kDirectoryWireBytes = 2620;
    struct Directory {{ uint32_t generation; }};
    __attribute__((noinline)) bool DecodeDirectory(const unsigned char *wire, size_t length, Directory *directory) {{
      if (length != kDirectoryWireBytes) return false;
      directory->generation = uint32_t(wire[0]) | (uint32_t(wire[1]) << 8);
      return wire[2] != 0xff;
    }}
    __attribute__((noinline)) bool DecodeDirectoryCommit{name.capitalize()}(void *context, const unsigned char *bytes, size_t length) {{
      if (length != kDirectoryWireBytes) return false;
      auto *directory = static_cast<Directory *>(context);{body}
    }}
    """


def main() -> int:
    try:
        text = PROFILE_STORE.read_text(encoding="utf-8")
        require("return DecodeDirectory(bytes, length, directory);" in text,
                "direct directory decoder callback shape missing")
        callback = text[text.index("bool DecodeDirectoryCommit"):text.index("struct RecordCommitContext")]
        require("uint8_t wire[kDirectoryWireBytes]" not in callback,
                "F6-sized directory stack copy has returned")
        require("-O3" in PLATFORMIO.read_text(encoding="utf-8"), "glyph_mk6 O3 flag missing")
        framework = FRAMEWORK_MAIN.read_text(encoding="utf-8")
        require("bool core1_separate_stack __attribute__((weak)) = false;" in framework,
                "pinned framework default core1 stack model changed")
        require("multicore_launch_core1(main1);" in framework,
                "pinned framework default launch path changed")
        with tempfile.TemporaryDirectory(prefix="glyph-profile-stack-") as raw:
            directory = Path(raw)
            old = stack_usage(callback_source("old", True), "old", directory)
            repaired = stack_usage(callback_source("repaired", False), "repaired", directory)
        require(old > DEPLOYED_STACK_BYTES,
                f"old F6 reconstruction unexpectedly fits {DEPLOYED_STACK_BYTES} byte stack ({old})")
        require(repaired <= DIRECT_LIMIT,
                f"repaired callback consumes {repaired}, above {DIRECT_LIMIT} byte gate")
    except (AssertionError, OSError, subprocess.CalledProcessError) as error:
        print(f"glyph_profile_store_directory_stack: FAIL: {error}")
        return 1
    print("glyph_profile_store_directory_stack: PASS")
    print(f"toolchain=pinned-arm-none-eabi-g++ cortex_m0plus=true old_f6_bytes={old} repaired_bytes={repaired} "
          f"deployed_stack_bytes={DEPLOYED_STACK_BYTES} repaired_limit={DIRECT_LIMIT} "
          f"margin_bytes={DEPLOYED_STACK_BYTES - repaired} core1_separate_stack_default=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
