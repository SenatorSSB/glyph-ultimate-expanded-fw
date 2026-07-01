#!/usr/bin/env python3
"""Validate runtime-config semantics evaluator bridge artifacts and negative corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import (
    load_source_tables,
    normalized_table_names,
    source_symbol_by_normalized_name,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/runtime_config/runtime_config_semantics_evaluator_bridge.md"
SCHEMA_DOC_PATH = REPO_ROOT / "docs/runtime_config/runtime_loaded_config_schema_design.md"
ARCH_DOC_PATH = REPO_ROOT / "docs/runtime_config/firmware_interpreter_architecture_spec.md"
BASELINE_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/current_baseline_runtime_config_semantics_bridge.json"
INTERPRETER_BASELINE_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/current_baseline_runtime_config_interpreter_source_baseline.json"
PREVIEW_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/current_baseline_extracted_config_preview.json"
INVALID_FIXTURE_PATH = REPO_ROOT / "docs/runtime_config/fixtures/invalid_runtime_config_semantics_cases.json"

EXPECTED_TABLE_COUNT = 28
EXPECTED_POINTS_PER_TABLE = 9
EXPECTED_TABLE_FAMILY = "StickPoint"
EXPECTED_TABLE_SHAPE = "StickPoint[9]"

REQUIRED_INVALID_CLASSES = {
    "macro_timing_automation_attempt",
    "turbo_rapid_fire_attempt",
    "arbitrary_script_attempt",
    "hidden_device_write_behavior",
    "missing_fallback_policy",
    "out_of_range_coordinate",
    "missing_table",
    "unknown_role_without_source_authority",
    "runtime_config_claiming_nunchuk_validation",
    "runtime_config_claiming_webserial_device_write_authority",
}

EXPECTED_SOURCE_REFERENCE_ROLES = {
    "src/modes/Ultimate.cpp": "current_baseline_source",
    "src/modes/UltimateIdentityRuntimeTables.hpp": "generated_like_table_constants",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp": "runtime_config_interpreter_boundary",
    "tools/extract_glyph_identity_runtime_tables.py": "source_table_extractor",
}

DOC_REQUIRED_PHRASES = {
    DOC_PATH: (
        "current baseline oracle",
        "baseline equivalence invariant",
        "runtime-loaded config boundary",
        "source-owned current baseline",
        "validate-before-use",
        "fallback-to-known-good",
        "manual hardware-test trigger points",
        "non-claims",
    ),
    SCHEMA_DOC_PATH: (
        "implementation stop line",
        "design-only",
        "forbidden semantics",
        "does not implement runtime-loaded config",
        "future schema",
        "stable table ids",
    ),
    ARCH_DOC_PATH: (
        "ultimateruntimeconfiginterpreter.hpp",
        "source-owned runtime config interpreter boundary",
        "validation-before-use",
        "fallback-to-known-good",
        "known-good",
        "storage assumptions deferred",
        "binary serialization",
        "webserial transport",
        "device write",
    ),
}


class BridgeCheckError(ValueError):
    """Raised when evaluator bridge fixtures diverge from design constraints."""


def fail(message: str) -> None:
    raise BridgeCheckError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path} must be a JSON object")
    return payload


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        fail(f"{label} must be a boolean")
    return value


def require_int(value: Any, label: str) -> int:
    if not isinstance(value, int):
        fail(f"{label} must be an integer")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_doc_phrases() -> None:
    for path, phrases in DOC_REQUIRED_PHRASES.items():
        lowered = path.read_text(encoding="utf-8").lower()
        for phrase in phrases:
            if phrase not in lowered:
                fail(f"{path.relative_to(REPO_ROOT)} missing required phrase: {phrase}")


def validate_file_reference(entry: dict[str, Any], label: str) -> None:
    path = require_string(entry.get("path"), f"{label}.path")
    require_string(entry.get("role"), f"{label}.role")
    sha = require_string(entry.get("sha256"), f"{label}.sha256")
    if len(sha) != 64:
        fail(f"{label}.sha256 must be a sha256 hex digest")
    if "TODO" in sha:
        fail(f"{label}.sha256 contains TODO")
    ref = REPO_ROOT / path
    if not ref.exists():
        fail(f"{label}.path does not exist: {path}")
    if sha256_file(ref) != sha:
        fail(f"{label}.sha256 mismatch for {path}")


def validate_reference_list(entries: list[Any], label: str, expected_roles: dict[str, str]) -> None:
    if not entries:
        fail(f"{label} must not be empty")
    if len(entries) != len(expected_roles):
        fail(f"{label} must contain exactly {len(expected_roles)} references")

    seen_paths: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"{label}[{index}] must be an object")
        validate_file_reference(entry, f"{label}[{index}]")

        path = require_string(entry.get("path"), f"{label}[{index}].path")
        role = require_string(entry.get("role"), f"{label}[{index}].role")
        expected_role = expected_roles.get(path)
        if expected_role is None:
            fail(f"{label}[{index}] references unexpected path: {path}")
        if role != expected_role:
            fail(f"{label}[{index}].role must be {expected_role!r}")
        seen_paths.add(path)

    missing = sorted(set(expected_roles) - seen_paths)
    if missing:
        fail(f"{label} missing required path(s): " + ", ".join(missing))


def expected_symbol_for(name: str) -> str:
    return source_symbol_by_normalized_name()[name]


def validate_table_set(
    entries: list[dict[str, Any]],
    label: str,
    source_tables: dict[str, tuple[tuple[int, int], ...]],
    *,
    require_value_source: bool = False,
) -> dict[str, dict[str, Any]]:
    if len(entries) != EXPECTED_TABLE_COUNT:
        fail(f"{label} must contain {EXPECTED_TABLE_COUNT} tables")

    seen: set[str] = set()
    by_name: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"{label}[{index}] must be an object")

        name = require_string(entry.get("name"), f"{label}[{index}].name")
        if name in seen:
            fail(f"{label} contains duplicate table name: {name}")
        seen.add(name)
        by_name[name] = entry

        symbol = require_string(entry.get("source_symbol"), f"{label}[{index}].source_symbol")
        if symbol != expected_symbol_for(name):
            fail(f"{label}[{index}].source_symbol must match source mapping for {name}")

        point_count = require_int(entry.get("point_count"), f"{label}[{index}].point_count")
        if point_count != EXPECTED_POINTS_PER_TABLE:
            fail(f"{label}[{index}].point_count must be {EXPECTED_POINTS_PER_TABLE}")

        shape = entry.get("shape")
        if shape is not None:
            if require_string(shape, f"{label}[{index}].shape") != EXPECTED_TABLE_SHAPE:
                fail(f"{label}[{index}].shape must be {EXPECTED_TABLE_SHAPE}")

        if require_value_source:
            value_source = require_string(entry.get("value_source"), f"{label}[{index}].value_source")
            if value_source != "src/modes/Ultimate.cpp":
                fail(f"{label}[{index}].value_source must be src/modes/Ultimate.cpp")

        for raw_field in ("points", "values", "table_values", "raw_points", "raw"):
            if raw_field in entry:
                fail(f"{label}[{index}] must not include raw field {raw_field}")

    expected_names = set(normalized_table_names())
    source_names = set(source_tables)
    if seen != expected_names:
        missing = sorted(expected_names - seen)
        unexpected = sorted(seen - expected_names)
        msg = []
        if missing:
            msg.append("missing=" + ", ".join(missing))
        if unexpected:
            msg.append("unexpected=" + ", ".join(unexpected))
        fail(f"{label} table names mismatch ({'; '.join(msg)})")

    for name, points in source_tables.items():
        if len(points) != EXPECTED_POINTS_PER_TABLE:
            fail(f"source table {name} must have {EXPECTED_POINTS_PER_TABLE} points")

    return by_name


def validate_baseline(fixture: dict[str, Any], source_tables: dict[str, tuple[tuple[int, int], ...]]) -> None:
    required_fields = {
        "artifact_id",
        "schema_name",
        "status",
        "mode_scope",
        "runtime_loaded_config",
        "consumed_by_firmware",
        "table_family",
        "expected_table_count",
        "expected_point_count_per_table",
        "source_baseline",
        "table_summary",
        "config_owned_candidate_data",
        "firmware_owned_semantics",
        "forbidden_config_semantics",
        "future_gates",
        "caveats",
        "interpreter_source_baseline",
    }
    missing = required_fields - set(fixture)
    if missing:
        fail("baseline fixture missing fields: " + ", ".join(sorted(missing)))

    if require_string(fixture.get("status"), "baseline.status") != "design_fixture_not_runtime_config":
        fail("baseline.status must remain design_fixture_not_runtime_config")
    if require_string(fixture.get("mode_scope"), "baseline.mode_scope") != "MODE_ULTIMATE":
        fail("baseline.mode_scope must be MODE_ULTIMATE")
    if require_bool(fixture.get("runtime_loaded_config"), "baseline.runtime_loaded_config"):
        fail("baseline must not claim runtime-loaded config implemented")
    if require_bool(fixture.get("consumed_by_firmware"), "baseline.consumed_by_firmware"):
        fail("baseline must not be consumed by firmware")
    if require_string(fixture.get("table_family"), "baseline.table_family") != EXPECTED_TABLE_FAMILY:
        fail("baseline.table_family must be StickPoint")
    if require_int(fixture.get("expected_table_count"), "baseline.expected_table_count") != EXPECTED_TABLE_COUNT:
        fail(f"baseline.expected_table_count must be {EXPECTED_TABLE_COUNT}")
    if require_int(
        fixture.get("expected_point_count_per_table"),
        "baseline.expected_point_count_per_table",
    ) != EXPECTED_POINTS_PER_TABLE:
        fail("baseline.expected_point_count_per_table must be 9")

    validate_reference_list(
        require_list(fixture.get("source_baseline"), "baseline.source_baseline"),
        "baseline.source_baseline",
        EXPECTED_SOURCE_REFERENCE_ROLES,
    )

    preview_ref = fixture.get("source_baseline_preview")
    if preview_ref is not None:
        validate_file_reference(require_object(preview_ref, "baseline.source_baseline_preview"), "baseline.source_baseline_preview")

    interpreter_baseline = load_json_object(INTERPRETER_BASELINE_FIXTURE_PATH)
    if fixture.get("interpreter_source_baseline") != interpreter_baseline:
        fail("baseline.interpreter_source_baseline must match the dedicated interpreter baseline fixture")

    validate_table_set(
        require_list(fixture.get("table_summary"), "baseline.table_summary"),
        "baseline.table_summary",
        source_tables,
    )

    for field in ("config_owned_candidate_data", "firmware_owned_semantics", "forbidden_config_semantics", "future_gates", "caveats"):
        values = require_list(fixture.get(field), f"baseline.{field}")
        if not values or not all(isinstance(item, str) and item for item in values):
            fail(f"baseline.{field} must be a non-empty string list")


def validate_preview(fixture: dict[str, Any], source_tables: dict[str, tuple[tuple[int, int], ...]], baseline_path: Path) -> None:
    required_fields = {
        "artifact_id",
        "schema_name",
        "preview_version",
        "status",
        "mode_scope",
        "generated_from_source_baseline",
        "consumed_by_firmware",
        "runtime_loaded_config",
        "table_family",
        "expected_table_count",
        "expected_point_count_per_table",
        "source_baseline_fixture",
        "source_authority",
        "table_metadata",
        "preview_caveats",
    }
    missing = required_fields - set(fixture)
    if missing:
        fail("preview fixture missing fields: " + ", ".join(sorted(missing)))

    if require_string(fixture.get("status"), "preview.status") != "source_backed_preview_not_runtime_config":
        fail("preview.status must be source_backed_preview_not_runtime_config")
    if require_string(fixture.get("mode_scope"), "preview.mode_scope") != "MODE_ULTIMATE":
        fail("preview.mode_scope must be MODE_ULTIMATE")
    if not require_bool(fixture.get("generated_from_source_baseline"), "preview.generated_from_source_baseline"):
        fail("preview.generated_from_source_baseline must be true")
    if require_bool(fixture.get("runtime_loaded_config"), "preview.runtime_loaded_config"):
        fail("preview must not claim runtime-loaded config")
    if require_bool(fixture.get("consumed_by_firmware"), "preview.consumed_by_firmware"):
        fail("preview must not be consumed by firmware")
    if require_string(fixture.get("table_family"), "preview.table_family") != EXPECTED_TABLE_FAMILY:
        fail("preview.table_family must be StickPoint")
    if require_int(fixture.get("expected_table_count"), "preview.expected_table_count") != EXPECTED_TABLE_COUNT:
        fail(f"preview.expected_table_count must be {EXPECTED_TABLE_COUNT}")
    if require_int(fixture.get("expected_point_count_per_table"), "preview.expected_point_count_per_table") != EXPECTED_POINTS_PER_TABLE:
        fail("preview.expected_point_count_per_table must be 9")

    source_baseline_fixture = require_string(
        fixture.get("source_baseline_fixture"), "preview.source_baseline_fixture"
    )
    if source_baseline_fixture != str(baseline_path.relative_to(REPO_ROOT)):
        fail("preview.source_baseline_fixture must reference the bridge baseline fixture")

    authority = require_object(fixture.get("source_authority"), "preview.source_authority")
    validate_reference_list(
        require_list(authority.get("references"), "preview.source_authority.references"),
        "preview.source_authority.references",
        EXPECTED_SOURCE_REFERENCE_ROLES,
    )

    validate_table_set(
        require_list(fixture.get("table_metadata"), "preview.table_metadata"),
        "preview.table_metadata",
        source_tables,
        require_value_source=True,
    )

    preview_caveats = require_list(fixture.get("preview_caveats"), "preview.preview_caveats")
    if not preview_caveats or not all(isinstance(item, str) and item for item in preview_caveats):
        fail("preview.preview_caveats must be a non-empty string list")


def validate_invalid_corpus(corpus: dict[str, Any], baseline_path: Path, preview_path: Path) -> int:
    required_fields = {
        "artifact_id",
        "schema_name",
        "corpus_version",
        "status",
        "mode_scope",
        "hardware_status",
        "nunchuk_status",
        "baseline_fixture",
        "baseline_preview",
        "required_invalid_classes",
        "cases",
    }
    missing = required_fields - set(corpus)
    if missing:
        fail("invalid corpus missing fields: " + ", ".join(sorted(missing)))

    if require_string(corpus.get("status"), "invalid.status") != "docs_tools_negative_corpus":
        fail("invalid.status must be docs_tools_negative_corpus")
    if require_string(corpus.get("mode_scope"), "invalid.mode_scope") != "MODE_ULTIMATE":
        fail("invalid.mode_scope must be MODE_ULTIMATE")
    if require_string(corpus.get("baseline_fixture"), "invalid.baseline_fixture") != str(baseline_path.relative_to(REPO_ROOT)):
        fail("invalid.baseline_fixture must reference the bridge baseline fixture")
    if require_string(corpus.get("baseline_preview"), "invalid.baseline_preview") != str(preview_path.relative_to(REPO_ROOT)):
        fail("invalid.baseline_preview must reference the baseline preview fixture")

    required_classes = set(require_list(corpus.get("required_invalid_classes"), "invalid.required_invalid_classes"))
    if not all(isinstance(item, str) and item for item in required_classes):
        fail("invalid.required_invalid_classes must be a non-empty string list")
    missing_required = REQUIRED_INVALID_CLASSES - set(required_classes)
    if missing_required:
        fail("invalid.required_invalid_classes missing: " + ", ".join(sorted(missing_required)))

    cases = require_list(corpus.get("cases"), "invalid.cases")
    if not cases:
        fail("invalid.cases must not be empty")

    seen_classes = set()
    for index, case_obj in enumerate(cases):
        case = require_object(case_obj, f"invalid.cases[{index}]")
        case_id = require_string(case.get("case_id"), f"invalid.cases[{index}].case_id")
        if require_string(case.get("status"), f"{case_id}.status") != "invalid":
            fail(f"{case_id} must declare status invalid")
        if case.get("declared_invalid") is not True:
            fail(f"{case_id} must set declared_invalid true")

        invalid_class = require_string(case.get("invalid_class"), f"{case_id}.invalid_class")
        if invalid_class not in REQUIRED_INVALID_CLASSES:
            fail(f"{case_id} uses unsupported invalid_class {invalid_class!r}")

        expected_error_codes = require_list(case.get("expected_error_codes"), f"{case_id}.expected_error_codes")
        if not expected_error_codes or not all(isinstance(item, str) and item for item in expected_error_codes):
            fail(f"{case_id}.expected_error_codes must be non-empty string list")

        seen_classes.add(invalid_class)

    missing = REQUIRED_INVALID_CLASSES - seen_classes
    if missing:
        fail("invalid cases do not cover required classes: " + ", ".join(sorted(missing)))
    return len(cases)


def ensure_artifacts_exist() -> None:
    for path in (
        DOC_PATH,
        SCHEMA_DOC_PATH,
        ARCH_DOC_PATH,
        BASELINE_FIXTURE_PATH,
        INTERPRETER_BASELINE_FIXTURE_PATH,
        PREVIEW_FIXTURE_PATH,
        INVALID_FIXTURE_PATH,
    ):
        if not path.exists():
            fail(f"missing required artifact: {path}")


def main() -> int:
    print("glyph_runtime_config_semantics_evaluator_bridge")
    try:
        ensure_artifacts_exist()
        validate_doc_phrases()

        source_tables = load_source_tables(REPO_ROOT / "src/modes/Ultimate.cpp")

        baseline = load_json_object(BASELINE_FIXTURE_PATH)
        preview = load_json_object(PREVIEW_FIXTURE_PATH)
        invalid = load_json_object(INVALID_FIXTURE_PATH)

        validate_baseline(baseline, source_tables)
        validate_preview(preview, source_tables, BASELINE_FIXTURE_PATH)
        case_count = validate_invalid_corpus(invalid, BASELINE_FIXTURE_PATH, PREVIEW_FIXTURE_PATH)

        print("status=PASS")
        print(f"table_count={len(source_tables)}")
        print(f"expected_point_count={EXPECTED_POINTS_PER_TABLE}")
        print(f"invalid_cases={case_count}")
        return 0
    except (BridgeCheckError, OSError, ValueError, TypeError, KeyError) as exc:
        print("status=FAIL")
        print("table_count=0")
        print(f"expected_point_count={EXPECTED_POINTS_PER_TABLE}")
        print("invalid_cases=0")
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
