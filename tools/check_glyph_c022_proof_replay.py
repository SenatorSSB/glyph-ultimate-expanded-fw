#!/usr/bin/env python3
"""039 authentication of immutable C022 and independent predecessor observations."""
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, io, json, os, re, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
C='b4e03566ceaa0815df7ba0eef975cf0ac0583622'
B='14400b3ff75b5d017a9e7cf8e6d8be785c342187'
TREE='6f4e4610798c12e49b99b46a974d51c38e68b478'
ENGINE='tools/check_glyph_gp_config022_rgb_target_validation.py'
ENGINE_FIXTURE='docs/runtime_config/fixtures/gp_config022_rgb_target_validation.json'
FIXTURE='docs/runtime_config/fixtures/gp_val039_c022_consumer_replay.json'
FIXTURE_SHA='00ee3e334c574917b72bdb0f99c6e11e5614a9fb0aed34e526ffeccf15efdc02'
ENGINE_SHA='3707dc5f5e318aaf44b0da4b9265eacff01dcc9b2aee8613a3bb24a6afcbd529'
ENGINE_BLOB='62ff2c2e1ed5ebe219edc3c5a7816576126d9ca9'
CONSUMERS=('button012', 'button020', 'kbd001', 'menu009', 'modifier011', 'modifier014', 'neopixel016_017', 'persistence', 'raw_get', 'rebind008', 'recovery021', 'transaction005', 'transition035', 'transition038', 'usb013', 'usb019')
PHASES={'BASELINE','SOURCE_FREE_PROCESSOR','CANDIDATE_VALIDATION_ONLY','ACCEPTED_TRANSITION'}
class ReplayError(ValueError):pass
def require(value,message):
 if not value:raise ReplayError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def path_ok(path):
 require(type(path)is str and path and not Path(path).is_absolute() and all(p not in ('','.','..')for p in path.split('/'))and not any(c in path for c in ('\\','\0','\n','\r','\t',':')),'unsafe input path')
def regular(root,path,mode=0o644):
 path_ok(path);root=Path(root).resolve();target=root/path
 for item in (target,*target.parents):
  if item==root:break
  require(not item.is_symlink(),'symlink input '+path)
 require(target.is_file()and stat.S_IMODE(target.stat().st_mode)==mode,'regular exact-mode input '+path);return target.read_bytes()
def unique(pairs):
 out={}
 for k,v in pairs:require(k not in out,'duplicate JSON key');out[k]=v
 return out
def git(root,*args,input=None,timeout=40):
 result=subprocess.run(['git','-c','protocol.allow=never',*args],cwd=root,input=input,capture_output=True,timeout=timeout)
 require(result.returncode==0,'native Git failure '+repr(args)+' '+result.stderr.decode(errors='replace'));return result.stdout
def tree_rows(raw):
 out={}
 require(not raw or raw.endswith(b'\0'),'unterminated raw tree')
 for record in raw.split(b'\0'):
  if not record:continue
  metadata,p=record.split(b'\t',1);mode,kind,identity=metadata.decode().split();p=p.decode();path_ok(p);require(p not in out,'duplicate Git path');out[p]={'mode':mode,'kind':kind,'blob':identity}
 return out
def object_inputs(root,revision,pins):
 require(revision in (C,B),'unexpected immutable revision');require(type(pins)is dict and pins,'empty immutable pins')
 rows=tree_rows(git(root,'ls-tree','-r','-z',revision,'--',*pins));require(set(rows)==set(pins),'immutable pin omission/extra')
 for p,pin in pins.items():
  require(type(pin)is dict and set(pin)=={'mode','blob','sha256'}and pin['mode']in ('100644','100755'),'immutable pin type/mode')
  require(rows[p]=={'mode':pin['mode'],'kind':'blob','blob':pin['blob']},'immutable mode/blob '+p)
 response=git(root,'cat-file','--batch',input=(''.join(v['blob']+'\n'for v in pins.values())).encode());stream=io.BytesIO(response);out={}
 for p,pin in pins.items():
  identity,kind,n=stream.readline().decode().split();raw=stream.read(int(n));end=stream.read(1)
  require(identity==pin['blob']and kind=='blob'and end==b'\n'and blob(raw)==identity and sha(raw)==pin['sha256'],'immutable bytes '+p);out[p]=raw
 require(not stream.read(),'extra immutable object response');return out
