#!/usr/bin/env python3
"""Validate the Glyph clean-room adapter candidate schema validator packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_clean_room_adapter_candidate_schema_validator_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_clean_room_adapter_candidate_SCHEMA_PLACEHOLDER_2026-06-04.json"
)
CONTRACT_CHECKER = "tools/check_glyph_clean_room_adapter_candidate_schema_contract.py"

SCHEMA_NAME = "glyph_clean_room_adapter_candidate_schema_validator"
STATUS = "placeholder_only_no_adapter_output"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_PLACEHOLDER_FIELDS = {
    "active_profile_round_trip_safe": False,
    "adapter_implemented": False,
    "device_write_allowed": False,
    "external_json_generated": False,
    "hardware_status": HARDWARE_STATUS,
    "loss_warnings_required": True,
    "official_compatibility_claimed": False,
    "placeholder_only": True,
    "protobuf_binary_generation_allowed": False,
    "round_trip_safe": False,
    "runtime_loaded_config_allowed": False,
    "runtime_owned_behavior_represented_in_external_profile": False,
    "runtime_owned_behavior_sidecar_required": True,
    "schema_name": "glyph_clean_room_adapter_candidate_placeholder",
    "schema_version": 1,
    "socd_policy_sidecar_required": True,
    "source_authority_promoted": False,
    "status": STATUS,
    "webserial_allowed": False,
}

REQUIRED_DOC_PHRASES = (
    "placeholder_only_no_adapter_output",
    "placeholder only",
    "adapter not implemented",
    "not adapter output",
    "not an external-remapper-compatible json candidate",
    "not round-trip safe",
    "external json is not generated",
    "no output path to external json exists",
    "no generated artifact is referenced",
)

FORBIDDEN_FIXTURE_SUBSTRINGS = (
    "docs/calibration/artifacts/",
    "docs/calibration/fixtures/glyph_offline_remapper_exported_glyphuserprofiles",
    "external_json_output_path",
    "generated_artifact",
    "generated_external_json_path",
    "output_path",
)


class CleanRoomAdapterCandidateSchemaValidatorError(ValueError):
    """Raised when the clean-room adapter candidate schema validator drifts."""


def fail(message: str) -> None:
    raise CleanRoomAdapterCandidateSchemaValidatorError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(REPO_ROOT)} must contain a JSON object")
    return payload


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def validate_contract_checker() -> None:
    checker_path = REPO_ROOT / CONTRACT_CHECKER
    if not checker_path.exists():
        fail(f"missing contract checker: {CONTRACT_CHECKER}")
    completed = subprocess.run(
        [sys.executable, CONTRACT_CHECKER],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        output = "\n".join(
            part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
        )
        fail(f"contract checker failed: {CONTRACT_CHECKER}: {output}")
    if "status=PASS" not in completed.stdout:
        fail(f"contract checker did not report PASS: {CONTRACT_CHECKER}")


def validate_placeholder_fixture() -> None:
    payload = load_json_object(FIXTURE_PATH)
    if list(payload) != sorted(REQUIRED_PLACEHOLDER_FIELDS):
        fail("placeholder fixture keys must remain canonically sorted")
    if set(payload) != set(REQUIRED_PLACEHOLDER_FIELDS):
        fail("placeholder fixture keys drifted")
    for key, value in REQUIRED_PLACEHOLDER_FIELDS.items():
        if payload.get(key) != value:
            fail(f"placeholder fixture {key} must be {value!r}")

    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    if committed_text != canonical_json_text(payload):
        fail("placeholder fixture must be canonical sorted JSON")

    lowered = committed_text.lower()
    for forbidden in FORBIDDEN_FIXTURE_SUBSTRINGS:
        if forbidden in lowered:
            fail(f"placeholder fixture must not reference generated artifact content: {forbidden}")
    for key in payload:
        key_lower = key.lower()
        if "artifact" in key_lower or "path" in key_lower:
            fail(f"placeholder fixture must not contain artifact/path key: {key}")
    for value in payload.values():
        if isinstance(value, str) and ("/" in value or value.endswith(".json")):
            fail("placeholder fixture must not reference an output path or generated artifact")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{DOC_PATH.relative_to(REPO_ROOT)} missing required phrase: {phrase}")


def main() -> int:
    print(SCHEMA_NAME)
    try:
        validate_contract_checker()
        validate_placeholder_fixture()
        validate_doc()
    except (OSError, CleanRoomAdapterCandidateSchemaValidatorError, ValueError) as exc:
        print("status=FAIL")
        print("placeholder_only=true")
        print("adapter_implemented=false")
        print("external_json_generated=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("placeholder_only=true")
    print("adapter_implemented=false")
    print("external_json_generated=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
