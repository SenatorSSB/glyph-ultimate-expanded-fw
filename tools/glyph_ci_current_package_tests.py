"""Offline public source, lineage, package storage, and WebSerial authority regressions."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
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
from storage_fence_regressions import response as decode_status


DEVICE_PATH_MARKERS = ("rpi-rp2", "bootsel", "picoboot", "rp2040", "/dev/", "physicaldrive")
COPY_CALLS = {"shutil.copy", "shutil.copy2", "shutil.copyfile", "shutil.copytree",
              "copy.copy", "copy.copy2", "copy.copyfile", "copy.copytree"}
PROCESS_CALLS = {"subprocess.run", "subprocess.call", "subprocess.check_call",
                 "subprocess.check_output", "os.system", "os.popen"}


def _dotted_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return base + "." + node.attr if base else node.attr
    return ""


def _literal_text(node, names):
    """Return statically visible path/command text without guessing runtime values."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return names.get(node.id, "")
    if isinstance(node, (ast.List, ast.Tuple)):
        return " ".join(filter(None, (_literal_text(item, names) for item in node.elts)))
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Div)):
        return _literal_text(node.left, names) + _literal_text(node.right, names)
    if isinstance(node, ast.Call) and _dotted_name(node.func) in {"str", "Path"} and node.args:
        return _literal_text(node.args[0], names)
    return ""


def _is_device_path(text):
    lowered = text.lower()
    return any(marker in lowered for marker in DEVICE_PATH_MARKERS)


def _is_flash_command(command):
    lowered = command.lower()
    tokens = re.split(r"\s+", lowered)
    return (
        "picotool" in tokens
        or "openocd" in tokens
        or ("pio" in tokens or "platformio" in tokens) and "run" in tokens and "upload" in tokens
        or "uf2" in tokens and "write" in tokens
        or "dd" in tokens and ("of=/dev/" in lowered or "of=/dev" in lowered)
    )


def current_flashing_automation_reasons(relpath, source):
    """Classify executable flashing actions, not ordinary host fixture copying.

    Generic copy APIs are rejected only when their statically visible source or
    destination identifies a bootloader/device path.  Python string literals on
    their own are deliberately not actions: this keeps regression fixtures and
    documentation from becoming evidence of a host-initiated device mutation.
    """
    suffix = Path(relpath).suffix.lower()
    if suffix == ".py":
        try:
            tree = ast.parse(source, filename=relpath)
        except SyntaxError as error:
            return [f"unparseable Python source: {error.msg}"]
        names = {}
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for imported in node.names:
                    if imported.asname:
                        aliases[imported.asname] = imported.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                for imported in node.names:
                    aliases[imported.asname or imported.name] = node.module + "." + imported.name
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = _literal_text(node.value, names)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and value:
                        names[target.id] = value
        reasons = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _dotted_name(node.func)
            if "." in name:
                prefix, remainder = name.split(".", 1)
                name = aliases.get(prefix, prefix) + "." + remainder
            else:
                name = aliases.get(name, name)
            arguments = " ".join(_literal_text(arg, names) for arg in node.args)
            if name in COPY_CALLS and _is_device_path(arguments):
                reasons.append(f"device-context copy at line {node.lineno}")
            elif name in PROCESS_CALLS and _is_flash_command(arguments):
                reasons.append(f"flashing command at line {node.lineno}")
            elif (isinstance(node.func, ast.Attribute) and node.func.attr in {"write_bytes", "write_text"}) or name == "open":
                target = _literal_text(node.func.value, names) if isinstance(node.func, ast.Attribute) else arguments
                rendered = target + " " + arguments
                if _is_device_path(rendered) and ".uf2" in rendered.lower():
                    reasons.append(f"UF2 device write at line {node.lineno}")
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(target, ast.Name) and target.id in {"upload_port", "upload_protocol"}
                       for target in targets):
                    reasons.append(f"automated upload configuration at line {node.lineno}")
        return reasons
    if suffix in {".sh", ".bash", ".zsh", ".ini", ".cfg", ".mk", ".make"} or Path(relpath).name == "Makefile":
        lowered = source.lower()
        patterns = (
            r"\b(?:pio|platformio)\s+run\b[^\n]*(?:-t|--target)\s*upload\b",
            r"^\s*upload_(?:port|protocol)\s*=",
            r"\b(?:picotool|openocd)\b",
            r"\bdd\b[^\n]*\bof=/dev/",
            r"\buf2\s+write\b",
        )
        return ["flashing command or upload configuration"] if any(
            re.search(pattern, lowered, flags=re.MULTILINE) for pattern in patterns) else []
    return []


