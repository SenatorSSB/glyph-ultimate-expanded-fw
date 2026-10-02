#!/usr/bin/env python3
"""Host proof for GP-CONFIG-020's populated Button binding validator."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/core/config_button_validation.cpp"
HEADER = ROOT / "include/core/config_button_validation.hpp"
HANDLER = ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp"
SCHEMA = ROOT / "tools/fixtures/gp_config012_button_host/schema/config.proto"
GENERATED = ROOT / "tools/fixtures/gp_config012_button_host/generated/config.pb.h"
HARNESS = ROOT / "tools/fixtures/gp_config020_button_validation/validation_harness.cpp"
HOST_INCLUDE = ROOT / "tools/fixtures/gp_config020_button_validation/include"
SETCONFIG_HARNESS = ROOT / "tools/fixtures/gp_config020_button_validation/setconfig_harness.cpp"
TRANSACTION_STUBS = ROOT / "tools/fixtures/configurator_setconfig_host/include"
DECODER_HARNESS = ROOT / "tools/fixtures/gp_config020_button_validation/decoder_harness.cpp"
NANOPB = ROOT / "tools/fixtures/gp_config012_button_host/nanopb"
GENERATED_DIR = ROOT / "tools/fixtures/gp_config012_button_host/generated"


class ContractError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def enum_pairs(path: Path, pattern: str) -> list[tuple[str, int]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, re.S)
    require(match is not None, f"Button enum not found: {path}")
    return [(name, int(value)) for name, value in re.findall(r"\b(BTN_[A-Z0-9_]+)\s*=\s*(\d+)", match.group(1))]


def validate_contract() -> None:
    schema_values = enum_pairs(SCHEMA, r"enum\s+Button\s*\{(.*?)\}")
    generated_values = enum_pairs(GENERATED, r"typedef\s+enum\s+_Button\s*\{(.*?)\}\s*Button\s*;")
    expected = [("BTN_UNSPECIFIED", 0)] + [
        (name, number) for number, name in enumerate(
            [f"BTN_LF{i}" for i in range(1, 17)] +
            [f"BTN_RF{i}" for i in range(1, 17)] +
            [f"BTN_LT{i}" for i in range(1, 9)] +
            [f"BTN_RT{i}" for i in range(1, 9)] +
            [f"BTN_MB{i}" for i in range(1, 13)], start=1
        )
    ]
    require(schema_values == expected, "schema Button domain or enumerator set changed")
    require(generated_values == expected, "generated Button domain or enumerator set changed")

    source = SOURCE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    require("validate_config_button_bindings(const Config &config)" in header, "public validator contract drift")
    require("std::memcmp(&button, &supported, sizeof(Button))" in source,
            "validator must compare complete raw enum object representations")
    require("sizeof(Button) == 4" in source and "std::numeric_limits<unsigned int>::digits" in source,
            "selected four-byte Pico enum representation assertions missing")
    require("Persistence" not in source and "SaveConfig" not in source and "LoadConfig" not in source,
            "pure validator gained persistence access")
    require("RgbConfig" not in source and "button_colors" not in source,
            "RGB target IDs entered GP-CONFIG-020")
    require("BTN_UNSPECIFIED" in source and "is_remap_disable" in source,
            "remap disable sentinel preservation missing")
    for field in ("activation_binding", "button_remapping", "socd_pairs", "modifiers",
                  "button_combo_mappings", "digital_button_mappings", "stick_direction_mappings",
                  "analog_trigger_mappings", "buttons_to_keycodes"):
        require(field in source, f"field class missing from validator: {field}")
    mask_source = (ROOT / "HAL/pico/include/util/state_util.hpp").read_text(encoding="utf-8")
    require("button_mask |= (1ULL << (buttons[j] - 1));" in mask_source,
            "accepted make_button_mask arithmetic changed")
    caller_sources = [
        ROOT / "src/modes/CustomControllerMode.cpp",
        ROOT / "src/core/mode_selection.cpp",
        ROOT / "src/core/config_utils.cpp",
    ]
    require(sum(path.read_text(encoding="utf-8").count("make_button_mask(") for path in caller_sources) == 4,
            "production make_button_mask caller census changed")

    handler = HANDLER.read_text(encoding="utf-8")
    start = handler.index("bool ConfiguratorBackend::HandleSetConfig()")
    end = handler.index("bool ConfiguratorBackend::HandleUnknownCommand", start)
    body = handler[start:end]
    require(body.index("pb_decode(&istream, Config_fields, &candidate)") <
            body.index("validate_config_button_bindings(candidate)"), "validator must follow successful decode")
    require(body.index("validate_config_button_bindings(candidate)") <
            body.index("persistence.SaveConfig(candidate)"), "validator must precede save")
    require(body.index("validate_config_button_bindings(candidate)") <
            body.index("_config = candidate;"), "validator must precede live publication")
    require("WritePacket(CMD_ERROR" in body[body.index("validate_config_button_bindings(candidate)"):],
            "validator failure must use existing error response")


def compile_and_run() -> str:
    compiler = shutil.which("c++")
    require(compiler is not None, "host C++ compiler unavailable")
    with tempfile.TemporaryDirectory(prefix="glyph-gp-config020-") as directory:
        binary = Path(directory) / "button_validation"
        command = [
            compiler, "-std=gnu++17", "-Wall", "-Wextra", "-Werror",
            "-fsanitize=enum,shift", "-fno-sanitize-recover=all",
            f"-I{ROOT / 'include'}",
            f"-I{HOST_INCLUDE}",
            f"-I{ROOT / 'HAL/pico/include'}",
            f"-I{ROOT / 'tools/fixtures/gp_config012_button_host/generated'}",
            f"-I{ROOT / 'tools/fixtures/gp_config012_button_host/nanopb'}",
            str(SOURCE), str(HARNESS), "-o", str(binary),
        ]
        compiled = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        require(compiled.returncode == 0, f"host compile failed:\n{compiled.stdout}{compiled.stderr}")
        executed = subprocess.run([str(binary)], cwd=ROOT, text=True, capture_output=True, check=False)
        require(executed.returncode == 0, f"host validation failed:\n{executed.stdout}{executed.stderr}")
        expected = [
            "button_class_count=12 result=PASS",
            "named_ids=1..60 per class result=PASS",
            "invalid_raw=0,61..65,127,255,ffffffff per class result=PASS",
            "extent_absence_disable_sentinel_rgb_exclusion accepted_defaults result=PASS",
        ]
        require(executed.stdout.splitlines() == expected, "host result shape drift")
        transaction_binary = Path(directory) / "setconfig_transaction"
        transaction_command = [
            compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-Wno-keyword-macro", "-pedantic",
            f"-I{TRANSACTION_STUBS}", f"-I{ROOT / 'include'}",
            f"-I{ROOT / 'HAL/pico/include'}", str(SETCONFIG_HARNESS),
            "-o", str(transaction_binary),
        ]
        transaction_compiled = subprocess.run(transaction_command, cwd=ROOT, text=True,
                                              capture_output=True, check=False)
        require(transaction_compiled.returncode == 0,
                f"SetConfig host compile failed:\n{transaction_compiled.stdout}{transaction_compiled.stderr}")
        transaction_run = subprocess.run([str(transaction_binary)], cwd=ROOT, text=True,
                                         capture_output=True, check=False)
        require(transaction_run.returncode == 0,
                f"SetConfig transaction failed:\n{transaction_run.stdout}{transaction_run.stderr}")
        expected_transaction = [
            "case=malformed_decode result=PASS",
            "case=invalid_default_backend_index result=PASS",
            "case=invalid_default_game_mode_reference result=PASS",
            "case=invalid_keyboard_mode_condition result=PASS",
            "case=invalid_custom_mode_condition result=PASS",
            "case=out_of_range_keyboard_config result=PASS",
            "case=out_of_range_custom_config result=PASS",
            "case=invalid_button_binding result=PASS",
            "case=save_failure result=PASS",
            "case=full_success result=PASS",
            "production_source=HAL/pico/src/comms/ConfiguratorBackend.cpp",
            "production_handler_cases=10 result=PASS",
        ]
        require(transaction_run.stdout.splitlines() == expected_transaction,
                f"SetConfig transaction result shape drift:\n{transaction_run.stdout}{transaction_run.stderr}")

        cc = shutil.which("cc")
        require(cc is not None, "host C compiler unavailable for authenticated Nanopb vectors")
        objects = []
        for index, source_path in enumerate((NANOPB / "pb_decode.c", NANOPB / "pb_common.c",
                                             GENERATED_DIR / "config.pb.c")):
            obj = Path(directory) / f"decoder-{index}.o"
            c_command = [cc, "-std=c99", "-O0", "-g", f"-I{NANOPB}", f"-I{GENERATED_DIR}",
                         "-c", str(source_path), "-o", str(obj)]
            c_compiled = subprocess.run(c_command, cwd=ROOT, text=True,
                                        capture_output=True, check=False)
            require(c_compiled.returncode == 0,
                    f"Nanopb C compile failed:\n{c_compiled.stdout}{c_compiled.stderr}")
            objects.append(str(obj))
        decoder_binary = Path(directory) / "button_decoder_validation"
        decoder_command = [
            compiler, "-std=gnu++17", "-Wall", "-Wextra", "-Werror",
            "-fsanitize=enum,shift", "-fno-sanitize-recover=all",
            f"-I{ROOT / 'include'}", f"-I{GENERATED_DIR}", f"-I{NANOPB}",
            str(SOURCE), str(DECODER_HARNESS), *objects, "-o", str(decoder_binary),
        ]
        decoder_compiled = subprocess.run(decoder_command, cwd=ROOT, text=True,
                                           capture_output=True, check=False)
        require(decoder_compiled.returncode == 0,
                f"decoder host compile failed:\n{decoder_compiled.stdout}{decoder_compiled.stderr}")
        decoder_run = subprocess.run([str(decoder_binary)], cwd=ROOT, text=True,
                                     capture_output=True, check=False)
        require(decoder_run.returncode == 0,
                f"decoded binding matrix failed:\n{decoder_run.stdout}{decoder_run.stderr}")
        expected_decoder = [
            "decoded_named_ids=1..60 across 12 classes result=PASS",
            "decoded_raw_controls=0,61..65,127,255,256,300,negative result=PASS",
            "malformed_trailing_last_element_overflow result=PASS",
            "binding_order_mask_identity_no_mutation result=PASS",
        ]
        require(decoder_run.stdout.splitlines() == expected_decoder,
                "decoder result shape drift")
        return executed.stdout + transaction_run.stdout + decoder_run.stdout


def main() -> int:
    try:
        validate_contract()
        output = compile_and_run()
        print(output, end="")
        print("glyph_gp_config020_button_validation: PASS; raw enum matrix; source-free host proof")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, ValueError) as exc:
        print(f"glyph_gp_config020_button_validation: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
