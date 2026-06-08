#!/usr/bin/env python3
"""Validate the Phase 7A/7B design-time storage simulator report."""

from __future__ import annotations

import json

try:
    from glyph_runtime_config_storage_simulator import REPORT_PATH, build_report
except ModuleNotFoundError:
    from tools.glyph_runtime_config_storage_simulator import REPORT_PATH, build_report


class StorageSimulatorError(ValueError):
    """Raised when the design-time storage simulator drifts."""


def fail(message: str) -> None:
    raise StorageSimulatorError(message)


def main() -> int:
    if not REPORT_PATH.exists():
        fail(f"missing storage simulation report: {REPORT_PATH}")
    expected = build_report()
    actual = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    if actual != expected:
        fail("storage simulation report does not regenerate deterministically")
    for key in (
        "not_firmware_storage",
        "not_config_bin",
        "not_device_write",
        "not_runtime_loaded_firmware_behavior",
    ):
        if actual.get(key) is not True:
            fail(f"report.{key} must be true")
    cases = {case["case_id"]: case for case in actual.get("cases", [])}
    expected_cases = {
        "missing_storage": (False, True),
        "valid_storage": (True, False),
        "corrupt_storage": (False, True),
        "wrong_version": (False, True),
        "wrong_checksum": (False, True),
        "invalid_payload": (False, True),
    }
    if set(cases) != set(expected_cases):
        fail("storage simulation cases mismatch")
    for case_id, (accepted, fallback) in expected_cases.items():
        case = cases[case_id]
        if case["accepted_candidate"] != accepted:
            fail(f"{case_id}.accepted_candidate mismatch")
        if case["fallback_to_source_owned_baseline"] != fallback:
            fail(f"{case_id}.fallback_to_source_owned_baseline mismatch")
    print("status=PASS")
    print(f"cases={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
