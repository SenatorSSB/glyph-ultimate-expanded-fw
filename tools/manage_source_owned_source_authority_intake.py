#!/usr/bin/env python3
"""CLI for the offline source-authority intake workflow."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from source_owned_source_authority_intake import EXIT_CODES, GeneratorModesError, IntakeError, create_template, emit_generator_input, inspect_baseline, load_json, review_intake, select_validation_failure_category, write_json

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__); s = p.add_subparsers(dest="command", required=True)
    s.add_parser("inspect-baseline")
    for name in ("create-template",): s.add_parser(name).add_argument("--output", type=Path, required=True)
    for name in ("validate", "review"):
        c=s.add_parser(name); c.add_argument("input", type=Path); c.add_argument("--output", type=Path)
    for name in ("emit-generator-input", "prove-source-equivalence"):
        c=s.add_parser(name); c.add_argument("input", type=Path); c.add_argument("--output", type=Path, required=True)
    a=p.parse_args(argv)
    try:
        if a.command == "inspect-baseline": result=inspect_baseline()
        elif a.command == "create-template": result=create_template(); write_json(a.output, result)
        else:
            payload=load_json(a.input); report=review_intake(payload)
            if a.command in {"validate", "review"}:
                result=report
                (write_json(a.output, result, input_path=a.input) if a.output else None)
                print(json.dumps(result, indent=2, sort_keys=True))
                if a.command == "validate":
                    category = select_validation_failure_category(report)
                    return EXIT_CODES[category] if category else EXIT_CODES["success"]
                return EXIT_CODES["success"]
            else:
                op="production_changeset" if a.command == "emit-generator-input" else "source_equivalence_proof"; value, artifact, manifest=emit_generator_input(payload, operation=op); result=value; write_json(a.output, result, input_path=a.input)
        print(json.dumps(result, indent=2, sort_keys=True)); return 0
    except (IntakeError, GeneratorModesError) as exc: print(f"error: {exc}", file=sys.stderr); return EXIT_CODES.get(exc.category, EXIT_CODES["invalid_input"])
    except (OSError, json.JSONDecodeError) as exc: print(f"error: {exc}", file=sys.stderr); return EXIT_CODES["integrity"]
if __name__ == "__main__": raise SystemExit(main())
