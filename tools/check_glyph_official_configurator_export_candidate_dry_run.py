#!/usr/bin/env python3
"""Validate the offline official configurator candidate dry-run output."""

from __future__ import annotations

import json

from glyph_official_configurator_export_candidate_dry_run import (
    BLOCKED_CLAIMS,
    LABELS,
    PREVIEW_PATH,
    REPORT_PATH,
    build_preview,
)
from glyph_official_configurator_corpus import CorpusError, load_json_object, sha256_file


def fail(message: str) -> None:
    raise CorpusError(message)


def require_false_flags(flags: dict[str, object]) -> None:
    for key in (
        "production_export_created",
        "device_write_created",
        "webserial_created",
        "runtime_loaded_config_created",
        "official_compatibility_claimed",
        "firmware_flashing_automation_created",
        "nunchuk_validation_claimed",
    ):
        if flags.get(key) is not False:
            fail(f"{key} must be false")


def main() -> int:
    print("glyph_official_configurator_export_candidate_dry_run")
    try:
        committed = load_json_object(PREVIEW_PATH)
        expected = build_preview()
        if committed != expected:
            fail("generated preview fixture does not match deterministic dry-run output")
        if committed.get("status") != "offline_preview_only":
            fail("generated preview status must be offline_preview_only")
        if committed.get("preview_labels") != LABELS:
            fail("generated preview labels drifted")
        if committed.get("blocked_claims") != BLOCKED_CLAIMS:
            fail("generated preview blocked claims drifted")
        require_false_flags(committed.get("output_boundary", {}))

        report = load_json_object(REPORT_PATH)
        if report.get("status") != "OFFLINE_DRY_RUN_REPORT_ONLY":
            fail("generated dry-run report must remain report-only")
        if report.get("preview_sha256") != sha256_file(PREVIEW_PATH):
            fail("generated dry-run report preview hash must match committed preview")
        if report.get("labels") != LABELS:
            fail("generated dry-run report labels drifted")
        if report.get("blocked_claims") != BLOCKED_CLAIMS:
            fail("generated dry-run report blocked claims drifted")
        require_false_flags(report.get("non_claims", {}))
    except (CorpusError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print("offline_dry_run_only=true")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("offline_dry_run_only=true")
    print("production_export_created=false")
    print("official_configurator_compatibility_claim=false")
    print("device_write_created=false")
    print("webserial_created=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
