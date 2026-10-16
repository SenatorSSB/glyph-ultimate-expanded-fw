#!/usr/bin/env python3
"""Actual backend/store/checked-storage + pinned LittleFS, including frozen4ee.

Config is an explicit host boundary. Its loads assert the hook has ended; the
separate production Persistence matrix remains required. Opens no device.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from check_glyph_stage_b_ultimate_profiles import ROOT, NANOPB, make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
import glyph_serial_config_tool as transport

FROZEN='4ee63e26c912a0954ab9d7028a70a04ff80ced8d'
HOST=ROOT/'tools/fixtures/profile_store_timeout_host'
FIX=ROOT/'tools/fixtures/profile_store_root_reconcile_host/harness.cpp'

def run(args):
    p=subprocess.run(list(map(str,args)),cwd=ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
    if p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
    return p.stdout

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path);a=ap.parse_args()
    try:
        assert json.loads((FRAMEWORK/'package.json').read_text())['version']=='1.30603.0'
        results=[]
        with tempfile.TemporaryDirectory(prefix='glyph-root-reconcile-') as directory:
            temp=Path(directory);generated=temp/'generated';generated.mkdir();nano=Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB',str(NANOPB)))
            run([sys.executable,nano/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',generated,ROOT/'schema/haybox/config.proto'])
            pb,jf,_=transport.load_runtime_proto_modules(ROOT);_,payload=transport.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=temp/'fixture.pb';fixture.write_bytes(payload)
            library=FRAMEWORK/'libraries/LittleFS';libs=ROOT/'.pio/libdeps/glyph_mk6'
            # Instrument only Config load boundaries in the existing functional
            # mock. Production storage and its fault delivery are unmodified.
            overlay=temp/'overlay/core';overlay.mkdir(parents=True)
            text=(HOST/'include/core/Persistence.hpp').read_text().replace('class Persistence {','extern bool GlyphFaultHookInstalled();\nclass Persistence {').replace('    ++load_calls;','    if (GlyphFaultHookInstalled()) throw std::runtime_error("hook leaked into Config load");\n    ++load_calls;')
            (overlay/'Persistence.hpp').write_text('#include <stdexcept>\n'+text)
            includes=[temp/'overlay',HOST/'include',ROOT/'HAL/pico/include',ROOT/'include',generated,nano,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',library/'lib/littlefs']
            inc=[item for p in includes for item in ['-I',p]];san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'];common=['-fshort-enums','-DLFS_NAME_MAX=32','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1']
            objects=[]
            for src in [nano/'pb_common.c',nano/'pb_encode.c',nano/'pb_decode.c',generated/'config.pb.c',library/'src/lfs.c',library/'src/lfs_util.c']:
                obj=temp/(src.stem+'.o');run(['cc','-std=c11',*san,*common,*inc,'-c',src,'-o',obj]);objects.append(obj)
            probe=temp/'checked_probe.cpp';probe.write_text('#include '+json.dumps(str(ROOT/'HAL/pico/src/core/CheckedStorage.cpp'))+'\nbool GlyphFaultHookInstalled(){return CheckedStorage::faults!=nullptr;}\n')
            sources=[FIX,ROOT/'HAL/pico/src/core/ProfileStore.cpp',probe,ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp',libs/'nanopb-arduino/src/pb_arduino.cpp']
            flags=['-Wno-error=missing-field-initializers','-Wall','-Wextra','-Werror','-Wno-error=inconsistent-missing-override','-Wno-misleading-indentation','-Wno-error=unused-function']
            for variant in ('current','frozen','production'):
                extra=[];backend=ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp'
                if variant=='frozen':
                    freeze=temp/'frozen';(freeze/'include/core').mkdir(parents=True)
                    for relative in ('HAL/pico/src/comms/ConfiguratorBackend.cpp','include/core/ProfileStoreFaultControls.hpp'):
                        target=freeze/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(subprocess.check_output(['git','show',FROZEN+':'+relative],cwd=ROOT))
                    # Engine and checked shim are byte-identical to frozen4ee.
                    for relative in ('HAL/pico/src/core/ProfileStore.cpp','HAL/pico/src/core/CheckedStorage.cpp'):
                        assert (ROOT/relative).read_bytes()==subprocess.check_output(['git','show',FROZEN+':'+relative],cwd=ROOT)
                    backend=freeze/'HAL/pico/src/comms/ConfiguratorBackend.cpp';extra=['-I',freeze/'include','-DEXPECT_FROZEN=1']
                extra+=['-DEXPECT_PRODUCTION=1'] if variant=='production' else ['-DGLYPH_STRICT_HARDENING_CANDIDATE=1']
                exe=temp/(variant+'-test');run(['c++','-std=c++17','-DARDUINO=1',*san,*common,*flags,*extra,*inc,*sources,backend,*objects,'-o',exe])
                modes=['special','not-uncertain'] if variant=='production' else ['frozen-ordinary','special'] if variant=='frozen' else ['special','special-even','special-create','trace-fail42','trace-fail43','trace-fail44','ordinary','v1','zero-token','wrong-phase','wrong-ticket','record','config','control','rename','read','write','lost-ack','skip','status','list','read-only','replay','not-uncertain']
                for mode in modes:
                    line=run([exe,fixture,mode]);results.append({'variant':variant,'mode':mode,'output':line.strip()});print(line,end='')
        report={'result':'PASS','cases':results,'sanitizers':['ASan','UBSan'],'frozen':FROZEN,'device_actions':'NONE','source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [FIX,ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'HAL/pico/src/core/ProfileStore.cpp',ROOT/'HAL/pico/src/core/CheckedStorage.cpp',ROOT/'include/core/ProfileStoreFaultControls.hpp',ROOT/'schema/haybox/config.proto']}}
        if a.output_dir:a.output_dir.mkdir(parents=True,exist_ok=True);(a.output_dir/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print('glyph_profile_store_root_reconcile: PASS');return 0
    except Exception as e:print('glyph_profile_store_root_reconcile: FAIL: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())
