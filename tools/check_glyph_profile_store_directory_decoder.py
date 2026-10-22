#!/usr/bin/env python3
"""Compare the repaired direct decoder with the reconstructed F6 copy path."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT, run

FIXTURE = ROOT / "tools/fixtures/profile_store_directory_decoder_host.cpp"
PROFILE = ROOT / "HAL/pico/src/core/ProfileStore.cpp"
HOST = ROOT / "tools/fixtures/profile_store_migration_lifecycle_host/include"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def compile_variant(temp: Path, generated: Path, name: str, old_copy: bool) -> None:
    source = PROFILE.read_text(encoding="utf-8")
    if old_copy:
        # Retain the old F6 local-copy pattern as a semantic control around
        # the actual v2 decoder. The separate ARM checker retains the exact
        # historical 2620-byte F6 reservation failure proof.
        source += "\nbool DecodeDirectoryF6Control(const uint8_t *bytes, size_t length, ProfileStore::Directory *directory) { uint8_t wire[kDirectoryWireBytes]; if(length != sizeof(wire)) return false; std::memcpy(wire, bytes, sizeof(wire)); return DecodeDirectory(wire, length, directory); }\n"
        source += "#define DIRECTORY_DECODE_UNDER_TEST DecodeDirectoryF6Control\n"
    else:
        source += "\n#define DIRECTORY_DECODE_UNDER_TEST DecodeDirectory\n"
    # Directory is deliberately private in production. The host fixture includes
    # this source directly so its semantic corpus can call the internal decoder.
    source = source.replace('#include "core/ProfileStore.hpp"', '#define private public\n#include "core/ProfileStore.hpp"\n#undef private', 1)
    under_test = temp / "ProfileStore.under_test.cpp"
    under_test.write_text(source, encoding="utf-8")
    nanopb = Path(os.environ.get("GLYPH_PROFILE_STORE_NANOPB", str(NANOPB)))
    libs = ROOT / ".pio/libdeps/glyph_mk6"
    includes = [temp, HOST, ROOT / "HAL/pico/include", ROOT / "include", generated, nanopb,
                libs / "nanopb-arduino/src", ROOT / "config/glyph/common/include",
                ROOT / "config/glyph/glyph_mk6/include"]
    objects: list[Path] = []
    for unit in (nanopb / "pb_common.c", nanopb / "pb_decode.c", nanopb / "pb_encode.c", generated / "config.pb.c"):
        obj = temp / f"{unit.stem}-{name}.o"
        run(["cc", "-std=c11", "-fshort-enums", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-I", str(generated), "-I", str(nanopb), "-c", str(unit), "-o", str(obj)])
        objects.append(obj)
    for unit in (ROOT / "src/modes/UltimateNativeProfile.cpp", ROOT / "src/core/config_validation.cpp", ROOT / "src/core/config_button_validation.cpp",
                 ROOT / "src/core/config_usb_default_validation.cpp", ROOT / "src/core/config_rgb_target_validation.cpp",
                 ROOT / "config/glyph/common/src/glyph_config_validation.cpp"):
        obj = temp / f"{unit.stem}-{name}.o"
        run(["c++", "-std=c++17", "-DARDUINO=1", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fshort-enums", "-Wall", "-Wextra", "-Werror", "-Wno-misleading-indentation", "-Wno-unused-function", "-ffunction-sections", "-fdata-sections",
             *sum((["-I", str(item)] for item in includes[1:]), []), "-c", str(unit), "-o", str(obj)])
        objects.append(obj)
    exe = temp / name
    run(["c++", "-std=c++17", "-DARDUINO=1", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fshort-enums", "-Wall", "-Wextra", "-Werror", "-Wno-misleading-indentation", "-Wno-unused-function", "-ffunction-sections", "-fdata-sections",
         *sum((["-I", str(item)] for item in includes), []), str(FIXTURE), *map(str, objects), *( ["-Wl,-dead_strip"] if sys.platform == "darwin" else ["-Wl,--gc-sections"] ), "-o", str(exe)])
    result = run([str(exe)])
    require("profile_store_directory_decoder_semantics=PASS" in result, f"{name} semantic corpus failed")


def main() -> int:
    try:
        nanopb = Path(os.environ.get("GLYPH_PROFILE_STORE_NANOPB", str(NANOPB)))
        generator = nanopb / "generator/nanopb_generator.py"
        require(generator.is_file(), "Nanopb dependency unavailable; run python3 -m platformio run -e glyph_mk6")
        with tempfile.TemporaryDirectory(prefix="glyph-directory-decoder-") as raw:
            temp = Path(raw); generated = temp / "generated"; generated.mkdir()
            schema = ROOT / "schema/haybox"
            run(["python3", str(generator), "-I", str(schema), "-f", str(schema / "config.options"),
                 "--error-on-unmatched", "--no-timestamp", "-D", str(generated), str(schema / "config.proto")])
            compile_variant(temp, generated, "old_f6_copy", True)
            compile_variant(temp, generated, "repaired_direct", False)
    except (AssertionError, OSError, subprocess.CalledProcessError) as error:
        print(f"glyph_profile_store_directory_decoder: FAIL: {error}")
        return 1
    print("glyph_profile_store_directory_decoder: PASS")
    print("variants=old_f6_copy,repaired_direct format=v2 deployed_v1_reader=true malformed_metadata=true full_names=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
