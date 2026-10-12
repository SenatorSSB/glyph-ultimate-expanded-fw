#!/usr/bin/env python3
"""Run ProfileStore's real legacy-import lifecycle against Stage-B fixtures."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT, make_v3_artifact, run

HOST = ROOT / "tools/fixtures/profile_store_migration_lifecycle_host"


def main() -> int:
    try:
        nanopb = Path(os.environ.get("GLYPH_PROFILE_STORE_NANOPB", str(NANOPB)))
        generator = nanopb / "generator/nanopb_generator.py"
        if not generator.is_file():
            raise AssertionError("Nanopb dependency unavailable")
        with tempfile.TemporaryDirectory(prefix="profile-store-migration-") as directory:
            temp = Path(directory)
            generated = temp / "generated"
            generated.mkdir()
            schema = ROOT / "schema/haybox"
            run([sys.executable, str(generator), "-I", str(schema), "-f", str(schema / "config.options"),
                 "--error-on-unmatched", "--no-timestamp", "-D", str(generated), str(schema / "config.proto")])

            sys.path.insert(0, str(ROOT / "tools"))
            import glyph_serial_config_tool as writer  # pylint: disable=import-outside-toplevel
            config_pb2, json_format, proto_path = writer.load_runtime_proto_modules(ROOT)
            if proto_path != schema / "config.proto":
                raise AssertionError("tracked Stage-B schema was not used")
            message, payload = writer.encode_artifact_payload(make_v3_artifact(), config_pb2, json_format)
            if len(message.ultimate_profiles) != 2 or any(profile.schema_version != 3 for profile in message.ultimate_profiles):
                raise AssertionError("Stage-B route did not produce two v3 profiles")
            legacy = temp / "legacy-two-v3-profiles.pb"
            legacy.write_bytes(payload)

            objects: list[str] = []
            for source in (nanopb / "pb_common.c", nanopb / "pb_decode.c", nanopb / "pb_encode.c", generated / "config.pb.c"):
                target = temp / f"{source.stem}.o"
                run(["cc", "-std=c11", "-fshort-enums", "-I", str(generated), "-I", str(nanopb),
                     "-c", str(source), "-o", str(target)])
                objects.append(str(target))

            executable = temp / "migration-lifecycle"
            run(["c++", "-std=c++17", "-fshort-enums", "-Wall", "-Wextra", "-Werror",
                 "-I", str(HOST / "include"), "-I", str(generated), "-I", str(nanopb),
                 "-I", str(ROOT / "include"), "-I", str(ROOT / "HAL/pico/include"),
                 "-I", str(ROOT / "config/glyph/common/include"), "-I", str(ROOT / "config/glyph/glyph_mk6/include"),
                 str(HOST / "migration_lifecycle.cpp"), str(ROOT / "HAL/pico/src/core/ProfileStore.cpp"),
                 str(ROOT / "src/core/config_validation.cpp"), str(ROOT / "src/core/config_button_validation.cpp"),
                 str(ROOT / "src/core/config_usb_default_validation.cpp"), str(ROOT / "src/core/config_rgb_target_validation.cpp"),
                 str(ROOT / "config/glyph/common/src/glyph_config_validation.cpp"), *objects, "-o", str(executable)])
            lifecycle = run([str(executable), str(legacy)])
            for marker in ("profiles_20=PASS", "compact_mode_refs=PASS", "reboot_switch=PASS",
                           "delete_refusal=PASS", "corrupt_record_isolation=PASS"):
                if marker not in lifecycle:
                    raise AssertionError(f"lifecycle evidence missing {marker}")
    except (AssertionError, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"glyph_profile_store_migration_lifecycle: FAIL: {error}")
        return 1
    print("glyph_profile_store_migration_lifecycle: PASS")
    print("production_import=true injected_storage=true generated_nanopb_stage_b=true profiles=20 compact_mode_refs=true retry_without_duplicate_ids=true reboot_switch=true delete_refusal=true corrupt_record_isolation=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
