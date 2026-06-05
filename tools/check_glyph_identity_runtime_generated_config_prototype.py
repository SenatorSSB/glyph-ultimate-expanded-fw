#!/usr/bin/env python3
"""Validate the docs-only Glyph identity runtime generated-config prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import (
    DEFAULT_SOURCE_PATH,
    load_source_tables,
    normalized_table_names,
    source_symbol_by_normalized_name,
)
from generate_glyph_identity_runtime_config_prototype import (
    CONTRACT_VERSION,
    HARDWARE_STATUS,
    MODE_SCOPE,
    NUNCHUK_STATUS,
    SCHEMA_NAME,
    SOURCE_STATUS,
    build_config_prototype,
    render_cpp_prototype,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ROLE_MAP_FIXTURE = "docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json"
PROTOTYPE_FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_identity_runtime_generated_config_prototype_2026-05-28.json"
)
REQUIRED_PRIORITY_KEYS = {
    "physical_inputs",
    "lf8_lf7_removed",
    "lf4_submode_active",
    "lt2_sublayer_active",
    "forced_up_resolution",
    "button_carriers",
    "ls_to_dpad_routing",
    "table_output",
    "direction_plus_a",
    "rf6_low_magnitude_za",
    "rf7_hard_up_b",
    "c_stick_asdi",
    "rf9_null",
    "nunchuk_override",
}
REQUIRED_CPP_CAVEATS = (
    "generated prototype only",
    "not firmware source",
    "not runtime-loaded config",
    "not hardware validation",
)
FORBIDDEN_CPP_PHRASES = ("upload", "flash", "push-to-device", "macro", "turbo")


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise AssertionError(message)


def _require_int_point(point: Any, label: str) -> list[int]:
    if (
        not isinstance(point, list)
        or len(point) != 2
        or any(isinstance(coord, bool) or not isinstance(coord, int) for coord in point)
    ):
        fail(f"{label} must be [int, int]")
    if not all(0 <= coord <= 255 for coord in point):
        fail(f"{label} coordinates must be in [0,255]")
    return [point[0], point[1]]


def _validate_top_level(config: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "contract_version": CONTRACT_VERSION,
        "mode_scope": MODE_SCOPE,
        "source_status": SOURCE_STATUS,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            fail(f"{key} must be {value}")

    source_authority = config.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("source_authority must be an object")
    if source_authority.get("role_map_fixture") != ROLE_MAP_FIXTURE:
        fail("source_authority must reference the role-map fixture")


def _validate_tables(config: dict[str, Any]) -> None:
    tables = config.get("tables")
    if not isinstance(tables, dict):
        fail("tables must be an object")

    expected_names = set(normalized_table_names())
    if set(tables) != expected_names:
        missing = sorted(expected_names - set(tables))
        unexpected = sorted(set(tables) - expected_names)
        fail(f"tables names mismatch missing={missing} unexpected={unexpected}")

    source_tables = load_source_tables(DEFAULT_SOURCE_PATH)
    for name in normalized_table_names():
        table = tables.get(name)
        if not isinstance(table, list):
            fail(f"tables.{name} must be a list")
        if len(table) != 9:
            fail(f"tables.{name} must contain 9 points")
        points = [_require_int_point(point, f"tables.{name}[{index}]") for index, point in enumerate(table)]
        if points != [list(point) for point in source_tables[name]]:
            fail(f"tables.{name} does not match source-parsed table")


def _validate_priority_model(config: dict[str, Any]) -> None:
    priority_model = config.get("priority_model")
    if not isinstance(priority_model, dict):
        fail("priority_model must be an object")
    missing = sorted(REQUIRED_PRIORITY_KEYS - set(priority_model))
    if missing:
        fail("priority_model missing required key(s): " + ", ".join(missing))
    for key in ("digital_effective_direction", "analog"):
        if key not in priority_model:
            fail(f"priority_model missing {key}")
        if not isinstance(priority_model[key], list) or not all(isinstance(item, str) for item in priority_model[key]):
            fail(f"priority_model.{key} must be a string list")


def _validate_hard_overrides(config: dict[str, Any]) -> None:
    hard_overrides = config.get("hard_overrides")
    if not isinstance(hard_overrides, dict):
        fail("hard_overrides must be an object")
    if hard_overrides.get("rf7_hard_up_b") != {
        "left": [77, 172],
        "center": [128, 172],
        "right": [179, 172],
    }:
        fail("hard_overrides.rf7_hard_up_b does not match source-backed role-map values")
    if hard_overrides.get("rf9_null") != [128, 128]:
        fail("hard_overrides.rf9_null must be [128, 128]")
    if hard_overrides.get("rf6_low_magnitude_table") != "Lt1LowMagnitude":
        fail("hard_overrides.rf6_low_magnitude_table must reference Lt1LowMagnitude")


def _validate_cpp_text(text: str) -> None:
    lowered = text.lower()
    for caveat in REQUIRED_CPP_CAVEATS:
        if caveat not in lowered:
            fail(f"C++ prototype missing caveat text: {caveat}")
    for phrase in FORBIDDEN_CPP_PHRASES:
        if phrase in lowered:
            fail(f"C++ prototype contains forbidden phrase: {phrase}")

    symbols = source_symbol_by_normalized_name()
    for name in normalized_table_names():
        symbol = symbols[name]
        declaration = f"constexpr StickPoint {symbol}[9]"
        if declaration not in text:
            fail(f"C++ prototype missing table declaration: {declaration}")


def _validate_committed_fixture(config: dict[str, Any]) -> None:
    if not PROTOTYPE_FIXTURE_PATH.exists():
        fail(f"missing committed prototype fixture: {display(PROTOTYPE_FIXTURE_PATH)}")
    try:
        fixture = json.loads(PROTOTYPE_FIXTURE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid committed prototype fixture JSON: {exc}")
    if fixture != config:
        fail("committed prototype fixture does not match generated config")


def _validate_config(config: dict[str, Any]) -> None:
    _validate_top_level(config)
    _validate_tables(config)
    _validate_priority_model(config)
    _validate_hard_overrides(config)
    _validate_cpp_text(render_cpp_prototype(config))
    _validate_committed_fixture(config)


def main() -> int:
    print("glyph_identity_runtime_generated_config_prototype")
    print(f"source_path={display(DEFAULT_SOURCE_PATH)}")
    print(f"role_map_fixture={ROLE_MAP_FIXTURE}")
    print("hardware_status=not_new_hardware_result")

    try:
        config = build_config_prototype()
        _validate_config(config)
    except (AssertionError, OSError, ValueError, KeyError) as exc:
        print("status=FAIL")
        print("table_count=0")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"table_count={len(config['tables'])}")
    print(f"source_table_extractor=tools/extract_glyph_identity_runtime_tables.py")
    print(f"prototype_fixture={display(PROTOTYPE_FIXTURE_PATH)}")
    print(f"generated_cpp_table_declarations={len(normalized_table_names())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
