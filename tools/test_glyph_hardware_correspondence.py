"""Real temporary-Git adversarial tests for the GP-VAL-015 shared model."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import glyph_hardware_correspondence as correspondence
import check_glyph_checker_census as census_check
import generate_glyph_checker_census as census_generator


HANDLER = "HAL/pico/src/comms/ConfiguratorBackend.cpp"
CENSUS = "docs/runtime_config/fixtures/glyph_checker_census.json"
DOC = "docs/AGENT_CONTEXT.md"
GENERATED = "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
STUB = "tools/fixtures/configurator_setconfig_host/include/config.pb.h"
AGGREGATE_RUNNER = "tools/run_glyph_runtime_config_validation.py"
REVISION_THREE_DOCS = (
    "AGENTS.md", "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md",
    "docs/agent_framework/SUPERVISOR_CONTRACT.md", "docs/agent_framework/SCHEDULED_TASKS.md",
    "docs/agent_framework/CYCLE_STATE_MACHINE.md", "docs/agent_framework/PROMPT_TEMPLATES.md",
    "docs/agent_framework/JUDGE_WATCHDOG_CONTRACT.md", "docs/agent_framework/RUNNER_BOUNDARY.md",
    "docs/agent_framework/WORK_ORDER_TEMPLATE.md",
)
X1_HOST_PATHS = (
    "docs/agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md",
    "docs/agent_framework/SUBAGENT_CONTRACTS.md",
    "docs/calibration/fixtures/gp_x1_002_hardware_evidence_2026-09-21.json",
    "docs/runtime_config/intakes/x1_normal_restoration_overlay_hardware_candidate.intake.json",
    "docs/runtime_config/source_authority_intake_workflow.md",
    "tools/check_glyph_gp_x1_002_candidate.py",
    "tools/check_glyph_runtime_config_source_sync.py",
    "tools/check_glyph_runtime_config_validation_health.py",
    "tools/check_glyph_source_owned_source_authority_intake.py",
    "tools/source_owned_source_authority_intake.py",
)
GP_VAL_028_HOST_PATHS = (
    "tools/fixtures/mode_selection_host/generated/LICENSE.nanopb.txt",
    "tools/fixtures/mode_selection_host/generated/README.md",
    "tools/fixtures/mode_selection_host/generated/config.pb.h",
    "tools/fixtures/mode_selection_host/generated/nanopb.library.json",
    "tools/fixtures/mode_selection_host/generated/provenance.json",
    "tools/test_glyph_config_010_capacity_provenance.py",
)
GP_PROV_014_HOST_PATHS = (
    "docs/runtime_config/README.md",
    "docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json",
    "docs/runtime_config/gp_prov_014_decoder_closure.md",
    "tools/check_glyph_gp_prov_014_decoder_closure.py",
    "tools/test_glyph_gp_prov_014_decoder_closure.py",
)
GP_CONFIG_012_HOST_PATHS = (
    "docs/runtime_config/fixtures/gp_config012_button_mask_characterization.json",
    "docs/runtime_config/gp_config_012_button_mask_characterization.md",
    "tools/check_glyph_gp_config012_button_mask_characterization.py",
    "tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt",
    "tools/fixtures/gp_config012_button_host/button_harness.cpp",
    "tools/fixtures/gp_config012_button_host/generated/config.pb.c",
    "tools/fixtures/gp_config012_button_host/generated/config.pb.h",
    "tools/fixtures/gp_config012_button_host/include/Arduino.h",
    "tools/fixtures/gp_config012_button_host/include/pico/stdlib.h",
    "tools/fixtures/gp_config012_button_host/nanopb/pb.h",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_common.c",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_common.h",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c",
    "tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h",
    "tools/fixtures/gp_config012_button_host/schema/config.options",
    "tools/fixtures/gp_config012_button_host/schema/config.proto",
)
GP_CONFIG_013_HOST_PATHS = (
    "docs/runtime_config/fixtures/gp_config013_usb_default_characterization.json",
    "docs/runtime_config/gp_config013_usb_default_characterization.md",
    "tools/check_glyph_gp_config013_usb_default_characterization.py",
    "tools/fixtures/gp_config013_usb_host/usb_harness.cpp",
)
GP_CONFIG_013_COUPLED_PATHS = (
    CENSUS,
    "docs/runtime_config/fixtures/runtime_config_validation_health.json",
    "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
    "docs/runtime_config/runtime_config_validation_health.md",
)


class CorrespondenceTests(unittest.TestCase):
    def test_gp_val034_literal_hosts_preserve_critical_precedence(self):
        paths = (
            'tools/glyph_c014_campaign_transition.py',
            'tools/test_glyph_c014_campaign_transition.py',
            'docs/runtime_config/fixtures/gp_val034_c014_transition.json',
            'docs/runtime_config/fixtures/gp_val034_accepted_transitions.json',
            'tools/check_glyph_custom_modifier_cache_characterization.py',
            'tools/check_glyph_gp_config014_modifier_capacity.py',
            'tools/fixtures/gp_config014_modifier_capacity/modifier_capacity_harness.cpp',
            'docs/runtime_config/fixtures/gp_config014_modifier_capacity.json',
            'docs/runtime_config/gp_config014_modifier_capacity.md',
            'docs/agent_framework/GP_CONFIG_014_HARDWARE_PROTOCOL.md',
            'docs/calibration/gp_config_014_hardware_result.md',
            'docs/calibration/fixtures/gp_config_014_hardware_evidence.json',
            'docs/calibration/fixtures/gp_kbd_001_keyboard_pipeline_characterization.json',
            'docs/calibration/gp_kbd_001_keyboard_pipeline_characterization.md',
            'tools/check_glyph_gp_kbd_001_keyboard_pipeline.py',
            'tools/fixtures/gp_kbd_001_keyboard_pipeline/include/TUKeyboard.hpp',
            'tools/fixtures/gp_kbd_001_keyboard_pipeline/main.cpp',
        )
        for path in paths:
            self.assertEqual(correspondence.classify_path(path), 'NON_BEHAVIORAL')
            for alias in (path + '.bak', path.swapcase(), path.replace('014', '014x'), path.replace('kbd_001', 'kbd_001x')):
                if alias == path:
                    continue
                with self.assertRaises(correspondence.CorrespondenceError):
                    correspondence.classify_path(alias)
        critical = {'include/modes/CustomControllerMode.hpp',
                    'src/modes/CustomControllerMode.cpp', 'platformio.ini'}
        with mock.patch.object(correspondence, 'NON_BEHAVIORAL_PATHS',
                               correspondence.NON_BEHAVIORAL_PATHS | critical):
            for path in critical:
                self.assertEqual(correspondence.classify_path(path), 'CRITICAL')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="glyph-correspondence-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic correspondence test")
        self.git("config", "user.email", "correspondence@example.invalid")
        self.git("config", "core.filemode", "true")
        for path in (HANDLER, CENSUS, DOC, GENERATED, "platformio.ini", "config/glyph/env.ini"):
            self.write(path, "base\n")
        self.base = self.commit("base")
        self.write(HANDLER, "tested handler\n")
        self.write(CENSUS, "candidate census\n")
        self.write(DOC, "candidate documentation\n")
        self.candidate = self.commit("candidate")

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def verify(self, **kwargs):
        return correspondence.verify_correspondence(
            self.root, self.candidate, self.base, integrated=True, **kwargs)

    def test_exact_candidate_and_later_metadata(self):
        self.verify()
        self.write(CENSUS, "regenerated census\n")
        self.write(DOC, "superseding governance\n")
        self.write(STUB, "host-only config shape\n")
        self.commit("metadata evolution")
        report = self.verify()
        self.assertEqual(set(report["target_paths"]), {CENSUS, DOC, STUB})
        self.assertTrue(report["normal_metadata_validation_required"])

    def test_revision_three_exact_contracts_and_critical_precedence(self):
        for path in REVISION_THREE_DOCS:
            self.write(path, "synthetic source-free contract\n")
        self.commit("bounded Revision-3 metadata")
        self.assertEqual(self.verify()["target_paths"], {p: "NON_BEHAVIORAL" for p in REVISION_THREE_DOCS})
        for path in REVISION_THREE_DOCS:
            with mock.patch.object(correspondence, "CORRESPONDENCE_CRITICAL_PATHS",
                                   correspondence.CORRESPONDENCE_CRITICAL_PATHS | {path}):
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")
            for alias in (path + ".bak", path.lower(), "other/" + path):
                if alias == path:
                    continue
                with self.subTest(alias=alias), self.assertRaises(correspondence.CorrespondenceError):
                    correspondence.classify_path(alias)

    def test_revision_three_contract_modes_are_never_metadata(self):
        for number, path in enumerate(REVISION_THREE_DOCS):
            for kind in ("executable", "symlink", "gitlink"):
                with self.subTest(path=path, kind=kind):
                    self.git("switch", "-q", "-c", f"r3-mode-{number}-{kind}", self.candidate)
                    if kind == "executable":
                        self.write(path, "metadata\n")
                        (self.root / path).chmod(0o755)
                        self.commit("executable metadata")
                    elif kind == "symlink":
                        location = self.root / path
                        location.parent.mkdir(parents=True, exist_ok=True)
                        location.symlink_to("README.md")
                        self.commit("symlink metadata")
                    else:
                        self.git("update-index", "--add", "--cacheinfo", f"160000,{self.candidate},{path}")
                        self.git("commit", "-q", "-m", "gitlink metadata")
                    with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
                        self.verify(check_worktree=False)

    def test_x1_candidate_style_delta_and_later_evidence_are_exactly_classified(self):
        evidence = X1_HOST_PATHS[2]
        candidate_paths = tuple(path for path in X1_HOST_PATHS if path != evidence)
        self.git("switch", "-q", "-c", "x1-candidate", self.base)
        self.write(GENERATED, "tested x1 runtime table\n")
        for path in candidate_paths:
            self.write(path, f"candidate host path: {path}\n")
        self.candidate = self.commit("exact x1 candidate-style delta")
        self.write(evidence, "immutable hardware evidence\n")
        self.commit("later x1 evidence")

        report = self.verify()
        self.assertEqual(report["candidate_paths"][GENERATED], "CRITICAL")
        self.assertEqual(
            {path: report["candidate_paths"][path] for path in candidate_paths},
            {path: "NON_BEHAVIORAL" for path in candidate_paths},
        )
        self.assertEqual(report["target_paths"], {evidence: "NON_BEHAVIORAL"})

    def test_x1_inventory_rejects_unsafe_git_entry_modes(self):
        path = X1_HOST_PATHS[0]
        self.git("switch", "-q", "-c", "x1-bad-modes", self.candidate)
        self.write(path, "ordinary metadata\n")
        (self.root / path).chmod(0o755)
        self.commit("executable x1 metadata")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
            self.verify()

    def test_exact_aggregate_runner_is_host_metadata_with_closed_aliases(self):
        self.write(AGGREGATE_RUNNER, "bounded host-only historical object transfer\n")
        self.commit("exact aggregate runner metadata")
        self.assertEqual(self.verify()["target_paths"], {AGGREGATE_RUNNER: "NON_BEHAVIORAL"})
        for path in (
            "tools/Run_glyph_runtime_config_validation.py",
            "tools/run_glyph_runtime_config_validation.py.bak",
            "tools/run_glyph_runtime_config_validation_extra.py",
            "tools/other/run_glyph_runtime_config_validation.py",
            "tools/unreviewed_host_validation.py",
        ):
            with self.subTest(path=path), self.assertRaisesRegex(correspondence.CorrespondenceError, "unclassified"):
                correspondence.classify_path(path)
        with mock.patch.object(correspondence, "CORRESPONDENCE_CRITICAL_PATHS",
                               correspondence.CORRESPONDENCE_CRITICAL_PATHS | {AGGREGATE_RUNNER}):
            self.assertEqual(correspondence.classify_path(AGGREGATE_RUNNER), "CRITICAL")
        self.assertEqual(correspondence.classify_path(HANDLER), "CRITICAL")
        self.write(HANDLER, "dirty critical input")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_exact_aggregate_runner_rejects_executable_symlink_and_gitlink(self):
        for kind in ("executable", "symlink", "gitlink"):
            with self.subTest(kind=kind):
                self.git("switch", "-q", "-c", "runner-" + kind, self.candidate)
                if kind == "executable":
                    self.write(AGGREGATE_RUNNER, "host runner\n")
                    (self.root / AGGREGATE_RUNNER).chmod(0o755)
                    self.commit("executable runner")
                elif kind == "symlink":
                    path = self.root / AGGREGATE_RUNNER
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to("check_glyph_runtime_config_validation_aggregate.py")
                    self.commit("symlink runner")
                else:
                    self.git("update-index", "--add", "--cacheinfo", f"160000,{self.candidate},{AGGREGATE_RUNNER}")
                    self.git("commit", "-q", "-m", "gitlink runner")
                with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
                    self.verify(check_worktree=False)

    def test_gp_config_012_candidate_style_delta_is_exactly_classified(self):
        self.git("switch", "-q", "-c", "gp012-candidate", self.base)
        for path in GP_CONFIG_012_HOST_PATHS:
            self.write(path, f"host-only candidate input: {path}\n")
        self.candidate = self.commit("exact GP-CONFIG-012 host candidate delta")
        report = self.verify()
        self.assertEqual(
            {path: report["candidate_paths"][path] for path in GP_CONFIG_012_HOST_PATHS},
            {path: "NON_BEHAVIORAL" for path in GP_CONFIG_012_HOST_PATHS},
        )
        self.assertEqual(len(GP_CONFIG_012_HOST_PATHS), 16)
        self.assertEqual(len(report["candidate_paths"]), 16)
        self.assertEqual(report["target_paths"], {})

    def test_gp_config_012_candidate_style_delta_rejects_unsafe_modes(self):
        path = GP_CONFIG_012_HOST_PATHS[0]
        for kind in ("executable", "symlink", "gitlink"):
            with self.subTest(kind=kind):
                self.git("switch", "-q", "-c", "gp012-bad-" + kind, self.candidate)
                if kind == "executable":
                    self.write(path, "host metadata\n")
                    (self.root / path).chmod(0o755)
                    self.commit("executable GP-CONFIG-012 metadata")
                elif kind == "symlink":
                    target = self.root / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to("config.json")
                    self.commit("symlink GP-CONFIG-012 metadata")
                else:
                    self.git("update-index", "--add", "--cacheinfo", f"160000,{self.candidate},{path}")
                    self.git("commit", "-q", "-m", "gitlink GP-CONFIG-012 metadata")
                with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
                    self.verify(check_worktree=False)

    def test_gp_config_013_whole_candidate_and_each_exact_path(self):
        self.git("switch", "-q", "-c", "gp013-candidate", self.base)
        paths = GP_CONFIG_013_HOST_PATHS + GP_CONFIG_013_COUPLED_PATHS
        self.assertEqual(len(paths), 8)
        for path in paths:
            self.write(path, f"source-free C013 input: {path}\n")
        self.candidate = self.commit("exact GP-CONFIG-013 candidate-style delta")
        report = self.verify()
        self.assertEqual(report["candidate_paths"], {path: "NON_BEHAVIORAL" for path in paths})
        self.assertEqual(report["target_paths"], {})
        for path in GP_CONFIG_013_HOST_PATHS:
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "NON_BEHAVIORAL")

    def test_gp_config_013_adjacent_unknown_and_critical_precedence(self):
        for path in GP_CONFIG_013_HOST_PATHS:
            for lookalike in (path + ".bak", path.upper(), path.replace("/", "/other/", 1)):
                with self.subTest(path=lookalike), self.assertRaisesRegex(
                    correspondence.CorrespondenceError, "unclassified"
                ):
                    correspondence.classify_path(lookalike)
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unclassified"):
            correspondence.classify_path("tools/fixtures/gp_config013_usb_host/extra.cpp")
        for path in GP_CONFIG_013_HOST_PATHS:
            with self.subTest(critical=path), mock.patch.object(
                correspondence, "CORRESPONDENCE_CRITICAL_PATHS",
                correspondence.CORRESPONDENCE_CRITICAL_PATHS | {path},
            ):
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")
        self.assertEqual(correspondence.classify_path(HANDLER), "CRITICAL")

    def test_gp_config_013_host_paths_reject_bad_git_modes_and_types(self):
        for index, path in enumerate(GP_CONFIG_013_HOST_PATHS):
            for kind in ("executable", "symlink", "gitlink"):
                with self.subTest(path=path, kind=kind):
                    self.git("switch", "-q", "-c", f"gp013-{index}-{kind}", self.candidate)
                    if kind == "executable":
                        self.write(path, "host metadata\n")
                        (self.root / path).chmod(0o755)
                        self.commit("executable GP-CONFIG-013 metadata")
                    elif kind == "symlink":
                        target = self.root / path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.symlink_to("unexpected")
                        self.commit("symlink GP-CONFIG-013 metadata")
                    else:
                        self.git("update-index", "--add", "--cacheinfo", f"160000,{self.candidate},{path}")
                        self.git("commit", "-q", "-m", "gitlink GP-CONFIG-013 metadata")
                    with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
                        self.verify(check_worktree=False)

    def test_changed_handler_fails(self):
        self.write(HANDLER, "tested handler!\n")
        self.commit("one byte source drift")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "critical input"):
            self.verify()

    def test_unchanged_at_candidate_generated_input_later_drift_fails(self):
        self.write(GENERATED, "different runtime table\n")
        self.commit("generated active table drift")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_build_dependency_input_later_drift_fails(self):
        self.write("platformio.ini", "another dependency\n")
        self.commit("build drift")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_critical_addition_fails(self):
        self.write("src/new.cpp", "new firmware")
        self.commit("critical addition")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_critical_deletion_fails(self):
        (self.root / GENERATED).unlink()
        self.commit("critical deletion")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_critical_mode_change_fails(self):
        (self.root / HANDLER).chmod(0o755)
        self.commit("critical mode drift")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_critical_rename_to_metadata_fails(self):
        (self.root / HANDLER).replace(self.root / DOC)
        self.commit("rename source into metadata")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_unknown_candidate_change_fails_even_if_exact_after_integration(self):
        self.git("switch", "-q", "-c", "unknown-candidate", self.base)
        self.write("docs/unknown.json", "not reviewed")
        self.candidate = self.commit("unknown candidate input")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unclassified"):
            self.verify()

    def test_unknown_later_path_fails(self):
        self.write("tools/fixtures/configurator_setconfig_host/include/another.hpp", "lookalike")
        self.commit("unknown host-lookalike addition")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unclassified"):
            self.verify()

    def test_symlink_metadata_fails(self):
        (self.root / DOC).unlink()
        (self.root / DOC).symlink_to("../" + HANDLER)
        self.commit("metadata symlink")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
            self.verify()

    def test_executable_metadata_fails(self):
        (self.root / DOC).chmod(0o755)
        self.commit("executable metadata")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
            self.verify()

    def test_gitlink_metadata_fails(self):
        self.git("update-index", "--cacheinfo", f"160000,{self.candidate},{DOC}")
        self.git("commit", "-q", "-m", "gitlink metadata")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
            self.verify(check_worktree=False)

    def test_staged_source_fails(self):
        self.write(HANDLER, "dirty")
        self.git("add", HANDLER)
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_unstaged_source_fails(self):
        self.write(GENERATED, "dirty generated source")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_assume_unchanged_cannot_hide_dirty_source(self):
        self.git("update-index", "--assume-unchanged", HANDLER)
        self.write(HANDLER, "hidden modified handler")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_skip_worktree_cannot_hide_dirty_source(self):
        self.git("update-index", "--skip-worktree", HANDLER)
        self.write(HANDLER, "hidden modified handler")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_preserved_stat_and_size_cannot_hide_dirty_source(self):
        location = self.root / HANDLER
        previous = location.stat()
        self.write(HANDLER, "Tested handler\n")
        os.utime(location, ns=(previous.st_atime_ns, previous.st_mtime_ns))
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_core_filemode_false_cannot_hide_critical_mode_change(self):
        self.git("config", "core.fileMode", "false")
        (self.root / HANDLER).chmod(0o755)
        self.assertEqual(self.git("diff", "--name-only"), "")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_symlink_parent_cannot_hide_critical_input(self):
        self.git("update-index", "--skip-worktree", HANDLER)
        parent = (self.root / HANDLER).parent
        moved = self.root / "outside"
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "symlinked"):
            self.verify()

    def test_untracked_source_fails(self):
        self.write("include/new.hpp", "new untracked input")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_ignored_untracked_source_fails_without_sweeping_pio_cache(self):
        (self.root / ".git/info/exclude").write_text("src/ignored.cpp\n.pio/\n")
        self.write(".pio/libdeps/huge-cache.hpp", "ignored dependency cache")
        self.verify()
        self.write("src/ignored.cpp", "compiler still consumes this source")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "dirty critical"):
            self.verify()

    def test_untracked_unknown_fails(self):
        self.write("docs/new.md", "unreviewed")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unclassified"):
            self.verify()

    def test_dirty_regular_metadata_allowed_but_symlink_and_index_mode_fail(self):
        self.write(DOC, "dirty metadata")
        self.assertEqual(self.verify()["dirty_paths"], {DOC: "NON_BEHAVIORAL"})
        (self.root / DOC).chmod(0o755)
        self.git("add", DOC)
        (self.root / DOC).chmod(0o644)
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsupported"):
            self.verify()

    def test_dirty_metadata_symlink_fails(self):
        (self.root / DOC).unlink()
        (self.root / DOC).symlink_to("../" + HANDLER)
        with self.assertRaises(correspondence.CorrespondenceError):
            self.verify()

    def test_wrong_parent_and_recreated_candidate_fail(self):
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "parent"):
            correspondence.verify_correspondence(self.root, self.candidate, self.candidate, integrated=True)
        self.git("switch", "-q", "-c", "recreated", self.base)
        self.write(HANDLER, "tested handler\n")
        self.write(CENSUS, "candidate census\n")
        self.write(DOC, "candidate documentation\n")
        recreated = self.commit("recreated candidate with identical tree")
        self.assertNotEqual(recreated, self.candidate)
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "ancestry"):
            self.verify()

    def test_preintegration_clean_base_and_docs_pass_source_drift_fails(self):
        self.git("switch", "-q", "-c", "canonical", self.base)
        self.write(DOC, "canonical governance")
        self.commit("canonical metadata")
        correspondence.verify_correspondence(self.root, self.candidate, self.base, integrated=False)
        self.write("config/glyph/env.ini", "new build config")
        self.commit("canonical build drift")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "critical input"):
            correspondence.verify_correspondence(self.root, self.candidate, self.base, integrated=False)

    def test_real_merge_with_superseding_census_passes(self):
        self.git("switch", "-q", "-c", "canonical", self.base)
        self.write("docs/CURRENT_STATE.md", "canonical metadata")
        self.commit("canonical")
        self.git("merge", "--no-ff", self.candidate, "-m", "exact candidate integration")
        self.write(CENSUS, "later regenerated census")
        self.commit("regenerated inventory")
        self.verify()

    def test_normal_census_validator_remains_required_and_rejects_bad_metadata(self):
        valid = census_generator.rendered(census_generator.generate(self.root))
        self.write(CENSUS, valid)
        self.commit("valid regenerated census")
        self.verify()
        with mock.patch.object(census_check, "ARTIFACT", self.root / CENSUS), \
             mock.patch.object(census_check, "generate", side_effect=lambda: census_generator.generate(self.root)), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(census_check.main(), 0)
            self.write(CENSUS, '{"schema_version": 1, "entries": [], "invalid": true}\n')
            self.commit("invalid metadata still outside firmware")
            self.verify()
            self.assertEqual(census_check.main(), 1)

    def test_newline_git_path_is_not_split_into_safe_paths(self):
        self.write("docs/AGENT_CONTEXT.md\nextra", "unsafe newline path")
        self.commit("unsafe path")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unsafe"):
            self.verify()


class ClassificationTests(unittest.TestCase):
    def test_campaign_receipt_and_source_precedence(self):
        receipt = "docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json"
        self.assertEqual(correspondence.classify_path(receipt), "NON_BEHAVIORAL")
        for alias in (receipt + ".bak", receipt.swapcase(), "./" + receipt,
                      receipt.replace("current_arguments", "future_arguments")):
            with self.subTest(alias=alias), self.assertRaises(correspondence.CorrespondenceError):
                correspondence.classify_path(alias)
        for source in (HANDLER, "include/core/config_button_validation.hpp",
                       "src/core/config_button_validation.cpp"):
            with mock.patch.object(correspondence, "NON_BEHAVIORAL_PATHS",
                                   correspondence.NON_BEHAVIORAL_PATHS | {source}):
                self.assertEqual(correspondence.classify_path(source), "CRITICAL")

    def test_gp_config_012_exact_host_inventory(self):
        self.assertEqual(len(GP_CONFIG_012_HOST_PATHS), 16)
        for path in GP_CONFIG_012_HOST_PATHS:
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "NON_BEHAVIORAL")

    def test_gp_config_012_inventory_lookalikes_and_critical_paths_fail_closed(self):
        aliases = []
        for path in GP_CONFIG_012_HOST_PATHS:
            aliases.extend((path + ".bak", path.swapcase(), "prefix/" + path, "./" + path))
        for path in aliases:
            with self.subTest(path=path), self.assertRaises(correspondence.CorrespondenceError):
                correspondence.classify_path(path)
        for path in ("HAL/pico/src/comms/ConfiguratorBackend.cpp", "platformio.ini"):
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")
        with self.assertRaisesRegex(correspondence.CorrespondenceError, "unclassified"):
            correspondence.classify_path("tools/fixtures/gp_config012_button_host/generated/config.pb.c.bak")
        with mock.patch.object(correspondence, "NON_BEHAVIORAL_PATHS",
                               correspondence.NON_BEHAVIORAL_PATHS | {"platformio.ini"}):
            self.assertEqual(correspondence.classify_path("platformio.ini"), "CRITICAL")

    def test_exact_x1_host_inventory(self):
        self.assertEqual(len(X1_HOST_PATHS), 10)
        for path in X1_HOST_PATHS:
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "NON_BEHAVIORAL")

    def test_x1_inventory_lookalikes_fail_closed(self):
        aliases = []
        for path in X1_HOST_PATHS:
            aliases.extend((path + ".bak", path.swapcase(), "prefix/" + path, "./" + path))
        aliases.extend((
            "docs/agent_framework/../agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md",
            "docs//agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md",
            "docs\\agent_framework\\GP_X1_002_HARDWARE_PROTOCOL.md",
        ))
        for path in aliases:
            with self.subTest(path=path), self.assertRaises(correspondence.CorrespondenceError):
                correspondence.classify_path(path)

    def test_conservative_source_build_and_generated_categories(self):
        for path in (HANDLER, GENERATED, "hal/new.cpp", "include/new.hpp", "lib/new.cpp",
                     "config/glyph/common/include/example.hpp", "config/glyph/env.ini",
                     "builder_scripts/arduino_pico.py", "scripts/pio-local.sh", "glyph_nuker",
                     "platformio.ini", ".github/workflows/build.yml", "config/glyph/.github/workflows/build.yml",
                     ".gitmodules", ".gitattributes", "boards/pico.json", "src/harmless.json"):
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")

    def test_unknown_paths_aliases_and_prefix_tricks_fail(self):
        for path in ("docs/unknown.json", "tools/new.py", "docs/src/foo.cpp", "src2/file.cpp",
                     "docs/AGENT_CONTEXT.md.bak", "DOCS/AGENT_CONTEXT.md", "./" + DOC,
                     "docs//AGENT_CONTEXT.md", "docs/../" + DOC, "/" + DOC, "C:/" + DOC,
                     "docs\\AGENT_CONTEXT.md", DOC + "/", DOC + "\t", ""):
            with self.subTest(path=path), self.assertRaises(correspondence.CorrespondenceError):
                correspondence.classify_path(path)

    def test_gp_val_028_exact_host_paths_only(self):
        for path in GP_VAL_028_HOST_PATHS:
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "NON_BEHAVIORAL")
        for path in (
            "tools/fixtures/mode_selection_host/generated/config.pb.c",
            "tools/fixtures/mode_selection_host/generated/config.pb.h.bak",
            "tools/test_glyph_config_010_capacity_provenance.py.bak",
        ):
            with self.subTest(path=path), self.assertRaisesRegex(
                    correspondence.CorrespondenceError, "unclassified"):
                correspondence.classify_path(path)
        for path in ("src/core/mode_selection.cpp", "config/glyph/env.ini", "platformio.ini"):
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")

    def test_gp_prov_014_exact_host_paths_only(self):
        for path in GP_PROV_014_HOST_PATHS:
            with self.subTest(path=path):
                self.assertEqual(correspondence.classify_path(path), "NON_BEHAVIORAL")
            for alias in (path + ".bak", path.swapcase(), "prefix/" + path, "./" + path):
                with self.subTest(path=alias), self.assertRaises(correspondence.CorrespondenceError):
                    correspondence.classify_path(alias)
        self.assertEqual(correspondence.classify_path("src/core/mode_selection.cpp"), "CRITICAL")

    def test_gp_val043_literal_paths_and_critical_precedence(self):
        paths = (
            'tools/glyph_c020_abi_repair_transition.py',
            'docs/runtime_config/fixtures/gp_val043_c020_abi_repair.json',
            'docs/runtime_config/fixtures/gp_val043_accepted_transitions.json',
            'tools/fixtures/gp_config020_button_validation/abi_probe.cpp',
            'docs/runtime_config/gp_config020_abi_repair.md',
            'docs/runtime_config/fixtures/gp_config020_abi_repair.json',
        )
        for path in paths:
            self.assertEqual(correspondence.classify_path(path), 'NON_BEHAVIORAL')
            for alias in (path + '.bak', path.swapcase(), 'prefix/' + path, './' + path):
                with self.subTest(path=alias), self.assertRaises(correspondence.CorrespondenceError):
                    correspondence.classify_path(alias)
        for path in ('HAL/pico/src/comms/ConfiguratorBackend.cpp',
                     'include/core/config_button_validation.hpp', 'src/core/config_button_validation.cpp'):
            self.assertEqual(correspondence.classify_path(path), 'CRITICAL')

    def test_critical_precedence_over_inventory(self):
        with mock.patch.object(correspondence, "NON_BEHAVIORAL_PATHS", {HANDLER, GENERATED, "platformio.ini"}):
            for path in correspondence.NON_BEHAVIORAL_PATHS:
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")


class PersistentOwnerDirectionTests(unittest.TestCase):
    """The new literal record cannot rewrite prior direction or source authority."""
    def setUp(self):
        import glyph_c020_abi_repair_transition as campaign
        self.campaign = campaign
        self.temp = tempfile.TemporaryDirectory(prefix="glyph-owner-batch-")
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / "repo").resolve()
        self.command("clone", "--shared", "--no-checkout", str(Path(__file__).resolve().parents[1]), str(self.root), cwd=Path(self.temp.name))
        self.command("switch", "--detach", campaign.PERSISTENT_BATCH_AUTHORITY)

    def command(self, *args, cwd=None):
        result = subprocess.run(["git", *args], cwd=cwd or self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def scope(self):
        return self.campaign._owner_direction_scope(self.root, self.command("rev-parse", "HEAD"), {self.campaign.OWNER_DIRECTION})

    def test_exact_D2_and_historical_D1(self):
        self.assertEqual(self.scope(), self.campaign.REVISION_THREE_PATHS | self.campaign.PERSISTENT_BATCH_PATHS | {self.campaign.OWNER_DIRECTION})
        self.command("switch", "--detach", self.campaign.REVISION_THREE_AUTHORITY)
        self.assertEqual(self.scope(), self.campaign.REVISION_THREE_PATHS | {self.campaign.OWNER_DIRECTION})

    def test_no_source_or_evidence_or_prefix_authority(self):
        scope = self.scope()
        for path in self.campaign.PERSISTENT_BATCH_PATHS:
            self.assertIn(path, scope)
            for alias in (path + ".bak", path.swapcase(), "prefix/" + path):
                self.assertNotIn(alias, scope)
        for path in (HANDLER, "include/modes/CustomControllerMode.hpp", "src/modes/CustomControllerMode.cpp", "platformio.ini", self.campaign.PROTOCOL, self.campaign.EVIDENCE, self.campaign.RESULT, self.campaign.TRANSITIONS):
            self.assertNotIn(path, scope)

    def test_live_and_index_substitution(self):
        path = self.root / self.campaign.OWNER_DIRECTION
        path.write_bytes(path.read_bytes() + b"unreviewed\n")
        with self.assertRaises(correspondence.CorrespondenceError):
            self.scope()
        self.command("add", self.campaign.OWNER_DIRECTION)
        path.write_bytes(self.campaign.raw_bytes(self.root, self.campaign.PERSISTENT_BATCH_AUTHORITY, self.campaign.OWNER_DIRECTION))
        with self.assertRaises(correspondence.CorrespondenceError):
            self.scope()

    def test_mode_and_symlink_substitution(self):
        path = self.root / self.campaign.OWNER_DIRECTION
        path.chmod(0o755)
        with self.assertRaises(correspondence.CorrespondenceError):
            self.scope()
        path.chmod(0o644)
        data = path.read_bytes()
        target = Path(self.temp.name) / "external-direction.md"
        target.write_bytes(data)
        path.unlink()
        path.symlink_to(target)
        with self.assertRaises(correspondence.CorrespondenceError):
            self.scope()

    def test_parent_hash_and_earlier_direction_reseal(self):
        with mock.patch.object(self.campaign, "PERSISTENT_BATCH_PARENT", self.campaign.REVISION_THREE_AUTHORITY):
            with self.assertRaises(correspondence.CorrespondenceError):
                self.scope()
        with mock.patch.object(self.campaign, "PERSISTENT_BATCH_DIRECTION_SHA256", "0" * 64):
            with self.assertRaises(correspondence.CorrespondenceError):
                self.scope()
        original = self.campaign.raw_bytes
        bad = original(self.root, self.campaign.PERSISTENT_BATCH_AUTHORITY, self.campaign.OWNER_DIRECTION).replace(b"GLYPH-UD-028", b"GLYPH-UD-000", 1)
        def changed(root, ref, path):
            return bad if ref == self.campaign.PERSISTENT_BATCH_AUTHORITY and path == self.campaign.OWNER_DIRECTION else original(root, ref, path)
        import hashlib
        with mock.patch.object(self.campaign, "raw_bytes", side_effect=changed), mock.patch.object(self.campaign, "PERSISTENT_BATCH_DIRECTION_SHA256", hashlib.sha256(bad).hexdigest()):
            with self.assertRaises(correspondence.CorrespondenceError):
                self.scope()

    def test_extra_record_path_and_record_mode(self):
        original = self.campaign._git
        def changed(root, *args):
            if args[:2] == ("diff", "--name-only") and args[-1] == self.campaign.PERSISTENT_BATCH_AUTHORITY:
                return (self.campaign.OWNER_DIRECTION + "\n" + self.campaign.EVIDENCE + "\n").encode()
            return original(root, *args)
        with mock.patch.object(self.campaign, "_git", side_effect=changed):
            with self.assertRaises(correspondence.CorrespondenceError):
                self.scope()
        original_tree = self.campaign._tree
        def changed_tree(root, ref):
            value = dict(original_tree(root, ref))
            if ref == self.campaign.PERSISTENT_BATCH_AUTHORITY:
                entry = value[self.campaign.OWNER_DIRECTION]
                value[self.campaign.OWNER_DIRECTION] = ("100755", entry[1], entry[2])
            return value
        with mock.patch.object(self.campaign, "_tree", side_effect=changed_tree):
            with self.assertRaises(correspondence.CorrespondenceError):
                self.scope()


if __name__ == "__main__":
    unittest.main()
