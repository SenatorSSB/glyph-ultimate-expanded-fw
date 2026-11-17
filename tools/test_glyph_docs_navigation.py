#!/usr/bin/env python3
"""Focused public-doc regression controls; no tracked fixture mutations."""
import re
import unittest
from unittest.mock import patch

import check_glyph_docs_agent_surface as surface

import check_glyph_docs_navigation as nav
import check_glyph_agent_framework_docs as framework


class PublicDocsTests(unittest.TestCase):
    def setUp(self):
        self.docs = {p: (nav.REPO_ROOT / p).read_text(encoding='utf-8') for p in nav.PUBLIC_PATHS}

    def reject(self, path, before, after):
        self.assertIn(before, self.docs[path])
        self.docs[path] = self.docs[path].replace(before, after)
        with self.assertRaises(nav.DocsNavigationError):
            nav.validate_docs(overrides=self.docs)

    def test_public_agents_contract_negative_controls(self):
        original = self.docs['AGENTS.md']
        controls = (
            ('queue requirement', original + '\nACTIVE_AGENT_QUEUE.md is required for ordinary work.\n'),
            ('READY requirement', original + '\nA READY work order is required for every ordinary task.\n'),
            ('Planner prerequisite', original.replace('Start ordinary coding work with:',
                                                   'First follow Planner and Curator runway.')),
            ('Planner approval after history note', original + '\nPlanner approval is required before every ordinary task.\n'),
            ('Curator approval after history note', original + '\nCurator approval is mandatory before ordinary work.\n'),
            ('runway after history note', original + '\nBefore ordinary work, verify the runway.\n'),
            ('canonical environment prefix', original.replace('pio run -e glyph_mk6', 'pio run -e glyph_mk6_wrong')),
            ('build acceptance', original + '\nA CI build proves hardware acceptance.\n'),
            ('TIMEOUT PASS', original + '\nTIMEOUT is PASS.\n'),
            ('SKIPPED PASS', original + '\nSKIPPED means PASS.\n'),
            ('specific device authority', original.replace('specific device action', 'general task')),
            ('device boundary deletion', original.replace('unless the user explicitly authorizes that',
                                                         'because the user assigned a task about that')),
            ('canonical command', original.replace('pio run -e glyph_mk6', 'pio run -e other')),
            ('automatic login', original + '\nAfter network failure run gh auth login.\n'),
            ('automatic credentials', original + '\nAfter DNS failure change GitHub credentials.\n'),
        )
        for label, bad in controls:
            with self.subTest(control=label):
                self.setUp(); self.docs['AGENTS.md'] = bad
                self.assert_both_reject()
                with self.assertRaises(framework.FrameworkDocsError):
                    framework.check_public_agents_contract(bad)
        for action in ('serial/device write', 'hidden device mutation',
                       'destructive\nrecovery', 'controller operation'):
            with self.subTest(action=action):
                self.setUp()
                self.assertIn(action, original)
                self.docs['AGENTS.md'] = original.replace(action, 'ordinary action')
                self.assert_both_reject()
                with self.assertRaises(framework.FrameworkDocsError):
                    framework.check_public_agents_contract(self.docs['AGENTS.md'])

    def test_agent_route_cannot_return_to_internal_context(self):
        row = next(line for line in self.docs['docs/README.md'].splitlines()
                   if line.startswith('| Coding agents |'))
        for target in ('AGENT_CONTEXT.md', 'WORKFLOW.md', 'agent_framework/README.md',
                       'project/ACTIVE_AGENT_QUEUE.md'):
            with self.subTest(target=target):
                self.setUp()
                self.docs['docs/README.md'] = self.docs['docs/README.md'].replace(
                    row, '| Coding agents | [AGENTS.md](../AGENTS.md), then [required context](' + target + ') |')
                self.assert_both_reject()

    def test_current_state_cannot_require_internal_prerequisites(self):
        for path in ('AGENT_CONTEXT.md', 'project/ACTIVE_AGENT_QUEUE.md',
                     'docs/WORKFLOW.md', 'docs/agent_framework/'):
            with self.subTest(path=path):
                self.setUp()
                self.docs['docs/CURRENT_STATE.md'] = self.docs['docs/CURRENT_STATE.md'].replace(
                    '<!-- current-state-v1:end -->',
                    'Developers and coding agents must read ' + path + ' first.\n<!-- current-state-v1:end -->')
                self.assert_both_reject()

    def test_public_agents_semantic_rewording(self):
        text = self.docs['AGENTS.md'].replace('Build PASS is not hardware acceptance',
                                            'Build proof does not confer hardware acceptance').replace(
            'TIMEOUT is not PASS', 'TIMEOUT does not mean PASS').replace(
            'specific device action', 'particular device action').replace(
            '## Read first', '## Public entry points')
        self.docs['AGENTS.md'] = text
        nav.validate_docs(overrides=self.docs)
        surface.check_public_agents_contract(text)
        framework.check_public_agents_contract(text)

    def test_package_docs_do_not_read_historical_status_mirrors(self):
        retired = {surface.AGENT_CONTEXT, surface.RUNTIME_README,
                   surface.CALIBRATION_INDEX, surface.ARCHIVE_INDEX}
        original_read = surface.read_required
        def current_only(path):
            self.assertNotIn(path, retired)
            return original_read(path)
        with patch.object(surface, 'read_required', side_effect=current_only):
            surface.validate_docs()

    def test_framework_scan_excludes_public_agents(self):
        original_read = framework.read_required
        def internal_only(path):
            self.assertNotEqual(path, 'AGENTS.md')
            return original_read(path)
        with patch.object(framework, 'read_required', side_effect=internal_only):
            text = framework.active_framework_text()
        self.assertNotIn('# Coding-agent instructions', text)
        self.assertIn('GLYPH-UD-029', text)

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

    def assert_both_reject(self):
        with self.assertRaises(nav.DocsNavigationError):
            nav.validate_docs(overrides=self.docs)
        def read_override(path):
            return self.docs[path.relative_to(nav.REPO_ROOT).as_posix()]
        with patch.object(surface, 'read_required', side_effect=read_override):
            with self.assertRaises(surface.AgentSurfaceError):
                surface.validate_public_doc_surface()

    def test_technical_routes_in_both_consumers(self):
        for path, target in (
            ('README.md', 'docs/DEVELOPMENT.md'), ('README.md', 'AGENTS.md'),
            ('docs/README.md', 'DEVELOPMENT.md'),
            ('docs/ARCHITECTURE.md', 'PROFILE_SYSTEM.md'),
            ('docs/ARCHITECTURE.md', 'CAPABILITIES.md'),
            ('docs/ARCHITECTURE.md', '../config/glyph/common/src/config.cpp'),
            ('docs/DEVELOPMENT.md', 'ARCHITECTURE.md'),
            ('docs/DEVELOPMENT.md', 'CURRENT_STATE.md'),
            ('docs/DEVELOPMENT.md', 'PROFILE_SYSTEM.md')):
            with self.subTest(path=path, target=target):
                self.setUp()
                self.docs[path] = self.docs[path].replace(f']({target})', '](README.md)')
                self.assert_both_reject()

    def test_architecture_distinctions_in_both_consumers(self):
        for before, after in (
            ('stock row label is not a mode engine', 'stock row label is a mode engine'),
            ('mode engine is not a communication backend', 'mode engine is a communication backend'),
            ('Config row is not a ProfileStore record', 'Config row is a ProfileStore record'),
            ('neither alone is a complete package', 'each alone is a complete package'),
            ('transport is distinct from the retired', 'transport is the retired')):
            with self.subTest(before=before):
                self.setUp()
                text = self.docs['docs/ARCHITECTURE.md']
                # Whitespace in prose is not part of the contract.
                changed, count = re.subn(r'\s+'.join(map(re.escape, before.split())), after, text)
                self.assertGreater(count, 0)
                self.docs['docs/ARCHITECTURE.md'] = changed
                self.assert_both_reject()

    def test_development_evidence_and_policy_in_both_consumers(self):
        for before, after in (
            ('pio run -e glyph_mk6', 'pio run'),
            ('A CI build is not physical hardware acceptance', 'A CI build proves physical hardware acceptance'),
            ('TIMEOUT is not PASS', 'TIMEOUT is PASS'),
            ('SKIPPED is\nnot PASS', 'SKIPPED is PASS'),
            ('## Documentation maintenance policy', '## Notes')):
            with self.subTest(before=before):
                self.setUp()
                self.assertIn(before, self.docs['docs/DEVELOPMENT.md'])
                self.docs['docs/DEVELOPMENT.md'] = self.docs['docs/DEVELOPMENT.md'].replace(before, after)
                self.assert_both_reject()

    def test_public_path_does_not_require_internal_queue(self):
        for path, before, after in (
            ('README.md', 'Developers: build, test and contribute', 'Developers: first read ACTIVE_AGENT_QUEUE'),
            ('docs/README.md', '| Developers |', '| Developers: agent_framework required |'),
            ('docs/DEVELOPMENT.md', 'Branch from the current live', 'Read ACTIVE_AGENT_QUEUE first. Branch from the current live')):
            with self.subTest(path=path):
                self.setUp()
                self.docs[path] = self.docs[path].replace(before, after)
                self.assert_both_reject()

    def test_technical_prose_and_diagrams_can_be_reworded(self):
        self.docs['docs/ARCHITECTURE.md'] = self.docs['docs/ARCHITECTURE.md'].replace(
            'is not a mode engine', 'differs from a mode engine').replace(
            'flowchart LR', 'flowchart TD')
        nav.validate_docs(overrides=self.docs)
        technical = {p: self.docs[p] for p in ('README.md', 'docs/README.md',
                     'docs/ARCHITECTURE.md', 'docs/DEVELOPMENT.md')}
        surface.validate_technical_surface(technical)

    def test_development_guards_in_both_consumers(self):
        for before, after in (
            ('pio run -e glyph_mk6', 'pio run -e other'),
            ('TIMEOUT is not PASS', 'TIMEOUT is PASS'),
            ('SKIPPED is\nnot PASS', 'SKIPPED is PASS'),
            ('## Documentation maintenance policy', '## Other notes'),
            ('| [ROADMAP](ROADMAP.md) | Future intent |', '| Other | Future intent |'),
            ('A CI build is not physical hardware acceptance', 'A CI build proves physical hardware acceptance')):
            with self.subTest(before=before):
                self.setUp()
                self.assertIn(before, self.docs['docs/DEVELOPMENT.md'])
                self.docs['docs/DEVELOPMENT.md'] = self.docs['docs/DEVELOPMENT.md'].replace(before, after)
                self.assert_both_reject()

    def test_public_path_cannot_require_internal_workflow(self):
        for path, before, after in (
            ('README.md', '](docs/DEVELOPMENT.md)', '](docs/DEVELOPMENT.md), then [required queue](docs/project/ACTIVE_AGENT_QUEUE.md)'),
            ('docs/README.md', '](DEVELOPMENT.md)', '](DEVELOPMENT.md), then [required workflow](WORKFLOW.md)'),
            ('docs/DEVELOPMENT.md', 'Branch from the current live', 'Read docs/project/ACTIVE_AGENT_QUEUE.md first. Branch from the current live')):
            with self.subTest(path=path):
                self.setUp()
                self.docs[path] = self.docs[path].replace(before, after)
                self.assert_both_reject()

    def test_internal_workflow_cannot_become_public_prerequisite(self):
        for path, before, after in (
            ('README.md', 'Developers: build, test and contribute',
             'Developers: read AGENTS.md first, then build, test and contribute'),
            ('docs/README.md', '| Developers |', '| Developers: WORKFLOW.md first |'),
            ('docs/DEVELOPMENT.md', '## Supported public development path',
             '## Supported public development path\nRead ACTIVE_AGENT_QUEUE first.')):
            with self.subTest(path=path):
                self.setUp(); self.docs[path] = self.docs[path].replace(before, after)
                self.assert_both_reject()

    def test_technical_wording_is_not_paragraph_locked(self):
        self.docs['docs/ARCHITECTURE.md'] = self.docs['docs/ARCHITECTURE.md'].replace(
            'stock row label is not a mode engine', 'stock row label differs from the mode engine')
        self.docs['docs/DEVELOPMENT.md'] = self.docs['docs/DEVELOPMENT.md'].replace(
            'TIMEOUT is not PASS', 'TIMEOUT does not mean PASS')
        nav.validate_docs(overrides=self.docs)
        surface.validate_technical_surface(self.docs)

    def test_curated_acceptance_cannot_be_promoted(self):
        for before, after in (
            ('| DInput | N/A |', '| DInput | PASS |'),
            ('| DInput | N/A |', '| DInput | N/A / PASS |'),
            ('| Browser Gamepad API / JoyCheck | NOT_QUALIFIED |',
             '| Browser Gamepad API / JoyCheck | PASS |'),
            ('| Nunchuk | NOT_TESTED |', '| Nunchuk | PASS |')):
            with self.subTest(before=before):
                self.setUp(); self.reject('docs/history/HARDWARE_ACCEPTANCE.md', before, after)

    def test_ci_rebuild_does_not_inherit_acceptance(self):
        for path in ('docs/history/HARDWARE_ACCEPTANCE.md', 'docs/history/SOURCE_LINEAGE.md'):
            with self.subTest(path=path):
                self.setUp()
                self.docs[path] += '\nA CI rebuild inherits hardware acceptance.\n'
                with self.assertRaises(nav.DocsNavigationError):
                    nav.validate_docs(overrides=self.docs)

    def test_curated_tested_source_is_not_documentation_tip(self):
        for path in ('docs/history/HARDWARE_ACCEPTANCE.md', 'docs/history/SOURCE_LINEAGE.md'):
            with self.subTest(path=path):
                self.setUp()
                self.reject(path, '| Tested source | `dcf6e29589f558a95c021bef491578f87e41750f` |',
                            '| Tested source | `935f08f72dc52476dfbdd2e0059467c13ac5cd9d` |')

    def test_future_fresh_commit_is_not_tested_commit(self):
        self.reject('docs/history/SOURCE_LINEAGE.md',
                    'A fresh public repository commit will not become the physically tested source\ncommit.',
                    'A fresh public repository commit becomes the physically tested source commit.')

    def test_evidence_scope_warning_is_required(self):
        self.reject('docs/evidence/README.md',
                    'Linking evidence does not broaden its scope or upgrade\nits status.',
                    'Linking evidence upgrades every result.')

    def test_history_current_truth_owner_and_selected_scope(self):
        self.reject('docs/history/HISTORY.md',
                    'owns present truth', 'shares historical and present truth')
        self.setUp()
        self.reject('docs/history/HISTORY.md', 'not an exhaustive', 'an exhaustive')

    def test_historical_reader_route_is_public(self):
        path = 'docs/README.md'
        row = next(line for line in self.docs[path].splitlines()
                   if line.startswith('| Historical/evidence research |'))
        self.reject(path, row, '| Historical/evidence research | [Queue](project/ACTIVE_AGENT_QUEUE.md), then [framework](agent_framework/README.md) |')
        self.setUp()
        self.reject(path, row, row.replace(' |', ', then agent_framework required |', 1))

    def test_curated_private_locators_and_contacts_are_rejected(self):
        for path in nav.CURATED_PATHS:
            for locator in ('/Users/sample/private/capture.json', '/home/sample/capture.json',
                            'C:\\Users\\sample\\capture.json', 'local_backups/unit/firmware.uf2',
                            'private-capture-path: hidden', 'sample@example.invalid'):
                with self.subTest(path=path, locator=locator):
                    self.setUp(); self.docs[path] += '\n' + locator + '\n'
                    with self.assertRaises(nav.DocsNavigationError):
                        nav.validate_docs(overrides=self.docs)

    def test_curated_wording_and_milestones_are_not_locked(self):
        self.docs['docs/history/HISTORY.md'] = self.docs['docs/history/HISTORY.md'].replace(
            'selected chronology, not an exhaustive journal', 'selected milestones, not exhaustive history').replace(
            'Material change and evidence', 'Engineering milestone and sources')
        self.docs['docs/history/DECISIONS.md'] = self.docs['docs/history/DECISIONS.md'].replace(
            'Keep version domains independent', 'Preserve separate version contracts')
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
