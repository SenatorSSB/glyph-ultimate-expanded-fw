#!/usr/bin/env python3
"""Actual production decoder/import NOR differential against an explicit frozen source root."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from check_glyph_stage_b_ultimate_profiles import NANOPB,make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
import glyph_serial_config_tool as writer

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--source-root',type=Path,default=ROOT);ap.add_argument('--default-enum',action='store_true');ap.add_argument('--fixture',type=Path,default=ROOT/'tools/fixtures/profile_native_ultimate/decoder_import_nor.cpp');args=ap.parse_args();root=args.source_root.resolve();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);commands=[]
    def run(argv):
        argv=list(map(str,argv));commands.append(argv);p=subprocess.run(argv,cwd=root,capture_output=True,text=True,timeout=300,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'});(out/'last.log').write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError(' '.join(argv)+'\nfull output: '+str(out/'last.log')+'\n'+p.stderr[-1800:])
        return p.stdout+p.stderr
    gen=out/'generated';gen.mkdir(exist_ok=True);schema=root/'schema/haybox';run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',gen,schema/'config.proto'])
    pb,jf,_=writer.load_runtime_proto_modules(ROOT);_,payload=writer.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=out/'legacy.pb';fixture.write_bytes(payload)
    host=root/'tools/fixtures/profile_store_config_persistence_host';deps=root/'tools/fixtures/gp_config021_persisted_recovery/dependencies';library=FRAMEWORK/'libraries/LittleFS';includes=[host/'include',root/'tools/fixtures/gp_config021_persisted_recovery/include',gen,NANOPB,root/'include',root/'HAL/pico/include',root/'config/glyph/common/include',root/'config/glyph/glyph_mk6/include',library/'lib/littlefs',deps];inc=[x for p in includes for x in ['-I',p]]
    flags=(['-DGLYPH_TEST_DEFAULT_ENUM=1','-fno-short-enums'] if args.default_enum else [])+['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-DLFS_NAME_MAX=32']+([] if args.default_enum else ['-fshort-enums']);objects=[]
    for src in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',library/'src/lfs.c',library/'src/lfs_util.c']:
        obj=out/(src.stem+'.o');run(['cc','-std=c11',*flags,*inc,'-c',src,'-o',obj]);objects.append(obj)
    probe=out/'mounted-store.cpp';probe.write_text('#include '+json.dumps(str(root/'HAL/pico/src/core/ProfileStore.cpp'))+'\nbool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n){MountedStorage s;return s.ReadRange(p,o,b,n);}\n')
    persist_probe=out/'persistence-observed.cpp';text=(root/'HAL/pico/src/core/Persistence.cpp').read_text();persist_probe.write_text('#include '+json.dumps(str(root/'HAL/pico/src/core/Persistence.cpp'))+'\nbool GlyphPersistenceSlotClean(){for(auto c:save_file_slot)if(c)return false;return true;}\nbool GlyphPersistenceReadPhaseClean(){'+('const auto *p=reinterpret_cast<const unsigned char*>(&phase_workspace);for(size_t i=0;i<sizeof(phase_workspace);++i)if(p[i])return false;return true;' if 'phase_workspace' in text else 'return true;')+'}\n')
    sources=[args.fixture,persist_probe,probe,root/'HAL/pico/src/core/CheckedStorage.cpp',deps/'pb_arduino.cpp',deps/'CRC32.cpp',root/'src/modes/UltimateNativeProfile.cpp',root/'src/core/config_validation.cpp',root/'src/core/config_button_validation.cpp',root/'src/core/config_usb_default_validation.cpp',root/'src/core/config_rgb_target_validation.cpp',root/'config/glyph/common/src/glyph_config_validation.cpp'];exe=out/'decoder-import-nor'
    run(['c++','-std=c++17',*flags,'-Wall','-Wextra','-Werror','-Wno-error=missing-field-initializers','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1',*inc,*sources,*objects,'-o',exe]);output=run([exe,fixture]);(out/'run.log').write_text(output);(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');pins=[*sources,Path(__file__),root/'HAL/pico/include/core/CheckedStorageFile.hpp',root/'HAL/pico/include/core/Persistence.hpp',root/'include/core/ProfileStore.hpp',library/'lib/littlefs/lfs.c',library/'lib/littlefs/lfs.h'];(out/'report.json').write_text(json.dumps({'classification':'ACTUAL_PRODUCTION_NOR_DECODER_IMPORT_COMPONENTS_NOT_TARGET_PROOF','source_root':str(root),'default_enum':args.default_enum,'source_pins':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pins},'output_sha256':hashlib.sha256(output.encode()).hexdigest(),'hardware':'NOT_TESTED'},indent=2)+'\n');print(output.splitlines()[-1])
if __name__=='__main__':
    try:main()
    except (AssertionError,OSError,RuntimeError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);raise SystemExit(1)
