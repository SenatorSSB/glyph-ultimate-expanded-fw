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
        p['exceptions']['docs/project/x.md']['historical_exception']=True
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
        p=policy();p['embedded_notices']={'src/ok.txt':['Copyright']}
        self.reject([item()],p)

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
        b=b'rasmus'+b'.pekkarinen';p=policy()
        p['privacy_exceptions']['src/ok.txt']={'sha256':ex.digest(b),'match_sha256':[ex.digest(('owner_local:'+b.decode()).encode())],'purpose':'forbidden'}
        self.reject([item(body=b)],p)

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
