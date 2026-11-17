#!/usr/bin/env python3
"""Focused public-doc regression controls; no tracked fixture mutations."""
import unittest
from unittest.mock import patch

import check_glyph_docs_agent_surface as surface

import check_glyph_docs_navigation as nav


class PublicDocsTests(unittest.TestCase):
    def setUp(self):
        self.docs = {p: (nav.REPO_ROOT / p).read_text(encoding='utf-8') for p in nav.PUBLIC_PATHS}

    def reject(self, path, before, after):
        self.assertIn(before, self.docs[path])
        self.docs[path] = self.docs[path].replace(before, after)
        with self.assertRaises(nav.DocsNavigationError):
            nav.validate_docs(overrides=self.docs)

    def test_profile_system_routes(self):
        for path in ('docs/README.md', 'docs/CAPABILITIES.md', 'docs/USAGE.md'):
            with self.subTest(path=path):
                self.setUp()
                self.reject(path, '](PROFILE_SYSTEM.md)', '](USAGE.md)')
        self.setUp()
        self.reject('docs/PROFILE_SYSTEM.md', '](../profiles/README.md)', '](USAGE.md)')

    def test_authoring_schema_and_seed_routes(self):
        for target in ('schema/glyph-native-ultimate-profile.v1.schema.json',
                       'templates/UltimateNativeSeed.v1.profile.json'):
            with self.subTest(target=target):
                self.setUp()
                self.reject('profiles/README.md', f']({target})', '](ultimate/README.md)')

    def test_authoring_guardrails_in_both_current_consumers(self):
        def read_override(path):
            return self.docs[path.relative_to(nav.REPO_ROOT).as_posix()]
        for path in ('docs/PROFILE_SYSTEM.md', 'profiles/README.md'):
            for bad in ('Authoring JSON is a complete package.',
                        'The evaluator supports arbitrary scripts.',
                        'Timers are supported.', 'The native program provides arbitrary macros.'):
                with self.subTest(path=path, bad=bad):
                    self.setUp(); self.docs[path] += '\n' + bad + '\n'
                    with self.assertRaises(nav.DocsNavigationError):
                        nav.validate_docs(overrides=self.docs)
                    with patch.object(surface, 'read_required', side_effect=read_override):
                        with self.assertRaises(surface.AgentSurfaceError):
                            surface.validate_public_doc_surface()

    def test_nine_way_nonneutral_and_archival_distinctions(self):
        for path in ('docs/PROFILE_SYSTEM.md', 'profiles/README.md'):
            with self.subTest(path=path):
                self.setUp()
                self.docs[path] = self.docs[path].replace('non-center', 'center-only')
                with self.assertRaises(nav.DocsNavigationError):
                    nav.validate_docs(overrides=self.docs)
                self.setUp()
                self.docs[path] = self.docs[path].replace('7 8 9', '7 8')
                with self.assertRaises(nav.DocsNavigationError):
                    nav.validate_docs(overrides=self.docs)
        self.setUp()
        self.reject('profiles/README.md', 'archival', 'current template')

    def test_system_explanation_can_be_reworded(self):
        # Semantic checks should not lock paragraphs or the conceptual diagram.
        self.docs['docs/PROFILE_SYSTEM.md'] = self.docs['docs/PROFILE_SYSTEM.md'].replace(
            'It is not a\nseparate persisted scripting object', 'It is not a\nstandalone persisted scripting object')
        nav.validate_docs(overrides=self.docs)

    def test_package_consumer_requires_system_schema_and_seed(self):
        mutations = [('docs/README.md', '](PROFILE_SYSTEM.md)'),
                     ('docs/PROFILE_SYSTEM.md', '../profiles/README.md'),
                     ('profiles/README.md', '](schema/glyph-native-ultimate-profile.v1.schema.json)'),
                     ('profiles/README.md', '](templates/UltimateNativeSeed.v1.profile.json)')]
        for path, target in mutations:
            with self.subTest(path=path, target=target):
                self.setUp(); self.docs[path] = self.docs[path].replace(target, 'missing-route')
                def read_override(file):
                    return self.docs[file.relative_to(nav.REPO_ROOT).as_posix()]
                with patch.object(surface, 'read_required', side_effect=read_override):
                    with self.assertRaises(surface.AgentSurfaceError):
                        surface.validate_public_doc_surface()

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
