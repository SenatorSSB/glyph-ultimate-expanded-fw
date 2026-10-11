#!/usr/bin/env python3
"""Check the minimal common-wire Config bridge without a write path.

The Clean 1.0.7 side of this bridge is historical source proof only: its
shared field numbers and validator shape were inspected, but this checker does
not claim a Clean device test.  The other endpoint is the unchanged final
candidate named by the handoff (16fb02a5); this checker exercises the current
checked-out production decoder and validator only.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tools/fixtures/final_bc_cross_version_bridge_config.json"
SCHEMA = ROOT / "schema/haybox"
NANOPB = ROOT / ".pio/libdeps/glyph_mk6/Nanopb"
ADMISSION = ROOT / "tools/fixtures/stage_a_ultimate_profiles_host/admission.cpp"
EXPECTED_PAYLOAD = bytes.fromhex("0a140803220408131013220408141014220408231023120408021001120508081a012a30013801")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(command: list[str], *, cwd: Path = ROOT) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}{result.stderr}")
    return result.stdout


def load_proto():
    """Generate only a temporary Python reader for the tracked schema."""
    import grpc_tools.protoc  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory(prefix="final-bc-proto-") as directory:
        generated = Path(directory)
        result = grpc_tools.protoc.main([
            "protoc", f"-I{SCHEMA}", f"--python_out={generated}", str(SCHEMA / "config.proto")])
        require(result == 0, "protobuf Python generation failed")
        spec = importlib.util.spec_from_file_location("final_bc_config_pb2", generated / "config_pb2.py")
        require(spec is not None and spec.loader is not None, "generated protobuf module unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Keep the generated module usable after the temporary directory closes.
        return module


def assert_bridge_envelope(value: dict) -> None:
    """The bridge is deliberately the old/common subset, not a profile export."""
    require(set(value) == {"gameModeConfigs", "communicationBackendConfigs",
                           "defaultBackendConfig", "defaultUsbBackendConfig"},
            "bridge must contain only common Config fields")
    modes = value["gameModeConfigs"]
    backends = value["communicationBackendConfigs"]
    require(modes == [{
        "modeId": "MODE_ULTIMATE",
        "buttonRemapping": [
            {"physicalButton": "BTN_RF3", "activates": "BTN_RF3"},
            {"physicalButton": "BTN_RF4", "activates": "BTN_RF4"},
            {"physicalButton": "BTN_LT3", "activates": "BTN_LT3"},
        ],
    }], "bridge requires one Ultimate mode with only adapter-required identity remaps")
    require(len(backends) == 2, "bridge requires exactly two backends")
    require(backends[0] == {"backendId": "COMMS_BACKEND_XINPUT", "defaultModeConfig": 1},
            "bridge XInput backend drift")
    require(backends[1] == {"backendId": "COMMS_BACKEND_CONFIGURATOR", "activationBinding": ["BTN_RT2"]},
            "bridge Configurator backend must be RT2-only and omit defaultModeConfig")
    require(value["defaultBackendConfig"] == value["defaultUsbBackendConfig"] == 1,
            "bridge defaults must select XInput")
    forbidden = {"rgbConfigs", "customModes", "keyboardModes", "ultimateProfiles", "rgbBrightness"}
    require(not (forbidden & set(value)), "bridge must omit RGB/custom/keyboard/Ultimate data")


def assert_current_wire_contract() -> None:
    """Verify the current source retains every wire field used by the bridge."""
    schema = (SCHEMA / "config.proto").read_text(encoding="utf-8")
    for declaration in (
            "GameModeId mode_id = 1;",
            "string name = 2;",
            "Button physical_button = 1;",
            "Button activates = 2;",
            "CommunicationBackendId backend_id = 1;",
            "uint32 default_mode_config = 2;",
            "repeated Button activation_binding = 3;",
            "repeated GameModeConfig game_mode_configs = 1;",
            "repeated CommunicationBackendConfig communication_backend_configs = 2;",
            "uint32 default_backend_config = 6;",
            "uint32 default_usb_backend_config = 7;"):
        require(declaration in schema, f"current shared wire declaration drift: {declaration}")
    for declaration in ("MODE_ULTIMATE = 3;", "COMMS_BACKEND_XINPUT = 2;",
                        "COMMS_BACKEND_CONFIGURATOR = 8;", "BTN_RF3 = 19;",
                        "BTN_RF4 = 20;", "BTN_LT3 = 35;", "BTN_RT2 = 42;"):
        require(declaration in schema, f"current shared enum declaration drift: {declaration}")


def compile_admission(temp: Path) -> Path:
    generated = temp / "generated"
    generated.mkdir()
    run([sys.executable, str(NANOPB / "generator/nanopb_generator.py"), "-I", str(SCHEMA),
         "-f", str(SCHEMA / "config.options"), "--error-on-unmatched", "--no-timestamp",
         "-D", str(generated), str(SCHEMA / "config.proto")])
    includes = ["-I", str(generated), "-I", str(NANOPB), "-I", str(ROOT / "include"),
                "-I", str(ROOT / "HAL/pico/include"),
                "-I", str(ROOT / "config/glyph/common/include"),
                "-I", str(ROOT / "config/glyph/glyph_mk6/include")]
    objects: list[str] = []
    for source in (NANOPB / "pb_common.c", NANOPB / "pb_decode.c", generated / "config.pb.c"):
        target = temp / f"{source.stem}.o"
        run(["cc", "-std=c11", "-fshort-enums", *includes, "-c", str(source), "-o", str(target)])
        objects.append(str(target))
    executable = temp / "admission"
    run(["c++", "-std=c++17", "-fshort-enums", "-Wall", "-Wextra", "-Werror", *includes,
         str(ADMISSION), str(ROOT / "src/core/config_validation.cpp"),
         str(ROOT / "src/core/config_button_validation.cpp"),
         str(ROOT / "src/core/config_usb_default_validation.cpp"),
         str(ROOT / "src/core/config_rgb_target_validation.cpp"),
         str(ROOT / "config/glyph/common/src/glyph_config_validation.cpp"), *objects,
         "-o", str(executable)])
    return executable


def main() -> int:
    try:
        require(FIXTURE.is_file() and ADMISSION.is_file() and NANOPB.is_dir(),
                "required fixture or checked-in host mechanism is unavailable")
        raw = FIXTURE.read_bytes()
        source = json.loads(raw)
        assert_bridge_envelope(source)
        assert_current_wire_contract()
        pb = load_proto()
        from google.protobuf import json_format  # pylint: disable=import-outside-toplevel

        message = pb.Config()
        json_format.ParseDict(source, message, ignore_unknown_fields=False)
        payload = message.SerializeToString(deterministic=True)
        require(payload == EXPECTED_PAYLOAD, "common-wire payload drift")
        decoded = pb.Config()
        decoded.ParseFromString(payload)
        require(decoded.SerializeToString(deterministic=True) == payload,
                "protobuf binary round-trip drift")
        round_tripped = json_format.MessageToDict(
            decoded, preserving_proto_field_name=False, use_integers_for_enums=False)
        require(round_tripped == source, "JSON/protobuf round-trip drift")

        dry_run = subprocess.run(
            [sys.executable, str(ROOT / "tools/glyph_serial_config_tool.py"), "--dry-run",
             "--artifact", str(FIXTURE)], cwd=ROOT, capture_output=True, text=True, check=False)
        require(dry_run.returncode == 0,
                f"bridge serial-tool dry-run failed: {dry_run.stdout}{dry_run.stderr}")
        require("dry_run_serial_opened=false" in dry_run.stdout,
                "bridge dry-run did not prove no serial port was opened")
        require("live_device_access=false" in dry_run.stdout,
                "bridge dry-run did not prove no live device access")

        # Envelope-only negatives make omissions explicit; they do not claim that
        # every old source validator rejected fields introduced later.
        envelope_negatives = {
            "configurator_default_mode": lambda v: v["communicationBackendConfigs"][1].update(defaultModeConfig=1),
            "configurator_wrong_binding": lambda v: v["communicationBackendConfigs"][1].update(activationBinding=["BTN_RT1"]),
            "xinput_binding": lambda v: v["communicationBackendConfigs"][0].update(activationBinding=["BTN_RT2"]),
            "rgb": lambda v: v.update(rgbConfigs=[]),
            "ultimate_profile": lambda v: v.update(ultimateProfiles=[]),
        }
        for label, mutate in envelope_negatives.items():
            invalid = copy.deepcopy(source)
            mutate(invalid)
            try:
                assert_bridge_envelope(invalid)
            except AssertionError:
                continue
            raise AssertionError(f"bridge envelope accepted negative: {label}")

        with tempfile.TemporaryDirectory(prefix="final-bc-nanopb-") as directory:
            temp = Path(directory)
            executable = compile_admission(temp)

            def production_case(label: str, mutate, accepted: bool) -> None:
                candidate = pb.Config()
                candidate.CopyFrom(message)
                mutate(candidate)
                path = temp / f"{label}.bin"
                path.write_bytes(candidate.SerializeToString(deterministic=True))
                run([str(executable), str(path), "1" if accepted else "0"])

            production_case("bridge", lambda _: None, True)
            production_case("default_backend_out_of_range",
                            lambda v: setattr(v, "default_backend_config", 3), False)
            production_case("default_usb_backend_out_of_range",
                            lambda v: setattr(v, "default_usb_backend_config", 3), False)
            production_case("xinput_mode_out_of_range",
                            lambda v: setattr(v.communication_backend_configs[0], "default_mode_config", 2), False)
            production_case("configurator_invalid_binding", lambda v:
                            v.communication_backend_configs[1].activation_binding.__setitem__(
                                0, pb.BTN_UNSPECIFIED), False)
    except (AssertionError, OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f"glyph_final_bc_bridge_config: FAIL: {error}")
        return 1

    print("glyph_final_bc_bridge_config: PASS")
    print("bridge_envelope=common_fields_only clean_1_0_7_proof=HISTORICAL_FIELD_AND_VALIDATOR_ONLY final_candidate=16fb02a5 device_proof=NOT_CLAIMED")
    print("current_wire_fields=1,2,6,7 current_nanopb_decode_validate=PASS negatives=backend_refs:3 envelope:5 serial_dry_run=PASS serial_opened=false live_device_access=false")
    print(f"fixture_sha256={hashlib.sha256(raw).hexdigest()} payload_bytes={len(payload)} payload_sha256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
