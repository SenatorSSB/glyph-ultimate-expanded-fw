#!/usr/bin/env python3
"""Exercise the Stage-A Ultimate profile artifact through the guarded dry-run path."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRITER = ROOT / "tools" / "glyph_serial_config_tool.py"
FIXTURE = ROOT / "tools" / "fixtures" / "stage_a_ultimate_profiles_dry_run.json"


class CheckFailure(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run_dry_run() -> str:
    result = subprocess.run(
        [sys.executable, str(WRITER), "--dry-run", "--artifact", str(FIXTURE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    require(result.returncode == 0, f"guarded dry-run failed: {output}")
    required = (
        f"proto_source={ROOT / 'schema' / 'haybox' / 'config.proto'}",
        "protocol_source_confirmed=true",
        "status=PASS",
        "mode=dry_run",
        "artifact_validated=true",
        "live_device_access=false",
        "active_device_profile_updated=false",
        "readback_verified=false",
        "firmware_flashing=false",
        "dry_run_serial_opened=false",
    )
    for phrase in required:
        require(phrase in output, f"dry-run output missing {phrase!r}")
    return output


def verify_artifact_shape() -> None:
    artifact = json.loads(FIXTURE.read_text(encoding="utf-8"))
    modes = artifact["gameModeConfigs"]
    require(len(modes) == 3, "fixture must contain legacy plus two profile-bound Ultimate modes")
    require([mode["ultimateProfileConfig"] for mode in modes] == [0, 1, 2],
            "Ultimate mode references must be explicit legacy/one/two values")
    require(all(mode["modeId"] == "MODE_ULTIMATE" for mode in modes),
            "fixture controls must all be MODE_ULTIMATE")
    require(len({mode["name"] for mode in modes}) == 1,
            "fixture deliberately proves duplicate display names do not select profiles")

    profiles = artifact["ultimateProfiles"]
    require(len(profiles) == 2, "fixture must contain exactly two Stage-A profiles")
    for profile_index, profile in enumerate(profiles):
        require(profile["schemaVersion"] == 1, f"profile {profile_index} has wrong schema version")
        tables = profile["tables"]
        require(len(tables) == 28, f"profile {profile_index} must have all 28 tables")
        require([table["tableId"] for table in tables] == list(range(28)),
                f"profile {profile_index} table IDs must be explicit and ordered")
        require(all(len(table["coordinates"]) == 9 for table in tables),
                f"profile {profile_index} must have nine coordinates per table")
    require(profiles[0]["tables"][27]["coordinates"][0] == {"x": 89, "y": 89},
            "profile A must preserve the source-owned baseline value")
    require(profiles[1]["tables"][27]["coordinates"][0] == {"x": 90, "y": 89},
            "profile B must contain the one declared distinguishable coordinate change")


def verify_production_admission(message, encoded: bytes, config_pb2) -> None:
    """Decode the actual wire artifact and call the complete production Glyph validator.

    Regenerate Nanopb from tracked schema/options; cached generated config bindings
    and Python writer validation are deliberately not admission evidence.
    """
    nanopb = ROOT / ".pio/libdeps/glyph_mk6/Nanopb"
    generator = nanopb / "generator/nanopb_generator.py"
    require(generator.is_file(), "Nanopb dependency unavailable; prepare PlatformIO dependencies")

    def run(command: list[str]) -> str:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        require(result.returncode == 0,
                f"production admission command failed: {' '.join(command)}\n"
                f"{result.stdout}\n{result.stderr}")
        return result.stdout

    with tempfile.TemporaryDirectory(prefix="stage-a-admission-") as temporary:
        temp = Path(temporary)
        schema = ROOT / "schema/haybox"
        run([sys.executable, str(generator), "-I", str(schema), "-f",
             str(schema / "config.options"), "--error-on-unmatched", "--no-timestamp",
             "-D", str(temp), str(schema / "config.proto")])
        # Compile decoder and descriptors as C, matching firmware language selection.
        objects = []
        for source in (nanopb / "pb_common.c", nanopb / "pb_decode.c", temp / "config.pb.c"):
            target = temp / (source.stem + ".o")
            run(["cc", "-std=c11", "-fshort-enums", "-I", str(temp), "-I", str(nanopb),
                 "-c", str(source), "-o", str(target)])
            objects.append(str(target))
        executable = temp / "admission"
        run(["c++", "-std=c++17", "-fshort-enums", "-Wall", "-Wextra", "-Werror",
             "-I", str(temp), "-I", str(nanopb), "-I", str(ROOT / "include"),
             "-I", str(ROOT / "config/glyph/common/include"),
             "-I", str(ROOT / "config/glyph/glyph_mk6/include"),
             str(ROOT / "tools/fixtures/stage_a_ultimate_profiles_host/admission.cpp"),
             str(ROOT / "src/core/config_validation.cpp"),
             str(ROOT / "src/core/config_button_validation.cpp"),
             str(ROOT / "src/core/config_rgb_target_validation.cpp"),
             str(ROOT / "config/glyph/common/src/glyph_config_validation.cpp"),
             *objects, "-o", str(executable)])

        def check_payload(label: str, payload: bytes, expected: bool) -> None:
            path = temp / (label + ".bin")
            path.write_bytes(payload)
            run([str(executable), str(path), "1" if expected else "0"])

        check_payload("fixture", encoded, True)
        # Historical F evidence expected zero_usb_default to be refused.  The
        # composed C023 baseline deliberately removed that semantic rejection:
        # this acceptance counterexample fails if the obsolete check is restored.
        c023_zero_usb_default = config_pb2.Config()
        c023_zero_usb_default.CopyFrom(message)
        c023_zero_usb_default.default_usb_backend_config = 0
        check_payload(
            "c023_zero_usb_default_not_semantically_rejected",
            c023_zero_usb_default.SerializeToString(),
            True,
        )
        c023_out_of_range_usb_default = config_pb2.Config()
        c023_out_of_range_usb_default.CopyFrom(message)
        c023_out_of_range_usb_default.default_usb_backend_config = 2
        check_payload(
            "c023_out_of_range_usb_default_not_semantically_rejected",
            c023_out_of_range_usb_default.SerializeToString(),
            True,
        )
        # F historically rejected an empty backend envelope through the same
        # USB-default validator. C023 deliberately does not: retain this as a
        # named current acceptance counterexample rather than an F negative.
        c023_missing_backend_envelope = config_pb2.Config()
        c023_missing_backend_envelope.CopyFrom(message)
        c023_missing_backend_envelope.ClearField("communication_backend_configs")
        c023_missing_backend_envelope.ClearField("default_backend_config")
        c023_missing_backend_envelope.ClearField("default_usb_backend_config")
        check_payload(
            "c023_missing_backend_envelope_not_semantically_rejected",
            c023_missing_backend_envelope.SerializeToString(),
            True,
        )

        # Keep F's historical expectation explicit without treating it as the
        # current composed contract.  The remaining cases are profile and
        # non-USB negatives; incomplete_profile_table is the counterexample
        # that detects deleted or bypassed Ultimate-profile validation.
        mutations = (
            ("invalid_backend_mode", lambda m: setattr(m.communication_backend_configs[0], "default_mode_config", 4)),
            ("invalid_profile_reference", lambda m: setattr(m.game_mode_configs[2], "ultimate_profile_config", 3)),
            ("ultimate_validation_required_incomplete_profile_table",
             lambda m: m.ultimate_profiles[0].tables[0].coordinates.pop()),
        )
        for label, mutate in mutations:
            invalid = config_pb2.Config()
            invalid.CopyFrom(message)
            mutate(invalid)
            check_payload(label, invalid.SerializeToString(), False)
        renamed = config_pb2.Config()
        renamed.CopyFrom(message)
        for index, mode in enumerate(renamed.game_mode_configs):
            mode.name = f"Display {index}"
        check_payload("name_agnostic", renamed.SerializeToString(), True)
        overlong = config_pb2.Config()
        overlong.CopyFrom(message)
        overlong.game_mode_configs[0].name = "Ultimate Runtime Profile"
        path = temp / "overlong_name.bin"
        path.write_bytes(overlong.SerializeToString())
        require("string overflow" in run([str(executable), str(path), "2"]),
                "original overlong name must be rejected by the actual Nanopb decoder")
    print("production_nanopb_decode=true production_glyph_validation=PASS admission_negatives=5 decoder_negatives=1 name_agnostic=PASS")
    print("c023_zero_usb_default=accepted obsolete_usb_check_counterexample=PASS ultimate_validation_counterexample=PASS")


def verify_encoded_fields() -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    import glyph_serial_config_tool as writer  # pylint: disable=import-outside-toplevel

    config_pb2, json_format, proto_path = writer.load_runtime_proto_modules(ROOT)
    require(proto_path == ROOT / "schema" / "haybox" / "config.proto",
            "encoder must compile the tracked schema, not a .pio cache")
    message, encoded = writer.encode_artifact_payload(
        json.loads(FIXTURE.read_text(encoding="utf-8")), config_pb2, json_format
    )
    require(encoded, "dry-run artifact encoding must not be empty")
    decoded = writer.decode_config_payload(encoded, config_pb2)
    require([mode.ultimate_profile_config for mode in decoded.game_mode_configs] == [0, 1, 2],
            "encoded mode references changed")
    require(len(decoded.ultimate_profiles) == 2, "encoded profile count changed")
    require(all(len(profile.tables) == 28 for profile in decoded.ultimate_profiles),
            "encoded table count changed")
    require(all(len(table.coordinates) == 9 for profile in decoded.ultimate_profiles for table in profile.tables),
            "encoded coordinate count changed")
    require(decoded.ultimate_profiles[1].tables[27].coordinates[0].x == 90,
            "encoded profile-B distinguishing coordinate changed")
    require(not writer.verify_required_bindings(message, config_pb2),
            "writer rejected the encoded Stage-A fixture")
    verify_production_admission(message, encoded, config_pb2)

    non_ultimate_reference = config_pb2.Config()
    non_ultimate_reference.CopyFrom(message)
    invalid_mode = non_ultimate_reference.game_mode_configs.add()
    invalid_mode.mode_id = config_pb2.MODE_FGC
    invalid_mode.ultimate_profile_config = 1
    require(
        any("non-Ultimate" in failure
            for failure in writer.verify_required_bindings(non_ultimate_reference, config_pb2)),
        "writer accepted a non-Ultimate profile reference",
    )

    incomplete_stage_a_rows = config_pb2.Config()
    incomplete_stage_a_rows.CopyFrom(message)
    del incomplete_stage_a_rows.game_mode_configs[-1]
    require(
        any("exactly three MODE_ULTIMATE" in failure
            for failure in writer.verify_required_bindings(incomplete_stage_a_rows, config_pb2)),
        "writer accepted an incomplete Stage-A Ultimate row set",
    )


def main() -> int:
    try:
        require(FIXTURE.is_file(), f"missing fixture: {FIXTURE.relative_to(ROOT)}")
        verify_artifact_shape()
        run_dry_run()
        verify_encoded_fields()
    except (CheckFailure, OSError, ValueError, KeyError, TypeError) as error:
        print(f"glyph_stage_a_ultimate_profiles_dry_run: FAIL: {error}")
        return 1

    print("glyph_stage_a_ultimate_profiles_dry_run: PASS")
    print("profiles=2 tables_per_profile=28 coordinates_per_table=9 refs=0,1,2")
    print("serial_opened=false firmware_flashing=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
