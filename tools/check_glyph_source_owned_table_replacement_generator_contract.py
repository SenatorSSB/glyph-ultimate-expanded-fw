#!/usr/bin/env python3
"""Validate the source-owned table replacement generator contract."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-source-owned-table-replacement-generator-contract"
IMPLEMENTATION_BRANCH = "runtime-config-latest-tilt3-table-content-replacement"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

CONTRACT_DOC = REPO_ROOT / "docs/runtime_config/source_owned_table_replacement_generator_contract.md"
CONTRACT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_table_replacement_generator_contract.json"
INPUT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_table_replacement_input.example.json"
OUTPUT_FIXTURE = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/generated_outputs/UltimateIdentityRuntimeTables.replacement.example.hpp"
)
SOURCE_TABLES = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
GENERATOR = REPO_ROOT / "tools/generate_source_owned_table_replacement.py"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_source_owned_table_replacement_generator_contract.py"
GENERATOR_REL = "tools/generate_source_owned_table_replacement.py"

EXPECTED_SHAPE = {
    "table_count": 27,
    "points_per_table": 9,
    "axes_per_point": 2,
}

ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    GENERATOR_REL,
    CHECKER_REL,
}
ALLOWED_PREFIXES = ("docs/runtime_config/",)
ALLOWED_EXISTING_CHECKERS = {
    "tools/check_glyph_diagnostic_generated_source_owned_baseline_active.py",
    "tools/check_glyph_source_owned_table_replacement_design.py",
    "tools/check_glyph_latest_layout_y2_port_plan.py",
    "tools/check_glyph_latest_tilt3_table_content_replacement.py",
}
IMPLEMENTATION_ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
    "tools/check_glyph_latest_layout_y2_port_plan.py",
    "tools/check_glyph_latest_tilt3_table_content_replacement.py",
}
IMPLEMENTATION_ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")

FORBIDDEN_SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)")
FORBIDDEN_SPECIAL_PATH_RE = re.compile(
    r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

TABLE_RE = re.compile(
    r"constexpr\s+StickPoint\s+(?P<symbol>k[A-Za-z0-9_]+Table)\s*\[\s*9\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
POINT_RE = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "generator_contract_only": True,
    "active_view_selection_changed": False,
    "runtime_config_view_replacement_allowed": False,
    "source_owned_table_content_replacement_wired": False,
    "active_source_file_modified": False,
    "output_fixture_only": True,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

EXPECTED_EVIDENCE: dict[str, str] = {
    "source_owned_active_state_preselection": "HARDWARE_PASS",
    "parsed_candidate_machinery_present_source_owned_active_view": "HARDWARE_PASS",
    "parsed_candidate_view_active": "HARDWARE_FAIL",
    "source_owned_materialized_candidate_view_active": "HARDWARE_FAIL",
    "dedicated_active_storage_published_active": "HARDWARE_FAIL",
    "generated_source_owned_baseline_active": "HARDWARE_FAIL",
}

REQUIRED_DOC_PHRASES = (
    "source_owned_table_replacement_design.md",
    "generated source-owned baseline active HARDWARE_FAIL",
    "dedicated active storage",
    "HARDWARE_FAIL",
    "source-owned active-state preselection",
    "HARDWARE_PASS",
    "no RuntimeConfigView selection change",
    "runtime_config_view_replacement_allowed: false",
    "active_view_selection_changed: false",
    "source_owned_table_content_replacement_wired: false",
    "active_source_file_modified: false",
    "output_fixture_only: true",
    "runtime-loaded config remains not implemented",
    "Nunchuk remains `NOT_TESTED`",
)

REQUIRED_INDEX_PHRASES = (
    "source_owned_table_replacement_generator_contract.md",
    "fixtures/source_owned_table_replacement_generator_contract.json",
    "fixtures/source_owned_table_replacement_input.example.json",
    "generated_outputs/UltimateIdentityRuntimeTables.replacement.example.hpp",
    "tools/generate_source_owned_table_replacement.py",
    "no RuntimeConfigView selection change",
)

FORBIDDEN_OUTPUT_POSITIVE_CLAIMS = (
    "runtime_loaded_config_implemented: true",
    "persistent_storage_implemented: true",
    "webserial_device_write_implemented: true",
    "backend_config_pb_write_path_implemented: true",
    "flashing_automation_implemented: true",
    "RuntimeConfigStorage",
    "WebSerial",
    "config.pb",
    "flashing automation implemented",
)

FORBIDDEN_ACTIVE_SELECTION_TOKENS = (
    "RuntimeConfigView",
    "GetActiveRuntimeConfigState",
    "ResolveActiveRuntimeConfig",
    "UpdateAnalogOutputs",
    "active_view",
    "candidate.view",
)


class SourceOwnedTableReplacementGeneratorContractError(AssertionError):
    """Raised when the source-owned table replacement generator contract drifts."""


def fail(message: str) -> None:
    raise SourceOwnedTableReplacementGeneratorContractError(message)


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
    if branch not in {EXPECTED_BRANCH, IMPLEMENTATION_BRANCH, MERGED_BRANCH}:
        fail(f"checker must run on {EXPECTED_BRANCH}, {IMPLEMENTATION_BRANCH}, or {MERGED_BRANCH}, got {branch}")
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
    if branch in {EXPECTED_BRANCH, IMPLEMENTATION_BRANCH}:
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


def validate_changed_paths(paths: set[str], branch: str) -> None:
    for path in sorted(paths):
        if branch == IMPLEMENTATION_BRANCH:
            if FORBIDDEN_SPECIAL_PATH_RE.search(path):
                fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
            if path in IMPLEMENTATION_ALLOWED_EXACT_CHANGED_PATHS:
                continue
            if any(path.startswith(prefix) for prefix in IMPLEMENTATION_ALLOWED_PREFIXES):
                continue
            fail(f"out-of-scope changed path for implementation branch: {path}")
        if FORBIDDEN_SOURCE_PATH_RE.search(path):
            fail(f"firmware/source path changed on docs/tools branch: {path}")
        if FORBIDDEN_SPECIAL_PATH_RE.search(path):
            fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if path in ALLOWED_EXISTING_CHECKERS:
            continue
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


def parse_tables(text: str) -> list[tuple[str, tuple[tuple[int, int], ...], tuple[int, int]]]:
    tables: list[tuple[str, tuple[tuple[int, int], ...], tuple[int, int]]] = []
    seen: set[str] = set()
    for match in TABLE_RE.finditer(text):
        symbol = match.group("symbol")
        if symbol in seen:
            fail(f"duplicate table symbol: {symbol}")
        seen.add(symbol)
        points = tuple((int(x), int(y)) for x, y in POINT_RE.findall(match.group("body")))
        if len(points) != EXPECTED_SHAPE["points_per_table"]:
            fail(f"{symbol} must contain exactly 9 points")
        for x, y in points:
            if not (0 <= x <= 255 and 0 <= y <= 255):
                fail(f"{symbol} contains out-of-byte-range point ({x}, {y})")
        tables.append((symbol, points, (match.start("body"), match.end("body"))))
    if len(tables) != EXPECTED_SHAPE["table_count"]:
        fail(f"expected exactly 27 StickPoint tables, found {len(tables)}")
    return tables


def strip_table_bodies(text: str) -> str:
    parts: list[str] = []
    cursor = 0
    for _symbol, _points, (body_start, body_end) in parse_tables(text):
        parts.append(text[cursor:body_start])
        parts.append("<StickPoint table body>")
        cursor = body_end
    parts.append(text[cursor:])
    return "".join(parts)


def validate_contract_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("packet") != "source_owned_table_replacement_generator_contract":
        fail("fixture packet must be source_owned_table_replacement_generator_contract")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"fixture branch must be {EXPECTED_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"contract fixture {key} must be {expected!r}, got {actual!r}")
    evidence = fixture.get("evidence")
    if not isinstance(evidence, dict):
        fail("contract fixture evidence must be an object")
    for key, expected in EXPECTED_EVIDENCE.items():
        actual = evidence.get(key)
        if actual != expected:
            fail(f"contract fixture evidence.{key} must be {expected!r}, got {actual!r}")
    generator = fixture.get("generator")
    if not isinstance(generator, dict):
        fail("contract fixture generator must be an object")
    if generator.get("stdlib_only") is not True:
        fail("contract fixture generator.stdlib_only must be true")
    if generator.get("active_source_output_by_default") is not False:
        fail("contract fixture generator.active_source_output_by_default must be false")


def validate_input_fixture(payload: dict[str, Any], source_symbols: list[str]) -> None:
    if payload.get("schema_version") != 1:
        fail("input fixture schema_version must be 1")
    if payload.get("replacement_kind") != "source_owned_table_content_replacement":
        fail("input fixture replacement_kind is wrong")
    if payload.get("target_file") != "src/modes/UltimateIdentityRuntimeTables.hpp":
        fail("input fixture target_file is wrong")
    if payload.get("table_shape") != EXPECTED_SHAPE:
        fail(f"input fixture table_shape must be {EXPECTED_SHAPE!r}")
    tables = payload.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_SHAPE["table_count"]:
        fail("input fixture tables must contain exactly 27 tables")
    seen: set[str] = set()
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"input fixture tables[{table_index}] must be an object")
        symbol = table.get("table_symbol")
        if not isinstance(symbol, str) or not symbol:
            fail(f"input fixture tables[{table_index}].table_symbol must be a string")
        if symbol in seen:
            fail(f"input fixture duplicate table_symbol: {symbol}")
        seen.add(symbol)
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
    if seen != set(source_symbols):
        fail("input fixture table symbols must exactly match source table symbols")


def validate_output_fixture() -> None:
    source_text = read_required(SOURCE_TABLES)
    output_text = read_required(OUTPUT_FIXTURE)
    source_tables = parse_tables(source_text)
    output_tables = parse_tables(output_text)
    source_symbols = [symbol for symbol, _points, _span in source_tables]
    output_symbols = [symbol for symbol, _points, _span in output_tables]
    if output_symbols != source_symbols:
        fail("output fixture must preserve all table symbols and order")
    if strip_table_bodies(output_text) != strip_table_bodies(source_text):
        fail("output fixture differs from source outside StickPoint table initializer bodies")
    for token in FORBIDDEN_ACTIVE_SELECTION_TOKENS:
        if token in output_text:
            fail(f"output fixture must not touch active selection text: {token}")
    for phrase in FORBIDDEN_OUTPUT_POSITIVE_CLAIMS:
        if phrase in output_text:
            fail(f"output fixture contains forbidden positive implementation claim: {phrase}")


def validate_generator_determinism() -> None:
    tmp = OUTPUT_FIXTURE.with_suffix(OUTPUT_FIXTURE.suffix + ".tmp")
    try:
        run = subprocess.run(
            ["python3", rel(GENERATOR), rel(INPUT_FIXTURE), rel(tmp)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode != 0:
            fail("generator deterministic run failed: " + run.stderr.strip())
        diff = subprocess.run(
            ["diff", "-u", rel(OUTPUT_FIXTURE), rel(tmp)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if diff.returncode != 0:
            fail("generated output fixture is not deterministic:\n" + diff.stdout)
    finally:
        if tmp.exists():
            tmp.unlink()


def validate_docs() -> None:
    contract = read_required(CONTRACT_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)
    require_phrases(rel(CONTRACT_DOC), contract, REQUIRED_DOC_PHRASES)
    for path, text in ((README, readme), (CURRENT_STATE, current_state), (ROADMAP, roadmap)):
        require_phrases(rel(path), text, REQUIRED_INDEX_PHRASES)
        require_phrases(rel(path), text, ("source_owned_table_replacement_design.md",))
        require_phrases(rel(path), text, ("generated source-owned baseline active HARDWARE_FAIL",))
        require_phrases(rel(path), text, ("dedicated active storage HARDWARE_FAIL",))
        require_phrases(rel(path), text, ("source-owned active-state preselection HARDWARE_PASS",))
        require_phrases(rel(path), text, ("no RuntimeConfigView selection change",))


def main() -> int:
    branch = validate_branch()
    source_symbols = [symbol for symbol, _points, _span in parse_tables(read_required(SOURCE_TABLES))]
    validate_contract_fixture(load_json_object(CONTRACT_FIXTURE))
    validate_input_fixture(load_json_object(INPUT_FIXTURE), source_symbols)
    validate_output_fixture()
    validate_generator_determinism()
    validate_docs()
    validate_changed_paths(changed_paths(branch), branch)
    print("glyph_source_owned_table_replacement_generator_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- contract: {rel(CONTRACT_DOC)}")
    print(f"- generator: {rel(GENERATOR)}")
    print(f"- output: {rel(OUTPUT_FIXTURE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
