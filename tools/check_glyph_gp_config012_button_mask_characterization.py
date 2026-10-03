#!/usr/bin/env python3
"""Characterize exact Nanopb Button decoding and Glyph mask callers for GP-CONFIG-012."""
from __future__ import annotations

import hashlib

from glyph_campaign_transition import verify_current_source
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/gp_config012_button_mask_characterization.json"
HOST = ROOT / "tools/fixtures/gp_config012_button_host"
HARNESS = HOST / "button_harness.cpp"
GENERATED = HOST / "generated"
NANOPB = HOST / "nanopb"
SCHEMA = HOST / "schema"
PROVENANCE = ROOT / "docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json"
PROVENANCE_DOC = ROOT / "docs/runtime_config/gp_prov_014_decoder_closure.md"

UPSTREAM_NANOPB_COMMIT = "160d4f09e5fabb2b66aa2dea32d4f38ace2c4b3f"
PROTO_SELECTOR = "https://github.com/GregTurbo/HayBox-proto#db4e2f6"
SOURCE_PATHS = [
    "HAL/pico/include/util/state_util.hpp",
    "src/modes/CustomControllerMode.cpp",
    "src/core/mode_selection.cpp",
    "src/core/config_utils.cpp",
    "HAL/pico/src/comms/ConfiguratorBackend.cpp",
    "HAL/pico/src/core/Persistence.cpp",
    "HAL/pico/src/display/ConfigMenu.cpp",
    "HAL/pico/src/display/DefaultConfigMenu.cpp",
    "config/glyph/common/src/display/GlyphConfigMenu.cpp",
    "config/glyph/common/src/config.cpp",
    "config/glyph/common/include/glyph_overrides.hpp",
    "platformio.ini",
    "config/glyph/env.ini",
]
HOST_ASSETS = {
    "nanopb_pb_h": "nanopb/pb.h",
    "nanopb_pb_decode_c": "nanopb/pb_decode.c",
    "nanopb_pb_decode_h": "nanopb/pb_decode.h",
    "nanopb_pb_common_c": "nanopb/pb_common.c",
    "nanopb_pb_common_h": "nanopb/pb_common.h",
    "generated_c": "generated/config.pb.c",
    "generated_h": "generated/config.pb.h",
    "config_proto": "schema/config.proto",
    "config_options": "schema/config.options",
}


class ContractError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regular(root: Path, relative: str) -> Path:
    path = root / relative
    require(path.is_file(), f"missing regular file: {relative}")
    cursor = path
    while cursor != root and cursor != cursor.parent:
        require(not cursor.is_symlink(), f"symlink forbidden in fixture path: {relative}")
        cursor = cursor.parent
    return path


def section(source: str, start: str, end: str | None) -> str:
    begin = source.find(start)
    require(begin >= 0, f"missing production function: {start}")
    finish = len(source) if end is None else source.find(end, begin + len(start))
    require(finish >= 0, f"missing end anchor for: {start}")
    return source[begin:finish].rstrip() + "\n"


def production_fragments() -> tuple[str, dict[str, str]]:
    custom = regular(ROOT, "src/modes/CustomControllerMode.cpp").read_text(encoding="utf-8")
    mode = regular(ROOT, "src/core/mode_selection.cpp").read_text(encoding="utf-8")
    config = regular(ROOT, "src/core/config_utils.cpp").read_text(encoding="utf-8")
    custom_body = section(custom, "void CustomControllerMode::SetConfig(", "void CustomControllerMode::UpdateDigitalOutputs")
    mode_body = section(mode, "void setup_mode_activation_bindings(", None)
    config_body = section(config, "CommunicationBackendConfig backend_config_from_buttons(",
                          "CommunicationBackendConfig backend_config_from_id(")
    require(custom_body.count("make_button_mask(") == 2, "custom modifier/combo caller census drift")
    require(mode_body.count("make_button_mask(") == 1, "mode activation caller census drift")
    require(config_body.count("make_button_mask(") == 1, "backend activation caller census drift")
    return "\n".join((custom_body, mode_body, config_body)), {
        "custom_modifier_and_combo": hashlib.sha256(custom_body.encode()).hexdigest(),
        "mode_activation": hashlib.sha256(mode_body.encode()).hexdigest(),
        "backend_activation": hashlib.sha256(config_body.encode()).hexdigest(),
    }


