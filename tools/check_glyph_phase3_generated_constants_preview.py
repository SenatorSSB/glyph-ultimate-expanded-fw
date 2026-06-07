#!/usr/bin/env python3
"""Validate the Phase 3 generated constants dry-run preview artifact.

This checker is read-only and stdlib-only. It validates the preview contract,
preview artifact, source-backed hashes, and source table summary without
touching firmware, hardware, or build outputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import (
    DEFAULT_SOURCE_PATH,
    load_source_tables,
    normalized_table_names,
    source_symbol_by_normalized_name,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DOC_PATH = REPO_ROOT / "docs" / "generated_constants" / "phase3_generated_constants_contract.md"
PREVIEW_PATH = REPO_ROOT / "docs" / "generated_constants" / "preview" / "gfw3_generated_constants_preview.json"

REQUIRED_DOC_PHRASES = (
    "Phase 3 steps 1-4",
    "Source-diff checker contract",
    "product approval gate before firmware source integration",
    "build gate for any later firmware-integration branch",
    "hardware test gate for any later firmware-integration branch",
    "Phase 3 steps 1-4",
)

EXPECTED_PREVIEW_TOP_LEVEL = {
    "artifact_id": "gfw3_generated_constants_preview_2026-06-07",
    "artifact_kind": "DRY_RUN_PREVIEW",
    "generated_for_phase": 3,
    "consumed_by_firmware": False,
    "status": "preview_only_not_wired",
}

EXPECTED_SOURCE_AUTHORITY_CLASSIFICATION = "source_backed_current_baseline_preview_only"
EXPECTED_SOURCE_REFERENCES = {
    "src/modes/Ultimate.cpp": {
        "role": "current_baseline_source",
        "sha256": "7911d4460428df789a43ff77e3180046bfee39321dc8aea4f997a517b8362fec",
    },
    "src/modes/UltimateIdentityRuntimeTables.hpp": {
        "role": "approved_step6_firmware_integration_target",
        "sha256": "138887f00ea51ac791dbca0e725a3c85f393b8be48bdac2f78dfd88d90819400",
    },
    "tools/extract_glyph_identity_runtime_tables.py": {
        "role": "source_table_extractor",
        "sha256": "bb7abee75f597dec9e6380f3e68e1bca1b4c026f0b407f51408277f6ace80dc2",
    },
    "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json": {
        "role": "generated_config_baseline",
        "sha256": "d66efa458cc28921d3a1ccb0682e8486d880c3d3fe77260a19cc3e0afa63006f",
    },
    "docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt": {
        "role": "generated_cpp_baseline",
        "sha256": "3d8ac50a5dfcff3ff529fb3cb1888e4c62afaeebd04b82977e8653adab99d9b9",
    },
}
EXPECTED_SOURCE_UNKNOWNS = {
    "future firmware-path details beyond step 6",
    "future product approval decision",
    "future build and hardware result outcome",
}
EXPECTED_TARGET_FILE_CLASSES = {
    "docs/generated_constants/phase3_generated_constants_contract.md": (
        "phase3_contract_doc",
        "docs_only",
    ),
    "docs/generated_constants/preview/gfw3_generated_constants_preview.json": (
        "phase3_preview_artifact",
        "docs_only",
    ),
    "tools/check_glyph_phase3_generated_constants_preview.py": (
        "phase3_checker",
        "docs_only",
    ),
    "src/modes/UltimateIdentityRuntimeTables.hpp": (
        "current_firmware_integration_target",
        "approved_step6_reference_only",
    ),
    "include/generated/glyph_generated_constants.hpp": (
        "future_generated_constants_header",
        "proposed_future_candidate_only",
    ),
    "src/generated/glyph_generated_constants.cpp": (
        "future_generated_constants_source",
        "proposed_future_candidate_only",
    ),
}
EXPECTED_CAVEATS = {
    "not_runtime_loaded_config",
    "not_device_write",
    "not_protobuf_binary_write",
    "not_firmware_source",
    "not_consumed_by_firmware",
    "not_universal_official_compatibility_claim",
    "not_nunchuk_validation_claim",
}
EXPECTED_CONSTANTS_PREVIEW = {
    "table_family": "StickPoint",
    "table_count": 27,
    "point_count_per_table": 9,
    "value_representation": "current_baseline_source_summary",
}
EXPECTED_COMPARISON_CONTRACT = {
    "source_diff_mode": "preview_against_source_backed_baseline",
    "failure_mode": "fail_closed_when_authority_missing_or_inferred",
}
EXPECTED_REQUIRED_PASS_CONDITIONS = {
    "source_reference_hashes_match",
    "table_names_match_source",
    "table_point_counts_match_source",
    "source_symbols_match_source",
    "preview_consumed_by_firmware_false",
    "no_runtime_loaded_config_claim",
    "no_device_write_claim",
}
EXPECTED_FORBIDDEN_DIFFS = {
    "src_or_include_wiring_active",
    "runtime_loaded_config_claim",
    "device_write_claim",
    "protobuf_binary_write_claim",
    "firmware_behavior_change_claim",
    "profile_schema_change_claim",
    "nunchuk_validation_claim",
    "universal_compatibility_claim",
}
EXPECTED_ALLOWED_PREVIEW_ONLY_DIFFS = {
    "docs_only_artifact_paths",
    "provisional_future_target_file_names",
    "summary_only_value_representation",
    "source_backed_hash_provenance",
}


class Phase3PreviewError(ValueError):
    """Raised when the Phase 3 preview contract is not trustworthy."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise Phase3PreviewError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be an object: {display(path)}")
    return payload


