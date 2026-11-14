#!/usr/bin/env python3
"""Host-only actual SET_CONFIG proof; no serial, firmware build or device access.

Uses an explicit existing synthetic managed namespace. A copied host harness is
extended only to frame CMD_SET_CONFIG instead of CMD_PROFILE_STORE. All production
Config/PacketIO/Persistence/ProfileStore bodies remain unchanged.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, shutil, struct, subprocess, sys, zlib

def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,required=True,help='Pinned source export')
    ap.add_argument('--dependency-repo',type=Path,required=True,help='Same production source with existing .pio host dependencies')
    ap.add_argument('--seed-namespace',type=Path,required=True,help='Existing synthetic namespace, never physical reconstruction')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--framework',type=Path,required=True)
    a=ap.parse_args();repo=a.repo.resolve();deps=a.dependency_repo.resolve();out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    fixture=repo/'tools/fixtures/glyph_package_v1/transaction'
    draft=out/'host-harness';shutil.copytree(fixture,draft,ignore=shutil.ignore_patterns('__pycache__'))
    src=(draft/'harness.cpp').read_text()
    gate='if(!std::strcmp(argv[1],"transport")||!std::strcmp(argv[1],"recovery-transport")'
    assert src.count(gate)==1
    src=src.replace(gate,'if(!std::strcmp(argv[1],"set-config-transport")||!std::strcmp(argv[1],"transport")||!std::strcmp(argv[1],"recovery-transport")')
    old='packet.write(uint8_t(CMD_PROFILE_STORE))==1&&packet.write(request.data(),request.size())==request.size()&&packet.end()'
    new='packet.write(uint8_t(!std::strcmp(argv[1],"set-config-transport")?CMD_SET_CONFIG:CMD_PROFILE_STORE))==1&&packet.write(request.data(),request.size())==request.size()&&packet.end()'
    assert src.count(old)==1;src=src.replace(old,new);(draft/'harness.cpp').write_text(src)
    # Existing dependency checkout must match every production input; include
    # its entire firmware-facing directories, not merely translation units.
    checked={}
    for directory in ['HAL','include','src','config','schema']:
        for p in (repo/directory).rglob('*'):
            if p.is_file():
                rel=p.relative_to(repo);q=deps/rel
                assert q.is_file() and q.read_bytes()==p.read_bytes(), ('Source drift',str(rel))
                checked[str(rel)]=sha(p.read_bytes())
    (out/'production-inputs.json').write_text(json.dumps(checked,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('selector_host_build',draft/'build.py');build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
    binary=build.build(deps,out/'build',a.framework,deps/'.pio/libdeps/glyph_mk6/Nanopb',sanitize=True)
    sys.path[:0]=[str(repo/'tools'),str(fixture)]
    import glyph_serial_config_tool as transport
    from run import load_namespace,dump_namespace
    pb,_,_=transport.load_runtime_proto_modules(repo)
    disk=load_namespace(a.seed_namespace);original=pb.Config();original.ParseFromString(disk['/config-v2.bin'][8:])
    assert original.ultimate_profile_root_format==3 and original.managed_format==1
    assert any(r.managed_format==1 for r in original.game_mode_configs)
    # Synthetic fixture only: make the backend table match the physical contract's
    # one-based XInput1/GameCube2/Configurator3/Switch4 identities. Original
    # managed rows, root files and compact receipt are preserved byte-for-byte.
    routes = {b.backend_id: b.SerializeToString() for b in original.communication_backend_configs}
    del original.communication_backend_configs[:]
    for backend in [pb.COMMS_BACKEND_XINPUT, pb.COMMS_BACKEND_GAMECUBE,
                    pb.COMMS_BACKEND_CONFIGURATOR, pb.COMMS_BACKEND_NINTENDO_SWITCH]:
        entry = original.communication_backend_configs.add()
        if backend in routes: entry.ParseFromString(routes[backend])
        else: entry.backend_id, entry.default_mode_config = backend, 1
    original.default_backend_config = 2
    original.default_usb_backend_config = 1
    xinput, switch = [1], [4]
    current=pb.Config();current.CopyFrom(original);current.default_usb_backend_config=switch[0]
    current_raw=current.SerializeToString(deterministic=True);target=original.SerializeToString(deterministic=True)
    def wrap(b):return struct.pack('<II',len(b),zlib.crc32(b))+b
    # A valid ordinary default save rotates old current to prior. Preserve that
    # publication chain in the synthetic seed; changing only current out of band
    # can correctly fence a namespace whose terminal receipt binds old current.
    disk['/config-v2.prev']=disk['/config-v2.bin']
    disk['/config-v2.bin']=wrap(current_raw)
    dump_namespace(disk,out/'seed.namespace');(out/'current.pb').write_bytes(current_raw);(out/'target.pb').write_bytes(target)
    # requests() uses count + length + payload. The sole payload is complete
    # Config; the host-only harness frames it with real PacketIO command4.
    (out/'one-set-request.bin').write_bytes(struct.pack('<II',1,len(target))+target)
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
    logs=[]
    def run(*argv):
        r=subprocess.run([str(binary),*map(str,argv)],capture_output=True,env=env)
        logs.append({'argv':[str(binary),*map(str,argv)],'returncode':r.returncode,'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace')})
        (out/'commands.json').write_text(json.dumps(logs,indent=2)+'\n')
        assert r.returncode==0,(argv,r.stderr.decode(errors='replace'))
    run('seed',out/'seed.namespace',out/'seed.nor')
    episode=out/'episode';episode.mkdir()
    run('set-config-transport',out/'seed.nor',out/'one-set-request.bin',episode)
    request=transport.cobs_decode((episode/'requests.cobs').read_bytes())
    response=transport.cobs_decode((episode/'responses.cobs').read_bytes())
    assert request==bytes([4])+target and response==bytes([6]), 'Exact single SET and empty success acknowledgement'
    observed=load_namespace(episode/'namespace.bin')
    assert (episode/'saved-config.pb').read_bytes()==target
    assert observed['/config-v2.bin']==wrap(target)
    assert observed['/config-v2.prev']==disk['/config-v2.bin']
    assert observed.keys()==disk.keys()|{'/config-v2.prev'}
    protected=[p for p in disk if p not in ('/config-v2.bin','/config-v2.prev')]
    assert all(observed[p]==disk[p] for p in protected)
    report={'result':'PASS','kind':'Synthetic managed-root3 actual production SET_CONFIG host proof','configDelta':{'field':'default_usb_backend_config','before':switch[0],'after':xinput[0]},'configBeforeSha256':sha(current_raw),'configTargetSha256':sha(target),'setConfigRequests':1,'ack':'Exact empty CMD_SUCCESS6','allProtectedNamespaceFilesExact':protected,'configPriorExactOldCurrent':True,'liveAndSavedConfigExactTarget':True,'productionInputs':len(checked),'compiledProduction':['ConfiguratorBackend','PacketIO','Persistence','ProfileStore','Configured Glyph validators','LittleFS'],'substitutions':['Host-only input/output stream','Synthetic NOR/LittleFS mount','Platform-only host facades'],'limits':['Synthetic namespace does not reconstruct current physical flash','Separate exact Stage-H368B Config-pair source-validator proof remains necessary','No physical durability, receiver, installed-image attestation or timing claim','No firmware source changes or firmware build; no serial/device access']}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
