#!/usr/bin/env python3
"""Checker for explicit overlay/preserve generation and proof classification."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

from glyph_source_owned_overlay import (
    OverlayContractError,
    baseline_contract,
    generate_overlay_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = REPO_ROOT / "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def expect_reject(payload: dict, needle: str, *, production: bool = False) -> None:
    try:
        generate_overlay_payload(payload, production=production)
    except OverlayContractError as exc:
        if needle not in str(exc):
            fail(f"expected {needle!r} in error, got {exc}")
        return
    fail(f"expected rejection containing {needle!r}")


def base_payload(mode: str = "overlay_preserve") -> dict:
    baseline = baseline_contract()
    table = copy.deepcopy(baseline["tables"][7])
    return {
        "schema_version": 1,
        "artifact_kind": "generated_source_owned_runtime_config_table",
        "controller_family": "glyph_mk6",
        "profile_name": "authorized_overlay_profile",
        "revision": 1,
        "generation_mode": mode,
        "baseline": {
            "baseline_id": baseline["baseline_id"],
            "source_path": baseline["source_path"],
            "semantic_digest": baseline["semantic_digest"],
            "table_count": 28,
        },
        "owned_tables": ["kY2Table"],
        "tables": [table],
    }


def run_positive_and_negative_tests() -> None:
    baseline = baseline_contract()
    full = {
        "schema_version": 1,
        "artifact_kind": "generated_source_owned_runtime_config_table",
        "controller_family": "glyph_mk6",
        "profile_name": "authorized_full_profile",
        "revision": 1,
        "generation_mode": "full_replacement",
        "tables": copy.deepcopy(baseline["tables"]),
    }
    output, report = generate_overlay_payload(full)
    if len(output["tables"]) != 28 or len(report["manifest"]) != 28:
        fail("full replacement must emit a complete 28-row artifact and manifest")
    if any(row["action"] != "replace_explicit_owned" for row in report["manifest"]):
        fail("full replacement manifest action mismatch")

    overlay = base_payload()
    output, report = generate_overlay_payload(overlay)
    if len(output["tables"]) != 28 or sum(row["action"] == "preserve_source_owned_baseline" for row in report["manifest"]) != 27:
        fail("overlay must preserve 27 tables")
    if report["output_semantic_digest"] != baseline["semantic_digest"]:
        fail("source-aligned overlay should be a semantic no-op")

    changed = base_payload()
    changed["tables"][0]["points"][4] = {"x": 127, "y": 128}
    _output, changed_report = generate_overlay_payload(changed)
    if not any(row["changed"] and row["table_symbol"] == "kY2Table" for row in changed_report["manifest"]):
        fail("explicitly owned changed table missing from manifest")

    expect_reject({"tables": []}, "generation_mode")
    expect_reject({"generation_mode": "unknown", "tables": []}, "generation_mode")
    full_partial = base_payload("full_replacement")
    full_partial.pop("owned_tables")
    expect_reject({**full_partial, "tables": []}, "exactly 28")
    expect_reject({**base_payload("reject_partial"), "tables": []}, "refuses partial")
    expect_reject({**base_payload(), "baseline": {}}, "baseline identity")
    missing = base_payload(); missing["owned_tables"] = ["kY2Table", "kTilt3Table"]
    expect_reject(missing, "owned table missing")
    not_owned = base_payload(); not_owned["tables"].append(copy.deepcopy(baseline["tables"][21]))
    expect_reject(not_owned, "not explicitly owned")
    unknown = base_payload(); unknown["owned_tables"] = ["kUnknownTable"]
    expect_reject(unknown, "unknown owned")
    duplicate = base_payload(); duplicate["owned_tables"] = ["kY2Table", "kY2Table"]
    expect_reject(duplicate, "duplicate owned")
    changed_unowned = base_payload(); changed_unowned["owned_tables"] = ["kTilt3Table"]
    expect_reject(changed_unowned, "not explicitly owned")
    digest = base_payload(); digest["baseline"]["semantic_digest"] = "bad"
    expect_reject(digest, "digest mismatch")
    wrong_shape = base_payload(); wrong_shape["baseline"]["table_count"] = 27
    expect_reject(wrong_shape, "table_count")
    example = base_payload(); example["profile_name"] = "example_source_owned_runtime_config"
    expect_reject(example, "example", production=True)
    # Test-only override is deliberately accepted only by the checker/tool test path.
    generate_overlay_payload(example, production=True, test_only_override=True)


def proof_report() -> dict:
    raw = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    mode = raw.get("generation_mode")
    if mode is None or "owned_tables" not in raw:
        return {
            "proof_input": str(EXAMPLE.relative_to(REPO_ROOT)),
            "generation_mode": mode,
            "explicit_owned_tables": [],
            "changed_tables": [],
            "preserved_table_count": 0,
            "manifest_status": "not_generated",
            "classification": "SOURCE_AUTHORITY_BLOCKER",
            "candidate_eligibility": "not_a_hardware_candidate",
            "reason": "current example/layout-spec input declares no explicit table ownership",
        }
    _output, report = generate_overlay_payload(raw)
    changed = [row["table_symbol"] for row in report["manifest"] if row["changed"]]
    owned = raw.get("owned_tables", [])
    return {
        "proof_input": str(EXAMPLE.relative_to(REPO_ROOT)),
        "generation_mode": mode,
        "explicit_owned_tables": owned,
        "changed_tables": changed,
        "preserved_table_count": sum(row["action"] == "preserve_source_owned_baseline" for row in report["manifest"]),
        "manifest_status": "complete_28_rows",
        "output_semantic_digest": report["output_semantic_digest"],
        "classification": "NO_OP" if not changed else "EXPLICIT_OWNED_TABLE_CHANGESET",
        "candidate_eligibility": "not_a_hardware_candidate" if not changed else "separate_candidate_requires_review",
    }


def main() -> int:
    try:
        run_positive_and_negative_tests()
        print(json.dumps({"status": "PASS", "negative_tests": 16, "proof": proof_report()}, indent=2, sort_keys=True))
    except (AssertionError, OSError, json.JSONDecodeError, OverlayContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
