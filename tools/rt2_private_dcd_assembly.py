#!/usr/bin/env python3
"""Capture frozen/patched actual-flag assembly and enforce final DCD uniqueness.

This replays only the private DCD object and compiles a pristine comparison
object, never firmware or device inputs.
The emitted disassembly still requires independent structural review; the JSON
does not promote instruction listings into a completed human assembly review.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import shlex

from rt2_private_dcd import (INSTALLED_RELATIVE, GENERATED_RELATIVE, PINNED_SHA256,
                             PRISTINE_RELATIVE, validate_patched, verify_pin)


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def parse_function(disassembly, name="dcd_rp2040_irq"):
    """Read objdump -dr instructions and relocations, retaining literal words."""
    match = re.search(r"^[0-9a-f]+ <" + re.escape(name) + r">:\n", disassembly, re.M)
    assert match, f"missing assembly function {name}"
    body = disassembly[match.end():]
    end = re.search(r"^[0-9a-f]+ <[^>]+>:\n", body, re.M)
    if end:
        body = body[:end.start()]
    instructions, literals, relocations = [], {}, {}
    for line in body.splitlines():
        relocated = re.match(r"\s*([0-9a-f]+):\s+R_ARM_\w+\s+(.+)", line)
        if relocated:
            relocations[int(relocated[1], 16)] = relocated[2]
            continue
        item = re.match(r"\s*([0-9a-f]+):\s+([0-9a-f]{4,8}(?: [0-9a-f]{4})?)\s+([.\w]+)\s*(.*)", line)
        if not item:
            continue
        address, opcode, operands = int(item[1], 16), item[3], item[4]
        if opcode == ".word":
            literals[address] = int(operands, 16)
        elif not opcode.startswith("."):
            instructions.append({"address": address, "opcode": opcode,
                                 "operands": operands, "text": line.strip()})
    return instructions, literals, relocations


def entry_status_audit(disassembly, require_marker=True):
    """Fail closed on observer work before INTS and trace the exact first value.

    The accepted pre-load vocabulary is only compiler register/stack prologue
    plus the actual address calculation. Every other instruction is rejected.
    Later source structure is additionally bound by validate_patched and replay.
    """
    instructions, literals, relocations = parse_function(disassembly)
    registers, dependencies, prefix, loads = {}, {}, [], []
    first_marker = None
    # Literal/address propagation follows the actual instruction stream. The
    # exact insertion-only source gate separately forbids any hidden reread.
    for ins in instructions:
        addr, op = ins["address"], ins["opcode"].split(".")[0]
        raw = ins["operands"]
        args = raw.split("@", 1)[0].strip()
        parts = [part.strip() for part in args.split(",")]
        destination = parts[0] if parts else ""
        if not loads:
            prefix.append(ins)
        if op in ("bl", "blx"):
            target = relocations.get(addr, raw)
            if ("GlyphDcdPrivateStatus" in target or "GlyphDcdPrivateMarker" in target) and first_marker is None:
                assert loads, "diagnostic call precedes private INTS load"
                assert "GlyphDcdPrivateStatus" in target, "first diagnostic is not dedicated STATUS publication"
                assert registers.get("r0") == "local_status", "STATUS argument is not exact loaded local value"
                first_marker = ins
            for reg in ("r0", "r1", "r2", "r3", "ip", "lr"):
                registers.pop(reg, None)
                dependencies.pop(reg, None)
            continue
        if op in ("mov", "movs") and len(parts) == 2:
            source = parts[1]
            if source.startswith("#"):
                registers[destination] = int(source[1:], 0)
                dependencies[destination] = {addr}
            else:
                registers[destination] = registers.get(source)
                dependencies[destination] = dependencies.get(source, set()) | {addr}
        elif op == "ldr":
            literal = re.search(r"\[pc, #[^]]+\].*@ \(([0-9a-f]+) ", raw)
            if literal:
                at = int(literal[1], 16)
                registers[destination] = literals.get(at) if at not in relocations else None
                dependencies[destination] = {addr}
            else:
                memory = re.search(r"\[([\w]+)(?:, (#[^] ]+|[\w]+))?\]", args)
                value, used = None, set()
                if memory:
                    base, offset = memory[1], memory[2]
                    base_value = registers.get(base)
                    offset_value = 0 if offset is None else (int(offset[1:], 0) if offset.startswith("#") else registers.get(offset))
                    used = dependencies.get(base, set()) | (set() if offset is None or offset.startswith("#") else dependencies.get(offset, set()))
                    if isinstance(base_value, int) and isinstance(offset_value, int):
                        value = base_value + offset_value
                if value == 0x50110098:
                    loads.append({"instruction": ins, "address_materialization": sorted(used)})
                    registers[destination] = "local_status"
                    dependencies[destination] = {addr}
                else:
                    registers.pop(destination, None)
                    dependencies.pop(destination, None)
        elif op in ("add", "adds", "sub", "subs", "lsl", "lsls"):
            source = destination if len(parts) == 2 else parts[1]
            operand = parts[-1]
            old = registers.get(source)
            amount = int(operand[1:], 0) if operand.startswith("#") else registers.get(operand)
            if isinstance(old, int) and isinstance(amount, int):
                registers[destination] = (old << amount) if op.startswith("lsl") else old + (amount if op.startswith("add") else -amount)
                dependencies[destination] = dependencies.get(source, set()) | {addr} | (set() if operand.startswith("#") else dependencies.get(operand, set()))
            else:
                registers.pop(destination, None)
                dependencies.pop(destination, None)
        elif op not in ("push", "pop", "cmp", "tst", "str", "strb", "strh", "dmb", "dsb", "isb", "nop") and not op.startswith("b"):
            # Unknown result cannot inherit a stale address/local-status fact.
            registers.pop(destination, None)
            dependencies.pop(destination, None)
    assert len(loads) == 1, f"exactly one resolved original INTS load required: {loads}"
    load = loads[0]
    allowed_address = set(load["address_materialization"])
    before = prefix[:-1]
    prologue = []
    for ins in before:
        op = ins["opcode"].split(".")[0]
        operands = ins["operands"].split("@", 1)[0].strip()
        if ins["address"] in allowed_address:
            assert op in ("ldr", "mov", "movs", "add", "adds", "lsl", "lsls"), "unexpected status-address operation"
            continue
        # GCC's ordinary high-register save sequence and stack allocation have
        # no observer semantics. Arbitrary stores and arbitrary moves fail.
        is_save = op == "push" and re.fullmatch(r"\{(?:r[4-9]|sl|fp|lr)(?:, (?:r[4-9]|sl|fp|lr))*\}", operands)
        is_move = op in ("mov", "movs") and re.fullmatch(r"(?:r[4-9]|sl|fp|lr), (?:r[4-9]|sl|fp|lr)", operands)
        is_stack = op in ("sub", "subs") and re.fullmatch(r"sp, #\d+", operands)
        assert is_save or is_move or is_stack, f"intentional/unexplained operation before INTS: {ins['text']}"
        prologue.append(ins["text"])
    if require_marker:
        assert first_marker is not None, "first STATUS publication missing"
    return {"status_load": load["instruction"]["text"],
            "status_load_count": len(loads),
            "diagnostic_instructions_before_status": 0,
            "diagnostic_barriers_before_status": 0,
            "compiler_prologue_before_status": prologue,
            "address_materialization_before_status": [ins["text"] for ins in before if ins["address"] in allowed_address],
            "first_status_publication": first_marker["text"] if first_marker else None,
            "first_publication_exact_local_value": bool(first_marker),
            "static_handler_instructions": len(instructions),
            "static_handler_barriers": sum(ins["opcode"] in ("dmb", "dsb", "isb") for ins in instructions)}


def compile_receipt(root, build, compile_db):
    """Prefer captured actual command; recover only from one exact compiledb TU."""
    captured = build / "rt2-private-dcd/compile-command.json"
    if captured.is_file():
        receipt = json.loads(captured.read_text())
        receipt["provenance"] = {"kind": "SCons_object_preaction", "path": str(captured)}
        return receipt
    assert compile_db is not None, "missing actual compile receipt; provide --compile-db for byte-identical replay recovery"
    database = (root / compile_db).resolve()
    entries = json.loads(database.read_text())
    patched = (root / GENERATED_RELATIVE).resolve()
    candidates = [entry for entry in entries if Path(entry["directory"], entry["file"]).resolve() == patched]
    assert len(candidates) == 1, f"one actual compiledb private DCD command required: {len(candidates)}"
    entry = candidates[0]
    command = entry.get("arguments") or shlex.split(entry["command"])
    assert command.count("-o") == 1
    obj = Path(entry["directory"], command[command.index("-o") + 1]).resolve()
    installed = Path.home() / ".platformio/packages/framework-arduinopico" / INSTALLED_RELATIVE
    return {"arguments": command, "directory": entry["directory"], "object": str(obj),
            "installed_source": str(installed), "installed_sha256": PINNED_SHA256,
            "patched_source": str(patched), "patched_sha256": sha256(patched.read_bytes()).hexdigest(),
            "provenance": {"kind": "actual_compile_database_replay", "path": str(database),
                           "sha256": sha256(database.read_bytes()).hexdigest(), "matching_commands": len(candidates)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=Path(".pio/build/glyph_mk6"))
    parser.add_argument("--compile-db", type=Path, help="actual PlatformIO compile_commands.json; used only if object pre-action receipt is absent")
    parser.add_argument("--output-dir", type=Path, default=Path("local_backups/private-handler/assembly"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    build = (root / args.build_dir).resolve()
    out = (root / args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    receipt = compile_receipt(root, build, args.compile_db)
    original = root / PRISTINE_RELATIVE
    verify_pin(original.read_bytes())
    verify_pin(Path(receipt["installed_source"]).read_bytes(), "installed source")
    patched = Path(receipt["patched_source"])
    validate_patched(patched.read_bytes())
    assert sha256(patched.read_bytes()).hexdigest() == receipt["patched_sha256"]
    command = receipt["arguments"].copy()
    source_indices = [i for i, token in enumerate(command) if token.endswith(".c") and Path(receipt["directory"], token).resolve() == patched.resolve()]
    assert len(source_indices) == 1, "one exact source argument required"
    assert command.count("-o") == 1
    output_index = command.index("-o") + 1
    object_path = Path(receipt["object"])
    assert Path(receipt["directory"], command[output_index]).resolve() == object_path.resolve()
    assert "rt2-private-dcd/" in str(object_path), "compiled object must be candidate owned"
    # Replay the exact patched command with ONLY -o changed. This proves the
    # command/flags belong to the actual built object before pristine comparison.
    replay = out / "patched-replay.o"
    command[output_index] = str(replay)
    run(command, receipt["directory"])
    assert replay.read_bytes() == object_path.read_bytes(), "patched replay is not byte-identical to actual build object"
    patched_command = command.copy()
    comparison = out / "frozen-original.o"
    command[source_indices[0]] = str(original)
    command[output_index] = str(comparison)
    run(command, receipt["directory"])
    compiler = Path(command[0])
    objdump = compiler.with_name(compiler.name.replace("gcc", "objdump"))
    nm = compiler.with_name(compiler.name.replace("gcc", "nm"))
    final_elf = build / "firmware.elf"
    disassemblies = {}
    for label, path in (("frozen-original", comparison), ("patched-object", object_path), ("final-elf", final_elf)):
        disassembly = run([str(objdump), "-dr", str(path)], root)
        disassemblies[label] = disassembly
        (out / (label + ".disassembly.txt")).write_text(disassembly)
    audits = {label: entry_status_audit(assembly, label != "frozen-original") for label, assembly in disassemblies.items()}
    marker_audits = {}
    for name in ("GlyphDcdPrivateStatus", "GlyphDcdPrivateMarker"):
        instructions, _, _ = parse_function(disassemblies["final-elf"], name)
        nested = [ins["text"] for ins in instructions if ins["opcode"] in ("bl", "blx")]
        assert not nested, f"{name} must inline observer publication, not call another hook layer: {nested}"
        marker_audits[name] = {
            "static_instructions_all_paths": len(instructions),
            "static_barriers_all_paths": sum(ins["opcode"] in ("dmb", "dsb", "isb") for ins in instructions),
            "nested_calls": nested,
            "path_cost_review": "REQUIRED_SEPARATELY; static totals are not a dynamic path cost"}
    symbols = run([str(nm), "--defined-only", str(final_elf)], root)
    handlers = [line for line in symbols.splitlines() if re.search(r"\bdcd_rp2040_irq(?:\.\w+)?$", line)]
    assert len(handlers) == 1, f"exactly one final private DCD handler required: {handlers}"
    assert "observed_dcd_irq" not in symbols, "per-IRQ observer trampoline must be absent"
    map_text = (build / "firmware.map").read_text()
    objects = set(re.findall(r"[^\s()]*dcd_rp2040(?:\.c)?\.o", map_text))
    assert objects, "map must identify active DCD object"
    assert all("rt2-private-dcd/" in item for item in objects), f"original or duplicate DCD object: {objects}"
    assert len(objects) == 1, f"more than one DCD object: {objects}"
    report = {"result": "PASS_AUTOMATED_IDENTITY_ENTRY_STATUS_AND_UNIQUENESS",
              "structural_assembly_review": "REQUIRED_SEPARATELY_FOR_LATER_BRANCH_EVENT_CLEAR_ORDER_AND_MARKER_COST",
              "compile_provenance": receipt["provenance"],
              "patched_replay_byte_identity": True,
              "original_sha256": sha256(original.read_bytes()).hexdigest(),
              "patched_sha256": sha256(patched.read_bytes()).hexdigest(),
              "original_object_sha256": sha256(comparison.read_bytes()).hexdigest(),
              "patched_object_sha256": sha256(object_path.read_bytes()).hexdigest(),
              "final_elf_sha256": sha256(final_elf.read_bytes()).hexdigest(),
              "entry_status_assembly_audits": audits,
              "post_status_marker_assembly_audits": marker_audits,
              "final_handler_symbols": handlers, "map_dcd_objects": sorted(objects),
              "patched_replay_compile_arguments": patched_command,
              "comparison_compile_arguments": command}
    (out / "identity-and-uniqueness.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if not key.endswith("compile_arguments")}, indent=2))


if __name__ == "__main__":
    main()
