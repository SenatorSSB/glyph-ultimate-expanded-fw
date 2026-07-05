#!/usr/bin/env python3
"""Validate the latest Tilt3 source-owned table-content replacement branch."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-latest-tilt3-table-content-replacement"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
REFERENCE_BRANCH = "codex/update-custom-modifier-tables-y2"

SOURCE_TABLES_REL = "src/modes/UltimateIdentityRuntimeTables.hpp"
ULTIMATE_CPP_REL = "src/modes/Ultimate.cpp"
INTERPRETER_REL = "src/modes/UltimateRuntimeConfigInterpreter.hpp"
CHECKER_REL = "tools/check_glyph_latest_tilt3_table_content_replacement.py"
GENERATOR_REL = "tools/generate_source_owned_table_replacement.py"
INPUT_FIXTURE_REL = "docs/runtime_config/fixtures/latest_tilt3_table_content_replacement_input.json"

PACKET = REPO_ROOT / "docs/runtime_config/latest_tilt3_table_content_replacement.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/latest_tilt3_table_content_replacement.json"
BUILD_REPORT = REPO_ROOT / "docs/runtime_config/latest_tilt3_table_content_replacement_build_report_2026-06-29.md"
BUILD_REPORT_FIXTURE = (
    REPO_ROOT / "docs/runtime_config/fixtures/latest_tilt3_table_content_replacement_build_report_2026-06-29.json"
)
HARDWARE_PLAN = REPO_ROOT / "docs/calibration/latest_tilt3_table_content_replacement_hardware_plan_2026-06-29.md"
HARDWARE_PLAN_FIXTURE = (
    REPO_ROOT / "docs/calibration/fixtures/latest_tilt3_table_content_replacement_hardware_plan_2026-06-29.json"
)
README = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
SOURCE_TABLES = REPO_ROOT / SOURCE_TABLES_REL
ULTIMATE_CPP = REPO_ROOT / ULTIMATE_CPP_REL
INTERPRETER = REPO_ROOT / INTERPRETER_REL
INPUT_FIXTURE = REPO_ROOT / INPUT_FIXTURE_REL
GENERATOR = REPO_ROOT / GENERATOR_REL

EXPECTED_TILT3_VALUES: tuple[tuple[int, int], ...] = (
    (69, 82),
    (128, 83),
    (187, 82),
    (69, 128),
    (128, 128),
    (187, 128),
    (76, 169),
    (128, 179),
    (180, 169),
)
EXPECTED_TABLE_COUNT = 27
EXPECTED_POINTS_PER_TABLE = 9
EXPECTED_SHAPE = {
    "table_count": EXPECTED_TABLE_COUNT,
    "points_per_table": EXPECTED_POINTS_PER_TABLE,
    "axes_per_point": 2,
}
EXPECTED_ROWS = [
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "TILT3-TABLE-001",
    "ACTIVE-VIEW-SELECTION-UNCHANGED-001",
    "RUNTIMECONFIGVIEW-UNCHANGED-001",
    "Y2-ROUTING-NOT-IMPLEMENTED-001",
    "NO-PARSER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
]

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": True,
    "hardware_test_required_before_merge": True,
    "latest_layout_partial_port": True,
    "implements_y2_routing": False,
    "implements_y2_table_identity": False,
    "implements_lt3_y2_role": False,
    "active_view_selection_changed": False,
    "runtime_config_view_replacement": False,
    "source_owned_table_content_replacement_wired": True,
    "changed_source_file": SOURCE_TABLES_REL,
    "changed_tables": ["kTilt3Table"],
    "reference_branch": REFERENCE_BRANCH,
    "port_plan": "docs/runtime_config/latest_layout_y2_port_plan.md",
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

ALLOWED_EXACT_CHANGED_PATHS = {
    SOURCE_TABLES_REL,
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
    "tools/check_glyph_latest_layout_y2_port_plan.py",
    "tools/check_glyph_source_owned_table_replacement_generator_contract.py",
}
ALLOWED_PREFIXES = (
    "docs/runtime_config/",
    "docs/calibration/",
)
FORBIDDEN_EXACT_PATHS = {
    ULTIMATE_CPP_REL,
    INTERPRETER_REL,
}
FORBIDDEN_PATH_RE = re.compile(
    r"^(?:HAL|hal|backend)(?:/|$)|"
    r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)|"
    r"GeneratedRuntimeConfigBaselineActiveView|generated_active|active_wrapper",
)
TABLE_RE = re.compile(
    r"constexpr\s+StickPoint\s+(?P<symbol>k[A-Za-z0-9_]+Table)\s*\[\s*9\s*\]\s*=\s*\{"
    r"(?P<body>.*?)"
    r"\};",
    re.DOTALL,
)
POINT_RE = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")

REQUIRED_PACKET_PHRASES = (
    "Status: FIRMWARE_BEHAVIOR_PENDING_HARDWARE.",
    "codex/update-custom-modifier-tables-y2",
    "direct merge of",
    "Changed source file: `src/modes/UltimateIdentityRuntimeTables.hpp`.",
    "Changed table: `kTilt3Table`.",
    "tools/generate_source_owned_table_replacement.py",
    "implements_y2_routing`: `false`",
    "implements_y2_table_identity`: `false`",
    "implements_lt3_y2_role`: `false`",
    "active_view_selection_changed`: `false`",
    "runtime_config_view_replacement`: `false`",
    "source_owned_table_content_replacement_wired`: `true`",
    "This branch does not modify `src/modes/Ultimate.cpp`.",
    "This branch does not modify",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp",
    "This branch does not implement Y2 routing",
    "This branch does not modify RuntimeConfigView symbols",
    "candidate view publication",
    "generated active wrappers",
    "runtime-loaded config",
    "backend/config.pb write paths",
    "No nunchuk validation is claimed",
    "hardware PASS is required",
)
REQUIRED_INDEX_PHRASES = (
    "latest_tilt3_table_content_replacement.md",
    "latest_tilt3_table_content_replacement.json",
    "latest_tilt3_table_content_replacement_input.json",
    "latest_tilt3_table_content_replacement_build_report_2026-06-29.md",
    "latest_tilt3_table_content_replacement_hardware_plan_2026-06-29.md",
    "check_glyph_latest_tilt3_table_content_replacement.py",
    "Y2 routing",
    "Nunchuk remains NOT_TESTED",
)


class LatestTilt3TableContentReplacementError(AssertionError):
    """Raised when the latest Tilt3 table-content replacement drifts."""


def fail(message: str) -> None:
    raise LatestTilt3TableContentReplacementError(message)


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
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    return completed


def git_lines(args: list[str], *, preserve_status: bool = False) -> list[str]:
    completed = git(args)
    if preserve_status:
        return [line for line in completed.stdout.splitlines() if line.strip()]
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def git_show(rel_path: str) -> str:
    completed = git(["show", f"{BASE_BRANCH}:{rel_path}"])
    return completed.stdout


def current_branch() -> str:
    branch = git_lines(["branch", "--show-current"])
    if not branch:
        fail("checker could not determine current branch")
    return branch[0]


def validate_branch() -> str:
    branch = current_branch()
    if branch not in {EXPECTED_BRANCH, MERGED_BRANCH}:
        fail(f"checker must run on {EXPECTED_BRANCH} or {MERGED_BRANCH}, got {branch}")
    result = git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False)
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
        if path in FORBIDDEN_EXACT_PATHS:
            fail(f"forbidden source path changed: {path}")
        if FORBIDDEN_PATH_RE.search(path):
            fail(f"forbidden runtime/write/flashing/generated-active path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
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
        if len(points) != EXPECTED_POINTS_PER_TABLE:
            fail(f"{symbol} must contain exactly {EXPECTED_POINTS_PER_TABLE} points")
        for x, y in points:
            if not (0 <= x <= 255 and 0 <= y <= 255):
                fail(f"{symbol} contains out-of-byte-range point ({x}, {y})")
        tables.append((symbol, points, (match.start("body"), match.end("body"))))
    if len(tables) != EXPECTED_TABLE_COUNT:
        fail(f"source must contain exactly {EXPECTED_TABLE_COUNT} StickPoint tables, found {len(tables)}")
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


def validate_source_tables() -> None:
    base_text = git_show(SOURCE_TABLES_REL)
    current_text = read_required(SOURCE_TABLES)
    base_tables = parse_tables(base_text)
    current_tables = parse_tables(current_text)
    base_symbols = [symbol for symbol, _points, _span in base_tables]
    current_symbols = [symbol for symbol, _points, _span in current_tables]
    if current_symbols != base_symbols:
        fail("table symbol names/order must be preserved")
    if strip_table_bodies(current_text) != strip_table_bodies(base_text):
        fail("source changed outside StickPoint table initializer bodies")
    base_points = {symbol: points for symbol, points, _span in base_tables}
    current_points = {symbol: points for symbol, points, _span in current_tables}
    changed = [symbol for symbol in current_symbols if current_points[symbol] != base_points[symbol]]
    if changed != ["kTilt3Table"]:
        fail(f"only kTilt3Table may change, got {changed!r}")
    if current_points["kTilt3Table"] != EXPECTED_TILT3_VALUES:
        fail(f"kTilt3Table values are not the latest intended values: {current_points['kTilt3Table']!r}")


def validate_unchanged_against_base(rel_path: str, path: Path) -> None:
    if read_required(path) != git_show(rel_path):
        fail(f"{rel_path} must remain unchanged against {BASE_BRANCH}")


def validate_input_fixture(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != 1:
        fail("input fixture schema_version must be 1")
    if payload.get("replacement_kind") != "source_owned_table_content_replacement":
        fail("input fixture replacement_kind must be source_owned_table_content_replacement")
    if payload.get("target_file") != SOURCE_TABLES_REL:
        fail(f"input fixture target_file must be {SOURCE_TABLES_REL}")
    if payload.get("table_shape") != EXPECTED_SHAPE:
        fail(f"input fixture table_shape must be {EXPECTED_SHAPE!r}")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        fail("input fixture metadata must be an object")
    if metadata.get("reference_branch") != REFERENCE_BRANCH:
        fail(f"input fixture metadata.reference_branch must be {REFERENCE_BRANCH}")
    if metadata.get("port_plan") != "docs/runtime_config/latest_layout_y2_port_plan.md":
        fail("input fixture metadata.port_plan must reference latest_layout_y2_port_plan.md")
    source_symbols = [symbol for symbol, _points, _span in parse_tables(read_required(SOURCE_TABLES))]
    tables = payload.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_TABLE_COUNT:
        fail("input fixture tables must contain exactly 27 tables")
    seen: set[str] = set()
    symbols: list[str] = []
    for table_index, table in enumerate(tables):
        if not isinstance(table, dict):
            fail(f"input fixture tables[{table_index}] must be an object")
        symbol = table.get("table_symbol")
        if not isinstance(symbol, str) or not symbol:
            fail(f"input fixture tables[{table_index}].table_symbol must be a string")
        if symbol in seen:
            fail(f"input fixture duplicate table_symbol: {symbol}")
        seen.add(symbol)
        symbols.append(symbol)
        points = table.get("points")
        if not isinstance(points, list) or len(points) != EXPECTED_POINTS_PER_TABLE:
            fail(f"input fixture {symbol}.points must contain exactly 9 points")
        normalized: list[tuple[int, int]] = []
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                fail(f"input fixture {symbol}.points[{point_index}] must be an object")
            x = point.get("x")
            y = point.get("y")
            if not isinstance(x, int) or isinstance(x, bool) or not 0 <= x <= 255:
                fail(f"input fixture {symbol}.points[{point_index}].x must be an integer byte")
            if not isinstance(y, int) or isinstance(y, bool) or not 0 <= y <= 255:
                fail(f"input fixture {symbol}.points[{point_index}].y must be an integer byte")
            normalized.append((x, y))
        if symbol == "kTilt3Table" and tuple(normalized) != EXPECTED_TILT3_VALUES:
            fail("input fixture kTilt3Table values do not match latest intended values")
    if symbols != source_symbols:
        fail("input fixture table symbols/order must match active source")


def validate_generator_output_matches_source() -> None:
    with tempfile.NamedTemporaryFile(prefix="glyph-latest-tilt3-", suffix=".hpp") as tmp:
        run = subprocess.run(
            ["python3", rel(GENERATOR), rel(INPUT_FIXTURE), tmp.name],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode != 0:
            fail("table replacement generator failed: " + run.stderr.strip())
        generated = Path(tmp.name).read_text(encoding="utf-8")
    if generated != read_required(SOURCE_TABLES):
        fail("active source table file must match generator output from checked-in input fixture")


def validate_replacement_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema_name") != "glyph_latest_tilt3_table_content_replacement":
        fail("replacement fixture schema_name is wrong")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"replacement fixture branch must be {EXPECTED_BRANCH}")
    if fixture.get("base_branch") != BASE_BRANCH:
        fail(f"replacement fixture base_branch must be {BASE_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"replacement fixture {key} must be {expected!r}, got {actual!r}")
    if fixture.get("latest_tilt3_values") != [list(point) for point in EXPECTED_TILT3_VALUES]:
        fail("replacement fixture latest_tilt3_values do not match expected values")


def validate_hardware_plan_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema_name") != "glyph_latest_tilt3_table_content_replacement_hardware_plan":
        fail("hardware plan fixture schema_name is wrong")
    if fixture.get("status") != "PLAN_ONLY":
        fail("hardware plan fixture status must be PLAN_ONLY")
    if fixture.get("branch_under_test") != EXPECTED_BRANCH:
        fail(f"hardware plan fixture branch_under_test must be {EXPECTED_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        if key in {"changed_source_file", "changed_tables", "reference_branch", "port_plan", "root_cause_proven"}:
            continue
        actual = fixture.get(key)
        if actual != expected:
            fail(f"hardware plan fixture {key} must be {expected!r}, got {actual!r}")
    rows = fixture.get("rows")
    if not isinstance(rows, list):
        fail("hardware plan fixture rows must be a list")
    actual_rows = [row.get("id") for row in rows if isinstance(row, dict)]
    if actual_rows != EXPECTED_ROWS:
        fail(f"hardware plan rows must be {EXPECTED_ROWS!r}, got {actual_rows!r}")
    for row in rows:
        if not isinstance(row, dict) or row.get("status") != "NOT_TESTED":
            fail("all hardware plan rows must be NOT_TESTED")


def validate_build_report_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema_name") != "glyph_latest_tilt3_table_content_replacement_build_report":
        fail("build report fixture schema_name is wrong")
    if fixture.get("status") != "local_build_report":
        fail("build report fixture status must be local_build_report")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"build report fixture branch must be {EXPECTED_BRANCH}")
    if fixture.get("canonical_build_command") != "pio run -e glyph_mk6":
        fail("build report fixture canonical_build_command must be pio run -e glyph_mk6")
    if fixture.get("local_build_result") != "PASS":
        fail("build report fixture local_build_result must be PASS")
    if fixture.get("build_completed") is not True:
        fail("build report fixture build_completed must be true")
    if fixture.get("artifact_hashes_are_rebuild_stable") is not False:
        fail("build report fixture artifact_hashes_are_rebuild_stable must be false")
    if fixture.get("artifact_hashes_are_checker_gate") is not False:
        fail("build report fixture artifact_hashes_are_checker_gate must be false")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        if key in {"changed_source_file", "changed_tables", "reference_branch", "port_plan", "root_cause_proven"}:
            continue
        actual = fixture.get(key)
        if actual != expected:
            fail(f"build report fixture {key} must be {expected!r}, got {actual!r}")
    hashes = fixture.get("artifact_hashes")
    if not isinstance(hashes, list) or len(hashes) < 1:
        fail("build report fixture must record at least one artifact hash observation")
    for item in hashes:
        if not isinstance(item, dict):
            fail("build report artifact_hashes entries must be objects")
        if item.get("available") is True:
            digest = item.get("sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                fail("available artifact hash entries must include a sha256 digest")


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).lower()


def require_phrases(label: str, text: str, phrases: tuple[str, ...] | list[str]) -> None:
    normalized_text = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized_text]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_docs() -> None:
    packet = read_required(PACKET)
    build_report = read_required(BUILD_REPORT)
    hardware_plan = read_required(HARDWARE_PLAN)
    require_phrases(rel(PACKET), packet, REQUIRED_PACKET_PHRASES)
    for direction, (x, y) in enumerate(EXPECTED_TILT3_VALUES, start=1):
        require_phrases(rel(PACKET), packet, (f"| {direction} | {x} | {y} |",))
    require_phrases(
        rel(BUILD_REPORT),
        build_report,
        (
            "Canonical command: pio run -e glyph_mk6",
            "artifact_hashes_are_rebuild_stable`: `false`",
            "artifact_hashes_are_checker_gate`: `false`",
            "No hardware result is claimed.",
            "hardware_test_required_before_merge: true",
            "Nunchuk remains NOT_TESTED",
        ),
    )
    require_phrases(rel(HARDWARE_PLAN), hardware_plan, EXPECTED_ROWS)
    require_phrases(rel(HARDWARE_PLAN), hardware_plan, ("Status: PLAN_ONLY.", "Do not let this active behavior change remain merged"))
    for path in (README, CURRENT_STATE, ROADMAP):
        require_phrases(rel(path), read_required(path), REQUIRED_INDEX_PHRASES)
    require_phrases(
        rel(CALIBRATION_INDEX),
        read_required(CALIBRATION_INDEX),
        (
            "latest_tilt3_table_content_replacement_hardware_plan_2026-06-29.md",
            "fixtures/latest_tilt3_table_content_replacement_hardware_plan_2026-06-29.json",
            "Y2 routing",
            "Nunchuk remains NOT_TESTED",
        ),
    )


def require_hardware_pass_after_merge(branch: str) -> None:
    if branch != MERGED_BRANCH:
        return
    candidates = [
        *REPO_ROOT.glob("docs/runtime_config/fixtures/*latest_tilt3_table_content_replacement*hardware*result*.json"),
        *REPO_ROOT.glob("docs/calibration/fixtures/*latest_tilt3_table_content_replacement*hardware*result*.json"),
    ]
    for candidate in candidates:
        payload = load_json_object(candidate)
        result = payload.get("overall_result") or payload.get("hardware_result") or payload.get("result")
        if result == "HARDWARE_PASS":
            return
    fail("configurator mode requires a preserved HARDWARE_PASS hardware result for this active behavior change")


def main() -> int:
    branch = validate_branch()
    validate_changed_paths(changed_paths(branch))
    validate_source_tables()
    validate_unchanged_against_base(ULTIMATE_CPP_REL, ULTIMATE_CPP)
    validate_unchanged_against_base(INTERPRETER_REL, INTERPRETER)
    validate_input_fixture(load_json_object(INPUT_FIXTURE))
    validate_generator_output_matches_source()
    validate_replacement_fixture(load_json_object(FIXTURE))
    validate_hardware_plan_fixture(load_json_object(HARDWARE_PLAN_FIXTURE))
    validate_build_report_fixture(load_json_object(BUILD_REPORT_FIXTURE))
    validate_docs()
    require_hardware_pass_after_merge(branch)
    print("glyph_latest_tilt3_table_content_replacement: PASS")
    print(f"- branch: {branch}")
    print(f"- changed_source_file: {SOURCE_TABLES_REL}")
    print(f"- changed_tables: kTilt3Table")
    print(f"- hardware_test_required_before_merge: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
