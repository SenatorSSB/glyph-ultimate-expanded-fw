#!/usr/bin/env python3
"""Compile the real ConfiguratorBackend with PacketIO COBS and prove timeout recovery."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "tools/fixtures/profile_store_timeout_host"
BUILD = ROOT / ".pio/build/glyph_mk6/nanopb/generated-src"
LIBS = ROOT / ".pio/libdeps/glyph_mk6"


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError("command failed:\n" + " ".join(command) + "\n" + completed.stdout + completed.stderr)


def main() -> int:
    try:
        source = (ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp").read_text(encoding="utf-8")
        if "static constexpr size_t kFrameLimit = 8192;" not in source:
            raise AssertionError("production 8 KiB profile-store cap missing")
        if "Profile store frame timeout" not in source or "millis() - last_progress" not in source:
            raise AssertionError("production inactivity timeout missing")
        required = [BUILD / "config.pb.h", BUILD / "config.pb.c", LIBS / "PacketIO/src/cobs/Stream.h",
                    LIBS / "Nanopb/pb_decode.c", LIBS / "nanopb-arduino/src/pb_arduino.cpp"]
        if not all(path.is_file() for path in required):
            raise AssertionError("run python3 -m platformio run -e glyph_mk6 first to provision pinned host inputs")
        with tempfile.TemporaryDirectory(prefix="glyph-profile-timeout-") as directory:
            temp = Path(directory)
            objects: list[Path] = []
            for name in ("pb_common", "pb_decode", "pb_encode", "config.pb"):
                source_path = BUILD / "config.pb.c" if name == "config.pb" else LIBS / "Nanopb" / f"{name}.c"
                object_path = temp / f"{name}.o"
                run(["cc", "-std=c11", "-fshort-enums", "-I", str(BUILD), "-I", str(LIBS / "Nanopb"),
                     "-c", str(source_path), "-o", str(object_path)])
                objects.append(object_path)
            executable = temp / "timeout"
            run(["c++", "-std=c++17", "-DARDUINO=1", "-fshort-enums", "-Wall", "-Wextra",
                 "-I", str(HOST / "include"), "-I", str(ROOT / "HAL/pico/include"), "-I", str(ROOT / "include"),
                 "-I", str(BUILD), "-I", str(LIBS / "Nanopb"), "-I", str(LIBS / "nanopb-arduino/src"),
                 "-I", str(LIBS / "PacketIO/src"), str(HOST / "timeout_harness.cpp"),
                 str(ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp"),
                 str(LIBS / "nanopb-arduino/src/pb_arduino.cpp"), *map(str, objects), "-o", str(executable)])
            run([str(executable)])
    except (AssertionError, OSError, RuntimeError) as error:
        print(f"glyph_profile_store_timeout_resynchronization: FAIL: {error}")
        return 1
    print("glyph_profile_store_timeout_resynchronization: PASS")
    print("real_configurator=true real_packetio_cobs=true virtual_timeout=true no_mutation=true delimiter_resync=true later_status=true frame_cap=8192")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