def literal_tables(raw,names):
 values={}
 def literal(node):
  if isinstance(node,ast.List):return [literal(n)for n in node.elts]
  if isinstance(node,ast.Subscript)and isinstance(node.value,ast.Name)and node.value.id=='RGB_UNITS'and isinstance(node.slice,ast.Constant)and type(node.slice.value)is int and node.slice.value in (0,1):
   require('RGB_UNITS'in values,'source literal order');return values['RGB_UNITS'][node.slice.value]
  return ast.literal_eval(node)
 for node in ast.parse(raw).body:
  if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in names|{'RGB_UNITS'}:
   name=node.targets[0].id;require(name not in values,'duplicate literal');values[name]=literal(node.value)
 require(set(names)<=set(values),'literal omission');return {name:values[name]for name in names}

def critical_rows(rows):
    # Use native precedence, including its exact executable correspondence literal.
    import glyph_hardware_correspondence as native
    out={}
    for path,entry in rows.items():
        try:category=native.classify_path(path)
        except native.CorrespondenceError:continue
        if category=='CRITICAL':
            native._entries_safe(path,category,(entry['mode'],entry['kind'],entry['blob']))
            out[path]=entry
    return out

def guard_critical(actual_E,actual_C,value):
    require(type(actual_E)is dict and type(actual_C)is dict,'critical inventory type')
    require(len(actual_E)==238 and len(actual_C)==243,'complete native238/243 census')
    require(actual_E==value['native_critical_E']and actual_C==value['native_critical_C'],'native critical mode/type/blob substitution or omission')
    allowed=set(value['critical_production_paths'])
    require(len(allowed)==7,'exact seven production paths')
    changed={p for p in set(actual_E)|set(actual_C)if actual_E.get(p)!=actual_C.get(p)}
    require(changed==allowed,'unknown/omitted critical source delta')
    for path in allowed:require(actual_C[path]['mode']=='100644'and actual_C[path]['kind']=='blob','new/changed production regular100644')
    require(sum(actual_E.get(p)==actual_C.get(p)for p in actual_E)==236,'unchanged236 baseline modes/blobs')
    executables={p for p,v in actual_E.items()if v['mode']=='100755'}
    require(executables=={'glyph_nuker','scripts/build-glyph-mk6-quiet.sh','scripts/build-glyph-mk6-senscope-playtest-quiet.sh','scripts/pio-local.sh','tools/check_glyph_profile_adapter_prewrite.py'},'native existing executable census')
    require(all(actual_E[p]==actual_C[p]for p in executables),'existing executable changed')

def validate_original_pins(value,original,engine_fixture,tables):
    require(value['original_C_PINS_count']==209 and len(tables['PIN_PATHS'])==209,'original209 count')
    pins=value['original_C_inputs']
    require(type(pins)is dict and set(pins)==set(tables['PIN_PATHS'])|{ENGINE_FIXTURE},'original210 input omission/extra')
    require(engine_fixture['base']==B and tables['BASE']==B and engine_fixture['expected_cases']==tables['EXPECTED_CASES'],'original literal base/census')
    require(set(engine_fixture['pins'])==set(tables['PIN_PATHS']),'original209 fixture omission')
    for path,pin in pins.items():
        require(type(pin)is dict and set(pin)=={'mode','blob','sha256'}and pin['mode']=='100644','original pin type/mode')
        require(path in original and sha(original[path])==pin['sha256']and blob(original[path])==pin['blob'],'original pin substitution')
        if path!=ENGINE_FIXTURE:require(engine_fixture['pins'][path]=={'mode':'100644','sha256':pin['sha256']},'original pin was resealed/refreshed')
    require(value['proof_expectations']=={'short':{'validation':534,'decoder':538,'persistence':827,'setconfig':1139,'startup':68,'consumer':11},'ordinary':{'validation':539,'decoder':538,'persistence':827,'setconfig':1139,'startup':68,'consumer':11},'dependencies':209,'compiled_mutants':16,'identity_negatives':215,'total_negatives':231,'raw_validator_dependencies':21,'raw_interface_controls':6},'current proof expectation substitution/type/count')

