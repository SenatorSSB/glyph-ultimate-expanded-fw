#!/usr/bin/env python3
"""Check the committed Glyph runtime config validation report artifacts."""

from __future__ import annotations

import json

from generate_glyph_runtime_config_validation_report import (
    REPORT_SCHEMA_NAME,
    REPORT_STATUS,
    REPORT_VERSION,
    REPO_ROOT,
    build_report,
    display,
)


FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json"
)
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_runtime_config_validation_report_2026-06-03.md"
REQUIRED_DOC_PHRASES = (
    "offline docs/tools report only",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)


class RuntimeConfigValidationReportCheckError(ValueError):
    """Raised when committed report artifacts drift from regenerated output."""


def fail(message: str) -> None:
    raise RuntimeConfigValidationReportCheckError(message)


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_runtime_config_validation_report")
    try:
        regenerated = build_report()
        committed_text = FIXTURE_PATH.read_text(encoding="utf-8")
        expected_text = json.dumps(regenerated, indent=2, sort_keys=True) + "\n"
        if committed_text != expected_text:
            fail("committed report fixture does not exactly match regenerated output")
        committed = json.loads(committed_text)
        if committed.get("schema_name") != REPORT_SCHEMA_NAME:
            fail("committed report schema_name drifted")
        if committed.get("report_version") != REPORT_VERSION:
            fail("committed report version drifted")
        if committed.get("status") != REPORT_STATUS:
            fail("committed report status drifted")
        validate_doc()
    except (OSError, ValueError, RuntimeConfigValidationReportCheckError) as exc:
        print("status=FAIL")
        print("sample_candidate_validation_status=unknown")
        print("invalid_corpus_case_count=0")
        print("table_count=0")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"sample_candidate_validation_status={committed['sample_candidate_validation_status']}")
    print(f"invalid_corpus_case_count={committed['invalid_corpus_case_count']}")
    print(f"table_count={committed['table_count']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
