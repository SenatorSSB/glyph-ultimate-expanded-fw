#!/usr/bin/env python3
"""Validate Phase 6 bounded config architecture docs and guardrails."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_BRANCH = "configurator"

ARCHITECTURE_DOC = REPO_ROOT / "docs/runtime_config/phase6_bounded_config_owned_data_architecture.md"
SOURCE_AUTHORITY_DOC = REPO_ROOT / "docs/runtime_config/phase6_bounded_config_source_authority.md"
BLOCKERS_DOC = REPO_ROOT / "docs/runtime_config/runtime_config_blockers_1_to_5_decision_packet.md"
SCHEMA_CANDIDATE = REPO_ROOT / "docs/runtime_config/fixtures/phase6_bounded_config_owned_modifier_data_schema_candidate.json"
INVALID_CORPUS = REPO_ROOT / "docs/runtime_config/fixtures/phase6_bounded_config_invalid_cases.json"
SLICE_PLAN = REPO_ROOT / "docs/runtime_config/phase6_to_phase7_implementation_slice_plan.md"
HARDWARE_MATRIX = REPO_ROOT / "docs/calibration/glyph_runtime_config_phase6_phase7_hardware_matrix_TEMPLATE.md"

REQUIRED_PATHS = (
    ARCHITECTURE_DOC,
    SOURCE_AUTHORITY_DOC,
    BLOCKERS_DOC,
    SCHEMA_CANDIDATE,
    INVALID_CORPUS,
    SLICE_PLAN,
    HARDWARE_MATRIX,
)

ALLOWED_CHANGED_PREFIXES = (
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
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
    "platformio.ini",
    "scripts/",
)

REQUIRED_ARCH_PHRASES = (
    "PHASE6_DESIGN_COMPLETE_NOT_IMPLEMENTED",
    "MODE_ULTIMATE",
    "Firmware-Owned Semantics",
    "Config-Owned Bounded Data",
    "Forbidden Config-Owned Behavior",
    "Validation-Before-Use Invariant",
    "Fallback Invariant",
    "Implementation Stop Line",
    "Hardware Gates",
    "Runtime-loaded config is not implemented",
)

REQUIRED_SOURCE_PHRASES = (
    "PHASE6_SOURCE_AUTHORITY_COMPLETE_NOT_IMPLEMENTED",
    "Inspected Files",
    "Inspected Searches",
    "Source-Backed Facts",
    "Fixture-Observed Evidence",
    "Inferred Or Proposed Decisions",
    "Unknowns",
    "Rejected Unsupported Claims",
    "No runtime-loaded config implementation claim is made",
)

REQUIRED_BLOCKER_PHRASES = (
    "BLOCKERS_1_TO_5_DESIGN_COMPLETE_NOT_IMPLEMENTED",
    "Blocker 1 - Storage Location And Ownership",
    "Blocker 2 - Firmware Parser Format",
    "Blocker 3 - Boot/Load Entry Point",
    "Blocker 4 - Fallback, Recovery, And Rollback",
    "Blocker 5 - Device-Write / WebSerial Authority Boundary",
    "PROPOSED_DECISION_NOT_IMPLEMENTED",
    "Stop line before implementation",
)

REQUIRED_FORBIDDEN_TERMS = (
    "macros",
    "turbo",
    "timing automation",
    "arbitrary scripting",
    "hidden device write",
)

REQUIRED_SLICE_PHRASES = (
    "SLICE_PLAN_DESIGN_ONLY_NOT_IMPLEMENTED",
    "Slice 7A",
    "Slice 7B",
    "Slice 7C",
    "Slice 8A",
    "Slice 8B",
    "Hardware plan/result requirement",
)

POSITIVE_IMPLEMENTATION_PATTERNS = (
    r"\bruntime-loaded config is implemented\b",
    r"\bruntime-config storage is implemented\b",
    r"\bfirmware parser is implemented\b",
    r"\bfirmware parser implementation is implemented\b",
    r"\bwebserial/device write is implemented\b",
    r"\bdevice write / webserial is implemented\b",
    r"\bfirmware flashing automation is implemented\b",
    r"\bpublic release is claimed\b",
    r"\bofficial configurator compatibility is claimed\b",
    r"\bnunchuk validation is claimed\b",
)


class Phase6ArchitectureError(ValueError):
    """Raised when Phase 6 architecture guardrails drift."""


def fail(message: str) -> None:
    raise Phase6ArchitectureError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def require_phrases(text: str, phrases: tuple[str, ...], label: str) -> None:
    lowered = normalize(text)
    for phrase in phrases:
        if phrase.lower() not in lowered:
            fail(f"{label} missing required phrase: {phrase}")


def ensure_no_positive_implementation_claims(text: str, label: str) -> None:
    lowered = normalize(text)
    for pattern in POSITIVE_IMPLEMENTATION_PATTERNS:
        if re.search(pattern, lowered):
            fail(f"{label} contains positive implementation claim matching {pattern!r}")


def changed_paths() -> list[str]:
    paths: set[str] = set()
    commands = (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            paths.update(line.strip() for line in result.stdout.splitlines() if line.strip())

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line:
                paths.add(line[3:].strip())
    return sorted(paths)


def ensure_changed_paths_in_scope() -> None:
    changed = changed_paths()
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_CHANGED_PREFIXES)]
    if forbidden:
        fail("Phase 6 branch changed forbidden firmware/source/build paths: " + ", ".join(forbidden))
    out_of_scope = [
        path for path in changed
        if not path.startswith(ALLOWED_CHANGED_PREFIXES)
    ]
    if out_of_scope:
        fail("Phase 6 branch changed out-of-scope paths: " + ", ".join(out_of_scope))


def main() -> int:
    print("glyph_phase6_bounded_config_architecture")
    try:
        texts = {path: read_required(path) for path in REQUIRED_PATHS}
        require_phrases(texts[ARCHITECTURE_DOC], REQUIRED_ARCH_PHRASES, "architecture doc")
        require_phrases(texts[SOURCE_AUTHORITY_DOC], REQUIRED_SOURCE_PHRASES, "source authority doc")
        require_phrases(texts[BLOCKERS_DOC], REQUIRED_BLOCKER_PHRASES, "blockers packet")
        require_phrases(texts[ARCHITECTURE_DOC], REQUIRED_FORBIDDEN_TERMS, "architecture forbidden semantics")
        require_phrases(texts[SLICE_PLAN], REQUIRED_SLICE_PHRASES, "implementation slice plan")
        require_phrases(texts[HARDWARE_MATRIX], ("TEMPLATE_ONLY_NOT_A_RESULT", "nunchuk NOT_TESTED"), "hardware matrix")
        combined = "\n".join(texts.values())
        ensure_no_positive_implementation_claims(combined, "Phase 6 docs")
        ensure_changed_paths_in_scope()
    except (OSError, Phase6ArchitectureError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"architecture_doc={ARCHITECTURE_DOC.relative_to(REPO_ROOT)}")
    print(f"source_authority_doc={SOURCE_AUTHORITY_DOC.relative_to(REPO_ROOT)}")
    print(f"blockers_doc={BLOCKERS_DOC.relative_to(REPO_ROOT)}")
    print("runtime_loaded_config=false")
    print("storage_implemented=false")
    print("parser_implemented=false")
    print("device_write_implemented=false")
    print("firmware_source_changed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
