#!/usr/bin/env python3
"""Offline dry-run evaluator for coordinate-native runtime profile fixtures.

Offline tooling only. The generated result is not loaded by firmware. Runtime-
loaded config remains not implemented. No WebSerial/device write, no
persistence/storage, no flashing automation, and no active RuntimeConfigView
publication.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from check_glyph_coordinate_native_runtime_profile_contract import (
    CoordinateNativeRuntimeProfileContractError,
    load_json_object,
    rel,
    validate_profile_fixture,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_NOTE = (
    "offline tooling only; generated result is not loaded by firmware; "
    "runtime-loaded config remains not implemented; no WebSerial/device write; "
    "no persistence/storage; no flashing automation; no active RuntimeConfigView publication"
)


class CoordinateNativeRuntimeProfileDryRunError(Exception):
    """Raised when the offline dry-run evaluator rejects a case."""

    def __init__(self, selection_status: str, message: str, trace: list[dict[str, Any]]) -> None:
        super().__init__(message)
        self.selection_status = selection_status
        self.message = message
        self.trace = trace


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(selection_status: str, message: str, trace: list[dict[str, Any]]) -> None:
    raise CoordinateNativeRuntimeProfileDryRunError(selection_status, message, trace)


def trace_item(step: str, decision: str, reason: str, inputs: list[str]) -> dict[str, Any]:
    return {
        "step": step,
        "decision": decision,
        "reason": reason,
        "inputs": inputs,
    }


def load_required_object(path: Path, label: str) -> dict[str, Any]:
    payload = load_json_object(path)
    if not isinstance(payload, dict):
        raise CoordinateNativeRuntimeProfileContractError(f"{label} must be an object")
    return payload


def canonical_string_list(values: Any, label: str) -> list[str]:
    if not isinstance(values, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            f"{label} must be a list",
            [],
        )
    result: list[str] = []
    for index, item in enumerate(values):
        if not isinstance(item, str) or not item:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"{label}[{index}] must be a non-empty string",
                [],
            )
        result.append(item)
    return result


def validate_case_fixture(case: dict[str, Any]) -> None:
    for field in ("case_id", "profile_path", "input_state"):
        if field not in case:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"case fixture missing required field {field}",
                [],
            )
    if not isinstance(case.get("case_id"), str) or not case.get("case_id"):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "case_id must be a non-empty string",
            [],
        )
    if not isinstance(case.get("profile_path"), str) or not case.get("profile_path"):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "profile_path must be a non-empty string",
            [],
        )
    if not isinstance(case.get("input_state"), dict):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "input_state must be an object",
            [],
        )


def validate_input_state(input_state: dict[str, Any], profile: dict[str, Any]) -> tuple[list[str], list[str], str | None]:
    roles = profile.get("roles")
    if not isinstance(roles, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "profile.roles must be a list",
            [],
        )
    known_roles = {
        role.get("role_id")
        for role in roles
        if isinstance(role, dict) and isinstance(role.get("role_id"), str)
    }

    for field in ("state_id", "activations", "inactive_inputs", "resolved_direction_key"):
        if field not in input_state:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"input_state missing required field {field}",
                [],
            )
    state_id = input_state.get("state_id")
    if not isinstance(state_id, str) or not state_id:
        raise CoordinateNativeRuntimeProfileDryRunError("invalid_input", "input_state.state_id must be a non-empty string", [])
    activations = input_state.get("activations")
    if not isinstance(activations, list) or not activations:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "input_state.activations must be a non-empty list",
            [],
        )
    activation_role_ids: list[str] = []
    for index, activation in enumerate(activations):
        if not isinstance(activation, dict):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"input_state.activations[{index}] must be an object",
                [],
            )
        for field in ("input_id", "role_id", "pressed"):
            if field not in activation:
                raise CoordinateNativeRuntimeProfileDryRunError(
                    "invalid_input",
                    f"input_state.activations[{index}] missing required field {field}",
                    [],
                )
        if not isinstance(activation.get("input_id"), str) or not activation.get("input_id"):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"input_state.activations[{index}].input_id must be a non-empty string",
                [],
            )
        role_id = activation.get("role_id")
        if not isinstance(role_id, str) or not role_id:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"input_state.activations[{index}].role_id must be a non-empty string",
                [],
            )
        if role_id not in known_roles:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"input_state.activations[{index}].role_id references unknown role_id {role_id}",
                [],
            )
        if not isinstance(activation.get("pressed"), bool):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"input_state.activations[{index}].pressed must be a boolean",
                [],
            )
        if activation["pressed"]:
            activation_role_ids.append(role_id)

    inactive_inputs = input_state.get("inactive_inputs")
    if not isinstance(inactive_inputs, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "input_state.inactive_inputs must be a list",
            [],
        )
    canonical_string_list(inactive_inputs, "input_state.inactive_inputs")

    resolved_direction_key = input_state.get("resolved_direction_key")
    if not isinstance(resolved_direction_key, int) or isinstance(resolved_direction_key, bool):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "resolved_direction_key must be an integer",
            [],
        )
    if not 1 <= resolved_direction_key <= 9:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "resolved_direction_key must be 1..9",
            [],
        )

    active_role_ids = canonical_string_list(input_state.get("active_role_ids"), "input_state.active_role_ids")
    active_modifier_ids = canonical_string_list(
        input_state.get("active_modifier_ids"), "input_state.active_modifier_ids"
    )
    active_selector_ids = set(active_role_ids) | set(active_modifier_ids)
    pressed_role_ids = set(activation_role_ids)
    if active_selector_ids != pressed_role_ids:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "active_role_ids and active_modifier_ids must match the pressed activation role_ids",
            [],
        )
    routing_sublayer = input_state.get("routing_sublayer")
    if routing_sublayer is not None and (not isinstance(routing_sublayer, str) or not routing_sublayer):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "input_state.routing_sublayer must be a non-empty string when provided",
            [],
        )

    return active_role_ids, active_modifier_ids, routing_sublayer


def index_points(points: list[dict[str, Any]], label: str) -> dict[int, tuple[int, int]]:
    mapping: dict[int, tuple[int, int]] = {}
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"{label}[{index}] must be an object",
                [],
            )
        direction_key = point.get("direction_key")
        x = point.get("x")
        y = point.get("y")
        if not isinstance(direction_key, int) or isinstance(direction_key, bool) or not 1 <= direction_key <= 9:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"{label}[{index}].direction_key must be 1..9",
                [],
            )
        if not isinstance(x, int) or isinstance(x, bool) or not isinstance(y, int) or isinstance(y, bool):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"{label}[{index}] coordinates must be integers",
                [],
            )
        mapping[direction_key] = (x, y)
    return mapping


def build_lookup(entries: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"{key}[{index}] must be an object",
                [],
            )
        identifier = entry.get(key)
        if not isinstance(identifier, str) or not identifier:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"{key} entries must contain {key}",
                [],
            )
        if identifier in lookup:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"duplicate {key} {identifier}",
                [],
            )
        lookup[identifier] = entry
    return lookup


def merge_side_effect_ids(
    table: dict[str, Any],
    side_effect_lookup: dict[str, dict[str, Any]],
) -> list[str]:
    refs = table.get("digital_side_effect_refs")
    if not isinstance(refs, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "digital_side_effect_refs must be a list",
            [],
        )
    resolved: list[tuple[int, str]] = []
    seen: dict[str, dict[str, Any]] = {}
    for ref in refs:
        if not isinstance(ref, str) or not ref:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                "digital_side_effect_refs entries must be non-empty strings",
                [],
            )
        effect = side_effect_lookup.get(ref)
        if effect is None:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "missing_table",
                f"digital_side_effect_refs references unknown effect_id {ref}",
                [],
            )
        if ref in seen and seen[ref] != effect:
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"conflicting duplicate effect_id {ref}",
                [],
            )
        seen[ref] = effect
    for effect_id, effect in seen.items():
        priority = effect.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"digital side effect {effect_id} priority must be an integer",
                [],
            )
        resolved.append((priority, effect_id))
    resolved.sort(key=lambda item: (item[0], item[1]))
    return [effect_id for _, effect_id in resolved]


def build_success_result(
    *,
    case_id: str,
    profile_path: Path,
    case_path: Path,
    resolved_direction_key: int,
    selected_rule: dict[str, Any],
    selected_table: dict[str, Any],
    selected_coordinate: tuple[int, int],
    selected_side_effect_ids: list[str],
    trace: list[dict[str, Any]],
    explanation: dict[str, str],
) -> dict[str, Any]:
    return {
        "status": "PASS",
        "offline_only": True,
        "case_id": case_id,
        "profile_path": display(profile_path),
        "case_path": display(case_path),
        "selection_result": {
            "selection_status": "selected",
            "resolved_direction_key": resolved_direction_key,
            "selected_rule_id": selected_rule["rule_id"],
            "selected_table_id": selected_table["table_id"],
            "selected_coordinate": {"x": selected_coordinate[0], "y": selected_coordinate[1]},
            "selected_side_effect_ids": selected_side_effect_ids,
            "trace": trace,
            "explanation": explanation,
        },
    }


def build_failure_result(
    *,
    case_id: str,
    profile_path: Path,
    case_path: Path,
    selection_status: str,
    resolved_direction_key: int | None,
    message: str,
    trace: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "status": "FAIL",
        "offline_only": True,
        "case_id": case_id,
        "profile_path": display(profile_path),
        "case_path": display(case_path),
        "selection_result": {
            "selection_status": selection_status,
            "resolved_direction_key": resolved_direction_key,
            "selected_rule_id": None,
            "selected_table_id": None,
            "selected_coordinate": None,
            "selected_side_effect_ids": [],
            "trace": trace,
            "explanation": {
                "selection_summary": message,
                "priority_summary": "Selection failed before a deterministic winner could be emitted",
                "boundary_summary": BOUNDARY_NOTE,
            },
        },
    }


def evaluate_case(profile_path: Path, case_path: Path) -> dict[str, Any]:
    case = load_required_object(case_path, "case fixture")
    validate_case_fixture(case)
    if case["profile_path"] != display(profile_path) and case["profile_path"] != str(profile_path):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "case fixture profile_path must match the CLI profile path",
            [],
        )

    case_id = case["case_id"]

    try:
        profile = load_required_object(profile_path, "profile fixture")
        validate_profile_fixture(profile, label=rel(profile_path), require_selection_semantics=True)
    except CoordinateNativeRuntimeProfileContractError as exc:
        message = str(exc)
        if "unknown modifier_table_ref" in message or "missing modifier_table_ref" in message:
            return build_failure_result(
                case_id=case_id,
                profile_path=profile_path,
                case_path=case_path,
                selection_status="missing_table",
                resolved_direction_key=None,
                message=message,
                trace=[trace_item("validate_profile", "reject_profile", message, [display(profile_path)])],
            )
        if "routing_rules priorities must be strictly increasing" in message:
            return build_failure_result(
                case_id=case_id,
                profile_path=profile_path,
                case_path=case_path,
                selection_status="ambiguous_tie",
                resolved_direction_key=None,
                message=message,
                trace=[trace_item("validate_profile", "reject_profile", message, [display(profile_path)])],
            )
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            message,
            [trace_item("validate_profile", "reject_profile", message, [display(profile_path)])],
        ) from exc

    input_state = case["input_state"]
    active_role_ids, active_modifier_ids, routing_sublayer = validate_input_state(input_state, profile)
    resolved_direction_key = input_state["resolved_direction_key"]
    trace: list[dict[str, Any]] = [
        trace_item(
            "normalize_input_state",
            "use explicit activations",
            "offline tooling only and input_state is fixture-backed",
            [
                f"state_id={input_state['state_id']}",
                f"active_role_ids={','.join(active_role_ids)}",
                f"active_modifier_ids={','.join(active_modifier_ids)}",
            ],
        ),
        trace_item(
            "resolve_direction_key",
            "use resolver output",
            "resolved_direction_key is the only direction source",
            [f"resolved_direction_key={resolved_direction_key}"],
        ),
    ]

    routing_rules = profile.get("routing_rules")
    if not isinstance(routing_rules, list) or not routing_rules:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "profile.routing_rules must be a non-empty list",
            trace,
        )
    eligible_rules: list[tuple[int, int, dict[str, Any]]] = []
    for index, rule in enumerate(routing_rules):
        if not isinstance(rule, dict):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"routing_rules[{index}] must be an object",
                trace,
            )
        sublayer = rule.get("sublayer")
        if sublayer not in set(active_role_ids) | set(active_modifier_ids):
            continue
        if routing_sublayer is not None and sublayer != routing_sublayer:
            continue
        priority = rule.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise CoordinateNativeRuntimeProfileDryRunError(
                "invalid_input",
                f"routing_rules[{index}].priority must be an integer",
                trace,
            )
        eligible_rules.append((priority, index, rule))

    if not eligible_rules:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "no routing rule matched the active role/modifier state",
            trace
            + [
                trace_item(
                    "select_rule",
                    "reject",
                    "no eligible rule matched the active role/modifier state",
                    [f"active_selector_ids={','.join(sorted(set(active_role_ids) | set(active_modifier_ids)))}"],
                )
            ],
        )

    priorities = [priority for priority, _, _ in eligible_rules]
    if len(priorities) != len(set(priorities)):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "ambiguous_tie",
            "routing rule priorities must be unique for the active selection set",
            trace
            + [
                trace_item(
                    "select_rule",
                    "reject_profile",
                    "ambiguous priority tie",
                    [f"candidate_priorities={','.join(str(priority) for priority in priorities)}"],
                )
            ],
        )

    eligible_rules.sort(key=lambda item: (item[0], item[2]["sublayer"], item[2]["rule_id"], item[1]))
    selected_rule = eligible_rules[0][2]
    selected_rule_id = selected_rule["rule_id"]
    selected_table_ref = selected_rule["modifier_table_ref"]
    trace.append(
        trace_item(
            "select_rule",
            "select first eligible rule",
            "ascending priority with deterministic tie rejection",
            [f"selected_rule_id={selected_rule_id}", f"selected_table_ref={selected_table_ref}"],
        )
    )

    tables = profile.get("modifier_tables")
    if not isinstance(tables, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "profile.modifier_tables must be a list",
            trace,
        )
    table_lookup = build_lookup(tables, "table_id")
    selected_table = table_lookup.get(selected_table_ref)
    if selected_table is None:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "missing_table",
            f"routing rule references unknown modifier_table_ref {selected_table_ref}",
            trace,
        )
    trace.append(
        trace_item(
            "select_table",
            "use referenced modifier table",
            "table reference resolved successfully",
            [f"table_id={selected_table_ref}"],
        )
    )

    direction_points = selected_table.get("direction_points")
    if not isinstance(direction_points, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "selected modifier table direction_points must be a list",
            trace,
        )
    point_lookup = index_points(direction_points, f"modifier table {selected_table_ref}.direction_points")
    selected_coordinate = point_lookup.get(resolved_direction_key)
    if selected_coordinate is None:
        raise CoordinateNativeRuntimeProfileDryRunError(
            "missing_table",
            f"selected table {selected_table_ref} does not provide direction_key {resolved_direction_key}",
            trace,
        )
    trace.append(
        trace_item(
            "resolve_coordinate",
            "use exact raw coordinate from selected table",
            "direction key is resolved deterministically",
            [f"direction_key={resolved_direction_key}", f"coordinate={selected_coordinate[0]},{selected_coordinate[1]}"],
        )
    )

    side_effects = profile.get("digital_side_effects")
    if not isinstance(side_effects, list):
        raise CoordinateNativeRuntimeProfileDryRunError(
            "invalid_input",
            "profile.digital_side_effects must be a list",
            trace,
        )
    side_effect_lookup = build_lookup(side_effects, "effect_id")
    selected_side_effect_ids = merge_side_effect_ids(selected_table, side_effect_lookup)
    trace.append(
        trace_item(
            "merge_digital_side_effects",
            "merge by side-effect priority",
            "offline evaluation only; side effects are not executed",
            [f"selected_side_effect_ids={','.join(selected_side_effect_ids)}"],
        )
    )

    explanation = {
        "selection_summary": f"{selected_rule_id} selected deterministically from {selected_table_ref}",
        "priority_summary": "No tie or fallback was needed",
        "boundary_summary": BOUNDARY_NOTE,
    }
    return build_success_result(
        case_id=case_id,
        profile_path=profile_path,
        case_path=case_path,
        resolved_direction_key=resolved_direction_key,
        selected_rule=selected_rule,
        selected_table=selected_table,
        selected_coordinate=selected_coordinate,
        selected_side_effect_ids=selected_side_effect_ids,
        trace=trace,
        explanation=explanation,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Offline dry-run evaluator for coordinate-native runtime profile fixtures. "
            "Offline tooling only; the generated result is not loaded by firmware, "
            "runtime-loaded config remains not implemented, and no WebSerial/device "
            "write, persistence/storage, flashing automation, or active RuntimeConfigView "
            "publication is performed."
        )
    )
    parser.add_argument(
        "--profile",
        required=True,
        type=Path,
        help="Path to the coordinate-native runtime profile JSON fixture.",
    )
    parser.add_argument(
        "--case",
        required=True,
        type=Path,
        help="Path to the fixture-backed dry-run input case JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    profile_path = args.profile if args.profile.is_absolute() else (REPO_ROOT / args.profile)
    case_path = args.case if args.case.is_absolute() else (REPO_ROOT / args.case)
    case_id = "<unknown>"
    if case_path.exists():
        try:
            case_id = load_json_object(case_path).get("case_id", "<unknown>")
        except (OSError, json.JSONDecodeError, CoordinateNativeRuntimeProfileContractError, ValueError):
            case_id = "<unknown>"

    print("dry_run_coordinate_native_runtime_profile")
    try:
        result = evaluate_case(profile_path, case_path)
    except CoordinateNativeRuntimeProfileDryRunError as exc:
        result = build_failure_result(
            case_id=case_id,
            profile_path=profile_path,
            case_path=case_path,
            selection_status=exc.selection_status,
            resolved_direction_key=None,
            message=exc.message,
            trace=exc.trace,
        )
    except (OSError, json.JSONDecodeError, CoordinateNativeRuntimeProfileContractError, ValueError) as exc:
        result = build_failure_result(
            case_id=case_id,
            profile_path=profile_path,
            case_path=case_path,
            selection_status="invalid_input",
            resolved_direction_key=None,
            message=str(exc),
            trace=[],
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["selection_result"]["selection_status"] == "selected" else 1


if __name__ == "__main__":
    raise SystemExit(main())
