#!/usr/bin/env python3
"""Validate Phase 7A Diagnostic D5A-N2 resolver hot-path parse-status read removal."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read"
BASE_BRANCH = "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate"

DOC_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read.md"
REPORT_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.md"
REPORT_JSON = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.json"
PLAN_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.md"
PLAN_JSON = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.json"
RESULT_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.md"
RESULT_JSON = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.json"
RUNTIME_README = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs" / "calibration" / "INDEX.md"
ULTIMATE_CPP = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
N1_DOC_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate.md"

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
    "PARSE-STATUS-READ-001",
    "SOURCE-OWNED-ROUTING-001",
    "FALLBACK-001",
    "NO-PARSED-TABLES-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
}


class D5AN2Error(ValueError):
    """Raised when D5A-N2 guardrails drift."""


def fail(message: str) -> None:
    raise D5AN2Error(message)


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
        fail(f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate JSON key: {key}")
        seen[key] = value
    return seen


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path), object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{rel(path)} must be a JSON object")
    return payload


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, where: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{where} missing required phrase: {phrase!r}")


def extract_function(text: str, qualified_name: str) -> str:
    match = re.search(
        rf"(?:const\s+RuntimeConfigView&|void|bool|int|uint8_t|uint16_t|size_t|auto)\s+{re.escape(qualified_name)}\s*\([^)]*\)\s*\{{",
        text,
    )
    if not match:
        fail(f"missing function {qualified_name}")
    start = match.start()
    brace = text.find("{", match.end() - 1)
    if brace < 0:
        fail(f"malformed function: {qualified_name}")
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    fail(f"could not parse function: {qualified_name}")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if "//" in line:
            line = line.split("//", 1)[0]
        lines.append(line)
    return "\n".join(lines)


def line_contains_runtime_config_alias(line: str) -> bool:
    text = line.strip()
    if not text:
        return False
    if text.startswith("//"):
        return False
    if re.match(r"^\s*if\s*\(", text):
        return False
    if "(" in text:
        return False
    if re.search(r"\bRuntimeConfigView\b.*[=;]", text):
        return True
    return False


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

    no_comment_ultimate = strip_comments(ultimate)

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, no_comment_ultimate, flags=re.IGNORECASE):
            fail(f"forbidden source pattern present in Ultimate.cpp: {pattern}")

    require_phrase(ultimate, "kPhase7AD2BRetainedPayloadAnchor", "Ultimate.cpp")
    require_phrase(ultimate, "kPhase7AD3GlobalParseResult", "Ultimate.cpp")
    require_phrase(ultimate, "ParseUltimateRuntimeConfigPayload(", "Ultimate.cpp")

    if "kPhase7AD5AParseStatusGatedRuntimeConfigView" in ultimate:
        fail("parse-status alias remains in Ultimate.cpp")

    parser_calls = re.findall(r"\bParseUltimateRuntimeConfigPayload\s*\(", ultimate)
    if len(parser_calls) != 1:
        fail(f"expected one global parser call, found {len(parser_calls)}")

    if not re.search(
        r"\bkPhase7AD3GlobalParseResult\b.*?=\s*UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload\s*\(",
        ultimate,
        flags=re.S,
    ):
        fail("global parser call is not in the parse-result initializer")

    resolver = extract_function(ultimate, "ResolveActiveRuntimeConfig")
    require_phrase(resolver, "ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)", "resolver")
    require_phrase(resolver, "return kSourceOwnedCurrentBaselineRuntimeConfig;", "resolver")
    require_phrase(resolver, "return kKnownGoodRuntimeConfig;", "resolver")
    if "kPhase7AD3GlobalParseResult.status" in resolver:
        fail("resolver still reads parse-status in hot path")
    if "kSourceOwnedCurrentBaselineRuntimeConfig" not in resolver:
        fail("resolver must return canonical source-owned runtime config symbol")

    if "kPhase7AD3GlobalParseResult.status" in no_comment_ultimate:
        fail("resolver or other hot path still reads parse-status")

    # No separate RuntimeConfigView alias/copy besides the resolver callsite.
    for line in ultimate.splitlines():
        if line_contains_runtime_config_alias(line):
            text = line.strip()
            if text.startswith("const RuntimeConfigView& ResolveActiveRuntimeConfig("):
                continue
            if text.startswith("const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();"):
                continue
            if text.startswith("void ApplyDirectionPlusAOverride(const RuntimeConfigView &runtime_config,"):
                continue
            if text.startswith("void ApplyZAirdodgeOverride(const RuntimeConfigView &runtime_config,"):
                continue
            if text.startswith("void ApplyAnalogOutputs("):
                continue
            fail(f"RuntimeConfigView alias/copy found in Ultimate.cpp: {text}")

    analog = extract_function(ultimate, "Ultimate::UpdateAnalogOutputs")
    require_phrase(
        analog,
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "Ultimate::UpdateAnalogOutputs",
    )

    digital = extract_function(ultimate, "Ultimate::UpdateDigitalOutputs")
    base_digital = extract_function(base_ultimate, "Ultimate::UpdateDigitalOutputs")
    if digital != base_digital:
        fail("UpdateDigitalOutputs changed in D5A-N2")

    rf_keys = ("rf5", "rf6", "lt6")
    for token in rf_keys:
        current_lines = [line.strip() for line in no_comment_ultimate.splitlines() if token in line.lower()]
        base_lines = [line.strip() for line in strip_comments(base_ultimate).splitlines() if token in line.lower()]
        for line in current_lines:
            if line and line not in base_lines:
                fail(f"rf5/rf6/lt6-related expression changed relative to base: {line}")

    if "runtime_analog_output_lookup" in no_comment_ultimate and "kPhase7AD3GlobalParseResult" in no_comment_ultimate:
        pass

    if "parsed_table" in no_comment_ultimate and "kPhase7AD3GlobalParseResult" in no_comment_ultimate:
        fail("parsed table materialization appears to be present")

    if "kPhase7AD5ParsedRuntimeConfigView" in no_comment_ultimate:
        fail("parsed runtime-config view symbol found in source")


def validate_docs_and_reports() -> None:
    doc = read_required(DOC_MD)
    report_md = read_required(REPORT_MD)
    report = load_json(REPORT_JSON)
    plan_md = read_required(PLAN_MD)
    plan = load_json(PLAN_JSON)
    readme = read_required(RUNTIME_README)
    index = read_required(CALIBRATION_INDEX)
    result_md_text = read_required(RESULT_MD) if RESULT_MD.exists() else ""
    result_json_obj = load_json(RESULT_JSON) if RESULT_JSON.exists() else {}

    # Required docs / fixtures are linked from indexes.
    for required_path, container, label in (
        ("phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read.md", readme, "runtime_config/README.md"),
        ("phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.md", readme, "runtime_config/README.md"),
        ("fixtures/phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.json", readme, "runtime_config/README.md"),
        ("glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.md", readme, "runtime_config/README.md"),
        ("glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.md", index, "calibration/INDEX.md"),
        ("fixtures/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_plan_2026-06-09.json", index, "calibration/INDEX.md"),
    ):
        if required_path not in container:
            fail(f"{label} missing reference: {required_path}")

    require_phrase(doc, "D5A-N2", "D5A-N2 document")
    require_phrase(doc, "parse-status hot-path", "D5A-N2 document")
    require_phrase(doc, "no parsed table materialization", "D5A-N2 document")
    require_phrase(doc, "UpdateAnalogOutputs(...)", "D5A-N2 document")
    require_phrase(doc, "direct canonical source-owned", "D5A-N2 document")
    require_phrase(doc, "no hardware result claim", "D5A-N2 document")
    require_phrase(doc, "nunchuk not tested", "D5A-N2 document")

    if report.get("build_command") != "pio run -e glyph_mk6":
        fail("build report JSON build_command mismatch")
    if report.get("diagnostic_mode") != "D5A-N2":
        fail("build report diagnostic_mode must be D5A-N2")
    if report.get("branch") != BRANCH:
        fail("build report branch mismatch")
    if report.get("base_branch") != BASE_BRANCH:
        fail("build report base_branch mismatch")

    boolean_checks = {
        "payload_bytes_retained": True,
        "global_parse_result_added": True,
        "parser_called_by_global_static_initialization": True,
        "resolver_added": True,
        "parsed_result_routed_to_runtime_output_lookup": False,
        "parsed_table_materialization_added": False,
        "parse_status_gated_routing_added": False,
        "source_owned_runtime_view_routed_after_parse_ok": False,
        "hardware_required": True,
        "hardware_result_claimed": False,
        "artifact_hashes_are_checker_gate": False,
        "artifact_hashes_are_rebuild_stable": False,
    }
    for key, expected in boolean_checks.items():
        if report.get(key) is not expected:
            fail(f"build report key {key} must be {expected}")

    if not isinstance(report.get("artifacts"), list) or not report["artifacts"]:
        fail("build report must include a non-empty artifacts list")
    for artifact in report["artifacts"]:
        if artifact.get("artifact_type") not in {"uf2", "elf", "bin"}:
            fail("artifact type must be uf2/elf/bin")
        if not isinstance(artifact.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}|unknown", artifact["sha256"]):
            fail("artifact sha256 must be a 64-char hex digest or unknown")
        if not isinstance(artifact.get("size_bytes"), int) or artifact["size_bytes"] < 0:
            fail("artifact size_bytes must be a non-negative integer")
        if not isinstance(artifact.get("availability"), bool):
            fail("artifact availability must be boolean")

    require_phrase(report_md, "build command: `pio run -e glyph_mk6`", "build report markdown")
    require_phrase(report_md, "artifact_hashes_are_checker_gate: `false`", "build report markdown")

    if report.get("hardware_result_claimed") is not False:
        fail("build report should not claim hardware result")

    if plan.get("branch") != BRANCH:
        fail("hardware plan branch mismatch")
    if plan.get("base_branch") != BASE_BRANCH:
        fail("hardware plan base branch mismatch")
    if plan.get("hardware_result_recorded") is not False:
        fail("hardware plan should not record result yet")
    test_rows = plan.get("test_rows")
    if not isinstance(test_rows, list):
        fail("plan test_rows must be a list")
    found_rows = {row.get("row_id") for row in test_rows if isinstance(row, dict)}
    if found_rows != REQUIRED_PLAN_ROWS:
        fail(f"plan row IDs mismatch: expected {sorted(REQUIRED_PLAN_ROWS)}, found {sorted(found_rows)}")
    for row in test_rows:
        if not isinstance(row, dict):
            continue
        if row.get("result") != "NOT_TESTED":
            fail(f"plan row {row.get('row_id')} must be NOT_TESTED")

    require_phrase(plan_md, "Status: TEMPLATE_ONLY", "hardware plan markdown")
    require_phrase(plan_md, "Nunchuk scope for this branch: `NOT_TESTED`", "hardware plan markdown")

    if result_md_text:
        require_phrase(result_md_text, "D5A-N1 failed.", "D5A-N1 failure markdown")
        require_phrase(result_md_text, "Same disconnects as D5A", "D5A-N1 failure markdown")
        require_phrase(result_md_text, "RF5/RF6/LT6", "D5A-N1 failure markdown")
        require_phrase(result_md_text, "parse-status hot-path read inside `ResolveActiveRuntimeConfig()` remains the primary suspect.", "D5A-N1 failure markdown")
    if result_json_obj:
        if result_json_obj.get("diagnostic_branch") != "phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate":
            fail("D5A-N1 result diagnostic branch mismatch")
        if not result_json_obj.get("d5a_n1_failed", False):
            fail("D5A-N1 result must record D5A-N1 failed")
        if not result_json_obj.get("same_disconnects_as_d5a", False):
            fail("D5A-N1 result must confirm same disconnects as D5A")
        if not result_json_obj.get("rf5_disconnect_observed", False):
            fail("D5A-N1 result must show RF5 disconnect observed")
        if not result_json_obj.get("rf6_disconnect_observed", False):
            fail("D5A-N1 result must show RF6 disconnect observed")
        if not result_json_obj.get("lt6_disconnect_observed", False):
            fail("D5A-N1 result must show LT6 disconnect observed")

    # N1 scope docs are required in sequence before N2.
    n1_doc = read_required(N1_DOC_MD)
    require_phrase(n1_doc, "D5A-N1", "D5A-N1 document")
    require_phrase(n1_doc, "parse-status gate remains in resolver", "D5A-N1 document")


def main() -> None:
    validate_branch()
    validate_source()
    validate_docs_and_reports()
    print("glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read: ok")


if __name__ == "__main__":
    main()
