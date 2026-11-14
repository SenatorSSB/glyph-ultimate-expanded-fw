"""Stale-source refusal must precede fixture imports and cached execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from build import profile_store_sources, verify_build


class CachedBuildTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.out = Path(self.temp.name) / 'evidence'
        self.core = self.repo / 'HAL/pico/src/core'
        self.core.mkdir(parents=True)
        (self.out / 'build').mkdir(parents=True)
        for name in ('ProfileStore.cpp', 'ProfileStorePackage.inc', 'ProfileStoreLifecycle.inc'):
            (self.core / name).write_text('// ' + name + '\n')
        self.binary = self.out / 'build/package-fault-harness'
        self.binary.write_bytes(b'cached harness bytes')
        self.files = {str(p.relative_to(self.repo)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in profile_store_sources(self.repo)}
        self.publish()

    def publish(self):
        (self.out / 'build/source-manifest.json').write_text(json.dumps({
            'files': self.files,
            'fingerprint': hashlib.sha256(json.dumps(self.files, sort_keys=True).encode()).hexdigest(),
            'binary_sha256': hashlib.sha256(self.binary.read_bytes()).hexdigest(),
        }))

    def cli_refuses(self, message):
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('run.py')),
                                 '--repo', str(self.repo), '--out', str(self.out),
                                 '--corpus', str(self.repo / 'not-installed'), '--no-build'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)
        self.assertFalse((self.out / 'results.jsonl').exists())

    def test_unchanged_manifest_is_accepted(self):
        verify_build(self.repo, self.out / 'build')

    def test_lifecycle_only_change_is_refused_by_cli(self):
        (self.core / 'ProfileStoreLifecycle.inc').write_text('#error stale lifecycle binary\n')
        self.cli_refuses('source/tool changed since build:')

    def test_older_incomplete_manifest_requires_rebuild(self):
        del self.files['HAL/pico/src/core/ProfileStoreLifecycle.inc']
        self.publish()
        self.cli_refuses('build manifest omits compiled source; rebuild required:')

    def test_new_profile_store_include_requires_rebuild(self):
        (self.core / 'ProfileStoreFuture.inc').write_text('// new dependency\n')
        self.cli_refuses('build manifest omits compiled source; rebuild required:')

    def test_binary_replacement_is_refused(self):
        self.binary.write_bytes(b'another binary')
        self.cli_refuses('binary changed since build')


if __name__ == '__main__':
    unittest.main()
