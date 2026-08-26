#!/usr/bin/env python3
"""Validate timestamped build-input observations without resolving build inputs."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/runtime_config/fixtures/build_input_provenance_inventory.json"
PATH = ROOT / "docs/runtime_config/fixtures/build_input_resolution_observations.json"
EXPECTED_SHA = "d783688fdc140ad2a5706b168f24f76093d0a388431ca4b33253257c52dfc455"
EXPECTED_BLOB = "5e6d2f128cc6baccd98c39369fbd6bc5acc43851"
DIRECT_CATEGORIES = {"toolchain", "dependency", "workflow_action", "workflow_runner", "reusable_workflow"}
DERIVED = {"workflow.device.external_repo": "${{ inputs.repo }}", "workflow.device.external_revision": "${{ inputs.revision }}"}
FIELDS = {"selector_id","raw_selector","source_inventory_sha256","source_inventory_blob","observed_at","lookup_method","authoritative_upstream_locator","observed_identity","mutability","result","evidence_locator","unresolved_reason"}
RESULTS = {"OBSERVED_FULL_IDENTITY","BOUNDED_UNRESOLVED","VISIBLE_SOURCE_WITHOUT_INVOCATION","RUNTIME_DERIVED"}
MUTABILITY = {"IMMUTABLE_COMMIT","DECLARED_SELECTOR_ONLY","MOVING_REF","RUNTIME_DERIVED"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
URL = re.compile(r"^https?://[^\s]+$")

def fail(message: str) -> None: raise ValueError(message)
def tracked_blob(path: str) -> str:
    return subprocess.run(["git","rev-parse",f"HEAD:{path}"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
def expected_ids(inv: dict) -> dict[str, dict]:
    result = {i["id"]: i for i in inv["selectors"] if i["category"] in DIRECT_CATEGORIES or i["id"] in {"meta.external_repo","meta.external_revision"}}
    result.update({k: {"id": k, "raw_selector": v, "category": "derived"} for k,v in DERIVED.items()})
    return result
def check() -> None:
    inv=json.loads(INVENTORY.read_text(encoding="utf-8")); data=json.loads(PATH.read_text(encoding="utf-8"))
    if set(data) != {"schema_name","schema_version","status","source_inventory","records"}: fail("top-level schema mismatch")
    if data["schema_name"]!="glyph_build_input_resolution_observations" or data["schema_version"]!=1: fail("schema identity mismatch")
    if data["status"]!="timestamped_observations_without_selector_mutation_or_reproducibility": fail("status mismatch")
    source=data["source_inventory"]
    if set(source)!={"path","sha256","blob","base_configurator_sha"} or source["path"]!=str(INVENTORY.relative_to(ROOT)) or source["sha256"]!=EXPECTED_SHA or source["blob"]!=EXPECTED_BLOB: fail("stale source inventory identity")
    if hashlib.sha256(INVENTORY.read_bytes()).hexdigest()!=EXPECTED_SHA or tracked_blob(source["path"])!=EXPECTED_BLOB: fail("source inventory identity drift")
    if not SHA40.fullmatch(source["base_configurator_sha"]): fail("base SHA must be full lowercase Git identity")
    expected=expected_ids(inv); records=data["records"]
    if len(records)!=len(expected) or {r.get("selector_id") for r in records}!=set(expected): fail("selector omissions, duplicates, or extras")
    for r in records:
        if set(r)!=FIELDS: fail(f"record fields mismatch: {r.get('selector_id')}")
        item=expected[r["selector_id"]]
        if r["raw_selector"]!=item["raw_selector"] or r["source_inventory_sha256"]!=EXPECTED_SHA or r["source_inventory_blob"]!=EXPECTED_BLOB: fail(f"selector/source binding mismatch: {r['selector_id']}")
        try: datetime.strptime(r["observed_at"],"%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e: fail(f"invalid timestamp: {r['selector_id']}: {e}")
        if not isinstance(r["lookup_method"],str) or not r["lookup_method"]: fail("missing lookup method")
        if not URL.fullmatch(r["authoritative_upstream_locator"]) or not URL.fullmatch(r["evidence_locator"]): fail(f"invalid URL: {r['selector_id']}")
        if r["result"] not in RESULTS or r["mutability"] not in MUTABILITY: fail(f"unknown result/mutability: {r['selector_id']}")
        if r["result"]=="OBSERVED_FULL_IDENTITY":
            if r["mutability"]!="IMMUTABLE_COMMIT" or not SHA40.fullmatch(r["observed_identity"] or "") or r["unresolved_reason"] is not None: fail("invalid resolved identity")
        elif r["result"]=="RUNTIME_DERIVED":
            if r["selector_id"] not in DERIVED or r["mutability"]!="RUNTIME_DERIVED" or r["observed_identity"] is not None or not r["unresolved_reason"]: fail("invalid runtime-derived record")
        else:
            if r["observed_identity"] is not None or not r["unresolved_reason"]: fail("unresolved record must retain exact reason")
        if r["selector_id"]=="workflow.nested.reusable_caller" and r["result"]!="VISIBLE_SOURCE_WITHOUT_INVOCATION": fail("reusable-workflow distinction lost")
    if not any(r["result"]=="OBSERVED_FULL_IDENTITY" for r in records): fail("all external observations unresolved")
    print(f"glyph_build_input_resolution_observations: PASS; records={len(records)}; direct={len(expected)-len(DERIVED)}; derived={len(DERIVED)}")
if __name__=="__main__":
    try: check()
    except (OSError,ValueError,json.JSONDecodeError,subprocess.CalledProcessError) as e:
        print(f"glyph_build_input_resolution_observations: FAIL: {e}"); sys.exit(1)
