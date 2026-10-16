#!/usr/bin/env python3
"""Offline special-QUERY preflight, exact custody and no-retry proof."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
import glyph_profile_store_candidate_tool as cli
import glyph_serial_config_tool as transport

ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise AssertionError(m)
def main():
    pb,jf,_=transport.load_runtime_proto_modules(ROOT)
    with tempfile.TemporaryDirectory(prefix='glyph-reconcile-cli-') as directory:
        root=Path(directory)
        base=['--port','UNOPENED','query','--token','0xf000000000001c00','--reconcile-fault-ticket','8','--request-out',str(root/'query.request.json'),'--trace-out',str(root/'query.trace.jsonl')]
        args=cli.parse_args(base);message,_=cli.build_message(args,pb,jf)
        need(message.operation==pb.PROFILE_STORE_QUERY_TRANSACTION and message.protocol_version==2 and message.fault_ticket==8 and message.liveness_trace,'special query wire fields')
        ordinary,_=cli.build_message(cli.parse_args(['--port','UNOPENED','query','--token','9']),pb,jf)
        need(not ordinary.fault_ticket and not ordinary.liveness_trace,'ordinary query unchanged')
        valid=pb.ProfileStoreResponse(protocol_version=2,strict_hardening_candidate=True,mutation_protocol_version=2,storage_fault_capable=True,root_reconcile_fault_capable=True,fault_control_version=2,recovery_flags=8,storage_fault_pending=True,storage_fault_ticket=8,storage_fault_kind=2,storage_fault_operation=1,storage_fault_phase=1,storage_fault_result=1,storage_fault_path_class=2,storage_fault_skip=0)
        cli.verify_preflight(args,valid,message)
        for field,value in [('protocol_version',1),('strict_hardening_candidate',False),('mutation_protocol_version',1),('storage_fault_capable',False),('root_reconcile_fault_capable',False),('fault_control_version',1),('recovery_flags',0),('storage_fault_pending',False),('storage_fault_armed',True),('storage_fault_ticket',7),('storage_fault_kind',1),('storage_fault_kind',3),('storage_fault_operation',10),('storage_fault_operation',3),('storage_fault_operation',2),('storage_fault_phase',2),('storage_fault_result',2),('storage_fault_path_class',3),('storage_fault_skip',1)]:
            bad=pb.ProfileStoreResponse();bad.CopyFrom(valid);setattr(bad,field,value)
            try:cli.verify_preflight(args,bad,message)
            except transport.ToolError:pass
            else:raise AssertionError('unsafe preflight '+field)
        bad_argv=[['--port','UNOPENED',action,'--reconcile-fault-ticket','8'] for action in ['status','list','read','replay','arm','clear','create','update']]
        bad_argv+=[['--port','UNOPENED','query','--token','9','--fault-ticket','8'],base[:base.index('--request-out')],base[:base.index('--trace-out')],[*base,'--reconcile-fault-ticket','0x100000000']]
        for argv in bad_argv:
            with contextlib.redirect_stderr(io.StringIO()):
                try:cli.parse_args(argv)
                except SystemExit as e:need(e.code!=0,'parse rejected')
                else:raise AssertionError('unsafe CLI admitted')
        for outcome in ('unknown','timeout','bad-preflight','existing-receipt'):
            args=cli.parse_args([*base,'--request-out',str(root/(outcome+'.request.json')),'--trace-out',str(root/(outcome+'.trace.jsonl'))])
            ports=[];clock=[0.0]
            class Port:
                def __init__(self,*unused):self.fd=-1;self.timeout_sec=1;self.writes=[];self.replies=[];ports.append(self)
                def open(self):pass
                def close(self):pass
                def flush_input(self):pass
                def write_all(self,wire):
                    self.writes.append(wire);r=pb.ProfileStoreRequest.FromString(transport.cobs_decode(wire)[1:])
                    if r.operation==pb.PROFILE_STORE_STATUS:
                        reply=pb.ProfileStoreResponse();reply.CopyFrom(valid)
                        if outcome=='bad-preflight':reply.storage_fault_phase=2
                    else:
                        need(r==message,'exact single special QUERY transmitted')
                        receipt=json.loads(args.request_out.read_text());payload=r.SerializeToString(deterministic=True)
                        need(receipt['request_hex']==payload.hex() and receipt['request_sha256']==hashlib.sha256(payload).hexdigest(),'exclusive receipt durable before query transmission')
                        if outcome=='timeout':return
                        reply=pb.ProfileStoreResponse(protocol_version=2,request_token=r.request_token,status=pb.PROFILE_STORE_COMMIT_UNKNOWN,recovery_flags=26,storage_fault_ticket=8,storage_fault_triggered=True)
                    self.replies.append(transport.cobs_encode(bytes([9])+reply.SerializeToString()))
            if outcome=='existing-receipt':args.request_out.write_text('original receipt')
            def tick():clock[0]+=0.02;return clock[0]
            def ready(*unused):return ([-1],[],[]) if ports[-1].replies else ([],[],[])
            with patch.object(cli,'parse_args',return_value=args),patch.object(transport,'load_runtime_proto_modules',return_value=(pb,jf,None)),patch.object(transport,'PosixSerialPort',Port),patch.object(cli.time,'monotonic',tick),patch.object(cli.select,'select',ready),patch.object(cli.os,'read',lambda *unused:ports[-1].replies.pop(0)),contextlib.redirect_stdout(io.StringIO()) as output,contextlib.redirect_stderr(io.StringIO()):
                need(cli.main()==1,'unknown/refusal/timeout returns non-success')
            operations=[pb.ProfileStoreRequest.FromString(transport.cobs_decode(w)[1:]).operation for w in ports[0].writes]
            need(operations==([pb.PROFILE_STORE_STATUS,pb.PROFILE_STORE_QUERY_TRANSACTION] if outcome in ('unknown','timeout') else [pb.PROFILE_STORE_STATUS]),f'one STATUS then at most ONE QUERY, never retry: {outcome} {operations} {output.getvalue()}')
            events=[json.loads(line) for line in args.trace_out.read_text().splitlines()]
            need(sum(e['phase']=='query' and e['event']=='transmitted' for e in events)==(outcome in ('unknown','timeout')),'exact transmit journal')
            if outcome=='existing-receipt':need(args.request_out.read_text()=='original receipt','existing receipt preserved')
            if outcome=='unknown':
                replay=cli.parse_args(['--port','UNOPENED','replay','--replay-request',str(args.request_out)])
                try:cli.build_message(replay,pb,jf)
                except transport.ToolError:pass
                else:raise AssertionError('special query receipt admitted as mutation replay')
    print('glyph_profile_store_reconcile_cli: PASS preflight_negatives=19 orchestration=4 serial_opened=false no_retry=true');return 0
if __name__=='__main__':raise SystemExit(main())
