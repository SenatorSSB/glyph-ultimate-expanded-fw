#!/usr/bin/env python3
"""Bounded owner-invoked profile-store operations; never flash, reset or retry."""
from pathlib import Path
import argparse
import json
import hashlib
import os
import select
import time
import sys
import glyph_serial_config_tool as transport

ROOT=Path(__file__).resolve().parents[1]
OPERATIONS={'open-read':1,'open-write':2,'read':3,'write':4,'seek':5,'sync':6,'close':7,'stat':8,'remove':9,'rename':10}
PATHS={'record':(1,1),'root':(2,2),'control':(2,3),'config':(3,4)}

TRACE_SINK=None
def event(phase, state, **fields):
    row={'monotonic_ns':time.monotonic_ns(),'utc_ns':time.time_ns(),'phase':phase,'event':state,**fields}
    line=json.dumps(row,sort_keys=True)+'\n'
    print(line,end='',file=sys.stderr,flush=True)
    if TRACE_SINK is not None:
        TRACE_SINK.write(line);TRACE_SINK.flush();os.fsync(TRACE_SINK.fileno())

def request(port,pb,message,exact_payload=None,phase='request'):
    payload=exact_payload if exact_payload is not None else message.SerializeToString(deterministic=True)
    if len(payload)>8192: raise transport.ToolError('request exceeds frame bound')
    event(phase,'transmit_attempt',operation=message.operation,request_sha256=hashlib.sha256(payload).hexdigest())
    port.write_all(transport.cobs_encode(bytes([9])+payload))
    event(phase,'transmitted',operation=message.operation)
    deadline=time.monotonic()+port.timeout_sec
    frame=bytearray()
    while time.monotonic()<deadline:
        remaining=deadline-time.monotonic()
        if not select.select([port.fd],[],[],remaining)[0]:continue
        for byte in os.read(port.fd,1024):
            if byte:
                frame.append(byte)
                if len(frame)>8258:raise transport.ToolError('response exceeds bounded COBS frame')
                continue
            if not frame:continue  # Explicit transport resynchronization delimiter.
            decoded=transport.cobs_decode(bytes(frame)+b'\0');frame.clear()
            if not decoded or decoded[0]!=9:raise transport.ToolError('unexpected response command')
            if len(decoded)-1>8192:raise transport.ToolError('response exceeds protobuf bound')
            response=pb.ProfileStoreResponse();response.ParseFromString(decoded[1:])
            if response.request_token!=message.request_token:raise transport.ToolError('response token mismatch')
            if response.liveness_stage:
                event(phase,'device_stage',stage=response.liveness_stage)
                continue
            event(phase,'response',status=response.status)
            return response
    event(phase,'response_timeout',operation=message.operation)
    raise transport.ToolError(f'{phase}: bounded profile-store response timeout after transmission; inspect trace before retry')

MUTATIONS={'create':4,'update':5,'duplicate':6,'rename':7,'reorder':8,'delete':9,'set-reference':10}

