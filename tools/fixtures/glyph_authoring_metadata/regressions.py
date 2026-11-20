#!/usr/bin/env python3
"""Bounded metadata codecs and real managed LittleFS/backend regression proof.

No devices, source rewriting, admission overrides or historical-oracle changes.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import zlib

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tools/fixtures/glyph_package_v1/transaction')]
from run import dump_namespace,load_namespace
from check_glyph_profile_native_ultimate import program


def manifest(names,mask=None):
    mask=(1<<len(names))-1 if mask is None else mask
    return b'\1'+struct.pack('<I',mask)+b''.join(bytes([len(n)])+n for n in names)


def batch(items):
    return struct.pack('<I',len(items))+b''.join(struct.pack('<I',len(x))+x for x in items)


def frames(raw):
    result=[]
    assert raw.endswith(b'\0')
    for frame in raw.split(b'\0')[:-1]:
        at=0;body=bytearray()
        while at<len(frame):
            code=frame[at];at+=1
            assert code and at+code-1<=len(frame)
            body+=frame[at:at+code-1];at+=code-1
            if code!=255 and at<len(frame):body.append(0)
        result.append((body[0],bytes(body[1:])))
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--all-cuts',action='store_true');a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    counts={}
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1'}
    def run(*args):
        p=subprocess.run(list(map(str,args)),cwd=ROOT,env=env,capture_output=True,text=True)
        assert p.returncode==0,(args,p.stdout,p.stderr)
        return p.stdout
    def invoke(*args):return run(a.binary,*args)
    lib=out/'codec.dylib'
    run('c++','-std=c++17','-shared','-fPIC','-I',ROOT/'include',ROOT/'tools/fixtures/glyph_authoring_metadata/codec_ffi.cpp',ROOT/'src/core/PackageStorageFormat.cpp','-o',lib)
    codec=ctypes.CDLL(str(lib));codec.manifest_valid.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
    codec.rich_header.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t]
    codec.record_valid.argtypes=[ctypes.c_void_p,ctypes.c_size_t];codec.wrapper_size.argtypes=[ctypes.c_void_p,ctypes.c_size_t];codec.wrapper_size.restype=ctypes.c_size_t
    codec.charge.argtypes=[ctypes.c_size_t];codec.charge.restype=ctypes.c_uint64
    maximum=manifest([b'x'*12]*26+[b'y'*13]*2)
    good=[manifest([b'a']),manifest([b'a',b'a']),manifest(['é猫'.encode()]),manifest(['\ufffd'.encode()]),manifest([b'a'*64]),maximum]
    bad=[manifest([b'a'*65]),manifest([b'\0']),manifest([b'\x80']),manifest([b'\xc0\xaf']),manifest([b'\xed\xa0\x80']),manifest([b'\xf4\x90\x80\x80']),manifest([b'a'],0),manifest([b'a'],1<<28),manifest([b'a'])[:-1],manifest([b'a'])+b'x',maximum+b'x',manifest([b'x'*13]*28)]
    for b in good:assert codec.manifest_valid(b,len(b)),b
    for b in bad:assert not codec.manifest_valid(b,len(b)),b
    counts['manifest']=len(good)+len(bad)
    assert len(maximum)==371
    def record(wrapper,meta):
        payload=wrapper+meta;h=ctypes.create_string_buffer(128)
        assert codec.rich_header(h,payload,len(wrapper),len(meta))
        return h.raw+payload
    for wrapper,meta in [(b'x',good[0]),(b'x'*3341,maximum),(b'x',b'\x7f')]:
        b=record(wrapper,meta);assert codec.record_valid(b,len(b));assert codec.wrapper_size(b,len(b))==len(wrapper)
        changed=bytearray(b);changed[-1]^=1
        assert not codec.record_valid(bytes(changed),len(b))
        assert hashlib.sha256(b).digest()!=hashlib.sha256(changed).digest()
    max_record=record(b'x'*3341,maximum);assert len(max_record)==3840
    assert not codec.record_valid(max_record+b'x',3841)
    for n in (0,1,3342,0xffffffff):
        b=bytearray(max_record);struct.pack_into('<I',b,20,n)
        assert not codec.record_valid(bytes(b),len(b))
    assert codec.charge(3469)==codec.charge(3840)==4096 and codec.charge(3841)==8192
    counts['record_and_capacity']=16
    gen=out/'generated';gen.mkdir(exist_ok=True)
    run(sys.executable,'-m','grpc_tools.protoc','-I'+str(ROOT/'schema/haybox'),'--python_out='+str(gen),ROOT/'schema/haybox/config.proto',ROOT/'schema/haybox/package.proto')
    sys.path.insert(0,str(gen));import config_pb2 as cfg;import package_pb2 as pb
    pack=lambda x:x.SerializeToString(deterministic=True)
    source=cfg.Config(ultimate_profile_root_format=2,ultimate_profile_store_format=1,ultimate_profile_store_incarnation=42,default_usb_backend_config=1,profile_reference_digest=bytes(32),ultimate_profile_migration_receipt=bytes(32))
    source.communication_backend_configs.add(backend_id=cfg.COMMS_BACKEND_XINPUT)
    raw=pack(source);root=bytearray(3904);struct.pack_into('<4sHHII',root,0,b'PDS2',2,0,1,42);root=bytes(root)+struct.pack('<I',zlib.crc32(root))
    control=struct.pack('<4sII',b'PSC2',2,len(root));control+=struct.pack('<I',zlib.crc32(control)^zlib.crc32(root))+root
    disk={'/config-v2.bin':struct.pack('<II',len(raw),zlib.crc32(raw))+raw,'/ultimate-v2-0.bin':root,'/ultimate-v2-1.bin':root,'/ultimate-v2.ctrl':control,'/keep.bin':b'untouched'}
    seed=out/'seed';seed.mkdir(exist_ok=True);dump_namespace(disk,seed/'files');invoke('seed',seed/'files',seed/'seed.nor');nor=seed/'seed.nor'
    def body(name='Rich',rich=True,maximum_native=False):
        b=pb.PackageBody(version=2 if rich else 1,name=name);b.row.name=name;b.row.layout_plate=cfg.LAYOUT_PLATE_FGC
        b.native_body=program(cfg,cfg.GameModeConfig(mode_id=cfg.MODE_ULTIMATE),[]).native_payload
        if maximum_native:
            native=bytearray((ROOT/'docs/runtime_config/profile_native_ultimate/design_evidence/maximum-native.body').read_bytes());native[28:60]=b.native_body[28:60];b.native_body=bytes(native)
        if rich:b.authoring_metadata=maximum
        return b
    def req(op,token,key=0,revision=0,**fields):
        root=max([disk[f'/ultimate-v2-{i}.bin'] for i in (0,1)],key=lambda b:struct.unpack_from('<I',b,8)[0])
        raw=disk['/config-v2.bin'][8:]
        return pb.PackageEnvelope(protocol_version=3 if op==15 else 4,request_token=token,operation=op,expected_store_generation=struct.unpack_from('<I',root,8)[0],expected_store_incarnation=42,expected_config_generation=zlib.crc32(raw),expected_config_sha256=hashlib.sha256(raw).digest(),target_id=key,expected_revision=revision,**fields)
    def execute(request,label,expected=1,cut=-1):
        nonlocal nor,disk
        work=out/label;work.mkdir(exist_ok=True);(work/'request').write_bytes(pack(request));invoke('execute',nor,work/'request',work,cut)
        res=pb.PackageResponse.FromString((work/'response.pb').read_bytes())
        if expected is not None:assert res.status==expected,(label,res)
        disk=load_namespace(work/'namespace.bin');nor=work/'unwound.nor'
        return res,work
    # Closed scanner + canonical nanopb reencode: both versions, malformed tag7,
    # duplicates, unknown/misordered fields and the conservative maximum shape.
    wire_cases=[]
    b1=body('Legacy',False);b2=body('Rich')
    def wire_case(b,expected):
        wire_cases.append((pack(req(15,99,package_body=b)),expected))
    wire_case(pack(b1),True);wire_case(pack(b2),True)
    wire_case(pack(b1)+b'\x3a\x07'+manifest([b'a']),False)
    b=pb.PackageBody.FromString(pack(b2));b.ClearField('authoring_metadata');wire_case(pack(b),False)
    for suffix in [b'\x3a\x07'+manifest([b'a']),b'\x40\x01',b'\x08\x02']:
        wire_case(pack(b2)+suffix,False)
    wire_case(pack(body('Max',maximum_native=True)),True)
    # Conservative wire maximum need not be source-valid: strict wire proof is
    # independent of native/context admission, which still runs before writes.
    maximum_body=pb.PackageBody(version=2,name='S'*32,display_rank=0xffffffff,authoring_metadata=maximum)
    row=maximum_body.row;row.name='R'*17;row.menu_button_icon.extend([45]*7)
    for i in range(10):row.socd_pairs.add(button_dir1=60,button_dir2=60,socd_type=5)
    for i in range(60):row.button_remapping.add(physical_button=60,activates=60)
    row.activation_binding.extend([60]*4);row.layout_plate=4;row.applicable_backends.extend([10]*15)
    maximum_body.native_body=body(maximum_native=True).native_body
    maximum_body.rgb.default_color=0xffffffff;maximum_body.rgb.animation=5;maximum_body.rgb.speed=255
    for i in range(60):maximum_body.rgb.button_colors.add(button=1,color=0xffffffff)
    assert len(pack(maximum_body))==4865
    maximum_request=pb.PackageEnvelope(protocol_version=3,request_token=0xffffffffffffffff,operation=15,expected_store_generation=0xffffffff,expected_store_incarnation=0xffffffff,expected_config_generation=0xffffffff,expected_config_sha256=b'x'*32,package_body=pack(maximum_body))
    assert len(pack(maximum_request))==4938
    wire_cases.append((pack(maximum_request),True))
    (out/'wire.batch').write_bytes(batch([b for b,e in wire_cases]));invoke('wire-requests',out/'wire.batch',out/'wire.json')
    actual=json.loads((out/'wire.json').read_text())
    for result,(_,expected) in zip(actual,wire_cases):assert result['canonical_request']==expected and result['canonical_body']==expected,(result,expected)
    counts['package_wire']=len(wire_cases)
    legacy,_=execute(req(15,100,package_body=pack(body('Legacy',False))),'legacy-create')
    legacy_nor=nor;legacy_disk=dict(disk)
    rich,_=execute(req(15,200,package_body=pack(body('Rich'))),'rich-create')
    record_path=lambda key,rev:f'/ultpkg-{key:08x}-{rev:08x}.bin'
    rich_bytes=disk[record_path(2,1)];assert struct.unpack_from('<H',rich_bytes,4)[0]==3 and rich_bytes.endswith(maximum)
    legacy_bytes=disk[record_path(1,1)];assert struct.unpack_from('<H',legacy_bytes,4)[0]==2
    # A foreign future writer may persist an opaque bounded version. Change only
    # the metadata, and reseal the existing record/root/intent integrity witnesses.
    future=bytearray(rich_bytes);wrapper_n=struct.unpack_from('<I',future,20)[0]
    future[128+wrapper_n]=127
    struct.pack_into('<I',future,28,zlib.crc32(future[128:]));struct.pack_into('<I',future,112,0)
    struct.pack_into('<I',future,112,zlib.crc32(future[:128]))
    disk[record_path(2,1)]=bytes(future)
    installed_metadata=bytes(future[128+wrapper_n:])
    current=cfg.Config.FromString(disk['/config-v2.bin'][8:])
    for path,b in list(disk.items()):
        lead=16 if path=='/ultimate-v2.ctrl' else 0
        if not (path.startswith('/ultimate-v2-') or lead) or len(b)!=4420+lead:continue
        root=bytearray(b[lead:]);count=struct.unpack_from('<H',root,6)[0]
        if not any(struct.unpack_from('<I',root,320+i*56)[0]==2 for i in range(count)):continue
        h=hashlib.sha256(b'Glyph.Package.Set.v1\0'+struct.pack('<II',42,count))
        for i in range(count):
            e=root[320+i*56:376+i*56];key,rev=struct.unpack_from('<II',e)
            h.update(struct.pack('<IIII',key,rev,e[54],e[55]))
            h.update(hashlib.sha256(pack(current.game_mode_configs[e[54]-1])).digest())
            h.update(hashlib.sha256(pack(current.rgb_configs[e[55]-1]) if e[55] else b'').digest())
            h.update(hashlib.sha256(disk[record_path(key,rev)]).digest());h.update(hashlib.sha256(e).digest())
        aggregate=h.digest();root[264:296]=aggregate;root[4200:4232]=aggregate
        root[4072:4104]=hashlib.sha256(future).digest();root[4232:4264]=hashlib.sha256(future[:128]).digest()
        struct.pack_into('<I',root,4416,zlib.crc32(root[:4416]))
        if lead:
            header=bytearray(b[:16]);struct.pack_into('<I',header,12,zlib.crc32(header[:12])^zlib.crc32(root));disk[path]=bytes(header+root)
        else:disk[path]=bytes(root)
    future_seed=out/'future';future_seed.mkdir(exist_ok=True);dump_namespace(disk,future_seed/'files');invoke('seed',future_seed/'files',future_seed/'seed.nor');nor=future_seed/'seed.nor'
    execute(req(17,300,2,1,package_body=pack(body('Refuse',False))),'downgrade-refused',cfg.PROFILE_STORE_UNSUPPORTED)
    execute(req(17,400,1,1,package_body=pack(body('Upgrade'))),'legacy-upgrade')
    assert struct.unpack_from('<H',disk[record_path(1,2)],4)[0]==3
    for op,kw,label in [(18,{'replacement_name':'Renamed'},'rename'),(19,{'replacement_rank':9},'reorder')]:
        rev=1 if op==18 else 2
        before=disk[record_path(2,rev)][128:];execute(req(op,500+op,2,rev,**kw),label)
        assert disk[record_path(2,rev+1)][128:]==before
    counts['lifecycle']=6
    def rich_request(key,rev):
        root=max([disk[f'/ultimate-v2-{i}.bin'] for i in (0,1)],key=lambda b:struct.unpack_from('<I',b,8)[0])
        return cfg.ProfileStoreRequest(protocol_version=2,request_token=999,operation=cfg.PROFILE_STORE_READ,expected_store_generation=struct.unpack_from('<I',root,8)[0],profile_id=key,expected_profile_revision=rev,expected_config_generation=zlib.crc32(disk['/config-v2.bin'][8:]),expected_store_incarnation=42,include_authoring_metadata=True)
    def transport(items,label):
        work=out/label;work.mkdir(exist_ok=True);(work/'batch').write_bytes(batch(items));invoke('transport',nor,work/'batch',work)
        info=json.loads((work/'transport.json').read_text());assert info['unchanged'] and info['programs']==info['erases']==0 and info['no_handles']
        return frames((work/'responses.cobs').read_bytes())
    request=rich_request(2,3)
    response=cfg.ProfileStoreResponse.FromString(transport([pack(request)],'rich-read')[0][1])
    assert response.status==1 and response.authoring_state==2 and response.record_format==3 and response.authoring_metadata==installed_metadata
    assert response.record_sha256==hashlib.sha256(disk[record_path(2,3)]).digest()
    assert response.profile.SerializeToString()==disk[record_path(2,3)][128:128+struct.unpack_from('<I',disk[record_path(2,3)],20)[0]]
    stale=[]
    for field in ['expected_store_generation','expected_profile_revision','expected_store_incarnation','expected_config_generation']:
        v=cfg.ProfileStoreRequest.FromString(pack(request));setattr(v,field,getattr(v,field)+1);stale.append(pack(v))
    for command,b in transport(stale,'stale-read'):
        v=cfg.ProfileStoreResponse.FromString(b);assert command==9 and v.status==cfg.PROFILE_STORE_CONFLICT and not v.HasField('profile')
        assert not v.authoring_state and not v.authoring_metadata
    malformed=[pack(request)+b'\xc0\x01\x01',pack(request)[:-1]+b'\0',pack(request)[:-1]+b'\x81\0',pack(request)+b'\x08\x02']
    assert all(command!=9 for command,b in transport(malformed,'malformed-read'))
    ordinary=cfg.ProfileStoreRequest(protocol_version=2,request_token=1000,operation=cfg.PROFILE_STORE_READ,profile_id=2)
    v=cfg.ProfileStoreResponse.FromString(transport([pack(ordinary)],'ordinary-read')[0][1]);assert v.status==1 and not v.authoring_state
    saved_nor,saved_disk=nor,disk
    nor,disk=legacy_nor,legacy_disk
    response=cfg.ProfileStoreResponse.FromString(transport([pack(rich_request(1,1))],'legacy-rich-read')[0][1])
    assert response.status==1 and response.authoring_state==1 and response.record_format==2 and not response.authoring_metadata
    assert response.record_sha256==hashlib.sha256(disk[record_path(1,1)]).digest()
    nor,disk=saved_nor,saved_disk
    counts['rich_read']=11
    # The maximum actual native body is admitted under the same finite context.
    for i in range(3,21):
        execute(req(15,1000+i,package_body=pack(body('Max%02d'%i,maximum_native=True))),'capacity-%02d'%i)
        assert len(disk[record_path(i,1)])==3840
    # Two initial smaller records are upgraded to maximum too: twenty max rich.
    for key,rev in [(1,2),(2,3)]:
        execute(req(17,2000+key,key,rev,package_body=pack(body('Max%02d'%key,maximum_native=True))),'capacity-upgrade-%d'%key)
        assert len(disk[record_path(key,rev+1)])==3840
    assert sum(name.startswith('/ultpkg-') and len(b)==3840 for name,b in disk.items())>=20
    transport([pack(rich_request(1,3)),pack(rich_request(2,4))],'capacity-reopen')
    counts['maximum_profiles']=20
    before_survivors={name:b for name,b in disk.items() if name.startswith('/ultpkg-') and not name.startswith('/ultpkg-00000014-')}
    execute(req(20,3000,20,1),'delete-rich')
    assert not any(name.startswith('/ultpkg-00000014-') for name in disk)
    assert all(disk.get(name)==b for name,b in before_survivors.items())
    counts['lifecycle']+=1
    counts['unknown_version_copy_and_read']=3
    (out/'summary.json').write_text(json.dumps({'counts':counts,'all_pass':True},indent=2)+'\n')
    print(json.dumps(counts,sort_keys=True))

if __name__=='__main__':main()