def validate_contract_doc() -> None:
    if not CONTRACT_DOC_PATH.exists():
        fail(f"missing contract doc: {display(CONTRACT_DOC_PATH)}")
    text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"contract doc missing required phrase: {phrase}")


def validate_source_references(source_authority: dict[str, Any]) -> None:
    if source_authority.get("classification") != EXPECTED_SOURCE_AUTHORITY_CLASSIFICATION:
        fail("source_authority.classification must be source-backed preview-only")

    refs = source_authority.get("references")
    if not isinstance(refs, list):
        fail("source_authority.references must be a list")

    seen_paths: set[str] = set()
    for ref in refs:
        if not isinstance(ref, dict):
            fail("source_authority.references entries must be objects")
        path = ref.get("path")
        role = ref.get("role")
        sha256 = ref.get("sha256")
        if not isinstance(path, str) or not path:
            fail("source_authority.references entries must include path")
        if not isinstance(role, str) or not role:
            fail(f"{path} must include role")
        if not isinstance(sha256, str) or len(sha256) != 64:
            fail(f"{path} must include sha256")
        expected = EXPECTED_SOURCE_REFERENCES.get(path)
        if expected is None:
            fail(f"unexpected source reference: {path}")
        if expected["role"] != role:
            fail(f"{path} role must be {expected['role']!r}")
        actual_hash = sha256_file(REPO_ROOT / path)
        if actual_hash != sha256:
            fail(f"{path} sha256 does not match current file")
        if sha256 != expected["sha256"]:
            fail(f"{path} sha256 does not match committed baseline hash")
        seen_paths.add(path)

    missing = sorted(set(EXPECTED_SOURCE_REFERENCES) - seen_paths)
    if missing:
        fail("source_authority.references missing required path(s): " + ", ".join(missing))

    unknowns = source_authority.get("unknowns")
    if not isinstance(unknowns, list) or not all(isinstance(item, str) for item in unknowns):
        fail("source_authority.unknowns must be a string list")
    if set(unknowns) != EXPECTED_SOURCE_UNKNOWNS:
        fail("source_authority.unknowns must exactly match the recorded unknowns")


