#!/usr/bin/env python3
"""Authenticate C017 applicability and execute the unchanged original016 proof."""
from pathlib import Path
import argparse
import ast
import hashlib
import os
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "a6b7750e271324972c51915563fe0dc22f941f95"
CANDIDATE = "478f438804275f3e0c23e6f36bfd26e34aa343bf"
ORIGINAL016_SOURCE = "0da68bdab9bf0fed4ed595538bea9aba7d2f49f3"
HEADER = "HAL/pico/include/comms/NeoPixelBackend.hpp"
CALLER = "config/glyph/common/src/config.cpp"
CHECKER = "tools/check_glyph_neopixel_null_sendreport_characterization.py"
REPAIRED_HEADER = {"mode": "100644", "blob": "4724544d5989fdf403c5e6e0accab721371bc9d3", "sha256": "71108cbd6ac17f78fd2698be5236854c292a599077f8e74f002493565953b10b"}
EXPORT_TREE_METADATA = {".gitattributes": {"mode": "100644", "blob": "3244aa00c82c51bd52f86e097bed54e8d9ab5c15", "sha256": "07ab86e93ac0429deae65b956d08f2bebb6a15503dca2d032fe553d484e3f288"}}
CURRENT_CHECKER = "tools/check_glyph_gp_config_017_neopixel_repaired_current.py"
CURRENT_FIXTURE = "docs/runtime_config/fixtures/gp_config_017_neopixel_repaired_current.json"
CURRENT_HOST_IDENTITIES = {
    CURRENT_CHECKER: {"mode": "100644", "blob": "ad88fee6d08ba913bc75c0fb2aecefc4b6d8ea10", "sha256": "28fd0fb0485a1483e0ec0beab4657ad4746ea11a0149e67eaa78ca62ff245a29"},
    CURRENT_FIXTURE: {"mode": "100644", "blob": "f36c2d5530f35fb3b25101d66a22c162afd862b9", "sha256": "8b097e9df6d0d7807e469f8ed18b362b67a6b5eb2322ad5550dd33c3204510db"},
}
PINS = {'HAL/pico/include/comms/NeoPixelBackend.hpp': {'mode': '100644', 'blob': '843eb9b937ccebc616679b0ced24b805d8a6290d', 'sha256': 'a3a83278a2f13464f6fa15de7f611ec4189f40fcf14f0ce44ce0b8e6cc890dbc'}, 'HAL/pico/include/rgb/ButtonLocations.hpp': {'mode': '100644', 'blob': 'a291b9ff6ed8482a2caa7452362eafa3077b13f1', 'sha256': '4b1a0aa989c2c162e0700b0d30c22f0f1653dc27708ad8cc51f27c97cdb6cb05'}, 'config/glyph/common/src/config.cpp': {'mode': '100644', 'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726', 'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'}, 'docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json': {'mode': '100644', 'blob': '6646c82f303cbc9d89c91a44bd8fe6d1494f00fe', 'sha256': '92d9f40b6b548037532bc2974dd2eeaa1699f8696c9637f273e9e7d54cdf016b'}, 'tools/check_glyph_neopixel_null_sendreport_characterization.py': {'mode': '100644', 'blob': '7f1ecd243c190c703d031c8376458bfccbec14d0', 'sha256': 'a6204924f1d94b4e87abc9535fe67af8e6387302f2aa98e2c48c9170c63712e8'}, 'tools/fixtures/neopixel_null_host/neo_harness.cpp': {'mode': '100644', 'blob': 'c9a0ec576c7126798b9ef908cdd0b0a047baf322', 'sha256': '85f6d0922c20a20da2258cf2e871b9c35b644508a1b3b1f13b7e28529dd62c0e'}, 'tools/fixtures/neopixel_null_host/include/FastLED.h': {'mode': '100644', 'blob': 'e60dd96418f1def42a2b2ac4dd760873a127db09', 'sha256': '01a4ad9d08b879495c0115f2ea167704949e3bcf690d427ab4a9b21b70625f9e'}, 'tools/fixtures/neopixel_null_host/include/config.pb.h': {'mode': '100644', 'blob': '2ebb970f544622a4452410cea1822cae79c0fb46', 'sha256': '8e96d2814f29b04889c6bc25ae38faae492ede8f94631355891d7f63f5e7aa53'}, 'tools/fixtures/neopixel_null_host/include/core/CommunicationBackend.hpp': {'mode': '100644', 'blob': 'a0cad046c3fb51dd7c06006f09b90b465f7c9e76', 'sha256': '71c30c37faee0c7653d2150215c5abff49aba43454c5e436e6e95c008d858ff9'}, 'tools/fixtures/custom_modifier_cache_host/schema/config.pb.h': {'mode': '100644', 'blob': '9b8d8eb9e771e3a791356a94681cb5c89ce93e74', 'sha256': '532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3'}}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, timeout=30)


