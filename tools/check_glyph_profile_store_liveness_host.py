#!/usr/bin/env python3
"""Long-session actual ProfileStore + pinned LittleFS source diagnosis, no device I/O.

Storage-layer response loss means the returned transaction result is discarded,
then queried and exactly replayed. Serial/COBS/TinyUSB are tested separately.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT, make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK

HOST = ROOT / "tools/fixtures/profile_store_liveness_host"
FROZEN = "594066d9bb65b9f93c14e0e24e9d2002c3f83924"
SOURCES = ["HAL/pico/src/core/ProfileStore.cpp", "HAL/pico/src/core/CheckedStorage.cpp",
           "include/core/ProfileStore.hpp", "include/core/ProfileStoreStorage.hpp",
           "include/core/ProfileStoreFaultControls.hpp", "include/core/CheckedStorage.hpp"]


def run(args, *, timeout=180, expect_failure=False):
    result = subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True,
                            text=True, timeout=timeout,
                            env={**os.environ, "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"})
    if (result.returncode != 0) != expect_failure:
        raise RuntimeError(" ".join(map(str, args)) + "\n" + result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    report = {"frozen_candidate": FROZEN, "physical_device_actions": 0,
              "hardware_liveness_proven": False, "runs": {}, "source_sha256": {}}
    try:
        if json.loads((FRAMEWORK / "package.json").read_text())["version"] != "1.30603.0":
            raise RuntimeError("expected pinned Arduino-Pico 3.6.3")
        nanopb = Path(os.environ.get("GLYPH_PROFILE_STORE_NANOPB", str(NANOPB)))
        flags = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g", "-O1"]
        with tempfile.TemporaryDirectory(prefix="glyph-liveness-host-") as directory:
            temp = Path(directory)
            generated = temp / "generated"
            generated.mkdir()
            schema = ROOT / "schema/haybox"
            run([sys.executable, nanopb / "generator/nanopb_generator.py", "-I", schema,
                 "-f", schema / "config.options", "--error-on-unmatched", "--no-timestamp",
                 "-D", generated, schema / "config.proto"])
            import glyph_serial_config_tool as writer
            config_pb2, json_format, _ = writer.load_runtime_proto_modules(ROOT)
            _, payload = writer.encode_artifact_payload(make_v3_artifact(), config_pb2, json_format)
            fixture = temp / "legacy.pb"
            fixture.write_bytes(payload)
            library = FRAMEWORK / "libraries/LittleFS"
            includes = [generated, nanopb, ROOT / "include", ROOT / "HAL/pico/include",
                        ROOT / "config/glyph/common/include", ROOT / "config/glyph/glyph_mk6/include",
                        library / "lib/littlefs"]
            inc = [item for path in includes for item in ["-I", path]]
            objects = []
            for source in [nanopb / "pb_common.c", nanopb / "pb_decode.c", nanopb / "pb_encode.c",
                           generated / "config.pb.c", library / "src/lfs.c", library / "src/lfs_util.c"]:
                obj = temp / (source.stem + ".o")
                alloc = (["-include", HOST / "lfs_alloc.h", "-Dmalloc=liveness_lfs_malloc",
                          "-Dfree=liveness_lfs_free"] if source.stem.startswith("lfs") else [])
                run(["cc", "-std=c11", *flags, "-fshort-enums", "-DLFS_NAME_MAX=32", *alloc,
                     *inc, "-c", source, "-o", obj])
                objects.append(obj)
                report["source_sha256"][str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
            frozen = temp / "frozen"
            for relative in SOURCES:
                content = subprocess.run(["git", "show", FROZEN + ":" + relative], cwd=ROOT,
                                         capture_output=True, check=True).stdout
                target = frozen / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            validation = [ROOT / p for p in ["src/core/config_validation.cpp", "src/core/config_button_validation.cpp",
                          "src/core/config_usb_default_validation.cpp", "src/core/config_rgb_target_validation.cpp",
                          "config/glyph/common/src/glyph_config_validation.cpp"]]
            for name, source_root, extra in [("frozen_candidate", frozen, ["-DLIVENESS_FROZEN_ARM=1"]),
                                             ("current_candidate", ROOT, [])]:
                probe = temp / (name + "_mounted.cpp")
                probe.write_text('#include ' + json.dumps(str(source_root / SOURCES[0])) + '\n'
                                 'bool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n)'
                                 '{ MountedStorage s; return s.ReadRange(p,o,b,n); }\n')
                executable = temp / name
                compile_command = ["c++", "-std=c++17", *flags, "-fshort-enums", "-Wall", "-Wextra", "-Werror",
                                   "-DLFS_NAME_MAX=32", "-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1",
                                   "-DGLYPH_STRICT_HARDENING_CANDIDATE=1", *extra,
                                   "-I", source_root / "include", *inc,
                                   HOST / "liveness_harness.cpp", probe, source_root / SOURCES[1],
                                   *validation, *objects, "-o", executable]
                run(compile_command)
                output = run([executable, fixture])
                report["runs"][name] = {"result": "PASS", "output": output}
                print(name + ":\n" + output, flush=True)
            # Deliberate bounded mutation proves the leak oracle catches the exact
            # suspected missing-close mechanism. It is not an old production bug.
            mutant_source = (frozen / SOURCES[1]).read_text()
            needle = "if (!r && f.opened) { lfs_file_close(fs, handle(f)); f.opened = false; }"
            if mutant_source.count(needle) != 1:
                raise RuntimeError("missing-close negative control anchor changed")
            mutant = temp / "CheckedStorage.missing-close.cpp"
            mutant.write_text(mutant_source.replace(needle, "/* deliberate negative control: leak native open */"))
            negative = temp / "missing-close-negative"
            command = ["c++", "-std=c++17", *flags, "-fshort-enums", "-Wall", "-Wextra", "-Werror",
                       "-DLFS_NAME_MAX=32", "-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1",
                       "-DGLYPH_STRICT_HARDENING_CANDIDATE=1", "-DLIVENESS_FROZEN_ARM=1",
                       "-I", frozen / "include", *inc, HOST / "liveness_harness.cpp",
                       temp / "frozen_candidate_mounted.cpp", mutant, *validation, *objects, "-o", negative]
            run(command)
            negative_output = run([negative, fixture], expect_failure=True)
            if "native LittleFS handle retained" not in negative_output:
                raise RuntimeError("missing-close negative did not fail at intended handle oracle: " + negative_output)
            report["runs"]["deliberate_missing_close_negative"] = {"result": "DETECTED", "output": negative_output}
            print("deliberate_missing_close_negative=DETECTED (not historical source)\n" + negative_output, flush=True)
        for relative in SOURCES + ["tools/fixtures/profile_store_liveness_host/liveness_harness.cpp",
                                   "tools/fixtures/profile_store_liveness_host/lfs_alloc.h", str(Path(__file__).relative_to(ROOT))]:
            report["source_sha256"][relative] = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        report["result"] = "PASS"
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print("glyph_profile_store_liveness_host: PASS; old and current storage campaign responsive; physical root cause remains UNPROVEN")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print("glyph_profile_store_liveness_host: FAIL: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
