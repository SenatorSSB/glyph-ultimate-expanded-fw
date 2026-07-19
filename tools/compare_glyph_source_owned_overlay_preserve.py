#!/usr/bin/env python3
"""Compare an overlay artifact against its declared source baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from glyph_source_owned_overlay import OverlayContractError, baseline_contract, generate_overlay_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.artifact.read_text(encoding="utf-8"))
        _output, report = generate_overlay_payload(payload)
        expected = json.loads(args.manifest.read_text(encoding="utf-8"))
        if report != expected:
            raise OverlayContractError("manifest does not deterministically match artifact")
        changed = [row["table_symbol"] for row in report["manifest"] if row["changed"]]
        print(json.dumps({
            "classification": "NO_OP" if not changed else "EXPLICIT_OWNED_TABLE_CHANGESET",
            "changed_tables": changed,
            "preserved_table_count": sum(row["action"] == "preserve_source_owned_baseline" for row in report["manifest"]),
            "baseline_semantic_digest": baseline_contract()["semantic_digest"],
            "output_semantic_digest": report["output_semantic_digest"],
        }, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, OverlayContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
