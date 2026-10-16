#!/usr/bin/env python3
"""Offline request/bound/guard proof. Does not open a serial port."""
import contextlib
import io
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import sys
import glyph_profile_store_candidate_tool as candidate
import glyph_serial_config_tool as transport

ROOT=Path(__file__).resolve().parents[1]
def require(ok,message):
    if not ok:raise AssertionError(message)
def rejected(argv):
    with contextlib.redirect_stderr(io.StringIO()):
        try:candidate.parse_args(argv)
        except SystemExit as error:return error.code!=0
    return False

def main():
    try:
        pb,json_format,_=transport.load_runtime_proto_modules(ROOT)
        with tempfile.TemporaryDirectory(prefix='glyph-candidate-cli-') as directory:
            profile=Path(directory)/'profile.json';profile.write_text(json.dumps({'response':{'profile':{'schemaVersion':1}}}))
            base=['--port','UNOPENED','create','--token','0x100000009','--store-generation','8','--incarnation','1','--name','ä'*16,'--rank','0','--profile-json',str(profile),'--request-out',str(Path(directory)/'request.json')]
            require(rejected([*base,'--trace-out',str(profile)]),'trace cannot alias profile')
            require(rejected([*base,'--trace-out',str(profile)+'.out','--output',str(profile)+'.out']),'trace cannot alias response output')
            args=candidate.parse_args(base);request,host=candidate.build_message(args,pb,json_format)
            require(request.protocol_version==2 and request.request_token==0x100000009 and request.expected_store_generation==8 and request.expected_store_incarnation==1,'explicit mutation fences/full token')
            require(request.HasField('profile') and request.profile.schema_version==1 and len(request.name.encode('utf-8'))==32,'READ export profile and byte bound')
            payload=request.SerializeToString(deterministic=True)
            saved={'receipt_format':1,'incarnation':request.expected_store_incarnation,'request_hex':payload.hex(),'request_sha256':host['transmitted_request_sha256'],'decoded_request':json_format.MessageToDict(request,preserving_proto_field_name=True)}
            receipt=Path(directory)/'receipt.json';receipt.write_text(json.dumps(saved))
            replay_args=candidate.parse_args(['--port','UNOPENED','replay','--replay-request',str(receipt)])
            replay,replay_host=candidate.build_message(replay_args,pb,json_format)
            later=pb.ProfileStoreResponse(strict_hardening_candidate=True,mutation_protocol_version=2,store_incarnation=1,store_generation=99,transaction_token_high_water=0x100000099)
            candidate.verify_preflight(replay_args,later,replay)
            try:candidate.verify_preflight(args,later,request)
            except transport.ToolError:pass
            else:raise AssertionError('ordinary mutation incorrectly bypassed fresh fences')
            require(replay_host['_exact_payload']==payload and replay.request_token==request.request_token and replay.expected_store_generation==8,'exact replay preserves old bytes/token/expectations')
            require(len(host['profile_file_sha256'])==64 and len(host['transmitted_request_sha256'])==64,'source/wire custody hashes')
            require(rejected([*base[:base.index('--name')],'--name','ä'*17,*base[base.index('--rank'):]]),'excess UTF8 bytes refused')
            for option in ('--token','--incarnation','--store-generation'):
                bad=base.copy();bad[bad.index(option)+1]='0' if option!='--store-generation' else '0x100000000'
                require(rejected(bad),'invalid mutation bound refused')
            bad=base.copy();bad.extend(['--profile-sha256','0'*64])
            try:candidate.build_message(candidate.parse_args(bad),pb,json_format)
            except transport.ToolError:pass
            else:raise AssertionError('changed source digest accepted')
            args=candidate.parse_args(['--port','UNOPENED','list','--page','8','--page-size','8']);request,_=candidate.build_message(args,pb,json_format)
            require(request.page_cursor==8 and request.page_size==8,'paged backup request')
            for action in ('update','duplicate'):
                require(rejected(['--port','UNOPENED',action,'--profile-id','1','--token','9','--store-generation','8','--incarnation','1']),'revision/source guards')
            require(rejected(['--port','UNOPENED','query','--token','0']),'zero query token refused')
            # Every newly traceable mutation must serialize the opt-in; ordinary
            # requests keep it absent. This is CLI parsing + actual protobuf,
            # including profile-bearing UPDATE rather than a constructed stub.
            common=['--port','UNOPENED','--token','0x100000009','--store-generation','8','--incarnation','1','--request-out',str(Path(directory)/'trace-request.json')]
            mutation_options={
                'create':['--name','trace','--rank','0','--profile-json',str(profile)],
                'update':['--profile-id','22','--profile-revision','130','--profile-json',str(profile)],
                'duplicate':['--profile-id','22','--profile-revision','130','--name','trace','--rank','0'],
                'rename':['--profile-id','22','--name','trace'],
                'reorder':['--profile-id','22','--rank','0'],
                'delete':['--profile-id','22'],
                'set-reference':['--profile-id','22','--mode-index','0','--config-generation','1'],
            }
            for action,options in mutation_options.items():
                for traced in (False,True):
                    parsed=candidate.parse_args([*common,action,*options,*(['--trace'] if traced else [])])
                    outgoing,_=candidate.build_message(parsed,pb,json_format)
                    decoded=pb.ProfileStoreRequest.FromString(outgoing.SerializeToString(deterministic=True))
                    require(decoded.operation==candidate.MUTATIONS[action] and decoded.liveness_trace==traced,f'{action} trace opt-in survives actual protobuf serialization')
            replay_traced,_=candidate.build_message(candidate.parse_args(['--port','UNOPENED','replay','--replay-request',str(receipt),'--trace']),pb,json_format)
            require(replay_traced.SerializeToString(deterministic=True)==payload,'trace flag must not alter exact replay identity')
        # Exercise the real CLI orchestration with an offline port. Retained
        # journal distinguishes the two formerly identical timeout points.
        with tempfile.TemporaryDirectory(prefix='glyph-cli-phase-') as directory:
            for succeeds in (False,True):
                journal=Path(directory)/f'{succeeds}.jsonl'
                clock=[0.0]
                class Port:
                    def __init__(self,*args):self.fd=-1;self.timeout_sec=5;self.writes=[];self.replies=[];ports.append(self)
                    def open(self):pass
                    def close(self):pass
                    def flush_input(self):pass
                    def write_all(self,data):
                        self.writes.append(data)
                        if succeeds and len(self.writes)==1:
                            reply=pb.ProfileStoreResponse(protocol_version=2,status=pb.PROFILE_STORE_OK,strict_hardening_candidate=True,storage_fault_capable=True,fault_control_version=2)
                            self.replies.append(transport.cobs_encode(bytes([9])+reply.SerializeToString()))
                ports=[]
                def tick():clock[0]+=0.25;return clock[0]
                def ready(*args):return ([ports[-1].fd],[],[]) if ports[-1].replies else ([],[],[])
                argv=['candidate','--port','UNOPENED','arm','--path-class','record','--operation','write','--result','fail-before','--trace-out',str(journal)]
                with patch.object(sys,'argv',argv),patch.object(candidate.transport,'load_runtime_proto_modules',lambda root:(pb,json_format,None)),patch.object(candidate.transport,'PosixSerialPort',Port),patch.object(candidate.time,'monotonic',tick),patch.object(candidate.select,'select',ready),patch.object(candidate.os,'read',lambda *args:ports[-1].replies.pop(0)),contextlib.redirect_stdout(io.StringIO()) as output,contextlib.redirect_stderr(io.StringIO()):
                    require(candidate.main()==1,'offline bounded timeout exit')
                events=[json.loads(line) for line in journal.read_text().splitlines()]
                transmitted=[e['phase'] for e in events if e['event']=='transmitted']
                require(transmitted==(['status_preflight','arm'] if succeeds else ['status_preflight']),f'journal proves ARM transmitted vs not transmitted: {succeeds} {events} {output.getvalue()}')
                require(events[-1]['phase']==('arm' if succeeds else 'status_preflight') and events[-1]['event']=='response_timeout','exact timeout stage durable')
            # Multiple progress frames must be consumed without mistaking a
            # stage acknowledgement for the final STATUS result.
            class TracePort:
                fd=-1;timeout_sec=5
                def write_all(self,data):pass
            message=pb.ProfileStoreRequest(protocol_version=2,operation=pb.PROFILE_STORE_STATUS,request_token=123,liveness_trace=True)
            frames=[]
            for stage in (1,2,3,4,5,6,7,8,9,0):
                reply=pb.ProfileStoreResponse(protocol_version=2,request_token=123,liveness_stage=stage,status=0 if stage else pb.PROFILE_STORE_OK)
                frames.append(transport.cobs_encode(bytes([9])+reply.SerializeToString()))
            with patch.object(candidate.select,'select',lambda *args:([-1],[],[])),patch.object(candidate.os,'read',lambda *args:b''.join(frames)),contextlib.redirect_stderr(io.StringIO()) as log:
                require(candidate.request(TracePort(),pb,message,phase='status').status==pb.PROFILE_STORE_OK,'trace frames precede final response')
            require(log.getvalue().count('device_stage')==9,'all progress stages retained')
        # Real host parser: chunked large READ, terminal trailer, and partial timeout.
        args=candidate.parse_args(['--port','UNOPENED','read','--profile-id','1','--trace'])
        message,_=candidate.build_message(args,pb,json_format)
        require(message.liveness_trace,'READ opt-in trace serialized')
        final=pb.ProfileStoreResponse()
        retained=json.loads((ROOT/"tools/fixtures/profile_store_read_storage/physical_id1_response.json").read_text())
        json_format.ParseDict(retained["response"],final)
        final.request_token=message.request_token
        require(len(final.SerializeToString())==1989,"actual retained full READ payload")
        encoded=transport.cobs_encode(bytes([9])+final.SerializeToString())
        terminal=transport.cobs_encode(bytes([9])+pb.ProfileStoreResponse(liveness_stage=24,liveness_value=len(encoded)).SerializeToString())
        for mode in ('complete','partial','missing_trailer','failure','corrupt_then_failure'):
            raw=encoded+terminal if mode=='complete' else encoded[:5] if mode=='partial' else encoded
            if mode in ('failure','corrupt_then_failure'):
                raw=(b'\xff\x01\0' if mode=='corrupt_then_failure' else b'')+transport.cobs_encode(bytes([9])+pb.ProfileStoreResponse(liveness_stage=25).SerializeToString())
            chunks=([encoded[:1024],encoded[1024:-1],encoded[-1:],terminal] if mode=='complete' else [raw[i:i+1024] for i in range(0,len(raw),1024)]);clock=[0.0]
            def tick():clock[0]+=0.01;return clock[0]
            def ready(*args):return ([-1],[],[]) if chunks else ([],[],[])
            log=io.StringIO()
            with patch.object(candidate.time,'monotonic',tick),patch.object(candidate.select,'select',ready),patch.object(candidate.os,'read',lambda *args:chunks.pop(0)),contextlib.redirect_stderr(log):
                try:result=candidate.request(TracePort(),pb,message,phase='read')
                except transport.ToolError:require(mode!='complete','complete READ wrongly rejected')
                else:require(mode=='complete' and result==final,'incomplete READ wrongly accepted')
            rows=[json.loads(line) for line in log.getvalue().splitlines()]
            require(any(row['event']=='receive_chunk' for row in rows),'received bytes journaled')
            if mode=='complete':require(rows[-1]['event']=='read_complete','terminal observed after full response')
            if mode=='partial':
                last=rows[-1]
                require(last['event']=='response_timeout' and last['received_bytes']==5 and last['partial_frame_hex']==raw.hex() and not last['last_byte_is_delimiter'],'exact partial-prefix evidence')
            if mode=='missing_trailer':require(rows[-1]['final_response_received'],'timeout distinguishes complete response without completion trailer')
            if mode=='corrupt_then_failure':require(any(row['event']=='invalid_frame' for row in rows),'partial frame retained before failure trailer')
        # A valid CMD_ERROR is terminal diagnostic evidence, including during
        # traced READ where malformed partial frames may otherwise be skipped.
        diagnostics=(
            'Profile store frame timeout',
            'Profile store frame timeout phase=2 raw=256 decoded=253 elapsed_ms=5000 tasks=4972 last_ms=1 fetched=256 eop=0',
        )
        with tempfile.TemporaryDirectory(prefix='glyph-cli-rx-error-') as directory:
            for operation,traced in ((pb.PROFILE_STORE_UPDATE,False),(pb.PROFILE_STORE_UPDATE,True),(pb.PROFILE_STORE_READ,True)):
                for index,diagnostic in enumerate(diagnostics):
                    message=pb.ProfileStoreRequest(protocol_version=2,operation=operation,request_token=123,liveness_trace=traced)
                    wire=transport.cobs_encode(bytes([transport.CMD_ERROR])+diagnostic.encode())
                    chunks=[wire[:10],wire[10:-1],wire[-1:]]
                    journal=Path(directory)/f'{operation}-{traced}-{index}.jsonl'
                    with journal.open('x',encoding='utf-8') as sink,patch.object(candidate,'TRACE_SINK',sink),patch.object(candidate.select,'select',lambda *args:([-1],[],[])),patch.object(candidate.os,'read',lambda *args:chunks.pop(0)),contextlib.redirect_stderr(io.StringIO()):
                        try:candidate.request(TracePort(),pb,message,phase='update' if operation==pb.PROFILE_STORE_UPDATE else 'read')
                        except transport.ToolError as error:require(str(error)=='device CMD_ERROR: '+diagnostic,'exact timeout diagnostic rethrown')
                        else:raise AssertionError('CMD_ERROR accepted as a successful response')
                    events=[json.loads(line) for line in journal.read_text().splitlines()]
                    errors=[row for row in events if row['event']=='device_error']
                    require(len(errors)==1 and errors[0]['command']==transport.CMD_ERROR and errors[0]['diagnostic']==diagnostic,'valid device error retained durably')
                    require(not any(row['event'] in ('invalid_frame','response','response_timeout') for row in events),'valid error must not become invalid frame, success or host timeout')
                    last=events[-1]
                    require(last['event']=='device_error' and last['received_bytes']==len(wire) and last['delimiters']==1 and last['last_byte_is_delimiter'] and last['partial_frame_bytes']==0,'bounded receive evidence accompanies device error')
                    require(last['received_prefix_sha256']==hashlib.sha256(wire).hexdigest(),'exact error wire hash retained')
                    require(b''.join(bytes.fromhex(row['chunk_hex']) for row in events if row['event']=='receive_chunk')==wire,'fragmented raw diagnostic bytes retained')
                    require(not chunks,'delimiter received before terminal diagnostic')
        print('glyph_profile_store_candidate_tool: PASS offline=true serial_opened=false explicit_fences=true utf8_bound=true source_hash_guard=true paged_backup=true exact_replay_bypasses_fresh_fences=true mutation_trace=true device_error_journal=true')
        return 0
    except Exception as error:
        print(f'glyph_profile_store_candidate_tool: FAIL: {error}');return 1
if __name__=='__main__':raise SystemExit(main())
