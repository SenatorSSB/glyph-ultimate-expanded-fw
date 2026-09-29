#!/usr/bin/env python3
"""Isolated adversarial checks for the GP-PROV-014 snapshot verifier."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


CHECKER_PATH = Path(__file__).with_name("check_glyph_gp_prov_014_decoder_closure.py")
spec = importlib.util.spec_from_file_location("glyph_gp_prov_014_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def item(role: str, path: str, content: bytes) -> dict:
    return {"role": role, "path": path, "sha256": sha(content), "bytes": len(content)}


def report_fixture() -> dict:
    files = []
    for role in checker.REQUIRED_ROLES:
        if role in checker.GENERATED_ROLES:
            name = "config.pb.c" if role == "generated_c" else "config.pb.h"
            path = f".pio/build/glyph_mk6/nanopb/generated-src/{name}"
        else:
            if role.startswith("other_"):
                package = "HayBox-proto@src-777dd83f5e06d71aba0103adf11d16aa"
            elif role in {"proto_package", "config_proto", "config_options"}:
                package = "HayBox-proto"
            else:
                package = "Nanopb"
            name = {
                "nanopb_package": "library.json", "nanopb_generator": "generator/nanopb_generator.py",
                "nanopb_platformio_generator": "generator/platformio_generator.py",
                "nanopb_generator_proto_init": "generator/proto/__init__.py",
                "nanopb_generator_utils": "generator/proto/_utils.py",
                "nanopb_generator_nanopb_pb2": "generator/proto/nanopb_pb2.py",
                "nanopb_generator_nanopb_proto": "generator/proto/nanopb.proto",
                "nanopb_protoc": "generator/protoc",
                "nanopb_pb_h": "pb.h", "nanopb_pb_decode_c": "pb_decode.c",
                "nanopb_pb_decode_h": "pb_decode.h", "nanopb_pb_common_c": "pb_common.c",
                "nanopb_pb_common_h": "pb_common.h", "proto_package": "library.json",
                "config_proto": "config.proto", "config_options": "config.options",
                "other_proto_package": "library.json", "other_config_proto": "config.proto",
                "other_config_options": "config.options",
            }[role]
            path = f".pio/libdeps/glyph_mk6/{package}/{name}"
        files.append({"role": role, "path": path, "sha256": "1" * 64, "bytes": 1})
    by_role = {value["role"]: value for value in files}
    for role, value in {
        "nanopb_package": checker.NANOPB_PACKAGE_SHA256,
        "nanopb_generator": checker.GENERATOR_SHA256,
        "nanopb_platformio_generator": "3dd541f77affb32d0a6515ce472612e364a9042024f2d2f79a8e66da43b68312",
        "nanopb_generator_proto_init": "b387c9a6a553ed2184cf8c67243bb26b27bd46baf44465f0d5ffeb139c365105",
        "nanopb_generator_utils": "6d091e256cdda09002c357da4901d259078fe1ef53a010392a251dd1107d6313",
        "nanopb_generator_nanopb_pb2": "fe72409165c1973e05a41dbeee1292246d02fe1a0f05c4424270e771e2b4dbb4",
        "nanopb_generator_nanopb_proto": "1a50d0822c5ba4395297755b11864af952053be3e0dc44c860f988b1b73c3c55",
        "nanopb_protoc": "6bc34847cc6c0c9ef6ec6137beceef6b05c378f248dee6a7086e5b2166ffc71d",
        "config_proto": checker.PROTO_SHA256,
        "config_options": checker.OPTIONS_SHA256,
        "generated_h": checker.HEADER_SHA256,
        "nanopb_pb_decode_c": "f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632",
    }.items():
        by_role[role]["sha256"] = value
    return {
        "schema_name": "glyph_gp_prov_014_decoder_closure", "schema_version": 1,
        "work_order": "GP-PROV-014", "configurator_sha": "a" * 40,
        "resolution": {
            "nanopb_selector": checker.SELECTORS["platformio.ini"][0][0],
            "nanopb_version": "0.4.92", "nanopb_tag": "0.4.9.2",
            "nanopb_commit": checker.NANOPB_COMMIT,
            "nanopb_piopm_sha256": "bc8ba8afe756cc4b7a7c6146b098ef893c0f9dabd4ab0b1cdc608d15ab72ec7a",
            "nanopb_license_package_present": False,
            "nanopb_license_sha256": checker.NANOPB_LICENSE_SHA256,
            "generation_input_declaration": checker.GENERATION_PROTO_DECLARATION,
            "proto_instances": [
                {"role": "generation_input", "selector": checker.SELECTORS["config/glyph/env.ini"][0][0],
                 "selector_path": "config/glyph/env.ini", "package_path": ".pio/libdeps/glyph_mk6/HayBox-proto",
                 "source_commit": checker.PROTO_COMMIT,
                 "piopm_sha256": "e3c2aae427f4538bd25d277ba2cb76248b3687ce3962d41588d0db8b82b8c1ce",
                 "license_file_present": False, "license_declared": "GPL-3.0-only"},
                {"role": "other_resolved", "selector": checker.SELECTORS["platformio.ini"][0][1],
                 "selector_path": "platformio.ini",
                 "package_path": ".pio/libdeps/glyph_mk6/HayBox-proto@src-777dd83f5e06d71aba0103adf11d16aa",
                 "source_commit": checker.OTHER_PROTO_COMMIT,
                 "piopm_sha256": "0b4c1862132196c8ad5b2d14603093b6cc36c9b72c99e6b67ed05a66e206486d",
                 "license_file_present": False, "license_declared": "GPL-3.0-only"},
            ],
        },
        "generation": {
            "build_command": checker.EXPECTED_BUILD_COMMAND, "build_cwd": "{checkout}",
            "regeneration_command": checker.EXPECTED_REGENERATION_COMMAND,
            "regeneration_cwd": "{proto_dir}", "generator_version": "nanopb-0.4.9.2",
            "protobuf_version": "6.33.6", "grpcio_tools_version": "1.80.0",
            "generator_sha256": checker.GENERATOR_SHA256, "options": ["--error-on-unmatched"],
        },
        "files": files,
        "include_edges": [{"source_role": "generated_c", "header": "config.pb.h"}],
        "full_package_selection": {
            "build_src_filter": ["+<*.c>"],
            "pb_encode_c": {"path": ".pio/libdeps/glyph_mk6/Nanopb/pb_encode.c",
                            "sha256": "1" * 64, "bytes": 1},
        },
        "alternate_observation": {
            "nanopb_tag": "0.4.9.1",
            "nanopb_commit": "cad3c18ef15a663e30e3e43e3a752b66378adec1",
            "package_version": "0.4.91", "selected_for_observed_build": False,
            "generation_proto_sha256": checker.PROTO_SHA256,
            "generation_options_sha256": checker.OPTIONS_SHA256,
            "result": "REJECTED_VERSION_DRIFT", "files": copy.deepcopy(checker.ALTERNATE_FILES),
        },
        "non_claims": [
            "future compatible-range resolution", "historical tested-artifact package identity",
            "transitive reproducible build", "decoder behavior acceptance", "firmware behavior",
            "physical controller behavior", "GP-CONFIG-012/013 authorization",
        ],
    }


def rejected(label: str, expected: str, run) -> None:
    try:
        run()
    except checker.ClosureError as exc:
        assert expected in str(exc), (label, str(exc))
        return
    raise AssertionError(f"accepted {label}")


def test_record() -> int:
    value = report_fixture()
    checker.validate_record(value, snapshot_sha="a" * 40)
    cases = [
        ("wrong version", "resolution identity", lambda v: v["resolution"].__setitem__("nanopb_version", "0.4.91")),
        ("snapshot drift", "snapshot drift", lambda v: v.__setitem__("configurator_sha", "b" * 40)),
        ("missing source", "ordered source closure", lambda v: v["files"].pop(4)),
        ("extra source", "ordered source closure", lambda v: v["files"].append(copy.deepcopy(v["files"][0]))),
        ("mixed decoder", "observed decoder source identity drift", lambda v: next(x for x in v["files"] if x["role"] == "nanopb_pb_decode_c").__setitem__("sha256", "0" * 64)),
        ("mismatched regeneration command", "generation identity", lambda v: v["generation"]["regeneration_command"].remove("--error-on-unmatched")),
        ("mismatched actual build command", "generation identity", lambda v: v["generation"]["build_command"].insert(1, "-B")),
        ("missing license declaration", "proto instance shape", lambda v: v["resolution"]["proto_instances"][0].pop("license_declared")),
        ("invented package license", "resolution identity", lambda v: v["resolution"].__setitem__("nanopb_license_package_present", True)),
        ("future pin claim", "snapshot scope/non-claims", lambda v: v["non_claims"].remove("future compatible-range resolution")),
        ("generated header drift", "known independent source identity drift", lambda v: next(x for x in v["files"] if x["role"] == "generated_h").__setitem__("sha256", "0" * 64)),
        ("missing include edge", "missing include-edge observation", lambda v: v["include_edges"].clear()),
        ("package source filter drift", "package source-selection observation", lambda v: v["full_package_selection"].__setitem__("build_src_filter", ["+<pb_decode.c>"])),
        ("alternate promoted to current", "alternate observation identity/drift", lambda v: v["alternate_observation"].__setitem__("selected_for_observed_build", True)),
        ("alternate decoder hash changed", "alternate observation identity/drift", lambda v: v["alternate_observation"]["files"][0].__setitem__("sha256", "0" * 64)),
        ("0.4.9.1 decoder substituted into selected closure", "observed decoder source identity drift", lambda v: next(x for x in v["files"] if x["role"] == "nanopb_pb_decode_c").__setitem__("sha256", checker.ALTERNATE_FILES[0]["sha256"])),
    ]
    for label, expected, change in cases:
        changed = copy.deepcopy(value)
        change(changed)
        rejected(label, expected, lambda v=changed: checker.validate_record(v, snapshot_sha="a" * 40))
    return len(cases)


def write_bundle(root: Path) -> tuple[dict, dict[str, dict]]:
    entries = {
        "nanopb_package": b'{"name":"Nanopb","version":"0.4.92","build":{"srcFilter":["+<*.c>"]}}\n',
        "nanopb_generator": b"generator source\n", "nanopb_pb_h": b"pb.h\n",
        "nanopb_platformio_generator": b"PlatformIO generator\n",
        "nanopb_generator_proto_init": b"proto init\n",
        "nanopb_generator_utils": b"proto utils\n",
        "nanopb_generator_nanopb_pb2": b"nanopb pb2\n",
        "nanopb_generator_nanopb_proto": b"nanopb.proto\n",
        "nanopb_protoc": b"protoc launcher\n",
        "nanopb_pb_decode_c": b'#include "pb_decode.h"\n', "nanopb_pb_decode_h": b'#include "pb.h"\n',
        "nanopb_pb_common_c": b'#include "pb_common.h"\n', "nanopb_pb_common_h": b'#include "pb.h"\n',
        "proto_package": b'{"name":"HayBox-proto","license":"GPL-3.0-only"}\n',
        "config_proto": b"config.proto\n", "config_options": b"config.options\n",
        "other_proto_package": b'{"name":"HayBox-proto","license":"GPL-3.0-only"}\n',
        "other_config_proto": b"different config.proto\n",
        "other_config_options": b"different config.options\n",
        "generated_c": b'#include "config.pb.h"\n', "generated_h": b'#include <pb.h>\n',
    }
    value = report_fixture()
    by_role = {}
    for record in value["files"]:
        role = record["role"]
        record.update(item(role, record["path"], entries[role]))
        by_role[role] = record
        path = root / record["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(entries[role])
    encode = root / value["full_package_selection"]["pb_encode_c"]["path"]
    encode.write_bytes(b"pb_encode.c\n")
    value["full_package_selection"]["pb_encode_c"].update(
        {"sha256": sha(encode.read_bytes()), "bytes": encode.stat().st_size})
    value["include_edges"] = checker.include_edges(entries)
    interpreter = root / "explicit-python"
    interpreter.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib, sys\n"
        "if '-c' in sys.argv:\n"
        "    print('6.33.6\\n1.80.0')\n"
        "else:\n"
        "    out = pathlib.Path(sys.argv[sys.argv.index('--output-dir') + 1])\n"
        "    (out / 'config.pb.c').write_bytes(b'#include \\\"config.pb.h\\\"\\n')\n"
        "    (out / 'config.pb.h').write_bytes(b'#include <pb.h>\\n')\n",
        encoding="utf-8",
    )
    interpreter.chmod(0o755)
    return value, by_role


def test_resolved() -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-prov-014-test-") as temp:
        root = Path(temp)
        value, by_role = write_bundle(root)
        python = root / "explicit-python"
        checker.verify_resolved(value, by_role, root, python)
        cases = 0
        package_dir = root / ".pio/libdeps/glyph_mk6/Nanopb"
        extra_c = package_dir / "pb_unrecorded.c"
        extra_c.write_bytes(b"unrecorded selected source\n")
        rejected("extra selected Nanopb C source", "selected Nanopb C source set drift",
                 lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        extra_c.unlink()
        encode = package_dir / "pb_encode.c"
        encode.unlink()
        rejected("missing selected Nanopb C source", "selected Nanopb C source set drift",
                 lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        encode.symlink_to(package_dir / "pb_decode.c")
        rejected("symlinked selected Nanopb C source", "unsafe selected Nanopb C source",
                 lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        encode.unlink(); encode.write_bytes(b"pb_encode.c\n")
        generated_header = root / by_role["generated_h"]["path"]
        generated_header.unlink()
        rejected("missing actual generated header", "missing regular closure file",
                 lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        generated_header.write_bytes(b"#include <pb.h>\n")
        generated_c = root / by_role["generated_c"]["path"]
        generated_c.unlink()
        rejected("missing actual generated C", "missing regular closure file",
                 lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        generated_c.write_bytes(b'#include "config.pb.h"\n')
        target = root / by_role["nanopb_pb_decode_h"]["path"]
        target.write_bytes(b"tampered")
        rejected("tampered decoder header", "byte digest mismatch", lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        target.write_bytes(b'#include "pb.h"\n')
        target.unlink()
        rejected("omitted decoder header", "missing regular closure file", lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        target.symlink_to(root / by_role["nanopb_pb_h"]["path"])
        rejected("symlink decoder header", "symlink in closure", lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        target.unlink(); target.write_bytes(b'#include "pb.h"\n')
        package = root / by_role["nanopb_package"]["path"]
        package.write_bytes(b'{"name":"Nanopb","version":"0.4.91","build":{"srcFilter":["+<*.c>"]}}\n')
        changed = copy.deepcopy(by_role)
        changed["nanopb_package"] = item("nanopb_package", by_role["nanopb_package"]["path"], package.read_bytes())
        rejected("wrong package version with updated hash", "resolved package version drift", lambda: checker.verify_resolved(value, changed, root, python)); cases += 1
        package.write_bytes(b'{"name":"Nanopb","version":"0.4.92","build":{"srcFilter":["+<*.c>"]}}\n')
        generated = root / by_role["generated_c"]["path"]
        generated.write_bytes(b"mixed generated C")
        rejected("mixed preexisting generated C", "byte digest mismatch", lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        generated.write_bytes(b'#include "config.pb.h"\n')
        encode.write_bytes(b"different selected source")
        rejected("tampered selected encoder source", "byte digest mismatch", lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
        encode.write_bytes(b"pb_encode.c\n")
        python.write_text(python.read_text().replace("config.pb.h", "wrong.h"), encoding="utf-8")
        rejected("mismatched regenerated C", "mismatched generation", lambda: checker.verify_resolved(value, by_role, root, python)); cases += 1
    return cases


def test_checkout() -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-prov-014-checkout-") as temp:
        root = Path(temp)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "config", "user.name", "GP-PROV-014 test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "gp-prov-014@example.invalid"], cwd=root, check=True)
        (root / "README.md").write_text("observed\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "observed"], cwd=root, check=True)
        snapshot = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        value = {"configurator_sha": snapshot}
        checker.validate_resolved_checkout(value, root)
        rejected("wrong observed commit", "not the observed configurator snapshot",
                 lambda: checker.validate_resolved_checkout({"configurator_sha": "0" * 40}, root))
        (root / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        rejected("dirty resolved checkout", "resolved checkout has staged, unstaged, or untracked changes",
                 lambda: checker.validate_resolved_checkout(value, root))
    return 2


def test_package_identities() -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-prov-014-package-ids-") as temp:
        root = Path(temp)
        value = report_fixture()
        nanopb_meta = root / ".pio/libdeps/glyph_mk6/Nanopb/.piopm"
        nanopb_meta.parent.mkdir(parents=True)
        nanopb_meta.write_text(json.dumps({"name": "Nanopb", "version": "0.4.92",
                                            "spec": {"owner": "nanopb", "name": "Nanopb"}}), encoding="utf-8")
        value["resolution"]["nanopb_piopm_sha256"] = sha(nanopb_meta.read_bytes())
        for instance in value["resolution"]["proto_instances"]:
            package = root / instance["package_path"]
            package.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(package)], check=True)
            subprocess.run(["git", "config", "user.name", "GP-PROV-014 test"], cwd=package, check=True)
            subprocess.run(["git", "config", "user.email", "gp-prov-014@example.invalid"], cwd=package, check=True)
            (package / "README.md").write_text(instance["role"], encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=package, check=True)
            subprocess.run(["git", "commit", "-qm", "package"], cwd=package, check=True)
            instance["source_commit"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=package, text=True).strip()
            meta = package / ".git/.piopm"
            meta.write_text(json.dumps({"name": "HayBox-proto", "spec": {
                "uri": "git+" + instance["selector"]}}), encoding="utf-8")
            instance["piopm_sha256"] = sha(meta.read_bytes())
        checker.verify_package_identities(value, root)
        cases = 0
        nanopb_meta.write_bytes(b"tampered")
        rejected("tampered Nanopb install metadata", "byte digest mismatch",
                 lambda: checker.verify_package_identities(value, root)); cases += 1
        nanopb_meta.write_text(json.dumps({"name": "Nanopb", "version": "0.4.92",
                                            "spec": {"owner": "nanopb", "name": "Nanopb"}}), encoding="utf-8")
        selected = value["resolution"]["proto_instances"][0]
        selected_meta = root / selected["package_path"] / ".git/.piopm"
        selected_meta.write_text(json.dumps({"name": "HayBox-proto", "spec": {
            "uri": "git+https://github.com/wrong/HayBox-proto#db4e2f6"}}), encoding="utf-8")
        changed = copy.deepcopy(value)
        changed["resolution"]["proto_instances"][0]["piopm_sha256"] = sha(selected_meta.read_bytes())
        rejected("wrong installed selector with matching metadata digest", "installed proto selector drift",
                 lambda: checker.verify_package_identities(changed, root)); cases += 1
        selected_meta.write_text(json.dumps({"name": "HayBox-proto", "spec": {
            "uri": "git+" + selected["selector"]}}), encoding="utf-8")
        (root / selected["package_path"] / "README.md").write_text("new commit", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root / selected["package_path"], check=True)
        subprocess.run(["git", "commit", "-qm", "drift"], cwd=root / selected["package_path"], check=True)
        rejected("resolved package commit drift", "installed proto commit drift",
                 lambda: checker.verify_package_identities(value, root)); cases += 1
    return cases


def main() -> int:
    count = test_record() + test_resolved() + test_checkout() + test_package_identities()
    print(f"glyph_gp_prov_014_decoder_closure: PASS; {count} isolated adversarial cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
