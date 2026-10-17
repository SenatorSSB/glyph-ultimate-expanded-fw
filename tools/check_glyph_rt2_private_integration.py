#!/usr/bin/env python3
"""Focused source pin/insertion/routing controls; no firmware or device action."""
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile

from rt2_private_dcd import (MARKERS, PRISTINE_RELATIVE, PINNED_SHA256,
                             patch_source, prepare, validate_patched,
                             validate_routing)

ROOT = Path(__file__).resolve().parents[1]


def rejects(call):
    try:
        call()
    except (ValueError, RuntimeError):
        return
    raise AssertionError("negative control was unexpectedly accepted")


def main():
    pristine = (ROOT / PRISTINE_RELATIVE).read_bytes()
    patched = patch_source(pristine)
    validate_patched(patched)
    assert patch_source(pristine) == patched
    # Removing ANY boundary must fail: count and exact order are contractual.
    for name in MARKERS:
        changed, count = re.subn(
            rb"^ *GlyphDcdPrivateMarker\(GLYPH_DCD_PRIVATE_" + name.encode() + rb", [^\r\n]*\);\r\n",
            b"", patched, flags=re.M)
        assert count == 1
        rejects(lambda: validate_patched(changed))
    rejects(lambda: patch_source(pristine + b" "))
    rejects(lambda: validate_patched(patched.replace(b"STATUS, status", b"STATUS, usb_hw->ints")))
    rejects(lambda: validate_patched(patched.replace(b"reset_ep0_pid();", b"/* removed */")))
    rejects(lambda: validate_patched(patched.replace(b"PRIVATE_ENTRY, 0", b"PRIVATE_ENTRY, 1")))
    rejects(lambda: validate_patched(patched.replace(b"(status & USB_INTS_SETUP_REQ_BITS) != 0", b"1")))
    entry = b"  GlyphDcdPrivateMarker(GLYPH_DCD_PRIVATE_ENTRY, 0);\r\n"
    status_read = b"  uint32_t const status = usb_hw->ints;\r\n"
    rejects(lambda: validate_patched(patched.replace(entry, b"").replace(status_read, status_read + entry)))
    rejects(lambda: validate_patched(patched.replace(b'#include "core/RecoveryPrivateDcdMarkers.h"\r\n', b"")))
    with tempfile.TemporaryDirectory(prefix="glyph-private-dcd-") as temp:
        root = Path(temp)
        copy = root / PRISTINE_RELATIVE
        copy.parent.mkdir(parents=True)
        copy.write_bytes(pristine)
        installed = root / "installed.c"
        installed.write_bytes(pristine)
        generated, actual = prepare(root, installed)
        assert actual == patched and generated.read_bytes() == patched
        installed.write_bytes(pristine + b" ")
        rejects(lambda: prepare(root, installed))
        validate_routing(installed, installed, 1)
        rejects(lambda: validate_routing(installed, installed, 0))
        rejects(lambda: validate_routing(installed, installed, 2))
        rejects(lambda: validate_routing(installed, installed, 1, True))
        rejects(lambda: validate_routing(installed, root / "unexpected.c", 1))
    # Use the real pre-script with an isolated minimal SCons-compatible graph.
    # This exercises the replacement callback itself rather than a mirror.
    class Node:
        def __init__(self, path): self.path = Path(path)
        def srcnode(self): return self
        def get_abspath(self): return str(self.path.resolve())
        def children(self): return []
        def __str__(self): return str(self.path)
    class Env(dict):
        def subst(self, text):
            return text.replace("$PROJECT_DIR", str(ROOT)).replace("$BUILD_DIR", str(ROOT / ".pio/build/glyph_mk6"))
        def ParseFlags(self, flags): return {"CPPDEFINES": [("GLYPH_STRICT_HARDENING_CANDIDATE", "1")]}
        def PioPlatform(self): return self
        def get_package_dir(self, name): return str(Path.home() / ".platformio/packages/framework-arduinopico")
        def Clone(self): return self
        def Append(self, **values):
            for key, value in values.items(): self.setdefault(key, []).extend(value)
        def Object(self, target, source=None):
            if source is None:
                if isinstance(target, Node) and target.path.suffix == ".o":
                    raise ValueError("BuildSources cannot compile a bare object File")
                return [target]
            self["routed_source"] = source
            return [Node(target)]
        def AddPreAction(self, node, action): pass
        def AddBuildMiddleware(self, callback, pattern): self["middleware"] = callback
    env = Env()
    scope = {"env": env, "Import": lambda name: None}
    exec(compile((ROOT / "builder_scripts/rt2_private_dcd.py").read_text(), "rt2_private_dcd.py", "exec"), scope)
    original_node = Node(scope["installed"])
    other_node = Node(ROOT / "src/unrelated.c")
    assert env["middleware"](env, other_node) is other_node
    replacement = env["middleware"](env, original_node)
    assert replacement is not original_node
    # Match installed PlatformIO piobuild.BuildSources exactly: only File
    # results are passed through Object; the SCons NodeList must pass through.
    build_sources_result = env.Object(replacement) if isinstance(replacement, Node) else replacement
    assert build_sources_result is replacement
    assert isinstance(replacement, list) and len(replacement) == 1
    assert "rt2-private-dcd" in replacement[0].get_abspath()
    rejects(lambda: env.Object(replacement[0]))
    assert Path(env["routed_source"]).read_bytes() == patched
    scope["require_exclusion"]([], replacement, env)
    rejects(lambda: scope["require_exclusion"]([], [], env))
    foreign_object = Node(ROOT / ".pio/build/glyph_mk6/lib123/Adafruit_TinyUSB_Arduino/dcd_rp2040.c.o")
    rejects(lambda: scope["require_exclusion"]([], replacement + [foreign_object], env))
    rejects(lambda: env["middleware"](env, original_node))
    print(json.dumps({"result": "PASS", "pristine_sha256": PINNED_SHA256,
                      "patched_sha256": sha256(patched).hexdigest(),
                      "marker_removal_negative_controls": len(MARKERS),
                      "other_negative_controls": 16,
                      "actual_middleware_substitution": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