def guard_identity(value):
    require((value['schema_name'],value['schema_version'],value['candidate'],value['base'],value['candidate_tree'],value['candidate_direct_parent'])==('glyph_gp_val039_c022_consumer_replay',1,C,B,TREE,B),'039 replay identity/type substitution')
    require(type(value['schema_version'])is int and value['engine_path']==ENGINE and value['engine_fixture']==ENGINE_FIXTURE,'engine/fixture path substitution')

def parse_fixture(raw):
    require(sha(raw)==FIXTURE_SHA,'039 replay fixture byte substitution')
    value=json.loads(raw,object_pairs_hook=unique);guard_identity(value);return value

def verify_fixture(root):
    """Read-only immutable contract. Never calls campaign.authenticate."""
    root=Path(root).resolve();value=parse_fixture(regular(root,FIXTURE))
    require(git(root,'rev-list','--parents','-n','1',C).decode().split()==[C,B]and git(root,'rev-parse',C+'^{tree}').decode().strip()==TREE,'C direct parent/tree')
    trees={ref:tree_rows(git(root,'ls-tree','-r','-z',ref))for ref in (B,C)}
    for ref,key in ((B,'historical_snapshot'),(C,'candidate_snapshot')):
        snapshot=value[key];require(len(trees[ref])==snapshot['tracked_count']and sha(git(root,'ls-tree','-r','-z',ref))==snapshot['raw_tree_sha256'],'full immutable snapshot census/hash')
    guard_critical(critical_rows(trees[B]),critical_rows(trees[C]),value)
    require(sha(git(root,'diff-tree','-r','--no-renames','--raw','-z',B,C))==value['complete_raw_candidate_delta_sha256'],'complete raw NUL inventory')
    changed=sorted(p for p in set(trees[B])|set(trees[C])if trees[B].get(p)!=trees[C].get(p));require(changed==value['changed_inventory']and len(changed)==18,'complete eighteen-path inventory')
    original=object_inputs(root,C,value['original_C_inputs']);require(sha(original[ENGINE])==ENGINE_SHA and blob(original[ENGINE])==ENGINE_BLOB,'immutable C engine')
    tables=literal_tables(original[ENGINE],{'BASE','PIN_PATHS','SOURCE_PATHS','EXPECTED_CASES'})
    original_fixture=json.loads(original[ENGINE_FIXTURE],object_pairs_hook=unique)
    validate_original_pins(value,original,original_fixture,tables)
    require(sorted(tables['SOURCE_PATHS'])==value['critical_production_paths'],'original seven critical production literals')
    require(set(value['consumer_lanes'])==set(CONSUMERS)and len(CONSUMERS)==16,'finite historical lane omission/extra')
    for lane,record in value['consumer_lanes'].items():
        require(record['root']==B,'historical lane root')
        expected=['python3','tools/test_glyph_c021_campaign_transition.py']if lane=='transition038'else['python3','tools/check_glyph_c021_proof_replay.py']+([]if lane=='recovery021'else['--consumer',lane])
        require(record['command']==expected,'historical command substitution '+lane)
    roots=value['historical_object_roots'];require(type(roots)is list and len(roots)==55 and roots==sorted(set(roots))and B in roots,'finite historical object roots')
    for identity in roots:require(re.fullmatch('[0-9a-f]{40}',identity)and git(root,'cat-file','-t',identity)==b'commit\n','historical object root type')
    wrapper=value['historical_wrapper'];require(wrapper['path']=='tools/check_glyph_c021_proof_replay.py','historical wrapper path')
    object_inputs(root,B,{wrapper['path']:{k:wrapper[k]for k in ('mode','blob','sha256')}})
    require(value['retained_C_standalone_CLI_failure']['result']=='FAIL: critical object mode/type'and value['retained_C_standalone_CLI_failure']['log_sha256']=='68d1dc73a02431c79ffd5fd77135d6809420c16c57540079d72e964c9632a600','standalone original failure erased/substituted')
    return value

