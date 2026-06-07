#!/usr/bin/env python3
"""Offline checker for runtime-config binary preview and invalid corpus."""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

try:
    from extract_glyph_identity_runtime_tables import runtime_table_id_names
except ModuleNotFoundError:
    from tools.extract_glyph_identity_runtime_tables import runtime_table_id_names
from glyph_runtime_config_binary_roundtrip import (
    BINARY_MAGIC,
    BINARY_SCHEMA_NAME,
    BINARY_SCHEMA_VERSION,
    BINARY_FORMAT_VERSION,
    build_runtime_config_binary,
    decode_runtime_config_binary,
    load_source_tables,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED_DOC_PATH = REPO_ROOT / "docs" / "runtime_config" / "runtime_config_binary_representation_design.md"
PREVIEW_PATH = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "current_baseline_runtime_config_binary_preview.json"
INVALID_PATH = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "invalid_runtime_config_binary_cases.json"
BINARY_PATH = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "current_baseline_runtime_config_binary_preview.bin"

SOURCE_AUTHORITY_FIXTURE = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "current_baseline_runtime_config_semantics_bridge.json"
PREVIEW_SOURCE_FIXTURE = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "current_baseline_extracted_config_preview.json"

REQUIRED_DOC_PHRASES = (
    "offline-only deterministic binary preview",
    "do not modify firmware source",
    "no firmware runtime-config consumption",
    "no protobuf",
    "Explicit stop line",
    "before Step 13 firmware binary/protobuf parser integration",
)

EXPECTED_PREVIEW_FIELDS = {
    "artifact_id": "current_baseline_runtime_config_binary_preview_v1",
    "schema_name": BINARY_SCHEMA_NAME,
    "schema_version": BINARY_SCHEMA_VERSION,
    "status": "offline_preview_not_runtime_loaded",
    "mode_scope": "MODE_ULTIMATE",
    "runtime_loaded_config": False,
    "consumed_by_firmware": False,
    "transport_authority": "none",
}
EXPECTED_SOURCE_AUTHORITY_CLASSIFICATION = "source_backed_current_baseline_preview_only"
EXPECTED_SOURCE_REFERENCES = {
    "src/modes/Ultimate.cpp": "d54f082601697d6c47925b56dbb81e1bcb3636829266bf61b7f2dc8856372706",
    "src/modes/UltimateIdentityRuntimeTables.hpp": "138887f00ea51ac791dbca0e725a3c85f393b8be48bdac2f78dfd88d90819400",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp": "ce694ab1f656145742b2e657c2960a813bfa115a0d787a11f43df438eefe1a2f",
    "tools/extract_glyph_identity_runtime_tables.py": "e7d9bfd18cfd469d5f030d53628bfb9dd74d3c14b5f04ef533f6c7f8b8aa7bad",
}


class BinaryOfflineRoundtripError(ValueError):
    """Raised when the offline binary roundtrip contract is not valid."""


def fail(message: str) -> None:
    raise BinaryOfflineRoundtripError(message)


def sha256_file(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def load_json_object(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def validate_design_doc() -> None:
    if not REQUIRED_DOC_PATH.exists():
        fail(f"missing design doc: {REQUIRED_DOC_PATH.relative_to(REPO_ROOT)}")

    lowered = REQUIRED_DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"design doc missing required phrase: {phrase}")


def validate_preview_doc(preview: dict[str, Any], baseline_binary: bytes) -> dict[str, Any]:
    for key, expected in EXPECTED_PREVIEW_FIELDS.items():
        if preview.get(key) != expected:
            fail(f"preview.{key} must be {expected!r}")

    source_authority = preview.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("preview.source_authority must be an object")
    if source_authority.get("classification") != EXPECTED_SOURCE_AUTHORITY_CLASSIFICATION:
        fail("preview.source_authority.classification mismatch")

    references = source_authority.get("references")
    if not isinstance(references, list):
        fail("preview.source_authority.references must be a list")

    seen_paths = set()
    for entry in references:
        if not isinstance(entry, dict):
            fail("source_authority.references entries must be objects")
        path = entry.get("path")
        sha = entry.get("sha256")
        if not isinstance(path, str) or not path:
            fail("source reference entries must include path")
        if not isinstance(sha, str) or len(sha) != 64:
            fail(f"source reference {path!r} must include a valid sha256")
        expected_hash = EXPECTED_SOURCE_REFERENCES.get(path)
        if expected_hash is None:
            fail(f"unexpected source reference path: {path}")
        if sha != expected_hash:
            fail(f"source reference {path} sha mismatch; expected {expected_hash!r}")
        actual_hash = sha256_file(REPO_ROOT / path)
        if actual_hash != sha:
            fail(f"source reference {path} does not match file contents")
        seen_paths.add(path)

    if set(EXPECTED_SOURCE_REFERENCES) - seen_paths:
        fail("source_authority references missing required path(s)")

    artifact = preview.get("binary_artifact")
    if not isinstance(artifact, dict):
        fail("preview.binary_artifact must be an object")
    if artifact.get("path") != "docs/runtime_config/fixtures/current_baseline_runtime_config_binary_preview.bin":
        fail("preview.binary_artifact.path must point to the baseline binary fixture")
    if artifact.get("format") != "raw_binary_glyph_runtime_config":
        fail("preview.binary_artifact.format must be raw_binary_glyph_runtime_config")
    if artifact.get("magic") != BINARY_MAGIC.decode("ascii"):
        fail("preview.binary_artifact.magic must be GCFG")
    if artifact.get("format_version") != BINARY_FORMAT_VERSION:
        fail("preview.binary_artifact.format_version must be 1")
    if artifact.get("table_count") != 27 or artifact.get("point_count_per_table") != 9:
        fail("preview.binary_artifact table_count and point_count_per_table must be 27/9")
    if artifact.get("table_order") != list(runtime_table_id_names()):
        fail("preview.binary_artifact.table_order must match canonical table ids")

    expected_size = len(baseline_binary)
    if artifact.get("size_bytes") != expected_size:
        fail(f"preview.binary_artifact.size_bytes must be {expected_size}")
    expected_sha = sha256_file(BINARY_PATH)
    if artifact.get("sha256") != expected_sha:
        fail("preview.binary_artifact.sha256 must match binary fixture")

    source_refs = preview.get("source_baseline_references", {})
    if source_refs.get("source_preview") != str(PREVIEW_SOURCE_FIXTURE.relative_to(REPO_ROOT)):
        fail("preview.source_baseline_references.source_preview must reference extracted preview fixture")
    if source_refs.get("interpreter_baseline") != str(SOURCE_AUTHORITY_FIXTURE.relative_to(REPO_ROOT)):
        fail("preview.source_baseline_references.interpreter_baseline must reference semantics bridge baseline")

    caveats = preview.get("caveats")
    if not isinstance(caveats, list):
        fail("preview.caveats must be a list")
    required_caveats = {"not_runtime_loaded_config", "not_device_write", "not_webserial", "not_firmware_consumption"}
    if not required_caveats.issubset(set(caveats)):
        fail("preview.caveats missing required non-goal markers")

    return artifact


def validate_binary_roundtrip(binary_data: bytes) -> None:
    source_tables = load_source_tables()
    encoded = build_runtime_config_binary(source_tables)
    if encoded != binary_data:
        fail("baseline binary does not encode exactly from current source tables")

    decoded, issues = decode_runtime_config_binary(binary_data)
    if issues:
        fail("baseline binary should decode without issues: " + "; ".join(issue.code for issue in issues))
    if decoded.table_count != 27 or decoded.point_count_per_table != 9:
        fail("decoded baseline table_count/point_count must be 27/9")
    if decoded.table_order != list(runtime_table_id_names()):
        fail("decoded baseline table_order must match canonical table id order")


def validate_invalid_corpus(preview: dict[str, Any]) -> None:
    invalid = load_json_object(INVALID_PATH)
    if invalid.get("schema_name") != "glyph_runtime_config_binary_invalid_corpus":
        fail("invalid fixture schema_name must be glyph_runtime_config_binary_invalid_corpus")
    if invalid.get("schema_version") != 1:
        fail("invalid fixture schema_version must be 1")

    cases = require_list(invalid.get("cases"), "invalid.cases")
    if not cases:
        fail("invalid cases must not be empty")
    required_invalid_classes = require_list(
        invalid.get("required_invalid_classes"),
        "invalid.required_invalid_classes",
    )
    observed_classes = {case.get("invalid_class") for case in cases if isinstance(case, dict)}
    if set(required_invalid_classes) - observed_classes:
        missing = sorted(set(required_invalid_classes) - observed_classes)
        fail("invalid fixture missing required_invalid_classes: " + ", ".join(missing))
    for case in cases:
        invalid_class = case.get("invalid_class")
        if invalid_class not in required_invalid_classes:
            fail(f"case {case.get('case_id')} has invalid_class not listed in required_invalid_classes")

    binary_artifact = preview.get("binary_artifact", {})
    if not isinstance(binary_artifact, dict):
        fail("preview.binary_artifact must be present for invalid corpus checks")
    expected_path = binary_artifact.get("path")

    if expected_path != BINARY_PATH.relative_to(REPO_ROOT).as_posix():
        fail("invalid fixture baseline path must match preview binary artifact path")

    for case in cases:
        case_id = case.get("case_id")
        expected = require_list(case.get("expected_error_codes"), f"{case_id}.expected_error_codes")
        if not case_id or not isinstance(case_id, str):
            fail("each invalid case must have a case_id")
        mutated_hex = case.get("payload_hex")
        if not isinstance(mutated_hex, str) or not mutated_hex:
            fail(f"{case_id} must include payload_hex")
        try:
            payload = bytes.fromhex(mutated_hex)
        except ValueError as exc:
            fail(f"{case_id} payload_hex is not valid hex: {exc}")

        _, issues = decode_runtime_config_binary(payload)
        if not issues:
            fail(f"{case_id} unexpectedly decoded without issues")
        actual_codes = sorted({issue.code for issue in issues})
        missing = sorted(set(expected) - set(actual_codes))
        if missing:
            fail(f"{case_id} missing expected codes: {', '.join(missing)}")


def main() -> int:
    print("glyph_runtime_config_binary_offline_roundtrip")
    try:
        validate_design_doc()
        binary_payload = BINARY_PATH.read_bytes()
        preview = load_json_object(PREVIEW_PATH)
        validate_preview_doc(preview, binary_payload)
        validate_binary_roundtrip(binary_payload)
        validate_invalid_corpus(preview)
        print("status=PASS")
        return 0
    except (OSError, ValueError, BinaryOfflineRoundtripError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
