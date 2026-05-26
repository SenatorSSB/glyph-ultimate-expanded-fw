#!/usr/bin/env python3
"""Read-only inventory helper for Glyph physical/logical layout mapping evidence.

- Prints relevant source/fixture/doc paths.
- Reports file existence.
- Performs conservative text scans for key button/runtime tokens.
- Exits non-zero only when required files are missing.
"""

from __future__ import annotations

from pathlib import Path
import sys

REQUIRED_PATHS = [
    "config/glyph/glyph_mk6/include/matrix_definition.hpp",
    "config/glyph/glyph_mk6/include/button_positions.hpp",
    "HAL/pico/src/display/InputDisplay.cpp",
    "config/glyph/common/src/config.cpp",
    "include/core/state.hpp",
    "HAL/pico/include/util/state_util.hpp",
    "src/core/InputMode.cpp",
    "src/core/ControllerMode.cpp",
    "src/modes/Ultimate.cpp",
    "docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_test_result.md",
    "docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json",
    "docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json",
    "docs/calibration/glyph_full_capability_inventory_2026-05-26.md",
]

OPTIONAL_PATHS = [
    "docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md",
]

TOKENS = [
    "BTN_RF3",
    "BTN_RF4",
    "BTN_RF5",
    "BTN_LT1",
    "BTN_LT2",
    "inputs.lt1",
    "inputs.lt2",
]



def print_path_status(label: str, path_str: str) -> bool:
    p = Path(path_str)
    exists = p.exists()
    status = "EXISTS" if exists else "MISSING"
    print(f"[{label}] {status} {path_str}")
    return exists



def scan_tokens(path_str: str) -> None:
    p = Path(path_str)
    if not p.exists() or not p.is_file():
        return

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"  [SCAN_ERROR] {path_str}: {exc}")
        return

    lines = text.splitlines()
    print(f"  [SCAN] {path_str}")
    for token in TOKENS:
        hit_lines = [i + 1 for i, line in enumerate(lines) if token in line]
        if hit_lines:
            preview = ", ".join(str(n) for n in hit_lines[:8])
            if len(hit_lines) > 8:
                preview += ", ..."
            print(f"    - {token}: {len(hit_lines)} hit(s) at line(s) {preview}")



def main() -> int:
    print("Glyph physical/logical layout source inventory")
    print("=" * 48)

    missing_required = []

    print("\nRequired paths:")
    for path_str in REQUIRED_PATHS:
        exists = print_path_status("REQUIRED", path_str)
        if not exists:
            missing_required.append(path_str)

    print("\nOptional/related paths:")
    for path_str in OPTIONAL_PATHS:
        print_path_status("OPTIONAL", path_str)

    print("\nConservative token scan (existing files only):")
    for path_str in REQUIRED_PATHS + OPTIONAL_PATHS:
        scan_tokens(path_str)

    if missing_required:
        print("\nMissing required paths:")
        for path_str in missing_required:
            print(f"- {path_str}")
        return 1

    print("\nAll required source paths are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
