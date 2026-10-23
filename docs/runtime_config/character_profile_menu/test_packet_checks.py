#!/usr/bin/env python3
"""Offline retained-capture and negative-control tests. Never opens a controller."""
import base64, contextlib, copy, hashlib, importlib.util, io, json, tempfile, unittest, zlib, sys
from unittest.mock import patch
from pathlib import Path
P=Path(__file__).with_name('packet_checks.py');spec=importlib.util.spec_from_file_location('packet_checks',P);pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
PB,JF=pc.PB,pc.JF
PRIVATE=Path('/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-acceptance/GP_NATIVE_002_GC_LIVENESS_HW_V1_20261023/posttest_configurator')

def read_response(p):
 m=PB.ProfileStoreResponse();JF.ParseDict(json.loads(p.read_text())['response'],m);return m
BASE=read_response(PRIVATE/'status.json');CFG=PB.Config();CFG.ParseFromString(base64.b64decode(json.loads((PRIVATE/'config_backup.json').read_text())['rawConfigPayloadBase64']))
RECORDS={}
for page in range(0,48,8):
 for e in read_response(PRIVATE/f'list_{page}.json').entries:
  profile=read_response(PRIVATE/f'profile_{e.profile_id}.json').profile;RECORDS[e.profile_id]=(copy.deepcopy(e),copy.deepcopy(profile))

def wire(p,m):p.write_text(json.dumps({'response':JF.MessageToDict(m,preserving_proto_field_name=True)}))
def stage(p,c,records,g,h):
 p.mkdir();(p/'identity.json').write_text(json.dumps({'context':'configurator','status':'configurator','primary_backend':8}));s=copy.deepcopy(BASE);s.store_generation=g;s.transaction_token_high_water=h;raw=c.SerializeToString(deterministic=True);s.config_generation=zlib.crc32(raw)
 wire(p/'status-start.json',s);wire(p/'status-end.json',s);(p/'config.json').write_text(json.dumps({'rawConfigPayloadBase64':base64.b64encode(raw).decode()}))
 ids=list(records)
 for cursor in range(0,len(ids),8):
  r=PB.ProfileStoreResponse(protocol_version=2,mutation_protocol_version=2,status=PB.PROFILE_STORE_OK,store_incarnation=s.store_incarnation,store_generation=g,config_generation=s.config_generation,next_page_cursor=cursor+8 if cursor+8<len(ids) else 0)
  for ident in ids[cursor:cursor+8]:r.entries.add().CopyFrom(records[ident][0])
  wire(p/f'list-{cursor}.json',r)
 for ident,(e,profile) in records.items():
  r=PB.ProfileStoreResponse(protocol_version=2,mutation_protocol_version=2,status=PB.PROFILE_STORE_OK,store_incarnation=s.store_incarnation,store_generation=g,config_generation=s.config_generation,profile_id=ident,profile_revision=e.revision);r.profile.CopyFrom(profile);wire(p/f'read-{ident}.json',r)
 snap,_=pc.audit(p);(p/'snapshot.json').write_text(json.dumps(snap));return snap

def receipt(p,q,g,ident,revision=0):
 raw=q.SerializeToString(deterministic=True);rq=p.with_suffix('.request.json');rr=p.with_suffix('.result.json');rq.write_text(json.dumps({'request_hex':raw.hex(),'request_sha256':hashlib.sha256(raw).hexdigest()}));r=PB.ProfileStoreResponse(protocol_version=2,mutation_protocol_version=2,status=PB.PROFILE_STORE_OK,store_incarnation=q.expected_store_incarnation,store_generation=g,request_token=q.request_token,profile_id=ident,profile_revision=revision);wire(rr,r);return rq,rr

