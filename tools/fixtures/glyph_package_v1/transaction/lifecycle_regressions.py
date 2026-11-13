"""Exercise real lifecycle publication, restart and adversarial inputs on raw LittleFS NOR."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib

from run import dump_namespace, load_namespace


def u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def wrap(data):
    return struct.pack("<II", len(data), zlib.crc32(data)) + data


def batch(requests):
    return struct.pack("<I", len(requests)) + b"".join(struct.pack("<I", len(r)) + r for r in requests)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--all-cuts", action="store_true", help="inject every observed checked operation")
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[4]
    schema = repo / "schema/haybox"
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    generated = out / "generated"
    generated.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "grpc_tools.protoc", f"-I{schema}", f"--python_out={generated}",
                    str(schema / "config.proto"), str(schema / "package.proto")], check=True)
    corpus = args.corpus.resolve()
    sys.path[:0] = [str(generated), str(corpus / "wire"), str(corpus / "proof")]
    import config_pb2 as cfg
    import package_pb2 as pb
    from glyph_package_fixtures import source_root, source_control
    from vectors import body, native

    def invoke(mode, *argv):
        env = {**os.environ, "ASAN_OPTIONS": "detect_leaks=0", "UBSAN_OPTIONS": "halt_on_error=1"}
        result = subprocess.run([str(args.binary), mode, *map(str, argv)], capture_output=True, text=True,
                                env=env, timeout=90)
        assert result.returncode == 0, (mode, argv, result.stderr)

    def roots(disk):
        return max((disk[f"/ultimate-v2-{slot}.bin"] for slot in (0, 1)), key=lambda b: u32(b, 8))

    def request(disk, operation, token, profile_id=0, revision=0, **fields):
        raw = disk["/config-v2.bin"][8:]
        return pb.PackageEnvelope(protocol_version=3 if operation == 15 else 4,
                                  request_token=token, operation=operation,
                                  expected_store_generation=u32(roots(disk), 8),
                                  expected_store_incarnation=42, expected_config_generation=zlib.crc32(raw),
                                  expected_config_sha256=hashlib.sha256(raw).digest(),
                                  target_id=profile_id, expected_revision=revision, **fields)

    def make_body(name, rgb=True):
        package = body(rgb=rgb)
        package.row.name = package.name = name
        package.row.layout_plate = cfg.LAYOUT_PLATE_SPLIT_FGC if name == "Wren" else cfg.LAYOUT_PLATE_FGC
        package.display_rank = 111 if name == "Wren" else 17
        package.row.button_remapping.add(physical_button=cfg.BTN_RF1,
                                         activates=cfg.BTN_RF2 if name == "Wren" else cfg.BTN_LF2)
        package.row.socd_pairs.add(button_dir1=cfg.BTN_LF3, button_dir2=cfg.BTN_LF1,
                                   socd_type=cfg.SOCD_2IP if name == "Wren" else cfg.SOCD_NEUTRAL)
        package.row.applicable_backends.extend([cfg.COMMS_BACKEND_GAMECUBE, cfg.COMMS_BACKEND_XINPUT])
        if rgb:
            package.rgb.default_color = 0x123456 if name == "Wren" else 0x782343
        prog = bytearray(native(package.row, False))
        prog[96:114] = bytes([80 + len(name), 120 + len(name)]) * 9
        package.native_body = bytes(prog)
        return package

    def operate(nor, req, folder, cut=-1, *, active=None):
        folder.mkdir(exist_ok=True)
        buf = req.SerializeToString(deterministic=True)
        inp = folder / "request.pb"
        inp.write_bytes(buf)
        extra = [] if active is None else [active]
        invoke("execute", nor, inp, folder, cut, *extra)
        response = pb.PackageResponse.FromString((folder / "response.pb").read_bytes())
        return response, load_namespace(folder / "namespace.bin")

    def result(status, folder):
        return pb.PackageResponse.FromString((folder / status).read_bytes())

    def query(req):
        copy = pb.PackageEnvelope.FromString(req.SerializeToString())
        copy.ClearField("request_token")
        domain = b"Glyph.Package.Create.v1\0" if req.operation == 15 else b"Glyph.Package.Lifecycle.v2\0"
        digest = hashlib.sha256(domain + copy.SerializeToString(deterministic=True)).digest()
        return pb.PackageEnvelope(protocol_version=req.protocol_version, request_token=req.request_token,
                                  operation=16, expected_store_incarnation=42, expected_digest=digest)

    def packed(body):
        return body.SerializeToString(deterministic=True)

    source = cfg.Config(ultimate_profile_store_format=1, ultimate_profile_store_incarnation=42,
                        ultimate_profile_root_format=2, default_backend_config=1, default_usb_backend_config=2,
                        ultimate_profile_migration_receipt=bytes(32), profile_reference_digest=bytes(32))
    source.game_mode_configs.add(name="Original", mode_id=cfg.MODE_MELEE).menu_button_icon.extend([0] * 7)
    for route in [cfg.COMMS_BACKEND_GAMECUBE, cfg.COMMS_BACKEND_XINPUT, cfg.COMMS_BACKEND_NINTENDO_SWITCH]:
        source.communication_backend_configs.add(backend_id=route, default_mode_config=1)
    root = source_root()
    disk = {"/config-v2.bin": wrap(packed(source)), "/ultimate-v2-0.bin": root, "/ultimate-v2-1.bin": root,
            "/ultimate-v2.ctrl": source_control(root), "/keep.bin": bytes(range(128))}
    nor = out / "seed.nor"
    dump_namespace(disk, out / "seed.bin")
    invoke("seed", out / "seed.bin", nor)
    for num, name in enumerate(("Lark", "Wren"), start=1):
        req = request(disk, 15, num*100, package_body=packed(make_body(name)))
        folder = out / f"create-{num}"
        res, disk = operate(nor, req, folder)
        assert res.status == 1 and res.profile_id == num, res
        nor = folder / "unwound.nor"

    def record_name(key, revision):
        return f"/ultpkg-{key:08x}-{revision:08x}.bin"

    key = 1
    operations = [(18, {"replacement_name": "Ibis"}), (19, {"replacement_rank": 0}),
                  (17, {"package_body": packed(make_body("Updated", False))}),
                  (17, {"package_body": packed(make_body("Updated RGB", True))}), (20, {})]
    report = []
    for n, (op, fields) in enumerate(operations, start=1):
        rev = n
        before, original = disk, nor
        req = request(disk, op, 300+n*10, key, rev, **fields)
        folder = out / f"op-{n}-{op}"
        res, disk = operate(nor, req, folder)
        assert res.status == 1 and not res.write_fenced and res.profile_revision == rev+1, (op, res)
        assert res.profile_id == key and res.transaction_operation == op and res.semantic_digest == query(req).expected_digest
        nor = folder / "unwound.nor"
        trace = json.loads((folder / "trace.json").read_text())
        assert trace and res.logical == 3 and res.storage_floor == 2
        assert disk["/config-v2.prev"] == before["/config-v2.bin"]
        after_config = cfg.Config.FromString(disk["/config-v2.bin"][8:])
        old_config = cfg.Config.FromString(before["/config-v2.bin"][8:])
        expected = cfg.Config.FromString(packed(old_config))
        expected.managed_sequence += 1
        old_row = old_config.game_mode_configs[1]
        target = expected.game_mode_configs[1]
        if op == 18:
            target.name = fields["replacement_name"]
        if op == 17:
            replacement = pb.PackageBody.FromString(fields["package_body"])
            previous_rgb = target.rgb_config
            target.name = replacement.row.name
            target.layout_plate = replacement.row.layout_plate
            target.ClearField("socd_pairs")
            target.socd_pairs.extend(replacement.row.socd_pairs)
            target.ClearField("button_remapping")
            target.button_remapping.extend(replacement.row.button_remapping)
            if replacement.HasField("rgb"):
                if previous_rgb:
                    expected.rgb_configs[previous_rgb-1].CopyFrom(replacement.rgb)
                else:
                    expected.rgb_configs.add().CopyFrom(replacement.rgb)
                    target.rgb_config = len(expected.rgb_configs)
            elif previous_rgb:
                del expected.rgb_configs[previous_rgb-1]
                target.rgb_config = 0
                for row in expected.game_mode_configs:
                    if row.rgb_config > previous_rgb:
                        row.rgb_config -= 1
        if op == 20:
            removed_rgb = target.rgb_config
            del expected.game_mode_configs[1]
            if removed_rgb:
                del expected.rgb_configs[removed_rgb-1]
                for row in expected.game_mode_configs:
                    if row.rgb_config > removed_rgb:
                        row.rgb_config -= 1
            for backend in expected.communication_backend_configs:
                if backend.default_mode_config > 2:
                    backend.default_mode_config -= 1
        assert expected == after_config, (op, expected, after_config)
        assert before["/keep.bin"] == disk["/keep.bin"]
        assert record_name(key, rev) not in disk
        assert before[record_name(2, 1)] == disk[record_name(2, 1)]
        if op != 20:
            record = disk[record_name(key, rev+1)]
            assert u32(record, 16) == rev+1 and u32(record, 116) == (op << 16 | 2)
            assert res.record_sha == hashlib.sha256(record).digest()
            actual_program = cfg.UltimateProfile.FromString(record[128:]).native_payload
            if op in (18, 19):
                assert record[128:] == before[record_name(key, rev)][128:]
            else:
                assert actual_program == replacement.native_body
        else:
            assert not any(path.startswith("/ultpkg-00000001-") for path in disk)
        replay = folder / "retry"
        replayed, replay_disk = operate(nor, req, replay)
        assert replayed.status == 1 and replayed.semantic_digest == res.semantic_digest and replay_disk == disk
        assert (replay / "unwound.nor").read_bytes() == nor.read_bytes()
        stale = pb.PackageEnvelope.FromString(packed(req))
        stale.request_token += 1
        refused, unchanged = operate(nor, stale, folder / "stale")
        assert refused.status != 1 and unchanged == disk
        denied, unchanged = operate(original, req, folder / "active-refused", active=key)
        assert denied.status != 1 and unchanged == before
        cut_counts = {}
        # Each distinct publication move and the destructive retirement, immediately
        # before and after its action. Optional exhaustive mode covers reads/writes too.
        cuts = [e for e in trace if args.all_cuts or e["operation"] in (9, 10)]
        assert len(cuts) >= 16 and any(e["operation"] == 9 for e in cuts)
        for e in cuts:
            with tempfile.TemporaryDirectory(dir=folder) as d:
                cutdir = Path(d)
                _, observed = operate(original, req, cutdir, e["index"])
                summary = json.loads((cutdir / "summary.json").read_text())
                assert summary["fault_hit"] and summary["unchanged"]
                assert result("sameboot-query.pb", cutdir).write_fenced
                restart = cutdir / "restart"
                restart.mkdir()
                q = cutdir / "queries.pb"
                q.write_bytes(batch([packed(query(req))]))
                invoke("inspect", cutdir / "cut.nor", q, restart, cutdir / "request.pb", key)
                after = result("query-0.pb", restart)
                cut_counts[(after.status, after.write_fenced)] = cut_counts.get((after.status, after.write_fenced), 0) + 1
                assert (restart / "after.nor").read_bytes() == (cutdir / "cut.nor").read_bytes()
                assert load_namespace(restart / "namespace.bin") == observed
                if not after.write_fenced:
                    assert observed == before or observed == disk, ("silently valid partial state", e)
                if after.status == 1:
                    assert observed == disk and after.semantic_digest == res.semantic_digest
        report.append({"operation": op, "revision":rev+1, "trace_events":len(trace),
                       "cuts":len(cuts), "restart_results":{str(k):v for k,v in cut_counts.items()}})
        (out / "results.json").write_text(json.dumps(report, indent=2))
        print(f"PASS operation {op} revision {rev+1}, {len(cuts)} cut/restart cases", flush=True)
    # A CREATE after compaction proves old slots/records don't consume current capacity.
    fresh = request(disk, 15, 1000, package_body=packed(make_body("New")))
    res, disk = operate(nor, fresh, out / "create-after-delete")
    assert res.status == 1 and res.profile_id == 3
    print("PASS guarded lifecycle and create after reclaim on production LittleFS")


if __name__ == "__main__":
    main()
