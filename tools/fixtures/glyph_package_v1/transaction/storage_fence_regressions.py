"""Source/NOR startup refusal families; no device observation or automatic repair.

Synthetic namespaces remain distinct from optional exact historical Config bytes.
The actual current roots/control/previous revisions are UNKNOWN.
"""
import argparse, copy, hashlib, json, os, struct, subprocess, sys
from pathlib import Path
from run import dump_namespace


def response(raw, message):
    frames=raw.split(b'\0');assert frames[-1]==b'' and len(frames)==2
    encoded=frames[0];out=bytearray();at=0
    while at<len(encoded):
        code=encoded[at];at+=1;assert code and at+code-1<=len(encoded)
        out+=encoded[at:at+code-1];at+=code-1
        if code!=255 and at<len(encoded):out.append(0)
    assert out[0]==9
    return message.FromString(out[1:])


def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True,type=Path)
    p.add_argument('--corpus',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--historical-config',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.dont_write_bytecode=True;sys.path[:0]=[str(a.corpus/'proof'),str(a.corpus/'wire'),str(a.corpus.parents[1]/'tools/research')]
    import glyph_package_storage as m
    import glyph_package_fixtures as f
    import config_pb2 as cfg
    from source_native_oracle import SourceNativeOracle
    oracle=SourceNativeOracle(a.corpus/'wire');m.CONFIG_VALIDATOR=oracle.check_config;m.NATIVE_VALIDATOR=oracle.check;m.LEGACY_PROFILE_VALIDATOR=oracle.check_profile
    base=f.baseline(ultimate=True,backend=True)
    defaults=a.out/'defaults.pb';defaults.write_bytes(base['/config-v2.bin'][8:])
    cases=[]
    def add(name,disk,normal=False,diagnostic=None,selection=1<<24):cases.append((name,disk,normal,diagnostic,selection))
    add('healthy-compact',copy.deepcopy(base),True)
    prior=copy.deepcopy(base);prior['/config-v2.prev']=prior['/config-v2.bin'];add('current-and-identical-prior',prior,True)
    prior_only=copy.deepcopy(base);prior_only['/config-v2.prev']=prior_only.pop('/config-v2.bin');add('prior-only-rotation',prior_only,diagnostic='legacy: Config source invalid',selection=1<<25)
    legacy_only={'/config.bin':base['/config-v2.bin']};add('legacy-selected-without-roots',legacy_only,diagnostic='root0: absent/invalid',selection=1<<26)
    add('config-only',{'/config-v2.bin':base['/config-v2.bin']},diagnostic='root0: absent/invalid')
    for path in ['/ultimate-v2-0.bin','/ultimate-v2-1.bin','/ultimate-v2.ctrl']:
        disk=copy.deepcopy(base);del disk[path];add('missing-'+path[1:],disk,diagnostic='absent/invalid')
    for path in ['/config-v2.tmp','/ultimate-v2.ctmp']:
        disk=copy.deepcopy(base);disk[path]=base['/config-v2.bin'] if 'config' in path else base['/ultimate-v2.ctrl'];add('pending-'+path[1:],disk,diagnostic='legacy: temporary present')
    disk=copy.deepcopy(base);_,tree=m.config_body(disk['/config-v2.bin']);f.put(tree,210,0);disk['/config-v2.bin']=f.config_file(tree);add('pre-package-marker',disk,diagnostic='legacy: Config/store mismatch')
    disk=copy.deepcopy(base);_,tree=m.config_body(disk['/config-v2.bin']);f.put(tree,210,3);f.put(tree,211,1);disk['/config-v2.bin']=f.config_file(tree);add('managed-Config-no-package',disk,diagnostic='invalid package reservation')
    disk=copy.deepcopy(base);_,tree=m.config_body(disk['/config-v2.bin']);f.put(tree,211,2);disk['/config-v2.bin']=f.config_file(tree);add('future-Config-marker',disk,diagnostic='recognized newer storage')
    disk=copy.deepcopy(base);raw=bytearray(disk['/ultimate-v2.ctrl']);raw[-1]^=1;disk['/ultimate-v2.ctrl']=bytes(raw);add('corrupt-control',disk,diagnostic='control: absent/invalid')
    disk=copy.deepcopy(base);raw=bytearray(disk['/ultimate-v2-1.bin']);m.put32(raw,8,6);m.put32(raw,16,1);m.put32(raw,3904,m.crc(raw[:3904]));disk['/ultimate-v2-1.bin']=bytes(raw);add('slot-highwater-disagreement',disk,diagnostic='root slots disagree')
    disk=copy.deepcopy(base);disk['/config-v2.prev']=b'bad';add('invalid-prior-with-valid-current',disk,diagnostic='prior Config invalid')
    disk=copy.deepcopy(prior);disk['/config-v2.bin']=b'bad';add('bad-current-never-falls-back',disk,diagnostic='config.invalid',selection=0)
    old=cfg.Config.FromString(base['/config-v2.bin'][8:]);old.ClearField('profile_reference_digest');old.ClearField('ultimate_profile_migration_receipt');old.ClearField('ultimate_profile_root_format');old_body=old.SerializeToString(deterministic=True)
    disk=copy.deepcopy(base);disk['/config.bin']=struct.pack('<II',len(old_body),m.crc(old_body))+old_body
    add('retained-pre-fixed32-Config',disk,diagnostic='config.bin: retained input invalid')
    disk=f.completed_migration(3);disk={p:b for p,b in disk.items() if not p.startswith('/ultimate-v2')};add('legacy-roots-with-compact-marker',disk,diagnostic='root0: absent/invalid')
    for version in [2,3]:
        disk=f.completed_migration(version);add('completed-migration-'+str(version),disk,True)
    stages,_=f.package_plan(base,True,100)
    for stage,disk in stages.items():add('package-'+stage,disk,stage=='COMMITTED')
    historical=None
    if a.historical_config:
        body=a.historical_config.read_bytes();assert len(body)==280 and hashlib.sha256(body).hexdigest()=='804c2f86b78a70c5b25ce4eb5c8c301e8cd867d64a15dd023c9e75d98913363d'
        # Deliberately synthetic compact tuple, NOT reconstructed physical roots.
        disk=copy.deepcopy(base);root=bytearray(f.source_root(228,1));m.put32(root,16,53);m.put32(root,3904,m.crc(root[:3904]));root=bytes(root)
        disk.update({'/ultimate-v2-0.bin':root,'/ultimate-v2-1.bin':root,'/ultimate-v2.ctrl':f.source_control(root),'/config-v2.bin':struct.pack('<II',len(body),m.crc(body))+body})
        add('historical-Config-synthetic-roots',disk,True)
        retained=copy.deepcopy(disk);retained['/config.bin']=struct.pack('<II',len(old_body),m.crc(old_body))+old_body;add('historical-Config-retained-old-input',retained,diagnostic='config.bin: retained input invalid')
        historical={'config_body_sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'crc32':m.crc(body),'roots':'SYNTHETIC; no physical root/payload correspondence asserted'}
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
    results=[]
    def run(argv):
        c=subprocess.run(list(map(str,argv)),capture_output=True,text=True,timeout=30,env=env)
        if c.returncode:raise RuntimeError(str(argv)+'\n'+c.stdout+c.stderr)
    for index,(name,disk,normal,diagnostic,selection) in enumerate(cases):
        work=a.out/str(index);work.mkdir();dump_namespace(disk,work/'seed.namespace');run([a.binary,'seed',work/'seed.namespace',work/'seed.nor']);run([a.binary,'boot',work/'seed.nor',defaults,work])
        boot=json.loads((work/'boot.json').read_text());status=response((work/'status.cobs').read_bytes(),cfg.ProfileStoreResponse)
        assert boot['outcome']==(1 if normal else 6),(name,boot,status.diagnostic)
        if not normal:assert boot['recovery_visible'] and not boot['splash'] and status.status==8
        if diagnostic:assert diagnostic in status.diagnostic,(name,status.diagnostic,diagnostic)
        assert status.recovery_flags&((1<<24)|(1<<25)|(1<<26))==(0 if normal else selection),(name,status.recovery_flags,selection)
        assert not status.recovery_flags&(1<<21),(name,'local Config fence should not arise from reads')
        if normal:assert status.status==1 and status.recovery_flags==0
        elif selection or name=='bad-current-never-falls-back':assert status.recovery_flags&(1<<22)
        if name=='prior-only-rotation':assert status.store_incarnation==status.store_generation==0 and status.recovery_flags&0x32==0x32 and status.recovery_flags&(1<<30)
        if name=='historical-Config-retained-old-input':assert status.config_generation==223169280 and status.transaction_token_high_water==17293822569102712132 and status.store_incarnation==status.store_generation==0 and status.recovery_flags&0x32==0x32
        results.append({'name':name,'normal':normal,'outcome':boot['outcome'],'diagnostic':status.diagnostic,'recovery_flags':status.recovery_flags,'config_generation':status.config_generation,'store_incarnation':status.store_incarnation,'store_generation':status.store_generation,'transaction_highwater':status.transaction_token_high_water,'raw_nor_unchanged':boot['unchanged']})
        (a.out/'results.json').write_text(json.dumps({'cases':results,'historical':historical,'physical_filesystem':'UNKNOWN','hardware_operations':0},indent=2)+'\n')
    # A selected predecessor is observable but is never active G6 receipt truth.
    setter=cfg.ProfileStoreRequest(protocol_version=2,operation=10,request_token=9001,profile_id=1,expected_store_incarnation=42,expected_store_generation=7,expected_config_generation=m.crc(base['/config-v2.bin'][8:]))
    semantic=cfg.ProfileStoreRequest();semantic.CopyFrom(setter);semantic.request_token=0
    digest=hashlib.sha256(b'Glyph.ProfileStore.Request.v1\0'+semantic.SerializeToString(deterministic=True)).digest()
    _,tree=m.config_body(base['/config-v2.bin']);f.put(tree,204,9001);f.put(tree,205,digest.hex());f.put(tree,206,1);f.put(tree,207,7)
    prior=copy.deepcopy(base);prior['/config-v2.prev']=f.config_file(tree);del prior['/config-v2.bin']
    requests=[cfg.ProfileStoreRequest(protocol_version=2,operation=11,request_token=9001).SerializeToString(deterministic=True),setter.SerializeToString(deterministic=True)]
    work=a.out/'prior-active-replay';work.mkdir();dump_namespace(prior,work/'seed.namespace');run([a.binary,'seed',work/'seed.namespace',work/'seed.nor'])
    (work/'requests.bin').write_bytes(struct.pack('<I',len(requests))+b''.join(struct.pack('<I',len(r))+r for r in requests))
    run([a.binary,'recovery-transport',work/'seed.nor',work/'requests.bin',work])
    frames=(work/'responses.cobs').read_bytes().split(b'\0');assert len(frames)==3 and not frames[-1]
    states=[]
    for raw in frames[:-1]:
        r=response(raw+b'\0',cfg.ProfileStoreResponse);assert r.status==8 and not r.profile_id and not r.transaction_operation;states.append(r.status)
    receipt=json.loads((work/'transport.json').read_text());assert receipt['programs']==receipt['erases']==0 and receipt['unchanged']
    assert (work/'after.nor').read_bytes()==(work/'seed.nor').read_bytes()
    results.append({'name':'prior-is-not-active-G6-query-or-setter','statuses':states,'zero_write':True,'reconciliation':'UNCERTAIN'})
    for mode,diag in [('runtime-transport','package: runtime fence'),('local-fence-transport','config.local_fence')]:
        work=a.out/mode;work.mkdir();dump_namespace(base,work/'seed.namespace');run([a.binary,'seed',work/'seed.namespace',work/'seed.nor'])
        request=cfg.ProfileStoreRequest(protocol_version=2,operation=1,request_token=1).SerializeToString(deterministic=True)
        (work/'requests.bin').write_bytes(struct.pack('<II',1,len(request))+request)
        run([a.binary,mode,work/'seed.nor',work/'requests.bin',work])
        r=response((work/'responses.cobs').read_bytes(),cfg.ProfileStoreResponse);assert r.status==8 and r.diagnostic==diag,(mode,r)
        assert bool(r.recovery_flags&(1<<21))==(mode=='local-fence-transport') and r.recovery_flags&(1<<22) and r.recovery_flags&(1<<27)
        receipt=json.loads((work/'transport.json').read_text());assert receipt['programs']==receipt['erases']==0 and receipt['unchanged']
        results.append({'name':mode,'diagnostic':r.diagnostic,'recovery_flags':r.recovery_flags,'zero_inspection_writes':True})
    (a.out/'results.json').write_text(json.dumps({'cases':results,'historical':historical,'physical_filesystem':'UNKNOWN','hardware_operations':0},indent=2)+'\n')
    oracle.close();print(json.dumps({'cases':len(results),'normal':sum(x.get('normal',False) for x in results),'hardware_operations':0,'physical_filesystem':'UNKNOWN'}))
if __name__=='__main__':main()
