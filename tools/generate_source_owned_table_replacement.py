#!/usr/bin/env python3
"""Retired historical literal-table replacement entry point.

The former 27-table literal-body contract is superseded.  This compatibility
entry point intentionally fails before reading input or writing output so a
historical packet cannot be mistaken for current source authority.
"""

from __future__ import annotations

import sys
from pathlib import Path


EXIT_SUPERSEDED = 1
SUPERSESSION_MESSAGE = (
    "SUPERSEDED: the 27-table literal-body replacement generator is retired. "
    "Use tools/source_owned_generator_modes.py with "
    "docs/runtime_config/generated_source_owned_generator_modes.md and "
    "tools/manage_source_owned_source_authority_intake.py with "
    "docs/runtime_config/source_authority_intake_workflow.md instead. "
    "This command does not read historical input, patch active source, or write output."
)


class SourceOwnedTableReplacementError(ValueError):
    """Raised when a caller reaches the superseded generator."""


def generate(_input_path: Path, _output_path: Path | None = None) -> str:
    """Fail closed without interpreting a historical packet or creating output."""

    raise SourceOwnedTableReplacementError(SUPERSESSION_MESSAGE)


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: generate_source_owned_table_replacement.py INPUT_JSON [OUTPUT_HPP]", file=sys.stderr)
        return 2
    try:
        generate(Path(argv[1]), Path(argv[2]) if len(argv) == 3 else None)
    except SourceOwnedTableReplacementError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_SUPERSEDED
    raise AssertionError("superseded generator unexpectedly returned")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
