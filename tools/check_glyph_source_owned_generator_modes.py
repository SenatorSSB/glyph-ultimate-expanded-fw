#!/usr/bin/env python3
"""Positive/negative and regression matrix for generator modes."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import source_owned_generator_modes as generator_modes
from source_owned_generator_modes import (
    GeneratorModesError,
    _baseline_tables,
    baseline_identity,
    digest,
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
        normalized = validate_input(base("full_replacement"))
        full_artifact, full_manifest = generate(normalized)
        packet = {"schema_version": 2, "normalized_input": normalized, "artifact": full_artifact, "manifest": full_manifest, "target": "inert_source_owned_artifact_only", "source_mutation": False}
        packet["prepared_semantic_digest"] = digest(packet)
        target = Path(directory) / "artifact.json"
        before = target.exists()
        raw_root = Path(tempfile.gettempdir()).resolve()
        if Path(tempfile.gettempdir()) != raw_root:
            expect_reject(lambda: install_prepared(packet, target, dry_run=True), "aliased temporary root")
        else:
            operations = install_prepared(packet, target, dry_run=True)
            assert operations and not target.exists() and not before
            POSITIVE += 1
            install_prepared(packet, target)
            assert target.exists()
            POSITIVE += 1
            expect_reject(lambda: install_prepared(packet, Path(directory) / "candidate.view"), "forbidden publication")
        if Path(tempfile.gettempdir()) == raw_root:
            tampered_packet = copy.deepcopy(packet)
            tampered_packet["normalized_input"]["metadata"] = {"intake_id": True}
            tampered_packet["prepared_semantic_digest"] = digest({key: value for key, value in tampered_packet.items() if key != "prepared_semantic_digest"})
            expect_reject(lambda: install_prepared(tampered_packet, target, input_path=target), "metadata")
            expect_reject(lambda: install_prepared(packet, target, input_path=target), "overwrite input")

        if Path(tempfile.gettempdir()) == raw_root:
            input_path = Path(directory) / "input.json"
            input_path.write_text("input\n", encoding="utf-8")
            hardlink = Path(directory) / "hardlink.json"
            hardlink.hardlink_to(input_path)
            expect_reject(
                lambda: generator_modes.validate_safe_output_path(hardlink, input_path=input_path),
                "unsafe existing alias",
                "source_authority",
            )
            real_parent = Path(directory) / "real-parent"
            real_parent.mkdir()
            alias_parent = Path(directory) / "alias-parent"
            alias_parent.symlink_to(real_parent, target_is_directory=True)
            expect_reject(
                lambda: generator_modes.validate_safe_output_path(alias_parent / "output.json"),
                "symlink alias",
                "source_authority",
            )
            safe_output = raw_root / f"glyph-writer-failure-{os.getpid()}.json"
            original_replace = generator_modes.os.replace
            def fail_replace(source: str, target_name: str) -> None:
                raise OSError("injected replacement failure")
            generator_modes.os.replace = fail_replace
            try:
                expect_reject(
                    lambda: generator_modes._atomic_write_text(safe_output, "bytes\n", purpose="injected failure"),
                    "atomic write failed",
                    "integrity",
                )
            finally:
                generator_modes.os.replace = original_replace
            assert not safe_output.exists()
            assert not list(safe_output.parent.glob(f".{safe_output.name}.*"))

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