def parse_args(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    number=lambda text:int(text,0)
    parser.add_argument('--port',required=True);parser.add_argument('--timeout',type=float,default=5)
    parser.add_argument('action',choices=['pulse','status','list','read','health','query','arm','clear','replay',*MUTATIONS])
    parser.add_argument('--profile-id',type=number,default=0);parser.add_argument('--token',type=number,default=0)
    parser.add_argument('--page',type=number,default=0);parser.add_argument('--page-size',type=int,default=8)
    parser.add_argument('--store-generation',type=number);parser.add_argument('--profile-revision',type=number)
    parser.add_argument('--config-generation',type=number);parser.add_argument('--incarnation',type=number)
    parser.add_argument('--mode-index',type=number);parser.add_argument('--name');parser.add_argument('--rank',type=number)
    parser.add_argument('--profile-json',type=Path);parser.add_argument('--profile-sha256')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--trace-out',type=Path,help='exclusive fsynced phase journal, including transmission and device progress')
    parser.add_argument('--trace',action='store_true',help='candidate-only progress frames on STATUS/preflight')
    parser.add_argument('--fault-ticket',type=number,default=0,help='explicit pending fault ticket for this mutation only')
    parser.add_argument('--request-out',type=Path,help='new receipt file written before first mutation; existing files are refused')
    parser.add_argument('--replay-request',type=Path,help='exact immutable request receipt to send once, explicitly')
    parser.add_argument('--path-class',choices=PATHS);parser.add_argument('--operation',choices=OPERATIONS)
    parser.add_argument('--result',choices=['fail-before','lost-ack-after']);parser.add_argument('--skip',type=int,default=0)
    args=parser.parse_args(argv)
    if args.output and any(item and args.output.resolve()==item.resolve() for item in (args.request_out,args.replay_request,args.profile_json)):
        parser.error('output must not overwrite source profile or immutable request receipt')
    if args.fault_ticket and (args.action not in MUTATIONS or not 0<args.fault_ticket<=0xffffffff):parser.error('fault-ticket requires mutation and uint32')
    if args.trace_out and any(item and args.trace_out.resolve()==item.resolve() for item in (args.output,args.request_out,args.replay_request,args.profile_json)):parser.error('trace journal must be distinct from output, receipt and source paths')
    if not 0<args.timeout<=10:parser.error('timeout must be within (0,10] seconds')
    if not 0<=args.skip<=8:parser.error('skip must be 0..8')
    if not 0<=args.page<=64 or not 1<=args.page_size<=8:parser.error('page must be 0..64 and page-size 1..8')
    if args.action=='query' or args.action in MUTATIONS:
        if not 0<args.token<=0xffffffffffffffff:parser.error('requires full nonzero uint64 --token')
    if args.action=='replay' and not args.replay_request:parser.error('replay requires --replay-request receipt')
    if args.action in MUTATIONS:
        if not args.request_out:parser.error('mutation requires --request-out for exact request custody before transmission')
        if args.store_generation is None or args.incarnation is None:parser.error('mutation requires explicit --store-generation and --incarnation')
        if not 0<=args.store_generation<=0xffffffff or not 0<args.incarnation<=0xffffffff:parser.error('generation/incarnation outside current uint32 contract')
    if args.action in ('read','health','update','duplicate','rename','reorder','delete') and not 0<args.profile_id<=0xffffffff:parser.error('requires nonzero uint32 --profile-id')
    if args.action in ('create','update') and not args.profile_json:parser.error('requires --profile-json (bare UltimateProfile or READ response JSON)')
    if args.action in ('update','duplicate') and (args.profile_revision is None or not 0<args.profile_revision<=0xffffffff):parser.error('requires positive uint32 --profile-revision')
    if args.action in ('create','duplicate','rename') and args.name is None:parser.error('requires explicit --name (empty accepted)')
    if args.name is not None and (len(args.name.encode('utf-8'))>32 or '\0' in args.name):parser.error('name must be at most 32 UTF-8 bytes without NUL')
    if args.action in ('create','duplicate','reorder') and (args.rank is None or not 0<=args.rank<=0xffffffff):parser.error('requires explicit uint32 --rank')
    if args.action=='set-reference':
        if args.mode_index is None or args.config_generation is None:parser.error('requires explicit --mode-index and --config-generation')
        if not 0<=args.mode_index<=0xffffffff or not 0<=args.profile_id<=0xffffffff or not 0<=args.config_generation<=0xffffffff:parser.error('reference fields outside current uint32 contract')
    if args.action=='arm' and (not args.path_class or not args.operation or not args.result):parser.error('arm requires path-class, operation and result')
    return args

def build_message(args,pb,json_format):
    message=pb.ProfileStoreRequest(protocol_version=2,request_token=args.token)
    host={}
    if args.action=='replay':
        if args.replay_request.stat().st_size>131072:raise transport.ToolError('request receipt exceeds bounded size')
        saved=json.loads(args.replay_request.read_text(encoding='utf-8'))
        payload=bytes.fromhex(saved['request_hex'])
        if len(payload)>8192 or hashlib.sha256(payload).hexdigest()!=saved['request_sha256']:raise transport.ToolError('request receipt byte/hash mismatch')
        message.ParseFromString(payload)
        if saved.get('receipt_format')!=1 or message.protocol_version!=2 or message.operation not in MUTATIONS.values() or not message.request_token or not message.expected_store_incarnation or message.expected_store_incarnation!=saved.get('incarnation'):raise transport.ToolError('invalid replay receipt identity')
        if saved.get('decoded_request')!=json_format.MessageToDict(message,preserving_proto_field_name=True):raise transport.ToolError('receipt decoded fields do not match exact bytes')
        host['_exact_payload']=payload
    elif args.action in ('arm','clear'):
        message.operation=pb.PROFILE_STORE_ARM_STORAGE_FAULT
        if args.action=='clear':message.fault_clear=True
        else:
            message.fault_kind,message.fault_path_class=PATHS[args.path_class]
            message.fault_operation=OPERATIONS[args.operation]
            message.fault_phase,message.fault_result=(1,1) if args.result=='fail-before' else (2,2)
            message.fault_skip=args.skip
    elif args.action in MUTATIONS:
        message.operation=MUTATIONS[args.action]
        message.fault_ticket=args.fault_ticket
        message.expected_store_generation=args.store_generation
        message.expected_store_incarnation=args.incarnation
        message.profile_id=args.profile_id
        if args.profile_revision is not None:message.expected_profile_revision=args.profile_revision
        if args.config_generation is not None:message.expected_config_generation=args.config_generation
        if args.mode_index is not None:message.mode_config_index=args.mode_index
        if args.name is not None:message.name=args.name
        if args.rank is not None:message.display_rank=args.rank
        if args.profile_json:
            source=args.profile_json.read_bytes();host['profile_file_sha256']=hashlib.sha256(source).hexdigest()
            if args.profile_sha256 and args.profile_sha256.lower()!=host['profile_file_sha256']:raise transport.ToolError('profile JSON source digest mismatch')
            artifact=json.loads(source)
            if 'response' in artifact:artifact=artifact['response']
            if 'profile' in artifact:artifact=artifact['profile']
            json_format.ParseDict(artifact,message.profile,ignore_unknown_fields=False)
    else:
        message.operation={'pulse':pb.PROFILE_STORE_LIVENESS,'status':pb.PROFILE_STORE_STATUS,'list':pb.PROFILE_STORE_LIST,'read':pb.PROFILE_STORE_READ,'health':pb.PROFILE_STORE_INSPECT_HEALTH,'query':pb.PROFILE_STORE_QUERY_TRANSACTION}[args.action]
        message.profile_id=args.profile_id;message.page_cursor=args.page;message.page_size=args.page_size if args.action=='list' else 0
    if args.trace and args.action in ('pulse','status','arm','clear'):message.liveness_trace=True
    payload=host.get('_exact_payload',message.SerializeToString(deterministic=True))
    if len(payload)>8192:raise transport.ToolError('request exceeds bounded 8192-byte body')
    host['transmitted_request_sha256']=hashlib.sha256(payload).hexdigest()
    return message,host

def verify_preflight(args,status,message):
    if args.action in ('arm','clear'):
        if not status.strict_hardening_candidate or not status.storage_fault_capable or status.fault_control_version!=2:raise transport.ToolError('target does not advertise candidate fault capability')
    elif args.action=='replay':
        if not status.strict_hardening_candidate or status.mutation_protocol_version!=2 or status.store_incarnation!=message.expected_store_incarnation:raise transport.ToolError('replay requires same candidate store incarnation/protocol; no request sent')
        # Exact old expectations/token are intentional. No current
        # generation/high-water mutation preflight applies to replay.
    else:
        if not status.strict_hardening_candidate:raise transport.ToolError('mutation requires visible strict-hardening candidate')
        if status.mutation_protocol_version!=2:raise transport.ToolError('target does not advertise mutation protocol 2')
        if status.store_incarnation!=args.incarnation or status.store_generation!=args.store_generation:raise transport.ToolError('explicit incarnation/generation differs from target; no mutation sent')
        if args.token<=status.transaction_token_high_water:raise transport.ToolError('token is not above durable high water; use QUERY for lost response, never auto-retry')
        if args.fault_ticket and (status.fault_control_version!=2 or not status.storage_fault_pending or status.storage_fault_ticket!=args.fault_ticket):raise transport.ToolError('pending fault ticket differs; no mutation sent')
        if args.action=='set-reference' and status.config_generation!=args.config_generation:raise transport.ToolError('explicit Config generation differs from target; no mutation sent')

def main():
    global TRACE_SINK
    args=parse_args();port=transport.PosixSerialPort(args.port,115200,args.timeout)
    try:
        if args.trace_out:TRACE_SINK=args.trace_out.open('x',encoding='utf-8')
        pb,json_format,_=transport.load_runtime_proto_modules(ROOT)
        message,host=build_message(args,pb,json_format)
        port.open();port.flush_input()
        if args.action in ('arm','clear','replay') or args.action in MUTATIONS:
            status=request(port,pb,pb.ProfileStoreRequest(protocol_version=2,operation=pb.PROFILE_STORE_STATUS,liveness_trace=args.trace),phase='status_preflight')
            verify_preflight(args,status,message)
        exact_payload=host.pop('_exact_payload',None)
        if args.action in MUTATIONS:
            payload=message.SerializeToString(deterministic=True)
            receipt={'receipt_format':1,'incarnation':message.expected_store_incarnation,
                'request_hex':payload.hex(),'request_sha256':hashlib.sha256(payload).hexdigest(),
                'decoded_request':json_format.MessageToDict(message,preserving_proto_field_name=True)}
            # Exclusive creation preserves the original lost-response identity.
            with args.request_out.open('x',encoding='utf-8') as out:json.dump(receipt,out,sort_keys=True,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
            directory_fd=os.open(str(args.request_out.parent),os.O_RDONLY)
            try:os.fsync(directory_fd)
            finally:os.close(directory_fd)
        response=request(port,pb,message,exact_payload,phase=args.action)
        result={'response':json_format.MessageToDict(response,preserving_proto_field_name=True),'host':host}
        text=json.dumps(result,sort_keys=True,indent=2)+'\n'
        if args.output:args.output.write_text(text,encoding='utf-8')
        print(text,end='')
        return 0 if response.status in (pb.PROFILE_STORE_OK,pb.PROFILE_STORE_TRANSACTION_EXPIRED,pb.PROFILE_STORE_NOT_FOUND,pb.PROFILE_STORE_TRANSACTION_ABORTED) else 1
    except Exception as error:
        print(f'candidate tool: {error}');return 1
    finally:
        port.close()
        if TRACE_SINK is not None:TRACE_SINK.close();TRACE_SINK=None
if __name__=='__main__':raise SystemExit(main())
