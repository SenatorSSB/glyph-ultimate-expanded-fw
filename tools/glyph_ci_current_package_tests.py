"""Offline public source, lineage, package storage, and WebSerial authority regressions."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

import check_glyph_docs_agent_surface as docs
import check_glyph_runtime_config_webserial_device_write_source_authority as authority
from glyph_ci_package_scope import PACKAGE_BASE

ROOT = Path(__file__).resolve().parents[1]
TRANSACTION = ROOT / "tools/fixtures/glyph_package_v1/transaction"
sys.path.insert(0, str(TRANSACTION))
from build import build
from run import dump_namespace, load_namespace


def active_authority():
    docs.validate_docs()
    text = authority.read_required(authority.DOC)
    authority.require_phrases(text)
    authority.ensure_flag_false(text)
    authority.ensure_no_positive_claims(text)
    authority.ensure_no_runtime_write_symbols_added()
    changed = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", "-z",
                                       PACKAGE_BASE, "HEAD"], cwd=ROOT)
    authority.ensure_no_flashing_automation_changed([path.decode() for path in changed.split(b"\0") if path])


def run_package(temp):
    binary = build(ROOT, temp / "build", framework=os.environ.get("GLYPH_ARDUINOPICO_FRAMEWORK"), boot_probe=True)
    def invoke(*args, stdin=None):
        return subprocess.check_output([str(binary), *map(str, args)], input=stdin, text=True,
                                       env={**os.environ, "UBSAN_OPTIONS": "halt_on_error=1",
                                            "ASAN_OPTIONS": "detect_leaks=0"})
    old = (ROOT / "tools/fixtures/glyph_package_v1/historical_config/minimal.pb").read_bytes()
    assert hashlib.sha256(old).hexdigest() == "191856fe3a60529575e2305f839327d6186e909f35b2acfa52b794132b077de2"
    result = invoke("observe-historical-faults", stdin="\n".join(
        body.hex() for body in [old, old[:-1], old + b"\x30\x01"]) + "\n")
    assert result.splitlines() == ["0", "1", "1"], result

    status = bytes.fromhex("080310011801")
    packets = [status, status + b"\x18\x01", status[:-1]]
    pack = lambda items: struct.pack("<I", len(items)) + b"".join(struct.pack("<I", len(b)) + b for b in items)
    corpus = temp / "requests"
    corpus.write_bytes(pack(packets))
    invoke("wire-requests", corpus, temp / "wire.json")
    cases = json.loads((temp / "wire.json").read_text())
    assert [v["canonical_request"] for v in cases] == [True, False, False], cases
    corpus.write_bytes(pack([status]))
    for name, files in [("empty", {}), ("unsupported", {"/ultimate-v2-0.bin": b"PDS2\x04\x00"}),
                        ("corrupt", {"/ultimate-v2-0.bin": b"PDS2\x03\x00bad"})]:
        case = temp / name
        case.mkdir()
        files["/unrelated.bin"] = b"unmanaged public test sentinel"
        dump_namespace(files, case / "files")
        invoke("seed", case / "files", case / "seed.nor")
        invoke("inspect", case / "seed.nor", corpus, case)
        report = json.loads((case / "summary.json").read_text())
        assert report["no_handles"] and report["unchanged"] and report["programs"] == report["erases"] == 0
        assert (case / "after.nor").read_bytes() == (case / "seed.nor").read_bytes()
        assert load_namespace(case / "namespace.bin") == files
        boot = case / "boot"
        boot.mkdir()
        defaults = case / "defaults.pb"
        defaults.write_bytes(old)
        invoke("boot", case / "seed.nor", defaults, boot)
        assert (boot / "status.cobs").stat().st_size > 0
        assert json.loads((boot / "boot.json").read_text())["outcome"] != 0
    print("Current package wire, historical Config fault injection, startup/STATUS and intact LittleFS recovery passed")


if __name__ == "__main__":
    active_authority()
    with tempfile.TemporaryDirectory(prefix="glyph-public-package-") as scratch:
        run_package(Path(scratch))
