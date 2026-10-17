#!/usr/bin/env python3
"""Focused source pin/insertion/routing controls; no firmware or device action."""
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile

from rt2_private_dcd_assembly import entry_status_audit, compile_receipt

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
    source_negatives = {
        "S0_hook_removed": patched.replace(b"  GlyphDcdPrivateStatus(status);\r\n", b""),
        "S1_hook_removed": patched.replace(b"  GlyphDcdPrivateReturn(status, late_status);\r\n", b""),
        "S1_read_removed": patched.replace(b"  uint32_t const late_status = usb_hw->ints;\r\n", b""),
        "S0_marker_reread": patched.replace(b"GlyphDcdPrivateStatus(status)", b"GlyphDcdPrivateStatus(usb_hw->ints)"),
        "S1_marker_reread": patched.replace(b"GlyphDcdPrivateReturn(status, late_status)", b"GlyphDcdPrivateReturn(status, usb_hw->ints)"),
        "S0_replaced_by_late": patched.replace(b"GlyphDcdPrivateReturn(status, late_status)", b"GlyphDcdPrivateReturn(late_status, late_status)"),
        "PID_removed": patched.replace(b"reset_ep0_pid();", b"/* removed */"),
        "S1_changes_USB_branch": patched.replace(b"  GlyphDcdPrivateReturn", b"  if (late_status & USB_INTS_SETUP_REQ_BITS) usb_hw_clear->sie_status = USB_SIE_STATUS_SETUP_REC_BITS;\r\n  GlyphDcdPrivateReturn"),
        "SETUP_clear_added": patched.replace(b"  GlyphDcdPrivateReturn", b"  usb_hw_clear->sie_status = USB_SIE_STATUS_SETUP_REC_BITS;\r\n  GlyphDcdPrivateReturn"),
        "forced_IRQ": patched.replace(b"  GlyphDcdPrivateReturn", b"  irq_set_pending(USBCTRL_IRQ);\r\n  GlyphDcdPrivateReturn"),
        "retry_added": patched.replace(b"  GlyphDcdPrivateReturn", b"  dcd_rp2040_irq();\r\n  GlyphDcdPrivateReturn"),
        "branch_order_changed": patched.replace(b"    hw_handle_buff_status();", b"    dcd_event_sof(0, 0, true);\r\n    hw_handle_buff_status();"),
    }
    for changed in source_negatives.values():rejects(lambda changed=changed: validate_patched(changed))
    rejects(lambda: patch_source(pristine + b" "))
    status_read = b"  uint32_t const status = usb_hw->ints;\r\n"
    status_marker = b"  GlyphDcdPrivateStatus(status);\r\n"
    pre_read_negatives = {
        "diagnostic_statement": b"  diagnostic_count++;\r\n",
        "DMB": b"  __asm volatile(\"dmb\" ::: \"memory\");\r\n",
        "helper_call": b"  diagnostic_helper();\r\n",
        "atomic_store": b"  __atomic_store_n(&diagnostic_count, 1, __ATOMIC_RELAXED);\r\n",
        "extra_pre_S0_INTS_read": b"  uint32_t extra = usb_hw->ints;\r\n",
    }
    for statement in pre_read_negatives.values():
        rejects(lambda statement=statement: validate_patched(patched.replace(status_read, statement + status_read)))
    rejects(lambda: validate_patched(patched.replace(status_read + status_marker, status_marker + status_read)))
    # Registration must deliver the original callback directly; an unarmed
    # Enabled() load in a per-IRQ trampoline would already violate the boundary.
    usb = (ROOT / "HAL/pico/src/core/RecoveryUsbDiagnostics.cpp").read_text()
    assert "observed_dcd_irq" not in usb
    registration = usb[usb.index('extern "C" void __wrap_irq_add_shared_handler'):usb.index('extern "C" void __real_dcd_event_handler')]
    assert "__real_irq_add_shared_handler(irq,handler,priority);return;" in registration
    assert "registered_dcd_handler=handler;setup_observer.Registered();" in registration
    assert "pre_setup_observer.IrqEnter(" not in usb and "pre_setup_observer.IrqReturn(" not in usb
    assert "setup_observer.IrqEnter(" not in usb and "setup_observer.IrqReturn(" not in usb
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
    # Synthetic disassembly controls exercise the assembly hard gate itself;
    # actual build disassembly/replay remains required for hardware handoff.
    assembly = """00000000 <dcd_rp2040_irq>:
   0: 2398 movs r3, #152
   2: 4a0f ldr r2, [pc, #60] @ (40 <dcd_rp2040_irq+0x40>)
   4: b510 push {r4, lr}
   6: 58d3 ldr r3, [r2, r3]
   8: 001c movs r4, r3
   a: 0018 movs r0, r3
   c: f7ff fffe bl 0 <GlyphDcdPrivateStatus>
             c: R_ARM_THM_CALL GlyphDcdPrivateStatus
  10: 2398 movs r3, #152
  12: 4a0b ldr r2, [pc, #44] @ (40 <dcd_rp2040_irq+0x40>)
  14: 58d1 ldr r1, [r2, r3]
  16: 0020 movs r0, r4
  18: f7ff fffe bl 0 <GlyphDcdPrivateReturn>
            18: R_ARM_THM_CALL GlyphDcdPrivateReturn
  40: 50110000 .word 0x50110000
"""
    assert entry_status_audit(assembly)["diagnostic_instructions_before_status"] == 0
    def assembly_rejects(changed):
        try:entry_status_audit(changed)
        except AssertionError:return
        raise AssertionError("assembly negative control was unexpectedly accepted")
    assembly_negatives = {
        "DMB": "   5: f3bf 8f5f dmb sy\n",
        "helper_call": "   5: f7ff fffe bl 0 <diagnostic_helper>\n",
        "store": "   5: 6018 str r0, [r3, #0]\n",
        "atomic_store": "   5: f7ff fffe bl 0 <__atomic_store_4>\n",
        "observer_load": "   5: 6818 ldr r0, [r3, #0]\n",
        "argument_preparation": "   5: 2001 movs r0, #1\n",
        "H0_reinsertion": "   5: f7ff fffe bl 0 <GlyphDcdPrivateMarker>\n",
    }
    for insertion in assembly_negatives.values():assembly_rejects(assembly.replace("   6:", insertion + "   6:"))
    assembly_rejects(assembly.replace("   8:", "   7: 2398 movs r3, #152\n   7: 58d3 ldr r3, [r2, r3]\n   8:"))
    assembly_rejects(assembly.replace("movs r0, r3", "movs r0, #0"))
    assembly_rejects(assembly.replace("movs r0, r4", "movs r0, #0"))
    assembly_rejects(assembly.replace("14: 58d1 ldr r1, [r2, r3]", "14: 2100 movs r1, #0"))
    assembly_rejects(assembly.replace("GlyphDcdPrivateReturn", "other_return"))
    # Optimizer equality is accepted only when the original panic guard
    # dominates the entire normal-return block. Arbitrary CMP is insufficient.
    equality_assembly=assembly[:assembly.index("  10:")]+"""  10: 42a5 cmp r5, r4
  12: d000 beq.n 16 <dcd_rp2040_irq+0x16>
  14: e00c b.n 30 <dcd_rp2040_irq+0x30>
  16: 2398 movs r3, #152
  18: 4a09 ldr r2, [pc, #36] @ (40 <dcd_rp2040_irq+0x40>)
  1a: 0028 movs r0, r5
  1c: 58d1 ldr r1, [r2, r3]
  1e: f7ff fffe bl 0 <GlyphDcdPrivateReturn>
            1e: R_ARM_THM_CALL GlyphDcdPrivateReturn
  22: bd10 pop {r4, pc}
  30: f7ff fffe bl 0 <panic>
            30: R_ARM_THM_CALL panic
  40: 50110000 .word 0x50110000
"""
    assert entry_status_audit(equality_assembly)["normal_return_status_equality_proof"]
    assembly_rejects(equality_assembly.replace('beq.n 16','bne.n 16'))
    assembly_rejects(equality_assembly.replace('30: R_ARM_THM_CALL panic','30: R_ARM_THM_CALL ordinary_return').replace('<panic>','<ordinary_return>'))
    assembly_rejects(equality_assembly.replace('  10:','   f: e000 b.n 16 <dcd_rp2040_irq+0x16>\n  10:'))
    assembly_rejects(equality_assembly.replace('  10:','   f: e000 b.n 12 <dcd_rp2040_irq+0x12>\n  10:'))
    with tempfile.TemporaryDirectory(prefix="glyph-private-compiledb-") as temp:
        root = Path(temp)
        private_source = root / ".pio/rt2-private-dcd/dcd_rp2040.c"
        private_source.parent.mkdir(parents=True)
        private_source.write_bytes(patched)
        database = root / "compile_commands.json"
        entry = {"directory": str(root), "file": str(private_source),
                 "arguments": ["arm-none-eabi-gcc", "-o", str(root / ".pio/build/glyph_mk6/rt2-private-dcd/dcd_rp2040.c.o"), "-c", str(private_source)]}
        database.write_text(json.dumps([entry]))
        receipt = compile_receipt(root, root / ".pio/build/glyph_mk6", database)
        assert receipt["provenance"]["kind"] == "actual_compile_database_replay"
        assert receipt["arguments"] == entry["arguments"]
        assert receipt["patched_sha256"] == sha256(patched).hexdigest()
        def receipt_rejects(db):
            try:
                compile_receipt(root, root / ".pio/build/glyph_mk6", db)
            except AssertionError:
                return
            raise AssertionError("compile-database negative control was unexpectedly accepted")
        receipt_rejects(None)
        database.write_text(json.dumps([entry, entry]))
        receipt_rejects(database)
        database.write_text(json.dumps([{**entry, "file": str(root / "unrelated.c")}]))
        receipt_rejects(database)
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
                      "hook_removal_negative_controls": len(MARKERS),
                      "source_negative_controls": list(source_negatives),
                      "pre_status_negative_controls": list(pre_read_negatives),
                      "direct_original_handler_registration": "PASS",
                      "source_and_placement_negative_controls": len(source_negatives)+len(pre_read_negatives)+3,
                      "assembly_negative_controls": len(assembly_negatives) + 9,
                      "compile_database_negative_controls": 3,
                      "actual_middleware_substitution": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
