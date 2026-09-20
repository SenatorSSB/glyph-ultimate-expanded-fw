#!/usr/bin/env python3
"""Compile and run the exact production config-menu bodies under bounded host states."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/config_menu_invalid_state_characterization.json"
HARNESS = ROOT / "tools/fixtures/config_menu_host/menu_harness.cpp"
STUB_INCLUDE = ROOT / "tools/fixtures/config_menu_host/include"
CASES = ["null_current_mode", "empty_filtered_pages", "empty_child_page_update", "empty_usb_page_update", "injected_index_equals_count"]
EXPECTED_FAILURES = {"null_current_mode", "injected_index_equals_count"}
EXPECTED_RESULTS = {name: ("SANITIZER_FAILURE" if name in EXPECTED_FAILURES else "PASS") for name in CASES}

class ContractError(AssertionError):
    pass

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ContractError(message)

def load() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    require(value["schema_name"] == "glyph_config_menu_invalid_state_characterization", "fixture identity")
    require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-009", "fixture version")
    require([case["name"] for case in value["cases"]] == CASES, "case order")
    require({case["name"]: case["result"] for case in value["cases"]} == EXPECTED_RESULTS, "case result classification")
    require(value["observations"]["injected_state_label"] == "synthetic and reachability UNKNOWN", "injection label")
    return value

def validate_sources(value: dict) -> None:
    for record in value["production_sources"]:
        path = ROOT / record["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], f"source drift: {record['path']}")
        text = path.read_text(encoding="utf-8")
        for anchor in record["anchors"]:
            require(anchor in text, f"missing anchor: {record['path']}:{anchor}")
    text = HARNESS.read_text(encoding="utf-8")
    for include in [
        '"../../../HAL/pico/src/display/ConfigMenu.cpp"',
        '"../../../HAL/pico/src/display/DefaultConfigMenu.cpp"',
        '"../../../config/glyph/common/src/display/GlyphConfigMenu.cpp"',
    ]:
        require(text.count(include) == 1, f"production include count: {include}")
    require("ConfigMenu::HandleControls(" not in text, "harness copied production behavior")
    require("DefaultConfigMenu::DefaultConfigMenu(" not in text, "harness copied constructor")
    require("GlyphConfigMenu::GlyphConfigMenu(" not in text, "harness copied glyph constructor")

def run_case(binary: Path, name: str) -> tuple[int, str, str]:
    completed = subprocess.run([str(binary), name], cwd=ROOT, capture_output=True, text=True, check=False)
    return completed.returncode, completed.stdout, completed.stderr

def main() -> int:
    try:
        value = load()
        validate_sources(value)
        with tempfile.TemporaryDirectory(prefix="glyph-config-menu-host-") as temp:
            binary = Path(temp) / "config_menu_host"
            command = ["c++", "-std=c++20", "-Wall", "-Wextra", "-pedantic", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", f"-I{STUB_INCLUDE}", f"-I{ROOT / 'HAL/pico/include'}", f"-I{ROOT / 'config/glyph/common/include'}", str(HARNESS), "-o", str(binary)]
            compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            require(compiled.returncode == 0, f"host compile failed:\n{compiled.stdout}{compiled.stderr}")
            for name in [case for case in CASES if case not in EXPECTED_FAILURES]:
                code, stdout, stderr = run_case(binary, name)
                require(code == 0 and stdout.strip() == f"case={name} result=PASS", f"case failed: {name}: {stdout}{stderr}")
                print(stdout, end="")
            for name in CASES:
                if name not in EXPECTED_FAILURES:
                    continue
                code, stdout, stderr = run_case(binary, name)
                require(code != 0 and not stdout, f"{name} did not fail under sanitizer")
                require(any(token in stderr for token in ("AddressSanitizer", "UndefinedBehaviorSanitizer", "runtime error")), f"{name} failure was not sanitizer evidence")
                print(f"case={name} result=SANITIZER_FAILURE")
        print("production_sources=16 translation_units=3 result=PASS")
        print("glyph_config_menu_invalid_state_characterization: PASS; 5 cases; H1 host-only")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_config_menu_invalid_state_characterization: FAIL: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
