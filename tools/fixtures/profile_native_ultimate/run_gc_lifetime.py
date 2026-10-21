#!/usr/bin/env python3
"""Actual pinned LittleFS GC invariants; host-only, no serial/device operations."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from check_glyph_stage_b_ultimate_profiles import NANOPB,make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
import glyph_serial_config_tool as writer

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True,type=Path);parser.add_argument('--store-source',type=Path,default=ROOT/'HAL/pico/src/core/ProfileStore.cpp');args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    def run(argv):
        p=subprocess.run(list(map(str,argv)),cwd=ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
        if p.returncode:raise RuntimeError(' '.join(map(str,argv))+'\n'+p.stdout+p.stderr)
        return p.stdout+p.stderr
    gen=out/'generated';gen.mkdir(exist_ok=True);schema=ROOT/'schema/haybox'
    run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',gen,schema/'config.proto'])
    pb,jf,_=writer.load_runtime_proto_modules(ROOT);_,payload=writer.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=out/'legacy.pb';fixture.write_bytes(payload)
    library=FRAMEWORK/'libraries/LittleFS';includes=[gen,NANOPB,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',library/'lib/littlefs'];inc=[x for p in includes for x in ['-I',p]]
    flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-fshort-enums','-DLFS_NAME_MAX=32'];objects=[]
    for src in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',library/'src/lfs.c',library/'src/lfs_util.c']:
        obj=out/(src.stem+'.o');run(['cc','-std=c11',*flags,*inc,'-c',src,'-o',obj]);objects.append(obj)
    probe=out/'mounted-gc.cpp';probe.write_text('#include '+json.dumps(str(args.store_source.resolve()))+'\nbool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n){MountedStorage s;return s.ReadRange(p,o,b,n);}\n')
    harness=ROOT/'tools/fixtures/profile_native_ultimate/native_gc_lifetime.cpp';sources=[harness,probe,ROOT/'HAL/pico/src/core/CheckedStorage.cpp',ROOT/'src/modes/UltimateNativeProfile.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp'];exe=out/'gc-lifetime'
    run(['c++','-std=c++17',*flags,'-Wall','-Wextra','-Werror','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1',*inc,*sources,*objects,'-o',exe]);output=run([exe,fixture]);(out/'run.log').write_text(output);print(output,end='')
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.store_source,harness,Path(__file__),ROOT/'include/core/ProfileStore.hpp',ROOT/'HAL/pico/src/core/CheckedStorage.cpp',library/'lib/littlefs/lfs.c',library/'lib/littlefs/lfs.h']}
    (out/'report.json').write_text(json.dumps({'state':'PASS_HOST_REAL_NOR_LITTLEFS_GC_INVARIANTS','source_sha256':pins,'broader_namespace':'unrelated/matching-name/nested directories retained','positive_orphan_PENDING_MOVE':'NOT_RUN_HERE_separate_exact_witness_required','target_stack_timing':'NOT_MEASURED','output_sha256':hashlib.sha256(output.encode()).hexdigest()},indent=2)+'\n')
if __name__=='__main__':
    try:main()
    except (AssertionError,OSError,RuntimeError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);raise SystemExit(1)