def validate_provenance(value: dict[str, object]) -> None:
    provenance = json.loads(regular(ROOT, PROVENANCE.relative_to(ROOT).as_posix()).read_text(encoding="utf-8"),
                            object_pairs_hook=pairs)
    require(provenance["schema_name"] == "glyph_gp_prov_014_decoder_closure", "GP-PROV-014 fixture identity")
    require(provenance["resolution"]["nanopb_commit"] == UPSTREAM_NANOPB_COMMIT, "upstream Nanopb commit drift")
    require(provenance["resolution"]["nanopb_tag"] == "0.4.9.2", "accepted Nanopb tag drift")
    expected = {item["role"]: item for item in provenance["files"]}
    for role, relative in HOST_ASSETS.items():
        check_asset_identity(ROOT, (HOST / relative).relative_to(ROOT).as_posix(), expected[role], role)
    license_recorded = provenance["resolution"]["nanopb_license_sha256"]
    license_path = regular(ROOT, (HOST / "LICENSE.nanopb.txt").relative_to(ROOT).as_posix())
    require(sha256(license_path) == license_recorded, "Nanopb license bytes mismatch")
    require(provenance["resolution"]["generation_input_declaration"] ==
            "+<.pio/libdeps/${PIOENV}/HayBox-proto/config.proto>", "generated input declaration drift")
    require(provenance["resolution"]["proto_instances"][0]["source_commit"] ==
            "db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8", "selected proto commit drift")
    require(expected["generated_h"]["sha256"] == sha256(GENERATED / "config.pb.h"),
            "generated header identity drift")
    require(expected["generated_c"]["sha256"] == sha256(GENERATED / "config.pb.c"), "generated C identity drift")
    require(sha256(PROVENANCE_DOC) == value["provenance_document_sha256"], "GP-PROV-014 source note drift")


def check_asset_identity(root: Path, relative: str, record: dict[str, object], role: str) -> None:
    path = regular(root, relative)
    require(path.stat().st_size == record["bytes"], f"accepted closure size mismatch: {role}")
    require(sha256(path) == record["sha256"], f"accepted closure SHA-256 mismatch: {role}")


def validate_identity_adversarial_controls() -> None:
    with tempfile.TemporaryDirectory(prefix="glyph-gp-config012-identity-") as temp_name:
        root = Path(temp_name)
        target = root / "nanopb/pb.h"
        target.parent.mkdir(parents=True)
        original = b"authenticated fixture bytes\n"
        target.write_bytes(original)
        record = {"bytes": len(original), "sha256": hashlib.sha256(original).hexdigest()}
        check_asset_identity(root, "nanopb/pb.h", record, "nanopb_pb_h")
        target.unlink()
        try:
            check_asset_identity(root, "nanopb/pb.h", record, "nanopb_pb_h")
        except ContractError:
            pass
        else:
            raise ContractError("accepted closure omission control did not reject missing asset")
        target.write_bytes(original + b"tampered")
        try:
            check_asset_identity(root, "nanopb/pb.h", record, "nanopb_pb_h")
        except ContractError:
            pass
        else:
            raise ContractError("accepted closure tamper control did not reject changed bytes")


def enum_values(header: str) -> dict[str, int]:
    match = re.search(r"typedef enum _Button\s*\{(.*?)\}\s*Button\s*;", header, re.S)
    require(match is not None, "generated Button enum missing")
    pairs_found = [(name, int(number)) for name, number in
                   re.findall(r"\b(BTN_[A-Z0-9_]+)\s*=\s*(\d+)", match.group(1))]
    require([number for _, number in pairs_found] == list(range(61)), "Button enumerators must remain exactly 0..60")
    return dict(pairs_found)


