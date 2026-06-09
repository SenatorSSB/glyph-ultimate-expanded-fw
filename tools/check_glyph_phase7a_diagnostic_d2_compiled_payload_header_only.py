#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D2 compiled payload header-only branch."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d2-compiled-payload-header-only"
EXPECTED_DOC_PATH = REPO_ROOT / "docs" / "runtime_config" / "phase7a_diagnostic_d2_compiled_payload_header_only.md"
EXPECTED_REPORT_MD_PATH = (
    REPO_ROOT / "docs" / "runtime_config" /
    "phase7a_diagnostic_d2_compiled_payload_header_only_build_report_2026-06-09.md"
)
EXPECTED_REPORT_JSON_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "fixtures" /
    "phase7a_diagnostic_d2_compiled_payload_header_only_build_report_2026-06-09.json"
)
HARDWARE_PLAN_MD_PATH = REPO_ROOT / "docs" / "calibration" / "glyph_phase7a_diagnostic_d2_compiled_payload_header_only_hardware_plan_2026-06-09.md"
HARDWARE_PLAN_JSON_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_phase7a_diagnostic_d2_compiled_payload_header_only_hardware_plan_2026-06-09.json"
BASELINE_REPORT_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "fixtures" /
    "phase7a_build_size_and_map_baseline_2026-06-08.json"
)
HEADER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayload.hpp"
ULTIMATE_CPP_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
PARSER_HEADER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"

EXPECTED_STATUS_DOC = "DIAGNOSTIC_D2_IMPLEMENTED_PENDING_HARDWARE_RESULT"
EXPECTED_REPORT_STATUS = "diagnostic_d2_build_report_pending_hardware_result"
EXPECTED_REPORT_SCHEMA = "glyph_phase7a_diagnostic_d2_compiled_payload_header_only_build_report"
EXPECTED_D2_MODE = "D2A"
EXPECTED_HARDWARE_STATUS = "not_tested"
EXPECTED_BASELINE_BRANCH = "configurator"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"

FORBIDDEN_SOURCE_PATTERNS = (
    r"ParseUltimateRuntimeConfigPayload",
    r"ResolveActiveRuntimeConfig",
    r"\bkPhase7ACompiledPayloadParseResult\b",
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
)

ALLOWED_CHANGED_PREFIXES = (
    "docs/runtime_config/",
    "docs/calibration/",
    "tools/",
    "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
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
    "NO-RESOLVER-001",
    "NO-STORAGE-001",
    "NO-WRITE-001",
    "NO-FLASH-001",
    "NUNCHUK-001",
)


class Phase7AD2Error(ValueError):
    """Raised when D2 diagnostic guardrails are violated."""


def fail(message: str) -> None:
    raise Phase7AD2Error(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


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


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {rel(path)}")
    return path.read_text(encoding="utf-8")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    # Standard JSON parsing keeps the last duplicate key silently; fixtures must reject ambiguous metadata.
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def forbid_phrase(text: str, phrases: tuple[str, ...], label: str) -> None:
    lowered = text.lower()
    for phrase in phrases:
        if phrase.lower() in lowered:
            fail(f"{label} contains forbidden phrase: {phrase}")


def git_changed_paths(branch: str) -> set[str]:
    paths = set(git_lines(["diff", "--name-only", f"{branch}...HEAD"]))
    for status_line in git_lines(["status", "--short"], preserve_status=True):
        parts = status_line.split(None, 1)
        if len(parts) != 2:
            continue
        status, path = parts
        if status.startswith("??"):
            paths.add(path)
        elif status in {"A", "M", "D", "R", "C", "UU", "MM", "AM", "AD", "??"}:
            paths.add(path)
        else:
            paths.add(path)
    return paths


def validate_branch_scope() -> None:
    branch = git_lines(["branch", "--show-current"])[0]
    if branch != BRANCH:
        fail(f"unexpected branch: {branch!r}, expected {BRANCH!r}")

    for path in sorted(git_changed_paths("configurator")):
        if path.startswith("src/") and path != "src/modes/UltimateRuntimeConfigCompiledPayload.hpp":
            fail(f"this diagnostic branch must not change firmware source file: {path}")
        if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES):
            fail(f"changed path outside allowed D2 scope: {path}")