def validate_target_file_classes(target_file_classes: list[Any]) -> None:
    if not isinstance(target_file_classes, list):
        fail("target_file_classes must be a list")

    seen_paths: set[str] = set()
    for entry in target_file_classes:
        if not isinstance(entry, dict):
            fail("target_file_classes entries must be objects")
        path = entry.get("path")
        class_name = entry.get("class")
        state = entry.get("state")
        if not isinstance(path, str) or not path:
            fail("target_file_classes entries must include path")
        if not isinstance(class_name, str) or not class_name:
            fail(f"{path} must include class")
        if not isinstance(state, str) or not state:
            fail(f"{path} must include state")
        expected = EXPECTED_TARGET_FILE_CLASSES.get(path)
        if expected is None:
            fail(f"unexpected target file class path: {path}")
        expected_class, expected_state = expected
        if expected_class != class_name:
            fail(f"{path} class must be {expected_class!r}")
        if expected_state != state:
            fail(f"{path} state must be {expected_state!r}")
        seen_paths.add(path)

    missing = sorted(set(EXPECTED_TARGET_FILE_CLASSES) - seen_paths)
    if missing:
        fail("target_file_classes missing required path(s): " + ", ".join(missing))


def validate_caveats(caveats: list[Any]) -> None:
    if not isinstance(caveats, list) or not all(isinstance(item, str) for item in caveats):
        fail("preview_caveats must be a string list")
    missing = sorted(EXPECTED_CAVEATS - set(caveats))
    if missing:
        fail("preview_caveats missing required value(s): " + ", ".join(missing))


def validate_constants_preview(constants_preview: dict[str, Any]) -> None:
    for key, expected in EXPECTED_CONSTANTS_PREVIEW.items():
        if constants_preview.get(key) != expected:
            fail(f"constants_preview.{key} must be {expected!r}")

    tables = constants_preview.get("tables")
    if not isinstance(tables, list):
        fail("constants_preview.tables must be a list")

    source_names = normalized_table_names()
    source_symbols = source_symbol_by_normalized_name()
    source_tables = load_source_tables(DEFAULT_SOURCE_PATH)

    if len(tables) != len(source_names):
        fail(f"constants_preview.tables must contain {len(source_names)} entries")

    for index, expected_name in enumerate(source_names):
        entry = tables[index]
        if not isinstance(entry, dict):
            fail("constants_preview.tables entries must be objects")
        name = entry.get("name")
        source_symbol = entry.get("source_symbol")
        point_count = entry.get("point_count")
        shape = entry.get("shape")
        value_source = entry.get("value_source")
        if name != expected_name:
            fail(f"constants_preview.tables[{index}].name must be {expected_name!r}")
        expected_symbol = source_symbols[expected_name]
        if source_symbol != expected_symbol:
            fail(f"constants_preview.tables[{index}].source_symbol must be {expected_symbol!r}")
        if point_count != len(source_tables[expected_name]):
            fail(f"constants_preview.tables[{index}].point_count must be {len(source_tables[expected_name])}")
        if shape != "StickPoint[9]":
            fail(f"constants_preview.tables[{index}].shape must be 'StickPoint[9]'")
        if value_source != "src/modes/Ultimate.cpp":
            fail(f"constants_preview.tables[{index}].value_source must be src/modes/Ultimate.cpp")
        if any(key in entry for key in ("points", "values", "table_values")):
            fail(f"constants_preview.tables[{index}] must not embed raw point arrays in this summary preview")


