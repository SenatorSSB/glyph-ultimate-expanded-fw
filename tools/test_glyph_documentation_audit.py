#!/usr/bin/env python3
"""Synthetic Git-tree, strict JSON, determinism and privacy-output controls."""
import contextlib
import copy
import gzip
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import audit_glyph_documentation as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "docs").mkdir()
        (self.repo / "tools").mkdir()
        (self.repo / "docs/a.md").write_text("# Sample\n[link](b.md#one)\nlocal_backups/example\n/Users/synthetic/capture.txt\nsynthetic@example.invalid\n")
        (self.repo / "docs/b.md").write_text("# One\n")
        (self.repo / "docs/duplicate.md").write_bytes((self.repo / "docs/b.md").read_bytes())
        (self.repo / "tools/helper.py").write_text("raise RuntimeError('must never execute')\n")
        (self.repo / "tools/sample.py").write_text("import helper\np = f'docs/{name}.md'\n")
        (self.repo / "invalid.json").write_text('{"a":1,"a":2}')
        (self.repo / "sample.gz").write_bytes(gzip.compress(b"synthetic@example.invalid", mtime=0))
        (self.repo / "binary.bin").write_bytes(b"\0\xff")
        (self.repo / "link").symlink_to("/nonexistent/synthetic")
        self.git("add", ".")
        env = dict(os.environ, GIT_AUTHOR_NAME="Synthetic", GIT_AUTHOR_EMAIL="synthetic@example.invalid",
                   GIT_COMMITTER_NAME="Synthetic", GIT_COMMITTER_EMAIL="synthetic@example.invalid")
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "synthetic fixture"], env=env, check=True)
        self.sha = self.git("rev-parse", "HEAD").decode().strip()
        self.inv = audit.inventory(self.repo, self.sha)

    def git(self, *args):
        return audit.git(self.repo, *args)

    def test_exact_tree_and_modes(self):
        self.assertTrue(audit.validate(self.repo, self.sha, self.inv))
        actual = self.git("ls-tree", "-r", "-t", "--name-only", "-z", self.sha).split(b"\0")[:-1]
        self.assertEqual({os.fsdecode(p) for p in actual}, {r["path"] for r in self.inv["records"]})
        records = {r["path"]: r for r in self.inv["records"]}
        self.assertEqual(records["link"]["mode"], "120000")
        self.assertEqual(records["docs"]["type"], "tree")
        self.assertEqual(records["docs/b.md"]["oid"], records["docs/duplicate.md"]["oid"])
        self.assertIn("docs/duplicate.md", records)

    def test_reject_missing_duplicate_changed_identity(self):
        for change in ("missing", "duplicate", "oid", "mode", "size", "order"):
            with self.subTest(change=change):
                value = copy.deepcopy(self.inv)
                rows = value["records"]
                if change == "missing":
                    rows.pop()
                elif change == "duplicate":
                    rows[-1] = copy.deepcopy(rows[0])
                elif change == "order":
                    rows.reverse()
                else:
                    rows[0][change] = "0" * 40 if change == "oid" else "bad"
                with self.assertRaises(ValueError):
                    audit.validate(self.repo, self.sha, value)

    def test_strict_json(self):
        for raw in ('{"a":1,"a":2}', '{"a":{"b":1,"b":2}}', '{"n":NaN}'):
            with self.assertRaises(ValueError):
                audit.strict_json(raw)
        self.assertEqual(audit.strict_json(audit.render(self.inv)), self.inv)

    def test_scan_determinism_and_candidates(self):
        first = audit.scan(self.repo, self.inv)
        second = audit.scan(self.repo, audit.inventory(self.repo, self.sha))
        self.assertEqual(audit.render(first), audit.render(second))
        self.assertTrue(any(r["target"] == "docs/b.md" and r["anchor"] == "one"
                            for r in first["dependencies"] if r["kind"] == "markdown_link"))
        self.assertTrue(any(r["kind"] == "constructed_expression" and r["target"] is None for r in first["dependencies"]))
        self.assertTrue(any(r["kind"] == "python_import" and r["target"] == "tools/helper.py" for r in first["dependencies"]))
        self.assertTrue(any(r.get("json_status") == "INVALID_OR_DUPLICATE_KEYS" for r in first["scan_coverage"]))
        self.assertTrue(any(r["path"] == "sample.gz!gzip" for r in first["privacy_candidates"]))
        self.assertTrue(all(r["review"] == "UNREVIEWED" for r in first["sections"]))

    def test_stdout_privacy_and_private_permissions(self):
        out = self.root / "private"
        stdout = io.StringIO()
        with patch("sys.argv", ["audit", "--repo", str(self.repo), "--baseline", self.sha, "--output", str(out)]), contextlib.redirect_stdout(stdout):
            self.assertEqual(audit.main(), 0)
        for forbidden in ("synthetic@", "/Users/", str(out), "capture.txt"):
            self.assertNotIn(forbidden, stdout.getvalue())
        self.assertEqual(out.stat().st_mode & 0o777, 0o700)
        for path in out.iterdir():
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            audit.strict_json(path.read_bytes())
        with self.assertRaises(FileExistsError):
            audit.write_private(out / "inventory.json", {})

    def test_output_checkout_and_symlink_rejected(self):
        for out in (self.repo / "bad", self.root / "symlink"):
            if out.name == "symlink":
                out.symlink_to(self.repo / "other")
            with patch("sys.argv", ["audit", "--repo", str(self.repo), "--baseline", self.sha, "--output", str(out)]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main(), 1)

    def test_pinned_baseline_ignores_dirty_files(self):
        (self.repo / "docs/a.md").write_text("changed unrelated checkout")
        (self.repo / "untracked").write_text("untracked")
        self.assertEqual(audit.render(self.inv), audit.render(audit.inventory(self.repo, self.sha)))
        with self.assertRaises(ValueError):
            audit.inventory(self.repo, "HEAD")

    def test_bounded_gzip(self):
        raw = gzip.compress(b"x" * 4096, mtime=0)
        (self.repo / "large.gz").write_bytes(raw)
        self.git("add", "large.gz")
        # Exercise bounded expansion without another commit by passing an exact blob record.
        oid = self.git("hash-object", "large.gz").decode().strip()
        inv = dict(self.inv, records=[dict(path="large.gz", oid=oid, mode="100644", type="blob", size=len(raw))])
        with patch.object(audit, "LIMIT", 128):
            result = audit.scan(self.repo, inv)
        self.assertTrue(any(r["status"] == "OVERSIZE_UNREVIEWED" for r in result["scan_coverage"]))


if __name__ == "__main__":
    unittest.main()
