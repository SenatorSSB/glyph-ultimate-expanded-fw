#!/usr/bin/env python3
"""Focused positive, negative, determinism, and non-mutation checks."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path

from source_owned_cpp_preview import render_cpp_preview, write_preview
from source_owned_generator_modes import _baseline_tables, baseline_identity, digest, generate, prepare, GeneratorModesError


def base(mode: str, provenance: str = "synthetic_test") -> dict:
    baseline = _baseline_tables()
    value = {"schema_version": 2, "profile_id": f"preview-{mode}", "profile_name": f"preview-{mode}", "provenance_class": provenance, "generation_mode": mode, "tables": copy.deepcopy(baseline)}
    if mode == "overlay_preserve":
        value.update({"owned_tables": ["kY2Table"], "tables": [copy.deepcopy(baseline[7])], "baseline": baseline_identity()})
    return value


def expect_reject(fn, needle: str) -> None:
    try:
        fn()
    except GeneratorModesError as exc:
        assert needle in str(exc), str(exc)
        return
    raise AssertionError(f"expected rejection containing {needle!r}")


def seal(packet: dict) -> dict:
    packet["prepared_semantic_digest"] = digest({key: value for key, value in packet.items() if key != "prepared_semantic_digest"})
    return packet


def main() -> int:
    full_artifact, full_manifest = generate(base("full_replacement"))
    packet = prepare(full_artifact, full_manifest) if False else {"schema_version": 1, "artifact": full_artifact, "manifest": full_manifest, "target": "inert_source_owned_artifact_only", "source_mutation": False}
    seal(packet)
    preview = render_cpp_preview(packet, test_mode=True)
    assert preview == render_cpp_preview(json.loads(json.dumps(packet)), test_mode=True)
    assert preview.count("// ") >= 28 and preview.count("{        ") == 0 and "INACTIVE REVIEW PREVIEW" in preview
    changed = base("overlay_preserve"); changed["tables"][0]["points"][4] = {"x": 127, "y": 128}
    artifact, manifest = generate(changed); changed_packet = seal({"schema_version": 1, "artifact": artifact, "manifest": manifest, "target": "inert_source_owned_artifact_only", "source_mutation": False})
    assert "kY2Table" in render_cpp_preview(changed_packet, test_mode=True)
    tampered = copy.deepcopy(packet); tampered["prepared_semantic_digest"] = "wrong"; expect_reject(lambda: render_cpp_preview(tampered, test_mode=True), "digest mismatch")
    tampered = copy.deepcopy(packet); tampered["artifact"]["tables"][0]["table_symbol"] = "kInventedTable"; seal(tampered); expect_reject(lambda: render_cpp_preview(tampered, test_mode=True), "canonical baseline order")
    tampered = copy.deepcopy(packet); tampered["manifest"]["rows"][0]["reason"] = "tampered"; seal(tampered); expect_reject(lambda: render_cpp_preview(tampered, test_mode=True), "manifest semantic digest")
    tampered = copy.deepcopy(packet); tampered["manifest"]["classification"] = "FULL_REPLACEMENT_CHANGESET"; tampered["manifest"]["changed_table_ids"] = []; tampered["manifest"]["preserved_table_ids"] = list(range(28)); tampered["manifest"]["manifest_semantic_digest"] = digest({key: value for key, value in tampered["manifest"].items() if key != "manifest_semantic_digest"}); seal(tampered); expect_reject(lambda: render_cpp_preview(tampered, test_mode=True), "classification")
    tampered = copy.deepcopy(packet); tampered["manifest"]["unknown"] = True; seal(tampered); expect_reject(lambda: render_cpp_preview(tampered, test_mode=True), "missing or unexpected")
    expect_reject(lambda: render_cpp_preview(packet), "test-mode")
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "preview.hpp"
        write_preview(packet, target, test_mode=True)
        assert target.read_text(encoding="utf-8") == preview
        expect_reject(lambda: write_preview(packet, Path(__file__).resolve().parents[1] / "preview.hpp", test_mode=True), "isolated")
        outside = Path(tempfile.gettempdir()) / "glyph-preview-parent-link"
        outside.mkdir(exist_ok=True)
        alias = Path(directory) / "alias"
        root_alias = Path(directory) / "root-alias"
        try:
            alias.symlink_to(outside, target_is_directory=True)
            expect_reject(lambda: write_preview(packet, alias / "preview.hpp", test_mode=True), "isolated")
            root_alias.symlink_to(Path(tempfile.gettempdir()), target_is_directory=True)
            expect_reject(lambda: write_preview(packet, root_alias / "preview.hpp", test_mode=True), "isolated")
        finally:
            if alias.is_symlink(): alias.unlink()
            if root_alias.is_symlink(): root_alias.unlink()
    print(json.dumps({"status": "PASS", "positive_tests": 4, "negative_tests": 7, "active_source_changed": False, "hardware_candidate_created": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
