#!/usr/bin/env python3
"""Validate Phase 7A Diagnostic D5A parse-status-gated routing guardrails."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d5-parsed-result-runtime-routing"
BASE_BRANCH = "phase7a-diagnostic-d3-global-parse-result-only"
BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"

ULTIMATE_CPP = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
PARSER_HPP = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"
DOC_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5_parsed_result_runtime_routing.md"
REPORT_MD = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.md"
REPORT_JSON = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.json"
PLAN_MD = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.md"
PLAN_JSON = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.json"
RUNTIME_README = REPO_ROOT / "docs" / "runtime_config" / "README.md"
CALIBRATION_INDEX = REPO_ROOT / "docs" / "calibration" / "INDEX.md"

EXPECTED_CHANGED_PATHS = {
    "src/modes/Ultimate.cpp",
    "docs/runtime_config/README.md",
    "docs/runtime_config/phase7a_diagnostic_d5_parsed_result_runtime_routing.md",
    "docs/runtime_config/phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.md",
    "docs/runtime_config/fixtures/phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.json",
    "docs/calibration/INDEX.md",
    "docs/calibration/glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.md",
    "docs/calibration/fixtures/glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing_hardware_plan_2026-06-09.json",
    "tools/check_glyph_phase7a_diagnostic_d5_parsed_result_runtime_routing.py",
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

FORBIDDEN_SOURCE_PATTERNS = (
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


class Phase7AD5AError(ValueError):
    """Raised when D5A guardrails drift."""


def fail(message: str) -> None:
    raise Phase7AD5AError(message)


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
    return run_git(["show", f"{ref}:{rel(path)}"]).stdout


def extract_function(text: str, qualified_name: str) -> str:
    match = re.search(rf"(?:void|const\s+RuntimeConfigView&)\s+{re.escape(qualified_name)}\s*\([^)]*\)\s*\{{", text)
    if not match:
        fail(f"missing function: {qualified_name}")
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
    fail(f"could not parse function: {qualified_name}")


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
        fail("changed paths outside D5A scope: " + ", ".join(sorted(extra)))


def extract_struct(text: str, name: str) -> str:
    match = re.search(rf"\bstruct\s+{re.escape(name)}\s*\{{", text)
    if not match:
        fail(f"missing struct: {name}")
    start = match.start()
    brace = text.find("{", match.end() - 1)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                semicolon = text.find(";", index)
                return text[start:semicolon + 1]
    fail(f"could not parse struct: {name}")


def validate_source() -> None:
    ultimate = read_required(ULTIMATE_CPP)
    base_ultimate = git_show_text(BASE_BRANCH, ULTIMATE_CPP)
    parser = read_required(PARSER_HPP)
    impl = implementation_text(ultimate)

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, impl, flags=re.IGNORECASE):
            fail(f"forbidden source pattern present in Ultimate.cpp: {pattern}")

    require_phrase(ultimate, "kPhase7AD2BRetainedPayloadAnchor", "Ultimate.cpp")
    require_phrase(ultimate, "kPhase7AD3GlobalParseResult", "Ultimate.cpp")
    require_phrase(ultimate, "kPhase7AD5AParseStatusGatedRuntimeConfigView", "Ultimate.cpp")
    require_phrase(ultimate, "D5A does not materialize parsed tables", "Ultimate.cpp")
    require_phrase(ultimate, "ParseResult currently exposes status/counts only", "Ultimate.cpp")
    require_phrase(ultimate, "aliases the source-owned baseline", "Ultimate.cpp")

    parse_result = extract_struct(parser, "ParseResult")
    for phrase in ("ParseStatus status;", "size_t table_count;", "size_t point_count_per_table;"):
        require_phrase(parse_result, phrase, "ParseResult")
    for forbidden in ("RuntimeConfigView", "RuntimeTableView", "StickPoint"):
        if forbidden in parse_result:
            fail(f"ParseResult must not expose parsed runtime-config data: {forbidden}")
    if re.search(r"\b(?:tables?|runtime_config|view)\b\s*[;=]", parse_result):
        fail("ParseResult must expose only status/count metadata, not parsed data fields")

    if re.search(r"\bkPhase7AD5A.*Table", impl):
        fail("D5A must not add parsed table materialization")
    if "kPhase7AD5ParsedRuntimeConfigView" in ultimate:
        fail("old parsed-runtime-config-view symbol must not remain")

    parser_calls = re.findall(r"ParseUltimateRuntimeConfigPayload\s*\(", impl)
    if len(parser_calls) != 1:
        fail(f"expected exactly one global/static parser call, found {len(parser_calls)}")

    parse_result_decls = re.findall(r"\bkPhase7AD3GlobalParseResult\b", impl)
    if len(parse_result_decls) < 2:
        fail("D3 global parse result symbol is missing or no longer used")

    resolver_matches = re.findall(r"\bconst\s+RuntimeConfigView&\s+ResolveActiveRuntimeConfig\s*\(", impl)
    if len(resolver_matches) != 1:
        fail(f"expected exactly one ResolveActiveRuntimeConfig definition, found {len(resolver_matches)}")

    resolver = extract_function(ultimate, "ResolveActiveRuntimeConfig")
    require_phrase(
        resolver,
        "kPhase7AD3GlobalParseResult.status == UltimateRuntimeConfigParser::ParseStatus::Ok",
        "resolver",
    )
    require_phrase(resolver, "ValidateRuntimeConfigView(kPhase7AD5AParseStatusGatedRuntimeConfigView)", "resolver")
    require_phrase(resolver, "return kPhase7AD5AParseStatusGatedRuntimeConfigView;", "resolver")
    require_phrase(resolver, "ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)", "resolver")
    require_phrase(resolver, "? kSourceOwnedCurrentBaselineRuntimeConfig", "resolver")
    require_phrase(resolver, ": kKnownGoodRuntimeConfig", "resolver")
    if resolver.find("kPhase7AD3GlobalParseResult.status") > resolver.find("kSourceOwnedCurrentBaselineRuntimeConfig"):
        fail("resolver must attempt parse-status-gated source-owned view before fallback")

    analog = extract_function(ultimate, "Ultimate::UpdateAnalogOutputs")
    require_phrase(
        analog,
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "Ultimate::UpdateAnalogOutputs",
    )

    digital = extract_function(ultimate, "Ultimate::UpdateDigitalOutputs")
    base_digital = extract_function(base_ultimate, "Ultimate::UpdateDigitalOutputs")
    if digital != base_digital:
        fail("UpdateDigitalOutputs changed relative to D3")

    rf_lines = [line.strip() for line in ultimate.splitlines() if "rf5" in line.lower() or "rf6" in line.lower()]
    base_rf_lines = [line.strip() for line in base_ultimate.splitlines() if "rf5" in line.lower() or "rf6" in line.lower()]
    if rf_lines != base_rf_lines:
        fail("RF5/RF6 source expressions changed relative to D3")


def validate_docs_and_reports() -> None:
    doc = read_required(DOC_MD)
    report_md = read_required(REPORT_MD)
    plan_md = read_required(PLAN_MD)
    readme = read_required(RUNTIME_README)
    index = read_required(CALIBRATION_INDEX)
    report = load_json(REPORT_JSON)
    plan = load_json(PLAN_JSON)

    for path_text, container, label in (
        (DOC_MD.name, readme, "runtime config README"),
        (REPORT_MD.name, readme, "runtime config README"),
        ("fixtures/" + REPORT_JSON.name, readme, "runtime config README"),
        (PLAN_MD.name, readme, "runtime config README"),
        (PLAN_MD.name, index, "calibration index"),
        ("fixtures/" + PLAN_JSON.name, index, "calibration index"),
    ):
        if path_text not in container:
            fail(f"{label} does not link {path_text}")

    required_doc_phrases = (
        "DIAGNOSTIC_D5A_IMPLEMENTED_PENDING_HARDWARE_RESULT",
        "D5A is not true parsed-result data routing",
        "`ParseResult` supplies status/count metadata only",
        "source-owned current-baseline equivalent alias",
        "True parsed table materialization/routing is deferred to a possible D5B",
        "Does the combination of D2B retained payload bytes",
        "phase7a-diagnostic-d3-global-parse-result-only",
        "D2B passed",
        "D3 passed",
        "D4 passed",
        "kPhase7AD5AParseStatusGatedRuntimeConfigView",
        "ResolveActiveRuntimeConfig()",
        "const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();",
        "Artifact hashes are local observations only and are not a checker gate",
        "no storage/config.bin/Persistence",
        "no runtime-loaded config from device/user storage",
        "no nunchuk validation is claimed",
        "hardware-result claim: none",
    )
    for phrase in required_doc_phrases:
        require_phrase(doc, phrase, "D5A diagnostic doc")

    forbidden_claims = (
        "parsed_result_routed_to_runtime_output_lookup: `true`",
        '"parsed_result_routed_to_runtime_output_lookup": true',
        "parsed result selected: yes",
        "parsed table data used: yes",
        "true parsed-result data routing",
    )
    for claim in forbidden_claims:
        if normalize(claim) in normalize(doc) and claim != "true parsed-result data routing":
            fail(f"D5A diagnostic doc contains forbidden parsed-data claim: {claim}")
    for container, label in ((doc, "D5A diagnostic doc"), (report_md, "build report")):
        if "parsed-result resolver-selected equivalent view" in container:
            fail(f"{label} contains misleading parsed-result selected-view wording")

    for key, expected in {
        "diagnostic_mode": "D5A",
        "branch": BRANCH,
        "base_branch": BASE_BRANCH,
        "build_command": BUILD_COMMAND,
        "payload_bytes_retained": True,
        "global_parse_result_added": True,
        "parser_called_by_global_static_initialization": True,
        "resolver_added": True,
        "parsed_result_routed_to_runtime_output_lookup": False,
        "parsed_table_materialization_added": False,
        "parse_status_gated_routing_added": True,
        "source_owned_runtime_view_routed_after_parse_ok": True,
        "true_parsed_result_routing_deferred": True,
        "d5b_required_for_true_parsed_data_routing": True,
        "storage_added": False,
        "write_path_added": False,
        "flashing_automation_added": False,
        "runtime_behavior_changed_intended": True,
        "expected_output_values_changed": False,
        "hardware_required": True,
        "hardware_result_claimed": False,
        "nunchuk_status": "not_tested",
        "artifact_hashes_are_rebuild_stable": False,
        "artifact_hashes_are_checker_gate": False,
    }.items():
        if report.get(key) != expected:
            fail(f"build report JSON {key} must be {expected!r}")

    require_phrase(report_md, "artifact_hashes_are_rebuild_stable: `false`", "build report")
    require_phrase(report_md, "artifact_hashes_are_checker_gate: `false`", "build report")
    require_phrase(report_md, "Artifact observations are local build observations only", "build report")
    require_phrase(report_md, "diagnostic_mode: `D5A`", "build report")
    require_phrase(report_md, "parsed_result_routed_to_runtime_output_lookup: `false`", "build report")
    require_phrase(report_md, "parsed_table_materialization_added: `false`", "build report")
    require_phrase(report_md, "parse_status_gated_routing_added: `true`", "build report")
    require_phrase(report_md, "source_owned_runtime_view_routed_after_parse_ok: `true`", "build report")

    artifacts = report.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        fail("build report JSON artifacts must be a non-empty list")
    seen_types: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            fail("artifact entries must be objects")
        path = artifact.get("path")
        artifact_type = artifact.get("artifact_type")
        size = artifact.get("size_bytes")
        sha = artifact.get("sha256")
        if not isinstance(path, str) or not path:
            fail("artifact path must be a non-empty string")
        if artifact_type not in {"uf2", "elf", "bin"}:
            fail(f"unexpected artifact_type: {artifact_type!r}")
        if not isinstance(size, int) or size <= 0:
            fail(f"{artifact_type} size_bytes must be a positive int")
        if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
            fail(f"{artifact_type} sha256 must be lowercase 64-char hex")
        seen_types.add(artifact_type)
    if seen_types != {"uf2", "elf", "bin"}:
        fail("artifact list must contain uf2, elf, and bin entries")

    if plan.get("branch") != BRANCH:
        fail("hardware plan branch mismatch")
    if plan.get("base_branch") != BASE_BRANCH:
        fail("hardware plan base_branch mismatch")
    if plan.get("hardware_result_recorded") is not False:
        fail("hardware plan must not record a hardware result")
    require_phrase(json.dumps(plan), "not true parsed-result data routing", "hardware plan JSON")
    require_phrase(json.dumps(plan), "no parsed table materialization", "hardware plan JSON")
    rows = plan.get("test_rows")
    if not isinstance(rows, list):
        fail("hardware plan test_rows must be a list")
    row_ids = {row.get("row_id") for row in rows if isinstance(row, dict)}
    if row_ids != REQUIRED_ROWS:
        fail("hardware plan row IDs mismatch: " + ", ".join(sorted(str(row) for row in row_ids)))
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware plan rows must be objects")
        if row.get("result") != "NOT_TESTED":
            fail(f"hardware plan row {row.get('row_id')} must be NOT_TESTED")

    require_phrase(plan_md, "Status: TEMPLATE_ONLY", "hardware plan")
    require_phrase(plan_md, "Nunchuk scope for this branch: `NOT_TESTED`", "hardware plan")
    require_phrase(plan_md, "no hardware-result claim", "hardware plan")
    require_phrase(plan_md, "not true parsed-result data routing", "hardware plan")
    require_phrase(plan_md, "no parsed table materialization", "hardware plan")


def main() -> None:
    validate_branch()
    validate_changed_paths()
    validate_source()
    validate_docs_and_reports()
    print("glyph_phase7a_diagnostic_d5a_parse_status_gated_source_owned_runtime_routing: ok")


if __name__ == "__main__":
    main()
