#!/usr/bin/env python3
"""Characterize the literal production NeoPixel SendReport body on host."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json"
HARNESS = ROOT / "tools/fixtures/neopixel_null_host/neo_harness.cpp"
INCLUDE = ROOT / "tools/fixtures/neopixel_null_host/include"
SOURCE_HEADER = ROOT / "HAL/pico/include/comms/NeoPixelBackend.hpp"
SOURCE_CALLER = ROOT / "config/glyph/common/src/config.cpp"


class CheckError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_fixture(value: dict) -> None:
    require(list(value) == [
        "schema_name", "schema_version", "work_order", "base_configurator_sha",
        "production_sources", "literal_include", "cases", "observations",
    ], "fixture schema or field order")
    require(value["schema_name"] == "glyph_neopixel_null_sendreport_characterization", "fixture identity")
    require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-016", "fixture version/work order")
    require(value["base_configurator_sha"] == "0da68bdab9bf0fed4ed595538bea9aba7d2f49f3", "base configurator identity")
    require(value["literal_include"] == "../../../HAL/pico/include/comms/NeoPixelBackend.hpp", "literal include identity")
    require([row["path"] for row in value["production_sources"]] == [
        "HAL/pico/include/comms/NeoPixelBackend.hpp", "config/glyph/common/src/config.cpp"
    ], "production source order")
    require([row["id"] for row in value["cases"]] == [
        "startup_null", "no_mode", "no_config", "zero_rgb_index",
        "out_of_range_rgb_index", "unsupported_animation", "unknown_animation_enum",
        "valid_static", "valid_dynamic",
    ], "case order")
    require([row["kind"] for row in value["cases"]] == ["null"] * 7 + ["control"] * 2, "case classification")
    require(value["cases"][0]["sequence_class"] == "source_supported_initial_member_state", "startup sequence classification")
    require(all(row["sequence_class"] == "injected_host_setup" for row in value["cases"][1:7]), "null injected sequence classification")
    obs = value["observations"]
    require(obs["physical_reachability"] == "UNKNOWN", "physical reachability claim")
    require(obs["physical_controller_crash"] == "NOT_CLAIMED", "physical crash claim")
    require(obs["repair_policy"] == "NOT_SELECTED", "repair policy claim")
    require(obs["non_claims"] == ["physical call reachability", "controller crash", "default RGB policy", "firmware repair", "hardware acceptance", "root cause"], "non-claims")


def load_fixture() -> dict:
    value = json.loads(FIXTURE.read_text(), object_pairs_hook=unique_object)
    validate_fixture(value)
    return value


def verify_sources(value: dict, harness_text: str | None = None) -> None:
    source_text = SOURCE_HEADER.read_text()
    caller_text = SOURCE_CALLER.read_text()
    by_path = {row["path"]: row for row in value["production_sources"]}
    for path, file, text in [
        ("HAL/pico/include/comms/NeoPixelBackend.hpp", SOURCE_HEADER, source_text),
        ("config/glyph/common/src/config.cpp", SOURCE_CALLER, caller_text),
    ]:
        expected = by_path[path]
        actual = hashlib.sha256(file.read_bytes()).hexdigest()
        require(actual == expected["sha256"], f"production source drift: {path}")
        for anchor in expected["required_anchors"]:
            require(anchor in text, f"source anchor missing in {path}: {anchor}")
    read = "uint8_t deltaHue = (diff/1000) * (interval * _config->speed);"
    guard = "if(_config == nullptr)"
    require(source_text.index(read) < source_text.index(guard), "null guard unexpectedly precedes _config speed access")
    harness = HARNESS.read_text() if harness_text is None else harness_text
    include = f'#include "{value["literal_include"]}"'
    require(harness.count(include) == 1, "production header must be literal-included exactly once")
    require("SendReport() {" not in harness, "copied SendReport body found in harness")
    require("reached_SendReport" in harness, "target-entry marker missing")


def adversarial_contract_checks(value: dict) -> int:
    cases = 0
    for mutate, label in [
        (lambda candidate: candidate.update(schema_version=2), "schema version"),
        (lambda candidate: candidate.update(base_configurator_sha="0" * 40), "base SHA"),
        (lambda candidate: candidate["cases"][1].update(sequence_class="source_supported_initial_member_state"), "injected/source classification"),
        (lambda candidate: candidate["observations"].update(physical_reachability="PROVEN"), "physical claim"),
    ]:
        candidate = json.loads(json.dumps(value))
        mutate(candidate)
        try:
            validate_fixture(candidate)
        except CheckError:
            cases += 1
        else:
            raise CheckError(f"adversarial fixture accepted: {label}")
    candidate = json.loads(json.dumps(value))
    candidate["production_sources"][0]["sha256"] = "0" * 64
    try:
        verify_sources(candidate)
    except CheckError:
        cases += 1
    else:
        raise CheckError("adversarial production source digest accepted")
    try:
        verify_sources(value, HARNESS.read_text() + "\nvoid NeoPixelBackend::SendReport() {}\n")
    except CheckError:
        cases += 1
    else:
        raise CheckError("copied production method body accepted")
    return cases


def run_checker(value: dict) -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-neopixel-null-") as temp:
        binary = Path(temp) / "neo_harness"
        compile_result = subprocess.run([
            "c++", "-std=c++20", "-Wall", "-Wextra", "-pedantic",
            "-fsanitize=undefined", "-fno-sanitize-recover=all",
            f"-I{INCLUDE}", f"-I{ROOT / 'HAL/pico/include'}",
            str(HARNESS), "-o", str(binary),
        ], cwd=ROOT, capture_output=True, text=True)
        require(compile_result.returncode == 0, f"host compile failed: {compile_result.stdout}{compile_result.stderr}")
        null_cases = [case["id"] for case in value["cases"] if case["kind"] == "null"]
        control_cases = [case["id"] for case in value["cases"] if case["kind"] == "control"]
        for case_id in null_cases:
            result = subprocess.run([str(binary), case_id], cwd=ROOT, capture_output=True, text=True)
            combined = result.stdout + result.stderr
            require("reached_SendReport" in result.stderr, f"{case_id}: target entry not observed: {combined}")
            require(result.returncode != 0, f"{case_id}: expected UBSan failure, got: {combined}")
            require("runtime error: member access within null pointer" in result.stderr, f"{case_id}: expected null member diagnostic: {combined}")
            require("NeoPixelBackend.hpp" in result.stderr and "SUMMARY: UndefinedBehaviorSanitizer" in result.stderr, f"{case_id}: sanitizer source/result marker missing: {combined}")
        for case_id in control_cases:
            result = subprocess.run([str(binary), case_id], cwd=ROOT, capture_output=True, text=True)
            require(result.returncode == 0, f"{case_id}: valid control failed: {result.stdout}{result.stderr}")
            require(f"case={case_id} result=RETURNED show_count=1" in result.stdout, f"{case_id}: SendReport return/show not proven: {result.stdout}")
        return len(null_cases) + len(control_cases)


def main() -> int:
    try:
        value = load_fixture()
        verify_sources(value)
        adversarial = adversarial_contract_checks(value)
        cases = run_checker(value)
        print(f"glyph_neopixel_null_sendreport_characterization: PASS; {cases} isolated cases; {adversarial} adversarial contracts; H1 host evidence; physical reachability UNKNOWN")
        return 0
    except (OSError, subprocess.SubprocessError, CheckError, ValueError, KeyError, TypeError) as exc:
        print(f"glyph_neopixel_null_sendreport_characterization: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
