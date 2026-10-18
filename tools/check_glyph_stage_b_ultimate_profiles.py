#!/usr/bin/env python3
"""Decode and exercise the finite Stage-B Ultimate profile schema in production code."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "tools/fixtures/stage_b_ultimate_profiles_fixture.json"
STAGE_C = ROOT / "tools/fixtures/stage_c_ultimate_profiles_fixture.json"
STAGE_A = ROOT / "tools/fixtures/stage_a_ultimate_profiles_dry_run.json"
NANOPB = Path(os.environ.get("GLYPH_STAGE_B_NANOPB", str(ROOT / ".pio/libdeps/glyph_mk6/Nanopb")))


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


def make_v3_artifact() -> dict:
    artifact = make_v2_artifact()
    stage_c = json.loads(STAGE_C.read_text(encoding="utf-8"))
    version_2 = json.loads(SPEC.read_text(encoding="utf-8"))["version_2"]
    # Stage-C's handoff fixture reserves a deterministic Configurator recovery
    # envelope without changing the generic Config writer or validator.
    # Preserve the legacy Ultimate first-row default for the detected GameCube
    # path.  Omitting this row makes backend_config_from_id fall back to its
    # zero-mode sentinel instead of selecting the legacy Ultimate mode.
    artifact["communicationBackendConfigs"].append({
        "backendId": "COMMS_BACKEND_GAMECUBE",
        "defaultModeConfig": 1,
    })
    artifact["communicationBackendConfigs"].append({
        "backendId": "COMMS_BACKEND_CONFIGURATOR",
        "defaultModeConfig": 1,
        "activationBinding": ["BTN_RT2"],
    })
    for index, profile in enumerate(artifact["ultimateProfiles"]):
        profile.update(copy.deepcopy(version_2))
        profile["schemaVersion"] = stage_c["schema_version"]
        profile["routingSlots"] = copy.deepcopy(stage_c["routingSlots"])
        profile["outputProgram"] = copy.deepcopy(stage_c["outputProgram"] if index == 0 else stage_c["profileBOutputProgram"])
    return artifact


def make_v4_artifact() -> dict:
    """Derive the approved X1-only V4 fixture from the frozen V2 inventory."""
    artifact = make_v3_artifact()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    for profile in artifact["ultimateProfiles"]:
        profile["schemaVersion"] = 4
        profile["functionBindings"] = copy.deepcopy(spec["version_4"]["functionBindings"])
        profile["roles"] = [role for role in profile["roles"] if role["roleId"] != 2]
        rules = []
        for rule in profile["tableRules"]:
            if rule["priority"] in (10, 11):
                continue
            rewritten = copy.deepcopy(rule)
            for tokens in rewritten["condition"].values():
                for index, token in enumerate(tokens):
                    if token == 66:
                        tokens[index] = 97
            rules.append(rewritten)
        profile["tableRules"] = rules
    return artifact


def main() -> int:
    try:
        require(SPEC.is_file() and STAGE_C.is_file() and STAGE_A.is_file(), "missing Stage-B/C fixture inputs")
        sys.path.insert(0, str(ROOT / "tools"))
        import glyph_serial_config_tool as writer  # pylint: disable=import-outside-toplevel

        config_pb2, json_format, proto_path = writer.load_runtime_proto_modules(ROOT)
        require(proto_path == ROOT / "schema/haybox/config.proto", "tracked schema was not used")
        v1_message, v1_payload = writer.encode_artifact_payload(
            json.loads(STAGE_A.read_text(encoding="utf-8")), config_pb2, json_format)
        v2_message, v2_payload = writer.encode_artifact_payload(make_v2_artifact(), config_pb2, json_format)
        v3_message, v3_payload = writer.encode_artifact_payload(make_v3_artifact(), config_pb2, json_format)
        v4_message, v4_payload = writer.encode_artifact_payload(make_v4_artifact(), config_pb2, json_format)
        require(v1_message.ultimate_profiles[0].schema_version == 1, "v1 fixture drift")
        require(v2_message.ultimate_profiles[0].schema_version == 2, "v2 fixture did not encode")
        require(len(v2_message.ultimate_profiles[0].roles) == 22, "v2 role fixture drift")
        require(len(v2_message.ultimate_profiles[0].routing_slots) == 15, "v2 routing fixture drift")
        require(len(v2_message.ultimate_profiles[0].table_rules) == 19, "v2 table rule fixture drift")
        require(v3_message.ultimate_profiles[0].schema_version == 3, "v3 fixture did not encode")
        require(len(v3_message.ultimate_profiles[0].routing_slots) == 32, "v3 routing fixture drift")
        require(v3_message.ultimate_profiles[0].output_program.enabled, "v3 output program missing")
        require(len(v3_message.ultimate_profiles) == 2 and all(p.schema_version == 3 and len(p.output_program.effects) == 12 for p in v3_message.ultimate_profiles), "two complete v3 A/B profiles required")
        require(len(v4_message.ultimate_profiles) == 2 and all(p.schema_version == 4 and len(p.roles) == 21 and len(p.function_bindings) == 1 for p in v4_message.ultimate_profiles), "two complete v4 X1-binding profiles required")

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
            v3_output = admit("v3", v3_message, True, 3)
            v4_output = admit("v4", v4_message, True, 4)
            size_line = next((line for line in v2_output.splitlines() if line.startswith("sizeof_config=")), "")
            require(size_line != "", "host ABI measurement missing")
            require("sizeof_config=" in v3_output, "v3 host ABI measurement missing")
            require("sizeof_config=" in v4_output, "v4 host ABI measurement missing")
            mutations = (
                ("v1_extension", lambda value: value.ultimate_profiles[1].roles.add(role_id=1).condition.all_tokens.append(1)),
                ("unknown_token", lambda value: value.ultimate_profiles[0].roles[0].condition.all_tokens.append(61)),
                ("forward_role", lambda value: value.ultimate_profiles[0].roles[0].condition.all_tokens.append(66)),
                ("equal_priority", lambda value: setattr(value.ultimate_profiles[0].table_rules[1], "priority", 10)),
                ("missing_routing_slot", lambda value: value.ultimate_profiles[0].routing_slots.pop()),
                ("duplicate_routing_input", lambda value: setattr(value.ultimate_profiles[0].routing_slots[1], "input_token", 4)),
                ("missing_rule_condition", lambda value: value.ultimate_profiles[0].table_rules[0].ClearField("condition")),
                ("v3_missing_program", lambda value: value.ultimate_profiles[0].ClearField("output_program")),
                ("v3_disabled_program", lambda value: setattr(value.ultimate_profiles[0].output_program, "enabled", False)),
                ("v3_partial_routes", lambda value: value.ultimate_profiles[0].routing_slots.pop()),
                ("v4_missing_binding", lambda value: value.ultimate_profiles[0].function_bindings.pop()),
                ("v4_unknown_function", lambda value: setattr(value.ultimate_profiles[0].function_bindings[0], "function_class", 2)),
                ("v4_residual_role2", lambda value: value.ultimate_profiles[0].table_rules[0].condition.all_tokens.append(66)),
                ("v4_nonphysical_binding", lambda value: value.ultimate_profiles[0].function_bindings[0].activation_condition.all_tokens.append(65)),
                ("v4_colliding_priority", lambda value: setattr(value.ultimate_profiles[0].function_bindings[0], "base_priority", 1)),
            )
            for label, mutate in mutations:
                invalid = config_pb2.Config()
                invalid.CopyFrom(v4_message if label.startswith("v4_") else (v3_message if label.startswith("v3_") else (v2_message if label != "v1_extension" else v1_message)))
                mutate(invalid)
                admit(label, invalid, False, 1)
            # Encoded-size custody deliberately covers the empty legacy config,
            # one profile, two profiles, and the fixed-capacity maximum.
            legacy = config_pb2.Config(); legacy.CopyFrom(v1_message); legacy.ClearField("ultimate_profiles")
            for mode in legacy.game_mode_configs: mode.ultimate_profile_config = 0
            one = config_pb2.Config(); one.CopyFrom(v3_message); one.ultimate_profiles.pop()
            for mode in one.game_mode_configs:
                if mode.ultimate_profile_config > 1: mode.ultimate_profile_config = 1
            two = config_pb2.Config(); two.CopyFrom(v3_message)
            admit("resource_one",one,True,3); admit("resource_two",two,True,3)
            print(f"encoded_config_sizes=legacy:{len(legacy.SerializeToString())} one:{len(one.SerializeToString())} two:{len(two.SerializeToString())} max:{len(two.SerializeToString())}")
    except (AssertionError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"glyph_stage_b_ultimate_profiles: FAIL: {error}")
        return 1

    print("glyph_stage_b_ultimate_profiles: PASS")
    print("generated_nanopb_decode=true production_validation=true v1_legacy=true v2_evaluator=true v3_stage_c_routing=true v4_x1_binding=true negatives=15")
    print(size_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
