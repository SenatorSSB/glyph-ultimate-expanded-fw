#!/usr/bin/env python3
"""Render a prepared v2 packet as inactive C++ review text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from source_owned_cpp_preview import render_cpp_preview, write_preview
from source_owned_generator_modes import GeneratorModesError, load_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--test-mode", action="store_true")
    args = parser.parse_args(argv)
    try:
        packet = load_json(args.packet)
        if args.output:
            write_preview(packet, args.output, test_mode=args.test_mode)
        else:
            sys.stdout.write(render_cpp_preview(packet, test_mode=args.test_mode))
        return 0
    except (GeneratorModesError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3 if isinstance(exc, GeneratorModesError) and exc.category == "source_authority" else 2


if __name__ == "__main__":
    raise SystemExit(main())

