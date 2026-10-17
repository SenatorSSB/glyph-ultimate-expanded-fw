#!/usr/bin/env python3
"""Compile the actual CDC/FIFO engine and production COBS/writer; no device I/O."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'tools/fixtures/profile_store_cdc_progress'
FROZEN = 'd59684b9368be61183881bdfc82adc774ad5f0ba'

def run(argv, **kwargs):
    result = subprocess.run(list(map(str, argv)), cwd=ROOT, capture_output=True, text=True, timeout=120, **kwargs)
    if result.returncode:
        raise RuntimeError(' '.join(map(str,argv))+'\n'+result.stdout+result.stderr)
    return result.stdout

def extract_writer(source):
    start=source.index('class ProfilePacketWriter final')
    end=source.index('\n};',start)+3
    return source[start:end]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--framework',type=Path,default=Path.home()/'.platformio/packages/framework-arduinopico')
    parser.add_argument('--libdeps',type=Path,default=ROOT/'.pio/libdeps/glyph_mk6')
    args=parser.parse_args()
    usb=args.framework/'libraries/Adafruit_TinyUSB_Arduino/src'
    libs=args.libdeps
    if not (libs/'PacketIO').exists():
        raise RuntimeError('PacketIO dependency unavailable; populate glyph_mk6 dependencies or pass --libdeps')
    package=json.loads((args.framework/'package.json').read_text())
    assert package['version']=='1.30603.0', 'This regression requires pinned Arduino-Pico 3.6.3'
    target_config=(ROOT/'HAL/pico/include/tusb_config_pico.h').read_text()
    assert '#define CFG_TUD_CDC_TX_BUFSIZE 256' in target_config
    assert '#define CFG_TUSB_OS OPT_OS_PICO' in target_config
    manifest=json.loads((HOST/'payload_manifest.json').read_text())
    for name, metadata in manifest.items():
        data=(HOST/(name+'.pb')).read_bytes()
        assert len(data)==metadata['size'] and hashlib.sha256(data).hexdigest()==metadata['payload_sha256']
    with tempfile.TemporaryDirectory(prefix='glyph-cdc-progress-') as directory:
        tmp=Path(directory)
        cdc=tmp/'cdc_device.c'
        pinned=(usb/'class/cdc/cdc_device.c').read_text()
        assert 'tu_edpt_stream_write' not in pinned
        cdc.write_text(pinned+'\n'+(HOST/'cdc_fixture_tail.c').read_text())
        flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
        includes=['-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-I',HOST/'include','-I',usb,'-I',usb/'class/cdc','-I',libs/'PacketIO/src','-I',tmp]
        generated=tmp/'generated'; generated.mkdir()
        nanopb=libs/'Nanopb'
        run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',generated,ROOT/'schema/haybox/config.proto'])
        includes += ['-I',generated,'-I',nanopb]
        objects=[]
        for src in (cdc,usb/'common/tusb_fifo.c',nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',generated/'config.pb.c'):
            obj=tmp/(src.stem+'.o')
            run(['cc','-std=c11','-fshort-enums',*flags,*includes,'-c',src,'-o',obj]); objects.append(obj)
        outputs={}
        for old in (True,False):
            source=run(['git','show',FROZEN+':HAL/pico/src/comms/ConfiguratorBackend.cpp']) if old else (ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp').read_text()
            stream=run(['git','show',FROZEN+':HAL/pico/include/comms/CoordinatedCdcStream.hpp']) if old else (ROOT/'HAL/pico/include/comms/CoordinatedCdcStream.hpp').read_text()
            (tmp/'CoordinatedCdcStream.hpp').write_text(stream)
            (tmp/'writer.inc').write_text(extract_writer(source))
            start=source.index('bool ConfiguratorBackend::WriteProfilePacket(')
            end=source.index('\n}',start)+2
            (tmp/'packet.inc').write_text(source[start:end])
            exe=tmp/('old' if old else 'current')
            run(['c++','-std=c++17','-fshort-enums','-DARDUINO=1','-DGLYPH_CDC_COORDINATION_TEST=1',f'-DEXPECT_OLD={int(old)}',*flags,*includes,HOST/'harness.cpp',*objects,'-o',exe])
            outputs['old' if old else 'current']=run([exe,*(HOST/name for name in ('status.pb','list.pb','physical-id1-response.pb','maximum-stage-c-response.pb','physical-id3-response.pb','physical-id4-response.pb','physical-id22-response.pb'))])
            print(outputs['old' if old else 'current'].strip())
        report={'result':'PASS','frozen':FROZEN,'framework_version':package['version'],'payloads':manifest,'outputs':outputs,'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (usb/'class/cdc/cdc_device.c',usb/'common/tusb_fifo.c',usb/'osal/osal_pico.h',usb/'device/usbd.c',usb/'arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',args.framework/'cores/rp2040/delay.cpp',libs/'PacketIO/src/cobs/Print.h',HOST/'harness.cpp',HOST/'cdc_fixture_tail.c',ROOT/'HAL/pico/include/tusb_config_pico.h',ROOT/'schema/haybox/config.proto',ROOT/'HAL/pico/include/comms/CoordinatedCdcStream.hpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp')}}
        if args.output_dir:
            args.output_dir.mkdir(parents=True,exist_ok=True)
            (args.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
