#!/usr/bin/env python3
"""Validate the external-remapper source-misattribution correction packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT / "docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_external_remapper_misattribution_correction_2026-06-06.json"
)
OFFICIAL_MANIFEST = (
    REPO_ROOT
    / "docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json"
)
OFFICIAL_DIFF = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_official_configurator_corpus_diff_2026-06-06.json"
)

REQUIRED_TOP_LEVEL = {
    "schema_name": "glyph_external_remapper_misattribution_correction",
    "schema_version": 1,
    "packet_date": "2026-06-06",
    "status": "external_remapper_user_execution_evidence_quarantined",
}

REQUIRED_NON_CLAIMS = {
    "not_external_remapper_primary_source",
    "not_external_remapper_user_execution_evidence",
    "not_device_write_approval",
    "not_adapter_implementation_approval",
    "not_runtime_loaded_config_implementation",
    "not_protobuf_binary_write",
    "not_firmware_behavior_change",
    "not_active_profile_artifact_change",
    "not_nunchuk_validation",
    "not_gameplay_semantics",
}


class MisattributionCorrectionError(AssertionError):
    """Raised when the correction packet drifts."""


def fail(message: str) -> None:
    raise MisattributionCorrectionError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing JSON fixture: {display(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def validate_correction_fixture(payload: dict[str, Any]) -> None:
    for key, expected in REQUIRED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")

    clarification = payload.get("user_clarification")
    if not isinstance(clarification, dict):
        fail("user_clarification must be an object")
    if clarification.get("did_not_use_external_remapper_repo_or_app") is not True:
        fail("user clarification must record no external remapper use")
    if "official Glyph configurator app" not in str(
        clarification.get("GlyphUserProfilesDefault_json_source", "")
    ):
        fail("default file source must be official Glyph configurator app")
    if "official Glyph configurator app" not in str(
        clarification.get("GlyphUserProfilesBackAndForth_json_source", "")
    ):
        fail("back-and-forth file source must be official Glyph configurator app")

    corpus = payload.get("official_configurator_corpus")
    if not isinstance(corpus, dict):
        fail("official_configurator_corpus must be an object")
    if corpus.get("source_classification") != "primary_official_configurator_corpus":
        fail("official corpus must be primary_official_configurator_corpus")
    for key, expected_path in (
        ("manifest", OFFICIAL_MANIFEST),
        ("diff_fixture", OFFICIAL_DIFF),
    ):
        if corpus.get(key) != display(expected_path):
            fail(f"official_configurator_corpus.{key} path drifted")
        if not expected_path.exists():
            fail(f"official corpus referenced path missing: {display(expected_path)}")

    policy = payload.get("external_remapper_evidence_policy")
    if not isinstance(policy, dict):
        fail("external_remapper_evidence_policy must be an object")
    for key in (
        "must_not_be_used_as_primary_corpus_evidence",
        "must_not_be_treated_as_user_executed_evidence_without_independent_support",
        "existing_external_remapper_docs_are_non_authoritative_historical_pending_correction",
        "official_configurator_corpus_is_primary_export_shape_source",
    ):
        if policy.get(key) is not True:
            fail(f"external_remapper_evidence_policy.{key} must be true")

    non_claims = payload.get("explicit_non_claims")
    if not isinstance(non_claims, dict):
        fail("explicit_non_claims must be an object")
    missing = sorted(REQUIRED_NON_CLAIMS - set(non_claims))
    if missing:
        fail("explicit_non_claims missing: " + ", ".join(missing))
    for key in sorted(REQUIRED_NON_CLAIMS):
        if non_claims.get(key) is not True:
            fail(f"explicit_non_claims.{key} must be true")


def validate_docs(payload: dict[str, Any]) -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())
    for phrase in (
        "did not use or touch the custom external remapper",
        "official Glyph configurator app artifacts",
        "not valid user-provided evidence",
        "quarantined as non-authoritative",
        "official configurator corpus is now the primary source",
    ):
        if phrase.lower() not in normalized_text.lower():
            fail(f"correction doc missing required phrase: {phrase}")

    notice_title = payload.get("required_correction_notice_title")
    if notice_title != "CORRECTION / SOURCE MISATTRIBUTION":
        fail("required_correction_notice_title drifted")
    for rel_path in payload.get("quarantined_external_remapper_packets", []):
        if not isinstance(rel_path, str):
            fail("quarantined_external_remapper_packets entries must be strings")
        path = REPO_ROOT / rel_path
        if not path.exists():
            fail(f"quarantined packet missing: {rel_path}")
        packet_text = path.read_text(encoding="utf-8")
        normalized_packet_text = " ".join(packet_text.split())
        required = [
            "CORRECTION / SOURCE MISATTRIBUTION",
            "official Glyph configurator app artifacts",
            "quarantined",
            "must not be used as primary corpus evidence",
        ]
        for phrase in required:
            if phrase.lower() not in normalized_packet_text.lower():
                fail(f"{rel_path} missing correction phrase: {phrase}")


def main() -> int:
    print("glyph_external_remapper_misattribution_correction")
    try:
        payload = load_json_object(FIXTURE_PATH)
        validate_correction_fixture(payload)
        validate_docs(payload)
    except (OSError, MisattributionCorrectionError, ValueError) as exc:
        print("status=FAIL")
        print("external_remapper_user_execution_evidence=quarantined")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("external_remapper_user_execution_evidence=quarantined")
    print("official_configurator_corpus_primary=true")
    print("not_external_remapper_primary_source=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
