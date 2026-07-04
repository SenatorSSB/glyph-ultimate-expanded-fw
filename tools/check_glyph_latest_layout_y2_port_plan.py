#!/usr/bin/env python3
"""Validate the latest Y2/Tilt3 layout port-plan packet."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "runtime-config-latest-layout-y2-port-plan"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
REFERENCE_BRANCH = "codex/update-custom-modifier-tables-y2"

PLAN_DOC = REPO_ROOT / "docs/runtime_config/latest_layout_y2_port_plan.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/latest_layout_y2_port_plan.json"
README = REPO_ROOT / "docs/runtime_config/README.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_latest_layout_y2_port_plan.py"

ALLOWED_EXACT_CHANGED_PATHS = {
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
}
ALLOWED_PREFIXES = ("docs/runtime_config/",)
ALLOWED_EXISTING_SOURCE_OWNED_TABLE_CHECKERS = {
    "tools/check_glyph_source_owned_table_replacement_design.py",
    "tools/check_glyph_source_owned_table_replacement_generator_contract.py",
}

FORBIDDEN_SOURCE_PATH_RE = re.compile(r"^(?:src|include|lib|HAL|hal|backend)(?:/|$)")
FORBIDDEN_SPECIAL_PATH_RE = re.compile(
    r"(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)

EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "reference_branch": REFERENCE_BRANCH,
    "active_behavior_changed": False,
    "hardware_test_required_before_merge": False,
    "docs_checker_only": True,
    "direct_merge_reference_branch_allowed": False,
    "table_content_replacement_path_supported_by_hardware_pass": True,
    "routing_role_changes_require_separate_hardware_gate": True,
    "runtime_config_view_replacement_allowed": False,
    "active_view_selection_change_allowed": False,
    "generated_active_wrapper_allowed": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}

EXPECTED_TABLES: dict[str, dict[str, list[int]]] = {
    "Tilt3": {
        "1": [69, 82],
        "2": [128, 83],
        "3": [187, 82],
        "4": [69, 128],
        "5": [128, 128],
        "6": [187, 128],
        "7": [76, 169],
        "8": [128, 179],
        "9": [180, 169],
    },
    "Y2": {
        "1": [69, 78],
        "2": [128, 78],
        "3": [187, 78],
        "4": [61, 128],
        "5": [128, 128],
        "6": [195, 128],
        "7": [61, 164],
        "8": [128, 174],
        "9": [195, 164],
    },
}

EXPECTED_ROUTING_FACTS = [
    "LT3 selects Y2 and emits no L/R digital.",
    "Y2+RF1 alone keeps base A.",
    "Y2+RF1+RF4 emits X.",
    "Y1+RF1 no longer emits X sublayer.",
    "Y2+RF2 alone keeps base B.",
    "Y2+RF2 alone does not force up.",
    "Y2+RF2+RF4 forces up without base B.",
    "Y1+RF2 no longer forces up.",
    "Y2+RF3 emits B and uses LayerNormalX where applicable.",
    "Y1+RF3 no longer emits B sublayer.",
    "Y2+RF4 uses LayerFlipper where applicable.",
    "Y1+RF4 no longer flipper sublayer.",
    "Y2+RT1 selects Tilt2.",
    "Y2+RT1+RF4 selects Tilt3.",
    "Y2 priority remains below RT/RF modifiers.",
]

REQUIRED_PLAN_PHRASES = (
    "This branch does not implement the latest layout.",
    "This branch does not validate hardware for the latest layout.",
    "This branch only defines the port plan.",
    "A. Table-content-only update to current configurator.",
    "B. Routing/role update if required.",
    "Any routing/role update must be hardware-gated because it changes Ultimate.cpp and interpreter behavior.",
    "Do not directly port those generated artifacts unless a docs/checker branch needs them.",
    "Do not reintroduce generated active wrappers, RuntimeConfigView replacement, or generated active-view selection paths.",
    "RuntimeConfigView replacement is not allowed.",
    "Active-view selection change is not allowed.",
    "Generated active wrapper is not allowed.",
    "Nunchuk remains NOT_TESTED.",
    "Root cause for the failed active-publication diagnostics is not proven.",
)

REQUIRED_INDEX_PHRASES = (
    "latest_layout_y2_port_plan.md",
    "latest_layout_y2_port_plan.json",
    "check_glyph_latest_layout_y2_port_plan.py",
    "This branch does not implement the latest layout",
    "Nunchuk remains NOT_TESTED",
)


class LatestLayoutY2PortPlanError(AssertionError):
    """Raised when the latest layout port plan drifts."""


def fail(message: str) -> None:
    raise LatestLayoutY2PortPlanError(message)


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
        if path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str]) -> None:
    for path in sorted(paths):
        if FORBIDDEN_SOURCE_PATH_RE.search(path):
            fail(f"firmware/source path changed on docs/checker-only branch: {path}")
        if FORBIDDEN_SPECIAL_PATH_RE.search(path):
            fail(f"storage/write/WebSerial/flashing/config.pb path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if path in ALLOWED_EXISTING_SOURCE_OWNED_TABLE_CHECKERS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).lower()


def require_phrases(label: str, text: str, phrases: tuple[str, ...] | list[str]) -> None:
    normalized_text = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized_text]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("packet") != "latest_layout_y2_port_plan":
        fail("fixture packet must be latest_layout_y2_port_plan")
    if fixture.get("branch") != EXPECTED_BRANCH:
        fail(f"fixture branch must be {EXPECTED_BRANCH}")
    if fixture.get("base_branch") != BASE_BRANCH:
        fail(f"fixture base_branch must be {BASE_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = fixture.get(key)
        if actual != expected:
            fail(f"fixture {key} must be {expected!r}, got {actual!r}")

    table_values = fixture.get("latest_intended_table_values")
    if table_values != EXPECTED_TABLES:
        fail("fixture latest_intended_table_values do not match the required Tilt3/Y2 values")

    routing_facts = fixture.get("intended_routing_role_facts")
    if routing_facts != EXPECTED_ROUTING_FACTS:
        fail("fixture intended_routing_role_facts do not match the reference checker facts")

    classification = fixture.get("classification")
    if not isinstance(classification, dict):
        fail("fixture classification must be an object")
    table_only = classification.get("table_content_only_changes")
    if not isinstance(table_only, list) or len(table_only) != 1:
        fail("fixture classification.table_content_only_changes must contain only the Tilt3 table-content change")
    tilt3 = table_only[0]
    if not isinstance(tilt3, dict) or tilt3.get("symbol") != "kTilt3Table":
        fail("fixture table-content-only classification must identify kTilt3Table")
    if tilt3.get("candidate_for_source_owned_table_content_replacement") is not True:
        fail("kTilt3Table must be marked as source-owned table-content replacement candidate")

    routing_changes = classification.get("routing_role_evaluator_changes")
    if not isinstance(routing_changes, list):
        fail("fixture routing_role_evaluator_changes must be a list")
    for required in ("src/modes/Ultimate.cpp", "src/modes/UltimateRuntimeConfigInterpreter.hpp"):
        if required not in routing_changes:
            fail(f"fixture routing_role_evaluator_changes missing {required}")


def validate_docs() -> None:
    plan = read_required(PLAN_DOC)
    readme = read_required(README)
    current_state = read_required(CURRENT_STATE)
    roadmap = read_required(ROADMAP)

    require_phrases(rel(PLAN_DOC), plan, REQUIRED_PLAN_PHRASES)
    require_phrases(rel(PLAN_DOC), plan, EXPECTED_ROUTING_FACTS)
    for table_name, table in EXPECTED_TABLES.items():
        for direction, point in table.items():
            require_phrases(rel(PLAN_DOC), plan, (f"| {direction} | {point[0]} | {point[1]} |",))
        require_phrases(rel(PLAN_DOC), plan, (table_name,))

    for path, text in (
        (README, readme),
        (CURRENT_STATE, current_state),
        (ROADMAP, roadmap),
    ):
        require_phrases(rel(path), text, REQUIRED_INDEX_PHRASES)


def main() -> int:
    branch = validate_branch()
    fixture = load_json_object(FIXTURE)
    validate_fixture(fixture)
    validate_changed_paths(changed_paths(branch))
    validate_docs()
    print("glyph_latest_layout_y2_port_plan: PASS")
    print(f"- branch: {branch}")
    print(f"- reference_branch: {REFERENCE_BRANCH}")
    print(f"- fixture: {rel(FIXTURE)}")
    print(f"- plan: {rel(PLAN_DOC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
