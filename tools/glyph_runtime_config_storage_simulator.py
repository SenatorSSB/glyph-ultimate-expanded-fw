#!/usr/bin/env python3
"""Design-time runtime-config storage simulator for Phase 7A/7B planning.

This does not use firmware Persistence, does not read or write config.bin, does
not write device state, and does not describe runtime-loaded firmware behavior.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from glyph_runtime_config_candidate_generator import build_valid_payload
    from glyph_runtime_config_parser_oracle import parse_payload
except ModuleNotFoundError:
    from tools.glyph_runtime_config_candidate_generator import build_valid_payload
    from tools.glyph_runtime_config_parser_oracle import parse_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7b_storage_simulation_report.json"


@dataclass(frozen=True)
class SimulationResult:
    case_id: str
    storage_present: bool
    accepted_candidate: bool
    fallback_to_source_owned_baseline: bool
    error_code: str


def scenarios() -> dict[str, bytes | None]:
    valid = build_valid_payload()
    return {
        "missing_storage": None,
        "valid_storage": valid,
        "corrupt_storage": valid[:20] + b"corrupt",
        "wrong_version": valid[:4] + bytes([valid[4] + 1]) + valid[5:],
        "wrong_checksum": valid[:-1] + bytes([valid[-1] ^ 0x80]),
        "invalid_payload": b"not-a-gcfg-runtime-config-payload",
    }


def simulate_storage(payload: bytes | None, case_id: str) -> SimulationResult:
    if payload is None:
        return SimulationResult(
            case_id=case_id,
            storage_present=False,
            accepted_candidate=False,
            fallback_to_source_owned_baseline=True,
            error_code="storage:missing",
        )
    parsed = parse_payload(payload)
    return SimulationResult(
        case_id=case_id,
        storage_present=True,
        accepted_candidate=parsed.accepted,
        fallback_to_source_owned_baseline=not parsed.accepted,
        error_code=parsed.error_code,
    )


def build_report() -> dict[str, object]:
    results = [simulate_storage(payload, case_id) for case_id, payload in scenarios().items()]
    return {
        "schema_name": "glyph_phase7b_design_time_storage_simulation_report",
        "schema_version": 1,
        "status": "design_time_simulation_only_not_firmware_storage",
        "not_firmware_storage": True,
        "not_config_bin": True,
        "not_device_write": True,
        "not_runtime_loaded_firmware_behavior": True,
        "fallback_policy_simulated": "fallback_to_source_owned_baseline",
        "cases": [asdict(result) for result in results],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("status=PASS")
        print(f"cases={len(report['cases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
