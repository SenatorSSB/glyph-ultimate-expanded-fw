#!/usr/bin/env python3
"""Compile exact native ARM ABI and finite stack-layout probes; no device access."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True);a=parser.parse_args()
    out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
    nanopb=ROOT/'.pio/libdeps/glyph_mk6/Nanopb';toolchain=ROOT/'.platformio-home/packages/toolchain-rp2040-earlephilhower/bin'
    compiler=toolchain/'arm-none-eabi-g++';nm=toolchain/'arm-none-eabi-nm'
    commands=[]
    def run(command):
        commands.append([str(x) for x in command]);result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
        (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        return result.stdout
    gen=out/'generated';gen.mkdir(exist_ok=True);schema=ROOT/'schema/haybox'
    run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',gen,schema/'config.proto'])
    source=out/'layout.cpp';source.write_text('''#include "modes/UltimateNativeEvaluator.hpp"
#include "core/ProfileStore.hpp"
#define SIZE(name,type) char name[sizeof(type)]
SIZE(native_view_bytes,ultimate_native::PreparedView);
SIZE(native_owned_bytes,ultimate_native::OwnedProgram);
SIZE(native_candidate_bytes,ultimate_native::CandidateWorkspace);
char native_active_plus_candidate_bytes[sizeof(ultimate_native::OwnedProgram)+sizeof(ultimate_native::CandidateWorkspace)];
SIZE(native_frame_bytes,ultimate_native::FrameState);
SIZE(context_bytes,ResolvedInputContext);
char preprocessing_copy_bytes[2*sizeof(InputState)];
SIZE(profile_store_bytes,ProfileStore);
SIZE(config_bytes,Config);SIZE(mode_bytes,GameModeConfig);SIZE(profile_bytes,UltimateProfile);
SIZE(request_bytes,ProfileStoreRequest);SIZE(response_bytes,ProfileStoreResponse);
static_assert(sizeof(ultimate_native::PreparedView)<=560,"view cap");
static_assert(sizeof(ultimate_native::OwnedProgram)+sizeof(ultimate_native::CandidateWorkspace)<=7800,"active+candidate cap");
static_assert(sizeof(ultimate_native::FrameState)<=144,"frame cap");
''')
    common=['-std=c++17','-mcpu=cortex-m0plus','-mthumb','-Os','-fno-exceptions','-fno-rtti','-fstack-usage']
    for inc in [ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/include',gen,nanopb,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'src']:common+=['-I',str(inc)]
    report={'status':'PASS_ABI_LAYOUT','abis':{},'target_timing':'NOT_MEASURED','target_whole_stack':'NOT_MEASURED','core0_stack_reservation_bytes':2048,'core1_stack_reservation_bytes':2048,'limits_changed':False}
    for abi,flag in [('short','-fshort-enums'),('no-short','-fno-short-enums')]:
        target=out/(abi+'-layout.o');run([compiler,*common,flag,'-c',source,'-o',target]);raw=run([nm,'-S',target]);(out/(abi+'-nm.txt')).write_text(raw)
        sizes={line.split()[-1]:int(line.split()[1],16) for line in raw.splitlines() if len(line.split())==4 and line.split()[2]=='B'}
        report['abis'][abi]=sizes
        for relative in ['src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/modes/Ultimate.cpp','src/core/ControllerMode.cpp']:
            target=out/(abi+'-'+Path(relative).stem+'.o');run([compiler,*common,flag,'-c',ROOT/relative,'-o',target])
    report['source_hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/modes/Ultimate.cpp','src/core/ControllerMode.cpp','include/modes/UltimateNativeProfile.hpp','include/modes/UltimateNativeEvaluator.hpp','schema/haybox/config.proto','schema/haybox/config.options']}
    report['descriptor_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in gen.iterdir() if p.is_file()}
    report['operation_bounds']={'conditions':96,'condition_token_visits':768,'sources':8,'rules':32,'digital_bindings':32,'effects':16,'preprocessing':'existing remap once and ordered SOCD once'}
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
