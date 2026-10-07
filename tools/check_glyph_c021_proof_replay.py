#!/usr/bin/env python3
"""Authenticated C021 source replay and unchanged original-consumer execution."""
from __future__ import annotations
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import concurrent.futures
import signal
import shlex

ROOT=Path(__file__).resolve().parents[1]
C='a170bd40a51741582913324bfecbc14ce9b3211d'
B='c6887115f2e44f0803eb0956ebb574633cec53be'
TREE='91ca6d86c2fa28b55ef5a6b3623b25748b167feb'
ENGINE='tools/check_glyph_gp_config021_persisted_recovery.py'
ENGINE_BLOB='a3d3dd9186c7f885316adca16706d360e652dd90'
ENGINE_SHA='2dc78d118dd2936ad9544a297ef00a66a140f90dc58152c87c2abbe423ef556d'
FIXTURE='docs/runtime_config/fixtures/gp_val038_c021_consumer_replay.json'
FIXTURE_SHA='6724b99d5bb66f086a91fc7676fc08aa6488015783bbc134deaf8a8776a6cf31'
PHASES={'BASELINE','CANDIDATE_VALIDATION_ONLY','SOURCE_FREE_PROCESSOR','ACCEPTED_TRANSITION'}
CONSUMERS=('persistence', 'raw_get', 'transaction005', 'rebind008', 'menu009', 'button012', 'usb013', 'button020', 'kbd001', 'usb019', 'neopixel016_017', 'modifier011', 'modifier014', 'transition035')

class ReplayError(ValueError):pass

def require(value,message):
    if not value:raise ReplayError(message)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def git(root,*args,input=None,timeout=20):
    result=subprocess.run(['git','-c','protocol.allow=never',*args],cwd=root,input=input,capture_output=True,timeout=timeout)
    require(result.returncode==0,'native Git failed: '+str(args)+' '+result.stderr.decode(errors='replace'))
    return result.stdout

def path_ok(path):
    require(type(path)is str and path and not Path(path).is_absolute() and all(x not in ('','.','..') for x in path.split('/')) and not any(x in path for x in ('\\','\0','\n','\r','\t',':')),'unsafe finite path')

def regular(root,path,mode=0o644):
    path_ok(path);file=root/path
    for ancestor in (file,*file.parents):
        if ancestor==root:break
        require(not ancestor.is_symlink(),'input/ancestor symlink: '+path)
    require(file.is_file() and stat.S_IMODE(file.stat().st_mode)==mode,'regular exact mode input: '+path)
    return file.read_bytes()

def unique(items):
    out={}
    for key,value in items:
        require(key not in out,'duplicate JSON key');out[key]=value
    return out

def tree_rows(raw):
    rows={}
    for row in raw.split(b'\0'):
        if not row:continue
        metadata,path=row.split(b'\t');mode,kind,identity=metadata.decode().split();path=path.decode();path_ok(path)
        require(path not in rows,'duplicate Git tree path');rows[path]=(mode,kind,identity)
    return rows

def object_inputs(root,revision,pins):
    require(revision in (C,B),'unexpected immutable input revision')
    rows=tree_rows(git(root,'ls-tree','-r','-z',revision,'--',*pins))
    require(set(rows)==set(pins),'finite immutable closure omission/extra')
    for path,pin in pins.items():
        require(set(pin)=={'mode','blob','sha256'} and pin['mode']=='100644' and rows[path]==('100644','blob',pin['blob']),'immutable mode/blob: '+path)
    # Query only the explicitly reviewed file objects; index-pack/clone/fetch is
    # unnecessary for C's host engine. Every returned object is hashed again.
    result=git(root,'cat-file','--batch',input=(''.join(p['blob']+'\n' for p in pins.values())).encode())
    stream=io.BytesIO(result);out={}
    for path,pin in pins.items():
        identity,kind,size=stream.readline().decode().strip().split();raw=stream.read(int(size));terminator=stream.read(1)
        require(identity==pin['blob'] and kind=='blob' and terminator==b'\n' and blob(raw)==identity and sha(raw)==pin['sha256'],'immutable bytes: '+path);out[path]=raw
    require(not stream.read(),'unexpected batch objects')
    return out

