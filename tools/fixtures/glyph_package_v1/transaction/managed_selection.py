"""Two complete asymmetric packages through actual CREATE, selection and reboot on LittleFS."""
import argparse
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import zlib

from run import dump_namespace, load_namespace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    corpus = args.corpus.resolve()
    generated = args.out.resolve() / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    wire = corpus / "wire"
    subprocess.run([sys.executable, "-m", "grpc_tools.protoc", f"-I{wire}", f"--python_out={generated}",
                    str(wire / "config.proto"), str(wire / "package.proto")], check=True)
    sys.path[:0] = [str(generated), str(wire), str(corpus / "proof")]
    import config_pb2 as cfg
    import package_pb2 as pkg
    from vectors import body, native
    from glyph_package_fixtures import source_root, source_control

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "UBSAN_OPTIONS": "halt_on_error=1", "ASAN_OPTIONS": "detect_leaks=0"}

    def run(*argv):
        subprocess.run([str(args.binary), *map(str, argv)], env=env, check=True)

    def wrap(raw):
        return struct.pack("<II", len(raw), zlib.crc32(raw)) + raw

    gc, xbox, switch = cfg.COMMS_BACKEND_GAMECUBE, cfg.COMMS_BACKEND_XINPUT, cfg.COMMS_BACKEND_NINTENDO_SWITCH
    source = cfg.Config(ultimate_profile_store_format=1, ultimate_profile_store_incarnation=42,
                        ultimate_profile_root_format=2, default_backend_config=1, default_usb_backend_config=2,
                        ultimate_profile_migration_receipt=bytes(32), profile_reference_digest=bytes(32))
    source.game_mode_configs.add(name="Original", mode_id=cfg.MODE_MELEE).menu_button_icon.extend([0] * 7)
    for route in [gc, xbox, switch]:
        source.communication_backend_configs.add(backend_id=route, default_mode_config=1)
    root = source_root()
    disk = {"/config-v2.bin": wrap(source.SerializeToString()), "/ultimate-v2-0.bin": root,
            "/ultimate-v2-1.bin": root, "/ultimate-v2.ctrl": source_control(root), "/keep.bin": b"unchanged"}
    seed = out / "baseline.bin"
    dump_namespace(disk, seed)
    nor = out / "baseline.nor"
    run("seed", seed, nor)
    programs = {}
    generation = 7
    for profile_id, name, plate, rank, routes in [
            (1, "Lark", cfg.LAYOUT_PLATE_FGC, 300, [gc, switch]),
            (2, "Wren", cfg.LAYOUT_PLATE_SPLIT_FGC, 1, [gc, xbox])]:
        folder = out / name
        folder.mkdir(exist_ok=True)
        package = body(rgb=False)
        package.name = package.row.name = name
        package.display_rank = rank
        package.row.layout_plate = plate
        package.row.applicable_backends.extend(routes)
        package.row.button_remapping.add(physical_button=cfg.BTN_RF1,
                                         activates=cfg.BTN_LF1 if profile_id == 1 else cfg.BTN_RF2)
        package.row.socd_pairs.add(button_dir1=cfg.BTN_LF3, button_dir2=cfg.BTN_LF1,
                                   socd_type=cfg.SOCD_NEUTRAL if profile_id == 1 else cfg.SOCD_2IP)
        program = bytearray(native(package.row, False))
        program[96:114] = bytes([64 + profile_id, 120 + profile_id]) * 9
        programs[profile_id] = package.native_body = bytes(program)
        config_body = disk["/config-v2.bin"][8:]
        request = pkg.PackageEnvelope(protocol_version=3, request_token=100 * profile_id, operation=15,
                                      expected_store_generation=generation, expected_config_generation=zlib.crc32(config_body),
                                      expected_store_incarnation=42, expected_config_sha256=hashlib.sha256(config_body).digest(),
                                      package_body=package.SerializeToString())
        (folder / "request.pb").write_bytes(request.SerializeToString())
        run("execute", nor, folder / "request.pb", folder, -1)
        response = pkg.PackageResponse.FromString((folder / "response.pb").read_bytes())
        assert response.status == 1 and response.profile_id == profile_id, response
        generation = response.store_generation
        disk = load_namespace(folder / "namespace.bin")
        nor = folder / "unwound.nor"

    preserved = dict(disk)
    saved = cfg.Config.FromString(disk["/config-v2.bin"][8:])
    for i, (route, profile_id, accepted, visible) in enumerate([
            (gc, 2, True, [2, 1]), (xbox, 1, False, [2]), (xbox, 2, True, [2]),
            (switch, 2, False, [1]), (switch, 1, True, [1]), (gc, 1, True, [2, 1]),
            (gc, 99, False, [2, 1])]):
        folder = out / f"select-{i}"
        folder.mkdir(exist_ok=True)
        run("select-profile", nor, profile_id, folder, route, int(accepted))
        targets = list(map(str.split, (folder / "targets.txt").read_text().splitlines()))
        assert [int(k) for k, _ in targets] == [0, *visible], targets
        observed = load_namespace(folder / "namespace.bin")
        if not accepted:
            assert observed == disk and (folder / "after.nor").read_bytes() == nor.read_bytes()
            continue
        idx = [gc, xbox, switch].index(route)
        saved.communication_backend_configs[idx].default_mode_config = profile_id + 1
        if route == gc:
            saved.default_backend_config = idx + 1
        else:
            saved.default_usb_backend_config = idx + 1
        assert observed["/config-v2.bin"] == wrap(saved.SerializeToString())
        assert observed["/config-v2.prev"] == disk["/config-v2.bin"]
        for path in observed.keys() | preserved.keys():
            if path not in ("/config-v2.bin", "/config-v2.prev"):
                assert observed[path] == preserved[path], path
        disk, nor = observed, folder / "after.nor"
        restart = folder / "restart"
        restart.mkdir(exist_ok=True)
        run("boot-selected-profile", nor, profile_id, restart, route, 1)
        assert (restart / "active-native.bin").read_bytes() == programs[profile_id]
        assert load_namespace(restart / "namespace.bin") == disk
    for problem, path in [("missing", next(p for p in disk if p.startswith("/ultpkg-"))) ,
                          ("corrupt", "/config-v2.bin")]:
        folder = out / problem
        folder.mkdir(exist_ok=True)
        damaged = dict(disk)
        if problem == "missing":
            del damaged[path]
        else:
            # Source-valid row changes within an owned pair break the aggregate.
            bad = cfg.Config.FromString(disk[path][8:])
            bad.game_mode_configs[1].layout_plate = cfg.LAYOUT_PLATE_EVERYTHING
            damaged[path] = wrap(bad.SerializeToString())
        dump_namespace(damaged, folder / "seed.bin")
        run("seed", folder / "seed.bin", folder / "seed.nor")
        run("select-profile", folder / "seed.nor", 1, folder, gc, 0)
        assert load_namespace(folder / "namespace.bin") == damaged
    print("PASS two independent managed packages, asymmetric contexts/programs and plates, "
          "seven per-backend selections/refusals, four fresh-process activations, "
          "exact unrelated namespace/default preservation and two damaged pairs")


if __name__ == "__main__":
    main()
