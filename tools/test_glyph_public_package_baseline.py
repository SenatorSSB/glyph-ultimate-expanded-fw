#!/usr/bin/env python3
"""Current package closure remains exact in a new one-commit repository."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import glyph_ci_package_scope as scope

ROOT = Path(__file__).resolve().parents[1]


class PublicPackageBaseline(unittest.TestCase):
    def git(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *arguments], cwd=self.root, env=self.env,
                              text=True, capture_output=True, check=check)

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="glyph-public-package-contract-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        # Build a new repository from current source bytes, never a clone or
        # copied object store. No fetch command is used anywhere in this test.
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
        self.receipt = json.loads((ROOT / scope.PUBLIC_BASELINE).read_text())
        self.entries = json.loads((ROOT / self.receipt["manifest_path"]).read_text())["entries"]
        self.protected = self.receipt["protected_inputs"]
        for record in self.protected:
            destination = self.root / record["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / record["path"], destination)
            destination.chmod(0o755 if record["git_mode"] == "100755" else 0o644)
        self.receipt_path = self.root / scope.PUBLIC_BASELINE
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / scope.PUBLIC_BASELINE, self.receipt_path)
        self.manifest_path = self.root / self.receipt["manifest_path"]
        shutil.copyfile(ROOT / self.receipt["manifest_path"], self.manifest_path)
        self.git("init", "-q", "-b", "public-current")
        self.git("add", ".")
        self.git("-c", "user.name=Public contract test", "-c", "user.email=validation.invalid",
                 "commit", "-qm", "One current source root")
        self.source_path = self.root / self.protected[0]["path"]

    def assert_contract_rejected(self):
        with self.assertRaises(ValueError):
            scope.public_contract(self.root)

    def test_fresh_root_accepts_exact_current_sources_without_old_history(self):
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "1")
        self.assertEqual(self.git("show", "-s", "--format=%P", "HEAD").stdout.strip(), "")
        self.assertEqual(self.git("remote", "-v").stdout, "")
        self.assertFalse((self.root / ".git/objects/info/alternates").exists())
        self.assertFalse((self.root / ".git/objects/info/http-alternates").exists())
        self.assertNotEqual(self.git("cat-file", "-e", scope.PACKAGE_BASE + "^{commit}", check=False).returncode, 0)
        self.assertNotEqual(self.git("cat-file", "-e", scope.C023_DONE + "^{commit}", check=False).returncode, 0)
        self.assertEqual(len(self.git("ls-files", "-z").stdout.split("\0")) - 1,
                         len(self.protected) + 2)
        self.assertEqual(scope.public_contract(self.root), self.receipt)
        scope.verify_manifest_coverage(self.root, self.entries)
        self.assertTrue(scope.package_lineage(self.root))
        self.assertFalse(scope.current_package_comparison(self.root)["new_hardware_acceptance"])

    def test_changed_protected_bytes_fail(self):
        self.source_path.write_bytes(self.source_path.read_bytes() + b"\n// changed contract input\n")
        self.assert_contract_rejected()

    def test_changed_index_bytes_with_restored_worktree_fail(self):
        original = self.source_path.read_bytes()
        self.source_path.write_bytes(original + b"\n// staged drift\n")
        self.git("add", self.protected[0]["path"])
        self.source_path.write_bytes(original)
        self.assert_contract_rejected()

    def test_manifest_downgrade_and_missing_manifest_fail(self):
        original = self.manifest_path.read_bytes()
        value = json.loads(original)
        value["schema_version"] = 4
        self.manifest_path.write_text(json.dumps(value))
        self.assert_contract_rejected()
        self.manifest_path.unlink()
        self.assert_contract_rejected()

    def test_missing_protected_file_fails(self):
        self.source_path.unlink()
        self.assert_contract_rejected()

    def test_changed_disk_mode_fails(self):
        self.source_path.chmod(0o755 if self.protected[0]["git_mode"] == "100644" else 0o644)
        self.assert_contract_rejected()

    def test_changed_index_mode_fails(self):
        self.git("update-index", "--chmod=+x" if self.protected[0]["git_mode"] == "100644" else "--chmod=-x",
                 self.protected[0]["path"])
        self.assert_contract_rejected()

    def test_unexpected_untracked_protected_path_fails(self):
        extra = self.root / "src/g2b_unexpected_contract_input.cpp"
        extra.write_text("// unexpected source\n")
        self.assert_contract_rejected()

    def test_unexpected_tracked_protected_path_fails(self):
        extra = self.root / "src/g2b_unexpected_contract_input.cpp"
        extra.write_text("// unexpected source\n")
        self.git("add", extra.relative_to(self.root).as_posix())
        self.assert_contract_rejected()

    def test_protected_file_symlink_fails(self):
        target = self.root / self.protected[1]["path"]
        self.source_path.unlink()
        self.source_path.symlink_to(target)
        self.assert_contract_rejected()

    def test_protected_directory_symlink_fails(self):
        directory = self.root / scope.PROTECTED_PREFIXES[0]
        retained = self.root / "retained-directory"
        directory.rename(retained)
        directory.symlink_to(retained, target_is_directory=True)
        self.assert_contract_rejected()

    def test_missing_receipt_cannot_authorize_current_contract(self):
        self.receipt_path.unlink()
        self.assert_contract_rejected()
        self.assertFalse(scope.package_lineage(self.root))

    def test_tampered_receipt_fails(self):
        value = copy.deepcopy(self.receipt)
        value["protected_inputs"][0]["sha256"] = "0" * 64
        self.receipt_path.write_text(json.dumps(value))
        self.assert_contract_rejected()

    def test_symlink_receipt_fails(self):
        target = self.root / "receipt-copy.json"
        self.receipt_path.rename(target)
        self.receipt_path.symlink_to(target)
        self.assert_contract_rejected()

    def test_manifest_command_classification_and_dependency_drift_fail(self):
        mutations = (
            ("command", lambda row: row["command"].append("--different-argument")),
            ("classification", lambda row: row.update(applicability="historical_only")),
            ("dependency", lambda row: row["source_dependencies"].append("docs/unreviewed-dependency.md")),
            ("load-bearing", lambda row: row.update(load_bearing=False)),
            ("branch-policy", lambda row: row.update(branch_policy="named_evidence_branch")),
        )
        for label, mutate in mutations:
            with self.subTest(change=label):
                alternate = copy.deepcopy(self.entries)
                row = next(item for item in alternate if item["applicability"] == "current")
                mutate(row)
                with self.assertRaises(ValueError):
                    scope.verify_manifest_coverage(self.root, alternate)
        for label, alternate in (("missing-entry", self.entries[:-1]),
                                 ("added-entry", self.entries + [copy.deepcopy(self.entries[0])])):
            with self.subTest(change=label):
                with self.assertRaises(ValueError):
                    scope.verify_manifest_coverage(self.root, alternate)


if __name__ == "__main__":
    unittest.main()
