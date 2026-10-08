"""Focused fail-closed tests for exact C023 source-free admission."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import glyph_c023_campaign_transition as campaign
import glyph_campaign_transition as general_campaign
import run_glyph_runtime_config_validation as runner
from glyph_hardware_correspondence import CorrespondenceError

ROOT = Path(__file__).resolve().parents[1]


class C023AdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapping_bytes = (ROOT / campaign.MAPPING).read_bytes()
        self.mapping = json.loads(self.mapping_bytes)
        self.transition_bytes = (ROOT / campaign.TRANSITIONS).read_bytes()

    def _run(self, mapping=None, transitions=None) -> None:
        mapping_raw = self.mapping_bytes if mapping is None else (json.dumps(mapping, indent=2) + "\n").encode()
        transitions_raw = self.transition_bytes if transitions is None else (json.dumps(transitions, indent=2) + "\n").encode()
        original_current = campaign.current_bytes

        def current(root, path):
            if path == campaign.MAPPING:
                return mapping_raw
            if path == campaign.TRANSITIONS:
                return transitions_raw
            return original_current(root, path)

        with patch.object(campaign, "current_bytes", side_effect=current), \
             patch.object(campaign.previous, "predecessor_contract", return_value=({}, None)), \
             patch.object(campaign.previous, "source_contract", return_value=({}, {})):
            campaign.source_contract(ROOT)

    def _reject(self, mapping=None, transitions=None) -> None:
        with self.assertRaises(CorrespondenceError):
            self._run(mapping, transitions)

    def test_exact_candidate_inventory_is_admitted(self) -> None:
        self._run()

    def test_candidate_identity_substitution_rejected(self) -> None:
        bad = copy.deepcopy(self.mapping)
        bad["candidate"] = "0" * 40
        self._reject(bad)

    def test_missing_or_extra_raw_path_rejected(self) -> None:
        missing = copy.deepcopy(self.mapping)
        missing["entries"].pop()
        self._reject(missing)
        extra = copy.deepcopy(self.mapping)
        extra["entries"].append(copy.deepcopy(extra["entries"][0]))
        self._reject(extra)

    def test_mode_or_review_substitution_rejected(self) -> None:
        bad_mode = copy.deepcopy(self.mapping)
        bad_mode["entries"][0]["new_mode"] = "100755"
        self._reject(bad_mode)
        bad_review = copy.deepcopy(self.mapping)
        bad_review["review"]["reviewed_tree"] = "0" * 40
        self._reject(bad_review)

    def test_unearned_transition_is_rejected(self) -> None:
        catalog = json.loads(self.transition_bytes)
        catalog["accepted_transitions"].append({"work_order": "GP-CONFIG-023", "hardware_result": "PASS"})
        self._reject(transitions=catalog)


class C023HardwarePendingTests(unittest.TestCase):
    def setUp(self) -> None:
        head = campaign._git(ROOT, "rev-parse", "HEAD").decode().strip()
        self.order = campaign.item(ROOT, head, "GP-CONFIG-023")

    def test_exact_pending_handoff_is_admitted_without_physical_acceptance(self) -> None:
        record = campaign._hardware_pending_contract(ROOT, self.order)
        self.assertEqual(record["result"], "NOT_TESTED")
        self.assertTrue(all(step["observed"].startswith("NOT_TESTED") for step in record["steps"]))

    def test_pending_candidate_or_result_substitution_is_rejected(self) -> None:
        bad_identity = dict(self.order)
        bad_identity["firmware_artifact_sha256"] = "0" * 64
        with self.assertRaises(CorrespondenceError):
            campaign._hardware_pending_contract(ROOT, bad_identity)

        evidence = json.loads((ROOT / campaign.EVIDENCE).read_text())
        evidence["steps"][0]["observed"] = "PASS"
        original_current = campaign.current_bytes

        def tampered_current(root, path):
            if path == campaign.EVIDENCE:
                return (json.dumps(evidence) + "\n").encode()
            return original_current(root, path)

        with patch.object(campaign, "current_bytes", side_effect=tampered_current):
            with self.assertRaises(CorrespondenceError):
                campaign._hardware_pending_contract(ROOT, self.order)


class C023CatalogDispatchTests(unittest.TestCase):
    """The exact replay receives C023 roots before source integration."""

    def test_source_free_c023_replay_uses_c023_roots_and_c022_lane_stays_separate(self) -> None:
        runner.ROOT = ROOT
        c023 = {
            "id": "gp_config023_usb_index_validation",
            "path": "tools/check_glyph_c023_proof_replay.py",
            "command": ["python3", "tools/check_glyph_c023_proof_replay.py"],
            "applicability": "current",
        }
        c023_proofs = []
        original_c023_authenticate = campaign.authenticate
        def record_c023_authenticate(root):
            proof = original_c023_authenticate(root)
            c023_proofs.append(proof)
            return proof
        with patch.object(campaign, "authenticate", side_effect=record_c023_authenticate) as authenticate_c023:
            _, c023_roots = runner.required_catalog([c023])
            authenticate_c023.assert_called_once_with(ROOT)
        c023_proof = c023_proofs[0]
        self.assertEqual(c023_proof["phase"], "SOURCE_FREE_PROCESSOR")
        self.assertEqual(c023_proof["handoff_stage"], "HARDWARE_PENDING")
        self.assertIn(campaign.C, c023_proof["object_roots"])
        self.assertIn(campaign.C, c023_roots)

        c022 = {
            "id": "gp_config022_rgb_target_validation",
            "path": "tools/check_glyph_c022_proof_replay.py",
            "command": ["python3", "tools/check_glyph_c022_proof_replay.py"],
            "applicability": "current",
        }
        with patch.object(general_campaign, "authenticate", wraps=general_campaign.authenticate) as authenticate_c022:
            _, c022_roots = runner.required_catalog([c022])
            authenticate_c022.assert_called_once_with(ROOT)
        self.assertNotIn(campaign.C, c022_roots)


if __name__ == "__main__":
    unittest.main()