class PacketChecks(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name);self.c=copy.deepcopy(CFG);self.g=BASE.store_generation;self.h=BASE.transaction_token_high_water;self.a=self.p/'a';self.x=stage(self.a,self.c,RECORDS,self.g,self.h)
 def tearDown(self):self.t.cleanup()
 def rejected(self,fn):
  with self.assertRaises((ValueError,KeyError)):fn()
 def ref(self):
  c=copy.deepcopy(self.c);q=PB.ProfileStoreRequest(protocol_version=2,operation=PB.PROFILE_STORE_SET_MODE_REFERENCE,expected_store_incarnation=self.x['incarnation'],expected_store_generation=self.g,expected_config_generation=self.x['config_generation'],request_token=self.h+1,profile_id=27,mode_config_index=2);z=copy.deepcopy(q);z.request_token=0
  c.game_mode_configs[2].ultimate_profile_id=27;c.profile_reference_token=q.request_token;c.profile_reference_digest=hashlib.sha256(b'Glyph.ProfileStore.Request.v1\0'+z.SerializeToString(deterministic=True)).digest();c.profile_reference_result_id=27;c.profile_reference_result_mode_index=2;c.profile_reference_result_store_generation=self.g
  b=self.p/'ref';stage(b,c,RECORDS,self.g,self.h+1);rq,rr=receipt(self.p/'ref-op',q,self.g,27);pc.compare(self.a,b,'reference',rq,rr);return b,c,rq,rr
 def test_full_retained_snapshot_and_preserve(self):
  self.assertEqual(len(self.x['records']),43);b=self.p/'preserve';stage(b,self.c,RECORDS,self.g,self.h);pc.compare(self.a,b,'preserve')
 def test_identity_and_context_negatives(self):
  for field,value in [('name','unowned'),('revision','2')]:
   r=json.loads((self.a/'list-24.json').read_text());r['response']['entries'][0][field]=value;(self.a/'list-24.json').write_text(json.dumps(r));self.rejected(lambda:pc.audit(self.a));stage2=self.p/(field+'-new');stage(stage2,self.c,RECORDS,self.g,self.h);self.a=stage2
  c=copy.deepcopy(self.c);c.game_mode_configs[2].socd_pairs.clear();self.rejected(lambda:stage(self.p/'context',c,RECORDS,self.g,self.h))
 def test_crc_status_drift_and_recovery(self):
  s=read_response(self.a/'status-end.json');s.store_generation+=1;wire(self.a/'status-end.json',s);self.rejected(lambda:pc.audit(self.a))
  s=copy.deepcopy(BASE);s.recovery_flags=1;wire(self.a/'status-start.json',s);self.rejected(lambda:pc.status(self.a/'status-start.json'))
  s.recovery_flags=0;s.config_generation^=1;wire(self.a/'status-start.json',s);self.rejected(lambda:pc.config(self.a/'config.json',s))
  (self.a/'identity.json').write_text(json.dumps({'context':'configurator','status':'recovery','primary_backend':8}));self.rejected(lambda:pc.audit(self.a))
 def test_safe_selection_and_no_arithmetic_digest_assumption(self):
  b,c,rq,rr=self.ref();c2=copy.deepcopy(c);c2.default_usb_backend_config=1;c2.communication_backend_configs[0].default_mode_config=3;after=self.p/'selected';stage(after,c2,RECORDS,self.g,self.h+1);pc.compare(b,after,'selection',mode=2)
  self.assertEqual(pc.snapshot(b)['config_generation'],pc.snapshot(after)['config_generation'])
  bad=copy.deepcopy(c2);bad.rgb_brightness+=1;d=self.p/'unexpected';stage(d,bad,RECORDS,self.g,self.h+1);self.rejected(lambda:pc.compare(b,d,'selection',mode=2))
 def test_reference_receipt_token_and_payload_digest_negatives(self):
  b,c,rq,rr=self.ref();r=read_response(rr);r.profile_id=28;wire(rr,r);self.rejected(lambda:pc.compare(self.a,b,'reference',rq,rr))
  q=pc.request_receipt(rq);receipt(self.p/'ref-op',q,self.g,27);c.profile_reference_digest=b'x'*32;d=self.p/'bad-digest';stage(d,c,RECORDS,self.g,self.h+1);self.rejected(lambda:pc.compare(self.a,d,'reference',rq,rr))
 def test_twenty_delete_accounting_create_and_preservation(self):
  b,c,_,_=self.ref();records=copy.deepcopy(RECORDS);ops=self.p/'ops';ops.mkdir();h=self.h+1
  for off,ident in enumerate(sorted(pc.SEL),1):
   q=PB.ProfileStoreRequest(protocol_version=2,operation=PB.PROFILE_STORE_DELETE,expected_store_incarnation=self.x['incarnation'],expected_store_generation=self.g+off-1,request_token=h+off,profile_id=ident);receipt(ops/f'delete-{ident}',q,self.g+off,ident);s=copy.deepcopy(BASE);s.store_generation=self.g+off;s.transaction_token_high_water=h+off;s.config_generation=pc.snapshot(b)['config_generation'];wire(ops/f'delete-{ident}.post.json',s);del records[ident]
  after=self.p/'deleted';xs=stage(after,c,records,self.g+20,h+20);pc.compare(b,after,'deletes',ops)
  rnk=pc.rank(xs);self.assertGreater(rnk,records[27][0].display_rank);self.assertNotIn(rnk,[e.display_rank for e,_ in records.values()])
  new_id=4001;e=copy.deepcopy(records[27][0]);e.profile_id=new_id;e.name='Kazuya';e.display_rank=rnk;e.revision=1;records[new_id]=(e,copy.deepcopy(pc.KAZUYA));q=PB.ProfileStoreRequest(protocol_version=2,operation=PB.PROFILE_STORE_CREATE,expected_store_incarnation=self.x['incarnation'],expected_store_generation=self.g+20,request_token=h+21,name='Kazuya',display_rank=rnk);q.profile.CopyFrom(pc.KAZUYA);rq,rr=receipt(self.p/'create',q,self.g+21,new_id,1);final=self.p/'created';stage(final,c,records,self.g+21,h+21);pc.compare(after,final,'create',rq,rr)
  q.display_rank=0;receipt(self.p/'bad-create',q,self.g+21,new_id,1);self.rejected(lambda:pc.compare(after,final,'create',self.p/'bad-create.request.json',self.p/'bad-create.result.json'))
  s=read_response(ops/'delete-35.post.json');s.store_generation+=1;wire(ops/'delete-35.post.json',s);self.rejected(lambda:pc.compare(b,after,'deletes',ops))
 def test_single_delete_preflight_continuity_and_no_skip(self):
  b,c,_,_=self.ref();d=self.p/'delete-pre';stage(d,c,RECORDS,self.g,self.h+1)
  def invoke(ident):
   with patch.object(sys,'argv',['packet_checks.py','one',str(d),str(b),'--id',str(ident),'--previous-status',str(b/'status-end.json')]):pc.main()
  invoke(28);self.rejected(lambda:invoke(29))
  r=read_response(d/'list-0.json');r.entries[0].name='unexpected';wire(d/'list-0.json',r);self.rejected(lambda:invoke(28))
  r=read_response(d/'status-start.json');r.store_generation+=1;wire(d/'status-start.json',r);self.rejected(lambda:invoke(28))
 def test_exact_runtime_identity_and_no_gamecube_inference(self):
  b,c,_,_=self.ref();i={'context':'xinput','status':'persisted','primary_backend':2,'active_id':27,'requested_reference':27,'active_revision':1,'schema_version':5,'incarnation':self.x['incarnation'],'context_row':2,'payload_sha256':pc.payload_digest(RECORDS[27][1])};f=self.p/'identity.json';f.write_text(json.dumps(i))
  def invoke():
   with patch.object(sys,'argv',['packet_checks.py','identity',str(b),str(f),'--mode','2']):pc.main()
  invoke();i['primary_backend']=3;f.write_text(json.dumps(i));self.rejected(invoke)
 def test_rank_exhaustion_and_payload_mutant(self):
  x=copy.deepcopy(self.x);x['records']={k:v for k,v in x['records'].items() if int(k) not in pc.SEL};x['records']['27']['rank']=0xffffffff;self.rejected(lambda:pc.rank(x))
  records=copy.deepcopy(RECORDS);e,pr=records[27];pr.native_payload=pr.native_payload[:-1]+bytes([pr.native_payload[-1]^1]);self.rejected(lambda:stage(self.p/'bad-golden',self.c,records,self.g,self.h))

if __name__=='__main__':unittest.main()
