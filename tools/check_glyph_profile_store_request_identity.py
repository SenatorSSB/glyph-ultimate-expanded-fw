#!/usr/bin/env python3
"""Compile actual generated protocol and firmware SHA256/request identity."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
NANOPB = ROOT / '.pio/libdeps/glyph_mk6/Nanopb'

def run(args):
    p = subprocess.run(args,cwd=ROOT,text=True,capture_output=True,check=False,timeout=60)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout

def main():
    try:
        with tempfile.TemporaryDirectory(prefix='glyph-request-identity-') as directory:
            temp=Path(directory)
            run([sys.executable,str(NANOPB/'generator/nanopb_generator.py'),'-I',str(ROOT/'schema/haybox'),'-f',str(ROOT/'schema/haybox/config.options'),'--error-on-unmatched','--no-timestamp','-D',str(temp),str(ROOT/'schema/haybox/config.proto')])
            flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if os.getenv('GLYPH_PROFILE_STORE_SANITIZERS')=='1' else []
            includes=['-I',str(temp),'-I',str(NANOPB),'-I',str(ROOT/'include')]
            objects=[]
            for source in [NANOPB/'pb_common.c',NANOPB/'pb_encode.c',NANOPB/'pb_decode.c',temp/'config.pb.c']:
                target=temp/(source.stem+'.o'); run(['cc',*flags,'-std=c11',*includes,'-c',str(source),'-o',str(target)]);objects.append(str(target))
            exe=temp/'test';run(['c++',*flags,'-std=c++17','-Wall','-Wextra','-Werror',*includes,str(ROOT/'tools/fixtures/profile_store_request_identity_host.cpp'),*objects,'-o',str(exe)])
            print(run([str(exe)]).strip())
        print('glyph_profile_store_request_identity: PASS')
        return 0
    except Exception as error:
        print(f'glyph_profile_store_request_identity: FAIL: {error}')
        return 1
if __name__=='__main__': raise SystemExit(main())
