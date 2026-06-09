#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D4 runtime-resolver-only branch."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d4-runtime-resolver-only"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "phase7a_diagnostic_d4_runtime_resolver_only.md"
)
REPORT_MD_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "phase7a_diagnostic_d4_runtime_resolver_only_build_report_2026-06-09.md"
)
REPORT_JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "fixtures"
    / "phase7a_diagnostic_d4_runtime_resolver_only_build_report_2026-06-09.json"
)
HARDWARE_PLAN_MD_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_plan_2026-06-09.md"
)
HARDWARE_PLAN_JSON_PATH = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_plan_2026-06-09.json"
)
BASELINE_REPORT_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "fixtures"
    / "phase7a_build_size_and_map_baseline_2026-06-08.json"
)

ULTIMATE_CPP_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
PARSER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"
INTERPRETER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigInterpreter.hpp"
IDENTITY_PATH = REPO_ROOT / "src" / "modes" / "UltimateIdentityRuntimeTables.hpp"

HEADER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayload.hpp"
ANCHOR_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayloadAnchor.cpp"

EXPECTED_STATUS_DOC = "DIAGNOSTIC_D4_IMPLEMENTED_PENDING_HARDWARE_RESULT"
EXPECTED_REPORT_STATUS = "DIAGNOSTIC_D4_BUILD_REPORT_PENDING_HARDWARE_RESULT"
EXPECTED_JSON_STATUS = "diagnostic_d4_build_report_pending_hardware_result"
EXPECTED_REPORT_SCHEMA = "glyph_phase7a_diagnostic_d4_runtime_resolver_only_build_report"
EXPECTED_REPORT_MODE = "D4"
EXPECTED_BASELINE_BRANCH = "configurator"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_HARDWARE_STATUS = "not_tested"

ALLOWED_CHANGED_PREFIXES = (
    "docs/runtime_config/",
    "docs/calibration/",
    "tools/",
    "src/modes/",
)
ALLOWED_CHANGED_SOURCE_PATHS = {
    "src/modes/Ultimate.cpp",
    "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
    "src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp",
}

FORBIDDEN_SOURCE_PATTERNS = (
    r"RuntimeConfigCompiledPayload",
    r"kPhase7ACompiledPayload",
    r"kPhase7ACompiledPayloadParseResult",
    r"\.incbin",
)

FORBIDDEN_RUNTIME_PATTERNS = (
    r"\bPersistence\b",
    r"\bLittleFS\b",
    r"\bEEPROM\b",
    r"\bLoadRuntimeConfig\b",
    r"\bSaveRuntimeConfig\b",
    r"\bconfig\.bin\b",
    r"\bWebSerial\b",
    r"\bflash_uf2\b",
    r"\breboot_bootloader\b",
    r"\bfirmware flashing\b",
    r"\bruntime\-config write\b",
)

REQUIRED_HARDWARE_ROWS = (
    "BOOT-001",
    "BASELINE-001",
    "RF5-001",
    "RF6-001",
    "ORDINARY-DIR-001",
    "NEUTRAL-001",
    "UNRELATED-BUTTONS-001",
    "MODIFIERS-001",
    "NO-PARSER-001",
    "NO-PAYLOAD-001",
    "NO-GLOBAL-PARSE-001",
    "RESOLVER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
)


class Phase7AD4DiagnosticError(ValueError):
    """Raised when D4 checker constraints are violated."""


def fail(message: str) -> None:
    raise Phase7AD4DiagnosticError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


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
        fail(f"{rel(path)} must be a JSON object")
    return payload


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize_whitespace(phrase) not in normalize_whitespace(text):
        fail(f"{label} missing required phrase: {phrase}")


def forbid_phrase(text: str, phrase: str, label: str) -> None:
    if phrase.lower() in text.lower():
        fail(f"{label} contains forbidden phrase: {phrase}")


