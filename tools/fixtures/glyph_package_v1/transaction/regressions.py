#!/usr/bin/env python3
"""Allowed raw/G6, native/context and actual canonical Config CRC collision controls."""
from pathlib import Path
import argparse,hashlib,json,os,random,struct,subprocess,sys,zlib
from run import dump_namespace,load_namespace
from build import build

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--corpus',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--binary',type=Path);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);c=a.corpus.resolve();sys.dont_write_bytecode=True
 sys.path[:0]=[str(c/'proof'),str(c/'wire'),str(c.parents[1]/'tools/research')]
 import glyph_package_storage as m
 import functools
 m.config_wire=functools.lru_cache(maxsize=1)(m.config_wire)
 import glyph_package_fixtures as f
 import package_pb2 as p
 import config_pb2 as cfg
 import reachable_states as reachable
 from source_native_oracle import SourceNativeOracle
 from strict import response
 oracle=SourceNativeOracle(c/'wire');m.CONFIG_VALIDATOR=oracle.check_config;m.NATIVE_VALIDATOR=oracle.check;m.LEGACY_PROFILE_VALIDATOR=oracle.check_profile
 binary=a.binary or build(a.repo,out/'build');env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1','ASAN_OPTIONS':'detect_leaks=0'}
 def invoke(*args):
  proc=subprocess.run([str(binary),*map(str,args)],capture_output=True,text=True,env=env)
  if proc.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+proc.stdout+proc.stderr)
 def raw_input(name,disk,request):
  work=out/name;work.mkdir(exist_ok=True);dump_namespace(disk,work/'seed.namespace');(work/'create.pb').write_bytes(request);invoke('seed',work/'seed.namespace',work/'seed.nor');return work
 base=f.baseline(ultimate=True,backend=True);base['/keep.bin']=b'UNRELATED-CUSTODY\0'+bytes(range(128));first,_=f.package_plan(base,True,100);second,_=f.package_plan(first['COMMITTED'],False,200);prior=f.later_raw_create(second['COMMITTED'],300);reachable.model=m;reachable.fixtures=f;prior=reachable.save_config(prior,'G',400);prior=reachable.save_config(prior,'D',400)
 _,plan=f.package_plan(prior,True,500);work=raw_input('raw-and-g6',prior,plan['request']);invoke('regress',work/'seed.nor',work/'create.pb',work)
 managed_denials=json.loads((work/'managed-denials.json').read_text());assert managed_denials=={'cases':5,'zero_write':True,'namespace_healthy':True}
 original=m.decode_root(max((prior['/ultimate-v2-0.bin'],prior['/ultimate-v2-1.bin']),key=lambda b:m.u32(b,8)));managed={e['id']:e['entry_bytes'] for e in original['entries'] if e['managed']};results=[]
 results.append({'name':'managed-mutation-denials',**managed_denials})
 for name in ['update','duplicate','rename','reorder','delete','advance','gc','g6']:
  disk=load_namespace(work/(name+'.namespace.bin'));state=m.classify(disk);assert state['logical']=='COMMITTED' and not state['write_fenced'],(name,state)
  selected=max((disk['/ultimate-v2-0.bin'],disk['/ultimate-v2-1.bin']),key=lambda b:m.u32(b,8));root=m.decode_root(selected)
  assert root['aggregate']==original['aggregate'] and root['sequence']==original['sequence']
  assert {e['id']:e['entry_bytes'] for e in root['entries'] if e['managed']}==managed
  oldroot=max((prior['/ultimate-v2-0.bin'],prior['/ultimate-v2-1.bin']),key=lambda b:m.u32(b,8));assert selected[3904:4416]==oldroot[3904:4416],name+' terminal intent preservation'
  for path,data in prior.items():
   if path.startswith('/ultpkg-') or path=='/keep.bin':assert disk[path]==data,(name,path)
  if name!='g6':assert disk['/config-v2.bin']==prior['/config-v2.bin'],name+' Config unchanged'
  results.append({'name':name,'source_operation':True,'complete_managed_preservation':True,'state':state})
 gc=load_namespace(work/'gc.namespace.bin');assert m.u32(max((gc['/ultimate-v2-0.bin'],gc['/ultimate-v2-1.bin']),key=lambda b:m.u32(b,8)),16)==4
 assert '/ultimate-00000004-00000001.bin' not in gc,'GC releases deleted raw duplicate only after protected root advances'
 # Continue with a real package after all allowed raw/G6 mutations. ID4 was
 # consumed by duplicate/delete; the next reservation must be ID5, never reused.
 disk=load_namespace(work/'g6.namespace.bin');states,after=f.package_plan(disk,True,800);continuation=out/'package-after-raw-g6';continuation.mkdir(exist_ok=True);(continuation/'create.pb').write_bytes(after['request']);invoke('execute',work/'after.nor',continuation/'create.pb',continuation,-1)
 assert load_namespace(continuation/'namespace.bin')==states['COMMITTED'] and after['intent']['id']==5
 response((continuation/'response.pb').read_bytes(),15);results.append({'name':'package-after-raw-g6','next_id':5,'exact_namespace':True})
 # Deterministic birthday search among source-valid 17-byte ASCII names.
 # Both complete canonical Config bodies share CRC32 but have different SHA256.
 randomizer=random.Random(0xB2);seen={};collision=None;config=cfg.Config();config.ParseFromString(base['/config-v2.bin'][8:])
 for attempt in range(250000):
  config.game_mode_configs[0].name='c'+format(randomizer.getrandbits(64),'016x');body=config.SerializeToString(deterministic=True);crc=zlib.crc32(body)&0xffffffff
  if crc in seen and seen[crc]!=body:collision=(seen[crc],body,crc,attempt+1);break
  seen[crc]=body
 assert collision is not None,'bounded CRC birthday search did not produce a witness'
 left,right,crc,attempts=collision;assert left!=right and m.sha(left)!=m.sha(right) and m.CONFIG_VALIDATOR(left) and m.CONFIG_VALIDATOR(right)
 disk_a=dict(base);disk_b=dict(base);disk_a['/config-v2.bin']=struct.pack('<II',len(left),crc)+left;disk_b['/config-v2.bin']=struct.pack('<II',len(right),crc)+right
 _,expected=f.package_plan(disk_a,False,100);negative=raw_input('crc-collision-guard',disk_b,expected['request']);invoke('execute',negative/'seed.nor',negative/'create.pb',negative,-1)
 result=response((negative/'response.pb').read_bytes(),15);assert result.status==6 and not result.profile_id and load_namespace(negative/'namespace.bin')==disk_b and (negative/'unwound.nor').read_bytes()==(negative/'seed.nor').read_bytes()
 assert json.loads((negative/'summary.json').read_text())['trace_events']==0
 (negative/'config-a.pb').write_bytes(left);(negative/'config-b.pb').write_bytes(right);results.append({'name':'crc-collision-guard','crc32':crc,'sha_a':m.sha(left).hex(),'sha_b':m.sha(right).hex(),'attempts':attempts,'status':6,'zero_write':True})
 _,native_plan=f.package_plan(base,False,100)
 for name,mutate in [('native-header',lambda b:setattr(b,'native_body',bytes([b.native_body[0]^1])+b.native_body[1:])),('native-context',lambda b:b.row.button_remapping.add(physical_button=1,activates=2))]:
  request=p.PackageEnvelope();request.ParseFromString(native_plan['request']);body=p.PackageBody();body.ParseFromString(request.package_body);mutate(body);request.package_body=body.SerializeToString(deterministic=True)
  case=raw_input(name,base,request.SerializeToString(deterministic=True));invoke('execute',case/'seed.nor',case/'create.pb',case,-1);r=response((case/'response.pb').read_bytes(),15)
  assert r.status==2 and (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes() and load_namespace(case/'namespace.bin')==base
  results.append({'name':name,'status':2,'zero_write':True})
 # Missing current and previous raw dependencies are never admission credit.
 missing_cases=[('missing-protected-current',prior,'/ultimate-00000003-00000001.bin'),('missing-protected-previous',load_namespace(work/'update.namespace.bin'),'/ultimate-00000003-00000001.bin')]
 for name,complete,missing in missing_cases:
  absent=dict(complete);del absent[missing];_,plan_missing=f.package_plan(absent,False,900)
  case=raw_input(name,absent,plan_missing['request']);invoke('execute',case/'seed.nor',case/'create.pb',case,-1);r=response((case/'response.pb').read_bytes(),15)
  assert r.status!=1 and not r.profile_id and (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes() and not json.loads((case/'trace.json').read_text())
  results.append({'name':name,'status':r.status,'zero_write':True,'missing':missing})
 _,geometry_plan=f.package_plan(base,False,100);case=raw_input('used-below-logical',base,geometry_plan['request']);invoke('underreported',case/'seed.nor',case/'create.pb',case);r=response((case/'response.pb').read_bytes(),15)
 assert r.status!=1 and (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes();results.append({'name':'used-below-logical','reported_used':0,'observed_logical':sum(map(len,base.values())),'status':r.status,'zero_write':True})
 # All four immutable accepted CREATE digest witnesses, including max frame.
 for vector in json.loads((c/'wire/vectors.json').read_text())+[json.loads((c/'wire/max-frame-vector.json').read_text())]:
  if vector['name']=='query':continue
  request=p.PackageEnvelope();request.ParseFromString(bytes.fromhex(vector['request']));request.request_token=0;expected=m.sha(b'Glyph.Package.Create.v1\0'+request.SerializeToString(deterministic=True))
  case=raw_input('digest-'+vector['name'],base,bytes.fromhex(vector['request']));invoke('digest',case/'seed.nor',case/'create.pb',case);assert (case/'digest.bin').read_bytes()==expected
  results.append({'name':'digest-'+vector['name'],'exact_immutable_digest':True})
 # Source-invalid but canonical, unmarked designated prior cannot be hidden
 # by a CREATE that would overwrite it. Header CRC/canonicality alone is not truth.
 poisoned=dict(base);_,tree=m.config_body(base['/config-v2.bin']);f.put(tree,6,29);poisoned['/config-v2.prev']=f.config_file(tree);assert not m.CONFIG_VALIDATOR(poisoned['/config-v2.prev'][8:]);_,plan_poison=f.package_plan(poisoned,False,100)
 case=raw_input('invalid-unmarked-prior',poisoned,plan_poison['request']);invoke('execute',case/'seed.nor',case/'create.pb',case,-1);r=response((case/'response.pb').read_bytes(),15);assert r.status!=1 and (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes() and not json.loads((case/'trace.json').read_text());results.append({'name':'invalid-unmarked-prior','status':r.status,'zero_write':True})
 full=dict(base);_,tree=m.config_body(full['/config-v2.bin']);tree.append(dict(number=5,values=[[] for _ in range(30)]));full['/config-v2.bin']=f.config_file(tree);assert m.CONFIG_VALIDATOR(full['/config-v2.bin'][8:]);_,plan_full=f.package_plan(full,False,100)
 req=p.PackageEnvelope.FromString(plan_full['request']);body=p.PackageBody.FromString(req.package_body);body.rgb.SetInParent();req.package_body=body.SerializeToString(deterministic=True)
 case=raw_input('rgb-30-full',full,req.SerializeToString(deterministic=True));invoke('execute',case/'seed.nor',case/'create.pb',case,-1);r=response((case/'response.pb').read_bytes(),15);assert r.status==7 and (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes();results.append({'name':'rgb-30-full','status':7,'zero_write':True})
 for kind in ['g6','migration']:
  initial=f.completed_migration(2) if kind=='migration' else base;installed,_=f.package_plan(initial,True,100);case=raw_input('public-save-'+kind,installed['COMMITTED'],plan['request']);invoke('probe-save',case/'seed.nor',kind,case);assert load_namespace(case/'namespace.bin')==installed['COMMITTED'];results.append({'name':'public-save-'+kind,'zero_write':True})
 for kind in ['unresolved','unsupported','unscoped','wrong-path','wrong-token','package-helper','revoked-helper']:
  case=raw_input('lower-fallback-'+kind,base,plan['request']);invoke('fallback',case/'seed.nor',kind,case);summary=json.loads((case/'summary.json').read_text());assert summary['programs']==summary['erases']==0;results.append({'name':'lower-fallback-'+kind,'zero_nor_mutations':True,'helper_effects_checked':True})
 # Final serialized baseline rechecks happen after the last capacity callback.
 # IO-failed/lost-read acknowledgements must not become positive guard drift.
 for path in ['/config-v2.bin','/ultimate-v2-0.bin','/ultimate-v2-1.bin','/ultimate-v2.ctrl']:
  for when in ['before','after']+(['drift'] if path!='/config-v2.bin' else []):
   label='final-recheck-'+path[1:]+'-'+when;case=raw_input(label,base,native_plan['request'])
   invoke('preflight-recheck',case/'seed.nor',case/'create.pb',case,path,when)
   r=response((case/'response.pb').read_bytes(),15)
   assert r.status==(6 if when=='drift' else 9) and not r.profile_id and not r.HasField('semantic_digest')
   assert (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes() and load_namespace(case/'namespace.bin')==base
   results.append({'name':label,'zero_write':True,'status':r.status,'positive_read_destination_drift':when=='drift'})
 # A complete recognized future-version marker is six bytes, not eight.
 # Actual startup and CREATE must preserve every byte and never autoformat.
 for magic,version,path in [(b'PDS1',2,'/ultimate-dir-0.bin'),(b'PDS2',4,'/ultimate-v2-0.bin')]:
  for length in [6,7]:
   disk=dict(base);disk[path]=magic+struct.pack('<H',version)+b'X'*(length-6)
   label='future-root-'+magic.decode()+'-'+str(length);case=raw_input(label,disk,native_plan['request'])
   invoke('execute',case/'seed.nor',case/'create.pb',case,-1)
   r=response((case/'response.pb').read_bytes(),15)
   assert r.storage_floor==3 and r.write_fenced and not r.profile_id
   assert (case/'unwound.nor').read_bytes()==(case/'seed.nor').read_bytes() and load_namespace(case/'namespace.bin')==disk
   assert not json.loads((case/'trace.json').read_text())
   results.append({'name':label,'complete_marker_bytes':length,'unsupported':True,'zero_write':True})
 from transport_regressions import transport_regressions
 from wire_regressions import wire_regressions
 results.extend(wire_regressions(binary,c,out/'wire-corpus'))
 results.extend(transport_regressions(binary,a.repo,c,out/'transport',base,m,f,p,response))
 (out/'results.json').write_text(json.dumps(results,indent=2)+'\n');oracle.close();print('actual production regression checks',len(results),'PASS')
if __name__=='__main__':main()
