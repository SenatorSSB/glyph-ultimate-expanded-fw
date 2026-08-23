#!/usr/bin/env python3
"""CLI for the offline source-owned full/overlay/reject generator modes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from source_owned_generator_modes import (
    EXIT_CODES,
    GeneratorModesError,
    baseline_identity,
    generate,
    install_prepared,
    load_json,
    prepare,
    prepare_offline_packet,
    production_gate,
    _atomic_write_text,
    validate_input,
    validate_manifest,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("inspect-baseline")
    for name in ("validate-input", "generate", "generate-manifest", "compare", "classify", "prepare"):
        command = sub.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--json", action="store_true")
        if name in {"prepare", "classify"}:
            command.add_argument("--production", action="store_true")
            command.add_argument("--hardware-candidate", action="store_true")
        if name == "prepare":
            command.add_argument("--output", type=Path)
    install = sub.add_parser("install")
    install.add_argument("packet", type=Path)
    install.add_argument("target", type=Path)
    install.add_argument("--dry-run", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "inspect-baseline":
            result = baseline_identity()
        elif args.command == "validate-input":
            result = validate_input(load_json(args.input))
        elif args.command in {"generate", "generate-manifest", "compare", "classify", "prepare"}:
            artifact, manifest = generate(load_json(args.input))
            if args.command == "generate":
                result = artifact
            elif args.command == "generate-manifest":
                result = manifest
            elif args.command == "compare":
                result = {"artifact": artifact, "manifest": manifest}
            elif args.command == "classify":
                if args.production:
                    production_gate(artifact, manifest, hardware_candidate=args.hardware_candidate)
                result = {"classification": manifest["classification"], "manifest": manifest}
            else:
                if args.production:
                    packet = prepare(artifact, manifest, hardware_candidate=args.hardware_candidate)
                else:
                    packet = prepare_offline_packet(artifact, manifest)
                if args.output:
                    if args.output.resolve(strict=False) == args.input.resolve(strict=False):
                        raise GeneratorModesError("prepare output may not overwrite input", "source_authority")
                    _atomic_write_text(args.output, json.dumps(packet, indent=2, sort_keys=True) + "\n", purpose="prepare")
                result = packet
        else:
            packet = load_json(args.packet)
            result = {"operations": install_prepared(packet, args.target, dry_run=args.dry_run)}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except GeneratorModesError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CODES.get(exc.category, EXIT_CODES["invalid_input"])
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CODES["integrity"]


if __name__ == "__main__":
    raise SystemExit(main())
