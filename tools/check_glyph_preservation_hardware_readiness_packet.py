#!/usr/bin/env python3
"""Validate the Glyph preservation hardware readiness packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_preservation_hardware_readiness_packet_2026-06-06.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_preservation_hardware_readiness_packet_2026-06-06.json"
)

EXPECTED_TOP_LEVEL = {
    "schema_name": "glyph_preservation_hardware_readiness_packet",
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "readiness_packet_only",
    "preservation_hardware_status": "blocked_pending_user_hardware_execution",
    "source_matrix_path": "docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md",
    "source_template_path": "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
    "source_checker_path": "tools/check_glyph_ultimate_preservation_hardware_result.py",
    "post_gfw3_baseline_path": "docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md",
    "roadmap_next_work_index_path": "docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md",
    "future_result_branch": "glyph/gfw4-preservation-hardware-result",
    "result_recorded": False,
    "hardware_validation_claimed": False
}

REQUIRED_NON_CLAIMS = {
    "firmware_behavior_changed",
    "active_profile_artifact_changed",
    "runtime_loaded_config_implemented",
    "webserial_write_implemented",
    "device_write_implemented",
    "external_remapper_adapter_implemented",
    "nunchuk_hardware_validated",
}

EXPECTED_ALLOWED_STATUSES = [
    "PASS",
    "FAIL",
    "NOT_TESTED",
    "BLOCKED",
    "USER_ACCEPTED_RISK",
]

EXPECTED_FORBIDDEN_INFERENCES = {
    "do_not_infer_untested_rows",
    "do_not_claim_nunchuk_if_not_executed",
    "do_not_claim_external_remapper",
    "do_not_claim_runtime_loaded_config",
    "do_not_claim_webserial_or_device_write",
    "do_not_claim_active_profile_artifact_change",
}

REQUIRED_FUTURE_RESULT_FIELDS = {
    "result_doc",
    "result_fixture",
    "result_checker",
    "user_report_source",
    "per_row_statuses",
    "not_tested_handling",
    "failure_notes",
    "rollback_notes_if_needed",
}

REQUIRED_DOC_PHRASES = (
    "Purpose and scope",
    "Current post-GFW3 baseline",
    "blocked on user hardware execution",
    "does not record a preservation hardware pass or fail result",
    "No firmware behavior change",
    "No active profile artifact change",
    "No runtime-loaded config",
    "No WebSerial/device write",
    "No external remapper adapter",
    "No nunchuk hardware validation claim",
    "No hardware pass/fail result recorded here",
    "docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md",
    "docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md",
    "tools/check_glyph_ultimate_preservation_hardware_result.py",
    "docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md",
    "docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md",
    "docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md",
    "User-facing hardware execution summary",
    "glyph/gfw4-preservation-hardware-result",
    "in a result doc, fixture, and checker",
    "does not satisfy a behavior-changing merge gate",
)


class ReadinessPacketError(AssertionError):
    """Raised when the readiness packet drifts from its contract."""


def fail(message: str) -> None:
    raise ReadinessPacketError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_paths(payload: dict[str, Any]) -> None:
    for path in (DOC_PATH, FIXTURE_PATH):
        if not path.exists():
            fail(f"missing required path: {display(path)}")
    for key in (
        "source_matrix_path",
        "source_template_path",
        "source_checker_path",
        "post_gfw3_baseline_path",
        "roadmap_next_work_index_path",
        "identity_runtime_hardware_validation_and_rollback_path",
    ):
        rel_path = payload.get(key)
        if not isinstance(rel_path, str) or not rel_path.strip():
            fail(f"{key} must be a non-empty path string")
        if not (REPO_ROOT / rel_path).exists():
            fail(f"{key} references missing path: {rel_path}")


def validate_top_level(payload: dict[str, Any]) -> None:
    for key, expected in EXPECTED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")


def validate_non_claims(payload: dict[str, Any]) -> None:
    non_claims = payload.get("explicit_non_claims")
    if not isinstance(non_claims, dict):
        fail("explicit_non_claims must be an object")
    missing = sorted(REQUIRED_NON_CLAIMS - set(non_claims))
    if missing:
        fail("explicit_non_claims missing: " + ", ".join(missing))
    for key in sorted(REQUIRED_NON_CLAIMS):
        if non_claims.get(key) is not False:
            fail(f"explicit_non_claims.{key} must be false")


def validate_future_result_packet(payload: dict[str, Any]) -> None:
    packet = payload.get("required_future_result_packet")
    if not isinstance(packet, dict):
        fail("required_future_result_packet must be an object")
    missing = sorted(REQUIRED_FUTURE_RESULT_FIELDS - set(packet))
    if missing:
        fail("required_future_result_packet missing: " + ", ".join(missing))
    for key in sorted(REQUIRED_FUTURE_RESULT_FIELDS):
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            fail(f"required_future_result_packet.{key} must be a non-empty string")


def validate_statuses_and_inferences(payload: dict[str, Any]) -> None:
    if payload.get("allowed_statuses") != EXPECTED_ALLOWED_STATUSES:
        fail("allowed_statuses must match the preservation readiness contract")
    inferences = payload.get("forbidden_result_inferences")
    if not isinstance(inferences, list):
        fail("forbidden_result_inferences must be a list")
    found = set(inferences)
    missing = sorted(EXPECTED_FORBIDDEN_INFERENCES - found)
    if missing:
        fail("forbidden_result_inferences missing: " + ", ".join(missing))


def validate_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in text:
            fail(f"readiness doc missing required phrase: {phrase}")


def main() -> int:
    print("glyph_preservation_hardware_readiness_packet")
    try:
        payload = load_json_object(FIXTURE_PATH)
        require_paths(payload)
        validate_top_level(payload)
        validate_non_claims(payload)
        validate_future_result_packet(payload)
        validate_statuses_and_inferences(payload)
        validate_doc()
    except (OSError, ReadinessPacketError, ValueError) as exc:
        print("status=FAIL")
        print("packet_date=2026-06-06")
        print("result_recorded=false")
        print("hardware_validation_claimed=false")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("packet_date=2026-06-06")
    print("status_detail=readiness_packet_only")
    print("preservation_hardware_status=blocked_pending_user_hardware_execution")
    print("future_result_branch=glyph/gfw4-preservation-hardware-result")
    print("result_recorded=false")
    print("hardware_validation_claimed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
