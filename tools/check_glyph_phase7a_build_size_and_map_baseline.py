#!/usr/bin/env python3
"""Validate the Phase 7A build-size/map baseline report and fixture metadata."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "phase7a_build_size_and_map_baseline_2026-06-08.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "runtime_config"
    / "fixtures"
    / "phase7a_build_size_and_map_baseline_2026-06-08.json"
)

EXPECTED_STATUS_DOC = "BUILD_SIZE_BASELINE_RECORDED"
EXPECTED_STATUS_JSON = "build_size_baseline_recorded"
EXPECTED_BRANCH = "phase7a-build-size-and-map-baseline"
POST_MERGE_BRANCH = "configurator"
ANALYSIS_BRANCH = "phase7a-activation-failure-root-cause-analysis"
ALLOWED_BRANCHES = {EXPECTED_BRANCH, POST_MERGE_BRANCH, ANALYSIS_BRANCH}
EXPECTED_BASELINE_BRANCH = "configurator"
EXPECTED_BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
EXPECTED_CAVEATS = (
    "no firmware source edits",
    "no runtime behavior change",
    "no runtime-loaded config",
    "no runtime-config storage",
    "no webserial/device write",
    "no firmware flashing automation",
    "no hardware result claim",
    "nunchuk not_tested",
)


class Phase7ABuildSizeMapBaselineError(ValueError):
    """Raised when baseline report or fixture violates required constraints."""


def fail(message: str) -> None:
    raise Phase7ABuildSizeMapBaselineError(message)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"required file missing: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        fail(f"fixture must be a JSON object: {path.relative_to(REPO_ROOT)}")
    return payload


def require_match(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        fail(f"{label} missing expected pattern: {pattern!r}")
    if match.lastindex:
        return match.group(1).strip()
    return match.group(0).strip()


def is_sha(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{40}", value or ""))


def validate_no_forbidden_report_claims(text: str) -> None:
    lowered = text.lower()

    if "hardware pass" in lowered and "no hardware result" not in lowered:
        fail("report must not claim a hardware pass")

    if re.search(r"\bnunchuk\b.*\b(validated|validation|pass)\b", lowered):
        fail("report must not claim nunchuk validation")

    if re.search(r"runtime[- ]loaded config.*(?:implemented|enabled|active)", lowered):
        fail("report must not claim runtime-loaded config implementation")

    if re.search(r"runtime[- ]config storage.*(?:implemented|enabled|active)", lowered):
        fail("report must not claim runtime-config storage implementation")

    if re.search(r"webserial.*device write.*(?:implemented|enabled|active)", lowered):
        fail("report must not claim WebSerial/device write implementation")

    if re.search(r"firmware flashing automation.*(?:implemented|enabled|active)", lowered):
        fail("report must not claim firmware flashing automation implementation")


def validate_report() -> None:
    text = read_text(REPORT_PATH)
    lowered = text.lower()

    require_match(r"^status:\s*`" + re.escape(EXPECTED_STATUS_DOC) + r"`\s*$", text, "report status")
    require_match(r"^branch:\s*`([^`]+)`\s*$", text, "report branch")
    branch = require_match(r"^branch:\s*`([^`]+)`\s*$", text, "report branch")
    if branch not in ALLOWED_BRANCHES:
        fail(
            f"report branch mismatch: {branch!r} (allowed: "
            f"{', '.join(sorted(ALLOWED_BRANCHES))!r})"
        )

    baseline_branch = require_match(
        r"^baseline branch:\s*`([^`]+)`\s*$",
        text,
        "report baseline branch",
    )
    if baseline_branch != EXPECTED_BASELINE_BRANCH:
        fail(
            "report baseline mismatch: "
            f"{baseline_branch!r} != {EXPECTED_BASELINE_BRANCH!r}"
        )

    build_command = require_match(r"^build command:\s*`([^`]+)`\s*$", text, "report build command")
    if build_command != EXPECTED_BUILD_COMMAND:
        fail(
            f"report build command mismatch: "
            f"{build_command!r} != {EXPECTED_BUILD_COMMAND!r}"
        )

    commit_sha = require_match(r"^git commit SHA under build:\s*`([0-9a-fA-F]{40})`\s*$", text, "report commit SHA")
    if not is_sha(commit_sha):
        fail(f"report commit SHA invalid: {commit_sha!r}")

    validate_no_forbidden_report_claims(lowered)


def validate_fixture() -> None:
    payload = read_json(FIXTURE_PATH)

    if payload.get("schema_name") != "glyph_phase7a_build_size_and_map_baseline":
        fail("fixture schema_name must be glyph_phase7a_build_size_and_map_baseline")

    if payload.get("status") != EXPECTED_STATUS_JSON:
        fail(
            f'fixture status mismatch: {payload.get("status")!r} != '
            f"{EXPECTED_STATUS_JSON!r}"
        )

    if payload.get("branch") not in ALLOWED_BRANCHES:
        fail(
            f'fixture branch mismatch: {payload.get("branch")!r} (allowed: '
            f'{", ".join(sorted(ALLOWED_BRANCHES))!r})'
        )

    if payload.get("baseline_branch") != EXPECTED_BASELINE_BRANCH:
        fail(
            f'fixture baseline branch mismatch: '
            f'{payload.get("baseline_branch")!r} != {EXPECTED_BASELINE_BRANCH!r}'
        )

    commit_sha = payload.get("commit_sha")
    if not isinstance(commit_sha, str) or not is_sha(commit_sha):
        fail(f"fixture commit_sha must be a 40-hex git hash: {commit_sha!r}")

    if payload.get("build_command") != EXPECTED_BUILD_COMMAND:
        fail(
            f'fixture build_command mismatch: {payload.get("build_command")!r} != '
            f"{EXPECTED_BUILD_COMMAND!r}"
        )

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        fail("fixture artifacts must be a list")
    if not artifacts:
        fail("fixture artifacts list must include discovered artifacts")

    for index, entry in enumerate(artifacts):
        if not isinstance(entry, dict):
            fail(f"artifacts[{index}] must be an object")

        for key in ("path", "artifact_type", "size_bytes", "sha256", "available"):
            if key not in entry:
                fail(f"artifacts[{index}] missing key: {key}")

        artifact_type = entry.get("artifact_type")
        if artifact_type not in ("uf2", "elf", "bin"):
            fail(f"artifacts[{index}] has unexpected artifact_type: {artifact_type!r}")

        available = entry.get("available")
        if not isinstance(available, bool):
            fail(f"artifacts[{index}].available must be boolean")

        if available:
            path = entry.get("path")
            if not isinstance(path, str) or not path.strip():
                fail(f"artifacts[{index}] available item must have non-empty path")
            size_bytes = entry.get("size_bytes")
            if not isinstance(size_bytes, int) or size_bytes <= 0:
                fail(
                    f"artifacts[{index}] available item must have positive size_bytes "
                    f"(got {size_bytes!r})"
                )
            sha = entry.get("sha256")
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
                fail(f"artifacts[{index}] available item sha256 must be 64-lowercase hex chars")
        else:
            # Unavailable artifact placeholders are optional and intentionally sparse.
            pass

    for artifact_type, expected_available_key in (
        ("map", "map_file_available"),
        ("elf", "elf_file_available"),
        ("uf2", "uf2_file_available"),
        ("bin", "bin_file_available"),
    ):
        available_value = payload.get(expected_available_key)
        if not isinstance(available_value, bool):
            fail(f"{expected_available_key} must be boolean")
        actual_available = any(
            artifact.get("artifact_type") == artifact_type and artifact.get("available")
            for artifact in artifacts
            if isinstance(artifact, dict)
        )
        if available_value != actual_available:
            fail(
                f"{expected_available_key} mismatch: declared {available_value} but "
                f"artifact list has {actual_available}"
            )

    for key in (
        "firmware_source_changed",
        "runtime_behavior_changed",
        "hardware_required",
        "hardware_result_claimed",
    ):
        if payload.get(key) is not False:
            fail(f"fixture {key} must be false")

    if payload.get("nunchuk_status") != "not_tested":
        fail(
            f'fixture nunchuk_status must be "not_tested", got {payload.get("nunchuk_status")!r}'
        )

    caveats = payload.get("caveats")
    if not isinstance(caveats, list) or not caveats:
        fail("fixture caveats must be a non-empty list")
    caveats_text = " ".join(entry.lower() for entry in caveats if isinstance(entry, str))
    for required in EXPECTED_CAVEATS:
        if required.lower() not in caveats_text:
            fail(f"fixture caveats missing required phrase: {required!r}")


def validate_git_context() -> None:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        fail("unable to determine current branch")
    current = completed.stdout.strip()
    if current not in ALLOWED_BRANCHES:
        fail(
            f"checker must run on {', '.join(sorted(ALLOWED_BRANCHES))}, got {current!r}"
        )


def main() -> int:
    validate_report()
    validate_fixture()
    validate_git_context()

    print("status=PASS")
    print(f"report={REPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"fixture={FIXTURE_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
