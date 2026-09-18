#!/usr/bin/env python3
"""Compile and run the real GP-CONFIG-005 production SetConfig handler."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

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
    require(source["sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "source digest")
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


def compile_and_run(expected_names: list[str]) -> str:
    with tempfile.TemporaryDirectory(prefix="glyph-setconfig-host-") as temp:
        binary = Path(temp) / "configurator_setconfig_host"
        command = [
            "c++", "-std=c++17", "-Wall", "-Wextra", "-pedantic",
            f"-I{STUB_INCLUDE}", f"-I{ROOT / 'HAL/pico/include'}",
            str(HARNESS), "-o", str(binary),
        ]
        compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        require(compiled.returncode == 0, f"host compile failed:\n{compiled.stdout}{compiled.stderr}")
        executed = subprocess.run([str(binary)], cwd=ROOT, capture_output=True, text=True, check=False)
        require(executed.returncode == 0, f"host harness failed:\n{executed.stdout}{executed.stderr}")
        lines = executed.stdout.splitlines()
        require(lines[: len(expected_names)] == [f"case={name} result=PASS" for name in expected_names],
                "host case output drift")
        require(lines[len(expected_names):] == [
            "production_source=HAL/pico/src/comms/ConfiguratorBackend.cpp",
            "production_handler_cases=9 result=PASS",
        ], "host production correspondence output drift")
        return executed.stdout


def main() -> int:
    try:
        value = json.loads(FIXTURE.read_text(encoding="utf-8"), object_pairs_hook=pairs)
        expected_names = validate_fixture(value)
        validate_correspondence()
        output = compile_and_run(expected_names)
        print(output, end="")
        print("glyph_configurator_setconfig_transaction: PASS; compiled exact production handler; 9 cases")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_configurator_setconfig_transaction: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
