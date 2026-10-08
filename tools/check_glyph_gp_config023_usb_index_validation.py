#!/usr/bin/env python3
"""Bounded GP-CONFIG-023 USB-index production host proof."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "docs/runtime_config/fixtures/gp_config023_usb_index_validation.json"
REPORT = "docs/runtime_config/gp_config023_usb_index_validation.md"
HOST = "tools/fixtures/gp_config023_usb_host/usb_index_harness.cpp"
STUBS = "tools/fixtures/gp_config023_usb_host/host_stubs.hpp"
DECODER = "tools/fixtures/gp_config012_button_host"
BASE = "b224227a76cb8edb73e5f4b2ad5de874d1e61ad1"
SOURCE_SHA256 = {
    "HAL/pico/src/comms/backend_init.cpp": "913d6c3e96ecb6670097d4faebbdbbd34c706e4bfab4f76a5b3b8f692d7f6b2c",
    "config/glyph/common/src/config.cpp": "af19d625ac562e7404293ddb181870c2279393c7c7fb4710530572900aed44ae",
    "include/core/config_validation.hpp": "a45124019b1e24ee6b44a09b0c5d88e121113e1eb9e8ff1b7f6f8fb90ce4d0d4",
    "src/core/config_validation.cpp": "5e3a262be086a981de9832117398be690be52fd1cfc881f88473f9638d32cf8b",
    "include/core/config_usb_default_validation.hpp": "d08a1a7489933bf64480c94334accfa714644a21874bf5f1e9660cd66c52cf11",
    "src/core/config_usb_default_validation.cpp": "bf617caab589c1a286a6856f0199d2726cf80c4810337e77c90d4981bef5edeb",
    "include/core/config_button_validation.hpp": "176cec58249c48e51d418af0af9f64b4d6b8942d4c53c6a8b6f519dcc9c3193f",
    "src/core/config_button_validation.cpp": "4025f581961e63a8ef6a290b41786b59291bada5e77ab665dbe448ed27418d2d",
    "config/glyph/common/src/glyph_config_validation.cpp": "344e607e46a668d83e8cf706afd31fd7854c76e2523997c721a43d25d899337e",
    "HAL/pico/src/comms/ConfiguratorBackend.cpp": "e3fd8f93300ef66a79f8877e6ed72628d95831f32f95c46c3f8c011a8bd1c121",
    "HAL/pico/src/core/Persistence.cpp": "07589fff75f0663465bfa6b8bf5d268591934c785cc18956d06d209ddf40f23f",
    "tools/fixtures/gp_config012_button_host/generated/config.pb.h": "bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323",
}
HOST_SHA256 = {
    HOST: "971b40091ec507d3b2e7347d8c78ce5b6acb5cf05fcbe32ec444cb6244a1bd04",
    STUBS: "b813240ea035d3bfb124535f110f7dd6d65e92981977e9f9018c4729b01a4732",
}
FRAGMENT_SHA256 = {
    "initialize_backends": "cb5eca0652f2555a6ace87037fe1ce66aed3c2a13801aa7723c22e8b4c7837d9",
    "selectors": "0ac13fa680676c0ab32692eb4152e61b9e634e837a17937cf7e114cff15a484a",
}


class ProofError(AssertionError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ProofError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, timeout=30)
    require(result.returncode == 0, "Git read failed: " + result.stderr.decode(errors="replace"))
    return result.stdout


def regular(path: str) -> Path:
    file = ROOT / path
    for parent in (file, *file.parents):
        if parent == ROOT:
            break
        require(not parent.is_symlink(), "symlink input: " + path)
    require(file.is_file() and stat.S_ISREG(file.stat().st_mode), "missing/nonregular input: " + path)
    require(stat.S_IMODE(file.stat().st_mode) == 0o644, "fixture input mode is not 100644: " + path)
    return file


def load_fixture() -> dict:
    value = json.loads(regular(FIXTURE).read_text(), object_pairs_hook=_unique)
    require(value["schema_name"] == "glyph_gp_config023_usb_index_validation" and
            value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-023",
            "fixture identity")
    require(value["candidate_base"] == BASE, "candidate base changed")
    require(value["pinned_inputs"] == {
        "gp_config013_base": "7a2dba85332c90fa2bcc6c06e1205c4745facb92",
        "gp_config021_base": "c6887115f2e44f0803eb0956ebb574633cec53be",
        "gp_config022_base": "14400b3ff75b5d017a9e7cf8e6d8be785c342187",
        "gp_config022_accepted_transition": "ec95a1437c428cefd86c2fc8c6220c50319522b9",
    }, "pinned C013/021/022 input identities changed")
    for sha in value["pinned_inputs"].values():
        require(git("cat-file", "-t", sha).decode().strip() == "commit", "pinned input commit unavailable")
    for path, expected in SOURCE_SHA256.items():
        raw = regular(path).read_bytes()
        require(digest(raw) == expected, "production/decoder source hash mismatch: " + path)
    for path, expected in HOST_SHA256.items():
        require(digest(regular(path).read_bytes()) == expected, "host fixture hash mismatch: " + path)
    require(value["production_sources"] == [{"path": p, "sha256": h} for p, h in sorted(SOURCE_SHA256.items())],
            "production input inventory changed")
    require(value["host_sources"] == [{"path": p, "sha256": h} for p, h in sorted(HOST_SHA256.items())],
            "host input inventory changed")
    report = regular(REPORT).read_text()
    for token in ("GP-CONFIG-023", "4,096", "NOT_CLAIMED", "NOT_TESTED", "UNPROVEN", "host-only"):
        require(token in report, "report nonclaim/coverage token missing: " + token)
    return value


def _unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def fragment(source: str, start: str, end: str) -> str:
    text = regular(source).read_text()
    require(text.count(start) == 1, "missing/duplicate production body start: " + start)
    begin = text.index(start)
    finish = text.find(end, begin + len(start))
    require(finish >= 0, "production body end missing: " + end)
    return text[begin:finish].rstrip() + "\n"


def production_fragments() -> dict[str, str]:
    source = "HAL/pico/src/comms/backend_init.cpp"
    return {
        "initialize_backends": fragment(source, "size_t initialize_backends(", "void init_primary_backend("),
        "selectors": fragment(source, "backend_config_selector_t get_backend_config_default = [](", "// clang-format on"),
    }


def function_body(source: str, start: str, end: str) -> str:
    text = regular(source).read_text()
    require(text.count(start) == 1, "missing/duplicate source-bound consumer: " + start)
    begin = text.index(start)
    finish = text.find(end, begin + len(start))
    require(finish >= 0, "consumer boundary missing: " + end)
    return text[begin:finish]


def check_consumers() -> None:
    setconfig = function_body("HAL/pico/src/comms/ConfiguratorBackend.cpp",
        "bool ConfiguratorBackend::HandleSetConfig()", "bool ConfiguratorBackend::HandleUnknownCommand(")
    require(setconfig.index("pb_decode(&istream, Config_fields, &candidate)") <
            setconfig.index("persistence.ValidateConfig(candidate, validation_error)") <
            setconfig.index("persistence.SaveConfig(candidate)") < setconfig.index("_config = candidate;"),
            "SetConfig must decode, use the shared validator, save, then publish")
    require(setconfig.count("_config = candidate;") == 1, "SetConfig publication count")

    persistence = regular("HAL/pico/src/core/Persistence.cpp").read_text()
    validate = function_body("HAL/pico/src/core/Persistence.cpp",
        "bool Persistence::ValidateConfig(", "bool Persistence::SaveConfig(")
    load = function_body("HAL/pico/src/core/Persistence.cpp",
        "Persistence::LoadResult Persistence::LoadConfigChecked(", "bool Persistence::CheckSavedConfig()")
    require("return _validator(config, error);" in validate, "Persistence must call its installed semantic validator")
    require(load.index("pb_decode(&istream, Config_fields, &candidate)") <
            load.index("ValidateConfig(candidate, error)") < load.index("config = candidate;"),
            "LoadConfigChecked must validate before publishing the candidate")
    require("SaveConfig(" not in load, "rejected stored config must not be saved")

    glyph_validator = function_body("config/glyph/common/src/glyph_config_validation.cpp",
        "bool validate_glyph_config(", "\n}")
    require("validate_config_semantics(config, error)" in glyph_validator,
            "Glyph validator must preserve shared semantic validation")

    setup = function_body("config/glyph/common/src/config.cpp", "void setup()", "void loop()")
    require(setup.index("persistence.SetValidator(validate_glyph_config)") <
            setup.index("persistence.ValidateConfig(config, validation_error)") <
            setup.index("persistence.LoadConfigChecked(config)") < setup.index("initialize_backends("),
            "Glyph defaults/stored load must use the shared validator before backend initialization")
    require(setup.index("initialize_backends(") < setup.index("if (!is_valid_usb_default_index(config))") <
            setup.index("refuse_boot(BootOutcome::StartupConfigRejected") <
            setup.index("setup_mode_activation_bindings(") < setup.index("if(backend_count == 0)"),
            "invalid startup selection must refuse before mode bindings and zero-backend fallback")
    require("SaveConfig(" not in setup, "startup refusal path must not save Config")

    refusal = function_body("config/glyph/common/src/config.cpp", "void refuse_boot(", "}  // namespace")
    require("watchdog_hw->scratch[0] = 0;" in refusal and "watchdog_hw->scratch[1] = 0;" in refusal and
            refusal.index("draw_recovery_page(outcome)") < refusal.index("publish_boot_state(outcome, display_ready)"),
            "startup refusal must clear watchdog selection and publish recovery state")

    setup1 = function_body("config/glyph/common/src/config.cpp", "void setup1()", "void dummyloop()")
    require(setup1.index("while (snapshot.outcome == BootOutcome::Pending)") <
            setup1.index("if (refused(snapshot.outcome))") < setup1.index("static RgbBrightnessMenu"),
            "secondary core must gate normal menu setup after startup refusal")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=45)
    require(result.returncode == 0, "host command failed: " + " ".join(command) + "\n" + result.stdout + result.stderr)
    return result


def compile_and_run(temp: Path, fragments: dict[str, str], short_enum: bool) -> str:
    for name, body in fragments.items():
        (temp / ("production_" + ("backend_init" if name == "initialize_backends" else "backend_selectors") + ".inc")).write_text(body)
    includes = ["-I" + str(ROOT / "tools/fixtures/gp_config023_usb_host"),
                "-I" + str(ROOT / "include"),
                "-I" + str(ROOT / DECODER / "generated"),
                "-I" + str(ROOT / DECODER / "nanopb"), "-I" + str(temp)]
    flags = ["-O0", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer"]
    if short_enum:
        flags.append("-fshort-enums")
    sources = ["src/core/config_usb_default_validation.cpp", "src/core/config_button_validation.cpp",
               "src/core/config_validation.cpp", HOST]
    objects = []
    for index, source in enumerate(sources):
        obj = temp / f"{index}.o"
        run(["c++", "-std=gnu++20", *flags, *includes, "-c", str(ROOT / source), "-o", str(obj)])
        objects.append(str(obj))
    binary = temp / ("usb-index-short-enum" if short_enum else "usb-index-default-enum")
    run(["c++", *flags, *objects, "-o", str(binary)])
    result = run([str(binary)])
    require(not result.stderr, "unexpected sanitizer stderr")
    return result.stdout


def main() -> int:
    try:
        value = load_fixture()
        check_consumers()
        parts = production_fragments()
        for name, body in parts.items():
            require(digest(body.encode()) == FRAGMENT_SHA256[name], "production fragment changed: " + name)
        head = git("rev-parse", "HEAD").decode().strip()
        require(head == value["candidate_base"] or
                git("show", "-s", "--format=%P", head).decode().strip() == value["candidate_base"],
                "checker must run on the exact B023 base or its direct candidate child")
        require(git("branch", "--show-current").decode().strip() == "codex/gp-config-023-release-safety",
                "candidate branch changed")
        parent = git("show", "-s", "--format=%P", head).decode().strip()
        if head == BASE:
            require(parent == "9644ae6648558326b8157b5368faa9e6086aa034", "B023 ancestry changed")
        else:
            require(parent == BASE, "C023 must be a direct child of B023")
            require(git("show", "-s", "--format=%P", parent).decode().strip() ==
                    "9644ae6648558326b8157b5368faa9e6086aa034", "B023 ancestry changed")
        with tempfile.TemporaryDirectory(prefix="glyph-config023-usb-index-") as folder:
            outputs = []
            for short_enum in (False, True):
                outputs.append(compile_and_run(Path(folder), parts, short_enum))
        require(outputs[0] == outputs[1], "ABI observations differ")
        lines = outputs[0].splitlines()
        require(len(lines) == 8 and lines[-1] == "gp_config023_usb_index_validation: PASS (host-only; no hardware claim)",
                "unexpected bounded proof output:\n" + outputs[0])
        require(lines[0].startswith("index_matrix counts=0..15 indices=0..255 cases=4096 accepted=120 actual_extent=15"),
                "index/count matrix result")
        print(outputs[0], end="")
        print("ABIs=default,short-enum ASan_UBSan=PASS exact_production_fragments=2 hardware=NOT_CLAIMED")
        return 0
    except (OSError, subprocess.SubprocessError, ProofError, KeyError, TypeError, ValueError) as error:
        print("gp_config023_usb_index_validation: FAIL: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
