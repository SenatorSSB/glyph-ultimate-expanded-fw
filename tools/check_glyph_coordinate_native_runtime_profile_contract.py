#!/usr/bin/env python3
"""Validate the coordinate-native runtime profile contract packet.

Offline tooling only. The checker exercises fixture-backed dry-run evaluation
but the generated result is not loaded by firmware, runtime-loaded config
remains not implemented, and there is no WebSerial/device write, no
persistence/storage, no flashing automation, and no active RuntimeConfigView
publication.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-coordinate-native-selection-semantics"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
ALLOWED_BRANCH_PREFIXES = ("codex/runtime-config-coordinate-native-",)

CONTRACT_DOC = REPO_ROOT / "docs/runtime_config/coordinate_native_runtime_profile_contract.md"
SCHEMA = REPO_ROOT / "docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json"
MINIMAL_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json"
NINE_WAY_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json"
Y2_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json"
MERGE_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_merge.example.json"
DRY_RUN_NEUTRAL_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_neutral_5.json"
DRY_RUN_CARDINAL_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_cardinal_2.json"
DRY_RUN_DIAGONAL_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_diagonal_7.json"
DRY_RUN_MERGE_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_merge_5.json"
DRY_RUN_NEGATIVE_FIXTURES: tuple[Path, ...] = (
    REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_missing_table.json",
    REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_ambiguous_priority.json",
    REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_invalid_direction_key.json",
    REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_unresolved_role_state.json",
)
DRY_RUN_TOOL = REPO_ROOT / "tools/dry_run_coordinate_native_runtime_profile.py"
NEGATIVE_FIXTURE_REASON_PAIRS: tuple[tuple[Path, str], ...] = (
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_missing_neutral_5.json",
        "neutral_direction_key must be 5",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_direction_key_outside_range.json",
        "direction_key must be 1..9",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_raw_coordinate_outside_byte_range.json",
        "coordinates must stay in the byte range",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_malformed_9way_table.json",
        "must contain exactly 9 points",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_duplicate_priority.json",
        "routing_rules priorities must be strictly increasing",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_missing_capability_metadata.json",
        "missing required field capability_metadata",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_runtime_loaded_claim.json",
        "runtime_loaded_config_implemented must be False",
    ),
    (
        REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_missing_modifier_table_ref.json",
        "references unknown modifier_table_ref",
    ),
)
README = REPO_ROOT / "docs/runtime_config/README.md"
BOUNDARY = REPO_ROOT / "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_coordinate_native_runtime_profile_contract.py"

ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
    "docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_merge.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_neutral_5.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_cardinal_2.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_diagonal_7.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_merge_5.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_missing_table.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_ambiguous_priority.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_invalid_direction_key.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_negative_unresolved_role_state.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_invalid_missing_modifier_table_ref.json",
    "docs/runtime_config/README.md",
    "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
    "tools/dry_run_coordinate_native_runtime_profile.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_docs_agent_surface.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_agent_framework_docs.py",
}
ALLOWED_PREFIXES = ("docs/",)

FORBIDDEN_SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)")
FORBIDDEN_SPECIAL_PATH_RE = re.compile(
    r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

CONTRACT_REQUIRED_FIELDS = (
    "schema_version",
    "packet",
    "branch",
    "profile_variant",
    "contract_status",
    "design_only_contract",
    "active_behavior_changed",
    "hardware_test_required_before_merge",
    "runtime_loaded_config_implemented",
    "persistent_storage_implemented",
    "webserial_device_write_implemented",
    "backend_config_pb_write_path_implemented",
    "flashing_automation_implemented",
    "nunchuk_status",
    "root_cause_proven",
    "version_metadata",
    "capability_metadata",
    "physical_input_ids",
    "roles",
    "direction_resolver",
    "exact_raw_coordinates",
    "modifier_tables",
    "routing_rules",
    "digital_side_effects",
)

CONTRACT_BOOLEAN_FIELDS = {
    "design_only_contract": True,
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "root_cause_proven": False,
}

CONTRACT_STRING_FIELDS = {
    "packet": "coordinate_native_runtime_profile_contract",
    "contract_status": "inactive_design_only",
    "nunchuk_status": "NOT_TESTED",
}

SELECTION_SEMANTICS_REQUIRED_FIELDS = (
    "input_state_shape",
    "activation_representation",
    "direction_key_source",
    "routing_order",
    "tie_behavior",
    "sublayer_selection",
    "missing_table_behavior",
    "digital_side_effect_merge_behavior",
    "output_shape",
    "future_dry_run_examples",
)

CONTRACT_MIN_COUNTS = {
    "contract_manifest": {"inputs": 3, "roles": 3, "tables": 1},
    "minimal_profile": {"inputs": 1, "roles": 1, "tables": 1},
    "9way_modifier_table_profile": {"inputs": 2, "roles": 2, "tables": 2},
    "y2_inspired_sketch": {"inputs": 3, "roles": 3, "tables": 2},
}

REQUIRED_DOC_PHRASES = (
    "Status label: INACTIVE DESIGN / DOCS-CHECKER ONLY.",
    "physical input IDs",
    "direction resolver",
    "direction keys `1..9`",
    "neutral key `5`",
    "exact raw coordinates",
    "9-way modifier tables",
    "sublayer and routing rules",
    "priorities",
    "digital side effects",
    "version and capability metadata",
    "Deterministic Selection Semantics",
    "future dry-run contract",
    "selection_result",
    "future_dry_run_examples",
    "does not implement runtime interpretation",
    "runtime-loaded config",
    "WebSerial/device write path",
    "backend/config.pb write path",
    "firmware flashing automation",
    "Nunchuk remains `NOT_TESTED`",
    "root cause remains unproven",
)

REQUIRED_SCHEMA_PHRASES = (
    "\"title\": \"Glyph Coordinate-Native Runtime Profile Contract\"",
    "\"packet\": { \"const\": \"coordinate_native_runtime_profile_contract\" }",
    "\"contract_status\": { \"const\": \"inactive_design_only\" }",
    "\"neutral_direction_key\": { \"const\": 5 }",
    "\"x\": { \"type\": \"integer\", \"minimum\": 0, \"maximum\": 255 }",
    "\"y\": { \"type\": \"integer\", \"minimum\": 0, \"maximum\": 255 }",
    "\"selection_semantics\"",
    "\"future_dry_run_examples\"",
)

REQUIRED_CURRENT_STATE_PHRASES = (
    "docs/AGENT_CONTEXT.md",
    "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
    "source-owned Y2 layout HARDWARE_PASS",
    "Active RuntimeConfigView selection remains unchanged",
    "coordinate-native runtime profile contract scaffolding",
    "deterministic selection semantics",
    "offline dry-run evaluator",
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
    "Nunchuk remains NOT_TESTED",
    "root cause remains unproven",
)

REQUIRED_ROADMAP_PHRASES = (
    "Phase 2 - Coordinate-Native Runtime Profile Contract Scaffolding",
    "coordinate-native runtime profile contract scaffolding",
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
    "deterministic selection semantics",
    "future_dry_run_examples",
    "offline dry-run evaluator",
    "future browser/protobuf/persistence backend",
    "after the runtime model exists",
)

REQUIRED_README_PHRASES = (
    "Coordinate-Native Runtime Profile Contract",
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
    "docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json",
    "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json",
    "future_dry_run_examples",
    "selection_result",
    "design-only",
    "inactive",
    "offline dry-run evaluator",
    "python3 tools/dry_run_coordinate_native_runtime_profile.py --profile",
    "offline tooling only",
    "generated result is not loaded by firmware",
    "runtime-loaded config remains not implemented",
    "no WebSerial/device write",
    "no persistence/storage",
    "no flashing automation",
    "no active RuntimeConfigView publication",
)

REQUIRED_BOUNDARY_PHRASES = (
    "coordinate-native runtime profile support",
    "coordinate-native runtime profile contract scaffold",
    "design-only and inactive",
    "deterministic selection semantics",
    "future dry-run annotations",
    "browser/protobuf/persistence work may be future infrastructure",
)


class CoordinateNativeRuntimeProfileContractError(AssertionError):
    """Raised when the contract scaffold drifts."""


def fail(message: str) -> None:
    raise CoordinateNativeRuntimeProfileContractError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            fail(f"duplicate JSON key: {key}")
        values[key] = value
    return values


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def git_lines(args: list[str], *, preserve_status: bool = False) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    if preserve_status:
        return [line for line in completed.stdout.splitlines() if line.strip()]
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def current_branch() -> str:
    branch = git_lines(["branch", "--show-current"])
    if not branch:
        fail("checker could not determine current branch")
    return branch[0]


def validate_branch() -> str:
    branch = current_branch()
    if branch not in {EXPECTED_BRANCH, MERGED_BRANCH, RECOVERY_BRANCH} and not any(
        branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES
    ):
        fail(f"checker must run on {EXPECTED_BRANCH} or {MERGED_BRANCH}, got {branch}")
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")
    return branch


def status_path(status_line: str) -> str:
    path = status_line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def changed_paths(branch: str) -> set[str]:
    paths: set[str] = set()
    if branch == EXPECTED_BRANCH or any(branch.startswith(prefix) for prefix in ALLOWED_BRANCH_PREFIXES):
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if FORBIDDEN_SOURCE_PATH_RE.search(path):
            fail(f"firmware/source path changed on docs/checker-only branch: {path}")
        if FORBIDDEN_SPECIAL_PATH_RE.search(path):
            fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("`", "").split())


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized_text = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized_text]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_schema(schema: dict[str, Any]) -> None:
    if schema.get("title") != "Glyph Coordinate-Native Runtime Profile Contract":
        fail("schema title must be Glyph Coordinate-Native Runtime Profile Contract")
    if schema.get("type") != "object":
        fail("schema type must be object")
    required = schema.get("required")
    if not isinstance(required, list):
        fail("schema required must be a list")
    for key in CONTRACT_REQUIRED_FIELDS:
        if key not in required:
            fail(f"schema required missing {key}")
    if "selection_semantics" not in required:
        fail("schema required missing selection_semantics")
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        fail("schema properties must be an object")
    if properties.get("packet", {}).get("const") != "coordinate_native_runtime_profile_contract":
        fail("schema packet const must be coordinate_native_runtime_profile_contract")
    if properties.get("contract_status", {}).get("const") != "inactive_design_only":
        fail("schema contract_status const must be inactive_design_only")
    direction_resolver = properties.get("direction_resolver")
    if not isinstance(direction_resolver, dict):
        fail("schema direction_resolver must be an object")
    resolver_props = direction_resolver.get("properties")
    if not isinstance(resolver_props, dict):
        fail("schema direction_resolver.properties must be an object")
    direction_keys = resolver_props.get("direction_keys")
    if not isinstance(direction_keys, dict):
        fail("schema direction_keys must be an object")
    items = direction_keys.get("items")
    if not isinstance(items, dict):
        fail("schema direction_keys.items must be an object")
    if items.get("minimum") != 1 or items.get("maximum") != 9:
        fail("schema direction key range must be 1..9")
    if resolver_props.get("neutral_direction_key", {}).get("const") != 5:
        fail("schema neutral_direction_key const must be 5")
    exact_raw_coordinates = properties.get("exact_raw_coordinates")
    if not isinstance(exact_raw_coordinates, dict):
        fail("schema exact_raw_coordinates must be an object")
    exact_items = exact_raw_coordinates.get("items")
    if not isinstance(exact_items, dict):
        fail("schema exact_raw_coordinates.items must be an object")
    exact_props = exact_items.get("properties")
    if not isinstance(exact_props, dict):
        fail("schema exact_raw_coordinates.items.properties must be an object")
    if exact_props.get("x", {}).get("minimum") != 0 or exact_props.get("x", {}).get("maximum") != 255:
        fail("schema exact_raw_coordinates x range must be 0..255")
    if exact_props.get("y", {}).get("minimum") != 0 or exact_props.get("y", {}).get("maximum") != 255:
        fail("schema exact_raw_coordinates y range must be 0..255")
    selection_semantics = properties.get("selection_semantics")
    if not isinstance(selection_semantics, dict):
        fail("schema selection_semantics must be an object")
    if selection_semantics.get("type") != "object":
        fail("schema selection_semantics type must be object")
    semantics_props = selection_semantics.get("properties")
    if not isinstance(semantics_props, dict):
        fail("schema selection_semantics.properties must be an object")
    for key in (
        "input_state_shape",
        "activation_representation",
        "direction_key_source",
        "routing_order",
        "tie_behavior",
        "sublayer_selection",
        "missing_table_behavior",
        "digital_side_effect_merge_behavior",
        "output_shape",
        "future_dry_run_examples",
    ):
        if key not in semantics_props:
            fail(f"schema selection_semantics missing {key}")


def validate_points(points: list[dict[str, Any]], label: str) -> None:
    if len(points) != 9:
        fail(f"{label} must contain exactly 9 points")
    seen: set[int] = set()
    for point in points:
        if not isinstance(point, dict):
            fail(f"{label} points must be objects")
        direction_key = point.get("direction_key")
        x = point.get("x")
        y = point.get("y")
        if not isinstance(direction_key, int) or not 1 <= direction_key <= 9:
            fail(f"{label} direction_key must be 1..9")
        if direction_key in seen:
            fail(f"{label} contains duplicate direction_key {direction_key}")
        seen.add(direction_key)
        if not isinstance(x, int) or not isinstance(y, int):
            fail(f"{label} coordinates must be integers")
        if not (0 <= x <= 255 and 0 <= y <= 255):
            fail(f"{label} coordinates must stay in the byte range")
    if seen != set(range(1, 10)):
        fail(f"{label} must cover direction keys 1..9")


def validate_profile_variant_rules(profile_variant: Any) -> tuple[int, int, int, bool]:
    if not isinstance(profile_variant, str):
        fail("profile_variant must be a string")
    variant_rules = {
        "contract_manifest": (3, 3, 1, True),
        "minimal_profile": (1, 1, 1, False),
        "9way_modifier_table_profile": (2, 2, 2, False),
        "y2_inspired_sketch": (3, 3, 2, False),
    }
    try:
        return variant_rules[profile_variant]
    except KeyError as exc:
        fail(f"unknown profile_variant: {profile_variant}")
        raise AssertionError("unreachable") from exc


def validate_selection_semantics(semantics: Any, *, label: str) -> None:
    if not isinstance(semantics, dict):
        fail(f"{label} selection_semantics must be an object")
    for key in SELECTION_SEMANTICS_REQUIRED_FIELDS:
        if key not in semantics:
            fail(f"{label} selection_semantics missing required field {key}")

    input_state_shape = semantics.get("input_state_shape")
    if not isinstance(input_state_shape, dict):
        fail(f"{label} selection_semantics.input_state_shape must be an object")
    for field in (
        "state_object_name",
        "activation_array_field",
        "required_activation_fields",
        "direction_key_field",
        "direction_key_domain",
        "neutral_direction_key",
    ):
        if field not in input_state_shape:
            fail(f"{label} selection_semantics.input_state_shape missing {field}")
    if input_state_shape.get("state_object_name") != "input_state":
        fail(f"{label} selection_semantics.input_state_shape.state_object_name must be 'input_state'")
    if input_state_shape.get("activation_array_field") != "activations":
        fail(f"{label} selection_semantics.input_state_shape.activation_array_field must be 'activations'")
    if input_state_shape.get("direction_key_field") != "resolved_direction_key":
        fail(
            f"{label} selection_semantics.input_state_shape.direction_key_field must be 'resolved_direction_key'"
        )
    if input_state_shape.get("neutral_direction_key") != 5:
        fail(f"{label} selection_semantics.input_state_shape.neutral_direction_key must be 5")
    required_activation_fields = input_state_shape.get("required_activation_fields")
    if not isinstance(required_activation_fields, list) or not required_activation_fields:
        fail(f"{label} selection_semantics.input_state_shape.required_activation_fields must be a non-empty list")
    for field in ("input_id", "role_id", "pressed"):
        if field not in required_activation_fields:
            fail(
                f"{label} selection_semantics.input_state_shape.required_activation_fields missing {field}"
            )
    direction_key_domain = input_state_shape.get("direction_key_domain")
    if direction_key_domain != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        fail(f"{label} selection_semantics.input_state_shape.direction_key_domain must be 1..9")

    activation_representation = semantics.get("activation_representation")
    if not isinstance(activation_representation, dict):
        fail(f"{label} selection_semantics.activation_representation must be an object")
    if activation_representation.get("active_record_field") != "activations":
        fail(f"{label} selection_semantics.activation_representation.active_record_field must be 'activations'")
    if activation_representation.get("inactive_record_field") != "inactive_inputs":
        fail(
            f"{label} selection_semantics.activation_representation.inactive_record_field must be 'inactive_inputs'"
        )
    if activation_representation.get("activation_mode") != "explicit per-input activation records":
        fail(
            f"{label} selection_semantics.activation_representation.activation_mode must be 'explicit per-input activation records'"
        )

    direction_key_source = semantics.get("direction_key_source")
    if not isinstance(direction_key_source, dict):
        fail(f"{label} selection_semantics.direction_key_source must be an object")
    if direction_key_source.get("resolver_field") != "direction_resolver":
        fail(f"{label} selection_semantics.direction_key_source.resolver_field must be 'direction_resolver'")
    if direction_key_source.get("output_field") != "resolved_direction_key":
        fail(f"{label} selection_semantics.direction_key_source.output_field must be 'resolved_direction_key'")
    if direction_key_source.get("neutral_direction_key") != 5:
        fail(f"{label} selection_semantics.direction_key_source.neutral_direction_key must be 5")
    if direction_key_source.get("direction_key_domain") != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        fail(f"{label} selection_semantics.direction_key_source.direction_key_domain must be 1..9")

    routing_order = semantics.get("routing_order")
    if routing_order != [
        "normalize input_state into activation records",
        "read resolved_direction_key from the direction resolver output",
        "rank routing rules by priority, then by sublayer name, then by stable table or rule identifier",
        "select the first rule whose referenced modifier table exists",
        "resolve the exact raw coordinate for the selected table and direction key",
        "merge digital side effects deterministically",
        "emit trace and explanation metadata with the result",
    ]:
        fail(f"{label} selection_semantics.routing_order must match the documented deterministic order")

    tie_behavior = semantics.get("tie_behavior")
    if not isinstance(tie_behavior, dict):
        fail(f"{label} selection_semantics.tie_behavior must be an object")
    for field in ("routing_rule_tie_breakers", "table_tie_breakers", "side_effect_tie_breakers"):
        values = tie_behavior.get(field)
        if not isinstance(values, list) or len(values) < 3:
            fail(f"{label} selection_semantics.tie_behavior.{field} must be a list with at least 3 entries")
    if tie_behavior.get("ambiguous_result_policy") != "reject_profile":
        fail(
            f"{label} selection_semantics.tie_behavior.ambiguous_result_policy must be 'reject_profile'"
        )

    sublayer_selection = semantics.get("sublayer_selection")
    if not isinstance(sublayer_selection, dict):
        fail(f"{label} selection_semantics.sublayer_selection must be an object")
    if sublayer_selection.get("selection_field") != "sublayer":
        fail(f"{label} selection_semantics.sublayer_selection.selection_field must be 'sublayer'")
    if not isinstance(sublayer_selection.get("selection_rule"), str) or not sublayer_selection.get("selection_rule"):
        fail(f"{label} selection_semantics.sublayer_selection.selection_rule must be a non-empty string")
    if sublayer_selection.get("missing_sublayer_behavior") != "reject_profile":
        fail(f"{label} selection_semantics.sublayer_selection.missing_sublayer_behavior must be 'reject_profile'")

    missing_table_behavior = semantics.get("missing_table_behavior")
    if not isinstance(missing_table_behavior, dict):
        fail(f"{label} selection_semantics.missing_table_behavior must be an object")
    for field, expected in {
        "missing_modifier_table_ref": "reject_profile",
        "missing_direction_point": "emit_missing_table_result",
        "unmapped_direction_key": "emit_missing_table_result",
    }.items():
        if missing_table_behavior.get(field) != expected:
            fail(f"{label} selection_semantics.missing_table_behavior.{field} must be {expected!r}")
    if missing_table_behavior.get("output_coordinate") not in (None, {}):
        fail(f"{label} selection_semantics.missing_table_behavior.output_coordinate must be null or an object")

    merge_behavior = semantics.get("digital_side_effect_merge_behavior")
    if not isinstance(merge_behavior, dict):
        fail(f"{label} selection_semantics.digital_side_effect_merge_behavior must be an object")
    if merge_behavior.get("merge_order") != "routing_rule_order then side-effect priority":
        fail(
            f"{label} selection_semantics.digital_side_effect_merge_behavior.merge_order must be 'routing_rule_order then side-effect priority'"
        )
    if merge_behavior.get("dedupe_key") != "effect_id":
        fail(f"{label} selection_semantics.digital_side_effect_merge_behavior.dedupe_key must be 'effect_id'")
    if merge_behavior.get("conflict_resolution") != "deduplicate identical effect_id and fail on conflicting duplicates":
        fail(
            f"{label} selection_semantics.digital_side_effect_merge_behavior.conflict_resolution must be 'deduplicate identical effect_id and fail on conflicting duplicates'"
        )
    if merge_behavior.get("suppression_trace") is not True:
        fail(f"{label} selection_semantics.digital_side_effect_merge_behavior.suppression_trace must be True")

    output_shape = semantics.get("output_shape")
    if not isinstance(output_shape, dict):
        fail(f"{label} selection_semantics.output_shape must be an object")
    if output_shape.get("result_field") != "selection_result":
        fail(f"{label} selection_semantics.output_shape.result_field must be 'selection_result'")
    required_result_fields = output_shape.get("required_result_fields")
    if not isinstance(required_result_fields, list) or not required_result_fields:
        fail(f"{label} selection_semantics.output_shape.required_result_fields must be a non-empty list")
    for field in (
        "selection_status",
        "resolved_direction_key",
        "selected_rule_id",
        "selected_table_id",
        "selected_coordinate",
        "selected_side_effect_ids",
        "trace",
        "explanation",
    ):
        if field not in required_result_fields:
            fail(f"{label} selection_semantics.output_shape.required_result_fields missing {field}")
    status_values = output_shape.get("selection_status_values")
    if not isinstance(status_values, list) or len(status_values) < 4:
        fail(f"{label} selection_semantics.output_shape.selection_status_values must contain at least 4 values")
    for value in ("selected", "missing_table", "ambiguous_tie", "invalid_input"):
        if value not in status_values:
            fail(f"{label} selection_semantics.output_shape.selection_status_values missing {value}")
    trace_item_fields = output_shape.get("trace_item_fields")
    if not isinstance(trace_item_fields, list) or len(trace_item_fields) < 4:
        fail(f"{label} selection_semantics.output_shape.trace_item_fields must contain at least 4 values")
    for field in ("step", "decision", "reason", "inputs"):
        if field not in trace_item_fields:
            fail(f"{label} selection_semantics.output_shape.trace_item_fields missing {field}")
    if output_shape.get("explanation_field") != "explanation":
        fail(f"{label} selection_semantics.output_shape.explanation_field must be 'explanation'")

    examples = semantics.get("future_dry_run_examples")
    if not isinstance(examples, list) or not examples:
        fail(f"{label} selection_semantics.future_dry_run_examples must be a non-empty list")
    for example in examples:
        if not isinstance(example, dict):
            fail(f"{label} selection_semantics.future_dry_run_examples entries must be objects")
        for field in ("case_id", "input_state", "expected_result", "trace_markers"):
            if field not in example:
                fail(f"{label} selection_semantics.future_dry_run_examples entries missing {field}")
        if not isinstance(example.get("case_id"), str) or not example.get("case_id"):
            fail(f"{label} selection_semantics.future_dry_run_examples.case_id must be a non-empty string")
        input_state = example.get("input_state")
        if not isinstance(input_state, dict):
            fail(f"{label} selection_semantics.future_dry_run_examples.input_state must be an object")
        for field in ("state_id", "activations", "inactive_inputs", "resolved_direction_key"):
            if field not in input_state:
                fail(f"{label} selection_semantics.future_dry_run_examples.input_state missing {field}")
        if not isinstance(input_state.get("state_id"), str) or not input_state.get("state_id"):
            fail(f"{label} selection_semantics.future_dry_run_examples.input_state.state_id must be a non-empty string")
        activations = input_state.get("activations")
        if not isinstance(activations, list) or not activations:
            fail(f"{label} selection_semantics.future_dry_run_examples.input_state.activations must be a non-empty list")
        for activation in activations:
            if not isinstance(activation, dict):
                fail(
                    f"{label} selection_semantics.future_dry_run_examples.input_state.activations entries must be objects"
                )
            for field in ("input_id", "role_id", "pressed"):
                if field not in activation:
                    fail(
                        f"{label} selection_semantics.future_dry_run_examples.input_state.activations entries missing {field}"
                    )
        if not isinstance(input_state.get("inactive_inputs"), list):
            fail(f"{label} selection_semantics.future_dry_run_examples.input_state.inactive_inputs must be a list")
        if not isinstance(input_state.get("resolved_direction_key"), int) or not 1 <= input_state.get("resolved_direction_key") <= 9:
            fail(
                f"{label} selection_semantics.future_dry_run_examples.input_state.resolved_direction_key must be 1..9"
            )
        expected_result = example.get("expected_result")
        if not isinstance(expected_result, dict):
            fail(f"{label} selection_semantics.future_dry_run_examples.expected_result must be an object")
        for field in (
            "selection_status",
            "resolved_direction_key",
            "selected_rule_id",
            "selected_table_id",
            "selected_coordinate",
            "selected_side_effect_ids",
            "trace",
            "explanation",
        ):
            if field not in expected_result:
                fail(
                    f"{label} selection_semantics.future_dry_run_examples.expected_result missing {field}"
                )
        if expected_result.get("selection_status") not in {"selected", "missing_table", "ambiguous_tie", "invalid_input"}:
            fail(
                f"{label} selection_semantics.future_dry_run_examples.expected_result.selection_status must be a supported status"
            )
        selected_coordinate = expected_result.get("selected_coordinate")
        if selected_coordinate is not None:
            if not isinstance(selected_coordinate, dict):
                fail(
                    f"{label} selection_semantics.future_dry_run_examples.expected_result.selected_coordinate must be null or an object"
                )
            for field in ("x", "y"):
                if field not in selected_coordinate:
                    fail(
                        f"{label} selection_semantics.future_dry_run_examples.expected_result.selected_coordinate missing {field}"
                    )
                if not isinstance(selected_coordinate.get(field), int):
                    fail(
                        f"{label} selection_semantics.future_dry_run_examples.expected_result.selected_coordinate.{field} must be an integer"
                    )
        if not isinstance(expected_result.get("selected_side_effect_ids"), list):
            fail(
                f"{label} selection_semantics.future_dry_run_examples.expected_result.selected_side_effect_ids must be a list"
            )
        for side_effect_id in expected_result.get("selected_side_effect_ids", []):
            if not isinstance(side_effect_id, str) or not side_effect_id:
                fail(
                    f"{label} selection_semantics.future_dry_run_examples.expected_result.selected_side_effect_ids entries must be non-empty strings"
                )
        trace = expected_result.get("trace")
        if not isinstance(trace, list) or not trace:
            fail(f"{label} selection_semantics.future_dry_run_examples.expected_result.trace must be a non-empty list")
        for item in trace:
            if not isinstance(item, dict):
                fail(
                    f"{label} selection_semantics.future_dry_run_examples.expected_result.trace entries must be objects"
                )
            for field in ("step", "decision", "reason", "inputs"):
                if field not in item:
                    fail(
                        f"{label} selection_semantics.future_dry_run_examples.expected_result.trace entries missing {field}"
                    )
        if not isinstance(example.get("trace_markers"), list) or not example.get("trace_markers"):
            fail(f"{label} selection_semantics.future_dry_run_examples.trace_markers must be a non-empty list")


def validate_profile_fixture(
    fixture: dict[str, Any],
    *,
    label: str,
    expect_variant: str | None = None,
    min_inputs: int | None = None,
    min_roles: int | None = None,
    min_tables: int | None = None,
    allow_legacy_evidence: bool = False,
    require_selection_semantics: bool = True,
) -> None:
    for key, expected in CONTRACT_STRING_FIELDS.items():
        if fixture.get(key) != expected:
            fail(f"{label} {key} must be {expected!r}")
    for key, expected in CONTRACT_BOOLEAN_FIELDS.items():
        if fixture.get(key) != expected:
            fail(f"{label} {key} must be {expected!r}")
    for key in CONTRACT_REQUIRED_FIELDS:
        if key not in fixture:
            fail(f"{label} missing required field {key}")
    if fixture.get("schema_version") != 1:
        fail(f"{label} schema_version must be 1")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"{label} branch must be {EXPECTED_BRANCH}")
    profile_variant = fixture.get("profile_variant")
    if expect_variant is not None and profile_variant != expect_variant:
        fail(f"{label} profile_variant must be {expect_variant!r}")
    variant_min_inputs, variant_min_roles, variant_min_tables, variant_allow_legacy = validate_profile_variant_rules(profile_variant)
    if min_inputs is None:
        min_inputs = variant_min_inputs
    if min_roles is None:
        min_roles = variant_min_roles
    if min_tables is None:
        min_tables = variant_min_tables
    allow_legacy_evidence = allow_legacy_evidence or variant_allow_legacy
    version_metadata = fixture.get("version_metadata")
    if not isinstance(version_metadata, dict):
        fail(f"{label} version_metadata must be an object")
    if version_metadata.get("schema_version") != 1 or version_metadata.get("contract_revision") != 1:
        fail(f"{label} version_metadata must stay on schema_version 1 and contract_revision 1")
    capability_metadata = fixture.get("capability_metadata")
    if not isinstance(capability_metadata, dict):
        fail(f"{label} capability_metadata must be an object")
    for key in (
        "physical_input_ids",
        "roles",
        "direction_resolver",
        "direction_keys_1_to_9",
        "neutral_5",
        "exact_raw_coordinates",
        "nine_way_modifier_tables",
        "sublayers",
        "priorities",
        "digital_side_effects",
    ):
        if capability_metadata.get(key) is not True:
            fail(f"{label} capability_metadata.{key} must be true")
    physical_inputs = fixture.get("physical_input_ids")
    if not isinstance(physical_inputs, list) or len(physical_inputs) < min_inputs:
        fail(f"{label} physical_input_ids must contain at least {min_inputs} entries")
    roles = fixture.get("roles")
    if not isinstance(roles, list) or len(roles) < min_roles:
        fail(f"{label} roles must contain at least {min_roles} entries")
    role_ids: set[str] = set()
    for role in roles:
        if not isinstance(role, dict):
            fail(f"{label} roles entries must be objects")
        role_id = role.get("role_id")
        if not isinstance(role_id, str) or not role_id:
            fail(f"{label} roles entries must contain role_id")
        if role_id in role_ids:
            fail(f"{label} roles must have unique role_id values")
        role_ids.add(role_id)
    for physical_input in physical_inputs:
        if not isinstance(physical_input, dict):
            fail(f"{label} physical_input_ids entries must be objects")
        if physical_input.get("role") not in role_ids:
            fail(f"{label} physical_input_ids.role must reference a defined role")
    resolver = fixture.get("direction_resolver")
    if not isinstance(resolver, dict):
        fail(f"{label} direction_resolver must be an object")
    if resolver.get("direction_keys") != [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        fail(f"{label} direction_resolver.direction_keys must be 1..9")
    if resolver.get("neutral_direction_key") != 5:
        fail(f"{label} direction_resolver.neutral_direction_key must be 5")
    if resolver.get("resolved_direction_key_range") != [1, 9]:
        fail(f"{label} direction_resolver.resolved_direction_key_range must be [1, 9]")
    exact_raw = fixture.get("exact_raw_coordinates")
    if not isinstance(exact_raw, list):
        fail(f"{label} exact_raw_coordinates must be a list")
    validate_points(exact_raw, f"{label} exact_raw_coordinates")
    tables = fixture.get("modifier_tables")
    if not isinstance(tables, list) or len(tables) < min_tables:
        fail(f"{label} modifier_tables must contain at least {min_tables} entries")
    table_ids: set[str] = set()
    for table in tables:
        if not isinstance(table, dict):
            fail(f"{label} modifier_tables entries must be objects")
        for field in ("table_id", "table_name", "sublayer"):
            if not isinstance(table.get(field), str) or not table.get(field):
                fail(f"{label} modifier_tables entries must contain {field}")
        table_id = table["table_id"]
        if table_id in table_ids:
            fail(f"{label} modifier_tables must have unique table_id values")
        table_ids.add(table_id)
        if not isinstance(table.get("priority"), int) or table["priority"] < 0:
            fail(f"{label} modifier_tables priority must be a non-negative integer")
        direction_points = table.get("direction_points")
        if not isinstance(direction_points, list):
            fail(f"{label} direction_points must be a list")
        validate_points(direction_points, f"{label} modifier table {table['table_name']}")
        refs = table.get("digital_side_effect_refs")
        if not isinstance(refs, list) or not refs:
            fail(f"{label} digital_side_effect_refs must be a non-empty list")
    routing_rules = fixture.get("routing_rules")
    if not isinstance(routing_rules, list) or not routing_rules:
        fail(f"{label} routing_rules must be a non-empty list")
    priorities: list[int] = []
    rule_ids: set[str] = set()
    sublayers: set[str] = set()
    for rule in routing_rules:
        if not isinstance(rule, dict):
            fail(f"{label} routing_rules entries must be objects")
        for field in ("rule_id", "sublayer", "modifier_table_ref"):
            if not isinstance(rule.get(field), str) or not rule.get(field):
                fail(f"{label} routing_rules entries must contain {field}")
        if rule["rule_id"] in rule_ids:
            fail(f"{label} routing_rules must have unique rule_id values")
        rule_ids.add(rule["rule_id"])
        if rule["sublayer"] in sublayers:
            fail(f"{label} routing_rules must have unique sublayer values")
        sublayers.add(rule["sublayer"])
        if not isinstance(rule.get("priority"), int) or rule["priority"] < 0:
            fail(f"{label} routing_rules priority must be a non-negative integer")
        priorities.append(rule["priority"])
    if priorities != sorted(priorities) or len(set(priorities)) != len(priorities):
        fail(f"{label} routing_rules priorities must be strictly increasing")
    existing_table_ids = {
        table.get("table_id")
        for table in tables
        if isinstance(table, dict) and isinstance(table.get("table_id"), str)
    }
    side_effects = fixture.get("digital_side_effects")
    if not isinstance(side_effects, list) or not side_effects:
        fail(f"{label} digital_side_effects must be a non-empty list")
    effect_ids: set[str] = set()
    effect_priorities: list[int] = []
    for effect in side_effects:
        if not isinstance(effect, dict):
            fail(f"{label} digital_side_effects entries must be objects")
        for field in ("effect_id", "trigger", "side_effect"):
            if not isinstance(effect.get(field), str) or not effect.get(field):
                fail(f"{label} digital_side_effects entries must contain {field}")
        if not isinstance(effect.get("priority"), int) or effect["priority"] < 0:
            fail(f"{label} digital_side_effects priority must be a non-negative integer")
        if effect.get("design_only") is not True:
            fail(f"{label} digital_side_effects entries must be design-only")
        effect_ids.add(effect["effect_id"])
        effect_priorities.append(effect["priority"])
    if effect_priorities != sorted(effect_priorities) or len(set(effect_priorities)) != len(effect_priorities):
        fail(f"{label} digital_side_effects priorities must be strictly increasing")
    for table in tables:
        refs = table.get("digital_side_effect_refs")
        if not isinstance(refs, list):
            fail(f"{label} digital_side_effect_refs must be a list")
        for ref in refs:
            if ref not in effect_ids:
                fail(f"{label} digital_side_effect_refs references unknown effect_id {ref}")
    for rule in routing_rules:
        ref = rule["modifier_table_ref"]
        if ref not in existing_table_ids:
            fail(f"{label} routing_rules references unknown modifier_table_ref {ref}")
    if fixture.get("notes") and "runtime semantics" in normalize(str(fixture.get("notes"))):
        fail(f"{label} notes must not claim runtime semantics")
    if require_selection_semantics:
        validate_selection_semantics(fixture.get("selection_semantics"), label=label)
    if allow_legacy_evidence:
        evidence = fixture.get("accepted_evidence")
        if not isinstance(evidence, dict):
            fail(f"{label} accepted_evidence must be an object")
        for key, expected in {
            "source_owned_y2_layout": "HARDWARE_PASS",
            "active_runtime_config_view_selection_unchanged": True,
            "source_owned_current_baseline_published": True,
            "candidate_view_active_publication": "HARDWARE_FAIL",
            "source_owned_materialized_candidate_view_active_publication": "HARDWARE_FAIL",
            "dedicated_ram_backed_active_storage_publication": "HARDWARE_FAIL",
            "generated_source_owned_baseline_runtime_config_view_active_publication": "HARDWARE_FAIL",
        }.items():
            if evidence.get(key) != expected:
                fail(f"{label} accepted_evidence.{key} must be {expected!r}")
        runtime_primitive = fixture.get("required_runtime_primitive")
        if runtime_primitive != "active_role_modifier_state_plus_resolved_direction_key_1_to_9_to_exact_raw_coordinate":
            fail(f"{label} required_runtime_primitive is incorrect")
        v0_path = fixture.get("v0_production_path")
        if not isinstance(v0_path, list) or len(v0_path) != 3:
            fail(f"{label} v0_production_path must be a 3-item list")


def validate_profile_file(path: Path) -> None:
    path = path.resolve()
    fixture = load_json_object(path)
    validate_profile_fixture(fixture, label=rel(path), require_selection_semantics=True)


def run_negative_fixture_checks() -> None:
    for path, expected_reason in NEGATIVE_FIXTURE_REASON_PAIRS:
        try:
            validate_profile_fixture(load_json_object(path), label=rel(path), require_selection_semantics=False)
        except CoordinateNativeRuntimeProfileContractError as exc:
            message = str(exc)
            if expected_reason not in message:
                fail(
                    f"{rel(path)} failed with unexpected reason: {message!r} "
                    f"(expected substring {expected_reason!r})"
                )
        else:
            fail(f"{rel(path)} unexpectedly validated successfully")


def validate_docs() -> None:
    require_phrases(rel(CONTRACT_DOC), read_required(CONTRACT_DOC), REQUIRED_DOC_PHRASES)
    require_phrases(rel(SCHEMA), read_required(SCHEMA), REQUIRED_SCHEMA_PHRASES)
    require_phrases(rel(CURRENT_STATE), read_required(CURRENT_STATE), REQUIRED_CURRENT_STATE_PHRASES)
    require_phrases(rel(ROADMAP), read_required(ROADMAP), REQUIRED_ROADMAP_PHRASES)
    require_phrases(rel(README), read_required(README), REQUIRED_README_PHRASES)
    require_phrases(rel(BOUNDARY), read_required(BOUNDARY), REQUIRED_BOUNDARY_PHRASES)


def validate_contract_fixture() -> None:
    validate_profile_fixture(
        load_json_object(FIXTURE),
        label="contract fixture",
        expect_variant="contract_manifest",
        min_inputs=3,
        min_roles=3,
        min_tables=1,
        allow_legacy_evidence=True,
    )


def validate_example_fixtures() -> None:
    validate_profile_fixture(
        load_json_object(MINIMAL_FIXTURE),
        label="minimal example",
        expect_variant="minimal_profile",
        min_inputs=1,
        min_roles=1,
        min_tables=1,
    )
    validate_profile_fixture(
        load_json_object(NINE_WAY_FIXTURE),
        label="9-way example",
        expect_variant="9way_modifier_table_profile",
        min_inputs=2,
        min_roles=2,
        min_tables=2,
    )
    validate_profile_fixture(
        load_json_object(Y2_FIXTURE),
        label="y2-inspired example",
        expect_variant="y2_inspired_sketch",
        min_inputs=3,
        min_roles=3,
        min_tables=2,
    )
    validate_profile_fixture(
        load_json_object(MERGE_FIXTURE),
        label="merge example",
        expect_variant="minimal_profile",
        min_inputs=1,
        min_roles=1,
        min_tables=1,
    )


def load_case_fixture(path: Path) -> dict[str, Any]:
    payload = load_json_object(path)
    return payload


def parse_tool_json(output: str) -> dict[str, Any]:
    start = output.find("{")
    if start == -1:
        fail("dry-run tool output did not include JSON")
    try:
        payload = json.loads(output[start:])
    except json.JSONDecodeError as exc:
        fail(f"dry-run tool output was not valid JSON: {exc}")
    if not isinstance(payload, dict):
        fail("dry-run tool output must be a JSON object")
    return payload


def run_dry_run_tool(profile_path: Path, case_path: Path) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        [
            sys.executable,
            str(DRY_RUN_TOOL.relative_to(REPO_ROOT)),
            "--profile",
            str(profile_path.relative_to(REPO_ROOT)),
            "--case",
            str(case_path.relative_to(REPO_ROOT)),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode, parse_tool_json(output)


def validate_dry_run_case_fixture(path: Path, *, expect_failure: bool) -> None:
    case = load_case_fixture(path)
    profile_path = REPO_ROOT / case.get("profile_path", "")
    if not profile_path.exists():
        fail(f"{rel(path)} references missing profile_path {case.get('profile_path')}")
    exit_code, payload = run_dry_run_tool(profile_path, path)
    if payload.get("offline_only") is not True:
        fail(f"{rel(path)} tool output must stay offline_only")
    if payload.get("case_id") != case.get("case_id"):
        fail(f"{rel(path)} tool output case_id drifted")
    selection_result = payload.get("selection_result")
    if not isinstance(selection_result, dict):
        fail(f"{rel(path)} tool output missing selection_result object")
    expected_key = "expected_failure" if expect_failure else "expected_result"
    expected = case.get(expected_key)
    if not isinstance(expected, dict):
        fail(f"{rel(path)} missing {expected_key}")
    if selection_result != expected:
        fail(f"{rel(path)} dry-run selection_result drifted from {expected_key}")
    if expect_failure and exit_code == 0:
        fail(f"{rel(path)} dry-run tool unexpectedly succeeded")
    if not expect_failure and exit_code != 0:
        fail(f"{rel(path)} dry-run tool unexpectedly failed")


def validate_dry_run_fixtures() -> None:
    validate_dry_run_case_fixture(DRY_RUN_NEUTRAL_FIXTURE, expect_failure=False)
    validate_dry_run_case_fixture(DRY_RUN_CARDINAL_FIXTURE, expect_failure=False)
    validate_dry_run_case_fixture(DRY_RUN_DIAGONAL_FIXTURE, expect_failure=False)
    validate_dry_run_case_fixture(DRY_RUN_MERGE_FIXTURE, expect_failure=False)
    for path in DRY_RUN_NEGATIVE_FIXTURES:
        validate_dry_run_case_fixture(path, expect_failure=True)


def validate_contract_schema() -> None:
    validate_schema(load_json_object(SCHEMA))


def validate_contract_fixture_and_docs() -> None:
    require_phrases(rel(CONTRACT_DOC), read_required(CONTRACT_DOC), REQUIRED_DOC_PHRASES)
    require_phrases(rel(SCHEMA), read_required(SCHEMA), REQUIRED_SCHEMA_PHRASES)
    require_phrases(rel(CURRENT_STATE), read_required(CURRENT_STATE), REQUIRED_CURRENT_STATE_PHRASES)
    require_phrases(rel(ROADMAP), read_required(ROADMAP), REQUIRED_ROADMAP_PHRASES)
    require_phrases(rel(README), read_required(README), REQUIRED_README_PHRASES)
    require_phrases(rel(BOUNDARY), read_required(BOUNDARY), REQUIRED_BOUNDARY_PHRASES)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--validate-profile",
        type=Path,
        help="Validate one coordinate-native runtime profile JSON file",
    )
    group.add_argument(
        "--check-negative-fixtures",
        action="store_true",
        help="Validate the invalid fixture corpus and assert each expected failure reason",
    )
    group.add_argument(
        "--check-dry-run-fixtures",
        action="store_true",
        help=(
            "Run the offline dry-run evaluator against the positive and negative fixture corpus; "
            "offline tooling only and the generated result is not loaded by firmware"
        ),
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if args.validate_profile is not None:
        validate_profile_file(args.validate_profile)
        print("glyph_coordinate_native_runtime_profile_contract: PROFILE PASS")
        print(f"- fixture: {rel(args.validate_profile.resolve())}")
        return 0
    if args.check_negative_fixtures:
        run_negative_fixture_checks()
        print("glyph_coordinate_native_runtime_profile_contract: NEGATIVE FIXTURES PASS")
        for path, _ in NEGATIVE_FIXTURE_REASON_PAIRS:
            print(f"- {rel(path)}")
        return 0
    if args.check_dry_run_fixtures:
        validate_dry_run_fixtures()
        print("glyph_coordinate_native_runtime_profile_contract: DRY-RUN FIXTURES PASS")
        for path in (
            DRY_RUN_NEUTRAL_FIXTURE,
            DRY_RUN_CARDINAL_FIXTURE,
            DRY_RUN_DIAGONAL_FIXTURE,
            DRY_RUN_MERGE_FIXTURE,
            *DRY_RUN_NEGATIVE_FIXTURES,
        ):
            print(f"- {rel(path)}")
        return 0
    branch = validate_branch()
    validate_contract_schema()
    validate_contract_fixture()
    validate_example_fixtures()
    validate_dry_run_fixtures()
    if branch != MERGED_BRANCH:
        validate_changed_paths(changed_paths(branch))
    validate_contract_fixture_and_docs()
    print("glyph_coordinate_native_runtime_profile_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- contract: {rel(CONTRACT_DOC)}")
    print(f"- dry-run tool: {rel(DRY_RUN_TOOL)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