def parse_compiled_payload_header(text: str) -> tuple[int, str, str, list[int], str]:
    size_match = re.search(r"constexpr size_t kPhase7ACompiledPayloadSize\s*=\s*(\d+);", text)
    if not size_match:
        fail("compiled payload header missing kPhase7ACompiledPayloadSize")
    declared_size = int(size_match.group(1))

    sha_match = re.search(r'constexpr const char kPhase7ACompiledPayloadSha256\[\]\s*=\s*"([0-9a-fA-F]{64})";', text)
    if not sha_match:
        fail("compiled payload header missing kPhase7ACompiledPayloadSha256")
    declared_sha = sha_match.group(1).lower()

    path_match = re.search(
        r'constexpr const char kPhase7ACompiledPayloadFixturePath\[\]\s*=\s*"([^"]+)";',
        text,
    )
    if not path_match:
        fail("compiled payload header missing kPhase7ACompiledPayloadFixturePath")
    fixture_path = path_match.group(1).strip()

    array_match = re.search(
        r"constexpr uint8_t kPhase7ACompiledPayload[^=]*=\s*\{(.*?)\};",
        text,
        flags=re.S,
    )
    if not array_match:
        fail("compiled payload header missing kPhase7ACompiledPayload array")
    array_text = array_match.group(1)
    byte_matches = re.findall(r"0x[0-9a-fA-F]{2}|\\b\\d+\\b", array_text)
    payload = [int(value, 0) for value in byte_matches]
    if len(payload) != declared_size:
        fail(
            f"compiled payload array length mismatch: {len(payload)} != "
            f"{declared_size} (declared)"
        )
    for byte in payload:
        if not (0 <= byte <= 0xFF):
            fail(f"compiled payload byte out of range: {byte}")

    return declared_size, declared_sha, fixture_path, payload, array_match.group(0)


def validate_header_payload() -> None:
    header_text = read_required(HEADER_PATH)
    size, declared_sha, fixture_path, payload, _array_source = parse_compiled_payload_header(header_text)

    fixture = REPO_ROOT / fixture_path
    if not fixture.exists():
        fail(f"compiled payload fixture missing from header path: {fixture_path}")
    fixture_bytes = fixture.read_bytes()

    if len(fixture_bytes) != size:
        fail(
            f"fixture size mismatch: {len(fixture_bytes)} != {size} "
            "declared in header"
        )

    actual_sha = sha256_bytes(fixture_bytes)
    if actual_sha != declared_sha:
        fail(f"fixture sha mismatch: {actual_sha} != {declared_sha}")

    bytes_from_header = bytes(payload)
    if bytes_from_header != fixture_bytes:
        fail("compiled payload header byte array does not match fixture bytes")


def validate_source_guardrails() -> None:
    ultimate = read_required(ULTIMATE_CPP_PATH)
    parser = read_required(PARSER_HEADER_PATH)
    if '#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"' in ultimate:
        fail("Ultimate.cpp must not include compiled payload header in D2A")

    if "ResolveActiveRuntimeConfig" in ultimate:
        fail("Ultimate.cpp must not add ResolveActiveRuntimeConfig in D2A")

    if "kKnownGoodRuntimeConfig" not in ultimate or "ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)" not in ultimate:
        fail("Ultimate.cpp runtime-config selection must retain configurator source-owned baseline path")

    if "kPhase7ACompiledPayloadParseResult" in ultimate:
        fail("global parse result declaration must remain absent from Ultimate.cpp")

    for source_name in ("src/modes/Ultimate.cpp", "src/modes/UltimateRuntimeConfigParser.hpp", "src/modes/UltimateRuntimeConfigCompiledPayload.hpp"):
        source_text = read_required(REPO_ROOT / source_name)
        implementation_text = "\n".join(
            line for line in source_text.splitlines() if not line.lstrip().startswith("//")
        )

        if source_name != "src/modes/UltimateRuntimeConfigParser.hpp":
            if "ParseUltimateRuntimeConfigPayload" in implementation_text:
                fail(
                    f"{source_name} contains forbidden parser call outside parser "
                    "implementation"
                )
            if re.search(r"\bParseResult\b", implementation_text):
                fail(f"{source_name} contains ParseResult outside parser scaffold")

        if re.search(r"\bResolveActiveRuntimeConfig\b", implementation_text):
            fail(f"{source_name} contains ResolveActiveRuntimeConfig")

        for pattern in FORBIDDEN_RUNTIME_PATTERNS:
            if re.search(pattern, implementation_text):
                fail(f"{source_name} contains forbidden runtime/storage/flash symbol: {pattern}")

    src_files_with_header_include = [
        path
        for path in (
            "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
            "src/modes/UltimateRuntimeConfigInterpreter.hpp",
            "src/modes/UltimateRuntimeConfigParser.hpp",
            "src/modes/UltimateIdentityRuntimeTables.hpp",
            "src/modes/Ultimate.cpp",
        )
        if '#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"' in read_required(REPO_ROOT / path)
    ]
    if src_files_with_header_include:
        fail(
            "compiled payload header must be present but not included by firmware translation units in D2A: "
            + ", ".join(src_files_with_header_include)
        )