def object_bytes(root, revision, path, identity):
    entry = git(root, "ls-tree", "-z", revision, "--", path)
    expected = ("100644 blob " + identity["blob"] + "\t" + path).encode() + b"\0"
    require(entry == expected, "immutable mode/blob custody: " + path)
    data = git(root, "show", revision + ":" + path)
    require(sha(data) == identity["sha256"] and blob(data) == identity["blob"],
            "immutable bytes custody: " + path)
    return data


def current_bytes(root, head, path, identity):
    target = root / path
    require(target.is_file() and not target.is_symlink(), "missing/unsafe current input: " + path)
    require(stat.S_ISREG(target.stat().st_mode) and not target.stat().st_mode & 0o111,
            "current input must be regular100644: " + path)
    for parent in target.parents:
        require(not parent.is_symlink(), "symlink input ancestor: " + path)
        if parent == root:
            break
    data = target.read_bytes()
    require(sha(data) == identity["sha256"] and blob(data) == identity["blob"],
            "current immutable dependency byte drift: " + path)
    require(git(root, "ls-tree", "-z", head, "--", path) ==
            ("100644 blob " + identity["blob"] + "\t" + path).encode() + b"\0",
            "current committed mode/blob drift: " + path)
    require(git(root, "ls-files", "--stage", "-z", "--", path) ==
            ("100644 " + identity["blob"] + " 0\t" + path).encode() + b"\0",
            "current index mode/blob/stage drift: " + path)
    require(git(root, "ls-files", "-v", "-z", "--", path) ==
            ("H " + path).encode() + b"\0", "current index flag drift: " + path)
    return data


def authenticate_current(root):
    from glyph_c017_campaign_transition import present, authenticate, C, B
    require(C == CANDIDATE and B == BASE, "C017 module literal C/B mismatch")
    require(present(root), "missing native035 contract")
    proof = authenticate(root)
    require(proof["candidate"] == CANDIDATE and proof["base"] == BASE,
            "authenticated C017 identity mismatch")
    require({BASE, CANDIDATE, ORIGINAL016_SOURCE} <= set(proof["object_roots"]),
            "missing authenticated immutable historical/C017 roots")
    require(proof["phase"] in {"BASELINE", "CANDIDATE_VALIDATION_ONLY", "SOURCE_FREE_PROCESSOR", "ACCEPTED_TRANSITION"},
            "unknown native035 phase")
    head = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    require(proof["target"] == head, "native035 target/HEAD mismatch")
    repaired = proof["phase"] in {"CANDIDATE_VALIDATION_ONLY", "ACCEPTED_TRANSITION"}
    if repaired:
        require(proof["source_candidates"].get(HEADER) == CANDIDATE,
                "repaired NeoPixel lacks exact C017 source ownership")
    else:
        require(proof["source_candidates"].get(HEADER) != CANDIDATE,
                "source-free phase claims repaired C017")
    for path, identity in PINS.items():
        object_bytes(root, BASE, path, identity)
        current_bytes(root, head, path, REPAIRED_HEADER if path == HEADER and repaired else identity)
    for path in (HEADER, CALLER):
        object_bytes(root, ORIGINAL016_SOURCE, path, PINS[path])
    require(git(root, "rev-parse", "HEAD").decode().strip() == head,
            "HEAD changed during historical dependency authentication")
    return proof


