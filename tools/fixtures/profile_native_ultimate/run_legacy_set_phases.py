#!/usr/bin/env python3
"""Actual legacy SET handler differential; host-only named Persistence boundary."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from check_glyph_stage_b_ultimate_profiles import NANOPB,make_v3_artifact
import glyph_serial_config_tool as writer

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True,type=Path);parser.add_argument('--default-enum',action='store_true');parser.add_argument('--backend-source',type=Path,default=ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp');args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True);commands=[]
    def run(a):
        a=list(map(str,a));commands.append(a);p=subprocess.run(a,cwd=ROOT,text=True,capture_output=True,timeout=120,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'});(out/'last.log').write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError(' '.join(a)+'\n'+p.stdout+p.stderr)
        return p.stdout+p.stderr
    gen=out/'generated';gen.mkdir(exist_ok=True);schema=ROOT/'schema/haybox';run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',gen,schema/'config.proto'])
    pb,jf,_=writer.load_runtime_proto_modules(ROOT);_,payload=writer.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=out/'legacy.pb';fixture.write_bytes(payload)
    host=ROOT/'tools/fixtures/profile_store_timeout_host';libs=ROOT/'.pio/libdeps/glyph_mk6';includes=[host/'include',ROOT/'HAL/pico/include',ROOT/'include',gen,NANOPB,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include'];inc=[x for p in includes for x in ['-I',p]]
    flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']+([] if args.default_enum else ['-fshort-enums']);objects=[];sources=[]
    for src in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c']:
        obj=out/(src.stem+'.o');run(['cc','-std=c11',*flags,*inc,'-c',src,'-o',obj]);objects.append(obj)
    for name,src,extra in [('store',ROOT/'HAL/pico/src/core/ProfileStore.cpp',['-Dprofile_store=production_profile_store']),('checked',host/'checked_storage_unavailable.cpp',[]),('native',ROOT/'src/modes/UltimateNativeProfile.cpp',[]),('validation',ROOT/'src/core/config_validation.cpp',[]),('buttons',ROOT/'src/core/config_button_validation.cpp',[]),('usb',ROOT/'src/core/config_usb_default_validation.cpp',[]),('rgb',ROOT/'src/core/config_rgb_target_validation.cpp',[]),('glyph',ROOT/'config/glyph/common/src/glyph_config_validation.cpp',[]),('pb_arduino',libs/'nanopb-arduino/src/pb_arduino.cpp',[]),('backend',args.backend_source,[])]:
        sources.append(src);obj=out/(name+'.o');run(['c++','-std=c++17','-DARDUINO=1',*flags,'-Wall','-Wextra','-Werror','-Wno-error=missing-field-initializers','-Wno-error=inconsistent-missing-override',*extra,*inc,'-c',src,'-o',obj]);objects.append(obj)
    harness=ROOT/'tools/fixtures/profile_native_ultimate/legacy_set_phases.cpp';exe=out/'legacy-set';run(['c++','-std=c++17','-DARDUINO=1',*flags,'-Wall','-Wextra','-Werror','-Wno-error=inconsistent-missing-override','-Wno-error=unused-function',*inc,harness,*objects,'-o',exe]);output=''.join(run([exe,fixture,str(i)]) for i in range(17));(out/'run.log').write_text(output);(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+[harness,Path(__file__),host/'include/core/Persistence.hpp',host/'timeout_harness.cpp']};(out/'report.json').write_text(json.dumps({'state':'PASS_ACTUAL_LEGACY_SET_HANDLER_AT_FUNCTIONAL_PERSISTENCE_BOUNDARY','default_enum':args.default_enum,'source_sha256':pins,'output_sha256':hashlib.sha256(output.encode()).hexdigest(),'actual_nor':'SEPARATE_PRODUCTION_PERSISTENCE_DIFFERENTIAL','hardware':'NOT_TESTED'},indent=2)+'\n');print(output,end='')
if __name__=='__main__':
    try:main()
    except (AssertionError,OSError,RuntimeError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);raise SystemExit(1)
