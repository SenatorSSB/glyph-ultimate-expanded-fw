#!/usr/bin/env python3
"""Replay the captured physical predecessor Config through real validators."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "6b73a7c507f35c111745c6bdd341618b490cbdcd"
BACKUP = Path(os.environ.get(
    "GLYPH_REAL_PREDECESSOR_BACKUP",
    "/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/"
    "local_backups/hardware-tests/multi-profile-store-20261013/preflash-config-backup.json",
))
HOST = ROOT / "tools/fixtures/profile_store_predecessor_host/replay_validation.cpp"
BUILD = ROOT / ".pio/build/glyph_mk6/nanopb/generated-src"
NANOPB = ROOT / ".pio/libdeps/glyph_mk6/Nanopb"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError("command failed:\n" + " ".join(command) + "\n" + result.stdout + result.stderr)
    return result


def main() -> int:
    try:
        raw = base64.b64decode(json.loads(BACKUP.read_text(encoding="utf-8"))["rawConfigPayloadBase64"], validate=True)
        if len(raw) != 4201 or hashlib.sha256(raw).hexdigest() != "f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480":
            raise AssertionError("captured predecessor fixture identity mismatch")
        if not (BUILD / "config.pb.c").is_file():
            raise AssertionError("run the pinned glyph_mk6 build to provision generated Nanopb inputs")
        with tempfile.TemporaryDirectory(prefix="glyph-real-predecessor-") as directory:
            temp = Path(directory); fixture = temp / "predecessor.pb"; fixture.write_bytes(raw)
            objects: list[Path] = []
            for source in (NANOPB / "pb_common.c", NANOPB / "pb_decode.c", NANOPB / "pb_encode.c", BUILD / "config.pb.c"):
                target = temp / f"{source.stem}.o"
                run(["cc", "-std=c11", "-fshort-enums", "-I", str(BUILD), "-I", str(NANOPB), "-c", str(source), "-o", str(target)])
                objects.append(target)
            includes = [BUILD, NANOPB, ROOT / "include", ROOT / "HAL/pico/include",
                        ROOT / "config/glyph/common/include", ROOT / "config/glyph/glyph_mk6/include"]
            common = [ROOT / "src/core/config_button_validation.cpp", ROOT / "src/core/config_usb_default_validation.cpp",
                      ROOT / "src/core/config_rgb_target_validation.cpp", ROOT / "config/glyph/common/src/glyph_config_validation.cpp"]
            for label, validation in (("candidate", ROOT / "src/core/config_validation.cpp"), ("base", temp / "config_validation_base.cpp")):
                label_includes = includes
                if label == "base":
                    validation.write_text(run(["git", "show", f"{BASE}:src/core/config_validation.cpp"]).stdout, encoding="utf-8")
                    base_include = temp / "base-include"; base_include.mkdir()
                    (base_include / "config_rgb_target_domain.hpp").write_text(
                        run(["git", "show", f"{BASE}:config/glyph/common/include/config_rgb_target_domain.hpp"]).stdout,
                        encoding="utf-8")
                    label_includes = [base_include, *includes]
                exe = temp / label
                run(["c++", "-std=c++17", "-fshort-enums", "-Wall", "-Wextra",
                     *( ["-DBASE_COMPARISON"] if label == "base" else []),
                     *sum((["-I", str(i)] for i in label_includes), []),
                     str(HOST), str(validation), *map(str, common), *map(str, objects), "-o", str(exe)])
                result = run([str(exe), str(fixture)], check=False)
                expected = 0 if label == "candidate" else 1
                if result.returncode != expected:
                    raise AssertionError(f"{label} validator result {result.returncode}, expected {expected}")
                print(f"{label}_exit={result.returncode}")
                print(result.stdout, end="")
    except (AssertionError, OSError, ValueError, RuntimeError) as error:
        print(f"glyph_real_predecessor_config: FAIL: {error}")
        return 1
    print("fixture_bytes=4201 fixture_sha256=f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480 candidate_legacy_admission=PASS base_rgb_rejection=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