def replay_original(root, directory):
    """Materialize only the ten literal original source and host dependencies."""
    for path, identity in PINS.items():
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(object_bytes(root, BASE, path, identity))
        target.chmod(0o644)
    scratch = directory / "private-tmp"
    scratch.mkdir()
    result = subprocess.run([sys.executable, "-B", str(directory / CHECKER)], cwd=directory,
                            env=dict(os.environ, TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE="1"),
                            text=True, capture_output=True, timeout=100)
    require(result.returncode == 0, "unchanged original016 actual replay failed:\n" + result.stdout + result.stderr)
    marker = "glyph_neopixel_null_sendreport_characterization: PASS; 9 isolated cases; 9 adversarial contracts; H1 host evidence; physical reachability UNKNOWN"
    require(result.stdout.strip() == marker, "original016 exact completion marker absent")
    for path, identity in PINS.items():
        target = directory / path
        require(target.is_file() and not target.is_symlink() and not target.stat().st_mode & 0o111 and
                sha(target.read_bytes()) == identity["sha256"], "historical replay input changed: " + path)
    return result.stdout


def current_contract(root):
    raw = object_bytes(root, CANDIDATE, CURRENT_CHECKER, CURRENT_HOST_IDENTITIES[CURRENT_CHECKER])
    parsed = ast.parse(raw.decode("utf-8"))
    tables = {}
    for node in parsed.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"CURRENT_PINS", "ORIGINAL_BASE_PINS"}:
                require(name not in tables, "duplicate immutable current17 pin table")
                tables[name] = ast.literal_eval(node.value)
    require(set(tables) == {"CURRENT_PINS", "ORIGINAL_BASE_PINS"}, "immutable current17 pin tables missing")
    require(len(tables["CURRENT_PINS"]) == 17 and len(tables["ORIGINAL_BASE_PINS"]) == 15,
            "immutable finite current17 closure extent")
    for table, revision in ((tables["CURRENT_PINS"], CANDIDATE), (tables["ORIGINAL_BASE_PINS"], BASE)):
        for path, identity in table.items():
            require(isinstance(path, str) and not Path(path).is_absolute() and ".." not in Path(path).parts,
                    "unsafe immutable closure path")
            require(identity["mode"] == "100644", "unsafe immutable closure mode")
            object_bytes(root, revision, path, identity)
    pins = dict(tables["CURRENT_PINS"])
    require(not set(pins) & set(CURRENT_HOST_IDENTITIES), "overlapping independent current17 identities")
    pins.update(CURRENT_HOST_IDENTITIES)
    require(pins[HEADER] == REPAIRED_HEADER, "immutable repaired source identity differs")
    return pins, tables["ORIGINAL_BASE_PINS"]


def authenticate_repaired_inputs(root, proof):
    pins, original = current_contract(root)
    repaired = proof["phase"] in {"CANDIDATE_VALIDATION_ONLY", "ACCEPTED_TRANSITION"}
    for path, identity in pins.items():
        current_bytes(root, proof["target"], path, PINS[HEADER] if path == HEADER and not repaired else identity)
    return pins, original


