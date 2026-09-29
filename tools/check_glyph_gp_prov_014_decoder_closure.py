#!/usr/bin/env python3
"""Check one recorded GP-PROV-014 decoder closure without resolving packages.

The default check validates the immutable observation and tracked repository
inputs. ``--resolved-root`` additionally checks actual isolated resolution
bytes and regenerates the Nanopb C/header pair using an explicit interpreter.
Neither mode claims that a moving dependency selector will resolve the same
package in a later build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REPORT = Path("docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json")
PINNED_REPORT_SHA256 = "a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f"
SNAPSHOT_SHA = "739c9c58acfde78de1639cd18be5a7c60fa06f1a"
NANOPB_COMMIT = "160d4f09e5fabb2b66aa2dea32d4f38ace2c4b3f"
PROTO_COMMIT = "db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8"
OTHER_PROTO_COMMIT = "5b2bb5d2c2a212647d5aaef7d5dc794be5197ecb"
PROTO_SHA256 = "2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b"
OPTIONS_SHA256 = "6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805"
HEADER_SHA256 = "bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323"
NANOPB_PACKAGE_SHA256 = "01f2027fcd3c19b304581c0bba7a9f0096a16842874e6686a38d168a69d952fe"
NANOPB_LICENSE_SHA256 = "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"
GENERATOR_SHA256 = "67d3c5e6de1e5dbd9f45bb4e5b7055d888d1afd6d6e1690791ab8607b6c6b738"
SELECTORS = {
    "platformio.ini": (("nanopb/Nanopb@^0.4.8", "https://github.com/JonnyHaystack/HayBox-proto#5b2bb5d"),
                       "99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9"),
    "config/glyph/env.ini": (("https://github.com/GregTurbo/HayBox-proto#db4e2f6",),
                             "c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf"),
}
GENERATION_PROTO_DECLARATION = "+<.pio/libdeps/${PIOENV}/HayBox-proto/config.proto>"
TRACKED = {
    "tools/fixtures/custom_modifier_cache_host/schema/config.proto": PROTO_SHA256,
    "tools/fixtures/custom_modifier_cache_host/schema/config.options": OPTIONS_SHA256,
    "tools/fixtures/mode_selection_host/generated/config.pb.h": HEADER_SHA256,
    "tools/fixtures/mode_selection_host/generated/nanopb.library.json": NANOPB_PACKAGE_SHA256,
    "tools/fixtures/mode_selection_host/generated/LICENSE.nanopb.txt": NANOPB_LICENSE_SHA256,
}
REQUIRED_ROLES = (
    "nanopb_package", "nanopb_generator", "nanopb_pb_h", "nanopb_pb_decode_c",
    "nanopb_platformio_generator", "nanopb_generator_proto_init", "nanopb_generator_utils",
    "nanopb_generator_nanopb_pb2", "nanopb_generator_nanopb_proto", "nanopb_protoc",
    "nanopb_pb_decode_h", "nanopb_pb_common_c", "nanopb_pb_common_h",
    "proto_package", "config_proto", "config_options", "other_proto_package",
    "other_config_proto", "other_config_options", "generated_c", "generated_h",
)
GENERATED_ROLES = ("generated_c", "generated_h")
INCLUDE_SOURCES = (
    "nanopb_pb_decode_c", "nanopb_pb_decode_h", "nanopb_pb_common_c",
    "nanopb_pb_common_h", "generated_c", "generated_h",
)
LOCAL_HEADERS = {
    "pb.h", "pb_decode.h", "pb_common.h", "config.pb.h",
}
EXPECTED_BUILD_COMMAND = [
    "{python}", "{generator}", "--output-dir", "{build_output_dir}",
    "--error-on-unmatched", "--proto-path", "{proto_dir}", "config.proto",
]
EXPECTED_REGENERATION_COMMAND = [
    "{python}", "-B", "{generator}", "--output-dir", "{output_dir}",
    "--error-on-unmatched", "--proto-path", "{proto_dir}", "config.proto",
]
ALTERNATE_FILES = [
    {"role": "pb_decode_c", "path": "nanopb-0.4.9.1/pb_decode.c",
     "sha256": "6c2fc2f357bffdb774c1d329b533e981498d58405c0b1ef066f5a87fd46b5a17", "bytes": 53847},
    {"role": "pb_decode_h", "path": "nanopb-0.4.9.1/pb_decode.h",
     "sha256": "1747746e5961de5789bcf0795588da0790cd18b2e4e706ad9c7099a0fa1cc83f", "bytes": 7870},
    {"role": "regenerated_config_c", "path": "regenerated/config.pb.c",
     "sha256": "99a682d90b04e77f3e0c52620d5f3403a7ee5e3014711c4c2883f1a14f592ea2", "bytes": 1076},
    {"role": "regenerated_config_h", "path": "regenerated/config.pb.h",
     "sha256": "532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3", "bytes": 73915},
]


class ClosureError(AssertionError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ClosureError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def regular(root: Path, relative: str) -> Path:
    path = Path(relative)
    require(not path.is_absolute() and path.as_posix() == relative and ".." not in path.parts,
            f"unsafe relative path: {relative}")
    current = root
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), f"symlink in closure: {relative}")
    require(current.is_file(), f"missing regular closure file: {relative}")
    return current


def check_hash(root: Path, relative: str, expected: str) -> bytes:
    data = regular(root, relative).read_bytes()
    require(digest(data) == expected, f"byte digest mismatch: {relative}")
    return data


def load_report(root: Path = ROOT) -> dict:
    require(re.fullmatch(r"[0-9a-f]{64}", PINNED_REPORT_SHA256) is not None,
            "reviewed report digest has not been pinned")
    raw = regular(root, REPORT.as_posix()).read_bytes()
    require(digest(raw) == PINNED_REPORT_SHA256, "report digest drift")
    return json.loads(raw)


def validate_record(record: dict, *, snapshot_sha: str = SNAPSHOT_SHA) -> dict[str, dict]:
    require(set(record) == {"schema_name", "schema_version", "work_order", "configurator_sha",
                           "resolution", "generation", "files", "include_edges",
                           "full_package_selection", "alternate_observation", "non_claims"},
            "report top-level shape")
    require(record["schema_name"] == "glyph_gp_prov_014_decoder_closure"
            and record["schema_version"] == 1 and record["work_order"] == "GP-PROV-014", "report identity")
    require(re.fullmatch(r"[0-9a-f]{40}", snapshot_sha) is not None
            and record["configurator_sha"] == snapshot_sha, "observed configurator snapshot drift")
    resolution = record["resolution"]
    require(set(resolution) == {"nanopb_selector", "nanopb_version", "nanopb_tag", "nanopb_commit",
                                "nanopb_piopm_sha256",
                                "nanopb_license_package_present", "nanopb_license_sha256",
                                "generation_input_declaration", "proto_instances"},
            "resolution shape")
    require(resolution["nanopb_selector"] == SELECTORS["platformio.ini"][0][0]
            and resolution["nanopb_version"] == "0.4.92"
            and resolution["nanopb_tag"] == "0.4.9.2"
            and resolution["nanopb_commit"] == NANOPB_COMMIT
            and resolution["nanopb_license_package_present"] is False
            and resolution["nanopb_license_sha256"] == NANOPB_LICENSE_SHA256
            and isinstance(resolution["nanopb_piopm_sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", resolution["nanopb_piopm_sha256"]) is not None
            and resolution["generation_input_declaration"] == GENERATION_PROTO_DECLARATION,
            "resolution identity")
    instances = resolution["proto_instances"]
    require(isinstance(instances, list) and len(instances) == 2, "two resolved proto instances required")
    expected_instances = (
        ("generation_input", SELECTORS["config/glyph/env.ini"][0][0], "config/glyph/env.ini",
         ".pio/libdeps/glyph_mk6/HayBox-proto", PROTO_COMMIT),
        ("other_resolved", SELECTORS["platformio.ini"][0][1], "platformio.ini",
         ".pio/libdeps/glyph_mk6/HayBox-proto@src-777dd83f5e06d71aba0103adf11d16aa", OTHER_PROTO_COMMIT),
    )
    for instance, (role, selector, selector_path, package_path, commit_prefix) in zip(instances, expected_instances):
        require(isinstance(instance, dict) and set(instance) == {"role", "selector", "selector_path",
                                                             "package_path", "source_commit",
                                                             "piopm_sha256", "license_file_present",
                                                             "license_declared"},
                "proto instance shape")
        require(instance["role"] == role and instance["selector"] == selector
                and instance["selector_path"] == selector_path
                and instance["package_path"] == package_path
                and isinstance(instance["source_commit"], str)
                and re.fullmatch(r"[0-9a-f]{40}", instance["source_commit"]) is not None
                and instance["source_commit"] == commit_prefix
                and isinstance(instance["piopm_sha256"], str)
                and re.fullmatch(r"[0-9a-f]{64}", instance["piopm_sha256"]) is not None
                and instance["license_file_present"] is False
                and instance["license_declared"] == "GPL-3.0-only",
                f"proto instance identity: {role}")
    generation = record["generation"]
    require(set(generation) == {"build_command", "build_cwd", "regeneration_command",
                                "regeneration_cwd", "generator_version", "protobuf_version", "grpcio_tools_version",
                                "generator_sha256", "options"}, "generation shape")
    require(generation["build_command"] == EXPECTED_BUILD_COMMAND
            and generation["build_cwd"] == "{checkout}"
            and generation["regeneration_command"] == EXPECTED_REGENERATION_COMMAND
            and generation["regeneration_cwd"] == "{proto_dir}"
            and generation["generator_version"] == "nanopb-0.4.9.2"
            and generation["protobuf_version"] == "6.33.6"
            and generation["grpcio_tools_version"] == "1.80.0"
            and generation["generator_sha256"] == GENERATOR_SHA256
            and generation["options"] == ["--error-on-unmatched"], "generation identity")
    require(record["non_claims"] == [
        "future compatible-range resolution", "historical tested-artifact package identity",
        "transitive reproducible build", "decoder behavior acceptance", "firmware behavior",
        "physical controller behavior", "GP-CONFIG-012/013 authorization",
    ], "snapshot scope/non-claims")
    files = record["files"]
    require(isinstance(files, list) and [item.get("role") for item in files] == list(REQUIRED_ROLES),
            "ordered source closure")
    by_role = {}
    for item in files:
        require(set(item) == {"role", "path", "sha256", "bytes"}, "source file record shape")
        require(isinstance(item["path"], str) and isinstance(item["bytes"], int)
                and item["bytes"] > 0 and isinstance(item["sha256"], str)
                and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
                f"invalid source file identity: {item['role']}")
        path = item["path"]
        role = item["role"]
        if role in GENERATED_ROLES:
            expected_path = f".pio/build/glyph_mk6/nanopb/generated-src/config.pb.{'c' if role == 'generated_c' else 'h'}"
        elif role.startswith("nanopb_"):
            expected_path = ".pio/libdeps/glyph_mk6/Nanopb/" + {
                "nanopb_package": "library.json", "nanopb_generator": "generator/nanopb_generator.py",
                "nanopb_platformio_generator": "generator/platformio_generator.py",
                "nanopb_generator_proto_init": "generator/proto/__init__.py",
                "nanopb_generator_utils": "generator/proto/_utils.py",
                "nanopb_generator_nanopb_pb2": "generator/proto/nanopb_pb2.py",
                "nanopb_generator_nanopb_proto": "generator/proto/nanopb.proto",
                "nanopb_protoc": "generator/protoc",
                "nanopb_pb_h": "pb.h", "nanopb_pb_decode_c": "pb_decode.c",
                "nanopb_pb_decode_h": "pb_decode.h", "nanopb_pb_common_c": "pb_common.c",
                "nanopb_pb_common_h": "pb_common.h",
            }[role]
        else:
            package = instances[1]["package_path"] if role.startswith("other_") else instances[0]["package_path"]
            name = {
                "proto_package": "library.json", "config_proto": "config.proto",
                "config_options": "config.options", "other_proto_package": "library.json",
                "other_config_proto": "config.proto", "other_config_options": "config.options",
            }[role]
            expected_path = package + "/" + name
        require(path == expected_path, f"unexpected source path: {role}")
        by_role[item["role"]] = item
    require(len({item["path"] for item in files}) == len(files), "duplicate closure path")
    require(by_role["nanopb_package"]["sha256"] == NANOPB_PACKAGE_SHA256
            and by_role["nanopb_generator"]["sha256"] == GENERATOR_SHA256
            and by_role["config_proto"]["sha256"] == PROTO_SHA256
            and by_role["config_options"]["sha256"] == OPTIONS_SHA256
            and by_role["generated_h"]["sha256"] == HEADER_SHA256,
            "known independent source identity drift")
    require(by_role["nanopb_pb_decode_c"]["sha256"] ==
            "f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632",
            "observed decoder source identity drift")
    expected_helpers = {
        "nanopb_platformio_generator": "3dd541f77affb32d0a6515ce472612e364a9042024f2d2f79a8e66da43b68312",
        "nanopb_generator_proto_init": "b387c9a6a553ed2184cf8c67243bb26b27bd46baf44465f0d5ffeb139c365105",
        "nanopb_generator_utils": "6d091e256cdda09002c357da4901d259078fe1ef53a010392a251dd1107d6313",
        "nanopb_generator_nanopb_pb2": "fe72409165c1973e05a41dbeee1292246d02fe1a0f05c4424270e771e2b4dbb4",
        "nanopb_generator_nanopb_proto": "1a50d0822c5ba4395297755b11864af952053be3e0dc44c860f988b1b73c3c55",
        "nanopb_protoc": "6bc34847cc6c0c9ef6ec6137beceef6b05c378f248dee6a7086e5b2166ffc71d",
    }
    for role, expected in expected_helpers.items():
        require(by_role[role]["sha256"] == expected, f"generator helper identity drift: {role}")
    require(by_role["other_config_proto"]["sha256"] != PROTO_SHA256
            and by_role["other_config_options"]["sha256"] != OPTIONS_SHA256,
            "distinct resolved proto instance evidence missing")
    edges = record["include_edges"]
    require(isinstance(edges, list) and bool(edges), "missing include-edge observation")
    for edge in edges:
        require(isinstance(edge, dict) and set(edge) == {"source_role", "header"}
                and edge["source_role"] in INCLUDE_SOURCES
                and edge["header"] in LOCAL_HEADERS,
                "invalid include-edge observation")
    require({"source_role": "generated_c", "header": "config.pb.h"} in edges,
            "generated C include edge missing")
    selection = record["full_package_selection"]
    require(isinstance(selection, dict) and set(selection) == {"build_src_filter", "pb_encode_c"}
            and selection["build_src_filter"] == ["+<*.c>"], "package source-selection observation")
    encode = selection["pb_encode_c"]
    require(isinstance(encode, dict) and set(encode) == {"path", "sha256", "bytes"}
            and encode["path"] == ".pio/libdeps/glyph_mk6/Nanopb/pb_encode.c"
            and isinstance(encode["sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", encode["sha256"]) is not None
            and isinstance(encode["bytes"], int) and encode["bytes"] > 0,
            "pb_encode.c selection identity")
    alternate = record["alternate_observation"]
    require(isinstance(alternate, dict) and set(alternate) == {
        "nanopb_tag", "nanopb_commit", "package_version", "selected_for_observed_build",
        "generation_proto_sha256", "generation_options_sha256", "result", "files",
    }, "alternate observation shape")
    require(alternate == {
        "nanopb_tag": "0.4.9.1", "nanopb_commit": "cad3c18ef15a663e30e3e43e3a752b66378adec1",
        "package_version": "0.4.91", "selected_for_observed_build": False,
        "generation_proto_sha256": PROTO_SHA256, "generation_options_sha256": OPTIONS_SHA256,
        "result": "REJECTED_VERSION_DRIFT", "files": ALTERNATE_FILES,
    }, "alternate observation identity/drift")
    return by_role


def validate_tracked(record: dict, root: Path = ROOT) -> None:
    for path, expected in TRACKED.items():
        check_hash(root, path, expected)
    for path, (needles, expected) in SELECTORS.items():
        data = check_hash(root, path, expected)
        source = data.decode("utf-8")
        for needle in needles:
            require(source.splitlines().count("    " + needle) == 1
                    if path.endswith("env.ini") else needle in source,
                    f"selector drift: {path}: {needle}")
    require(GENERATION_PROTO_DECLARATION in (root / "platformio.ini").read_text(encoding="utf-8"),
            "generation input declaration drift")
    header = regular(root, "tools/fixtures/mode_selection_host/generated/config.pb.h").read_text(encoding="utf-8")
    require("/* Generated by nanopb-0.4.9.2 */" in header, "tracked generated version drift")
    package = json.loads(regular(root, "tools/fixtures/mode_selection_host/generated/nanopb.library.json").read_text())
    require(package["name"] == "Nanopb" and package["version"] == "0.4.92", "tracked package version drift")
    # The report is pinned to one observed source snapshot. No current HEAD
    # equality or future dependency resolution is implied.
    result = subprocess.run(["git", "cat-file", "-e", f"{record['configurator_sha']}^{{commit}}"],
                            cwd=root, capture_output=True, check=False)
    require(result.returncode == 0, "observed configurator commit unavailable locally")


def validate_resolved_checkout(record: dict, resolved_root: Path) -> None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=resolved_root,
                            capture_output=True, text=True, check=False, timeout=15)
    require(result.returncode == 0 and result.stdout.strip() == record["configurator_sha"],
            "resolved checkout is not the observed configurator snapshot")
    status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"],
                            cwd=resolved_root, capture_output=True, text=True, check=False, timeout=15)
    require(status.returncode == 0 and not status.stdout,
            "resolved checkout has staged, unstaged, or untracked changes")


def include_edges(contents: dict[str, bytes]) -> list[dict[str, str]]:
    edges = []
    pattern = re.compile(r'^\s*#\s*include\s*([<"])([^>"]+)[>"]', re.MULTILINE)
    for role in INCLUDE_SOURCES:
        source = contents[role].decode("utf-8")
        for opener, header in pattern.findall(source):
            if opener == '"' and header not in LOCAL_HEADERS:
                raise ClosureError(f"unrecorded local include: {role}: {header}")
            if header in LOCAL_HEADERS:
                edges.append({"source_role": role, "header": header})
    return edges


def verify_package_identities(record: dict, resolved_root: Path) -> None:
    nanopb_meta_path = ".pio/libdeps/glyph_mk6/Nanopb/.piopm"
    nanopb_meta = json.loads(check_hash(resolved_root, nanopb_meta_path,
                                        record["resolution"]["nanopb_piopm_sha256"]))
    require(nanopb_meta["name"] == "Nanopb" and nanopb_meta["version"] == "0.4.92"
            and nanopb_meta["spec"]["owner"] == "nanopb"
            and nanopb_meta["spec"]["name"] == "Nanopb", "Nanopb installed package identity drift")
    for instance in record["resolution"]["proto_instances"]:
        package = instance["package_path"]
        metadata_path = package + "/.git/.piopm"
        metadata = json.loads(check_hash(resolved_root, metadata_path, instance["piopm_sha256"]))
        require(metadata["name"] == "HayBox-proto"
                and metadata["spec"]["uri"] == "git+" + instance["selector"],
                f"installed proto selector drift: {instance['role']}")
        git = subprocess.run(["git", "-C", str(resolved_root / package), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=False, timeout=15)
        require(git.returncode == 0 and git.stdout.strip() == instance["source_commit"],
                f"installed proto commit drift: {instance['role']}")
        require(not (resolved_root / package / "LICENSE").exists()
                and not (resolved_root / package / "LICENSE.txt").exists(),
                f"proto package license-file observation drift: {instance['role']}")
    nanopb_dir = resolved_root / ".pio/libdeps/glyph_mk6/Nanopb"
    require(not (nanopb_dir / "LICENSE").exists() and not (nanopb_dir / "LICENSE.txt").exists(),
            "Nanopb package license-file observation drift")


def verify_selected_nanopb_c(resolved_root: Path) -> None:
    """Bind the package's +<*.c> selector to its exact top-level source set."""
    package = resolved_root / ".pio/libdeps/glyph_mk6/Nanopb"
    require(package.is_dir() and not package.is_symlink(), "missing regular Nanopb package directory")
    selected = {entry.name: entry for entry in package.iterdir() if entry.name.endswith(".c")}
    require(set(selected) == {"pb_common.c", "pb_decode.c", "pb_encode.c"},
            "selected Nanopb C source set drift")
    for name, path in selected.items():
        require(path.is_file() and not path.is_symlink(), f"unsafe selected Nanopb C source: {name}")