def validate_comparison_contract(comparison_contract: dict[str, Any]) -> None:
    if comparison_contract.get("source_diff_mode") != EXPECTED_COMPARISON_CONTRACT["source_diff_mode"]:
        fail("comparison_contract.source_diff_mode must be preview_against_source_backed_baseline")
    if comparison_contract.get("failure_mode") != EXPECTED_COMPARISON_CONTRACT["failure_mode"]:
        fail("comparison_contract.failure_mode must fail closed when authority is missing or inferred")

    required_pass_conditions = comparison_contract.get("required_pass_conditions")
    if not isinstance(required_pass_conditions, list) or not all(
        isinstance(item, str) for item in required_pass_conditions
    ):
        fail("comparison_contract.required_pass_conditions must be a string list")
    missing_pass = sorted(EXPECTED_REQUIRED_PASS_CONDITIONS - set(required_pass_conditions))
    if missing_pass:
        fail("comparison_contract.required_pass_conditions missing required value(s): " + ", ".join(missing_pass))

    forbidden_diffs = comparison_contract.get("forbidden_diffs")
    if not isinstance(forbidden_diffs, list) or not all(isinstance(item, str) for item in forbidden_diffs):
        fail("comparison_contract.forbidden_diffs must be a string list")
    missing_forbidden = sorted(EXPECTED_FORBIDDEN_DIFFS - set(forbidden_diffs))
    if missing_forbidden:
        fail("comparison_contract.forbidden_diffs missing required value(s): " + ", ".join(missing_forbidden))

    allowed_preview_only_diffs = comparison_contract.get("allowed_preview_only_diffs")
    if not isinstance(allowed_preview_only_diffs, list) or not all(
        isinstance(item, str) for item in allowed_preview_only_diffs
    ):
        fail("comparison_contract.allowed_preview_only_diffs must be a string list")
    missing_allowed = sorted(EXPECTED_ALLOWED_PREVIEW_ONLY_DIFFS - set(allowed_preview_only_diffs))
    if missing_allowed:
        fail(
            "comparison_contract.allowed_preview_only_diffs missing required value(s): "
            + ", ".join(missing_allowed)
        )


def validate_preview_artifact(preview: dict[str, Any]) -> None:
    for key, expected in EXPECTED_PREVIEW_TOP_LEVEL.items():
        if preview.get(key) != expected:
            fail(f"{key} must be {expected!r}")

    source_authority = preview.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("source_authority must be an object")
    validate_source_references(source_authority)

    target_file_classes = preview.get("target_file_classes")
    validate_target_file_classes(target_file_classes)

    caveats = preview.get("preview_caveats")
    validate_caveats(caveats)

    constants_preview = preview.get("constants_preview")
    if not isinstance(constants_preview, dict):
        fail("constants_preview must be an object")
    validate_constants_preview(constants_preview)

    comparison_contract = preview.get("comparison_contract")
    if not isinstance(comparison_contract, dict):
        fail("comparison_contract must be an object")
    validate_comparison_contract(comparison_contract)

    future_gate = preview.get("future_integration_gate")
    if not isinstance(future_gate, dict):
        fail("future_integration_gate must be an object")
    if future_gate.get("product_approval_required") is not True:
        fail("future_integration_gate.product_approval_required must be true")
    if future_gate.get("build_gate_required") is not True:
        fail("future_integration_gate.build_gate_required must be true")
    if future_gate.get("hardware_test_gate_required") is not True:
        fail("future_integration_gate.hardware_test_gate_required must be true")
    if future_gate.get("rollback_required") is not True:
        fail("future_integration_gate.rollback_required must be true")

    provenance = preview.get("provenance")
    if not isinstance(provenance, dict):
        fail("provenance must be an object")
    if provenance.get("baseline_branch") != "configurator":
        fail("provenance.baseline_branch must be configurator")
    if provenance.get("created_on_branch") != "phase3-generated-constants-contract":
        fail("provenance.created_on_branch must be phase3-generated-constants-contract")
    if provenance.get("source_snapshot") != "current_worktree_baseline":
        fail("provenance.source_snapshot must be current_worktree_baseline")


def main() -> int:
    print("glyph_phase3_generated_constants_preview")
    print(f"contract_doc={display(CONTRACT_DOC_PATH)}")
    print(f"preview_path={display(PREVIEW_PATH)}")
    try:
        validate_contract_doc()
        preview = load_json_object(PREVIEW_PATH)
        preview_sha256 = sha256_file(PREVIEW_PATH)
        validate_preview_artifact(preview)
    except (Phase3PreviewError, OSError, KeyError, ValueError) as exc:
        print("status=FAIL")
        print("table_count=0")
        print("source_hashes_checked=0")
        print("preview_sha256=UNKNOWN")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"table_count={len(normalized_table_names())}")
    print(f"source_hashes_checked={len(EXPECTED_SOURCE_REFERENCES)}")
    print(f"preview_sha256={preview_sha256}")
    print(f"artifact_id={preview['artifact_id']}")
    print(f"comparison_mode={preview['comparison_contract']['source_diff_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
