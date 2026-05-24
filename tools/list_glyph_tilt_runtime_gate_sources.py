#!/usr/bin/env python3
"""Read-only scanner for Glyph Ultimate tilt runtime gate source candidates."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SOURCE_SUFFIXES = {
    ".cpp",
    ".hpp",
    ".h",
    ".c",
    ".cc",
    ".proto",
    ".options",
    ".ini",
    ".json",
    ".md",
    ".py",
}

SCAN_ROOTS = [
    "src",
    "include",
    "HAL/pico/include",
    "HAL/pico/src",
    "config",
    "docs/calibration",
    "tools",
    ".pio/libdeps/glyph_mk6/HayBox-proto",
    ".pio/build/glyph_mk6/nanopb/generated-src",
]

SYMBOL_RE = re.compile(
    r"\b("
    r"modifier|modifiers|AnalogModifier|AnalogAxis|axis_pointer|OutputState|"
    r"UpdateAnalogOutputs|stick_range|multiplier|uint8_t|analog_axes|"
    r"leftStickX|leftStickY|rightStickX|rightStickY|triggerLAnalog|triggerRAnalog|"
    r"COMBINATION_MODE_[A-Z_]+|AXIS_[A-Z_]+|UpdateDirections|flipper|clamp|saturat|overflow"
    r")\b",
    re.IGNORECASE,
)

FUNCTION_RE = re.compile(
    r"^\s*(?:[A-Za-z_][A-Za-z0-9_:<>&*\s]+)?"
    r"(UpdateAnalogOutputs|axis_pointer|UpdateDirections|SetConfig)\s*\("
)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in SOURCE_SUFFIXES:
                files.append(path)
    return sorted(set(files))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    candidate_files: list[tuple[Path, int, set[str]]] = []
    function_hits: list[tuple[Path, int, str]] = []

    for path in iter_files():
        text = read_text(path)
        symbols = {match.group(1) for match in SYMBOL_RE.finditer(text)}
        if symbols:
            candidate_files.append((path, len(symbols), symbols))
        for line_number, line in enumerate(text.splitlines(), start=1):
            if FUNCTION_RE.search(line) and (
                "UpdateAnalogOutputs" in line
                or "axis_pointer" in line
                or "OutputState" in text
                or "axis_pointer" in text
            ):
                function_hits.append((path, line_number, line.strip()))

    print(f"candidate_source_files={len(candidate_files)}")
    for path, symbol_count, symbols in candidate_files:
        relative = path.relative_to(REPO_ROOT)
        preview = ", ".join(sorted(symbols, key=str.lower)[:10])
        print(f"- {relative} symbols={symbol_count}: {preview}")

    print()
    print("modifier_axis_uint8_stick_range_multiplier_symbols:")
    symbol_sources: dict[str, set[str]] = {}
    for path, _, symbols in candidate_files:
        relative = str(path.relative_to(REPO_ROOT))
        for symbol in symbols:
            symbol_sources.setdefault(symbol, set()).add(relative)
    for symbol in sorted(symbol_sources, key=str.lower):
        source_list = ", ".join(sorted(symbol_sources[symbol])[:8])
        print(f"- {symbol}: {source_list}")

    print()
    print("functions_containing_updateanalogoutputs_axis_pointer_outputstate:")
    for path, line_number, line in function_hits:
        relative = path.relative_to(REPO_ROOT)
        print(f"- {relative}:{line_number}: {line}")


if __name__ == "__main__":
    main()
