#!/usr/bin/env python3
"""Validate the committed offline remapper export structural diff artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

from analyze_glyph_offline_remapper_export_diff import (
    ACTIVE_ARTIFACT_PATH,
    ANALYSIS_VERSION,
    CAVEATS,
    EXPORTED_ARTIFACT_PATH,
    HARDWARE_STATUS,
    SCHEMA_NAME,
    STATUS,
    build_summary,
    canonical_json_text,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_export_structural_diff_2026-06-04.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_export_structural_diff_2026-06-04.json"
)


class OfflineRemapperExportStructuralDiffCheckError(ValueError):
    """Raised when the structural diff artifacts drift from committed expectations."""


def fail(message: str) -> None:
    raise OfflineRemapperExportStructuralDiffCheckError(message)


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


def validate_top_level(summary: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "analysis_version": ANALYSIS_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_fixture(summary: dict[str, Any]) -> None:
    committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
    expected_text = canonical_json_text(summary)
    if committed_text != expected_text:
        fail("committed fixture does not exactly match regenerated analyzer JSON")

    committed = load_json_object(FIXTURE_PATH)
    if committed != summary:
        fail("committed fixture JSON object drifted from regenerated analyzer output")

    for label, artifact_path in (
        ("input_artifact", ACTIVE_ARTIFACT_PATH),
        ("exported_artifact", EXPORTED_ARTIFACT_PATH),
    ):
        artifact = committed.get(label)
        if not isinstance(artifact, dict):
            fail(f"{label} must be an object")
        if artifact.get("path") != display(artifact_path):
            fail(f"{label}.path must be {display(artifact_path)!r}")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in CAVEATS:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required caveat phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_export_structural_diff")
    objects_equal = "unknown"
    byte_hashes_equal = "unknown"
    try:
        summary = build_summary()
        validate_top_level(summary)
        validate_fixture(summary)
        validate_doc()
        objects_equal = str(summary["objects_equal"]).lower()
        byte_hashes_equal = str(summary["byte_hashes_equal"]).lower()
    except (
        OSError,
        OfflineRemapperExportStructuralDiffCheckError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print(f"objects_equal={objects_equal}")
        print(f"byte_hashes_equal={byte_hashes_equal}")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"objects_equal={objects_equal}")
    print(f"byte_hashes_equal={byte_hashes_equal}")
    print(f"hardware_status={HARDWARE_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
