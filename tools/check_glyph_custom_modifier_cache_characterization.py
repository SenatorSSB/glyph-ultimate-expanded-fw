#!/usr/bin/env python3
"""Validate exact-source GP-CONFIG-011 modifier-cache characterization."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/custom_modifier_cache_characterization.json"
HARNESS = ROOT / "tools/fixtures/custom_modifier_cache_host/modifier_cache_harness.cpp"
SCHEMA_DIR = Path("tools/fixtures/custom_modifier_cache_host/schema")
SCHEMA_FILES = [
    "config.proto", "config.options", "config.pb.h", "pb.h",
    "LICENSE.nanopb.txt", "haybox-proto.library.json",
]
# This reviewed digest pins the complete immutable upstream commit/blob/SHA
# inventory, independently of the mutable fixture's own identity claims.
PROVENANCE_SHA256 = "fca4d0d34165ee3d48b37864e357482d867b879ca1430433a81575de910cc59b"
HISTORICAL_FIXTURE_SHA256 = "ca259e765e4e22571917e7d1b88a7f90d655dad2a42d0d681e5850a42525fe73"
PROTO_COMMIT = "db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8"
NANOPB_COMMIT = "cad3c18ef15a663e30e3e43e3a752b66378adec1"
PROTO_SELECTOR = "https://github.com/GregTurbo/HayBox-proto#db4e2f6"
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


def regular_file(root: Path, relative: Path) -> Path:
    path = root / relative
    require(path.is_file(), f"missing file: {relative}")
    for part in [relative, *relative.parents]:
        require(not (root / part).is_symlink(), f"unsafe symlink: {part}")
    return path


def validate_schema(root: Path = ROOT) -> dict:
    names = [*SCHEMA_FILES, "provenance.json"]
    paths = [SCHEMA_DIR / name for name in names]
    for path in paths:
        regular_file(root, path)
    # Stage-zero regular-file custody is also required outside the aggregate.
    result = subprocess.run(
        ["git", "ls-files", "--stage", "-z", "--", *map(str, paths)],
        cwd=root, text=True, capture_output=True, check=True,
    )
    records = {}
    for line in result.stdout.split("\0"):
        if line:
            metadata, path = line.split("\t", 1)
            mode, blob, stage = metadata.split()
            require(path not in records and mode == "100644" and stage == "0",
                    f"unsafe tracked schema entry: {path}")
            records[path] = blob
    require(set(records) == set(map(str, paths)), "schema closure must be tracked regular files")
    provenance_path = root / SCHEMA_DIR / "provenance.json"
    require(sha256(provenance_path) == PROVENANCE_SHA256, "schema provenance drift")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    require(provenance["haybox_proto"]["commit"] == PROTO_COMMIT, "proto commit identity")
    require(provenance["nanopb"]["commit"] == NANOPB_COMMIT, "Nanopb commit identity")
    require(list(provenance["files"]) == SCHEMA_FILES, "ordered schema closure")
    require(provenance["custom_mode_modifiers_max_count"] == 20, "schema extent identity")
    for name, identity in provenance["files"].items():
        data = (root / SCHEMA_DIR / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        require(hashlib.sha256(data).hexdigest() == identity["sha256"], f"schema bytes drift: {name}")
        require(blob == identity["git_blob"], f"schema blob drift: {name}")
        require(records[str(SCHEMA_DIR / name)] == blob, f"staged schema blob drift: {name}")
    selector = regular_file(root, Path("config/glyph/env.ini")).read_text(encoding="utf-8")
    require(selector.splitlines().count("    " + PROTO_SELECTOR) == 1, "tracked proto selector drift")
    require("AnalogModifier modifiers[20];" in (root / SCHEMA_DIR / "config.pb.h").read_text(),
            "generated modifier extent drift")
    return provenance


def validate_fixture(value: dict) -> None:
    require(value["schema_name"] == "glyph_custom_modifier_cache_characterization", "fixture identity")
    require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-011", "fixture version/work order")
    require(value["cases"] == EXPECTED_CASES, "ordered case corpus")
    require(value["observations"]["non_claims"] == [
        "cache or schema repair", "modifier semantics", "SetConfig policy", "physical reachability",
        "device behavior", "firmware behavior", "hardware acceptance", "root cause",
    ], "non-claims")


def validate_correspondence(value: dict, root: Path = ROOT) -> None:
    historical = regular_file(root, FIXTURE.relative_to(ROOT))
    require(sha256(historical) == HISTORICAL_FIXTURE_SHA256, "historical characterization fixture drift")
    harness = regular_file(root, HARNESS.relative_to(ROOT))
    harness_text = harness.read_text(encoding="utf-8")
    require(sha256(harness) == value["harness"]["sha256"], "harness drift")
    require(harness_text.count('#include "../../../src/modes/CustomControllerMode.cpp"') == 1,
            "exact production implementation include is not uniquely bound")
    records = value["production_sources"]
    require([record["path"] for record in records] == SOURCE_PATHS, "ordered production-source set")
    for record in records:
        path = regular_file(root, Path(record["path"]))
        require(sha256(path) == record["sha256"], f"source drift: {record['path']}")
        text = path.read_text(encoding="utf-8")
        for anchor in record["anchors"]:
            require(anchor in text, f"missing source anchor {anchor} in {record['path']}")
    provenance = validate_schema(root)
    for filename, field in [
        ("config.pb.h", "generated_header_sha256"),
        ("config.proto", "config_proto_sha256"),
        ("config.options", "config_options_sha256"),
    ]:
        require(provenance["files"][filename]["sha256"] == value["resolved_schema"][field],
                f"historical schema correspondence drift: {filename}")
    require(value["resolved_schema"]["custom_mode_modifiers_max_count"] == 20, "schema max_count")
    require(value["resolved_schema"]["dependency_commit"] == PROTO_COMMIT, "dependency identity")


def compile_harness(output: Path) -> None:
    extent = output.parent / "schema_extent.cpp"
    extent.write_text(
        '#include <config.pb.h>\n'
        'static_assert(sizeof(((CustomModeConfig*)nullptr)->modifiers) / sizeof(AnalogModifier) == 20, '
        '"exact generated modifier extent");\n', encoding="utf-8",
    )
    command = [
        "c++", "-std=c++17", "-O1", "-g", "-fno-omit-frame-pointer",
        "-fsanitize=address,undefined,bounds", "-I" + str(SCHEMA_DIR),
        "-Itools/fixtures/custom_modifier_cache_host/include",
        "-Iinclude", "-IHAL/pico/include",
        str(HARNESS), "src/core/ControllerMode.cpp",
        "src/core/InputMode.cpp", "src/core/socd.cpp", str(extent), "-o", str(output),
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

    # Exercise real filesystem and Git-index failures in a disposable minimal
    # copy. The original checkout, schema, and historical record stay untouched.
    with tempfile.TemporaryDirectory(prefix="glyph-schema-negative-") as temp:
        root = Path(temp)
        relative_paths = [
            *map(Path, SOURCE_PATHS), FIXTURE.relative_to(ROOT), HARNESS.relative_to(ROOT),
            *(SCHEMA_DIR / name for name in [*SCHEMA_FILES, "provenance.json"]),
        ]
        for relative in relative_paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        subprocess.run(["git", "-c", "init.templateDir=", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-c", "core.autocrlf=false", "add", "--", *map(str, relative_paths)],
                       cwd=root, check=True)
        validate_correspondence(value, root)

        def rejected(label: str) -> None:
            try:
                validate_correspondence(value, root)
            except (Error, OSError, ValueError, subprocess.SubprocessError):
                return
            raise Error(f"negative control accepted: {label}")

        for name in [*SCHEMA_FILES, "provenance.json"]:
            path = root / SCHEMA_DIR / name
            original = path.read_bytes()
            path.unlink()
            rejected("missing " + name)
            path.write_bytes(original + b"\n")
            rejected("tampered " + name)
            path.unlink()
            path.symlink_to(ROOT / SCHEMA_DIR / name)
            rejected("symlink " + name)
            path.unlink()
            path.write_bytes(original)

        schema = root / SCHEMA_DIR
        held = root / "held-schema"
        schema.rename(held)
        schema.symlink_to(held, target_is_directory=True)
        rejected("symlink schema directory")
        schema.unlink()
        held.rename(schema)

        metadata = schema / "provenance.json"
        original = metadata.read_bytes()
        for section, field, mutation in [
            ("haybox_proto", "commit", "0" * 40),
            ("nanopb", "commit", "0" * 40),
            ("haybox_proto", "selector", PROTO_SELECTOR + "0"),
            ("files", "config.proto", {"sha256": "0" * 64, "git_blob": "0" * 40}),
        ]:
            altered = json.loads(original)
            altered[section][field] = mutation
            metadata.write_text(json.dumps(altered), encoding="utf-8")
            rejected("wrong " + section + "." + field)
        altered = json.loads(original)
        altered["custom_mode_modifiers_max_count"] = 10
        metadata.write_text(json.dumps(altered), encoding="utf-8")
        rejected("wrong schema capacity")
        header = schema / "config.pb.h"
        header_original = header.read_bytes()
        header.write_bytes(header_original.replace(b"AnalogModifier modifiers[20];", b"AnalogModifier modifiers[10];"))
        data = header.read_bytes()
        altered["files"]["config.pb.h"] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
        }
        metadata.write_text(json.dumps(altered), encoding="utf-8")
        rejected("coordinated schema and provenance replacement")
        metadata.write_bytes(original)
        header.write_bytes(header_original)

        for relative in [
            "config/glyph/env.ini", "src/modes/CustomControllerMode.cpp",
            str(FIXTURE.relative_to(ROOT)), str(HARNESS.relative_to(ROOT)),
        ]:
            path = root / relative
            original_source = path.read_bytes()
            if relative.endswith("env.ini"):
                path.write_bytes(original_source.replace(PROTO_SELECTOR.encode(), (PROTO_SELECTOR + "0").encode()))
            else:
                path.write_bytes(original_source + b"\n")
            rejected("source/selector drift " + relative)
            path.write_bytes(original_source)
        subprocess.run(["git", "update-index", "--force-remove", "--", str(SCHEMA_DIR / "pb.h")],
                       cwd=root, check=True)
        rejected("untracked schema header")


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
