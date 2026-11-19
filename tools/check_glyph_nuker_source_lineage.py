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
DISCOVERY = ROOT / "docs/runtime_config/fixtures/glyph_nuker_source_discovery_g2b.v1.json"
REPRODUCTION = ROOT / "docs/runtime_config/fixtures/glyph_nuker_source_reproduction_g2d.v1.json"
G2D_RAW_SHA256 = "3ff7af9ab670029c8a3c8e8118349cfc44b3c80ac163528c31537bb35fccca73"
G2D_SEMANTIC_SHA256 = "a76bc6670d85f5b7615be3158e4fee66c64072120be93063e9a70edc21563284"
G2F = ROOT / "docs/runtime_config/fixtures/glyph_nuker_release_rights_g2f.v1.json"
G2F_SEMANTIC_SHA256 = "df7ded8a19e9d781cdbc7dc056384511c41930828ae4529c72a3d25717d8de11"
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
    sealed_receipt(FIXTURE, "292728ec8d9f78d2bb1a3dd5dc9cf52dc07a273af57a9e3561a2b8e4b44c4fe1")
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
                "status": "GLYPH_NUKER_CORRESPONDING_SOURCE_PACKAGING_REQUIRED",
                "public_action": "OMIT_AND_BLOCK_PUBLICATION"}:
            fail("omitted postprocessor lacks explicit public blocking contract")

def validate_g2c(value: dict) -> None:
    """Validate G2C knowledge at its historical checkpoint, before G2D."""
    if value["binary"] != {"path": "glyph_nuker", "git_blob": EXPECTED_BLOB, "sha256": EXPECTED_SHA256} or any(v != "UNKNOWN" for v in value["claims"].values()):
        fail("G2B historical binary/unknown claims drifted")
    current = value["stage_g2c"]
    provenance = current["binary_provenance"]
    if (provenance["binary_origin_repository"] != "LimitLabs/FW-Glyph"
            or provenance["git_blob"] != EXPECTED_BLOB
            or provenance["sha256"] != EXPECTED_SHA256
            or provenance["introduction_commit"] != EXPECTED_INTRO
            or provenance["binary_blob_match"] != "exact"
            or provenance["binary_bytes_match"] != "exact"):
        fail("verified upstream binary identity drifted")
    source = current["source_candidate"]
    if (source["repository"] != "GregTurbo/glyph-nuker"
            or source["revision"] != "5c544caa61fe378eb44be4edf74993b7841bf907"
            or source["license"] != "UNKNOWN"
            or source["exact_binary_relationship"] != "UNKNOWN"
            or source["classification"] != "SOURCE_FOUND_BUILD_RECIPE_INCOMPLETE"):
        fail("candidate source evidence was promoted or changed")
    expected_claims = {key: "UNKNOWN" for key in (
        "corresponding_source", "source_lineage", "build_recipe",
        "byte_transformation", "purpose", "reproducibility", "license")}
    if current["canonical_binary_claims"] != expected_claims:
        fail("canonical source/build/license claims were promoted")
    build = current["bounded_build"]
    if (build["produced_executable"] is not False
            or build["nuker_executables_executed"] is not False
            or build["exact_byte_comparison"] != "NOT_POSSIBLE_NO_OUTPUT"):
        fail("bounded build evidence was promoted")
    if (current["export_classification"] != "REVIEW_REQUIRED"
            or current["public_export"] != "BLOCKED"
            or current["export_blocker_status"] != "GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED"
            or current["stage_result"] != "SOURCE_FOUND_BINARY_NOT_REPRODUCED"):
        fail("unresolved export gate was promoted")


def validate_g2c_receipt() -> None:
    sealed_receipt(DISCOVERY, "15c4846e0182a671a0ad59d54b62b4ca250293848cbfb74c0e2df53ccf8e9c5d")
    value = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    validate_g2c(value)
    # Negative controls protect the distinction between a source candidate and
    # clearance of the exact executable. No binary or network execution occurs.
    for field, promoted in (
            ("canonical_binary_claims", {"license": "GPLv3"}),
            ("public_export", "PASS"),
            ("source_candidate", {**value["stage_g2c"]["source_candidate"], "license": "GPLv3"}),
            ("source_candidate", {**value["stage_g2c"]["source_candidate"], "exact_binary_relationship": "EXACT_BINARY_REPRODUCED"})):
        tampered = copy.deepcopy(value)
        tampered["stage_g2c"][field] = promoted
        try:
            validate_g2c(tampered)
        except LineageError:
            pass
        else:
            fail("unsupported G2C clearance accepted: " + field)


