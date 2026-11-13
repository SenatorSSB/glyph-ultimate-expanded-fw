"""Exercise the workflow classifier on real Git tree and mode changes."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from glyph_ci_build_inputs import needs_build


class FirmwareInputs(unittest.TestCase):
    def test_changes(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }):
            previous = os.getcwd()
            self.addCleanup(os.chdir, previous)
            os.chdir(directory)
            def git(*args):
                return subprocess.check_output(["git", *args], text=True).strip()
            def commit():
                git("add", "-A")
                git("commit", "--allow-empty", "-qm", "fixture")
                return git("rev-parse", "HEAD")
            git("init", "-q")
            base = commit()
            Path("docs").mkdir()
            prose = Path("docs/review notes.md")
            prose.write_text("notes\n")
            docs = commit()
            self.assertFalse(needs_build(base, docs))
            self.assertFalse(needs_build(docs, base))
            prose.chmod(0o755)
            executable = commit()
            self.assertTrue(needs_build(docs, executable))
            self.assertTrue(needs_build(executable, docs))
            prose.chmod(0o644)
            prose.rename("docs/validate.py")
            script = commit()
            self.assertTrue(needs_build(docs, script))
            self.assertTrue(needs_build(script, docs))
            Path("firmware.cpp").write_text("profile\n")
            mixed = commit()
            self.assertTrue(needs_build(docs, mixed))
            Path("docs/link.md").symlink_to("review notes.md")
            self.assertTrue(needs_build(mixed, commit()))
            self.assertTrue(needs_build("0" * 40, docs))
            self.assertTrue(needs_build(None, docs))


if __name__ == "__main__":
    unittest.main()
