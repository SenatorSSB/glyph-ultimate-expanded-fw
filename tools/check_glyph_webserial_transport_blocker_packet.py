#!/usr/bin/env python3
"""Validate the Glyph WebSerial transport blocker packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json"
)

SCHEMA_NAME = "glyph_webserial_transport_blocker_packet"
PACKET_VERSION = 1
STATUS = "blocked_pending_source_authority_and_user_approval"
HARDWARE_STATUS = "not_new_hardware_result"
REQUIRED_MISSING_AUTHORITY = {
    "official packet framing",
    "official configurator behavior source",
}
REQUIRED_FUTURE_EVIDENCE = {
    "source-backed packet framing",
    "safe no-device dry-run",
    "readback strategy",
    "rollback plan",
    "hardware test plan",
    "user approval",
    "no accidental Save to Device path",
    "no firmware flashing path",
}
REQUIRED_FORBIDDEN_CLAIMS = {
    "WebSerial transport is implemented",
    "WebSerial write is implemented",
    "serial dry-run is live device access",
    "device write is implemented",
    "Save to Device is implemented",
    "firmware flashing is implemented",
    "official packet framing authority is available",
    "official configurator behavior source is available",
    "external WebSerial observations are authoritative",
    "hardware validation has been performed",
}
REQUIRED_APPROVAL = {
    "explicit user approval for any WebSerial implementation path",
    "explicit user approval for any serial/device write or Save to Device path",
    "explicit user approval for any firmware flashing path",
    "source-authority review approval for packet framing and official configurator behavior claims",
    "hardware-test-plan approval before any implementation branch can claim hardware results",
}
REQUIRED_DOC_PHRASES = (
    "serial dry-run is not live device access",
    "WebSerial write not implemented",
    "device write not implemented",
    "firmware flashing not implemented",
    "external WebSerial observations non-authoritative",
    "not hardware validation",
)


class BlockerPacketError(ValueError):
    """Raised when the WebSerial transport blocker packet drifts."""


def fail(message: str) -> None:
    raise BlockerPacketError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty string list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{label}[{index}] must be a non-empty string")
        result.append(item)
    return result


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "packet_version": PACKET_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "current_serial_dry_run_exists": True,
        "serial_dry_run_is_live_device_access": False,
        "webserial_transport_implemented": False,
        "device_write_implemented": False,
        "firmware_flashing_implemented": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_required_missing_authority(fixture: dict[str, Any]) -> None:
    missing_authority = set(
        require_string_list(
            fixture.get("required_missing_authority"),
            "required_missing_authority",
        )
    )
    missing = sorted(REQUIRED_MISSING_AUTHORITY - missing_authority)
    if missing:
        fail("required_missing_authority is missing required entries: " + ", ".join(missing))


def validate_required_future_evidence(fixture: dict[str, Any]) -> None:
    future_evidence = set(
        require_string_list(
            fixture.get("required_future_evidence"),
            "required_future_evidence",
        )
    )
    missing = sorted(REQUIRED_FUTURE_EVIDENCE - future_evidence)
    if missing:
        fail("required_future_evidence is missing required entries: " + ", ".join(missing))


def validate_required_subset(fixture: dict[str, Any], key: str, required: set[str]) -> None:
    observed = set(require_string_list(fixture.get(key), key))
    missing = sorted(required - observed)
    if missing:
        fail(f"{key} is missing required entries: " + ", ".join(missing))


def validate_lists(fixture: dict[str, Any]) -> None:
    for label in (
        "forbidden_current_claims",
        "required_approval",
        "source_backed_inputs",
        "doc_caveats",
    ):
        require_string_list(fixture.get(label), label)

    for relpath in fixture["source_backed_inputs"]:
        if relpath.startswith(("http://", "https://")):
            fail(f"source_backed_inputs must reference repo files only: {relpath}")
        if not (REPO_ROOT / relpath).exists():
            fail(f"source_backed_inputs references missing path: {relpath}")
    validate_required_subset(fixture, "forbidden_current_claims", REQUIRED_FORBIDDEN_CLAIMS)
    validate_required_subset(fixture, "required_approval", REQUIRED_APPROVAL)


def validate_doc(fixture: dict[str, Any]) -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")
    for phrase in fixture["doc_caveats"]:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing fixture-declared caveat phrase: {phrase}")


def main() -> int:
    print("glyph_webserial_transport_blocker_packet")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_required_missing_authority(fixture)
        validate_required_future_evidence(fixture)
        validate_lists(fixture)
        validate_doc(fixture)
    except (OSError, BlockerPacketError, ValueError) as exc:
        print("status=FAIL")
        print("webserial_transport_implemented=false")
        print("device_write_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("webserial_transport_implemented=false")
    print("device_write_implemented=false")
    print(f"hardware_status={fixture['hardware_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
