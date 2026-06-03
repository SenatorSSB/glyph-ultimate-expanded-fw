#!/usr/bin/env python3
"""Validate the external Glyph remapper config-shape comparison matrix."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_config_shape_matrix_2026-06-03.json"
)

SCHEMA_NAME = "glyph_external_remapper_config_shape_matrix"
MATRIX_VERSION = 1
STATUS = "external_non_authoritative_config_shape_matrix"
HARDWARE_STATUS = "not_new_hardware_result"
AUTHORITY_STATUS = "non_authoritative_external_comparison"
ALLOWED_EXTERNAL_STATUSES = {
    "observed_from_external_repo_docs",
    "observed_from_external_code_excerpt",
    "not_verified",
}
ALLOWED_COMPATIBILITY_STATUSES = {
    "compatible_observed",
    "compatible_internal_only",
    "partial_gap",
    "unknown_needs_source_audit",
    "out_of_scope",
}
REQUIRED_CATEGORY_IDS = (
    "profile_list_profile_configs",
    "game_mode_config",
    "button_remapping_entries",
    "explicit_disable_entries",
    "button_activation_output_semantics",
    "socd_pairs",
    "rgb_configs",
    "rgb_config_1_based_indexing",
    "keyboard_mode_configs",
    "keyboard_scancodes",
    "menu_button_icon_display_metadata",
    "default_config_payload",
    "protobuf_encode_decode_path",
    "json_import_export_path",
    "webserial_load_save_path",
    "custom_profile_modifier_support",
)
REQUIRED_DOC_PHRASES = (
    "non-authoritative comparison",
    "not official configurator compatibility",
    "not device write behavior",
    "not runtime-loaded config",
    "not hardware validation",
)


class ConfigShapeMatrixError(ValueError):
    """Raised when the config-shape matrix drifts from required boundaries."""


def fail(message: str) -> None:
    raise ConfigShapeMatrixError(message)


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


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{key} must be a non-empty list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{key}[{index}] must be a non-empty string")
        result.append(item)
    return result


def require_categories(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    value = fixture.get("comparison_categories")
    if not isinstance(value, list) or not value:
        fail("comparison_categories must be a non-empty list")
    categories: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"comparison_categories[{index}] must be an object")
        categories.append(item)
    return categories


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "matrix_version": MATRIX_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "external_source_promoted_to_authority": False,
        "official_configurator_compatibility_claimed": False,
        "device_write_implemented": False,
        "runtime_loaded_config_implemented": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_source_inputs(fixture: dict[str, Any]) -> None:
    source = fixture.get("external_observation_source")
    if not isinstance(source, dict):
        fail("external_observation_source must be an object")
    if source.get("authority_status") != AUTHORITY_STATUS:
        fail("external_observation_source.authority_status must stay non-authoritative")
    for key in ("doc", "fixture"):
        relpath = source.get(key)
        if not isinstance(relpath, str) or not relpath:
            fail(f"external_observation_source.{key} must be a non-empty string")
        if not (REPO_ROOT / relpath).exists():
            fail(f"external_observation_source.{key} references missing path: {relpath}")

    repo_inputs = require_string_list(fixture, "repo_comparison_inputs")
    for relpath in repo_inputs:
        if not (REPO_ROOT / relpath).exists():
            fail(f"repo_comparison_inputs references missing path: {relpath}")


def validate_categories(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    categories = require_categories(fixture)
    ids: list[str] = []
    seen: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}

    for index, entry in enumerate(categories):
        category_id = entry.get("category_id")
        if not isinstance(category_id, str) or not category_id:
            fail(f"comparison_categories[{index}].category_id must be a non-empty string")
        if category_id in seen:
            fail(f"duplicate category_id: {category_id}")
        seen.add(category_id)
        ids.append(category_id)
        by_id[category_id] = entry

        external_status = entry.get("external_observation_status")
        if external_status not in ALLOWED_EXTERNAL_STATUSES:
            fail(f"{category_id} has unsupported external_observation_status: {external_status!r}")

        for field_name in ("external_notes", "our_artifact_reference", "required_follow_up"):
            value = entry.get(field_name)
            if not isinstance(value, str) or not value:
                fail(f"{category_id}.{field_name} must be a non-empty string")

        compatibility_status = entry.get("compatibility_status")
        if compatibility_status not in ALLOWED_COMPATIBILITY_STATUSES:
            fail(f"{category_id} has unsupported compatibility_status: {compatibility_status!r}")

        if entry.get("authority_status") != AUTHORITY_STATUS:
            fail(f"{category_id}.authority_status must stay {AUTHORITY_STATUS!r}")

    if tuple(ids) != REQUIRED_CATEGORY_IDS:
        fail("comparison_categories must contain the required category ids in stable order")

    if by_id["webserial_load_save_path"].get("compatibility_status") != "out_of_scope":
        fail("webserial_load_save_path must remain out_of_scope while device write is not implemented")

    custom_status = by_id["custom_profile_modifier_support"].get("compatibility_status")
    if custom_status not in {"unknown_needs_source_audit", "partial_gap"}:
        fail("custom_profile_modifier_support must remain unknown_needs_source_audit or partial_gap")

    return categories


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_config_shape_matrix")
    comparison_categories_count = 0
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_source_inputs(fixture)
        categories = validate_categories(fixture)
        comparison_categories_count = len(categories)
        validate_doc()
    except (OSError, ConfigShapeMatrixError, ValueError) as exc:
        print("status=FAIL")
        print(f"comparison_categories={comparison_categories_count}")
        print("external_source_promoted_to_authority=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"comparison_categories={comparison_categories_count}")
    print("external_source_promoted_to_authority=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("device_write_implemented=false")
    print("runtime_loaded_config_implemented=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
