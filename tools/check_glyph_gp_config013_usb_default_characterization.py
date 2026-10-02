#!/usr/bin/env python3
"""Exact-source host characterization for GP-CONFIG-013; makes no policy choice."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/gp_config013_usb_default_characterization.json"
HARNESS = ROOT / "tools/fixtures/gp_config013_usb_host/usb_harness.cpp"
HOST012 = ROOT / "tools/fixtures/gp_config012_button_host"
P014 = ROOT / "docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json"
BASE = "7a2dba85332c90fa2bcc6c06e1205c4745facb92"
REQUIRED_SOURCE_PATHS = {
    "HAL/pico/src/comms/backend_init.cpp", "src/core/config_utils.cpp",
    "HAL/pico/include/util/state_util.hpp", "config/glyph/common/src/config.cpp",
    "HAL/pico/src/core/Persistence.cpp", "HAL/pico/src/comms/ConfiguratorBackend.cpp",
    "src/core/mode_selection.cpp", "HAL/pico/include/config_defaults.hpp",
    "config/glyph/common/include/glyph_overrides.hpp", "HAL/pico/include/comms/backend_init.hpp",
    "platformio.ini", "config/glyph/env.ini",
    "tools/fixtures/gp_config012_button_host/schema/config.proto",
    "tools/fixtures/gp_config012_button_host/schema/config.options",
    "tools/fixtures/gp_config012_button_host/generated/config.pb.h",
    "tools/fixtures/gp_config012_button_host/generated/config.pb.c",
    "tools/fixtures/gp_config012_button_host/nanopb/pb.h",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_common.h",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_common.c",
    "tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt",
    "docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json",
    "docs/runtime_config/gp_prov_014_decoder_closure.md",
    "docs/runtime_config/fixtures/gp_config012_button_mask_characterization.json",
}


class ContractError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in items:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regular(relative: str) -> Path:
    path = ROOT / relative
    require(path.is_file(), f"missing regular file: {relative}")
    cursor = path
    while cursor != ROOT and cursor != cursor.parent:
        require(not cursor.is_symlink(), f"symlink in source/dependency path: {relative}")
        cursor = cursor.parent
    return path


def read_fixture() -> dict[str, object]:
    value = json.loads(regular(FIXTURE.relative_to(ROOT).as_posix()).read_text(encoding="utf-8"),
                       object_pairs_hook=pairs)
    require(value["schema_name"] == "glyph_gp_config013_usb_default_characterization" and
            value["schema_version"] == 1, "fixture schema identity mismatch")
    require(value["work_order_id"] == "GP-CONFIG-013" and value["work_order_state"] == "READY",
            "fixture authorization identity mismatch")
    require(value["base_configurator_sha"] == BASE, "fixture base identity mismatch")
    base_object = subprocess.run(["git", "cat-file", "-e", f"{BASE}^{{commit}}"], cwd=ROOT,
                                 capture_output=True, text=True)
    require(base_object.returncode == 0, "authorized base commit is unavailable")
    require(value["candidate_successor"] == "GP-VAL-036" and
            value["canonical_integration"] == "WAITING_FOR_GP-VAL-036_DONE",
            "candidate stop point drift")
    return value


def validate_source(value: dict[str, object]) -> None:
    records = value["production_sources"]
    require({item["path"] for item in records} == REQUIRED_SOURCE_PATHS,
            "production/accepted-dependency source inventory changed")
    seen: set[str] = set()
    for item in records:
        path = item["path"]
        require(path not in seen, f"duplicate production/dependency path: {path}")
        seen.add(path)
        file = regular(path)
        require(sha256(file) == item["sha256"], f"source/dependency SHA-256 drift: {path}")
        blob = subprocess.run(["git", "rev-parse", f"{BASE}:{path}"], cwd=ROOT,
                              capture_output=True, text=True)
        require(blob.returncode == 0 and blob.stdout.strip() == item["blob"],
                f"source/dependency Git blob drift: {path}")
        text = file.read_text(encoding="utf-8", errors="strict")
        for anchor in item["anchors"]:
            require(anchor in text, f"source anchor missing: {path}: {anchor}")

    p014 = json.loads(regular(P014.relative_to(ROOT).as_posix()).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs)
    require(p014["schema_name"] == "glyph_gp_prov_014_decoder_closure" and
            p014["resolution"]["nanopb_tag"] == "0.4.9.2" and
            p014["resolution"]["nanopb_commit"] == "160d4f09e5fabb2b66aa2dea32d4f38ace2c4b3f",
            "accepted GP-PROV-014 Nanopb identity drift")
    require(p014["resolution"]["proto_instances"][0]["source_commit"] ==
            "db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8", "selected schema source identity drift")
    header = regular("tools/fixtures/gp_config012_button_host/generated/config.pb.h").read_text()
    require("uint8_t default_usb_backend_config;" in header and
            "communication_backend_configs[15]" in header and "game_mode_configs[30]" in header,
            "generated uint8/tag-7 or Config extents changed")
    proto = regular("tools/fixtures/gp_config012_button_host/schema/config.proto").read_text()
    require("uint32 default_usb_backend_config = 7" in proto, "wire schema tag 7 changed")
    backend = regular("HAL/pico/src/comms/backend_init.cpp").read_text()
    getter = backend[backend.index("usb_backend_getter_t get_usb_backend_config_default = []("):]
    getter = getter[:getter.index("\n};") + 3]
    require("config.default_usb_backend_config > 0" in getter and
            "config.default_usb_backend_config <= config.communication_backend_configs_count" in getter and
            "config.communication_backend_configs[config.default_usb_backend_config - 1]" in getter and
            "else" not in getter, "USB getter's one-based guarded copy shape changed")
    init = backend[backend.index("size_t initialize_backends("):backend.index("\nvoid init_primary_backend(")]
    require("CommunicationBackendConfig usb_backend_config;" in init and
            "get_usb_backend_config(usb_backend_config, config);" in init and
            "usb_backend_config.backend_id" in init,
            "preliminary USB initialization source sequence changed")
    require("COMMS_BACKEND_XINPUT" in init and "COMMS_BACKEND_DINPUT" in init and
            "COMMS_BACKEND_NINTENDO_SWITCH" in init and "COMMS_BACKEND_CONFIGURATOR" in init,
            "USB detection branch set changed")
    require("watchdog_caused_reboot()" in init and "backend_config.default_mode_config" in init,
            "watchdog/default-mode path changed")
    mode_selection = regular("src/core/mode_selection.cpp").read_text(encoding="utf-8")
    keyboard_case = mode_selection[mode_selection.index("case MODE_KEYBOARD:"):]
    require("backend->BackendId() != COMMS_BACKEND_DINPUT" in keyboard_case and
            "mode_config.keyboard_mode_config" in keyboard_case,
            "Keyboard mode DInput applicability check changed")


def function_fragment(source: str, start: str, next_marker: str) -> str:
    a = source.find(start)
    require(a >= 0, f"missing production fragment: {start}")
    b = source.find(next_marker, a + len(start))
    require(b >= 0, f"missing production fragment end: {next_marker}")
    return source[a:b].rstrip() + "\n"


def lambda_fragment(source: str, start: str, end: str) -> str:
    a = source.find(start)
    require(a >= 0, f"missing production callback: {start}")
    b = source.find(end, a + len(start))
    require(b >= 0, f"missing production callback end: {end}")
    return source[a:b].rstrip() + "\n"


def production_fragments() -> str:
    backend = regular("HAL/pico/src/comms/backend_init.cpp").read_text(encoding="utf-8")
    utils = regular("src/core/config_utils.cpp").read_text(encoding="utf-8")
    state = regular("HAL/pico/include/util/state_util.hpp").read_text(encoding="utf-8")
    pieces = [
        function_fragment(backend, "size_t initialize_backends(", "\nvoid init_primary_backend("),
        lambda_fragment(backend, "backend_config_selector_t get_backend_config_default = [](",
                        "/* Default is to get default USB backend from config. */"),
        lambda_fragment(backend, "usb_backend_getter_t get_usb_backend_config_default = [](",
                        "// clang-format on"),
        function_fragment(utils, "CommunicationBackendConfig backend_config_from_buttons(",
                          "uint8_t backend_config_id_from_backend_id("),
        function_fragment(state, "inline uint64_t make_button_mask(", "inline bool any_button_held("),
    ]
    return "\n".join(piece.strip() for piece in pieces) + "\n"


def compile_harness(temp: Path, sanitized: bool = False) -> Path:
    temp.mkdir(parents=True, exist_ok=True)
    cc, cxx = shutil.which("cc"), shutil.which("c++")
    require(cc is not None and cxx is not None, "host C/C++ compiler unavailable")
    flags = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitized else []
    nanopb = HOST012 / "nanopb"
    generated = HOST012 / "generated"
    objects: list[Path] = []
    for i, rel in enumerate(("pb_decode.c", "pb_common.c")):
        obj = temp / f"nanopb-{i}.o"
        result = subprocess.run([cc, "-std=c99", "-O0", "-g", "-fshort-enums", *flags,
                                 f"-I{nanopb}", f"-I{generated}", "-c", str(nanopb / rel),
                                 "-o", str(obj)], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, f"Nanopb compile failed: {result.stdout}{result.stderr}")
        objects.append(obj)
    obj = temp / "generated-config.o"
    result = subprocess.run([cc, "-std=c99", "-O0", "-g", "-fshort-enums", *flags, f"-I{nanopb}",
                             f"-I{generated}", "-c", str(generated / "config.pb.c"), "-o", str(obj)],
                            cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, f"generated schema compile failed: {result.stdout}{result.stderr}")
    objects.append(obj)
    (temp / "production_fragments.inc").write_text(production_fragments(), encoding="utf-8")
    harness_obj = temp / "harness.o"
    result = subprocess.run([cxx, "-std=gnu++20", "-O0", "-g", "-fshort-enums", *flags,
                             f"-I{nanopb}", f"-I{generated}", f"-I{temp}", "-c", str(HARNESS),
                             "-o", str(harness_obj)], cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, f"host harness compile failed: {result.stdout}{result.stderr}")
    binary = temp / "gp-config013-usb"
    result = subprocess.run([cxx, "-fshort-enums", *flags, *map(str, [*objects, harness_obj]), "-o", str(binary)],
                            cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, f"host harness link failed: {result.stdout}{result.stderr}")
    return binary


def validate_observations(binary: Path, value: dict[str, object]) -> str:
    result = subprocess.run([str(binary)], cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0 and not result.stderr,
            f"production-fragment harness failed: {result.stdout}{result.stderr}")
    lines = result.stdout.splitlines()
    require("getter_matrix indices=0..255 counts=0..15 valid=120 invalid=3976" in lines,
            "getter index/count exhaustive matrix mismatch")
    decode_rows: dict[str, dict[str, str]] = {}
    route_rows: dict[str, dict[str, str]] = {}
    for line in lines:
        if line.startswith("decode=") or line.startswith("route="):
            fields = dict(part.split("=", 1) for part in line.split() if "=" in part)
            if line.startswith("decode="):
                require(fields["decode"] not in decode_rows, f"duplicate decoder row: {fields['decode']}")
                decode_rows[fields["decode"]] = fields
            else:
                require(fields["route"] not in route_rows, f"duplicate route row: {fields['route']}")
                route_rows[fields["route"]] = fields
    expected_decode = {
        "omitted_tag7": ("accept", "0"), "repeated_tag7": ("accept", "1"),
        "uint8_overflow_256": ("reject", "0"), "partial_malformed_trailing": ("reject", "2"),
        "malformed_tag7_wire_type": ("reject", "0"), "malformed_overlong_varint": ("reject", "0"),
        "backend_count_16": ("reject", "0"),
    }
    for name, (status, usb) in expected_decode.items():
        row = decode_rows.get(name)
        require(row is not None and row.get("result") == status and row.get("usb") == usb,
                f"decoder observation changed for {name}: {row}")
    expected_routes = {
        "usb_detect_xinput": ("1", "2,2", "1", "0"),
        "usb_detect_dinput": ("1", "2,2", "1", "0"),
        "usb_detect_switch": ("1", "2,2", "1", "0"),
        "configurator_detect": ("1", "2,2", "1", "0"),
        "gc_preliminary_usb": ("1", "2,3", "1", "0"),
        "button_hold_dinput": ("1", "1", "1", "0"),
        "button_hold_switch": ("1", "7", "3", "0"),
        "button_hold_keyboard_dinput": ("1", "1", "6", "0"),
        "watchdog_override": ("1", "2,2", "2", "1"),
        "undetected_console": ("0", "2,0", "0", "0"),
    }
    for name, expected in expected_routes.items():
        row = route_rows.get(name)
        require(row is not None and (row.get("count"), row.get("primary"), row.get("mode"), row.get("saves")) == expected,
                f"source route observation changed for {name}: {row}")
    required = set(value["cases"])
    expected_cases = {"getter_index_0_255_by_backend_count_0_15"} | set(decode_rows) | set(route_rows)
    require(len(value["cases"]) == len(required) and required == expected_cases,
            "fixture case inventory drift")
    observations = value["observations"]
    require(observations["getter_matrix"] == {
        "index_range": "0..255", "backend_count_range": "0..15", "valid_copies": 120,
        "invalid_preserved": 3976}, "fixture getter observations drift")
    for name, row in decode_rows.items():
        expected = observations["decoder"][name]
        require((expected["result"], str(expected["usb_index"]), str(expected["decoded_backend_count"])) ==
                (row["result"], row["usb"], row["backends"]),
                f"fixture decoder observation drift: {name}")
    for name, row in route_rows.items():
        expected = observations["routes"][name]
        calls = [int(part) for part in row["primary"].split(",")]
        require((expected["count"], expected["primary_calls"], expected["mode_id"], expected["saves"]) ==
                (int(row["count"]), calls, int(row["mode"]), int(row["saves"])),
                f"fixture route observation drift: {name}")
    return result.stdout


def validate_adversarial_identity() -> None:
    original = b"exact closure bytes\n"
    digest = hashlib.sha256(original).hexdigest()
    with tempfile.TemporaryDirectory(prefix="glyph-gp-config013-identity-") as temp_name:
        root = Path(temp_name)
        target = root / "nested/asset.bin"
        target.parent.mkdir(parents=True)
        def check() -> None:
            require(target.is_file() and not target.is_symlink() and sha256(target) == digest,
                    "closure identity mismatch")
        target.write_bytes(original); check()
        target.unlink()
        try: check()
        except ContractError: pass
        else: raise ContractError("omitted dependency negative was accepted")
        target.write_bytes(original + b"substitution")
        try: check()
        except ContractError: pass
        else: raise ContractError("substituted dependency negative was accepted")


def main() -> int:
    try:
        value = read_fixture()
        validate_source(value)
        validate_adversarial_identity()
        with tempfile.TemporaryDirectory(prefix="glyph-gp-config013-") as temp_name:
            temp = Path(temp_name)
            output = validate_observations(compile_harness(temp / "normal"), value)
            sanitized = validate_observations(compile_harness(temp / "sanitized", True), value)
            require(sanitized == output, "sanitized/ordinary harness observations differ")
        print("GP-CONFIG-013 exact-source host characterization PASS")
        print(output, end="")
        return 0
    except (ContractError, KeyError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"GP-CONFIG-013 characterization FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
