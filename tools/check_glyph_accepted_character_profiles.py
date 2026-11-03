#!/usr/bin/env python3
"""Exact accepted-source proof and immutable Kazuya history replay. No device I/O.

Historical pins retain their original meaning. A temporary exact Git snapshot
supplies old expectations; the accepted replay compiles current production C++
and consumes the canonical source. No historical evidence is rewritten.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import io
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_ACCEPTED='5e30341ee06761e20e864ccc013ca6658e42b5ca'
CANONICAL_BASE='a6e3bc885d46e2a7412ec697aa822bcd8c4ce495'
V5_REVIEWED='510234798d74d4aa29dbc35df030df5530c26c81'
V5_SOURCE='profiles/kazuya/v5/KazuyaV5.profile.json'
CHAPTER=ROOT/'docs/runtime_config/accepted_character_profiles'
NATIVE_PREFIXES=('src/','include/','HAL/','config/','schema/','tools/fixtures/')
# All unchanged Python tooling that can be imported by the frozen native suites.
HOST_EXCEPTIONS={'tools/glyph_profile_store_production_tool.py','tools/check_glyph_profile_store_production_tool.py'}
def sha(data):return hashlib.sha256(data).hexdigest()
def need(ok,why):
 if not ok:raise ValueError(why)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def tracked():
 rows=[]
 for entry in git('ls-tree','-rz','--full-tree',HISTORICAL_ACCEPTED).split(b'\0'):
  if not entry:continue
  left,path=entry.split(b'\t',1);mode,kind,blob=left.decode().split();rows.append((path.decode(),mode,kind,blob))
 return rows
def source_proof():
 sys.path.insert(0,str(ROOT/'tools'));import glyph_native_profile_json as codec
 authority=json.loads((CHAPTER/'ACCEPTED_KAZUYA.json').read_text())
 raw=(ROOT/authority['canonical_source_path']).read_bytes();original=git('show',V5_REVIEWED+':'+authority['accepted_source_path'])
 need(raw==original and sha(raw)==authority['source_sha256'],'canonical source differs from gameplay-accepted exact v5 bytes')
 need(git('hash-object',authority['canonical_source_path']).decode().strip()==authority['source_git_blob'],'canonical source Git blob differs from reviewed v5 source')
 p=json.loads(raw);wire=codec.compile_profile(p);body=codec.unwrap_profile(wire);report=codec.compile_report(p)
 expected_report={key:value for key,value in authority['compiled_identity'].items() if key!='production_protobuf_json_sha256'}
 need(report==expected_report,'canonical compile/resource/provenance report differs from v5 accepted identity')
 protobuf_json=(json.dumps(codec.profile_to_protobuf_json(p),indent=2)+'\n').encode()
 need(sha(protobuf_json)==authority['compiled_identity']['production_protobuf_json_sha256'],'canonical production protobuf JSON differs from accepted identity')
 need(sha(wire)==authority['stored_profile']['wrapper_sha256'] and sha(body)==authority['stored_profile']['body_sha256'],'source to ID53 body/wrapper mismatch')
 for version in range(1,5):
  path='profiles/kazuya/v%d/Kazuya%s.profile.json'%(version,'' if version==1 else 'V%d'%version)
  if version==1:path='profiles/kazuya/v1/Kazuya.profile.json'
  need((ROOT/path).read_bytes()==git('show',CANONICAL_BASE+':'+path),'historical Kazuya v%d source changed'%version)
 need((ROOT/'profiles/kazuya/README.v1.md').read_bytes()==git('show',CANONICAL_BASE+':profiles/kazuya/README.v1.md'),'v1 README archival copy changed')
 need((ROOT/'profiles/ultimate/Ultimate.profile.json').read_bytes()==git('show',CANONICAL_BASE+':profiles/ultimate/Ultimate.profile.json'),'archival Ultimate source changed')
 return report
def input_proof():
 out={}
 for path,mode,kind,blob in tracked():
  native=path.startswith(NATIVE_PREFIXES) or path=='platformio.ini'
  python=path.startswith('tools/') and path.endswith('.py') and path not in HOST_EXCEPTIONS
  authoring=path.startswith('profiles/') and not path.startswith('profiles/kazuya/')
  v5_tool=path=='tools/test_kazuya_profile_v5.py'
  accepted_tool=path=='tools/check_glyph_accepted_character_profiles.py'
  if not(native or (python and not v5_tool and not accepted_tool) or authoring):continue
  need(mode=='100644' or mode=='100755','unexpected non-regular production/harness input '+path)
  expected=git('cat-file','blob',blob);current=(ROOT/path).read_bytes();need(current==expected,'current production/harness input drift '+path)
  out[path]=sha(current)
 # Any tracked or untracked firmware change is outside this promotion's scope.
 need(not git('diff',HISTORICAL_ACCEPTED,'--','src','include','HAL','config','schema','platformio.ini').strip(),'firmware/source delta not allowed')
 for rel in git('ls-files','--others','--exclude-standard','src','include','HAL','config','schema').decode().splitlines():raise ValueError('untracked production input '+rel)
 return out
def run_case(name,command,cwd,logs,expected_tests=None):
 completed=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
 (logs/(name+'.stdout.log')).write_text(completed.stdout);(logs/(name+'.stderr.log')).write_text(completed.stderr)
 need(completed.returncode==0,name+' failed; inspect '+str(logs))
 if expected_tests is not None:need(re.search(r'Ran '+str(expected_tests)+r' tests?\b',completed.stderr),name+' did not execute expected suite count')
 return {'status':'PASS','returncode':completed.returncode,'tests':expected_tests,'stdout_sha256':sha(completed.stdout.encode()),'stderr_sha256':sha(completed.stderr.encode())}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True);parser.add_argument('--identity-only',action='store_true');a=parser.parse_args()
 report={'status':'INCOMPLETE','historical_accepted_commit':HISTORICAL_ACCEPTED,'canonical_base':CANONICAL_BASE,'reviewed_v5_commit':V5_REVIEWED,'canonical_source':'profiles/kazuya/Kazuya.profile.json','controller_mutations':0,'firmware_build_or_flash':False}
 try:
  report['compile_report']=source_proof();print('PASS exact canonical v5 source / accepted wrapper, body, provenance and archived v1-v4',flush=True)
  report['current_production_and_harness_sha256']=input_proof();print('PASS current production/harness correspondence',len(report['current_production_and_harness_sha256']),flush=True)
  if not a.identity_only:
   logs=a.report.with_suffix('.logs');logs.mkdir(exist_ok=False)
   results={}
   for name,file,count in [('authoring_v0','test_glyph_native_profile_json.py',17),('authoring_v1','test_glyph_native_profile_json_v1.py',23)]:
    results[name]=run_case(name,[sys.executable,str(ROOT/'tools'/file),'-v'],ROOT,logs,count);print('PASS',name,flush=True)
   historical_snapshots=[(1,6,'f96b3fd81589251296fff8d85043864b06f9eaf0'),(2,8,'1381193b0101825d2a9afb46cd7a01009da67cdf'),(3,11,'b2d72b1367ea6c350574727168cdc8b5c2ce3f1d'),(4,11,HISTORICAL_ACCEPTED)]
   report['historical_snapshot_commits']={str(version):commit for version,_,commit in historical_snapshots}
   nanopb=ROOT/'.pio/libdeps/glyph_mk6/Nanopb';need(nanopb.is_dir(),'existing Nanopb dependency missing')
   for version,count,commit in historical_snapshots:
    with tempfile.TemporaryDirectory(prefix='accepted-kazuya-v%d-'%version) as temporary:
     snapshot=Path(temporary);archive=git('archive','--format=tar',commit,'src','include','HAL','config','schema','tools','profiles','platformio.ini')
     with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
      need(all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and not m.issym() and not m.islnk() for m in tar.getmembers()),'unsafe Git snapshot member')
      tar.extractall(snapshot,filter='data')
     deps=snapshot/'.pio/libdeps/glyph_mk6';deps.mkdir(parents=True);(deps/'Nanopb').symlink_to(nanopb.resolve(),target_is_directory=True)
     filename='test_kazuya_profile.py' if version==1 else 'test_kazuya_profile_v'+str(version)+'.py'
     label='historical_kazuya_v'+str(version);results[label]=run_case(label,[sys.executable,str(snapshot/'tools'/filename),'-v'],snapshot,logs,count);print('PASS',label,flush=True)
   results['canonical_v5_current_cpp']=run_case('canonical_v5_current_cpp',[sys.executable,str(ROOT/'tools/test_kazuya_profile_v5.py'),'-v'],ROOT,logs,7);print('PASS canonical v5 on current C++',flush=True)
   # Revalidate current inputs after all compiles/runs, not just before them.
   need(input_proof()==report['current_production_and_harness_sha256'],'inputs changed during native replay')
   need(source_proof()==report['compile_report'],'canonical source changed during native replay')
   report['suites']=results;report['logs_directory']=str(logs)
  report['status']='PASS_IDENTITY_ONLY' if a.identity_only else 'PASS'
 except Exception as error:report['status']='FAIL';report['error']=str(error);print('FAIL',error,flush=True)
 a.report.write_text(json.dumps(report,indent=2)+'\n');return 0 if report['status'].startswith('PASS') else 1
if __name__=='__main__':raise SystemExit(main())
