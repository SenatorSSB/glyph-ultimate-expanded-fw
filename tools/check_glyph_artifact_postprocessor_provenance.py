#!/usr/bin/env python3
"""Validate the inert, observed-only artifact provenance contract."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/runtime_config/artifact_postprocessor_provenance.md"
FIXTURE_PATH = (
    REPO_ROOT / "docs/runtime_config/fixtures/artifact_postprocessor_provenance.json"
)
TRACKED_NUKER = REPO_ROOT / "glyph_nuker"
EXPECTED_NUKER_SHA256 = "8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae"
EXPECTED_CANDIDATE_GIT_SHA = "7688ee287491ff05898038045f5c1918be09f675"


class ProvenanceError(ValueError):
    """Raised when the static provenance contract is not fail-closed."""


def fail(message: str) -> None:
    raise ProvenanceError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def validate_sidecar(sidecar: dict[str, Any], artifact: bytes) -> None:
    if sidecar.get("schema_name") != "glyph_artifact_postprocessor_provenance":
        fail("schema_name drifted")
    if sidecar.get("schema_version") != 1:
        fail("schema_version must be 1")
    if sidecar.get("status") != "observed_only_no_artifact_acceptance":
        fail("status must preserve observed-only classification")
    candidate_sha = sidecar.get("candidate_git_sha")
    if not isinstance(candidate_sha, str) or len(candidate_sha) != 40:
        fail("candidate_git_sha must be a full 40-character Git SHA")
    if any(character not in "0123456789abcdef" for character in candidate_sha):
        fail("candidate_git_sha must be lowercase hexadecimal")
    if candidate_sha != EXPECTED_CANDIDATE_GIT_SHA:
        fail("candidate_git_sha does not match the observed live configurator snapshot")

    artifact_meta = sidecar.get("final_artifact")
    if not isinstance(artifact_meta, dict):
        fail("final_artifact must be an object")
    if artifact_meta.get("filename") != "Glyph-synthetic.uf2":
        fail("final artifact filename drifted")
    if artifact_meta.get("size_bytes") != len(artifact):
        fail("final artifact size does not match synthetic bytes")
    if artifact_meta.get("sha256") != sha256_bytes(artifact):
        fail("final artifact SHA-256 does not match synthetic bytes")

    postprocessor = sidecar.get("postprocessor")
    if not isinstance(postprocessor, dict):
        fail("postprocessor must be an object")
    if postprocessor.get("path") != "glyph_nuker":
        fail("postprocessor path drifted")
    if postprocessor.get("sha256") != EXPECTED_NUKER_SHA256:
        fail("postprocessor SHA-256 does not match the tracked file identity")
    if postprocessor.get("purpose") != "UNKNOWN":
        fail("postprocessor purpose must remain UNKNOWN")
    if postprocessor.get("byte_transformation") != "UNKNOWN":
        fail("postprocessor byte transformation must remain UNKNOWN")

    if sidecar.get("immutable_locator") is not None:
        fail("immutable_locator must be null because no durable store is established")
    if sidecar.get("source_authority") != {
        "classification": "observed_only",
        "workflow_source": ".github/workflows/build.yml",
        "artifact_store_established": False,
    }:
        fail("source_authority classification drifted")


def check_fixture() -> None:
    fixture = load_object(FIXTURE_PATH)
    encoded = fixture.get("synthetic_artifact_bytes_base64")
    if not isinstance(encoded, str):
        fail("fixture synthetic bytes are missing")
    try:
        artifact = base64.b64decode(encoded, validate=True)
    except ValueError as exc:
        fail(f"invalid synthetic artifact bytes: {exc}")
    sidecar = fixture.get("sidecar")
    if not isinstance(sidecar, dict):
        fail("fixture sidecar is missing")
    validate_sidecar(sidecar, artifact)

    if not TRACKED_NUKER.is_file() or sha256_file(TRACKED_NUKER) != EXPECTED_NUKER_SHA256:
        fail("tracked glyph_nuker identity changed")

    with tempfile.TemporaryDirectory(prefix="glyph-provenance-") as directory:
        artifact_path = Path(directory) / sidecar["final_artifact"]["filename"]
        artifact_path.write_bytes(artifact)
        if artifact_path.stat().st_size != sidecar["final_artifact"]["size_bytes"]:
            fail("synthetic artifact size verification failed")
        if sha256_file(artifact_path) != sidecar["final_artifact"]["sha256"]:
            fail("synthetic artifact hash verification failed")

        tampered = json.loads(json.dumps(sidecar))
        tampered["candidate_git_sha"] = "f" * 40
        try:
            validate_sidecar(tampered, artifact)
        except ProvenanceError:
            pass
        else:
            fail("tampered candidate Git SHA was accepted")

        tampered_artifact = json.loads(json.dumps(sidecar))
        tampered_artifact["final_artifact"]["sha256"] = "0" * 64
        try:
            validate_sidecar(tampered_artifact, artifact)
        except ProvenanceError:
            pass
        else:
            fail("tampered artifact SHA-256 was accepted")

        locator_claim = json.loads(json.dumps(sidecar))
        locator_claim["immutable_locator"] = "https://example.invalid/not-a-store"
        try:
            validate_sidecar(locator_claim, artifact)
        except ProvenanceError:
            pass
        else:
            fail("false immutable locator claim was accepted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the committed fixture")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")
    check_fixture()
    print("artifact_postprocessor_provenance=PASS")
    print("tracked_postprocessor_execution=NOT_PERFORMED")
    print("artifact_transformation=UNKNOWN")
    print("immutable_locator=UNRESOLVED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
