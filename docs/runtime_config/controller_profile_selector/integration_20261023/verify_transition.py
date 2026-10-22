#!/usr/bin/env python3
"""Read-only exact GP-NATIVE-002 accepted-transition and source verifier.

No build, Git mutation, device I/O, or acceptance of a different tuple.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
F='8b2c75e35bb990aee06de3165e5780082c4f08ad'
FT='cd5d280e3b04a3b4e9d9a1bc760917406175b988'
E='7ee104debde92c61390ff44fcc35afa14e9e5548'
ADOPT='02c5d8a29ffc666fddd1c311d1e8b515aec3f22b'
I='785057b470321a9e36b427144775fad261465e05'
BASE='3a7a8174f10dfc11563b4a6a6d2029a4e2acf29f'
R='cc132574660a2b2e0065f07dad225f971e70d01c'
UF2='ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760'
RECORD='docs/runtime_config/controller_profile_selector/liveness_candidate_8b2c75e3/hardware_20261023/evidence.json'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def obj(ref,path):return git('show',ref+':'+path)
def entries(ref):
 result={}
 for row in git('ls-tree','-r','-z',ref).split(b'\0'):
  if not row:continue
  h,p=row.split(b'\t',1);mode,kind,blob=h.decode().split();result[p.decode()]=(mode,kind,blob)
 return result
def ancestor(a,b):
 if subprocess.run(['git','merge-base','--is-ancestor',a,b],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:raise ValueError('missing ancestry '+a+' -> '+b)
def require(c,m):
 if not c:raise ValueError(m)
def queue(ref):
 text=obj(ref,'docs/project/ACTIVE_AGENT_QUEUE.md').decode();return json.loads(text.split('<!-- queue-state:start -->')[1].split('```json')[1].split('```')[0])
def verify(snapshot, custody_root=None, override=None):
 cat=json.loads((HERE/'ACCEPTED_TRANSITION.json').read_text()) if override is None else override
 require((cat['F'],cat['F_tree'],cat['E'],cat['I'],cat['accepted_UF2_sha256'],cat['accepted_UF2_bytes'])==(F,FT,E,I,UF2,1046016),'catalog tested tuple mismatch')
 require(cat['physical_no_poll']=='NOT_TESTED' and cat['root_cause']=='UNPROVEN' and cat['Nunchuk']=='NOT_TESTED','limitations altered')
 require(cat['GameCube']=='OWNER_REPORTED_PASS_NORMAL_SWITCH_ADAPTER_NO_RAW_IDENTITY','GameCube claim widened')
 require(git('rev-parse',F+'^{tree}').decode().strip()==FT,'F tree changed')
 require(git('rev-parse',I+'^{tree}').decode().strip()==cat['I_tree'],'I tree mismatch')
 require(git('show','-s','--format=%P',F).decode().strip()==cat['F_parent'],'F parent mismatch')
 require(git('show','-s','--format=%P',I).decode().split()==[ADOPT,F],'integration parents are not genuine adoptedE + testedF')
 for a,b in [(R,E),(E,ADOPT),(BASE,ADOPT),(ADOPT,I),(F,I),(I,snapshot)]:ancestor(a,b)
 ebytes=obj(E,RECORD);require(hashlib.sha256(ebytes).hexdigest()==cat['evidence_sha256'],'immutable E bytes mismatch')
 ev=json.loads(ebytes);require(ev['candidate_git_sha']==F and ev['firmware_artifact_sha256']==UF2 and ev['result']=='PASS' and ev['evidence_gaps']==[],'E acceptance mismatch')
 require(ev['schema_name']=='glyph_hardware_evidence_record' and ev['schema_version']==2,'E schema mismatch')
 q=next(x for x in queue(ADOPT)['items'] if x['id']=='GP-NATIVE-002');require(q['status']=='HARDWARE_VALIDATED' and q['hardware_result']=='PASS' and q['candidate_git_sha']==F and q['hardware_evidence_gaps']==[],'canonical source-free adoption mismatch')
 require(q['hardware_evidence_record']=='git-json:'+E+':'+RECORD,'adoption substitutes E')
 f,merge,now,old,adopt=map(entries,[F,I,snapshot,BASE,ADOPT])
 critical_bytes=(HERE/'full-critical-source-build-303.json').read_bytes()
 require(hashlib.sha256(critical_bytes).hexdigest()==cat['critical_inventory_sha256'],'critical manifest hash mismatch')
 critical=json.loads(critical_bytes)['files'];require(len(critical)==303 and len({x['path'] for x in critical})==303,'critical inventory changed')
 product=lambda t:{p:v for p,v in t.items() if p.startswith(('HAL/','config/','include/','src/','schema/','builder_scripts/','lib/','scripts/')) or p=='platformio.ini'}
 require(product(f)==product(merge)==product(now),'complete product/build namespace mismatch')
 require({x['path'] for x in critical}==set(product(f))|{'tools/glyph_tracked_worktree_integrity.py'},'critical closure missing or extra path')
 for row in critical:
  p=row['path'];expected=(row['mode'],row['type'],row['blob']);require(f.get(p)==merge.get(p)==now.get(p)==expected,'critical Git mode/blob mismatch '+p)
  require(hashlib.sha256(obj(snapshot,p)).hexdigest()==row['sha256'],'critical SHA256 mismatch '+p)
 for p in cat['reviewed_F_paths']:
  require(f.get(p)==merge.get(p)==now.get(p),'reviewed source/test/fixture mismatch '+p)
 # E must remain source-free against its canonical predecessor.
 require(product(old)==product(adopt),'source integrated before acceptance publication')
 protected=['docs/runtime_config/controller_profile_selector/hardware_failure_20261022/']
 for p,v in old.items():
  if any(p.startswith(x) for x in protected):require(now.get(p)==v,'historical FAIL rewritten '+p)
 require(obj(snapshot,RECORD)==ebytes,'canonical accepted evidence changed')
 allowed=set(cat['reviewed_F_paths'])
 for p,v in old.items():
  if p.startswith('docs/') and p not in allowed and not p.startswith('docs/runtime_config/controller_profile_selector/integration_20261023/'):
   require(p in now,'canonical historical document deleted '+p)
 custody='NOT_REQUESTED'
 if custody_root:
  p=Path(custody_root)/'local_backups/hardware-artifacts'/F/UF2/'firmware.uf2'
  require(p.is_file() and not p.is_symlink(),'UF2 custody missing or symlinked');data=p.read_bytes();require(len(data)==1046016 and hashlib.sha256(data).hexdigest()==UF2,'tested UF2 custody mismatch');custody='EXACT_RETAINED_UF2_MATCH'
 return {'status':'PASS_EXACT_ACCEPTED_TRANSITION','snapshot':snapshot,'integration':I,'F':F,'F_tree':FT,'E':E,'critical_inputs':303,'reviewed_F_paths':len(cat['reviewed_F_paths']),'all_modes_blobs_sha256':'MATCH','all_product_build_namespace':'EXACT_F','R_E_I_ancestry':'PASS','historical_failure':'UNCHANGED','custody':custody,'physical_no_poll':'NOT_TESTED','root_cause':'UNPROVEN','Nunchuk':'NOT_TESTED','GameCube':cat['GameCube'],'build_performed':False,'device_operations':0}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--snapshot',default='HEAD');p.add_argument('--custody-root',type=Path);p.add_argument('--negative-controls',action='store_true');a=p.parse_args();snapshot=git('rev-parse',a.snapshot).decode().strip();r=verify(snapshot,a.custody_root)
 if a.negative_controls:
  cat=json.loads((HERE/'ACCEPTED_TRANSITION.json').read_text());controls=[]
  for field,value in [('F','4898951994bcabcaef2846145de2922a674656f8'),('accepted_UF2_sha256','7ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e'),('physical_no_poll','PASS')]:
   changed={**cat,field:value}
   try:verify(snapshot,None,changed)
   except ValueError:controls.append(field+' REJECTED')
   else:raise ValueError('negative control accepted '+field)
  try:verify('4898951994bcabcaef2846145de2922a674656f8')
  except ValueError:controls.append('actual_failed_predecessor_snapshot REJECTED')
  else:raise ValueError('failed predecessor accepted as integrated source')
  r['negative_controls']=controls
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
