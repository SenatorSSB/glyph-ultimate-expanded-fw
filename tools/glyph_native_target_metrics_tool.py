#!/usr/bin/env python3
"""Strict retained native target snapshot decoder/read-only XInput query.

A supplied --port authorizes only the one fixed16-byte GET_SNAPSHOT. Device
session execution still requires the separately approved exact candidate packet.
No Configurator/profile/reset/flash/control command is implemented.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import secrets
import struct
import time
import glyph_runtime_identity_tool as identity

MAGIC=b'\xd7GNM'

def request(token):
    if not 0<token<2**64:raise ValueError('nonzero uint64 token required')
    return MAGIC+struct.pack('<BBHQ',1,1,16,token)

def decode(frame,token,expected_source=None):
    if len(frame)!=160 or frame[:8]!=MAGIC+struct.pack('<BBH',1,129,160):raise ValueError('invalid diagnostic header/version/kind/length')
    if struct.unpack_from('<Q',frame,8)[0]!=token:raise ValueError('diagnostic token mismatch')
    status,backend,valid=struct.unpack_from('<BBH',frame,16)
    if status>2 or backend!=2 or valid&~511:raise ValueError('invalid diagnostic status/backend/validity bits')
    source=frame[20:40].hex();sequence,generation=struct.unpack_from('<II',frame,40)
    if not sequence:raise ValueError('missing capture sequence')
    if expected_source and source!=expected_source.lower():raise ValueError('exact candidate source SHA differs')
    source_flags,timer_flags,uptime=struct.unpack_from('<HHI',frame,152)
    if source_flags&~3 or timer_flags&~8191:raise ValueError('unknown source/timer flags')
    statistics={}
    for i,name in enumerate(('native_frame','native_activation','timer_calibration')):
        count,minimum,maximum,low,high=struct.unpack_from('<5I',frame,48+20*i);total=(high<<32)|low
        if not count and any((minimum,maximum,total)):raise ValueError('empty statistic has values')
        if count and minimum>maximum:raise ValueError('statistic min exceeds max')
        saturated=bool(timer_flags&(3<<(2*i)))
        if count and not saturated and not minimum*count<=total<=maximum*count:raise ValueError('inconsistent statistic sum')
        statistics[name]={'count':count,'min_us':minimum,'max_us':maximum,'sum_us':total,'saturated':saturated}
    scans={}
    for core,offset in enumerate((108,124)):
        used,sp,scan,maximum,flags,reserved=struct.unpack_from('<HHIIHH',frame,offset)
        if reserved or flags&~511 or used>2048 or sp>2048:raise ValueError('invalid stack extent/flags/reserved')
        scans['core'+str(core)]={'observed_used_bytes':used,'sampled_sp_used_bytes':sp,'completed_scan_generation':scan,'chunk_max_us':maximum,'flags':flags}
    if bool(valid&32)!=(source_flags==3):raise ValueError('source validity disagrees with source flags')
    if valid&64 and not generation:raise ValueError('valid native generation is zero')
    if status==0:
        if valid!=511 or timer_flags&~(1<<10) or source_flags!=3 or not generation:raise ValueError('COMPLETE snapshot has invalid flags')
        if not statistics['native_frame']['count'] or not statistics['native_activation']['count'] or statistics['timer_calibration']['count']!=16:raise ValueError('COMPLETE lacks samples/calibration')
        for scan in scans.values():
            if scan['flags']&(4|32|64|128|256) or scan['flags']&27!=27 or not scan['completed_scan_generation']:raise ValueError('COMPLETE has incomplete/faulted scan')
        if uptime>=3600:raise ValueError('COMPLETE expired session')
    return {'status':('complete','partial','invalid')[status],'backend':'xinput','validity_flags':valid,
            'source_git_sha':source,'capture_sequence':sequence,'native_generation':generation,
            'statistics':statistics,'stack_observations':scans,
            'overhead_max_us':dict(zip(('frame_record','activation_record','observer_service'),struct.unpack_from('<3I',frame,140))),
            'source_flags':source_flags,'timer_flags':timer_flags,'uptime_seconds':uptime,
            'limits':'post-startup finite observations; includes preemption/quantization; not cycles/WCET or whole-stack proof'}

class Decoder:
    def __init__(self,token,expected_source=None):
        request(token);self.token=token;self.expected_source=expected_source;self.pending=bytearray();self.response=None
        self.viewer_records=0;self.identities=[]
    def feed(self,data):
        self.pending.extend(data)
        while self.pending:
            if self.pending[0] in (48,49):
                if len(self.pending)<25:return
                if any(b not in (48,49) for b in self.pending[:24]) or self.pending[24]!=10:raise ValueError('invalid viewer record')
                del self.pending[:25];self.viewer_records+=1;continue
            if self.pending[0]==MAGIC[0]:
                if len(self.pending)<8:return
                if self.pending[:8]!=MAGIC+struct.pack('<BBH',1,129,160):raise ValueError('invalid diagnostic frame header')
                if len(self.pending)<160:return
                frame=bytes(self.pending[:160]);del self.pending[:160]
                if self.response is not None:raise ValueError('duplicate diagnostic response')
                self.response=decode(frame,self.token,self.expected_source);continue
            if self.pending[0]==identity.MAGIC[0]:
                if len(self.pending)<8:return
                if self.pending[:8]!=identity.MAGIC+struct.pack('<BBH',1,2,72):raise ValueError('invalid identity frame header')
                if len(self.pending)<72:return
                frame=bytes(self.pending[:72]);del self.pending[:72]
                decoder=identity.Decoder(struct.unpack_from('<Q',frame,8)[0],expected_backend=2);decoder.feed(frame)
                self.identities.append(decoder.finish());continue
            raise ValueError('unknown/ambiguous XInput stream byte')
    def finish(self):
        if self.pending or self.response is None:raise ValueError('partial/timeout/no complete diagnostic response')
        return dict(self.response,viewer_records=self.viewer_records,identity_observations=self.identities)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);src=parser.add_mutually_exclusive_group(required=True)
    src.add_argument('--capture',type=Path);src.add_argument('--port')
    parser.add_argument('--token',type=lambda x:int(x,0));parser.add_argument('--session',required=True)
    parser.add_argument('--expected-source-sha');parser.add_argument('--timeout',type=float,default=2)
    parser.add_argument('--raw-out',type=Path);parser.add_argument('--request-out',type=Path)
    a=parser.parse_args(argv)
    if not 0<a.timeout<=10:parser.error('timeout must be within(0,10]')
    if a.capture and a.token is None:parser.error('capture requires its exact token')
    if a.expected_source_sha and (len(a.expected_source_sha)!=40 or any(x not in '0123456789abcdef' for x in a.expected_source_sha.lower())):parser.error('full40hex source SHA required')
    if a.port and (not a.raw_out or not a.request_out or not a.expected_source_sha):parser.error('port requires new raw/request custody paths and exact candidate source SHA')
    token=a.token if a.token is not None else secrets.randbits(64) or 1
    decoder=Decoder(token,a.expected_source_sha)
    if a.capture:decoder.feed(a.capture.read_bytes())
    else:
        import serial
        query=request(token)
        with a.request_out.open('x') as out:
            json.dump({'session':a.session,'protocol':'Glyph.Native.TargetMetrics.v1','request_hex':query.hex(),'expected_source_sha':a.expected_source_sha},out);out.write('\n');out.flush();os.fsync(out.fileno())
        with a.raw_out.open('xb') as raw,serial.Serial(port=None,baudrate=115200,timeout=.05,write_timeout=.1) as wire:
            wire.dtr=True;wire.rts=False;wire.port=a.port;wire.open()
            if wire.write(query)!=16:raise ValueError('short request write; no retry')
            deadline=time.monotonic()+a.timeout
            while time.monotonic()<deadline and (decoder.response is None or decoder.pending):
                chunk=wire.read(max(1,min(256,wire.in_waiting)));raw.write(chunk);raw.flush();os.fsync(raw.fileno());decoder.feed(chunk)
    print(json.dumps(dict(session=a.session,observation='current_boot_xinput_only',**decoder.finish()),indent=2,sort_keys=True));return 0

if __name__=='__main__':raise SystemExit(main())