def verify_snapshot(root,revision,expected):
    rows=tree_rows(git(root,'ls-tree','-r','-z',revision));require(len(rows)==expected['tracked_count']and sha(git(root,'ls-tree','-r','-z',revision))==expected['raw_tree_sha256'],'snapshot immutable tree extent/hash')
    require(git(root,'rev-parse','HEAD').decode().strip()==revision,'private snapshot HEAD')
    wanted=b''.join((v['mode']+' '+v['blob']+' 0\t'+p+'\0').encode()for p,v in sorted(rows.items()))
    require(git(root,'ls-files','--stage','-z')==wanted,'private snapshot index mode/blob/stage')
    require(git(root,'ls-files','-v','-z')==b''.join(('H '+p+'\0').encode()for p in sorted(rows)),'private index flags')
    for path,entry in rows.items():
        require(entry['kind']=='blob'and entry['mode']in ('100644','100755'),'private unsupported Git object')
        require(blob(regular(root,path,0o644 if entry['mode']=='100644'else 0o755))==entry['blob'],'private full live bytes/mode '+path)
    require(git(root,'status','--porcelain','--untracked-files=all')==b'','private snapshot dirty/untracked')
    return rows

def materialize(root,directory,revision,value):
    require(revision in (B,C)and not directory.exists(),'fresh exact C/E root required');directory.mkdir(parents=True)
    # Explicit authenticated roots; no network, alternates or copying .git/objects.
    roots=sorted(set(value['historical_object_roots'])|{revision})
    pack=git(root,'pack-objects','--revs','--stdout',input=('\n'.join(roots)+'\n').encode(),timeout=60)
    git(directory,'-c','init.templateDir=','init','-q');git(directory,'index-pack','--stdin',input=pack,timeout=60)
    require(not(directory/'.git/objects/info/alternates').exists(),'private object alternates forbidden')
    git(directory,'checkout','--detach',revision)
    verify_snapshot(directory,revision,value['candidate_snapshot'if revision==C else'historical_snapshot'])
    return {'revision':revision,'object_roots':roots,'pack_sha256':sha(pack),'tracked_count':value['candidate_snapshot'if revision==C else'historical_snapshot']['tracked_count'],'classification':'EXACT_FINITE_PRIVATE_GIT_SNAPSHOT_NO_NETWORK'}

def authenticate(root):
    import glyph_c022_campaign_transition as campaign
    require(campaign.present(root)and campaign.C==C and campaign.B==B and campaign.TREE==TREE,'exact039 campaign module unavailable')
    proof=campaign.authenticate(root);require(proof['contract']=='c022_rgb_targets'and proof['phase']in PHASES and proof['candidate']==C and proof['base']==B,'039 phase/source identity')
    campaign.source_contract(root)
    require(C in proof['object_roots']and B in proof['object_roots'],'039 immutable C/E object roots omitted')
    return proof

