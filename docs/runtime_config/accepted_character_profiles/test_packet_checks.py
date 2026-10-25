#!/usr/bin/env python3
"""Synthetic offline tests for exact rename/delete packet guards. No device I/O."""
import base64,copy,hashlib,importlib.util,json,sys,tempfile,unittest,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('accepted_packet_checks',Path(__file__).with_name('packet_checks.py'));check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
import glyph_native_profile_json as codec
PB=check.PB;JF=check.JF

def write_json(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def write_response(path,m):write_json(path,{'response':JF.MessageToDict(m,preserving_proto_field_name=True)})

class PacketTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='accepted-packet-synthetic-');self.work=Path(self.temp.name)
  self.records={}
  for ident,e in check.EXPECTED.items():
   p=PB.UltimateProfile();p.ParseFromString(codec.compile_profile(codec.load_json(ROOT/e['source_path'])))
   self.records[ident]={'name':e['name'],'rank':e['rank'],'revision':e['revision'],'profile':p}
  self.records[42]={'name':'Unrelated legacy preserved','rank':400,'revision':7,'profile':PB.UltimateProfile(schema_version=1)}
  self.initial=self.capture('initial',self.records,51,100,2**61)
  self.safe=self.capture('safe',self.records,27,100,2**61)
 def tearDown(self):self.temp.cleanup()
 def config(self,reference):
  c=PB.Config(ultimate_profile_root_format=2,ultimate_profile_store_format=1,ultimate_profile_store_incarnation=1,default_backend_config=1,default_usb_backend_config=2)
  m=c.game_mode_configs.add(mode_id=PB.MODE_ULTIMATE,ultimate_profile_engine=1,ultimate_profile_id=reference)
  for r in codec.load_json(ROOT/'profiles/kazuya/Kazuya.profile.json')['preprocessing']['remaps']:m.button_remapping.add(physical_button=getattr(PB,'BTN_'+r['physical']),activates=getattr(PB,'BTN_'+r['activates']))
  for a,b in [('LF3','LF1'),('LF5','LF2')]:m.socd_pairs.add(button_dir1=getattr(PB,'BTN_'+a),button_dir2=getattr(PB,'BTN_'+b),socd_type=PB.SOCD_2IP)
  c.communication_backend_configs.add(backend_id=PB.COMMS_BACKEND_GAMECUBE,default_mode_config=1)
  c.communication_backend_configs.add(backend_id=PB.COMMS_BACKEND_XINPUT,default_mode_config=1)
  return c
 def capture(self,name,records,reference,generation,token):
  d=self.work/name;d.mkdir();c=self.config(reference);raw=c.SerializeToString(deterministic=True);cfg=zlib.crc32(raw)
  def response(**kw):return PB.ProfileStoreResponse(protocol_version=2,mutation_protocol_version=2,status=PB.PROFILE_STORE_OK,store_incarnation=1,store_generation=generation,config_generation=cfg,**kw)
  status=response(transaction_token_high_water=token,mutation_feasible=True,admissible_profiles=30)
  write_response(d/'status-start.json',status);write_response(d/'status-end.json',status)
  write_json(d/'identity.json',{'context':'configurator','status':'configurator','primary_backend':8})
  write_json(d/'config.json',{'rawConfigPayloadBase64':base64.b64encode(raw).decode()})
  listing=response()
  for ident,e in records.items():
   listing.entries.add(profile_id=ident,name=e['name'],display_rank=e['rank'],revision=e['revision'],payload_version=e['profile'].schema_version)
   r=response(profile_id=ident,profile_revision=e['revision']);r.profile.CopyFrom(e['profile']);write_response(d/('read-'+str(ident)+'.json'),r)
  write_response(d/'list-0.json',listing);return d
 def operation(self,before,records,action,step):
  plan=check.prepare_action(before,action);kind,ident,name=check.ACTIONS[action];out=copy.deepcopy(records)
  if kind=='rename':out[ident]['name']=name
  else:del out[ident]
  after=self.capture('after'+str(step),out,27,plan['store_generation']+1,plan['token'])
  q=PB.ProfileStoreRequest(protocol_version=2,operation=PB.PROFILE_STORE_RENAME if kind=='rename' else PB.PROFILE_STORE_DELETE,profile_id=ident,request_token=plan['token'],expected_store_incarnation=1,expected_store_generation=plan['store_generation'])
  if name:q.name=name
  receipt=self.work/('request'+str(step)+'.json');self.receipt(receipt,q)
  cfg=check.read_snapshot(after)[0]['fences'][2]
  result=PB.ProfileStoreResponse(protocol_version=2,mutation_protocol_version=2,status=PB.PROFILE_STORE_OK,request_token=plan['token'],profile_id=ident,profile_revision=out[ident]['revision'] if kind=='rename' else 0,store_incarnation=1,store_generation=plan['store_generation']+1,config_generation=cfg)
  resultpath=self.work/('result'+str(step)+'.json');write_response(resultpath,result)
  return after,out,receipt,resultpath,q,result
 def receipt(self,path,q):
  raw=q.SerializeToString(deterministic=True);write_json(path,{'receipt_format':1,'mode':'production_acceptance','incarnation':1,'request_hex':raw.hex(),'request_sha256':hashlib.sha256(raw).hexdigest()})
 def test_exact_five_operation_chain_and_unknown_preservation(self):
  a,c=check.read_snapshot(self.initial);check.require_original(a);check.compare_selection(self.initial,self.safe)
  before=self.safe;records=self.records
  for step,action in enumerate(['rename27','delete48','rename51','delete49','delete50']):
   after,records,receipt,result,q,r=self.operation(before,records,action,step)
   check.compare_mutation(before,after,receipt,result,action);before=after
  result=check.compare_final(self.safe,before)
  self.assertEqual(result['native_menu'],['Pikachu','Kazuya']);self.assertEqual(records[42]['name'],'Unrelated legacy preserved')
  self.assertEqual(records[27]['revision'],1);self.assertEqual(records[51]['revision'],1)
 def test_referenced_or_unknown_delete_never_planned(self):
  with self.assertRaises(ValueError):check.prepare_action(self.initial,'delete48') # Not yet safely returned.
  refs=self.capture('referenced',self.records,48,100,2**61)
  with self.assertRaises(ValueError):check.require_original(check.read_snapshot(refs)[0])
  with self.assertRaises(ValueError):check.prepare_action(self.safe,'delete42')
 def test_previous_checkpoint_drift_blocks_next_operation(self):
  same=self.capture('safe-same',self.records,27,100,2**61);check.compare_preserve(self.safe,same)
  records=copy.deepcopy(self.records);records[42]['name']='Concurrent legacy change'
  changed=self.capture('safe-drift',records,27,101,2**61+1)
  with self.assertRaises(ValueError):check.compare_preserve(self.safe,changed)
 def test_unknown_native_stops_instead_of_deleting(self):
  records=copy.deepcopy(self.records);records[99]=copy.deepcopy(records[49]);records[99]['name']='KazTest999'
  unknown=self.capture('unknown-native',records,27,100,2**61)
  with self.assertRaises(ValueError):check.read_snapshot(unknown)
 def test_payload_rank_revision_and_name_drift_stop(self):
  for index,change in enumerate(['payload','rank','revision','name']):
   records=copy.deepcopy(self.records)
   if change=='payload':
    data=bytearray(records[51]['profile'].native_payload);data[96]=62;records[51]['profile'].native_payload=bytes(data)
   elif change=='rank':records[51]['rank']+=1
   elif change=='revision':records[51]['revision']+=1
   else:records[51]['name']='Unapproved name'
   d=self.capture('drift'+str(index),records,27,100,2**61)
   with self.assertRaises(ValueError):check.read_snapshot(d)
 def test_wrong_operation_hidden_payload_and_wrong_identity_rejected(self):
  after,records,receipt,result,q,r=self.operation(self.safe,self.records,'rename51',8)
  for index,edit in enumerate(['update','id','payload','rank','fault']):
   bad=PB.ProfileStoreRequest();bad.CopyFrom(q)
   if edit=='update':bad.operation=PB.PROFILE_STORE_UPDATE
   elif edit=='id':bad.profile_id=27
   elif edit=='payload':bad.profile.CopyFrom(self.records[51]['profile'])
   elif edit=='rank':bad.display_rank=154
   else:bad.fault_ticket=1
   path=self.work/('bad-request'+str(index)+'.json');self.receipt(path,bad)
   with self.assertRaises(ValueError):check.compare_mutation(self.safe,after,path,result,'rename51')
 def test_response_uncertainty_and_accounting_stop(self):
  after,records,receipt,result,q,r=self.operation(self.safe,self.records,'rename27',9)
  for index,field in enumerate(['profile_id','request_token','profile_revision','store_generation','status']):
   bad=PB.ProfileStoreResponse();bad.CopyFrom(r)
   setattr(bad,field,PB.PROFILE_STORE_CONFLICT if field=='status' else getattr(bad,field)+1)
   path=self.work/('bad-response'+str(index)+'.json');write_response(path,bad)
   with self.assertRaises(ValueError):check.compare_mutation(self.safe,after,receipt,path,'rename27')
 def test_unrelated_metadata_change_fails_preservation(self):
  after,records,receipt,result,q,r=self.operation(self.safe,self.records,'rename27',10)
  records[42]['name']='Unexpected other change';bad=self.capture('other-change',records,27,101,2**61+1)
  with self.assertRaises(ValueError):check.compare_mutation(self.safe,bad,receipt,result,'rename27')
 def test_health_crc_and_torn_snapshot_stop(self):
  for index,field in enumerate(['recovery_flags','mutation_feasible','store_generation','config_generation']):
   d=self.capture('bad-state'+str(index),self.records,27,100,2**61)
   r=check.response(d/'status-end.json');setattr(r,field,False if field=='mutation_feasible' else getattr(r,field)+1);write_response(d/'status-end.json',r)
   with self.assertRaises(ValueError):check.read_snapshot(d)

if __name__=='__main__':unittest.main(verbosity=2)
