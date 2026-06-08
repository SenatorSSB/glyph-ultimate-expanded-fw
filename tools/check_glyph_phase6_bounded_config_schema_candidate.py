#!/usr/bin/env python3
"""Validate Phase 6 bounded config-owned schema candidate fixtures."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = REPO_ROOT / "docs/runtime_config/fixtures/phase6_bounded_config_owned_modifier_data_schema_candidate.json"
INVALID = REPO_ROOT / "docs/runtime_config/fixtures/phase6_bounded_config_invalid_cases.json"

REQUIRED_TOP_LEVEL = {
    "schema_name",
    "schema_version",
    "status",
    "mode_scope",
    "consumed_by_firmware",
    "runtime_loaded_config",
    "config_owned_candidate_data",
    "firmware_owned_semantics",
    "forbidden_config_semantics",
    "proposed_storage",
    "proposed_format",
    "proposed_boot_load",
    "caveats",
}

REQUIRED_CONFIG_DATA = {
    "table_values",
    "table_ids",
    "table_order",
    "point_count",
    "coordinate_bounds",
    "metadata",
    "provenance",
    "checksums",
}

REQUIRED_FIRMWARE_OWNED = {
    "evaluator_phase_order",
    "priority_logic",
    "role_resolution",
    "table_selection",
    "validation",
    "fallback",
    "migration",
    "storage_policy",
    "device_write_policy",
}

REQUIRED_FORBIDDEN = {
    "macros",
    "turbo",
    "timing_automation",
    "arbitrary_scripting",
    "hidden_device_write",
    "transport_commands",
    "firmware_patches",
    "history_dependent_logic",
}

REQUIRED_INVALID_CLASSES = {
    "macro attempt",
    "turbo attempt",
    "timing automation",
    "arbitrary script",
    "hidden device-write command",
    "transport command embedded in config",
    "firmware patch payload",
    "unknown mode scope",
    "cross-mode table injection",
    "wrong table count",
    "wrong point count",
    "out-of-range coordinate",
    "missing fallback",
    "duplicate table id",
    "unknown table id",
    "config claims evaluator priority ownership",
    "config claims storage write policy",
    "config claims WebSerial authority",
    "config claims nunchuk validation",
}

FORBIDDEN_CONFIG_DATA_KEYS = {
    "priority_logic",
    "storage_policy",
    "webserial_authority",
    "nunchuk_validation",
    "cross_mode_tables",
    "table_count",
}


class Phase6SchemaError(ValueError):
    """Raised when a Phase 6 schema candidate fixture drifts."""


def fail(message: str) -> None:
    raise Phase6SchemaError(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required fixture: {path.relative_to(REPO_ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return payload


def ensure_canonical(path: Path, payload: dict[str, Any]) -> None:
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.read_text(encoding="utf-8") != expected:
        fail(f"{path.relative_to(REPO_ROOT)} must be canonical sorted JSON")


def require_keys(obj: dict[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(obj))
    if missing:
        fail(f"{label} missing keys: {', '.join(missing)}")


def validate_candidate(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    def issue(code: str) -> None:
        if code not in issues:
            issues.append(code)

    if set(payload) - REQUIRED_TOP_LEVEL:
        issue("unexpected_top_level_key")
    if REQUIRED_TOP_LEVEL - set(payload):
        issue("missing_top_level_key")
    if payload.get("schema_name") != "phase6_bounded_config_owned_modifier_data_schema_candidate":
        issue("bad_schema_name")
    if payload.get("schema_version") != 1:
        issue("bad_schema_version")
    if payload.get("status") != "SCHEMA_CANDIDATE_NOT_RUNTIME_CONFIG":
        issue("bad_status")
    if payload.get("mode_scope") != "MODE_ULTIMATE":
        issue("bad_mode_scope")
    if payload.get("consumed_by_firmware") is not False:
        issue("firmware_consumption_claim")
    if payload.get("runtime_loaded_config") is not False:
        issue("runtime_loaded_config_claim")

    config_data = payload.get("config_owned_candidate_data")
    firmware_owned = payload.get("firmware_owned_semantics")
    forbidden = payload.get("forbidden_config_semantics")
    if not isinstance(config_data, dict):
        issue("bad_config_owned_candidate_data")
        config_data = {}
    if not isinstance(firmware_owned, dict):
        issue("bad_firmware_owned_semantics")
        firmware_owned = {}
    if not isinstance(forbidden, dict):
        issue("bad_forbidden_config_semantics")
        forbidden = {}

    if set(config_data) != REQUIRED_CONFIG_DATA:
        issue("bad_config_owned_candidate_data_keys")
    if set(config_data) & FORBIDDEN_CONFIG_DATA_KEYS:
        issue("config_claims_firmware_owned_policy")
    for key, value in config_data.items():
        if not isinstance(value, dict):
            issue("bad_config_owned_candidate_data")
            continue
        if key not in {"point_count", "coordinate_bounds"} and value.get("allowed") is not True:
            issue("config_candidate_data_disabled")
    if set(firmware_owned) != REQUIRED_FIRMWARE_OWNED:
        issue("bad_firmware_owned_semantics_keys")
    if set(forbidden) != REQUIRED_FORBIDDEN:
        issue("bad_forbidden_config_semantics_keys")
    if any(value is not True for value in firmware_owned.values()):
        issue("firmware_owned_semantic_disabled")
    if any(value is not True for value in forbidden.values()):
        issue("forbidden_semantic_disabled")

    point_count = config_data.get("point_count")
    if not isinstance(point_count, dict) or point_count.get("expected") != 9:
        issue("bad_point_count")
    bounds = config_data.get("coordinate_bounds")
    if not isinstance(bounds, dict):
        issue("bad_coordinate_bounds")
    else:
        for axis in ("x", "y"):
            axis_bounds = bounds.get(axis)
            if not isinstance(axis_bounds, dict):
                issue("bad_coordinate_bounds")
                continue
            if axis_bounds.get("min") != 0 or axis_bounds.get("max") != 255:
                issue("bad_coordinate_bounds")
            if axis_bounds.get("type") != "integer":
                issue("bad_coordinate_bounds")

    storage = payload.get("proposed_storage")
    fmt = payload.get("proposed_format")
    boot = payload.get("proposed_boot_load")
    if not isinstance(storage, dict) or storage.get("separate_mode_scoped_runtime_config_artifact") is not True or storage.get("not_current_config_bin") is not True or storage.get("not_implemented") is not True:
        issue("bad_proposed_storage")
    if not isinstance(fmt, dict) or fmt.get("gcfg_like_binary_candidate") is not True or fmt.get("not_implemented") is not True:
        issue("bad_proposed_format")
    if not isinstance(boot, dict) or boot.get("validate_before_use") is not True or boot.get("fallback_to_source_owned_baseline") is not True or boot.get("not_implemented") is not True:
        issue("bad_proposed_boot_load")

    return issues


def apply_patch(payload: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    mutated = copy.deepcopy(payload)
    for operation in operations:
        target: Any = mutated
        path = operation["path"]
        for part in path[:-1]:
            target = target[part]
        last = path[-1]
        if operation["op"] == "set":
            target[last] = operation["value"]
        elif operation["op"] == "add":
            target[last] = operation["value"]
        else:
            fail(f"unsupported invalid-corpus operation: {operation['op']}")
    return mutated


def validate_invalid_corpus(corpus: dict[str, Any], baseline: dict[str, Any]) -> None:
    if corpus.get("schema_name") != "phase6_bounded_config_invalid_cases":
        fail("invalid corpus schema_name drifted")
    if corpus.get("status") != "INVALID_CORPUS_NOT_RUNTIME_CONFIG":
        fail("invalid corpus status drifted")
    cases = corpus.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("invalid corpus must include cases")
    classes = {case.get("invalid_class") for case in cases if isinstance(case, dict)}
    missing = REQUIRED_INVALID_CLASSES - classes
    if missing:
        fail("invalid corpus missing classes: " + ", ".join(sorted(missing)))
    for case in cases:
        if not isinstance(case, dict):
            fail("invalid corpus case must be an object")
        patch = case.get("patch")
        if not isinstance(patch, list):
            fail(f"invalid corpus case {case.get('case_id')} missing patch list")
        mutated = apply_patch(baseline, patch)
        issues = validate_candidate(mutated)
        if not issues:
            fail(f"invalid corpus case did not fail validation: {case.get('case_id')}")


def main() -> int:
    print("glyph_phase6_bounded_config_schema_candidate")
    try:
        candidate = load_json(CANDIDATE)
        invalid = load_json(INVALID)
        ensure_canonical(CANDIDATE, candidate)
        ensure_canonical(INVALID, invalid)
        require_keys(candidate, REQUIRED_TOP_LEVEL, "schema candidate")
        issues = validate_candidate(candidate)
        if issues:
            fail("schema candidate validation failed: " + ", ".join(issues))
        validate_invalid_corpus(invalid, candidate)
    except (OSError, json.JSONDecodeError, Phase6SchemaError, KeyError, TypeError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"schema_candidate={CANDIDATE.relative_to(REPO_ROOT)}")
    print(f"invalid_corpus={INVALID.relative_to(REPO_ROOT)}")
    print(f"invalid_classes={len(REQUIRED_INVALID_CLASSES)}")
    print("runtime_loaded_config=false")
    print("consumed_by_firmware=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
