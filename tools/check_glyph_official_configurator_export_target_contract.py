#!/usr/bin/env python3
"""Validate the official configurator export target contract."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_BRANCH = "configurator"

SOURCE_AUTHORITY_DOC = REPO_ROOT / "docs/export/official_configurator_export_source_authority.md"
TARGET_CONTRACT_DOC = REPO_ROOT / "docs/export/official_configurator_export_target_contract.md"
EXPORT_README = REPO_ROOT / "docs/export/README.md"
PREVIEW_FIXTURE = REPO_ROOT / "docs/export/fixtures/official_configurator_export_candidate_preview.json"
BLOCKER_DOC = REPO_ROOT / "docs/export/official_configurator_export_candidate_blocker.md"
INVALID_CORPUS = REPO_ROOT / "docs/export/fixtures/official_configurator_export_invalid_cases.json"

MANIFEST_PATH = (
    REPO_ROOT / "docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json"
)
DEFAULT_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/"
    "glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json"
)
BACK_AND_FORTH_FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/"
    "glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json"
)

ALLOWED_CHANGED_PREFIXES = (
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/WORKFLOW.md",
    "docs/release/",
    "docs/calibration/",
    "docs/runtime_config/",
    "docs/export/",
    "tools/",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
    "lib/",
    "scripts/",
)

REQUIRED_SOURCE_AUTHORITY_PHRASES = (
    "OFFLINE_SOURCE_AUTHORITY_RECORDED",
    "primary_official_configurator_corpus",
    "external-remapper records remain quarantined",
    "no production export claim",
    "no official configurator compatibility claim",
    "no device write claim",
    "no WebSerial claim",
    "no runtime-loaded config claim",
    "no firmware flashing automation claim",
)

REQUIRED_CONTRACT_PHRASES = (
    "OFFLINE_CONTRACT_ONLY",
    "Allowed Input Classes",
    "Allowed Output Preview Classes",
    "Source-Backed Field Subset",
    "Required Metadata And Provenance",
    "Required Hashes",
    "Observable Boundary",
    "Unsupported Or Unknown Fields",
    "Validation Rules",
    "Invalid Classes",
    "Round-Trip Expectations",
    "Stop Line Before Production Export",
    "Stop Lines",
    "Explicit Non-Claims",
    "offline preview only",
    "not production export",
    "not device write",
    "not webserial",
    "not runtime-loaded config",
    "not official compatibility claim",
)

REQUIRED_README_PHRASES = (
    "Official Configurator Export Target Docs",
    "offline-only, source-backed export-target contract documentation",
    "do not add production export output here",
    "do not add device-write or WebSerial workflows here",
    "keep preview fixtures explicitly labeled offline-only and non-production",
)

REQUIRED_INVALID_CASE_IDS = (
    "external_remapper_only_evidence_promoted_as_official",
    "missing_provenance",
    "missing_fixture_hash",
    "unknown_field_claimed_source_backed",
    "device_write_flag_present",
    "runtime_loaded_config_claim",
    "official_compatibility_claim",
    "universal_compatibility_claim",
    "nunchuk_validation_claim",
    "production_export_claim",
)

REQUIRED_PREVIEW_LABELS = (
    "offline_preview_only",
    "not_production_export",
    "not_device_write",
    "not_webserial",
    "not_runtime_loaded_config",
    "not_official_compatibility_claim",
)

REQUIRED_PREVIEW_BLOCKED_CLAIMS = (
    "production export",
    "device write",
    "WebSerial",
    "runtime-loaded config",
    "firmware flashing automation",
    "official configurator compatibility claim",
    "universal compatibility claim",
    "nunchuk validation claim",
)


class OfficialConfiguratorExportTargetContractError(ValueError):
    """Raised when the target contract drifts from the allowed boundary."""


def fail(message: str) -> None:
    raise OfficialConfiguratorExportTargetContractError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {display(path)}")
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_required(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must contain a JSON object")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths_against_base() -> list[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", f"{BASE_BRANCH}...HEAD"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    ):
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())

    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line:
                paths.add(line[3:].strip())
    return sorted(paths)


def ensure_changed_scope() -> None:
    changed = changed_paths_against_base()
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_CHANGED_PREFIXES)]
    if forbidden:
        fail("firmware/source/build/device paths changed on export-contract branch: " + ", ".join(forbidden))
    out_of_scope = [path for path in changed if not path.startswith(ALLOWED_CHANGED_PREFIXES)]
    if out_of_scope:
        fail("branch contains out-of-scope changed paths: " + ", ".join(out_of_scope))


def require_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    missing = [phrase for phrase in phrases if phrase.lower() not in lowered]
    if missing:
        fail(f"{label} missing required phrase(s): " + ", ".join(missing))


def validate_export_readme() -> None:
    text = read_required(EXPORT_README)
    require_phrases(text, REQUIRED_README_PHRASES, label="docs/export/README.md")


def validate_source_authority_doc() -> None:
    text = read_required(SOURCE_AUTHORITY_DOC)
    require_phrases(text, REQUIRED_SOURCE_AUTHORITY_PHRASES, label="source authority doc")
    for phrase in (
        "Inspected Source And Search Scope",
        "Manifest Status",
        "Exact Fixture Files Identified",
        "Source Classification",
        "Source-Backed Fields And Shapes",
        "Unknowns",
        "What Cannot Be Claimed",
        "Explicit Non-Claims",
    ):
        if f"## {phrase.lower()}" not in text.lower():
            fail(f"source authority doc missing required section: {phrase}")


def actual_official_shape() -> dict[str, Any]:
    manifest = load_json_object(MANIFEST_PATH)
    default = load_json_object(DEFAULT_FIXTURE_PATH)
    back = load_json_object(BACK_AND_FORTH_FIXTURE_PATH)

    expected_manifest_hash = sha256_file(MANIFEST_PATH)
    if manifest.get("fixture_sha256", {}).get(
        "fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json"
    ) != sha256_file(DEFAULT_FIXTURE_PATH):
        fail("manifest default fixture hash must match the committed default fixture")
    if manifest.get("fixture_sha256", {}).get(
        "fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json"
    ) != sha256_file(BACK_AND_FORTH_FIXTURE_PATH):
        fail("manifest back-and-forth fixture hash must match the committed fixture")

    if manifest.get("source_classification") != "primary_official_configurator_corpus":
        fail("official manifest source classification must remain primary_official_configurator_corpus")

    def shape_summary(payload: dict[str, Any]) -> dict[str, Any]:
        game_mode_shapes = [
            {
                "name": mode.get("name"),
                "modeId": mode.get("modeId"),
                "keys": sorted(mode.keys()),
            }
            for mode in payload.get("gameModeConfigs", [])
            if isinstance(mode, dict)
        ]
        return {
            "top_level_keys": list(payload.keys()),
            "counts": {
                "gameModeConfigs": len(payload.get("gameModeConfigs", [])),
                "communicationBackendConfigs": len(payload.get("communicationBackendConfigs", [])),
                "keyboardModes": len(payload.get("keyboardModes", [])),
                "rgbConfigs": len(payload.get("rgbConfigs", [])),
            },
            "game_mode_shapes": game_mode_shapes,
            "communication_backend_key_sets": sorted(
                {
                    tuple(sorted(item.keys()))
                    for item in payload.get("communicationBackendConfigs", [])
                    if isinstance(item, dict)
                }
            ),
            "keyboard_mode_key_sets": sorted(
                {
                    tuple(sorted(item.keys()))
                    for item in payload.get("keyboardModes", [])
                    if isinstance(item, dict)
                }
            ),
            "rgb_config_key_sets": sorted(
                {
                    tuple(sorted(item.keys()))
                    for item in payload.get("rgbConfigs", [])
                    if isinstance(item, dict)
                }
            ),
            "scalar_defaults": {
                "defaultBackendConfig": payload.get("defaultBackendConfig"),
                "defaultUsbBackendConfig": payload.get("defaultUsbBackendConfig"),
                "rgbBrightness": payload.get("rgbBrightness"),
                "defaultDashboardOption": payload.get("defaultDashboardOption"),
            },
        }

    return {
        "manifest_hash": expected_manifest_hash,
        "manifest": manifest,
        "default_shape": shape_summary(default),
        "back_shape": shape_summary(back),
    }


def validate_preview_fixture() -> None:
    preview = load_json_object(PREVIEW_FIXTURE)
    require_phrases(
        json.dumps(preview, ensure_ascii=False, sort_keys=True),
        REQUIRED_PREVIEW_LABELS,
        label="preview fixture",
    )

    if preview.get("schema_name") != "official_configurator_export_candidate_preview":
        fail("preview schema_name must remain official_configurator_export_candidate_preview")
    if preview.get("contract_version") != 1:
        fail("preview contract_version must remain 1")
    if preview.get("status") != "offline_preview_only":
        fail("preview status must remain offline_preview_only")
    if preview.get("source_authority_doc") != "docs/export/official_configurator_export_source_authority.md":
        fail("preview must cite the source-authority doc")

    source_authority = preview.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("preview source_authority must be an object")

    manifest = load_json_object(MANIFEST_PATH)
    if source_authority.get("corpus_id") != manifest.get("corpus_id"):
        fail("preview corpus_id must match the official manifest")
    if source_authority.get("source_classification") != manifest.get("source_classification"):
        fail("preview source_classification must match the official manifest")
    if source_authority.get("manifest_path") != display(MANIFEST_PATH):
        fail("preview manifest_path must match the official manifest path")
    if source_authority.get("manifest_sha256") != sha256_file(MANIFEST_PATH):
        fail("preview manifest_sha256 must match the official manifest hash")

    expected_fixture_paths = [
        display(DEFAULT_FIXTURE_PATH),
        display(BACK_AND_FORTH_FIXTURE_PATH),
    ]
    if source_authority.get("fixture_paths") != expected_fixture_paths:
        fail("preview fixture_paths must match the official corpus")
    expected_fixture_hashes = {
        display(DEFAULT_FIXTURE_PATH): sha256_file(DEFAULT_FIXTURE_PATH),
        display(BACK_AND_FORTH_FIXTURE_PATH): sha256_file(BACK_AND_FORTH_FIXTURE_PATH),
    }
    if source_authority.get("fixture_hashes") != expected_fixture_hashes:
        fail("preview fixture_hashes must match the official corpus")

    observed = preview.get("observed_shape")
    if not isinstance(observed, dict):
        fail("preview observed_shape must be an object")

    actual = actual_official_shape()
    if observed.get("top_level_keys") != actual["default_shape"]["top_level_keys"]:
        fail("preview top_level_keys must match the official corpus")
    if observed.get("counts") != actual["default_shape"]["counts"]:
        fail("preview counts must match the official corpus")
    if observed.get("game_mode_shapes") != actual["default_shape"]["game_mode_shapes"]:
        fail("preview game_mode_shapes must match the official corpus")
    if observed.get("communication_backend_key_sets") != [list(item) for item in actual["default_shape"]["communication_backend_key_sets"]]:
        fail("preview communication_backend_key_sets must match the official corpus")
    if observed.get("keyboard_mode_key_sets") != [list(item) for item in actual["default_shape"]["keyboard_mode_key_sets"]]:
        fail("preview keyboard_mode_key_sets must match the official corpus")
    if observed.get("rgb_config_key_sets") != [list(item) for item in actual["default_shape"]["rgb_config_key_sets"]]:
        fail("preview rgb_config_key_sets must match the official corpus")
    if observed.get("scalar_defaults") != actual["default_shape"]["scalar_defaults"]:
        fail("preview scalar_defaults must match the official corpus")

    required_unknowns = {
        "exact official configurator app version",
        "exact capture timestamp",
        "exact push/download route details",
    }
    unknowns = set(preview.get("unknowns", []))
    if not required_unknowns.issubset(unknowns):
        fail("preview unknowns must preserve the official corpus unknowns")

    blocked = set(preview.get("blocked_claims", []))
    if not {
        "production export",
        "device write",
        "WebSerial",
        "runtime-loaded config",
        "firmware flashing automation",
        "official configurator compatibility claim",
        "universal compatibility claim",
        "nunchuk validation claim",
    }.issubset(blocked):
        fail("preview blocked_claims must preserve the forbidden claim set")

    notes = preview.get("validation_notes")
    if not isinstance(notes, list) or sorted(notes) != sorted(REQUIRED_PREVIEW_LABELS):
        fail("preview validation_notes must preserve the offline-only labels")


def validate_invalid_corpus() -> None:
    if not INVALID_CORPUS.exists():
        return
    corpus = load_json_object(INVALID_CORPUS)
    if corpus.get("schema_name") != "official_configurator_export_target_contract_invalid_corpus":
        fail("invalid corpus schema_name must remain stable")
    if corpus.get("contract_version") != 1:
        fail("invalid corpus contract_version must remain 1")
    if corpus.get("status") != "negative_offline_contract_corpus":
        fail("invalid corpus status must remain negative_offline_contract_corpus")
    if corpus.get("validator_tool") != "tools/check_glyph_official_configurator_export_target_contract.py":
        fail("invalid corpus validator_tool must point to this checker")

    cases = corpus.get("cases")
    if not isinstance(cases, list):
        fail("invalid corpus cases must be a list")

    found = set()
    for case in cases:
        if not isinstance(case, dict):
            fail("invalid corpus case must be an object")
        case_id = case.get("case_id")
        expected_rejection = case.get("expected_rejection")
        if not isinstance(case_id, str) or not case_id:
            fail("invalid corpus case must have a string case_id")
        if not isinstance(expected_rejection, str) or not expected_rejection:
            fail(f"{case_id} must include a string expected_rejection")
        found.add(case_id)

    missing = [case_id for case_id in REQUIRED_INVALID_CASE_IDS if case_id not in found]
    if missing:
        fail("invalid corpus missing required case_id(s): " + ", ".join(missing))

    invalid_claim_markers = {
        "external-remapper evidence promoted as primary official corpus authority",
        "preview omits corpus id, manifest path, or source classification",
        "preview omits a corpus fixture hash",
        "a field not observed in the official corpus is claimed as source-backed",
        "device-write behavior is claimed or enabled",
        "runtime-loaded config is claimed",
        "official configurator compatibility is claimed",
        "universal compatibility is claimed",
        "nunchuk validation is claimed",
        "the preview is treated as production export output",
    }
    actual_markers = {case.get("claim") for case in cases if isinstance(case, dict)}
    if not invalid_claim_markers.issubset(actual_markers):
        fail("invalid corpus claim set drifted from the contract")


def validate_blocker_option() -> None:
    if PREVIEW_FIXTURE.exists():
        return
    if not BLOCKER_DOC.exists():
        fail("missing preview fixture and missing blocker doc")
    text = read_required(BLOCKER_DOC)
    require_phrases(
        text,
        (
            "source authority is insufficient",
            "offline preview fixture was not created",
            "no production export claim",
            "no official configurator compatibility claim",
            "no device write claim",
            "no WebSerial claim",
            "no runtime-loaded config claim",
        ),
        label="blocker doc",
    )


def validate_no_positive_claims() -> None:
    for path in (SOURCE_AUTHORITY_DOC, TARGET_CONTRACT_DOC, EXPORT_README):
        text = read_required(path)
        lowered = normalize(text)
        for marker in (
            "production export output is",
            "official configurator compatibility is claimed",
            "universal compatibility is claimed",
            "device write is implemented",
            "webserial is implemented",
            "runtime-loaded config is implemented",
            "firmware flashing automation is implemented",
            "nunchuk validation is claimed",
        ):
            if marker.lower() in lowered:
                fail(f"{display(path)} contains forbidden positive claim: {marker}")


def main() -> int:
    print("glyph_official_configurator_export_target_contract")
    try:
        validate_export_readme()
        validate_source_authority_doc()
        if PREVIEW_FIXTURE.exists():
            validate_preview_fixture()
        else:
            validate_blocker_option()
        validate_invalid_corpus()
        validate_no_positive_claims()
        ensure_changed_scope()
    except (OSError, ValueError, OfficialConfiguratorExportTargetContractError) as exc:
        print("status=FAIL")
        print("offline_contract_only=true")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("offline_contract_only=true")
    print("official_configurator_compatibility_claim=false")
    print("production_export_claim=false")
    print("device_write_claim=false")
    print("webserial_claim=false")
    print("runtime_loaded_config_claim=false")
    print("firmware_flashing_claim=false")
    print("nunchuk_validation_claim=false")
    print(f"source_authority={display(SOURCE_AUTHORITY_DOC)}")
    print(f"target_contract={display(TARGET_CONTRACT_DOC)}")
    print(f"preview_fixture={display(PREVIEW_FIXTURE)}")
    print(f"invalid_corpus={display(INVALID_CORPUS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
