#!/usr/bin/env python3
"""Portable actual-source publication cuts and exact raw-NOR restart proofs."""
from pathlib import Path
import argparse,hashlib,json,os,struct,subprocess,sys,zlib
from build import build

def dump_namespace(disk,path):
 b=bytearray(struct.pack('<I',len(disk)))
 for name,data in sorted(disk.items()):
  name=name.encode();b+=struct.pack('<I',len(name))+name+struct.pack('<I',len(data))+data
 path.write_bytes(b)
def load_namespace(path):
 b=path.read_bytes();at=0
 def word():
  nonlocal at
  v=struct.unpack_from('<I',b,at)[0];at+=4;return v
 count=word();disk={}
 for _ in range(count):
  n=word();name=b[at:at+n].decode();at+=n;n=word();disk[name]=b[at:at+n];at+=n
 assert at==len(b);return disk

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--corpus',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--framework',type=Path);ap.add_argument('--nanopb',type=Path);ap.add_argument('--no-build',action='store_true');ap.add_argument('--contexts',default='first,second,prior');ap.add_argument('--limit',type=int);ap.add_argument('--start',type=int,default=0);ap.add_argument('--continue-on-failure',action='store_true');a=ap.parse_args()
 if a.limit is not None and a.limit<1:ap.error('--limit must be positive')
 if a.start<0:ap.error('--start must be nonnegative')
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);corpus=a.corpus.resolve();sys.dont_write_bytecode=True
 sys.path[:0]=[str(corpus/'proof'),str(corpus/'wire'),str(corpus.parents[1]/'tools/research')]
 import glyph_package_storage as m
 import functools
 # Cache only construction of the constant frozen schema adapter. Every byte
 # parse, encode, namespace classification and query proof still executes.
 m.config_wire=functools.lru_cache(maxsize=1)(m.config_wire)
 import glyph_package_fixtures as f
 import package_pb2 as pb
 import reachable_states as reachable
 from source_native_oracle import SourceNativeOracle
 from strict import response as strict_response
 oracle=SourceNativeOracle(corpus/'wire');m.CONFIG_VALIDATOR=oracle.check_config;m.NATIVE_VALIDATOR=oracle.check;m.LEGACY_PROFILE_VALIDATOR=oracle.check_profile
 binary=out/'build/package-fault-harness'
 if not a.no_build:binary=build(a.repo,out/'build',a.framework,a.nanopb)
 manifest=json.loads((out/'build/source-manifest.json').read_text());fingerprint=manifest['fingerprint']
 for name,wanted in manifest['files'].items():
  p=Path(name) if Path(name).is_absolute() else a.repo/name
  if hashlib.sha256(p.read_bytes()).hexdigest()!=wanted:raise RuntimeError('source/tool changed since build: '+str(p))
 (out/'results.jsonl').write_text('')
 env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1','ASAN_OPTIONS':'detect_leaks=0'}
 def run(*args):
  p=subprocess.run([str(binary),*map(str,args)],capture_output=True,text=True,env=env)
  if p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
  return p
 base=f.baseline(ultimate=True,backend=True);base['/keep.bin']=b'UNRELATED-CUSTODY\0'+bytes(range(128))
 first,v1=f.package_plan(base,True,100);second,v2=f.package_plan(first['COMMITTED'],False,200)
 prior=f.later_raw_create(second['COMMITTED'],300);reachable.model=m;reachable.fixtures=f;prior=reachable.save_config(prior,'G',400);prior=reachable.save_config(prior,'D',400)
 contexts={'first':(base,first,v1),'second':(first['COMMITTED'],second,v2),'prior':(prior,*f.package_plan(prior,True,500))}
 logical={'NONE':0,'PROVEN_ABORTED':1,'INCOMPLETE':2,'COMMITTED':3,'UNRESOLVED':4};floor={'UNRESOLVED':0,'NO_MANAGED':1,'SUPPORTED':2,'UNSUPPORTED':3}
 def query(token,digest,inc):return pb.PackageEnvelope(protocol_version=3,request_token=token,operation=16,expected_store_incarnation=inc,expected_digest=digest).SerializeToString(deterministic=True)
 def compare(raw,expected):
  r=strict_response(raw,16)
  actual=[r.status,r.logical,r.storage_floor,r.write_fenced,r.store_generation,r.config_generation,r.transaction_token_high_water]
  wanted=[expected['status'],logical[expected['logical']],floor[expected['floor']],expected['write_fenced'],expected['store_generation'],expected['config_generation'],expected['transaction_token_high_water']]
  assert actual==wanted,('query metadata',actual,wanted)
  receipt=expected.get('receipt')
  if receipt:
   assert r.profile_id==receipt['id'] and r.profile_revision==1 and r.HasField('row_index') and r.row_index==receipt['row'] and r.rgb_index==receipt['rgb']
   assert r.semantic_digest==receipt['digest'] and r.config_sha==receipt['config_sha'] and r.record_sha==receipt['record_sha'] and r.record_publication_generation==receipt['generation']
  else:assert not(r.profile_id or r.profile_revision or r.transaction_operation or r.HasField('row_index') or r.HasField('semantic_digest') or r.HasField('config_sha') or r.HasField('record_sha') or r.record_publication_generation)
  return {'status':r.status,'logical':r.logical,'floor':r.storage_floor,'fenced':r.write_fenced,'store_generation':r.store_generation,'high_token':r.transaction_token_high_water,'id':r.profile_id}
 results=[];failures=[];coverage={}
 (out/'summary.json').write_text(json.dumps({'source_fingerprint':fingerprint,'tested':0,'passed':0,'failures':0,'coverage':{},'complete':False},indent=2)+'\n')
 for context in a.contexts.split(','):
  disk,states,plan=contexts[context];work=out/context;work.mkdir(exist_ok=True);dump_namespace(disk,work/'seed.namespace');(work/'create.pb').write_bytes(plan['request']);run('seed',work/'seed.namespace',work/'seed.nor')
  clean=work/'clean';clean.mkdir(exist_ok=True);run('execute',work/'seed.nor',work/'create.pb',clean,-1)
  assert load_namespace(clean/'namespace.bin')==states['COMMITTED'],context+' exact successful namespace'
  strict_response((clean/'response.pb').read_bytes(),15)
  # A transport-lost successful response grants only exact read-only receipt
  # lookup/re-entry. This new process consumes the committed raw NOR directly.
  lost=clean/'lost-response';lost.mkdir(exist_ok=True);q=query(plan['intent']['token'],plan['intent']['digest'],plan['intent']['incarnation']);(clean/'queries.bin').write_bytes(struct.pack('<II',1,len(q))+q)
  run('inspect',clean/'unwound.nor',clean/'queries.bin',lost,work/'create.pb',plan['intent']['id'])
  lost_summary=json.loads((lost/'summary.json').read_text());assert lost_summary['programs']==lost_summary['erases']==0 and lost_summary['reentries']==2
  compare((lost/'query-0.pb').read_bytes(),m.query_package(states['COMMITTED'],plan['intent']['token'],plan['intent']['digest'],plan['intent']['incarnation']))
  for n in range(2):strict_response((lost/('reentry-'+str(n)+'.pb')).read_bytes(),15)

  events=json.loads((clean/'trace.json').read_text());coverage[context]={'events':len(events),'by_operation':{},'by_checkpoint':{}}
  for event in events:
   key=str(event['operation'])+':'+str(event['when']);coverage[context]['by_operation'][key]=coverage[context]['by_operation'].get(key,0)+1
   key=str(event['call_phase'])+':'+str(event['intent_phase']);coverage[context]['by_checkpoint'][key]=coverage[context]['by_checkpoint'].get(key,0)+1
  selected=events[a.start:a.start+a.limit if a.limit is not None else None]
  for event in selected:
   cutdir=work/('cut-'+str(event['index']).zfill(4));cutdir.mkdir(exist_ok=True);record={'context':context,'event':event,'source_fingerprint':fingerprint,'pass':False}
   try:
    run('execute',work/'seed.nor',work/'create.pb',cutdir,event['index']);summary=json.loads((cutdir/'summary.json').read_text());assert summary['fault_hit'],'target cut not reached'
    assert summary['unchanged'],'error unwind changed NOR after the captured cut'
    observed_events=json.loads((cutdir/'trace.json').read_text());assert observed_events[:event['index']+1]==events[:event['index']+1],'fault path/event prefix diverged from admitted baseline'
    strict_response((cutdir/'response.pb').read_bytes(),15)
    strict_response((cutdir/'sameboot-query.pb').read_bytes(),16)
    strict_response((cutdir/'sameboot-status.pb').read_bytes(),1)
    cut=(cutdir/'cut.nor').read_bytes();assert len(cut)==524288 and cut==(cutdir/'unwound.nor').read_bytes()
    inspect=cutdir/'restart';inspect.mkdir(exist_ok=True)
    identities=[(plan['intent']['token'],plan['intent']['digest'])]
    for name,data in disk.items():
     if name.startswith('/ultpkg-') and name.endswith('.bin'):
      rec=m.decode_record(data);identities.append((rec['token'],rec['digest']))
    identities=list(dict.fromkeys(identities));query_bytes=[query(t,d,plan['intent']['incarnation']) for t,d in identities]
    query_bytes += [query(plan['intent']['token'],bytes(32),plan['intent']['incarnation']),query(2**64-1,bytes(32),plan['intent']['incarnation'])]
    packed=bytearray(struct.pack('<I',len(query_bytes)))
    for request in query_bytes:packed+=struct.pack('<I',len(request))+request
    (cutdir/'queries.bin').write_bytes(packed)
    run('inspect',cutdir/'cut.nor',cutdir/'queries.bin',inspect,work/'create.pb',plan['intent']['id'])
    restart=json.loads((inspect/'summary.json').read_text());assert restart['programs']==restart['erases']==0 and restart['unchanged'] and restart['no_handles']
    for index in range(restart.get('reentries',0)):strict_response((inspect/('reentry-'+str(index)+'.pb')).read_bytes(),15)
    assert (inspect/'after.nor').read_bytes()==cut,'restart reconstructed/reseeded or mutated raw NOR'
    observed=load_namespace(inspect/'namespace.bin');observation={'mounted':restart['mounted'],'configuration_ok':True,'namespace_ok':restart['mounted']}
    record['queries']=[]
    for index,request in enumerate(query_bytes):
     q=pb.PackageEnvelope();q.ParseFromString(request);expected=m.query_package(observed,q.request_token,q.expected_digest,q.expected_store_incarnation,**observation)
     record['queries'].append(compare((inspect/('query-'+str(index)+'.pb')).read_bytes(),expected))
    # Reserved namespace may change; preexisting unmanaged data and all old
    # immutable managed records must remain byte-identical, even at torn cuts.
    for name,data in disk.items():
     if name not in {'/ultimate-v2-0.bin','/ultimate-v2-1.bin','/ultimate-v2.ctrl','/config-v2.bin','/config-v2.prev'}:assert observed.get(name)==data,('unrelated data changed',name)
    record.update(pass_=True,raw_nor_sha256=hashlib.sha256(cut).hexdigest(),mounted=restart['mounted'],reboot_query_programs=restart['programs'],reboot_query_erases=restart['erases'],no_handles=True,unrelated_preserved=True,reentries=restart.get('reentries',0),hidden_checks=restart.get('hidden_checks',0),sameboot_sticky_fence=True)
    record['pass']=True
    (cutdir/'cut.nor.zlib').write_bytes(zlib.compress(cut,9))
    trace_bytes=(cutdir/'trace.json').read_bytes();(cutdir/'trace.json.zlib').write_bytes(zlib.compress(trace_bytes,9));(cutdir/'trace.json').unlink()
    for p in [cutdir/'cut.nor',cutdir/'unwound.nor',inspect/'after.nor']:p.unlink()
   except Exception as error:
    record['error']=str(error);failures.append(record);print('FAIL',context,event,str(error),flush=True)
   results.append(record)
   with (out/'results.jsonl').open('a') as stream:stream.write(json.dumps(record,sort_keys=True)+'\n')
   (out/'summary.json').write_text(json.dumps({'source_fingerprint':fingerprint,'tested':len(results),'passed':sum(x['pass'] for x in results),'failures':len(failures),'coverage':coverage,'complete':False},indent=2)+'\n')
   if failures and not a.continue_on_failure:oracle.close();return 1
  print(context,'tested',len(selected),'of',len(events),'admitted publication events',flush=True)
 summary=json.loads((out/'summary.json').read_text());summary['complete']=a.limit is None and a.start==0 and not failures and len(results)==sum(c['events'] for c in coverage.values());(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 oracle.close();print('tested',len(results),'passed',sum(x['pass'] for x in results),'failures',len(failures));return bool(failures)
if __name__=='__main__':raise SystemExit(main())