def validate_source(value: dict[str, object]) -> tuple[str, dict[str, str]]:
    sources = value["production_sources"]
    require([item["path"] for item in sources] == SOURCE_PATHS, "ordered source inventory drift")
    texts: dict[str, str] = {}
    for item in sources:
        path = regular(ROOT, item["path"])
        # Authenticate the current transition separately; these frozen producer
        # observations describe B020, while the unchanged mask bodies below
        # are compiled from the current checkout.
        text = verify_current_source(ROOT, item["path"], item["sha256"]).decode("utf-8")
        for anchor in item["anchors"]:
            require(anchor in path.read_text(encoding="utf-8"), f"current source anchor missing: {anchor}")
            require(anchor in text, f"production source anchor missing: {item['path']}: {anchor}")
        texts[item["path"]] = text
    helper = texts[SOURCE_PATHS[0]]
    require("button_mask |= (1ULL << (buttons[j] - 1));" in helper, "helper shift body drift")
    require("nanopb/Nanopb@^0.4.8" in texts["platformio.ini"], "Nanopb compatible-range selector drift")
    require("-fshort-enums" in texts["platformio.ini"], "Pico short-enum ABI flag missing")
    require(PROTO_SELECTOR in texts["config/glyph/env.ini"], "selected HayBox-proto selector drift")
    require("pb_decode(&istream, Config_fields, &candidate)" in texts[SOURCE_PATHS[4]],
            "Configurator decode path drift")
    require("pb_decode(&istream, Config_fields, &config)" in texts[SOURCE_PATHS[5]],
            "Persistence decode path drift")
    configurator_body = section(texts[SOURCE_PATHS[4]], "bool ConfiguratorBackend::HandleSetConfig()", "bool ConfiguratorBackend::HandleUnknownCommand(")
    persistence_body = section(texts[SOURCE_PATHS[5]], "bool Persistence::LoadConfig(Config &config)", "bool Persistence::CheckSavedConfig()")
    require("pb_decode(&istream, Config_fields, &candidate)" in configurator_body,
            "Configurator transaction decode path drift")
    require("pb_decode(&istream, Config_fields, &config)" in persistence_body,
            "Persistence load decode path drift")
    for name, body in (("Configurator", configurator_body), ("Persistence", persistence_body)):
        require("Button" not in body and "BTN_" not in body and "make_button_mask" not in body,
                f"{name} producer path gained Button validation or mask semantics")
    for path in SOURCE_PATHS[6:9]:
        menu_source = texts[path]
        require("make_button_mask" not in menu_source and "activation_binding" not in menu_source,
                f"menu path gained direct activation Button conversion: {path}")
    defaults = texts["config/glyph/common/include/glyph_overrides.hpp"]
    activations = re.findall(r"\.activation_binding\s*=\s*\{([^}]*)\}", defaults)
    button_names = enum_values((GENERATED / "config.pb.h").read_text(encoding="utf-8"))
    named_bindings: list[list[str]] = []
    for binding in activations:
        names = re.findall(r"BTN_[A-Z0-9_]+", binding)
        require(names and all(name in button_names and button_names[name] in range(1, 61) for name in names),
                "default activation binding contains unspecified or unknown Button")
        named_bindings.append(names)
    require(named_bindings, "default activation binding source inventory empty")
    require(value["default_activation_bindings"] == named_bindings,
            "source-supported default activation binding matrix drift")
    return production_fragments()


def compile_variant(temp: Path, name: str, sanitizers: list[str]) -> Path:
    cc, cxx = shutil.which("cc"), shutil.which("c++")
    require(cc is not None and cxx is not None, "host C/C++ compiler unavailable")
    flags = ["-O0", "-g", "-fshort-enums", *sanitizers]
    objects: list[Path] = []
    for index, source in enumerate([NANOPB / "pb_decode.c", NANOPB / "pb_common.c", GENERATED / "config.pb.c"]):
        obj = temp / f"{name}-{index}.o"
        command = [cc, "-std=c99", *flags, f"-I{NANOPB}", f"-I{GENERATED}", "-c", str(source), "-o", str(obj)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, f"{name} C source compile failed:\n{result.stdout}{result.stderr}")
        objects.append(obj)
    fragments, _ = production_fragments()
    (temp / "production_fragments.inc").write_text(fragments, encoding="utf-8")
    harness_obj = temp / f"{name}-harness.o"
    command = [cxx, "-std=gnu++17", *flags, f"-I{GENERATED}", f"-I{NANOPB}",
               f"-I{HOST / 'include'}",
               f"-I{ROOT / 'HAL/pico/include'}",
               f"-I{ROOT / 'tools/fixtures/custom_modifier_cache_host/include'}",
               f"-I{temp}", "-c", str(HARNESS), "-o", str(harness_obj)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, f"{name} C++ source compile failed:\n{result.stdout}{result.stderr}")
    binary = temp / name
    result = subprocess.run([cxx, *flags, *map(str, [*objects, harness_obj]), "-o", str(binary)],
                            cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, f"{name} link failed:\n{result.stdout}{result.stderr}")
    return binary


def run(binary: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(binary), *args], cwd=ROOT, capture_output=True, text=True)


