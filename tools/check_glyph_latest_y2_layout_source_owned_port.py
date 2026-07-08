#!/usr/bin/env python3
"""Validate the latest Y2 layout source-owned port result and merged state."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BRANCH = "runtime-config-latest-y2-layout-source-owned-port"
RESULT_BRANCH = "runtime-config-latest-y2-layout-source-owned-port-hardware-result"
RECOVERY_BRANCH = "generator-source-owned-baseline-artifact-refresh"
DOCS_SURFACE_BRANCH = "docs-agent-surface-cleanup"
AGENT_FRAMEWORK_BRANCH = "docs-agent-framework-contracts"
MERGED_BRANCH = "configurator"
BASE_BRANCH = "configurator"
REFERENCE_BRANCH = "codex/update-custom-modifier-tables-y2"

ULTIMATE = REPO_ROOT / "src/modes/Ultimate.cpp"
TABLES_HPP = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
INTERPRETER_HPP = REPO_ROOT / "src/modes/UltimateRuntimeConfigInterpreter.hpp"
DOC = REPO_ROOT / "docs/runtime_config/latest_y2_layout_source_owned_port.md"
FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/latest_y2_layout_source_owned_port.json"
BUILD_REPORT = REPO_ROOT / "docs/runtime_config/latest_y2_layout_source_owned_port_build_report_2026-06-29.md"
BUILD_FIXTURE = REPO_ROOT / "docs/runtime_config/fixtures/latest_y2_layout_source_owned_port_build_report_2026-06-29.json"
HARDWARE_PLAN = REPO_ROOT / "docs/calibration/latest_y2_layout_source_owned_port_hardware_plan_2026-06-29.md"
HARDWARE_PLAN_FIXTURE = REPO_ROOT / "docs/calibration/fixtures/latest_y2_layout_source_owned_port_hardware_plan_2026-06-29.json"
README = REPO_ROOT / "docs/runtime_config/README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs/calibration/INDEX.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CHECKER_REL = "tools/check_glyph_latest_y2_layout_source_owned_port.py"

HARDWARE_RESULT = REPO_ROOT / "docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md"
HARDWARE_RESULT_FIXTURE = REPO_ROOT / "docs/calibration/fixtures/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.json"

ALLOWED_EXACT_CHANGED_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "docs/AGENT_CONTEXT.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    CHECKER_REL,
    "tools/check_glyph_agent_framework_docs.py",
    "tools/check_glyph_coordinate_native_runtime_plan.py",
    "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
    "tools/check_glyph_docs_agent_surface.py",
    "tools/check_glyph_docs_navigation.py",
}
IMPLEMENTATION_SOURCE_PATHS = {
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp",
    "src/modes/Ultimate.cpp",
}
ALLOWED_PREFIXES = ("docs/runtime_config/", "docs/calibration/", "docs/agent_framework/")
ALLOWED_EXISTING_CHECKERS = {
    "tools/check_glyph_latest_layout_y2_port_plan.py",
    "tools/check_glyph_source_owned_table_replacement_design.py",
    "tools/check_glyph_source_owned_table_replacement_generator_contract.py",
}

FORBIDDEN_CHANGED_PATH_RE = re.compile(
    r"^(?:HAL|hal|backend)(?:/|$)|(^|/)(?:config\.pb|storage|write|WebSerial|webserial|flash|flashing)(?:/|$)"
)
TABLE_RE = re.compile(
    r"constexpr\s+StickPoint\s+(?P<name>k[A-Za-z0-9]+Table)\s*\[\s*9\s*\]\s*=\s*\{(?P<body>.*?)\};",
    re.S,
)
POINT_RE = re.compile(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}")

EXPECTED_TILT3 = (
    (69, 82), (128, 83), (187, 82),
    (69, 128), (128, 128), (187, 128),
    (76, 169), (128, 179), (180, 169),
)
EXPECTED_Y2 = (
    (69, 78), (128, 78), (187, 78),
    (61, 128), (128, 128), (195, 128),
    (61, 164), (128, 174), (195, 164),
)
EXPECTED_FIXTURE_VALUES: dict[str, Any] = {
    "active_behavior_changed": True,
    "hardware_test_required_before_merge": True,
    "full_latest_layout_port": True,
    "partial_tilt3_only_port": False,
    "implements_y2_routing": True,
    "implements_y2_table_identity": True,
    "implements_lt3_y2_role": True,
    "removes_lt3_l_r_digital_behavior": True,
    "active_view_selection_changed": False,
    "runtime_config_view_replacement": False,
    "generated_active_wrapper_used": False,
    "candidate_view_published_active": False,
    "ram_backed_active_table_publication": False,
    "source_owned_table_content_replacement_wired": True,
    "reference_branch": REFERENCE_BRANCH,
    "port_plan": "docs/runtime_config/latest_layout_y2_port_plan.md",
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
    "y1_simple_modifier": True,
    "y1_rf_sublayers_removed": True,
    "y2_sublayer_modifier": True,
    "y1_sublayers_migrated_to_y2": True,
}
EXPECTED_HARDWARE_RESULT_VALUES: dict[str, Any] = {
    "schema_version": 1,
    "packet": "latest_y2_layout_source_owned_port_hardware_result",
    "status": "HARDWARE_PASS",
    "branch_under_test": IMPLEMENTATION_BRANCH,
    "result_branch": RESULT_BRANCH,
    "baseline_branch": BASE_BRANCH,
    "overall_result": "HARDWARE_PASS",
    "merge_approved": True,
    "user_report": "everything works, all usual tests pass, including Up+A and Down+A",
    "active_behavior_changed": True,
    "hardware_test_required_before_merge": True,
    "full_latest_layout_port": True,
    "rf5_forced_a_up_disconnect": False,
    "lt6_forced_a_down_disconnect": False,
    "usual_layout_tests_passed": True,
    "full_latest_y2_layout_passed": True,
    "y1_simple_y2_sublayer_migration_passed": True,
    "active_view_selection_changed": False,
    "runtime_config_view_replacement": False,
    "generated_active_wrapper_used": False,
    "candidate_view_published_active": False,
    "ram_backed_active_table_publication": False,
    "source_owned_table_content_replacement_wired": True,
    "runtime_loaded_config_implemented": False,
    "persistent_storage_implemented": False,
    "webserial_device_write_implemented": False,
    "backend_config_pb_write_path_implemented": False,
    "flashing_automation_implemented": False,
    "nunchuk_status": "NOT_TESTED",
    "root_cause_proven": False,
}
EXPECTED_CHANGED_SOURCE_FILES = [
    "src/modes/UltimateIdentityRuntimeTables.hpp",
    "src/modes/UltimateRuntimeConfigInterpreter.hpp",
    "src/modes/Ultimate.cpp",
]
HARDWARE_ROWS = [
    "BOOT-001",
    "RF5-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "TILT3-TABLE-001",
    "Y2-TABLE-001",
    "LT3-Y2-001",
    "NO-LR-BUTTON-001",
    "Y2-RF1-001",
    "Y2-RF2-001",
    "Y2-RF3-001",
    "Y2-RF4-001",
    "Y2-RT1-001",
    "Y2-RT1-RF4-TILT3-001",
    "Y1-SUBLAYER-REMOVED-001",
    "ACTIVE-VIEW-SELECTION-UNCHANGED-001",
    "RUNTIMECONFIGVIEW-UNCHANGED-001",
    "NO-PARSER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
    "Y1-SIMPLE-001",
    "Y1-RF-SUBLAYER-REMOVED-001",
    "Y2-SUBLAYER-MIGRATION-001",
]
EXPECTED_HARDWARE_RESULT_ROWS = {
    row_id: ("NOT_TESTED" if row_id == "NUNCHUK-001" else "PASS")
    for row_id in HARDWARE_ROWS
}


class CheckFailure(AssertionError):
    """Raised when the latest Y2 source-owned port drifts."""


def fail(message: str) -> None:
    raise CheckFailure(message)


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


def base_branch_for(branch: str) -> str:
    if branch == RESULT_BRANCH:
        return IMPLEMENTATION_BRANCH
    if branch in {DOCS_SURFACE_BRANCH, AGENT_FRAMEWORK_BRANCH, RECOVERY_BRANCH, "runtime-config-coordinate-native-profile-contract"}:
        return BASE_BRANCH
    if branch == MERGED_BRANCH:
        return MERGED_BRANCH
    fail(f"checker must run on {RESULT_BRANCH}, {DOCS_SURFACE_BRANCH}, {AGENT_FRAMEWORK_BRANCH}, {MERGED_BRANCH}, or runtime-config-coordinate-native-profile-contract, got {branch}")


def validate_branch() -> tuple[str, str]:
    branch = current_branch()
    if branch not in {RESULT_BRANCH, DOCS_SURFACE_BRANCH, AGENT_FRAMEWORK_BRANCH, MERGED_BRANCH, RECOVERY_BRANCH, "runtime-config-coordinate-native-profile-contract"}:
        fail(f"checker must run on {RESULT_BRANCH}, {DOCS_SURFACE_BRANCH}, {AGENT_FRAMEWORK_BRANCH}, or {MERGED_BRANCH}, got {branch}")
    base_branch = base_branch_for(branch)
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_branch, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{base_branch} must be an ancestor of HEAD")
    return branch, base_branch


def status_path(status_line: str) -> str:
    path = status_line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def changed_paths(branch: str, base_branch: str) -> set[str]:
    paths: set[str] = set()
    if branch in {RESULT_BRANCH, RECOVERY_BRANCH}:
        paths.update(git_lines(["diff", "--name-only", f"{base_branch}...HEAD"]))
    for line in git_lines(["status", "--short"], preserve_status=True):
        path = status_path(line)
        if path:
            paths.add(path)
    return paths


def validate_changed_paths(paths: set[str], branch: str) -> None:
    for path in sorted(paths):
        if FORBIDDEN_CHANGED_PATH_RE.search(path):
            fail(f"forbidden HAL/backend/config.pb/storage/write/WebSerial/flashing path changed: {path}")
        if path in IMPLEMENTATION_SOURCE_PATHS:
            if branch == RESULT_BRANCH:
                fail(f"result branch may not change firmware source relative to {IMPLEMENTATION_BRANCH}: {path}")
            continue
        if path.startswith("src/"):
            fail(f"out-of-scope source path changed: {path}")
        if path in ALLOWED_EXACT_CHANGED_PATHS:
            continue
        if path in ALLOWED_EXISTING_CHECKERS:
            continue
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        fail(f"out-of-scope changed path: {path}")


def strip_cpp_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def extract_function(text: str, name: str) -> str:
    match = re.search(r"\b" + re.escape(name) + r"\s*\([^)]*\)\s*\{", text)
    if not match:
        fail(f"missing function: {name}")
    index = match.end() - 1
    depth = 0
    for offset in range(index, len(text)):
        char = text[offset]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[index : offset + 1]
    fail(f"could not parse function body: {name}")


def parse_tables() -> dict[str, tuple[tuple[int, int], ...]]:
    source = read_required(TABLES_HPP)
    tables: dict[str, tuple[tuple[int, int], ...]] = {}
    for match in TABLE_RE.finditer(source):
        name = match.group("name")
        points = tuple((int(x), int(y)) for x, y in POINT_RE.findall(match.group("body")))
        if len(points) != 9:
            fail(f"{name} must have 9 points")
        if any(not (0 <= coord <= 255) for point in points for coord in point):
            fail(f"{name} contains out-of-byte-range coordinates")
        normalized = name[1:-5] if name.startswith("k") and name.endswith("Table") else name
        tables[normalized] = points
    return tables


@dataclass(frozen=True)
class Evaluation:
    table_id: str
    left_stick: tuple[int, int]
    digital_buttons: set[str]
    button_l: bool
    trigger_l: bool
    trigger_r: bool
    y2_active: bool
    force_up: bool


def direction_index(left: bool, right: bool, down: bool, up: bool) -> int:
    x = -1 if left and not right else 1 if right and not left else 0
    y = -1 if down and not up else 1 if up and not down else 0
    return ((y + 1) * 3) + (x + 1)


def evaluate(buttons: set[str], tables: dict[str, tuple[tuple[int, int], ...]]) -> Evaluation:
    def pressed(name: str) -> bool:
        return name in buttons

    cstick_any = any(pressed(name) for name in ("RT2", "RT3", "RT4", "RT5"))
    y2_anchor = pressed("LT3") and not pressed("LF4") and (pressed("RF3") or pressed("RF4"))
    force_up = pressed("RF5") or (y2_anchor and pressed("RF2")) or (pressed("LF4") and pressed("RF3"))
    horizontal = (1 if pressed("LF1") else 0) - (1 if pressed("LF3") else 0)
    left = horizontal < 0
    right = horizontal > 0
    up = pressed("LF2") or force_up
    down = (pressed("LF5") or pressed("LT6")) and not force_up

    y2_sublayer = pressed("LT3") and not pressed("LF4") and (pressed("RF3") or pressed("RF4"))
    base_rf3_x = pressed("RF3") and not pressed("LT3") and not pressed("LF4")
    rf9_base_rf3_x = pressed("RF9") and base_rf3_x
    rf4_suppressed_by_rf9 = rf9_base_rf3_x and pressed("RF4")
    rt1_rf4 = pressed("RT1") and pressed("RF4") and not rf4_suppressed_by_rf9
    rf4_suppressed_by_cstick = pressed("RF4") and cstick_any and not rt1_rf4
    rf4_available = pressed("RF4") and not rf4_suppressed_by_cstick and not rf4_suppressed_by_rf9
    y2_rf3 = y2_sublayer and pressed("RF3")
    y2_rf4 = pressed("LT3") and not pressed("LF4") and rf4_available and not rt1_rf4
    lf4_rf2_deactivates_rf4 = pressed("LF4") and pressed("RF2")
    tilt1 = rf4_available and (not pressed("LT3") or pressed("LF4")) and not pressed("RT1") and not lf4_rf2_deactivates_rf4
    tilt2 = pressed("RT1") and not pressed("RF4")
    tilt3 = rt1_rf4
    y1_active = pressed("LT2") and not pressed("LF4")
    y2_active = pressed("LT3") and not pressed("LF4") and not y2_sublayer
    layer_normal = y2_rf3
    layer_flipper = y2_rf4

    base_rf1_a = pressed("RF1") and not y2_sublayer
    base_rf2_b = pressed("RF2") and not pressed("LF4") and not y2_sublayer
    y2_rf1_x = y2_sublayer and pressed("RF1") and not cstick_any
    lf4_rf2_x = pressed("LF4") and pressed("RF2") and not cstick_any
    digital: set[str] = set()
    if base_rf1_a or pressed("LT6") or pressed("RF5"):
        digital.add("A")
    if base_rf2_b or pressed("LF4") or pressed("RF7") or (pressed("LT3") and not pressed("LF4") and pressed("RF3")):
        digital.add("B")
    if (base_rf3_x and not (rf9_base_rf3_x and not cstick_any)) or y2_rf1_x or lf4_rf2_x:
        digital.add("X")
    if pressed("RF10"):
        digital.add("Y")
    if pressed("LT1"):
        digital.add("L")
    if pressed("RF6"):
        digital.add("Z")
    if pressed("RF16"):
        digital.add("R")

    table_id = select_table(
        y1_active=y1_active,
        y2_active=y2_active,
        layer_normal=layer_normal,
        layer_flipper=layer_flipper,
        tilt1=tilt1,
        tilt2=tilt2,
        tilt3=tilt3,
    )
    rf4_rf2_minus41 = rf4_available and pressed("RF2") and not pressed("LT3") and not pressed("LF4") and not rt1_rf4
    if rf4_rf2_minus41:
        table_id = "Tilt1Minus41"

    point = tables[table_id][direction_index(left, right, down, up)]
    if pressed("LT6") or pressed("RF5"):
        point = tables["Default"][7 if (pressed("RF5") or force_up) else 1]

    return Evaluation(
        table_id=table_id,
        left_stick=point,
        digital_buttons=digital,
        button_l=pressed("LT1"),
        trigger_l=pressed("LT1"),
        trigger_r=pressed("RF16"),
        y2_active=y2_active,
        force_up=force_up,
    )


def select_table(
    *,
    y1_active: bool,
    y2_active: bool,
    layer_normal: bool,
    layer_flipper: bool,
    tilt1: bool,
    tilt2: bool,
    tilt3: bool,
) -> str:
    if tilt1 and tilt2:
        return "RT1RF4Custom"
    layer_normal_effective = layer_normal and not layer_flipper
    rt_rf_effective = layer_normal_effective or layer_flipper or tilt1 or tilt2 or tilt3
    y2_effective = y2_active and not rt_rf_effective
    active = [
        ("Y1", y1_active),
        ("Y2", y2_effective),
        ("LayerNormalX", layer_normal_effective),
        ("LayerFlipper", layer_flipper),
        ("Tilt3", tilt3),
        ("Tilt1", tilt1 and not tilt3),
        ("Tilt2", tilt2 and not tilt1 and not tilt3),
    ]
    selected = [name for name, is_active in active if is_active]
    return selected[0] if len(selected) == 1 else "Default"


def assert_eval(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def validate_runtime_behavior(tables: dict[str, tuple[tuple[int, int], ...]]) -> None:
    def ev(*buttons: str) -> Evaluation:
        return evaluate(set(buttons), tables)

    assert_eval("RF5 forced A+Up buttons", ev("RF5").digital_buttons, {"A"})
    assert_eval("RF5 forced A+Up point", ev("RF5").left_stick, (128, 205))
    assert_eval("LT6 forced A+Down buttons", ev("LT6").digital_buttons, {"A"})
    assert_eval("LT6 forced A+Down point", ev("LT6").left_stick, (128, 51))

    assert_eval("LT3 table", ev("LT3").table_id, "Y2")
    assert_eval("LT3 y2 role", ev("LT3").y2_active, True)
    assert_eval("LT3 digital buttons", ev("LT3").digital_buttons, set())
    assert_eval("LT3 buttonL", ev("LT3").button_l, False)
    assert_eval("LT3 triggerL", ev("LT3").trigger_l, False)
    assert_eval("LT3 triggerR", ev("LT3").trigger_r, False)

    assert_eval("Y2+RF1 alone keeps base A", ev("LT3", "RF1").digital_buttons, {"A"})
    assert_eval("Y2+RF1 alone keeps Y2", ev("LT3", "RF1").table_id, "Y2")
    assert_eval("Y2+RF1+RF4 emits X", ev("LT3", "RF1", "RF4").digital_buttons, {"X"})
    assert_eval("Y1+RF1 no old X sublayer", ev("LT2", "RF1").digital_buttons, {"A"})

    assert_eval("Y2+RF2 alone keeps base B", ev("LT3", "RF2").digital_buttons, {"B"})
    assert_eval("Y2+RF2 alone no force up", ev("LT3", "RF2").force_up, False)
    assert_eval("Y2+RF2+RF4 forces up without base B", ev("LT3", "RF2", "RF4").digital_buttons, set())
    assert_eval("Y2+RF2+RF4 forced-up point", ev("LT3", "RF2", "RF4").left_stick, (128, 205))
    assert_eval("Y1+RF2 no force up", ev("LT2", "RF2").force_up, False)
    assert_eval("Y1+RF2 keeps base B", ev("LT2", "RF2").digital_buttons, {"B"})

    assert_eval("Y2+RF3 emits B", ev("LT3", "RF3", "LF1").digital_buttons, {"B"})
    assert_eval("Y2+RF3 LayerNormalX", ev("LT3", "RF3", "LF1").table_id, "LayerNormalX")
    assert_eval("Y1+RF3 no old B sublayer", ev("LT2", "RF3", "LF1").digital_buttons, {"X"})
    assert_eval("Y1+RF3 simple Y1 table", ev("LT2", "RF3", "LF1").table_id, "Y1")

    assert_eval("Y2+RF4 LayerFlipper", ev("LT3", "RF4", "LF1").table_id, "LayerFlipper")
    assert_eval("Y1+RF4 no old flipper", ev("LT2", "RF4", "LF1").table_id, "Default")

    assert_eval("Y2+RT1 selects Tilt2", ev("LT3", "RT1", "LF1").table_id, "Tilt2")
    assert_eval("Y2+RT1+RF4 selects Tilt3", ev("LT3", "RT1", "RF4", "LF1").table_id, "Tilt3")
    assert_eval("Y2+RT1+RF4 Tilt3 point", ev("LT3", "RT1", "RF4", "LF1").left_stick, (187, 128))
    assert_eval("Y2+RF4 priority above Y2", ev("LT3", "RF4", "LF1").left_stick, (87, 128))


def validate_source() -> None:
    ultimate = read_required(ULTIMATE)
    interpreter = read_required(INTERPRETER_HPP)
    tables = parse_tables()
    if tables.get("Tilt3") != EXPECTED_TILT3:
        fail("kTilt3Table does not match required latest values")
    if tables.get("Y2") != EXPECTED_Y2:
        fail("kY2Table does not match required latest values")

    required_interpreter_tokens = (
        "constexpr size_t kRuntimeTableCount = 28;",
        "RuntimeTableId::Y2",
        '"kY2Table"',
        "{RuntimeTableId::Y2, \"kY2Table\", kY2Table, kRuntimeTablePointCount}",
        "kSourceOwnedCurrentBaselineRuntimeTables[kRuntimeTableCount]",
    )
    for token in required_interpreter_tokens:
        if token not in interpreter:
            fail(f"interpreter missing Y2 identity/order/count token: {token}")

    get_state = strip_cpp_comments(extract_function(ultimate, "GetActiveRuntimeConfigState"))
    if "&kSourceOwnedCurrentBaselineRuntimeConfig" not in get_state:
        fail("GetActiveRuntimeConfigState must publish &kSourceOwnedCurrentBaselineRuntimeConfig")
    for forbidden in ("candidate.view", "active_storage.view", "GeneratedRuntimeConfig", "RuntimeConfigActiveStorageStatus::SourceOwnedEquivalent"):
        if forbidden in get_state:
            fail(f"GetActiveRuntimeConfigState must not publish {forbidden}")

    resolve = strip_cpp_comments(extract_function(ultimate, "ResolveActiveRuntimeConfig"))
    if "return *GetActiveRuntimeConfigState().active_view;" not in resolve:
        fail("ResolveActiveRuntimeConfig must dereference GetActiveRuntimeConfigState().active_view")

    update_analog = strip_cpp_comments(extract_function(ultimate, "Ultimate::UpdateAnalogOutputs"))
    if "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();" not in update_analog:
        fail("UpdateAnalogOutputs must resolve active runtime config through ResolveActiveRuntimeConfig()")

    forbidden_source_tokens = (
        'GeneratedRuntimeConfigBaselineActiveView.current.hpp',
        'candidate.view,',
        '&candidate.view',
        '&active_storage.view',
        'return candidate.view',
        'return active_storage.view',
    )
    for token in forbidden_source_tokens:
        if token in ultimate:
            fail(f"forbidden active-publication token present: {token}")
    generated_active_wrapper = REPO_ROOT / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaselineActiveView.current.hpp"
    if generated_active_wrapper.exists():
        fail("generated active RuntimeConfigView wrapper exists")

    old_y1_tokens = (
        "lt2_sublayer_active",
        "lt2_rf1_x_active",
        "lt2_rf2_force_up_active",
        "lt2_rf3_active",
        "lt2_rf4_active",
        "y1_layer_normal_x_special_active",
        "y1_layer_flipper_special_active",
        "y1_tilt1_special_active",
        "outputs.buttonL = inputs.lt1 || inputs.lt3",
        "outputs.triggerLDigital = inputs.lt1 || inputs.lt3",
        "outputs.triggerRDigital = inputs.rf16 || inputs.lt3",
    )
    for token in old_y1_tokens:
        if token in ultimate:
            fail(f"old Y1/LT3 sublayer or L/R behavior token remains: {token}")

    required_y2_tokens = (
        "outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;",
        "const bool down_a_active = inputs.lt6;",
        "const bool up_a_active = inputs.rf5;",
        "state.y1_active = inputs.lt2 && !inputs.lf4;",
        "state.y2_active = inputs.lt3 && !inputs.lf4 && !y2_sublayer_active;",
        "const bool y2_sublayer_active = inputs.lt3 && !inputs.lf4 && (inputs.rf3 || inputs.rf4);",
        "const bool y2_rf34_sublayer_anchor_active = inputs.lt3 && !inputs.lf4 && (inputs.rf3 || inputs.rf4);",
        "state.layer_rf3_normal_x_active = y2_rf3_active;",
        "state.rf4_layer_flipper_active = y2_rf4_active;",
        "state.tilt3_effective = rt1_rf4_custom_active;",
        "outputs.buttonL = inputs.lt1;",
        "outputs.triggerLDigital = inputs.lt1;",
        "outputs.triggerRDigital = inputs.rf16;",
    )
    for token in required_y2_tokens:
        if token not in ultimate:
            fail(f"required Y2/LT3 routing token missing: {token}")

    validate_runtime_behavior(tables)


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).lower()


def require_phrases(label: str, text: str, phrases: list[str] | tuple[str, ...]) -> None:
    normalized = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized]
    if missing:
        fail(f"{label} missing required phrases: " + ", ".join(missing))


def validate_fixture(payload: dict[str, Any]) -> None:
    if payload.get("packet") != "latest_y2_layout_source_owned_port":
        fail("fixture packet must be latest_y2_layout_source_owned_port")
    if payload.get("branch") != IMPLEMENTATION_BRANCH:
        fail(f"fixture branch must be {IMPLEMENTATION_BRANCH}")
    if payload.get("base_branch") != BASE_BRANCH:
        fail(f"fixture base_branch must be {BASE_BRANCH}")
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        if payload.get(key) != expected:
            fail(f"fixture {key} must be {expected!r}, got {payload.get(key)!r}")
    if payload.get("changed_source_files") != EXPECTED_CHANGED_SOURCE_FILES:
        fail("fixture changed_source_files must match the allowed firmware source files")
    expected_tables = {
        "Tilt3": {str(index + 1): list(point) for index, point in enumerate(EXPECTED_TILT3)},
        "Y2": {str(index + 1): list(point) for index, point in enumerate(EXPECTED_Y2)},
    }
    if payload.get("required_table_values") != expected_tables:
        fail("fixture required_table_values do not match Tilt3/Y2 requirements")


def validate_build_fixture(payload: dict[str, Any]) -> None:
    if payload.get("packet") != "latest_y2_layout_source_owned_port_build_report":
        fail("build fixture packet mismatch")
    expected = {
        "canonical_command": "pio run -e glyph_mk6",
        "artifact_hashes_are_rebuild_stable": False,
        "artifact_hashes_are_checker_gate": False,
        "nunchuk_status": "NOT_TESTED",
        "root_cause_proven": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"build fixture {key} must be {value!r}")
    hashes = payload.get("artifact_hashes")
    if not isinstance(hashes, list):
        fail("build fixture artifact_hashes must be a list")


def validate_hardware_plan(payload: dict[str, Any]) -> None:
    if payload.get("packet") != "latest_y2_layout_source_owned_port_hardware_plan":
        fail("hardware plan fixture packet mismatch")
    if payload.get("hardware_test_required_before_merge") is not True:
        fail("hardware plan must require hardware test before merge")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail("hardware plan rows must be a list")
    row_by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    if set(row_by_id) != set(HARDWARE_ROWS):
        fail("hardware plan row IDs do not match the required row set")
    for row_id in HARDWARE_ROWS:
        if row_by_id[row_id].get("status") != "NOT_TESTED":
            fail(f"hardware plan row {row_id} must be NOT_TESTED")


def validate_hardware_result(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_HARDWARE_RESULT_VALUES.items():
        if payload.get(key) != expected:
            fail(f"hardware result fixture {key} must be {expected!r}, got {payload.get(key)!r}")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail("hardware result fixture rows must be a list")
    row_by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    if set(row_by_id) != set(EXPECTED_HARDWARE_RESULT_ROWS):
        fail("hardware result fixture row IDs do not match the required row set")
    for row_id, expected_status in EXPECTED_HARDWARE_RESULT_ROWS.items():
        if row_by_id[row_id].get("status") != expected_status:
            fail(f"hardware result row {row_id} must be {expected_status}")


def validate_docs(branch: str) -> None:
    doc_text = read_required(DOC)
    build_text = read_required(BUILD_REPORT)
    hardware_text = read_required(HARDWARE_PLAN)
    hardware_result_text = read_required(HARDWARE_RESULT)
    readme_text = read_required(README)
    index_text = read_required(CALIBRATION_INDEX)
    current_text = read_required(CURRENT_STATE)
    roadmap_text = read_required(ROADMAP)

    common_phrases = (
        IMPLEMENTATION_BRANCH,
        REFERENCE_BRANCH,
        "RuntimeConfigView replacement is not used",
        "active view selection unchanged",
        "candidate.view is not active",
        "RAM-backed active table publication is not used",
        "Nunchuk remains NOT_TESTED",
        "root cause remains unproven",
    )
    require_phrases(rel(DOC), doc_text, common_phrases)
    require_phrases(
        rel(DOC),
        doc_text,
        (
            RESULT_BRANCH,
            "HARDWARE_PASS",
            "merge approved",
            "everything works, all usual tests pass, including Up+A and Down+A",
            "Source-owned table/routing source path passed hardware for this layout",
        ),
    )
    require_phrases(rel(BUILD_REPORT), build_text, ("pio run -e glyph_mk6", "artifact hashes are local observations only"))
    require_phrases(rel(HARDWARE_PLAN), hardware_text, HARDWARE_ROWS)
    require_phrases(
        rel(HARDWARE_RESULT),
        hardware_result_text,
        (
            "HARDWARE_PASS",
            IMPLEMENTATION_BRANCH,
            RESULT_BRANCH,
            "merge-approved after HARDWARE_PASS",
            "RuntimeConfigView replacement is not used",
            "Source-owned table/routing source path passed hardware for this layout",
            "Nunchuk remains NOT_TESTED",
        ),
    )
    require_phrases(
        rel(README),
        readme_text,
        (
            "latest_y2_layout_source_owned_port.md",
            "latest_y2_layout_source_owned_port_build_report_2026-06-29.md",
            "latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md",
            "accepts the hardware-result branch and configurator after merge",
        ),
    )
    require_phrases(
        rel(CALIBRATION_INDEX),
        index_text,
        (
            "latest_y2_layout_source_owned_port_hardware_plan_2026-06-29.md",
            "latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md",
            "merge-approved",
            "Nunchuk remains NOT_TESTED",
        ),
    )
    require_phrases(
        rel(CURRENT_STATE),
        current_text,
        (
            IMPLEMENTATION_BRANCH,
            RESULT_BRANCH,
            "merge-approved after hardware PASS",
            "generated active wrapper is not used",
            "source-owned table/routing source path passed hardware for this layout",
        ),
    )
    require_phrases(
        rel(ROADMAP),
        roadmap_text,
        (
            RESULT_BRANCH,
            "merge-approved after hardware PASS",
            "generated active wrapper",
            "everything works, all usual tests pass, including Up+A and Down+A",
        ),
    )

    validate_fixture(load_json_object(FIXTURE))
    validate_build_fixture(load_json_object(BUILD_FIXTURE))
    validate_hardware_plan(load_json_object(HARDWARE_PLAN_FIXTURE))
    validate_hardware_result(load_json_object(HARDWARE_RESULT_FIXTURE))
    if branch == MERGED_BRANCH and (not HARDWARE_RESULT.exists() or not HARDWARE_RESULT_FIXTURE.exists()):
        fail("configurator merge requires preserved HARDWARE_PASS result for this active behavior change")


def main() -> int:
    print("glyph_latest_y2_layout_source_owned_port")
    try:
        branch, base_branch = validate_branch()
        if branch == RESULT_BRANCH:
            validate_changed_paths(changed_paths(branch, base_branch), branch)
        validate_source()
        validate_docs(branch)
    except CheckFailure as exc:
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print(f"branch={branch}")
    print(f"base_branch={base_branch}")
    print("active_behavior_changed=true")
    print("hardware_test_required_before_merge=true")
    print("merge_approved=true")
    print("active_view_selection_changed=false")
    print("runtime_config_view_replacement=false")
    print("nunchuk_status=NOT_TESTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
