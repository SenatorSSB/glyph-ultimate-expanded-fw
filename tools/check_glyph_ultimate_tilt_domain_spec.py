#!/usr/bin/env python3
"""Read-only validator for glyph_ultimate_tilt_domain_spec fixture."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_ultimate_tilt_domain_spec.json"

EXPECTED_KEYS = {str(index) for index in range(1, 10)}
EXPECTED_BASE = {
    "1": {"x": 28, "y": 28},
    "2": {"x": 128, "y": 28},
    "3": {"x": 228, "y": 28},
    "4": {"x": 28, "y": 128},
    "5": {"x": 128, "y": 128},
    "6": {"x": 228, "y": 128},
    "7": {"x": 28, "y": 228},
    "8": {"x": 128, "y": 228},
    "9": {"x": 228, "y": 228},
}
EXPECTED_TILT1 = {
    "1": {"x": 187, "y": 87},
    "2": {"x": 128, "y": 87},
    "3": {"x": 69, "y": 87},
    "4": {"x": 187, "y": 128},
    "5": {"x": 128, "y": 128},
    "6": {"x": 69, "y": 128},
    "7": {"x": 187, "y": 169},
    "8": {"x": 128, "y": 169},
    "9": {"x": 69, "y": 169},
}
EXPECTED_TILT2 = {
    "1": {"x": 88, "y": 79},
    "2": {"x": 128, "y": 79},
    "3": {"x": 168, "y": 79},
    "4": {"x": 88, "y": 128},
    "5": {"x": 128, "y": 128},
    "6": {"x": 168, "y": 128},
    "7": {"x": 88, "y": 177},
    "8": {"x": 128, "y": 177},
    "9": {"x": 168, "y": 177},
}


def _load_fixture() -> dict[str, object]:
    if not FIXTURE_PATH.exists():
        raise AssertionError(f"missing fixture: {FIXTURE_PATH}")
    try:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON in fixture: {exc}") from exc
    if not isinstance(payload, dict):
        raise AssertionError("fixture root must be an object")
    return payload


def _assert_table_shape(table_name: str, table: object) -> dict[str, dict[str, int]]:
    if not isinstance(table, dict):
        raise AssertionError(f"{table_name} must be an object")
    keys = set(table.keys())
    if keys != EXPECTED_KEYS:
        raise AssertionError(f"{table_name} keys mismatch: expected {sorted(EXPECTED_KEYS)}, got {sorted(keys)}")

    normalized: dict[str, dict[str, int]] = {}
    for direction in sorted(EXPECTED_KEYS, key=int):
        raw_point = table[direction]
        if not isinstance(raw_point, dict):
            raise AssertionError(f"{table_name}[{direction}] must be an object")
        if set(raw_point.keys()) != {"x", "y"}:
            raise AssertionError(f"{table_name}[{direction}] must have only x/y keys")

        x = raw_point["x"]
        y = raw_point["y"]
        if not isinstance(x, int) or not isinstance(y, int):
            raise AssertionError(f"{table_name}[{direction}] x/y must be integers")
        if not (0 <= x <= 255 and 0 <= y <= 255):
            raise AssertionError(f"{table_name}[{direction}] out of byte range: ({x}, {y})")

        normalized[direction] = {"x": x, "y": y}
    return normalized


def _assert_neutral(table_name: str, table: dict[str, dict[str, int]]) -> None:
    neutral = table["5"]
    if neutral != {"x": 128, "y": 128}:
        raise AssertionError(f"{table_name}[5] must equal neutral (128,128), got {neutral}")


def _assert_expected_table(
    table_name: str,
    observed: dict[str, dict[str, int]],
    expected: dict[str, dict[str, int]],
) -> None:
    if observed != expected:
        raise AssertionError(f"{table_name} table mismatch with expected values")


def _assert_bool(mapping: dict[str, object], key: str, expected: bool) -> None:
    if mapping.get(key) is not expected:
        raise AssertionError(f"{key} must be {expected}, got {mapping.get(key)!r}")


def _assert_button_id_confirmation(spec: dict[str, object]) -> None:
    confirmation = spec.get("button_id_confirmation")
    if not isinstance(confirmation, dict):
        raise AssertionError("button_id_confirmation must be an object")

    status = confirmation.get("status")
    if status != "CONFIRMED_FOR_UPLOADED_MVP_LAYOUT":
        return

    tilt1 = confirmation.get("tilt1")
    tilt2 = confirmation.get("tilt2")
    runtime_semantics = confirmation.get("runtime_semantics")
    rejected = confirmation.get("rejected_button_ids")

    if not isinstance(tilt1, dict):
        raise AssertionError("button_id_confirmation.tilt1 must be an object")
    if not isinstance(tilt2, dict):
        raise AssertionError("button_id_confirmation.tilt2 must be an object")
    if not isinstance(runtime_semantics, dict):
        raise AssertionError("button_id_confirmation.runtime_semantics must be an object")
    if not isinstance(rejected, list):
        raise AssertionError("button_id_confirmation.rejected_button_ids must be a list")

    expected_fields = {
        "tilt1.physical_button": (tilt1.get("physical_button"), "BTN_RF3"),
        "tilt1.logical_post_remap_input": (tilt1.get("logical_post_remap_input"), "BTN_LT1"),
        "tilt1.future_runtime_input": (tilt1.get("future_runtime_input"), "inputs.lt1"),
        "tilt2.physical_button": (tilt2.get("physical_button"), "BTN_RF4"),
        "tilt2.logical_post_remap_input": (tilt2.get("logical_post_remap_input"), "BTN_LT2"),
        "tilt2.future_runtime_input": (tilt2.get("future_runtime_input"), "inputs.lt2"),
    }
    for label, (observed, expected) in expected_fields.items():
        if observed != expected:
            raise AssertionError(f"button_id_confirmation.{label} expected {expected!r}, got {observed!r}")

    _assert_bool(runtime_semantics, "use_post_remap_logical_inputs", True)
    _assert_bool(runtime_semantics, "bypass_remap_with_physical_inputs", False)
    _assert_bool(runtime_semantics, "profile_remap_change_required", False)
    _assert_bool(runtime_semantics, "runtime_approved", True)

    rejected_ids = {entry.get("id") for entry in rejected if isinstance(entry, dict)}
    if "BTN_RF5" not in rejected_ids:
        raise AssertionError("button_id_confirmation.rejected_button_ids must include BTN_RF5")


def _assert_runtime_implementation(spec: dict[str, object]) -> None:
    runtime = spec.get("runtime_implementation")
    if not isinstance(runtime, dict):
        raise AssertionError("runtime_implementation must be an object")

    expected_fields = {
        "status": "IMPLEMENTED_IN_NATIVE_ULTIMATE",
        "source_file": "src/modes/Ultimate.cpp",
        "tilt1_runtime_input": "inputs.lt1",
        "tilt2_runtime_input": "inputs.lt2",
    }
    for key, expected in expected_fields.items():
        observed = runtime.get(key)
        if observed != expected:
            raise AssertionError(f"runtime_implementation.{key} expected {expected!r}, got {observed!r}")

    for key in (
        "uses_post_remap_logical_inputs",
        "left_stick_only",
        "preserve_right_stick",
        "preserve_triggers",
        "no_overflow_dependency",
    ):
        _assert_bool(runtime, key, True)

    _assert_bool(runtime, "hardware_tested", False)


def main() -> None:
    spec = _load_fixture()

    if spec.get("source_kind") != "USER_SUPPLIED_DOMAIN_SPEC":
        raise AssertionError("source_kind must be USER_SUPPLIED_DOMAIN_SPEC")

    status = spec.get("status")
    if not isinstance(status, dict):
        raise AssertionError("status must be an object")
    if status.get("firmware_implemented") is not True:
        raise AssertionError("status.firmware_implemented must be true")
    if status.get("hardware_tested") is not False:
        raise AssertionError("status.hardware_tested must be false")
    if status.get("runtime_behavior_changed_in_branch") is not True:
        raise AssertionError("status.runtime_behavior_changed_in_branch must be true")

    tables = spec.get("tables")
    if not isinstance(tables, dict):
        raise AssertionError("tables must be an object")

    base = _assert_table_shape("tables.base", tables.get("base"))
    tilt1 = _assert_table_shape("tables.tilt1", tables.get("tilt1"))
    tilt2 = _assert_table_shape("tables.tilt2", tables.get("tilt2"))

    _assert_neutral("tables.base", base)
    _assert_neutral("tables.tilt1", tilt1)
    _assert_neutral("tables.tilt2", tilt2)

    _assert_expected_table("tables.base", base, EXPECTED_BASE)
    _assert_expected_table("tables.tilt1", tilt1, EXPECTED_TILT1)
    _assert_expected_table("tables.tilt2", tilt2, EXPECTED_TILT2)

    if spec.get("no_overflow_dependency") is not True:
        raise AssertionError("no_overflow_dependency must be true")

    target_outputs = spec.get("target_outputs")
    if target_outputs != ["left_stick"]:
        raise AssertionError(f"target_outputs must be exactly ['left_stick'], got {target_outputs}")

    preserve_outputs = spec.get("preserve_outputs")
    if not isinstance(preserve_outputs, list):
        raise AssertionError("preserve_outputs must be a list")
    preserve_set = set(preserve_outputs)
    if "right_stick" not in preserve_set or "triggers" not in preserve_set:
        raise AssertionError("preserve_outputs must include right_stick and triggers")

    _assert_button_id_confirmation(spec)
    _assert_runtime_implementation(spec)

    print(
        "glyph_ultimate_tilt_domain_spec: pass "
        "tables=3 directions=9 button_id_confirmation=confirmed "
        "runtime_implementation=native_ultimate byte_safe=true no_overflow_dependency=true"
    )


if __name__ == "__main__":
    main()
