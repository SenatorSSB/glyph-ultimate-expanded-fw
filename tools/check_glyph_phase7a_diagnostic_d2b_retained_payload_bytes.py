#!/usr/bin/env python3
"""Validate the Phase 7A Diagnostic D2B payload-retention artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRANCH = "phase7a-diagnostic-d2b-retained-payload-bytes"
RESULT_BRANCH = "phase7a-diagnostic-d2b-retained-payload-bytes-hardware-result"
DOC_PATH = (
    REPO_ROOT / "docs" / "runtime_config" /
    "phase7a_diagnostic_d2b_retained_payload_bytes.md"
)
REPORT_MD_PATH = (
    REPO_ROOT / "docs" / "runtime_config" /
    "phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md"
)
REPORT_JSON_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "fixtures" /
    "phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.json"
)
HARDWARE_PLAN_MD_PATH = (
    REPO_ROOT / "docs" / "calibration" /
    "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_plan_2026-06-09.md"
)
HARDWARE_PLAN_JSON_PATH = (
    REPO_ROOT / "docs" / "calibration" / "fixtures" /
    "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_plan_2026-06-09.json"
)
BASELINE_REPORT_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "fixtures" /
    "phase7a_build_size_and_map_baseline_2026-06-08.json"
)
D2A_REPORT_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "fixtures" /
    "phase7a_diagnostic_d2_compiled_payload_header_only_build_report_2026-06-09.json"
)
HEADER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayload.hpp"
ANCHOR_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigCompiledPayloadAnchor.cpp"
ULTIMATE_CPP_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
PARSER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigParser.hpp"
INTERPRETER_PATH = REPO_ROOT / "src" / "modes" / "UltimateRuntimeConfigInterpreter.hpp"
IDENTITY_PATH = REPO_ROOT / "src" / "modes" / "UltimateIdentityRuntimeTables.hpp"

EXPECTED_STATUS_DOC = "DIAGNOSTIC_D2B_IMPLEMENTED_PENDING_HARDWARE_RESULT"
EXPECTED_REPORT_STATUS = "diagnostic_d2b_build_report_pending_hardware_result"
EXPECTED_REPORT_SCHEMA = "glyph_phase7a_diagnostic_d2b_retained_payload_bytes_build_report"
EXPECTED_REPORT_D2_MODE = "D2B"
EXPECTED_BASELINE_BRANCH = "configurator"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_COMMIT_PATH = "docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin"
EXPECTED_SHA = "0f668127c270fb7be382677f68a528d1e1d18829254bb7f16fa901e30414bc32"
EXPECTED_SIZE = 530
PAYLOAD_FIXTURE_PATH = REPO_ROOT / EXPECTED_COMMIT_PATH
ARTIFACT_SCAN_PATHS = {
    "bin": REPO_ROOT / ".pio" / "build" / "glyph_mk6" / "firmware.bin",
    "elf": REPO_ROOT / ".pio" / "build" / "glyph_mk6" / "firmware.elf",
    "uf2": REPO_ROOT / ".pio" / "build" / "glyph_mk6" / "firmware.uf2",
}

ALLOWED_CHANGED_PREFIXES = (
    "src/modes/UltimateRuntimeConfigCompiledPayload.hpp",
    "src/modes/UltimateRuntimeConfigCompiledPayloadAnchor.cpp",
    "docs/runtime_config/",
    "docs/calibration/",
    "tools/",
)

FORBIDDEN_SOURCE_PATTERNS = (
    r"ParseUltimateRuntimeConfigPayload",
    r"\bResolveActiveRuntimeConfig\b",
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
    r"\breboot_bootloader\b",
    r"\bflash_uf2\b",
    r"\bfirmware flashing\b",
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


class Phase7AD2BError(ValueError):
    """Raised when D2B guardrails are violated."""


def fail(message: str) -> None:
    raise Phase7AD2BError(message)


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
        fail(f"{rel(path)} must contain a JSON object")
    return payload


def find_all_offsets(data: bytes, needle: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(needle, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def scan_payload_sequence() -> dict[str, dict[str, Any]]:
    if not PAYLOAD_FIXTURE_PATH.exists():
        fail(f"payload fixture missing: {rel(PAYLOAD_FIXTURE_PATH)}")

    payload = PAYLOAD_FIXTURE_PATH.read_bytes()
    if len(payload) != EXPECTED_SIZE:
        fail(f"payload fixture size mismatch: {len(payload)} != {EXPECTED_SIZE}")
    actual_sha = hashlib.sha256(payload).hexdigest()
    if actual_sha != EXPECTED_SHA:
        fail(f"payload fixture sha mismatch: {actual_sha} != {EXPECTED_SHA}")

    scan: dict[str, dict[str, Any]] = {}
    for artifact_type, path in ARTIFACT_SCAN_PATHS.items():
        if not path.exists():
            scan[artifact_type] = {
                "path": rel(path),
                "available": False,
                "found": False,
                "offsets": [],
            }
            continue

        data = path.read_bytes()
        offsets = find_all_offsets(data, payload)
        scan[artifact_type] = {
            "path": rel(path),
            "available": True,
            "found": bool(offsets),
            "offsets": offsets,
            "offsets_hex": [hex(offset) for offset in offsets],
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    if not (scan["bin"]["found"] or scan["elf"]["found"]):
        fail("full payload byte sequence not found in firmware.bin or firmware.elf")
    return scan


def expected_offset_entries(
    sequence_scan: dict[str, dict[str, Any]],
) -> list[dict[str, int | str]]:
    entries: list[dict[str, int | str]] = []
    for artifact_type in ("bin", "elf", "uf2"):
        for offset in sequence_scan[artifact_type]["offsets"]:
            entries.append({"artifact_type": artifact_type, "offset": offset})
    return entries


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require_phrase(text: str, phrase: str, label: str) -> None:
    if normalize(phrase) not in normalize(text):
        fail(f"{label} missing required phrase: {phrase}")


def forbid_phrase(text: str, phrase: str, label: str) -> None:
    if phrase.lower() in text.lower():
        fail(f"{label} contains forbidden phrase: {phrase}")


def git_changed_paths(branch: str) -> set[str]:
    paths = set(
        subprocess.run(
            ["git", "diff", "--name-only", f"{branch}...HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.splitlines()
    )
    for status_line in subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.splitlines():
        status_line = status_line.strip()
        if not status_line:
            continue
        parts = status_line.split(None, 1)
        if len(parts) != 2:
            continue
        path = parts[1]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return {p.strip() for p in paths if p.strip()}


def validate_branch_scope() -> None:
    branch = (
        subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        .stdout.strip()
    )
    if branch not in {BRANCH, RESULT_BRANCH}:
        fail(
            "unexpected branch: "
            f"{branch!r}, expected {BRANCH!r} or {RESULT_BRANCH!r}"
        )

    for path in sorted(git_changed_paths("configurator")):
        if path.startswith("src/") and path not in {
            str(HEADER_PATH.relative_to(REPO_ROOT)),
            str(ANCHOR_PATH.relative_to(REPO_ROOT)),
        }:
            fail(
                "this branch must not change firmware source files outside "
                "payload-retention files: "
                + path
            )
        if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES):
            fail(f"changed path outside D2B scope: {path}")


def parse_compiled_payload_header() -> None:
    header_text = read_required(HEADER_PATH)
    size_match = re.search(
        r"constexpr size_t kPhase7ACompiledPayloadSize\s*=\s*(\d+);",
        header_text,
    )
    if not size_match:
        fail("compiled payload header missing kPhase7ACompiledPayloadSize")
    declared_size = int(size_match.group(1))
    if declared_size != EXPECTED_SIZE:
        fail(
            f"payload size mismatch: expected {EXPECTED_SIZE}, got {declared_size}"
        )

    sha_match = re.search(
        r'constexpr const char kPhase7ACompiledPayloadSha256\[\]\s*=\s*"([0-9a-fA-F]{64})";',
        header_text,
    )
    if not sha_match:
        fail("compiled payload header missing kPhase7ACompiledPayloadSha256")
    declared_sha = sha_match.group(1).lower()
    if declared_sha != EXPECTED_SHA:
        fail(f"payload sha mismatch: expected {EXPECTED_SHA}, got {declared_sha}")

    path_match = re.search(
        r'constexpr const char kPhase7ACompiledPayloadFixturePath\[\]\s*=\s*"([^"]+)";',
        header_text,
    )
    if not path_match:
        fail("compiled payload header missing kPhase7ACompiledPayloadFixturePath")
    fixture_path = path_match.group(1)
    if fixture_path != EXPECTED_COMMIT_PATH:
        fail(f"compiled payload fixture path mismatch: expected {EXPECTED_COMMIT_PATH}, got {fixture_path}")

    fixture = (REPO_ROOT / fixture_path)
    if not fixture.exists():
        fail(f"compiled payload fixture missing: {fixture_path}")

    array_match = re.search(
        r"constexpr uint8_t kPhase7ACompiledPayload[^=]*=\s*\{(.*?)\};",
        header_text,
        flags=re.S,
    )
    if not array_match:
        fail("compiled payload header missing kPhase7ACompiledPayload array")

    byte_matches = re.findall(r"0x[0-9a-fA-F]{2}|\b\d+\b", array_match.group(1))
    payload = bytes(int(value, 0) for value in byte_matches)
    if len(payload) != EXPECTED_SIZE:
        fail(
            f"compiled payload array length mismatch: {len(payload)} != "
            f"{EXPECTED_SIZE}"
        )

    if fixture.read_bytes() != payload:
        fail("compiled payload bytes do not match fixture bytes")

    actual_sha = hashlib.sha256(fixture.read_bytes()).hexdigest()
    if actual_sha != EXPECTED_SHA:
        fail(f"fixture sha mismatch at runtime: {actual_sha} != {EXPECTED_SHA}")


def validate_retention_anchor() -> None:
    anchor_text = read_required(ANCHOR_PATH)
    require_phrase(anchor_text, "UltimateRuntimeConfigCompiledPayload", "anchor")
    require_phrase(
        anchor_text,
        "kPhase7AD2BRetainedPayloadAnchor",
        "anchor variable name",
    )
    require_phrase(anchor_text, ".rodata.phase7a_d2b_payload", "anchor section")
    require_phrase(anchor_text, '\\"aR\\"', "anchor retained section flags")
    require_phrase(anchor_text, ".incbin", "anchor payload include")
    require_phrase(anchor_text, EXPECTED_COMMIT_PATH, "anchor fixture path")


def validate_source_patterns() -> None:
    files = [
        ULTIMATE_CPP_PATH,
        ANCHOR_PATH,
        PARSER_PATH,
        INTERPRETER_PATH,
        IDENTITY_PATH,
        HEADER_PATH,
    ]
    for path in files:
        text = read_required(path)
        implementation = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("//")
        )
        if path == PARSER_PATH:
            if "ParseUltimateRuntimeConfigPayload" not in implementation:
                fail("parser header must retain ParseUltimateRuntimeConfigPayload symbol")
        else:
            for pattern in FORBIDDEN_SOURCE_PATTERNS:
                if re.search(pattern, implementation):
                    fail(f"forbidden parser/resolver symbol in {rel(path)}: {pattern}")

            if re.search(r"\bParseResult\b", implementation):
                fail(f"{rel(path)} contains ParseResult outside parser scaffold")

        for symbol in FORBIDDEN_RUNTIME_PATTERNS:
            if re.search(symbol, implementation):
                fail(f"forbidden runtime/storage symbol in {rel(path)}: {symbol}")

    ultimate_text = read_required(ULTIMATE_CPP_PATH)
    if "#include \"modes/UltimateRuntimeConfigCompiledPayload.hpp\"" in ultimate_text:
        fail("Ultimate.cpp must not include compiled payload header")


def validate_documents() -> None:
    doc_text = read_required(DOC_PATH)
    require_phrase(doc_text, f"status: {EXPECTED_STATUS_DOC}", "diagnostic document")
    require_phrase(doc_text, f"diagnostic branch: `{BRANCH}`", "diagnostic document")
    require_phrase(doc_text, "D2B", "diagnostic document")
    require_phrase(doc_text, "no parser call", "diagnostic document")
    require_phrase(doc_text, "no global parse result", "diagnostic document")
    require_phrase(doc_text, "no runtime resolver", "diagnostic document")
    require_phrase(doc_text, "no runtime behavior change", "diagnostic document")
    require_phrase(doc_text, "no storage", "diagnostic document")
    require_phrase(doc_text, "no webserial", "diagnostic document")
    require_phrase(doc_text, "no firmware flashing automation", "diagnostic document")
    require_phrase(doc_text, "not a hardware-result", "diagnostic document")
    require_phrase(doc_text, "not merge candidate", "diagnostic document")

    report_md = read_required(REPORT_MD_PATH)
    require_phrase(report_md, f"payload-retained-in-image: `true`", "build report")
    require_phrase(report_md, f"branch: `{BRANCH}`", "build report")
    require_phrase(report_md, f"diagnostic mode: `{EXPECTED_REPORT_D2_MODE}`", "build report")
    require_phrase(report_md, "retained-payload-size-bytes: `530`", "build report")
    require_phrase(report_md, "payload-sequence-scan-performed: `true`", "build report")
    require_phrase(
        report_md,
        "retention-proof-status: `proven_full_payload_sequence_present`",
        "build report",
    )
    require_phrase(report_md, "firmware.bin` | true", "build report")
    require_phrase(report_md, "firmware.elf` | true", "build report")
    require_phrase(report_md, "hardware result required before conclusions", "build report")

    hardware_plan_text = read_required(HARDWARE_PLAN_MD_PATH)
    require_phrase(hardware_plan_text, f"Branch: `{BRANCH}`", "hardware plan")
    for row in REQUIRED_HARDWARE_ROWS:
        if not re.search(
            rf"\|\s*{re.escape(row)}\s*\|[^\n]*\|[^\n]*\|\s*NOT_TESTED\s*\|",
            hardware_plan_text,
            flags=re.IGNORECASE,
        ):
            fail(f"hardware plan row not present as NOT_TESTED: {row}")

    hardware_plan = load_json(HARDWARE_PLAN_JSON_PATH)
    if hardware_plan.get("branch") != BRANCH:
        fail("hardware plan branch mismatch")
    if hardware_plan.get("hardware_result_recorded") is not False:
        fail("hardware plan should not record hardware result")
    if hardware_plan.get("status") != "TEMPLATE_ONLY":
        fail("hardware plan status must be TEMPLATE_ONLY")

    test_rows = hardware_plan.get("test_rows")
    if not isinstance(test_rows, list):
        fail("hardware plan test_rows must be a list")
    row_ids = {str(item.get("row_id")) for item in test_rows if isinstance(item, dict)}
    for row in REQUIRED_HARDWARE_ROWS:
        if row not in row_ids:
            fail(f"hardware plan JSON missing row: {row}")
    for row in test_rows:
        if not isinstance(row, dict):
            fail("hardware plan row entries must be objects")
        if str(row.get("result", "")).upper() != "NOT_TESTED":
            fail(f"hardware plan row must stay NOT_TESTED before result: {row.get('row_id')}")

    if hardware_plan.get("intent", {}).get("description", "") == "":
        fail("hardware plan intent description missing")


def validate_build_report_data() -> None:
    sequence_scan = scan_payload_sequence()
    report = load_json(REPORT_JSON_PATH)
    if report.get("schema_name") != EXPECTED_REPORT_SCHEMA:
        fail("unexpected build report schema_name")
    if report.get("status") != EXPECTED_REPORT_STATUS:
        fail("unexpected build report status")
    if report.get("branch") != BRANCH:
        fail("build report branch mismatch")
    if report.get("diagnostic_mode") != EXPECTED_REPORT_D2_MODE:
        fail("build report diagnostic mode mismatch")
    found_in_bin = bool(sequence_scan["bin"]["found"])
    found_in_elf = bool(sequence_scan["elf"]["found"])
    if report.get("payload_sequence_scan_performed") is not True:
        fail("build report must state payload_sequence_scan_performed true")
    if report.get("payload_sequence_found_in_bin") is not found_in_bin:
        fail("build report payload_sequence_found_in_bin mismatch")
    if report.get("payload_sequence_found_in_elf") is not found_in_elf:
        fail("build report payload_sequence_found_in_elf mismatch")
    if report.get("payload_sequence_found_in_uf2") is not bool(sequence_scan["uf2"]["found"]):
        fail("build report payload_sequence_found_in_uf2 mismatch")
    if not (found_in_bin or found_in_elf):
        if report.get("payload_bytes_retained_in_firmware_image") is not False:
            fail("absent payload sequence must mark payload retention false")
        fail("D2B is not proven because payload sequence is absent")
    if report.get("payload_bytes_retained_in_firmware_image") is not True:
        fail("build report must state payload retained in firmware image")
    if report.get("retention_proof_status") != "proven_full_payload_sequence_present":
        fail("build report retention_proof_status must prove full payload sequence")
    if report.get("retained_payload_size_bytes") != EXPECTED_SIZE:
        fail("build report retained payload size mismatch")
    if report.get("baseline_branch") != EXPECTED_BASELINE_BRANCH:
        fail("build report baseline branch mismatch")
    if report.get("build_command") != EXPECTED_BUILD_COMMAND:
        fail("build report build command mismatch")
    if report.get("runtime_behavior_changed") is not False:
        fail("build report must mark runtime_behavior_changed false")
    if report.get("hardware_required") is not True:
        fail("build report must require hardware")
    if report.get("hardware_result_claimed") is not False:
        fail("build report must not claim hardware result")
    if report.get("nunchuk_status") != "not_tested":
        fail("build report nunchuk_status must be not_tested")

    offsets = report.get("payload_sequence_found_offsets")
    if not isinstance(offsets, list):
        fail("build report payload_sequence_found_offsets must be a list")
    found_artifact_types: set[str] = set()
    for item in offsets:
        if not isinstance(item, dict):
            fail("payload_sequence_found_offsets entries must be objects")
        if item.get("artifact_type") not in {"bin", "elf", "uf2"}:
            fail("payload_sequence_found_offsets entry has invalid artifact_type")
        if not isinstance(item.get("offset"), int) or item["offset"] < 0:
            fail("payload_sequence_found_offsets entry has invalid offset")
        found_artifact_types.add(str(item.get("artifact_type")))

    if not {"bin", "elf"}.issubset(found_artifact_types):
        fail("build report offsets must include bin and elf entries")
    if report.get("payload_sequence_found_offsets") != offsets:
        fail("payload sequence offsets must remain self-consistent")

    artifacts = report.get("artifacts")
    if not isinstance(artifacts, list):
        fail("report artifacts must be a list")
    artifact_types = set()
    for item in artifacts:
        if not isinstance(item, dict):
            fail("each artifact entry must be object")
        artifact_type = str(item.get("artifact_type"))
        if artifact_type not in {"uf2", "elf", "bin"}:
            fail(f"unexpected artifact_type: {artifact_type}")
        artifact_types.add(artifact_type)

        if not isinstance(item.get("path"), str) or not item.get("path"):
            fail(f"artifact path must be present for {artifact_type}")
        if item.get("available") is not True:
            fail(f"artifact availability must remain true for {artifact_type}")
        if not isinstance(item.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-f]{64}", str(item.get("sha256"))
        ):
            fail(f"invalid artifact sha256 for {artifact_type}")
        if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] <= 0:
            fail(f"artifact size must be positive int for {artifact_type}")

    if artifact_types != {"uf2", "elf", "bin"}:
        fail("report artifacts must include uf2, elf, and bin entries")

    deltas = report.get("artifacts_deltas_vs_baseline")
    if deltas is not None:
        if not isinstance(deltas, list):
            fail("artifacts_deltas_vs_baseline must be a list when present")
        for item in deltas:
            if not isinstance(item, dict):
                fail("artifacts_deltas_vs_baseline entries must be objects")
            if item.get("artifact_type") not in {"uf2", "elf", "bin"}:
                fail("artifacts_deltas_vs_baseline entry has invalid artifact_type")

    deltas_d2a = report.get("artifacts_deltas_vs_d2a")
    if deltas_d2a is not None:
        if not isinstance(deltas_d2a, list):
            fail("artifacts_deltas_vs_d2a must be a list when present")
        for item in deltas_d2a:
            if not isinstance(item, dict):
                fail("artifacts_deltas_vs_d2a entries must be objects")
            if item.get("artifact_type") not in {"uf2", "elf", "bin"}:
                fail("artifacts_deltas_vs_d2a entry has invalid artifact_type")

    report_md = read_required(REPORT_MD_PATH)
    require_phrase(
        report_md,
        "Retention verification note",
        "build report",
    )
    require_phrase(
        report_md,
        "full committed 530-byte payload fixture sequence",
        "build report",
    )


def validate_ultimate_unchanged() -> None:
    base = subprocess.run(
        ["git", "show", "configurator:src/modes/Ultimate.cpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if base.returncode != 0:
        fail("unable to read configurator::src/modes/Ultimate.cpp")
    if base.stdout != read_required(ULTIMATE_CPP_PATH):
        fail("Ultimate.cpp differs from configurator in D2B branch")

    base_parser = subprocess.run(
        ["git", "show", "configurator:src/modes/UltimateRuntimeConfigParser.hpp"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if base_parser.returncode != 0:
        fail("unable to read configurator::src/modes/UltimateRuntimeConfigParser.hpp")
    if base_parser.stdout != read_required(PARSER_PATH):
        fail("UltimateRuntimeConfigParser.hpp differs from configurator")


def validate_no_hardware_claims() -> None:
    for path in (DOC_PATH, REPORT_MD_PATH, REPORT_JSON_PATH, HARDWARE_PLAN_MD_PATH):
        text = read_required(path)
        forbid_phrase(
            text,
            "hardware pass",
            rel(path),
        )
        lowered = text.lower()
        if "hardware-result claim" in lowered and "no hardware-result claim" not in lowered:
            fail(f"{rel(path)} contains forbidden affirmative hardware-result claim")
        lowered = text.lower()
        if (
            "nunchuk validation" in lowered
            and "no nunchuk validation" not in lowered
            and "nunchuk scope" not in lowered
            and "not tested" not in lowered
        ):
            fail(f"{rel(path)} contains nunchuk validation claim")


def main() -> int:
    try:
        validate_branch_scope()
        parse_compiled_payload_header()
        validate_retention_anchor()
        validate_source_patterns()
        validate_documents()
        validate_build_report_data()
        validate_ultimate_unchanged()
        validate_no_hardware_claims()
    except (FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError, ValueError, Phase7AD2BError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"diagnostic_doc={rel(DOC_PATH)}")
    print(f"build_report_json={rel(REPORT_JSON_PATH)}")
    print(f"build_report_md={rel(REPORT_MD_PATH)}")
    print(f"hardware_plan={rel(HARDWARE_PLAN_JSON_PATH)}")
    print("payload_retained_in_firmware_image=true")
    print("runtime_behavior_changed=false")
    print("hardware_required=true")
    print("hardware_result_claimed=false")
    print("nunchuk_status=not_tested")
    print("global_parser_call=false")
    print("global_parse_result=false")
    print("runtime_resolver=false")
    print("ultimate_cpp_unchanged=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
