#!/usr/bin/env python3
"""Compile exact production GET_CONFIG/raw-load bodies against host doubles."""
from __future__ import annotations
import copy, hashlib, json, subprocess, tempfile
from pathlib import Path
from glyph_campaign_transition import verify_current_source
from check_glyph_configurator_setconfig_transaction import compile_translation_unit, current_abi_modes, ContractError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/getconfig_raw_load_characterization.json"
RAW = ROOT / "tools/fixtures/getconfig_raw_host/handler_harness.cpp"
GET = ROOT / "tools/fixtures/getconfig_raw_host/getconfig_handler_harness.cpp"
SOURCE_GET = ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp"
SOURCE_RAW = ROOT / "HAL/pico/src/core/Persistence.cpp"

class Error(AssertionError): pass
def require(ok, msg):
    if not ok: raise Error(msg)
def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, f"duplicate key: {key}")
        result[key] = value
    return result
def load():
    require(hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == "c81f187323d0da42facf145dd6b976e990435337f18c5510bd5312d429b70891", "frozen historical fixture drift")
    value = json.loads(FIXTURE.read_text(), object_pairs_hook=pairs)
    require(list(value) == ["schema_name","schema_version","work_order","production_sources","cases","observations"], "fixture schema")
    require(value["schema_name"] == "glyph_getconfig_raw_load_characterization" and value["schema_version"] == 1 and value["work_order"] == "GP-PERSIST-002", "fixture identity")
    require(value["production_sources"] == [
        {"path":"HAL/pico/src/comms/ConfiguratorBackend.cpp","sha256":"28ef942416d0ec4b92588304fcf72f219a0c6b1e2a582f20e2dc7e0e07d1b876","function":"bool ConfiguratorBackend::HandleGetConfig()"},
        {"path":"HAL/pico/src/core/Persistence.cpp","sha256":"941cc54f0fb762e6067db338601325d33cf7f980148a59caa1d61f226e140955","function":"size_t Persistence::LoadConfigRaw(Print &out, bool validate)"},
    ], "production source identity")
    require(value["cases"] == ["invalid_check_no_raw_load","open_failure","seek_failure","empty_eof","payload_order","validate_false","zero_output_write","partial_output_write","read_error_sentinel","raw_result_ignored_packet_end_wins","packet_end_failure_propagates"], "case order")
    require(value["observations"]["non_claims"] == ["device delivery","filesystem correctness","persistence integrity","recovery","atomicity","hardware acceptance"], "non-claims")
    return value
def correspondence():
    get_text, raw_text = SOURCE_GET.read_text(), SOURCE_RAW.read_text()
    expected = {row["path"]: row["sha256"] for row in load()["production_sources"]}
    frozen = verify_current_source(ROOT, "HAL/pico/src/comms/ConfiguratorBackend.cpp", expected["HAL/pico/src/comms/ConfiguratorBackend.cpp"])
    start = "bool ConfiguratorBackend::HandleGetConfig()"
    end = "bool ConfiguratorBackend::HandleSetConfig()"
    require(get_text[get_text.index(start):get_text.index(end)] == frozen.decode()[frozen.decode().index(start):frozen.decode().index(end)], "GET body drift")
    require(hashlib.sha256(SOURCE_RAW.read_bytes()).hexdigest() == expected["HAL/pico/src/core/Persistence.cpp"], "LoadConfigRaw source drift")
    require("bool ConfiguratorBackend::HandleGetConfig()" in get_text and "persistence.LoadConfigRaw(_out, false);" in get_text, "GET source anchors")
    require("size_t Persistence::LoadConfigRaw(Print &out, bool validate)" in raw_text and "out.write((uint8_t)value);" in raw_text, "raw source anchors")
    for harness, include in [(GET, "ConfiguratorBackend.cpp"), (RAW, "Persistence.cpp")]:
        text = harness.read_text()
        require(text.count(f'"../../../HAL/pico/src/{"comms/ConfiguratorBackend.cpp" if include == "ConfiguratorBackend.cpp" else "core/Persistence.cpp"}"') == 1, f"literal {include} include")
        require("HandleGetConfig() {" not in text and "LoadConfigRaw(Print &out" not in text, "copied production body")
def compile_run(source, expected):
    if source == GET:
        for historical in (True, False):
            for abi_mode in current_abi_modes(historical):
                output = compile_translation_unit(GET, historical=historical, abi_mode=abi_mode)
                require(all(line in output for line in expected), "GET historical/current output drift")
        return
    with tempfile.TemporaryDirectory(prefix="glyph-getconfig-host-") as td:
        binary = Path(td) / "host"
        include = ROOT / ("tools/fixtures/configurator_setconfig_host/include" if source == GET else "tools/fixtures/getconfig_raw_host/include")
        command = ["c++","-std=c++17","-Wall","-Wextra","-pedantic",f"-I{include}",f"-I{ROOT / 'HAL/pico/include'}",str(source),"-o",str(binary)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, f"compile failed: {result.stdout}{result.stderr}")
        run = subprocess.run([str(binary)], cwd=ROOT, capture_output=True, text=True)
        require(run.returncode == 0 and all(line in run.stdout for line in expected), f"host failed: {run.stdout}{run.stderr}")
def adversarial(value):
    candidate = copy.deepcopy(value); candidate["schema_version"] = 2
    try:
        if candidate["schema_version"] == 1: raise Error("tamper accepted")
    except Error: raise
    candidate = copy.deepcopy(value); candidate["production_sources"][0]["sha256"] = "0" * 64
    require(candidate["production_sources"][0]["sha256"] != hashlib.sha256(SOURCE_GET.read_bytes()).hexdigest(), "source tamper accepted")
    raw = FIXTURE.read_text(); require('"schema_version": 1' in raw, "fixture literal")
    return 1
def main():
    try:
        value = load(); correspondence(); adversarial(value)
        compile_run(RAW, ["case=open_failure result=PASS","case=payload_order result=PASS","case=validate_false result=PASS","production_method=LoadConfigRaw literal include result=PASS"])
        compile_run(GET, ["case=invalid_check_no_raw_load result=PASS","case=raw_result_ignored_packet_end_wins result=PASS","case=packet_end_failure_propagates result=PASS"])
        print("glyph_getconfig_raw_load_characterization: PASS; 11 cases; H1 research only")
        return 0
    except (OSError, subprocess.SubprocessError, Error, ContractError, ValueError, KeyError, TypeError) as exc:
        print(f"glyph_getconfig_raw_load_characterization: FAIL: {exc}")
        return 1
if __name__ == "__main__": raise SystemExit(main())
