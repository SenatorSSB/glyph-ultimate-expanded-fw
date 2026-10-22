#!/usr/bin/env python3
"""Production native codec/evaluator versus independent frozen legacy evidence."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile, struct, os
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT,NANOPB,run,require,make_v3_artifact
from convert_glyph_native_ultimate_profile import convert
HOST=ROOT/'tools/fixtures/profile_native_ultimate'


def compile_runner(temp,default=False,metrics=False):
    gen=temp/'generated';gen.mkdir();schema=ROOT/'schema/haybox'
    run([sys.executable,str(NANOPB/'generator/nanopb_generator.py'),'-I',str(schema),'-f',str(schema/'config.options'),'--error-on-unmatched','--no-timestamp','-D',str(gen),str(schema/'config.proto')])
    flags=['-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-non-c-typedef-for-linkage']+([] if default else ['-fshort-enums'])
    for inc in [ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/include',gen,NANOPB,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',ROOT/'src',HOST]:flags+=['-I',str(inc)]
    objects=[]
    if metrics:
        flags+=['-DGLYPH_NATIVE_TARGET_METRICS=1','-DGLYPH_NATIVE_METRICS_HOST=1','-I',str(ROOT/'tools/fixtures/native_target_metrics/include')]
        for relative in ['HAL/pico/src/core/NativeTargetMetrics.cpp','tools/fixtures/native_target_metrics/runner_clock.cpp']:
            obj=temp/(Path(relative).stem+'.o');run(['c++','-std=c++17',*flags,'-c',str(ROOT/relative),'-o',str(obj)]);objects.append(str(obj))
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


def host_admission_tests(pb,config):
    from convert_glyph_native_ultimate_profile import validate_profile_wire,validate_standalone_profile,validate_native_body
    import glyph_serial_config_tool as writer
    source=config.ultimate_profiles[0];context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    mixed=pb.UltimateProfile();mixed.CopyFrom(source);mixed.native_payload=b'invalid-native-in-legacy'
    try:convert(mixed,context,pb,'historical_compatibility')
    except ValueError:pass
    else:raise AssertionError('mixed legacy/native converter source accepted')
    invalid=pb.Config();invalid.ultimate_profiles.add().CopyFrom(mixed)
    require(writer.verify_ultimate_profiles(invalid,pb),'host embedded profile validator rejects mixed source')
    for suffix in (b'\x42\x00',b'\x42\x01x'):
        for raw in (source.SerializeToString()+suffix,suffix+source.SerializeToString()):
            try:validate_profile_wire(raw)
            except ValueError:pass
            else:raise AssertionError('raw empty/nonempty tag8 presence lost in legacy source')
    native,report=convert(source,context,pb,'historical_compatibility')
    require(validate_standalone_profile(native,pb)['engine_abi']==1,'host names native engine only with valid body header')
    require(len(report['correspondence_report']['families'])==18 and len(report['correspondence_report']['effects'])==12,'profile-specific complete18family/12effect correspondence')
    require(len(report['correspondence_report']['table_mapping'])==28 and len(report['correspondence_report']['legacy_role_mapping'])==len(source.roles),'literal tables/explicit sparse role mapping report')
    for offset,value in ((4,2),(6,2),(10,97),(19,8),(94,1)):
        body=bytearray(native.native_payload);body[offset]=value
        try:validate_native_body(bytes(body))
        except ValueError:pass
        else:raise AssertionError('host native body mutation accepted')
    print('PASS host converter mixed/empty native presence refusal; finite body admission; concrete18family/role/table/rule/effect report')


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
            options={'physical_input':38}
            if selected_policy=='clean_down_a':options.update(down_input=5,up_input=2)
            else:options.update(table_id=3,table_priority=5,forced_x=79,forced_y=81)
            native,metadata=convert(legacy,context,pb,selected_policy,options=options)
            if selected_policy=='forced_table_down_a':
                require(native.native_payload[96+3*18:96+4*18]==bytes([79,81])*9,
                        'forced coordinates are all nine ordinary target-table points, with no extra force effect')
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
    # Forced-table modifier with completely empty preprocessing and a physical
    # carrier unrelated to any cardinal source: it adds no hidden Down signal.
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    options={'physical_input':49,'table_id':3,'table_priority':5,'forced_x':79,'forced_y':81}
    physical=1<<48
    native,_=convert(legacy,context,pb,'forced_table_down_a',options=options)
    rows=sequence(native,[physical,physical|1,physical|(1<<2)])
    require(rows[0][0]&0x3c0000==0 and rows[0][1:3]==[79,81], 'forced-table neutral modifier adds no cardinal direction')
    require(rows[1][0]&(1<<19) and not rows[1][0]&(1<<21), 'forced-table preserves incoming Right digital direction')
    options['table_priority']=254
    native,_=convert(legacy,context,pb,'forced_table_down_a',options=options)
    row=sequence(native,[physical|(1<<23)])[0]
    require(row[0]&1 and row[0]&0x3c0000==0 and row[1:3]!=[79,81], 'losing forced modifier adds neither coordinates nor implicit Down')
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


def complete_profile(native,pb,variant,carriers=(49,50,51)):
    # Keep every converted source family and add original-domain A+post-SOCD
    # Down, an ordinary forced table, and one-input A+L+R to each body.
    clean,forced,digital=carriers
    require(len(set(carriers))==3 and all(1<=x<=60 for x in carriers),"explicit distinct complete profile carriers")
    body=native.native_payload;header=bytearray(body[:96]);count,early,sources,rules,bindings,effects=header[10:16]
    tokens=struct.unpack_from('<H',header,92)[0];offset=600
    conditions=bytearray(body[offset:offset+count*3]);offset+=count*3
    pool=bytearray(body[offset:offset+tokens*2]);offset+=tokens*2
    direction_sources=bytearray(body[offset:offset+sources*9]);offset+=sources*9
    rule_data=bytearray(body[offset:offset+rules*4]);offset+=rules*4
    binding_data=bytearray(body[offset:offset+bindings*6]);offset+=bindings*6
    effect_data=body[offset:offset+effects*32];offset+=effects*32;mask=body[offset:]
    old_down=struct.unpack_from('<H',direction_sources,5)[0]
    conditions+=struct.pack('<BH',count+1,2<<2);pool+=struct.pack('<HH',old_down,0x2000+clean)
    struct.pack_into('<H',direction_sources,5,0x3000+count+1)
    rule_data+=struct.pack('<BBH',3,19,forced)
    binding_data+=struct.pack('<HHBB',clean,1,255,0)+struct.pack('<HHBB',forced,1,255,0)+struct.pack('<HHBB',digital,193,255,0)
    tables=bytearray(body[96:600]);tables[19*18:20*18]=bytes([77+variant,83+variant])*9
    header[10]=count+1;header[11]=early+1;header[13]=rules+1;header[14]=bindings+3
    struct.pack_into('<H',header,92,tokens+2)
    derivation=b'Glyph.Native.Complete20.v1\0'+bytes([variant])+body
    if carriers!=(49,50,51):derivation+=b'Glyph.Native.PacketCarriers.v1\0'+bytes(carriers)
    header[60:92]=hashlib.sha256(derivation).digest()
    result=header+tables+conditions+pool+direction_sources+rule_data+binding_data+effect_data+mask
    struct.pack_into('<H',result,8,len(result))
    from convert_glyph_native_ultimate_profile import validate_native_body
    validate_native_body(bytes(result))
    return pb.UltimateProfile(schema_version=5,native_payload=bytes(result))


def store_tests(temp,flags,objects,pb,config):
    from check_glyph_profile_store_littlefs_host import FRAMEWORK
    directory=temp/'twenty-native';directory.mkdir()
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    context.socd_pairs.add(button_dir1=49,button_dir2=2,socd_type=1)
    context_file=directory/'context.pb';context_file.write_bytes(context.SerializeToString())
    digests=set();manifest=[]
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
        native=complete_profile(native,pb,i)
        wire=native.SerializeToString();digests.add(hashlib.sha256(wire).hexdigest());(directory/(str(i)+'.pb')).write_bytes(wire)
        manifest.append({'id':i,'wrapper_bytes':len(wire),'body_bytes':len(native.native_payload),'record_bytes':len(wire)+32,'file_charge_4096':4096,'sha256':hashlib.sha256(wire).hexdigest(),'all28tables':True,'all_source_families':True,'clean_original49_post49Down':True,'forced50_table19_all9points':[77+i,83+i],'original51_A_L_R_mask':193})
    require(len(digests)==20,'twenty independently varied complete native payloads')
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    library=FRAMEWORK/'libraries/LittleFS'
    current_flags=[*flags,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-DLFS_NAME_MAX=32','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-I',str(library/'lib/littlefs')]
    lfs=[]
    for source in [library/'src/lfs.c',library/'src/lfs_util.c']:
        obj=temp/(source.stem+'.o');run(['cc','-std=c11',*current_flags,'-c',str(source),'-o',str(obj)]);lfs.append(str(obj))
    probe=temp/'mounted-native.cpp'
    probe.write_text('#include '+json.dumps(str(ROOT/'HAL/pico/src/core/ProfileStore.cpp'))+'\n'+'bool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n){MountedStorage s;return s.ReadRange(p,o,b,n); }\n'+'CheckedStorage::Result GlyphMountedWriteProbe(const char *p,const uint8_t *b,size_t n){static MountedStorage owners[2];static unsigned next=0;const unsigned current=(next++)%2;const auto other=owners[1-current].LastFailure();const auto result=owners[current].CheckedWrite(p,b,n,CheckedStorage::Kind::Record);if(owners[1-current].LastFailure()!=other)std::abort();return result; }\n'+'bool GlyphMountedWriteStateClean(){return !mounted_write_inputs.owner&&!mounted_write_inputs.path&&!mounted_write_inputs.bytes&&!mounted_write_inputs.length&&mounted_write_inputs.kind==Kind{}&&!mounted_write_file.opened; }\n')
    sources=['src/core/profile_selection.cpp','HAL/pico/src/core/CheckedStorage.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/modes/Ultimate.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/CommunicationBackend.cpp','src/core/socd.cpp']
    exe=temp/'native-store'
    run(['c++','-std=c++17',*current_flags,str(HOST/'native_store.cpp'),str(probe),*[str(ROOT/s) for s in sources],*objects,*lfs,'-o',str(exe)])
    legacy=temp/'store-legacy.pb';legacy.write_bytes(config.SerializeToString())
    print(run([str(exe),str(directory),str(legacy),str(context_file)]),end='')
    print('twenty_native_profile_manifest='+json.dumps(manifest,sort_keys=True))


def full_frozen_replay(temp,flags,objects,pb,config):
    directory=temp/'full-frozen-native';directory.mkdir()
    fallback=pb.UltimateProfile();fallback.CopyFrom(config.ultimate_profiles[0]);fallback.schema_version=1
    for field in ('roles','routing_slots','table_rules','default_table_id','output_program'):fallback.ClearField(field)
    (directory/'fallback-legacy.pb').write_bytes(fallback.SerializeToString())
    host=ROOT/'tools/fixtures/stage_c_ultimate_profiles_host'
    source=(host/'pipeline.cpp').read_text()
    source=source.replace('#define Ultimate LegacyUltimate\n#include "modes/Ultimate.hpp"',
        '#define Ultimate LegacyUltimate\n#include "'+str(HOST/'frozen/modes/Ultimate.hpp')+'"')
    source=source.replace('#undef Ultimate\n','#undef Ultimate\n#include "'+str(HOST/'native_legacy_adapter.hpp')+'"\n#define Ultimate NativeActual\n',1)
    pipeline=temp/'full-native-pipeline.cpp';pipeline.write_text(source)
    sources=['src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp']
    exe=temp/'full-native-pipeline'
    run(['c++','-std=c++17',*flags,str(pipeline),*[str(ROOT/s) for s in sources],str(temp/'legacy.o'),*objects,'-o',str(exe)])
    fixture=temp/'full-source.pb';fixture.write_bytes(config.SerializeToString())
    capture=subprocess.run([str(exe),str(fixture)],env={**os.environ,'GLYPH_NATIVE_REPLAY_DIR':str(directory),'GLYPH_NATIVE_CAPTURE':'1'},capture_output=True,text=True)
    require(capture.returncode==0,'frozen vector/profile capture failed: '+capture.stdout+capture.stderr)
    profiles=list(directory.glob('*.legacy.pb'))
    for file in profiles:
        p=pb.UltimateProfile();p.ParseFromString(file.read_bytes());context=pb.GameModeConfig();context.ParseFromString(file.with_name(file.name.replace('.legacy.pb','.context.pb')).read_bytes())
        native,_=convert(p,context,pb,'historical_compatibility')
        file.with_name(file.name.replace('.legacy.pb','.native.pb')).write_bytes(native.SerializeToString())
    result=subprocess.run([str(exe),str(fixture)],env={**os.environ,'GLYPH_NATIVE_REPLAY_DIR':str(directory)},capture_output=True,text=True)
    require(result.returncode==0,'exact frozen full native replay failed: '+result.stdout+result.stderr)
    require('comparisons=1222420' in result.stdout,'full frozen input/assertion count changed')
    print(f'PASS exact frozen Stage-C1,222,420 native full-output replays; converted profile/context snapshots={len(profiles)}; all original reorder/A-B-A/effect assertions retained')
    print('source-owned absent-reference vectors use explicit converted baseline as native test control; production fallback separately unchanged')


def custom_hook_tests(temp,flags,objects):
    flags=[*flags,'-Wno-unused-parameter']
    # Authenticate untouched actual consumers against adopted A; keep historical
    # C010/C011/C012/C014 campaign/selector debt raw in their stock reports.
    for relative in ['src/modes/CustomControllerMode.cpp','include/modes/CustomControllerMode.hpp','src/core/InputMode.cpp','src/core/socd.cpp','include/core/state.hpp','HAL/pico/include/util/state_util.hpp']:
        baseline=subprocess.check_output(['git','show','753932c8fbec3e002d455f4cd2b9b1dbc0ed896f:'+relative],cwd=ROOT)
        require((ROOT/relative).read_bytes()==baseline,'unrelated actual consumer changed: '+relative)
    old_controller=temp/'legacy-controller.o';old_custom=temp/'legacy-custom.o'
    run(['c++','-std=c++17','-DControllerMode=LegacyControllerMode','-I',str(HOST/'frozen_custom'),*flags,'-c',str(HOST/'frozen/legacy_controller.cpp'),'-o',str(old_controller)])
    run(['c++','-std=c++17','-DControllerMode=LegacyControllerMode','-DCustomControllerMode=LegacyCustomControllerMode','-I',str(HOST/'frozen_custom'),*flags,'-c',str(ROOT/'src/modes/CustomControllerMode.cpp'),'-o',str(old_custom)])
    exe=temp/'current-custom-hook';sources=['src/modes/CustomControllerMode.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','src/core/config_button_validation.cpp']
    run(['c++','-std=c++17',*flags,str(HOST/'current_custom_hook.cpp'),*[str(ROOT/s) for s in sources],str(old_controller),str(old_custom),*objects,'-o',str(exe)])
    print(run([str(exe)]),end='')




def current_caller_tests(temp):
    import check_glyph_gp_config012_button_mask_characterization as buttons
    sub=temp/'current-button-callers';sub.mkdir()
    binary=buttons.compile_variant(sub,'current-callers',[],current_generated=temp/'generated',current_nanopb=NANOPB)
    output,_=buttons.validate_decoder(binary)
    for raw in range(1,61):
        for caller in ('mode_activation','backend_activation','custom_modifier','custom_combo'):
            result=buttons.run(binary,'caller',caller,str(raw))
            require(result.returncode==0,'current actual button caller '+caller+'/'+str(raw)+': '+result.stdout+result.stderr)
    print('PASS HOST_COMPONENT_ONLY current button decoder/original assertions; all60IDs×4actual source callers; frozen harness uses scratch3arg/defaultboot0+chord symbol adapter')
    host=ROOT/'tools/fixtures/profile_store_selection_recovery_host'
    compat=temp/'current-mode-interface/core';compat.mkdir(parents=True)
    double=(host/'include/core/ProfileStore.hpp').read_text()
    (compat/'ProfileStore.hpp').write_text(double.replace('  unsigned activations=','  const void *ActiveNativeView() const { return nullptr; }\n  unsigned activations='))
    includes=[compat.parent,host/'include',temp/'generated',NANOPB,ROOT/'tools/fixtures/mode_selection_host/include',ROOT/'include']
    exe=temp/'current-mode-capacity'
    run(['c++','-std=c++17','-fshort-enums','-Wall','-Wextra','-Werror','-Wno-missing-field-initializers','-Wno-unneeded-internal-declaration','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DMODE_SELECTION_SOURCE="'+str(ROOT/'src/core/mode_selection.cpp')+'"',*sum((['-I',str(p)] for p in includes),[]),str(HOST/'current_mode_capacity.cpp'),'-o',str(exe)])
    print(run([str(exe)]),end='')


def mutation_controls(temp,flags,objects,pb):
    # Independent data fixture: first serialized rule has priority20/table4,
    # later rule has priority10/table3. Raw carrier49 sets A independently.
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    context.socd_pairs.add(button_dir1=49,button_dir2=2,socd_type=1)
    native=program(pb,context,[(49,1,255,0)],carrier=51,table=4)
    body=bytearray(native.native_payload)
    # One existing early condition/token grows into two; sources/rules/bindings
    # move as whole immutable sections, then table4's rule is followed by3.
    body[10]=body[11]=2;body[13]=2
    body[600:605]=struct.pack('<BH',1,1)+struct.pack('<BH',2,1)+struct.pack('<HH',0x2033,0x2034)
    body[628:632]=struct.pack('<BBH',20,4,0x3002)+struct.pack('<BBH',10,3,0x3001)
    struct.pack_into('<H',body,8,len(body));struct.pack_into('<H',body,92,2)
    native.native_payload=bytes(body);wire=temp/'mutation.pb';wire.write_bytes(native.SerializeToString())
    source_paths=['src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp']
    sources={p:(ROOT/p).read_text() for p in source_paths}
    controller='src/core/ControllerMode.cpp';socd='    HandleSocd(post_inputs);'
    require(sources[controller].count(socd)==1,'one exact production SOCD callsite')
    sources[controller]=sources[controller].replace(socd,'    ++native_socd_visits;'+socd)+'\n'
    sources[controller]='extern unsigned native_socd_visits;\n'+sources[controller]
    tests=[('control',None,None,None,None),
      ('intrinsic_slot_leak','src/modes/UltimateNativeEvaluator.cpp','o.buttons=(o.buttons&0xf0030000u)|f.buttons;','o.buttons=(o.buttons&0xf0030000u)|f.buttons; if(c.original.buttons&2) o.a=true;','old intrinsic carrier2'),
      ('enum_bit_alias','src/modes/UltimateNativeEvaluator.cpp','case 0: return (c.original.buttons & (uint64_t{1}<<(id-1)))!=0;','case 0: return (c.original.buttons & (uint64_t{1}<<(id%32)))!=0;','original-domain binding'),
      ('cancelled_down_gates_a','src/modes/UltimateNativeEvaluator.cpp','case 0: return (c.original.buttons & (uint64_t{1}<<(id-1)))!=0;','case 0: return (c.post.buttons & (uint64_t{1}<<(id-1)))!=0;','original A survives post-SOCD cancellation'),
      ('double_socd',controller,'++native_socd_visits;    HandleSocd(post_inputs);','++native_socd_visits; HandleSocd(post_inputs); ++native_socd_visits; HandleSocd(post_inputs);','exactly one SOCD'),
      ('array_order_priority','src/modes/UltimateNativeEvaluator.cpp','if(p[0]<f.table_priority && Value(Read16(p+2),c,f))','if(f.table_priority==255 && Value(Read16(p+2),c,f))','unique table priority'),
      ('losing_table_influence','src/modes/UltimateNativeEvaluator.cpp','if(p[0]<f.table_priority && Value(Read16(p+2),c,f))','if(p[0]<f.table_priority)','losing or inactive table'),
      ('copied_owner','src/modes/UltimateNativeProfile.cpp','&v.owner->view == &v && ','','copied view cannot'),
      ('stale_generation','src/modes/Ultimate.cpp','_native->generation != _native_generation || ','','latched active generation')]
    base_objects=[]
    for i,p in enumerate(source_paths):
        path=temp/f'mutation-base-{i}.cpp';path.write_text(sources[p]);obj=temp/f'mutation-base-{i}.o'
        run(['c++','-std=c++17',*flags,'-c',str(path),'-o',str(obj)]);base_objects.append(str(obj))
    for label,p,old,new,assertion in tests:
        selected=list(base_objects)
        if p:
            require(sources[p].count(old)==1,'unambiguous mutation: '+label)
            path=temp/(label+'.cpp');path.write_text(sources[p].replace(old,new));obj=temp/(label+'.o')
            run(['c++','-std=c++17',*flags,'-c',str(path),'-o',str(obj)]);selected[source_paths.index(p)]=str(obj)
        exe=temp/('mutation-'+label)
        run(['c++','-std=c++17',*flags,str(HOST/'native_mutations.cpp'),*selected,*objects,'-o',str(exe)])
        result=subprocess.run([str(exe),str(wire)],capture_output=True,text=True)
        if p:require(result.returncode!=0 and assertion in result.stderr,'mutant must fail named assertion '+label+': '+result.stdout+result.stderr)
        else:require(result.returncode==0,'mutation control itself failed: '+result.stdout+result.stderr)
        print(f'PASS source mutation {label}: '+(assertion or result.stdout.strip()))


    # Independent canonical wire/hash assertions exercise callback poisoning,
    # encoded length, request identity and explicit embedded-native refusal.
    profile_source=(ROOT/'src/modes/UltimateNativeProfile.cpp').read_text()
    ordinary=temp/'codec-ordinary.body'
    import glyph_serial_config_tool as writer
    config,_=writer.encode_artifact_payload(make_v3_artifact(),pb,writer.load_runtime_proto_modules(ROOT)[1])
    native,_=convert(config.ultimate_profiles[0],pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE),pb,'historical_compatibility');ordinary.write_bytes(native.native_payload)
    codec_tests=[('codec_control',None,None,None),
       ('incoming_callback_alias','std::memcmp(bytes, lease->bytes + offset, n)','((void)offset,false)','incoming callback alias poisoning'),
       ('encode_size_mismatch','pb_encode_string(stream, lease->bytes, lease->size)','pb_encode_string(stream, lease->bytes, lease->size-1)','callback encode size/bytes'),
       ('embedded_skipped','p.native_payload.funcs.decode=RejectPayload;p.native_payload.arg=nullptr;','p.native_payload.funcs.decode=nullptr;p.native_payload.arg=nullptr;','actual Config decoder rejects native callback')]
    for label,old,new,assertion in codec_tests:
        text=profile_source
        if old:require(text.count(old)==1,'unique callback mutation '+label);text=text.replace(old,new)
        path=temp/(label+'.cpp');path.write_text(text);exe=temp/label
        run(['c++','-std=c++17',*flags,str(HOST/'native_negative.cpp'),str(path),*objects,'-o',str(exe)])
        result=subprocess.run([str(exe),str(ordinary),str(ROOT/'docs/runtime_config/profile_native_ultimate/design_evidence/maximum-native.body')],capture_output=True,text=True)
        if old:require(result.returncode!=0 and assertion in result.stderr,'callback mutant must fail '+label+': '+result.stdout+result.stderr)
        else:require(result.returncode==0,'callback controls failed: '+result.stdout+result.stderr)
        print('PASS source mutation '+label+': '+(assertion or result.stdout.strip()))
    override=temp/'request-identity-mutation/core';override.mkdir(parents=True)
    original=(ROOT/'include/core/ProfileStoreRequestIdentity.hpp').read_text()
    (override/'ProfileStoreRequestIdentity.hpp').write_text(original.replace('request.request_token = 0;','request.request_token = 0; request.has_profile = false;'))
    exe=temp/'omitted-request-payload'
    run(['c++','-std=c++17','-I',str(override.parent),*flags,str(HOST/'native_negative.cpp'),str(ROOT/'src/modes/UltimateNativeProfile.cpp'),*objects,'-o',str(exe)])
    result=subprocess.run([str(exe),str(ordinary),str(ROOT/'docs/runtime_config/profile_native_ultimate/design_evidence/maximum-native.body')],capture_output=True,text=True)
    require(result.returncode!=0 and 'request identity matches independent full native wire' in result.stderr,'omitted request payload mutant fails named identity assertion: '+result.stdout+result.stderr)
    print('PASS source mutation omitted_request_payload: independent full native wire request identity')


def dispatch_tests(temp,pb,config,default=False):
    import check_glyph_profile_store_timeout_resynchronization as transport
    gen=temp/'generated';host=ROOT/'tools/fixtures/profile_store_timeout_host';libs=ROOT/'.pio/libdeps/glyph_mk6'
    flags=['-O2','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-DARDUINO=1','-Wall','-Wextra','-Werror','-Wno-error=missing-field-initializers','-Wno-error=inconsistent-missing-override','-Wno-unused-function']
    if not default:flags+=['-fshort-enums']
    for inc in [host/'include',ROOT/'HAL/pico/include',ROOT/'include',gen,NANOPB,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include']:flags+=['-I',str(inc)]
    objects=[]
    for source in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c']:
        obj=temp/('dispatch-'+source.stem+'.o');run(['cc','-std=c11',*flags,'-c',str(source),'-o',str(obj)]);objects.append(str(obj))
    store=temp/'dispatch-store.o';run(['c++','-std=c++17',*flags,'-Dprofile_store=unused_dispatch_store','-c',str(ROOT/'HAL/pico/src/core/ProfileStore.cpp'),'-o',str(store)]);objects.append(str(store))
    sources=['HAL/pico/src/comms/ConfiguratorBackend.cpp','src/modes/UltimateNativeProfile.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp']
    exe=temp/'native-dispatch';run(['c++','-std=c++17',*flags,str(HOST/'native_dispatch.cpp'),*[str(ROOT/s) for s in sources],str(host/'checked_storage_unavailable.cpp'),str(libs/'nanopb-arduino/src/pb_arduino.cpp'),*objects,'-o',str(exe)])
    legacy=temp/'dispatch-legacy.pb';legacy.write_bytes(config.SerializeToString())
    native,_=convert(config.ultimate_profiles[0],pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE),pb,'historical_compatibility');ordinary=temp/'dispatch-native.pb';ordinary.write_bytes(native.SerializeToString())
    maximum=temp/'dispatch-maximum.pb';maximum.write_bytes(pb.UltimateProfile(schema_version=5,native_payload=(ROOT/'docs/runtime_config/profile_native_ultimate/design_evidence/maximum-native.body').read_bytes()).SerializeToString())
    print(run([str(exe),str(legacy),str(ordinary),str(maximum)]),end='')
    backend_source=(ROOT/sources[0]).read_text()
    anchor='    static pb_ostream_t output; output = pb_ostream_from_buffer(frame, sizeof(frame));'
    require(backend_source.count(anchor)==1,'exact native response encode boundary')
    for label,injection,assertion in [
        ('overwritten_response_lease','if(response.has_profile && response.profile.schema_version==5) std::memset(const_cast<uint8_t *>(ultimate_native::Lease(response.profile)->bytes),0xcc,ultimate_native::Lease(response.profile)->size);','READ independent record lease survives shared response frame reuse'),
        ('released_response_lease','if(response.has_profile && response.profile.schema_version==5) const_cast<ultimate_native::PayloadLease *>(ultimate_native::Lease(response.profile))->Release();','COBS delimiter')]:
        mutant=temp/(label+'.cpp');mutant.write_text(backend_source.replace(anchor,'    '+injection+'\n'+anchor));mutant_exe=temp/label
        run(['c++','-std=c++17',*flags,str(HOST/'native_dispatch.cpp'),str(mutant),*[str(ROOT/s) for s in sources[1:]],str(host/'checked_storage_unavailable.cpp'),str(libs/'nanopb-arduino/src/pb_arduino.cpp'),*objects,'-o',str(mutant_exe)])
        result=subprocess.run([str(mutant_exe),str(legacy),str(ordinary),str(maximum)],capture_output=True,text=True)
        require(result.returncode!=0 and assertion in result.stderr,'response lease mutant must fail named assertion '+label+': '+result.stdout+result.stderr)
        print('PASS source mutation '+label+': '+assertion)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--default-enum',action='store_true');parser.add_argument('--metrics-enabled',action='store_true');a=parser.parse_args()
    import glyph_serial_config_tool as writer
    pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    with tempfile.TemporaryDirectory(prefix='native-ultimate-') as directory:
        temp=Path(directory);exe,negative,flags,objects=compile_runner(temp,a.default_enum,a.metrics_enabled)
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
        host_admission_tests(pb,config)
        composition_tests(temp,exe,pb,config.ultimate_profiles[0])
        store_tests(temp,flags,objects,pb,config)
        full_frozen_replay(temp,flags,objects,pb,config)
        custom_hook_tests(temp,flags,objects)
        dispatch_tests(temp,pb,config,a.default_enum)
        mutation_controls(temp,flags,objects,pb)
        current_caller_tests(temp)
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