def sealed_receipt(path: Path, expected: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        fail("required regular receipt missing: " + path.name)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        fail("sealed receipt drifted: " + path.name)
    return raw


def unique_pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            fail("duplicate G2D key: " + key)
        result[key] = value
    return result


def validate_g2d(value: dict) -> None:
    # This is a closed reviewed receipt, not admission of arbitrary new build
    # results. The semantic seal protects every matrix hash/size, input identity,
    # limitation, negative control and release field against unsupported edits.
    semantic = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(semantic).hexdigest() != G2D_SEMANTIC_SHA256:
        fail("G2D reviewed evidence/limitations/release status drifted")
    if (value["schema"] != "glyph_nuker_source_reproduction_g2d.v1"
            or value["stage_result"] != "SOURCE_REPRODUCED_LICENSE_UNRESOLVED"):
        fail("G2D disposition drifted")
    rows = value["matrix"]
    revisions = {item["revision"] for item in value["source"]["revisions"]}
    if (len(rows) != 8 or {(r["revision"], r["optimization"]) for r in rows}
            != {(rev, opt) for rev in revisions for opt in
                ("Debug", "ReleaseSafe", "ReleaseFast", "ReleaseSmall")}):
        fail("G2D complete bounded matrix required")
    for row in rows:
        exact = (row["revision"] == value["build"]["matching_revision"]
                 and row["optimization"] == "ReleaseSmall")
        if (row["build_exit"] != 0 or row["python_exact_bytes_equal"] is not exact
                or row["cmp_exit"] != (0 if exact else 1)
                or row["outcome"] != ("EXACT" if exact else "DIFFERENT")
                or (row["sha256"] == EXPECTED_SHA256) != exact):
            fail("G2D unsupported exact-match claim")
    output = value["matching_output"]
    if output["git_blob"] != EXPECTED_BLOB or output["sha256"] != EXPECTED_SHA256 or output["size_bytes"] != 23336:
        fail("G2D matching binary identity drifted")
    release = value["release"]
    if (release["source_license"] != "UNRESOLVED"
            or release["executable_license"] != "UNRESOLVED"
            or release["public_export"] != "BLOCKED"
            or release["export_classification"] != "REVIEW_REQUIRED"
            or release["export_blocker_status"] != "GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED"
            or release["release_inputs_cleared"] is not False):
        fail("G2D license/export gate drifted")


def validate_g2d_receipt() -> list[str]:
    raw = sealed_receipt(REPRODUCTION, G2D_RAW_SHA256)
    value = json.loads(raw, object_pairs_hook=unique_pairs)
    validate_g2d(value)
    # Each mutation is checked against the semantic validator rather than only
    # the raw-file seal. No source compilation or executable execution occurs.
    changes = [
        ("incorrect_source_revision", ("build", "matching_revision"), "0" * 40),
        ("incorrect_optimization", ("build", "matching_optimization"), "ReleaseFast"),
        ("incorrect_binary_identity", ("matching_output", "sha256"), "0" * 64),
        ("unsupported_exact_match", ("matrix", 0, "outcome"), "EXACT"),
        ("fabricated_source_license", ("release", "source_license"), "GPLv3"),
        ("fabricated_executable_license", ("release", "executable_license"), "GPLv3"),
        ("unsupported_public_export", ("release", "public_export"), "CLEARED"),
        ("changed_release_blocker", ("release", "export_blocker_status"), "RESOLVED"),
        ("hardware_transfer", ("limitations", "hardware_qualification_transfer"), True),
        ("historical_attestation", ("limitations", "historical_original_build_procedure"), "VERIFIED"),
        ("missing_matrix_row", ("matrix",), value["matrix"][:-1]),
        ("changed_output_size", ("matrix", 0, "size_bytes"), 23336),
        ("negative_control_promotion", ("comparison", "negative_controls", 1, "python_exact_bytes_equal"), True),
    ]
    rejected = []
    for label, path, replacement in changes:
        tampered = copy.deepcopy(value)
        parent = tampered
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = replacement
        try:
            validate_g2d(tampered)
        except LineageError:
            rejected.append(label)
        else:
            fail("unsupported G2D claim accepted: " + label)
    return rejected



def validate_g2f(value: dict) -> None:
    # Closed reviewed engineering interpretation. This seal includes every
    # evidence locator, standalone-license caveat, OWNER_SUPPLIED label,
    # packaging obligation and limitation. New findings require explicit review.
    semantic = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(semantic).hexdigest() != G2F_SEMANTIC_SHA256:
        fail("G2F provenance/source/recipe/obligation/limitation drifted")


def validate_g2f_receipt() -> list[str]:
    # Keep this offline evidence checker independent of the exporter module;
    # the existing manifest's direct-helper boundary remains unchanged.
    NUKER_OBLIGATION = "GLYPH_NUKER_CORRESPONDING_SOURCE_PACKAGING_REQUIRED"
    G2F_SHA256 = "66890d4b2cd8c8065ba480e145af365ad3864b785e83eb15fb517f39bfc84f79"
    value = json.loads(sealed_receipt(G2F, G2F_SHA256), object_pairs_hook=unique_pairs)
    validate_g2f(value)
    for path, wanted in value["historical_receipts_sha256"].items():
        sealed_receipt(ROOT / path, wanted)
    policy = json.loads((ROOT / "tools/fixtures/glyph_public_export_policy.v1.json").read_text(), object_pairs_hook=unique_pairs)
    if policy.get("glyph_nuker_obligation") != {
            "status": NUKER_OBLIGATION,
            "receipt": G2F.relative_to(ROOT).as_posix(), "receipt_sha256": G2F_SHA256,
            "source_prefix": "third_party/glyph-nuker/",
            "source_revision": value["source"]["matching_revision"],
            "required_notices": ["LICENSE", "THIRD_PARTY_NOTICES.md"]}:
        fail("current mandatory source/provenance obligation missing or drifted")
    binary_record = policy["exceptions"]["glyph_nuker"]
    dependency = next(row for row in policy["dependencies"] if row["name"] == "glyph_nuker")
    if (binary_record["classification"] != "REVIEW_REQUIRED"
            or dependency["action"] != "REVIEW_REQUIRED"
            or dependency["license_evidence"] != G2F.relative_to(ROOT).as_posix()
            or dependency["selector_kind"] != "tracked_blob_with_exact_reproduced_corresponding_source"):
        fail("G2F pending source packaging/known correspondence policy drifted")
    if "GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED" in json.dumps(policy):
        fail("retired missing-source blocker returned in current policy")
    if policy["notice_sha256"]["THIRD_PARTY_NOTICES.md"] != hashlib.sha256((ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()).hexdigest():
        fail("current third-party notices hash drifted")
    from glyph_ci_package_scope import public_contract
    if public_contract(ROOT)["opaque_postprocessor"] != {
            "path": "glyph_nuker", "sha256": EXPECTED_SHA256,
            "status": NUKER_OBLIGATION, "public_action": "OMIT_AND_BLOCK_PUBLICATION"}:
        fail("current public omission obligation drifted")
    current = DOC.read_text().split("## Historical G2D", 1)[0]
    for phrase in ("Current G2F", NUKER_OBLIGATION, "OWNER_SUPPLIED", "not release-ready"):
        if phrase not in current:
            fail("current lineage wording missing: " + phrase)
    changes = [
        ("official_binary_identity", ("official_repository", "binary", "sha256"), "0" * 64),
        ("matching_revision", ("source", "matching_revision"), "0" * 40),
        ("reproduced_command", ("reproduced_recipe", "command"), "zig build"),
        ("reproduced_zig", ("reproduced_recipe", "zig"), "0.15.1"),
        ("reproduced_target", ("reproduced_recipe", "target"), "aarch64-linux"),
        ("reproduced_cpu", ("reproduced_recipe", "cpu"), "native"),
        ("reproduced_optimization", ("reproduced_recipe", "optimization"), "ReleaseFast"),
        ("fabricated_standalone_license", ("source", "standalone_license_file"), True),
        ("lost_gpl_declaration", ("official_repository", "project_license", "declaration"), "UNKNOWN"),
        ("source_downgrade", ("source", "correspondence"), "UNKNOWN"),
        ("source_promotion", ("source", "correspondence"), "ALL_REVISIONS_REPRODUCED"),
        ("lost_packaging_obligation", ("release", "current_obligation"), None),
        ("historical_attestation", ("limitations", "historical_maintainer_build_attestation"), True),
        ("hardware_transfer", ("limitations", "hardware_acceptance_transfer"), True),
        ("release_ready", ("release", "export_classification"), "PASS"),
        ("overall_release_ready", ("release", "overall_release_ready"), True),
        ("public_export_pass", ("release", "public_export"), "PASS"),
        ("lost_source_notice_obligations", ("release", "required_obligations"), []),
        ("old_blocker_reactivated", ("release", "current_obligation"), "GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED"),
        ("owner_relationship_promotion", ("owner_relationship", "source_kind"), "INDEPENDENTLY_VERIFIED"),
        ("sealed_history_mutation", ("historical_receipts_sha256", "docs/runtime_config/fixtures/glyph_nuker_source_lineage.json"), "0" * 64),
    ]
    rejected = []
    for label, path, replacement in changes:
        tampered = copy.deepcopy(value)
        parent = tampered
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = replacement
        try:
            validate_g2f(tampered)
        except LineageError:
            rejected.append(label)
        else:
            fail("unsupported G2F claim accepted: " + label)
    # ABSENT is the valid positive control, not a missing-source conclusion.
    if value["source"]["standalone_license_file"] is not False:
        fail("standalone-license absence documentation lost")
    validate_g2f(value)
    return rejected


def main() -> int:
    try:
        validate(load())
        if sys.argv[1:] == ["--historical"]:
            validate_historical_repository_facts()
        elif sys.argv[1:]:
            fail("expected no arguments or --historical")
        validate_current_receipt()
        validate_g2c_receipt()
        rejected = validate_g2d_receipt()
        g2f_rejected = validate_g2f_receipt()
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
        print("glyph_nuker_source_lineage: PASS; sealed historical/G2C receipts unchanged; G2D exact source-build correspondence; G2F combined GPLv3 provenance reconciled; missing-source blocker RETIRED; GLYPH_NUKER_CORRESPONDING_SOURCE_PACKAGING_REQUIRED; PUBLIC_EXPORT BLOCKED")
        print("G2D negative controls rejected: " + ", ".join(rejected))
        print("G2F negative controls rejected: " + ", ".join(g2f_rejected))
        print("G2F positive control: standalone LICENSE absent; exact source correspondence retained; no missing-source blocker")
        return 0
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"glyph_nuker_source_lineage: FAIL: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
