#!/usr/bin/env python3
"""Validate the inert, observed-only artifact provenance contract."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
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


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def fail(message: str) -> None:
    raise ProvenanceError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True,
        text=True, check=False,
    )
    if completed.returncode or not re.fullmatch(r"[0-9a-f]{40}", completed.stdout.strip()):
        fail("could not resolve a full lowercase checked-out Git SHA")
    return completed.stdout.strip()


def require_full_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        fail(f"{label} must be a full lowercase Git SHA")
    return value


def verify_checkout(candidate_sha: str | None = None) -> str:
    observed = require_full_sha(candidate_sha or os.environ.get("GITHUB_SHA"), "GITHUB_SHA")
    if observed != git_head():
        fail("GITHUB_SHA does not equal checked-out HEAD")
    if not TRACKED_NUKER.is_file() or sha256_file(TRACKED_NUKER) != EXPECTED_NUKER_SHA256:
        fail("tracked glyph_nuker identity changed")
    return observed


def build_sidecar(candidate_sha: str, artifact_path: Path) -> dict[str, Any]:
    candidate_sha = require_full_sha(candidate_sha, "candidate_git_sha")
    if not artifact_path.is_file() or artifact_path.is_symlink():
        fail("final artifact must be a regular file")
    return {
        "schema_name": "glyph_artifact_postprocessor_provenance",
        "schema_version": 1,
        "status": "observed_only_no_artifact_acceptance",
        "candidate_git_sha": candidate_sha,
        "final_artifact": {
            "filename": artifact_path.name,
            "size_bytes": artifact_path.stat().st_size,
            "sha256": sha256_file(artifact_path),
        },
        "postprocessor": {
            "path": "glyph_nuker",
            "sha256": EXPECTED_NUKER_SHA256,
            "purpose": "UNKNOWN",
            "byte_transformation": "UNKNOWN",
        },
        "immutable_locator": None,
        "source_authority": {
            "classification": "observed_only",
            "workflow_source": ".github/workflows/build.yml",
            "artifact_store_established": False,
        },
    }


def write_sidecar(candidate_sha: str, artifact_path: Path, sidecar_path: Path) -> None:
    sidecar = build_sidecar(candidate_sha, artifact_path)
    sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")


def verify_real_sidecar(sidecar_path: Path, artifact_path: Path, candidate_sha: str) -> None:
    sidecar = load_object(sidecar_path)
    candidate_sha = require_full_sha(candidate_sha, "candidate_git_sha")
    if sidecar.get("candidate_git_sha") != candidate_sha:
        fail("sidecar candidate Git SHA does not match workflow SHA")
    expected = build_sidecar(candidate_sha, artifact_path)
    if sidecar != expected:
        fail("sidecar does not exactly match final artifact and observed-only contract")


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def validate_sidecar(sidecar: dict[str, Any], artifact: bytes) -> None:
    if set(sidecar) != {
        "schema_name", "schema_version", "status", "candidate_git_sha",
        "final_artifact", "postprocessor", "immutable_locator", "source_authority",
    }:
        fail("sidecar has missing or unexpected top-level fields")
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
    if set(artifact_meta) != {"filename", "size_bytes", "sha256"}:
        fail("final_artifact has missing or unexpected fields")
    if artifact_meta.get("filename") != "Glyph-synthetic.uf2":
        fail("final artifact filename drifted")
    if artifact_meta.get("size_bytes") != len(artifact):
        fail("final artifact size does not match synthetic bytes")
    if artifact_meta.get("sha256") != sha256_bytes(artifact):
        fail("final artifact SHA-256 does not match synthetic bytes")

    postprocessor = sidecar.get("postprocessor")
    if not isinstance(postprocessor, dict):
        fail("postprocessor must be an object")
    if set(postprocessor) != {"path", "sha256", "purpose", "byte_transformation"}:
        fail("postprocessor has missing or unexpected fields")
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
    global EXPECTED_NUKER_SHA256
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

        missing_locator = json.loads(json.dumps(sidecar))
        missing_locator.pop("immutable_locator")
        try:
            validate_sidecar(missing_locator, artifact)
        except ProvenanceError:
            pass
        else:
            fail("missing immutable locator was accepted")

        extra_field = json.loads(json.dumps(sidecar))
        extra_field["unexpected"] = True
        try:
            validate_sidecar(extra_field, artifact)
        except ProvenanceError:
            pass
        else:
            fail("unexpected sidecar field was accepted")

        tampered_postprocessor = json.loads(json.dumps(sidecar))
        tampered_postprocessor["postprocessor"]["sha256"] = "0" * 64
        try:
            validate_sidecar(tampered_postprocessor, artifact)
        except ProvenanceError:
            pass
        else:
            fail("tampered postprocessor identity was accepted")

        for malformed_sha in ("short", "A" * 40):
            try:
                verify_checkout(malformed_sha)
            except ProvenanceError:
                pass
            else:
                fail("malformed or uppercase checkout SHA was accepted")

        try:
            verify_checkout("0" * 40)
        except ProvenanceError:
            pass
        else:
            fail("HEAD-mismatched checkout SHA was accepted")

        original_nuker_sha = EXPECTED_NUKER_SHA256
        EXPECTED_NUKER_SHA256 = "0" * 64
        try:
            try:
                verify_checkout(git_head())
            except ProvenanceError:
                pass
            else:
                fail("changed postprocessor identity was accepted")
        finally:
            EXPECTED_NUKER_SHA256 = original_nuker_sha

        real_sidecar = Path(directory) / "real.provenance.json"
        candidate_sha = EXPECTED_CANDIDATE_GIT_SHA
        write_sidecar(candidate_sha, artifact_path, real_sidecar)
        verify_real_sidecar(real_sidecar, artifact_path, candidate_sha)
        real_sidecar_payload = load_object(real_sidecar)
        real_sidecar_payload["candidate_git_sha"] = "f" * 40
        real_sidecar.write_text(json.dumps(real_sidecar_payload), encoding="utf-8")
        try:
            verify_real_sidecar(real_sidecar, artifact_path, candidate_sha)
        except ProvenanceError:
            pass
        else:
            fail("tampered written sidecar was accepted")

        duplicate_top_level = (
            '{"candidate_git_sha":"' + "0" * 40 + '",'
            '"candidate_git_sha":"' + candidate_sha + '"}'
        )
        duplicate_nested = (
            '{"final_artifact":{"sha256":"' + "0" * 64 + '",'
            '"sha256":"' + sidecar["final_artifact"]["sha256"] + '"}}'
        )
        for duplicate_payload in (duplicate_top_level, duplicate_nested):
            duplicate_path = Path(directory) / "duplicate.json"
            duplicate_path.write_text(duplicate_payload, encoding="utf-8")
            try:
                load_object(duplicate_path)
            except ProvenanceError:
                pass
            else:
                fail("duplicate JSON key was accepted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the committed fixture")
    parser.add_argument("--verify-checkout", action="store_true")
    parser.add_argument("--write-sidecar", action="store_true")
    parser.add_argument("--verify-sidecar", action="store_true")
    parser.add_argument("--candidate-sha")
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--sidecar", type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            check_fixture()
            print("artifact_postprocessor_provenance=PASS")
            print("tracked_postprocessor_execution=NOT_PERFORMED")
            print("artifact_transformation=UNKNOWN")
            print("immutable_locator=UNRESOLVED")
        elif args.verify_checkout:
            print(f"checked_out_git_sha={verify_checkout(args.candidate_sha)}")
            print("tracked_postprocessor=PASS")
        elif args.write_sidecar:
            if not args.artifact or not args.sidecar or not args.candidate_sha:
                parser.error("--write-sidecar requires --candidate-sha, --artifact, and --sidecar")
            write_sidecar(args.candidate_sha, args.artifact, args.sidecar)
            print(f"sidecar_written={args.sidecar}")
        elif args.verify_sidecar:
            if not args.artifact or not args.sidecar or not args.candidate_sha:
                parser.error("--verify-sidecar requires --candidate-sha, --artifact, and --sidecar")
            verify_real_sidecar(args.sidecar, args.artifact, args.candidate_sha)
            print("sidecar_verification=PASS")
        else:
            parser.error("one of --check, --verify-checkout, --write-sidecar, or --verify-sidecar is required")
    except (OSError, ProvenanceError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