def git_lines(args: list[str], *, accept_failure: bool = False) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 and not accept_failure:
        fail(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def git_changed_paths(branch: str) -> set[str]:
    paths: set[str] = set(git_lines(["diff", "--name-status", f"{branch}...HEAD"]))
    # Fallback for uncommitted worktree state and to capture new files.
    for status_line in git_lines(["status", "--short"], accept_failure=True):
        if not status_line:
            continue
        status, _, path = status_line.partition(" ")
        if "->" in path:
            path = path.split(" -> ")[-1].strip()
        paths.add(path)
    resolved: set[str] = set()
    for entry in paths:
        if not entry:
            continue
        parts = entry.split("\t")
        if len(parts) == 2:
            resolved_path = parts[1]
        elif entry.startswith("??"):
            resolved_path = entry.split("??", 1)[1].strip()
        else:
            # Example lines from name-status can be 'M\tpath' or 'D\tpath'
            tokens = entry.split(None, 1)
            resolved_path = tokens[1] if len(tokens) == 2 else tokens[0]
        if resolved_path:
            resolved.add(resolved_path)
    return resolved


def extract_function(text: str, name: str) -> str:
    pattern = rf"void\s+Ultimate::{re.escape(name)}\s*\([^\)]*\)\s*\{{"
    match = re.search(pattern, text)
    if not match:
        fail(f"could not locate Ultimate::{name} in text")
    start = match.start()
    open_brace = text.index("{", match.start())
    depth = 0
    index = open_brace
    while index < len(text):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
        index += 1
    fail(f"unbalanced braces while extracting Ultimate::{name}")


def validate_branch_scope() -> None:
    branch = git_lines(["branch", "--show-current"])[0]
    if branch != BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {BRANCH!r}")

    changed = git_changed_paths("configurator")
    if not changed:
        fail("no changed paths detected")

    source_changes = {path for path in changed if path.startswith("src/")}
    for path in source_changes:
        if path not in ALLOWED_CHANGED_SOURCE_PATHS:
            fail(f"unexpected source change under src/: {path}")

    for path in sorted(changed):
        if path.startswith("docs/") or path.startswith("tools/") or path.startswith("src/"):
            continue
        fail(f"changed path outside required D4 scope: {path}")

    if source_changes != {
        "src/modes/Ultimate.cpp",
        "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
        "src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp",
    }:
        fail(
            "source changes should be Ultimate.cpp plus deliberate payload-header/anchor removals"
            f" (got: {sorted(source_changes)})"
        )


def validate_no_payload_artifacts() -> None:
    if HEADER_PATH.exists():
        fail("compiled payload header file must be removed")
    if ANCHOR_PATH.exists():
        fail("payload anchor file must be removed")


def validate_resolver_pattern() -> None:
    ultimate_text = read_required(ULTIMATE_CPP_PATH)
    if "#include \"modes/UltimateRuntimeConfigCompiledPayload.hpp\"" in ultimate_text:
        fail("Ultimate.cpp must not include compiled payload header")

    defs = re.findall(
        r"const\s+RuntimeConfigView&\s+ResolveActiveRuntimeConfig\s*\([^\)]*\)\s*\{([^}]*)\}",
        ultimate_text,
        flags=re.S,
    )
    if len(defs) != 1:
        fail(f"expected exactly one ResolveActiveRuntimeConfig definition, found {len(defs)}")

    body = defs[0]
    if "kSourceOwnedCurrentBaselineRuntimeConfig" not in body:
        fail("resolver body must reference kSourceOwnedCurrentBaselineRuntimeConfig")
    if "kKnownGoodRuntimeConfig" not in body:
        fail("resolver body must reference kKnownGoodRuntimeConfig")
    if "ValidateRuntimeConfigView" not in body:
        fail("resolver body must validate kSourceOwnedCurrentBaselineRuntimeConfig")
    if "?" not in body or ":" not in body:
        fail("resolver body must contain ternary fallback expression")

    call_count = len(re.findall(r"\bResolveActiveRuntimeConfig\s*\(", ultimate_text))
    if call_count != 2:
        fail(f"expected one resolver definition and one callsite, found {call_count} mentions")

    if re.search(
        r"const\s+RuntimeConfigView\s*&\s*runtime_config\s*=\s*ResolveActiveRuntimeConfig\s*\(\)\s*;",
        ultimate_text,
    ) is None:
        fail("UpdateAnalogOutputs must call ResolveActiveRuntimeConfig for runtime_config binding")


def validate_no_forbidden_source_symbols() -> None:
    files_to_check = [ULTIMATE_CPP_PATH, INTERPRETER_PATH, IDENTITY_PATH]
    for path in files_to_check:
        text = read_required(path)
        implementation = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("//")
        )
        for pattern in FORBIDDEN_SOURCE_PATTERNS:
            if re.search(pattern, implementation):
                fail(f"forbidden source symbol in {rel(path)}: {pattern}")
        for pattern in FORBIDDEN_RUNTIME_PATTERNS:
            if re.search(pattern, implementation):
                fail(f"forbidden storage/write/flash symbol in {rel(path)}: {pattern}")

        if "ParseUltimateRuntimeConfigPayload" in implementation:
            fail(f"ParseUltimateRuntimeConfigPayload appears in {rel(path)}")

        if re.search(r"\bParseResult\b", implementation) and path != PARSER_PATH:
            fail(f"ParseResult should not appear outside parser header in {rel(path)}")


