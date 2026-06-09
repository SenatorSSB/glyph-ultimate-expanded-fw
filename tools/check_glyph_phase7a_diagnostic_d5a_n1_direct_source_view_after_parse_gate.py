#!/usr/bin/env python3
"""Validate Phase 7A Diagnostic D5A-N1 source and documentation guardrails."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate"
BASE_BRANCH = "phase7a-diagnostic-d5-parsed-result-runtime-routing"

DOC_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate.md"
REPORT_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.md"
REPORT_JSON = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.json"
PLAN_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.md"
PLAN_JSON = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.json"
RESULT_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_result_2026-06-09.md"
RESULT_JSON = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_result_2026-06-09.json"
RUNTIME_README = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
ULTIMATE_CPP = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"

FORBIDDEN_SOURCE_PATTERNS = (
    r"\bPersistence\b",
    r"\bLittleFS\b",
    r"\bEEPROM\b",
    r"\bconfig\.bin\b",
    r"\bWebSerial\b",
    r"\bdevice\s+write\b",
    r"\breboot_bootloader\b",
    r"\bflash_uf2\b",
    r"\bfirmware flashing automation\b",
)

REQUIRED_PLAN_ROWS = {
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "LT6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "UNRELATED-BUTTONS-001",
    "MODIFIERS-001",
    "PAYLOAD-001",
    "GLOBAL-PARSE-001",
    "PARSER-CALL-001",
    "RESOLVER-001",
    "PARSE-STATUS-GATE-001",
    "SOURCE-OWNED-ROUTING-001",
    "NO-PARSED-TABLES-001",
    "FALLBACK-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}


class D5AN1Error(ValueError):
    """Raised when D5A-N1 check guardrails fail."""


def fail(message: str) -> None:
    raise D5AN1Error(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        fail("git " + " ".join(args) + " failed: " + result.stderr.strip())
    return result


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {rel(path)}")
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
        fail(f"{rel(path)} must be a JSON object")
    return payload


def require_phrase(text: str, phrase: str, where: str) -> None:
    if phrase not in text:
        fail(f"{where} missing required phrase: {phrase!r}")


def require_normalized_phrase(text: str, phrase: str, where: str) -> None:
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    expected = re.sub(r"\s+", " ", phrase).strip().lower()
    if expected not in normalized:
        fail(f"{where} missing required phrase: {phrase!r}")


def extract_function(text: str, signature: str) -> str:
    match = re.search(rf"\b{re.escape(signature)}\s*\([^)]*\)\s*\{{", text)
    if not match:
        fail(f"missing function {signature}")
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
    fail(f"could not parse function {signature}")


def validate_branch() -> None:
    branch = run_git(["branch", "--show-current"]).stdout.strip()
    if branch != BRANCH:
        fail(f"unexpected branch {branch!r}, expected {BRANCH!r}")
    if run_git(["merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"], check=False).returncode != 0:
        fail(f"{BASE_BRANCH} must be an ancestor of HEAD")


def validate_source() -> None:
    ultimate = read_required(ULTIMATE_CPP)
    base_ultimate = run_git(["show", f"{BASE_BRANCH}:src/modes/Ultimate.cpp"]).stdout
    if not base_ultimate:
        fail(f"unable to read base source from {BASE_BRANCH}:src/modes/Ultimate.cpp")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, ultimate, flags=re.IGNORECASE):
            fail(f"forbidden source pattern present: {pattern}")

    require_phrase(ultimate, "kPhase7AD2BRetainedPayloadAnchor", "Ultimate.cpp")
    require_phrase(ultimate, "kPhase7AD3GlobalParseResult", "Ultimate.cpp")
    require_phrase(ultimate, "ParseUltimateRuntimeConfigPayload(", "Ultimate.cpp")
    if "kPhase7AD5AParseStatusGatedRuntimeConfigView" in ultimate:
        fail("separate D5A parse-status-gated RuntimeConfigView alias remains in source")

    # Ensure resolver stays parse-status gated and returns canonical source-owned view
    resolver = extract_function(ultimate, "const RuntimeConfigView& ResolveActiveRuntimeConfig")
    require_phrase(
        resolver,
        "kPhase7AD3GlobalParseResult.status == UltimateRuntimeConfigParser::ParseStatus::Ok",
        "resolver",
    )
    require_phrase(resolver, "ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)", "resolver")
    require_phrase(resolver, "return kSourceOwnedCurrentBaselineRuntimeConfig;", "resolver")
    require_phrase(resolver, "return kKnownGoodRuntimeConfig;", "resolver")

    # No separate RuntimeConfigView copy/alias should be introduced.
    if re.search(r"\bRuntimeConfigView\s+[A-Za-z0-9_]+\s*(?:[=;])", ultimate):
        # Allow function return type and parameter references; keep this guard for aliases/copies.
        for line in ultimate.splitlines():
            stripped = line.strip()
            if stripped.startswith("const RuntimeConfigView& ResolveActiveRuntimeConfig("):
                continue
            if stripped.startswith("const RuntimeConfigView &runtime_config"):
                continue
            if re.search(r"\bRuntimeConfigView\s+[A-Za-z0-9_]+\s*(?:[=;])", stripped):
                fail("runtime config RuntimeConfigView alias/copy found in Ultimate.cpp")

    # Analog routing remains in UpdateAnalogOutputs only via resolver
    analog = extract_function(ultimate, "Ultimate::UpdateAnalogOutputs")
    require_phrase(
        analog,
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "Ultimate::UpdateAnalogOutputs",
    )

    # UpdateDigitalOutputs unchanged relative to base branch
    digital = extract_function(ultimate, "Ultimate::UpdateDigitalOutputs")
    base_digital = extract_function(base_ultimate, "Ultimate::UpdateDigitalOutputs")
    if digital != base_digital:
        fail("UpdateDigitalOutputs changed in D5A-N1")

    # RF5/RF6/LT6 expressions must be unchanged from D3 source
    for token in ("rf5", "rf6", "lt6"):
        for snippet in [line.strip() for line in ultimate.splitlines() if token in line.lower() and "inputs." in line.lower()]:
            if not snippet:
                continue
            if snippet not in base_ultimate:
                fail(f"input expression changed relative to base branch: {snippet}")

    if "kPhase7AD5ParsedRuntimeConfigView" in ultimate:
        fail("parsed-result runtime view symbol found in source")


def validate_docs_and_reports() -> None:
    doc = read_required(DOC_MD)
    report_md = read_required(REPORT_MD)
    report = load_json(REPORT_JSON)
    plan_md = read_required(PLAN_MD)
    plan = load_json(PLAN_JSON)
    readme = read_required(RUNTIME_README)
    index = read_required(CALIBRATION_INDEX)
    result_md = read_required(RESULT_MD)
    result = load_json(RESULT_JSON)

    # docs index links
    for required_path, container, label in (
        ("phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate.md", readme, "runtime_config/README.md"),
        ("phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.md", readme, "runtime_config/README.md"),
        ("phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate.md", readme, "runtime_config/README.md"),
        ("fixtures/phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.json", readme, "runtime_config/README.md"),
        ("glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.md", readme, "runtime_config/README.md"),
        ("glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_result_2026-06-09.md", readme, "runtime_config/README.md"),
        ("glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.md", index, "calibration/INDEX.md"),
        ("fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_plan_2026-06-09.json", index, "calibration/INDEX.md"),
        ("glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_result_2026-06-09.md", index, "calibration/INDEX.md"),
        ("fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_result_2026-06-09.json", index, "calibration/INDEX.md"),
    ):
        if required_path not in container:
            fail(f"{label} missing link/reference: {required_path}")

    # D5A-N1 scope and non-claims in doc/report/plan
    require_phrase(doc, "D5A-N1", "D5A-N1 document")
    require_phrase(doc, "parse-status gate remains in resolver", "D5A-N1 document")
    require_phrase(doc, "resolver call from `UpdateAnalogOutputs(...)`", "D5A-N1 document")
    require_phrase(doc, "Do not add parsed table materialization", "D5A-N1 document")
    require_phrase(doc, "RF5, RF6, and LT6", "D5A-N1 document")
    require_phrase(doc, "no hardware result claim", "D5A-N1 document")
    require_phrase(doc, "nunchuk remains not_tested", "D5A-N1 document")

    require_normalized_phrase(
        report_md,
        "build command: `pio run -e glyph_mk6`",
        "build report markdown",
    )
    require_phrase(report_md, "artifact_hashes_are_checker_gate: `false`", "build report markdown")
    require_phrase(report_md, "Artifact observations are local build observations only", "build report markdown")

    require_phrase(plan_md, "Status: TEMPLATE_ONLY", "hardware plan markdown")
    require_phrase(plan_md, "Nunchuk scope for this branch: `NOT_TESTED`", "hardware plan markdown")
    require_phrase(plan_md, "Hardware result required", "hardware plan markdown")
    require_phrase(plan_md, "RF5-001", "hardware plan markdown")
    require_phrase(plan_md, "RF6-001", "hardware plan markdown")
    require_phrase(plan_md, "LT6-001", "hardware plan markdown")

    require_phrase(result_md, "USER_REPORTED_FAILURE", "hardware result markdown")
    require_phrase(result_md, "RF5", "hardware result markdown")
    require_phrase(result_md, "RF6", "hardware result markdown")
    require_phrase(result_md, "LT6", "hardware result markdown")

    if report.get("build_command") != "pio run -e glyph_mk6":
        fail("build report JSON must use pio run -e glyph_mk6")
    if report.get("diagnostic_mode") != "D5A-N1":
        fail("build report JSON must use diagnostic_mode D5A-N1")
    if report.get("branch") != BRANCH:
        fail("build report branch mismatch")
    if report.get("base_branch") != BASE_BRANCH:
        fail("build report base branch mismatch")
    boolean_checks = {
        "payload_bytes_retained": True,
        "global_parse_result_added": True,
        "parser_called_by_global_static_initialization": True,
        "resolver_added": True,
        "parsed_result_routed_to_runtime_output_lookup": False,
        "parsed_table_materialization_added": False,
        "parse_status_gated_routing_added": True,
        "source_owned_runtime_view_routed_after_parse_ok": True,
        "runtime_behavior_changed_intended": True,
        "expected_output_values_changed": False,
        "hardware_required": True,
        "hardware_result_claimed": False,
        "artifact_hashes_are_checker_gate": False,
    }
    for key, expected in boolean_checks.items():
        if report.get(key) is not expected:
            fail(f"build report key {key} must be {expected}")

    if report.get("artifact_hashes_are_checker_gate") is not False:
        fail("report must not use artifact hashes as checker gates")
    if report.get("artifact_hashes_are_rebuild_stable") is not False:
        fail("artifact_hashes_are_rebuild_stable must be false")
    if not isinstance(report.get("artifacts"), list) or not report["artifacts"]:
        fail("report JSON must include a non-empty artifacts list")

    for artifact in report["artifacts"]:
        if artifact.get("artifact_type") not in {"uf2", "elf", "bin"}:
            fail(f"unexpected artifact_type: {artifact.get('artifact_type')}")
        if not isinstance(artifact.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
            fail("artifact sha256 must be a lowercase 64-char hex digest")
        if not isinstance(artifact.get("size_bytes"), int) or artifact["size_bytes"] <= 0:
            fail("artifact size_bytes must be a positive integer")
        if not isinstance(artifact.get("availability"), bool):
            fail("artifact availability must be boolean")

    if plan.get("branch") != BRANCH:
        fail("hardware plan branch mismatch")
    if plan.get("base_branch") != BASE_BRANCH:
        fail("hardware plan base branch mismatch")
    if plan.get("hardware_result_recorded") is not False:
        fail("hardware plan must not record result yet")
    plan_rows = plan.get("test_rows")
    if not isinstance(plan_rows, list):
        fail("plan JSON test_rows must be a list")
    found_rows = {row.get("row_id") for row in plan_rows if isinstance(row, dict)}
    if found_rows != REQUIRED_PLAN_ROWS:
        fail(f"plan row IDs mismatch: expected {sorted(REQUIRED_PLAN_ROWS)}, found {sorted(found_rows)}")

    if not result.get("hardware_result_recorded"):
        fail("failure result must be recorded")
    if result.get("diagnostic_branch") != BRANCH:
        fail("hardware result branch mismatch")
    if result.get("rf5_disconnect_observed") is not True:
        fail("failure result must report rf5_disconnect_observed=true")
    if result.get("rf6_disconnect_observed") is not True:
        fail("failure result must report rf6_disconnect_observed=true")
    if result.get("lt6_disconnect_observed") is not True:
        fail("failure result must report lt6_disconnect_observed=true")
    if result.get("nunchuk_status") != "not_tested":
        fail("hardware result must remain nunchuk NOT_TESTED")

    failure_rows = {
        row.get("row_id"): row.get("result")
        for row in result.get("result_rows", [])
        if isinstance(row, dict)
    }
    for required_row, required_result in (
        ("RF5-001", "FAIL"),
        ("RF6-001", "FAIL"),
        ("LT6-001", "FAIL"),
    ):
        if failure_rows.get(required_row) != required_result:
            fail(f"failure result row {required_row} must be {required_result}")


def main() -> None:
    validate_branch()
    validate_source()
    validate_docs_and_reports()
    print("glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate: ok")


if __name__ == "__main__":
    main()
