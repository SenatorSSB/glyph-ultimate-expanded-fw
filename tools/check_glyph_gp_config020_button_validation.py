#!/usr/bin/env python3
"""Host proof for GP-CONFIG-020's populated Button binding validator."""
from __future__ import annotations

import re
import hashlib
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
ABI_PROBE = ROOT / "tools/fixtures/gp_config020_button_validation/abi_probe.cpp"
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
    authenticated = {
        SCHEMA: "2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b",
        GENERATED: "bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323",
        GENERATED_DIR / "config.pb.c": "d7041bfaf221cc747c7f2dc3fa8586352a1b8dc363fbdcfca181774562941626",
        NANOPB / "pb.h": "e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2",
        NANOPB / "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
        NANOPB / "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
        NANOPB / "pb_decode.h": "fcac5f7680fe6e870157e4bcf34d5162bdd4fff0d7db3cad1122f2ad24a6da87",
        NANOPB / "pb_decode.c": "f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632",
    }
    for path, expected in authenticated.items():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                f"authenticated schema/generated/Nanopb byte drift: {path.relative_to(ROOT)}")
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
    require("sizeof(Button) == 1 || sizeof(Button) == 4" in source and
            "std::numeric_limits<ButtonStorage>::digits" in source and
            "std::is_unsigned<ButtonStorage>" in source,
            "selected verified enum representation assertions missing")
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


