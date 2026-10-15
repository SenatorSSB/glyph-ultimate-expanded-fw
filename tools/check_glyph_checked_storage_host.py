#!/usr/bin/env python3
"""Exercise production checked operations on pinned LittleFS; no physical claim."""
from pathlib import Path
import os
import json
import subprocess
import tempfile
from check_glyph_profile_store_littlefs_host import FRAMEWORK, ROOT, run

def main():
    try:
        if json.loads((FRAMEWORK/'package.json').read_text())['version']!='1.30603.0':raise RuntimeError('expected pinned Arduino-Pico3.6.3')
        library=FRAMEWORK/'libraries/LittleFS'
        flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
        with tempfile.TemporaryDirectory(prefix='glyph-checked-storage-') as directory:
            temp=Path(directory); objects=[]
            for name in ('lfs','lfs_util'):
                obj=temp/(name+'.o');run(['cc','-std=c11',*flags,'-DLFS_NAME_MAX=32','-c',str(library/'src'/(name+'.c')),'-o',str(obj)]);objects.append(str(obj))
            exe=temp/'checked-storage'
            run(['c++','-std=c++17',*flags,'-Wall','-Wextra','-Werror','-DLFS_NAME_MAX=32','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-I',str(ROOT/'include'),'-I',str(library/'lib/littlefs'),str(ROOT/'HAL/pico/src/core/CheckedStorage.cpp'),str(ROOT/'tools/fixtures/checked_storage_host/checked_storage_harness.cpp'),*objects,'-o',str(exe)])
            print(run([str(exe)]),end='')
        print('glyph_checked_storage_host: PASS ASAN=true UBSAN=true physical_multicore=NOT_TESTED');return 0
    except (OSError,RuntimeError,subprocess.SubprocessError) as e:
        print('glyph_checked_storage_host: FAIL: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())
