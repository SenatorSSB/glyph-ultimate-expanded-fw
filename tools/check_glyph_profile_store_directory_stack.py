#!/usr/bin/env python3
"""Prove the ProfileStore directory-commit callback stays below the RP2040 stack budget.

The production Pico image uses setup1()/loop1().  On the pinned Arduino-Pico
3.6.3 build the linked ELF exposes two 0x800-byte default stack reservations.
This checker deliberately compiles the old F6 callback reconstruction and the
current direct-buffer callback with the same pinned ARM compiler, Cortex-M0+
target and O3 optimisation used by glyph_mk6.  It reads GCC's -fstack-usage
output: the old local 2620-byte copy must exceed the 2048-byte minimum reservation,
while the repaired shape must remain at or below 128 bytes.
"""
from __future__ import annotations

import re
import os
import sys
from check_glyph_stage_b_ultimate_profiles import NANOPB
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
RESERVED_STACK_BYTES = 2048


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


def compile_production(source: str, name: str, directory: Path, generated: Path) -> dict[str, int]:
    path = directory / (name + '.cpp'); path.write_text(source)
    nanopb = Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB', str(NANOPB)))
    subprocess.run([str(TOOLCHAIN), '-std=gnu++17', '-mcpu=cortex-m0plus', '-mthumb', '-O3',
                    '-fshort-enums', '-ffunction-sections', '-fdata-sections', '-fstack-usage',
                    '-I', str(ROOT/'include'), '-I', str(generated), '-I', str(nanopb),
                    '-I', str(ROOT/'config/glyph/common/include'), '-I', str(ROOT/'config/glyph/glyph_mk6/include'),
                    '-c', str(path), '-o', str(directory/(name+'.o'))], check=True)
    rows = {}
    for line in path.with_suffix('.su').read_text().splitlines():
        function, amount, _ = line.rsplit('\t', 2)
        rows[function] = int(amount)
    return rows


def frame(rows: dict[str,int], needle: str) -> int:
    found = [size for name, size in rows.items() if needle in name]
    require(bool(found), 'missing actual production stack frame: '+needle)
    return max(found)


def main() -> int:
    try:
        text = PROFILE_STORE.read_text(encoding='utf-8')
        require('ClearDirectory(*d);' in text, 'in-place decoder reset missing')
        require('-O3' in PLATFORMIO.read_text(), 'glyph_mk6 O3 flag missing')
        framework = FRAMEWORK_MAIN.read_text()
        require('bool core1_separate_stack __attribute__((weak)) = false;' in framework,
                'pinned framework default core1 stack model changed')
        require('multicore_launch_core1(main1);' in framework, 'pinned default launch path changed')
        with tempfile.TemporaryDirectory(prefix='glyph-profile-stack-') as raw:
            directory = Path(raw); generated = directory/'generated'; generated.mkdir()
            nanopb = Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB', str(NANOPB)))
            schema = ROOT/'schema/haybox'
            subprocess.run([sys.executable, str(nanopb/'generator/nanopb_generator.py'), '-I', str(schema),
                '-f', str(schema/'config.options'), '--error-on-unmatched', '--no-timestamp',
                '-D', str(generated), str(schema/'config.proto')], check=True, capture_output=True)
            # Preserve the historical F6 2620-byte local-copy failure exactly;
            # it is independent of the larger v2 metadata/root representation.
            old = stack_usage(callback_source('old', True), 'old', directory)
            current = compile_production(text, 'current_v2', directory, generated)
            measured = {name:frame(current,name) for name in
                ('DecodeDirectory(', 'ProfileStore::Bootstrap(', 'ProfileStore::ReadRoot(',
                 'ProfileStore::Begin(', 'ProfileStore::BeginRecovery(')}
            require(measured['DecodeDirectory('] <= 128, 'v2 decoder frame exceeds 128 bytes')
            require(measured['ProfileStore::Bootstrap('] <= 512, 'boot path with inlined deployed-v1 decoder exceeds 512 bytes')
            for name in ('ProfileStore::ReadRoot(', 'ProfileStore::Begin(', 'ProfileStore::BeginRecovery('):
                require(measured[name] <= 128, name+' frame exceeds 128 bytes')
            # Recent compiler-proven regression: Directory{} assignments create
            # a nearly 4KiB automatic temporary despite concise source syntax.
            mutant = text.replace('ClearDirectory(*d);', '*d={};')
            mutant = mutant.replace('ClearDirectory(*_directory);', '*_directory={};')
            mutated = compile_production(mutant, 'old_directory_temporary', directory, generated)
            temporary = {name:frame(mutated,name) for name in ('DecodeLegacy(', 'ProfileStore::Begin(')}
            require(all(value > RESERVED_STACK_BYTES for value in temporary.values()),
                    'Directory{} negative control no longer proves reservation overflow: '+str(temporary))
        require(old > RESERVED_STACK_BYTES, 'historical F6 copy no longer exceeds reservation')
    except (AssertionError, OSError, subprocess.CalledProcessError) as error:
        print(f'glyph_profile_store_directory_stack: FAIL: {error}')
        return 1
    print('glyph_profile_store_directory_stack: PASS')
    print('historical_f6_copy_bytes='+str(old)+' actual_v2_frames='+str(measured)+
          ' directory_temporary_negative='+str(temporary)+
          ' reservation_bytes=2048 scratch_bank_envelope_bytes=4096 whole_target_bound=NOT_CLAIMED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