def run(command: list[str], label: str, *, expected_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    require((result.returncode == 0) == expected_success,
            f"{label} {'failed' if expected_success else 'unexpectedly passed'}:\n"
            f"command={' '.join(command)}\n{result.stdout}{result.stderr}")
    return result


def compile_and_run() -> str:
    compiler, cc = shutil.which("c++"), shutil.which("cc")
    require(compiler is not None and cc is not None, "host C/C++ compiler unavailable")
    output = [f"c_compiler={run([cc, '--version'], 'C version').stdout.splitlines()[0]}",
              f"cxx_compiler={run([compiler, '--version'], 'C++ version').stdout.splitlines()[0]}"]
    with tempfile.TemporaryDirectory(prefix="glyph-gp-config020-") as directory:
        temp = Path(directory)
        for label, flag, expected_width in (("short", "-fshort-enums", 1),
                                            ("ordinary", "-fno-short-enums", 4)):
            cflags = ["-std=c99", "-O0", "-g", flag, f"-I{NANOPB}", f"-I{GENERATED_DIR}"]
            cxxflags = ["-std=gnu++17", "-O0", "-g", "-Wall", "-Wextra", "-Werror",
                        flag, "-fsanitize=enum,shift", "-fno-sanitize-recover=all",
                        f"-I{ROOT / 'include'}", f"-I{HOST_INCLUDE}",
                        f"-I{ROOT / 'HAL/pico/include'}", f"-I{GENERATED_DIR}", f"-I{NANOPB}"]
            objects: list[str] = []
            for index, path in enumerate((NANOPB / "pb_decode.c", NANOPB / "pb_common.c",
                                          GENERATED_DIR / "config.pb.c")):
                obj = temp / f"{label}-{index}.o"
                run([cc, *cflags, "-c", str(path), "-o", str(obj)], f"{label} C {path.name}")
                objects.append(str(obj))
            output.append(f"host_abi={label} flag={flag} expected_button_width={expected_width} c_units=pb_decode,pb_common,config.pb cxx_units=validator,harness,probe")

            probe = temp / f"{label}-probe"
            run([compiler, *cxxflags, "-DGP_C020_PROBE_MAIN", str(ABI_PROBE),
                 objects[1], objects[2], "-o", str(probe)], f"{label} descriptor probe compile")
            probe_run = run([str(probe)], f"{label} descriptor/layout guard")
            require(f"button_size={expected_width} " in probe_run.stdout,
                    f"{label} observed Button width drift")
            require(probe_run.stdout.count("result=PASS") == 12, f"{label} descriptor census incomplete")
            output.append(probe_run.stdout.rstrip())

            validation = temp / f"{label}-validation"
            val_command = [compiler, *cxxflags, str(SOURCE), str(HARNESS), "-o", str(validation)]
            run(val_command, f"{label} validation compile")
            validation_run = run([str(validation)], f"{label} raw validator matrix")
            expected_validation = [
                "button_class_count=12 result=PASS",
                "named_ids=1..60 per class result=PASS",
                "raw_0..255_all_classes highbyte_or_overflow_refusal result=PASS",
                "extent_absence_disable_sentinel_rgb_exclusion accepted_defaults result=PASS",
            ]
            require(validation_run.stdout.splitlines() == expected_validation,
                    f"{label} validation result shape drift")
            output.append(validation_run.stdout.rstrip())

            transaction = temp / f"{label}-transaction"
            transaction_command = [compiler, "-std=gnu++17", "-O0", "-g", "-Wall", "-Wextra",
                                   "-Werror", flag, "-fsanitize=enum,shift",
                                   "-fno-sanitize-recover=all", "-Wno-keyword-macro", "-pedantic",
                                   f"-I{TRANSACTION_STUBS}", f"-I{ROOT / 'include'}",
                                   f"-I{ROOT / 'HAL/pico/include'}", str(SETCONFIG_HARNESS),
                                   "-o", str(transaction)]
            run(transaction_command, f"{label} SetConfig transaction compile")
            transaction_run = run([str(transaction)], f"{label} mocked-validator transaction")
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
                "mocked_validator_transaction_cases=10 result=PASS",
            ]
            require(transaction_run.stdout.splitlines() == expected_transaction,
                    f"{label} mocked transaction shape drift")
            output.append(transaction_run.stdout.rstrip())

            decoder = temp / f"{label}-decoder"
            run([compiler, *cxxflags, str(SOURCE), str(DECODER_HARNESS), str(ABI_PROBE),
                 *objects, "-o", str(decoder)], f"{label} decoder compile")
            decoder_run = run([str(decoder)], f"{label} authenticated wire vectors")
            expected_wide = [
                f"wire_raw={raw} decoded_classes={12 if label == 'ordinary' and raw <= 4294967295 else 0} "
                f"rejected_or_decode_failed={0 if label == 'ordinary' and raw <= 4294967295 else 12} result=PASS"
                for raw in (256, 257, 300, 4294967295, 18446744073709551615)
            ]
            expected_decoder = expected_wide + [
                "decoded_named_ids=1..60 across 12 classes result=PASS",
                "decoded_raw=0..255,256,257,300,uint32max,uint64max across 12 classes result=PASS",
                "malformed_trailing_last_element_overflow result=PASS",
                "binding_order_mask_identity_no_mutation result=PASS",
            ]
            require(decoder_run.stdout.splitlines() == expected_decoder,
                    f"{label} decoder result shape drift:\n{decoder_run.stdout}")
            output.append(decoder_run.stdout.rstrip())

            typed_source = temp / f"{label}-typed-invalid.cpp"
            typed_source.write_text(
                '#include "config.pb.h"\n#include <cstring>\n'
                'int main() { Button button; unsigned char raw[sizeof(Button)]{}; '
                'raw[0] = 64; std::memcpy(&button, raw, sizeof(button)); '
                'volatile unsigned observed = static_cast<unsigned>(button); (void)observed; }\n',
                encoding="utf-8")
            typed_binary = temp / f"{label}-typed-invalid"
            run([compiler, *cxxflags, str(typed_source), "-o", str(typed_binary)],
                f"{label} typed-invalid sanitizer compile")
            typed_failure = run([str(typed_binary)], f"{label} typed-invalid sanitizer",
                                expected_success=False)
            require("runtime error: load of value 64" in typed_failure.stderr and
                    "not a valid value for type 'Button'" in typed_failure.stderr,
                    f"{label} typed-invalid control lacked enum sanitizer signature")
            output.append(f"negative_control={label}_typed_invalid_enum_read result=SANITIZER_DETECTED")

            if label == "short":
                truncated = temp / "negative-truncation"
                run([compiler, *cxxflags, "-DGP_C020_INJECT_TRUNCATION", str(SOURCE),
                     str(HARNESS), "-o", str(truncated)], "truncation control compile")
                failed = run([str(truncated)], "truncation control", expected_success=False)
                require("narrowed raw injection" in failed.stderr,
                        "truncation control failed for unrelated reason")
                output.append("negative_control=truncating_raw_injection result=DETECTED")
                # Deliberately link byte-layout generated C descriptors to a
                # four-byte C++ consumer. The pre-decode probe must refuse it.
                mixed = temp / "negative-mixed-probe"
                mixed_cxxflags = ["-fno-short-enums" if x == flag else x for x in cxxflags]
                run([compiler, *mixed_cxxflags, "-DGP_C020_PROBE_MAIN", str(ABI_PROBE),
                     objects[1], objects[2], "-o", str(mixed)], "mixed-layout compile")
                mixed_failure = run([str(mixed)], "mixed-layout descriptor guard",
                                    expected_success=False)
                require("class=" in mixed_failure.stdout and "result=FAIL" in mixed_failure.stdout,
                        "mixed-layout control lacked descriptor failure signature")
                output.append("negative_control=mixed_C_CXX_layout result=DETECTED")
    return "\n".join(output) + "\n"


def main() -> int:
    try:
        validate_contract()
        output = compile_and_run()
        print(output, end="")
        print("glyph_gp_config020_button_validation: PASS; dual-ABI host and descriptor proof; mocked transaction characterized")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, ValueError) as exc:
        print(f"glyph_gp_config020_button_validation: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
