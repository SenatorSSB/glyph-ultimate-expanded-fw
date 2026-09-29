#!/usr/bin/env python3
"""Validate GP-CONFIG-010's exact-source sanitizer characterization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/gp_config_010_mode_activation_capacity.json"
HARNESS = ROOT / "tools/fixtures/mode_selection_host/mode_selection_harness.cpp"
INCLUDE = ROOT / "tools/fixtures/mode_selection_host/include"
CASES = ["count_0", "count_10", "count_11", "count_13", "count_30", "count_31", "indices_0_to_12"]
GENERATED = "tools/fixtures/mode_selection_host/generated/config.pb.h"
PROVENANCE = "tools/fixtures/mode_selection_host/generated/provenance.json"
HOST_DOUBLE = "tools/fixtures/mode_selection_host/include/config.pb.h"
HEADER_SHA256 = "bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323"
PROVENANCE_SHA256 = "ec7340d123a4a213dbddd06fae3eee6c92424a2a7353db42b0f27c4abfc5c85b"
PROTO_SHA256 = "2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b"
OPTIONS_SHA256 = "6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805"
PACKAGE_SHA256 = "01f2027fcd3c19b304581c0bba7a9f0096a16842874e6686a38d168a69d952fe"
LICENSE_SHA256 = "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"
HOST_DOUBLE_SHA256 = "a8407293cc33e44985e386ab638332e64f7799b80c28c737598ced4253eb41ce"
GENERATED_CUSTODY = [
    GENERATED, PROVENANCE,
    "tools/fixtures/mode_selection_host/generated/nanopb.library.json",
    "tools/fixtures/mode_selection_host/generated/LICENSE.nanopb.txt",
    "tools/fixtures/mode_selection_host/generated/README.md",
]
SOURCE_RECORDS = [
    {"path": "src/core/mode_selection.cpp", "sha256": "8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44",
     "anchors": ["kModeActivationMaskCapacity = 30", "setup_mode_activation_bindings", "select_mode"]},
    {"path": "config/glyph/common/include/glyph_overrides.hpp", "sha256": "ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d",
     "anchors": [".game_mode_configs_count = 13", "GameModeConfig {"]},
]
MANIFEST_DEPENDENCIES = [
    "src/core/mode_selection.cpp", "config/glyph/common/include/glyph_overrides.hpp",
    "docs/runtime_config/gp_config_010_mode_activation_capacity.md",
    "docs/runtime_config/fixtures/gp_config_010_mode_activation_capacity.json",
    "tools/fixtures/mode_selection_host/mode_selection_harness.cpp", HOST_DOUBLE,
    GENERATED, PROVENANCE, GENERATED_CUSTODY[2], GENERATED_CUSTODY[3], GENERATED_CUSTODY[4],
    "tools/fixtures/custom_modifier_cache_host/schema/config.proto",
    "tools/fixtures/custom_modifier_cache_host/schema/config.options",
    "platformio.ini", "config/glyph/env.ini",
    "docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_PROTOCOL.md",
]


class ContractError(AssertionError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ContractError(message)


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), f"missing regular file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_custody(root: Path) -> None:
    for name in GENERATED_CUSTODY:
        require((root / name).is_file() and not (root / name).is_symlink(),
                f"missing regular generated fixture: {name}")
    result = subprocess.run(
        ["git", "ls-files", "--stage", "-z", "--", *GENERATED_CUSTODY],
        cwd=root, capture_output=True, text=True, check=True,
    )
    records: dict[str, str] = {}
    for line in result.stdout.split("\0"):
        if not line:
            continue
        metadata, path = line.split("\t", 1)
        mode, blob, stage = metadata.split()
        require(path not in records and mode == "100644" and stage == "0",
                f"unsafe generated fixture entry: {path}")
        records[path] = blob
    require(set(records) == set(GENERATED_CUSTODY), "generated fixture closure must be tracked")
    for name in GENERATED_CUSTODY:
        data = (root / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        require(records[name] == blob, f"staged generated fixture drift: {name}")


def validate_manifest(root: Path) -> None:
    path = root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = [entry for entry in manifest["entries"] if entry["id"] == "gp_config_010_mode_activation_capacity"]
    require(len(entries) == 1 and entries[0]["path"] == "tools/check_glyph_config_010_mode_activation_capacity.py",
            "capacity manifest entry")
    require(entries[0]["source_dependencies"] == MANIFEST_DEPENDENCIES,
            "capacity manifest dependency closure")


def validate_inputs(root: Path = ROOT) -> None:
    validate_custody(root)
    validate_manifest(root)
    value = json.loads((root / FIXTURE.relative_to(ROOT)).read_text(encoding="utf-8"))
    require(value["work_order"] == "GP-CONFIG-010", "fixture work order")
    require(value["capacity"] == 30 and value["default_count"] == 13, "capacity facts")
    require(value["cases"] == CASES, "case order")
    require(value["production_sources"] == SOURCE_RECORDS, "ordered production-source closure")
    require(value["generated_header"] == {
        "path": GENERATED, "sha256": HEADER_SHA256, "bytes": 73915,
        "version": "nanopb-0.4.9.2", "extent": "GameModeConfig game_mode_configs[30];",
        "provenance_path": PROVENANCE,
    }, "generated fixture identity")
    require(value["host_double"] == {
        "path": HOST_DOUBLE, "extent": "GameModeConfig game_mode_configs[30]{};",
    }, "host double identity")
    require(sha256(root / PROVENANCE) == PROVENANCE_SHA256, "provenance drift")
    provenance = json.loads((root / PROVENANCE).read_text(encoding="utf-8"))
    require(provenance["schema_name"] == "glyph_gp_val_028_generated_capacity_header"
            and provenance["work_order"] == "GP-VAL-028", "provenance identity")
    generated = provenance["generated_header"]
    require(generated == {
        "path": GENERATED, "sha256": HEADER_SHA256, "bytes": 73915,
        "generator_version": "nanopb-0.4.9.2", "proto_header_version": 40,
        "extent": 30,
    }, "generated provenance identity")
    header_path = root / GENERATED
    require(sha256(header_path) == HEADER_SHA256 and header_path.stat().st_size == 73915,
            "generated header drift")
    header = header_path.read_text(encoding="utf-8")
    require("/* Generated by nanopb-0.4.9.2 */" in header, "generated version drift")
    require("#if PB_PROTO_HEADER_VERSION != 40" in header, "proto header version drift")
    matches = re.findall(r"GameModeConfig\s+game_mode_configs\[(\d+)\];", header)
    require(matches == ["30"], "generated capacity drift")
    require(sha256(root / HOST_DOUBLE) == HOST_DOUBLE_SHA256, "host double drift")
    host_source = (root / HOST_DOUBLE).read_text(encoding="utf-8")
    host_matches = re.findall(r"GameModeConfig\s+game_mode_configs\[(\d+)\]\{\};", host_source)
    require(host_matches == matches, "host double extent differs from generated extent")
    require(HOST_DOUBLE != GENERATED and HOST_DOUBLE_SHA256 != HEADER_SHA256,
            "host double cannot be generated authority")

    schema = provenance["source_schema"]
    require(schema["commit"] == "db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8"
            and schema["selector"] == "https://github.com/GregTurbo/HayBox-proto#db4e2f6",
            "schema provenance drift")
    require(sha256(root / schema["proto_path"]) == schema["proto_sha256"] == PROTO_SHA256,
            "proto drift")
    require(sha256(root / schema["options_path"]) == schema["options_sha256"] == OPTIONS_SHA256,
            "options drift")
    require(sha256(root / schema["selector_path"]) == schema["selector_sha256"]
            == "c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf"
            and schema["selector"] in (root / schema["selector_path"]).read_text(encoding="utf-8"),
            "HayBox selector drift")

    nanopb = provenance["nanopb"]
    require(nanopb["commit"] == "160d4f09e5fabb2b66aa2dea32d4f38ace2c4b3f"
            and nanopb["tag"] == "0.4.9.2"
            and nanopb["generator_blob"] == "096d5c3b96b8a2712b087fc91e9cf74c2cd989ab"
            and nanopb["generator_sha256"] == "67d3c5e6de1e5dbd9f45bb4e5b7055d888d1afd6d6e1690791ab8607b6c6b738",
            "generator provenance drift")
    require(sha256(root / nanopb["package_path"]) == nanopb["package_sha256"] == PACKAGE_SHA256,
            "Nanopb package drift")
    package = json.loads((root / nanopb["package_path"]).read_text(encoding="utf-8"))
    require(package["name"] == "Nanopb" and package["version"] == nanopb["package_version"] == "0.4.92",
            "Nanopb package version drift")
    require(sha256(root / nanopb["license_path"]) == nanopb["license_sha256"] == LICENSE_SHA256,
            "Nanopb license drift")
    require(sha256(root / nanopb["selector_path"]) == nanopb["selector_sha256"]
            == "99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9"
            and nanopb["selector"] in (root / nanopb["selector_path"]).read_text(encoding="utf-8"),
            "Nanopb selector drift")
    require(provenance["host_generator"] == {"protobuf": "6.33.6", "grpcio_tools": "1.80.0"},
            "host generator drift")
    for record in value["production_sources"]:
        path = root / record["path"]
        require(sha256(path) == record["sha256"], f"source drift: {record['path']}")
        source = path.read_text(encoding="utf-8")
        for anchor in record["anchors"]:
            require(anchor in source, f"missing anchor: {record['path']}:{anchor}")
    source = (root / "src/core/mode_selection.cpp").read_text(encoding="utf-8")
    require("std::extent_v<decltype(Config::game_mode_configs)>" in source, "generated extent proof missing")
    require("kModeActivationMaskCapacity = 30" in source, "named capacity missing")
    require("if (mode_configs_count > kModeActivationMaskCapacity)" in source, "setup guard missing")
    require("if (config.game_mode_configs_count > kModeActivationMaskCapacity)" in source, "selection guard missing")
    require("sizeof(Config)" not in source, "Config-sized cache forbidden")


def main() -> int:
    try:
        validate_inputs()

        with tempfile.TemporaryDirectory(prefix="glyph-gp-config-010-") as temp:
            binary = Path(temp) / "mode_selection_host"
            command = ["c++", "-std=c++20", "-Wall", "-Wextra", "-pedantic", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", f"-I{INCLUDE}", str(HARNESS), "-o", str(binary)]
            compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            require(compiled.returncode == 0, f"host compile failed:\n{compiled.stdout}{compiled.stderr}")
            for case in CASES:
                result = subprocess.run([str(binary), case], cwd=ROOT, capture_output=True, text=True, check=False)
                require(result.returncode == 0 and result.stdout.strip() == f"case={case} result=PASS", f"case failed: {case}: {result.stdout}{result.stderr}")
                print(result.stdout, end="")
        print("glyph_config_010_mode_activation_capacity: PASS; 7 cases; authenticated current host fixture")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_config_010_mode_activation_capacity: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