def validate_decoder(binary: Path) -> tuple[str, dict[str, str]]:
    result = run(binary, "decode")
    require(result.returncode == 0, f"decoder matrix failed:\n{result.stdout}{result.stderr}")
    lines = result.stdout.splitlines()
    require(lines[0] == "abi sizeof_button=1 activation_element=1 modifier_element=1 empty_config=accept",
            "host ABI/empty negative control drift")
    require(lines[1] == "descriptor activation_element=1", "Nanopb enum descriptor width drift")
    records: dict[str, str] = {}
    for line in lines[2:]:
        fields = dict(part.split("=", 1) for part in line.split() if "=" in part)
        require("case" in fields and "decoder" in fields, f"invalid decoder output row: {line}")
        require(fields["case"] not in records, f"duplicate decoder row: {fields['case']}")
        records[fields["case"]] = line
    for value in range(61):
        fields = dict(part.split("=", 1) for part in records[f"enum_{value}"].split() if "=" in part)
        require(fields.get("decoder") == "accept" and fields.get("raw") == str(value),
                f"named/schema Button {value} did not preserve raw byte: {records[f'enum_{value}']}")
    for required in ("enum_61", "enum_62", "enum_63", "enum_64", "enum_65", "enum_127", "enum_255",
                     "enum_256", "enum_300", "enum_-1", "packed_four", "mixed_four",
                     "extent_activation_five", "extent_modifier_four", "malformed_truncated_varint",
                     "malformed_overlong_varint"):
        require(required in records, f"missing decoder characterization row: {required}")
    require("decoder=accept count=4" in records["packed_four"], "valid packed repeated control rejected")
    require("decoder=accept count=4" in records["mixed_four"], "valid mixed packed/unpacked control rejected")
    require("decoder=reject" in records["extent_activation_five"], "activation extent overrun accepted")
    require("decoder=reject" in records["extent_modifier_four"], "modifier button extent overrun accepted")
    require("decoder=reject" in records["malformed_truncated_varint"], "truncated varint accepted")
    require("decoder=reject" in records["malformed_overlong_varint"], "overlong varint accepted")
    return result.stdout, records


def validate_sanitizers(temp: Path) -> dict[str, list[str]]:
    enum_binary = compile_variant(temp, "enum-sanitizer", ["-fsanitize=enum", "-fno-sanitize-recover=enum"])
    shift_binary = compile_variant(temp, "shift-sanitizer", ["-fsanitize=shift", "-fno-sanitize-recover=shift"])
    valid_enum = run(enum_binary, "enum_read", "60")
    require(valid_enum.returncode == 0, f"valid enum read failed: {valid_enum.stderr}")
    valid_shift = run(shift_binary, "shift", "60")
    require(valid_shift.returncode == 0, f"valid boundary shift failed: {valid_shift.stderr}")
    empty = run(shift_binary, "empty_helper")
    require(empty.returncode == 0 and "mask=0" in empty.stdout, "empty binding negative control drift")
    enum_cases = ["61", "62", "63", "64", "65", "127", "255"]
    enum_evidence: list[str] = []
    for raw in enum_cases:
        result = run(enum_binary, "decoded_enum_read", raw)
        combined = result.stdout + result.stderr
        if int(raw) <= 63:
            require(result.returncode == 0 and not combined,
                    f"unexpected enum-read sanitizer result for decoded raw {raw}: {combined}")
            enum_evidence.append(f"{raw}: no diagnostic; ABI range control")
        else:
            require(result.returncode != 0 and "not a valid value" in combined,
                    f"enum-read sanitizer did not isolate decoded raw {raw}: {combined}")
            enum_evidence.append(f"{raw}: invalid Button enum read diagnosed")
    caller_values: list[str] = []
    for raw in (61, 62, 63, 64):
        expected_mask = str(1 << (raw - 1))
        direct = run(shift_binary, "shift", str(raw))
        require(direct.returncode == 0 and f"mask={expected_mask}" in direct.stdout,
                f"in-range shift for invalid enum {raw} drift: {direct.stdout}{direct.stderr}")
        for name in ("mode_activation", "backend_activation", "custom_modifier", "custom_combo"):
            reached = run(shift_binary, "caller", name, str(raw))
            expected_output = "backend_id=1" if name == "backend_activation" else f"mask={expected_mask}"
            require(reached.returncode == 0 and expected_output in reached.stdout,
                    f"invalid enum caller {name}/{raw} drift: {reached.stdout}{reached.stderr}")
        caller_values.append(f"{raw}: helper shift in range; mask={expected_mask}; 4 callers reached")
    shift_cases = ["0", "65", "255"]
    shift_evidence: list[str] = []
    for raw in shift_cases:
        result = run(shift_binary, "shift", raw)
        combined = result.stdout + result.stderr
        require(result.returncode != 0 and ("shift" in combined.lower() or "negative" in combined.lower()),
                f"shift sanitizer did not isolate raw {raw}: {combined}")
        shift_evidence.append(f"{raw}: invalid shift diagnosed")
    callers: dict[str, list[str]] = {}
    for name in ("mode_activation", "backend_activation", "custom_modifier", "custom_combo"):
        reached = run(shift_binary, "caller", name, "1")
        expected_output = "backend_id=1" if name == "backend_activation" else "mask="
        require(reached.returncode == 0 and f"caller={name}" in reached.stdout and expected_output in reached.stdout,
                f"source-supported valid caller control failed: {name}: {reached.stderr}")
        bad = run(shift_binary, "caller", name, "0")
        combined = bad.stdout + bad.stderr
        require(bad.returncode != 0 and ("shift" in combined.lower() or "negative" in combined.lower()),
                f"isolated shift did not reach caller: {name}: {combined}")
        callers[name] = ["valid BTN_LF1 completed", "zero value reached invalid shift"]
    negative = run(shift_binary, "shift", "-1")
    negative_text = negative.stdout + negative.stderr
    require(negative.returncode != 0 and ("shift" in negative_text.lower() or "negative" in negative_text.lower()),
            f"negative Button injection did not isolate shift failure: {negative_text}")
    shift_evidence.append("-1: invalid shift diagnosed after Button narrowing")
    return {"enum_read": enum_evidence, "helper_shift": shift_evidence,
            "in_range_invalid_enum_shifts": caller_values,
            "production_callers": [f"{name}: {rows[1]}" for name, rows in callers.items()]}


