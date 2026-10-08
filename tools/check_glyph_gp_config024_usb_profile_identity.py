#!/usr/bin/env python3
"""Exact C024 selector-identity host proof; no build or hardware claim."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "b404453ef22cc994eec54338b8a23c3ba61df808"
PLANNER = "fbf2d1c99569ddee3e5432501ddc868bbdee4990"
PRODUCTION = "HAL/pico/src/display/DefaultConfigMenu.cpp"
INPUT_MODE = "src/core/InputMode.cpp"
MODE_SETUP = "src/core/mode_selection.cpp"
FIXTURE = "docs/calibration/fixtures/gp_config_024_usb_profile_identity_repair.json"
REPORT = "docs/calibration/gp_config_024_usb_profile_identity_repair.md"
HOST = "tools/fixtures/gp_config024_usb_profile_identity"
ALLOWED = {
    PRODUCTION,
    "tools/check_glyph_gp_config024_usb_profile_identity.py",
    f"{HOST}/main.cpp",
    f"{HOST}/include/host_stubs.hpp",
    REPORT,
    FIXTURE,
    "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
    "docs/runtime_config/fixtures/glyph_checker_census.json",
    "docs/runtime_config/fixtures/runtime_config_validation_health.json",
    "docs/runtime_config/runtime_config_validation_health.md",
}


class ProofError(AssertionError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ProofError(message)


def git(*args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if result.returncode:
        raise ProofError(result.stderr.decode(errors="replace"))
    return result.stdout.decode() if text else result.stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def method_body(source: str, marker: str) -> str:
    start = source.find(marker)
    require(start >= 0, "SetUsbBackend production method is missing")
    opening = source.find("{", start)
    require(opening >= 0, "SetUsbBackend body is missing")
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ProofError("SetUsbBackend body is unterminated")


def candidate_inventory(value: dict) -> None:
    head = str(git("rev-parse", "HEAD")).strip()
    parents = str(git("rev-list", "--parents", "-n", "1", head)).split()
    require(parents == [head, BASE], "C024 candidate must be a direct child of the exact fresh B")
    changed = set(filter(None, str(git("diff", "--no-renames", "--name-only", "-z", BASE, head)).split("\0")))
    require(changed == ALLOWED, "C024 candidate path inventory differs from the exact ten-path envelope")
    tree = str(git("ls-tree", "-rz", "--full-tree", head))
    entries = {}
    for record in tree.split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode, kind, oid = metadata.split()
        if path in ALLOWED:
            entries[path] = (mode, kind, oid)
    require(set(entries) == ALLOWED, "C024 candidate tree omits an authorized path")
    require(all(entries[p][0:2] == ("100644", "blob") for p in ALLOWED), "C024 candidate contains a non-regular or executable path")
    require(not str(git("status", "--porcelain", "--untracked-files=all")).strip(), "C024 candidate checkout must be clean")
    for row in value["base_source_inventory"]:
        record = str(git("ls-tree", "-z", BASE, "--", row["path"]))
        require(record.startswith(f'{row["mode"]} blob {row["blob"]}\t{row["path"]}\0'), "fresh B source inventory changed: " + row["path"])
        require(digest(git("show", f'{BASE}:{row["path"]}', text=False)) == row["sha256"], "fresh B source bytes changed: " + row["path"])
    require(len(value["base_source_inventory"]) == 19, "C024 must bind the complete adopted 19-row source annex")
    packet = str(git("show", f'{PLANNER}:docs/planning/portfolio_20261005_0028.md'))
    original_rows = {}
    for line in packet.splitlines():
        match = re.match(r"\| `([^`]+)` \| `([0-9a-f]{40})` \| `([0-9a-f]{64})` \|", line)
        if match:
            original_rows[match.group(1)] = (match.group(2), match.group(3))
    require(set(original_rows) == {row["path"] for row in value["packet_source_inventory"]},
            "immutable packet source annex inventory changed")
    for row in value["packet_source_inventory"]:
        require(original_rows[row["path"]] == (row["blob"], row["sha256"]),
                "immutable packet annex row changed: " + row["path"])
    fresh = {row["path"]: row for row in value["base_source_inventory"]}
    changed = [path for path, (_, sha) in original_rows.items() if fresh[path]["sha256"] != sha]
    declared = {row["path"] for row in value["authorized_predecessor_deltas"]}
    require(set(changed) == declared, "fresh B has an undeclared predecessor source delta")
    for row in value["authorized_predecessor_deltas"]:
        require(fresh[row["path"]]["sha256"] == row["fresh_B_sha256"],
                "accepted predecessor source pin changed: " + row["path"])
        for revision in row["accepted_predecessor_commits"]:
            require(str(git("merge-base", "--is-ancestor", revision, BASE, text=True)) == "",
                    "accepted predecessor is not an ancestor of fresh B: " + revision)
            commit_path_delta = set(filter(None, str(git("diff", "--name-only", revision + "^1", revision, "--")).splitlines()))
            require(row["path"] in commit_path_delta,
                    "named predecessor did not change the claimed source path: " + revision)
    for row in value["candidate_file_hashes"]:
        require(row["path"] in ALLOWED and digest((ROOT / row["path"]).read_bytes()) == row["sha256"],
                "candidate proof/report/metadata byte substitution: " + row["path"])


def compile_and_run(mode: str) -> str:
    input_mode_source = Path(ROOT / INPUT_MODE).read_text()
    setup_source = Path(ROOT / MODE_SETUP).read_text()
    selector_source = Path(ROOT / PRODUCTION).read_text()
    methods = [
        method_body(input_mode_source, "GameModeConfig *InputMode::GetConfig()"),
        method_body(input_mode_source, "void InputMode::SetConfig(GameModeConfig &config)"),
        method_body(setup_source, "void set_mode(CommunicationBackend *backend, ControllerMode *mode)"),
        method_body(setup_source, "void set_mode(CommunicationBackend *backend, KeyboardMode *mode)"),
        method_body(setup_source, "void set_mode(CommunicationBackend *backend, GameModeConfig &mode_config, Config &config)"),
        method_body(selector_source, "void DefaultConfigMenu::SetUsbBackend("),
    ]
    with tempfile.TemporaryDirectory(prefix="glyph-c024-selector-") as folder:
        temp = Path(folder)
        (temp / "production_methods.inc").write_text("\n\n".join(methods) + "\n")
        executable = temp / "c024-host"
        flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer"]
        if mode == "short-enum":
            flags.extend(["-fshort-enums", "-DEXPECT_SHORT_ENUM"])
        command = ["c++", "-std=gnu++20", *flags,
                   "-I" + str(ROOT / f"{HOST}/include"),
                   "-I" + str(temp), str(ROOT / f"{HOST}/main.cpp"), "-o", str(executable)]
        built = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        require(built.returncode == 0, f"{mode} host compile failed:\n{built.stdout}{built.stderr}")
        result = subprocess.run([str(executable)], cwd=ROOT, capture_output=True, text=True, timeout=20)
        require(result.returncode == 0, f"{mode} host proof failed:\n{result.stdout}{result.stderr}")
        require(not result.stderr, f"{mode} sanitizer emitted diagnostics:\n{result.stderr}")
        return result.stdout.strip()


def main() -> int:
    try:
        value = json.loads((ROOT / FIXTURE).read_text())
        require(value["schema_name"] == "glyph_gp_config024_usb_profile_identity_repair"
                and value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-024", "fixture identity mismatch")
        candidate_inventory(value)
        messages = [compile_and_run(mode) for mode in ("default-enum", "short-enum")]
        require(messages[0] == messages[1], "host enum-mode outputs differ")
        require(messages[0] == value["expected_host_output"], "host output differs from the frozen fixture")
        print(messages[0])
        print("C024 exact candidate source correspondence, ten-path inventory, verified enum widths in both host modes and ASan/UBSan: PASS")
        print("firmware build and hardware acceptance: NOT_CLAIMED")
        return 0
    except (OSError, subprocess.SubprocessError, ProofError, KeyError, TypeError, ValueError) as error:
        print("gp_config024_usb_profile_identity: FAIL: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
