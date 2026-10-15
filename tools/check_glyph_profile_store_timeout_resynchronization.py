#!/usr/bin/env python3
"""Exercise real Configurator/ProfileStore framing, timeout, and 8 KiB recovery."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT, make_v3_artifact, run

HOST = ROOT / "tools/fixtures/profile_store_timeout_host"


SANITIZERS = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"] if os.environ.get("GLYPH_PROFILE_STORE_SANITIZERS") == "1" else []


def invoke(command: list[str]) -> str:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=30, env={**os.environ, "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"})
    if completed.returncode:
        raise RuntimeError("command failed:\n" + " ".join(command) + "\n" + completed.stdout + completed.stderr)
    return completed.stdout


def compile_object(source: Path, target: Path, includes: list[Path], extra: list[str] | None = None) -> None:
    invoke(["c++", *SANITIZERS, "-std=c++17", "-DARDUINO=1", "-fshort-enums", "-Wall", "-Wextra", "-Werror", "-Wno-error=missing-field-initializers", "-Wno-error=inconsistent-missing-override", *(extra or []),
            *sum((["-I", str(item)] for item in includes), []), "-c", str(source), "-o", str(target)])


def build_and_run(temp: Path, generated: Path, fixture: Path, original: bool, legacy_record_temp: bool = False, strict_only: bool = False, candidate_faults: bool = False) -> None:
    nanopb = Path(os.environ.get("GLYPH_PROFILE_STORE_NANOPB", str(NANOPB)))
    libs = ROOT / ".pio/libdeps/glyph_mk6"
    includes = [HOST / "include", ROOT / "HAL/pico/include", ROOT / "include", generated, nanopb,
                libs / "nanopb-arduino/src", libs / "PacketIO/src", ROOT / "config/glyph/common/include",
                ROOT / "config/glyph/glyph_mk6/include"]
    objects: list[Path] = []
    for name, source in (("pb_common", nanopb / "pb_common.c"), ("pb_decode", nanopb / "pb_decode.c"),
                         ("pb_encode", nanopb / "pb_encode.c"), ("config", generated / "config.pb.c")):
        target = temp / f"{name}.o"
        invoke(["cc", *SANITIZERS, "-std=c11", "-fshort-enums", "-I", str(generated), "-I", str(nanopb),
                "-c", str(source), "-o", str(target)])
        objects.append(target)
    profile = temp / "profile.o"
    profile_source = ROOT / "HAL/pico/src/core/ProfileStore.cpp"
    if legacy_record_temp:
        profile_source = temp / "ProfileStore.legacy-temp.cpp"
        text = (ROOT / "HAL/pico/src/core/ProfileStore.cpp").read_text(encoding="utf-8")
        pattern = r"ProfileStorePaths::RecordTemporaryPath\(temp,\s*sizeof\(temp\),\s*id,\s*rev\);"
        if not re.search(pattern,text):
            raise AssertionError("record temporary path repair shape missing")
        text=re.sub(r"char path\[32\],\s*temp\[32\];","char path[64],temp[64];",text,count=1)
        text=re.sub(pattern,'std::snprintf(temp,sizeof(temp),"%s.tmp",path);',text,count=1)
        profile_source.write_text(text,encoding="utf-8")
    compile_object(profile_source, profile, includes, ["-Dprofile_store=production_profile_store"])
    objects.append(profile)
    for name, source in (("checked_unavailable", HOST / "checked_storage_unavailable.cpp"),
                         ("validation", ROOT / "src/core/config_validation.cpp"),
                         ("button", ROOT / "src/core/config_button_validation.cpp"),
                         ("usb", ROOT / "src/core/config_usb_default_validation.cpp"),
                         ("rgb", ROOT / "src/core/config_rgb_target_validation.cpp"),
                         ("glyph", ROOT / "config/glyph/common/src/glyph_config_validation.cpp"),
                         ("arduino_pb", libs / "nanopb-arduino/src/pb_arduino.cpp")):
        target = temp / f"{name}.o"; compile_object(source, target, includes); objects.append(target)
    backend_source = ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp"
    if original:
        backend_source = temp / "ConfiguratorBackend.original.cpp"
        text = (ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp").read_text(encoding="utf-8")
        needle = "            HandleProfileStore();\n            return;"
        if needle not in text:
            raise AssertionError("repair shape missing for duplicate-next negative control")
        backend_source.write_text(text.replace(needle, "            HandleProfileStore();\n            break;", 1), encoding="utf-8")
    backend = temp / ("backend-original.o" if original else "backend.o")
    compile_object(backend_source, backend, includes, ["-DGLYPH_STRICT_HARDENING_CANDIDATE=1"] if candidate_faults else []); objects.append(backend)
    exe = temp / ("original" if original else "repaired")
    flags = (["-DEXPECT_DUPLICATE_NEXT_DROP"] if original else []) + (["-DEXPECT_LEGACY_RECORD_TEMP_PATH"] if legacy_record_temp else []) + (["-DGLYPH_STRICT_HARDENING_CANDIDATE=1"] if candidate_faults else [])
    invoke(["c++", *SANITIZERS, "-std=c++17", "-DARDUINO=1", "-fshort-enums", "-Wall", "-Wextra", "-Werror", "-Wno-error=inconsistent-missing-override", "-Wno-error=unused-function", *flags,
            *sum((["-I", str(item)] for item in includes), []), str(HOST / "timeout_harness.cpp"),
            *map(str, objects), "-o", str(exe)])
    if strict_only:
        result = invoke([str(exe), str(fixture), "--strict-protocol"])
        if "profile_store_strict_protocol=PASS" not in result:
            raise AssertionError("strict protocol evidence missing")
        print(result.strip())
        return
    invoke([str(exe), str(fixture)])
    if not original:
        empty_create = invoke([str(exe), str(fixture), "--empty-create"])
        if "profile_store_full_stream_empty_create=PASS" not in empty_create:
            raise AssertionError("full-stream empty CREATE evidence missing")
        for mode in ("--io-temp-open-write", "--io-temp-write", "--io-temp-read", "--io-verify",
                     "--io-dest-remove", "--io-rename"):
            diagnostic = invoke([str(exe), str(fixture), mode])
            if "profile_store_full_stream_create_diagnostic=PASS" not in diagnostic:
                raise AssertionError(f"full-stream CREATE diagnostic evidence missing for {mode}")
        reset = invoke([str(exe), str(fixture), "--io-stale-reset"])
        if "profile_store_full_stream_diagnostic_reset=PASS" not in reset:
            raise AssertionError("request-bound diagnostic reset evidence missing")
        path_limited_create = invoke([str(exe), str(fixture), "--path-limit-create"])
        if legacy_record_temp:
            if "profile_store_full_stream_legacy_path_rejected=PASS" not in path_limited_create:
                raise AssertionError("legacy temporary-name rejection evidence missing")
        else:
            if "profile_store_full_stream_path_limited_create=PASS" not in path_limited_create:
                raise AssertionError("strict LittleFS component-limit CREATE evidence missing")
            for mode, marker in ([(f"--deep-create-{mask}", "profile_store_stale_files_root_rotation=PASS") for mask in range(16)] + [(f"--drop-create-response-{budget}", "profile_store_successful_commit_tx_failure=PASS") for budget in range(4)]):
                if marker not in invoke([str(exe), str(fixture), mode]):
                    raise AssertionError(f"deep CREATE evidence missing for {mode}")
            for mode, marker in (("--root-faults", "profile_store_root_corruption_fail_closed=PASS"), ("--reference-purity", "profile_store_reference_transactional_purity=PASS"), ("--direct-create-replay", "profile_store_direct_create_replay=PASS")):
                if marker not in invoke([str(exe), str(fixture), mode]):
                    raise AssertionError(f"reference/replay evidence missing for {mode}")
            for mode in ("--old-valid-record", "--old-valid-directory"):
                if "profile_store_old_valid_readback_rejected=PASS" not in invoke([str(exe), str(fixture), mode]):
                    raise AssertionError(f"old valid readback control missing for {mode}")
            path_limited_import = invoke([str(exe), str(fixture), "--path-limit-import"])
            if "profile_store_strict_path_import=PASS" not in path_limited_import:
                raise AssertionError("strict LittleFS component-limit ImportLegacy evidence missing")
            for mode in ("--directory-temp-open", "--directory-temp-write", "--directory-temp-read",
                         "--directory-temp-size", "--directory-verify", "--directory-dest-remove",
                         "--directory-rename"):
                directory = invoke([str(exe), str(fixture), mode])
                if "profile_store_full_stream_directory_diagnostic=PASS" not in directory:
                    raise AssertionError(f"directory diagnostic evidence missing for {mode}")


def main() -> int:
    try:
        nanopb = Path(os.environ.get("GLYPH_PROFILE_STORE_NANOPB", str(NANOPB)))
        generator = nanopb / "generator/nanopb_generator.py"
        if not generator.is_file():
            raise AssertionError("Nanopb dependency unavailable; run python3 -m platformio run -e glyph_mk6")
        with tempfile.TemporaryDirectory(prefix="glyph-profile-configurator-") as directory:
            temp = Path(directory); generated = temp / "generated"; generated.mkdir()
            schema = ROOT / "schema/haybox"
            run([sys.executable, str(generator), "-I", str(schema), "-f", str(schema / "config.options"),
                 "--error-on-unmatched", "--no-timestamp", "-D", str(generated), str(schema / "config.proto")])
            sys.path.insert(0, str(ROOT / "tools"))
            import glyph_serial_config_tool as writer  # pylint: disable=import-outside-toplevel
            config_pb2, json_format, _ = writer.load_runtime_proto_modules(ROOT)
            _, payload = writer.encode_artifact_payload(make_v3_artifact(), config_pb2, json_format)
            fixture = temp / "stage-b-two-v3.pb"; fixture.write_bytes(payload)
            build_and_run(temp, generated, fixture, True)
            legacy = build_and_run(temp, generated, fixture, False, True)
            build_and_run(temp, generated, fixture, False)
    except (AssertionError, OSError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as error:
        print(f"glyph_profile_store_timeout_resynchronization: FAIL: {error}")
        return 1
    print("glyph_profile_store_timeout_resynchronization: PASS")
    print(f"sanitizers={bool(SANITIZERS)}")
    print("real_configurator=true real_packetio_cobs=true real_nanopb=true real_profile_store=true duplex_rx_tx=true empty_create=true io_stage_diagnostics=temp_open_write,temp_write,temp_read,verify,rename destination_remove_gap_absent=true directory_diagnostics=temp_open_write,temp_write,temp_read,temp_size,verify,rename diagnostic_reset=true pinned_littlefs_component_limit=31 legacy_temp_rejected=true path_limited_create=true path_limited_import=true stale_file_combinations=16 root_rotation_creates=512 rotating_directory_failure_stages=6 old_valid_record_and_root_rejected=true root_corruption_fail_closed=true invalid_root_is_not_empty=true ambiguous_root_readonly=true reference_durable_live_separation=true reference_failure_atomicity=true reference_generation_races=true durable_and_live_delete_guards=true direct_create_replay_nonmutation=true tx_failure_budgets=0,1,7 tx_failure_transaction_recovery=true tx_no_space=true tx_short_write=true tx_deadline_ms=2000 retained_transport_resync=true consecutive_list=3 duplicate_next_negative=true crud=create,read,update,rename,reorder,duplicate,set_reference,delete,query timeout_boundary_ms=5000 timeout_nonmutation=config,storage,count,generation,save_count timeout_resync=true frame_cap=8192 external_timeout_seconds=30")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
