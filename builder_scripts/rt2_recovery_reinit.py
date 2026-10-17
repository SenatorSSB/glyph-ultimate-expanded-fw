"""Strict Mk6 recovery-only lifecycle seams; replaces old private-DCD routing."""
from hashlib import sha256
import json
from pathlib import Path
import shlex
import sys

Import("env")
root = Path(env.subst("$PROJECT_DIR"))
sys.path.insert(0, str(root / "tools"))
from rt2_recovery_reinit import PINS, prepare, validate_routing

defines = env.ParseFlags(env.get("BUILD_FLAGS", [])).get("CPPDEFINES", [])
strict = any(isinstance(item, (tuple, list)) and item[0] == "GLYPH_STRICT_HARDENING_CANDIDATE"
             and str(item[1]) == "1" for item in defines)
if strict and env.subst("$PIOENV") == "glyph_mk6":
    framework = Path(env.PioPlatform().get_package_dir("framework-arduinopico"))
    records = prepare(root, framework)
    counts = {key: 0 for key in PINS}
    for key, record in records.items():
        record["object"] = str((root / env.subst("$BUILD_DIR") /
            "rt2-recovery-reinit" / (Path(record["installed"]).name + ".o")).resolve())

    def substitute(build_env, node):
        source_path = Path(node.srcnode().get_abspath()).resolve()
        for key, record in records.items():
            installed = (framework / record["installed"]).resolve()
            if source_path != installed:
                continue
            counts[key] += 1
            if counts[key] != 1:
                raise RuntimeError("duplicate recovery source routing: " + key)
            private_env = build_env.Clone()
            private_env.Append(CPPPATH=[str(installed.parent)])
            replacement = private_env.Object(target=record["object"], source=record["generated"])

            def record_compile(target, source, env, key=key, record=record):
                command_name = "$CXXCOM" if Path(record["generated"]).suffix == ".cpp" else "$CCCOM"
                command = env.subst(command_name, target=target, source=source)
                receipt = Path(record["object"]).parent / (key + "-compile-command.json")
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_text(json.dumps(dict(record, directory=str(root),
                    arguments=shlex.split(command)), indent=2) + "\n")
            private_env.AddPreAction(replacement, record_compile)
            return replacement
        return node

    def require_exclusion(target, source, env):
        linked = {key: set() for key in PINS}
        pending, visited = list(source), set()
        while pending:
            node = pending.pop()
            identity = str(node)
            if identity in visited:
                continue
            visited.add(identity)
            path = Path(node.get_abspath()).resolve()
            for key, record in records.items():
                name = Path(record["installed"]).name
                if path.name in (name + ".o", Path(name).stem + ".o"):
                    linked[key].add(str(path))
            pending.extend(node.children())
        validate_routing(records, counts, linked)
        now = prepare(root, framework)
        for key in records:
            if now[key]["generated_sha256"] != records[key]["generated_sha256"]:
                raise RuntimeError("recovery source changed during build: " + key)
        receipt = Path(records["dcd"]["object"]).parent / "routing.json"
        receipt.write_text(json.dumps(dict(records=records, replacements=counts,
            linked={key: sorted(value) for key, value in linked.items()}), indent=2) + "\n")

    env.AddBuildMiddleware(substitute, "*dcd_rp2040.c")
    env.AddBuildMiddleware(substitute, "*usbd.c")
    env.AddBuildMiddleware(substitute, "*Adafruit_TinyUSB_rp2040.cpp")
    env.AddPreAction("$BUILD_DIR/${PROGNAME}.elf", require_exclusion)
    env.Append(LINKFLAGS=["-Wl,-Map," + env.subst("$BUILD_DIR/firmware.map")])
