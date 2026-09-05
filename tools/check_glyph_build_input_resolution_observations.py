#!/usr/bin/env python3
"""Validate source-bound, timestamped build-input observations offline."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/runtime_config/fixtures/build_input_provenance_inventory.json"
PATH = ROOT / "docs/runtime_config/fixtures/build_input_resolution_observations.json"
MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
BASE = "8c04262c66613d46b933b1b739c01c575cb0c580"
OBSERVATION_BASE = "ffc007552abc848051841362b0b0ac4c1a7d087b"
INVENTORY_SHA = "d783688fdc140ad2a5706b168f24f76093d0a388431ca4b33253257c52dfc455"
INVENTORY_BLOB = "5e6d2f128cc6baccd98c39369fbd6bc5acc43851"
WORKFLOW_BLOB = "40f8ca91fefc64674c08c03183595983c5054d1f"
META_BLOB = "b875b765da097f247823d9550b9d417b0f657656"
WORKFLOW = ".github/workflows/build-device-config.yml"
META = "config/glyph/meta.yaml"
DIRECT_CATEGORIES = {"toolchain", "dependency", "workflow_action", "workflow_runner", "reusable_workflow"}
FIELDS = {"selector_id","raw_selector","source_class","source_inventory_sha256","source_inventory_blob","observed_at","lookup_method","authoritative_upstream_locator","observed_identity","mutability","result","evidence_locator","unresolved_reason"}
RESULTS = {"OBSERVED_FULL_IDENTITY","BOUNDED_UNRESOLVED","VISIBLE_SOURCE_WITHOUT_INVOCATION","RUNTIME_DERIVED"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
URL = re.compile(r"^https?://[^\s]+$")

def fail(message: str) -> None:
    raise ValueError(message)

def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True).stdout

def base_blob(path: str) -> str:
    return git("rev-parse", f"{BASE}:{path}").strip()

def base_text(path: str) -> str:
    return git("show", f"{BASE}:{path}")

def historical_inventory() -> dict:
    return json.loads(base_text(str(INVENTORY.relative_to(ROOT))))

def historical_observations() -> dict:
    return json.loads(git("show", f"{OBSERVATION_BASE}:{PATH.relative_to(ROOT)}"))

def historical_observations_bytes() -> bytes:
    return subprocess.run(
        ["git", "show", f"{OBSERVATION_BASE}:{PATH.relative_to(ROOT)}"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout

def blob_locator(commit: str, path: str) -> str:
    return f"https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/blob/{commit}/{path}"

def expected_records(inv: dict, workflow_text: str) -> list[dict]:
    direct = [item for item in inv["selectors"] if item["category"] in DIRECT_CATEGORIES or item["id"] in {"meta.external_repo", "meta.external_revision"}]
    derived = [
        ("workflow.device.external_repo", re.search(r"HAYBOX_REPO:\s*\${{\s*(.*?)\s*\}}", workflow_text)),
        ("workflow.device.external_revision", re.search(r"HAYBOX_REVISION:\s*\${{\s*(.*?)\s*\}}", workflow_text)),
    ]
    if any(match is None for _, match in derived):
        fail("required workflow-derived expressions are missing")
    records = []
    for item in direct:
        path = item["declaring_path"]
        if item["id"] == "pio.arduino_pico.platform":
            locator = "https://github.com/maxgerhardt/platform-raspberrypi/commit/5e87ae34ca025274df25b3303e9e9cb6c120123c"
            records.append({"selector_id": item["id"], "raw_selector": item["raw_selector"], "source_class": item["category"], "lookup_method": "git_ls_remote_commit", "authoritative_upstream_locator": locator, "observed_identity": "5e87ae34ca025274df25b3303e9e9cb6c120123c", "mutability": "IMMUTABLE_COMMIT", "result": "OBSERVED_FULL_IDENTITY", "unresolved_reason": None, "_path": path})
        else:
            records.append({"selector_id": item["id"], "raw_selector": item["raw_selector"], "source_class": item["category"], "lookup_method": "tracked_declaration_only", "authoritative_upstream_locator": blob_locator(BASE, path), "observed_identity": None, "mutability": "DECLARED_SELECTOR_ONLY", "result": "BOUNDED_UNRESOLVED", "unresolved_reason": "Only the declared selector and immutable declaration bytes are recorded; package, action, runner, ownership, and resolved content remain unobserved.", "_path": path})
    workflow_locator = blob_locator(BASE, WORKFLOW)
    for selector_id, match in derived:
        records.append({"selector_id": selector_id, "raw_selector": "${{ " + match.group(1).strip() + " }}", "source_class": "runtime_derived", "lookup_method": "static_tracked_expression_inspection", "authoritative_upstream_locator": workflow_locator, "observed_identity": None, "mutability": "RUNTIME_DERIVED", "result": "RUNTIME_DERIVED", "unresolved_reason": "Expression is derived from the tracked workflow metadata output; no external repository or revision identity is promoted.", "_path": WORKFLOW})
    for record in records:
        if record["selector_id"] == "workflow.nested.reusable_caller":
            record.update(result="BOUNDED_UNRESOLVED", lookup_method="tracked_declaration_only", mutability="DECLARED_SELECTOR_ONLY", unresolved_reason="The tracked caller names an upstream workflow, but no upstream commit-tree lookup is retained; invocation, ownership, permissions, and secrets remain unproven.")
    return records

def check() -> None:
    inv = historical_inventory()
    data = json.loads(PATH.read_text(encoding="utf-8"))
    historical_data = historical_observations()
    if PATH.read_bytes() != historical_observations_bytes() or data != historical_data:
        fail("timestamped observation packet drifted from immutable historical object")
    if set(data) != {"schema_name","schema_version","status","source_inventory","records"}:
        fail("top-level schema mismatch")
    if data["schema_name"] != "glyph_build_input_resolution_observations" or data["schema_version"] != 1:
        fail("schema identity mismatch")
    if data["status"] != "timestamped_observations_without_selector_mutation_or_reproducibility":
        fail("status mismatch")
    source = data["source_inventory"]
    if source != {"path": str(INVENTORY.relative_to(ROOT)), "sha256": INVENTORY_SHA, "blob": INVENTORY_BLOB, "base_configurator_sha": BASE}:
        fail("source inventory identity or base binding mismatch")
    if base_blob(source["path"]) != INVENTORY_BLOB:
        fail("historical source inventory blob drifted")
    if base_blob(WORKFLOW) != WORKFLOW_BLOB or base_blob(META) != META_BLOB:
        fail("bound workflow or metadata blob drifted")
    subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT, check=True, capture_output=True)
    expected = expected_records(inv, base_text(WORKFLOW))
    records = data["records"]
    if len(records) != len(expected):
        fail("record count mismatch")
    for actual, wanted in zip(records, expected):
        if set(actual) != FIELDS:
            fail(f"record fields mismatch: {actual.get('selector_id')}")
        for key in ("selector_id","raw_selector","source_class","lookup_method","authoritative_upstream_locator","observed_identity","mutability","result","unresolved_reason"):
            if actual[key] != wanted[key]:
                fail(f"source-bound policy mismatch: {actual.get('selector_id')}:{key}")
        if actual["source_inventory_sha256"] != INVENTORY_SHA or actual["source_inventory_blob"] != INVENTORY_BLOB:
            fail(f"record inventory identity mismatch: {actual['selector_id']}")
        try:
            datetime.strptime(actual["observed_at"], "%Y-%m-%dT%H:%M:%SZ")
        except (TypeError, ValueError) as exc:
            fail(f"invalid timestamp: {actual['selector_id']}: {exc}")
        if not URL.fullmatch(actual["authoritative_upstream_locator"]) or not URL.fullmatch(actual["evidence_locator"]):
            fail(f"invalid immutable locator: {actual['selector_id']}")
        if actual["result"] == "OBSERVED_FULL_IDENTITY":
            if not SHA40.fullmatch(actual["observed_identity"] or "") or actual["unresolved_reason"] is not None:
                fail(f"invalid resolved identity: {actual['selector_id']}")
        elif actual["result"] in RESULTS - {"OBSERVED_FULL_IDENTITY"}:
            if actual["observed_identity"] is not None or not actual["unresolved_reason"]:
                fail(f"unresolved record must retain null identity and reason: {actual['selector_id']}")
        else:
            fail(f"unknown result: {actual['selector_id']}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next((item for item in manifest["entries"] if item["id"] == "build_input_resolution_observations"), None)
    if entry is None or entry["source_dependencies"] != [str(INVENTORY.relative_to(ROOT)), WORKFLOW, META]:
        fail("manifest direct dependencies are not exact")
    print(f"glyph_build_input_resolution_observations: PASS; records={len(records)}; direct={len(records)-2}; derived=2; base={BASE}")

if __name__ == "__main__":
    try:
        check()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"glyph_build_input_resolution_observations: FAIL: {exc}")
        sys.exit(1)
