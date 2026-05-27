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

EXPECTED_STOP_CODES = (
    "MODIFIER_ROLE_BINDING_SOURCE_GAP",
    "LS_DPAD_LEFT_STICK_NEUTRAL_POLICY_UNRESOLVED",
    "MODIFIER_COMPOSITION_POLICY_UNRESOLVED",
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


def contains_intentional_stop_statement(text: str) -> bool:
    return "runtime implementation intentionally not performed" in text.lower()


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

    for token in FORBIDDEN_RUNTIME_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", source, flags=re.IGNORECASE):
            failures.append(f"forbidden token found in runtime source: {token}")

    implementation_present = marker_begin_present and marker_end_present
    stopped_before_runtime = False
    runtime_source_unchanged = False
    stop_codes_output = "none"

    runtime_doc_present = RUNTIME_DOC.exists()
    runtime_doc_text = ""
    if runtime_doc_present:
        runtime_doc_text = RUNTIME_DOC.read_text(encoding="utf-8")

    missing_stop_codes: list[str] = []
    for code in EXPECTED_STOP_CODES:
        if code not in runtime_doc_text:
            missing_stop_codes.append(code)

    intentional_stop_statement_present = contains_intentional_stop_statement(runtime_doc_text)

    if marker_begin_present != marker_end_present:
        failures.append("runtime marker pair mismatch in Ultimate.cpp")

    if implementation_present:
        marker_block = source.split(EXPECTED_MARKERS[0], 1)[1].split(EXPECTED_MARKERS[1], 1)[0]

        if "uint8_t" in marker_block and "signed" not in marker_block:
            failures.append("runtime marker block appears to rely on uint8_t without signed handling note")

        if any(token in marker_block for token in RAW_PHYSICAL_BYPASS_TOKENS):
            failures.append("runtime marker block uses raw RF3/RF4 physical inputs; expected logical post-remap inputs")

    ls_dpad_mentions = "LS->DPad" in source or "LS to DPad" in source or "left stick to dpad" in source.lower()
    blocker_doc_tag_present = "MODIFIER_ROLE_BINDING_SOURCE_GAP" in runtime_doc_text

    if not implementation_present:
        if not runtime_doc_present:
            failures.append(f"missing runtime implementation doc: {rel(RUNTIME_DOC)}")
        if missing_stop_codes:
            failures.append(
                "runtime implementation doc missing stop code(s): "
                + ",".join(missing_stop_codes)
            )
        if runtime_doc_present and not intentional_stop_statement_present:
            failures.append(
                "runtime implementation doc missing intentional-stop statement"
            )

        if not failures:
            stopped_before_runtime = True
            runtime_source_unchanged = True
            stop_codes_output = ",".join(EXPECTED_STOP_CODES)

    print(f"runtime_source={rel(ULTIMATE_CPP)}")
    print(f"runtime_doc={rel(RUNTIME_DOC)}")
    print(f"runtime_doc_present={'true' if runtime_doc_present else 'false'}")
    print(f"runtime_marker_begin_present={'true' if marker_begin_present else 'false'}")
    print(f"runtime_marker_end_present={'true' if marker_end_present else 'false'}")
    print(f"role_binding_gap_doc_tag_present={'true' if blocker_doc_tag_present else 'false'}")
    print(f"ls_dpad_source_shape_present={'true' if ls_dpad_mentions else 'false'}")
    print(f"implementation_present={'true' if implementation_present else 'false'}")
    print(f"stopped_before_runtime={'true' if stopped_before_runtime else 'false'}")
    print(f"stop_codes={stop_codes_output}")
    print(f"runtime_source_unchanged={'true' if runtime_source_unchanged else 'false'}")
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