def load_engine(root,value):
    module_path=root/ENGINE;require(sha(regular(root,ENGINE))==ENGINE_SHA,'private C engine changed')
    spec=importlib.util.spec_from_file_location('glyph_c022_immutable_engine',module_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    require(module.BASE==B and len(module.PIN_PATHS)==209,'private engine literals changed')
    return module

def raw_interface_controls(root,directory,evidence):
    records=[]
    for abi in ('short','ordinary'):
        validator=evidence['raw_validators'][abi];binary=Path(validator['path']);require(binary.is_file()and sha(binary.read_bytes())==validator['sha256'],'raw validator executable substitution')
        for path,digest in validator['source_pins'].items():require(sha(regular(root,path))==digest,'raw validator source pin '+path)
        d=directory/abi
        for name,body,expected in (('empty_valid',b'',0),('malformed',b'\x80',2),('archived_original',None,1)):
            raw=d/('raw-interface-'+name+'.bin')if body is not None else d/'archived-original.raw.bin'
            if body is not None:raw.write_bytes(body)
            cmd=[str(binary),'--config-raw',str(raw)];result=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=10)
            parsed=json.loads(result.stdout,object_pairs_hook=unique)
            require(result.returncode==expected and not result.stderr and set(parsed)=={'accepted','decoded','error'},'actual raw JSON/exit/stderr contract')
            require(parsed['accepted']==(expected==0)and parsed['decoded']==(expected!=2),'actual raw decoded/accepted contract')
            if expected==1:require(parsed['error']=='Config contains an invalid RGB target','archive exact expected RGB rejection')
            records.append({'abi':abi,'case':name,'command':cmd,'exit':result.returncode,'stdout':parsed,'stderr':'','raw_sha256':sha(raw.read_bytes())})
    return records

def check_current_evidence(evidence,value,negative_controls=True):
    expectation=value['proof_expectations']
    require(len(evidence['dependencies'])==209 and set(evidence['dependencies'])==set(value['original_C_inputs'])-{ENGINE_FIXTURE},'full original209 source closure')
    require(len(evidence['negative_controls'])==(231 if negative_controls else 0),'original complete negative controls')
    for abi in ('short','ordinary'):
        rows=evidence['abis'][abi];want=expectation[abi]
        for suite in ('validation','decoder','persistence','setconfig'):require(rows[suite]['cases']==want[suite],'actual current case omission '+abi+'/'+suite)
        require(rows['setconfig']['missing_callback_cases']==1,'fresh actual missing callback omitted')
        require(len(rows['startup']['cases'])==68 and all(r['exit']==0 and not r['stderr']for r in rows['startup']['cases']),'actual68 startup schedules')
        require(rows['consumer']['runs']==11 and rows['consumer']['unchanged_valid']=='BYTE_EXACT'and rows['consumer']['legacy_corrected_all76pixels_all60slots']=='BYTE_EXACT','actual consumer equality omitted')
        require(rows['archived_owner']['classification']=='ARCHIVED_HISTORICAL_NOT_FRESH'and rows['archived_owner']['all_unrelated_semantic_fields']=='IDENTICAL','archive minimal-repair proof')
        validator=evidence['raw_validators'][abi];require(len(validator['source_pins'])==21 and re.fullmatch('[0-9a-f]{64}',validator['sha256']),'raw validator source/compile closure')
    require(len(evidence['raw_interface_controls'])==6,'raw JSON/exit controls omitted')
    require(evidence['default_delta']['corrected_sha256']=='7a1bc4b09745767d7a34d4b2495edfe22af5d3b4b960eb822c361ac16590803c'and evidence['default_delta']['other12blocks_and_unrelated_source']=='BYTE_EXACT','approved source-default correction only')

