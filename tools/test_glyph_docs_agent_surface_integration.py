#!/usr/bin/env python3
"""Exact GP-CONFIG-005 integration applicability against the historical Git merge."""

from dataclasses import replace
from pathlib import Path
from unittest import TestCase, main, mock
import json

import check_glyph_docs_agent_surface as surface
from glyph_checker_context import CheckerContext, ScopeValidationError


BASE = "0fd9e30f158fa41b06ea193c32a854a36e8cab31"
MERGE = "55eaec9bde837e149647627f67e2bf7c34135cca"


class ExactIntegrationTests(TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.context = CheckerContext(
            self.root, "arbitrary-integration-name", MERGE, "origin/configurator", BASE,
            None, BASE, True, frozenset({surface.GP005_HAL_PATH}),
            frozenset(), frozenset(),
        )
        self.original_git = surface.git_output

    def git(self, root, *args):
        if args == ("rev-parse", "origin/configurator"):
            return BASE
        return self.original_git(root, *args)

    def decision(self, context=None, alteration=None):
        def git(root, *args):
            result = self.git(root, *args)
            return alteration(args, result) if alteration else result
        context = context or self.context
        with mock.patch.object(surface, "git_output", side_effect=git):
            surface.validate_surface_scope(context)
            return surface.exact_gp005_integration(context)

    def test_exact_validated_integration_passes(self):
        self.assertTrue(self.decision())

    def test_ordinary_unauthorized_hal_fails(self):
        with self.assertRaises(ScopeValidationError):
            self.decision(replace(self.context, head=BASE))

    def test_different_hal_entry_fails(self):
        def alter(args, result):
            if args[:2] == ("ls-tree", MERGE) and args[-1] == surface.GP005_HAL_PATH:
                return result.replace("blob ", "blob changed-")
            return result
        with self.assertRaises(ScopeValidationError):
            self.decision(alteration=alter)

    def test_no_pass_or_stale_candidate_or_wrong_artifact_fails(self):
        for field, value in (("status", "READY"), ("candidate_git_sha", "0" * 40),
                             ("firmware_artifact_sha256", "0" * 64)):
            with self.subTest(field=field):
                def alter(args, result):
                    if args[0] == "show" and args[1].endswith(":" + surface.QUEUE_PATH):
                        return result.replace(f'"{field}": "' + ("HARDWARE_VALIDATED" if field == "status" else getattr(surface, "GP005_CANDIDATE" if field == "candidate_git_sha" else "GP005_ARTIFACT")) + '"', f'"{field}": "{value}"', 1)
                    return result
                with self.assertRaises(ScopeValidationError):
                    self.decision(alteration=alter)
        def wrong_evidence(args, result):
            if args[0] == "show" and args[1].endswith("gp_config_005_hardware_evidence_2026-09-17.json"):
                data = json.loads(result); data["result"] = "FAIL"; return json.dumps(data)
            return result
        with self.assertRaises(ScopeValidationError):
            self.decision(alteration=wrong_evidence)

    def test_mixed_or_dirty_source_fails(self):
        for context in (
            replace(self.context, committed_paths=frozenset({surface.GP005_HAL_PATH, "HAL/other.cpp"})),
            replace(self.context, committed_paths=frozenset({surface.GP005_HAL_PATH, "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"})),
            replace(self.context, staged_paths=frozenset({surface.GP005_HAL_PATH})),
            replace(self.context, unstaged_paths=frozenset({surface.GP005_HAL_PATH})),
        ):
            with self.subTest(context=context):
                with self.assertRaises(ScopeValidationError):
                    self.decision(context)

    def test_docs_tooling_branch_uses_ordinary_rules(self):
        context = replace(self.context, head=BASE, committed_paths=frozenset({"docs/readme.md", "tools/check.py"}))
        self.assertFalse(self.decision(context))


if __name__ == "__main__":
    main()
