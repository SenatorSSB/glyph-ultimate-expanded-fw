#!/usr/bin/env python3
"""Generate a complete inert artifact from explicit table ownership."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from glyph_source_owned_overlay import OverlayContractError, generate_overlay_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--test-only-override", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        output, report = generate_overlay_payload(payload, production=args.production, test_only_override=args.test_only_override)
        if args.artifact:
            args.artifact.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.manifest:
            args.manifest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not args.artifact and not args.manifest:
            print(json.dumps({"artifact": output, "manifest": report}, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, OverlayContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
