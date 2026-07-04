#!/usr/bin/env python3
"""Validate the source-owned table-content replacement diagnostic branch."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-diagnostic-source-owned-table-content-replacement"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

SOURCE_TABLES = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
ULTIMATE_CPP = REPO_ROOT / "src/modes/Ultimate.cpp"
INTERPRETER = REPO_ROOT / "src/modes/UltimateRuntimeConfigInterpreter.hpp"
DOC = REPO_ROOT / "docs/runtime_config/diagnostic_source_owned_table_content_replacement.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/diagnostic_source_owned_table_content_replacement.json"
INPUT_FIXTURE = (
    REPO_ROOT / "docs/runtime_config/fixtures/source_owned_table_content_replacement_diagnostic_input.json"
)
BUILD_REPORT = (
    REPO_ROOT / "docs/runtime_config/diagnostic_source_owned_table_content_replacement_build_report_2026-06-29.md"
)
BUILD_REPORT_FIXTURE = (
    REPO_ROOT
    / "docs/runtime_config/fixtures/diagnostic_source_owned_table_content_replacement_build_report_2026-06-29.json"
)
HARDWARE_PLAN = (
    REPO_ROOT / "docs/calibration/diagnostic_source_owned_table_content_replacement_hardware_plan_2026-06-29.md"
)
HARDWARE_PLAN_FIXTURE = (
    REPO_ROOT
    / "docs/calibration/fixtures/diagnostic_source_owned_table_content_replacement_hardware_plan_2026-06-29.json"
)
README = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_diagnostic_source_owned_table_content_replacement.py"

EXPECTED_SHAPE = {"table_count": 27, "points_per_table": 9, "axes_per_point": 2}
EXPECTED_CHANGED_POINTS = [
    {
        "table_symbol": "kRT1RF4CustomTable",
        "point_index": 4,
        "old_x": 128,
        "old_y": 128,
        "new_x": 129,
        "new_y": 128,
    }
]
EXPECTED_HARDWARE_ROWS = {
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "TABLE-CONTENT-REPLACEMENT-001",
    "ACTIVE-VIEW-SELECTION-UNCHANGED-001",
    "RUNTIMECONFIGVIEW-UNCHANGED-001",
    "NO-PARSER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}

ALLOWED_EXACT_CHANGED_PATHS = {
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/")
ALLOWED_EXISTING_CHECKERS = {
    "tools/check_glyph_diagnostic_generated_source_owned_baseline_active.py",
    "tools/check_glyph_source_owned_table_replacement_design.py",
    "tools/check_glyph_source_owned_table_replacement_generator_contract.py",
}

FORBIDDEN_EXACT_PATHS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp",
}
FORBIDDEN_PATH_RE = re.compile(
    r"^(?:HAL|hal|backend)(?:/|$)|(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
GENERATED_ACTIVE_WRAPPER_RE = re.compile(r"GeneratedRuntimeConfig.*ActiveView|ActiveView.*GeneratedRuntimeConfig")
TABLE_RE = re.compile(
    r"constexpr\s+StickPoint\s+(?P<symbol>k[A-Za-z0-9_]+Table)\s*\[\s*9\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
POINT_RE = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")

EXPECTED_FALSE_KEYS = {
    "active_view_selection_changed",
    "runtime_config_view_replacement",
    "runtime_loaded_config_implemented",
    "persistent_storage_implemented",
    "webserial_device_write_implemented",
    "backend_config_pb_write_path_implemented",
    "flashing_automation_implemented",
    "root_cause_proven",
}
EXPECTED_TRUE_KEYS = {
    "active_behavior_changed",
    "hardware_test_required_before_merge",
    "source_owned_table_content_replacement_wired",
}
FORBIDDEN_SOURCE_CLAIMS = (
    "runtime_loaded_config_implemented: true",
    "persistent_storage_implemented: true",
    "webserial_device_write_implemented: true",
    "backend_config_pb_write_path_implemented: true",
    "flashing_automation_implemented: true",
    "candidate.view is active",
    "candidate.view active publication: implemented",
    "nunchuk tested",
    "NUNCHUK_PASS",
)
REQUIRED_DOC_PHRASES = (
    "kRT1RF4CustomTable",
    "Point index",
    "128",
    "129",
    "active_behavior_changed",
    "hardware_test_required_before_merge",
    "active_view_selection_changed",
    "runtime_config_view_replacement",
    "source_owned_table_content_replacement_wired",
    "GetActiveRuntimeConfigState().active_view",
    "kSourceOwnedCurrentBaselineRuntimeConfig",
    "kSourceOwnedCurrentBaselineRuntimeTables",
    "runtime-loaded config: not implemented",
    "Nunchuk remains `NOT_TESTED`",
)
REQUIRED_NAV_PHRASES = (
    "diagnostic_source_owned_table_content_replacement.md",
    "diagnostic_source_owned_table_content_replacement.json",
    "source_owned_table_content_replacement_diagnostic_input.json",
    "diagnostic_source_owned_table_content_replacement_build_report_2026-06-29",
    "diagnostic_source_owned_table_content_replacement_hardware_plan_2026-06-29",
    "kRT1RF4CustomTable",
    "hardware-gated",
    "Nunchuk remains NOT_TESTED",
)


class DiagnosticSourceOwnedTableContentReplacementError(AssertionError):
    """Raised when the diagnostic branch violates its guardrails."""


def fail(message: str) -> None:
    raise DiagnosticSourceOwnedTableContentReplacementError(message)


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


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if check and completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    return completed


def git_lines(args: list[str]) -> list[str]:
    return [line.strip() for line in git(args).stdout.splitlines() if line.strip()]


def current_branch() -> str:
    lines = git_lines(["branch", "--show-current"])
    if not lines:
        fail("could not determine current branch")
    return lines[0]


def validate_branch() -> str:
    branch = current_branch()
    if branch not in {EXPECTED_BRANCH, MERGED_BRANCH}:
        fail(f"checker must run on {EXPECTED_BRANCH} or {MERGED_BRANCH}, got {branch}")
    ancestor = git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False)
    if ancestor.returncode != 0:
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
    for line in git(["status", "--short"]).stdout.splitlines():
        path = status_path(line)
        if path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if path in FORBIDDEN_EXACT_PATHS:
            fail(f"forbidden source file changed: {path}")
        if FORBIDDEN_PATH_RE.search(path):
            fail(f"forbidden storage/write/WebSerial/flashing/backend/config.pb path changed: {path}")
        if GENERATED_ACTIVE_WRAPPER_RE.search(path):
            fail(f"generated active wrapper path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if path in ALLOWED_EXISTING_CHECKERS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


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
    for _symbol, _points, (start, end) in parse_tables(text):
        parts.append(text[cursor:start])
        parts.append("<StickPoint table body>")
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def configurator_file(path: Path) -> str:
    return git(["show", f"{BASE_BRANCH}:{rel(path)}"]).stdout


def changed_point_list(
    baseline_tables: list[tuple[str, tuple[tuple[int, int], ...], tuple[int, int]]],
    current_tables: list[tuple[str, tuple[tuple[int, int], ...], tuple[int, int]]],
) -> list[dict[str, int | str]]:
    baseline_by_symbol = {symbol: points for symbol, points, _span in baseline_tables}
    changes: list[dict[str, int | str]] = []
    for symbol, points, _span in current_tables:
        for point_index, (new_x, new_y) in enumerate(points):
            old_x, old_y = baseline_by_symbol[symbol][point_index]
            if (old_x, old_y) != (new_x, new_y):
                changes.append(
                    {
                        "table_symbol": symbol,
                        "point_index": point_index,
                        "old_x": old_x,
                        "old_y": old_y,
                        "new_x": new_x,
                        "new_y": new_y,
                    }
                )
    return changes


def validate_source_diff(fixture: dict[str, Any]) -> None:
    baseline_text = configurator_file(SOURCE_TABLES)
    current_text = read_required(SOURCE_TABLES)
    baseline_tables = parse_tables(baseline_text)
    current_tables = parse_tables(current_text)
    baseline_symbols = [symbol for symbol, _points, _span in baseline_tables]
    current_symbols = [symbol for symbol, _points, _span in current_tables]
    if current_symbols != baseline_symbols:
        fail("table symbol names/order changed")
    if strip_table_bodies(current_text) != strip_table_bodies(baseline_text):
        fail("source changed outside StickPoint table initializer bodies")
    changes = changed_point_list(baseline_tables, current_tables)
    if changes != EXPECTED_CHANGED_POINTS:
        fail(f"changed point list mismatch: {changes!r}")
    fixture_changes = [
        {key: point[key] for key in ("table_symbol", "point_index", "old_x", "old_y", "new_x", "new_y")}
        for point in fixture.get("changed_points", [])
    ]
    if fixture_changes != EXPECTED_CHANGED_POINTS:
        fail("diagnostic fixture changed_points does not match expected source delta")


def validate_required_fixture_values(label: str, payload: dict[str, Any]) -> None:
    for key in EXPECTED_TRUE_KEYS:
        if payload.get(key) is not True:
            fail(f"{label} {key} must be true")
    for key in EXPECTED_FALSE_KEYS:
        if payload.get(key) is not False:
            fail(f"{label} {key} must be false")
    if payload.get("nunchuk_status") != "NOT_TESTED":
        fail(f"{label} nunchuk_status must be NOT_TESTED")


def validate_input_fixture(payload: dict[str, Any], source_symbols: list[str]) -> None:
    if payload.get("schema_version") != 1:
        fail("input fixture schema_version must be 1")
    if payload.get("replacement_kind") != "source_owned_table_content_replacement":
        fail("input fixture replacement_kind mismatch")
    if payload.get("target_file") != "src/modes/UltimateIdentityRuntimeTables.hpp":
        fail("input fixture target_file mismatch")
    if payload.get("table_shape") != EXPECTED_SHAPE:
        fail("input fixture table_shape mismatch")
    tables = payload.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_SHAPE["table_count"]:
        fail("input fixture must contain 27 tables")
    seen: set[str] = set()
    for table in tables:
        if not isinstance(table, dict):
            fail("input fixture table entries must be objects")
        symbol = table.get("table_symbol")
        if not isinstance(symbol, str) or not symbol:
            fail("input fixture table_symbol must be a non-empty string")
        if symbol in seen:
            fail(f"input fixture duplicate table_symbol: {symbol}")
        seen.add(symbol)
        points = table.get("points")
        if not isinstance(points, list) or len(points) != EXPECTED_SHAPE["points_per_table"]:
            fail(f"input fixture {symbol} must contain 9 points")
        for point in points:
            if not isinstance(point, dict):
                fail(f"input fixture {symbol} point must be an object")
            for axis in ("x", "y"):
                value = point.get(axis)
                if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255:
                    fail(f"input fixture {symbol}.{axis} values must be integer bytes")
    if list(seen) and seen != set(source_symbols):
        fail("input fixture table symbols must exactly match source table symbols")


def validate_hardware_plan(payload: dict[str, Any]) -> None:
    if payload.get("hardware_test_required_before_merge") is not True:
        fail("hardware plan must require hardware before merge")
    if payload.get("active_behavior_changed") is not True:
        fail("hardware plan active_behavior_changed must be true")
    if payload.get("nunchuk_status") != "NOT_TESTED":
        fail("hardware plan nunchuk_status must be NOT_TESTED")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail("hardware plan rows must be a list")
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    if set(by_id) != EXPECTED_HARDWARE_ROWS:
        fail("hardware plan rows do not match required row ids")
    for row_id, row in by_id.items():
        if row.get("status") != "NOT_TESTED":
            fail(f"hardware plan row {row_id} must be NOT_TESTED")


def validate_build_report(payload: dict[str, Any]) -> None:
    if payload.get("canonical_command") != "pio run -e glyph_mk6":
        fail("build report canonical_command mismatch")
    if payload.get("artifact_hashes_are_rebuild_stable") is not False:
        fail("artifact_hashes_are_rebuild_stable must be false")
    if payload.get("artifact_hashes_are_checker_gate") is not False:
        fail("artifact_hashes_are_checker_gate must be false")
    if payload.get("changed_source_file") != rel(SOURCE_TABLES):
        fail("build report changed_source_file mismatch")
    fixture_changes = [
        {key: point[key] for key in ("table_symbol", "point_index", "old_x", "old_y", "new_x", "new_y")}
        for point in payload.get("changed_points", [])
    ]
    if fixture_changes != EXPECTED_CHANGED_POINTS:
        fail("build report changed_points mismatch")


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split())


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_docs() -> None:
    doc_text = read_required(DOC)
    build_text = read_required(BUILD_REPORT)
    plan_text = read_required(HARDWARE_PLAN)
    for phrase in FORBIDDEN_SOURCE_CLAIMS:
        for label, text in ((rel(DOC), doc_text), (rel(BUILD_REPORT), build_text), (rel(HARDWARE_PLAN), plan_text)):
            if phrase in text:
                fail(f"{label} contains forbidden claim: {phrase}")
    require_phrases(rel(DOC), doc_text, REQUIRED_DOC_PHRASES)
    require_phrases(rel(HARDWARE_PLAN), plan_text, tuple(sorted(EXPECTED_HARDWARE_ROWS)))
    for path in (README, CURRENT_STATE, ROADMAP):
        require_phrases(rel(path), read_required(path), REQUIRED_NAV_PHRASES)
    require_phrases(
        rel(CALIBRATION_INDEX),
        read_required(CALIBRATION_INDEX),
        (
            "diagnostic_source_owned_table_content_replacement_hardware_plan_2026-06-29",
            "kRT1RF4CustomTable",
            "hardware-gated",
            "Nunchuk remains NOT_TESTED",
        ),
    )


def validate_unchanged_active_path_files() -> None:
    for path in (ULTIMATE_CPP, INTERPRETER):
        diff = git(["diff", "--quiet", BASE_BRANCH, "--", rel(path)], check=False)
        if diff.returncode != 0:
            fail(f"{rel(path)} changed against {BASE_BRANCH}")
    ultimate_text = read_required(ULTIMATE_CPP)
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in ultimate_text:
        fail("UpdateAnalogOutputs must continue resolving active runtime config through ResolveActiveRuntimeConfig")
    if "&kSourceOwnedCurrentBaselineRuntimeConfig" not in ultimate_text:
        fail("GetActiveRuntimeConfigState must continue publishing kSourceOwnedCurrentBaselineRuntimeConfig")
    for required in ("kDirectionTwoIndex", "kDirectionEightIndex", "kDirectionFiveIndex"):
        if required not in ultimate_text:
            fail(f"Ultimate.cpp must preserve {required} expression")


def validate_configurator_hardware_gate(branch: str, fixture: dict[str, Any]) -> None:
    if branch != MERGED_BRANCH:
        return
    if fixture.get("active_behavior_changed") is not True:
        return
    result_fixture = (
        REPO_ROOT
        / "docs/calibration/fixtures/diagnostic_source_owned_table_content_replacement_hardware_result_2026-06-29.json"
    )
    if not result_fixture.exists():
        fail("configurator merge with active behavior change requires preserved HARDWARE_PASS result fixture")
    result = load_json_object(result_fixture)
    if result.get("overall_result") != "HARDWARE_PASS":
        fail("configurator merge requires overall_result HARDWARE_PASS")
    if result.get("nunchuk_status") != "NOT_TESTED":
        fail("hardware result must preserve nunchuk_status NOT_TESTED unless actually tested")


def main() -> int:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch))
    fixture = load_json_object(FIXTURE)
    validate_required_fixture_values(rel(FIXTURE), fixture)
    validate_source_diff(fixture)
    source_symbols = [symbol for symbol, _points, _span in parse_tables(read_required(SOURCE_TABLES))]
    validate_input_fixture(load_json_object(INPUT_FIXTURE), source_symbols)
    validate_hardware_plan(load_json_object(HARDWARE_PLAN_FIXTURE))
    validate_build_report(load_json_object(BUILD_REPORT_FIXTURE))
    validate_unchanged_active_path_files()
    validate_docs()
    validate_configurator_hardware_gate(branch, fixture)
    print("glyph_diagnostic_source_owned_table_content_replacement: PASS")
    print(f"- branch: {branch}")
    print("- changed point: kRT1RF4CustomTable[4] (128,128) -> (129,128)")
    print("- active_view_selection_changed=false")
    print("- runtime_config_view_replacement=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
