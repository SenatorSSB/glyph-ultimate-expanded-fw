#!/usr/bin/env python3
"""Validate native Ultimate table fixture contract JSON.

This is a read-only contract checker. It validates fixture shape and coordinate
math before any production runtime table patch exists.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_native_ultimate_table_contract_TEMPLATE.json"
DIRECTIONS = {str(index) for index in range(1, 10)}


class DuplicateKeyTracker:
    def __init__(self) -> None:
        self.duplicates: list[str] = []

    def hook(self, pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        counts: dict[str, int] = defaultdict(int)
        result: dict[str, Any] = {}
        for key, value in pairs:
            counts[key] += 1
            if counts[key] > 1:
                self.duplicates.append(key)
            result[key] = value
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a Glyph native Ultimate table contract fixture.")
    parser.add_argument("fixture", nargs="?", type=Path, default=DEFAULT_FIXTURE)
    return parser.parse_args()


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path, errors: list[str]) -> tuple[dict[str, Any] | None, list[str]]:
    tracker = DuplicateKeyTracker()
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text, object_pairs_hook=tracker.hook)
    except Exception as exc:  # pragma: no cover - defensive parse guard
        errors.append(f"failed to parse JSON: {exc}")
        return None, tracker.duplicates
    if not isinstance(payload, dict):
        errors.append("root must be a JSON object")
        return None, tracker.duplicates
    return payload, tracker.duplicates


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    return value


def require_int(value: Any, label: str, errors: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{label} must be an integer")
        return None
    return value


def validate_coord(value: Any, label: str, errors: list[str]) -> tuple[int, int] | None:
    obj = require_object(value, label, errors)
    if obj is None:
        return None
    x_value = require_int(obj.get("x"), f"{label}.x", errors)
    y_value = require_int(obj.get("y"), f"{label}.y", errors)
    if x_value is None or y_value is None:
        return None
    if not 0 <= x_value <= 255:
        errors.append(f"{label}.x must be in [0,255], got {x_value}")
    if not 0 <= y_value <= 255:
        errors.append(f"{label}.y must be in [0,255], got {y_value}")
    return x_value, y_value


def validate_offset(value: Any, label: str, errors: list[str]) -> tuple[int, int] | None:
    obj = require_object(value, label, errors)
    if obj is None:
        return None
    x_value = require_int(obj.get("x"), f"{label}.x", errors)
    y_value = require_int(obj.get("y"), f"{label}.y", errors)
    if x_value is None or y_value is None:
        return None
    return x_value, y_value


def validate_direction_table(table: Any, state_label: str, errors: list[str]) -> None:
    table_obj = require_object(table, f"{state_label}.direction_table", errors)
    if table_obj is None:
        return
    keys = set(table_obj.keys())
    if keys != DIRECTIONS:
        missing = sorted(DIRECTIONS - keys)
        extra = sorted(keys - DIRECTIONS)
        if missing:
            errors.append(f"{state_label}.direction_table missing directions: {', '.join(missing)}")
        if extra:
            errors.append(f"{state_label}.direction_table has invalid directions: {', '.join(extra)}")
    if "5" not in table_obj:
        errors.append(f"{state_label}.direction_table must include neutral direction 5")

    for direction in sorted(keys & DIRECTIONS, key=int):
        entry_label = f"{state_label}.direction_table[{direction}]"
        entry = require_object(table_obj[direction], entry_label, errors)
        if entry is None:
            continue
        raw = validate_coord(entry.get("raw"), f"{entry_label}.raw", errors)
        offset = validate_offset(entry.get("center_relative"), f"{entry_label}.center_relative", errors)
        if raw is not None and offset is not None:
            expected = (raw[0] - 128, raw[1] - 128)
            if offset != expected:
                errors.append(
                    f"{entry_label}.center_relative must equal raw minus 128; "
                    f"got {offset}, expected {expected}",
                )


def validate_payload(payload: dict[str, Any], duplicate_keys: list[str]) -> list[str]:
    errors: list[str] = []
    if duplicate_keys:
        errors.append("duplicate JSON object keys detected: " + ", ".join(sorted(set(duplicate_keys))))

    version = require_int(payload.get("table_contract_version"), "table_contract_version", errors)
    if version is not None and version < 1:
        errors.append("table_contract_version must be >= 1")

    if "runtime_branch_exclusivity" not in payload:
        errors.append("runtime_branch_exclusivity metadata is required")
    elif not isinstance(payload.get("runtime_branch_exclusivity"), dict):
        errors.append("runtime_branch_exclusivity must be an object")

    if "conflict_chord_policy" not in payload:
        errors.append("conflict_chord_policy metadata is required")
    elif not isinstance(payload.get("conflict_chord_policy"), dict):
        errors.append("conflict_chord_policy must be an object")

    states = payload.get("modifier_states")
    if not isinstance(states, list) or not states:
        errors.append("modifier_states must be a non-empty list")
        return errors

    seen_state_ids: set[str] = set()
    for state_index, state in enumerate(states):
        state_label = f"modifier_states[{state_index}]"
        state_obj = require_object(state, state_label, errors)
        if state_obj is None:
            continue
        state_id = state_obj.get("state_id")
        if not isinstance(state_id, str) or not state_id.strip():
            errors.append(f"{state_label}.state_id must be a non-empty string")
        elif state_id in seen_state_ids:
            errors.append(f"duplicate modifier state_id: {state_id}")
        else:
            seen_state_ids.add(state_id)

        modifier_sources = state_obj.get("modifier_sources")
        if not isinstance(modifier_sources, list):
            errors.append(f"{state_label}.modifier_sources must be a list")
        validate_direction_table(state_obj.get("direction_table"), state_label, errors)

    return errors


def main() -> int:
    args = parse_args()
    path = args.fixture if args.fixture.is_absolute() else REPO_ROOT / args.fixture
    errors: list[str] = []
    payload, duplicate_keys = load_json(path, errors)
    if payload is not None:
        errors.extend(validate_payload(payload, duplicate_keys))

    print("glyph_native_ultimate_table_fixture")
    print(f"fixture={display(path)}")
    print(f"status={'FAIL' if errors else 'PASS'}")
    if errors:
        print("errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    states = payload.get("modifier_states", []) if payload else []
    print(f"modifier_states={len(states)}")
    print("directions=1,2,3,4,5,6,7,8,9")
    print("neutral_direction=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
