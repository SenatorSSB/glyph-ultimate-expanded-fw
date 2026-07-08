#!/usr/bin/env python3
"""Validate the coordinate-native runtime profile contract packet."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-coordinate-native-profile-contract"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

CONTRACT_DOC = REPO_ROOT / "docs/runtime_config/coordinate_native_runtime_profile_contract.md"
SCHEMA = REPO_ROOT / "docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json"
MINIMAL_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json"
NINE_WAY_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json"
Y2_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json"
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
    "docs/runtime_config/README.md",
    "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
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
)

REQUIRED_CURRENT_STATE_PHRASES = (
    "docs/AGENT_CONTEXT.md",
    "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
    "source-owned Y2 layout HARDWARE_PASS",
    "Active RuntimeConfigView selection remains unchanged",
    "coordinate-native runtime profile contract scaffolding",
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
    "Nunchuk remains NOT_TESTED",
    "root cause remains unproven",
)

REQUIRED_ROADMAP_PHRASES = (
    "Phase 2 - Coordinate-Native Runtime Profile Contract Scaffolding",
    "coordinate-native runtime profile contract scaffolding",
    "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
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
    "design-only",
    "inactive",
)

REQUIRED_BOUNDARY_PHRASES = (
    "coordinate-native runtime profile support",
    "coordinate-native runtime profile contract scaffold",
    "design-only and inactive",
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
    if branch not in {EXPECTED_BRANCH, MERGED_BRANCH, RECOVERY_BRANCH}:
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
    if branch == EXPECTED_BRANCH:
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


def validate_profile_fixture(
    fixture: dict[str, Any],
    *,
    label: str,
    expect_variant: str,
    min_inputs: int,
    min_roles: int,
    min_tables: int,
    allow_legacy_evidence: bool = False,
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
    if fixture.get("profile_variant") != expect_variant:
        fail(f"{label} profile_variant must be {expect_variant!r}")
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
    for table in tables:
        if not isinstance(table, dict):
            fail(f"{label} modifier_tables entries must be objects")
        for field in ("table_id", "table_name", "sublayer"):
            if not isinstance(table.get(field), str) or not table.get(field):
                fail(f"{label} modifier_tables entries must contain {field}")
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
    for rule in routing_rules:
        if not isinstance(rule, dict):
            fail(f"{label} routing_rules entries must be objects")
        for field in ("rule_id", "sublayer", "modifier_table_ref"):
            if not isinstance(rule.get(field), str) or not rule.get(field):
                fail(f"{label} routing_rules entries must contain {field}")
        if not isinstance(rule.get("priority"), int) or rule["priority"] < 0:
            fail(f"{label} routing_rules priority must be a non-negative integer")
        priorities.append(rule["priority"])
    if priorities != sorted(priorities):
        fail(f"{label} routing_rules priorities must be sorted")
    side_effects = fixture.get("digital_side_effects")
    if not isinstance(side_effects, list) or not side_effects:
        fail(f"{label} digital_side_effects must be a non-empty list")
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
    if fixture.get("notes") and "runtime semantics" in normalize(str(fixture.get("notes"))):
        fail(f"{label} notes must not claim runtime semantics")
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


def validate_contract_schema() -> None:
    validate_schema(load_json_object(SCHEMA))


def validate_contract_fixture_and_docs() -> None:
    require_phrases(rel(CONTRACT_DOC), read_required(CONTRACT_DOC), REQUIRED_DOC_PHRASES)
    require_phrases(rel(SCHEMA), read_required(SCHEMA), REQUIRED_SCHEMA_PHRASES)
    require_phrases(rel(CURRENT_STATE), read_required(CURRENT_STATE), REQUIRED_CURRENT_STATE_PHRASES)
    require_phrases(rel(ROADMAP), read_required(ROADMAP), REQUIRED_ROADMAP_PHRASES)
    require_phrases(rel(README), read_required(README), REQUIRED_README_PHRASES)
    require_phrases(rel(BOUNDARY), read_required(BOUNDARY), REQUIRED_BOUNDARY_PHRASES)


def main() -> int:
    branch = validate_branch()
    validate_contract_schema()
    validate_contract_fixture()
    validate_example_fixtures()
    if branch != MERGED_BRANCH:
        validate_changed_paths(changed_paths(branch))
    validate_contract_fixture_and_docs()
    print("glyph_coordinate_native_runtime_profile_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- contract: {rel(CONTRACT_DOC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
