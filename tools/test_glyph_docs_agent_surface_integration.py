#!/usr/bin/env python3
"""Portable real-Git tests of exact hardware-authorized integration scope."""

from dataclasses import replace
from pathlib import Path
from unittest import TestCase, main, mock
import json
import subprocess
import tempfile

import check_glyph_docs_agent_surface as surface
from glyph_checker_context import CheckerContext, ScopeValidationError

CENSUS = "docs/runtime_config/fixtures/glyph_checker_census.json"
EVIDENCE = "docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json"
GENERATED = "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"


class ExactIntegrationTests(TestCase):
    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "canonical")
        self.git("config", "user.name", "Synthetic review")
        self.git("config", "user.email", "synthetic@example.invalid")
        for path in (surface.GP005_HAL_PATH, GENERATED, "config/glyph/env.ini", "platformio.ini"):
            self.write(path, "baseline\n")
        self.write(CENSUS, "initial census\n")
        self.tested_base = self.commit("tested base")
        self.git("switch", "-qc", surface.GP005_BRANCH)
        self.write(surface.GP005_HAL_PATH, "tested handler\n")
        self.write(CENSUS, "candidate census\n")
        self.candidate = self.commit("exact candidate")
        self.tree = self.git("rev-parse", "HEAD^{tree}")
        self.git("switch", "-q", "canonical")
        identity = {"candidate_git_sha": self.candidate,
                    "candidate_base_configurator_sha": self.tested_base,
                    "firmware_artifact_sha256": surface.GP005_ARTIFACT}
        self.evidence = dict(identity, work_order_id="GP-CONFIG-005", result="PASS", evidence_gaps=[])
        self.write(EVIDENCE, json.dumps(self.evidence))
        evidence_commit = self.commit("immutable hardware evidence")
        self.item = dict(identity, id="GP-CONFIG-005", status="HARDWARE_VALIDATED", hardware_result="PASS",
                         hardware_evidence_gaps=[], hardware_evidence_record=f"git-json:{evidence_commit}:{EVIDENCE}")
        self.write_queue()
        self.base = self.commit("canonical authorization")
        self.git("update-ref", "refs/remotes/origin/configurator", self.base)
        self.git("switch", "-qc", "arbitrary-integration-name")
        self.git("merge", "--no-ff", "-qm", "exact merge", self.candidate)
        self.merge = self.git("rev-parse", "HEAD")
        self.context = CheckerContext(
            self.root, "arbitrary-integration-name", self.merge, "origin/configurator", self.base,
            None, self.base, True, frozenset({surface.GP005_HAL_PATH, CENSUS}),
            frozenset(), frozenset(),
        )
        for name, value in (("GP005_CANDIDATE", self.candidate), ("GP005_BASE", self.tested_base), ("GP005_TREE", self.tree)):
            patch = mock.patch.object(surface, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def write_queue(self):
        self.write(surface.QUEUE_PATH, "<!-- queue-state:start -->\n```json\n" + json.dumps({"items": [self.item]}) + "\n```\n")

    def decision(self, context=None):
        context = context or self.context
        surface.validate_surface_scope(context)
        return surface.exact_gp005_integration(context)

    def test_exact_validated_integration_passes(self):
        self.assertTrue(self.decision())

    def test_census_and_governance_evolution_passes_correspondence(self):
        self.write(CENSUS, "legitimate later census (ordinary census validation remains separate)\n")
        self.write("docs/ROADMAP.md", "superseding governance\n")
        head = self.commit("later host metadata")
        self.assertTrue(self.decision(replace(self.context, head=head)))

    def test_other_critical_inputs_and_handler_one_byte_fail(self):
        for path in (surface.GP005_HAL_PATH, GENERATED, "config/glyph/env.ini", "platformio.ini"):
            with self.subTest(path=path):
                self.git("switch", "--detach", "-q", self.merge)
                self.write(path, (self.root / path).read_text() + "x")
                head = self.commit("one byte critical drift")
                with self.assertRaises(ScopeValidationError):
                    self.decision(replace(self.context, head=head, committed_paths=self.context.committed_paths | {path}))

    def test_ordinary_unauthorized_hal_fails(self):
        with self.assertRaises(ScopeValidationError):
            self.decision(replace(self.context, head=self.base))

    def test_recreated_candidate_does_not_pass(self):
        self.git("switch", "--detach", "-q", self.base)
        self.git("cherry-pick", self.candidate)
        recreated = self.git("rev-parse", "HEAD")
        self.assertNotEqual(recreated, self.candidate)
        with self.assertRaises(ScopeValidationError):
            self.decision(replace(self.context, head=recreated))

    def test_moved_candidate_ref_fails(self):
        self.git("update-ref", f"refs/heads/{surface.GP005_BRANCH}", self.base)
        with self.assertRaises(ScopeValidationError):
            self.decision()

    def test_wrong_tree_or_parent_pin_fails(self):
        for name in ("GP005_TREE", "GP005_BASE"):
            with self.subTest(name=name), mock.patch.object(surface, name, "0" * 40), self.assertRaises(ScopeValidationError):
                self.decision()

    def test_no_pass_or_stale_authorization_fails(self):
        original = surface.git_output
        for field, value in (("status", "READY"), ("candidate_git_sha", "0" * 40),
                             ("candidate_base_configurator_sha", "0" * 40),
                             ("firmware_artifact_sha256", "0" * 64), ("hardware_evidence_gaps", ["gap"])):
            def altered(root, *args):
                result = original(root, *args)
                if args == ("show", f"{self.base}:{surface.QUEUE_PATH}"):
                    item = dict(self.item, **{field: value})
                    return "<!-- queue-state:start -->\n```json\n" + json.dumps({"items": [item]}) + "\n```"
                return result
            with self.subTest(field=field), mock.patch.object(surface, "git_output", side_effect=altered), self.assertRaises(ScopeValidationError):
                self.decision()

    def test_pass_for_another_candidate_or_artifact_fails(self):
        original = surface.git_output
        for field, value in (("candidate_git_sha", "0" * 40), ("firmware_artifact_sha256", "0" * 64),
                             ("result", "FAIL"), ("evidence_gaps", ["missing"])):
            def altered(root, *args):
                result = original(root, *args)
                if args[0] == "show" and args[1].endswith(":" + EVIDENCE):
                    return json.dumps(dict(self.evidence, **{field: value}))
                return result
            with self.subTest(field=field), mock.patch.object(surface, "git_output", side_effect=altered), self.assertRaises(ScopeValidationError):
                self.decision()

    def test_dirty_protected_source_fails(self):
        self.write(surface.GP005_HAL_PATH, "dirty\n")
        for staged in (False, True):
            if staged:
                self.git("add", surface.GP005_HAL_PATH)
            with self.subTest(staged=staged), self.assertRaises(ScopeValidationError):
                self.decision()  # Even a stale context cannot hide actual dirty input.

    def test_untracked_source_and_unknown_host_path_fail(self):
        for path in ("HAL/other.cpp", "docs/unknown-generated-input.hpp"):
            self.write(path, "unknown\n")
            with self.subTest(path=path), self.assertRaises(ScopeValidationError):
                self.decision()
            (self.root / path).unlink()

    def test_docs_tooling_branch_uses_ordinary_rules(self):
        context = replace(self.context, head=self.base, committed_paths=frozenset({"docs/readme.md", "tools/check.py"}))
        self.assertFalse(self.decision(context))


if __name__ == "__main__":
    main()