def ensure_no_current_flashing_automation(changed):
    findings = []
    for relpath in changed:
        path = ROOT / relpath
        if path.is_file():
            for reason in current_flashing_automation_reasons(relpath, path.read_text(encoding="utf-8", errors="ignore")):
                findings.append(f"{relpath}: {reason}")
    if findings:
        raise ValueError("current flashing automation found in changed source: " + "; ".join(findings))


def verify_current_flashing_automation_controls():
    """Focused positive/negative controls for the current semantic guard."""
    allowed = (
        'import shutil\nshutil.copytree("fixtures", scratch / "fixture")\n',
        'import shutil\nshutil.copy("fixture.json", scratch / "fixture.json")\n',
        'import shutil\nshutil.copy("request.pb", scratch / "request.pb")\n',
        # Removing the RPI-RP2 destination makes this an ordinary host copy.
        'import shutil\nshutil.copy("firmware.uf2", scratch / "firmware.uf2")\n',
    )
    forbidden = (
        'import shutil\nshutil.copy("firmware.uf2", "/Volumes/RPI-RP2/firmware.uf2")\n',
        'import shutil\ntarget = "/Volumes/RPI-RP2"\nshutil.copy("firmware.uf2", target)\n',
        'import subprocess\nsubprocess.run(["pio", "run", "-t", "upload"], check=True)\n',
        'import subprocess\nsubprocess.run(["picotool", "load", "firmware.uf2"], check=True)\n',
        'import subprocess\nsubprocess.run(["openocd", "-f", "flash.cfg"], check=True)\n',
        'from pathlib import Path\nPath("/Volumes/RPI-RP2/firmware.uf2").write_bytes(image)\n',
        'upload_port = "/dev/ttyACM0"\n',
        'upload_protocol = "picotool"\n',
    )
    assert all(not current_flashing_automation_reasons("host_fixture.py", source) for source in allowed)
    assert all(current_flashing_automation_reasons("host_tool.py", source) for source in forbidden)
    assert current_flashing_automation_reasons("platformio.ini", "upload_port = /dev/ttyACM0\n")
    assert current_flashing_automation_reasons("flash.sh", "dd if=firmware.uf2 of=/dev/sdb\n")
    print("Current flashing-automation semantic guard controls passed")


def active_authority():
    docs.validate_docs()
    text = authority.read_required(authority.DOC)
    authority.require_phrases(text)
    authority.ensure_flag_false(text)
    authority.ensure_no_positive_claims(text)
    authority.ensure_no_runtime_write_symbols_added()
    verify_current_flashing_automation_controls()
    changed = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", "-z",
                                       PACKAGE_BASE, "HEAD"], cwd=ROOT)
    ensure_no_current_flashing_automation([path.decode() for path in changed.split(b"\0") if path])


def offline_source_tools():
    import check_glyph_generated_source_owned_generator_contract as generator
    import check_glyph_generated_source_owned_baseline_artifact as baseline
    import check_glyph_generated_source_owned_artifact_install as installer
    generator.validate_generator_behavior(generator.load_json_object(generator.INPUT_FIXTURE),
                                         generator.load_json_object(generator.LAYOUT_SPEC_EXAMPLE))
    baseline.validate_deterministic_generation()
    baseline.validate_equivalence()
    installer.validate_bridge_install_workflow(installer.validate_fixture(installer.load_json_object(installer.FIXTURE)))
    script = ROOT / "tools/check_glyph_coordinate_native_runtime_profile_contract.py"
    for option in ("--check-negative-fixtures", "--check-offline-pipeline", "--check-offline-export-package"):
        subprocess.run([sys.executable, str(script), option], cwd=ROOT, check=True)


def current_messages(temp):
    schema = ROOT / "schema/haybox"
    subprocess.run([sys.executable, "-m", "grpc_tools.protoc", "-I" + str(schema),
                    "--python_out=" + str(temp), str(schema / "config.proto"),
                    str(schema / "package.proto")], check=True)
    sys.path.insert(0, str(temp))
    import package_pb2 as package
    import config_pb2 as cfg
    return package, cfg



def positive_create(temp, invoke, messages):
    package, cfg = messages
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
    messages = current_messages(temp)
    package, cfg = messages
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
        boot_result = json.loads((boot / "boot.json").read_text())
        assert boot_result["outcome"] == 6 and boot_result["recovery_visible"]
        assert boot_result["backend_initializations"] == 0 and boot_result["unchanged"]
        status = decode_status((boot / "status.cobs").read_bytes(), cfg.ProfileStoreResponse)
        assert status.status == cfg.PROFILE_STORE_IO_FAILURE and status.recovery_flags, status
    positive_create(temp, invoke, messages)
    print("Current package wire, historical Config fault injection, startup/STATUS and intact LittleFS recovery passed")


if __name__ == "__main__":
    active_authority()
    offline_source_tools()
    with tempfile.TemporaryDirectory(prefix="glyph-public-package-") as scratch:
        run_package(Path(scratch))
