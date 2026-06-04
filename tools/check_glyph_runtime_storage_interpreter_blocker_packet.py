#!/usr/bin/env python3
"""Validate the Glyph runtime storage/interpreter blocker packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.json"
)

SCHEMA_NAME = "glyph_runtime_storage_interpreter_blocker_packet"
PACKET_VERSION = 1
STATUS = "blocked_pending_design_source_authority_and_user_approval"
HARDWARE_STATUS = "not_new_hardware_result"
REQUIRED_UNRESOLVED_DESIGN_DECISIONS = {
    "storage location",
    "representation",
    "boot-time validation",
    "fallback policy",
    "version migration",
    "maximum config size",
    "profile-bound vs global scope",
    "latency/performance evidence",
    "hardware validation plan",
    "nunchuk decision",
}
REQUIRED_FIRMWARE_OWNED_SEMANTICS = {
    "evaluator phase order",
    "allowed role classes",
}
REQUIRED_FORBIDDEN_CONFIG_CAPABILITIES = {
    "scripts",
    "macros",
    "turbo",
    "timing",
    "history-dependent logic",
    "phase-order mutation",
}
REQUIRED_DOC_PHRASES = (
    "runtime-loaded config not implemented",
    "storage not implemented",
    "interpreter not implemented",
    "firmware owns evaluator phase order",
    "config must not own scripts/macros/turbo/timing/history",
    "not hardware validation",
)


class BlockerPacketError(ValueError):
    """Raised when the runtime storage/interpreter blocker packet drifts."""


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
        "runtime_loaded_config_implemented": False,
        "storage_implemented": False,
        "interpreter_implemented": False,
        "external_source_promoted_to_authority": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_required_subset(fixture: dict[str, Any], key: str, required: set[str]) -> None:
    observed = set(require_string_list(fixture.get(key), key))
    missing = sorted(required - observed)
    if missing:
        fail(f"{key} is missing required entries: " + ", ".join(missing))


def validate_lists(fixture: dict[str, Any]) -> None:
    for key in (
        "required_missing_evidence",
        "required_approval",
        "source_backed_inputs",
        "doc_caveats",
    ):
        require_string_list(fixture.get(key), key)

    for relpath in fixture["source_backed_inputs"]:
        if relpath.startswith(("http://", "https://")):
            fail(f"source_backed_inputs must reference repo files only: {relpath}")
        if not (REPO_ROOT / relpath).exists():
            fail(f"source_backed_inputs references missing path: {relpath}")


def validate_doc(fixture: dict[str, Any]) -> None:
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")
    for phrase in fixture["doc_caveats"]:
        if phrase.lower() not in text:
            fail(f"{display(DOC_PATH)} missing fixture-declared caveat phrase: {phrase}")


def main() -> int:
    print("glyph_runtime_storage_interpreter_blocker_packet")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_required_subset(
            fixture,
            "required_unresolved_design_decisions",
            REQUIRED_UNRESOLVED_DESIGN_DECISIONS,
        )
        validate_required_subset(
            fixture,
            "firmware_owned_semantics",
            REQUIRED_FIRMWARE_OWNED_SEMANTICS,
        )
        validate_required_subset(
            fixture,
            "forbidden_config_capabilities",
            REQUIRED_FORBIDDEN_CONFIG_CAPABILITIES,
        )
        validate_lists(fixture)
        validate_doc(fixture)
    except (OSError, BlockerPacketError, ValueError) as exc:
        print("status=FAIL")
        print("runtime_loaded_config_implemented=false")
        print("storage_implemented=false")
        print("interpreter_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("runtime_loaded_config_implemented=false")
    print("storage_implemented=false")
    print("interpreter_implemented=false")
    print(f"hardware_status={fixture['hardware_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
