#!/usr/bin/env python3
"""Sealed current receipt failures never fall back to historical Git."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_glyph_source_owned_source_authority_intake as authority
import check_glyph_build_input_resolution_observations as observations
import check_glyph_nuker_source_lineage as nuker
import check_glyph_build_input_provenance_inventory as inventory


class CurrentReceipts(unittest.TestCase):
    def test_semantic_reference_is_exact_without_git(self):
        with patch.object(authority.subprocess, "check_output", side_effect=AssertionError("unexpected Git")):
            value = authority.load_semantic_reference()
        self.assertEqual(value["original_packet"]["ownership"]["owned_tables"], ["kX1Table"])
        self.assertEqual(len(value["original_packet"]["replacements"][0]["points"]), 9)

    def test_missing_mutated_and_symlink_semantic_reference_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reference.json"
            with patch.object(authority, "SEMANTIC_REFERENCE", path):
                with self.assertRaises(OSError): authority.load_semantic_reference()
                path.write_text("{}")
                with self.assertRaises(ValueError): authority.load_semantic_reference()
                path.unlink(); path.symlink_to(authority.ROOT / "docs/runtime_config/fixtures/source_owned_x1_pre_f4_semantic_reference.v1.json")
                with self.assertRaises(ValueError): authority.load_semantic_reference()

    def test_observation_reference_does_not_read_historical_objects(self):
        with patch.object(observations, "HISTORICAL", False), patch.object(observations, "git", side_effect=AssertionError("unexpected Git")):
            value = observations.historical_inventory()
            self.assertGreater(len(value["selectors"]), 0)
            self.assertEqual(observations.base_blob(observations.WORKFLOW), observations.WORKFLOW_BLOB)

    def test_observation_reference_missing_mutated_symlink_fail(self):
        original = observations.RECEIPT
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reference.json"
            with patch.object(observations, "RECEIPT", path):
                with self.assertRaises(OSError): observations.sealed_observation_receipt()
                path.write_text(original.read_text() + " ")
                with self.assertRaises(ValueError): observations.sealed_observation_receipt()
                path.unlink(); path.symlink_to(original)
                with self.assertRaises(ValueError): observations.sealed_observation_receipt()

    def test_missing_binary_needs_positive_contract(self):
        import glyph_ci_package_scope as scope
        with patch.object(scope, "public_contract", side_effect=ValueError("no contract")):
            with self.assertRaises(ValueError): inventory.omitted_postprocessor_record(Path.cwd())

    def test_unknown_nuker_claim_cannot_be_promoted(self):
        for key in nuker.load()["claims"]:
            value = copy.deepcopy(nuker.load()); value["claims"][key] = "KNOWN"
            with self.assertRaises(nuker.LineageError): nuker.validate(value)


if __name__ == "__main__":
    unittest.main()
