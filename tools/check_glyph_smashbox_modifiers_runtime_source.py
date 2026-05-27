#!/usr/bin/env python3
"""Read-only source-shape checker for Smash Box modifier runtime scope."""

from __future__ import annotations

from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
ULTIMATE_CPP = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
RUNTIME_DOC = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md"
)

EXPECTED_MARKERS = (
    "Smash Box modifiers runtime begin",
    "Smash Box modifiers runtime end",
)

FORBIDDEN_RUNTIME_TOKENS = (
    "uf2",
    "reboot_bootloader",
    "flash",
    "RPI-RP2",
)

RAW_PHYSICAL_BYPASS_TOKENS = (
    "inputs.rf3",
    "inputs.rf4",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    failures: list[str] = []

    if not ULTIMATE_CPP.exists():
        failures.append(f"missing runtime source file: {rel(ULTIMATE_CPP)}")
        print(f"runtime_source={rel(ULTIMATE_CPP)}")
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    source = ULTIMATE_CPP.read_text(encoding="utf-8")

    marker_begin_present = EXPECTED_MARKERS[0] in source
    marker_end_present = EXPECTED_MARKERS[1] in source

    if marker_begin_present != marker_end_present:
        failures.append("runtime marker pair mismatch in Ultimate.cpp")

    if not marker_begin_present:
        failures.append(
            "fixed-profile Smash Box runtime markers missing (implementation not present)"
        )

    for token in FORBIDDEN_RUNTIME_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", source, flags=re.IGNORECASE):
            failures.append(f"forbidden token found in runtime source: {token}")

    if marker_begin_present:
        marker_block = source.split(EXPECTED_MARKERS[0], 1)[1].split(EXPECTED_MARKERS[1], 1)[0]

        if "uint8_t" in marker_block and "signed" not in marker_block:
            failures.append("runtime marker block appears to rely on uint8_t without signed handling note")

        if any(token in marker_block for token in RAW_PHYSICAL_BYPASS_TOKENS):
            failures.append("runtime marker block uses raw RF3/RF4 physical inputs; expected logical post-remap inputs")

    runtime_doc_present = RUNTIME_DOC.exists()
    blocker_doc_tag_present = False
    if runtime_doc_present:
        runtime_doc_text = RUNTIME_DOC.read_text(encoding="utf-8")
        blocker_doc_tag_present = "MODIFIER_ROLE_BINDING_SOURCE_GAP" in runtime_doc_text

    ls_dpad_mentions = "LS->DPad" in source or "LS to DPad" in source or "left stick to dpad" in source.lower()

    print(f"runtime_source={rel(ULTIMATE_CPP)}")
    print(f"runtime_doc={rel(RUNTIME_DOC)}")
    print(f"runtime_doc_present={'true' if runtime_doc_present else 'false'}")
    print(f"runtime_marker_begin_present={'true' if marker_begin_present else 'false'}")
    print(f"runtime_marker_end_present={'true' if marker_end_present else 'false'}")
    print(f"role_binding_gap_doc_tag_present={'true' if blocker_doc_tag_present else 'false'}")
    print(f"ls_dpad_source_shape_present={'true' if ls_dpad_mentions else 'false'}")
    print("firmware_flashing_logic_present=false")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
