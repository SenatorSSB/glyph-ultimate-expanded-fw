#!/usr/bin/env python3
"""Offline accepted-character packet checks/plans. Never opens a port or sends I/O.

Only the unchanged production tool transmits protocol operations. This module
validates saved reads, exact identities, Config references, receipts and deltas.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import zlib
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import glyph_serial_config_tool as transport
import glyph_profile_store_production_tool as production
from convert_glyph_native_ultimate_profile import validate_standalone_profile,preprocessing_bytes
PB,JF,_=transport.load_runtime_proto_modules(ROOT)
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'CONTROLLER_PLAN.json').read_text())
EXPECTED={int(x['id']):x for x in PLAN['native_records']}
DELETE_IDS={x for x,r in EXPECTED.items() if r['disposition']=='DELETE_SUPERSEDED'}
ACTIONS={'rename27':('rename',27,'Pikachu'),'rename51':('rename',51,'Kazuya'),'delete48':('delete',48,None),'delete49':('delete',49,None),'delete50':('delete',50,None)}
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def response(p):
 data=load(p);m=PB.ProfileStoreResponse();JF.ParseDict(data.get('response',data),m,ignore_unknown_fields=False)
 need(m.protocol_version==2 and m.mutation_protocol_version==2 and m.status==PB.PROFILE_STORE_OK,'nonproduction/non-OK saved response '+str(p));return m
def state(s):return [s.store_incarnation,s.store_generation,s.config_generation,s.transaction_token_high_water]
def status(p):
 s=response(p);production.verify_production_status(argparse.Namespace(action='status'),PB,s)
 need(s.store_incarnation>0 and not s.recovery_flags and s.mutation_feasible,'unhealthy/recovery/uncertain/not mutation-admissible')
 need(s.store_generation<0xffffffff and s.transaction_token_high_water<0xfffffffffffffffe,'store generation/token exhaustion')
 return s
def read_directory(d,start):
 cursor=0;visited=set();entries={}
 while True:
  need(cursor not in visited and len(visited)<9,'LIST cycle/page bound');visited.add(cursor);r=response(d/('list-'+str(cursor)+'.json'))
  need(state(r)[:3]==state(start)[:3],'LIST fence drift')
  for e in r.entries:
   need(e.profile_id>0 and e.profile_id not in entries,'duplicate/zero directory ID')
   entries[e.profile_id]={'id':e.profile_id,'name':e.name,'rank':e.display_rank,'revision':e.revision,'payload_version':e.payload_version}
  cursor=r.next_page_cursor
  if not cursor:break
 need(0<len(entries)<=64,'directory extent invalid')
 return entries

def read_snapshot(directory):
 d=Path(directory);start=status(d/'status-start.json');endfile=d/'status-end.json'
 if not endfile.exists():endfile=d/'end/status.json'
 end=status(endfile);need(state(start)==state(end),'state drift while read-only capture was taken')
 identity=load(d/'identity.json');need(identity.get('context')=='configurator' and identity.get('status')=='configurator' and identity.get('primary_backend')==8,'normal Configurator identity absent')
 data=load(d/'config.json');raw=base64.b64decode(data['rawConfigPayloadBase64'],validate=True);need(zlib.crc32(raw)==start.config_generation,'Config CRC/status mismatch')
 config=PB.Config();config.ParseFromString(raw)
 need(config.ultimate_profile_root_format==2 and config.ultimate_profile_store_format==1 and not config.ultimate_profiles,'not compact production Config')
 need(config.ultimate_profile_store_incarnation==start.store_incarnation,'Config/store incarnation mismatch')
 need(0<len(config.game_mode_configs)<=30 and 0<len(config.communication_backend_configs)<=15,'Config extent invalid')
 for b in config.communication_backend_configs:need(0<b.default_mode_config<=len(config.game_mode_configs),'backend default invalid')
 need(0<config.default_backend_config<=len(config.communication_backend_configs) and 0<config.default_usb_backend_config<=len(config.communication_backend_configs),'Config default backend invalid')
 entries=read_directory(d,start)
 records={};profiles={}
 for ident,e in entries.items():
  r=response(d/('read-'+str(ident)+'.json'));need(state(r)[:3]==state(start)[:3] and r.profile_id==ident and r.profile_revision==e['revision'],'READ fence/ID/revision mismatch')
  validate_standalone_profile(r.profile,PB);wire=r.profile.SerializeToString(deterministic=True)
  profiles[ident]=r.profile;records[str(ident)]={**e,'schema':r.profile.schema_version,'wrapper_sha256':sha(wire),'body_sha256':sha(r.profile.native_payload) if r.profile.schema_version==5 else None}
  need((e['payload_version']==5)==(r.profile.schema_version==5),'directory/READ native classification mismatch')
 refs={}
 for i,m in enumerate(config.game_mode_configs):
  if m.ultimate_profile_id:
   need(m.mode_id==PB.MODE_ULTIMATE and m.ultimate_profile_id in profiles,'dangling/wrong-mode Config reference');refs.setdefault(str(m.ultimate_profile_id),[]).append(i)
  if m.ultimate_profile_engine==1:
   need(m.ultimate_profile_id in profiles and profiles[m.ultimate_profile_id].schema_version==5,'native context not backed by native record')
   need(sha(preprocessing_bytes(m,PB))==profiles[m.ultimate_profile_id].native_payload[28:60].hex(),'native context preprocessing mismatch')
 native={int(k) for k,r in records.items() if r['schema']==5}
 need({27,51}<=native,'accepted native IDs absent');need(native<=set(EXPECTED),'unknown/unapproved native record: reconcile before two-profile cleanup')
 for ident in native:
  r=records[str(ident)];expected=EXPECTED[ident]
  for key in ['rank','revision','schema','wrapper_sha256','body_sha256']:need(r[key]==expected[key],'exact known profile drift ID'+str(ident)+' '+key)
  names=[expected['name']]+([expected['target_name']] if 'target_name' in expected else [])
  need(r['name'] in names,'unexpected metadata name ID'+str(ident))
  need(profiles[ident].native_payload[28:60].hex()==expected['preprocessing_sha256'],'preprocessing drift ID'+str(ident))
  need(profiles[ident].native_payload[60:92].hex()==expected['provenance_sha256'],'provenance drift ID'+str(ident))
 return {'fences':state(end),'records':records,'native_ids':sorted(native),'references':refs,'config_raw_sha256':sha(raw),'config_raw_hex':raw.hex(),'record_count':len(records),'private_capture':str(d.resolve())},config

def require_original(s):
 need(set(s['native_ids'])==set(EXPECTED),'initial native inventory changed')
 for ident,e in EXPECTED.items():need(s['records'][str(ident)]['name']==e['name'],'initial name changed; do not replay packet')
 for ident in DELETE_IDS:need(not s['references'].get(str(ident)),'superseded delete candidate referenced; owner must return safely then capture again')
 need(s['fences'][1]<=0xffffffff-5 and s['fences'][3]<=0xfffffffffffffffe-5,'insufficient complete five-operation runway')

def require_safe(s,c):
 for ident in DELETE_IDS:need(not s['references'].get(str(ident)),'never delete a referenced record')
 native_rows=[m for m in c.game_mode_configs if m.ultimate_profile_engine==1]
 need(native_rows and all(m.ultimate_profile_id==27 for m in native_rows),'return to Pikachu ID27 through normal physical selection before mutations')
 backend=c.communication_backend_configs[c.default_backend_config-1]
 need(backend.backend_id==PB.COMMS_BACKEND_GAMECUBE,'safe GameCube default route not established')
 mode=c.game_mode_configs[backend.default_mode_config-1]
 need(mode.mode_id==PB.MODE_ULTIMATE and mode.ultimate_profile_engine==1 and mode.ultimate_profile_id==27,'GameCube default not accepted ID27')

def prepare_action(directory,action):
 need(action in ACTIONS,'operation outside exact approved packet')
 s,c=read_snapshot(directory);require_safe(s,c);kind,ident,name=ACTIONS[action]
 need(str(ident) in s['records'],'planned record absent; never replay uncertain mutation')
 current=s['records'][str(ident)];expected=EXPECTED[ident]
 need(current['name']==expected['name'],'planned record name changed; reconcile instead of retry')
 if kind=='delete':need(ident in DELETE_IDS and not s['references'].get(str(ident)),'not an unreferenced exact superseded candidate')
 inc,gen,cfg,hwm=s['fences'];return {'action':kind,'profile_id':ident,'name':name,'incarnation':inc,'store_generation':gen,'config_generation_observed':cfg,'token':hwm+1,'expected_revision':current['revision'],'preserved_rank':current['rank'],'wrapper_sha256':current['wrapper_sha256'],'body_sha256':current['body_sha256'],'before_capture':str(Path(directory).resolve()),'operation_label':action,'no_retry':True,'payload_in_request':False}

def compare_preserve(before,after):
 a,ca=read_snapshot(before);b,cb=read_snapshot(after)
 need(a['fences']==b['fences'] and a['records']==b['records'] and a['config_raw_hex']==b['config_raw_hex'],'state changed since previous verified checkpoint; no next mutation')

def compare_selection(before,after,backend_id=3):
 a,ca=read_snapshot(before);b,cb=read_snapshot(after);need(a['records']==b['records'],'physical selection changed profiles')
 need(a['fences'][:2]==b['fences'][:2] and a['fences'][3]==b['fences'][3],'physical selection changed store/token state')
 matches=[i for i,m in enumerate(cb.game_mode_configs) if m.mode_id==PB.MODE_ULTIMATE and m.ultimate_profile_engine==1 and m.ultimate_profile_id==27]
 need(len(matches)==1,'ambiguous ID27 selection context');i=matches[0];m=ca.game_mode_configs[i]
 need(m.mode_id==PB.MODE_ULTIMATE and m.ultimate_profile_engine==1,'selection changed template kind')
 m.ultimate_profile_id=27;m.ultimate_profile_engine=1;m.ultimate_profile_config=0
 backends=[j for j,b in enumerate(ca.communication_backend_configs) if b.backend_id==backend_id];need(len(backends)==1,'ambiguous backend for physical selection');j=backends[0]
 ca.communication_backend_configs[j].default_mode_config=i+1
 if backend_id in [PB.COMMS_BACKEND_XINPUT,PB.COMMS_BACKEND_DINPUT,PB.COMMS_BACKEND_NINTENDO_SWITCH]:ca.default_usb_backend_config=j+1
 else:ca.default_backend_config=j+1
 need(ca.SerializeToString(deterministic=True)==cb.SerializeToString(deterministic=True),'physical selection changed unrelated Config fields')
 require_safe(b,cb)

def compare_mutation(before,after,receipt,result,action):
 plan=prepare_action(before,action);a,ca=read_snapshot(before);b,cb=read_snapshot(after);saved=load(receipt);raw=bytes.fromhex(saved['request_hex']);need(sha(raw)==saved['request_sha256'],'request receipt digest mismatch')
 q=PB.ProfileStoreRequest();q.ParseFromString(raw);r=response(result);kind,ident,name=ACTIONS[action]
 need(q.protocol_version==2 and q.operation==(PB.PROFILE_STORE_RENAME if kind=='rename' else PB.PROFILE_STORE_DELETE),'wrong operation')
 need(q.profile_id==ident and q.request_token==plan['token'] and q.expected_store_incarnation==plan['incarnation'] and q.expected_store_generation==plan['store_generation'],'request ID/fence/token mismatch')
 need(not q.HasField('profile') and not q.display_rank and not q.expected_profile_revision and not q.mode_config_index and not q.expected_config_generation,'metadata/delete request carries unsupported payload/rank/revision/Config changes')
 need(q.name==(name or ''),'request name mismatch')
 expected_request=PB.ProfileStoreRequest(protocol_version=2,operation=q.operation,profile_id=ident,request_token=plan['token'],expected_store_incarnation=plan['incarnation'],expected_store_generation=plan['store_generation'])
 if name is not None:expected_request.name=name
 need(q.SerializeToString(deterministic=True)==expected_request.SerializeToString(deterministic=True),'unexpected extra request fields')
 need(saved.get('receipt_format')==1 and saved.get('mode')=='production_acceptance' and saved.get('incarnation')==plan['incarnation'],'receipt not exact production request')
 need(r.profile_id==ident and r.request_token==q.request_token,'returned ID/token mismatch')
 need(state(r)[:3]==b['fences'][:3],'response/store/Config fences disagree')
 need(b['fences']==[plan['incarnation'],plan['store_generation']+1,a['fences'][2],q.request_token],'mutation accounting/config fence mismatch')
 need(a['config_raw_hex']==b['config_raw_hex'],'rename/delete changed raw Config or references')
 expected=dict(a['records'])
 if kind=='rename':
  expected[str(ident)]=dict(expected[str(ident)],name=name)
  need(r.profile_revision==a['records'][str(ident)]['revision'],'RENAME unexpectedly changed payload revision')
 else:
  del expected[str(ident)]
 need(b['records']==expected,'unexpected record/payload/metadata change')
 require_safe(b,cb)

def compare_final(safe,final):
 a,ca=read_snapshot(safe);b,cb=read_snapshot(final);require_original(a);require_safe(a,ca);require_safe(b,cb)
 need(b['native_ids']==[27,51],'final native menu is not exactly two accepted records')
 expected={k:dict(v) for k,v in a['records'].items() if int(k) not in DELETE_IDS}
 expected['27']['name']='Pikachu';expected['51']['name']='Kazuya'
 need(b['records']==expected,'final accepted/unrelated profile preservation mismatch')
 need(a['config_raw_hex']==b['config_raw_hex'],'final raw Config differs from safe ID27 checkpoint')
 need(b['fences']==[a['fences'][0],a['fences'][1]+5,a['fences'][2],a['fences'][3]+5],'five exact metadata/delete operations not accounted')
 return {'status':'PASS_API_PRESERVATION','native_menu':['Pikachu','Kazuya'],'active_native_id':27,'stable_ids':[27,51],'payloads_unchanged':True,'payload_revisions_unchanged':True,'other_records_unchanged':True,'gameplay_retest_required':False,'physical_menu_smoke':'OWNER_REPORT_REQUIRED'}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['audit','plan','compare-selection','compare-mutation','final','cursor','ids','fields','attest','compare-preserve']);parser.add_argument('directory');parser.add_argument('other',nargs='?');parser.add_argument('--original',action='store_true');parser.add_argument('--safe',action='store_true');parser.add_argument('--operation',choices=list(ACTIONS));parser.add_argument('--receipt');parser.add_argument('--result');parser.add_argument('--output',type=Path);a=parser.parse_args()
 if a.action=='attest':
  manifest=load(HERE/'TOOLS_MANIFEST.json');review=load(HERE/'INDEPENDENT_REVIEW.json')
  need(review.get('verdict')=='PASS' and review.get('packet_id')==PLAN['packet_id'],'packet independent review absent')
  need(sha((HERE/'TOOLS_MANIFEST.json').read_bytes())==review['tools_manifest_sha256'],'tool manifest differs from reviewed packet')
  for rel,digest in manifest['files_sha256'].items():need(sha((ROOT/rel).read_bytes())==digest,'reviewed packet/tool drift '+rel)
  print('PASS exact independently reviewed packet/tools');return 0
 if a.action=='cursor':print(response(a.directory).next_page_cursor);return 0
 if a.action=='ids':print('\n'.join(map(str,read_directory(Path(a.directory),status(Path(a.directory)/'status-start.json')))));return 0
 if a.action=='fields':
  x=load(a.directory);print(x['incarnation'],x['store_generation'],x['token']);return 0
 if a.action=='audit':
  out,c=read_snapshot(a.directory)
  if a.original:require_original(out)
  if a.safe:require_safe(out,c)
  out.pop('config_raw_hex');print('PASS read-only snapshot:',out['record_count'],'records;',len(out['native_ids']),'native')
 elif a.action=='plan':out=prepare_action(a.directory,a.operation);print('PASS offline plan:',a.operation,'(no device I/O)')
 elif a.action=='compare-preserve':compare_preserve(a.directory,a.other);out={'status':'PASS_CHECKPOINT_PRESERVATION'};print(out['status'])
 elif a.action=='compare-selection':compare_selection(a.directory,a.other);out={'status':'PASS_PHYSICAL_SELECTION_PRESERVATION'};print(out['status'])
 elif a.action=='compare-mutation':compare_mutation(a.directory,a.other,a.receipt,a.result,a.operation);out={'status':'PASS_'+a.operation};print(out['status'])
 else:out=compare_final(a.directory,a.other);print(out['status'])
 if a.output:
  with a.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:print('STOP: '+str(e));raise SystemExit(1)
