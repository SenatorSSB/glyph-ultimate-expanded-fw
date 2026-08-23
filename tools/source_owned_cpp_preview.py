#!/usr/bin/env python3
"""Render validated source-owned v2 packets as inactive C++ review text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from source_owned_generator_modes import (
    GeneratorModesError,
    PRODUCTION_ALLOWED,
    TABLE_COUNT,
    POINTS_PER_TABLE,
    baseline_identity,
    canonical_json,
    digest,
    production_gate,
    tables_digest,
    _atomic_write_text,
    validate_offline_output_target,
    validate_manifest,
)

PREPARED_SCHEMA_VERSION = 1
EXPECTED_TARGET = "inert_source_owned_artifact_only"
PREVIEW_NAMESPACE = "glyph::runtime_config::source_owned_cpp_preview"


def _fail(message: str, category: str = "invalid_input") -> None:
    raise GeneratorModesError(message, category)


def _strict_object(label: str, value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(f"{label} has missing or unexpected fields", "integrity")
    return value


def _prepared_digest(packet: dict[str, Any]) -> str:
    body = dict(packet)
    body.pop("prepared_semantic_digest", None)
    return digest(body)


def validate_prepared_packet(packet: dict[str, Any], *, test_mode: bool = False) -> dict[str, Any]:
    _strict_object(
        "prepared packet",
        packet,
        {"schema_version", "artifact", "manifest", "target", "source_mutation", "prepared_semantic_digest"},
    )
    if packet["schema_version"] != PREPARED_SCHEMA_VERSION:
        _fail("unsupported prepared packet schema_version")
    if packet["prepared_semantic_digest"] != _prepared_digest(packet):
        _fail("prepared packet digest mismatch", "integrity")
    if packet["target"] != EXPECTED_TARGET or packet["source_mutation"] is not False:
        _fail("prepared packet is not an inert source-owned artifact", "source_authority")

    artifact = _strict_object(
        "prepared artifact",
        packet["artifact"],
        {"schema_version", "profile_id", "profile_name", "provenance_class", "generation_mode", "baseline", "table_shape", "tables", "artifact_semantic_digest", "generator_version"},
    )
    manifest = _strict_object(
        "prepared manifest",
        packet["manifest"],
        {"schema_version", "baseline", "input_profile_id", "input_semantic_digest", "generator_version", "artifact_semantic_digest", "rows", "changed_table_ids", "preserved_table_ids", "changed_table_count", "preserved_table_count", "classification", "manifest_semantic_digest"},
    )
    if artifact["schema_version"] != 1 or manifest["schema_version"] != 1:
        _fail("prepared artifact and manifest schemas must be version 1")
    shape = _strict_object("artifact table_shape", artifact["table_shape"], {"table_count", "points_per_table", "axes_per_point"})
    if shape != {"table_count": TABLE_COUNT, "points_per_table": POINTS_PER_TABLE, "axes_per_point": 2}:
        _fail("prepared artifact has unsupported table shape")
    actual_baseline = baseline_identity()
    if artifact["baseline"] != actual_baseline or manifest["baseline"] != actual_baseline:
        _fail("prepared baseline identity does not match the authoritative source", "baseline_mismatch")
    if manifest["artifact_semantic_digest"] != artifact["artifact_semantic_digest"]:
        _fail("prepared manifest/artifact digest mismatch", "integrity")
    manifest_body = dict(manifest)
    manifest_body.pop("manifest_semantic_digest", None)
    if manifest["manifest_semantic_digest"] != digest(manifest_body):
        _fail("manifest semantic digest mismatch", "integrity")
    if manifest["input_profile_id"] != artifact["profile_id"] or manifest["generator_version"] != artifact["generator_version"]:
        _fail("prepared manifest metadata mismatch", "integrity")
    row_keys = {"table_id", "table_symbol", "action", "explicit_ownership", "ownership_source", "provenance", "baseline_digest", "candidate_digest", "changed", "reason"}
    if not isinstance(manifest["rows"], list) or len(manifest["rows"]) != TABLE_COUNT:
        _fail("prepared manifest must contain exactly 28 rows")
    for row_id, row in enumerate(manifest["rows"]):
        _strict_object(f"manifest rows[{row_id}]", row, row_keys)
        if row["table_id"] != row_id or row["table_symbol"] != actual_baseline["table_order"][row_id]:
            _fail("prepared manifest row order or symbol is invalid")
    if not isinstance(artifact["tables"], list) or len(artifact["tables"]) != TABLE_COUNT:
        _fail("prepared artifact must contain exactly 28 tables")
    symbols: list[str] = []
    for table_id, table in enumerate(artifact["tables"]):
        table = _strict_object(f"artifact tables[{table_id}]", table, {"table_id", "table_symbol", "table_name", "points"})
        if table["table_id"] != table_id or not isinstance(table["table_symbol"], str) or not table["table_symbol"]:
            _fail("prepared table order or symbol is invalid")
        if not isinstance(table["points"], list) or len(table["points"]) != POINTS_PER_TABLE:
            _fail("prepared table must contain exactly nine points")
        for point_id, point in enumerate(table["points"], 1):
            _strict_object(f"artifact tables[{table_id}].points[{point_id}]", point, {"x", "y"})
            if any(not isinstance(point[axis], int) or isinstance(point[axis], bool) or not 0 <= point[axis] <= 255 for axis in ("x", "y")):
                _fail("prepared point coordinate is invalid")
        symbols.append(table["table_symbol"])
    if symbols != actual_baseline["table_order"]:
        _fail("prepared table symbols are not in canonical baseline order")
    if artifact["artifact_semantic_digest"] != tables_digest(artifact["tables"]):
        _fail("artifact semantic digest does not match table content", "integrity")
    if manifest["changed_table_count"] + manifest["preserved_table_count"] != TABLE_COUNT:
        _fail("prepared manifest counts do not cover all tables")
    validate_manifest(artifact, manifest)
    changed_rows = [row for row in manifest["rows"] if row["changed"]]
    changed_ids = [row["table_id"] for row in changed_rows]
    preserved_ids = [row["table_id"] for row in manifest["rows"] if not row["changed"]]
    if manifest["changed_table_ids"] != changed_ids or manifest["preserved_table_ids"] != preserved_ids:
        _fail("prepared manifest changed/preserved IDs do not match its rows", "integrity")
    if not changed_rows:
        expected_classification = "NO_OP"
    elif artifact["generation_mode"] == "full_replacement":
        expected_classification = "FULL_REPLACEMENT_CHANGESET"
    elif any(not row["explicit_ownership"] for row in changed_rows):
        expected_classification = "UNSAFE_UNOWNED_CHANGE"
    else:
        expected_classification = "EXPLICIT_OWNED_TABLE_CHANGESET"
    if manifest["classification"] != expected_classification:
        _fail("prepared manifest classification does not match its rows", "integrity")
    if artifact["provenance_class"] not in PRODUCTION_ALLOWED:
        if not test_mode or artifact["provenance_class"] != "synthetic_test":
            _fail("synthetic/example/unknown packets require explicit --test-mode", "source_authority")
    else:
        production_gate(artifact, manifest)
    if artifact["provenance_class"] == "source_baseline_derived" and manifest["classification"] != "NO_OP":
        _fail("source-baseline changes are not eligible for preview", "source_authority")
    if manifest["classification"] in {"SOURCE_AUTHORITY_BLOCKER", "UNSAFE_UNOWNED_CHANGE"}:
        _fail("prepared packet classification is not preview-eligible", "source_authority")
    return packet


def render_cpp_preview(packet: dict[str, Any], *, test_mode: bool = False) -> str:
    validate_prepared_packet(packet, test_mode=test_mode)
    artifact, manifest = packet["artifact"], packet["manifest"]
    lines = [
        "#pragma once",
        "",
        "#include <cstdint>",
        "",
        f"namespace {PREVIEW_NAMESPACE} {{",
        "",
        "// INACTIVE REVIEW PREVIEW: not production source and not wired into runtime selection.",
        f"// profile: {artifact['profile_id']} ({artifact['profile_name']})",
        f"// provenance: {artifact['provenance_class']}; classification: {manifest['classification']}",
        f"// artifact_semantic_digest: {artifact['artifact_semantic_digest']}",
        f"// manifest_semantic_digest: {manifest['manifest_semantic_digest']}",
        "static constexpr std::uint8_t kPreviewTables[28][9][2] = {",
    ]
    for table in artifact["tables"]:
        lines.append(f"    {{  // {table['table_id']} {table['table_symbol']}")
        for point in table["points"]:
            lines.append(f"        {{{point['x']}u, {point['y']}u}},")
        lines.append("    },")
    lines.extend(["};", "", f"}}  // namespace {PREVIEW_NAMESPACE}", ""])
    return "\n".join(lines)


def write_preview(packet: dict[str, Any], target: Path, *, test_mode: bool = False) -> None:
    validate_offline_output_target(target, purpose="preview")
    _atomic_write_text(target, render_cpp_preview(packet, test_mode=test_mode), purpose="preview")
