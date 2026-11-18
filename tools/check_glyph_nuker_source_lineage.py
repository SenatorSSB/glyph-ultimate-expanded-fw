#!/usr/bin/env python3
"""Validate the bounded, offline glyph_nuker lineage evidence packet."""
from __future__ import annotations
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/runtime_config/glyph_nuker_source_lineage.md"
FIXTURE = ROOT / "docs/runtime_config/fixtures/glyph_nuker_source_lineage.json"
NUKER = ROOT / "glyph_nuker"
EXPECTED_SHA256 = "8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae"
EXPECTED_BLOB = "d0524944a90503a8881281b6673b1f46e36f9383"
EXPECTED_BASE = "a747dd54b02b207483142331d8b5be1113fc951e"
EXPECTED_HEAD = "d5050847d3f850951b3f47865dc8a91aedea0834"
EXPECTED_INTRO = "cc57c4fcbcf25c5e33fab21fd5b8312e0543c8dd"
EXPECTED_SEARCH_IDS = {"senatorssb_history", "senatorssb_releases", "gregturbo_repository", "gregturbo_releases"}

class LineageError(ValueError):
    pass

def fail(message: str) -> None:
    raise LineageError(message)

def load() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail("fixture must be an object")
    return value

def require_sha(value: object, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        fail(f"{label} must be a full lowercase SHA")

def validate(value: dict) -> None:
    required = {"schema_name", "schema_version", "status", "observed_at", "canonical_base", "tracked_binary", "workflow_invocation", "local_history", "searches", "claims"}
    if set(value) != required:
        fail("fixture top-level fields drifted")
    if value["schema_name"] != "glyph_nuker_source_lineage_fixture" or value["schema_version"] != 1:
        fail("schema identity drifted")
    if value["status"] != "BOUNDED_SOURCE_LINEAGE_NOT_FOUND":
        fail("status must remain bounded not-found")
    if value["canonical_base"] != {"repository": "https://github.com/SenatorSSB/glyph-ultimate-expanded-fw.git", "commit": EXPECTED_BASE, "identity_kind": "immutable_commit"}:
        fail("canonical base drifted")
    if value["tracked_binary"] != {"path": "glyph_nuker", "git_mode": "100755", "git_blob": EXPECTED_BLOB, "sha256": EXPECTED_SHA256}:
        fail("tracked binary identity drifted")
    if value["workflow_invocation"] != {"path": ".github/workflows/build.yml", "source_commit": EXPECTED_BASE, "locator": f"git-json:{EXPECTED_BASE}:.github/workflows/build.yml", "observed_command": "ls *.uf2 | xargs ./glyph_nuker", "placement_command": "mv glyph_nuker $PIO_ENV/glyph_nuker"}:
        fail("workflow invocation drifted")
    history = value["local_history"]
    if history["introduction_commit"] != EXPECTED_INTRO or history["introduction_tag"] != "1.0.6" or history["source_paths_found"] or history["build_recipe_paths_found"] or history["outcome"] != value["status"] or history["immutable_evidence_identity"] != EXPECTED_BASE:
        fail("local history evidence drifted")
    require_sha(history["introduction_commit"], "introduction_commit")
    searches = value["searches"]
    if not isinstance(searches, list) or {item.get("id") for item in searches} != EXPECTED_SEARCH_IDS:
        fail("search surfaces are incomplete or duplicated")
    for item in searches:
        if set(item) != {"id", "surface", "method", "query", "locator", "outcome", "immutable_evidence_identity", "limitations"}:
            fail(f"search fields drifted: {item.get('id')}")
        if item["outcome"] != value["status"] or not item["limitations"]:
            fail(f"search outcome/limitation drifted: {item['id']}")
        if item["immutable_evidence_identity"] is not None:
            require_sha(item["immutable_evidence_identity"], f"{item['id']} evidence identity")
    claims = value["claims"]
    if set(claims) != {"source_lineage", "purpose", "byte_transformation", "build_recipe", "reproducible_build", "artifact_acceptance", "safety", "hardware"} or any(item != "UNKNOWN" for item in claims.values()):
        fail("unknown claims were promoted")

def validate_historical_repository_facts() -> None:
    if not NUKER.is_file() or NUKER.is_symlink() or hashlib.sha256(NUKER.read_bytes()).hexdigest() != EXPECTED_SHA256:
        fail("tracked glyph_nuker SHA-256 drifted")
    mode = subprocess.check_output(["git", "ls-files", "-s", "--", "glyph_nuker"], cwd=ROOT, text=True).strip()
    if not mode.startswith(f"100755 {EXPECTED_BLOB} "):
        fail("tracked glyph_nuker Git mode/blob drifted")
    blob = subprocess.check_output(["git", "rev-parse", f"{EXPECTED_BASE}:glyph_nuker"], cwd=ROOT, text=True).strip()
    if blob != EXPECTED_BLOB:
        fail("canonical base glyph_nuker blob drifted")
    workflow = subprocess.check_output(["git", "show", f"{EXPECTED_BASE}:.github/workflows/build.yml"], cwd=ROOT, text=True)
    if "mv glyph_nuker $PIO_ENV/glyph_nuker" not in workflow or "ls *.uf2 | xargs ./glyph_nuker" not in workflow:
        fail("canonical workflow invocation drifted")
    if EXPECTED_HEAD not in subprocess.check_output(["git", "rev-list", "--all"], cwd=ROOT, text=True):
        fail("live configurator evidence identity is unavailable locally")

def validate_current_receipt() -> None:
    # The packet seals a bounded historical search, never positive lineage.
    if hashlib.sha256(FIXTURE.read_bytes()).hexdigest() != "292728ec8d9f78d2bb1a3dd5dc9cf52dc07a273af57a9e3561a2b8e4b44c4fe1":
        fail("sealed source-search receipt drifted")
    workflow = (ROOT / ".github/workflows/build.yml").read_text()
    for command in ("mv glyph_nuker $PIO_ENV/glyph_nuker", "ls *.uf2 | xargs ./glyph_nuker"):
        if command not in workflow:
            fail("current artifact-processing command changed")
    if NUKER.exists() or NUKER.is_symlink():
        if not NUKER.is_file() or NUKER.is_symlink() or hashlib.sha256(NUKER.read_bytes()).hexdigest() != EXPECTED_SHA256:
            fail("tracked glyph_nuker SHA-256 drifted")
        mode = subprocess.check_output(["git", "ls-files", "-s", "--", "glyph_nuker"], cwd=ROOT, text=True).strip()
        if not mode.startswith(f"100755 {EXPECTED_BLOB} "):
            fail("tracked glyph_nuker Git mode/blob drifted")
    else:
        from glyph_ci_package_scope import public_contract
        contract = public_contract(ROOT)
        if contract["opaque_postprocessor"] != {
                "path": "glyph_nuker", "sha256": EXPECTED_SHA256,
                "status": "GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED",
                "public_action": "OMIT_AND_BLOCK_PUBLICATION"}:
            fail("omitted postprocessor lacks explicit public blocking contract")

def main() -> int:
    try:
        validate(load())
        if sys.argv[1:] == ["--historical"]:
            validate_historical_repository_facts()
        elif sys.argv[1:]:
            fail("expected no arguments or --historical")
        validate_current_receipt()
        if not DOC.is_file() or "BOUNDED_SOURCE_LINEAGE_NOT_FOUND" not in DOC.read_text(encoding="utf-8"):
            fail("lineage document missing bounded status")
        tampered = copy.deepcopy(load())
        tampered["claims"]["purpose"] = "UF2 postprocessor"
        try:
            validate(tampered)
        except LineageError:
            pass
        else:
            fail("unsupported purpose claim accepted")
        print("glyph_nuker_source_lineage: PASS; sealed bounded search receipt only; source/license UNKNOWN; GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED")
        return 0
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, LineageError) as exc:
        print(f"glyph_nuker_source_lineage: FAIL: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
