"""Offline tests of the actual continuation adapter and unchanged v2 transport."""
from pathlib import Path
import importlib.util
import json
import contextlib
import io
import shutil
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

e=module('continuation',HERE/'executor.py')
t=module('v2_test_fixtures',HERE.parent/'hardware_v2/test_executor.py')
# Replay all actually retained v2 READ bodies, not synthetic unobserved profiles.
for p in (e.INHERITED/'pre_snapshot').glob('*-READ-*-decoded.bin'):
    raw=p.read_bytes()[1:];t.CAPTURED[t.PB.ProfileStoreResponse.FromString(raw).profile_id]=raw

class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='glyph-cont-offline-')
        self.c=Path(self.tmp.name).resolve()
        e.copy_baseline(self.c)
        self.io=t.FakeIO()
        self.runner=e.Runner(t.POLICY,self.c,t.PB,t.PACKAGE,self.io)
        self.guard=patch.object(e.v2.LiveIO,'ports',side_effect=AssertionError('FORBIDDEN_REAL_DEVICE_ACCESS'))
        self.guard.start()
    def tearDown(self):
        self.guard.stop();self.tmp.cleanup()
    def run_stage(self,name,event=None):
        self.io.stage=name
        return self.runner.execute(name,event or t.owner_event(name))
    def first_and_visual(self):
        self.run_stage('first_xinput_boot');self.run_stage('display')
    def test_actual_full_remaining_sequence_36(self):
        for name in e.STAGES:self.run_stage(name)
        self.assertEqual((len(self.io.writes),self.io.opens,self.io.closes),(36,3,3))
        self.assertFalse((self.c/'install').exists())
        self.assertEqual(e.load(self.c/'pre_snapshot/result.json')['controller_exchanges'],34)
        self.assertEqual(e.load(self.c/'finish/result.json')['packet_result'],'PASS_BOUNDED_LEGACY_DISPLAY_AND_PRESERVATION')
        for p in (e.INHERITED/'pre_snapshot').iterdir():
            if p.is_file():self.assertEqual(p.read_bytes(),(self.c/'pre_snapshot'/p.name).read_bytes())
    def test_no_install_or_new_pre_snapshot(self):
        for name in ('install','pre_snapshot','CREATE','unknown'):
            with self.assertRaises(ValueError):self.runner.execute(name,{})
        self.assertEqual(len(self.io.writes),0)
    def test_owner_report_accepted_without_volume_metadata(self):
        self.assertEqual(e.load(e.INHERITED/'install/owner-event.json')['fresh_volume_path'],'')
        self.runner.prior('install')
        self.assertFalse((e.INHERITED/'install/result.json').exists())
    def test_inherited_copy_tamper_stops(self):
        p=self.c/'pre_snapshot/profile-53.pb';p.write_bytes(p.read_bytes()+b'x')
        with self.assertRaises(ValueError):self.run_stage('first_xinput_boot')
        self.assertEqual(len(self.io.writes),0)
    def test_identity_transport_and_admission_failures(self):
        for fault in ('wrong_runtime','runtime_digest','identity_token','duplicate_identity','bad_viewer','timeout','partial_write','cancel','close'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory(prefix='glyph-cont-negative-') as tmp:
                self.c=Path(tmp).resolve();e.copy_baseline(self.c);self.io=t.FakeIO();self.io.fault=fault
                self.runner=e.Runner(t.POLICY,self.c,t.PB,t.PACKAGE,self.io)
                with self.assertRaises(BaseException):self.run_stage('first_xinput_boot')
                self.assertTrue((self.c/'terminal.json').exists())
                self.assertFalse((self.c/'first_xinput_boot/result.json').exists())
    def test_preservation_failures_stop(self):
        for fault in ('payload_change','payload_schema_change','Config_change','directory_change','wrong_id','wrong_revision','READ_token','READ_error','READ_recovery','unsupported','cross_family','bad_legacy','native53_change','recovery','duplicate_frame','malformed_COBS'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory(prefix='glyph-cont-preserve-negative-') as tmp:
                self.c=Path(tmp).resolve();e.copy_baseline(self.c);self.io=t.FakeIO()
                self.runner=e.Runner(t.POLICY,self.c,t.PB,t.PACKAGE,self.io);self.first_and_visual();self.io.fault=fault
                with self.assertRaises(BaseException):self.run_stage('post_snapshot')
                self.assertTrue((self.c/'terminal.json').exists())
                self.assertFalse((self.c/'post_snapshot/result.json').exists())
                self.assertLessEqual(len(self.io.writes),35)
    def test_visual_failure_terminal(self):
        self.run_stage('first_xinput_boot');event=t.owner_event('display');event['viewer_name']='wrong'
        with self.assertRaises(ValueError):self.run_stage('display',event)
        self.assertTrue((self.c/'terminal.json').exists())
    def test_actual_cli_preflight_failure_terminal_no_resume(self):
        e.save(self.c,'begin-claim.json',{'continuation_id':e.ID})
        with patch.object(e,'EPISODE',self.c),patch.object(e.v2.sys,'argv',['executor.py','check']),patch.object(e,'verify',side_effect=ValueError('changed')):
            with self.assertRaises(ValueError):e.main()
        self.assertTrue((self.c/'terminal.json').exists())
        with patch.object(e,'EPISODE',self.c),patch.object(e.v2.sys,'argv',['executor.py','check']),patch.object(e,'verify') as restored:
            with self.assertRaises(ValueError):e.main()
            restored.assert_not_called()
    def test_actual_cli_complete_remaining_sequence(self):
        destination=self.c/'cli-episode'
        receipt={'owner_directive':True,'owner_message_reference':'OFFLINE_TEST_DOUBLE_NOT_OWNER_APPROVAL',
                 'continuation_id':e.ID,'manifest_sha256':e.digest((HERE/'MANIFEST.json').read_bytes()),
                 **{k:e.load(HERE/'INHERITED.json')[k] for k in ('v2_terminal_commit','built_source_sha','uf2_sha256')}}
        authority=self.c/'test-authority.json';authority.write_text(json.dumps(receipt))
        with patch.object(e,'EPISODE',destination),patch.object(e,'verify',return_value=(t.POLICY,t.PB,t.PACKAGE)), \
             patch.object(e.v2,'LiveIO',return_value=self.io),contextlib.redirect_stdout(io.StringIO()):
            with patch.object(e.v2.sys,'argv',['executor.py','begin','--authority',str(authority)]):e.main()
            for name in e.STAGES:
                self.io.stage=name
                event=self.c/(name+'-event.json');event.write_text(json.dumps(t.owner_event(name)))
                with patch.object(e.v2.sys,'argv',['executor.py',name,'--authority',str(authority),'--owner-event',str(event)]):e.main()
        self.assertEqual(len(self.io.writes),36)
        self.assertTrue((destination/'finish/result.json').exists())
        self.assertFalse((destination/'install').exists())

    def test_original_v2_seal_hashes_are_enforced_before_dependency_verification(self):
        original_load=e.load
        for field in ('sealed_v2_packet_sha256','sealed_v2_preparation_sha256'):
            manifest=original_load(HERE/'MANIFEST.json');manifest['files']={};manifest[field]='0'*64
            def test_load(path):
                return manifest if Path(path)==HERE/'MANIFEST.json' else original_load(path)
            with self.subTest(field=field),patch.object(e,'load',side_effect=test_load), \
                 patch.object(e.v2,'verify_preparation') as old_verifier:
                with self.assertRaises(ValueError):e.verify()
                old_verifier.assert_not_called()

    def test_operation_limits_and_authority(self):
        with self.assertRaises(ValueError):e.authorize({'owner_directive':False})
        self.runner.count=34
        with self.assertRaises(ValueError):self.runner.exchange(None,self.c,'READ',9,b'',1)
        self.first_and_visual()
        with self.assertRaises((ValueError,FileNotFoundError)):self.runner.execute('finish',t.owner_event('finish'))

if __name__=='__main__':unittest.main(verbosity=2)
