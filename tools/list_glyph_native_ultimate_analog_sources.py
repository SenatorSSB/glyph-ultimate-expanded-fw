#!/usr/bin/env python3
"""Read-only static scanner for Glyph native Ultimate analog source assignments."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ANALOG_FIELDS = (
    "leftStickX",
    "leftStickY",
    "rightStickX",
    "rightStickY",
    "triggerLAnalog",
    "triggerRAnalog",
)

SCAN_FILES = (
    "src/modes/Ultimate.cpp",
    "include/modes/Ultimate.hpp",
    "src/core/ControllerMode.cpp",
    "include/core/ControllerMode.hpp",
    "src/core/InputMode.cpp",
    "include/core/state.hpp",
    "config/glyph/common/include/glyph_overrides.hpp",
)

OPTIONAL_SCAN_FILES = (
    "config/glyph/common/include/config.pb.h",
    ".pio/build/glyph_mk6/nanopb/generated-src/config.pb.h",
)

FUNCTION_PATTERNS = (
    re.compile(r"\bUltimate::UpdateAnalogOutputs\s*\("),
    re.compile(r"\bUltimate::UpdateDigitalOutputs\s*\("),
    re.compile(r"\bControllerMode::UpdateOutputs\s*\("),
    re.compile(r"\bControllerMode::UpdateDirections\s*\("),
)

ASSIGNMENT_RE = re.compile(
    r"\boutputs\.(leftStickX|leftStickY|rightStickX|rightStickY|triggerLAnalog|triggerRAnalog)\s*=\s*([^;]+);"
)

NUMBER_RE = re.compile(r"\b(?:0x[0-9A-Fa-f]+|\d+(?:\.\d+)?)\b")
TOKEN_RE = re.compile(
    r"\b("
    r"inputs\.(?:lf\d+|rf\d+|lt\d+|rt\d+|mb\d+|nunchuk_[a-z_]+)"
    r"|outputs\.(?:modX|modY)"
    r"|directions\.(?:horizontal|vertical|diagonal|x|y|cx|cy)"
    r"|shield_button_pressed"
    r")\b"
)


@dataclass(frozen=True)
class SourceLine:
    path: str
    line: int
    text: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.text}"


@dataclass(frozen=True)
class AssignmentContext:
    field: str
    source_line: SourceLine
    constants: tuple[str, ...]
    tokens: tuple[str, ...]


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None


def _iter_scan_targets() -> tuple[list[Path], list[Path]]:
    targets: list[Path] = [REPO_ROOT / rel for rel in SCAN_FILES]
    optional: list[Path] = [REPO_ROOT / rel for rel in OPTIONAL_SCAN_FILES]
    return targets, optional


def _collect_context_tokens(lines: list[str], index: int, radius: int = 3) -> tuple[tuple[str, ...], tuple[str, ...]]:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    window = "\n".join(lines[start:end])
    constants = tuple(sorted(set(NUMBER_RE.findall(window))))
    tokens = tuple(sorted(set(match.group(1) for match in TOKEN_RE.finditer(window))))
    return constants, tokens


def _scan_file(relative_path: str, text: str) -> tuple[list[SourceLine], list[AssignmentContext]]:
    functions: list[SourceLine] = []
    assignments: list[AssignmentContext] = []
    lines = text.splitlines()

    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        if any(pattern.search(stripped) for pattern in FUNCTION_PATTERNS):
            functions.append(SourceLine(path=relative_path, line=line_number, text=stripped))

        assignment_match = ASSIGNMENT_RE.search(stripped)
        if assignment_match is None:
            continue

        field = assignment_match.group(1)
        constants, tokens = _collect_context_tokens(lines, line_number - 1)
        assignments.append(
            AssignmentContext(
                field=field,
                source_line=SourceLine(path=relative_path, line=line_number, text=stripped),
                constants=constants,
                tokens=tokens,
            )
        )

    return functions, assignments


def _group_assignments_by_field(assignments: list[AssignmentContext]) -> dict[str, list[AssignmentContext]]:
    grouped: dict[str, list[AssignmentContext]] = {field: [] for field in ANALOG_FIELDS}
    for item in assignments:
        grouped.setdefault(item.field, []).append(item)
    for field in grouped:
        grouped[field].sort(key=lambda entry: (entry.source_line.path, entry.source_line.line, entry.source_line.text))
    return grouped


def main() -> None:
    required_targets, optional_targets = _iter_scan_targets()

    scanned_files = 0
    missing_required: list[str] = []
    missing_optional: list[str] = []
    functions: list[SourceLine] = []
    assignments: list[AssignmentContext] = []

    for path in required_targets:
        text = _read_text(path)
        relative = str(path.relative_to(REPO_ROOT))
        if text is None:
            missing_required.append(relative)
            continue
        scanned_files += 1
        file_functions, file_assignments = _scan_file(relative, text)
        functions.extend(file_functions)
        assignments.extend(file_assignments)

    for path in optional_targets:
        text = _read_text(path)
        relative = str(path.relative_to(REPO_ROOT))
        if text is None:
            missing_optional.append(relative)
            continue
        scanned_files += 1
        file_functions, file_assignments = _scan_file(relative, text)
        functions.extend(file_functions)
        assignments.extend(file_assignments)

    functions.sort(key=lambda entry: (entry.path, entry.line, entry.text))
    grouped = _group_assignments_by_field(assignments)

    print(f"scanned_files={scanned_files}")
    if missing_required:
        print(f"missing_required_files={len(missing_required)}")
        for entry in sorted(missing_required):
            print(f"- {entry}")
    if missing_optional:
        print(f"missing_optional_files={len(missing_optional)}")
        for entry in sorted(missing_optional):
            print(f"- {entry}")

    print()
    print("functions_found:")
    for entry in functions:
        print(f"- {entry.render()}")

    print()
    print("analog_assignments:")
    for field in ANALOG_FIELDS:
        entries = grouped.get(field, [])
        print(f"{field}: count={len(entries)}")
        for assignment in entries:
            print(f"- {assignment.source_line.render()}")

    print()
    print("numeric_constants_near_assignments:")
    for field in ANALOG_FIELDS:
        entries = grouped.get(field, [])
        print(f"{field}:")
        for assignment in entries:
            constants = ", ".join(assignment.constants) if assignment.constants else "none"
            print(f"- {assignment.source_line.path}:{assignment.source_line.line}: constants={constants}")

    print()
    print("button_modifier_tokens_near_assignments:")
    for field in ANALOG_FIELDS:
        entries = grouped.get(field, [])
        print(f"{field}:")
        for assignment in entries:
            tokens = ", ".join(assignment.tokens) if assignment.tokens else "none"
            print(f"- {assignment.source_line.path}:{assignment.source_line.line}: tokens={tokens}")


if __name__ == "__main__":
    main()
