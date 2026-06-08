#!/usr/bin/env python3
"""Validate the public/manual workflow release-candidate planning package.

This checker is intentionally read-only and depends only on the Python standard
library.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_BRANCH = "runtime-config-public-workflow-release-candidate-plan"
PLAN_DOC = REPO_ROOT / "docs/release/public_manual_workflow_release_candidate_plan.md"
CHECKLIST_DOC = REPO_ROOT / "docs/release/public_manual_workflow_release_candidate_checklist.md"
HARDWARE_PLAN_DOC = REPO_ROOT / "docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.md"
HARDWARE_PLAN_JSON = REPO_ROOT / "docs/calibration/fixtures/glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.json"
INDEX_DOC = REPO_ROOT / "docs/calibration/INDEX.md"
README_DOC = REPO_ROOT / "README.md"
CURRENT_STATE_DOC = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP_DOC = REPO_ROOT / "docs/ROADMAP.md"
RUNNER_PATH = REPO_ROOT / "tools/run_glyph_next_runtime_change_readiness_checks.py"
RESULT_DOC_PHRASE = (
    "Public/manual workflow release-candidate hardware result is recorded for applicable doable scope in "
    "`docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`; "
    "the plan/checklist remain plan-only and no public release or official configurator compatibility claim is made."
)

BASE_BRANCH = "configurator"

ALLOWED_CHANGED_PREFIXES = (
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/release/",
    "docs/export/",
    "docs/calibration/",
    "docs/runtime_config/",
    "tools/",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
    "lib/",
    "scripts/",
)

EXPECTED_PLAN_STATUS = "PLAN_ONLY_NOT_RELEASED"
EXPECTED_HARDWARE_STATUS = "TEMPLATE_ONLY_NOT_A_RESULT"
EXPECTED_ROWS = (
    "BOOT-001",
    "PROFILE-001",
    "BASELINE-001",
    "MODIFIERS-001",
    "SPECIAL-001",
    "OVERRIDE-001",
    "CSTICK-001",
    "DOCS-001",
    "NO-WRITE-001",
    "NO-FLASH-AUTO-001",
    "RECOVERY-001",
    "PROFILE-REG-001",
    "NUNCHUK-001",
)

REQUIRED_PLAN_PHRASES = (
    "PLAN_ONLY_NOT_RELEASED",
    "Public / Manual RC Scope",
    "Allowed Public Claims",
    "Explicit Non-Claims",
    "Operator-Run Workflow Boundary",
    "Offline Tooling Role",
    "Manual Firmware Update / Recovery Boundary",
    "Required Pre-Hardware Checks",
    "Hardware Test Trigger",
    "Post-Hardware Result Recording Requirement",
    "Stop Line Before Public Release Claims",
    "manual/operator-run firmware update path",
    "no hidden writes",
    "no runtime-loaded config",
    "no WebSerial/device write",
    "no flashing automation",
    "hardware result must be recorded in a separate result branch after the test",
)

REQUIRED_CHECKLIST_HEADINGS = (
    "Repository Baseline",
    "Required Prior Evidence Packets",
    "Required Checkers",
    "Required Non-Claims",
    "Manual Workflow Docs",
    "Pre-Hardware Local Verification",
    "Hardware Plan",
    "Result Recording",
    "Release Blockers",
)

REQUIRED_CHECKLIST_PHRASES = (
    "no runtime-loaded config claim is made",
    "no runtime-config storage claim is made",
    "no firmware binary/protobuf parser integration claim is made",
    "no WebSerial/device write claim is made",
    "no push-to-device claim is made",
    "no firmware flashing automation claim is made",
    "no official configurator compatibility claim is made",
    "no nunchuk validation claim is made unless separately tested and recorded",
    "no public release claim is made",
    "docs/release/public_manual_workflow_release_candidate_plan.md",
    "docs/release/public_manual_workflow_release_candidate_checklist.md",
)

REQUIRED_INDEX_PHRASES = (
    "public/manual workflow release-candidate prep",
    "docs/release/public_manual_workflow_release_candidate_plan.md",
    "docs/release/public_manual_workflow_release_candidate_checklist.md",
    "glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.md",
    "glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.json",
    "glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md",
    "glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.json",
)

REQUIRED_DOC_SYNC_PHRASES = {
    README_DOC: (
        "Step 14 manual firmware-consuming runtime-config load is blocked before implementation",
        "Step 15 source-authority research complete",
        "Step 16 WebSerial/device-write implementation is blocked before implementation",
        "Step 17 flashing automation is forbidden/not approved",
        RESULT_DOC_PHRASE,
        "Runtime-loaded config is not implemented",
        "Runtime-config storage is not implemented",
        "Firmware binary/protobuf parser integration is not implemented",
        "WebSerial/device write is not implemented",
        "Firmware flashing automation is not implemented",
        "No public release claim is made",
        "No nunchuk validation claim is made",
    ),
    CURRENT_STATE_DOC: (
        "Step 14 manual firmware-consuming runtime-config load is blocked before implementation",
        "Step 15 source-authority research complete",
        "Step 16 WebSerial/device-write implementation is blocked before implementation",
        "Step 17 flashing automation is forbidden/not approved; safety boundary complete",
        RESULT_DOC_PHRASE,
        "Runtime-loaded config is not implemented",
        "Runtime-config storage is not implemented",
        "Firmware binary/protobuf parser integration is not implemented",
        "WebSerial/device write is not implemented",
        "Firmware flashing automation is not implemented",
        "Nunchuk remains NOT_TESTED unless explicitly validated",
    ),
    ROADMAP_DOC: (
        "Step 14 manual firmware-consuming runtime-config load is blocked before implementation",
        "Step 15 source-authority research complete",
        "Step 16 WebSerial/device-write implementation is blocked before implementation",
        "Step 17 flashing automation is forbidden/not approved; safety boundary complete",
        RESULT_DOC_PHRASE,
        "public/manual workflow release-candidate plan and checklist",
        "Runtime-loaded config remains not implemented",
        "Runtime-config storage remains not implemented",
        "Firmware binary/protobuf parser integration remains not implemented",
        "WebSerial/device write remains not implemented",
        "Firmware flashing automation remains not implemented",
        "Nunchuk remains NOT_TESTED unless explicitly validated",
    ),
}

POSITIVE_RELEASE_PHRASES = (
    "released",
    "validated on hardware",
    "officially compatible",
    "nunchuk validated",
)


class PublicManualWorkflowRCError(ValueError):
    """Raised when the release-candidate planning package drifts."""


def fail(message: str) -> None:
    raise PublicManualWorkflowRCError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return payload


def changed_paths_against_base() -> list[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    ):
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())

    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line:
                paths.add(line[3:].strip())
    return sorted(paths)


def current_branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("unable to determine current branch")
    branch = completed.stdout.strip()
    if not branch:
        fail("unable to determine current branch")
    return branch


def require_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    missing = [phrase for phrase in phrases if phrase.lower() not in lowered]
    if missing:
        fail(f"{label} missing required phrase(s): " + ", ".join(missing))


def require_headings(text: str, headings: tuple[str, ...], *, label: str) -> None:
    lowered = text.lower()
    for heading in headings:
        if f"## {heading.lower()}" not in lowered:
            fail(f"{label} missing required section heading: {heading}")


def parse_markdown_table(text: str) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] == "Row ID":
            in_table = True
            continue
        if not in_table or set(cells[0]) == {"-"}:
            continue
        rows[cells[0]] = (cells[2], cells[3])
    return rows


def require_no_positive_release_claims(text: str, *, label: str) -> None:
    lowered = normalize(text)
    for phrase in POSITIVE_RELEASE_PHRASES:
        pattern = rf"(?<!no )(?<!not )\b{re.escape(phrase)}\b"
        if re.search(pattern, lowered):
            fail(f"{label} contains positive release/pass claim phrase: {phrase}")


def validate_status_sync() -> None:
    for path, phrases in REQUIRED_DOC_SYNC_PHRASES.items():
        require_phrases(read_required(path), phrases, label=path.relative_to(REPO_ROOT).as_posix())


def validate_plan_doc() -> None:
    text = read_required(PLAN_DOC)
    require_phrases(text, REQUIRED_PLAN_PHRASES, label="release candidate plan")
    require_no_positive_release_claims(text, label="release candidate plan")
    if EXPECTED_PLAN_STATUS.lower() not in normalize(text):
        fail("release candidate plan must state PLAN_ONLY_NOT_RELEASED")


def validate_checklist_doc() -> None:
    text = read_required(CHECKLIST_DOC)
    require_headings(text, REQUIRED_CHECKLIST_HEADINGS, label="release candidate checklist")
    require_phrases(text, REQUIRED_CHECKLIST_PHRASES, label="release candidate checklist")
    require_no_positive_release_claims(text, label="release candidate checklist")


def validate_hardware_plan() -> None:
    markdown = read_required(HARDWARE_PLAN_DOC)
    require_phrases(
        markdown,
        (
            "Status: TEMPLATE_ONLY_NOT_A_RESULT",
            "manual/operator-run firmware update path only",
            "No runtime-loaded config",
            "No WebSerial/device write",
            "No flashing automation",
            "No hidden writes",
            "hardware result must be recorded in a separate result branch after the test",
            "all rows start as `NOT_TESTED`",
            "Nunchuk scope for this branch: `NOT_TESTED`",
            "This is a hardware-test template",
        ),
        label="hardware plan markdown",
    )
    require_no_positive_release_claims(markdown, label="hardware plan markdown")

    table_rows = parse_markdown_table(markdown)
    if set(table_rows) != set(EXPECTED_ROWS):
        missing = sorted(set(EXPECTED_ROWS) - set(table_rows))
        unexpected = sorted(set(table_rows) - set(EXPECTED_ROWS))
        details = []
        if missing:
            details.append("missing=" + ", ".join(missing))
        if unexpected:
            details.append("unexpected=" + ", ".join(unexpected))
        fail("hardware plan markdown rows mismatch (" + "; ".join(details) + ")")

    for row_id in EXPECTED_ROWS:
        _planned_check, result = table_rows[row_id]
        if result != "NOT_TESTED":
            fail(f"hardware plan markdown row {row_id} must start as NOT_TESTED")

    fixture = load_json_object(HARDWARE_PLAN_JSON)
    expected_fields = {
        "schema_name": "glyph_public_manual_workflow_release_candidate_hardware_plan",
        "plan_version": 1,
        "status": EXPECTED_HARDWARE_STATUS,
        "branch": "runtime-config-public-workflow-release-candidate-plan",
        "build_command": "./scripts/build-glyph-mk6-quiet.sh",
        "hardware_result_recorded": False,
        "commit_sha_under_test": "unknown",
        "firmware_artifact_path": "unknown",
        "firmware_artifact_sha256": "unknown",
        "tester": "unknown",
        "test_date": "unknown",
    }
    for key, expected in expected_fields.items():
        if fixture.get(key) != expected:
            fail(f"hardware plan fixture {key} must be {expected!r}")

    intent = fixture.get("intent")
    if not isinstance(intent, dict):
        fail("hardware plan fixture intent must be an object")
    description = intent.get("description")
    if not isinstance(description, str) or not description:
        fail("hardware plan fixture intent.description is required")

    rows = fixture.get("test_rows")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_ROWS):
        fail("hardware plan fixture test_rows must contain all expected rows")

    seen_rows: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            fail("hardware plan fixture rows must be objects")
        row_id = row.get("row_id")
        result = row.get("result")
        if row_id not in EXPECTED_ROWS:
            fail(f"hardware plan fixture contains unexpected row: {row_id}")
        if result != "NOT_TESTED":
            fail(f"hardware plan fixture row {row_id} must start as NOT_TESTED")
        seen_rows[row_id] = result

    if set(seen_rows) != set(EXPECTED_ROWS):
        fail("hardware plan fixture rows do not match expected row set")

    caveats = fixture.get("caveats")
    if not isinstance(caveats, list):
        fail("hardware plan fixture caveats must be a list")
    required_caveats = {
        "no_runtime_loaded_config",
        "no_webserial_or_device_write",
        "no_firmware_flashing_automation",
        "no_hidden_writes",
        "no_public_release_claim",
        "no_nunchuk_validation_claim",
    }
    if not required_caveats.issubset(set(caveats)):
        missing = sorted(required_caveats - set(caveats))
        fail("hardware plan fixture missing required caveats: " + ", ".join(missing))


def ensure_no_out_of_scope_changes() -> None:
    changed = changed_paths_against_base()
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_CHANGED_PREFIXES)]
    if forbidden:
        fail("firmware/source/build-script paths changed on the RC planning branch: " + ", ".join(forbidden))

    out_of_scope = [path for path in changed if not path.startswith(ALLOWED_CHANGED_PREFIXES)]
    if out_of_scope:
        fail("branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))

    result_files = [path for path in changed if "hardware_result" in path.lower()]
    if current_branch() == PLAN_BRANCH and result_files:
        fail("hardware result files are not allowed on the planning branch: " + ", ".join(result_files))


def ensure_runner_includes_new_checker() -> None:
    text = read_required(RUNNER_PATH)
    require_phrases(
        text,
        (
            "tools/check_glyph_public_manual_workflow_release_candidate.py",
            "tools/check_glyph_public_manual_workflow_release_candidate_hardware_result.py",
        ),
        label="aggregate runner",
    )


def ensure_index_mentions_release_candidate() -> None:
    text = read_required(INDEX_DOC)
    require_phrases(text, REQUIRED_INDEX_PHRASES, label="calibration index")


def main() -> int:
    print("glyph_public_manual_workflow_release_candidate")
    try:
        validate_status_sync()
        validate_plan_doc()
        validate_checklist_doc()
        validate_hardware_plan()
        ensure_index_mentions_release_candidate()
        ensure_runner_includes_new_checker()
        ensure_no_out_of_scope_changes()
    except (OSError, ValueError, PublicManualWorkflowRCError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"plan_doc={PLAN_DOC.relative_to(REPO_ROOT)}")
    print(f"checklist_doc={CHECKLIST_DOC.relative_to(REPO_ROOT)}")
    print(f"hardware_plan_doc={HARDWARE_PLAN_DOC.relative_to(REPO_ROOT)}")
    print(f"hardware_plan_json={HARDWARE_PLAN_JSON.relative_to(REPO_ROOT)}")
    print("plan_only_not_released=true")
    print("hardware_result_recorded=false")
    print("manual_operator_run_only=true")
    print("no_runtime_loaded_config=true")
    print("no_webserial_device_write=true")
    print("no_firmware_flashing_automation=true")
    print("no_public_release_claim=true")
    print("nunchuk_validation_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
