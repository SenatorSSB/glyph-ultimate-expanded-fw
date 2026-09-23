#!/usr/bin/env python3
"""Validate GP-CONFIG-010's exact-source sanitizer characterization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/gp_config_010_mode_activation_capacity.json"
HARNESS = ROOT / "tools/fixtures/mode_selection_host/mode_selection_harness.cpp"
INCLUDE = ROOT / "tools/fixtures/mode_selection_host/include"
CASES = ["count_0", "count_10", "count_11", "count_13", "count_30", "count_31", "indices_0_to_12"]


class ContractError(AssertionError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ContractError(message)


def main() -> int:
    try:
        value = json.loads(FIXTURE.read_text(encoding="utf-8"))
        require(value["work_order"] == "GP-CONFIG-010", "fixture work order")
        require(value["capacity"] == 30 and value["default_count"] == 13, "capacity facts")
        require(value["cases"] == CASES, "case order")
        for record in value["production_sources"]:
            path = ROOT / record["path"]
            require(path.is_file(), f"missing source: {record['path']}")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], f"source drift: {record['path']}")
            source = path.read_text(encoding="utf-8")
            for anchor in record["anchors"]:
                require(anchor in source, f"missing anchor: {record['path']}:{anchor}")

        source = (ROOT / "src/core/mode_selection.cpp").read_text(encoding="utf-8")
        require("std::extent_v<decltype(Config::game_mode_configs)>" in source, "generated extent proof missing")
        require("kModeActivationMaskCapacity = 30" in source, "named capacity missing")
        require("if (mode_configs_count > kModeActivationMaskCapacity)" in source, "setup guard missing")
        require("if (config.game_mode_configs_count > kModeActivationMaskCapacity)" in source, "selection guard missing")
        require("sizeof(Config)" not in source, "Config-sized cache forbidden")

        with tempfile.TemporaryDirectory(prefix="glyph-gp-config-010-") as temp:
            binary = Path(temp) / "mode_selection_host"
            command = ["c++", "-std=c++20", "-Wall", "-Wextra", "-pedantic", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", f"-I{INCLUDE}", str(HARNESS), "-o", str(binary)]
            compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            require(compiled.returncode == 0, f"host compile failed:\n{compiled.stdout}{compiled.stderr}")
            for case in CASES:
                result = subprocess.run([str(binary), case], cwd=ROOT, capture_output=True, text=True, check=False)
                require(result.returncode == 0 and result.stdout.strip() == f"case={case} result=PASS", f"case failed: {case}: {result.stdout}{result.stderr}")
                print(result.stdout, end="")
        print("glyph_config_010_mode_activation_capacity: PASS; 7 cases; H3 integration candidate validation")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_config_010_mode_activation_capacity: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
