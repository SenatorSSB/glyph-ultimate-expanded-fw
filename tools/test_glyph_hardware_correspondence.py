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


class CorrespondenceTests(unittest.TestCase):
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

    def test_critical_precedence_over_inventory(self):
        with mock.patch.object(correspondence, "NON_BEHAVIORAL_PATHS", {HANDLER, GENERATED, "platformio.ini"}):
            for path in correspondence.NON_BEHAVIORAL_PATHS:
                self.assertEqual(correspondence.classify_path(path), "CRITICAL")


if __name__ == "__main__":
    unittest.main()