def validate_documents() -> None:
    doc = read_required(EXPECTED_DOC_PATH)
    require_phrase(doc, f"status: {EXPECTED_STATUS_DOC}", "diagnostic doc")
    require_phrase(doc, f"branch: `{BRANCH}`", "diagnostic doc")
    require_phrase(doc, "D2 mode selected:", "diagnostic doc")
    require_phrase(doc, "D2A", "diagnostic doc")
    require_phrase(doc, "no parser call", "diagnostic doc")
    require_phrase(doc, "no global `ParseResult`", "diagnostic doc")
    require_phrase(doc, "resolveactiveruntimeconfig", "diagnostic doc")
    require_phrase(doc, "no runtime-config storage", "diagnostic doc")
    require_phrase(doc, "no webserial/device write", "diagnostic doc")
    require_phrase(doc, "no firmware flashing automation", "diagnostic doc")
    require_phrase(doc, "No nunchuk validation", "diagnostic doc")
    require_phrase(doc, "hardware result is required", "diagnostic doc")
    forbid_phrase(doc, ("hardware pass", "hardware result is recorded", "nunchuk validation claimed"), "diagnostic doc")

    if "not merge candidate" not in normalize(doc):
        fail("diagnostic doc must mark branch as non-merge candidate evidence state")

    report_md = read_required(EXPECTED_REPORT_MD_PATH)
    require_phrase(report_md, "status: DIAGNOSTIC_D2_BUILD_REPORT_PENDING_HARDWARE_RESULT", "build report")
    require_phrase(report_md, f"branch: `{BRANCH}`", "build report")
    require_phrase(report_md, "diagnostic mode: `D2A`", "build report")
    require_phrase(report_md, "payload-retained-in-image: `false`", "build report")
    require_phrase(report_md, EXPECTED_BUILD_COMMAND, "build report")
    forbid_phrase(report_md, ("hardware pass", "nunchuk validated", "firmware pass"), "build report")

    hardware_plan = read_required(HARDWARE_PLAN_MD_PATH)
    require_phrase(hardware_plan, "Status: TEMPLATE_ONLY", "hardware plan")
    require_phrase(hardware_plan, f"Branch: `{BRANCH}`", "hardware plan")
    for row in REQUIRED_HARDWARE_ROWS:
        if not re.search(rf"\|\s*{re.escape(row)}\s*\|\s*[^|]+\|\s*[^|]+\|\s*NOT_TESTED\s*\|", hardware_plan, flags=re.IGNORECASE):
            fail(f"hardware plan row {row} not present as NOT_TESTED")

    if not HARDWARE_PLAN_JSON_PATH.exists():
        fail(f"hardware plan JSON not found: {rel(HARDWARE_PLAN_JSON_PATH)}")

    report_json = load_json(EXPECTED_REPORT_JSON_PATH)
    hardware_plan_json = load_json(HARDWARE_PLAN_JSON_PATH)

    if hardware_plan_json.get("status") != "TEMPLATE_ONLY":
        fail("hardware plan JSON must be TEMPLATE_ONLY")

    if hardware_plan_json.get("branch") != BRANCH:
        fail(f"hardware plan JSON branch mismatch: {hardware_plan_json.get('branch')!r} != {BRANCH!r}")

    test_rows = hardware_plan_json.get("test_rows")
    if not isinstance(test_rows, list):
        fail("hardware plan JSON test_rows must be a list")
    row_ids = {str(row.get("row_id")) for row in test_rows if isinstance(row, dict) and "row_id" in row}
    missing = [row_id for row_id in REQUIRED_HARDWARE_ROWS if row_id not in row_ids]
    if missing:
        fail(f"hardware plan JSON missing required rows: {missing}")
    for row in test_rows:
        if not isinstance(row, dict):
            fail("hardware plan JSON test_rows entries must be objects")
        if row.get("result", "").upper() != "NOT_TESTED":
            fail(f"hardware plan row {row.get('row_id')} is not NOT_TESTED")

    if report_json.get("status") != EXPECTED_REPORT_STATUS:
        fail(f"build report JSON status mismatch: {report_json.get('status')!r}")

    if report_json.get("branch") != BRANCH:
        fail(f"build report JSON branch mismatch: {report_json.get('branch')!r} != {BRANCH!r}")

    if report_json.get("diagnostic_mode") != EXPECTED_D2_MODE:
        fail(f"build report diagnostic_mode mismatch: {report_json.get('diagnostic_mode')!r}")

    if report_json.get("payload_bytes_retained_in_firmware_image") is not False:
        fail("build report must keep payload_bytes_retained_in_firmware_image false for D2A")

    if report_json.get("baseline_branch") != EXPECTED_BASELINE_BRANCH:
        fail(f"build report baseline branch mismatch: {report_json.get('baseline_branch')!r}")

    if report_json.get("build_command") != EXPECTED_BUILD_COMMAND:
        fail(f"build report build command mismatch: {report_json.get('build_command')!r}")

    if report_json.get("hardware_result_claimed") is not False:
        fail("build report must not claim hardware result")

    if report_json.get("nunchuk_status") != EXPECTED_HARDWARE_STATUS:
        fail(f"build report nunchuk status must be {EXPECTED_HARDWARE_STATUS!r}")

    if report_json.get("runtime_behavior_changed") is not False:
        fail("build report must set runtime_behavior_changed false")

    if report_json.get("hardware_required") is not True:
        fail("build report should require hardware before conclusion")

    if not isinstance(report_json.get("caveats"), list) or "no runtime resolver" not in " ".join(
        str(entry).lower() for entry in report_json["caveats"]
    ):
        fail("build report caveats must include no runtime resolver")

    artifacts = report_json.get("artifacts")
    deltas = report_json.get("artifacts_deltas_vs_baseline")
    if not isinstance(artifacts, list) or not isinstance(deltas, list):
        fail("build report must include artifacts and artifacts_deltas_vs_baseline as lists")

    baseline = load_json(BASELINE_REPORT_PATH)
    baseline_artifacts = {
        str(item.get("artifact_type")): item
        for item in baseline.get("artifacts", [])
        if isinstance(item, dict)
    }
    delta_map = {str(item.get("artifact_type")): item for item in deltas if isinstance(item, dict)}
    for item in artifacts:
        if not isinstance(item, dict):
            fail("each artifacts entry must be an object")
        artifact_type = item.get("artifact_type")
        if artifact_type not in ("uf2", "elf", "bin"):
            fail(f"unexpected artifact_type: {artifact_type!r}")
        size_bytes = item.get("size_bytes")
        if not isinstance(size_bytes, int) or size_bytes <= 0:
            fail(f"artifact size_bytes must be positive int: {artifact_type!r}")
        sha = item.get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            fail(f"artifact sha256 must be 64-char lowercase hex for {artifact_type!r}")
        baseline_item = baseline_artifacts.get(str(artifact_type))
        if not baseline_item:
            fail(f"baseline artifact missing type {artifact_type!r}")
        delta_item = delta_map.get(str(artifact_type))
        if not isinstance(delta_item, dict):
            fail(f"artifact delta missing type {artifact_type!r}")
        baseline_size = int(baseline_item.get("size_bytes", 0))
        expected_delta = size_bytes - baseline_size
        if delta_item.get("baseline_size_bytes") != baseline_size:
            fail(
                f"{artifact_type} baseline_size_bytes mismatch: "
                f"{delta_item.get('baseline_size_bytes')!r} != {baseline_size!r}"
            )
        if delta_item.get("size_delta_bytes") != expected_delta:
            fail(
                f"{artifact_type} size_delta_bytes mismatch: "
                f"{delta_item.get('size_delta_bytes')!r} != {expected_delta!r}"
            )


