#!/usr/bin/env python3
"""Validate the source-declared, literal-only Glyph configuration census."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/build_input_non_selector_configuration.json"
SOURCES = {
    "platformio.ini": ("4d56f8630c1b12e84cd12f40ce05a4dc71b9362e", "99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9"),
    "config/glyph/env.ini": ("fac4e20461ad632ca1d65826241a4a9c73630f04", "c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf"),
}
CHAIN = ["env", "arduino_pico_base", "glyph_base", "env:glyph_mk6"]
SCALARS = ["build_type", "lib_ldf_mode", "debug_tool", "monitor_speed", "board_build.f_cpu", "board_build.filesystem_size", "lib_archive", "upload_protocol"]
LISTS = ["build_flags", "build_unflags"]
DECLARATION_COUNTS = Counter({
    ("platformio.ini", "env", "build_type"): 1,
    ("platformio.ini", "env", "lib_ldf_mode"): 1,
    ("platformio.ini", "env", "build_flags"): 4,
    ("platformio.ini", "env", "custom_nanopb_options"): 1,
    ("platformio.ini", "arduino_pico_base", "debug_tool"): 1,
    ("platformio.ini", "arduino_pico_base", "monitor_speed"): 1,
    ("platformio.ini", "arduino_pico_base", "board_build.f_cpu"): 1,
    ("platformio.ini", "arduino_pico_base", "board_build.filesystem_size"): 1,
    ("platformio.ini", "arduino_pico_base", "lib_archive"): 1,
    ("platformio.ini", "arduino_pico_base", "build_unflags"): 1,
    ("platformio.ini", "arduino_pico_base", "build_flags"): 10,
    ("config/glyph/env.ini", "glyph_base", "extends"): 1,
    ("config/glyph/env.ini", "glyph_base", "upload_protocol"): 1,
    ("config/glyph/env.ini", "glyph_base", "build_flags"): 3,
    ("config/glyph/env.ini", "env:glyph_mk6", "extends"): 1,
})
EXPECTED_REFERENCES = [
    {"path": "platformio.ini", "section": "arduino_pico_base", "key": "build_flags", "raw": "    ${env.build_flags}", "order": 1, "origin": "arduino_pico_base", "expands": "env.build_flags"},
    {"path": "platformio.ini", "section": "arduino_pico_base", "key": "custom_nanopb_options", "raw": "    ${env.custom_nanopb_options}", "order": 1, "origin": "arduino_pico_base", "expands": "env.custom_nanopb_options"},
    {"path": "config/glyph/env.ini", "section": "glyph_base", "key": "build_flags", "raw": "    ${arduino_pico_base.build_flags}", "order": 1, "origin": "glyph_base", "expands": "arduino_pico_base.build_flags"},
    {"path": "config/glyph/env.ini", "section": "glyph_base", "key": "build_src_filter", "raw": "    ${arduino_pico_base.build_src_filter}", "order": 1, "origin": "glyph_base", "expands": "arduino_pico_base.build_src_filter"},
    {"path": "config/glyph/env.ini", "section": "glyph_base", "key": "lib_deps", "raw": "    ${arduino_pico_base.lib_deps}", "order": 1, "origin": "glyph_base", "expands": "arduino_pico_base.lib_deps"},
    {"path": "config/glyph/env.ini", "section": "glyph_base", "key": "lib_ignore", "raw": "    ${env.lib_ignore}", "order": 1, "origin": "glyph_base", "expands": "env.lib_ignore"},
    {"path": "config/glyph/env.ini", "section": "env:glyph_mk6", "key": "extends", "raw": "extends = glyph_base", "order": 1, "origin": "env:glyph_mk6", "expands": "glyph_base"},
]


def fail(message: str) -> None:
    raise ValueError(message)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def check() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    required = {"schema_name", "schema_version", "status", "canonical_environment", "source_files", "inheritance_order", "scalar_keys", "ordered_list_keys", "non_path_custom_nanopb_options", "runtime_interpolation_tokens", "references", "declarations"}
    if set(data) != required:
        fail("schema mismatch")
    if data["schema_name"] != "glyph_build_input_non_selector_configuration" or data["schema_version"] != 1 or data["status"] != "declared_effective_literal_census_not_platformio_or_compiler_resolution":
        fail("identity/status mismatch")
    if data["canonical_environment"] != "glyph_mk6" or data["inheritance_order"] != CHAIN or data["scalar_keys"] != SCALARS or data["ordered_list_keys"] != LISTS or data["non_path_custom_nanopb_options"] != ["--error-on-unmatched"] or data["runtime_interpolation_tokens"] != ["${PIOENV}", "${platformio.name}"]:
        fail("contract boundary mismatch")
    if data["source_files"] != [{"path": path, "git_blob": values[0], "sha256": values[1]} for path, values in SOURCES.items()]:
        fail("source identity declaration mismatch")
    for path, (blob, digest) in SOURCES.items():
        if git("hash-object", path) != blob or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            fail(f"source drift: {path}")
    references = data["references"]
    if references != EXPECTED_REFERENCES:
        fail("list-reference expansion mismatch")
    texts = {path: (ROOT / path).read_text(encoding="utf-8").splitlines() for path in SOURCES}
    for reference in references:
        if reference["raw"].strip() not in {line.strip() for line in texts[reference["path"]]}:
            fail(f"reference missing: {reference['path']}:{reference['raw']}")
    declarations = data["declarations"]
    fields = {"path", "section", "key", "raw", "order", "origin", "value"}
    if any(set(item) != fields for item in declarations):
        fail("declaration shape mismatch")
    if Counter((item["path"], item["section"], item["key"]) for item in declarations) != DECLARATION_COUNTS:
        fail("exact declaration coverage mismatch")
    for item in declarations:
        if item["path"] not in SOURCES or item["origin"] not in CHAIN or item["key"] not in SCALARS + LISTS + ["custom_nanopb_options", "extends"]:
            fail("declaration scope mismatch")
        if item["raw"].strip() not in {line.strip() for line in texts[item["path"]]}:
            fail(f"declaration missing: {item['path']}:{item['raw']}")
        if item["order"] < 1:
            fail("declaration order mismatch")
    if not any(item["key"] == "build_flags" and "${PIOENV}" in item["value"] for item in declarations) or not any(item["key"] == "build_flags" and "${platformio.name}" in item["value"] for item in declarations):
        fail("unresolved interpolation token was omitted or promoted")
    if not any(item["key"] == "custom_nanopb_options" and item["value"] == "--error-on-unmatched" for item in declarations):
        fail("custom nanopb option missing")
    print(f"glyph_build_input_non_selector_configuration: PASS; declarations={len(declarations)}; references={len(references)}; chain={'/'.join(CHAIN)}")


if __name__ == "__main__":
    try:
        check()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"glyph_build_input_non_selector_configuration: FAIL: {exc}")
        sys.exit(1)
