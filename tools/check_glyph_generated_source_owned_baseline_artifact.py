#!/usr/bin/env python3
"""Validate the inert generated source-owned current-baseline artifact."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-generated-source-owned-baseline-artifact"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

ARTIFACT = REPO_ROOT / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
SOURCE_TABLES = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
SOURCE_INTERPRETER = REPO_ROOT / "src/modes/UltimateRuntimeConfigInterpreter.hpp"
ULTIMATE_CPP = REPO_ROOT / "src/modes/Ultimate.cpp"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_baseline_artifact.json"
DOC = REPO_ROOT / "docs/runtime_config/generated_source_owned_baseline_artifact.md"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
GENERATOR = REPO_ROOT / "tools/generate_source_owned_runtime_config.py"

EXPECTED_TABLE_COUNT = 28
EXPECTED_POINT_COUNT = 9
EXPECTED_AXES_PER_POINT = 2

ALLOWED_PATH_RE = re.compile(
    r"^(?:docs/runtime_config/|docs/agent_framework/|docs/CURRENT_STATE\.md|docs/ROADMAP\.md|tools/|"
    r"src/modes/runtime_config/generated_source_owned/)"
)
FORBIDDEN_CHANGED_PATH_RE = re.compile(
    r"^(?:src/modes/Ultimate\.cpp|HAL/|backend/)|"
    r"(?:^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
ARTIFACT_PATH_RE = re.compile(
    r"^src/modes/runtime_config/generated_source_owned/[A-Za-z0-9_.-]+\.(?:h|hpp|hh|cc|cpp)$"
)

REQUIRED_ARTIFACT_MARKERS = (
    "generated source-owned runtime config artifact",
    "inert generated-table placeholder",
    "not wired into runtime selection",
    "generated baseline equivalent to kSourceOwnedCurrentBaselineRuntimeConfig",
)
FORBIDDEN_ARTIFACT_TOKENS = (
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

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "baseline_artifact_only": True,
    "generated_baseline_artifact_equivalent_to_current_source_owned_baseline": True,
    "generated_tables_wired_active": False,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

REQUIRED_DOC_PHRASES = (
    "generated_source_owned_artifact_install.md",
    "generated_source_owned_generator_contract.md",
    "--emit-current-source-owned-baseline",
    "active-storage `HARDWARE_FAIL` evidence",
    "source-owned active-state `HARDWARE_PASS` evidence",
    "future hardware gate required before generated source-owned baseline artifact is selected active",
    "not included by `src/modes/Ultimate.cpp`",
    "not wired into runtime selection",
    "does not change active firmware behavior",
    "RAM-backed active table publication remains unsafe under current diagnostics",
    "low-level failure mechanism remains unproven",
    "Nunchuk remains `NOT_TESTED`",
)
REQUIRED_INDEX_PHRASES = (
    "generated_source_owned_baseline_artifact.md",
    "fixtures/generated_source_owned_baseline_artifact.json",
    "GeneratedRuntimeConfigBaseline.current.hpp",
    "generated_source_owned_artifact_install.md",
    "generated_source_owned_generator_contract.md",
    "--emit-current-source-owned-baseline",
    "active-storage `HARDWARE_FAIL` evidence",
    "source-owned active-state `HARDWARE_PASS` evidence",
    "future hardware gate required before generated source-owned baseline artifact is selected active",
)


class GeneratedSourceOwnedBaselineArtifactError(AssertionError):
    """Raised when the generated source-owned baseline artifact drifts."""


def fail(message: str) -> None:
    raise GeneratedSourceOwnedBaselineArtifactError(message)


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


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if not ALLOWED_PATH_RE.search(path):
            fail(f"out-of-scope changed path: {path}")
        if FORBIDDEN_CHANGED_PATH_RE.search(path):
            fail(f"forbidden runtime/storage/write/WebSerial/flashing/backend path changed: {path}")
        if path.startswith("src/modes/runtime_config/generated_source_owned/") and not ARTIFACT_PATH_RE.match(path):
            fail(f"generated artifact path is outside allowed source-owned artifact shape: {path}")


def parse_source_stick_tables(text: str) -> dict[str, list[tuple[int, int]]]:
    table_re = re.compile(
        r"constexpr\s+StickPoint\s+(k[A-Za-z0-9_]+Table)\s*\[\s*9\s*\]\s*=\s*\{(?P<body>.*?)\};",
        re.DOTALL,
    )
    point_re = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")
    tables: dict[str, list[tuple[int, int]]] = {}
    for match in table_re.finditer(text):
        symbol = match.group(1)
        points = [(int(x), int(y)) for x, y in point_re.findall(match.group("body"))]
        if len(points) != EXPECTED_POINT_COUNT:
            fail(f"{symbol} must contain {EXPECTED_POINT_COUNT} points")
        for x, y in points:
            if not (0 <= x <= 255 and 0 <= y <= 255):
                fail(f"{symbol} contains out-of-byte-range point ({x}, {y})")
        if symbol in tables:
            fail(f"duplicate source table symbol: {symbol}")
        tables[symbol] = points
    return tables


def parse_source_baseline_order(text: str) -> list[str]:
    block_match = re.search(
        r"kSourceOwnedCurrentBaselineRuntimeTables\s*\[\s*[^\]]+\s*\]\s*=\s*\{(?P<body>.*?)\};",
        text,
        re.DOTALL,
    )
    if block_match is None:
        fail("could not find kSourceOwnedCurrentBaselineRuntimeTables")
    row_re = re.compile(
        r"\{\s*RuntimeTableId::[A-Za-z0-9_]+\s*,\s*\"(?P<symbol>k[A-Za-z0-9_]+Table)\"\s*,\s*(?P=symbol)\s*,"
    )
    symbols = [match.group("symbol") for match in row_re.finditer(block_match.group("body"))]
    if len(symbols) < EXPECTED_TABLE_COUNT:
        fail(f"source baseline must contain at least {EXPECTED_TABLE_COUNT} tables, found {len(symbols)}")
    if len(set(symbols)) != len(symbols):
        fail("source baseline contains duplicate table symbols")
    return symbols


def source_baseline_tables() -> list[tuple[str, list[tuple[int, int]]]]:
    tables = parse_source_stick_tables(read_required(SOURCE_TABLES))
    ordered_symbols = parse_source_baseline_order(read_required(SOURCE_INTERPRETER))
    ordered_tables: list[tuple[str, list[tuple[int, int]]]] = []
    for symbol in ordered_symbols:
        if symbol not in tables:
            fail(f"source baseline references missing table: {symbol}")
        ordered_tables.append((symbol, tables[symbol]))
    return ordered_tables


def parse_generated_artifact(text: str, expected_table_count: int) -> list[tuple[str, list[tuple[int, int]]]]:
    for marker in REQUIRED_ARTIFACT_MARKERS:
        if marker not in text:
            fail(f"generated baseline artifact missing marker {marker!r}")
    for token in FORBIDDEN_ARTIFACT_TOKENS:
        if token in text:
            fail(f"generated baseline artifact contains forbidden active wiring token {token!r}")

    table_count = re.search(r"kGeneratedSourceOwnedRuntimeConfigTableCount\s*=\s*(\d+)u", text)
    point_count = re.search(r"kGeneratedSourceOwnedRuntimeConfigPointsPerTable\s*=\s*(\d+)u", text)
    axes_count = re.search(r"kGeneratedSourceOwnedRuntimeConfigAxesPerPoint\s*=\s*(\d+)u", text)
    if not table_count or int(table_count.group(1)) != expected_table_count:
        fail("generated baseline artifact table count does not match expected shape")
    if not point_count or int(point_count.group(1)) != EXPECTED_POINT_COUNT:
        fail("generated baseline artifact point count does not match expected shape")
    if not axes_count or int(axes_count.group(1)) != EXPECTED_AXES_PER_POINT:
        fail("generated baseline artifact axes-per-point does not match expected shape")

    row_re = re.compile(
        rf"\{{\s*//\s*(?P<index>\d+)\s+(?P<symbol>k[A-Za-z0-9_]+Table)\s*(?P<body>.*?)\n\s*\}},",
        re.DOTALL,
    )
    point_re = re.compile(r"\{\s*(\d+)u?\s*,\s*(\d+)u?\s*\}")
    tables: list[tuple[str, list[tuple[int, int]]]] = []
    seen_indexes: set[int] = set()
    seen_symbols: set[str] = set()
    for match in row_re.finditer(text):
        index = int(match.group("index"))
        symbol = match.group("symbol")
        points = [(int(x), int(y)) for x, y in point_re.findall(match.group("body"))]
        if len(points) != EXPECTED_POINT_COUNT:
            fail(f"generated table {symbol} must contain {EXPECTED_POINT_COUNT} points")
        if index in seen_indexes:
            fail(f"generated artifact contains duplicate table index: {index}")
        if symbol in seen_symbols:
            fail(f"generated artifact contains duplicate table symbol: {symbol}")
        seen_indexes.add(index)
        seen_symbols.add(symbol)
        tables.append((symbol, points))
    if len(tables) != expected_table_count:
        fail(f"generated artifact must contain {expected_table_count} tables, found {len(tables)}")
    if sorted(seen_indexes) != list(range(expected_table_count)):
        fail(f"generated artifact table indexes must be contiguous from 0 to {expected_table_count - 1}")
    return tables


def validate_equivalence() -> None:
    source = source_baseline_tables()
    expected_table_count = len(source)
    generated = parse_generated_artifact(read_required(ARTIFACT), expected_table_count)
    if len(source) != len(generated):
        fail("generated baseline artifact table count differs from source baseline")
    for index, ((source_name, source_points), (generated_name, generated_points)) in enumerate(zip(source, generated)):
        if source_name != generated_name:
            fail(
                f"generated baseline artifact table name/order mismatch at {index}: "
                f"{generated_name} != {source_name}"
            )
        if len(source_points) != len(generated_points):
            fail(f"generated baseline artifact point count mismatch for {source_name}")
        for point_index, (source_point, generated_point) in enumerate(zip(source_points, generated_points)):
            if source_point != generated_point:
                fail(
                    f"generated baseline artifact point mismatch for {source_name}[{point_index}]: "
                    f"{generated_point} != {source_point}"
                )


def validate_fixture(fixture: dict[str, Any]) -> None:
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"fixture {key} must be {expected!r}, got {actual!r}")
    artifact = fixture.get("baseline_artifact")
    if artifact != rel(ARTIFACT):
        fail(f"fixture baseline_artifact must be {rel(ARTIFACT)!r}")
    comparison = fixture.get("equivalence_comparison")
    if not isinstance(comparison, dict):
        fail("fixture equivalence_comparison must be an object")
    expected_comparison = {
        "method": "source-inspection",
        "source_tables": rel(SOURCE_TABLES),
        "source_runtime_view": rel(SOURCE_INTERPRETER),
        "artifact_tables": rel(ARTIFACT),
        "table_count": len(source_baseline_tables()),
        "points_per_table": EXPECTED_POINT_COUNT,
        "axes_per_point": EXPECTED_AXES_PER_POINT,
    }
    for key, expected in expected_comparison.items():
        if comparison.get(key) != expected:
            fail(f"fixture equivalence_comparison.{key} must be {expected!r}")


def require_phrases(label: str, text: str, phrases: tuple[str, ...]) -> None:
    normalized_text = " ".join(text.lower().split())
    missing = [
        phrase
        for phrase in phrases
        if " ".join(phrase.lower().split()) not in normalized_text
    ]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_docs() -> None:
    doc = read_required(DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)
    require_phrases(rel(DOC), doc, REQUIRED_DOC_PHRASES)
    for path, text in (
        (README, readme),
        (CURRENT_STATE, current_state),
        (ROADMAP, roadmap),
    ):
        require_phrases(rel(path), text, REQUIRED_INDEX_PHRASES)


def validate_not_included_by_ultimate() -> None:
    ultimate_text = read_required(ULTIMATE_CPP)
    if ARTIFACT.name in ultimate_text:
        fail(f"{rel(ARTIFACT)} must not be included by src/modes/Ultimate.cpp")
    if "runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp" in ultimate_text:
        fail(f"{rel(ARTIFACT)} must not be included by src/modes/Ultimate.cpp")


def validate_deterministic_generation() -> None:
    completed = subprocess.run(
        ["python3", str(GENERATOR), "--emit-current-source-owned-baseline"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("baseline generator failed: " + completed.stderr.strip())
    if completed.stdout != read_required(ARTIFACT):
        fail("generated baseline artifact does not match deterministic source-baseline generator output")


def main() -> int:
    branch = validate_branch()
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)
    validate_changed_paths(changed_paths(branch))
    validate_not_included_by_ultimate()
    validate_equivalence()
    validate_deterministic_generation()
    validate_docs()
    print("glyph_generated_source_owned_baseline_artifact: PASS")
    print(f"- branch: {branch}")
    print(f"- artifact: {rel(ARTIFACT)}")
    print("- baseline equivalence: proven by source/artifact table comparison")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
