#!/usr/bin/env python3
"""Finite retained diagnostic protocol/actual-source/ARM layout checks, offline."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile
import glyph_native_target_metrics_tool as host

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tools/fixtures/native_target_metrics'

def run(args,**kwargs):
    result=subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,text=True,**kwargs)
    if result.returncode:raise AssertionError('command failed: '+shlex.join(map(str,args))+'\n'+result.stdout+result.stderr)
    return result.stdout+result.stderr

def require(value,message):
    if not value:raise AssertionError(message)

def rejected(call):
    try:call()
    except (ValueError,AssertionError,RuntimeError):return True
    return False

def check(out):
    exe=out/'metrics-host';capture=out/'complete.bin'
    flags=['-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DGLYPH_NATIVE_TARGET_METRICS=1','-DGLYPH_NATIVE_METRICS_HOST=1','-I',FIX/'include','-I',ROOT/'include','-I',ROOT]
    run(['c++',*flags,FIX/'metrics_host.cpp','-o',exe]);print(run([exe,capture]),end='')
    frame=capture.read_bytes();source=bytes(range(1,21)).hex();decoded=host.decode(frame,42,source)
    require(decoded['status']=='complete' and decoded['statistics']['native_frame']['max_us']==20,'actual complete snapshot decoded')
    viewer=b'01'*12+b'\n';identity=bytearray(72);identity[:8]=b'\xa5GRI'+struct.pack('<BBH',1,2,72);struct.pack_into('<QBBHIIIII',identity,8,0x4d4e47d7,0,2,0,1,1,17,3,5);identity[40:]=b'x'*32
    stream=viewer+bytes(identity)+frame+viewer
    for width in (1,3,7,25,72,160,1024):
        decoder=host.Decoder(42,source)
        for i in range(0,len(stream),width):decoder.feed(stream[i:i+width])
        result=decoder.finish();require(result['viewer_records']==2 and len(result['identity_observations'])==1,'opaque framed records preserve viewer/identity')
    for offset,value in ((4,2),(5,2),(6,159),(16,3),(17,8),(19,128),(122,1),(138,1),(153,1),(155,128)):
        bad=bytearray(frame);bad[offset]=value;require(rejected(lambda:host.decode(bytes(bad),42,source)),'host rejects header/reserved/unknown flags '+str(offset))
    require(rejected(lambda:host.decode(frame,43,source)),'token mismatch')
    require(rejected(lambda:host.decode(frame,42,'0'*40)),'candidate source mismatch')
    require(rejected(lambda:host.Decoder(42).feed(frame+frame)),'duplicate frame')
    partial=host.Decoder(42);partial.feed(frame[:-1]);require(rejected(partial.finish),'partial response')
    # Preserve the entire original identity parser/wire apart from its sole accessor.
    prior=run(['git','show','9e16e1c36babdd5c655893b35ae92cd39725c37f:include/core/RuntimeIdentityWire.hpp'])
    current=(ROOT/'include/core/RuntimeIdentityWire.hpp').read_text().replace('    bool HasPartialFrame() const { return _used != 0; }\n','')
    require(current==prior,'identity parser/wire exact historical bytes apart from accessor')
    spec=importlib.util.spec_from_file_location('native_builder',ROOT/'builder_scripts/native_target_metrics.py');builder=importlib.util.module_from_spec(spec);previous_bytecode=sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode=True;spec.loader.exec_module(builder)
    finally:sys.dont_write_bytecode=previous_bytecode
    class Result:
        returncode=0
        def __init__(self,text):self.stdout=text
    # No hidden status work is bypassed: fake a root without the integrity helper
    # only for early dirty/malformed rejection (before helper import).
    require(rejected(lambda:builder.source_identity(ROOT,lambda args,**k:Result('dirty' if 'status' in args else 'a'*40))),'dirty build rejected')
    require(rejected(lambda:builder.source_identity(ROOT,lambda *a,**k:Result('bad'))),'short source label rejected')
    production=(ROOT/'HAL/pico/src/core/NativeTargetMetrics.cpp').read_text()
    require('time_us_64(' not in production and 'while (' not in production and 'while(' not in production,'bounded clock/service source')
    # Independent failures are driven through actual implementation mutations.
    implementation=(ROOT/'HAL/pico/src/core/NativeTargetMetrics.cpp').read_text()
    harness=(FIX/'metrics_host.cpp').read_text()
    for name,old,new in [
        ('unbounded_scan_chunk','i<16&&s.cursor<s.top','i<17&&s.cursor<s.top'),
        ('odd_mailbox_accepted','!first||(first&1)||first!=last','!first||first!=last'),
        ('incoherent_timer_accepted','!coherent||uptime>=3600000000ull','uptime>=3600000000ull')]:
        require(implementation.count(old)==1,'unique metric mutant '+name)
        mutant=out/(name+'.cpp');mutant.write_text(implementation.replace(old,new))
        caller=out/(name+'-host.cpp');caller.write_text(harness.replace('"HAL/pico/src/core/NativeTargetMetrics.cpp"',json.dumps(str(mutant))))
        program=out/name;run(['c++',*flags,caller,'-o',program])
        result=subprocess.run([str(program)],cwd=ROOT,capture_output=True,text=True,timeout=30)
        (out/(name+'.log')).write_text(result.stdout+result.stderr)
        require(result.returncode!=0,'metric negative control escaped '+name)
        print('PASS metric source mutation '+name)
    # Compile the pinned production CDC and FIFO unchanged; only endpoints and
    # IRQ arrival scheduling are host doubles. This exercises the target-only
    # guarded Service path rather than the generic Wire used above.
    framework=ROOT/'.platformio-home/packages/framework-arduinopico'
    usb=framework/'libraries/Adafruit_TinyUSB_Arduino/src'
    cdc=out/'observer-cdc.c'
    cdc.write_text((usb/'class/cdc/cdc_device.c').read_text()+'\n'+(ROOT/'tools/fixtures/profile_store_cdc_rx_progress/cdc_fixture_tail.c').read_text()+'\nunsigned fixture_tx_pending(void) { return tu_fifo_count(&_cdcd_itf[0].tx_ff); }\n')
    cdc_includes=['-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-I',FIX/'include','-I',ROOT/'tools/fixtures/profile_store_cdc_rx_progress/include','-I',usb,'-I',usb/'class/cdc','-I',ROOT/'include','-I',ROOT]
    cdc_objects=[]
    for source in [cdc,usb/'common/tusb_fifo.c']:
        obj=out/(source.stem+'.o');run(['cc','-std=c11','-fsanitize=address,undefined','-fno-omit-frame-pointer',*cdc_includes,'-c',source,'-o',obj]);cdc_objects.append(obj)
    observer=out/'cdc-observer'
    run(['c++','-std=c++17','-DGLYPH_NATIVE_TARGET_METRICS=1','-DGLYPH_NATIVE_METRICS_HOST=1','-DGLYPH_CDC_COORDINATION_TEST=1','-fsanitize=address,undefined','-fno-omit-frame-pointer',*cdc_includes,FIX/'cdc_observer.cpp',*cdc_objects,'-o',observer])
    print(run([observer]),end='')
    for source,fragments in [(framework/'cores/rp2040/main.cpp',['loop();\n            __loop();','extern void __loop() {\n#ifdef USE_TINYUSB\n    yield();']), (framework/'cores/rp2040/delay.cpp',['TinyUSB_Device_Task();\n        TinyUSB_Device_FlushCDC();'])]:
        require(all(fragment in source.read_text() for fragment in fragments),'existing post-loop deferred USB task progress')
    # Actual production recipe and target ABI; emitted objects are analysis only,
    # with a fixed test source constant, never a candidate firmware artifact.
    db=json.loads((ROOT/'docs/runtime_config/profile_native_ultimate/native_production_stack_final/compile_commands.json').read_text())
    entry=next(e for e in db if e['file'].endswith('/ProfileStore.cpp'));recipe=shlex.split(entry['command'])
    source_header=out/'native_target_source.hpp';analysis_sha=run(['git','rev-parse','HEAD']).strip();values=','.join('0x'+analysis_sha[i:i+2] for i in range(0,40,2))
    source_header.write_text('#pragma once\n#include <cstdint>\nconstexpr uint8_t kNativeTargetSourceSha[20]={'+values+'};\nconstexpr uint16_t kNativeTargetSourceFlags=3;\n')
    objects=[]
    for relative in ['HAL/pico/src/core/NativeTargetMetrics.cpp','HAL/pico/src/core/NativeTargetMetricsEntry.S','src/core/ControllerMode.cpp']:
        obj=out/(Path(relative).name+'.o');args=recipe.copy();args[args.index('-o')+1]=str(obj);args[args.index(entry['file'])]=relative
        args[1:1]=['-DGLYPH_NATIVE_TARGET_METRICS=1','-I',str(out)];args+=['-fstack-usage'];run(args);objects.append(obj)
    compiler=Path(recipe[0]);objdump=compiler.with_name('arm-none-eabi-objdump');nm=compiler.with_name('arm-none-eabi-nm')
    disassembly=run([objdump,'-drC',*objects]);(out/'target-objects.disassembly.txt').write_text(disassembly)
    symbols=run([nm,'-S',*objects]);(out/'target-objects.symbols.txt').write_text(symbols)
    require('__atomic_' not in symbols and '__sync_' not in symbols and '__cxa_guard' not in symbols,'no atomic helper/guard construction')
    require('dmb' in disassembly,'actual seq-cst mailbox load/store barriers emitted')
    require('PRIMASK' in disassembly or 'primask' in disassembly,'entry restores saved IRQ state')
    assembly=run([objdump,'-drC',objects[1]])
    require('push' not in assembly and '\tbl\t' not in assembly,'entry adapters stackless and no calls')
    require('__real_main' in assembly and '__real_multicore_launch_core1' in assembly and 'main1' in assembly,'exact external entry relocations')
    mutable=0
    for line in symbols.splitlines():
        parts=line.split()
        if len(parts)>=4 and parts[2] in ('b','B','d','D'):mutable+=int(parts[1],16)
    require(mutable==420,'actual ARM mutable static layout408 plus emitted frame words12')
    const=20 # Account source constant conservatively even if linker places it in RAM.
    require(mutable+const<=512,'diagnostic static subcap')
    result={'state':'OFFLINE_COMPONENT_AND_ARM_OBJECT_PROOF_ONLY','mutable_static_bytes':mutable,'source_constant_bytes_charged':const,'diagnostic_static_subcap':512,'wrapper_declared_static_words_bytes':16,'wrapper_emitted_static_words_bytes':12,'conservative_all_new_static_charge_bytes':444,'analysis_source_label_head':analysis_sha,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['HAL/pico/src/core/NativeTargetMetrics.cpp','HAL/pico/src/core/NativeTargetMetricsEntry.S','include/core/RuntimeIdentityService.hpp','include/core/RuntimeIdentityWire.hpp']},
            'objects_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},
            'whole_stack_and_final_link_interception':'PENDING exact committed ELF/source review','target_observations':'NOT_MEASURED'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('glyph_native_target_metrics: PASS offline components/ARM layout; final ELF/stack/hardware incomplete')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
    try:
        if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);check(args.output_dir)
        else:
            with tempfile.TemporaryDirectory(prefix='glyph-native-metrics-') as d:check(Path(d))
        return 0
    except Exception as error:print('glyph_native_target_metrics: FAIL: '+str(error));return 1
if __name__=='__main__':raise SystemExit(main())
