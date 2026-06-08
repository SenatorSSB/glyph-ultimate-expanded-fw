#!/usr/bin/env python3
"""Validate Step 13 runtime-config firmware binary parser plan guardrails."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUTHORITY_DOC = (
    REPO_ROOT / "docs" / "runtime_config" / "runtime_config_firmware_binary_parser_source_authority.md"
)
INTEGRATION_PLAN_DOC = (
    REPO_ROOT / "docs" / "runtime_config" / "runtime_config_firmware_binary_parser_integration_plan.md"
)
HARDWARE_PLAN_TEMPLATE = (
    REPO_ROOT / "docs" / "calibration" / "glyph_runtime_config_firmware_binary_parser_hardware_plan_TEMPLATE.md"
)

BASE_BRANCH = "configurator"

ALLOWED_CHANGED_PREFIXES = (
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/release/",
    "docs/export/",
    "docs/runtime_config/",
    "docs/calibration/",
    "tools/",
)

FORBIDDEN_CHANGED_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
    "lib/",
)

REQUIRED_SOURCE_PHRASES = (
    "IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false",
    "Step 13 firmware binary/protobuf parser integration remains blocked",
    "must not make firmware consume",
    "What Current Config Persistence Supports",
    "What Current Config Persistence Does Not Support",
    "Firmware parser implementation is not implemented",
    "Runtime-loaded config consumption is not implemented",
    "Runtime-config storage is not implemented",
    "WebSerial/device write is not implemented",
    "Firmware flashing automation is not implemented",
    "Nunchuk validation is not claimed",
    "Official protobuf compatibility is not claimed",
)

REQUIRED_PLAN_PHRASES = (
    "DESIGN_APPROVAL_GATE_ONLY",
    "Parser Input Boundary",
    "Why The Offline Container Is Not Yet Firmware Format",
    "Validation-Before-Use Sequence",
    "Checksum And CRC Policy",
    "Schema And Version Policy",
    "Mode Scope Policy",
    "Table ID And Order Validation",
    "Coordinate Validation Before Narrowing",
    "Fallback-To-Known-Good Policy",
    "Storage Dependency Status",
    "Boot-Time Read Dependency Status",
    "Rollback And Recovery Requirements",
    "Exact Stop Line Before Implementation",
    "Firmware parser implementation is not implemented",
    "Runtime-loaded config consumption is not implemented",
    "Runtime-config storage is not implemented",
    "WebSerial/device write is not implemented",
    "Firmware flashing automation is not implemented",
)

REQUIRED_HARDWARE_ROWS = (
    "Boot with no stored runtime config",
    "Boot with valid runtime config if future implementation supports it",
    "Invalid checksum fallback",
    "Unsupported version fallback",
    "Missing table fallback",
    "Out-of-range coordinate rejection",
    "Baseline output preservation",
    "Profile regression",
    "Recovery/rollback behavior if testable",
    "Nunchuk scope",
    "NOT_TESTED",
)

REQUIRED_GATE_PHRASES = (
    "explicit user product approval",
    "selected firmware-owned parser format",
    "source-backed storage/boot entry point decision",
    "source-backed fallback and recovery policy",
    "memory and maximum-size review",
    "hardware test plan and recorded hardware result",
)

POSITIVE_IMPLEMENTATION_PATTERNS = (
    r"\bfirmware parser implementation is implemented\b",
    r"\bruntime-loaded config consumption is implemented\b",
    r"\bruntime-config storage is implemented\b",
    r"\bwebserial/device write is implemented\b",
    r"\bfirmware flashing automation is implemented\b",
    r"\bnunchuk validation is claimed\b",
    r"\bofficial protobuf compatibility is claimed\b",
    r"\buniversal official configurator compatibility is claimed\b",
    r"\bfirmware consumes this binary\b",
    r"\bloads runtime protobuf\b",
    r"\buses config\.bin for runtime config\b",
)


class FirmwareBinaryParserPlanError(ValueError):
    """Raised when Step 13 parser-plan guardrails drift."""


def fail(message: str) -> None:
    raise FirmwareBinaryParserPlanError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def require_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    for phrase in phrases:
        if phrase.lower() not in lowered:
            fail(f"{label} missing required phrase: {phrase}")


def ensure_section_has_bullet(text: str, heading: str, *, label: str) -> None:
    pattern = rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    if not match:
        fail(f"{label} missing section heading: {heading}")
    if not any(line.strip().startswith("-") for line in match.group(1).splitlines()):
        fail(f"{label} section {heading!r} must include bullet guardrails")


def ensure_no_positive_implementation_claims(text: str, *, label: str) -> None:
    lowered = normalize(text)
    for pattern in POSITIVE_IMPLEMENTATION_PATTERNS:
        if re.search(pattern, lowered):
            fail(f"{label} contains positive implementation claim matching {pattern!r}")


def ensure_implementation_allowed_false_or_gated(text: str) -> None:
    lowered = normalize(text)
    if "implementation_allowed_by_source_audit=false" in lowered:
        return

    missing_gates = [phrase for phrase in REQUIRED_GATE_PHRASES if phrase not in lowered]
    if missing_gates:
        fail(
            "source authority doc must keep IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false "
            "unless all explicit gates are present; missing: "
            + ", ".join(missing_gates)
        )


def changed_paths_against_base() -> list[str]:
    paths: set[str] = set()

    for command in (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    ):
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if not line:
                continue
            paths.add(line[3:].strip())

    return sorted(paths)


def ensure_no_firmware_source_changed() -> None:
    changed = changed_paths_against_base()
    forbidden = [
        path
        for path in changed
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES)
    ]
    if forbidden:
        fail("firmware/source paths changed on Step 13 design branch: " + ", ".join(forbidden))

    out_of_scope = [
        path
        for path in changed
        if not path.startswith(ALLOWED_CHANGED_PREFIXES)
    ]
    if out_of_scope:
        fail("Step 13 branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))


def ensure_no_runtime_parser_symbols_added() -> None:
    candidates = (
        REPO_ROOT / "src",
        REPO_ROOT / "include",
        REPO_ROOT / "HAL",
        REPO_ROOT / "config",
    )
    suspicious_patterns = (
        "DecodeRuntimeConfigBinary",
        "ParseRuntimeConfigBinary",
        "LoadRuntimeConfig",
        "SaveRuntimeConfig",
        "CMD_SET_RUNTIME_CONFIG",
        "CMD_GET_RUNTIME_CONFIG",
    )
    for root in candidates:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".cpp", ".hpp", ".h", ".c", ".cc"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in suspicious_patterns:
                if marker in text:
                    fail(
                        f"firmware/source contains runtime parser marker {marker!r} "
                        f"in {path.relative_to(REPO_ROOT)}"
                    )


def main() -> int:
    print("glyph_runtime_config_firmware_binary_parser_plan")
    try:
        source_text = read_required(SOURCE_AUTHORITY_DOC)
        plan_text = read_required(INTEGRATION_PLAN_DOC)
        hardware_text = read_required(HARDWARE_PLAN_TEMPLATE)

        require_phrases(source_text, REQUIRED_SOURCE_PHRASES, label="source authority doc")
        require_phrases(plan_text, REQUIRED_PLAN_PHRASES, label="integration plan")
        require_phrases(hardware_text, REQUIRED_HARDWARE_ROWS, label="hardware plan template")

        for heading in ("Non-Claims", "Stop Conditions Hit"):
            ensure_section_has_bullet(source_text, heading, label="source authority doc")
        ensure_section_has_bullet(plan_text, "Non-Claims", label="integration plan")
        ensure_section_has_bullet(hardware_text, "Non-Claims", label="hardware plan template")

        ensure_implementation_allowed_false_or_gated(source_text)
        ensure_no_positive_implementation_claims(source_text, label="source authority doc")
        ensure_no_positive_implementation_claims(plan_text, label="integration plan")
        ensure_no_positive_implementation_claims(hardware_text, label="hardware plan template")
        ensure_no_firmware_source_changed()
        ensure_no_runtime_parser_symbols_added()
    except (OSError, ValueError, FirmwareBinaryParserPlanError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"source_authority_doc={SOURCE_AUTHORITY_DOC.relative_to(REPO_ROOT)}")
    print(f"integration_plan={INTEGRATION_PLAN_DOC.relative_to(REPO_ROOT)}")
    print(f"hardware_plan_template={HARDWARE_PLAN_TEMPLATE.relative_to(REPO_ROOT)}")
    print("implementation_allowed_by_source_audit=false")
    print("firmware_parser_implemented=false")
    print("runtime_loaded_config_consumption=false")
    print("runtime_config_storage_implemented=false")
    print("webserial_device_write_implemented=false")
    print("firmware_flashing_automation_implemented=false")
    print("nunchuk_validation_claim=false")
    print("official_protobuf_compatibility_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
