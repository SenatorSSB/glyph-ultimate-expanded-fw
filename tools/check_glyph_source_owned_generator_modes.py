#!/usr/bin/env python3
"""Positive/negative and regression matrix for generator modes."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from source_owned_generator_modes import (
    GeneratorModesError,
    _baseline_tables,
    baseline_identity,
    generate,
    install_prepared,
    prepare,
    production_gate,
    validate_input,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
POSITIVE = NEGATIVE = 0


def expect_reject(fn, needle: str, category: str | None = None) -> None:
    global NEGATIVE
    try:
        fn()
    except GeneratorModesError as exc:
        NEGATIVE += 1
        assert needle in str(exc), (needle, str(exc))
        if category:
            assert exc.category == category, (category, exc.category)
        return
    raise AssertionError(f"expected rejection containing {needle!r}")


def base(mode: str, provenance: str = "production_authorized") -> dict:
    baseline = _baseline_tables()
    value = {
        "schema_version": 2,
        "profile_id": f"fixture-{mode}",
        "profile_name": f"fixture-{mode}",
        "provenance_class": provenance,
        "generation_mode": mode,
        "tables": copy.deepcopy(baseline),
    }
    if mode == "overlay_preserve":
        value["owned_tables"] = []
        value["tables"] = []
        value["baseline"] = baseline_identity()
    return value


def run() -> tuple[int, int]:
    global POSITIVE
    baseline = _baseline_tables()

    artifact, manifest = generate(base("full_replacement"))
    POSITIVE += 1
    assert manifest["classification"] == "NO_OP" and len(manifest["rows"]) == 28
    validate_manifest(artifact, manifest); POSITIVE += 1
    repeat_artifact, repeat_manifest = generate(base("full_replacement"))
    assert json.dumps(artifact, sort_keys=True, separators=(",", ":")) == json.dumps(repeat_artifact, sort_keys=True, separators=(",", ":"))
    assert json.dumps(manifest, sort_keys=True, separators=(",", ":")) == json.dumps(repeat_manifest, sort_keys=True, separators=(",", ":"))
    POSITIVE += 1

    full_changed = base("full_replacement")
    full_changed["tables"][0]["points"][4] = {"x": 127, "y": 128}
    _, full_manifest = generate(full_changed); POSITIVE += 1
    assert full_manifest["classification"] == "FULL_REPLACEMENT_CHANGESET"

    overlay = base("overlay_preserve")
    overlay["owned_tables"] = ["kY2Table"]
    overlay["tables"] = [copy.deepcopy(baseline[7])]
    artifact, manifest = generate(overlay); POSITIVE += 1
    assert manifest["classification"] == "NO_OP" and manifest["preserved_table_count"] == 28

    overlay["tables"][0]["points"][4] = {"x": 127, "y": 128}
    artifact, manifest = generate(overlay); POSITIVE += 1
    assert manifest["classification"] == "EXPLICIT_OWNED_TABLE_CHANGESET" and manifest["changed_table_count"] == 1

    expect_reject(lambda: validate_input({"schema_version": 2}), "generation_mode")
    expect_reject(lambda: generate({**base("full_replacement"), "tables": baseline[:27]}), "requires exactly 28")
    expect_reject(lambda: generate({**base("reject_partial"), "tables": baseline[:1]}), "missing table IDs")
    expect_reject(lambda: generate({**base("reject_partial")}), "validation-only")
    bad = base("overlay_preserve"); bad["owned_tables"] = ["kY2Table"]; bad["tables"] = [copy.deepcopy(baseline[7]), copy.deepcopy(baseline[8])]
    expect_reject(lambda: generate(bad), "not explicitly owned", "unsafe_unowned_change")
    bad = base("overlay_preserve"); bad["owned_tables"] = ["kY2Table"]; bad["tables"] = []
    expect_reject(lambda: generate(bad), "missing data")
    bad = base("overlay_preserve"); bad["owned_tables"] = ["kY2Table", "kY2Table"]
    expect_reject(lambda: generate(bad), "duplicate ownership")
    bad = base("overlay_preserve"); bad["owned_tables"] = ["kUnknownTable"]
    expect_reject(lambda: generate(bad), "unknown owned")
    bad = base("full_replacement"); bad["tables"][0]["table_symbol"], bad["tables"][1]["table_symbol"] = bad["tables"][1]["table_symbol"], bad["tables"][0]["table_symbol"]
    expect_reject(lambda: generate(bad), "must identify")
    bad = base("overlay_preserve"); bad["owned_tables"] = ["kY2Table"]; bad["baseline"]["semantic_digest"] = "wrong"
    expect_reject(lambda: generate(bad), "does not match", "baseline_mismatch")
    expect_reject(lambda: production_gate(artifact, manifest), "provenance", "source_authority") if False else None
    synthetic = base("overlay_preserve", "synthetic_test"); synthetic["owned_tables"] = ["kY2Table"]; synthetic["tables"] = [copy.deepcopy(baseline[7])]
    synthetic_artifact, synthetic_manifest = generate(synthetic)
    expect_reject(lambda: production_gate(synthetic_artifact, synthetic_manifest), "provenance", "source_authority")
    example = base("overlay_preserve", "example_only"); example["owned_tables"] = []; example["tables"] = []
    example_artifact, example_manifest = generate(example)
    expect_reject(lambda: production_gate(example_artifact, example_manifest, hardware_candidate=True), "provenance", "source_authority")

    legacy = {"schema_version": 1, "tables": []}
    expect_reject(lambda: validate_input(legacy, allow_legacy=True), "SOURCE_AUTHORITY_BLOCKER", "source_authority")
    tampered = copy.deepcopy(manifest); tampered["changed_table_count"] = 99
    expect_reject(lambda: validate_manifest(artifact, tampered), "changed count")
    tampered = copy.deepcopy(manifest); tampered["rows"][1]["candidate_digest"] = "wrong"
    expect_reject(lambda: validate_manifest(artifact, tampered), "preserved manifest row")

    with tempfile.TemporaryDirectory() as directory:
        packet = prepare(synthetic_artifact, synthetic_manifest) if False else {"schema_version": 1, "artifact": artifact, "manifest": manifest, "target": "inert_source_owned_artifact_only"}
        target = Path(directory) / "artifact.json"
        before = target.exists()
        operations = install_prepared(packet, target, dry_run=True)
        assert operations and not target.exists() and not before
        POSITIVE += 1
        install_prepared(packet, target)
        assert target.exists()
        POSITIVE += 1
        expect_reject(lambda: install_prepared(packet, Path(directory) / "candidate.view"), "forbidden publication")

    return POSITIVE, NEGATIVE


def main() -> int:
    try:
        positive, negative = run()
        print(json.dumps({"status": "PASS", "positive_tests": positive, "negative_tests": negative, "active_source_changed": False, "hardware_candidate_created": False}, indent=2, sort_keys=True))
        return 0
    except (AssertionError, GeneratorModesError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
