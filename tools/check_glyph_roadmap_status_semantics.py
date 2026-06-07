#!/usr/bin/env python3
"""Validate current Glyph roadmap status semantics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
WORKFLOW = REPO_ROOT / "docs/WORKFLOW.md"
ROADMAP_FIXTURE = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_roadmap_next_work_index_2026-06-06.json"
)

STATUS_TERMS = (
    "COMPLETE",
    "CURRENT_BASELINE",
    "READY_FOR_ENGINEERING_DESIGN",
    "READY_FOR_SOURCE_RESEARCH",
    "READY_FOR_PROTOTYPE",
    "READY_FOR_USER_PRODUCT_DECISION",
    "WAITING_FOR_USER_ARTIFACT",
    "WAITING_FOR_HARDWARE_TEST",
    "FUTURE_PHASE",
    "NOT_STARTED",
    "FORBIDDEN_BY_POLICY",
    "OUT_OF_SCOPE",
)

REQUIREMENT_FIELDS = (
    "requires_user_domain_input",
    "requires_user_product_approval",
    "requires_source_research",
    "requires_hardware_test",
    "requires_user_artifact",
    "requires_firmware_change",
    "requires_safety_review",
    "requires_schema_decision",
    "requires_transport_authority",
)


class RoadmapStatusSemanticsError(AssertionError):
    """Raised when roadmap status semantics drift."""


def fail(message: str) -> None:
    raise RoadmapStatusSemanticsError(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def load_fixture() -> dict[str, Any]:
    if not ROADMAP_FIXTURE.exists():
        fail(f"missing fixture: {ROADMAP_FIXTURE.relative_to(REPO_ROOT)}")
    payload = json.loads(ROADMAP_FIXTURE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail("roadmap fixture must be an object")
    return payload


def item(payload: dict[str, Any], item_id: str) -> dict[str, Any]:
    for raw in payload.get("roadmap_items", []):
        if isinstance(raw, dict) and raw.get("item_id") == item_id:
            return raw
    fail(f"roadmap fixture missing item: {item_id}")


def require_phrases(name: str, text: str, phrases: tuple[str, ...]) -> None:
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        fail(f"{name} missing required phrases: " + ", ".join(missing))


def validate_docs() -> None:
    roadmap = read(ROADMAP)
    current = read(CURRENT_STATE)
    workflow = read(WORKFLOW)

    require_phrases("docs/ROADMAP.md", roadmap, ("Status Taxonomy", *STATUS_TERMS, *REQUIREMENT_FIELDS))
    require_phrases(
        "docs/CURRENT_STATE.md",
        current,
        (
            "Current Readiness Categories",
            "The user is not currently blocking runtime-loaded config",
            "Those items are not implemented because they are future",
            "Engineering design and source-research branches may proceed",
            "User domain input is required only for product/domain choices",
            "Forbidden by policy",
        ),
    )
    require_phrases(
        "docs/WORKFLOW.md",
        workflow,
        (
            "Docs/tools, source research, and engineering design can proceed autonomously",
            "User domain input is not required for routine engineering design",
            "User product approval is required before",
            "Hardware tests are required only after a firmware/candidate artifact exists",
            "Avoid `blocked` for current status unless the task is actually waiting on a",
            "specific external item",
        ),
    )


def validate_fixture() -> None:
    payload = load_fixture()
    if payload.get("schema_version") != 2:
        fail("roadmap fixture schema_version must be 2")
    if set(payload.get("requirement_fields", [])) != set(REQUIREMENT_FIELDS):
        fail("roadmap fixture must list separate requirement fields")

    generated_cpp = item(payload, "generated_cpp_constants_firmware_build_path")
    if generated_cpp.get("current_status") != "READY_FOR_ENGINEERING_DESIGN":
        fail("generated C++ constants path must be READY_FOR_ENGINEERING_DESIGN")
    if generated_cpp.get("requires_user_domain_input") is not False:
        fail("generated C++ constants path must not require user domain input")
    if generated_cpp.get("requires_user_product_approval") is not True:
        fail("generated C++ constants path must require product approval before firmware implementation")

    runtime = item(payload, "runtime_loaded_config_implementation")
    if runtime.get("current_status") != "FUTURE_PHASE":
        fail("runtime-loaded config must be FUTURE_PHASE")
    if runtime.get("requires_user_domain_input") is not False:
        fail("runtime-loaded config must not be user-domain-blocked")

    webserial = item(payload, "webserial_device_write")
    if webserial.get("current_status") != "FUTURE_PHASE":
        fail("WebSerial/device write must be FUTURE_PHASE")
    if webserial.get("requires_user_domain_input") is not False:
        fail("WebSerial/device write must not be user-domain-blocked")
    if webserial.get("requires_transport_authority") is not True:
        fail("WebSerial/device write must require transport authority")

    nunchuk = item(payload, "nunchuk_hardware_validation_claim")
    if nunchuk.get("current_status") != "OUT_OF_SCOPE":
        fail("nunchuk must be out of scope for current hardware")
    if nunchuk.get("requires_hardware_test") is not False:
        fail("nunchuk must not be a general implementation blocker")

    for item_id in ("firmware_flashing_automation", "external_source_code_reuse"):
        if item(payload, item_id).get("current_status") != "FORBIDDEN_BY_POLICY":
            fail(f"{item_id} must remain FORBIDDEN_BY_POLICY")


def main() -> int:
    print("glyph_roadmap_status_semantics")
    try:
        validate_docs()
        validate_fixture()
    except (OSError, json.JSONDecodeError, RoadmapStatusSemanticsError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("status_taxonomy=current")
    print("requirements_separated=true")
    print("runtime_loaded_config_user_domain_blocked=false")
    print("webserial_device_write_user_domain_blocked=false")
    print("nunchuk_general_implementation_blocker=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
