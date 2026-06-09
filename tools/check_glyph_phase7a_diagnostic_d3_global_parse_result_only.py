#!/usr/bin/env python3
"""Validate Phase 7A Diagnostic D3 global-parse-result-only guardrails."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d3-global-parse-result-only"
BASE_BRANCH = "phase7a-diagnostic-d2b-retained-payload-bytes"
BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_PAYLOAD_SHA = "0f668127c270fb7be382677f68a528d1e1d18829254bb7f16fa901e30414bc32"
EXPECTED_PAYLOAD_SIZE = 530

ULTIMATE_CPP = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
PARSER_HPP = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"
HEADER_HPP = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayload.hpp"
ANCHOR_CPP = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayloadAnchor.cpp"
INTERPRETER_HPP = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigInterpreter.hpp"
IDENTITY_HPP = REPO_ROOT / "src" / "modes" / "UltimateIdentityRuntimeTables.hpp"

DOC_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d3_global_parse_result_only.md"
REPORT_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md"
REPORT_JSON = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.json"
PLAN_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.md"
PLAN_JSON = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.json"
RUNTIME_README = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
D2B_RESULT_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.md"

PAYLOAD_FIXTURE = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_valid_baseline_runtime_config_payload.bin"

EXPECTED_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/runtime_config/README.md",
    "docs/runtime_config/phase7a_diagnostic_d3_global_parse_result_only.md",
    "docs/runtime_config/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md",
    "docs/runtime_config/fixtures/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.json",
    "docs/calibration/INDEX.md",
    "docs/calibration/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.md",
    "docs/calibration/fixtures/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.json",
    "tools/check_glyph_phase7a_diagnostic_d3_global_parse_result_only.py",
}

REQUIRED_ROWS = {
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "UNRELATED-BUTTONS-001",
    "MODIFIERS-001",
    "PAYLOAD-001",
    "GLOBAL-PARSE-001",
    "PARSER-CALL-001",
    "NO-RESOLVER-001",
    "NO-RUNTIME-ROUTING-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}

FORBIDDEN_PATTERNS = (
    r"\bResolveActiveRuntimeConfig\s*\(",
    r"\bPersistence\b",
    r"\bLittleFS\b",
    r"\bEEPROM\b",
    r"\bconfig\.bin\b",
    r"\bWebSerial\b",
    r"\bdevice\s+write\b",
    r"\bruntime[-_ ]config\s+command\b",
    r"\breboot_bootloader\b",
    r"\bflash_uf2\b",
    r"\bfirmware flashing automation\b",
)


class Phase7AD3Error(ValueError):
    """Raised when D3 guardrails drift."""


def fail(message: str) -> None:
    raise Phase7AD3Error(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
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


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def implementation_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))


def parse_status_path(status_line: str) -> str:
    parts = status_line.strip().split(None, 1)
    if len(parts) != 2:
        return ""
    path = parts[1]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip()


def changed_paths() -> set[str]:
    diff_paths = set(run_git(["diff", "--name-only", f"{BASE_BRANCH}...HEAD"]).stdout.splitlines())
    for line in run_git(["status", "--short"]).stdout.splitlines():
        path = parse_status_path(line)
        if path:
            diff_paths.add(path)
    return {path for path in diff_paths if path}


def git_show_text(ref: str, path: Path) -> str:
    completed = run_git(["show", f"{ref}:{rel(path)}"])
    return completed.stdout


def extract_function(text: str, name: str) -> str:
    match = re.search(rf"void\s+Ultimate::{re.escape(name)}\s*\([^)]*\)\s*\{{", text)
    if not match:
        fail(f"missing Ultimate::{name}")
    start = match.start()
    brace = text.find("{", match.end() - 1)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    fail(f"could not parse Ultimate::{name}")


def validate_branch() -> None:
    branch = run_git(["branch", "--show-current"]).stdout.strip()
    if branch != BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {BRANCH!r}")
    if run_git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False).returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")


def validate_changed_paths() -> None:
    paths = changed_paths()
    missing = EXPECTED_CHANGED_PATHS - paths
    if missing:
        fail("missing expected changed paths: " + ", ".join(sorted(missing)))
    extra = paths - EXPECTED_CHANGED_PATHS
    if extra:
        fail("changed paths outside D3 scope: " + ", ".join(sorted(extra)))


def validate_payload_retained() -> None:
    fixture = PAYLOAD_FIXTURE.read_bytes()
    if len(fixture) != EXPECTED_PAYLOAD_SIZE:
        fail("payload fixture size mismatch")
    if hashlib.sha256(fixture).hexdigest() != EXPECTED_PAYLOAD_SHA:
        fail("payload fixture sha mismatch")

    header = read_required(HEADER_HPP)
    if "kPhase7ACompiledPayloadSize = 530" not in header:
        fail("compiled payload header no longer declares 530-byte payload")
    if EXPECTED_PAYLOAD_SHA not in header:
        fail("compiled payload header no longer records expected SHA")

    anchor = read_required(ANCHOR_CPP)
    for phrase in (
        "kPhase7AD2BRetainedPayloadAnchor",
        ".incbin",
        "phase7a_valid_baseline_runtime_config_payload.bin",
        ".size kPhase7AD2BRetainedPayloadAnchor, 530",
    ):
        require_phrase(anchor, phrase, "D2B retained payload anchor")


def validate_source_guardrails() -> None:
    ultimate = read_required(ULTIMATE_CPP)
    base_ultimate = git_show_text(BASE_BRANCH, ULTIMATE_CPP)
    impl = implementation_text(ultimate)

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, impl, flags=re.IGNORECASE):
            fail(f"forbidden source pattern present in Ultimate.cpp: {pattern}")

    if "UltimateRuntimeConfigCompiledPayload.hpp" in ultimate:
        fail("D3 must not include compiled payload header in Ultimate.cpp")
    require_phrase(ultimate, "extern \"C\" const uint8_t", "Ultimate.cpp")
    require_phrase(ultimate, "kPhase7AD2BRetainedPayloadAnchor", "Ultimate.cpp")
    require_phrase(ultimate, "kPhase7AD3GlobalParseResult", "Ultimate.cpp")
    require_phrase(ultimate, "__attribute__((used))", "Ultimate.cpp")

    parse_calls = re.findall(r"UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload\s*\(", impl)
    if len(parse_calls) != 1:
        fail(f"D3 must contain exactly one parser call in Ultimate.cpp, found {len(parse_calls)}")

    global_parse_pattern = re.compile(
        r"const\s+UltimateRuntimeConfigParser::ParseResult\s+"
        r"kPhase7AD3GlobalParseResult\s+__attribute__\(\(used\)\)\s*=\s*"
        r"UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload\s*\(\s*"
        r"kPhase7AD2BRetainedPayloadAnchor\s*,\s*"
        r"UltimateRuntimeConfigParser::kPayloadSize\s*\)",
        flags=re.S,
    )
    if not global_parse_pattern.search(impl):
        fail("global/static parse result initialization path not found")

    current_analog = extract_function(ultimate, "UpdateAnalogOutputs")
    base_analog = extract_function(base_ultimate, "UpdateAnalogOutputs")
    if current_analog != base_analog:
        fail("UpdateAnalogOutputs changed relative to D2B")

    current_digital = extract_function(ultimate, "UpdateDigitalOutputs")
    base_digital = extract_function(base_ultimate, "UpdateDigitalOutputs")
    if current_digital != base_digital:
        fail("UpdateDigitalOutputs changed relative to D2B")

    rf_patterns = (
        r"state\.force_up_active\s*=.*inputs\.rf5",
        r"up_a_active\s*=\s*inputs\.rf5",
        r"outputs\.a\s*=.*inputs\.rf5",
        r"state\.z_airdodge_override_active\s*=\s*inputs\.rf6\s*;",
        r"outputs\.buttonR\s*=\s*inputs\.rf6\s*;",
    )
    for pattern in rf_patterns:
        current_lines = re.findall(rf"^.*{pattern}.*$", ultimate, flags=re.M)
        base_lines = re.findall(rf"^.*{pattern}.*$", base_ultimate, flags=re.M)
        if current_lines != base_lines:
            fail(f"RF5/RF6 source expression changed for pattern: {pattern}")

    forbidden_output_bindings = (
        r"LookupRuntime(?:Table|StickPoint)\s*\([^)]*kPhase7AD3GlobalParseResult",
        r"ApplyTableAnalogOutput\s*\([^)]*kPhase7AD3GlobalParseResult",
        r"ApplyDirectionPlusAOverride\s*\([^)]*kPhase7AD3GlobalParseResult",
        r"ApplyZAirdodgeOverride\s*\([^)]*kPhase7AD3GlobalParseResult",
    )
    for pattern in forbidden_output_bindings:
        if re.search(pattern, impl, flags=re.S):
            fail("parsed result is routed into output lookup")

    for path in (PARSER_HPP, HEADER_HPP, ANCHOR_CPP, INTERPRETER_HPP, IDENTITY_HPP):
        text = implementation_text(read_required(path))
        if "ResolveActiveRuntimeConfig" in text:
            fail(f"ResolveActiveRuntimeConfig present in {rel(path)}")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"forbidden runtime/storage pattern present in {rel(path)}: {pattern}")


def validate_markdown_docs() -> None:
    doc = read_required(DOC_MD)
    for phrase in (
        "status: DIAGNOSTIC_D3_IMPLEMENTED_PENDING_HARDWARE_RESULT",
        f"diagnostic branch: `{BRANCH}`",
        f"base branch: `{BASE_BRANCH}`",
        "global/static parser initialization only",
        "kPhase7AD3GlobalParseResult",
        "kPhase7AD2BRetainedPayloadAnchor",
        "UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload",
        "No second payload copy is intentionally introduced by D3",
        "no runtime resolver",
        "no runtime output routing to the parsed result",
        "no `UpdateDigitalOutputs(...)` edit",
        "no RF5/RF6 expression edit",
        "no storage/config.bin/Persistence",
        "no WebSerial/device write",
        "no firmware flashing automation",
        "no hardware-result claim",
        "no nunchuk validation claim",
        "If D3 passes, static/global parser initialization alone is unlikely",
        "If D3 fails, H1 global/static parser initialization and H4 parser loop/static-init become strong suspects",
        "Root cause is not proven",
    ):
        require_phrase(doc, phrase, "D3 diagnostic packet")

    report_md = read_required(REPORT_MD)
    for phrase in (
        "diagnostic_mode: `D3`",
        f"branch: `{BRANCH}`",
        f"base_branch: `{BASE_BRANCH}`",
        f"build command: `{BUILD_COMMAND}`",
        "payload bytes retained: `true`",
        "parser_called_by_global_static_initialization: `true`",
        "global_parse_result_added: `true`",
        "resolver_added: `false`",
        "runtime_behavior_changed_intended: `false`",
        "UpdateAnalogOutputs changed: `false`",
        "storage/write/flashing: `false`",
        "hardware_required: `true`",
        "hardware_result_claimed: `false`",
        "nunchuk_status: `not_tested`",
        "artifact observations are local build observations",
    ):
        require_phrase(report_md, phrase, "D3 build report")

    plan_md = read_required(PLAN_MD)
    require_phrase(plan_md, f"Branch: `{BRANCH}`", "D3 hardware plan")
    require_phrase(plan_md, "not a merge candidate", "D3 hardware plan")
    require_phrase(plan_md, "Hardware result must be recorded separately", "D3 hardware plan")
    for row in REQUIRED_ROWS:
        if not re.search(
            rf"\|\s*{re.escape(row)}\s*\|[^\n]*\|[^\n]*\|\s*NOT_TESTED\s*\|",
            plan_md,
            flags=re.IGNORECASE,
        ):
            fail(f"hardware plan row missing or not NOT_TESTED: {row}")


def validate_json_docs() -> None:
    report = load_json(REPORT_JSON)
    expected_report = {
        "schema_name": "glyph_phase7a_diagnostic_d3_global_parse_result_only_build_report",
        "status": "diagnostic_d3_build_report_pending_hardware_result",
        "diagnostic_mode": "D3",
        "branch": BRANCH,
        "base_branch": BASE_BRANCH,
        "build_command": BUILD_COMMAND,
        "payload_bytes_retained": True,
        "payload_size_bytes": EXPECTED_PAYLOAD_SIZE,
        "payload_sequence_scan_performed": True,
        "parser_called_by_global_static_initialization": True,
        "global_parse_result_added": True,
        "resolver_added": False,
        "runtime_behavior_changed_intended": False,
        "update_analog_outputs_changed": False,
        "update_digital_outputs_changed": False,
        "rf5_rf6_source_expressions_changed": False,
        "storage_write_flashing": False,
        "hardware_required": True,
        "hardware_result_claimed": False,
        "nunchuk_status": "not_tested",
        "artifact_observations_are_local_not_rebuild_gate": True,
    }
    for key, expected in expected_report.items():
        if report.get(key) != expected:
            fail(f"build report JSON mismatch for {key}: {report.get(key)!r}")
    if "kPhase7AD2BRetainedPayloadAnchor" not in str(report.get("payload_source", "")):
        fail("build report JSON payload_source must cite D2B retained anchor")
    artifacts = report.get("artifacts")
    if not isinstance(artifacts, list) or {a.get("artifact_type") for a in artifacts if isinstance(a, dict)} != {"uf2", "elf", "bin"}:
        fail("build report JSON artifacts must include uf2, elf, and bin")
    for item in artifacts:
        if not isinstance(item, dict):
            fail("artifact entries must be objects")
        if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] <= 0:
            fail("artifact entry size_bytes must be positive")
        if not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))):
            fail("artifact entry sha256 must be a lowercase SHA-256")

    plan = load_json(PLAN_JSON)
    if plan.get("schema_name") != "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan":
        fail("hardware plan schema mismatch")
    if plan.get("status") != "TEMPLATE_ONLY":
        fail("hardware plan status must be TEMPLATE_ONLY")
    if plan.get("branch") != BRANCH or plan.get("base_branch") != BASE_BRANCH:
        fail("hardware plan branch/base mismatch")
    if plan.get("hardware_result_recorded") is not False:
        fail("hardware plan must not record hardware result")
    rows = plan.get("test_rows")
    if not isinstance(rows, list):
        fail("hardware plan test_rows must be a list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware plan row entries must be objects")
        row_id = str(row.get("row_id", ""))
        if row_id in seen:
            fail(f"duplicate hardware plan row: {row_id}")
        seen.add(row_id)
        if str(row.get("result", "")).upper() != "NOT_TESTED":
            fail(f"hardware plan row must remain NOT_TESTED: {row_id}")
    if seen != REQUIRED_ROWS:
        fail("hardware plan row set mismatch")
    caveats = plan.get("caveats")
    if not isinstance(caveats, list) or "nunchuk NOT_TESTED" not in caveats:
        fail("hardware plan must preserve nunchuk NOT_TESTED caveat")


def validate_navigation_and_prior_evidence() -> None:
    runtime_readme = read_required(RUNTIME_README)
    calibration_index = read_required(CALIBRATION_INDEX)
    for phrase in (
        "phase7a_diagnostic_d3_global_parse_result_only.md",
        "phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md",
        "fixtures/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.json",
        "tools/check_glyph_phase7a_diagnostic_d3_global_parse_result_only.py",
    ):
        require_phrase(runtime_readme, phrase, "runtime config README")
    for phrase in (
        "glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.md",
        "fixtures/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_plan_2026-06-09.json",
    ):
        require_phrase(calibration_index, phrase, "calibration index")

    prior = read_required(D2B_RESULT_MD)
    require_phrase(prior, "status: USER_REPORTED_PASS", "D2B prior evidence")
    require_phrase(prior, "Retained payload bytes alone did not reproduce the RF5/RF6 disconnect", "D2B prior evidence")


def main() -> int:
    validate_branch()
    validate_changed_paths()
    validate_payload_retained()
    validate_source_guardrails()
    validate_markdown_docs()
    validate_json_docs()
    validate_navigation_and_prior_evidence()
    print("glyph_phase7a_diagnostic_d3_global_parse_result_only: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
