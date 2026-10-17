#!/usr/bin/env python3
"""Capture frozen/patched actual-flag assembly and enforce final DCD uniqueness.

This compiles only a frozen comparison object, never firmware or device inputs.
The emitted disassembly still requires independent structural review; the JSON
does not promote instruction listings into a completed human assembly review.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

from rt2_private_dcd import PRISTINE_RELATIVE, validate_patched, verify_pin


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=Path(".pio/build/glyph_mk6"))
    parser.add_argument("--output-dir", type=Path, default=Path("local_backups/private-handler/assembly"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    build = (root / args.build_dir).resolve()
    out = (root / args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    receipt = json.loads((build / "rt2-private-dcd/compile-command.json").read_text())
    original = root / PRISTINE_RELATIVE
    verify_pin(original.read_bytes())
    verify_pin(Path(receipt["installed_source"]).read_bytes(), "installed source")
    patched = Path(receipt["patched_source"])
    validate_patched(patched.read_bytes())
    assert sha256(patched.read_bytes()).hexdigest() == receipt["patched_sha256"]
    command = receipt["arguments"].copy()
    comparison = out / "frozen-original.o"
    source_indices = [i for i, token in enumerate(command) if token.endswith(".c") and Path(receipt["directory"], token).resolve() == patched.resolve()]
    assert len(source_indices) == 1, "one exact source argument required"
    command[source_indices[0]] = str(original)
    output_index = command.index("-o") + 1
    command[output_index] = str(comparison)
    run(command, receipt["directory"])
    compiler = Path(command[0])
    objdump = compiler.with_name(compiler.name.replace("gcc", "objdump"))
    nm = compiler.with_name(compiler.name.replace("gcc", "nm"))
    final_elf = build / "firmware.elf"
    object_path = Path(receipt["object"])
    for label, path in (("frozen-original", comparison), ("patched-object", object_path), ("final-elf", final_elf)):
        disassembly = run([str(objdump), "-dr", str(path)], root)
        (out / (label + ".disassembly.txt")).write_text(disassembly)
    symbols = run([str(nm), "--defined-only", str(final_elf)], root)
    handlers = [line for line in symbols.splitlines() if re.search(r"\bdcd_rp2040_irq(?:\.\w+)?$", line)]
    assert len(handlers) == 1, f"exactly one final private DCD handler required: {handlers}"
    map_text = (build / "firmware.map").read_text()
    objects = set(re.findall(r"[^\s()]*dcd_rp2040(?:\.c)?\.o", map_text))
    assert objects, "map must identify active DCD object"
    assert all("rt2-private-dcd/" in item for item in objects), f"original or duplicate DCD object: {objects}"
    assert len(objects) == 1, f"more than one DCD object: {objects}"
    report = {"result": "PASS_AUTOMATED_IDENTITY_AND_UNIQUENESS",
              "structural_assembly_review": "REQUIRED_SEPARATELY",
              "original_sha256": sha256(original.read_bytes()).hexdigest(),
              "patched_sha256": sha256(patched.read_bytes()).hexdigest(),
              "original_object_sha256": sha256(comparison.read_bytes()).hexdigest(),
              "patched_object_sha256": sha256(object_path.read_bytes()).hexdigest(),
              "final_elf_sha256": sha256(final_elf.read_bytes()).hexdigest(),
              "final_handler_symbols": handlers, "map_dcd_objects": sorted(objects),
              "comparison_compile_arguments": command}
    (out / "identity-and-uniqueness.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "comparison_compile_arguments"}, indent=2))


if __name__ == "__main__":
    main()
