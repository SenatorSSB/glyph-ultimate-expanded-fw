#!/usr/bin/env python3
"""Validate the generated source-owned runtime generator contract."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-generated-source-owned-generator-contract"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
DOWNSTREAM_ARTIFACT_INSTALL_BRANCH = "runtime-config-generated-source-owned-artifact-install"
DOWNSTREAM_BASELINE_ARTIFACT_BRANCH = "runtime-config-generated-source-owned-baseline-artifact"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

CONTRACT_DOC = REPO_ROOT / "docs/runtime_config/generated_source_owned_generator_contract.md"
LAYOUT_SPEC_DOC = REPO_ROOT / "docs/runtime_config/generated_source_owned_layout_spec.md"
CONTRACT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_generator_contract.json"
LAYOUT_SPEC_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
LAYOUT_SPEC_EXAMPLE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.example.json"
INPUT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json"
OUTPUT_FIXTURE = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp"
)
GENERATOR = REPO_ROOT / "tools/generate_source_owned_runtime_config.py"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
SPEC_INPUT_MODE = "--emit-from-layout-spec"

ALLOWED_TOOL_PATHS = {
    "tools/generate_source_owned_runtime_config.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/dry_run_coordinate_native_runtime_profile.py",
    "tools/check_glyph_docs_navigation.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_latest_y2_layout_source_owned_port.py",
    "tools/check_glyph_diagnostic_active_storage_published.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
    "tools/check_glyph_generated_source_owned_artifact_install.py",
    "tools/check_glyph_generated_source_owned_baseline_artifact.py",
    "tools/check_glyph_source_owned_table_symbol_map.py",
    "tools/check_glyph_docs_agent_surface.py",
    "tools/convert_coordinate_native_profile_to_source_owned_spec.py",
    "tools/check_glyph_runtime_config_activation_alternatives.py",
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "tools/extract_glyph_identity_runtime_tables.py",
}
ALLOWED_INERT_SOURCE_PREFIX = "src/modes/runtime_config/generated_source_owned/"
ALLOWED_INERT_SOURCE_RE = re.compile(
    r"^src/modes/runtime_config/generated_source_owned/[A-Za-z0-9_.-]+\.(?:h|hpp|hh|cc|cpp)$"
)

FORBIDDEN_CHANGED_PREFIXES = (
    "src/modes/",
    "HAL/",
    "backend/",
)
FORBIDDEN_CHANGED_PARTS = (
    "config.pb",
    "storage",
    "write",
    "WebSerial",
    "webserial",
    "flash",
    "flashing",
)

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "generator_contract_only": True,
    "layout_spec_contract_inert": True,
    "generated_tables_wired_active": False,
    "generated_artifacts_written_to_active_source_path_by_default": False,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

EXPECTED_INPUT_VALUES: dict[str, Any] = {
    "schema_version": 1,
    "artifact_kind": "generated_source_owned_runtime_config_table",
    "controller_family": "glyph_mk6",
    "profile_name": "example_source_owned_runtime_config",
    "revision": 1,
}

EXPECTED_LAYOUT_SPEC_VALUES: dict[str, Any] = {
    "schema_version": 1,
    "layout_spec_kind": "generated_source_owned_layout_spec",
    "layout_name": "current_source_owned_baseline_layout",
    "controller_family": "glyph_mk6",
    "profile_name": "example_source_owned_runtime_config",
    "revision": 1,
}

EXPECTED_SHAPE = {
    "table_count": 28,
    "points_per_table": 9,
    "axes_per_point": 2,
}

REQUIRED_DOC_PHRASES = (
    "GENERATOR CONTRACT / DOCS-TOOLS ONLY",
    "generated_source_owned_realization_design.md",
    "generated_source_owned_schema_scaffold.md",
    "generated_source_owned_layout_spec.md",
    "declarative layout spec",
    "layout_spec",
    "--emit-from-layout-spec",
    "duplicate keys rejected",
    "`table_count: 28`",
    "`points_per_table: 9`",
    "`axes_per_point: 2`",
    "integer byte values `x` and `y`",
    "generated source-owned runtime config artifact",
    "`static constexpr`",
    "not under active firmware include paths",
    "does not write generated artifacts into active source paths by default",
    "does not wire generated tables active",
    "does not change active firmware behavior",
    "RAM-backed active runtime table publication remains forbidden",
    "low-level failure mechanism remains unproven",
    "Nunchuk remains `NOT_TESTED`",
)

REQUIRED_INDEX_PHRASES = (
    "generated_source_owned_generator_contract.md",
    "fixtures/generated_source_owned_generator_contract.json",
    "generated_source_owned_generator_input.example.json",
    "generated_source_owned_layout_spec.md",
    "fixtures/generated_source_owned_layout_spec.json",
    "fixtures/generated_source_owned_layout_spec.example.json",
    "generated_outputs/generated_source_owned_runtime_config.example.hpp",
    "tools/generate_source_owned_runtime_config.py",
    "--emit-from-layout-spec",
    "generated tables not wired active",
    "nunchuk `NOT_TESTED`",
)

FORBIDDEN_OUTPUT_TOKENS = (
    "GetActiveRuntimeConfigState",
    "ResolveActiveRuntimeConfig",
    "UpdateAnalogOutputs",
    "active_view =",
    "candidate.view",
    "RuntimeConfigStorage",
    "WebSerial",
    "config.pb",
    "flash",
    "flashing",
)
REQUIRED_INERT_SOURCE_MARKERS = (
    "generated source-owned runtime config artifact",
    "inert generated-table placeholder",
    "not wired into runtime selection",
)
GENERATED_OUTPUT_TABLE_START_RE = re.compile(r"^\s*\{\s*//\s*(?P<label>.+?)\s*$")
GENERATED_OUTPUT_POINT_RE = re.compile(r"^\s*\{\s*(\d+)u,\s*(\d+)u\},\s*$")


class GeneratedSourceOwnedGeneratorContractError(AssertionError):
    """Raised when the generated source-owned generator contract drifts."""


def fail(message: str) -> None:
    raise GeneratedSourceOwnedGeneratorContractError(message)


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
    if branch != MERGED_BRANCH:
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path and path.endswith("/"):
            directory = REPO_ROOT / path
            if directory.is_dir():
                paths.update(rel(file_path) for file_path in directory.rglob("*") if file_path.is_file())
        elif path:
            paths.add(path)
    return paths


def validate_inert_source_artifact(path: str) -> None:
    if not ALLOWED_INERT_SOURCE_RE.match(path):
        fail(f"inert generated artifact path is outside allowed area: {path}")
    text = read_required(REPO_ROOT / path)
    for marker in REQUIRED_INERT_SOURCE_MARKERS:
        if marker not in text:
            fail(f"inert generated artifact missing marker {marker!r}: {path}")
    validate_output_fixture(text)


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path in ALLOWED_TOOL_PATHS:
            continue
        if path.startswith(ALLOWED_INERT_SOURCE_PREFIX):
            validate_inert_source_artifact(path)
            continue
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES):
            fail(f"forbidden active runtime/HAL/backend path changed: {path}")
        if any(part in path for part in FORBIDDEN_CHANGED_PARTS):
            fail(f"forbidden config/storage/write/WebSerial/flashing path changed: {path}")
        if path.startswith("docs/runtime_config/") or path.startswith("docs/agent_framework/"):
            continue
        if path in {"docs/CURRENT_STATE.md", "docs/ROADMAP.md"}:
            continue
        if path.startswith("docs/"):
            fail(f"out-of-scope docs path changed: {path}")
        if path.startswith("tools/"):
            fail(f"out-of-scope tool path changed: {path}")
        fail(f"out-of-scope changed path: {path}")


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized_text = " ".join(text.lower().split())
    missing = [
        phrase
        for phrase in phrases
        if " ".join(phrase.lower().split()) not in normalized_text
    ]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def require_exact_keys(label: str, value: dict[str, Any], required: set[str]) -> None:
    missing = sorted(required - set(value))
    if missing:
        fail(f"{label} missing required keys: {', '.join(missing)}")
    extra = sorted(set(value) - required)
    if extra:
        fail(f"{label} has unexpected keys: {', '.join(extra)}")


def validate_contract_fixture(fixture: dict[str, Any]) -> None:
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"contract fixture {key} must be {expected!r}, got {actual!r}")
    generator = fixture.get("generator")
    if not isinstance(generator, dict):
        fail("contract fixture generator must be an object")
    if generator.get("stdlib_only") is not True:
        fail("contract fixture generator.stdlib_only must be true")
    if generator.get("active_source_output_by_default") is not False:
        fail("contract fixture generator.active_source_output_by_default must be false")
    if generator.get("spec_input_mode") != SPEC_INPUT_MODE:
        fail(f"contract fixture generator.spec_input_mode must be {SPEC_INPUT_MODE!r}")
    if generator.get("spec_input_requires_layout_spec") is not True:
        fail("contract fixture generator.spec_input_requires_layout_spec must be true")
    input_contract = fixture.get("input_contract")
    if not isinstance(input_contract, dict):
        fail("contract fixture input_contract must be an object")
    required_top_level_keys = input_contract.get("required_top_level_keys")
    if not isinstance(required_top_level_keys, list):
        fail("contract fixture input_contract.required_top_level_keys must be a list")
    for required_key in (
        "schema_version",
        "artifact_kind",
        "controller_family",
        "profile_name",
        "revision",
        "layout_spec",
        "table_shape",
        "tables",
    ):
        if required_key not in required_top_level_keys:
            fail(f"contract fixture input_contract.required_top_level_keys missing {required_key}")
    output_contract = fixture.get("output_contract")
    if not isinstance(output_contract, dict):
        fail("contract fixture output_contract must be an object")
    if output_contract.get("required_marker") != "generated source-owned runtime config artifact":
        fail("contract fixture output_contract.required_marker is wrong")


def validate_layout_spec_packet(packet: dict[str, Any]) -> None:
    if packet.get("schema_version") != 1:
        fail("layout spec packet schema_version must be 1")
    if packet.get("packet") != "generated_source_owned_layout_spec":
        fail("layout spec packet name is wrong")
    for key, expected in {
        "active_behavior_changed": False,
        "hardware_test_required_before_merge": False,
        "generator_contract_only": True,
        "layout_spec_contract_inert": True,
        "generated_tables_wired_active": False,
        "generated_artifacts_written_to_active_source_path_by_default": False,
        "runtime_loaded_config_implemented": False,
        "persistent_storage_implemented": False,
        "webserial_device_write_implemented": False,
        "backend_config_pb_write_path_implemented": False,
        "flashing_automation_implemented": False,
        "nunchuk_status": "NOT_TESTED",
        "root_cause_proven": False,
    }.items():
        actual = packet.get(key)
        if actual != expected:
            fail(f"layout spec packet {key} must be {expected!r}, got {actual!r}")
    spec = packet.get("layout_spec")
    if not isinstance(spec, dict):
        fail("layout spec packet layout_spec must be an object")
    require_exact_keys(
        "layout spec packet layout_spec",
        spec,
        set(EXPECTED_LAYOUT_SPEC_VALUES) | {"table_shape", "tables"},
    )
    for key, expected in EXPECTED_LAYOUT_SPEC_VALUES.items():
        actual = spec.get(key)
        if actual != expected:
            fail(f"layout spec packet layout_spec {key} must be {expected!r}, got {actual!r}")
    shape = spec.get("table_shape")
    if shape != EXPECTED_SHAPE:
        fail(f"layout spec packet layout_spec.table_shape must be {EXPECTED_SHAPE!r}, got {shape!r}")
    tables = spec.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_SHAPE["table_count"]:
        fail("layout spec packet layout_spec.tables must contain exactly 28 entries")
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"layout spec packet layout_spec.tables[{table_index}] must be an object")
        require_exact_keys(
            f"layout spec packet layout_spec.tables[{table_index}]",
            table,
            {"table_id", "table_name", "table_symbol"},
        )
        table_id = table.get("table_id")
        if not isinstance(table_id, int) or isinstance(table_id, bool):
            fail(f"layout spec packet layout_spec.tables[{table_index}].table_id must be an integer")
        if table_id != table_index:
            fail(f"layout spec packet layout_spec.tables[{table_index}].table_id must be {table_index}")
        table_name = table.get("table_name")
        if not isinstance(table_name, str) or not table_name:
            fail(f"layout spec packet layout_spec.tables[{table_index}].table_name must be a string")
        table_symbol = table.get("table_symbol")
        if not isinstance(table_symbol, str) or not table_symbol:
            fail(f"layout spec packet layout_spec.tables[{table_index}].table_symbol must be a string")
        expected_symbol = f"k{table_name}Table"
        if table_symbol != expected_symbol:
            fail(
                f"layout spec packet layout_spec.tables[{table_index}].table_symbol must be {expected_symbol!r}"
            )
    if {table["table_id"] for table in tables} != set(range(EXPECTED_SHAPE["table_count"])):
        fail("layout spec packet table_id values must cover 0..27")


def validate_input_fixture(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_INPUT_VALUES.items():
        actual = payload.get(key)
        if actual != expected:
            fail(f"input fixture {key} must be {expected!r}, got {actual!r}")
    layout_spec = payload.get("layout_spec")
    if not isinstance(layout_spec, dict):
        fail("input fixture layout_spec must be an object")
    require_exact_keys(
        "input fixture layout_spec",
        layout_spec,
        set(EXPECTED_LAYOUT_SPEC_VALUES) | {"table_shape", "tables"},
    )
    for key, expected in EXPECTED_LAYOUT_SPEC_VALUES.items():
        actual = layout_spec.get(key)
        if actual != expected:
            fail(f"input fixture layout_spec {key} must be {expected!r}, got {actual!r}")
    shape = layout_spec.get("table_shape")
    if shape != EXPECTED_SHAPE:
        fail(f"input fixture layout_spec table_shape must be {EXPECTED_SHAPE!r}, got {shape!r}")
    tables = layout_spec.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_SHAPE["table_count"]:
        fail("input fixture layout_spec.tables must contain exactly 28 entries")
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"input fixture layout_spec.tables[{table_index}] must be an object")
        require_exact_keys(
            f"input fixture layout_spec.tables[{table_index}]",
            table,
            {"table_id", "table_name", "table_symbol"},
        )
        table_id = table.get("table_id")
        if not isinstance(table_id, int) or isinstance(table_id, bool):
            fail(f"input fixture layout_spec.tables[{table_index}].table_id must be an integer")
        if table_id != table_index:
            fail(f"input fixture layout_spec.tables[{table_index}].table_id must be {table_index}")
        for key in ("table_name", "table_symbol"):
            value = table.get(key)
            if not isinstance(value, str) or not value:
                fail(f"input fixture layout_spec.tables[{table_index}].{key} must be a string")
        if table["table_symbol"] != f"k{table['table_name']}Table":
            fail(
                "input fixture layout_spec tables must use matching source-owned table_symbol names"
            )
    shape = payload.get("table_shape")
    if shape != EXPECTED_SHAPE:
        fail(f"input fixture table_shape must be {EXPECTED_SHAPE!r}, got {shape!r}")
    tables = payload.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_SHAPE["table_count"]:
        fail("input fixture tables must contain exactly 28 tables")
    seen_ids: set[int] = set()
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"input fixture tables[{table_index}] must be an object")
        table_id = table.get("table_id")
        if not isinstance(table_id, int) or isinstance(table_id, bool):
            fail(f"input fixture tables[{table_index}].table_id must be an integer")
        if table_id in seen_ids:
            fail(f"input fixture duplicate table_id: {table_id}")
        seen_ids.add(table_id)
        points = table.get("points")
        if not isinstance(points, list) or len(points) != EXPECTED_SHAPE["points_per_table"]:
            fail(f"input fixture tables[{table_index}].points must contain exactly 9 points")
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                fail(f"input fixture tables[{table_index}].points[{point_index}] must be an object")
            for axis in ("x", "y"):
                value = point.get(axis)
                if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255:
                    fail(
                        f"input fixture tables[{table_index}].points[{point_index}].{axis} "
                        "must be an integer byte"
                    )
    if seen_ids != set(range(EXPECTED_SHAPE["table_count"])):
        fail("input fixture table_id values must cover 0..27")


def validate_layout_spec_example(payload: dict[str, Any]) -> None:
    validate_input_fixture(payload)


def validate_output_fixture(text: str) -> None:
    if "generated source-owned runtime config artifact" not in text:
        fail("generated output fixture missing required marker")
    if "static constexpr" not in text:
        fail("generated output fixture must use static constexpr style")
    for token in FORBIDDEN_OUTPUT_TOKENS:
        if token in text:
            fail(f"generated output fixture contains forbidden token {token!r}")


def canonicalize_output_label(label: str) -> str:
    label = label.strip()
    if " " in label:
        prefix, rest = label.split(" ", 1)
        if prefix.isdigit():
            label = rest.strip()
    if label.startswith("k") and label.endswith("Table") and len(label) > len("kTable"):
        return label[1:-5]
    return label


def parse_generated_output_tables(text: str) -> list[tuple[str, list[tuple[int, int]]]]:
    lines = text.splitlines()
    tables: list[tuple[str, list[tuple[int, int]]]] = []
    index = 0
    while index < len(lines):
        match = GENERATED_OUTPUT_TABLE_START_RE.match(lines[index])
        if match is None:
            index += 1
            continue
        label = canonicalize_output_label(match.group("label"))
        points: list[tuple[int, int]] = []
        for point_offset in range(1, 10):
            if index + point_offset >= len(lines):
                fail(f"generated output table {label} is truncated")
            point_match = GENERATED_OUTPUT_POINT_RE.match(lines[index + point_offset])
            if point_match is None:
                fail(f"generated output table {label} has malformed point data")
            points.append((int(point_match.group(1)), int(point_match.group(2))))
        if index + 10 >= len(lines) or lines[index + 10].strip() != "},":
            fail(f"generated output table {label} is missing its closing brace")
        tables.append((label, points))
        index += 11
    return tables


def run_generator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(GENERATOR), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def generate_current_source_owned_baseline() -> str:
    completed = run_generator("--emit-current-source-owned-baseline")
    if completed.returncode != 0:
        fail("generator failed on current source-owned baseline: " + completed.stderr.strip())
    return completed.stdout


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def expect_generator_failure(input_text: str, directory: Path, label: str) -> None:
    input_path = directory / f"{label}.json"
    output_path = directory / f"{label}.hpp"
    input_path.write_text(input_text, encoding="utf-8")
    completed = run_generator(input_path, output_path)
    if completed.returncode == 0:
        fail(f"generator accepted malformed input case: {label}")


def validate_generator_behavior(input_payload: dict[str, Any], layout_spec_payload: dict[str, Any]) -> None:
    fixture_output = read_required(OUTPUT_FIXTURE)
    with tempfile.TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        generated_one = temp_dir / "generated_one.hpp"
        generated_spec_one = temp_dir / "generated_spec_one.hpp"
        generated_spec_two = temp_dir / "generated_spec_two.hpp"
        generated_two = temp_dir / "generated_two.hpp"
        first = run_generator(INPUT_FIXTURE, generated_one)
        if first.returncode != 0:
            fail("generator failed on sample input: " + first.stderr.strip())
        layout_spec_run = run_generator(SPEC_INPUT_MODE, LAYOUT_SPEC_FIXTURE, generated_spec_one)
        if layout_spec_run.returncode != 0:
            fail("generator failed on layout spec example: " + layout_spec_run.stderr.strip())
        layout_spec_second_run = run_generator(SPEC_INPUT_MODE, LAYOUT_SPEC_FIXTURE, generated_spec_two)
        if layout_spec_second_run.returncode != 0:
            fail("generator failed on second layout spec run: " + layout_spec_second_run.stderr.strip())
        second = run_generator(INPUT_FIXTURE, generated_two)
        if second.returncode != 0:
            fail("generator failed on second deterministic run: " + second.stderr.strip())
        first_text = generated_one.read_text(encoding="utf-8")
        second_text = generated_two.read_text(encoding="utf-8")
        layout_spec_text = generated_spec_one.read_text(encoding="utf-8")
        layout_spec_second_text = generated_spec_two.read_text(encoding="utf-8")
        if first_text != second_text:
            fail("generator output is not deterministic across repeated runs")
        if first_text != fixture_output:
            fail("generator output does not match checked-in generated output fixture")
        if layout_spec_text != fixture_output:
            fail("layout spec example does not match checked-in generated output fixture")
        if layout_spec_text != layout_spec_second_text:
            fail("layout spec mode output is not deterministic across repeated runs")
        layout_spec_example_run = run_generator(SPEC_INPUT_MODE, LAYOUT_SPEC_EXAMPLE, temp_dir / "generated_layout_spec_example.hpp")
        if layout_spec_example_run.returncode != 0:
            fail("generator failed on layout spec example fixture: " + layout_spec_example_run.stderr.strip())
        layout_spec_example_text = (temp_dir / "generated_layout_spec_example.hpp").read_text(encoding="utf-8")
        if layout_spec_example_text != fixture_output:
            fail("layout spec example fixture does not match checked-in generated output fixture")

        baseline = generate_current_source_owned_baseline()
        fixture_tables = parse_generated_output_tables(fixture_output)
        baseline_tables = parse_generated_output_tables(baseline)
        if len(fixture_tables) != len(baseline_tables):
            fail("generated output fixture table count does not match current source-owned baseline output")
        fixture_names = [label for label, _ in fixture_tables]
        baseline_names = [label for label, _ in baseline_tables]
        if fixture_names != baseline_names:
            fail("generated output fixture table order does not match current source-owned baseline output")
        for target_name in ("Y2", "Tilt3"):
            fixture_points = dict(fixture_tables)[target_name]
            baseline_points = dict(baseline_tables)[target_name]
            if fixture_points != baseline_points:
                fail(f"generated output fixture {target_name} table does not match current source-owned baseline output")

        def expect_layout_spec_rejection(payload: dict[str, Any], label: str) -> None:
            candidate_path = temp_dir / f"{label}.json"
            candidate_output = temp_dir / f"{label}.hpp"
            write_json(candidate_path, payload)
            if run_generator(candidate_path, candidate_output).returncode == 0:
                fail(f"generator accepted malformed layout spec case: {label}")
            if run_generator(SPEC_INPUT_MODE, candidate_path, candidate_output).returncode == 0:
                fail(f"spec-input mode accepted malformed layout spec case: {label}")

        missing_layout_spec = copy.deepcopy(layout_spec_payload)
        missing_layout_spec.pop("layout_spec")
        write_json(temp_dir / "missing_layout_spec.json", missing_layout_spec)
        if run_generator(str(temp_dir / "missing_layout_spec.json"), str(temp_dir / "missing_layout_spec_generic.hpp")).returncode == 0:
            fail("generator accepted input without layout_spec")
        if run_generator(SPEC_INPUT_MODE, str(temp_dir / "missing_layout_spec.json"), str(temp_dir / "missing_layout_spec.hpp")).returncode == 0:
            fail("spec-input mode accepted input without layout_spec")

        duplicate_key = '{"schema_version": 1, "schema_version": 1}'
        expect_generator_failure(duplicate_key, temp_dir, "duplicate_key")

        missing_required = copy.deepcopy(layout_spec_payload)
        missing_required.pop("tables")
        write_json(temp_dir / "missing_required.json", missing_required)
        if run_generator(temp_dir / "missing_required.json", temp_dir / "missing_required.hpp").returncode == 0:
            fail("generator accepted input missing required tables key")

        missing_layout_spec_tables = copy.deepcopy(layout_spec_payload)
        missing_layout_spec_tables["layout_spec"].pop("tables")
        expect_layout_spec_rejection(missing_layout_spec_tables, "missing_layout_spec_tables")

        wrong_layout_spec_kind = copy.deepcopy(layout_spec_payload)
        wrong_layout_spec_kind["layout_spec"]["layout_spec_kind"] = "wrong"
        expect_layout_spec_rejection(wrong_layout_spec_kind, "wrong_layout_spec_kind")

        wrong_layout_spec_shape = copy.deepcopy(layout_spec_payload)
        wrong_layout_spec_shape["layout_spec"]["table_shape"]["table_count"] = 26
        expect_layout_spec_rejection(wrong_layout_spec_shape, "wrong_layout_spec_shape")

        wrong_layout_spec_axes = copy.deepcopy(layout_spec_payload)
        wrong_layout_spec_axes["layout_spec"]["table_shape"]["axes_per_point"] = 3
        expect_layout_spec_rejection(wrong_layout_spec_axes, "wrong_layout_spec_axes")

        reordered_layout_spec = copy.deepcopy(layout_spec_payload)
        reordered_layout_spec["layout_spec"]["tables"][0], reordered_layout_spec["layout_spec"]["tables"][1] = (
            reordered_layout_spec["layout_spec"]["tables"][1],
            reordered_layout_spec["layout_spec"]["tables"][0],
        )
        expect_layout_spec_rejection(reordered_layout_spec, "reordered_layout_spec")

        truncated_layout_spec = copy.deepcopy(layout_spec_payload)
        truncated_layout_spec["layout_spec"]["tables"] = truncated_layout_spec["layout_spec"]["tables"][:-1]
        expect_layout_spec_rejection(truncated_layout_spec, "truncated_layout_spec")

        wrong_layout_spec_fixture = copy.deepcopy(layout_spec_payload)
        wrong_layout_spec_fixture["layout_spec"]["tables"][0]["table_symbol"] = "kWrongTable"
        expect_layout_spec_rejection(wrong_layout_spec_fixture, "wrong_layout_spec_fixture")

        extra_key_layout_spec = copy.deepcopy(layout_spec_payload)
        extra_key_layout_spec["layout_spec"]["tables"][0]["extra"] = "unexpected"
        expect_layout_spec_rejection(extra_key_layout_spec, "extra_key_layout_spec")

        missing_layout_spec_table_symbol = copy.deepcopy(layout_spec_payload)
        missing_layout_spec_table_symbol["layout_spec"]["tables"][0].pop("table_symbol")
        expect_layout_spec_rejection(missing_layout_spec_table_symbol, "missing_layout_spec_table_symbol")

        wrong_layout_spec_table_id = copy.deepcopy(layout_spec_payload)
        wrong_layout_spec_table_id["layout_spec"]["tables"][0]["table_id"] = 99
        expect_layout_spec_rejection(wrong_layout_spec_table_id, "wrong_layout_spec_table_id")

        out_of_range = copy.deepcopy(input_payload)
        out_of_range["tables"][0]["points"][0]["x"] = 256
        write_json(temp_dir / "out_of_range.json", out_of_range)
        if run_generator(str(temp_dir / "out_of_range.json"), str(temp_dir / "out_of_range.hpp")).returncode == 0:
            fail("generator accepted byte value outside 0..255")

        wrong_count = copy.deepcopy(input_payload)
        wrong_count["table_shape"]["table_count"] = 26
        write_json(temp_dir / "wrong_table_count.json", wrong_count)
        if run_generator(str(temp_dir / "wrong_table_count.json"), str(temp_dir / "wrong_table_count.hpp")).returncode == 0:
            fail("generator accepted wrong table_count")

        wrong_points = copy.deepcopy(input_payload)
        wrong_points["tables"][0]["points"] = wrong_points["tables"][0]["points"][:-1]
        write_json(temp_dir / "wrong_points.json", wrong_points)
        if run_generator(str(temp_dir / "wrong_points.json"), str(temp_dir / "wrong_points.hpp")).returncode == 0:
            fail("generator accepted a table without exactly 9 points")

        wrong_axes = copy.deepcopy(input_payload)
        wrong_axes["table_shape"]["axes_per_point"] = 3
        write_json(temp_dir / "wrong_axes.json", wrong_axes)
        if run_generator(str(temp_dir / "wrong_axes.json"), str(temp_dir / "wrong_axes.hpp")).returncode == 0:
            fail("generator accepted axes_per_point other than 2")

        active_output = temp_dir / "src" / "generated.hpp"
        completed = run_generator(str(INPUT_FIXTURE), str(active_output))
        if completed.returncode == 0:
            fail("generator accepted an active source-like output path")


def validate_docs() -> None:
    contract_doc = read_required(CONTRACT_DOC)
    layout_spec_doc = read_required(LAYOUT_SPEC_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)
    require_phrases(rel(CONTRACT_DOC), contract_doc, REQUIRED_DOC_PHRASES)
    require_phrases(
        rel(LAYOUT_SPEC_DOC),
        layout_spec_doc,
        (
            "INERT LAYOUT SPEC / DOCS-TOOLS ONLY",
            "generated_source_owned_generator_contract.md",
            "declarative layout spec",
            "layout_spec",
            "not wired into runtime selection",
            "does not change active firmware behavior",
            "future hardware gate required before generated source-owned tables are selected active",
            "Nunchuk remains `NOT_TESTED`",
        ),
    )
    for path, text in (
        (README, readme),
        (CURRENT_STATE, current_state),
        (ROADMAP, roadmap),
    ):
        require_phrases(rel(path), text, REQUIRED_INDEX_PHRASES)


def main() -> int:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch))
    contract_fixture = load_json_object(CONTRACT_FIXTURE)
    layout_spec_fixture = load_json_object(LAYOUT_SPEC_FIXTURE)
    layout_spec_example = load_json_object(LAYOUT_SPEC_EXAMPLE)
    input_fixture = load_json_object(INPUT_FIXTURE)
    validate_contract_fixture(contract_fixture)
    validate_layout_spec_packet(layout_spec_fixture)
    validate_layout_spec_example(layout_spec_example)
    validate_input_fixture(input_fixture)
    validate_output_fixture(read_required(OUTPUT_FIXTURE))
    validate_generator_behavior(input_fixture, layout_spec_example)
    validate_docs()
    print("glyph_generated_source_owned_generator_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- contract: {rel(CONTRACT_DOC)}")
    print(f"- layout spec: {rel(LAYOUT_SPEC_DOC)}")
    print(f"- generator: {rel(GENERATOR)}")
    print(f"- sample output: {rel(OUTPUT_FIXTURE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
