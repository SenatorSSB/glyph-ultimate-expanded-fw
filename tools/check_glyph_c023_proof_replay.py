#!/usr/bin/env python3
"""Replay the exact committed C023 host proof from its immutable candidate."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import glyph_c023_campaign_transition as campaign

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    campaign.source_contract(ROOT)
    with tempfile.TemporaryDirectory(prefix="glyph-c023-proof-") as directory:
        candidate = Path(directory) / "candidate"
        cloned = subprocess.run(["git", "clone", "--shared", "--no-hardlinks", str(ROOT), str(candidate)],
                                capture_output=True, text=True, timeout=90)
        if cloned.returncode:
            raise RuntimeError("cannot materialize exact C023 proof source: " + cloned.stderr)
        branch = subprocess.run(["git", "checkout", "-b", "codex/gp-config-023-release-safety", campaign.C],
                                cwd=candidate, capture_output=True, text=True, timeout=90)
        if branch.returncode:
            raise RuntimeError("cannot select exact C023 proof branch: " + branch.stderr)
        result = subprocess.run([sys.executable, "tools/check_glyph_gp_config023_usb_index_validation.py"],
                                cwd=candidate, capture_output=True, text=True, timeout=180)
        if result.returncode or result.stderr:
            raise RuntimeError("exact C023 proof failed:\n" + result.stdout + result.stderr)
        if "cases=4096 accepted=120" not in result.stdout or \
                "ABIs=default,short-enum ASan_UBSan=PASS" not in result.stdout or \
                "hardware=NOT_CLAIMED" not in result.stdout:
            raise RuntimeError("exact C023 proof output lacks required bounded evidence")
        print("C023 exact candidate proof replay: PASS")
        print("host matrix, selector routes, both ABIs and sanitizers: PASS")
        print("firmware build and hardware acceptance: NOT_CLAIMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
