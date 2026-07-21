#!/usr/bin/env python3
"""Validate supersession of the historical literal-table replacement contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RECOVERY_BRANCH = "runtime-config-literal-table-contract-supersession"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"

CONTRACT_DOC = REPO_ROOT / "docs/runtime_config/source_owned_table_replacement_generator_contract.md"
CONTRACT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_table_replacement_generator_contract.json"
INPUT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/source_owned_table_replacement_input.example.json"
OUTPUT_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/generated_outputs/UltimateIdentityRuntimeTables.replacement.example.hpp"
SOURCE_TABLES = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
GENERATOR = REPO_ROOT / "tools/generate_source_owned_table_replacement.py"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
AGENT_CONTEXT = REPO_ROOT / "docs/AGENT_CONTEXT.md"
CHECKER_REL = "tools/check_glyph_source_owned_table_replacement_generator_contract.py"
GENERATOR_REL = "tools/generate_source_owned_table_replacement.py"

EXPECTED_TABLE_COUNT = 28
EXPECTED_POINTS_PER_TABLE = 9
EXPECTED_AXES_PER_POINT = 2
FINAL_TABLE_SYMBOL = "kLt1LowMagnitudeTable"
GENERATED_BASELINE_INCLUDE = '#include "runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"'
ALIAS_RE = re.compile(r"SOURCE_OWNED_GENERATED_TABLE\(\s*(k[A-Za-z0-9_]+Table)\s*,\s*(\d+)\s*\);")
LITERAL_TABLE_RE = re.compile(r"constexpr\s+StickPoint\s+k[A-Za-z0-9_]+Table\s*\[\s*9\s*\]\s*=\s*\{")
HISTORICAL_LITERAL_TABLE_RE = re.compile(r"constexpr\s+StickPoint\s+k[A-Za-z0-9_]+Table\s*\[\s*9\s*\]\s*=\s*\{")

ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/AGENT_CONTEXT.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    GENERATOR_REL,
    CHECKER_REL,
    "tools/check_glyph_docs_agent_surface.py",
}
ALLOWED_PREFIXES = ("docs/runtime_config/",)
FORBIDDEN_SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)")
FORBIDDEN_SPECIAL_PATH_RE = re.compile(r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)")

SUCCESSOR_REFERENCES = (
    "generated_source_owned_generator_modes.md",
    "source_authority_intake_workflow.md",
    "tools/source_owned_generator_modes.py",
    "tools/manage_source_owned_source_authority_intake.py",
    "parse_source_owned_baseline_contract",
)


class SourceOwnedTableReplacementGeneratorContractError(AssertionError):
    """Raised when the historical supersession boundary drifts."""


def fail(message: str) -> None:
    raise SourceOwnedTableReplacementGeneratorContractError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def git_lines(args: list[str], *, preserve_status: bool = False) -> list[str]:
    completed = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + completed.stderr.strip())
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    return lines if preserve_status else [line.strip() for line in lines]


def validate_branch() -> str:
    branches = git_lines(["branch", "--show-current"])
    if not branches:
        fail("checker could not determine current branch")
    branch = branches[0]
    if branch not in {RECOVERY_BRANCH, MERGED_BRANCH}:
        fail(f"checker must run on {RECOVERY_BRANCH} or {MERGED_BRANCH}, got {branch}")
    if branch == RECOVERY_BRANCH:
        result = subprocess.run(["git", "merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], cwd=REPO_ROOT)
        if result.returncode != 0:
            fail(f"{BASE_BRANCH} must be an ancestor of HEAD")
    return branch


def status_path(status_line: str) -> str:
    path = status_line[3:].strip()
    return path.split(" -> ", 1)[-1]


def changed_paths(branch: str) -> set[str]:
    paths: set[str] = set()
    if branch == RECOVERY_BRANCH:
        paths.update(git_lines(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]))
    paths.update(status_path(line) for line in git_lines(["status", "--short"], preserve_status=True))
    return {path for path in paths if path}


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if FORBIDDEN_SOURCE_PATH_RE.search(path):
            fail(f"firmware/source or publication path changed on recovery branch: {path}")
        if FORBIDDEN_SPECIAL_PATH_RE.search(path):
            fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS or any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


def canonical_baseline() -> dict[str, Any]:
    tools_dir = str(REPO_ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    try:
        from generate_source_owned_runtime_config import parse_source_owned_baseline_contract

        return parse_source_owned_baseline_contract()
    except Exception as exc:  # canonical parser supplies the source-specific detail
        fail(f"canonical source-owned baseline extraction failed: {exc}")


def validate_current_representation(baseline: dict[str, Any]) -> list[str]:
    tables = baseline.get("tables")
    if not isinstance(tables, list) or len(tables) != EXPECTED_TABLE_COUNT:
        fail(f"canonical extraction must return exactly {EXPECTED_TABLE_COUNT} tables")
    symbols: list[str] = []
    for table_id, table in enumerate(tables):
        if not isinstance(table, dict) or table.get("table_id") != table_id:
            fail(f"canonical table {table_id} has unstable identity")
        symbol = table.get("table_symbol")
        points = table.get("points")
        if not isinstance(symbol, str) or not symbol:
            fail(f"canonical table {table_id} has no symbol")
        if not isinstance(points, list) or len(points) != EXPECTED_POINTS_PER_TABLE:
            fail(f"{symbol} must contain exactly {EXPECTED_POINTS_PER_TABLE} canonical points")
        for point in points:
            if not isinstance(point, dict) or set(point) != {"x", "y"}:
                fail(f"{symbol} canonical point shape drifted")
            if any(not isinstance(point[axis], int) or isinstance(point[axis], bool) or not 0 <= point[axis] <= 255 for axis in ("x", "y")):
                fail(f"{symbol} canonical point is outside byte range")
        symbols.append(symbol)
    if len(set(symbols)) != len(symbols):
        fail("canonical extraction returned duplicate table symbols")
    if symbols[-1] != FINAL_TABLE_SYMBOL:
        fail(f"final canonical table must be {FINAL_TABLE_SYMBOL}")

    source = read_required(SOURCE_TABLES)
    if GENERATED_BASELINE_INCLUDE not in source:
        fail("active table header must include the current generated baseline artifact")
    if "#define SOURCE_OWNED_GENERATED_TABLE(" not in source or "#define SOURCE_OWNED_GENERATED_TABLE_POINT(" not in source:
        fail("active table header must retain macro-backed source-owned aliases")
    if LITERAL_TABLE_RE.search(source):
        fail("active table header must not contain obsolete direct literal StickPoint table bodies")
    aliases = [(symbol, int(index)) for symbol, index in ALIAS_RE.findall(source)]
    if len(aliases) != EXPECTED_TABLE_COUNT:
        fail(f"active table header must declare exactly {EXPECTED_TABLE_COUNT} macro-backed aliases")
    if [symbol for symbol, _index in aliases] != symbols:
        fail("active macro-backed table symbols must match canonical extraction order")
    if [index for _symbol, index in aliases] != list(range(EXPECTED_TABLE_COUNT)):
        fail("active macro-backed table indexes must be stable and complete")
    return symbols


def validate_historical_fixtures() -> None:
    contract = load_json_object(CONTRACT_FIXTURE)
    if contract.get("status") != "SUPERSEDED_HISTORICAL_DOCS_TOOLS_CONTRACT":
        fail("contract fixture must declare superseded historical status")
    if contract.get("current_table_shape") != {
        "table_count": EXPECTED_TABLE_COUNT,
        "points_per_table": EXPECTED_POINTS_PER_TABLE,
        "axes_per_point": EXPECTED_AXES_PER_POINT,
    }:
        fail("contract fixture must identify the current 28-table shape")
    if contract.get("historical_table_shape", {}).get("table_count") != 27:
        fail("contract fixture must preserve the historical 27-table shape")
    if contract.get("historical_fixtures_current_inputs") is not False:
        fail("historical fixtures must not be presented as current inputs")
    if contract.get("direct_literal_body_replacement_current_path") is not False:
        fail("direct literal-body replacement must not be presented as current")
    if contract.get("retired_generator_fail_closed") is not True:
        fail("contract fixture must require retired-generator fail-closed behavior")
    successors = contract.get("successor_references")
    if not isinstance(successors, list) or not all(item in successors for item in SUCCESSOR_REFERENCES[:-1]):
        fail("contract fixture is missing current successor references")

    input_fixture = load_json_object(INPUT_FIXTURE)
    if input_fixture.get("historical_status") != "HISTORICAL_SUPERSEDED_NOT_CURRENT_INPUT":
        fail("historical input fixture must be explicitly non-current")
    if input_fixture.get("table_shape", {}).get("table_count") != 27 or len(input_fixture.get("tables", [])) != 27:
        fail("historical input fixture must preserve its 27-table evidence shape")
    if any(len(table.get("points", [])) != EXPECTED_POINTS_PER_TABLE for table in input_fixture["tables"] if isinstance(table, dict)):
        fail("historical input fixture must preserve nine-point table evidence")
    if len({table.get("table_symbol") for table in input_fixture["tables"] if isinstance(table, dict)}) != 27:
        fail("historical input fixture must preserve unique table symbols")

    output = read_required(OUTPUT_FIXTURE)
    if not output.startswith("// HISTORICAL / SUPERSEDED:"):
        fail("historical output fixture must begin with an explicit supersession label")
    if len(HISTORICAL_LITERAL_TABLE_RE.findall(output)) != 27:
        fail("historical output fixture must preserve 27 literal-table bodies as evidence")


def validate_docs() -> None:
    contract_doc = read_required(CONTRACT_DOC)
    normalized_contract_doc = " ".join(contract_doc.replace("`", "").split()).lower()
    required_doc_phrases = (
        "Status: SUPERSEDED / HISTORICAL DOCS-TOOLS CONTRACT",
        "27 literal table bodies",
        "28 macro-backed source-owned tables",
        "historical evidence only",
        "not valid current generator inputs",
        "direct literal-body replacement is not the current production path",
        "does not establish hardware validity",
        "candidate isolation, build, and HARDWARE_PASS",
        *SUCCESSOR_REFERENCES,
    )
    for phrase in required_doc_phrases:
        if " ".join(phrase.replace("`", "").split()).lower() not in normalized_contract_doc:
            fail(f"supersession document missing required phrase: {phrase}")
    if "source_owned_table_replacement_generator_contract.md" not in read_required(README):
        fail(f"{rel(README)} must retain navigation to the superseded contract")
    for path in (README, CURRENT_STATE, ROADMAP, AGENT_CONTEXT):
        text = read_required(path)
        if "SUPERSEDED" not in text:
            fail(f"{rel(path)} must mark the literal-table contract superseded")


def validate_retired_generator() -> None:
    with tempfile.TemporaryDirectory(prefix="glyph-retired-literal-table-") as temp_dir:
        output = Path(temp_dir) / "must-not-exist.hpp"
        run = subprocess.run(
            ["python3", rel(GENERATOR), rel(INPUT_FIXTURE), str(output)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode == 0:
            fail("retired generator must fail with a nonzero exit status")
        if output.exists():
            fail("retired generator created output before failing")
        for phrase in ("SUPERSEDED", "source_owned_generator_modes.py", "source_authority_intake_workflow.md"):
            if phrase not in run.stderr:
                fail(f"retired generator stderr missing supersession guidance: {phrase}")


def main() -> int:
    branch = validate_branch()
    baseline = canonical_baseline()
    symbols = validate_current_representation(baseline)
    validate_historical_fixtures()
    validate_docs()
    validate_retired_generator()
    validate_changed_paths(changed_paths(branch))
    print("glyph_source_owned_table_replacement_generator_contract: PASS")
    print(f"- branch: {branch}")
    print(f"- canonical_table_count: {len(symbols)}")
    print(f"- final_table_symbol: {symbols[-1]}")
    print("- retired_generator: fail_closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
