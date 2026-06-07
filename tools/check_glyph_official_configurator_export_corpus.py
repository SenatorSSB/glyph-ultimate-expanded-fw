#!/usr/bin/env python3
"""Validate the user-provided official Glyph configurator export corpus."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from glyph_official_configurator_corpus import (
    BACK_AND_FORTH_FIXTURE_REL,
    CORPUS_ID,
    DEFAULT_FIXTURE_REL,
    FORBIDDEN_NON_CLAIMS,
    MANIFEST_PATH,
    NOTES_PATH,
    REQUIRED_TOP_LEVEL_KEYS,
    CorpusError,
    display,
    fixture_paths,
    load_fixtures,
    load_json_object,
)


EXPECTED_SOURCE_KIND = "official_glyph_configurator_user_provided_export"
EXPECTED_CLASSIFICATION = "primary_official_configurator_corpus"


def fail(message: str) -> None:
    raise CorpusError(message)


def current_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        check=False,
        cwd=MANIFEST_PATH.parents[4],
        text=True,
    )
    if completed.returncode != 0:
        fail(completed.stderr.strip() or completed.stdout.strip() or "git rev-parse failed")
    return completed.stdout.strip()


def validate_manifest(manifest: dict[str, Any]) -> None:
    expected_pairs = {
        "corpus_id": CORPUS_ID,
        "source_kind": EXPECTED_SOURCE_KIND,
        "source_classification": EXPECTED_CLASSIFICATION,
    }
    for key, expected in expected_pairs.items():
        if manifest.get(key) != expected:
            fail(f"manifest.{key} must be {expected!r}")

    if manifest.get("captured_at") not in {"2026-06-06", "UNKNOWN_EXACT_TIMESTAMP"}:
        fail("manifest.captured_at must be 2026-06-06 or UNKNOWN_EXACT_TIMESTAMP")
    if manifest.get("captured_by") != "Rasmus / user-provided":
        fail("manifest.captured_by must be Rasmus / user-provided")
    if manifest.get("glyph_repo_commit") != current_commit():
        fail("manifest.glyph_repo_commit must match current HEAD")
    if manifest.get("firmware_source_commit") != manifest.get("glyph_repo_commit"):
        fail("manifest.firmware_source_commit must match glyph_repo_commit for this corpus")
    if manifest.get("configurator_source_reference") != "UNKNOWN_NOT_PROVIDED":
        fail("manifest.configurator_source_reference must remain UNKNOWN_NOT_PROVIDED")
    if manifest.get("configurator_version_label") != "UNKNOWN_NOT_PROVIDED":
        fail("manifest.configurator_version_label must remain UNKNOWN_NOT_PROVIDED")

    fixture_files = manifest.get("fixture_files")
    expected_files = [DEFAULT_FIXTURE_REL, BACK_AND_FORTH_FIXTURE_REL]
    if fixture_files != expected_files:
        fail("manifest.fixture_files must match expected stable fixture names")
    if manifest.get("fixture_roles") != ["default_profiles", "back_and_forth_custom_profile"]:
        fail("manifest.fixture_roles must match expected roles")

    non_claims = manifest.get("explicit_non_claims")
    if not isinstance(non_claims, dict):
        fail("manifest.explicit_non_claims must be an object")
    missing = sorted(FORBIDDEN_NON_CLAIMS - set(non_claims))
    if missing:
        fail("manifest.explicit_non_claims missing: " + ", ".join(missing))
    for key in sorted(FORBIDDEN_NON_CLAIMS):
        if non_claims.get(key) is not True:
            fail(f"manifest.explicit_non_claims.{key} must be true")


def validate_fixture(role: str, payload: dict[str, Any]) -> None:
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in payload:
            fail(f"{role} missing top-level key: {key}")
    modes = payload.get("gameModeConfigs")
    if not isinstance(modes, list):
        fail(f"{role}.gameModeConfigs must be a list")
    if not any(isinstance(mode, dict) and mode.get("modeId") == "MODE_ULTIMATE" for mode in modes):
        fail(f"{role} must include at least one MODE_ULTIMATE game mode")


def validate_notes() -> None:
    if not NOTES_PATH.exists():
        fail(f"missing notes doc: {display(NOTES_PATH)}")
    text = NOTES_PATH.read_text(encoding="utf-8")
    required_phrases = [
        "official Glyph configurator app JSON files",
        "must not be attributed to the external remapper",
        "default profiles JSON",
        "custom profile pushed through and downloaded/exported back",
        "primary evidence for official configurator JSON export shape",
        "does not itself implement adapter generation or device write",
    ]
    for phrase in required_phrases:
        if phrase.lower() not in text.lower():
            fail(f"notes missing required phrase: {phrase}")


def main() -> int:
    print("glyph_official_configurator_export_corpus")
    try:
        manifest = load_json_object(MANIFEST_PATH)
        validate_manifest(manifest)
        fixtures = load_fixtures()
        for role, payload in fixtures.items():
            validate_fixture(role, payload)
        default = fixtures["default_profiles"]
        back = fixtures["back_and_forth_custom_profile"]
        if default == back:
            fail("default and back-and-forth fixtures must not be identical")
        if set(default) != set(back):
            fail("top-level key set must be stable between fixtures")
        changed_top_level = [key for key in REQUIRED_TOP_LEVEL_KEYS if default.get(key) != back.get(key)]
        if not changed_top_level:
            fail("changed top-level sections must be identified")
        for role, path in fixture_paths().items():
            if not path.exists():
                fail(f"missing fixture file for {role}: {display(path)}")
            json.loads(path.read_text(encoding="utf-8"))
        validate_notes()
    except (CorpusError, OSError, json.JSONDecodeError) as exc:
        print("status=FAIL")
        print(f"corpus_id={CORPUS_ID}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"corpus_id={CORPUS_ID}")
    print("fixture_count=2")
    print("top_level_keys_stable=true")
    print("fixtures_differ=true")
    print("not_external_remapper=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
