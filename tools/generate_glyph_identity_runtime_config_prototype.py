#!/usr/bin/env python3
"""Generate a docs-only Glyph identity runtime config prototype.

The generated data is a review artifact for the current MODE_ULTIMATE identity
runtime tables and role metadata. It is not firmware source, is not included by
firmware, is not runtime-loaded config, and is not hardware validation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import (
    DEFAULT_SOURCE_PATH,
    load_source_tables,
    normalized_table_names,
    source_symbol_by_normalized_name,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROLE_MAP_FIXTURE_PATH = (
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_identity_runtime_role_map_2026-05-28.json"
)
DEFAULT_BEHAVIOR_CASES_FIXTURE_PATH = (
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_identity_runtime_behavior_cases_2026-05-28.json"
)
ALLOWED_WRITE_ROOT = REPO_ROOT / "docs" / "calibration" / "fixtures"

SCHEMA_NAME = "glyph_identity_runtime_generated_config_prototype"
CONTRACT_VERSION = 1
MODE_SCOPE = "MODE_ULTIMATE"
SOURCE_STATUS = "source_backed_prototype_not_runtime_loaded"
HARDWARE_STATUS = "not_new_hardware_result"
NUNCHUK_STATUS = "preserved_but_not_hardware_validated"
LOW_MAGNITUDE_TABLE_NAME = "Lt1LowMagnitude"


class ConfigPrototypeError(ValueError):
    """Raised when the generated prototype cannot be source-backed."""


def _relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigPrototypeError(f"invalid JSON in {_relative_path(path)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigPrototypeError(f"JSON root must be an object: {_relative_path(path)}")
    return payload


def load_role_map_fixture(path: Path = DEFAULT_ROLE_MAP_FIXTURE_PATH) -> dict[str, Any]:
    payload = load_json_object(path)
    if payload.get("schema_name") != "glyph_identity_runtime_role_map":
        raise ConfigPrototypeError("role-map fixture schema_name must be glyph_identity_runtime_role_map")
    if payload.get("mode_scope") != MODE_SCOPE:
        raise ConfigPrototypeError(f"role-map fixture mode_scope must be {MODE_SCOPE}")
    if payload.get("nunchuk_status") != NUNCHUK_STATUS:
        raise ConfigPrototypeError(f"role-map fixture nunchuk_status must be {NUNCHUK_STATUS}")
    return payload


def load_behavior_cases_fixture(path: Path = DEFAULT_BEHAVIOR_CASES_FIXTURE_PATH) -> dict[str, Any]:
    payload = load_json_object(path)
    if payload.get("schema_name") != "glyph_identity_runtime_behavior_cases":
        raise ConfigPrototypeError("behavior-case fixture schema_name must be glyph_identity_runtime_behavior_cases")
    if payload.get("mode_scope") != MODE_SCOPE:
        raise ConfigPrototypeError(f"behavior-case fixture mode_scope must be {MODE_SCOPE}")
    return payload


def _table_points_as_lists(
    tables: dict[str, tuple[tuple[int, int], ...]],
) -> dict[str, list[list[int]]]:
    return {name: [list(point) for point in tables[name]] for name in normalized_table_names()}


def _role_map_low_magnitude_points(role_map: dict[str, Any]) -> list[list[int]]:
    analog_constants = role_map.get("analog_constants")
    if not isinstance(analog_constants, dict):
        raise ConfigPrototypeError("role-map fixture missing analog_constants object")
    low_magnitude = analog_constants.get("lt1_low_magnitude_table")
    if not isinstance(low_magnitude, dict):
        raise ConfigPrototypeError("role-map fixture missing analog_constants.lt1_low_magnitude_table object")

    points: list[list[int]] = []
    for index in range(1, 10):
        point = low_magnitude.get(str(index))
        if (
            not isinstance(point, list)
            or len(point) != 2
            or any(isinstance(coord, bool) or not isinstance(coord, int) for coord in point)
        ):
            raise ConfigPrototypeError(f"lt1_low_magnitude_table.{index} must be [int, int]")
        points.append([point[0], point[1]])
    return points


def _assert_role_map_tables_agree(
    role_map: dict[str, Any],
    tables: dict[str, tuple[tuple[int, int], ...]],
) -> None:
    table_ids = role_map.get("table_ids_and_selection")
    if not isinstance(table_ids, dict):
        raise ConfigPrototypeError("role-map fixture missing table_ids_and_selection object")
    active_tables = table_ids.get("active_tables")
    if not isinstance(active_tables, list) or not all(isinstance(name, str) for name in active_tables):
        raise ConfigPrototypeError("role-map fixture table_ids_and_selection.active_tables must be a string list")

    unknown_active_tables = sorted(set(active_tables) - set(tables))
    if unknown_active_tables:
        raise ConfigPrototypeError("role-map fixture references unknown active table(s): " + ", ".join(unknown_active_tables))

    role_map_low_magnitude = _role_map_low_magnitude_points(role_map)
    source_low_magnitude = [list(point) for point in tables[LOW_MAGNITUDE_TABLE_NAME]]
    if role_map_low_magnitude != source_low_magnitude:
        raise ConfigPrototypeError("role-map LT5/RF11 low-magnitude table disagrees with source-parsed table")


def _hard_overrides(role_map: dict[str, Any]) -> dict[str, Any]:
    analog_constants = role_map.get("analog_constants")
    if not isinstance(analog_constants, dict):
        raise ConfigPrototypeError("role-map fixture missing analog_constants object")

    hard_up_b = analog_constants.get("rf7_hard_up_b")
    if not isinstance(hard_up_b, dict):
        raise ConfigPrototypeError("role-map fixture missing analog_constants.rf7_hard_up_b object")
    try:
        left = int(hard_up_b["left"])
        center = int(hard_up_b["center"])
        right = int(hard_up_b["right"])
        y = int(hard_up_b["y"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigPrototypeError("role-map rf7_hard_up_b must provide integer left/center/right/y") from exc

    rf9_null = analog_constants.get("rf9_null")
    if (
        not isinstance(rf9_null, list)
        or len(rf9_null) != 2
        or any(isinstance(coord, bool) or not isinstance(coord, int) for coord in rf9_null)
    ):
        raise ConfigPrototypeError("role-map rf9_null must be [int, int]")

    for label, point in {
        "rf7_hard_up_b.left": [left, y],
        "rf7_hard_up_b.center": [center, y],
        "rf7_hard_up_b.right": [right, y],
        "rf9_null": rf9_null,
    }.items():
        if any(coord < 0 or coord > 255 for coord in point):
            raise ConfigPrototypeError(f"{label} coordinate must be in [0,255]")

    return {
        "rf7_hard_up_b": {
            "left": [left, y],
            "center": [center, y],
            "right": [right, y],
        },
        "rf9_null": list(rf9_null),
        "rf6_low_magnitude_table": LOW_MAGNITUDE_TABLE_NAME,
    }


def _priority_stage(stage: str, priority_order: list[Any]) -> dict[str, Any]:
    if stage not in priority_order:
        raise ConfigPrototypeError(f"role-map priority order missing {stage}")
    return {"stage": stage, "source": "role_map_fixture.layering.priority"}


def _priority_model(role_map: dict[str, Any], hard_overrides: dict[str, Any]) -> dict[str, Any]:
    bindings = role_map.get("bindings")
    layering = role_map.get("layering")
    if not isinstance(bindings, dict):
        raise ConfigPrototypeError("role-map fixture missing bindings object")
    if not isinstance(layering, dict):
        raise ConfigPrototypeError("role-map fixture missing layering object")

    priority = layering.get("priority")
    if not isinstance(priority, dict):
        raise ConfigPrototypeError("role-map fixture missing layering.priority object")
    digital_priority = priority.get("digital_effective_direction")
    analog_priority = priority.get("analog")
    if not isinstance(digital_priority, list) or not all(isinstance(item, str) for item in digital_priority):
        raise ConfigPrototypeError("role-map digital_effective_direction priority must be a string list")
    if not isinstance(analog_priority, list) or not all(isinstance(item, str) for item in analog_priority):
        raise ConfigPrototypeError("role-map analog priority must be a string list")

    modifiers = bindings.get("modifiers")
    buttons = bindings.get("buttons")
    directional = bindings.get("directional")
    if not isinstance(modifiers, dict) or not isinstance(buttons, dict) or not isinstance(directional, dict):
        raise ConfigPrototypeError("role-map bindings must include buttons, directional, and modifiers objects")

    return {
        "digital_effective_direction": [
            "physical_inputs",
            "lf4_submode_active",
            "lt2_sublayer_active",
            "forced_up_resolution",
            "button_carriers",
            "ls_to_dpad_routing",
        ],
        "analog": [
            "table_output",
            "direction_plus_a",
            "rf6_low_magnitude_za",
            "rf7_hard_up_b",
            "c_stick_asdi",
            "rf9_null",
            "nunchuk_override",
        ],
        "physical_inputs": role_map.get("physical_inputs"),
        "lf8_lf7_removed": {
            "layer_direction": [],
            "scratched_inputs": ["LF8", "LF7"],
            "source": "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md",
        },
        "lf4_submode_active": {
            "condition": ["LF4"],
            "source": "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md",
        },
        "lt2_sublayer_active": {
            "condition": ["LT2", "RF1 OR RF2 OR RF3 OR RF4", "not LF4"],
            "source": "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md",
        },
        "forced_up_resolution": _priority_stage("forced_up_resolution", digital_priority),
        "button_carriers": {
            "LT1": "L",
            "LT3": "L+R",
            "LT4": "X2/MX2",
            "LT5": "X1/MX1",
            "LT6": "A",
            "LF4": "B",
            "MB4": buttons.get("MB4"),
            "MB5": buttons.get("MB5"),
            "MB6": buttons.get("MB6"),
            "MB7": buttons.get("MB7"),
            "RF1": "A",
            "RF2": "B",
            "RF3": "X",
            "RF5": "A",
            "RF6": "Z",
            "RF7": "B",
            "RF10": buttons.get("RF10"),
            "RF16": buttons.get("RF16"),
        },
        "ls_to_dpad_routing": {
            "binding": modifiers.get("RF13"),
            "source": "role_map_fixture.bindings.modifiers.RF13",
        },
        "table_output": {
            "direction_convention": role_map.get("direction_convention"),
            "table_ids_and_selection": role_map.get("table_ids_and_selection"),
        },
        "direction_plus_a": {
            "bindings": {"RF5": "DirectionPlusA"},
            "down_binding": {"LT6": bindings.get("special_functions", {}).get("LT6")},
            "source": "docs/calibration/glyph_gfw3_runtime_remap_rework_spec_2026-06-04.md",
        },
        "rf6_low_magnitude_za": {
            "bindings": {"RF6": "Z"},
            "table": hard_overrides["rf6_low_magnitude_table"],
        },
        "c_stick_asdi": {
            "condition": ["RT2/RT3/RT4/RT5 diagonal C-stick"],
            "source": "src/modes/Ultimate.cpp",
        },
        "rf7_hard_up_b": hard_overrides["rf7_hard_up_b"],
        "rf9_null": hard_overrides["rf9_null"],
        "nunchuk_override": {
            "status": role_map.get("nunchuk_status"),
            "source": "role_map_fixture.nunchuk_status",
        },
    }


def _role_binding_count(role_bindings: Any) -> int:
    if not isinstance(role_bindings, dict):
        return 0
    count = 0
    for value in role_bindings.values():
        if isinstance(value, dict):
            count += len(value)
        elif isinstance(value, list):
            count += len(value)
    return count


def _coverage_metadata(behavior_cases: dict[str, Any], behavior_cases_path: Path) -> dict[str, Any]:
    cases = behavior_cases.get("cases")
    if not isinstance(cases, list):
        raise ConfigPrototypeError("behavior-case fixture cases must be a list")
    categories = sorted(
        {
            case.get("category")
            for case in cases
            if isinstance(case, dict) and isinstance(case.get("category"), str)
        }
    )
    return {
        "behavior_cases_fixture": _relative_path(behavior_cases_path),
        "case_count": len(cases),
        "category_count": len(categories),
        "categories": categories,
        "hardware_status": behavior_cases.get("hardware_status"),
    }


def build_config_prototype(
    source_path: Path = DEFAULT_SOURCE_PATH,
    role_map_path: Path = DEFAULT_ROLE_MAP_FIXTURE_PATH,
    behavior_cases_path: Path = DEFAULT_BEHAVIOR_CASES_FIXTURE_PATH,
) -> dict[str, Any]:
    tables = load_source_tables(source_path)
    role_map = load_role_map_fixture(role_map_path)
    behavior_cases = load_behavior_cases_fixture(behavior_cases_path)
    _assert_role_map_tables_agree(role_map, tables)

    hard_overrides = _hard_overrides(role_map)
    role_bindings = role_map.get("bindings")
    if not isinstance(role_bindings, dict):
        raise ConfigPrototypeError("role-map fixture bindings must be an object")

    return {
        "schema_name": SCHEMA_NAME,
        "contract_version": CONTRACT_VERSION,
        "mode_scope": MODE_SCOPE,
        "source_status": SOURCE_STATUS,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
        "direction_convention": role_map.get("direction_convention"),
        "source_authority": {
            "runtime": _relative_path(source_path),
            "table_extractor": "tools/extract_glyph_identity_runtime_tables.py",
            "role_map_fixture": _relative_path(role_map_path),
            "behavior_cases_fixture": _relative_path(behavior_cases_path),
            "role_map_doc": "docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md",
            "behavior_cases_doc": "docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md",
            "table_source_sync_doc": "docs/calibration/glyph_identity_runtime_table_source_sync_2026-05-28.md",
        },
        "tables": _table_points_as_lists(tables),
        "table_source_symbols": source_symbol_by_normalized_name(),
        "role_bindings": role_bindings,
        "priority_model": _priority_model(role_map, hard_overrides),
        "hard_overrides": hard_overrides,
        "suppression_rules": role_map.get("suppression_rules"),
        "coverage_metadata": _coverage_metadata(behavior_cases, behavior_cases_path),
        "non_goals": [
            "not_runtime_loaded",
            "not_firmware_source",
            "not_hardware_validation",
            "not_serial_device_write_path",
            "not_senscope_game_semantics",
            "does_not_alter_table_values_or_behavior",
        ],
    }


def render_cpp_prototype(config: dict[str, Any]) -> str:
    tables = config.get("tables")
    symbols = config.get("table_source_symbols")
    if not isinstance(tables, dict) or not isinstance(symbols, dict):
        raise ConfigPrototypeError("config must include tables and table_source_symbols")

    lines: list[str] = [
        "// generated prototype only",
        "// do not include in firmware",
        "// not firmware source",
        "// not runtime-loaded config",
        "// not hardware validation",
        f"// schema_name={config.get('schema_name')}",
        f"// source_status={config.get('source_status')}",
        f"// hardware_status={config.get('hardware_status')}",
        "",
    ]

    for name in normalized_table_names():
        symbol = symbols.get(name)
        table = tables.get(name)
        if not isinstance(symbol, str) or not isinstance(table, list):
            raise ConfigPrototypeError(f"config table metadata missing for {name}")
        lines.append(f"constexpr StickPoint {symbol}[9] = {{")
        for point in table:
            if not isinstance(point, list) or len(point) != 2:
                raise ConfigPrototypeError(f"config table {name} contains malformed point")
            lines.append(f"    {{{int(point[0])}, {int(point[1])}}},")
        lines.append("};")
        lines.append("")

    role_bindings = config.get("role_bindings")
    if isinstance(role_bindings, dict):
        lines.append("// role metadata from role-map fixture")
        for section_name in sorted(role_bindings):
            section = role_bindings[section_name]
            if not isinstance(section, dict):
                continue
            for key in sorted(section):
                lines.append(f"// role_binding.{section_name}.{key} = {section[key]}")
        lines.append("")

    priority_model = config.get("priority_model")
    if isinstance(priority_model, dict):
        for stage_name in ("digital_effective_direction", "analog"):
            stage = priority_model.get(stage_name)
            if isinstance(stage, list):
                lines.append(f"// priority.{stage_name} = " + " -> ".join(str(item) for item in stage))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _write_json(path: Path, config: dict[str, Any]) -> None:
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved_root = ALLOWED_WRITE_ROOT.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ConfigPrototypeError("--write-json path must be under docs/calibration/fixtures/") from exc
    resolved_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_text_summary(config: dict[str, Any], write_json_path: Path | None = None) -> None:
    role_binding_count = _role_binding_count(config.get("role_bindings"))
    source_authority = config.get("source_authority")
    print("glyph_identity_runtime_generated_config_prototype")
    print("status=PASS")
    print(f"table_count={len(config.get('tables', {}))}")
    print(f"role_binding_count={role_binding_count}")
    if isinstance(source_authority, dict):
        for key in sorted(source_authority):
            print(f"source_{key}={source_authority[key]}")
    print(f"hardware_status={config.get('hardware_status')}")
    if write_json_path is not None:
        print(f"wrote_json={_relative_path(write_json_path)}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="print deterministic JSON")
    output.add_argument("--cpp", action="store_true", help="print deterministic C++-shaped prototype text")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH, help="path to Ultimate.cpp")
    parser.add_argument("--role-map", type=Path, default=DEFAULT_ROLE_MAP_FIXTURE_PATH, help="role-map JSON fixture")
    parser.add_argument(
        "--behavior-cases",
        type=Path,
        default=DEFAULT_BEHAVIOR_CASES_FIXTURE_PATH,
        help="behavior-case JSON fixture",
    )
    parser.add_argument("--write-json", type=Path, help="write config JSON under docs/calibration/fixtures/")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        config = build_config_prototype(args.source, args.role_map, args.behavior_cases)
        if args.write_json is not None:
            _write_json(args.write_json, config)
    except (OSError, ConfigPrototypeError, KeyError) as exc:
        print("glyph_identity_runtime_generated_config_prototype")
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    if args.json:
        print(json.dumps(config, indent=2, sort_keys=True))
    elif args.cpp:
        try:
            print(render_cpp_prototype(config), end="")
        except ConfigPrototypeError as exc:
            print("glyph_identity_runtime_generated_config_prototype")
            print("status=FAIL")
            print(f"error={exc}")
            return 1
    else:
        print_text_summary(config, args.write_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
