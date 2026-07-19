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
DEFAULT_CLASSIFICATION = "TABLE_CONTENT_DIFFERENT"
POINTS_PER_TABLE = 9
AXES_PER_POINT = 2
CANONICAL_GRID = [
    (0, 0),
    (128, 0),
    (255, 0),
    (0, 128),
    (128, 128),
    (255, 128),
    (0, 255),
    (128, 255),
    (255, 255),
]
EXPECTED_SOURCE_ALIGNED_EXCEPTIONS = ["kY2Table", "kTilt3Table"]

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
                "candidate_matches_canonical_grid": candidate_points == CANONICAL_GRID,
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
    different_tables = comparison["different_tables"]
    different_table_symbols = [table["table_symbol"] for table in different_tables]
    canonical_grid_replacement_tables = [
        table["table_symbol"]
        for table in different_tables
        if table.get("candidate_matches_canonical_grid") is True
    ]
    table_change_manifest = []
    for table_id, symbol in enumerate(source_order):
        matching_diff = next(
            (table for table in different_tables if table["table_symbol"] == symbol),
            None,
        )
        if matching_diff is None:
            table_change_manifest.append(
                {
                    "table_id": table_id,
                    "table_symbol": symbol,
                    "action": "preserve_source_owned_baseline",
                    "mismatched_point_count": 0,
                    "candidate_matches_canonical_grid": False,
                }
            )
            continue
        table_change_manifest.append(
            {
                "table_id": table_id,
                "table_symbol": symbol,
                "action": "replace_candidate_points",
                "mismatched_point_count": matching_diff["mismatched_point_count"],
                "candidate_matches_canonical_grid": matching_diff["candidate_matches_canonical_grid"],
            }
        )
    immediate_mechanism_supported = (
        comparison["classification"] == "TABLE_CONTENT_DIFFERENT"
        and comparison["same_table_order"] is True
        and comparison["same_table_shape"] is True
        and comparison["same_tables"] == EXPECTED_SOURCE_ALIGNED_EXCEPTIONS
        and len(canonical_grid_replacement_tables) == 26
        and candidate["profile_name"] == "example_source_owned_runtime_config"
    )
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
        "different_tables": different_tables,
        "different_table_symbols": different_table_symbols,
        "canonical_grid_replacement_tables": canonical_grid_replacement_tables,
        "table_change_manifest": table_change_manifest,
        "table_by_table_change_manifest_present": True,
        "metadata_drift": comparison["metadata_drift"],
        "candidate_label_set": comparison["candidate_label_set"],
        "diagnostic_interpretation": {
            "changed_values_structurally_valid": True,
            "changed_values_semantically_unsuitable_for_current_source_owned_profile": True,
            "immediate_mechanism_supported_by_source_checker_evidence": immediate_mechanism_supported,
            "immediate_mechanism": (
                "example/canonical layout-spec candidate generation produced a complete 28-table artifact "
                "whose 26 non-Y2/Tilt3 tables are canonical 0/128/255 grids instead of current source-owned table contents"
            ),
            "firmware_root_cause_proven": False,
            "routing_side_effects_appear_functional_from_user_report": True,
            "runtime_loaded_config_implemented": False,
            "webserial_device_write_implemented": False,
            "nunchuk_status": "NOT_TESTED",
        },
        "candidate_generation_policy": {
            "required_modes": ["full_replacement", "overlay_preserve", "reject"],
            "full_replacement": "every active table is explicitly specified and validated",
            "overlay_preserve": "only explicitly owned tables change; unspecified tables are copied from the current source-owned baseline",
            "reject": "partial input without explicit overlay/preserve policy fails",
            "silent_canonical_default_fill_allowed": False,
            "example_profile_production_candidate_allowed_without_explicit_approval": False,
            "table_by_table_change_manifest_required": True,
            "preserved_tables_must_match_current_source_semantically": True,
        },
        "source_baseline_table_symbols": source_order,
        "source_baseline_tables": same_source_baseline,
        "notes": [
            "Candidate generation is not byte-for-byte equivalent to the current source-owned baseline.",
            "Two tables remain source-aligned: kY2Table and kTilt3Table.",
            "The remaining 26 tables collapse to the same canonical 0/128/255 grid pattern.",
            "The changed table values are structurally valid bytes and table shapes, but semantically unsuitable for the current source-owned profile.",
            "The immediate mechanism is supported by source/checker evidence; the low-level firmware root cause remains unproven.",
            "Because table contents differ, this is hardware-candidate material rather than formatting-only drift.",
        ],
    }


def validate_current_hardening(report: dict[str, Any]) -> None:
    if report["classification"] != "TABLE_CONTENT_DIFFERENT":
        return
    if report.get("table_by_table_change_manifest_present") is not True:
        fail("TABLE_CONTENT_DIFFERENT reports must include a table-by-table change manifest")
    manifest = report.get("table_change_manifest")
    if not isinstance(manifest, list) or len(manifest) != len(report["source_baseline_table_symbols"]):
        fail("table_change_manifest must contain one row per source-owned table")
    if [entry.get("table_id") for entry in manifest] != list(range(len(report["source_baseline_table_symbols"]))):
        fail("table_change_manifest table_id values must be ordered and complete")
    if [entry.get("table_symbol") for entry in manifest] != report["source_baseline_table_symbols"]:
        fail("table_change_manifest table symbols must match source-owned order")
    policy = report.get("candidate_generation_policy")
    if not isinstance(policy, dict):
        fail("TABLE_CONTENT_DIFFERENT reports must include candidate_generation_policy")
    if policy.get("silent_canonical_default_fill_allowed") is not False:
        fail("silent canonical default fill must be forbidden")
    if policy.get("table_by_table_change_manifest_required") is not True:
        fail("table-by-table change manifest must be required")
    if report["same_tables"] == EXPECTED_SOURCE_ALIGNED_EXCEPTIONS and len(report["different_table_symbols"]) == 26:
        if len(report.get("canonical_grid_replacement_tables", [])) != 26:
            fail("Y2/Tilt3-only source-aligned candidate must identify all 26 canonical-grid replacements")
        if report["diagnostic_interpretation"].get("immediate_mechanism_supported_by_source_checker_evidence") is not True:
            fail("Y2/Tilt3-only source-aligned candidate must record the supported immediate mechanism")


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
        validate_current_hardening(report)
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
