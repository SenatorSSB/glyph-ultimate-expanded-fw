#!/usr/bin/env python3
"""Validate the committed offline remapper SOCD drift classification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_ultimate_diff_report_2026-06-04.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_socd_drift_classification_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_socd_drift_classification"
REPORT_VERSION = 1
STATUS = "docs_tools_socd_drift_classification"
DRIFT_SEVERITY = "adapter_blocking_drift"
HARDWARE_STATUS = "not_new_hardware_result"
SOURCE_SCHEMA_NAME = "glyph_offline_remapper_ultimate_diff_report"
SOURCE_STATUS = "docs_tools_ultimate_profile_diff"

EXPECTED_FALSE_FLAGS = {
    "adapter_implemented": False,
    "official_compatibility_claimed": False,
    "hardware_validation_claimed": False,
    "external_source_promoted_to_authority": False,
}

EXPECTED_INTERPRETATION = [
    "external remapper export changes profile-level socd structure",
    "no gameplay/runtime correctness can be inferred",
    "no official compatibility claim",
]

EXPECTED_ADDED_EXPORTED_PAIRS = [
    {
        "buttonDir1": "BTN_LF2",
        "buttonDir2": "BTN_RF4",
        "socdType": "SOCD_2IP",
    },
    {
        "buttonDir1": "BTN_LF8",
        "buttonDir2": "BTN_LF6",
    },
    {
        "buttonDir1": "BTN_RF7",
        "buttonDir2": "BTN_RF8",
    },
]

EXPECTED_MISSING_FROM_EXPORTED = [
    {
        "buttonDir1": "BTN_LF5",
        "buttonDir2": "BTN_LF2",
        "socdType": "SOCD_2IP",
    }
]

REQUIRED_DOC_PHRASES = (
    "adapter_blocking_drift",
    "input socd count = 4",
    "exported socd count = 6",
    "btn_lf2/btn_rf4",
    "btn_lf8/btn_lf6",
    "btn_rf7/btn_rf8",
    "btn_lf5/btn_lf2",
    "external remapper export changes profile-level socd structure",
    "no gameplay/runtime correctness can be inferred",
    "no official compatibility claim",
    "not hardware validation",
)


class OfflineRemapperSocdDriftClassificationError(ValueError):
    """Raised when the committed SOCD drift classification drifts."""


def fail(message: str) -> None:
    raise OfflineRemapperSocdDriftClassificationError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def canonical_json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_classification() -> dict[str, Any]:
    source_report = load_json_object(SOURCE_REPORT_PATH)
    if source_report.get("schema_name") != SOURCE_SCHEMA_NAME:
        fail(f"source report schema_name must be {SOURCE_SCHEMA_NAME!r}")
    if source_report.get("status") != SOURCE_STATUS:
        fail(f"source report status must be {SOURCE_STATUS!r}")
    if source_report.get("hardware_status") != HARDWARE_STATUS:
        fail(f"source report hardware_status must be {HARDWARE_STATUS!r}")

    mode_ultimate = source_report.get("mode_ultimate_profile_diff")
    if not isinstance(mode_ultimate, dict):
        fail("source report mode_ultimate_profile_diff must be an object")

    socd_pairs = mode_ultimate.get("socdPairs")
    if not isinstance(socd_pairs, dict):
        fail("source report mode_ultimate_profile_diff.socdPairs must be an object")

    input_socd_count = socd_pairs.get("input_count")
    exported_socd_count = socd_pairs.get("exported_count")
    if not isinstance(input_socd_count, int) or not isinstance(exported_socd_count, int):
        fail("source report SOCD counts must be integers")

    added_in_exported = socd_pairs.get("added_in_exported")
    missing_from_exported = socd_pairs.get("missing_from_exported")
    if not isinstance(added_in_exported, list) or not isinstance(
        missing_from_exported, list
    ):
        fail("source report SOCD drift lists must be lists")

    return {
        "adapter_implemented": False,
        "drift_severity": DRIFT_SEVERITY,
        "external_source_promoted_to_authority": False,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "interpretation": EXPECTED_INTERPRETATION,
        "official_compatibility_claimed": False,
        "report_version": REPORT_VERSION,
        "schema_name": SCHEMA_NAME,
        "socd_drift_summary": {
            "added_exported_pairs": added_in_exported,
            "exported_socd_count": exported_socd_count,
            "input_socd_count": input_socd_count,
            "missing_from_exported_pairs": missing_from_exported,
            "socd_pairs_exact_value_equality": socd_pairs.get("exact_value_equality"),
        },
        "source_report": {
            "path": display(SOURCE_REPORT_PATH),
            "schema_name": SOURCE_SCHEMA_NAME,
            "sha256": sha256(SOURCE_REPORT_PATH),
            "status": SOURCE_STATUS,
        },
        "status": STATUS,
    }


def validate_top_level(classification: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "report_version": REPORT_VERSION,
        "status": STATUS,
        "drift_severity": DRIFT_SEVERITY,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if classification.get(key) != value:
            fail(f"{key} must be {value!r}")
    for key, value in EXPECTED_FALSE_FLAGS.items():
        if classification.get(key) != value:
            fail(f"{key} must be {value!r}")
    if classification.get("interpretation") != EXPECTED_INTERPRETATION:
        fail("interpretation drifted")


def validate_socd_drift_summary(classification: dict[str, Any]) -> None:
    summary = classification.get("socd_drift_summary")
    if not isinstance(summary, dict):
        fail("socd_drift_summary must be an object")

    expected = {
        "input_socd_count": 4,
        "exported_socd_count": 6,
        "added_exported_pairs": EXPECTED_ADDED_EXPORTED_PAIRS,
        "missing_from_exported_pairs": EXPECTED_MISSING_FROM_EXPORTED,
        "socd_pairs_exact_value_equality": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            fail(f"socd_drift_summary.{key} must be {value!r}")


def validate_source_report(classification: dict[str, Any]) -> None:
    source_report = classification.get("source_report")
    if not isinstance(source_report, dict):
        fail("source_report must be an object")
    expected = {
        "path": display(SOURCE_REPORT_PATH),
        "schema_name": SOURCE_SCHEMA_NAME,
        "status": SOURCE_STATUS,
        "sha256": sha256(SOURCE_REPORT_PATH),
    }
    for key, value in expected.items():
        if source_report.get(key) != value:
            fail(f"source_report.{key} must be {value!r}")


def validate_fixture(classification: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(classification)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated classification JSON")

    committed = load_json_object(FIXTURE_PATH)
    if committed != classification:
        fail("committed fixture JSON object drifted from regenerated classification output")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the committed docs/tools-only SOCD drift classification "
            "derived from the offline remapper MODE_ULTIMATE diff report."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of the concise validation summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        classification = build_classification()
        if args.json:
            print(canonical_json_text(classification), end="")
            return 0
        validate_top_level(classification)
        validate_socd_drift_summary(classification)
        validate_source_report(classification)
        validate_fixture(classification)
        validate_doc()
    except (
        OSError,
        OfflineRemapperSocdDriftClassificationError,
        ValueError,
    ) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print(f"drift_severity={DRIFT_SEVERITY}")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print(f"drift_severity={DRIFT_SEVERITY}")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