def validate_fixture(value: dict[str, object]) -> None:
    require(value["schema_name"] == "glyph_gp_config012_button_mask_characterization", "fixture schema identity")
    require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-012", "fixture version")
    require(value["authorized_source_snapshot"] == "1b0364ce16b1c20fcea6dfef3ed12130c5c27093",
            "authorized source snapshot drift")
    require(value["observed_configurator_base"] == "6b6424dc9f915530b4a3386cd3864671a236d4e6",
            "implementation source baseline drift")
    require(value["nanopb_commit"] == UPSTREAM_NANOPB_COMMIT, "Nanopb source identity drift")
    require(value["proto_selector"] == PROTO_SELECTOR, "selected proto identity drift")
    require(value["modifiers_count_limit"] == 10, "GP-CONFIG-014 isolation boundary drift")
    require(value["source_supported_enum_values"] == list(range(61)), "source enum value matrix drift")
    require(value["injected_enum_values"] == [61, 62, 63, 64, 65, 127, 255, 256, 300, -1],
            "injected enum matrix drift")



def verify_frozen_fixture() -> None:
    """Retain every historical observation, including fields not used below."""
    historical = subprocess.check_output([
        "git", "show",
        "3dac79dac4eefcf832510817e8cb5ecd6a27f219:" + FIXTURE.relative_to(ROOT).as_posix(),
    ], cwd=ROOT)
    require(FIXTURE.is_file() and not FIXTURE.is_symlink() and
            FIXTURE.read_bytes() == historical, "frozen historical fixture changed")

def main() -> int:
    try:
        verify_frozen_fixture()
        value = json.loads(regular(ROOT, FIXTURE.relative_to(ROOT).as_posix()).read_text(encoding="utf-8"),
                           object_pairs_hook=pairs)
        validate_fixture(value)
        validate_identity_adversarial_controls()
        validate_provenance(value)
        fragments, fragment_hashes = validate_source(value)
        require(value["production_fragment_sha256"] == fragment_hashes, "production function correspondence drift")
        harness = regular(ROOT, HARNESS.relative_to(ROOT).as_posix())
        require(sha256(harness) == value["harness_sha256"], "host harness drift")
        with tempfile.TemporaryDirectory(prefix="glyph-gp-config012-") as temp_name:
            temp = Path(temp_name)
            (temp / "production_fragments.inc").write_text(fragments, encoding="utf-8")
            binary = compile_variant(temp, "decode-host", [])
            output, records = validate_decoder(binary)
            sanitizer_results = validate_sanitizers(temp)
        expected = value["decoder_observations"]
        require({name: records[name] for name in expected} == expected, "recorded decoder observations drift")
        require(value["sanitizer_observations"] == sanitizer_results, "sanitizer observations drift")
        print(output, end="")
        print("sanitizer enum-read and shift cases: PASS; caller reachability: 4/4")
        print("glyph_gp_config012_button_mask_characterization: PASS; exact 0.4.9.2 closure; H1 host only")
        print("historical_observations=FROZEN; current_source=authenticated; hardware_acceptance=NOT_CLAIMED")
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_gp_config012_button_mask_characterization: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
