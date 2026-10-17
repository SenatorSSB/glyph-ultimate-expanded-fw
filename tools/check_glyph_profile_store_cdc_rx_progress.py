#!/usr/bin/env python3
"""Pinned TinyUSB CDC RX/FIFO + actual PacketIO reader regression; no device I/O."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT/'tools/fixtures/profile_store_cdc_rx_progress'
FROZEN='895109eb662a8ad6b6c99889cb37a254dce49998'

def run(argv,**kwargs):
    r=subprocess.run(list(map(str,argv)),cwd=ROOT,capture_output=True,text=True,timeout=180,**kwargs)
    if r.returncode:raise RuntimeError(' '.join(map(str,argv))+'\n'+r.stdout+r.stderr)
    return r.stdout

def method(source,name):
    start=source.index('size_t ConfiguratorBackend::'+name+'(')
    end=source.index('\n}',start)+2
    return source[start:end]

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--old-only',action='store_true');p.add_argument('--framework',type=Path,default=Path.home()/'.platformio/packages/framework-arduinopico');a=p.parse_args()
    usb=a.framework/'libraries/Adafruit_TinyUSB_Arduino/src';libs=ROOT/'.pio/libdeps/glyph_mk6';nano=libs/'Nanopb'
    package=json.loads((a.framework/'package.json').read_text());assert package['version']=='1.30603.0'
    config=(ROOT/'HAL/pico/include/tusb_config_pico.h').read_text();assert '#define CFG_TUD_CDC_RX_BUFSIZE 256' in config and '#define CFG_TUSB_OS OPT_OS_PICO' in config
    pinned=(usb/'class/cdc/cdc_device.c').read_text();assert 'tu_edpt_stream_read' not in pinned and '_prep_out_transaction(p_cdc)' in pinned
    manifest=json.loads((HOST/'physical-request-manifest.json').read_text());physical=(HOST/'physical-ticketed-update.pb').read_bytes();assert len(physical)==manifest['request_size'] and hashlib.sha256(physical).hexdigest()==manifest['request_sha256']
    import glyph_serial_config_tool as transport
    pb,json_format,_=transport.load_runtime_proto_modules(ROOT)
    request=pb.ProfileStoreRequest();request.ParseFromString(physical);assert request.SerializeToString(deterministic=True)==physical
    payloads={'physical-update':physical}
    for name in ('physical-arm','physical-status'):
        body=(HOST/(name+'.pb')).read_bytes();meta=manifest['controls'][name]
        assert len(body)==meta['bytes'] and hashlib.sha256(body).hexdigest()==meta['sha256']
        payloads[name]=body
    for name,op in [('arm',pb.PROFILE_STORE_ARM_STORAGE_FAULT),('status',pb.PROFILE_STORE_STATUS),('pulse',pb.PROFILE_STORE_LIVENESS),('read',pb.PROFILE_STORE_READ),('query',pb.PROFILE_STORE_QUERY_TRANSACTION),('rename',pb.PROFILE_STORE_RENAME)]:
        q=pb.ProfileStoreRequest(protocol_version=2,operation=op)
        if name=='arm':q.fault_kind=1;q.fault_path_class=1;q.fault_operation=2;q.fault_phase=1;q.fault_result=1
        if name in ('read','rename'):q.profile_id=22
        if name in ('query','rename'):q.request_token=request.request_token
        if name=='rename':q.expected_store_generation=160;q.expected_store_incarnation=1;q.name='RX metadata-only'
        payloads[name]=q.SerializeToString(deterministic=True)
    for name in ('physical-id1-response','physical-id3-response','physical-id4-response','maximum-stage-c-response'):
        r=pb.ProfileStoreResponse();r.ParseFromString((ROOT/'tools/fixtures/profile_store_cdc_progress'/(name+'.pb')).read_bytes())
        q=pb.ProfileStoreRequest();q.CopyFrom(request);q.profile.CopyFrom(r.profile)
        payloads['update-'+name]=q.SerializeToString(deterministic=True)
    import check_glyph_stage_b_ultimate_profiles as stages
    for name,artifact in (('stage-a',json.loads(stages.STAGE_A.read_text())),('stage-b',stages.make_v2_artifact()),('stage-c',stages.make_v3_artifact())):
        config,_=transport.encode_artifact_payload(artifact,pb,json_format)
        q=pb.ProfileStoreRequest();q.CopyFrom(request);q.profile.CopyFrom(config.ultimate_profiles[0])
        payloads['update-'+name]=q.SerializeToString(deterministic=True)
    # All operation/path/phase request control shapes; no store implementation runs here.
    import glyph_profile_store_candidate_tool as cli
    for path,(kind,path_class) in cli.PATHS.items():
        for operation,number in cli.OPERATIONS.items():
            for phase,result in ((1,1),(2,2)):
                q=pb.ProfileStoreRequest(protocol_version=2,operation=pb.PROFILE_STORE_ARM_STORAGE_FAULT,fault_kind=kind,fault_path_class=path_class,fault_operation=number,fault_phase=phase,fault_result=result)
                payloads[f'arm-{path}-{operation}-{phase}']=q.SerializeToString(deterministic=True)
    for name,op in cli.MUTATIONS.items():
        q=pb.ProfileStoreRequest();q.CopyFrom(request);q.operation=op
        if name not in ('create','update'):q.ClearField('profile')
        payloads['ticketed-'+name]=q.SerializeToString(deterministic=True)
    # A legitimate unknown length-delimited protobuf field exercises the transport
    # ceiling; nanopb skips it. It is not claimed to be a semantically valid UPDATE.
    def varint(n):
        out=bytearray()
        while n>127:out.append((n&127)|128);n>>=7
        out.append(n);return bytes(out)
    prefix=payloads['status'];tag=varint((100<<3)|2)
    filler=8191-len(prefix)-len(tag)-2
    payloads['near-ceiling-unknown-field']=prefix+tag+varint(filler)+bytes(filler)
    assert len(payloads['near-ceiling-unknown-field'])==8191
    for size in (63,64,65,127,128,255,256,257,512):
        # Valid protobuf with a skippable unknown field makes exact byte bounds.
        filler=next(n for n in range(size) if len(prefix)+len(tag)+len(varint(n))+n==size)
        body=prefix+tag+varint(filler)+bytes(filler)
        q=pb.ProfileStoreRequest();q.ParseFromString(body)
        assert len(body)==size and q.operation==pb.PROFILE_STORE_STATUS
        payloads['protobuf-size-'+str(size)]=body

    with tempfile.TemporaryDirectory(prefix='glyph-cdc-rx-') as directory:
        tmp=Path(directory);generated=tmp/'generated';generated.mkdir()
        run([sys.executable,nano/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',generated,ROOT/'schema/haybox/config.proto'])
        cdc=tmp/'cdc_device.c';cdc.write_text(pinned+'\n'+(HOST/'cdc_fixture_tail.c').read_text())
        flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
        inc=['-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-I',HOST/'include','-I',usb,'-I',usb/'class/cdc','-I',libs/'PacketIO/src','-I',tmp,'-I',generated,'-I',nano,'-I',ROOT/'include']
        objs=[]
        for src in (cdc,usb/'common/tusb_fifo.c',nano/'pb_common.c',nano/'pb_decode.c',nano/'pb_encode.c',generated/'config.pb.c'):
            obj=tmp/(src.stem+'.o');run(['cc','-std=c11','-fshort-enums',*flags,*inc,'-c',src,'-o',obj]);objs.append(obj)
        paths=[]
        for name,body in payloads.items():path=tmp/(name+'.pb');path.write_bytes(body);paths.append(path)
        outputs={};extracted={}
        for old in ([True] if a.old_only else [True,False]):
            source=run(['git','show',FROZEN+':HAL/pico/src/comms/ConfiguratorBackend.cpp']) if old else (ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp').read_text()
            stream=run(['git','show',FROZEN+':HAL/pico/include/comms/CoordinatedCdcStream.hpp']) if old else (ROOT/'HAL/pico/include/comms/CoordinatedCdcStream.hpp').read_text()
            reader=method(source,'ReadPacket')
            extracted['old' if old else 'current']={'reader_sha256':hashlib.sha256(reader.encode()).hexdigest(),'stream_sha256':hashlib.sha256(stream.encode()).hexdigest()}
            (tmp/'reader.inc').write_text(reader);(tmp/'CoordinatedCdcStream.hpp').write_text(stream)
            exe=tmp/('old' if old else 'current')
            run(['c++','-std=c++17','-fshort-enums','-DARDUINO=1','-DGLYPH_CDC_COORDINATION_TEST=1',f'-DEXPECT_OLD={int(old)}',*flags,*inc,HOST/'harness.cpp',*objs,'-o',exe])
            output=run([exe,*paths]);outputs['old' if old else 'current']=output;print(output)
        report={'result':'PASS','frozen':FROZEN,'framework_version':package['version'],'physical':manifest,'payloads':{name:{'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'wire_bytes':len(transport.cobs_encode(bytes([9])+body))}for name,body in payloads.items()},'outputs':outputs,'extracted':extracted,'sources':{str(path):hashlib.sha256(path.read_bytes()).hexdigest()for path in (usb/'class/cdc/cdc_device.c',usb/'common/tusb_fifo.c',usb/'osal/osal_pico.h',usb/'device/usbd.c',usb/'arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',a.framework/'cores/rp2040/delay.cpp',libs/'PacketIO/src/cobs/Stream.h',libs/'PacketIO/src/cobs/Print.h',HOST/'harness.cpp',HOST/'cdc_fixture_tail.c',ROOT/'HAL/pico/include/comms/CoordinatedCdcStream.hpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'include/core/ProfileStoreRxDiagnostics.hpp')}}
        if a.output_dir:a.output_dir.mkdir(parents=True,exist_ok=True);(a.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