def export_finite_objects(root, directory, pins, original):
    """Export exact C/B commits and only closure ancestor trees and file blobs."""
    git(directory, "-c", "init.templateDir=", "init", "-q")
    exported = set()
    def export(identity, kind):
        if identity in exported:
            return
        require(git(root, "cat-file", "-t", identity).decode().strip() == kind, "export object kind")
        data = git(root, "cat-file", kind, identity)
        hashed = hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(hashed == identity, "export immutable object hash mismatch")
        actual = subprocess.check_output(["git", "hash-object", "-t", kind, "-w", "--stdin"],
                                         cwd=directory, input=data, timeout=30).decode().strip()
        require(actual == identity, "private immutable object import mismatch")
        exported.add(identity)
    # Native Git validates root tree attribute references during object import.
    # Import this one fixed ancillary blob without materializing or staging it.
    for revision in (BASE, CANDIDATE):
        for path, identity in EXPORT_TREE_METADATA.items():
            object_bytes(root, revision, path, identity)
            export(identity["blob"], "blob")
    for revision, table in ((BASE, original), (CANDIDATE, pins)):
        export(revision, "commit")
        export(git(root, "rev-parse", revision + "^{tree}").decode().strip(), "tree")
        for path, identity in table.items():
            parts = path.split("/")
            for index in range(1, len(parts)):
                export(git(root, "rev-parse", revision + ":" + "/".join(parts[:index])).decode().strip(), "tree")
            export(identity["blob"], "blob")
    for path, identity in pins.items():
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(object_bytes(root, CANDIDATE, path, identity))
        target.chmod(0o644)
        git(directory, "update-index", "--add", "--cacheinfo", "100644", identity["blob"], path)
    git(directory, "update-ref", "--no-deref", "HEAD", CANDIDATE)
    require(git(directory, "rev-parse", "HEAD").decode().strip() == CANDIDATE, "private exact C017 HEAD")
    return len(exported)


def run_repaired(root, proof, directory):
    pins, original = authenticate_repaired_inputs(root, proof)
    repaired = proof["phase"] in {"CANDIDATE_VALIDATION_ONLY", "ACCEPTED_TRANSITION"}
    if repaired:
        execution = root
        classification = "ACTUAL_CURRENT_C017_SOURCE_HOST_PROOF"
    else:
        execution = directory / "immutable-c017"
        execution.mkdir()
        export_finite_objects(root, execution, pins, original)
        classification = "IMMUTABLE_C017_SOURCE_REPLAY_ONLY"
    scratch = directory / "private-tmp"
    scratch.mkdir()
    result = subprocess.run([sys.executable, "-B", str(execution / CURRENT_CHECKER)], cwd=execution,
                            env=dict(os.environ, TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE="1"),
                            text=True, capture_output=True, timeout=100)
    require(result.returncode == 0, "unchanged current17 actual execution failed:\n" + result.stdout + result.stderr)
    require("layout=debug-struct-time cases=9 PASS" in result.stdout and
            "layout=NDEBUG-scalar-time cases=9 PASS" in result.stdout and
            "negative_controls=36 PASS" in result.stdout and
            "glyph_gp_config_017_neopixel_repaired_current: PASS" in result.stdout,
            "unchanged current17 full completion markers missing")
    for path, identity in pins.items():
        current_bytes(root, proof["target"], path, PINS[HEADER] if path == HEADER and not repaired else identity)
    return result.stdout, classification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repaired-current", action="store_true", help="execute separate exact C017 host proof")
    args = parser.parse_args()
    try:
        before = authenticate_current(ROOT)
        with tempfile.TemporaryDirectory(prefix="glyph-016-immutable-replay-", dir="/private/tmp") as directory:
            if args.repaired_current:
                completion, classification = run_repaired(ROOT, before, Path(directory))
            else:
                completion = replay_original(ROOT, Path(directory))
                classification = "IMMUTABLE_ORIGINAL016_ACTUAL_REPLAY"
        after = authenticate_current(ROOT)
        require(after == before, "native035 state changed during original016 replay")
        print(completion, end="")
        print("glyph_neopixel_historical_replay: PASS; proof=" + classification + "; native035phase=" + before["phase"])
        if not args.repaired_current:
            print("historical_expected_null_failures=7 current017_proof=SEPARATE")
        print("physical_null_reachability=UNKNOWN firmware_build=NOT_RUN hardware_acceptance=NOT_CLAIMED Nunchuk=NOT_TESTED root_cause=UNPROVEN")
        return 0
    except (AssertionError, OSError, ValueError, KeyError, TypeError, ImportError, subprocess.SubprocessError) as exc:
        print("glyph_neopixel_historical_replay: FAIL: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
