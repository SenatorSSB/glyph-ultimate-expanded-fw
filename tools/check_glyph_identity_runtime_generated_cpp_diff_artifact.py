#!/usr/bin/env python3
"""Validate generated C++-shaped Glyph identity runtime table review text.

This is a docs/tools-only diff artifact checker. It does not generate firmware
source, include generated files in firmware, load runtime config, write a
device, or validate hardware behavior.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from extract_glyph_identity_runtime_tables import (
    DEFAULT_SOURCE_PATH,
    EXPECTED_POINT_COUNT,
    load_source_tables,
    normalized_table_names,
    source_symbol_by_normalized_name,
)
from generate_glyph_identity_runtime_config_prototype import (
    build_config_prototype,
    render_cpp_prototype,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_CHECKER_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_generated_config_prototype.py"
COMMITTED_ARTIFACT_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt"
)
ALLOWED_ARTIFACT_ROOT = REPO_ROOT / "docs" / "calibration" / "fixtures"

REQUIRED_CPP_CAVEATS = (
    "generated prototype only",
    "do not include in firmware",
    "not firmware source",
    "not runtime-loaded config",
    "not hardware validation",
)
FORBIDDEN_GENERATED_CPP_PHRASES = (
    "#include",
    "namespace",
    "mode_ultimate implementation hook",
    "upload",
    "flash",
    "push-to-device",
    "macro",
    "turbo",
)

_TABLE_PATTERN = re.compile(
    r"constexpr\s+StickPoint\s+"
    r"(?P<symbol>k[A-Za-z0-9]+Table)"
    r"\s*\[\s*(?P<size>\d+)\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
_POINT_PATTERN = re.compile(r"\{\s*(?P<x>\d+)\s*,\s*(?P<y>\d+)\s*\}")


class GeneratedCppDiffArtifactError(ValueError):
    """Raised when generated C++-shaped table text is not source-faithful."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise GeneratedCppDiffArtifactError(message)


