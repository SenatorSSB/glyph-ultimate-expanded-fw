#!/usr/bin/env python3
"""Validate Phase 7A offline parser fixtures against the source-owned baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from extract_glyph_identity_runtime_tables import load_source_tables, runtime_table_id_names
    from glyph_runtime_config_binary_roundtrip import decode_runtime_config_binary
    from glyph_runtime_config_candidate_generator import BIN_PATH, JSON_PATH, REPORT_PATH, VECTOR_PATH, build_valid_payload
    from glyph_runtime_config_parser_oracle import validate_vectors
except ModuleNotFoundError:
    from tools.extract_glyph_identity_runtime_tables import load_source_tables, runtime_table_id_names
    from tools.glyph_runtime_config_binary_roundtrip import decode_runtime_config_binary
    from tools.glyph_runtime_config_candidate_generator import BIN_PATH, JSON_PATH, REPORT_PATH, VECTOR_PATH, build_valid_payload
    from tools.glyph_runtime_config_parser_oracle import validate_vectors


REPO_ROOT = Path(__file__).resolve().parents[1]


class Phase7AEquivalenceError(ValueError):
    """Raised when Phase 7A parser fixtures drift."""


def fail(message: str) -> None:
    raise Phase7AEquivalenceError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return value


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    for path in (BIN_PATH, JSON_PATH, REPORT_PATH, VECTOR_PATH):
        if not path.exists():
            fail(f"missing required fixture: {path.relative_to(REPO_ROOT)}")

    expected_payload = build_valid_payload()
    actual_payload = BIN_PATH.read_bytes()
    if actual_payload != expected_payload:
        fail("valid baseline payload fixture does not regenerate from source-owned tables")

    decoded, issues = decode_runtime_config_binary(actual_payload)
    if issues:
        fail("valid baseline payload should decode without issues: " + ", ".join(issue.code for issue in issues))
    if decoded.table_order != list(runtime_table_id_names()):
        fail("decoded table order must match RuntimeTableId order")
    if decoded.table_count != 27 or decoded.point_count_per_table != 9:
        fail("decoded payload shape must be 27 tables x 9 points")
    if decoded.tables != {name: list(points) for name, points in load_source_tables().items()}:
        fail("decoded payload tables must equal source-owned 27-table baseline")
    for table_name, points in decoded.tables.items():
        for index, (x, y) in enumerate(points):
            if not 0 <= x <= 255 or not 0 <= y <= 255:
                fail(f"{table_name}[{index}] contains coordinate outside 0..255")

    payload_doc = load_json(JSON_PATH)
    report = load_json(REPORT_PATH)
    vectors = load_json(VECTOR_PATH)
    expected_sha = sha256_bytes(actual_payload)
    if payload_doc.get("payload_sha256") != expected_sha or report.get("payload_sha256") != expected_sha:
        fail("payload fixture/report sha256 must match binary")
    if payload_doc.get("table_order") != list(runtime_table_id_names()):
        fail("payload JSON table_order must match RuntimeTableId")
    if report.get("runtime_activation") is not False:
        fail("report must not claim runtime activation")
    if report.get("storage") is not False or report.get("device_write") is not False:
        fail("report must not claim storage or device write")
    if vectors.get("status") != "offline_parser_vectors_not_runtime_active":
        fail("vector corpus must stay offline/not runtime active")

    results = validate_vectors(VECTOR_PATH)
    accepted = [result for result in results if result["accepted"]]
    if [result["case_id"] for result in accepted] != ["valid_baseline_payload"]:
        fail("oracle must accept only the valid baseline vector")

    print("status=PASS")
    print(f"payload_sha256={expected_sha}")
    print(f"vectors={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
