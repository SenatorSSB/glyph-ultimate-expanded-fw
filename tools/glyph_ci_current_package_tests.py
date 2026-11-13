"""Offline public source, lineage, package storage, and WebSerial authority regressions."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib

from check_glyph_profile_native_ultimate import program

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


def positive_create(temp, invoke):
    schema = ROOT / "schema/haybox"
    subprocess.run([sys.executable, "-m", "grpc_tools.protoc", "-I" + str(schema),
                    "--python_out=" + str(temp), str(schema / "config.proto"),
                    str(schema / "package.proto")], check=True)
    sys.path.insert(0, str(temp))
    import package_pb2 as package
    import config_pb2 as cfg

    incarnation = 42
    revision = 1
    config = cfg.Config(ultimate_profile_root_format=2, ultimate_profile_store_format=1,
                        ultimate_profile_store_incarnation=incarnation, default_usb_backend_config=1)
    config.communication_backend_configs.add(backend_id=cfg.COMMS_BACKEND_XINPUT)
    config.profile_reference_digest = bytes(32)
    config.ultimate_profile_migration_receipt = bytes(32)
    raw = config.SerializeToString(deterministic=True)
    crc = zlib.crc32(raw)
    root = bytearray(3904)
    struct.pack_into("<4sHHII", root, 0, b"PDS2", 2, 0, revision, incarnation)
    root = bytes(root) + struct.pack("<I", zlib.crc32(root))
    control = struct.pack("<4sII", b"PSC2", 2, len(root))
    control += struct.pack("<I", zlib.crc32(control) ^ zlib.crc32(root)) + root
    files = {"/config-v2.bin": struct.pack("<II", len(raw), crc) + raw,
             "/ultimate-v2-0.bin": root, "/ultimate-v2-1.bin": root,
             "/ultimate-v2.ctrl": control, "/keep.bin": b"independent public sentinel"}
    baseline = temp / "healthy"
    baseline.mkdir()
    dump_namespace(files, baseline / "files")
    invoke("seed", baseline / "files", baseline / "seed.nor")
    invoke("migration-diagnostic", baseline / "seed.nor", -1, baseline)
    classification = json.loads((baseline / "classification.json").read_text())
    assert not classification["write_fenced"], classification
    context = cfg.GameModeConfig(mode_id=cfg.MODE_ULTIMATE)
    body = package.PackageBody(version=1, name="Public Test", display_rank=4)
    body.row.name = body.name
    body.row.layout_plate = cfg.LAYOUT_PLATE_FGC
    body.native_body = program(cfg, context, []).native_payload
    create = package.PackageEnvelope(protocol_version=3, operation=package.CREATE_PACKAGE, request_token=17,
        expected_store_incarnation=incarnation, expected_store_generation=revision, expected_config_generation=crc,
        expected_config_sha256=hashlib.sha256(raw).digest(), package_body=body.SerializeToString(deterministic=True))
    request = baseline / "create.pb"
    request.write_bytes(create.SerializeToString(deterministic=True))
    invoke("execute", baseline / "seed.nor", request, baseline, -1)
    result = package.PackageResponse.FromString((baseline / "response.pb").read_bytes())
    assert result.status == cfg.PROFILE_STORE_OK and result.logical == package.COMMITTED, result
    assert result.profile_id == 1 and result.row_index == 0 and result.profile_revision == 1
    observed = load_namespace(baseline / "namespace.bin")
    assert observed["/keep.bin"] == files["/keep.bin"]
    stored = cfg.Config.FromString(observed["/config-v2.bin"][8:])
    assert len(stored.game_mode_configs) == 1 and stored.game_mode_configs[0].layout_plate == cfg.LAYOUT_PLATE_FGC
    assert list(stored.communication_backend_configs) == list(config.communication_backend_configs)
    # Reuse exactly the admitted request against a fresh mount. Its token and
    # semantic digest must resolve the original record with no new write.
    duplicate = baseline / "duplicate"
    duplicate.mkdir()
    invoke("execute", baseline / "unwound.nor", request, duplicate, -1)
    replay = package.PackageResponse.FromString((duplicate / "response.pb").read_bytes())
    assert replay.profile_id == result.profile_id and replay.logical == package.COMMITTED
    assert replay.semantic_digest == result.semantic_digest
    assert (duplicate / "unwound.nor").read_bytes() == (baseline / "unwound.nor").read_bytes()
    events = json.loads((baseline / "trace.json").read_text())
    assert len(events) >= 3
    for cut in [events[0], events[len(events)//2], events[-1]]:
        interrupted = temp / ("cut-" + str(cut["index"]))
        interrupted.mkdir()
        invoke("execute", baseline / "seed.nor", request, interrupted, cut["index"])
        info = json.loads((interrupted / "summary.json").read_text())
        assert info["fault_hit"] and info["unchanged"]
        assert (interrupted / "cut.nor").read_bytes() == (interrupted / "unwound.nor").read_bytes()
        query = package.PackageEnvelope(protocol_version=3, request_token=17, operation=package.QUERY_PACKAGE,
            expected_store_incarnation=incarnation, expected_digest=result.semantic_digest)
        wire = query.SerializeToString(deterministic=True)
        (interrupted / "queries").write_bytes(struct.pack("<II", 1, len(wire)) + wire)
        invoke("inspect", interrupted / "cut.nor", interrupted / "queries", interrupted)
        query_result = package.PackageResponse.FromString((interrupted / "query-0.pb").read_bytes())
        assert query_result.request_token == create.request_token
        if query_result.logical == package.COMMITTED:
            assert query_result.profile_id == result.profile_id and query_result.semantic_digest == result.semantic_digest
        elif query_result.logical in (package.UNRESOLVED, package.INCOMPLETE):
            assert query_result.write_fenced
        else:
            assert query_result.logical in (package.LOGICAL_NONE, package.PROVEN_ABORTED), query_result
        assert (interrupted / "after.nor").read_bytes() == (interrupted / "cut.nor").read_bytes()
        assert load_namespace(interrupted / "namespace.bin")["/keep.bin"] == files["/keep.bin"]
    print("Public synthetic CREATE and three actual publication cuts passed with byte-exact read-only restart")


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
    positive_create(temp, invoke)
    print("Current package wire, historical Config fault injection, startup/STATUS and intact LittleFS recovery passed")


if __name__ == "__main__":
    active_authority()
    with tempfile.TemporaryDirectory(prefix="glyph-public-package-") as scratch:
        run_package(Path(scratch))