def validate_source_parser_symbol_scope() -> None:
    parser_text = read_required(PARSER_PATH)
    allowed_call = "ParseUltimateRuntimeConfigPayload"
    if allowed_call not in parser_text:
        fail("parser header missing ParseUltimateRuntimeConfigPayload symbol")

    if parser_text.count(allowed_call) == 0:
        fail("parser header should contain ParseUltimateRuntimeConfigPayload")

    for path in [ULTIMATE_CPP_PATH, INTERPRETER_PATH, IDENTITY_PATH]:
        text = read_required(path)
        for match in re.finditer(r"ParseUltimateRuntimeConfigPayload\s*\(", text):
            fail(
                f"ParseUltimateRuntimeConfigPayload call detected outside parser in {rel(path)}:"
                f" {match.group(0)!r}"
            )


def validate_analog_digital_path_guardrails() -> None:
    current_text = read_required(ULTIMATE_CPP_PATH)

    update_digital_current = extract_function(current_text, "UpdateDigitalOutputs")
    base_digital = subprocess.run(
        ["git", "show", "configurator:src/modes/Ultimate.cpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if base_digital.returncode != 0:
        fail("unable to read configurator:src/modes/Ultimate.cpp")

    update_digital_base = extract_function(base_digital.stdout, "UpdateDigitalOutputs")
    if update_digital_current != update_digital_base:
        fail("UpdateDigitalOutputs must remain unchanged by this diagnostic")

    diff_text = subprocess.run(
        ["git", "diff", "configurator...HEAD", "--", "src/modes/Ultimate.cpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    for line in diff_text.splitlines():
        if not line:
            continue
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            if re.search(r"\brf5\b", line) or re.search(r"\brf6\b", line):
                fail("Update changed rf5/rf6 source lines; they must stay unchanged")


def validate_documents_and_artifacts() -> None:
    doc_text = read_required(DOC_PATH)
    require_phrase(doc_text, f"status: {EXPECTED_STATUS_DOC}", "diagnostic document")
    require_phrase(doc_text, f"diagnostic branch: `{BRANCH}`", "diagnostic document")
    require_phrase(doc_text, "no parser call", "diagnostic document")
    require_phrase(doc_text, "no compiled payload header", "diagnostic document")
    require_phrase(doc_text, "no payload anchor", "diagnostic document")
    require_phrase(doc_text, "not hardware-result", "diagnostic document")
    require_phrase(doc_text, "evidence-producing only", "diagnostic document")

    report_md = read_required(REPORT_MD_PATH)
    require_phrase(report_md, f"status: {EXPECTED_REPORT_STATUS}", "build report markdown")
    require_phrase(report_md, f"branch: `{BRANCH}`", "build report markdown")
    require_phrase(report_md, "diagnostic mode: `D4`", "build report markdown")
    require_phrase(report_md, "payload-retained-in-image: `false`", "build report markdown")
    require_phrase(report_md, f"build command: `{EXPECTED_BUILD_COMMAND}`", "build report markdown")
    require_phrase(report_md, "hardware result required before conclusions", "build report markdown")

    hardware_plan_text = read_required(HARDWARE_PLAN_MD_PATH)
    require_phrase(hardware_plan_text, f"Branch: `{BRANCH}`", "hardware plan markdown")
    require_phrase(hardware_plan_text, "Status: TEMPLATE_ONLY", "hardware plan markdown")
    for row in REQUIRED_HARDWARE_ROWS:
        pattern = rf"\|\s*{re.escape(row)}\s*\|[^\n]*\|[^\n]*\|\s*NOT_TESTED\s*\|"
        if not re.search(pattern, hardware_plan_text, flags=re.IGNORECASE):
            fail(f"hardware plan row missing/not tested: {row}")

    hardware_plan = load_json(HARDWARE_PLAN_JSON_PATH)
    if hardware_plan.get("schema_name") != "glyph_phase7a_diagnostic_d4_runtime_resolver_only_hardware_plan":
        fail("hardware plan schema_name mismatch")
    if hardware_plan.get("status") != "TEMPLATE_ONLY":
        fail("hardware plan status must be TEMPLATE_ONLY")
    if hardware_plan.get("branch") != BRANCH:
        fail("hardware plan branch mismatch")
    if hardware_plan.get("hardware_result_recorded") is not False:
        fail("hardware plan must not record hardware result")
    if not isinstance(hardware_plan.get("test_rows"), list):
        fail("hardware plan test_rows must be a list")
    test_rows = hardware_plan["test_rows"]
    row_ids = {str(item.get("row_id")) for item in test_rows if isinstance(item, dict)}
    for row in REQUIRED_HARDWARE_ROWS:
        if row not in row_ids:
            fail(f"hardware plan JSON missing row: {row}")
    for row in test_rows:
        if not isinstance(row, dict):
            fail("hardware plan row entry must be object")
        if str(row.get("result", "")).upper() != "NOT_TESTED":
            fail(f"hardware plan row should remain NOT_TESTED: {row.get('row_id')}")

    if hardware_plan.get("intent", {}).get("non_claims") is None:
        fail("hardware plan intent non_claims missing")

    report = load_json(REPORT_JSON_PATH)
    if report.get("schema_name") != EXPECTED_REPORT_SCHEMA:
        fail("build report schema_name mismatch")
    if report.get("status") != EXPECTED_JSON_STATUS:
        fail("build report status mismatch")
    if report.get("branch") != BRANCH:
        fail("build report branch mismatch")
    if report.get("baseline_branch") != EXPECTED_BASELINE_BRANCH:
        fail("build report baseline branch mismatch")
    if report.get("diagnostic_mode") != EXPECTED_REPORT_MODE:
        fail("build report diagnostic mode mismatch")
    if report.get("resolver_added") is not True:
        fail("build report must set resolver_added true")
    if report.get("parser_called") is not False:
        fail("build report must set parser_called false")
    if report.get("global_parse_result_added") is not False:
        fail("build report must set global_parse_result_added false")
    if report.get("compiled_payload_added") is not False:
        fail("build report must set compiled_payload_added false")
    if report.get("payload_bytes_retained_in_firmware_image") is not False:
        fail("build report must set payload_bytes_retained_in_firmware_image false")
    if report.get("ultimate_cpp_changed") is not True:
        fail("build report must set ultimate_cpp_changed true")
    if report.get("runtime_behavior_changed_intended") is not False:
        fail("build report must set runtime_behavior_changed_intended false")
    if report.get("hardware_required") is not True:
        fail("build report must mark hardware_required true")
    if report.get("hardware_result_claimed") is not False:
        fail("build report must not claim hardware result")
    if report.get("nunchuk_status") != EXPECTED_HARDWARE_STATUS:
        fail("nunchuk_status must be not_tested")
    if report.get("build_command") != EXPECTED_BUILD_COMMAND:
        fail("build report build command mismatch")
    if not isinstance(report.get("commit_sha"), str) or not re.fullmatch(r"[0-9a-fA-F]{40}", report["commit_sha"]):
        fail("build report commit_sha invalid")
    if report.get("runtime_behavior_changed") is not False:
        fail("build report runtime_behavior_changed must be false")

    artifacts = report.get("artifacts")
    if not isinstance(artifacts, list):
        fail("report artifacts must be list")

    artifact_paths = {
        "uf2": REPO_ROOT / ".pio/build/glyph_mk6/firmware.uf2",
        "elf": REPO_ROOT / ".pio/build/glyph_mk6/firmware.elf",
        "bin": REPO_ROOT / ".pio/build/glyph_mk6/firmware.bin",
    }

    report_map: dict[str, dict[str, Any]] = {}
    for entry in artifacts:
        if not isinstance(entry, dict):
            fail("each artifact entry must be object")
        artifact_type = str(entry.get("artifact_type"))
        if artifact_type not in {"uf2", "elf", "bin"}:
            fail(f"unexpected artifact type: {artifact_type}")
        if not isinstance(entry.get("path"), str) or not entry.get("path"):
            fail(f"artifact {artifact_type} must include path")
        if entry.get("available") is not True:
            fail(f"artifact {artifact_type} should be available")
        if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] <= 0:
            fail(f"artifact {artifact_type} size_bytes invalid")
        if not isinstance(entry.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-f]{64}", str(entry.get("sha256"))
        ):
            fail(f"artifact {artifact_type} sha256 invalid")

        expected = artifact_paths.get(artifact_type)
        if expected and not expected.exists():
            fail(f"artifact file missing: {expected}")
        if expected and expected.exists():
            actual_sha = hashlib.sha256(expected.read_bytes()).hexdigest()
            if actual_sha != str(entry["sha256"]):
                fail(f"artifact sha mismatch for {artifact_type}")
            if expected.stat().st_size != int(entry["size_bytes"]):
                fail(f"artifact size mismatch for {artifact_type}")

        report_map[artifact_type] = entry

    if set(report_map.keys()) != {"uf2", "elf", "bin"}:
        fail("report artifacts must include uf2, elf, and bin")

    baseline = load_json(BASELINE_REPORT_PATH)
    baseline_artifacts = {
        str(item.get("artifact_type")): item
        for item in baseline.get("artifacts", [])
        if isinstance(item, dict) and str(item.get("artifact_type")) in {"uf2", "elf", "bin"}
    }
    deltas = report.get("artifacts_deltas_vs_baseline")
    if not isinstance(deltas, list) or len(deltas) != 3:
        fail("artifacts_deltas_vs_baseline must include 3 entries")

    for item in deltas:
        if not isinstance(item, dict):
            fail("artifact delta entries must be objects")
        artifact_type = str(item.get("artifact_type"))
        if artifact_type not in {"uf2", "elf", "bin"}:
            fail(f"unexpected delta artifact_type: {artifact_type}")
        baseline_entry = baseline_artifacts.get(artifact_type)
        if not baseline_entry:
            fail(f"missing baseline artifact entry for {artifact_type}")
        if not isinstance(item.get("size_delta_bytes"), int):
            fail(f"delta size for {artifact_type} must be integer")
        report_size = report_map[artifact_type]["size_bytes"]
        expected_delta = report_size - int(baseline_entry["size_bytes"])
        if item.get("size_delta_bytes") != expected_delta:
            fail(f"delta size mismatch for {artifact_type}")
        if item.get("baseline_size_bytes") != baseline_entry.get("size_bytes"):
            fail(f"baseline size mismatch in delta for {artifact_type}")
        if item.get("baseline_sha256") != baseline_entry.get("sha256"):
            fail(f"baseline sha mismatch in delta for {artifact_type}")

    if report.get("map_file_available") is not False:
        fail("map_file_available must be false")
    if report.get("elf_file_available") is not True:
        fail("elf_file_available must be true")
    if report.get("uf2_file_available") is not True:
        fail("uf2_file_available must be true")
    if report.get("bin_file_available") is not True:
        fail("bin_file_available must be true")

def validate_no_hardware_claims() -> None:
    for path in (DOC_PATH, REPORT_MD_PATH, HARDWARE_PLAN_MD_PATH):
        text = read_required(path).lower()
        if "hardware pass" in text and "no hardware pass" not in text and "not a hardware-result" not in text:
            fail(f"forbidden hardware pass claim in {rel(path)}")


def main() -> int:
    try:
        validate_branch_scope()
        validate_no_payload_artifacts()
        validate_resolver_pattern()
        validate_no_forbidden_source_symbols()
        validate_source_parser_symbol_scope()
        validate_analog_digital_path_guardrails()
        validate_documents_and_artifacts()
        validate_no_hardware_claims()
    except (
        FileNotFoundError,
        OSError,
        ValueError,
        subprocess.CalledProcessError,
        Phase7AD4DiagnosticError,
    ) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"diagnostic_doc={rel(DOC_PATH)}")
    print(f"build_report_md={rel(REPORT_MD_PATH)}")
    print(f"build_report_json={rel(REPORT_JSON_PATH)}")
    print(f"hardware_plan={rel(HARDWARE_PLAN_JSON_PATH)}")
    print("resolver_added=true")
    print("parser_called=false")
    print("global_parse_result=false")
    print("compiled_payload_added=false")
    print("runtime_behavior_changed=false")
    print("hardware_required=true")
    print("hardware_result_claimed=false")
    print("nunchuk_status=not_tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
