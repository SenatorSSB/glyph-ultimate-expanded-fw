#!/usr/bin/env python3
"""Compile CURRENT Persistence.cpp against named-file fault doubles and real Nanopb/CRC.

Host rename failures are definite no-op failures. Target LittleFS power-loss,
ambiguous acknowledgements, sync/close and allocator geometry are not emulated.
"""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT
HOST = ROOT / 'tools/fixtures/profile_store_config_persistence_host'
DEPS = ROOT / 'tools/fixtures/gp_config021_persisted_recovery'

def run(args):
    p = subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True, text=True, timeout=60,
                       env={**os.environ, 'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
    if p.returncode: raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
    return p.stdout

def main():
    try:
        nanopb = Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB', str(NANOPB)))
        sanitize = ['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if os.environ.get('GLYPH_PROFILE_STORE_SANITIZERS') == '1' else []
        with tempfile.TemporaryDirectory(prefix='profile-config-persistence-') as d:
            temp=Path(d); generated=temp/'generated';generated.mkdir();schema=ROOT/'schema/haybox'
            run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',generated,schema/'config.proto'])
            includes=[HOST/'include',DEPS/'include',ROOT/'HAL/pico/include',ROOT/'include',generated,nanopb,DEPS/'dependencies']
            flags=[item for p in includes for item in ['-I',p]]
            objects=[]
            for src in [nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',generated/'config.pb.c']:
                obj=temp/(src.stem+'.o');run(['cc',*sanitize,'-std=c11','-fshort-enums',*flags,'-c',src,'-o',obj]);objects.append(obj)
            sources=[HOST/'persistence_harness.cpp',ROOT/'HAL/pico/src/core/Persistence.cpp',DEPS/'dependencies/pb_arduino.cpp',DEPS/'dependencies/CRC32.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp']
            exe=temp/'persistence';run(['c++',*sanitize,'-std=c++17','-DARDUINO=1','-fshort-enums','-Wall','-Wextra','-Werror','-Wno-error=missing-field-initializers',*flags,*sources,*objects,'-o',exe])
            print(run([exe]),end='')
        print('glyph_profile_store_config_persistence: PASS; current_source=true hardware=NOT_CLAIMED')
        return 0
    except (OSError,RuntimeError,subprocess.SubprocessError) as e:
        print('glyph_profile_store_config_persistence: FAIL: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())
