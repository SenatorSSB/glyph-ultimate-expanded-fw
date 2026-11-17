#!/usr/bin/env python3
"""Focused public-doc regression controls; no tracked fixture mutations."""
import unittest

import check_glyph_docs_navigation as nav


class PublicDocsTests(unittest.TestCase):
    def setUp(self):
        self.docs = {p: (nav.REPO_ROOT / p).read_text(encoding='utf-8') for p in nav.PUBLIC_PATHS}

    def reject(self, path, before, after):
        self.assertIn(before, self.docs[path])
        self.docs[path] = self.docs[path].replace(before, after, 1)
        with self.assertRaises(nav.DocsNavigationError):
            nav.validate_docs(overrides=self.docs)

    def test_current_candidate(self):
        nav.validate_docs(overrides=self.docs)

    def test_required_player_routes(self):
        for target in ('docs/USAGE.md', 'docs/CAPABILITIES.md', 'docs/CURRENT_STATE.md'):
            with self.subTest(target=target):
                self.setUp()
                self.reject('README.md', f']({target})', '](docs/README.md)')

    def test_v0_cannot_replace_current_authoring(self):
        self.reject('README.md', '](profiles/README.md)', '](profiles/ultimate/README.md)')

    def test_dinput_cannot_be_promoted(self):
        self.reject('docs/CURRENT_STATE.md', '| DInput | N/A,', '| DInput | PASS,')

    def test_dinput_na_cannot_hide_added_pass(self):
        self.reject('docs/CURRENT_STATE.md', '| DInput | N/A,', '| DInput | N/A / PASS,')

    def test_freeze_distinction(self):
        self.reject('docs/CURRENT_STATE.md', 'PREPARED_NOT_ACTIVATED', 'ACTIVATED')

    def test_public_release_claim(self):
        for path in nav.PUBLIC_PATHS:
            with self.subTest(path=path):
                self.setUp()
                if path in ('docs/CURRENT_STATE.md', 'docs/ROADMAP.md'):
                    marker = '<!-- current-state-v1:end -->' if path.endswith('CURRENT_STATE.md') else '<!-- current-roadmap-v1:end -->'
                    self.reject(path, marker, 'Public release is available.\n' + marker)
                else:
                    self.docs[path] += '\nPublic release is available.\n'
                    with self.assertRaises(nav.DocsNavigationError):
                        nav.validate_docs(overrides=self.docs)

    def test_stale_blanket_current_claim(self):
        self.reject('docs/CURRENT_STATE.md', '<!-- current-state-v1:end -->',
                    'Runtime-loaded config is not implemented.\n<!-- current-state-v1:end -->')

    def test_keyboard_is_not_backend(self):
        self.reject('docs/CAPABILITIES.md', '| XInput |', '| Keyboard |')

    def test_shared_budget_required(self):
        for path in ('README.md', 'docs/USAGE.md', 'docs/CAPABILITIES.md'):
            with self.subTest(path=path):
                self.setUp()
                self.reject(path, 'shared 30-row budget', '30 additional Ultimate profiles')

    def test_legacy_prose_is_not_current_claim(self):
        for path in ('docs/CURRENT_STATE.md', 'docs/ROADMAP.md'):
            self.docs[path] += '\nRuntime-loaded config is not implemented.\nPublic release is available.\n'
        nav.validate_docs(overrides=self.docs)

    def test_boundaries_fail_closed(self):
        self.reject('docs/CURRENT_STATE.md', '<!-- current-state-v1:end -->', '')

    def test_broken_public_link(self):
        self.reject('docs/README.md', '](USAGE.md)', '](MISSING.md)')


if __name__ == '__main__':
    unittest.main()