def constant_tables(raw,names):
    out={}
    for node in ast.parse(raw).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in names:
            require(node.targets[0].id not in out,'duplicate immutable table');out[node.targets[0].id]=ast.literal_eval(node.value)
    require(set(out)==set(names),'immutable literal table omission');return out

def verify_fixture(root):
    """Read-only finite custody entry; no campaign authentication recursion."""
    root=Path(root).resolve();raw=regular(root,FIXTURE);require(sha(raw)==FIXTURE_SHA,'independent038 replay fixture substitution')
    value=json.loads(raw,object_pairs_hook=unique)
    require((value['schema_name'],value['schema_version'],value['candidate'],value['base'],value['candidate_tree'])==('glyph_gp_val038_c021_consumer_replay',1,C,B,TREE),'038 replay fixture identity')
    require(set(value['consumer_lanes'])==set(CONSUMERS) and value['engine_path']==ENGINE and len(value['original_C_inputs'])==216,'finite consumer/engine closure')
    original=object_inputs(root,C,value['original_C_inputs']);engine=original[ENGINE]
    require(blob(engine)==ENGINE_BLOB and sha(engine)==ENGINE_SHA,'immutable C engine changed')
    tables=constant_tables(engine,{'PINS','BASE','FIXTURE_SHA256'})
    require(tables['BASE']==B and len(tables['PINS'])==214 and {p:value['original_C_inputs'][p] for p in tables['PINS']}==tables['PINS'],'original214 PINS were dropped/refreshed')
    engine_fixture=original[value['engine_fixture']];require(sha(engine_fixture)==tables['FIXTURE_SHA256'],'original C fixture substitution')
    for name,lane in value['consumer_lanes'].items():
        require(lane['root']==B and lane['original_path'] in lane['pins'],'original consumer entry/root absent')
        object_inputs(root,B,lane['pins'])
        require(lane['commands']==[['python3',lane['original_path']]]+([['python3',lane['original_path'],'--repaired-current']] if name=='neopixel016_017' else []),'consumer command substitution')
    snapshot=value['historical_snapshot'];raw_tree=git(root,'ls-tree','-r','-z',B)
    require(snapshot['commit']==B and snapshot['tracked_count']==1432 and snapshot['raw_tree_sha256']==sha(raw_tree) and snapshot['tree']==git(root,'rev-parse',B+'^{tree}').decode().strip(),'complete immutableB support substitution')
    require(len(value['compiler_dependencies'])==194 and len(set(value['compiler_dependencies']))==194,'actual MMD closure extent')
    require(set(value['supplementary_current_inputs'])==set(value['supplementary_current_paths']) and len(value['supplementary_current_paths'])==2,'finite current host lanes')
    for path,pin in value['supplementary_current_inputs'].items():
        raw=regular(root,path);require(pin['mode']=='100644' and blob(raw)==pin['blob'] and sha(raw)==pin['sha256'],'current observation fixture substitution')
    kb=value['keyboard_observation_input'];object_inputs(root,B,{kb['path']:kb['pin']})
    verify_current_roles(root,value)
    return value

