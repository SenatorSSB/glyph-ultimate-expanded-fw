"""Strict Mk6 diagnostic: replace, never mutate, the exact pinned framework TU."""
import json
from pathlib import Path
import shlex
import sys

Import("env")
root = Path(env.subst("$PROJECT_DIR"))
sys.path.insert(0, str(root / "tools"))
from rt2_private_dcd import (INSTALLED_RELATIVE, PINNED_SHA256, prepare,
                             validate_routing)

defines = env.ParseFlags(env.get("BUILD_FLAGS", [])).get("CPPDEFINES", [])
strict = any(isinstance(item, (tuple, list)) and item[0] == "GLYPH_STRICT_HARDENING_CANDIDATE"
             and str(item[1]) == "1" for item in defines)
if strict:
    framework = Path(env.PioPlatform().get_package_dir("framework-arduinopico"))
    installed = framework / INSTALLED_RELATIVE
    generated, patched = prepare(root, installed)
    state = {"replacements": 0}
    object_path = (root / env.subst("$BUILD_DIR") / "rt2-private-dcd/dcd_rp2040.c.o").resolve()
    receipt_path = object_path.parent / "compile-command.json"

    def record_compile(target, source, env):
        from hashlib import sha256
        command = env.subst("$CCCOM", target=target, source=source)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps({
            "installed_source": str(installed), "installed_sha256": PINNED_SHA256,
            "pristine_sha256": PINNED_SHA256,
            "patched_source": str(generated), "patched_sha256": sha256(patched).hexdigest(),
            "object": str(object_path), "directory": str(root),
            "arguments": shlex.split(command)}, indent=2) + "\n")

    def substitute_dcd(build_env, node):
        candidate = Path(node.srcnode().get_abspath()).resolve()
        if candidate != installed.resolve():
            return node
        state["replacements"] += 1
        if state["replacements"] != 1:
            raise RuntimeError("duplicate framework DCD source routing")
        private_env = build_env.Clone()
        private_env.Append(CPPPATH=[str(installed.parent)])
        # Return SCons' NodeList, not its File element. PlatformIO BuildSources
        # passes non-File middleware results through; a bare .o File would be
        # incorrectly fed back to env.Object as though it were C input.
        replacement = private_env.Object(target=str(object_path), source=str(generated))
        private_env.AddPreAction(replacement, record_compile)
        return replacement

    def require_exclusion(target, source, env):
        # Validate on every link, including incremental links. All source routing
        # happens while SCons constructs the graph, before this pre-action runs.
        pending = list(source)
        visited = set()
        linked_objects = set()
        while pending:
            node = pending.pop()
            identity = str(node)
            if identity in visited:
                continue
            visited.add(identity)
            if Path(identity).name in ("dcd_rp2040.o", "dcd_rp2040.c.o"):
                linked_objects.add(Path(node.get_abspath()).resolve())
            pending.extend(node.children())
        validate_routing(installed, framework / INSTALLED_RELATIVE, state["replacements"],
                         linked_objects != {object_path})
        verify_source, current_patch = prepare(root, installed)
        if current_patch != patched:
            raise RuntimeError("private DCD source changed during build")

    env.AddBuildMiddleware(substitute_dcd, "*dcd_rp2040.c")
    env.AddPreAction("$BUILD_DIR/${PROGNAME}.elf", require_exclusion)
    env.Append(LINKFLAGS=["-Wl,-Map," + env.subst("$BUILD_DIR/firmware.map")])
