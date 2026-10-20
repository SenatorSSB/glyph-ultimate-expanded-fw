#!/usr/bin/env python3
"""Current production v2 engine: bounded512KiB + actual pinned LittleFS fault proof."""
from pathlib import Path
import os
import json
import subprocess
import sys
import tempfile
from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT, make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
HOST=ROOT/'tools/fixtures/profile_store_strict_host'
def run(args):
 p=subprocess.run([str(a) for a in args],cwd=ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
 if p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
 return p.stdout

def main():
 try:
  if json.loads((FRAMEWORK/'package.json').read_text())['version']!='1.30603.0':raise RuntimeError('expected pinned Arduino-Pico3.6.3')
  nanopb=Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB',str(NANOPB))); flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
  with tempfile.TemporaryDirectory(prefix='glyph-strict-store-') as directory:
   temp=Path(directory);generated=temp/'generated';generated.mkdir();schema=ROOT/'schema/haybox'
   run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',generated,schema/'config.proto'])
   import glyph_serial_config_tool as writer
   config_pb2,json_format,_=writer.load_runtime_proto_modules(ROOT);_,payload=writer.encode_artifact_payload(make_v3_artifact(),config_pb2,json_format);fixture=temp/'legacy.pb';fixture.write_bytes(payload)
   library=FRAMEWORK/'libraries/LittleFS';includes=[generated,nanopb,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',library/'lib/littlefs'];inc=[item for p in includes for item in ['-I',p]];objects=[]
   for src in [nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',generated/'config.pb.c',library/'src/lfs.c',library/'src/lfs_util.c']:
    obj=temp/(src.stem+'.o');run(['cc','-std=c11',*flags,'-fshort-enums','-DLFS_NAME_MAX=32',*inc,'-c',src,'-o',obj]);objects.append(obj)
   # Host-only source inclusion exposes the real anonymous-namespace adapter
   # through one temporary probe. No production API or alternate adapter.
   probe=temp/'mounted_storage_probe.cpp'
   probe.write_text('#include '+json.dumps(str(ROOT/'HAL/pico/src/core/ProfileStore.cpp'))+'\n'
                    'bool GlyphMountedReadRangeProbe(const char *p,size_t offset,uint8_t *b,size_t n) { MountedStorage storage; return storage.ReadRange(p,offset,b,n); }\n')
   sources=[HOST/'strict_harness.cpp',probe,ROOT/'HAL/pico/src/core/CheckedStorage.cpp',ROOT/'src/modes/UltimateNativeProfile.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp'];exe=temp/'strict-store'
   run(['c++','-std=c++17',*flags,'-fshort-enums','-Wall','-Wextra','-Werror','-DLFS_NAME_MAX=32','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1',*inc,*sources,*objects,'-o',exe]);print(run([exe,fixture]),end='')
   # Genuine previous production negative controls, with its frozen headers.
   frozen=temp/'frozen';(frozen/'include/core').mkdir(parents=True)
   revision='f7ba82d4cbe79d4353e8d87b7d1b24be3fc15113'
   for relative in ['HAL/pico/src/core/ProfileStore.cpp','include/core/ProfileStore.hpp','include/core/ProfileStoreStorage.hpp','include/core/ProfileStoreAtomicCommit.hpp','include/core/ProfileStorePaths.hpp','include/core/ProfileStoreCapacity.hpp']:
    result=subprocess.run(['git','show',revision+':'+relative],cwd=ROOT,capture_output=True,check=False)
    if result.returncode:raise RuntimeError('frozen source unavailable '+relative)
    target=frozen/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(result.stdout)
   negative=temp/'frozen-negative';negative_inc=['-I',frozen/'include','-I',ROOT/'tools/fixtures/profile_store_migration_lifecycle_host/include',*inc]
   run(['c++','-std=c++17',*flags,'-fshort-enums','-Wall','-Wextra','-Werror',*negative_inc,HOST/'negative_harness.cpp',frozen/'HAL/pico/src/core/ProfileStore.cpp',*sources[3:],*objects[:4],'-o',negative]);print(run([negative,fixture]),end='')
  print('glyph_profile_store_strict_host: PASS');return 0
 except (OSError,RuntimeError,subprocess.SubprocessError) as e:
  print('glyph_profile_store_strict_host: FAIL: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())
