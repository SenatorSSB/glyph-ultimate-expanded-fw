#!/usr/bin/env python3
"""Validate the committed offline remapper binding-loss classification."""

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
    / "docs/calibration/glyph_offline_remapper_binding_loss_classification_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json"
)

SCHEMA_NAME = "glyph_offline_remapper_binding_loss_classification"
REPORT_VERSION = 1
STATUS = "docs_tools_binding_loss_classification"
LOSS_SEVERITY = "adapter_blocking_loss"
HARDWARE_STATUS = "not_new_hardware_result"
SOURCE_SCHEMA_NAME = "glyph_offline_remapper_ultimate_diff_report"
SOURCE_STATUS = "docs_tools_ultimate_profile_diff"

EXPECTED_FALSE_FLAGS = {
    "adapter_implemented": False,
    "round_trip_safe_for_active_profile": False,
    "external_source_promoted_to_authority": False,
    "official_compatibility_claimed": False,
    "hardware_validation_claimed": False,
}

EXPECTED_INTERPRETATION = [
    "external remapper export cannot currently preserve active profile artifact identity/activation binding semantics",
    "profile-level export is not round-trip safe for our active profile artifact",
    "not evidence of firmware/runtime behavior",
]

REQUIRED_DOC_PHRASES = (
    "adapter_blocking_loss",
    "input buttonremapping count = 42",
    "exported buttonremapping count = 17",
    "input entries with activates = 42",
    "exported entries with activates = 0",
    "all input activates entries are missing or stripped in the exported profile",
    "external remapper export cannot currently preserve active profile artifact identity/activation binding semantics",
    "profile-level export is not round-trip safe for our active profile artifact",
    "not evidence of firmware/runtime behavior",
    "not official compatibility",
    "not hardware validation",
)


class OfflineRemapperBindingLossClassificationError(ValueError):
    """Raised when the committed binding-loss classification drifts."""


def fail(message: str) -> None:
    raise OfflineRemapperBindingLossClassificationError(message)


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

    button_remapping = mode_ultimate.get("buttonRemapping")
    if not isinstance(button_remapping, dict):
        fail("source report mode_ultimate_profile_diff.buttonRemapping must be an object")

    entries_with_activates = mode_ultimate.get("entries_with_activates")
    if not isinstance(entries_with_activates, dict):
        fail(
            "source report mode_ultimate_profile_diff.entries_with_activates must be an object"
        )

    missing_from_exported = button_remapping.get("missing_from_exported")
    if not isinstance(missing_from_exported, list):
        fail(
            "source report mode_ultimate_profile_diff.buttonRemapping.missing_from_exported must be a list"
        )

    input_button_remapping_count = button_remapping.get("input_count")
    exported_button_remapping_count = button_remapping.get("exported_count")
    input_entries_with_activates = entries_with_activates.get("input")
    exported_entries_with_activates = entries_with_activates.get("exported")
    if not all(
        isinstance(value, int)
        for value in (
            input_button_remapping_count,
            exported_button_remapping_count,
            input_entries_with_activates,
            exported_entries_with_activates,
        )
    ):
        fail("source report binding-loss counts must be integers")

    missing_or_stripped_count = sum(
        1
        for entry in missing_from_exported
        if isinstance(entry, dict) and "activates" in entry
    )

    all_input_activates_entries_missing_or_stripped = (
        input_entries_with_activates > 0
        and exported_entries_with_activates == 0
        and missing_or_stripped_count == input_entries_with_activates
    )

    return {
        "adapter_implemented": False,
        "binding_loss_summary": {
            "all_input_activates_entries_missing_or_stripped_in_exported_profile": (
                all_input_activates_entries_missing_or_stripped
            ),
            "button_remapping_exact_value_equality": button_remapping.get(
                "exact_value_equality"
            ),
            "exported_button_remapping_count": exported_button_remapping_count,
            "exported_entries_with_activates": exported_entries_with_activates,
            "exported_profile_retains_profile_level_structure": mode_ultimate.get(
                "exported_profile_retains_profile_level_structure"
            ),
            "input_button_remapping_count": input_button_remapping_count,
            "input_entries_missing_or_stripped_in_exported_profile": (
                missing_or_stripped_count
            ),
            "input_entries_with_activates": input_entries_with_activates,
        },
        "external_source_promoted_to_authority": False,
        "hardware_status": HARDWARE_STATUS,
        "hardware_validation_claimed": False,
        "interpretation": EXPECTED_INTERPRETATION,
        "loss_severity": LOSS_SEVERITY,
        "official_compatibility_claimed": False,
        "report_version": REPORT_VERSION,
        "round_trip_safe_for_active_profile": False,
        "schema_name": SCHEMA_NAME,
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
        "loss_severity": LOSS_SEVERITY,
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


def validate_binding_loss_summary(classification: dict[str, Any]) -> None:
    summary = classification.get("binding_loss_summary")
    if not isinstance(summary, dict):
        fail("binding_loss_summary must be an object")

    expected = {
        "input_button_remapping_count": 42,
        "exported_button_remapping_count": 17,
        "input_entries_with_activates": 42,
        "exported_entries_with_activates": 0,
        "input_entries_missing_or_stripped_in_exported_profile": 42,
        "all_input_activates_entries_missing_or_stripped_in_exported_profile": True,
        "button_remapping_exact_value_equality": False,
        "exported_profile_retains_profile_level_structure": True,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            fail(f"binding_loss_summary.{key} must be {value!r}")


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
            "Validate the committed docs/tools-only binding-loss classification "
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
    round_trip_safe = "false"
    try:
        classification = build_classification()
        if args.json:
            print(canonical_json_text(classification), end="")
            return 0
        validate_top_level(classification)
        validate_binding_loss_summary(classification)
        validate_source_report(classification)
        validate_fixture(classification)
        validate_doc()
    except (
        OSError,
        OfflineRemapperBindingLossClassificationError,
        ValueError,
    ) as exc:
        print(SCHEMA_NAME)
        print("status=FAIL")
        print(f"loss_severity={LOSS_SEVERITY}")
        print(f"round_trip_safe_for_active_profile={round_trip_safe}")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print(SCHEMA_NAME)
    print("status=PASS")
    print(f"loss_severity={LOSS_SEVERITY}")
    print(f"round_trip_safe_for_active_profile={round_trip_safe}")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
