#!/usr/bin/env python3
"""Decode and exercise the finite Stage-B Ultimate profile schema in production code."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "tools/fixtures/stage_b_ultimate_profiles_fixture.json"
STAGE_A = ROOT / "tools/fixtures/stage_a_ultimate_profiles_dry_run.json"
NANOPB = ROOT / ".pio/libdeps/glyph_mk6/Nanopb"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(command: list[str], *, cwd: Path = ROOT) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise AssertionError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def make_v2_artifact() -> dict:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    artifact = json.loads(STAGE_A.read_text(encoding="utf-8"))
    profile = artifact["ultimateProfiles"][spec["profile_index"]]
    profile["schemaVersion"] = 2
    profile.update(copy.deepcopy(spec["version_2"]))
    return artifact


def main() -> int:
    try:
        require(SPEC.is_file() and STAGE_A.is_file(), "missing Stage-B fixture inputs")
        sys.path.insert(0, str(ROOT / "tools"))
        import glyph_serial_config_tool as writer  # pylint: disable=import-outside-toplevel

        config_pb2, json_format, proto_path = writer.load_runtime_proto_modules(ROOT)
        require(proto_path == ROOT / "schema/haybox/config.proto", "tracked schema was not used")
        v1_message, v1_payload = writer.encode_artifact_payload(
            json.loads(STAGE_A.read_text(encoding="utf-8")), config_pb2, json_format)
        v2_message, v2_payload = writer.encode_artifact_payload(make_v2_artifact(), config_pb2, json_format)
        require(v1_message.ultimate_profiles[0].schema_version == 1, "v1 fixture drift")
        require(v2_message.ultimate_profiles[0].schema_version == 2, "v2 fixture did not encode")
        require(len(v2_message.ultimate_profiles[0].roles) == 22, "v2 role fixture drift")
        require(len(v2_message.ultimate_profiles[0].routing_slots) == 15, "v2 routing fixture drift")
        require(len(v2_message.ultimate_profiles[0].table_rules) == 19, "v2 table rule fixture drift")

        generator = NANOPB / "generator/nanopb_generator.py"
        require(generator.is_file(), "Nanopb dependency unavailable")
        with tempfile.TemporaryDirectory(prefix="stage-b-ultimate-") as directory:
            temp = Path(directory)
            generated = temp / "generated"
            generated.mkdir()
            schema = ROOT / "schema/haybox"
            run([sys.executable, str(generator), "-I", str(schema), "-f", str(schema / "config.options"),
                 "--error-on-unmatched", "--no-timestamp", "-D", str(generated), str(schema / "config.proto")])
            objects: list[str] = []
            for source in (NANOPB / "pb_common.c", NANOPB / "pb_decode.c", generated / "config.pb.c"):
                target = temp / (source.stem + ".o")
                run(["cc", "-std=c11", "-fshort-enums", "-I", str(generated), "-I", str(NANOPB),
                     "-c", str(source), "-o", str(target)])
                objects.append(str(target))
            executable = temp / "admission"
            run(["c++", "-std=c++17", "-fshort-enums", "-Wall", "-Wextra", "-Werror",
                 "-I", str(generated), "-I", str(NANOPB), "-I", str(ROOT / "include"),
                 "-I", str(ROOT / "HAL/pico/include"),
                 "-I", str(ROOT / "config/glyph/common/include"), "-I", str(ROOT / "config/glyph/glyph_mk6/include"),
                 str(ROOT / "tools/fixtures/stage_b_ultimate_profiles_host/admission.cpp"),
                 str(ROOT / "src/core/config_validation.cpp"),
                 str(ROOT / "src/core/config_button_validation.cpp"),
                 str(ROOT / "src/core/config_usb_default_validation.cpp"),
                 str(ROOT / "src/core/config_rgb_target_validation.cpp"),
                 str(ROOT / "config/glyph/common/src/glyph_config_validation.cpp"), *objects, "-o", str(executable)])

            def admit(label: str, message, expected: bool, version: int) -> str:
                payload = message.SerializeToString()
                path = temp / f"{label}.bin"
                path.write_bytes(payload)
                return run([str(executable), str(path), "1" if expected else "0", str(version)])

            admit("v1", v1_message, True, 1)
            v2_output = admit("v2", v2_message, True, 2)
            size_line = next((line for line in v2_output.splitlines() if line.startswith("sizeof_config=")), "")
            require(size_line != "", "host ABI measurement missing")
            mutations = (
                ("v1_extension", lambda value: value.ultimate_profiles[1].roles.add(role_id=1).condition.all_tokens.append(1)),
                ("unknown_token", lambda value: value.ultimate_profiles[0].roles[0].condition.all_tokens.append(61)),
                ("forward_role", lambda value: value.ultimate_profiles[0].roles[0].condition.all_tokens.append(66)),
                ("equal_priority", lambda value: setattr(value.ultimate_profiles[0].table_rules[1], "priority", 10)),
                ("missing_routing_slot", lambda value: value.ultimate_profiles[0].routing_slots.pop()),
                ("duplicate_routing_input", lambda value: setattr(value.ultimate_profiles[0].routing_slots[1], "input_token", 4)),
                ("missing_rule_condition", lambda value: value.ultimate_profiles[0].table_rules[0].ClearField("condition")),
            )
            for label, mutate in mutations:
                invalid = config_pb2.Config()
                invalid.CopyFrom(v2_message if label != "v1_extension" else v1_message)
                mutate(invalid)
                admit(label, invalid, False, 1)
    except (AssertionError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"glyph_stage_b_ultimate_profiles: FAIL: {error}")
        return 1

    print("glyph_stage_b_ultimate_profiles: PASS")
    print("generated_nanopb_decode=true production_validation=true v1_legacy=true v2_evaluator=true negatives=7")
    print(size_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
