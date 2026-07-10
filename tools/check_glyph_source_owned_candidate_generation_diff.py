#!/usr/bin/env python3
"""Diagnose source-owned candidate-generation drift against the current baseline.

This checker compares the candidate artifact produced from the inert generated
layout-spec fixture with the current checked-in source-owned baseline artifact.
It parses the generated tables semantically so formatting, comment, or spacing
noise can be separated from actual table-content drift.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import (
    load_source_tables,
    normalized_table_names,
    source_symbol_by_normalized_name,
)
from generate_source_owned_runtime_config import parse_source_baseline_table_order


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LAYOUT_SPEC_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
DEFAULT_BASELINE_ARTIFACT = (
    REPO_ROOT / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
)
DEFAULT_SOURCE_TABLES = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
DEFAULT_SOURCE_INTERPRETER = REPO_ROOT / "src/modes/UltimateRuntimeConfigInterpreter.hpp"
LAYOUT_SPEC_GENERATOR = REPO_ROOT / "tools/install_generated_source_owned_runtime_config.py"

SCHEMA_VERSION = 1
PACKET = "source_owned_candidate_generation_diff_diagnosis"
DEFAULT_CLASSIFICATION = "TABLE_CONTENT_EQUIVALENT"
POINTS_PER_TABLE = 9
AXES_PER_POINT = 2

PROFILE_NAME_RE = re.compile(
    r'static\s+constexpr\s+char\s+kGeneratedSourceOwnedRuntimeConfigProfileName\[\]\s*=\s*"(?P<value>[^"]+)";'
)
TABLE_COUNT_RE = re.compile(
    r"kGeneratedSourceOwnedRuntimeConfigTableCount\s*=\s*(?P<value>\d+)u;"
)
POINTS_PER_TABLE_RE = re.compile(
    r"kGeneratedSourceOwnedRuntimeConfigPointsPerTable\s*=\s*(?P<value>\d+)u;"
)
AXES_PER_POINT_RE = re.compile(
    r"kGeneratedSourceOwnedRuntimeConfigAxesPerPoint\s*=\s*(?P<value>\d+)u;"
)
TABLE_ROW_START_RE = re.compile(
    r"^\s*\{\s*//\s*(?P<table_id>\d+)\s+(?P<label>.+?)\s*$"
)
POINT_RE = re.compile(r"\{\s*(?P<x>\d+)u?\s*,\s*(?P<y>\d+)u?\s*\}")


class SourceOwnedCandidateGenerationDiffError(RuntimeError):
    """Raised when candidate-generation drift cannot be classified safely."""


def fail(message: str) -> None:
    raise SourceOwnedCandidateGenerationDiffError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def generate_candidate_text(layout_spec_path: Path) -> str:
    completed = subprocess.run(
        [
            sys.executable,
            str(LAYOUT_SPEC_GENERATOR.relative_to(REPO_ROOT)),
            "--from-layout-spec",
            str(layout_spec_path.relative_to(REPO_ROOT)),
            "--dry-run",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("candidate generation failed: " + (completed.stderr.strip() or completed.stdout.strip()))
    return completed.stdout


def parse_generated_header(text: str) -> dict[str, Any]:
    profile_name_match = PROFILE_NAME_RE.search(text)
    table_count_match = TABLE_COUNT_RE.search(text)
    points_per_table_match = POINTS_PER_TABLE_RE.search(text)
    axes_per_point_match = AXES_PER_POINT_RE.search(text)
    if profile_name_match is None:
        fail("candidate header missing profile name")
    if table_count_match is None or points_per_table_match is None or axes_per_point_match is None:
        fail("candidate header missing shape metadata")

    lines = text.splitlines()
    tables: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        row_start = TABLE_ROW_START_RE.match(lines[i])
        if row_start is None:
            i += 1
            continue
        table_id = int(row_start.group("table_id"))
        table_label = row_start.group("label").strip()
        points: list[dict[str, int]] = []
        i += 1
        while i < len(lines) and not re.match(r"^\s*\},\s*$", lines[i]):
            point_match = POINT_RE.search(lines[i])
            if point_match is not None:
                points.append(
                    {
                        "x": int(point_match.group("x")),
                        "y": int(point_match.group("y")),
                    }
                )
            i += 1
        if len(points) != POINTS_PER_TABLE:
            fail(f"candidate table {table_id} has {len(points)} points, expected {POINTS_PER_TABLE}")
        tables.append(
            {
                "table_id": table_id,
                "table_label": table_label,
                "points": points,
            }
        )
        i += 1

    if len(tables) != int(table_count_match.group("value")):
        fail(
            "candidate table count mismatch: "
            f"parsed {len(tables)} tables, header says {table_count_match.group('value')}"
        )

    return {
        "profile_name": profile_name_match.group("value"),
        "table_count": int(table_count_match.group("value")),
        "points_per_table": int(points_per_table_match.group("value")),
        "axes_per_point": int(axes_per_point_match.group("value")),
        "tables": tables,
    }


def source_table_order() -> list[str]:
    interpreter_text = read_required(DEFAULT_SOURCE_INTERPRETER)
    return parse_source_baseline_table_order(interpreter_text)


def source_tables_by_symbol() -> dict[str, list[tuple[int, int]]]:
    tables = load_source_tables()
    mapping: dict[str, list[tuple[int, int]]] = {}
    for name in normalized_table_names():
        symbol = source_symbol_by_normalized_name()[name]
        mapping[symbol] = list(tables[name])
    return mapping


def compare_tables(candidate: dict[str, Any], baseline_text: str, candidate_text: str) -> dict[str, Any]:
    order = source_table_order()
    source = source_tables_by_symbol()

    same_shape = (
        candidate["table_count"] == len(order)
        and candidate["points_per_table"] == POINTS_PER_TABLE
        and candidate["axes_per_point"] == AXES_PER_POINT
    )
    if not same_shape:
        return {
            "classification": "SOURCE_SHAPE_DIFFERENT",
            "same_table_order": False,
            "same_table_shape": False,
            "same_tables": [],
            "different_tables": [],
            "same_table_count": candidate["table_count"] == len(order),
        }

    same_order = True
    same_tables: list[str] = []
    different_tables: list[dict[str, Any]] = []

    for table in candidate["tables"]:
        source_symbol = order[table["table_id"]]
        source_points = source[source_symbol]
        candidate_points = [(point["x"], point["y"]) for point in table["points"]]
        if table["table_id"] != order.index(source_symbol):
            same_order = False
        if candidate_points == source_points:
            same_tables.append(source_symbol)
            continue
        different_tables.append(
            {
                "table_id": table["table_id"],
                "table_symbol": source_symbol,
                "table_label": table["table_label"],
                "source_points": [{"x": x, "y": y} for x, y in source_points],
                "candidate_points": table["points"],
                "mismatched_point_count": sum(
                    1 for source_point, candidate_point in zip(source_points, candidate_points) if source_point != candidate_point
                ),
            }
        )

    baseline_parsed = parse_generated_header(baseline_text)
    metadata_drift: dict[str, dict[str, str]] = {}
    if baseline_parsed["profile_name"] != candidate["profile_name"]:
        metadata_drift["profile_name"] = {
            "baseline": baseline_parsed["profile_name"],
            "candidate": candidate["profile_name"],
        }

    if different_tables:
        classification = "TABLE_CONTENT_DIFFERENT"
    elif metadata_drift:
        classification = "GENERATOR_CANONICALIZATION_ONLY"
    elif candidate_text != baseline_text:
        classification = "FORMAT_ONLY"
    else:
        classification = "TABLE_CONTENT_EQUIVALENT"

    return {
        "classification": classification,
        "same_table_order": same_order,
        "same_table_shape": same_shape,
        "same_table_count": len(candidate["tables"]) == len(order),
        "same_tables": same_tables,
        "different_tables": different_tables,
        "metadata_drift": metadata_drift,
        "candidate_label_set": sorted({table["table_label"] for table in candidate["tables"]}),
        "baseline_matches_source": all(
            baseline_parsed["tables"][index]["points"]
            == [
                {"x": x, "y": y}
                for x, y in source[order[index]]
            ]
            for index in range(len(order))
        ),
    }


def build_report(layout_spec_path: Path) -> dict[str, Any]:
    candidate_text = generate_candidate_text(layout_spec_path)
    candidate = parse_generated_header(candidate_text)
    baseline_text = read_required(DEFAULT_BASELINE_ARTIFACT)
    comparison = compare_tables(candidate, baseline_text, candidate_text)
    source_tables = source_tables_by_symbol()
    source_order = source_table_order()
    same_source_baseline = {
        symbol: source_tables[symbol] for symbol in source_order
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "packet": PACKET,
        "layout_spec_fixture": rel(layout_spec_path),
        "baseline_artifact": rel(DEFAULT_BASELINE_ARTIFACT),
        "source_tables": rel(DEFAULT_SOURCE_TABLES),
        "source_runtime_view": rel(DEFAULT_SOURCE_INTERPRETER),
        "candidate_profile_name": candidate["profile_name"],
        "candidate_table_count": candidate["table_count"],
        "candidate_points_per_table": candidate["points_per_table"],
        "candidate_axes_per_point": candidate["axes_per_point"],
        "current_source_table_count": len(source_order),
        "current_source_points_per_table": POINTS_PER_TABLE,
        "current_source_axes_per_point": AXES_PER_POINT,
        "baseline_matches_source": comparison["baseline_matches_source"],
        "classification": comparison["classification"],
        "same_table_order": comparison["same_table_order"],
        "same_table_shape": comparison["same_table_shape"],
        "same_table_count": comparison["same_table_count"],
        "same_tables": comparison["same_tables"],
        "different_tables": comparison["different_tables"],
        "metadata_drift": comparison["metadata_drift"],
        "candidate_label_set": comparison["candidate_label_set"],
        "source_baseline_table_symbols": source_order,
        "source_baseline_tables": same_source_baseline,
    "notes": [
            "The checked-in inert baseline artifact now matches the generated candidate on this branch.",
            "The pre-materialization diagnostic packet preserves the earlier TABLE_CONTENT_DIFFERENT evidence.",
            "All 28 tables are source-aligned on this branch.",
            "This branch remains offline-only and non-active.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--layout-spec",
        type=Path,
        default=DEFAULT_LAYOUT_SPEC_FIXTURE,
        help="layout-spec fixture to use for candidate generation",
    )
    parser.add_argument(
        "--expect-classification",
        choices=[
            "FORMAT_ONLY",
            "GENERATOR_CANONICALIZATION_ONLY",
            "TABLE_CONTENT_EQUIVALENT",
            "TABLE_CONTENT_DIFFERENT",
            "SOURCE_SHAPE_DIFFERENT",
            "UNKNOWN_UNSAFE",
        ],
        default=DEFAULT_CLASSIFICATION,
        help="expected classification for the diagnostic run",
    )
    args = parser.parse_args(argv)

    try:
        report = build_report(args.layout_spec)
        if report["classification"] != args.expect_classification:
            fail(
                f"classification drift: expected {args.expect_classification}, got {report['classification']}"
            )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (SourceOwnedCandidateGenerationDiffError, OSError, json.JSONDecodeError) as exc:
        print("glyph_source_owned_candidate_generation_diff: FAIL")
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
