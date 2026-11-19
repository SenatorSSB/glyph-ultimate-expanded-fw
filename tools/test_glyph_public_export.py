#!/usr/bin/env python3
"""Public export fail-closed controls; uses disposable byte trees only."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
import glyph_public_export as ex


def policy():
    return {'rules': [{'prefix': 'src/', 'classification': 'PUBLIC_INCLUDE', 'purpose': 'fixture'}],
            'exceptions': {}, 'binary_records': {}, 'privacy_exceptions': {},
            'notice_obligations': [], 'dependencies': []}


def item(path='src/ok.txt', body=b'public source\n'):
    return path, '100644', body


class ExportTests(unittest.TestCase):
    def reject(self, entries, p=None):
        with self.assertRaises(ex.ExportError):
            ex.plan(entries, p or policy())

    def test_unclassified_new_family(self):
        self.reject([item('new-family.txt')])

    def test_ambiguous_rules(self):
        p=policy();p['rules'].append(dict(p['rules'][0]))
        self.reject([item()],p)

    def test_duplicate_source(self):
        self.reject([item(),item()])

    def test_path_escape_absolute_backslash_and_caches(self):
        for path in ['../escape', '/absolute', 'src/../escape', 'src/./x', 'src//x',
                     'src\\x', 'C:/x', 'src/.git/x', 'src/.GIT/x', 'src/.pio/x',
                     'src/__pycache__/x', 'src/node_modules/x', 'src/local_backups/x']:
            with self.subTest(path=path): self.reject([item(path)])

    def test_personal_path_and_encoded_path(self):
        for body in [b'/'+b'Users/person/work', b'%2fUsers%2fperson%2fwork',
                     b'mail'+b'@example.invalid', b'private-capture-path']:
            with self.subTest(body=body): self.reject([item(body=body)])

    def test_encoded_locators_and_other_host_roots(self):
        for b in [br'\u002fUsers\u002fperson\u002fwork', b'%252fUsers%252fperson%252fwork',
                  br'\x2fUsers\x2fperson', b'/root/person', b'/Volumes/disk/person',
                  b'/mnt/owner', b'/run/user/123', b'/var/tmp/owner',
                  br'person\u0040example.invalid']:
            with self.subTest(body=b):self.reject([item(body=b)])
        deep=b'/Users/person'
        for _ in range(10):deep=deep.replace(b'%',b'%25').replace(b'/',b'%2f')
        self.reject([item(body=deep)])

    def test_output_cannot_relocate_into_historical_family(self):
        p=policy();p['exceptions']['src/a']={'classification':'PUBLIC_INCLUDE','purpose':'test','output':'docs/project/leak'}
        self.reject([item('src/a')],p)

    def test_historical_family_requires_narrow_record(self):
        p=policy();p['exceptions']['docs/project/x.md']={'classification':'PUBLIC_INCLUDE','purpose':'bad'}
        self.reject([item('docs/project/x.md')],p)
        p['exceptions']['docs/project/x.md'].update(historical_exception=True,sha256=ex.digest(item()[2]))
        self.assertIn('docs/project/x.md',ex.plan([item('docs/project/x.md')],p)[1])

    def test_binary_defaults_to_deny(self):
        rows,out,_=ex.plan([item('src/x.pb',b'\x08\x01')],policy())
        self.assertEqual(rows[0]['classification'],'PUBLIC_EXCLUDE_HISTORICAL')
        self.assertFalse(out)

    def test_binary_exact_inclusion_requires_record(self):
        p=policy();p['exceptions']['src/x.pb']={'classification':'PUBLIC_INCLUDE','purpose':'bad'}
        self.reject([item('src/x.pb',b'\x08\x01')],p)

    def test_binary_digest_schema_consumer_and_bounds(self):
        b=b'\x08\x01';p=policy();p['exceptions']['src/x.pb']={'classification':'PUBLIC_INCLUDE','purpose':'test'}
        rec={'sha256':ex.digest(b),'schema':'synthetic.proto','decoder':'wire fixture','consumer':'test','purpose':'test','max_bytes':2}
        p['binary_records']['src/x.pb']=rec
        self.assertTrue(ex.plan([item('src/x.pb',b)],p)[1])
        for key,value in [('sha256','wrong'),('consumer',''),('schema',''),('decoder',''),('max_bytes',1)]:
            q=copy.deepcopy(p);q['binary_records']['src/x.pb'][key]=value
            with self.subTest(key=key):self.reject([item('src/x.pb',b)],q)
        self.reject([item('src/x.pb',b'\x12\x05')],p)

    def test_gzip_bounded_decompression_hash_and_privacy(self):
        b=gzip.compress(b'public',mtime=0);p=policy();p['exceptions']['src/x.gz']={'classification':'PUBLIC_INCLUDE','purpose':'test'}
        p['binary_records']['src/x.gz']={'sha256':ex.digest(b),'consumer':'test','purpose':'test','max_decompressed_bytes':6,'decompressed_sha256':ex.digest(b'public')}
        self.assertTrue(ex.plan([item('src/x.gz',b)],p)[1])
        q=copy.deepcopy(p);q['binary_records']['src/x.gz']['max_decompressed_bytes']=5
        self.reject([item('src/x.gz',b)],q)
        q=copy.deepcopy(p);q['binary_records']['src/x.gz']['decompressed_sha256']='bad'
        self.reject([item('src/x.gz',b)],q)
        private=b'/'+b'Users/synthetic/private';b=gzip.compress(private,mtime=0)
        p['binary_records']['src/x.gz'].update(sha256=ex.digest(b),max_decompressed_bytes=100,decompressed_sha256=ex.digest(private))
        self.reject([item('src/x.gz',b)],p)

    def test_required_bundled_and_embedded_notices(self):
        p=policy();p['notice_obligations']=[{'material_prefix':'src/','notices':['LICENSE']}]
        self.reject([item()],p)
        p=policy();p['embedded_notices']={'src/ok.txt':{'sha256':ex.digest(b'full embedded license')}}
        self.reject([item()],p)

    def test_embedded_notice_cannot_be_truncated_to_keywords(self):
        full=b'MIT License Copyright Permission is hereby granted FULL BODY source'
        p=policy();p['embedded_notices']={'src/ok.txt':{'sha256':ex.digest(full)}}
        self.assertTrue(ex.plan([item(body=full)],p)[1])
        self.reject([item(body=b'MIT License Copyright Permission is hereby granted source')],p)

    def test_notice_mutation(self):
        p=policy();p['notice_obligations']=[{'material_prefix':'src/','notices':['src/LICENSE']}]
        p['notice_sha256']={'src/LICENSE':ex.digest(b'full license')}
        self.assertTrue(ex.plan([item(),item('src/LICENSE',b'full license')],p)[1])
        for b in [b'',b'truncated']:
            with self.subTest(body=b):self.reject([item(),item('src/LICENSE',b)],p)

    def test_journal_transform_title_current_only_and_idempotence(self):
        for path,kind in ex.JOURNALS.items():
            b=(f'# Title\n\n<!-- {kind}:start -->\n## Current\nPublic.\n<!-- {kind}:end -->\n\nLegacy PRIVATE body\n').encode()
            out=ex.transform(path,b)
            self.assertTrue(out.startswith(b'# Title\n'));self.assertNotIn(b'PRIVATE',out)
            self.assertEqual(out,ex.transform(path,out))
            for bad in [b.replace(b':start',b':missing'), b+b'<!-- '+kind.encode()+b':start -->',
                        b.replace(b'## Current',b'legacy-current-state-journal')]:
                with self.subTest(path=path,bad=bad),self.assertRaises(ex.ExportError):ex.transform(path,bad)
        with self.assertRaises(ex.ExportError):ex.transform('src/ok.txt',b'anything')

    def test_whole_journal_cannot_be_included(self):
        p=policy();path='docs/CURRENT_STATE.md';p['exceptions'][path]={'classification':'PUBLIC_INCLUDE','purpose':'bad'}
        b=b'# State\n<!-- current-state-v1:start -->\nCurrent\n<!-- current-state-v1:end -->\nPRIVATE LEGACY'
        self.reject([item(path,b)],p)

    def test_output_collision_and_escape(self):
        p=policy()
        for src in ['src/a','src/b']:p['exceptions'][src]={'classification':'PUBLIC_INCLUDE','purpose':'test','output':'same'}
        self.reject([item('src/a'),item('src/b')],p)
        p['exceptions']['src/a']['output']='../escape'
        self.reject([item('src/a')],p)

    def test_staging_rejects_git_cache_and_symlinks(self):
        _,output,_=ex.plan([item()],policy())
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'out';ex.write_staging(root,output)
            ex.validate_staging(root,output)
            with self.assertRaises(ex.ExportError):ex.write_staging(root,output)
            for name in ['.git','.pio','__pycache__']:
                (root/name).mkdir()
                with self.assertRaises(ex.ExportError):ex.validate_staging(root,output)
                (root/name).rmdir()
            (root/'link').symlink_to(root/'src/ok.txt')
            with self.assertRaises(ex.ExportError):ex.validate_staging(root,output)

    def test_privacy_exception_is_bound_to_exact_source_and_tokens(self):
        b=b'test'+b'@example.invalid';p=policy();p['privacy_exceptions']['src/ok.txt']={'sha256':ex.digest(b),'match_sha256':[ex.digest(('contact:'+b.decode()).encode())],'purpose':'synthetic'}
        ex.scan('src/ok.txt',b,p)
        with self.assertRaises(ex.ExportError):ex.scan('src/ok.txt',b+b' drift',p)
        q=copy.deepcopy(p);q['privacy_exceptions']['src/ok.txt']['match_sha256']=[]
        with self.assertRaises(ex.ExportError):ex.scan('src/ok.txt',b,q)

    def test_owner_marker_cannot_be_excepted(self):
        b=b'synthetic.owner';p=policy();p['forbidden_markers']=[{'length':len(b),'sha256':ex.digest(b)}]
        p['privacy_exceptions']['src/ok.txt']={'sha256':ex.digest(b),'match_sha256':[ex.digest(('owner_local:'+b.decode()).encode())],'purpose':'forbidden'}
        for embedded in [b, b + b'.json', b'prefix-' + b, b'machine=' + b + b'-backup', b.upper()]:
            with self.subTest(body=embedded):self.reject([item(body=embedded)],p)

    def nuker_policy(self):
        return ex.load_policy(ex.ROOT / ex.POLICY)

    def test_nuker_workflow_requires_source_packaging(self):
        output = {'.github/workflows/build.yml': ('100644', b'ls *.uf2 | xargs ./glyph_nuker')}
        p = self.nuker_policy()
        self.assertEqual(ex.workflow_publication_blockers(output, p),
                         ['.github/workflows/build.yml:' + ex.NUKER_OBLIGATION])
        output['glyph_nuker'] = ('100755', b'synthetic executable for packaging tests')
        self.assertTrue(ex.workflow_publication_blockers(output, p))
        self.assertNotIn('GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED', str(ex.workflow_publication_blockers(output, p)))

    def test_nuker_obligation_cannot_be_dropped_or_reverted(self):
        for field, value in [('glyph_nuker_obligation', None),
                             ('glyph_nuker_obligation', {'status': 'GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED'})]:
            p = self.nuker_policy(); p[field] = value
            with self.subTest(value=value), self.assertRaisesRegex(ex.ExportError, 'mandatory source/provenance'):
                ex.plan([('glyph_nuker', '100755', b'synthetic executable for packaging tests')], p)

    def test_nuker_executable_inclusion_without_source_fails(self):
        p = self.nuker_policy()
        p['exceptions']['glyph_nuker']['classification'] = 'PUBLIC_INCLUDE'
        data = b'synthetic executable for packaging tests'
        # Inspection admission is separately guarded by the existing binary
        # scanner. Isolate the packaging gate, without admitting/executing ELF.
        from unittest.mock import patch
        p['binary_records']['glyph_nuker'] = {'sha256': ex.digest(data)}
        p['notice_obligations'] = []
        with patch.object(ex, 'inspect_binary', return_value={}):
            with self.assertRaisesRegex(ex.ExportError, 'executable lacks exact Corresponding Source'):
                ex.plan([('glyph_nuker', '100755', data)], p)

    def test_nuker_relocation_cannot_bypass_packaging(self):
        p = self.nuker_policy()
        p['exceptions']['glyph_nuker'].update(classification='PUBLIC_INCLUDE', output='tools/renamed_nuker')
        p['notice_obligations'] = []
        with self.assertRaisesRegex(ex.ExportError, 'executable relocation forbidden'):
            ex.plan([('glyph_nuker', '100755', b'synthetic executable for packaging tests')], p)

    def test_nuker_positive_packaging_and_individual_omissions(self):
        # Exercise the complete gate with synthetic source bytes in memory. No
        # external source is imported into this repository or a release tree.
        from unittest.mock import patch
        p = self.nuker_policy()
        receipt = json.loads((ex.ROOT / ex.G2F_RECEIPT).read_bytes())
        receipt['official_repository']['binary']['sha256'] = ex.digest(b'synthetic executable for packaging tests')
        synthetic = {name: ('synthetic preferred source: ' + name).encode()
                     for name in receipt['source']['files_sha256']}
        receipt['source']['files_sha256'] = {name: ex.digest(body) for name, body in synthetic.items()}
        raw = json.dumps(receipt).encode()
        output = {'.github/workflows/build.yml': ('100644', b'./glyph_nuker'),
                  'glyph_nuker': ('100755', b'synthetic executable for packaging tests'),
                  ex.G2F_RECEIPT: ('100644', raw)}
        for path in p['glyph_nuker_obligation']['required_notices'] + [receipt['source']['evidence']]:
            output[path] = ('100644', (ex.ROOT / path).read_bytes())
        output.update({ex.NUKER_POLICY['source_prefix'] + name: ('100644', body)
                       for name, body in synthetic.items()})
        with patch.object(ex, 'G2F_SHA256', ex.digest(raw)):
            self.assertTrue(ex.nuker_packaging_complete(output, p))
            q = copy.deepcopy(p)
            q['privacy_exceptions'].pop(ex.G2F_RECEIPT, None)
            q['binary_records']['glyph_nuker']['sha256'] = ex.digest(output['glyph_nuker'][1])
            q['dependencies'].append({'name': 'unrelated', 'action': 'REVIEW_REQUIRED'})
            with patch.object(ex, 'inspect_binary', return_value={}):
                rows, admitted, totals = ex.plan([(path, mode, body) for path, (mode, body) in output.items()], q)
                self.assertIn('glyph_nuker', admitted)
                self.assertEqual(ex.release_blockers(rows, admitted, q), ['license:unrelated'])
                self.assertEqual(sum(group['files'] for group in totals.values()), len(output))
                # Every omitted required byte set keeps normal export refused.
                for missing in set(output) - {'.github/workflows/build.yml', 'glyph_nuker'}:
                    with self.subTest(plan_missing=missing):
                        subset = {path: value for path, value in output.items() if path != missing}
                        try:
                            rr, oo, _ = ex.plan([(path, mode, body) for path, (mode, body) in subset.items()], q)
                        except ex.ExportError:
                            continue
                        self.assertNotIn('glyph_nuker', oo)
                        self.assertTrue(ex.release_blockers(rr, oo, q))
            self.assertEqual(ex.workflow_publication_blockers(output, p), [])
            # No standalone LICENSE exists in this valid source fixture.
            self.assertFalse(receipt['source']['standalone_license_file'])
            for path in set(output) - {'.github/workflows/build.yml'}:
                with self.subTest(missing=path):
                    q = dict(output); q.pop(path)
                    self.assertFalse(ex.nuker_packaging_complete(q, p))
            for path in [ex.NUKER_POLICY['source_prefix'] + 'src/root.zig', ex.G2F_RECEIPT, 'LICENSE', 'THIRD_PARTY_NOTICES.md']:
                with self.subTest(altered=path):
                    q = dict(output); q[path] = (q[path][0], q[path][1] + b'altered')
                    self.assertFalse(ex.nuker_packaging_complete(q, p))
            q = dict(output); q[ex.NUKER_POLICY['source_prefix'] + 'extra.zig'] = ('100644', b'extra')
            self.assertFalse(ex.nuker_packaging_complete(q, p))

    def test_source_ingestion_exact_set_hash_modes_and_no_git(self):
        from unittest.mock import patch
        import os
        receipt = json.loads((ex.ROOT / ex.G2F_RECEIPT).read_bytes())
        synthetic = {name: ('synthetic source ' + name).encode()
                     for name in receipt['source']['files_sha256']}
        receipt['source']['files_sha256'] = {name: ex.digest(body) for name, body in synthetic.items()}
        raw = json.dumps(receipt).encode()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'source'; source.mkdir()
            record = root / ex.G2F_RECEIPT; record.parent.mkdir(parents=True); record.write_bytes(raw)
            for name, body in synthetic.items():
                target = source / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(body)
            with patch.object(ex, 'ROOT', root), patch.object(ex, 'G2F_SHA256', ex.digest(raw)):
                self.assertEqual(len(ex.corresponding_source_entries(source)), 5)
                target = source / 'src/root.zig'; original = target.read_bytes()
                for change in ('missing', 'bytes', 'executable', 'symlink', 'extra', 'git'):
                    with self.subTest(change=change):
                        extra = None
                        if change == 'missing': target.unlink()
                        elif change == 'bytes': target.write_bytes(b'drift')
                        elif change == 'executable': target.chmod(0o755)
                        elif change == 'symlink': target.unlink(); target.symlink_to(source / 'src/main.zig')
                        elif change == 'extra': extra = source / 'README.md'; extra.write_bytes(b'extra')
                        elif change == 'git': extra = source / '.git'; extra.mkdir(); (extra / 'config').write_bytes(b'private')
                        with self.assertRaises(ex.ExportError): ex.corresponding_source_entries(source)
                        if extra:
                            if extra.is_dir(): (extra / 'config').unlink(); extra.rmdir()
                            else: extra.unlink()
                        if target.is_symlink(): target.unlink()
                        target.write_bytes(original); target.chmod(0o644)
                link = root / 'link'; link.symlink_to(source, target_is_directory=True)
                with self.assertRaises(ex.ExportError): ex.corresponding_source_entries(link)

    def test_actual_policy_keeps_unstaged_source_blocked(self):
        p = self.nuker_policy()
        data = (ex.ROOT / 'glyph_nuker').read_bytes()
        rows, out, _ = ex.plan([('glyph_nuker', '100755', data)], p)
        self.assertEqual(rows[0]['classification'], 'REVIEW_REQUIRED')
        self.assertNotIn('glyph_nuker', out)
        self.assertIn('license:glyph_nuker', ex.release_blockers(rows, out, p))

    def test_current_package_offline_fixture_closure(self):
        import check_glyph_coordinate_native_runtime_profile_contract as contract
        p = ex.load_policy(ex.ROOT / ex.POLICY)
        cases = [
            contract.DRY_RUN_NEUTRAL_FIXTURE, contract.DRY_RUN_CARDINAL_FIXTURE,
            contract.DRY_RUN_DIAGONAL_FIXTURE, contract.DRY_RUN_MERGE_FIXTURE,
            contract.DRY_RUN_Y2_NEUTRAL_FIXTURE, contract.DRY_RUN_Y2_CARDINAL_FIXTURE,
            contract.DRY_RUN_Y2_DIAGONAL_FIXTURE, contract.DRY_RUN_Y2_TILT3_FIXTURE,
            *contract.DRY_RUN_NEGATIVE_FIXTURES,
        ]
        inputs = [path for path, _ in contract.NEGATIVE_FIXTURE_REASON_PAIRS] + [
            contract.OFFLINE_PIPELINE_PROFILE_FIXTURE, *cases,
            *contract.CONVERTER_PROFILE_FIXTURES, *contract.CONVERTER_NEGATIVE_FIXTURES,
            contract.LAYOUT_SPEC_FIXTURE, contract.GENERATED_OUTPUT_FIXTURE,
            contract.OFFLINE_ARTIFACT_BUNDLE_MANIFEST_FIXTURE,
            contract.OFFLINE_EXPORT_PACKAGE_FIXTURE,
        ]
        inputs += [ex.ROOT / json.loads(path.read_text())['profile_path'] for path in cases]
        for path in inputs:
            relative = path.relative_to(ex.ROOT).as_posix()
            with self.subTest(path=relative):
                self.assertIn(ex.classify(relative, path.read_bytes(), p), ex.PUBLIC)
                ex.scan(relative, path.read_bytes(), p)

    def test_repository_policy_regular_tracked_paths_and_direct_dependencies(self):
        p=ex.load_policy(ex.ROOT/ex.POLICY)
        dispositions={path:ex.classify(path,b,p) for path,_,b in ex.tracked_tree(ex.ROOT,'HEAD')}
        self.assertTrue(dispositions)
        m=json.loads((ex.ROOT/'docs/runtime_config/fixtures/runtime_config_validation_manifest.json').read_text())
        for e in m['entries']:
            if e['applicability']=='current':
                for path in e['source_dependencies']:
                    with self.subTest(check=e['id'],path=path):self.assertIn(dispositions[path],ex.PUBLIC|{'REVIEW_REQUIRED'})
        for path,c in dispositions.items():
            if path.endswith('.gz'):self.assertNotIn(c,ex.PUBLIC)
            if path.startswith('docs/sources/raw/'):self.assertNotIn(c,ex.PUBLIC)

if __name__=='__main__':unittest.main()
