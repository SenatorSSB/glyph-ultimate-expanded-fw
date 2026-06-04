#!/usr/bin/env python3
"""Validate the offline remapper adapter gap matrix."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_adapter_gap_matrix"
MATRIX_VERSION = 1
STATUS = "offline_adapter_gap_matrix_only"
HARDWARE_STATUS = "not_new_hardware_result"
ALLOWED_GAP_STATUSES = {
    "blocked_missing_source_authority",
    "blocked_pending_manual_experiment",
    "blocked_pending_license_review",
    "allowed_as_sidecar_only",
    "out_of_scope",
}
REQUIRED_GAP_IDS = (
    "external_custom_modifier_representation",
    "official_protobuf_schema",
    "external_protobuf_encode_decode_assumptions",
    "webserial_packet_framing",
    "save_to_device_behavior",
    "official_configurator_json_edge_cases",
    "rgb_shared_index_behavior",
    "menu_button_display_vs_runtime_behavior",
    "keyboard_scancode_mapping",
    "socd_semantic_equivalence",
    "profile_count_limits",
    "external_default_config_provenance",
    "external_license_code_reuse",
    "import_export_no_device_experiment_evidence",
)
REQUIRED_DOC_PHRASES = (
    "blocked-field gap matrix",
    "no adapter generation",
    "no external code reuse",
    "no device write behavior",
    "no webserial transport",
    "not hardware validation",
)


class OfflineRemapperAdapterGapMatrixError(ValueError):
    """Raised when the gap matrix drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperAdapterGapMatrixError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    return value


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty list")
    items: list[str] = []
    for index, item in enumerate(value):
        items.append(require_string(item, f"{label}[{index}]"))
    return items


def require_bool(payload: dict[str, Any], key: str, expected: bool) -> None:
    if payload.get(key) is not expected:
        fail(f"{key} must be {expected!r}")


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "matrix_version": MATRIX_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")

    for key in (
        "adapter_implemented",
        "external_source_promoted_to_authority",
        "external_source_code_copied",
        "official_configurator_compatibility_claimed",
        "device_write_implemented",
        "webserial_transport_implemented",
        "protobuf_binary_generation_implemented",
        "runtime_loaded_config_implemented",
        "hardware_validation_claimed",
    ):
        require_bool(fixture, key, False)


def validate_source_inputs(fixture: dict[str, Any]) -> None:
    inputs = require_string_list(fixture.get("source_inputs"), "source_inputs")
    for relpath in inputs:
        if not (REPO_ROOT / relpath).exists():
            fail(f"source_inputs references missing path: {relpath}")


def validate_gaps(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    gaps = fixture.get("gaps")
    if not isinstance(gaps, list) or not gaps:
        fail("gaps must be a non-empty list")

    seen: set[str] = set()
    for index, gap in enumerate(gaps):
        if not isinstance(gap, dict):
            fail(f"gaps[{index}] must be an object")
        gap_id = require_string(gap.get("gap_id"), f"gaps[{index}].gap_id")
        if gap_id in seen:
            fail(f"duplicate gap_id in gaps: {gap_id}")
        seen.add(gap_id)

        status = require_string(gap.get("status"), f"gaps[{index}].status")
        if status not in ALLOWED_GAP_STATUSES:
            fail(f"gaps[{index}].status must be allowed: {status}")

        require_string(gap.get("risk"), f"gaps[{index}].risk")
        require_string_list(gap.get("required_evidence"), f"gaps[{index}].required_evidence")
        require_string_list(gap.get("must_not_generate"), f"gaps[{index}].must_not_generate")
        require_string(gap.get("notes"), f"gaps[{index}].notes")

    missing = [gap_id for gap_id in REQUIRED_GAP_IDS if gap_id not in seen]
    if missing:
        fail(f"gaps missing required gap_id values: {', '.join(missing)}")
    return gaps


def gap_by_id(gaps: list[dict[str, Any]], gap_id: str) -> dict[str, Any]:
    for gap in gaps:
        if gap["gap_id"] == gap_id:
            return gap
    fail(f"missing gap for {gap_id}")


def validate_required_statuses(gaps: list[dict[str, Any]]) -> None:
    custom_modifier = gap_by_id(gaps, "external_custom_modifier_representation")
    if custom_modifier["status"] != "blocked_missing_source_authority":
        fail("external_custom_modifier_representation must be blocked_missing_source_authority")

    webserial = gap_by_id(gaps, "webserial_packet_framing")
    if webserial["status"] not in {"blocked_missing_source_authority", "out_of_scope"}:
        fail("webserial_packet_framing must be blocked_missing_source_authority or out_of_scope")

    save_to_device = gap_by_id(gaps, "save_to_device_behavior")
    if save_to_device["status"] not in {"blocked_missing_source_authority", "out_of_scope"}:
        fail("save_to_device_behavior must be blocked_missing_source_authority or out_of_scope")

    license_review = gap_by_id(gaps, "external_license_code_reuse")
    if license_review["status"] != "blocked_pending_license_review":
        fail("external_license_code_reuse must be blocked_pending_license_review")
    forbidden = " ".join(license_review["must_not_generate"]).lower()
    if "code copy" not in forbidden:
        fail("external_license_code_reuse must_not_generate must forbid code copy")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_adapter_gap_matrix")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_source_inputs(fixture)
        gaps = validate_gaps(fixture)
        validate_required_statuses(gaps)
        validate_doc()
    except (OSError, OfflineRemapperAdapterGapMatrixError, ValueError) as exc:
        print("status=FAIL")
        print("gaps=0")
        print("adapter_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"gaps={len(fixture['gaps'])}")
    print("adapter_implemented=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("external_source_promoted_to_authority=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
