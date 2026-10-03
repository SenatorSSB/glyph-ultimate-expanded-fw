#!/usr/bin/env python3
"""Compile and run the real GP-CONFIG-005 production SetConfig handler."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import tempfile

from glyph_campaign_transition import C, authenticate, verify_current_source

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp"
PRODUCTION_HEADER = ROOT / "HAL/pico/include/comms/ConfiguratorBackend.hpp"
FIXTURE = ROOT / "docs/runtime_config/fixtures/configurator_setconfig_transaction.json"
HOST_ROOT = ROOT / "tools/fixtures/configurator_setconfig_host"
HARNESS = HOST_ROOT / "handler_harness.cpp"
STUB_INCLUDE = HOST_ROOT / "include"
PRODUCTION_INCLUDE = '#include "../../../HAL/pico/src/comms/ConfiguratorBackend.cpp"'


class ContractError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_fixture(value: dict[str, object]) -> list[str]:
    require(
        list(value) == [
            "schema_name", "schema_version", "work_order", "production_source",
            "build_contract", "dependency_substitutions", "cases", "non_claims",
        ],
        "fixture schema drift",
    )
    require(value["schema_name"] == "glyph_configurator_setconfig_transaction", "schema name")
    require(value["schema_version"] == 2 and value["work_order"] == "GP-CONFIG-005", "fixture identity")
    source = value["production_source"]
    require(type(source) is dict and list(source) == ["path", "sha256", "method"], "source schema")
    require(source["path"] == SOURCE.relative_to(ROOT).as_posix(), "source path")
    verify_current_source(ROOT, source["path"], source["sha256"])
    require(source["method"] == "literal translation-unit include compiled by host C++ compiler", "source method")
    build = value["build_contract"]
    require(type(build) is dict and list(build) == ["translation_unit", "production_header", "stub_include_root"], "build schema")
    require(build == {
        "translation_unit": HARNESS.relative_to(ROOT).as_posix(),
        "production_header": PRODUCTION_HEADER.relative_to(ROOT).as_posix(),
        "stub_include_root": STUB_INCLUDE.relative_to(ROOT).as_posix(),
    }, "build paths")
    require(value["dependency_substitutions"] == [
        "nanopb decode/stream plumbing",
        "Persistence SaveConfig result and observation",
        "packet stream/output plumbing",
        "platform-only USB/reboot/delay symbols",
        "host Config shape with production array cardinalities used by the handler",
    ], "dependency substitutions")
    cases = value["cases"]
    require(type(cases) is list and all(type(case) is dict for case in cases), "case list")
    expected_names = [
        "malformed_decode",
        "invalid_default_backend_index",
        "invalid_default_game_mode_reference",
        "invalid_keyboard_mode_condition",
        "invalid_custom_mode_condition",
        "out_of_range_keyboard_config",
        "out_of_range_custom_config",
        "save_failure",
        "full_success",
    ]
    require([case.get("name") for case in cases] == expected_names, "case order")
    for case in cases:
        require(list(case) == ["name", "result"], f"case schema: {case.get('name')}")
        require(case["result"] == "PASS", f"case expected result: {case['name']}")
    require(value["non_claims"] == [
        "disk rollback",
        "atomic config.bin",
        "persistence recovery",
        "power-loss safety",
        "device hardware acceptance",
    ], "non-claims")
    return expected_names


def validate_correspondence() -> None:
    harness = HARNESS.read_text(encoding="utf-8")
    stub_sources = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(STUB_INCLUDE.rglob("*")) if path.is_file()
    )
    require(harness.count(PRODUCTION_INCLUDE) == 1, "harness must literally include production .cpp once")
    require("bool ConfiguratorBackend::HandleSetConfig" not in harness, "harness contains copied handler definition")
    require("HandleSetConfig() {" not in stub_sources, "stub contains copied handler definition")
    require("#include \"../../../HAL/pico/include/comms/ConfiguratorBackend.hpp\"" in harness,
            "harness must use production class declaration")
    function = SOURCE.read_text(encoding="utf-8")
    start = function.index("bool ConfiguratorBackend::HandleSetConfig()")
    end = function.index("bool ConfiguratorBackend::HandleUnknownCommand", start)
    handler = function[start:end]
    require(handler.count("_config = candidate;") == 1, "production publication assignment must be unique")
    require(handler.index("persistence.SaveConfig(candidate)") < handler.index("_config = candidate;"),
            "production publication must follow successful SaveConfig")
    require("persistence.LoadConfig(_config)" not in handler, "decode rejection must not reload live config")
    require("pb_decode(&istream, Config_fields, &_config)" not in handler, "production decode targets live config")


HISTORICAL_SOURCE_SHA256 = "28ef942416d0ec4b92588304fcf72f219a0c6b1e2a582f20e2dc7e0e07d1b876"


def current_abi_modes(historical: bool = False) -> tuple[str | None, ...]:
    if historical or hashlib.sha256(SOURCE.read_bytes()).hexdigest() == HISTORICAL_SOURCE_SHA256:
        return (None,)
    proof = authenticate(ROOT)
    return ("short", "ordinary") if proof['contract'] == 'c020_abi_repair' and proof['candidate'] != C else (None,)


def compile_translation_unit(harness: Path, historical: bool = False, abi_mode: str | None = None) -> str:
    """Run a literal production TU in an isolated mirror; never replace the live tree."""
    frozen = verify_current_source(ROOT, SOURCE.relative_to(ROOT).as_posix(), HISTORICAL_SOURCE_SHA256)
    current = SOURCE.read_bytes()
    require(hashlib.sha256((ROOT / "tools/fixtures/gp_config012_button_host/generated/config.pb.h").read_bytes()).hexdigest() == "bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323", "frozen generated schema/ABI dependency drift")
    require(hashlib.sha256((ROOT / "tools/fixtures/gp_config012_button_host/nanopb/pb.h").read_bytes()).hexdigest() == "e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2", "frozen generated schema/ABI dependency drift")

    repaired = not historical and current != frozen
    require(abi_mode in (None, "short", "ordinary"), "unknown host ABI mode")
    require(abi_mode is None or repaired, "ABI modes apply only to the real candidate helper")
    with tempfile.TemporaryDirectory(prefix="glyph-setconfig-host-") as temp:
        mirror = Path(temp)
        shutil.copytree(HOST_ROOT, mirror / HOST_ROOT.relative_to(ROOT))
        for relative in (harness.relative_to(ROOT).as_posix(),
                         "tools/fixtures/gp_config012_button_host/generated/config.pb.h",
                         "tools/fixtures/gp_config012_button_host/nanopb/pb.h",
                         "HAL/pico/src/comms/ConfiguratorBackend.cpp", "HAL/pico/include/comms/ConfiguratorBackend.hpp"):
            destination = mirror / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / relative).read_bytes())
        (mirror / SOURCE.relative_to(ROOT)).write_bytes(frozen if historical else current)
        command = ["c++", "-std=c++17", "-Wall", "-Wextra", "-pedantic",
                   f"-I{mirror / STUB_INCLUDE.relative_to(ROOT)}", f"-I{mirror / 'HAL/pico/include'}"]
        if repaired:
            for relative in ("include/core/config_button_validation.hpp", "src/core/config_button_validation.cpp"):
                destination = mirror / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / relative).read_bytes())
            command += ["-DGLYPH_ACTUAL_BUTTON_VALIDATOR", f"-I{mirror / 'include'}",
                        f"-I{mirror / 'tools/fixtures/gp_config012_button_host/nanopb'}",
                        str(mirror / "src/core/config_button_validation.cpp")]
        if abi_mode is not None:
            # Every Config-consuming C++ unit receives the same explicit ABI.
            # Decode is mocked here; the separate frozen C_R suite checks actual C descriptors.
            width = 1 if abi_mode == "short" else 4
            probe = mirror / "abi_assert.hpp"
            probe.write_text('#include "' + str(mirror / "tools/fixtures/gp_config012_button_host/generated/config.pb.h") +
                             '"\nstatic_assert(sizeof(Button) == GLYPH_EXPECT_BUTTON_BYTES, "host Button ABI mismatch");\n')
            command += ["-fshort-enums" if abi_mode == "short" else "-fno-short-enums",
                        "-include", str(probe), f"-DGLYPH_EXPECT_BUTTON_BYTES={width}"]
            if harness == HARNESS:
                negative = [part if not part.startswith("-DGLYPH_EXPECT_BUTTON_BYTES=") else
                            f"-DGLYPH_EXPECT_BUTTON_BYTES={4 if width == 1 else 1}" for part in command]
                negative += ["-fsyntax-only", str(mirror / harness.relative_to(ROOT))]
                rejected = subprocess.run(negative, cwd=mirror, capture_output=True, text=True, check=False)
                require(rejected.returncode != 0 and "host Button ABI mismatch" in rejected.stderr,
                        "contradictory host ABI assertion was not rejected")
        binary = mirror / "host"
        command += [str(mirror / harness.relative_to(ROOT)), "-o", str(binary)]
        compiled = subprocess.run(command, cwd=mirror, capture_output=True, text=True, check=False)
        require(compiled.returncode == 0, f"host compile failed:\n{compiled.stdout}{compiled.stderr}")
        executed = subprocess.run([str(binary)], cwd=mirror, capture_output=True, text=True, check=False)
        require(executed.returncode == 0, f"host harness failed:\n{executed.stdout}{executed.stderr}")
        return executed.stdout


def compile_and_run(expected_names: list[str]) -> str:
    outputs = []
    repaired = hashlib.sha256(SOURCE.read_bytes()).hexdigest() != HISTORICAL_SOURCE_SHA256
    for historical in (True, False):
        names = expected_names + (["invalid_button_binding", "invalid_binding_count"] if repaired and not historical else [])
        for abi_mode in current_abi_modes(historical):
            output = compile_translation_unit(HARNESS, historical=historical, abi_mode=abi_mode)
            require(output.splitlines() == [f"case={name} result=PASS" for name in names] + [
                "production_source=HAL/pico/src/comms/ConfiguratorBackend.cpp",
                "production_handler_cases=11 actual_validator=linked result=PASS" if repaired and not historical else "production_handler_cases=9 result=PASS",
            ], "host production correspondence output drift")
            label = ("historical" if historical else "current") + (f" ABI={abi_mode}" if abi_mode else "")
            outputs.append(label + " translation-unit proof:\n" + output)
    return "".join(outputs)


def main() -> int:
    try:
        require(hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == "f483e7d371189663098dbec44b77c7cedf7274dc389d0513fc4cf7ca7a238d8f", "frozen historical fixture drift")
        value = json.loads(FIXTURE.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        expected_names = validate_fixture(value)
        validate_correspondence()
        output = compile_and_run(expected_names)
        print(output, end="")
        print("glyph_configurator_setconfig_transaction: PASS; separate historical/current literal TU proofs")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_configurator_setconfig_transaction: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