def validate_no_global_parser_result_and_calls() -> None:
    parse_source = read_required(PARSER_HEADER_PATH)
    for path in ("src/modes/Ultimate.cpp", "src/modes/UltimateRuntimeConfigInterpreter.hpp", "src/modes/UltimateRuntimeConfigCompiledPayload.hpp", "src/modes/UltimateIdentityRuntimeTables.hpp"):
        text = read_required(REPO_ROOT / path)
        implementation = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))
        for pattern in FORBIDDEN_SOURCE_PATTERNS:
            if path != "src/modes/UltimateRuntimeConfigParser.hpp" and re.search(pattern, implementation):
                fail(f"{path} contains forbidden parser/result symbol: {pattern}")

        if path == "src/modes/UltimateRuntimeConfigCompiledPayload.hpp" and "ParseUltimateRuntimeConfigPayload" in implementation:
            fail("payload header must not call ParseUltimateRuntimeConfigPayload")

        if path != "src/modes/UltimateRuntimeConfigParser.hpp":
            if "ParseResult" in implementation:
                fail(f"{path} must not reference ParseResult outside parser scaffold")


def validate_ultimate_no_diff_from_configurator() -> None:
    try:
        base_text = subprocess.run(
            ["git", "show", "configurator:src/modes/Ultimate.cpp"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        fail(f"unable to inspect configurator::src/modes/Ultimate.cpp: {exc}")
    if base_text.returncode != 0:
        fail("git show configurator:src/modes/Ultimate.cpp failed")

    if read_required(ULTIMATE_CPP_PATH) != base_text.stdout:
        fail("Ultimate.cpp differs from configurator; D2 must not modify runtime path")

    # Parser scaffold is expected to already exist and be unchanged for this branch.
    base_parser = subprocess.run(
        ["git", "show", "configurator:src/modes/UltimateRuntimeConfigParser.hpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if base_parser.returncode != 0:
        fail("git show configurator:src/modes/UltimateRuntimeConfigParser.hpp failed")
    if parser_text := read_required(PARSER_HEADER_PATH):
        if parser_text != base_parser.stdout:
            # Conservative: this branch should not alter parser behavior for D2A.
            fail("parser scaffold changed from configurator unexpectedly in D2A")


def main() -> int:
    try:
        validate_branch_scope()
        validate_header_payload()
        validate_source_guardrails()
        validate_no_global_parser_result_and_calls()
        validate_documents()
        validate_ultimate_no_diff_from_configurator()
    except (OSError, ValueError, Phase7AD2Error) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"branch={BRANCH}")
    print(f"diagnostic_doc={EXPECTED_DOC_PATH.relative_to(REPO_ROOT)}")
    print(f"build_report_md={EXPECTED_REPORT_MD_PATH.relative_to(REPO_ROOT)}")
    print(f"build_report_json={EXPECTED_REPORT_JSON_PATH.relative_to(REPO_ROOT)}")
    print(f"hardware_plan_md={HARDWARE_PLAN_MD_PATH.relative_to(REPO_ROOT)}")
    print(f"hardware_plan_json={HARDWARE_PLAN_JSON_PATH.relative_to(REPO_ROOT)}")
    print(f"compiled_payload_header={HEADER_PATH.relative_to(REPO_ROOT)}")
    print("diagnostic_mode=D2A")
    print("payload_retained_in_image=false")
    print("runtime_behavior_changed=false")
    print("hardware_required=true")
    print("hardware_result_claimed=false")
    print("nunchuk_status=not_tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
