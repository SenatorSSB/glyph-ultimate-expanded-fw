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
        self.order = campaign.item(ROOT, campaign.R, "GP-CONFIG-023")

    def _pending(self, order):
        original_current = campaign.current_bytes
        def historical_current(root, path):
            if path in {campaign.EVIDENCE, campaign.RESULT, campaign.PROTOCOL}:
                return campaign.raw_bytes(root, campaign.R, path)
            return original_current(root, path)
        with patch.object(campaign, "current_bytes", side_effect=historical_current):
            return campaign._hardware_pending_contract(ROOT, order)

    def test_exact_pending_handoff_is_admitted_without_physical_acceptance(self) -> None:
        record = self._pending(self.order)
        self.assertEqual(record["result"], "NOT_TESTED")
        self.assertTrue(all(step["observed"].startswith("NOT_TESTED") for step in record["steps"]))

    def test_pending_candidate_or_result_substitution_is_rejected(self) -> None:
        bad_identity = dict(self.order)
        bad_identity["firmware_artifact_sha256"] = "0" * 64
        with self.assertRaises(CorrespondenceError):
            self._pending(bad_identity)

        evidence = json.loads(campaign.raw_bytes(ROOT, campaign.R, campaign.EVIDENCE))
        evidence["steps"][0]["observed"] = "PASS"
        original_current = campaign.current_bytes

        def tampered_current(root, path):
            if path == campaign.EVIDENCE:
                return (json.dumps(evidence) + "\n").encode()
            if path in {campaign.RESULT, campaign.PROTOCOL}:
                return campaign.raw_bytes(root, campaign.R, path)
            return original_current(root, path)

        with patch.object(campaign, "current_bytes", side_effect=tampered_current):
            with self.assertRaises(CorrespondenceError):
                campaign._hardware_pending_contract(ROOT, self.order)


class C023CatalogDispatchTests(unittest.TestCase):
    """The selected replay gets roots for the current authenticated phase."""

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
        self.assertIn(c023_proof["phase"], {"SOURCE_FREE_PROCESSOR", "ACCEPTED_TRANSITION"})
        self.assertIn(c023_proof["handoff_stage"], {"HARDWARE_PENDING", "HARDWARE_VALIDATED"})
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
        if campaign.has_source_overlay(ROOT):
            # Once accepted C023 source is integrated, the general current-source
            # guard must carry its exact roots even when a C022 consumer is
            # selected. Before integration, the C022-only lane stays isolated.
            self.assertIn(campaign.C, c022_roots)
            self.assertIn(campaign.F, c022_roots)
        else:
            self.assertNotIn(campaign.C, c022_roots)
            self.assertNotIn(campaign.F, c022_roots)


class C023HardwareAcceptanceControls(unittest.TestCase):
    """Synthetic row/schema negatives confer no physical acceptance."""
    def setUp(self):
        self.record = json.loads(campaign.raw_bytes(ROOT, campaign.R, campaign.EVIDENCE))
        self.record.update(result="PASS", anomalies=[], evidence_gaps=[])
        for row in self.record["steps"]:
            row["observed"] = "PASS synthetic acceptance control; no hardware claim"
        self.result = (campaign.KEYBOARD_DISPOSITION + "\nPRESERVE_ORIGINAL_RAW_KEYBOARD_OUTPUT\n"
                       "POST_BETA_KEYBOARD_PHYSICAL_VALIDATION\nPHYSICAL_NOT_SAFELY_TESTABLE\n").encode()

    def test_missing_duplicate_or_partial_row_rejected(self):
        for mutation in ("missing", "duplicate", "partial"):
            record = copy.deepcopy(self.record)
            if mutation == "missing": record["steps"].pop()
            if mutation == "duplicate": record["steps"][-1] = record["steps"][0]
            if mutation == "partial": record["steps"][0]["observed"] = "PARTIAL"
            with self.assertRaises(CorrespondenceError):
                campaign._hardware_rows(record, self.result)

    def test_keyboard_physical_pass_or_missing_owner_scope_rejected(self):
        for raw in (self.result + b"Keyboard physical PASS", self.result.replace(
                campaign.KEYBOARD_DISPOSITION.encode(), b"Keyboard untested")):
            with self.assertRaises(CorrespondenceError):
                campaign._hardware_rows(self.record, raw)

    def test_predecessor_catalog_loss_extra_or_forged_tuple_rejected(self):
        prior = campaign.previous._catalog(campaign.raw_bytes(ROOT, campaign.B,
                                                             campaign.previous.TRANSITIONS))
        forged = {"work_order":"GP-CONFIG-023", "candidate":campaign.C, "build":"0"*40,
                  "parent":campaign.C, "tree":campaign.F_TREE, "review_commit":campaign.R,
                  "evidence_commit":"1"*40, "integration":"2"*40}
        for records in ([], prior + [forged], prior + [forged, forged]):
            with self.assertRaises(CorrespondenceError):
                campaign._catalog({"schema_version":1,"accepted_transitions":records}, prior)


if __name__ == "__main__":
    unittest.main()
