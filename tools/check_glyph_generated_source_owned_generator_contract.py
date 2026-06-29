#!/usr/bin/env python3
"""Validate the generated source-owned runtime generator contract."""

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-generated-source-owned-generator-contract"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

CONTRACT_DOC = REPO_ROOT / "docs/runtime_config/generated_source_owned_generator_contract.md"
CONTRACT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_generator_contract.json"
INPUT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json"
OUTPUT_FIXTURE = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp"
)
GENERATOR = REPO_ROOT / "tools/generate_source_owned_runtime_config.py"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"

ALLOWED_TOOL_PATHS = {
    "tools/generate_source_owned_runtime_config.py",
    "tools/check_glyph_generated_source_owned_generator_contract.py",
    "tools/check_glyph_diagnostic_active_storage_published.py",
    "tools/check_glyph_generated_source_owned_realization_design.py",
    "tools/check_glyph_generated_source_owned_schema_scaffold.py",
}

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
    "revision": 1,
}

EXPECTED_SHAPE = {
    "table_count": 27,
    "points_per_table": 9,
    "axes_per_point": 2,
}

REQUIRED_DOC_PHRASES = (
    "GENERATOR CONTRACT / DOCS-TOOLS ONLY",
    "generated_source_owned_realization_design.md",
    "generated_source_owned_schema_scaffold.md",
    "duplicate keys rejected",
    "`table_count: 27`",
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
    "generated_outputs/generated_source_owned_runtime_config.example.hpp",
    "tools/generate_source_owned_runtime_config.py",
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
    if branch not in {EXPECTED_BRANCH, MERGED_BRANCH}:
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
        if path and path.endswith("/"):
            directory = REPO_ROOT / path
            if directory.is_dir():
                paths.update(rel(file_path) for file_path in directory.rglob("*") if file_path.is_file())
        elif path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path in ALLOWED_TOOL_PATHS:
            continue
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES):
            fail(f"forbidden active runtime/HAL/backend path changed: {path}")
        if any(part in path for part in FORBIDDEN_CHANGED_PARTS):
            fail(f"forbidden config/storage/write/WebSerial/flashing path changed: {path}")
        if path.startswith("docs/runtime_config/"):
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
    output_contract = fixture.get("output_contract")
    if not isinstance(output_contract, dict):
        fail("contract fixture output_contract must be an object")
    if output_contract.get("required_marker") != "generated source-owned runtime config artifact":
        fail("contract fixture output_contract.required_marker is wrong")


def validate_input_fixture(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_INPUT_VALUES.items():
        actual = payload.get(key)
        if actual != expected:
            fail(f"input fixture {key} must be {expected!r}, got {actual!r}")
    shape = payload.get("table_shape")
    if shape != EXPECTED_SHAPE:
        fail(f"input fixture table_shape must be {EXPECTED_SHAPE!r}, got {shape!r}")
    tables = payload.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_SHAPE["table_count"]:
        fail("input fixture tables must contain exactly 27 tables")
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
        fail("input fixture table_id values must cover 0..26")


def validate_output_fixture(text: str) -> None:
    if "generated source-owned runtime config artifact" not in text:
        fail("generated output fixture missing required marker")
    if "static constexpr" not in text:
        fail("generated output fixture must use static constexpr style")
    for token in FORBIDDEN_OUTPUT_TOKENS:
        if token in text:
            fail(f"generated output fixture contains forbidden token {token!r}")


def run_generator(input_path: Path, output_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(GENERATOR), str(input_path), str(output_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def expect_generator_failure(input_text: str, directory: Path, label: str) -> None:
    input_path = directory / f"{label}.json"
    output_path = directory / f"{label}.hpp"
    input_path.write_text(input_text, encoding="utf-8")
    completed = run_generator(input_path, output_path)
    if completed.returncode == 0:
        fail(f"generator accepted malformed input case: {label}")


def validate_generator_behavior(input_payload: dict[str, Any]) -> None:
    fixture_output = read_required(OUTPUT_FIXTURE)
    with tempfile.TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        generated_one = temp_dir / "generated_one.hpp"
        generated_two = temp_dir / "generated_two.hpp"
        first = run_generator(INPUT_FIXTURE, generated_one)
        if first.returncode != 0:
            fail("generator failed on sample input: " + first.stderr.strip())
        second = run_generator(INPUT_FIXTURE, generated_two)
        if second.returncode != 0:
            fail("generator failed on second deterministic run: " + second.stderr.strip())
        first_text = generated_one.read_text(encoding="utf-8")
        second_text = generated_two.read_text(encoding="utf-8")
        if first_text != second_text:
            fail("generator output is not deterministic across repeated runs")
        if first_text != fixture_output:
            fail("generator output does not match checked-in generated output fixture")

        duplicate_key = '{"schema_version": 1, "schema_version": 1}'
        expect_generator_failure(duplicate_key, temp_dir, "duplicate_key")

        missing_required = copy.deepcopy(input_payload)
        missing_required.pop("tables")
        write_json(temp_dir / "missing_required.json", missing_required)
        if run_generator(temp_dir / "missing_required.json", temp_dir / "missing_required.hpp").returncode == 0:
            fail("generator accepted input missing required tables key")

        out_of_range = copy.deepcopy(input_payload)
        out_of_range["tables"][0]["points"][0]["x"] = 256
        write_json(temp_dir / "out_of_range.json", out_of_range)
        if run_generator(temp_dir / "out_of_range.json", temp_dir / "out_of_range.hpp").returncode == 0:
            fail("generator accepted byte value outside 0..255")

        wrong_count = copy.deepcopy(input_payload)
        wrong_count["table_shape"]["table_count"] = 26
        write_json(temp_dir / "wrong_table_count.json", wrong_count)
        if run_generator(temp_dir / "wrong_table_count.json", temp_dir / "wrong_table_count.hpp").returncode == 0:
            fail("generator accepted wrong table_count")

        wrong_points = copy.deepcopy(input_payload)
        wrong_points["tables"][0]["points"] = wrong_points["tables"][0]["points"][:-1]
        write_json(temp_dir / "wrong_points.json", wrong_points)
        if run_generator(temp_dir / "wrong_points.json", temp_dir / "wrong_points.hpp").returncode == 0:
            fail("generator accepted a table without exactly 9 points")

        wrong_axes = copy.deepcopy(input_payload)
        wrong_axes["table_shape"]["axes_per_point"] = 3
        write_json(temp_dir / "wrong_axes.json", wrong_axes)
        if run_generator(temp_dir / "wrong_axes.json", temp_dir / "wrong_axes.hpp").returncode == 0:
            fail("generator accepted axes_per_point other than 2")

        active_output = temp_dir / "src" / "generated.hpp"
        completed = run_generator(INPUT_FIXTURE, active_output)
        if completed.returncode == 0:
            fail("generator accepted an active source-like output path")


def validate_docs() -> None:
    contract_doc = read_required(CONTRACT_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)
    require_phrases(rel(CONTRACT_DOC), contract_doc, REQUIRED_DOC_PHRASES)
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
    input_fixture = load_json_object(INPUT_FIXTURE)
    validate_contract_fixture(contract_fixture)
    validate_input_fixture(input_fixture)
    validate_output_fixture(read_required(OUTPUT_FIXTURE))
    validate_generator_behavior(input_fixture)
    validate_docs()
    print("glyph_generated_source_owned_generator_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- contract: {rel(CONTRACT_DOC)}")
    print(f"- generator: {rel(GENERATOR)}")
    print(f"- sample output: {rel(OUTPUT_FIXTURE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
