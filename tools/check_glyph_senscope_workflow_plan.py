#!/usr/bin/env python3
"""Read-only checker for the Glyph/Senscope workflow migration plan."""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_senscope_workflow_and_config_migration_plan_2026-05-27.md"
)

REQUIRED_ANCHORS = [
    ("current development workflow", "Current Development Workflow"),
    ("identity physical/logical policy", "Current Identity Physical/Logical Policy"),
    ("no gameplay protobuf/JSON parsing", "no protobuf/JSON parsing in gameplay frame loop"),
    ("compact runtime structs", "compact runtime structs in RAM"),
    ("O(1) lookup", "O(1) table lookup during gameplay"),
    ("Senscope integration level 0", "Level 0:"),
    ("Senscope integration level 1", "Level 1:"),
    ("Senscope integration level 2", "Level 2:"),
    ("Senscope integration level 3", "Level 3:"),
    ("closed-source Limit Labs configurator caveat", "Limit Labs webapp is closed-source"),
    ("lossy custom LT3 caveat", "observed lossy for custom LT3 import"),
    ("Senscope profile visualizer/writer", "Senscope profile visualizer/writer"),
    ("no flashing automation", "no firmware flashing automation"),
    ("no schema/proto changes in this branch", "no schema/proto changes in this branch"),
]


def _has(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()


def main() -> int:
    failures: list[str] = []

    if not DOC_PATH.exists():
        failures.append(f"missing doc: {DOC_PATH.relative_to(REPO_ROOT)}")
        text = ""
    else:
        text = DOC_PATH.read_text(encoding="utf-8")

    for label, needle in REQUIRED_ANCHORS:
        if not _has(text, needle):
            failures.append(f"missing anchor for {label}: {needle}")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    print(f"path={DOC_PATH.relative_to(REPO_ROOT)}")
    print("scope=workflow_plan_presence_only")
    print("planning_only=true")
    print("runtime_source_changes=false")
    print("profile_artifact_changes=false")
    print("schema_proto_configurator_changes=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