def run_candidate_replay(root,directory,value,negative_controls=True):
    """Explicit preparatory API; caller supplies independent campaign authentication."""
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    candidate=directory/'candidate';support=materialize(root,candidate,C,value);module=load_engine(candidate,value)
    pins=module.authenticate_inputs(candidate)
    require(len(pins)==209 and set(pins)==set(value['original_C_inputs'])-{ENGINE_FIXTURE},'original engine authentication/pins')
    # Original authenticate_repository/main is intentionally preserved and not
    # called: its actual FAIL remains recorded. The native039 guard ran above.
    evidence=module.run_host(candidate,directory/'host-output',negative_controls=negative_controls,pins=pins)
    evidence['raw_interface_controls']=raw_interface_controls(candidate,directory/'host-output',evidence)
    evidence['classification']='AUTHENTICATED_IMMUTABLE_C022_ACTUAL_HOST_EXECUTION'
    evidence['immutable_candidate']=C;evidence['immutable_base']=B;evidence['support']=support
    evidence['retained_C_standalone_CLI_failure']=value['retained_C_standalone_CLI_failure']
    check_current_evidence(evidence,value,negative_controls)
    verify_snapshot(candidate,C,value['candidate_snapshot'])
    (directory/'current-execution.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence

def identity_negatives(root,value):
    import copy
    original=object_inputs(root,C,value['original_C_inputs']);tables=literal_tables(original[ENGINE],{'BASE','PIN_PATHS','SOURCE_PATHS','EXPECTED_CASES'});engine_fixture=json.loads(original[ENGINE_FIXTURE]);records=[]
    def reject(name,operation):
        try:operation()
        except (ValueError,AssertionError,KeyError,TypeError):records.append({'name':name,'rejected':True,'classification':'ACTUAL039_GUARD_NEGATIVE'});return
        raise ReplayError('039 guard negative unexpectedly passed '+name)
    actual_E=value['native_critical_E'];actual_C=value['native_critical_C']
    for ref,rows in (('E',actual_E),('C',actual_C)):
        for path in rows:
            changed=copy.deepcopy(rows);del changed[path]
            reject('critical_omission/'+ref+'/'+path,lambda changed=changed,ref=ref:guard_critical(changed if ref=='E'else actual_E,changed if ref=='C'else actual_C,value))
    for path,entry in actual_E.items():
        if entry['mode']!='100755':continue
        for field,new in (('mode','100644'),('blob','0'*40),('kind','tree')):
            changed=copy.deepcopy(actual_C);changed[path][field]=new
            reject('executable_'+field+'/'+path,lambda changed=changed:guard_critical(actual_E,changed,value))
    for path in value['critical_production_paths']:
        changed=copy.deepcopy(actual_C);changed[path]['mode']='100755';reject('production_mode/'+path,lambda changed=changed:guard_critical(actual_E,changed,value))
    changed=copy.deepcopy(actual_C);changed['src/unknown_c022_helper.cpp']={'mode':'100644','kind':'blob','blob':'0'*40};reject('unknown_critical_helper',lambda:guard_critical(actual_E,changed,value))
    for path in value['original_C_inputs']:
        changed=copy.deepcopy(value);del changed['original_C_inputs'][path];reject('original_pin_omission/'+path,lambda changed=changed:validate_original_pins(changed,original,engine_fixture,tables))
    for label in ('type','mode','hash','case_type','case_count'):
        changed=copy.deepcopy(value);path=ENGINE
        if label=='type':changed['original_C_inputs'][path]=[]
        elif label=='mode':changed['original_C_inputs'][path]['mode']='100755'
        elif label=='hash':changed['original_C_inputs'][path]['sha256']='0'*64
        elif label=='case_type':changed['proof_expectations']['short']['decoder']='538'
        else:changed['proof_expectations']['short']['decoder']=537
        reject('original_'+label,lambda changed=changed:validate_original_pins(changed,original,engine_fixture,tables))
    raw=regular(root,FIXTURE);mutated=bytearray(raw);mutated[len(mutated)//2]^=1;reject('fixture_one_byte',lambda:parse_fixture(mutated))
    for label in ('candidate','base','candidate_tree'):
        changed=copy.deepcopy(value);changed[label]='0'*40;reject(label+'_substitution',lambda changed=changed:guard_identity(changed))
    return records

def run_current(root,temporary,negative_controls=True):
    root=Path(root).resolve();value=verify_fixture(root);before=authenticate(root)
    evidence=run_candidate_replay(root,Path(temporary),value,negative_controls)
    if negative_controls:evidence['governance_negative_controls']=identity_negatives(root,value)
    require(authenticate(root)==before,'039 root/phase changed during current proof');verify_fixture(root)
    evidence['campaign_phase']=before['phase'];evidence['hardware']='NOT_CLAIMED';evidence['target_build']='NOT_RUN'
    (Path(temporary)/'current-execution.json').write_text(json.dumps(evidence,indent=2)+'\n');return evidence

def run_historical(root,directory,value,consumer):
    require(consumer in CONSUMERS,'unknown historical lane');directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    snapshot=directory/'historical-E';support=materialize(root,snapshot,B,value)
    env=dict(os.environ)
    for key in ('GLYPH_CHECKER_BASE','GLYPH_CHECKER_EXPECTED_MERGE_BASE','GLYPH_HOST_MOUNT_FAIL','GLYPH_HOST_CONFIG_FAIL','GLYPH_HOST_RGB_CTOR_OFFSETS'):env.pop(key,None)
    scratch=directory/'historical-tmp';scratch.mkdir();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',TMPDIR=str(scratch),GLYPH_CHECKER_BASE=B,GLYPH_CHECKER_EXPECTED_MERGE_BASE=B)
    lane=value['consumer_lanes'][consumer];command=[sys.executable,'-B','-u',*lane['command'][1:]]
    # The unchanged outer validation runner owns the process group and timeout.
    # No narrower inner timeout or private descendant-kill policy is introduced.
    stdout=directory/'historical.stdout.log';stderr=directory/'historical.stderr.log'
    with stdout.open('wb')as out,stderr.open('wb')as err:result=subprocess.run(command,cwd=snapshot,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
    record={'classification':'ACTUAL_IMMUTABLE_E_PREDECESSOR_EXECUTION_ONLY','consumer':consumer,'support':support,'command':command,'exit':result.returncode,'stdout':stdout.read_text(errors='replace'),'stderr':stderr.read_text(errors='replace'),'C022_execution':'SEPARATE_MANDATORY_DEFAULT_PROOF_REQUIRED','hardware':'NOT_CLAIMED'}
    (directory/'historical-execution.json').write_text(json.dumps(record,indent=2)+'\n')
    require(result.returncode==0 and'PASS'in record['stdout'],'preserved historical lane failed; actual outcome retained '+consumer+'\n'+record['stdout']+record['stderr'])
    verify_snapshot(snapshot,B,value['historical_snapshot']);return record

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--consumer',choices=CONSUMERS);parser.add_argument('--output',type=Path);args=parser.parse_args()
    try:
        value=verify_fixture(ROOT);before=authenticate(ROOT)
        def execute(directory):
            if args.consumer:
                result=run_historical(ROOT,directory,value,args.consumer)
                require(authenticate(ROOT)==before,'039 root/phase changed during historical lane');verify_fixture(ROOT)
                print('glyph_c022_proof_replay: PASS; ACTUAL_IMMUTABLE_E_PREDECESSOR_EXECUTION_ONLY consumer='+args.consumer+' C022_default=SEPARATE_MANDATORY_PROOF_REQUIRED phase='+before['phase'])
            else:
                result=run_current(ROOT,directory,negative_controls=True)
                print('glyph_c022_proof_replay: PASS; AUTHENTICATED_IMMUTABLE_C022_ACTUAL_HOST_EXECUTION phase='+before['phase'])
                print('validation=534/539 decoder=538/538 checked_load=827/827 SET=1139+1/1139+1 startup=68/68 consumer=11/11 original_negatives=231 MMD=209')
            print('original_C_standalone_CLI=RETAINED_FAIL hardware=NOT_CLAIMED target_build=NOT_RUN')
            return result
        if args.output:args.output.mkdir(parents=True,exist_ok=True);execute(args.output)
        else:
            with tempfile.TemporaryDirectory(prefix='glyph-c022-replay-',dir='/private/tmp'if Path('/private/tmp').is_dir()else None)as name:execute(Path(name))
        return 0
    except (ValueError,AssertionError,OSError,subprocess.SubprocessError)as error:print('glyph_c022_proof_replay: FAIL: '+str(error));return 1
if __name__=='__main__':raise SystemExit(main())