def run_generated_config_prototype_checker() -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, str(PROTOTYPE_CHECKER_PATH.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode == 0, output


def _parse_points(symbol: str, declared_size: str, body: str) -> tuple[tuple[int, int], ...]:
    try:
        size = int(declared_size)
    except ValueError as exc:
        fail(f"{symbol} has non-integer array size: {declared_size}")
        raise AssertionError("unreachable") from exc

    if size != EXPECTED_POINT_COUNT:
        fail(f"{symbol} declares {size} points, expected {EXPECTED_POINT_COUNT}")

    points: list[tuple[int, int]] = []
    for match in _POINT_PATTERN.finditer(body):
        x = int(match.group("x"))
        y = int(match.group("y"))
        if not 0 <= x <= 255 or not 0 <= y <= 255:
            fail(f"{symbol} contains out-of-range point ({x}, {y})")
        points.append((x, y))

    remainder = _POINT_PATTERN.sub("", body)
    if re.sub(r"[\s,]", "", remainder):
        fail(f"{symbol} contains malformed table body")

    if len(points) != EXPECTED_POINT_COUNT:
        fail(f"{symbol} contains {len(points)} points, expected {EXPECTED_POINT_COUNT}")

    return tuple(points)


def parse_generated_cpp_tables(text: str) -> dict[str, tuple[tuple[int, int], ...]]:
    """Return normalized table names mapped to generated C++-shaped points."""

    symbol_to_name = {symbol: name for name, symbol in source_symbol_by_normalized_name().items()}
    parsed_symbols: dict[str, tuple[tuple[int, int], ...]] = {}

    for match in _TABLE_PATTERN.finditer(text):
        symbol = match.group("symbol")
        if symbol not in symbol_to_name:
            fail(f"generated C++ contains unexpected table symbol: {symbol}")
        if symbol in parsed_symbols:
            fail(f"generated C++ contains duplicate table symbol: {symbol}")
        parsed_symbols[symbol] = _parse_points(symbol, match.group("size"), match.group("body"))

    expected_symbols = source_symbol_by_normalized_name()
    missing = [expected_symbols[name] for name in normalized_table_names() if expected_symbols[name] not in parsed_symbols]
    if missing:
        fail("generated C++ missing table declaration(s): " + ", ".join(missing))

    extra = sorted(set(parsed_symbols) - set(expected_symbols.values()))
    if extra:
        fail("generated C++ contains unexpected table declaration(s): " + ", ".join(extra))

    return {name: parsed_symbols[expected_symbols[name]] for name in normalized_table_names()}


def validate_cpp_caveats(text: str) -> None:
    lowered = text.lower()
    for caveat in REQUIRED_CPP_CAVEATS:
        if caveat not in lowered:
            fail(f"generated C++ missing caveat text: {caveat}")


def validate_no_forbidden_generated_cpp_phrases(text: str) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_GENERATED_CPP_PHRASES:
        if phrase in lowered:
            fail(f"generated C++ contains forbidden phrase: {phrase}")


def load_committed_artifact_if_present() -> str | None:
    if not COMMITTED_ARTIFACT_PATH.exists():
        return None

    try:
        COMMITTED_ARTIFACT_PATH.resolve().relative_to(ALLOWED_ARTIFACT_ROOT.resolve())
    except ValueError as exc:
        raise GeneratedCppDiffArtifactError(
            f"committed artifact must be under {display(ALLOWED_ARTIFACT_ROOT)}"
        ) from exc

    return COMMITTED_ARTIFACT_PATH.read_text(encoding="utf-8")


def validate_generated_tables_match_source(generated_tables: dict[str, tuple[tuple[int, int], ...]]) -> None:
    expected_names = set(normalized_table_names())
    if set(generated_tables) != expected_names:
        missing = sorted(expected_names - set(generated_tables))
        unexpected = sorted(set(generated_tables) - expected_names)
        fail(f"generated table names mismatch missing={missing} unexpected={unexpected}")

    source_tables = load_source_tables(DEFAULT_SOURCE_PATH)
    for name in normalized_table_names():
        if len(generated_tables[name]) != EXPECTED_POINT_COUNT:
            fail(f"{name} contains {len(generated_tables[name])} points, expected {EXPECTED_POINT_COUNT}")
        if generated_tables[name] != source_tables[name]:
            fail(f"{name} generated C++ table points do not match source-parsed table")


def validate_committed_artifact(generated_text: str) -> bool:
    committed_text = load_committed_artifact_if_present()
    if committed_text is None:
        return False
    if committed_text != generated_text:
        fail(f"{display(COMMITTED_ARTIFACT_PATH)} does not exactly match generated C++ text")
    return True


def main() -> int:
    print("glyph_identity_runtime_generated_cpp_diff_artifact")
    print(f"source_path={display(DEFAULT_SOURCE_PATH)}")
    print(f"artifact_path={display(COMMITTED_ARTIFACT_PATH)}")

    committed_present = COMMITTED_ARTIFACT_PATH.exists()
    prototype_checker_passed, prototype_checker_output = run_generated_config_prototype_checker()
    if not prototype_checker_passed:
        print("status=FAIL")
        print("table_count=0")
        print("generated_table_declarations=0")
        print(f"committed_artifact={'present' if committed_present else 'absent'}")
        print("hardware_status=not_new_hardware_result")
        print("prototype_checker_status=FAIL")
        if prototype_checker_output:
            print("prototype_checker_output:")
            print(prototype_checker_output)
        return 1

    try:
        generated_text = render_cpp_prototype(build_config_prototype())
        validate_cpp_caveats(generated_text)
        validate_no_forbidden_generated_cpp_phrases(generated_text)
        generated_tables = parse_generated_cpp_tables(generated_text)
        validate_generated_tables_match_source(generated_tables)
        committed_present = validate_committed_artifact(generated_text)
    except (GeneratedCppDiffArtifactError, OSError, ValueError, KeyError) as exc:
        print("status=FAIL")
        print("table_count=0")
        print("generated_table_declarations=0")
        print(f"committed_artifact={'present' if committed_present else 'absent'}")
        print("hardware_status=not_new_hardware_result")
        print("prototype_checker_status=PASS")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"table_count={len(normalized_table_names())}")
    print(f"generated_table_declarations={len(generated_tables)}")
    print(f"committed_artifact={'present' if committed_present else 'absent'}")
    print("hardware_status=not_new_hardware_result")
    print("prototype_checker_status=PASS")
    print(f"source_table_extractor=tools/extract_glyph_identity_runtime_tables.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