def materialize_candidate(root,directory,value):
    require(not directory.exists(),'fresh private C root required');directory.mkdir(parents=True)
    original=object_inputs(root,C,value['original_C_inputs'])
    for path,raw in original.items():
        target=directory/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);target.chmod(0o644)
    module_path=directory/ENGINE;spec=importlib.util.spec_from_file_location('glyph_c021_original_engine',module_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    require(module.PINS=={p:pin for p,pin in value['original_C_inputs'].items() if p not in (ENGINE,value['engine_fixture'])},'engine PINS runtime changed')
    require(module.FIXTURE_SHA256==sha(original[value['engine_fixture']]),'engine original fixture identity')
    module._live_inputs(directory);module._fixture_identity(directory);module.source_contract(directory)
    return module

def check_c_evidence(evidence,value,negative_controls=True):
    require(evidence['dependencies']==value['compiler_dependencies'] and len(evidence['negative_controls'])==(69 if negative_controls else 0),'full194/69 proof omitted')
    for abi,expected in value['proof_expectations'].items():
        if abi not in ('short','ordinary'):continue
        rows=evidence['abis'][abi]
        for suite in ('semantic','persistence','setconfig'):require(rows[suite]['cases']==expected[suite],'current case census: '+suite)
        require(rows['setconfig']['missing_callback_cases']==1 and len(rows['startup']['cases'])==40 and all(r['exit']==0 and not r['stderr'] for r in rows['startup']['cases']),'full fresh callback/startup cases')
    require(sum(r['classification']=='ACTUAL_LITERAL_TU_RUNTIME_REJECTION' for r in evidence['negative_controls'])==(32 if negative_controls else 0),'actual executable mutants omitted')

def run_candidate_replay(root,directory,value,negative_controls=True):
    module=materialize_candidate(root,directory/'candidate',value)
    evidence=module.run_host(directory/'candidate',directory/'host-output',negative_controls=negative_controls,pins=module.PINS)
    check_c_evidence(evidence,value,negative_controls)
    for path,pin in value['original_C_inputs'].items():
        raw=regular(directory/'candidate',path);require(sha(raw)==pin['sha256'] and blob(raw)==pin['blob'],'immutable C replay input changed: '+path)
    return evidence

def authenticate(root):
    import glyph_c021_campaign_transition as campaign
    require(campaign.present(root) and campaign.C==C and campaign.B==B and campaign.TREE==TREE,'exact038 campaign module missing/substituted')
    proof=campaign.authenticate(root);require(proof['phase'] in PHASES and proof['candidate']==C and proof['base']==B,'038 phase/identity mismatch')
    roots=proof['object_roots'];require(C in roots and B in roots,'authenticated C/B roots omitted')
    campaign.source_contract(root)
    return proof

def historical_snapshot(root,directory,value,object_roots):
    require(not directory.exists(),'fresh private B snapshot required');directory.mkdir()
    roots=sorted(set(object_roots)|{B});require(all(type(x)is str and len(x)==40 and all(c in '0123456789abcdef' for c in x) for x in roots),'unbounded object root')
    for identity in roots:require(git(root,'rev-parse','--verify',identity+'^{commit}').decode().strip()==identity,'historical root type/substitution')
    git(directory,'-c','init.templateDir=','init','-q')
    pack=git(root,'pack-objects','--revs','--stdout',input=('\n'.join(roots)+'\n').encode(),timeout=40)
    git(directory,'index-pack','--stdin',input=pack,timeout=40)
    require(not (directory/'.git/objects/info/alternates').exists(),'shared object alternates forbidden')
    git(directory,'checkout','--detach',B)
    require(git(directory,'rev-parse','HEAD').decode().strip()==B,'immutable historical HEAD')
    verify_historical_snapshot(directory,value)
    return {'object_roots':roots,'pack_sha256':sha(pack),'tracked_count':1432,'classification':'COMPLETE_IMMUTABLE_B_NATIVE_SUPPORT_ONLY'}

def verify_historical_snapshot(root,value):
    expected=tree_rows(git(root,'ls-tree','-r','-z',B));require(len(expected)==1432,'immutable B tracked extent')
    stage=git(root,'ls-files','--stage','-z');wanted=b''.join((mode+' '+identity+' 0\t'+path+'\0').encode() for path,(mode,kind,identity) in sorted(expected.items()))
    require(stage==wanted,'historical HEAD/index modes/blobs/stages')
    flags=git(root,'ls-files','-v','-z');require(flags==b''.join(('H '+path+'\0').encode() for path in sorted(expected)),'historical index flag trap')
    for path,(mode,kind,identity) in expected.items():
        require(kind=='blob' and mode in ('100644','100755'),'historical unsupported object mode')
        raw=regular(root,path,0o644 if mode=='100644' else 0o755);require(blob(raw)==identity,'historical live bytes: '+path)
    require(git(root,'status','--porcelain','--untracked-files=all')==b'','historical snapshot dirty/untracked')

def private_command(command,cwd,env,directory,label):
    """Keep descendants in the unchanged runner's owned process group.

    File-backed output permits bounded parent reaping on an inner timeout;
    the native outer runner owns cleanup of every remaining descendant.
    """
    stdout_path=directory/(label+'.stdout.log');stderr_path=directory/(label+'.stderr.log')
    with stdout_path.open('wb') as out,stderr_path.open('wb') as err:
        child=subprocess.Popen(command,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
        timed_out=False
        try:child.wait(timeout=100)
        except subprocess.TimeoutExpired:
            timed_out=True;child.kill();child.wait(timeout=2)
    record={'command':command,'exit':'TIMEOUT100' if timed_out else child.returncode,
            'stdout':stdout_path.read_text(errors='replace'),'stderr':stderr_path.read_text(errors='replace'),
            'process_ownership':'INHERITED_NATIVE_WRAPPER_GROUP'}
    (directory/(label+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    require(not timed_out,'private original/main TIMEOUT100 (retained FAIL): '+label+'\n'+record['stdout']+record['stderr'])
    return subprocess.CompletedProcess(command,child.returncode,record['stdout'],record['stderr'])

def run_historical(root,directory,value,consumer,proof):
    lane=value['consumer_lanes'][consumer];snapshot=directory/'historical-B'
    support=historical_snapshot(root,snapshot,value,proof['object_roots'])
    env=dict(os.environ)
    for key in ('GLYPH_CHECKER_BASE','GLYPH_CHECKER_EXPECTED_MERGE_BASE','GLYPH_HOST_MOUNT_FAIL','GLYPH_HOST_CONFIG_FAIL','GLYPH_HOST_RGB_CTOR_OFFSETS'):env.pop(key,None)
    scratch=directory/'historical-tmp';scratch.mkdir();env.update(TMPDIR=str(scratch),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',GLYPH_CHECKER_BASE=B,GLYPH_CHECKER_EXPECTED_MERGE_BASE=B)
    runs=[]
    for index,command in enumerate(lane['commands']):
        actual=[sys.executable,'-B','-u',*command[1:]]
        result=private_command(actual,snapshot,env,directory,'historical-'+str(index))
        record={'command':actual,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr};runs.append(record)
        require(result.returncode==0 and 'PASS' in result.stdout,'original historical main failed (retained FAIL): '+consumer+'\n'+result.stdout+result.stderr)
    verify_historical_snapshot(snapshot,value)
    return {'classification':'ACTUAL_IMMUTABLE_ORIGINAL_MAIN_REPLAY','consumer':consumer,'support':support,'runs':runs}


def method_body(raw,signature):
    begin=raw.index(signature);brace=raw.index(b'{',begin);depth=1;end=brace+1
    while depth:
        require(end<len(raw),'unterminated literal method');depth+=(raw[end:end+1]==b'{')-(raw[end:end+1]==b'}');end+=1
    return raw[begin:end]+b'\n'

def verify_current_roles(root,value):
    original=object_inputs(root,C,value['original_C_inputs'])
    original.update(object_inputs(root,C,value['unchanged_current_additional_pins']))
    equality=value['unchanged_current_source_paths']
    equal_pins={**value['original_C_inputs'],**value['unchanged_current_additional_pins']}
    historical=object_inputs(root,B,{p:equal_pins[p] for p in equality})
    require(all(historical[p]==original[p] for p in equality),'unchanged normal consumer body drift')
    path='HAL/pico/src/comms/ConfiguratorBackend.cpp'
    before=git(root,'show',B+':'+path);after=original[path]
    get=method_body(after,b'bool ConfiguratorBackend::HandleGetConfig()')
    require(get==method_body(before,b'bool ConfiguratorBackend::HandleGetConfig()'),'literal GET target body changed')
    rawpath='HAL/pico/src/core/Persistence.cpp'
    oldraw=method_body(git(root,'show',B+':'+rawpath),b'size_t Persistence::LoadConfigRaw(')
    currentraw=method_body(original[rawpath],b'size_t Persistence::LoadConfigRaw(')
    guard=b'    if (!IsAvailable()) {\n        return false;\n    }\n'
    require(currentraw.count(guard)==1 and currentraw.replace(guard,b'',1)==oldraw,'RAW sole availability guard consequence')
    return get

def run_current_consumers(root,directory,value,candidate=None,engine_output=None):
    """Literal current storage/SET consumers; independent external transport observations."""
    directory.mkdir(parents=True,exist_ok=True)
    if candidate is None:
        candidate=directory/'candidate';module=materialize_candidate(root,candidate,value)
    else:
        spec=importlib.util.spec_from_file_location('glyph_c021_bridge_engine',candidate/ENGINE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    getbody=verify_current_roles(root,value);(directory/'getconfig_body.inc').write_bytes(getbody)
    supplementary=value['supplementary_current_inputs']
    for path,pin in supplementary.items():
        raw=regular(root,path);require(blob(raw)==pin['blob'] and sha(raw)==pin['sha256'],'current host observation substitution: '+path)
        target=candidate/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);target.chmod(0o644)
    kb=value['keyboard_observation_input'];object_inputs(root,B,{kb['path']:kb['pin']})
    kbroot=directory/'keyboard-observation';kbroot.mkdir(exist_ok=True)
    (kbroot/'TUKeyboard.hpp').write_bytes(git(root,'show',B+':'+kb['path']))
    extra=['src/core/InputMode.cpp','src/core/ControllerMode.cpp','src/modes/CustomControllerMode.cpp','src/core/socd.cpp','HAL/pico/src/core/KeyboardMode.cpp','src/modes/CustomKeyboardMode.cpp']
    protections=['-fsanitize=address,undefined,enum,shift','-fno-sanitize-recover=all','-fno-omit-frame-pointer']
    cxx=module.shutil.which('clang++') or module.shutil.which('g++');cc=module.shutil.which('clang') or module.shutil.which('gcc');require(cxx and cc,'native host compiler absent')
    evidence={'classification':'ACTUAL_LITERAL_CURRENT_CONSUMERS_HOST_ONLY','abis':{},'commands':[],'dependencies':[],'get_body_sha256':sha(getbody),'body_equality_B_C':True,'COBS_wire':'NOT_TESTED'}
    dependencies=set()
    def command(args,label):
        result=subprocess.run(list(map(str,args)),cwd=candidate,capture_output=True,text=True,timeout=40)
        evidence['commands'].append(list(map(str,args)));(directory/(label+'.log')).write_text(json.dumps(list(map(str,args)))+'\n'+result.stdout+result.stderr)
        require(result.returncode==0 and not result.stderr,'current literal bridge failed: '+label+'\n'+result.stdout+result.stderr);return result
    for label,abi in [('short','-fshort-enums'),('ordinary','-fno-short-enums')]:
        out=directory/label;out.mkdir(exist_ok=True)
        includes=['-I'+str(kbroot),'-I'+str(directory)]+['-I'+str(candidate/p) for p in module.INCLUDES]
        common=['-O0','-g',abi,*protections,*includes]
        cpp=['-std=gnu++17','-Wno-missing-field-initializers','-Wno-non-c-typedef-for-linkage','-DFIRMWARE_NAME="host"','-DFIRMWARE_VERSION="host"','-DDEVICE_NAME="host"',*common]
        objects={};cobjects=[]
        def compile_file(path,name,compiler,flags):
            obj=out/(name+'.o');dep=out/(name+'.d');command([compiler,*flags,'-MMD','-MF',dep,'-c',path,'-o',obj],label+'-'+name+'.compile')
            raw=dep.read_text().replace('\\\n',' ');paths=shlex.split(raw.split(':',1)[1])
            for p in paths:
                file=Path(p).resolve()
                if sys.platform=='darwin' and file==Path('/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/SDKSettings.json').resolve():
                    evidence['system_toolchain_metadata']={'classification':'SELECTED_CLANG_SDK_METADATA','path':str(file),'sha256':sha(file.read_bytes())};continue
                if file==directory/'getconfig_body.inc':continue
                if file==kbroot/'TUKeyboard.hpp':dependencies.add(kb['path']);continue
                try:relative=file.relative_to(candidate).as_posix()
                except ValueError:
                    relative=file.relative_to(root).as_posix();require(relative in supplementary,'external bridge compiler dependency')
                require(relative in value['original_C_inputs'] or relative in supplementary,'unreviewed bridge dependency: '+relative);dependencies.add(relative)
            return obj
        for i,path in enumerate(module.GENERAL_UNITS):
            obj=engine_output/label/('general-'+str(i)+'.o') if engine_output else compile_file(candidate/path,'general'+str(i),cxx,cpp)
            require(obj.is_file(),'reused current literal object absent');objects[path]=obj
        for i,path in enumerate(module.C_UNITS):
            obj=engine_output/label/('c-'+str(i)+'.o') if engine_output else compile_file(candidate/path,'c'+str(i),cc,['-std=c99',*common]);require(obj.is_file(),'coherent C object absent');cobjects.append(obj)
        getobj=compile_file(candidate/value['supplementary_current_paths'][0],'get-harness',cxx,cpp)
        consumerobj=compile_file(candidate/value['supplementary_current_paths'][1],'consumer-harness',cxx,cpp)
        extraobjects=[compile_file(candidate/p,'extra'+str(i),cxx,cpp) for i,p in enumerate(extra)]
        binaries={}
        for suite,objs in [('getconfig',[objects[p] for p in module.GENERAL_UNITS[:5]]+cobjects+[getobj]),('consumers',list(objects.values())+cobjects+extraobjects+[consumerobj])]:
            binary=out/suite;command([cxx,*protections,*objs,'-o',binary],label+'-'+suite+'.link');binaries[suite]=binary
        runs={}
        env=dict(os.environ)
        for key in ('GLYPH_HOST_CONFIG_FAIL','GLYPH_HOST_MOUNT_FAIL'):env.pop(key,None)
        for suite,binary in binaries.items():
            result=subprocess.run([binary],cwd=candidate,env=env,capture_output=True,text=True,timeout=15)
            (directory/(label+'-'+suite+'.run.log')).write_text(result.stdout+result.stderr);require(result.returncode==0 and not result.stderr,'current '+suite+' runtime failed\n'+result.stdout+result.stderr)
            require(('raw_get_matrix cases=11 PASS' if suite=='getconfig' else 'current_consumer_matrix name_binding=20 transaction_cases=25 consumer_cases=2 PASS') in result.stdout,'current bridge census omitted')
            runs[suite]={'stdout':result.stdout,'stderr':result.stderr,'exit':result.returncode,'binary_sha256':sha(binary.read_bytes())}
        for fault in ('GLYPH_HOST_CONFIG_FAIL','GLYPH_HOST_MOUNT_FAIL'):
            result=subprocess.run([binaries['getconfig'],'--unavailable'],cwd=candidate,env={**env,fault:'1'},capture_output=True,text=True,timeout=15)
            (directory/(label+'-'+fault+'.log')).write_text(result.stdout+result.stderr);require(result.returncode==0 and not result.stderr and 'unavailable_error_no_raw_payload PASS' in result.stdout,'fresh unavailable GET guard failed')
            runs[fault]={'stdout':result.stdout,'stderr':result.stderr,'exit':result.returncode}
        evidence['abis'][label]=runs
    evidence['dependencies']=sorted(dependencies)
    require(set(value['current_bridge_dependencies'])<=dependencies<=set(value['compiler_dependencies'])|set(value['current_bridge_dependencies']),'actual bridge MMD closure omitted/substituted')
    (directory/'current-consumers.json').write_text(json.dumps(evidence,indent=2)+'\n');return evidence

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--consumer',choices=CONSUMERS);args=parser.parse_args()
    try:
        value=verify_fixture(ROOT);before=authenticate(ROOT)
        with tempfile.TemporaryDirectory(prefix='glyph-c021-replay-',dir='/private/tmp' if Path('/private/tmp').is_dir() else None) as name:
            directory=Path(name)
            def current_positive():
                current_root=directory/'current';current_root.mkdir()
                evidence=run_candidate_replay(ROOT,current_root,value,negative_controls=args.consumer is None)
                bridges=run_current_consumers(ROOT,current_root/'current-consumers',value,current_root/'candidate',current_root/'host-output')
                return evidence,bridges
            try:
                if args.consumer:
                    historical_dir=directory/'historical';historical_dir.mkdir()
                    def current_native035():
                        command=[sys.executable,'-B','-u',str(ROOT/'tools/test_glyph_c021_campaign_transition.py')]
                        native=private_command(command,ROOT,dict(os.environ),directory,'current038')
                        require(native.returncode==0 and not native.stderr and 'PASS' in native.stdout,
                                'current038 direct native proof failed\n'+native.stdout+native.stderr)
                        return native
                    # Independent roots, subprocesses, modules, objects and logs.
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        old=executor.submit(run_historical,ROOT,historical_dir,value,args.consumer,before)
                        new=executor.submit(current_native035 if args.consumer=='transition035' else current_positive)
                        outcomes={};errors=[]
                        for label,future in (('historical',old),('current',new)):
                            try:outcomes[label]=future.result()
                            except (ValueError,AssertionError,OSError,subprocess.SubprocessError) as error:
                                errors.append(label+': '+str(error))
                        require(not errors,'actual paired proof failure (both outcomes inspected)\n'+'\n'.join(errors))
                    historical=outcomes['historical']
                    if args.consumer=='transition035':print(outcomes['current'].stdout,end='')
                    else:result,current=outcomes['current']
                else:result,current=current_positive()
            finally:
                require(authenticate(ROOT)==before,'actual root/phase changed during replay');verify_fixture(ROOT)
        classification='IMMUTABLE_C021_SOURCE_REPLAY_ONLY' if before['phase'] in ('BASELINE','SOURCE_FREE_PROCESSOR') else 'AUTHENTICATED_CURRENT_C021_SOURCE_HOST_PROOF'
        if args.consumer:classification='ACTUAL_IMMUTABLE_ORIGINAL_MAIN_REPLAY + '+classification
        print('glyph_c021_proof_replay: PASS; '+classification+' phase='+before['phase']+' consumer='+str(args.consumer))
        if args.consumer!='transition035':
            print('semantic=1077/1173 Persistence=326/326 SET=868+1/868+1 startup=40/40 negatives='+('69' if args.consumer is None else 'DISABLED_ON_CONSUMER_LANE')+' MMD=194')
            print('current RAWGET=11+2/11+2 name_binding=20/20 SET_transactions=25/25 keyboard/custom_consumer_observations=2/2')
        print('original_C_standalone_CLI=RETAINED_FAIL hardware=NOT_CLAIMED target_build=NOT_RUN COBS_wire=NOT_TESTED')
        return 0
    except (ValueError,AssertionError,OSError,subprocess.SubprocessError) as error:
        print('glyph_c021_proof_replay: FAIL: '+str(error));return 1
if __name__=='__main__':raise SystemExit(main())
