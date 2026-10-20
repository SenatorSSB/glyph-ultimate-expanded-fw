#!/usr/bin/env python3
"""Production native codec/evaluator versus independent frozen legacy evidence."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile, struct
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT,NANOPB,run,require,make_v3_artifact
from convert_glyph_native_ultimate_profile import convert
HOST=ROOT/'tools/fixtures/profile_native_ultimate'


def compile_runner(temp,default=False):
    gen=temp/'generated';gen.mkdir();schema=ROOT/'schema/haybox'
    run([sys.executable,str(NANOPB/'generator/nanopb_generator.py'),'-I',str(schema),'-f',str(schema/'config.options'),'--error-on-unmatched','--no-timestamp','-D',str(gen),str(schema/'config.proto')])
    flags=['-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-non-c-typedef-for-linkage']+([] if default else ['-fshort-enums'])
    for inc in [ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/include',gen,NANOPB,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',ROOT/'src',HOST]:flags+=['-I',str(inc)]
    objects=[]
    for source in [NANOPB/'pb_common.c',NANOPB/'pb_encode.c',NANOPB/'pb_decode.c',gen/'config.pb.c']:
        obj=temp/(source.stem+'.o');run(['cc','-std=c11',*flags,'-c',str(source),'-o',str(obj)]);objects.append(str(obj))
    oracle=temp/'legacy.o';run(['c++','-std=c++17','-DUltimate=LegacyUltimate','-I',str(HOST/'frozen'),'-I',str(ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/frozen'),*flags,'-c',str(ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/legacy_ultimate.cpp'),'-o',str(oracle)])
    sources=['src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','src/core/config_button_validation.cpp']
    exe=temp/'native-runner';run(['c++','-std=c++17',*flags,str(HOST/'native_runner.cpp'),*[str(ROOT/s) for s in sources],str(oracle),*objects,'-o',str(exe)])
    negative=temp/'native-negative'
    run(['c++','-std=c++17',*flags,str(HOST/'native_negative.cpp'),str(ROOT/'src/modes/UltimateNativeProfile.cpp'),*objects,'-o',str(negative)])
    return exe,negative,flags,objects


def program(pb,context,bindings,*,carrier=None,table=0):
    from convert_glyph_native_ultimate_profile import preprocessing_bytes
    tables=bytearray()
    for t in range(28):
        for y in range(3):
            for x in range(3):tables+=bytes([28+100*x if t==0 else 10+t,28+100*y if t==0 else 40+t])
    conditions=b'';tokens=b'';rules=b''
    if carrier is not None:
        conditions=struct.pack('<BH',1,1);tokens=struct.pack('<H',0x2000+carrier);rules=struct.pack('<BBH',1,table,0x3001)
    sources=struct.pack('<BHHHH',1,0x2003,0x2001,0x2005,0x2002)+struct.pack('<BHHHH',2,0,0,0,0)
    effects=b''
    for target in (1,3,4):
        data=bytes([140]+[0]*17) if target in (3,4) else bytes(18)
        effects+=struct.pack('<BBHHBBBB18sBBH',target,200,0xffff if target==1 else 0x5000+(7 if target==3 else 8),0xffff,1 if target==1 else 0,1 if target==1 else 0,0,0,data,255,0,0)
    header=bytearray(96);header[:4]=b'GNP5';struct.pack_into('<HH',header,4,1,1)
    header[10:20]=bytes([int(carrier is not None),int(carrier is not None),2,int(carrier is not None),len(bindings),3,0,1,2,0])
    struct.pack_into('<HHHH',header,20,0,0xffff,0xffff,0)
    header[28:60]=hashlib.sha256(preprocessing_bytes(context,pb)).digest()
    struct.pack_into('<H',header,92,int(carrier is not None))
    body=header+tables+conditions+tokens+sources+rules+b''.join(struct.pack('<HHBB',*b) for b in bindings)+effects+struct.pack('<HHHH',0xffff,0,0,0)
    struct.pack_into('<H',body,8,len(body))
    return pb.UltimateProfile(schema_version=5,native_payload=bytes(body))


def composition_tests(temp,exe,pb,legacy):
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    context.button_remapping.add(physical_button=38,activates=5)
    pair=context.socd_pairs.add(button_dir1=5,button_dir2=2,socd_type=1)
    context_file=temp/'context.pb';frames=temp/'frames.txt';wire=temp/'composition.pb'
    def sequence(native,values):
        context_file.write_bytes(context.SerializeToString());wire.write_bytes(native.SerializeToString())
        frames.write_text(''.join(format(v,'x')+'\n' for v in values))
        return [[int(x,16) if i==0 else int(x) for i,x in enumerate(row.split())] for row in run([str(exe),str(wire),'sequence',str(context_file),str(frames)]).splitlines()]
    native=program(pb,context,[(38,1|64|128,255,0),(0x1005,4,255,0),(0x2005,2,255,0),(49,1,255,0)])
    down=1<<37;up=1<<1
    rows=sequence(native,[0,down,down|up,up,0,1<<48])
    require(rows[1][0]&0xfff==199 and rows[1][-2:]==[140,140], 'independent one-input A+L+R and pre/post bindings')
    require(rows[2][0]&0xfff==197 and rows[2][1:3]==[128,128], 'original/pre survive SOCD-cancelled Down; post is false')
    require(rows[-1][0]&0xfff==1,'multiple independent inputs OR same A')
    for policy in range(6):
        pair.socd_type=policy
        for selected_policy in ('clean_down_a','forced_table_down_a'):
            options={'physical_input':38,'down_input':5,'up_input':2}
            if selected_policy=='forced_table_down_a':options.update(table_id=3,table_priority=5,effect_priority=70,forced_x=79,forced_y=81)
            native,metadata=convert(legacy,context,pb,selected_policy,options=options)
            values=[0,down,down|up,up,0,up,down|up,down,0]
            rows=sequence(native,values)
            for value,row in zip(values,rows):
                require(bool(row[0]&1)==bool(value&down),f'{selected_policy} policy{policy}: A independent of cleaned direction/history')
                if selected_policy=='forced_table_down_a' and value&down:require(row[1:3]==[79,81], 'winning forced table applies exact explicit raw values')
    # Mode fallback priority250 defeats explicit254; independent A remains,
    # and the same payload can request an explicit winner-filtered A instead.
    pair.socd_type=1
    options.update(table_priority=254)
    losing=down|(1<<23)
    native,_=convert(legacy,context,pb,'forced_table_down_a',options=options)
    row=sequence(native,[losing])[0];require(row[1:3]!=[79,81] and row[0]&1,'losing forced table has no coordinate influence; A independent')
    options['a_winner_table']=3
    native,_=convert(legacy,context,pb,'forced_table_down_a',options=options)
    row=sequence(native,[losing])[0];require(not row[0]&1,'explicit A winner filter is honored')
    # Generic native table/condition/binding tokens have no intrinsic carrier
    # identity. Rebind each of18 family witnesses to every60 legal input IDs.
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    for family in range(18):
        for control in range(1,61):
            native=program(pb,context,[(0x2000+control,1,255,0)],carrier=control,table=family+1)
            wire.write_bytes(native.SerializeToString())
            got=run([str(exe),str(wire),format(1<<(control-1),'x')]).split()
            require(int(got[0],16)&1 and list(map(int,got[1:3]))==[11+family,41+family], 'rebound family input selects its own table/digital data')
            old=37 if control!=37 else 36
            got=run([str(exe),str(wire),format(1<<(old-1),'x')]).split()
            require(not int(got[0],16)&1,'old family carrier is inert')
    print('PASS original/pre/post composition;6SOCD policies/history; clean/forced table winner/loser/filter;18family witnesses×60carrier rebindings')


def store_tests(temp,flags,objects,pb,config):
    from check_glyph_profile_store_littlefs_host import FRAMEWORK
    directory=temp/'twenty-native';directory.mkdir()
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    digests=set()
    for i in range(1,21):
        source=pb.UltimateProfile();source.CopyFrom(config.ultimate_profiles[0])
        for table in source.tables:
            for point in table.coordinates:point.x=(point.x+i)%256;point.y=(point.y+3*i)%256
        # Each independently complete body retains all28 tables, all source
        # families and its own concrete conditions/bindings/effect program.
        old=source.routing_slots[0].input_token;replacement=(i%16)+1
        for slot in source.routing_slots[1:]:
            if slot.input_token==replacement:slot.input_token=old
        source.routing_slots[0].input_token=replacement
        native,metadata=convert(source,context,pb,'historical_compatibility')
        digests.add(metadata['body_sha256']);(directory/(str(i)+'.pb')).write_bytes(native.SerializeToString())
    require(len(digests)==20,'twenty independently varied complete native payloads')
    library=FRAMEWORK/'libraries/LittleFS'
    current_flags=[*flags,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-DLFS_NAME_MAX=32','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-I',str(library/'lib/littlefs')]
    lfs=[]
    for source in [library/'src/lfs.c',library/'src/lfs_util.c']:
        obj=temp/(source.stem+'.o');run(['cc','-std=c11',*current_flags,'-c',str(source),'-o',str(obj)]);lfs.append(str(obj))
    probe=temp/'mounted-native.cpp'
    probe.write_text('#include '+json.dumps(str(ROOT/'HAL/pico/src/core/ProfileStore.cpp'))+'\n'+'bool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n){MountedStorage s;return s.ReadRange(p,o,b,n); }\n')
    sources=['HAL/pico/src/core/CheckedStorage.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/modes/Ultimate.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp']
    exe=temp/'native-store'
    run(['c++','-std=c++17',*current_flags,str(HOST/'native_store.cpp'),str(probe),*[str(ROOT/s) for s in sources],*objects,*lfs,'-o',str(exe)])
    legacy=temp/'store-legacy.pb';legacy.write_bytes(config.SerializeToString())
    print(run([str(exe),str(directory),str(legacy)]),end='')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--default-enum',action='store_true');a=parser.parse_args()
    import glyph_serial_config_tool as writer
    pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    with tempfile.TemporaryDirectory(prefix='native-ultimate-') as directory:
        temp=Path(directory);exe,negative,flags,objects=compile_runner(temp,a.default_enum)
        rows=[json.loads(x) for x in (HOST/'independent_legacy/short-expected.jsonl').read_text().splitlines()]
        for row in rows:
            config=pb.Config();config.ParseFromString((HOST/'independent_legacy/corpus'/(row['id']+'.pb')).read_bytes())
            native,metadata=convert(config.ultimate_profiles[0],context,pb,'historical_compatibility')
            wire=temp/(row['id']+'.pb');wire.write_bytes(native.SerializeToString(deterministic=True))
            result=run([str(exe),str(wire),row['input']]).split()
            require(result==[row['buttons'],*map(str,row['axes'])],f"independent native mismatch {row['id']}: {result} expected {row}")
        print(f'PASS independent legacy/native full-output corpus={len(rows)}')
        config,_=writer.encode_artifact_payload(make_v3_artifact(),pb,jf)
        native,_=convert(config.ultimate_profiles[0],context,pb,'historical_compatibility')
        ordinary=temp/'ordinary.body';ordinary.write_bytes(native.native_payload)
        print(run([str(negative),str(ordinary),str(ROOT/'docs/runtime_config/profile_native_ultimate/design_evidence/maximum-native.body')]),end='')
        composition_tests(temp,exe,pb,config.ultimate_profiles[0])
        store_tests(temp,flags,objects,pb,config)
        for version in (1,2,3):
            sample=pb.Config();sample.CopyFrom(config)
            p=sample.ultimate_profiles[0];p.schema_version=version
            if version<3:p.ClearField('output_program')
            if version==1:
                for field in ('roles','routing_slots','table_rules','default_table_id'):p.ClearField(field)
            native,_=convert(p,context,pb,'historical_compatibility')
            wire=temp/('ordinary'+str(version)+'.pb');wire.write_bytes(native.SerializeToString());legacy=temp/'legacy.pb';legacy.write_bytes(sample.SerializeToString())
            print(f'v{version}: '+run([str(exe),str(wire),'matrix',str(legacy)]),end='')
    return 0
if __name__=='__main__':raise SystemExit(main())