def verify_resolved(record: dict, by_role: dict[str, dict], resolved_root: Path, python: Path) -> None:
    require(resolved_root.is_dir() and not resolved_root.is_symlink(), "missing clean resolved root")
    require(python.is_file(), "explicit Python interpreter required")
    verify_selected_nanopb_c(resolved_root)
    contents = {}
    for role, item in by_role.items():
        data = check_hash(resolved_root, item["path"], item["sha256"])
        require(len(data) == item["bytes"], f"closure size drift: {role}")
        contents[role] = data
    nanopb = json.loads(regular(resolved_root, by_role["nanopb_package"]["path"]).read_text())
    require(nanopb["name"] == "Nanopb" and nanopb["version"] == "0.4.92", "resolved package version drift")
    require(nanopb["build"]["srcFilter"] == record["full_package_selection"]["build_src_filter"],
            "resolved package source-selection drift")
    encode = record["full_package_selection"]["pb_encode_c"]
    encode_data = check_hash(resolved_root, encode["path"], encode["sha256"])
    require(len(encode_data) == encode["bytes"], "selected pb_encode.c size drift")
    proto = json.loads(regular(resolved_root, by_role["proto_package"]["path"]).read_text())
    require(proto["name"] == "HayBox-proto" and proto["license"] == "GPL-3.0-only", "resolved proto license declaration drift")
    other_proto = json.loads(regular(resolved_root, by_role["other_proto_package"]["path"]).read_text())
    require(other_proto["name"] == "HayBox-proto" and other_proto["license"] == "GPL-3.0-only",
            "other resolved proto license declaration drift")
    version_code = (
        "import importlib.metadata, google.protobuf; "
        "print(google.protobuf.__version__); "
        "print(importlib.metadata.version('grpcio-tools'))"
    )
    version = subprocess.run([str(python), "-c", version_code], capture_output=True, text=True,
                             check=False, timeout=15)
    require(version.returncode == 0 and version.stdout.splitlines() ==
            [record["generation"]["protobuf_version"], record["generation"]["grpcio_tools_version"]],
            "host generator package version drift")
    with tempfile.TemporaryDirectory(prefix="glyph-prov-014-") as temp:
        temporary = Path(temp)
        proto_dir, output_dir = temporary / "proto", temporary / "generated"
        proto_dir.mkdir(); output_dir.mkdir()
        shutil.copyfile(regular(resolved_root, by_role["config_proto"]["path"]), proto_dir / "config.proto")
        shutil.copyfile(regular(resolved_root, by_role["config_options"]["path"]), proto_dir / "config.options")
        generator = regular(resolved_root, by_role["nanopb_generator"]["path"])
        values = {"{python}": str(python), "{generator}": str(generator),
                  "{output_dir}": str(output_dir), "{proto_dir}": str(proto_dir)}
        command = [values.get(part, part) for part in record["generation"]["regeneration_command"]]
        run = subprocess.run(command, cwd=proto_dir, capture_output=True, text=True,
                             check=False, timeout=120)
        require(run.returncode == 0, f"Nanopb regeneration failed: {run.stderr.strip()}")
        for role, name in (("generated_c", "config.pb.c"), ("generated_h", "config.pb.h")):
            data = regular(output_dir, name).read_bytes()
            require(len(data) == by_role[role]["bytes"] and digest(data) == by_role[role]["sha256"],
                    f"mismatched generation: {role}")
            contents[role] = data
    require(include_edges(contents) == record["include_edges"], "include-edge correspondence drift")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolved-root", type=Path, help="isolated clean checkout with resolved .pio inputs")
    parser.add_argument("--python", type=Path, help="explicit interpreter for exact generator dependencies")
    args = parser.parse_args()
    try:
        require((args.resolved_root is None) == (args.python is None),
                "--resolved-root and --python must be supplied together")
        record = load_report()
        by_role = validate_record(record)
        validate_tracked(record)
        if args.resolved_root is not None:
            validate_resolved_checkout(record, args.resolved_root)
            verify_package_identities(record, args.resolved_root)
            verify_resolved(record, by_role, args.resolved_root, args.python)
        print("glyph_gp_prov_014_decoder_closure: PASS; one observed snapshot; "
              + ("resolved bytes and regeneration verified" if args.resolved_root else "record/tracked inputs verified"))
        return 0
    except (OSError, ClosureError, KeyError, TypeError, ValueError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as exc:
        print(f"glyph_gp_prov_014_decoder_closure: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
