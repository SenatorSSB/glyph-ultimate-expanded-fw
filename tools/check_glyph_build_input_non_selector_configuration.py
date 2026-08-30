#!/usr/bin/env python3
"""Check the declared-only non-selector configuration census.

This checker compares a reviewed literal census with the two tracked INI
sources.  It deliberately does not invoke PlatformIO, a compiler, or any
dependency, and does not interpret the effect of a literal.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/build_input_non_selector_configuration.json"
DOC = ROOT / "docs/runtime_config/build_input_non_selector_configuration.md"
SOURCES = {
    "platformio.ini": ("4d56f8630c1b12e84cd12f40ce05a4dc71b9362e", "99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9"),
    "config/glyph/env.ini": ("fac4e20461ad632ca1d65826241a4a9c73630f04", "c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf"),
}
SCALARS = {"build_type", "lib_ldf_mode", "debug_tool", "monitor_speed", "board_build.f_cpu", "board_build.filesystem_size", "lib_archive", "upload_protocol"}
LISTS = {"build_flags", "build_unflags"}
REFERENCE_KEYS = {"build_flags", "custom_nanopb_options", "build_src_filter", "lib_deps", "lib_ignore"}
REFERENCE_SOURCES = {
    ("platformio.ini", "arduino_pico_base", "build_flags"),
    ("platformio.ini", "arduino_pico_base", "build_src_filter"),
    ("platformio.ini", "arduino_pico_base", "lib_deps"),
    ("config/glyph/env.ini", "glyph_base", "build_flags"),
    ("config/glyph/env.ini", "glyph_base", "build_src_filter"),
    ("config/glyph/env.ini", "glyph_base", "lib_deps"),
    ("config/glyph/env.ini", "glyph_base", "lib_ignore"),
}
SCALAR_ORDERS = {("env", "build_type"): 1, ("env", "lib_ldf_mode"): 2, ("arduino_pico_base", "debug_tool"): 1, ("arduino_pico_base", "monitor_speed"): 2, ("arduino_pico_base", "board_build.f_cpu"): 3, ("arduino_pico_base", "board_build.filesystem_size"): 4}
NANOPB = {"--error-on-unmatched"}
SECTIONS = {"env", "arduino_pico_base", "glyph_base", "env:glyph_mk6"}
INTERPOLATION = {"${PIOENV}", "${platformio.name}"}


def fail(message: str) -> None:
    raise AssertionError(message)


def exact_keys(value: object, keys: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        fail(f"{label} keys drifted")


def source_records(path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    section = ""
    declarations: list[dict[str, str]] = []
    references: list[dict[str, str]] = []
    orders: dict[tuple[str, str], int] = {}
    active: tuple[str, str] | None = None
    for line in lines:
        header = re.fullmatch(r"\[([^]]+)\]", line)
        if header:
            section, active = header.group(1), None
            continue
        match = re.match(r"^([A-Za-z0-9_.:-]+)\s*=\s*(.*)$", line)
        if match:
            key, value = match.groups()
            active = (section, key)
            if section not in SECTIONS:
                continue
            if key in SCALARS or key == "extends" or (key in LISTS and value.strip() and not value.strip().startswith("${")):
                record = {"path": path, "section": section, "key": key, "raw": line.strip(), "order": SCALAR_ORDERS.get((section, key), 1), "origin": section, "value": value.strip()}
                declarations.append(record)
            continue
        if active and line.strip() and line.startswith((" ", "\t")):
            section_name, key = active
            if section not in SECTIONS or key not in REFERENCE_KEYS:
                continue
            order_key = (section_name, key)
            orders[order_key] = orders.get(order_key, 0) + 1
            token = line.strip()
            if token.startswith("${") and token.endswith("}") and (path, section_name, key) in REFERENCE_SOURCES:
                references.append({"path": path, "section": section_name, "key": key, "raw": line.rstrip(), "order": orders[order_key], "origin": section_name, "expands": token[2:-1]})
                continue
            if (key in LISTS and not token.startswith("${")) or token in NANOPB:
                order = orders[order_key] + (3 if section_name == "arduino_pico_base" and key == "build_flags" else 0)
                declarations.append({"path": path, "section": section_name, "key": key, "raw": line.rstrip(), "order": order, "origin": section_name, "value": token})
    return declarations, references


def normalize_records(records: list[dict[str, str]]) -> list[dict[str, object]]:
    return [{key: (0 if key == "order" else record[key]) for key in ("path", "section", "key", "raw", "order", "origin", "value")} for record in records]


def normalize_refs(records: list[dict[str, str]]) -> list[dict[str, object]]:
    return [{key: record[key] for key in ("path", "section", "key", "raw", "order", "origin", "expands")} for record in records]


def without_order(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{key: value for key, value in record.items() if key != "order"} for record in records]


def tracked_blob(path: str) -> str:
    result = subprocess.run(["git", "ls-files", "-s", "--", path], cwd=ROOT, text=True, capture_output=True, check=True)
    rows = result.stdout.splitlines()
    if len(rows) != 1 or not rows[0].startswith("100644 "):
        fail(f"{path} is not one tracked stage-0 regular file")
    return rows[0].split()[1]


def validate(data: dict[str, object]) -> None:
    exact_keys(data, {"schema_name", "schema_version", "status", "canonical_environment", "source_files", "inheritance_order", "scalar_keys", "ordered_list_keys", "non_path_custom_nanopb_options", "runtime_interpolation_tokens", "chain_references", "references", "declarations"}, "fixture")
    if data["schema_name"] != "glyph_build_input_non_selector_configuration" or data["schema_version"] != 1 or data["status"] != "declared_effective_literal_census_not_platformio_or_compiler_resolution" or data["canonical_environment"] != "glyph_mk6":
        fail("fixture identity/status drifted")
    if data["inheritance_order"] != ["env", "arduino_pico_base", "glyph_base", "env:glyph_mk6"] or data["scalar_keys"] != sorted(SCALARS, key=lambda x: ["build_type", "lib_ldf_mode", "debug_tool", "monitor_speed", "board_build.f_cpu", "board_build.filesystem_size", "lib_archive", "upload_protocol"].index(x)) or set(data["ordered_list_keys"]) != LISTS or data["non_path_custom_nanopb_options"] != sorted(NANOPB) or set(data["runtime_interpolation_tokens"]) != INTERPOLATION:
        fail("reviewed key or unresolved-token boundary drifted")
    files = data["source_files"]
    if not isinstance(files, list) or [{f["path"]: (f["git_blob"], f["sha256"])} for f in files] != [{path: identity} for path, identity in SOURCES.items()]:
        fail("source identities drifted")
    for path, (blob, digest) in SOURCES.items():
        if tracked_blob(path) != blob or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            fail(f"source identity mismatch: {path}")
    parsed: list[dict[str, object]] = []
    parsed_refs: list[dict[str, object]] = []
    for path in SOURCES:
        declarations, references = source_records(path)
        parsed.extend(normalize_records(declarations))
        parsed_refs.extend(normalize_refs(references))
    parsed_chain = [{"path": r["path"], "section": r["section"], "key": r["key"], "raw": r["raw"], "order": r["order"], "origin": r["origin"], "expands": r["value"]} for r in parsed if r["key"] == "extends"]
    if without_order(normalize_records(data["declarations"])) != without_order(parsed) or without_order(data["references"]) != without_order(parsed_refs) or without_order(data["chain_references"]) != without_order(parsed_chain):
        fail("literal declaration/reference correspondence drifted")
    for record in data["declarations"]:
        if set(record) != {"path", "section", "key", "raw", "order", "origin", "value"} or record["section"] not in SECTIONS or record["key"] not in SCALARS | LISTS | {"custom_nanopb_options", "extends"}:
            fail("malformed or out-of-scope declaration")
        if record["value"] in INTERPOLATION or record["value"].startswith("+<"):
            fail("selector or unresolved value entered literal census")
        if not isinstance(record["order"], int) or record["order"] < 1:
            fail("declaration order is not positive")
    for record in data["references"]:
        if set(record) != {"path", "section", "key", "raw", "order", "origin", "expands"} or not record["expands"]:
            fail("malformed reference")
    if not DOC.exists() or "declared literal census only" not in DOC.read_text(encoding="utf-8") or "does not resolve PlatformIO" not in DOC.read_text(encoding="utf-8"):
        fail("scope documentation missing")


def adversarial_checks(data: dict[str, object]) -> None:
    for mutation in ("declarations", "references", "source_files"):
        altered = copy.deepcopy(data)
        altered[mutation] = altered[mutation][:-1]
        try:
            validate(altered)
        except (AssertionError, KeyError, IndexError):
            continue
        fail(f"adversarial omission accepted: {mutation}")


def main() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    validate(data)
    adversarial_checks(data)
    print("PASS: declared non-selector configuration census")


if __name__ == "__main__":
    main()
