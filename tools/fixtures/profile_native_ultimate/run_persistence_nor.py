#!/usr/bin/env python3
"""Compare exact production Persistence operation/fault traces on pinned NOR/LFS."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from check_glyph_stage_b_ultimate_profiles import NANOPB
from check_glyph_profile_store_littlefs_host import FRAMEWORK

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True,type=Path);parser.add_argument('--source',type=Path,default=ROOT/'HAL/pico/src/core/Persistence.cpp');parser.add_argument('--default-enum',action='store_true');parser.add_argument('--fixture',type=Path,default=ROOT/'tools/fixtures/profile_native_ultimate/persistence_nor_lifetimes.cpp');args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    commands=[]
    def run(argv):
        argv=list(map(str,argv));commands.append(argv);p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=180,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
        (out/'last.log').write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError(' '.join(argv)+'\n'+p.stdout+p.stderr)
        return p.stdout+p.stderr
    gen=out/'generated';gen.mkdir(exist_ok=True);schema=ROOT/'schema/haybox';run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',gen,schema/'config.proto'])
    host=ROOT/'tools/fixtures/profile_store_config_persistence_host';deps=ROOT/'tools/fixtures/gp_config021_persisted_recovery/dependencies';library=FRAMEWORK/'libraries/LittleFS';includes=[host/'include',ROOT/'tools/fixtures/gp_config021_persisted_recovery/include',gen,NANOPB,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',library/'lib/littlefs',deps];inc=[x for p in includes for x in ['-I',p]]
    flags=['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-DLFS_NAME_MAX=32']+([] if args.default_enum else ['-fshort-enums']);objects=[]
    for src in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',library/'src/lfs.c',library/'src/lfs_util.c']:
        obj=out/(src.stem+'.o');run(['cc','-std=c11',*flags,*inc,'-c',src,'-o',obj]);objects.append(obj)
    probe=out/'mounted-store.cpp';probe.write_text('#include '+json.dumps(str(ROOT/'HAL/pico/src/core/ProfileStore.cpp'))+'\nbool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n){MountedStorage s;return s.ReadRange(p,o,b,n); }\n')
    fixture=args.fixture;sources=[fixture,args.source,probe,ROOT/'HAL/pico/src/core/CheckedStorage.cpp',deps/'pb_arduino.cpp',deps/'CRC32.cpp',ROOT/'src/modes/UltimateNativeProfile.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp'];exe=out/'persistence-nor'
    run(['c++','-std=c++17',*flags,'-Wall','-Wextra','-Werror','-Wno-error=missing-field-initializers','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1',*inc,*sources,*objects,'-o',exe]);output=run([exe]);(out/'run.log').write_text(output);(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    (out/'report.json').write_text(json.dumps({'state':'PASS_HOST_ACTUAL_PRODUCTION_NOR_LITTLEFS','default_enum':args.default_enum,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+[Path(__file__),ROOT/'tools/fixtures/profile_native_ultimate/persistence_nor_lifetimes.cpp',library/'lib/littlefs/lfs.c']},'trace_sha256':hashlib.sha256(output.encode()).hexdigest(),'target_stack_timing':'NOT_MEASURED'},indent=2)+'\n');print(output.splitlines()[-1])
if __name__=='__main__':
    try:main()
    except (AssertionError,OSError,RuntimeError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);raise SystemExit(1)
