#!/usr/bin/env python3
"""Validate the offline remapper experiment input manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/calibration/glyph_offline_remapper_experiment_input_manifest_2026-06-03.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs/calibration/fixtures/glyph_offline_remapper_experiment_input_manifest_2026-06-03.json"
)

SCHEMA_NAME = "glyph_offline_remapper_experiment_input_manifest"
MANIFEST_VERSION = 1
STATUS = "input_manifest_only_experiment_not_executed"
HARDWARE_STATUS = "not_new_hardware_result"

REQUIRED_INPUTS = (
    {
        "label": "active_profile_artifact",
        "path": "docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json",
        "sha256": "0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707",
        "expected_import_role": "import_candidate",
        "use_in_experiment": "primary import candidate for external remapper no-device import test",
        "authority_class": "repo_fixture_evidence",
        "caveats": "Current committed active profile artifact only; no device write, no WebSerial write, not hardware validation, and not official compatibility.",
    },
    {
        "label": "tilt_button_probe_fixture",
        "path": "docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json",
        "sha256": "0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707",
        "expected_import_role": "possible_import_candidate_if_compatible",
        "use_in_experiment": "secondary repo fixture reference",
        "authority_class": "repo_fixture_evidence",
        "caveats": "Secondary reference only; same current hash as the active profile artifact in this repo snapshot does not imply separate authority or proven compatibility.",
    },
    {
        "label": "senscope_export_package_sample",
        "path": "docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json",
        "sha256": "3497ce3150620a60838c50f58438250f472c121b3ce9623d3223ea5f780717a1",
        "expected_import_role": "reference_only",
        "use_in_experiment": "reference-only package, not expected external remapper import unless future adapter exists",
        "authority_class": "repo_fixture_evidence",
        "caveats": "Reference-only package; do not treat as direct import candidate, runtime-loaded config, device write payload, or official compatibility evidence.",
    },
    {
        "label": "runtime_config_candidate_sample",
        "path": "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json",
        "sha256": "e4e9b0e47b36f9f8585b37ac0e9f3cba2b6ae2833d79121e99af602c9d48543f",
        "expected_import_role": "reference_only",
        "use_in_experiment": "reference-only runtime candidate, not expected external remapper import unless future adapter exists",
        "authority_class": "repo_fixture_evidence",
        "caveats": "Reference-only runtime candidate; not firmware input, not runtime-loaded config implementation, no device write, and not hardware validation.",
    },
    {
        "label": "generated_config_prototype",
        "path": "docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json",
        "sha256": "d66efa458cc28921d3a1ccb0682e8486d880c3d3fe77260a19cc3e0afa63006f",
        "expected_import_role": "reference_only",
        "use_in_experiment": "reference-only generated config source",
        "authority_class": "repo_fixture_evidence",
        "caveats": "Reference-only generated config source; docs/tools-only artifact, not external remapper import candidate, not runtime-loaded config, and not hardware validation.",
    },
)
REQUIRED_DOC_PHRASES = (
    "input manifest only",
    "experiment not executed",
    "adapter not implemented",
    "no device write",
    "no webserial write",
    "not hardware validation",
)


class OfflineRemapperExperimentInputManifestError(ValueError):
    """Raised when the manifest drifts from required bounds."""


def fail(message: str) -> None:
    raise OfflineRemapperExperimentInputManifestError(message)


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


def sha256_for(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_top_level(fixture: dict[str, Any]) -> None:
    expected = {
        "schema_name": SCHEMA_NAME,
        "manifest_version": MANIFEST_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "experiment_executed": False,
        "adapter_implemented": False,
        "external_source_promoted_to_authority": False,
        "device_write_allowed": False,
        "webserial_write_allowed": False,
    }
    for key, value in expected.items():
        if fixture.get(key) != value:
            fail(f"{key} must be {value!r}")


def validate_inputs(fixture: dict[str, Any]) -> None:
    entries = fixture.get("inputs")
    if not isinstance(entries, list) or not entries:
        fail("inputs must be a non-empty list")
    if len(entries) != len(REQUIRED_INPUTS):
        fail("inputs drifted from required count")

    for index, expected in enumerate(REQUIRED_INPUTS):
        entry = entries[index]
        if not isinstance(entry, dict):
            fail(f"inputs[{index}] must be an object")

        for key, value in expected.items():
            if entry.get(key) != value:
                fail(f"inputs[{index}].{key} must be {value!r}")

        relpath = expected["path"]
        input_path = REPO_ROOT / relpath
        if not input_path.exists():
            fail(f"inputs[{index}] references missing path: {relpath}")
        actual_sha = sha256_for(input_path)
        if actual_sha != expected["sha256"]:
            fail(
                f"inputs[{index}] sha256 mismatch for {relpath}: "
                f"expected {expected['sha256']}, got {actual_sha}"
            )

        role = entry["expected_import_role"]
        if role == "reference_only" and "import candidate" in entry["use_in_experiment"]:
            fail(f"inputs[{index}] reference_only entry must not be marked import candidate")
        if role != "reference_only" and role not in (
            "import_candidate",
            "possible_import_candidate_if_compatible",
        ):
            fail(f"inputs[{index}] has unexpected import-role classification: {role}")
        if role == "import_candidate" and not entry["use_in_experiment"].startswith(
            "primary import candidate"
        ):
            fail(f"inputs[{index}] import_candidate use text drifted")
        if role == "possible_import_candidate_if_compatible" and entry[
            "use_in_experiment"
        ] != "secondary repo fixture reference":
            fail(f"inputs[{index}] possible import candidate use text drifted")


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_offline_remapper_experiment_input_manifest")
    try:
        fixture = load_json_object(FIXTURE_PATH)
        validate_top_level(fixture)
        validate_inputs(fixture)
        validate_doc()
    except (
        OSError,
        OfflineRemapperExperimentInputManifestError,
        ValueError,
    ) as exc:
        print("status=FAIL")
        print(f"inputs={len(REQUIRED_INPUTS)}")
        print("experiment_executed=false")
        print("adapter_implemented=false")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"inputs={len(REQUIRED_INPUTS)}")
    print("experiment_executed=false")
    print("adapter_implemented=false")
    print(f"hardware_status={HARDWARE_STATUS}")
    print("device_write_allowed=false")
    print("webserial_write_allowed=false")
    print("external_source_promoted_to_authority=false")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
