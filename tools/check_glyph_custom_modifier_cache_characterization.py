#!/usr/bin/env python3
"""Validate exact-source GP-CONFIG-011 modifier-cache characterization."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/custom_modifier_cache_characterization.json"
HARNESS = ROOT / "tools/fixtures/custom_modifier_cache_host/modifier_cache_harness.cpp"
BUILD_HEADER = ROOT / ".pio/build/glyph_mk6/nanopb/generated-src/config.pb.h"
PROTO = ROOT / ".pio/libdeps/glyph_mk6/HayBox-proto/config.proto"
OPTIONS = ROOT / ".pio/libdeps/glyph_mk6/HayBox-proto/config.options"
EXPECTED_CASES = [
    "setconfig_0", "setconfig_10", "setconfig_11", "setconfig_20",
    "process_0", "process_10", "process_11", "process_20",
]
SOURCE_PATHS = [
    "include/modes/CustomControllerMode.hpp", "src/modes/CustomControllerMode.cpp",
    "include/core/ControllerMode.hpp", "src/core/ControllerMode.cpp",
    "include/core/InputMode.hpp", "src/core/InputMode.cpp",
    "include/core/socd.hpp", "src/core/socd.cpp", "HAL/pico/include/util/state_util.hpp",
    "include/core/state.hpp", "platformio.ini", "config/glyph/env.ini",
]


class Error(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Error(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_fixture(value: dict) -> None:
    require(value["schema_name"] == "glyph_custom_modifier_cache_characterization", "fixture identity")
    require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-011", "fixture version/work order")
    require(value["cases"] == EXPECTED_CASES, "ordered case corpus")
    require(value["observations"]["non_claims"] == [
        "cache or schema repair", "modifier semantics", "SetConfig policy", "physical reachability",
        "device behavior", "firmware behavior", "hardware acceptance", "root cause",
    ], "non-claims")


def validate_correspondence(value: dict) -> None:
    harness_text = HARNESS.read_text(encoding="utf-8")
    require(sha256(HARNESS) == value["harness"]["sha256"], "harness drift")
    require(harness_text.count('#include "../../../src/modes/CustomControllerMode.cpp"') == 1,
            "exact production implementation include is not uniquely bound")
    records = value["production_sources"]
    require([record["path"] for record in records] == SOURCE_PATHS, "ordered production-source set")
    for record in records:
        path = ROOT / record["path"]
        require(path.is_file() and not path.is_symlink(), f"missing or unsafe source: {record['path']}")
        require(sha256(path) == record["sha256"], f"source drift: {record['path']}")
        text = path.read_text(encoding="utf-8")
        for anchor in record["anchors"]:
            require(anchor in text, f"missing source anchor {anchor} in {record['path']}")
    require(BUILD_HEADER.is_file() and not BUILD_HEADER.is_symlink(), "missing generated schema header")
    require(sha256(BUILD_HEADER) == value["resolved_schema"]["generated_header_sha256"], "generated schema drift")
    require(sha256(PROTO) == value["resolved_schema"]["config_proto_sha256"], "config.proto drift")
    require(sha256(OPTIONS) == value["resolved_schema"]["config_options_sha256"], "config.options drift")
    require(value["resolved_schema"]["custom_mode_modifiers_max_count"] == 20, "schema max_count")
    require(value["resolved_schema"]["dependency_commit"] == "db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8", "dependency identity")


def compile_harness(output: Path) -> None:
    command = [
        "c++", "-std=c++17", "-O1", "-g", "-fno-omit-frame-pointer",
        "-fsanitize=address,undefined,bounds", "-I.pio/build/glyph_mk6/nanopb/generated-src",
        "-I.pio/libdeps/glyph_mk6/Nanopb", "-Itools/fixtures/custom_modifier_cache_host/include",
        "-Iinclude", "-IHAL/pico/include",
        str(HARNESS), "src/core/ControllerMode.cpp",
        "src/core/InputMode.cpp", "src/core/socd.cpp", "-o", str(output),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    require(result.returncode == 0, f"host harness compile failed:\n{result.stdout}\n{result.stderr}")


def run_cases(binary: Path, expected: dict[str, str]) -> None:
    for case in EXPECTED_CASES:
        result = subprocess.run([str(binary), case], cwd=ROOT, text=True, capture_output=True)
        if expected[case] == "PASS":
            require(result.returncode == 0, f"{case} unexpectedly failed:\n{result.stderr}")
            require(f"case={case} status=completed" in result.stdout, f"{case} missing completion marker")
        else:
            require(result.returncode != 0, f"{case} did not fail under sanitizer")
            combined = result.stdout + result.stderr
            require("AddressSanitizer" in combined or "UndefinedBehaviorSanitizer" in combined
                    or "BOUNDARY_VIOLATION" in combined,
                    f"{case} failed without sanitizer evidence")


def adversarial(value: dict) -> None:
    tampered = json.loads(json.dumps(value))
    tampered["cases"] = list(reversed(tampered["cases"]))
    try:
        validate_fixture(tampered)
    except Error:
        pass
    else:
        raise Error("reversed case corpus accepted")
    tampered = json.loads(json.dumps(value))
    tampered["resolved_schema"]["custom_mode_modifiers_max_count"] = 10
    try:
        validate_fixture(tampered)
        validate_correspondence(tampered)
    except Error:
        pass
    else:
        raise Error("schema capacity mutation accepted")


def main() -> int:
    try:
        value = json.loads(FIXTURE.read_text(encoding="utf-8"))
        validate_fixture(value)
        validate_correspondence(value)
        expected = value["expected_results"]
        with tempfile.TemporaryDirectory(prefix="glyph-custom-modifier-") as temp:
            binary = Path(temp) / "modifier_cache_harness"
            compile_harness(binary)
            run_cases(binary, expected)
        adversarial(value)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, KeyError, TypeError, Error) as exc:
        print(f"glyph_custom_modifier_cache_characterization: FAIL: {exc}")
        return 1
    print("glyph_custom_modifier_cache_characterization: PASS; 8 cases; H1 characterization only")
    print("physical_reachability=UNKNOWN hardware_acceptance=NOT_APPLICABLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
