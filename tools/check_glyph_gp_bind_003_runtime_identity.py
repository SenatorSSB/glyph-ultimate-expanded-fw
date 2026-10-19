#!/usr/bin/env python3
"""Actual-source runtime identity, digest, viewer and dispatch proof; no device IO."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import ast
import copy

from check_glyph_stage_b_ultimate_profiles import ROOT, NANOPB, make_v2_artifact, make_v3_artifact
import glyph_runtime_identity_tool as identity

HOST = ROOT/'tools/fixtures/gp_bind_003_runtime_identity'
FLAGS = ['-O2', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']

def run(args):
    result = subprocess.run(list(map(str,args)), cwd=ROOT, text=True, capture_output=True, timeout=90,
                            env={**os.environ, 'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1', 'ASAN_OPTIONS':'detect_leaks=0'})
    if result.returncode:
        raise AssertionError(' '.join(map(str,args))+'\n'+result.stdout+result.stderr)
    return result.stdout

def decoder_tests():
    import struct
    frame = identity.MAGIC+struct.pack('<BBHQBBHIIIII',1,2,72,42,0,3,2,7,12,7,1,3)+bytes(range(32))
    viewer=b'0'*23+b'1\n'
    for split in range(len(frame)+1):
        decoder=identity.Decoder(42);decoder.feed(viewer+frame[:split]);decoder.feed(frame[split:]+viewer)
        assert decoder.finish()['active_id']==7 and decoder.viewer_records==2
    for length in range(72):
        try:
            decoder=identity.Decoder(42);decoder.feed(frame[:length]);decoder.finish()
        except ValueError:pass
        else:raise AssertionError('partial frame length accepted '+str(length))
    for bad in [frame[:71], frame+frame, viewer[1:]+frame, b'garbage'+frame,
                frame[:8]+bytes(8)+frame[16:],frame[:4]+b'\x02'+frame[5:]]:
        try:
            decoder=identity.Decoder(42);decoder.feed(bad);decoder.finish()
        except ValueError:
            pass
        else:
            raise AssertionError('ambiguous/partial/wrong token accepted')
    print('runtime_identity_host_split_ambiguous_timeout_token=PASS')

def configurator_cli_tests(temp):
    import struct
    response=identity.MAGIC+struct.pack('<BBHQBBHIIIII',1,2,72,42,2,8,0,0,0,0,0,0)+bytes(32)
    wire=identity.cobs_encode(bytes([identity.IDENTITY_COMMAND])+response)
    query=identity.wire_request(42,'configurator')
    assert identity.cobs_decode(query[:-1])==b'\x0a'+identity.request(42)
    assert identity.wire_request(42,'xinput')==identity.request(42)
    for split in range(len(wire)+1):
        decoder=identity.ConfiguratorDecoder(42);decoder.feed(wire[:split]);decoder.feed(wire[split:])
        assert decoder.finish()['status']=='configurator'
    corrupt_context=bytearray(response);corrupt_context[16]=4
    wrong_backend=bytearray(response);wrong_backend[17]=2
    wrong_row=bytearray(response);wrong_row[18]=1
    bad_frames=[wire[:-1],wire+wire,b'\0',b'\x02\0',bytes([255])*76+b'\0',
                identity.cobs_encode(b'\x04'+response),identity.cobs_encode(b'\x07'+response),
                identity.cobs_encode(b'\x09'+response),identity.cobs_encode(b'\x0a'+response[:-1]),
                identity.cobs_encode(b'\x0a'+corrupt_context),identity.cobs_encode(b'\x0a'+wrong_backend),
                identity.cobs_encode(b'\x0a'+wrong_row)]
    for bad in bad_frames:
        try:
            decoder=identity.ConfiguratorDecoder(42);decoder.feed(bad);decoder.finish()
        except ValueError:pass
        else:raise AssertionError('Configurator CLI accepted malformed/generic/wrong-context packet')
    capture=temp/'configurator-capture.bin';capture.write_bytes(wire)
    tool=ROOT/'tools/glyph_runtime_identity_tool.py'
    result=run([sys.executable,tool,'--context','configurator','--capture',capture,'--token','42','--session','host-fixture'])
    parsed=json.loads(result);assert parsed['status']=='configurator' and parsed['context']=='configurator' and parsed['active_id']==0
    for arguments in [ ['--context','write','--capture',capture,'--token','42','--session','x'],
                       ['--context','configurator','--capture',capture,'--token','43','--session','x'],
                       ['--context','configurator','--capture',capture,'--session','x'],
                       ['--context','configurator','--capture',capture,'--token','0','--session','x'],
                       ['--context','configurator','--capture',capture,'--token','42','--session','x','--command','7'] ]:
        result=subprocess.run([sys.executable,str(tool),*map(str,arguments)],cwd=ROOT,capture_output=True,text=True,timeout=10)
        assert result.returncode!=0,'CLI accepted invalid context/token or missing correlation'
    print('runtime_identity_configurator_cobs_cli_roundtrip_negatives=PASS')

def descriptor_checks(temp, nanopb, generated, objects, abi, profile):
    # Compile the exact production digest independently of mode/store access.
    inc=['-I',generated,'-I',nanopb,'-I',ROOT/'include']
    exe=temp/('digest-'+('short' if abi else 'default'))
    run(['c++','-std=c++17',*FLAGS,*abi,*inc,HOST/'digest.cpp',*objects[:4],'-o',exe])
    before=identity.payload_digest(profile)
    for field in ['schema_version','tables','roles','routing_slots','table_rules','output_program']:
        changed=type(profile)();changed.CopyFrom(profile);changed.ClearField(field)
        path=temp/(field+'.pb');path.write_bytes(changed.SerializeToString(deterministic=True))
        actual=run([exe,path]).strip()
        assert actual==identity.payload_digest(changed) and actual!=before, 'omitted field mutant escaped: '+field
    # Unknown raw fields differ in raw SHA but not decoded semantic identity.
    payload=profile.SerializeToString(deterministic=True)
    path=temp/'unknown-field.pb';path.write_bytes(payload+b'\x98\x06\x01')
    assert hashlib.sha256(path.read_bytes()).hexdigest()!=before
    assert run([exe,path]).strip()==before,'unknown raw field silently became semantic identity'
    print('runtime_identity_all_canonical_field_omissions_and_raw_hash_substitution=PASS')

def isolated_v4(temp,nanopb,abi):
    revision='b3d60feb48d637efa8612515d2351a470fe9df0e'
    isolated=temp/('isolated-v4-'+('short' if abi else 'default'));isolated.mkdir()
    paths=['schema/haybox/config.proto','schema/haybox/config.options','tools/check_glyph_stage_b_ultimate_profiles.py','tools/fixtures/stage_a_ultimate_profiles_dry_run.json','tools/fixtures/stage_b_ultimate_profiles_fixture.json','tools/fixtures/stage_c_ultimate_profiles_fixture.json']
    pins={}
    for relative in paths:
        data=subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)
        target=isolated/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);pins[relative]=hashlib.sha256(data).hexdigest()
    # Execute only the exact fixture constructors, against their exact source
    # inputs in disposable storage, never the failed test runner/product source.
    source=ast.parse((isolated/paths[2]).read_text())
    constructors=ast.Module(body=[node for node in source.body if isinstance(node,ast.FunctionDef) and node.name in ('make_v2_artifact','make_v3_artifact','make_v4_artifact')],type_ignores=[])
    namespace={'copy':copy,'json':json,'SPEC':isolated/paths[4],'STAGE_A':isolated/paths[3],'STAGE_C':isolated/paths[5]}
    exec(compile(constructors,'isolated-exact-v4-constructors','exec'),namespace)
    artifact=namespace['make_v4_artifact']()
    schema=isolated/'schema/haybox';generated=isolated/'generated';generated.mkdir()
    run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',generated,schema/'config.proto'])
    descriptor=isolated/'descriptor.pb'
    run([sys.executable,'-m','grpc_tools.protoc','-I',schema,'--descriptor_set_out='+str(descriptor),schema/'config.proto'])
    from google.protobuf import descriptor_pb2,descriptor_pool,message_factory,json_format
    file_set=descriptor_pb2.FileDescriptorSet.FromString(descriptor.read_bytes());pool=descriptor_pool.DescriptorPool()
    for item in file_set.file:pool.Add(item)
    cls=message_factory.GetMessageClass(pool.FindMessageTypeByName('UltimateProfile'))
    profile=cls();json_format.ParseDict(artifact['ultimateProfiles'][0],profile)
    assert profile.schema_version==4 and len(profile.function_bindings)==1
    objects=[];inc=['-I',generated,'-I',nanopb,'-I',ROOT/'include']
    for src in [nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',generated/'config.pb.c']:
        obj=isolated/(src.stem+'.o');run(['cc','-std=c11',*FLAGS,*abi,*inc,'-c',src,'-o',obj]);objects.append(obj)
    exe=isolated/'digest';run(['c++','-std=c++17',*FLAGS,*abi,*inc,HOST/'digest.cpp',*objects,'-o',exe])
    baseline=identity.payload_digest(profile)
    for field in [None,'schema_version','tables','roles','routing_slots','table_rules','output_program','function_bindings']:
        changed=cls();changed.CopyFrom(profile)
        if field:changed.ClearField(field)
        path=isolated/'payload.pb';path.write_bytes(changed.SerializeToString(deterministic=True));actual=run([exe,path]).strip()
        assert actual==identity.payload_digest(changed)
        if field:assert actual!=baseline,'isolated V4 omitted field mutant escaped: '+field
    print('runtime_identity_isolated_exact_failed_v4_descriptor_all_fields=PASS source='+revision+' pins='+json.dumps(pins,sort_keys=True))

def observer_mutants(temp,common,objects,engine_objects,fixture,expected_digest):
    observer=(ROOT/'include/core/RuntimeIdentity.hpp').read_text()
    digest=(ROOT/'include/core/RuntimeProfileDigest.hpp').read_text()
    mutants={
        'requested_id':('RuntimeIdentity.hpp',observer.replace('s.id = store.ActiveId();','s.id = s.requested;')),
        'stored_revision':('RuntimeIdentity.hpp',observer.replace('s.revision = store.ActiveRevision();','s.revision = store.EntryAt(0)->revision;')),
        'ignored_pointer':('RuntimeIdentity.hpp',observer.replace('profile != store.ActiveProfile()', 'false')),
        'stale_row':('RuntimeIdentity.hpp',observer.replace('if (!s.row || context->mode_id', 'if (!s.row) s.row = 1;\n    if (!s.row || context->mode_id')),
        'stored_readback':('RuntimeIdentity.hpp',observer.replace('if (!PayloadDigest(*profile, s.digest))','UltimateProfile stored = UltimateProfile_init_default; store.Read(store.ActiveId(), stored);\n    if (!PayloadDigest(stored, s.digest))')),
    }
    for field,statement in [('schema','profile.schema_version = 0;'),('table','profile.tables_count = 0;'),('role','profile.roles_count = 0;'),('routing','profile.routing_slots_count = 0;'),('rule','profile.table_rules_count = 0;'),('output','profile.has_output_program = false;')]:
        changed=digest.replace('const UltimateProfile &profile, uint8_t digest[32]) {','const UltimateProfile &source, uint8_t digest[32]) {\n    UltimateProfile profile = source; '+statement)
        mutants['omitted_'+field]=('RuntimeProfileDigest.hpp',changed)
    for name,(header,content) in mutants.items():
        assert content!=(observer if header=='RuntimeIdentity.hpp' else digest),'inactive mutant '+name
        shadow=temp/('mutant-'+name);(shadow/'core').mkdir(parents=True)
        (shadow/'core'/header).write_text(content)
        exe=temp/('mutant-bin-'+name)
        run(['c++','-std=c++17','-I',shadow,*common,HOST/'observer.cpp',*engine_objects,*objects,'-o',exe])
        result=subprocess.run([str(exe),str(fixture)],cwd=ROOT,capture_output=True,text=True,timeout=30,
                              env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1'})
        assert result.returncode!=0 or 'digest='+expected_digest not in result.stdout, 'actual observer mutant escaped: '+name
        assert not ('AddressSanitizer' in result.stderr or 'runtime error:' in result.stderr),'mutant rejected only by unrelated sanitizer '+name
    print('runtime_identity_actual_observer_identity_context_readback_payload_mutants=PASS count='+str(len(mutants)))

def main():
    decoder_tests()
    import glyph_serial_config_tool as writer
    pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    artifacts=[json.loads((ROOT/'tools/fixtures/stage_a_ultimate_profiles_dry_run.json').read_text()),make_v2_artifact(),make_v3_artifact()]
    nanopb=Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB',str(NANOPB)))
    with tempfile.TemporaryDirectory(prefix='gp-bind003-proof-') as directory:
        temp=Path(directory);generated=temp/'generated';generated.mkdir()
        configurator_cli_tests(temp)
        schema=ROOT/'schema/haybox'
        run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',generated,schema/'config.proto'])
        # Inert unrelated-mode declarations only; production Ultimate and all
        # headers it consumes remain real. Never copy failed source into repo.
        shadows=temp/'shadows';shadows.mkdir()
        for name in ['CustomControllerMode','CustomKeyboardMode','FgcMode','Melee20Button','ProjectM','RivalsOfAether','Rivals2','SenscopePrototype','64']:
            path=shadows/'modes'/f'{name}.hpp';path.parent.mkdir(exist_ok=True);path.write_text('#pragma once\n')
        path=shadows/'core/KeyboardMode.hpp';path.parent.mkdir(exist_ok=True)
        path.write_text('#pragma once\n#include "core/InputMode.hpp"\nclass KeyboardMode:public InputMode {public:void UpdateOutputs(const InputState &,OutputState &,CommunicationBackendId)override{}};\n')
        path=shadows/'prototypes/senscope/SenscopePrototypeBuildFlags.hpp';path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n')
        path=shadows/'stdlib.hpp';path.write_text('#pragma once\n#include <cstddef>\n#include <cstdint>\n#include <cstdlib>\nusing byte=uint8_t;\n')
        path=shadows/'serial.hpp';path.write_text('#pragma once\n#include "stdlib.hpp"\nnamespace serial {void init(unsigned long);void close();void print(const char*);void write(uint8_t);void write(uint8_t*,size_t);int available_for_write();}\n')
        sources=['src/modes/Ultimate.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/CommunicationBackend.cpp','src/core/socd.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp','src/comms/B0XXInputViewer.cpp']
        includes=[shadows,generated,nanopb,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'tools/fixtures/profile_store_migration_lifecycle_host/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',ROOT/'src',ROOT]
        for abi in ([],['-fshort-enums']):
            suffix='short' if abi else 'default';inc=[item for p in includes for item in ['-I',p]]
            common=[*FLAGS,*abi,'-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-missing-field-initializers','-Wno-non-c-typedef-for-linkage',*inc]
            objects=[]
            for src in [nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',generated/'config.pb.c']:
                obj=temp/(src.stem+suffix+'.o');run(['cc','-std=c11',*FLAGS,*abi,*inc,'-c',src,'-o',obj]);objects.append(obj)
            obj=temp/('store'+suffix+'.o');run(['c++','-std=c++17',*common,'-Dprofile_store=unused_production_profile_store','-c',ROOT/'HAL/pico/src/core/ProfileStore.cpp','-o',obj]);objects.append(obj)
            engine_objects=[]
            for index,src in enumerate([*[ROOT/s for s in sources],ROOT/'tools/fixtures/profile_store_migration_lifecycle_host/checked_storage_unavailable.cpp']):
                obj=temp/('engine-'+str(index)+suffix+'.o');run(['c++','-std=c++17',*common,'-c',src,'-o',obj]);engine_objects.append(obj)
            exe=temp/('observer'+suffix)
            run(['c++','-std=c++17',*common,HOST/'observer.cpp',*engine_objects,*objects,'-o',exe])
            for version,artifact in enumerate(artifacts,1):
                config,payload=writer.encode_artifact_payload(artifact,pb,jf);fixture=temp/f'v{version}.pb';fixture.write_bytes(payload)
                result=run([exe,fixture]);expected=identity.payload_digest(config.ultimate_profiles[0])
                assert 'digest='+expected in result, 'independent Python full-payload digest mismatch'
                print(f'abi={suffix} schema={version}\n'+result,end='')
            descriptor_checks(temp,nanopb,generated,objects,abi,config.ultimate_profiles[0])
            isolated_v4(temp,nanopb,abi)
            if not abi:observer_mutants(temp,common,objects,engine_objects,temp/'v3.pb',identity.payload_digest(config.ultimate_profiles[0]))
            # Configurator production dispatch uses its established stream and
            # storage fixture; no replacement dispatcher or identity model.
            legacy=ROOT/'tools/fixtures/profile_store_timeout_host';libs=ROOT/'.pio/libdeps/glyph_mk6'
            dispatch_inc=[legacy/'include',ROOT/'HAL/pico/include',ROOT/'include',generated,nanopb,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include']
            dc=[*FLAGS,*abi,'-DARDUINO=1','-Wall','-Wextra','-Werror','-Wno-error=inconsistent-missing-override','-Wno-error=missing-field-initializers','-Wno-unused-function',*[item for p in dispatch_inc for item in ['-I',p]]]
            dispatch_objects=objects
            dispatch_sources=['HAL/pico/src/comms/ConfiguratorBackend.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp']
            exe=temp/('dispatch'+suffix)
            run(['c++','-std=c++17',*dc,HOST/'configurator.cpp',*[ROOT/s for s in dispatch_sources],legacy/'checked_storage_unavailable.cpp',libs/'nanopb-arduino/src/pb_arduino.cpp',*dispatch_objects,'-o',exe])
            result=run([exe,temp/'v3.pb'])
            framed=next(line.removeprefix('configurator_frame=') for line in result.splitlines() if line.startswith('configurator_frame='))
            decoder=identity.ConfiguratorDecoder(42);decoder.feed(bytes.fromhex(framed))
            assert decoder.finish()['status']=='configurator','host rejected actual production Configurator COBS response'
            print(result,end='')
        print('descriptor_pins='+json.dumps({str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [schema/'config.proto',schema/'config.options',generated/'config.pb.h',generated/'config.pb.c',nanopb/'pb.h',nanopb/'pb_encode.c']},sort_keys=True))
    print('glyph_gp_bind_003_runtime_identity=PASS')
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except (AssertionError,OSError,subprocess.SubprocessError) as error:
        print(f'glyph_gp_bind_003_runtime_identity=FAIL: {error}',file=sys.stderr)
        raise SystemExit(1)
