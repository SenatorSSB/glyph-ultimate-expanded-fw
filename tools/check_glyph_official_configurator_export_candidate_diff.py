#!/usr/bin/env python3
"""Validate the offline candidate diff/simulation report."""

from __future__ import annotations

import json

from glyph_official_configurator_corpus import CorpusError, load_json_object, sha256_file
from glyph_official_configurator_export_candidate_diff import (
    DIFF_REPORT_JSON,
    DIFF_REPORT_MD,
    GENERATED_PREVIEW_PATH,
    build_report,
    markdown_report,
)


def fail(message: str) -> None:
    raise CorpusError(message)


def main() -> int:
    print("glyph_official_configurator_export_candidate_diff")
    try:
        committed = load_json_object(DIFF_REPORT_JSON)
        expected = build_report()
        if committed != expected:
            fail("candidate diff fixture does not match deterministic diff output")
        if committed.get("status") != "OFFLINE_DIFF_SIMULATION_ONLY":
            fail("candidate diff status must remain OFFLINE_DIFF_SIMULATION_ONLY")
        if committed["inputs"].get("generated_candidate_preview_sha256") != sha256_file(GENERATED_PREVIEW_PATH):
            fail("candidate diff generated preview hash must match committed preview")
        non_claims = committed.get("non_claims", {})
        if non_claims.get("manual_official_configurator_app_interaction_occurred") is not False:
            fail("candidate diff must state no manual official configurator app interaction occurred")
        for key in (
            "no_compatibility_claim",
            "no_production_export",
            "no_device_write",
            "no_runtime_loaded_config",
            "no_webserial",
            "no_firmware_flashing_automation",
            "no_nunchuk_validation",
        ):
            if non_claims.get(key) is not True:
                fail(f"candidate diff non-claim {key} must be true")
        expected_md = markdown_report(committed)
        if DIFF_REPORT_MD.read_text(encoding="utf-8") != expected_md:
            fail("candidate diff Markdown report does not match deterministic content")
    except (CorpusError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print("offline_diff_simulation_only=true")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("offline_diff_simulation_only=true")
    print("manual_official_configurator_app_interaction=false")
    print("official_configurator_compatibility_claim=false")
    print("production_export=false")
    print("device_write=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
