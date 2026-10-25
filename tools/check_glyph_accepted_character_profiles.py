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
ACCEPTED='5e30341ee06761e20e864ccc013ca6658e42b5ca'
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
 for entry in git('ls-tree','-rz','--full-tree',ACCEPTED).split(b'\0'):
  if not entry:continue
  left,path=entry.split(b'\t',1);mode,kind,blob=left.decode().split();rows.append((path.decode(),mode,kind,blob))
 return rows
def source_proof():
 sys.path.insert(0,str(ROOT/'tools'));import glyph_native_profile_json as codec
 authority=json.loads((CHAPTER/'ACCEPTED_KAZUYA.json').read_text())
 raw=(ROOT/authority['canonical_source_path']).read_bytes();original=git('show',ACCEPTED+':'+authority['accepted_source_path'])
 need(raw==original and sha(raw)==authority['source_sha256'],'canonical source differs from gameplay-accepted exact bytes')
 p=json.loads(raw);wire=codec.compile_profile(p);body=codec.unwrap_profile(wire);report=codec.compile_report(p)
 need(wire==(ROOT/'tools/fixtures/kazuya/v4/KazuyaV4.pb').read_bytes(),'canonical compilation differs from accepted wrapper')
 need(report==authority['compiled_identity'],'canonical compile/resource/provenance report differs from accepted identity')
 need(sha(wire)==authority['stored_profile']['wrapper_sha256'] and sha(body)==authority['stored_profile']['body_sha256'],'source to ID51 body/wrapper mismatch')
 need((ROOT/'profiles/kazuya/v1/Kazuya.profile.json').read_bytes()==git('show',ACCEPTED+':profiles/kazuya/Kazuya.profile.json'),'v1 source archival copy changed')
 need((ROOT/'profiles/kazuya/README.v1.md').read_bytes()==git('show',ACCEPTED+':profiles/kazuya/README.md'),'v1 README archival copy changed')
 need((ROOT/'profiles/ultimate/Ultimate.profile.json').read_bytes()==git('show',ACCEPTED+':profiles/ultimate/Ultimate.profile.json'),'archival Ultimate source changed')
 return report
def input_proof():
 out={}
 for path,mode,kind,blob in tracked():
  native=path.startswith(NATIVE_PREFIXES) or path=='platformio.ini'
  python=path.startswith('tools/') and path.endswith('.py') and path not in HOST_EXCEPTIONS
  authoring=path.startswith('profiles/') and path not in ['profiles/kazuya/Kazuya.profile.json','profiles/kazuya/README.md']
  if not(native or python or authoring):continue
  need(mode=='100644' or mode=='100755','unexpected non-regular production/harness input '+path)
  expected=git('cat-file','blob',blob);current=(ROOT/path).read_bytes();need(current==expected,'current production/harness input drift '+path)
  out[path]=sha(current)
 # Any tracked or untracked firmware change is outside this promotion's scope.
 need(not git('diff',ACCEPTED,'--','src','include','HAL','config','schema','platformio.ini').strip(),'firmware/source delta not allowed')
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
 report={'status':'INCOMPLETE','accepted_commit':ACCEPTED,'canonical_source':'profiles/kazuya/Kazuya.profile.json','controller_mutations':0,'firmware_build_or_flash':False}
 try:
  report['compile_report']=source_proof();print('PASS exact canonical source / accepted wrapper, body, provenance and archived v1',flush=True)
  report['current_production_and_harness_sha256']=input_proof();print('PASS current production/harness correspondence',len(report['current_production_and_harness_sha256']),flush=True)
  if not a.identity_only:
   logs=a.report.with_suffix('.logs');logs.mkdir(exist_ok=False)
   results={}
   for name,file,count in [('authoring_v0','test_glyph_native_profile_json.py',17),('authoring_v1','test_glyph_native_profile_json_v1.py',23)]:
    results[name]=run_case(name,[sys.executable,str(ROOT/'tools'/file),'-v'],ROOT,logs,count);print('PASS',name,flush=True)
   with tempfile.TemporaryDirectory(prefix='accepted-kazuya-history-') as temporary:
    snapshot=Path(temporary)
    archive=git('archive','--format=tar',ACCEPTED,'src','include','HAL','config','schema','tools','profiles','platformio.ini')
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
     need(all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and not m.issym() and not m.islnk() for m in tar.getmembers()),'unsafe Git snapshot member')
     tar.extractall(snapshot,filter='data')
    deps=snapshot/'.pio/libdeps/glyph_mk6';deps.mkdir(parents=True)
    nanopb=ROOT/'.pio/libdeps/glyph_mk6/Nanopb';need(nanopb.is_dir(),'existing Nanopb dependency missing');(deps/'Nanopb').symlink_to(nanopb.resolve(),target_is_directory=True)
    for version,count in [(1,6),(2,8),(3,11),(4,11)]:
     filename='test_kazuya_profile.py' if version==1 else 'test_kazuya_profile_v'+str(version)+'.py'
     label='historical_kazuya_v'+str(version);results[label]=run_case(label,[sys.executable,str(snapshot/'tools'/filename),'-v'],snapshot,logs,count);print('PASS',label,flush=True)
    # Frozen expectation/source graph, canonical payload, and CURRENT actual C++.
    bootstrap=logs/'canonical_native_bootstrap.py'
    bootstrap.write_text('''import sys,json,unittest\nfrom pathlib import Path\nsnapshot=Path(sys.argv[1]);current=Path(sys.argv[2]);sys.path.insert(0,str(snapshot/'tools'))\nimport test_kazuya_profile_v4 as suite\nimport check_glyph_profile_native_ultimate as native\nimport check_glyph_stage_b_ultimate_profiles as stage_b\nnative.ROOT=current;native.HOST=current/'tools/fixtures/profile_native_ultimate';native.NANOPB=current/'.pio/libdeps/glyph_mk6/Nanopb'\nsuite.SOURCE=current/'profiles/kazuya/Kazuya.profile.json';suite.base.SOURCE=suite.SOURCE\nresult=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(suite.KazuyaV4Tests))\nPath(sys.argv[3]).write_text(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'observations':suite.KazuyaV4Tests.observations,'canonical_source':str(suite.SOURCE),'production_cpp_root':str(native.ROOT),'expectation_snapshot':'5e30341ee06761e20e864ccc013ca6658e42b5ca'},indent=2)+'\\n')\nraise SystemExit(0 if result.wasSuccessful() and result.testsRun==11 else 1)\n''')
    results['canonical_v4_current_cpp']=run_case('canonical_v4_current_cpp',[sys.executable,str(bootstrap),str(snapshot),str(ROOT),str(logs/'canonical-native.json')],snapshot,logs,11);print('PASS canonical v4 on current C++',flush=True)
   # Revalidate current inputs after all compiles/runs, not just before them.
   need(input_proof()==report['current_production_and_harness_sha256'],'inputs changed during native replay')
   need(source_proof()==report['compile_report'],'canonical source changed during native replay')
   report['suites']=results;report['logs_directory']=str(logs)
  report['status']='PASS_IDENTITY_ONLY' if a.identity_only else 'PASS'
 except Exception as error:report['status']='FAIL';report['error']=str(error);print('FAIL',error,flush=True)
 a.report.write_text(json.dumps(report,indent=2)+'\n');return 0 if report['status'].startswith('PASS') else 1
if __name__=='__main__':raise SystemExit(main())
