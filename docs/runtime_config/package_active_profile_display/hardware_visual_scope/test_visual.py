"""Offline tests of actual visual evidence processor; no controller access."""
from pathlib import Path
import importlib.util,json,tempfile,unittest,contextlib,io
from unittest.mock import patch
HERE=Path(__file__).resolve().parent

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=module('visual_scope',HERE/'accept_visual.py')
t=module('adapter_fixtures',HERE.parent/'hardware_continuation_v2/test_executor.py')
e=v.e

class VisualTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='glyph-visual-offline-');self.root=Path(self.tmp.name).resolve()
        e.copy_baseline(self.root);self.io=t.t.FakeIO();self.runner=e.Runner(t.t.POLICY,self.root,t.t.PB,t.t.PACKAGE,self.io)
        self.receipt={'owner_scope_correction':True,'owner_message_reference':'OFFLINE_TEST_DOUBLE','scope_manifest_sha256':e.digest((HERE/'MANIFEST.json').read_bytes()),'continuation_id':e.ID,'viewer_name_result':'NOT_VISIBLE_NOT_VERIFIED'}
        self.guard=patch.object(e.v2.LiveIO,'ports',side_effect=AssertionError('NO_REAL_DEVICE_ACCESS'));self.guard.start()
        self.stage('first_xinput_boot')
    def tearDown(self):self.guard.stop();self.tmp.cleanup()
    def stage(self,name):
        self.io.stage=name;event=t.t.owner_event(name)
        if 'xinput' in name:event['xinput_screen_confirmed']=True
        return self.runner.execute(name,event)
    def event(self):
        return {'owner_present':True,'owner_message_reference':'OFFLINE_TEST_DOUBLE','dashboard_name':'KazTest5','plate':'Unknown Plate','backend':'XInput','responsive':True,'viewer_opened':True,'returned_dashboard':True,'viewer_name_result':'NOT_VISIBLE_NOT_VERIFIED'}
    def apply(self,stage,event=None):return v.apply(t.t.POLICY,t.t.PB,t.t.PACKAGE,self.root,stage,event or self.event(),self.receipt)
    def test_actual_full_scope_preservation_sequence(self):
        self.apply('display');self.stage('post_snapshot');self.stage('final_xinput_boot');result=self.apply('finish')
        self.assertEqual((len(self.io.writes),self.io.opens,self.io.closes),(36,3,3))
        self.assertFalse(result['visible_viewer_name_PASS'])
        self.assertEqual(result['viewer_name_result'],'NOT_VISIBLE_NOT_VERIFIED')
        self.assertEqual(result['new_controller_exchanges'],36)
    def test_actual_cli_display_and_finish(self):
        authority={'owner_directive':True,'owner_message_reference':'OFFLINE_TEST_DOUBLE','continuation_id':e.ID,'manifest_sha256':e.digest((e.HERE/'MANIFEST.json').read_bytes()),**{k:e.load(e.HERE/'INHERITED.json')[k] for k in ('v2_terminal_commit','built_source_sha','uf2_sha256')}}
        e.save(self.root,'begin-claim.json',{'continuation_id':e.ID});e.save(self.root,'authority.json',authority)
        for name,value in (('authority-input.json',authority),('scope-input.json',self.receipt),('event-input.json',self.event())):e.save(self.root,name,value)
        with patch.object(e,'EPISODE',self.root),patch.object(v,'verify',return_value=(t.t.POLICY,t.t.PB,t.t.PACKAGE)),contextlib.redirect_stdout(io.StringIO()):
            for name in ('display','finish'):
                if name=='finish':self.stage('post_snapshot');self.stage('final_xinput_boot')
                argv=['accept_visual.py',name,'--authority',str(self.root/'authority-input.json'),'--scope-directive',str(self.root/'scope-input.json'),'--owner-event',str(self.root/'event-input.json')]
                with patch.object(e.v2.sys,'argv',argv):v.main()
        self.assertFalse(e.load(self.root/'finish/result.json')['visible_viewer_name_PASS'])
    def test_bad_visual_reports_terminal(self):
        for field,value in (('dashboard_name','wrong'),('plate','wrong'),('backend','wrong'),('responsive',False),('viewer_opened',False),('returned_dashboard',False),('viewer_name_result','KazTest5')):
            with self.subTest(field=field),tempfile.TemporaryDirectory(prefix='glyph-visual-negative-') as tmp:
                root=Path(tmp).resolve();e.copy_baseline(root)
                # Explicit settled predecessor fixture; does not simulate hardware truth.
                (root/'first_xinput_boot').mkdir();e.save(root/'first_xinput_boot','result.json',{'result':'PASS'});e.save(root/'first_xinput_boot','settlement.json',{'port_closed':True})
                event=self.event();event[field]=value
                with self.assertRaises(ValueError):v.apply(t.t.POLICY,t.t.PB,t.t.PACKAGE,root,'display',event,self.receipt)
                self.assertTrue((root/'terminal.json').exists());self.assertFalse((root/'display/result.json').exists())
    def test_no_controller_stage_or_invented_name(self):
        with self.assertRaises(ValueError):self.apply('post_snapshot')
        self.assertEqual(len(self.io.writes),1)
    def test_finish_requires_settled_final_and_exact_count(self):
        self.apply('display')
        with self.assertRaises((ValueError,OSError)):self.apply('finish')
        self.assertFalse((self.root/'finish/result.json').exists())
    def test_scope_authority_required(self):
        v.authorize(self.receipt)
        for key,value in (('owner_scope_correction',False),('scope_manifest_sha256','0'*64),('viewer_name_result','KazTest5')):
            receipt=dict(self.receipt);receipt[key]=value
            with self.assertRaises(ValueError):v.authorize(receipt)

if __name__=='__main__':unittest.main(verbosity=2)
